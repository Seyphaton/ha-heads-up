"""Button presses come back as events and act for the right user (D-092, D-110, N-72, N-79)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import FakeDevice, fire_app_action, set_person, settle


async def notify(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> None:
    body = {
        "id": "m",
        "message": "Window open",
        "channels": ["banner", "push"],
        "to": {"push": {"recipients": ["person.anna"]}},
        "snoozable": True,
        "snooze_options": [{"minutes": 10}, {"hours": 1}],
        "actions": [{"key": "seen", "label": "Seen"}],
        **data,
    }
    await hass.services.async_call(DOMAIN, "notify", body, blocking=True)
    await settle(hass, entry)


def last_trace(entry: MockConfigEntry) -> dict[str, Any]:
    return dict(entry.runtime_data.hub.trace.entries("m")[0])


async def press(hass: HomeAssistant, entry: MockConfigEntry, action: str, **kw: Any) -> None:
    await fire_app_action(hass, action, **kw)
    await settle(hass, entry)


@pytest.fixture
async def anna(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> FakeDevice:
    """Anna's phone, with the message `m` already pushed to it."""
    set_person(hass, "person.anna", "home", user_id="anna-id")
    phone = await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )
    await notify(hass, entry)
    return phone


async def test_dismiss_hides_the_banner_for_the_person_and_clears_the_push(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:dismiss", user_id="anna-id")
    assert "anna-id" in entry.runtime_data.banners["m"].dismissed_by
    assert anna.calls[-1].data["message"] == "clear_notification"
    assert last_trace(entry)["reason"] == "ok"


async def test_snooze_uses_the_first_snooze_option(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:snooze", user_id="anna-id")
    until = entry.runtime_data.banners["m"].snoozed_until["anna-id"]
    assert (until - entry.runtime_data.banners["m"].updated_at).total_seconds() == pytest.approx(
        600, abs=5
    )


async def test_an_own_button_fires_the_banner_action_event(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    events = async_capture_events(hass, "heads_up_banner_action")
    await press(hass, entry, "hu:m:person.anna:b-seen", user_id="anna-id")
    assert events[0].data["key"] == "seen" and events[0].data["user_id"] == "anna-id"


async def test_the_person_decides_when_the_event_has_no_user(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:dismiss")
    assert "anna-id" in entry.runtime_data.banners["m"].dismissed_by


async def test_a_different_user_on_the_event_ignores_the_press(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:dismiss", user_id="someone-else")
    assert entry.runtime_data.banners["m"].dismissed_by == []
    assert last_trace(entry)["reason"] == "user_mismatch"


async def test_a_press_for_a_message_that_no_longer_exists_is_stale(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await hass.services.async_call(DOMAIN, "clear", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    await press(hass, entry, "hu:m:person.anna:dismiss", user_id="anna-id")
    assert entry.runtime_data.hub.trace.entries("m")[0]["reason"] == "stale_message"


async def test_a_press_naming_someone_who_was_not_notified_is_ignored(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    set_person(hass, "person.ben", "home", user_id="ben-id")
    await press(hass, entry, "hu:m:person.ben:dismiss", user_id="ben-id")
    assert entry.runtime_data.banners["m"].dismissed_by == []
    assert last_trace(entry)["reason"] == "unknown_recipient"


async def test_actions_that_are_not_ours_are_ignored(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    before = len(entry.runtime_data.hub.trace)
    await press(hass, entry, "something_else", user_id="anna-id")
    await press(hass, entry, "hu:onlytwo", user_id="anna-id")
    assert len(entry.runtime_data.hub.trace) == before


async def test_the_tag_in_the_event_is_not_trusted(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:dismiss", user_id="anna-id", tag="hu-zzzz-other")
    assert "anna-id" in entry.runtime_data.banners["m"].dismissed_by


async def test_an_unknown_action_word_is_traced(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:explode", user_id="anna-id")
    assert last_trace(entry)["reason"] == "unknown_action"


async def test_acknowledge_waits_for_the_policy_package(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await press(hass, entry, "hu:m:person.anna:ack", user_id="anna-id")
    assert last_trace(entry)["reason"] == "acknowledge_unavailable"


async def test_a_device_without_a_person_uses_the_registering_user(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    spare = await mobile_app_device("Spare phone", user_id="spare-id")
    await notify(hass, entry, to={"push": {"recipients": [spare.device_id]}})
    await press(hass, entry, f"hu:m:device:{spare.device_id}:dismiss", user_id="spare-id")
    assert "spare-id" in entry.runtime_data.banners["m"].dismissed_by


async def test_the_listener_is_removed_on_unload(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await notify(hass, entry)
    banner = entry.runtime_data.banners["m"]
    assert await hass.config_entries.async_unload(entry.entry_id)
    await fire_app_action(hass, "hu:m:person.anna:dismiss", user_id="anna-id")
    assert banner.dismissed_by == []
