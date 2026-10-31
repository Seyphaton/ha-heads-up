"""Acknowledgement state, the push button, the usage lookup and rule parity (D-081, D-111)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import fire_app_action, settle
from .policy_support import ESCALATION, REMINDER, add_policy, make_household, pushes, send, wait


def buttons(call: Any) -> list[str]:
    return [a["action"].rsplit(":", 1)[-1] for a in call.data["data"].get("actions", [])]


async def test_the_push_has_an_acknowledge_button_only_when_a_policy_applies(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, id="plain")
    assert "ack" not in buttons(pushes(home.anna)[0])
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, id="nagged")
    assert "ack" in buttons(pushes(home.anna)[1])


async def test_pressing_acknowledge_on_the_push_stops_the_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await fire_app_action(hass, "hu:m:person.anna:ack", user_id="anna-id")
    await settle(hass, entry)
    assert entry.runtime_data.banners["m"].acknowledged_by == ["anna-id"]
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)


async def test_acknowledging_keeps_the_banner_for_everyone(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    assert [b["id"] for b in entry.runtime_data.visible("ben-id")] == ["m"]


async def test_acknowledging_twice_changes_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    entry.runtime_data.acknowledge("m", "anna-id")
    assert entry.runtime_data.banners["m"].acknowledged_by == ["anna-id"]


async def test_acknowledging_an_unknown_message_is_an_error(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/acknowledge", "banner_id": "nope"})
    reply = await client.receive_json()
    assert not reply["success"] and reply["error"]["code"] == "not_found"


async def test_a_rule_message_gets_the_policies_for_the_tag_rule(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Rules", **ESCALATION, tags=["rule"])
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert len(pushes(home.ben)) == 1


async def test_a_rule_message_acknowledgement_resets_when_the_condition_flips(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    (rule_id,) = entry.runtime_data.rules
    entry.runtime_data.acknowledge(rule_id, "anna-id")
    hass.states.async_set(WINDOW, "off")
    await settle(hass, entry)
    assert entry.runtime_data.rules[rule_id].acknowledged_by == []


async def test_the_usage_lookup_lists_policies_naming_an_audience_or_group(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    uses_audience = {**ESCALATION, "targets": {"push": {"audience": "Admins"}}}
    uses_group = {
        **ESCALATION,
        "after_minutes": 9,
        "targets": {"speak": {"recipients": ["Hall (group)"]}},
    }
    await add_policy(hass, entry, "By audience", **uses_audience)
    await add_policy(hass, entry, "By group", **uses_group)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/hub_usage", "name": "Admins"})
    assert (await client.receive_json())["result"] == {"policies": ["By audience"]}
    await client.send_json_auto_id({"type": "heads_up/hub_usage", "name": "Hall"})
    assert (await client.receive_json())["result"] == {"policies": ["By group"]}


async def test_the_usage_lookup_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "heads_up/hub_usage", "name": "Admins"})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"
