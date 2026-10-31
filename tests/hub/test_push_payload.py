"""Payload of a Companion notification: tag, level, buttons, lock screen (DESIGN §23.8, N-62)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import FakeDevice, set_person, settle


async def push(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> dict[str, Any]:
    body = {
        "id": "m",
        "message": "Window open",
        "channels": ["push"],
        "to": {"push": {"recipients": ["person.anna"]}},
        **data,
    }
    response = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert response is not None
    return dict(response)


def sent(device: FakeDevice) -> dict[str, Any]:
    assert device.calls, "nothing was sent"
    return dict(device.calls[-1].data)


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def test_a_push_has_title_message_and_one_tag_per_message(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, title="Window")
    data = sent(anna)
    token = entry.options["install_token"]
    assert (data["title"], data["message"]) == ("Window", "Window open")
    assert data["data"]["tag"] == f"hu-{token}-m"
    assert data["data"]["group"] == f"hu-{token}"


async def test_a_message_without_a_title_sends_none(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry)
    assert "title" not in sent(anna)


@pytest.mark.parametrize(
    ("severity", "level", "importance"),
    [
        ("success", "passive", "low"),
        ("info", "passive", "low"),
        ("warning", "normal", "default"),
        ("critical", "time-sensitive", "high"),
    ],
)
async def test_severity_sets_level_importance_and_android_channel(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    anna: FakeDevice,
    severity: str,
    level: str,
    importance: str,
) -> None:
    await push(hass, entry, severity=severity)
    data = sent(anna)["data"]
    assert data["push"] == {"interruption-level": level}
    assert data["importance"] == importance
    assert data["channel"] == f"heads_up_{level.replace('-', '_')}"


async def test_ios_critical_is_an_opt_in_and_android_gets_time_sensitive(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, mobile_app_device: AddDevice
) -> None:
    entry.runtime_data.options["push_levels"] = {
        "success": "passive",
        "info": "passive",
        "warning": "normal",
        "critical": "critical",
    }
    await push(hass, entry, severity="critical")
    # The fake registration is an iOS device (helpers.py).
    data = sent(anna)["data"]
    assert data["push"]["interruption-level"] == "critical"
    assert data["push"]["sound"] == {"name": "default", "critical": 1, "volume": 1.0}
    android = await mobile_app_device(
        "Anna's tablet", user_id="anna-id", person_entity_id="person.anna"
    )
    hass.config_entries.async_update_entry(
        android.entry, data={**android.entry.data, "os_name": "Android"}
    )
    await push(hass, entry, id="n", severity="critical")
    assert sent(android)["data"]["push"] == {"interruption-level": "time-sensitive"}


@pytest.mark.parametrize(
    ("mode", "title", "message"),
    [
        ("full", "Window", "Window open"),
        ("title_only", "Window", "Open Home Assistant to read this message."),
        ("generic", "Heads Up", "New message"),
    ],
)
async def test_lock_screen_text_follows_the_setting(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    anna: FakeDevice,
    mode: str,
    title: str,
    message: str,
) -> None:
    entry.runtime_data.options["push_lockscreen"] = mode
    await push(hass, entry, title="Window")
    data = sent(anna)
    assert (data["title"], data["message"]) == (title, message)


async def test_generated_texts_follow_the_home_assistant_language(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.config.language = "de"
    entry.runtime_data.options["push_lockscreen"] = "generic"
    await push(hass, entry)
    assert sent(anna)["message"] == "Neue Nachricht"


async def test_sticky_and_click_action(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_sticky"] = True
    await push(hass, entry, tap_action={"action": "navigate", "navigation_path": "/lovelace/0"})
    data = sent(anna)["data"]
    assert data["sticky"] == "true"
    assert data["clickAction"] == "/lovelace/0"


async def test_a_tap_action_without_a_path_adds_no_click_action(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, tap_action={"action": "more-info"})
    assert "clickAction" not in sent(anna)["data"]


async def test_buttons_are_own_first_then_snooze_and_dismiss_with_ids(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(
        hass,
        entry,
        snoozable=True,
        actions=[{"key": "ack", "label": "Got it"}],
    )
    actions = sent(anna)["data"]["actions"]
    assert actions == [
        {"action": "hu:m:person.anna:b-ack", "title": "Got it"},
        {"action": "hu:m:person.anna:snooze", "title": "Snooze"},
        {"action": "hu:m:person.anna:dismiss", "title": "Dismiss"},
    ]


async def test_no_dismiss_or_snooze_button_when_the_message_is_not_dismissible(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, dismissible=False)
    assert "actions" not in sent(anna)["data"]


async def test_android_buttons_are_clipped_to_three_and_the_trace_says_so(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    phone = await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )
    hass.config_entries.async_update_entry(
        phone.entry, data={**phone.entry.data, "os_name": "Android"}
    )
    await push(
        hass,
        entry,
        snoozable=True,
        actions=[{"key": "one", "label": "1"}, {"key": "two", "label": "2"}],
    )
    assert len(sent(phone)["data"]["actions"]) == 3
    newest = entry.runtime_data.hub.trace.entries("m")[0]
    assert newest["reason"] == "buttons_clipped:1"


async def test_ios_takes_more_buttons(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(
        hass,
        entry,
        snoozable=True,
        actions=[{"key": "one", "label": "1"}, {"key": "two", "label": "2"}],
    )
    assert len(sent(anna)["data"]["actions"]) == 4
