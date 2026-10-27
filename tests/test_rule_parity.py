"""Rules offer what actions offer: buttons, tap action, dismiss scope, templates (§22)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.manager import HeadsUpError

from .test_rules import USER, WINDOW, add_rule, rule_id, set_state, shown

BUTTONS = [
    {"key": "ack", "label": "Got it", "dismiss": True},
    {"key": "later", "label": "Later", "action": {"action": "navigate", "navigation_path": "/x"}},
]


def payload(entry: MockConfigEntry, banner_id: str) -> dict[str, Any]:
    return next(b for b in entry.runtime_data.visible(USER) if b["id"] == banner_id)


async def test_rule_banner_carries_buttons_and_tap_action(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    tap = {"action": "navigate", "navigation_path": "/rooms"}
    sub = add_rule(hass, entry, dismissible=True, actions=BUTTONS, tap_action=tap)
    await hass.async_block_till_done()
    item = payload(entry, rule_id(sub))
    assert [b["key"] for b in item["actions"]] == ["ack", "later"]
    assert item["tap_action"] == tap


async def test_rule_button_fires_the_event_and_can_dismiss(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    sub = add_rule(hass, entry, dismissible=True, actions=BUTTONS)
    await hass.async_block_till_done()
    events = async_capture_events(hass, f"{DOMAIN}_banner_action")
    manager = entry.runtime_data
    manager.press(rule_id(sub), USER, "later")
    assert shown(entry) == [rule_id(sub)]
    manager.press(rule_id(sub), USER, "ack")
    await hass.async_block_till_done()
    assert [e.data["key"] for e in events] == ["later", "ack"]
    assert events[0].data["id"] == rule_id(sub) and events[0].data["tag"] == "rule"
    assert shown(entry) == []


async def test_rule_without_buttons_rejects_a_press(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    sub = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    try:
        entry.runtime_data.press(rule_id(sub), USER, "ack")
    except HeadsUpError as err:
        assert err.code == "unknown_action"
    else:
        raise AssertionError("expected unknown_action")


async def test_global_dismiss_of_a_rule_hides_it_for_everyone_until_the_condition_flips(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    sub = add_rule(hass, entry, dismissible=True, dismiss_scope="global")
    await hass.async_block_till_done()
    events = async_capture_events(hass, f"{DOMAIN}_banner_dismissed")
    entry.runtime_data.dismiss(rule_id(sub), USER)
    await hass.async_block_till_done()
    assert shown(entry, USER) == [] and shown(entry, "someone-else") == []
    assert events[0].data["scope"] == "global"
    assert rule_id(sub) in entry.runtime_data.rules  # a rule banner is never removed

    await set_state(hass, "off")
    await set_state(hass, "on")
    assert shown(entry, "someone-else") == [rule_id(sub)]


async def test_rule_without_dismiss_scope_stays_per_user(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(entry, options={"default_dismiss_scope": "global"})
    await set_state(hass, "on")
    sub = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    entry.runtime_data.dismiss(rule_id(sub), USER)
    assert shown(entry, "someone-else") == [rule_id(sub)]


async def test_template_rule_follows_the_template(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("sensor.a", "5")
    hass.states.async_set("sensor.b", "5")
    sub = add_rule(
        hass,
        entry,
        entity_id=None,
        template="{{ states('sensor.a') | int > states('sensor.b') | int }}",
        message="{name}: a is above b",
    )
    entry.runtime_data.sync_rules(entry.subentries)
    await hass.async_block_till_done()
    assert shown(entry) == []

    hass.states.async_set("sensor.a", "9")
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(sub)]
    assert payload(entry, rule_id(sub))["message"] == "Rule: a is above b"  # rule name for {name}

    hass.states.async_set("sensor.b", "10")
    await hass.async_block_till_done()
    assert shown(entry) == []


async def test_template_rule_honours_for(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.states.async_set("sensor.a", "9")
    sub = add_rule(
        hass, entry, entity_id=None, template="{{ states('sensor.a') | int > 5 }}", **{"for": 60}
    )
    entry.runtime_data.sync_rules(entry.subentries)
    await hass.async_block_till_done()
    assert shown(entry) == []

    freezer.tick(61)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(sub)]


async def test_deleting_a_template_rule_stops_its_tracking(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("sensor.a", "9")
    sub = add_rule(hass, entry, entity_id=None, template="{{ states('sensor.a') | int > 5 }}")
    entry.runtime_data.sync_rules(entry.subentries)
    await hass.async_block_till_done()
    assert rule_id(sub) in entry.runtime_data._template_trackers

    hass.config_entries.async_remove_subentry(entry, sub.subentry_id)
    await hass.async_block_till_done()
    assert entry.runtime_data._template_trackers == {}
    assert WINDOW not in entry.runtime_data.tracked_entities
