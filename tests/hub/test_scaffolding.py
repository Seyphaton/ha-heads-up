"""The fakes of the hub tests behave like the Home Assistant facts they stand for."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_capture_events

from .conftest import AddDevice, AddNotify
from .helpers import (
    ACTION_EVENT,
    FakeSpeakers,
    PersistentCapture,
    fire_app_action,
    notify_service_name,
    set_person,
    tick,
)


async def test_notify_service_name_follows_the_device_name() -> None:
    assert notify_service_name("Pixel 7") == "mobile_app_pixel_7"
    assert notify_service_name("Anna's phone") == "mobile_app_anna_s_phone"


async def test_fake_notify_records_calls(hass: HomeAssistant, fake_notify: AddNotify) -> None:
    calls = fake_notify("mobile_app_pixel_7")
    await hass.services.async_call(
        "notify",
        "mobile_app_pixel_7",
        {"message": "m", "data": {"tag": "t"}},
        blocking=True,
    )
    assert [c.data for c in calls] == [{"message": "m", "data": {"tag": "t"}}]


async def test_mobile_app_device_has_the_registration_shape(
    hass: HomeAssistant, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home", user_id="user-anna")
    device = await mobile_app_device(
        "Anna's phone", user_id="user-anna", person_entity_id="person.anna"
    )
    # N-71: person -> tracker entity -> registration -> notify service.
    person = hass.states.get("person.anna")
    assert person is not None
    assert person.attributes["device_trackers"] == [device.tracker_entity_id]
    assert person.attributes["user_id"] == "user-anna"
    tracker = er.async_get(hass).async_get(device.tracker_entity_id)
    assert tracker is not None
    assert tracker.platform == "mobile_app"
    assert tracker.unique_id == device.device_id
    registered = dr.async_get(hass).async_get(tracker.device_id or "")
    assert registered is not None
    assert ("mobile_app", device.device_id) in registered.identifiers
    assert device.entry.data["device_name"] == "Anna's phone"
    assert device.entry.data["user_id"] == "user-anna"
    assert device.notify_service == "mobile_app_anna_s_phone"
    assert hass.services.has_service("notify", device.notify_service)

    await hass.services.async_call(
        "notify", device.notify_service, {"message": "hi"}, blocking=True
    )
    assert len(device.calls) == 1


async def test_two_devices_of_one_person(hass: HomeAssistant, mobile_app_device: AddDevice) -> None:
    set_person(hass, "person.anna", "home")
    first = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    second = await mobile_app_device("Anna's tablet", person_entity_id="person.anna")
    person = hass.states.get("person.anna")
    assert person is not None
    assert person.attributes["device_trackers"] == [
        first.tracker_entity_id,
        second.tracker_entity_id,
    ]


async def test_set_person_states(hass: HomeAssistant) -> None:
    for state, expected in (
        ("home", "home"),
        ("not_home", "not_home"),
        ("work", "work"),
        ("unavailable", "unavailable"),
        (None, "unknown"),
    ):
        set_person(hass, "person.x", state)
        current = hass.states.get("person.x")
        assert current is not None
        assert current.state == expected


async def test_fire_app_action_carries_the_user(hass: HomeAssistant) -> None:
    events = async_capture_events(hass, ACTION_EVENT)
    await fire_app_action(hass, "hu:m1:anna:dismiss", tag="hu-abc-m1", user_id="user-anna")
    assert len(events) == 1
    assert events[0].data == {"action": "hu:m1:anna:dismiss", "tag": "hu-abc-m1"}
    assert events[0].context.user_id == "user-anna"


async def test_fake_speakers(hass: HomeAssistant, fake_speakers: FakeSpeakers) -> None:
    kitchen = hass.states.get(fake_speakers.announce_player)
    office = hass.states.get(fake_speakers.plain_player)
    assert kitchen is not None and office is not None
    announce = int(MediaPlayerEntityFeature.MEDIA_ANNOUNCE)
    assert int(kitchen.attributes["supported_features"]) & announce
    assert not int(office.attributes["supported_features"]) & announce
    await hass.services.async_call(
        "media_player",
        "play_media",
        {
            "entity_id": fake_speakers.announce_player,
            "media": {"media_content_id": "x", "media_content_type": "music"},
            "announce": True,
        },
        blocking=True,
    )
    await hass.services.async_call(
        "tts",
        "speak",
        {
            "entity_id": fake_speakers.tts_entity,
            "media_player_entity_id": fake_speakers.plain_player,
            "message": "hello",
        },
        blocking=True,
    )
    await hass.services.async_call(
        "assist_satellite",
        "announce",
        {"entity_id": fake_speakers.satellite, "message": "hello"},
        blocking=True,
    )
    assert len(fake_speakers.play_media) == 1
    assert len(fake_speakers.tts_speak) == 1
    assert len(fake_speakers.announce) == 1
    assert fake_speakers.volume_set == []


async def test_persistent_capture(
    hass: HomeAssistant, persistent_capture: PersistentCapture
) -> None:
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {"message": "m", "notification_id": "hu_m1"},
        blocking=True,
    )
    await hass.services.async_call(
        "persistent_notification", "dismiss", {"notification_id": "hu_m1"}, blocking=True
    )
    assert [c.data["notification_id"] for c in persistent_capture.create] == ["hu_m1"]
    assert [c.data["notification_id"] for c in persistent_capture.dismiss] == ["hu_m1"]


async def test_tick_fires_timers(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    fired: list[int] = []
    async_track_point_in_utc_time(
        hass, lambda _now: fired.append(1), dt_util.utcnow() + timedelta(seconds=60)
    )
    await tick(hass, freezer, 59)
    assert fired == []
    await tick(hass, freezer, 2)
    assert fired == [1]
