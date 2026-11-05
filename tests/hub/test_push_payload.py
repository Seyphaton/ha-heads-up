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


@pytest.fixture
async def android(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    phone = await mobile_app_device(
        "Anna's tablet", user_id="anna-id", person_entity_id="person.anna"
    )
    hass.config_entries.async_update_entry(
        phone.entry, data={**phone.entry.data, "os_name": "Android"}
    )
    return phone


CRITICAL_ON = {"success": "passive", "info": "passive", "warning": "normal", "critical": "critical"}


async def test_critical_is_an_alert_on_ios_and_an_alarm_on_android(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, android: FakeDevice
) -> None:
    entry.runtime_data.options["push_levels"] = CRITICAL_ON
    await push(hass, entry, severity="critical")
    # The fake registration of `anna` is an iOS device (helpers.py).
    ios = sent(anna)["data"]
    assert ios["push"]["interruption-level"] == "critical"
    assert ios["push"]["sound"] == {"name": "default", "critical": 1, "volume": 1.0}
    assert "priority" not in ios and "ttl" not in ios
    droid = sent(android)["data"]
    assert droid["channel"] == "alarm_stream"  # plays from the alarm stream, also when silent
    assert droid["importance"] == "max"
    assert droid["priority"] == "high" and droid["ttl"] == 0
    assert "sound" not in droid["push"]  # the iOS critical sound is not sent to Android


async def test_android_time_sensitive_is_delivered_at_once_on_its_own_channel(
    hass: HomeAssistant, entry: MockConfigEntry, android: FakeDevice
) -> None:
    await push(hass, entry, severity="critical")  # the default level of critical
    data = sent(android)["data"]
    assert data["channel"] == "heads_up_time_sensitive" and data["importance"] == "high"
    assert data["priority"] == "high" and data["ttl"] == 0


@pytest.mark.parametrize("severity", ["info", "warning"])
async def test_lower_levels_on_android_have_no_priority_and_no_ttl(
    hass: HomeAssistant, entry: MockConfigEntry, android: FakeDevice, severity: str
) -> None:
    await push(hass, entry, severity=severity)
    data = sent(android)["data"]
    assert "priority" not in data and "ttl" not in data
    assert data["channel"].startswith("heads_up_")


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
    titles = [a["title"] for a in sent(phone)["data"]["actions"]]
    assert titles == ["1", "2", "Dismiss"]  # Snooze goes first, the own buttons and Dismiss stay
    newest = entry.runtime_data.hub.trace.entries("m")[0]
    assert newest["reason"] == "buttons_clipped:1"


async def test_android_keeps_acknowledge_and_dismiss_before_the_own_buttons(
    hass: HomeAssistant, entry: MockConfigEntry, android: FakeDevice
) -> None:
    from .policy_support import ESCALATION, add_policy

    await add_policy(hass, entry, "Water", **ESCALATION)
    await push(
        hass,
        entry,
        snoozable=True,
        actions=[{"key": "one", "label": "1"}, {"key": "two", "label": "2"}],
    )
    titles = [a["title"] for a in sent(android)["data"]["actions"]]
    assert titles == ["1", "Acknowledge", "Dismiss"]  # in display order; 2 and Snooze are left out


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
