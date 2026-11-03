"""A message's own buttons stop acting once the message has ended (disable_ended_buttons)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.manager import HeadsUpError

from .conftest import CreateBanner
from .test_rules import USER, add_rule, rule_id, set_state

BUTTONS = [{"key": "later", "label": "Later"}]
CONDITION = {"entity_id": "binary_sensor.d", "state": "on"}


def press(entry: MockConfigEntry, banner_id: str, user_id: str) -> str | None:
    """The error code of a press, or None when it was accepted."""
    try:
        entry.runtime_data.press(banner_id, user_id, "later")
    except HeadsUpError as err:
        return err.code
    return None


async def test_a_press_before_the_message_ended_is_accepted(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    assert press(entry, "a", hass_admin_user.id) is None


async def test_a_press_after_dismissal_by_the_user_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    entry.runtime_data.dismiss("a", hass_admin_user.id)
    events = async_capture_events(hass, f"{DOMAIN}_banner_action")
    assert press(entry, "a", hass_admin_user.id) == "message_ended"
    await hass.async_block_till_done()
    assert events == []


async def test_dismissal_by_another_user_does_not_end_it_for_this_one(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    entry.runtime_data.dismiss("a", "someone-else")
    assert press(entry, "a", hass_admin_user.id) is None


async def test_a_press_after_acknowledgement_by_anyone_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    entry.runtime_data.acknowledge("a", "someone-else")
    assert press(entry, "a", hass_admin_user.id) == "message_ended"


async def test_a_press_while_the_condition_is_false_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    hass.states.async_set("binary_sensor.d", "on")
    await create(id="a", message="x", actions=BUTTONS, condition=CONDITION, mode="recurring")
    assert press(entry, "a", hass_admin_user.id) is None
    hass.states.async_set("binary_sensor.d", "off")
    await hass.async_block_till_done()
    assert press(entry, "a", hass_admin_user.id) == "message_ended"


async def test_a_snooze_does_not_end_it(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS, snoozable=True)
    entry.runtime_data.snooze("a", hass_admin_user.id, 900)
    assert press(entry, "a", hass_admin_user.id) is None


async def test_the_websocket_reports_the_error_code(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    entry.runtime_data.acknowledge("a", hass_admin_user.id)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/action", "banner_id": "a", "key": "later"})
    assert (await client.receive_json())["error"]["code"] == "message_ended"


async def test_a_rule_banner_follows_the_same_check(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    sub = add_rule(hass, entry, dismissible=True, actions=BUTTONS)
    await hass.async_block_till_done()
    assert press(entry, rule_id(sub), USER) is None
    entry.runtime_data.acknowledge(rule_id(sub), USER)
    assert press(entry, rule_id(sub), USER) == "message_ended"


@pytest.mark.parametrize("options", [{"disable_ended_buttons": False}])
async def test_with_the_setting_off_a_press_after_the_end_is_accepted(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_admin_user: Any
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    entry.runtime_data.dismiss("a", hass_admin_user.id)
    entry.runtime_data.acknowledge("a", hass_admin_user.id)
    events = async_capture_events(hass, f"{DOMAIN}_banner_action")
    assert press(entry, "a", hass_admin_user.id) is None
    await hass.async_block_till_done()
    assert len(events) == 1
