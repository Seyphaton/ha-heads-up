"""Speak channel: media players and Assist satellites (DESIGN §23.9, D-091, D-114).

Satellites get `assist_satellite.announce`. A media player whose state shows the announce feature
gets `tts.speak`, which announces (it passes `announce: true` itself). Any other player gets
`media_player.play_media` with the tts media source and no `announce`, at the volume it has.

Volume (D-208, D-215, D-217): the call's `volume`, else the volume of the severity, else the time
band, else none. A `sonos` player with announce takes it as the clip volume (`extra.volume`,
N-104, N-105), so its own volume never changes. Any other player is set before it speaks and put
back afterwards: when playback ends, or after an estimate of the speech length for a player that
announces over what it plays. Nothing is put back when someone changed the volume meanwhile, and
only once after the last of several messages on one speaker.

Speech cannot be taken back, so a message that ends says nothing. A speaker does one thing at a
time and does not repeat the same text within the cooldown.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player.const import MediaPlayerEntityFeature
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceNotFound
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from ...const import (
    DEFAULT_OPTIONS,
    OPT_SPEAK_COOLDOWN,
    OPT_SPEAK_LANGUAGE,
    OPT_SPEAK_MAX_LENGTH,
    OPT_SPEAK_RESTORE_VOLUME,
    OPT_SPEAK_SEVERITY_VOLUME,
    OPT_SPEAK_TTS_ENTITY,
    OPT_SPEAK_VOLUME_BANDS,
    TEST_ID_PREFIX,
)
from ...models import Banner
from .base import Capabilities, Outcome, Result, Target

if TYPE_CHECKING:
    from ...manager import BannerManager
    from ..engine import HubEngine

_LOGGER = logging.getLogger(__name__)
WARN_EVERY = 3600  # seconds between log warnings per speaker
MAX_WAIT = 30  # seconds to wait for a player to finish before the next message
NO_SPEAKER = frozenset({"group_empty", "entity_missing"})  # reasons that get a bell entry
SATELLITE = "assist_satellite"
PLAYER = "media_player"
# Integrations whose announce takes `extra.volume` for the clip only (verified in source, N-105).
CLIP_VOLUME_PLATFORMS = frozenset({"sonos"})
RESTORE_MAX_WAIT = 60  # seconds: the longest wait before a volume is put back
VOLUME_TOLERANCE = 0.011  # a player may round the level it was given


def _minutes(value: str) -> int:
    hours, minutes = str(value).split(":")[:2]
    return int(hours) * 60 + int(minutes)


def band_volume(bands: list[dict[str, Any]], now: datetime) -> float | None:
    """The volume of the first time band that `now` (local time) is in, 0 to 1, or None. A band
    from 22:00 to 07:00 runs over midnight; a band whose start equals its end is empty."""
    here = now.hour * 60 + now.minute
    for band in bands:
        try:
            start, end = _minutes(band["from"]), _minutes(band["to"])
            volume = float(band["volume"]) / 100
        except KeyError, TypeError, ValueError:
            continue
        inside = start <= here < end if start < end else (here >= start or here < end)
        if start != end and inside:
            return volume
    return None


def resolve_volume(message: Banner, options: dict[str, Any], now: datetime) -> float | None:
    """The call's volume, then the severity's, then the time band's, else None (D-208)."""
    if message.volume is not None:
        return message.volume
    by_severity = options.get(OPT_SPEAK_SEVERITY_VOLUME) or {}
    if (percent := by_severity.get(message.severity)) is not None:
        return float(percent) / 100
    return band_volume(list(options.get(OPT_SPEAK_VOLUME_BANDS) or []), now)


def speech_seconds(text: str) -> float:
    """About how long a text takes to say: 15 characters a second plus 2, from 4 to 60 (D-217)."""
    return min(max(len(text) / 15 + 2, 4), RESTORE_MAX_WAIT)


def media_source_id(hass: HomeAssistant, text: str, engine: str, language: str) -> str:
    """The tts media source of a text. Imported late: the tts component brings its own
    requirements, which exist only once it is set up (N-86)."""
    try:
        from homeassistant.components.tts.media_source import (
            generate_media_source_id,
        )
    except ImportError as err:
        raise HomeAssistantError("tts is not available") from err
    return generate_media_source_id(hass, message=text, engine=engine, language=language)


