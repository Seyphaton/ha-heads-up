"""Helpers for the hub tests: fake Companion devices, speakers, persons, events, time.

Everything here is a fake of a Home Assistant behavior the hub relies on; the facts are in
docs/dev/HA_API_NOTES.md (N-61 to N-74). No test needs a real device.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.core import Context, HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    async_mock_service,
)

MOBILE_APP = "mobile_app"
ACTION_EVENT = "mobile_app_notification_action"
CLEARED_EVENT = "mobile_app_notification_cleared"


def notify_service_name(device_name: str) -> str:
    """Name of the legacy notify service of a mobile_app device (N-70)."""
    return slugify(f"{MOBILE_APP}_{device_name}")


@dataclass
class FakeDevice:
    """A fake Companion app registration with its tracker, person and notify service."""

    device_name: str
    device_id: str
    user_id: str | None
    entry: MockConfigEntry
    tracker_entity_id: str
    notify_service: str
    calls: list[ServiceCall] = field(default_factory=list)


async def add_mobile_app_device(
    hass: HomeAssistant,
    device_name: str,
    *,
    user_id: str | None = None,
    person_entity_id: str | None = None,
    tracker_state: str = "home",
) -> FakeDevice:
    """Create what a Companion app registration leaves behind (N-71).

    A `mobile_app` config entry (not set up) with `device_name`, `device_id` and `user_id`, a
    device in the device registry with the identifier `(mobile_app, device_id)`, a
    `device_tracker` entity with `unique_id` = `device_id`, and the legacy notify service
    `notify.mobile_app_<slug of device_name>` recording its calls. With `person_entity_id` the
    tracker is added to that person's `device_trackers`.
    """
    device_id = f"dev_{slugify(device_name)}"
    entry = MockConfigEntry(
        domain=MOBILE_APP,
        title=device_name,
        data={
            "device_name": device_name,
            "device_id": device_id,
            "user_id": user_id,
            "webhook_id": f"webhook_{device_id}",
            "app_id": "io.homeassistant.companion.test",
            "app_name": "Home Assistant",
            "os_name": "iOS",
            "os_version": "18.0",
            "manufacturer": "Apple",
            "model": "iPhone",
            "supports_encryption": False,
        },
    )
    entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(MOBILE_APP, device_id)},
        name=device_name,
        manufacturer="Apple",
        model="iPhone",
    )
    tracker = er.async_get(hass).async_get_or_create(
        "device_tracker",
        MOBILE_APP,
        device_id,
        config_entry=entry,
        device_id=device.id,
        suggested_object_id=slugify(device_name),
        original_name=device_name,
    )
    hass.states.async_set(tracker.entity_id, tracker_state)
    service = notify_service_name(device_name)
    calls = async_mock_service(hass, "notify", service)
    if person_entity_id is not None:
        state = hass.states.get(person_entity_id)
        trackers = list(state.attributes.get("device_trackers", [])) if state else []
        set_person(
            hass,
            person_entity_id,
            state.state if state else "home",
            user_id=user_id,
            device_trackers=[*trackers, tracker.entity_id],
        )
    await hass.async_block_till_done()
    return FakeDevice(device_name, device_id, user_id, entry, tracker.entity_id, service, calls)


def set_person(
    hass: HomeAssistant,
    entity_id: str,
    state: str | None,
    *,
    user_id: str | None = None,
    device_trackers: list[str] | None = None,
) -> None:
    """Set a person state.

    `state` is `home`, `not_home`, a zone name, `unavailable` or `None`. A person without a
    usable tracker has the state `None` (N-63), which the state machine stores as `unknown`.
    """
    attributes: dict[str, Any] = {"id": entity_id.split(".", 1)[1], "editable": True}
    if user_id is not None:
        attributes["user_id"] = user_id
    attributes["device_trackers"] = device_trackers if device_trackers is not None else []
    hass.states.async_set(entity_id, "unknown" if state is None else state, attributes)


async def fire_app_action(
    hass: HomeAssistant,
    action: str,
    *,
    tag: str | None = None,
    user_id: str | None = None,
    **extra: Any,
) -> None:
    """Fire `mobile_app_notification_action` as the app does.

    `context.user_id` is the user who registered the device (N-72).
    """
    data: dict[str, Any] = {"action": action, **extra}
    if tag is not None:
        data["tag"] = tag
    hass.bus.async_fire(ACTION_EVENT, data, context=Context(user_id=user_id))
    await hass.async_block_till_done()


@dataclass
class FakeSpeakers:
    """Fake media players, Assist satellite and text-to-speech with recorded service calls."""

    play_media: list[ServiceCall]
    tts_speak: list[ServiceCall]
    announce: list[ServiceCall]
    volume_set: list[ServiceCall]
    announce_player: str = "media_player.kitchen"
    plain_player: str = "media_player.office"
    satellite: str = "assist_satellite.hall"
    tts_entity: str = "tts.fake"


def add_fake_speakers(hass: HomeAssistant) -> FakeSpeakers:
    """Fake players (with and without announce), a satellite and tts (N-65, N-66)."""
    base = MediaPlayerEntityFeature.PLAY_MEDIA | MediaPlayerEntityFeature.VOLUME_SET
    hass.states.async_set(
        "media_player.kitchen",
        "idle",
        {"supported_features": int(base | MediaPlayerEntityFeature.MEDIA_ANNOUNCE)},
    )
    hass.states.async_set("media_player.office", "idle", {"supported_features": int(base)})
    hass.states.async_set("assist_satellite.hall", "idle", {"supported_features": 1})
    hass.states.async_set("tts.fake", "unknown", {})
    return FakeSpeakers(
        play_media=async_mock_service(hass, "media_player", "play_media"),
        tts_speak=async_mock_service(hass, "tts", "speak"),
        announce=async_mock_service(hass, "assist_satellite", "announce"),
        volume_set=async_mock_service(hass, "media_player", "volume_set"),
    )


@dataclass
class PersistentCapture:
    """Recorded persistent notification service calls (N-67)."""

    create: list[ServiceCall]
    dismiss: list[ServiceCall]


def capture_persistent(hass: HomeAssistant) -> PersistentCapture:
    """Record `persistent_notification.create` and `dismiss` instead of running them."""
    return PersistentCapture(
        create=async_mock_service(hass, "persistent_notification", "create"),
        dismiss=async_mock_service(hass, "persistent_notification", "dismiss"),
    )


async def tick(hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float) -> None:
    """Move time forward and let timers fire (same pattern as `tests/test_snooze.py`)."""
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
