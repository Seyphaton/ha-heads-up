"""A manual policy applies only when a call names it (D-146)."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .policy_support import ESCALATION, add_policy, make_household, send


async def test_a_manual_policy_is_not_attached_to_a_matching_message(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    await send(hass, entry, severity="critical")
    assert entry.runtime_data.hub.policies.for_message(entry.runtime_data.banners["m"]) == []


async def test_a_manual_policy_is_attached_when_the_call_names_it(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    await send(hass, entry, severity="warning", policy="By hand")
    used = entry.runtime_data.hub.policies.for_message(entry.runtime_data.banners["m"])
    assert [p.name for p in used] == ["By hand"]
    assert entry.runtime_data.hub.ack_applies(entry.runtime_data.banners["m"]) is True


async def test_the_preview_lists_a_manual_policy_only_when_it_is_named(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    hub = entry.runtime_data.hub
    from custom_components.heads_up.hub.panel_test import build

    base = {"message": "x", "channels": ["banner"], "severity": "critical"}
    assert (await hub.preview(await build(hub, base)))["policies"] == []
    named = await hub.preview(
        await build(hub, {**base, "policy": "switch.heads_up_policy_by_hand"})
    )
    assert [p["name"] for p in named["policies"]] == ["By hand"]


async def test_a_watch_rule_can_name_a_manual_policy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    from ..test_rules import WINDOW, add_rule, rule_id, set_state

    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    named = add_rule(hass, entry, policy="By hand")
    plain = add_rule(hass, entry, entity_id=WINDOW)
    await set_state(hass, "on")
    book = entry.runtime_data.hub.policies
    rules = entry.runtime_data.rules
    assert [p.name for p in book.for_message(rules[rule_id(named)])] == ["By hand"]
    assert book.for_message(rules[rule_id(plain)]) == []


async def test_setting_a_visible_rule_to_no_policy_drops_its_reminder(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    from ..test_rules import add_rule, rule_id, set_state
    from .policy_support import REMINDER

    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nudge", **REMINDER)
    sub = add_rule(hass, entry)
    await set_state(hass, "on")
    ledger = entry.runtime_data.hub.ledger
    assert ledger.timers(rule_id(sub))
    hass.config_entries.async_update_subentry(entry, sub, data={**sub.data, "policy": "none"})
    await hass.async_block_till_done()
    assert all(row.state.value != "planned" for row in ledger.timers(rule_id(sub)))