def speech_text(message: Banner, limit: int) -> str:
    """What is said: `tts_message`, else the title, else the message (D-090), cut at a word."""
    text = " ".join((message.tts_message or message.title or message.message).split())
    if len(text) <= limit:
        return text
    cut = text[: max(limit - 1, 1)]
    if text[len(cut)] != " " and " " in cut:  # the cut is inside a word: drop that word
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,.;:") + "…"


class SpeakChannel:
    name = "speak"
    available = True
    capabilities = Capabilities(
        title=False, buttons=False, clear=False, replace=False, per_user=False
    )

    def __init__(self, hass: HomeAssistant, hub: HubEngine, manager: BannerManager) -> None:
        self._hass = hass
        self._hub = hub
        self._manager = manager
        self._warned: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._spoken: dict[
            tuple[str, str, float | None], Any
        ] = {}  # (speaker, text, volume) to the time
        # Volume restore per speaker: the level before the first change, the level last set,
        # and how many speeches still wait to finish (D-217).
        self._original: dict[str, float] = {}
        self._last_set: dict[str, float] = {}
        self._pending: dict[str, int] = {}
        self._restore_cancels: set[Any] = set()  # timers and listeners of waiting restores

    def stop(self) -> None:
        """Drop waiting restores when the integration unloads; the volume stays as it is."""
        for cancel in list(self._restore_cancels):
            cancel()
        self._restore_cancels.clear()

    # Settings ---------------------------------------------------------------------------

    def _opt(self, key: str) -> Any:
        return self._manager.options.get(key, DEFAULT_OPTIONS[key])

    def _tts_entity(self) -> str | None:
        """The configured engine, else the only one there is."""
        if configured := self._opt(OPT_SPEAK_TTS_ENTITY):
            return str(configured)
        engines = [s.entity_id for s in self._hass.states.async_all("tts")]
        return engines[0] if len(engines) == 1 else None

    # Delivery ---------------------------------------------------------------------------

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        entity = target.key
        if target.quiet:
            _LOGGER.debug("Speech on %s skipped: quiet hours", entity)
            return Outcome(Result.SKIPPED, "quiet_hours")  # quiet hours: speech is skipped
        state = self._hass.states.get(entity)
        if state is None:
            self._warn(entity, "Speech on %s failed: the speaker does not exist", entity)
            return Outcome(Result.FAILED, "entity_missing")
        text = speech_text(message, int(self._opt(OPT_SPEAK_MAX_LENGTH)))
        if not text:
            _LOGGER.debug("Speech on %s skipped: nothing to say", entity)
            return Outcome(Result.SKIPPED, "nothing_to_say")
        volume = resolve_volume(message, self._manager.options, dt_util.now())
        async with self._locks.setdefault(entity, asyncio.Lock()):
            key = (entity, text, volume)
            if self._repeated(key, message):
                _LOGGER.debug(
                    "Speech on %s skipped: the same text was said within the pause", entity
                )
                return Outcome(Result.SKIPPED, "cooldown")
            outcome = await self._speak(entity, state.attributes, text, volume)
            if outcome.result is Result.SENT:
                self._spoken[key] = dt_util.utcnow()
                await self._wait_until_done(entity, outcome)
            return outcome

    async def update(self, message: Banner, target: Target) -> Outcome:
        # An update does not repeat what was already said.
        row = self._hub.ledger.rows.get((message.id, self.name, target.key))
        if row is not None and row.state.value == "sent":
            return Outcome(Result.SKIPPED, "already_spoken")
        return await self.deliver(message, target)

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        return Outcome(Result.SKIPPED, "not_clearable")  # nothing is said when a message ends

    def _repeated(self, key: tuple[str, str, float | None], message: Banner) -> bool:
        """The same text on the same speaker at the same volume within the pause. A critical
        message and a message sent from Test send are never held back: a test repeats text on
        purpose, and a critical message must not be silenced by another one."""
        if message.severity == "critical" or message.id.startswith(TEST_ID_PREFIX):
            return False
        cooldown = int(self._opt(OPT_SPEAK_COOLDOWN))
        said = self._spoken.get(key)
        now = dt_util.utcnow()
        for key in [k for k, t in self._spoken.items() if now - t > timedelta(hours=1)]:
            del self._spoken[key]
        return bool(cooldown and said and now - said < timedelta(seconds=cooldown))

    async def _speak(
        self, entity: str, attributes: Any, text: str, volume: float | None = None
    ) -> Outcome:
        language = str(self._opt(OPT_SPEAK_LANGUAGE) or self._hass.config.language)
        if entity.split(".", 1)[0] == SATELLITE:
            return await self._call(
                entity, SATELLITE, "announce", {"entity_id": entity, "message": text}
            )
        engine = self._tts_entity()
        if engine is None:
            engines = [s.entity_id for s in self._hass.states.async_all("tts")]
            self._warn(
                "tts_engine",
                "Speech on %s failed: no text-to-speech engine is chosen. %s",
                entity,
                (
                    f"Found {len(engines)}: {', '.join(engines)}. Choose one in Speech settings."
                    if engines
                    else "None is set up in Home Assistant."
                ),
            )
            return Outcome(Result.FAILED, "no_tts_engine")
        features = int(attributes.get("supported_features", 0))
        announces = bool(features & MediaPlayerEntityFeature.MEDIA_ANNOUNCE)
        if volume is not None and announces and self._platform(entity) in CLIP_VOLUME_PLATFORMS:
            return await self._speak_clip(entity, text, engine, language, volume)
        changed = await self._set_volume(entity, features, volume)
        if announces:
            data = {
                "entity_id": engine,
                "media_player_entity_id": entity,
                "message": text,
                "language": language,
            }
            outcome = await self._call(entity, "tts", "speak", data)
        else:
            try:
                media_id = media_source_id(self._hass, text, engine, language)
            except HomeAssistantError as err:
                self._warn("tts_engine", "Speech on %s failed: %s", entity, err)
                outcome = Outcome(Result.FAILED, "no_tts_engine")
            else:
                media = {"media_content_id": media_id, "media_content_type": "music"}
                outcome = await self._call(
                    entity, PLAYER, "play_media", {"entity_id": entity, **media}
                )
        if changed:
            self._restore_later(entity, text, announces and outcome.result is Result.SENT)
        return outcome

    def _platform(self, entity: str) -> str | None:
        """The integration of a player, from the entity registry (N-107)."""
        entry = er.async_get(self._hass).async_get(entity)
        return entry.platform if entry is not None else None

    async def _speak_clip(
        self, entity: str, text: str, engine: str, language: str, volume: float
    ) -> Outcome:
        """Announce with a clip volume: the player's own volume stays as it is (D-217)."""
        try:
            media_id = media_source_id(self._hass, text, engine, language)
        except HomeAssistantError as err:
            self._warn("tts_engine", "Speech on %s failed: %s", entity, err)
            return Outcome(Result.FAILED, "no_tts_engine")
        data = {
            "entity_id": entity,
            "media_content_id": media_id,
            "media_content_type": "music",
            "announce": True,
            "extra": {"volume": volume},
        }
        return await self._call(entity, PLAYER, "play_media", data)

    def _restore_later(self, entity: str, text: str, overlay: bool) -> None:
        """Put the volume back once this speech is over: after the estimate for a player that
        announces over its music, else when it stops playing (at most a minute)."""
        if not self._opt(OPT_SPEAK_RESTORE_VOLUME):
            self._forget(entity)
            return
        cancels: list[Any] = []

        def drop() -> None:
            while cancels:
                cancel = cancels.pop()
                self._restore_cancels.discard(cancel)
                cancel()

        def track(cancel: Any) -> None:
            cancels.append(cancel)
            self._restore_cancels.add(cancel)

        @callback
        def done(*_: Any) -> None:
            drop()
            self._restore(entity)

        if overlay:
            track(async_call_later(self._hass, speech_seconds(text), done))
            return

        @callback
        def changed(event: Event[Any]) -> None:
            new = event.data["new_state"]
            if new is None or new.state != "playing":
                done()

        state = self._hass.states.get(entity)
        if state is None or state.state != "playing":
            # Not playing yet or any more: give it the estimate to start and finish.
            track(async_call_later(self._hass, speech_seconds(text), done))
            return
        track(async_track_state_change_event(self._hass, [entity], changed))
        track(async_call_later(self._hass, RESTORE_MAX_WAIT, done))

    @callback
    def _restore(self, entity: str) -> None:
        self._pending[entity] = max(self._pending.get(entity, 1) - 1, 0)
        if self._pending[entity]:
            return  # another message on this speaker still runs; the last one puts it back
        original = self._original.pop(entity, None)
        last = self._last_set.pop(entity, None)
        self._pending.pop(entity, None)
        state = self._hass.states.get(entity)
        if original is None or last is None or state is None:
            return
        current = state.attributes.get("volume_level")
        if current is None or abs(float(current) - last) > VOLUME_TOLERANCE:
            _LOGGER.debug("Volume of %s not put back: it was changed meanwhile", entity)
            return
        if abs(original - last) <= VOLUME_TOLERANCE:
            return
        self._hass.async_create_task(self._put_back(entity, original))

    async def _put_back(self, entity: str, volume: float) -> None:
        try:
            await self._hass.services.async_call(
                PLAYER, "volume_set", {"entity_id": entity, "volume_level": volume}, blocking=True
            )
        except HomeAssistantError as err:
            self._warn(f"volume:{entity}", "Putting back the volume of %s failed: %s", entity, err)

    def _forget(self, entity: str) -> None:
        self._pending[entity] = max(self._pending.get(entity, 1) - 1, 0)
        if not self._pending[entity]:
            for store in (self._original, self._last_set, self._pending):
                store.pop(entity, None)

    async def _set_volume(self, entity: str, features: int, volume: float | None) -> bool:
        """Set the volume before speech when there is one. A player that cannot be set, or that
        refuses, still speaks: the message matters more than its volume. Returns True when the
        volume was set, so it is put back later; a satellite has no volume to set."""
        if volume is None:
            return False
        if not features & MediaPlayerEntityFeature.VOLUME_SET:
            _LOGGER.debug("Volume for %s ignored: the player cannot set its volume", entity)
            return False
        state = self._hass.states.get(entity)
        before = state.attributes.get("volume_level") if state is not None else None
        try:
            await self._hass.services.async_call(
                PLAYER, "volume_set", {"entity_id": entity, "volume_level": volume}, blocking=True
            )
        except HomeAssistantError as err:
            self._warn(f"volume:{entity}", "Setting the volume of %s failed: %s", entity, err)
            return False
        if before is None and entity not in self._original:
            return False  # the earlier level is unknown: nothing to put back
        self._original.setdefault(entity, float(before) if before is not None else volume)
        self._last_set[entity] = volume
        self._pending[entity] = self._pending.get(entity, 0) + 1
        return True

    async def _call(self, entity: str, domain: str, service: str, data: dict[str, Any]) -> Outcome:
        _LOGGER.debug("Speaking on %s through %s.%s", entity, domain, service)
        try:
            await self._hass.services.async_call(domain, service, data, blocking=True)
        except ServiceNotFound:
            self._warn(entity, "%s.%s does not exist", domain, service)
            return Outcome(Result.FAILED, "service_not_found")
        except HomeAssistantError as err:
            self._warn(
                entity, "Speaking on %s through %s.%s failed: %s", entity, domain, service, err
            )
            return Outcome(Result.FAILED, "send_failed")
        return Outcome(Result.SENT)

    async def _wait_until_done(self, entity: str, outcome: Outcome) -> None:
        """Hold the speaker's queue while it plays what was just sent, so two messages do not cut
        each other off. A player that overlays (announce) and a satellite are not waited for."""
        state = self._hass.states.get(entity)
        if state is None or entity.split(".", 1)[0] != PLAYER or state.state != "playing":
            return
        if (
            int(state.attributes.get("supported_features", 0))
            & MediaPlayerEntityFeature.MEDIA_ANNOUNCE
        ):
            return
        done = asyncio.Event()

        @callback
        def changed(event: Event[Any]) -> None:
            new = event.data["new_state"]
            if new is None or new.state != "playing":
                done.set()

        unsub = async_track_state_change_event(self._hass, [entity], changed)
        try:
            async with asyncio.timeout(MAX_WAIT):
                await done.wait()
        except TimeoutError:
            pass
        finally:
            unsub()

    def _warn(self, key: str, message: str, *args: object) -> None:
        now = time.monotonic()
        if now - self._warned.get(key, -WARN_EVERY) >= WARN_EVERY:
            self._warned[key] = now
            _LOGGER.warning(message, *args)
