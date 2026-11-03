"""Speak channel: media players and Assist satellites (DESIGN §23.9, D-091, D-114).

Satellites get `assist_satellite.announce`. A media player whose state shows the announce feature
gets `tts.speak`, which announces (it passes `announce: true` itself). Any other player gets
`media_player.play_media` with the tts media source and no `announce`, at the volume it has. The
hub never changes or restores volume (N-66, N-75, N-76, N-86).

Speech cannot be taken back, so a message that ends says nothing. A speaker does one thing at a
time and does not repeat the same text within the cooldown.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player.const import MediaPlayerEntityFeature
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceNotFound
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from ...const import (
    DEFAULT_OPTIONS,
    OPT_SPEAK_COOLDOWN,
    OPT_SPEAK_LANGUAGE,
    OPT_SPEAK_MAX_LENGTH,
    OPT_SPEAK_TTS_ENTITY,
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
        self._spoken: dict[tuple[str, str], Any] = {}  # (speaker, text) to the time it was said

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
        if target.quiet:
            return Outcome(Result.SKIPPED, "quiet_hours")  # quiet hours: speech is skipped
        entity = target.key
        state = self._hass.states.get(entity)
        if state is None:
            return Outcome(Result.FAILED, "entity_missing")
        text = speech_text(message, int(self._opt(OPT_SPEAK_MAX_LENGTH)))
        if not text:
            return Outcome(Result.SKIPPED, "nothing_to_say")
        async with self._locks.setdefault(entity, asyncio.Lock()):
            if self._repeated(entity, text):
                return Outcome(Result.SKIPPED, "cooldown")
            outcome = await self._speak(entity, state.attributes, text)
            if outcome.result is Result.SENT:
                self._spoken[(entity, text)] = dt_util.utcnow()
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

    def _repeated(self, entity: str, text: str) -> bool:
        cooldown = int(self._opt(OPT_SPEAK_COOLDOWN))
        said = self._spoken.get((entity, text))
        now = dt_util.utcnow()
        for key in [k for k, t in self._spoken.items() if now - t > timedelta(hours=1)]:
            del self._spoken[key]
        return bool(cooldown and said and now - said < timedelta(seconds=cooldown))

    async def _speak(self, entity: str, attributes: Any, text: str) -> Outcome:
        language = str(self._opt(OPT_SPEAK_LANGUAGE) or self._hass.config.language)
        if entity.split(".", 1)[0] == SATELLITE:
            return await self._call(
                entity, SATELLITE, "announce", {"entity_id": entity, "message": text}
            )
        engine = self._tts_entity()
        if engine is None:
            return Outcome(Result.FAILED, "no_tts_engine")
        features = int(attributes.get("supported_features", 0))
        if features & MediaPlayerEntityFeature.MEDIA_ANNOUNCE:
            data = {
                "entity_id": engine,
                "media_player_entity_id": entity,
                "message": text,
                "language": language,
            }
            return await self._call(entity, "tts", "speak", data)
        try:
            media_id = media_source_id(self._hass, text, engine, language)
        except HomeAssistantError:
            return Outcome(Result.FAILED, "no_tts_engine")
        media = {"media_content_id": media_id, "media_content_type": "music"}
        return await self._call(entity, PLAYER, "play_media", {"entity_id": entity, **media})

    async def _call(self, entity: str, domain: str, service: str, data: dict[str, Any]) -> Outcome:
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
