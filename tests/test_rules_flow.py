"""Rule subentry flow: add, validation, reconfigure (DESIGN §17.3)."""

from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .test_rules import WINDOW


async def start(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "user"
    return str(result["flow_id"])


async def test_add_rule_with_defaults(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(WINDOW, "off")
    flow_id = await start(hass, entry)
    result = await hass.config_entries.subentries.async_configure(
        flow_id, {"name": "Window", "entity_id": WINDOW, "message": "Window open"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (subentry,) = entry.subentries.values()
    assert subentry.subentry_type == "rule" and subentry.title == "Window"
    assert dict(subentry.data) == {
        "entity_id": WINDOW,
        "operator": "equals",
        "state": ["on"],
        "message": "Window open",
        "severity": "warning",
        "people": [],
        "dismissible": False,
        "enabled": True,
    }


async def test_add_rule_with_all_fields(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(WINDOW, "off")
    hass.states.async_set("person.a", "home")
    flow_id = await start(hass, entry)
    given: dict[str, Any] = {
        "name": "Window",
        "entity_id": WINDOW,
        "operator": "not_equals",
        "state": ["on", "tilted"],
        "attribute": "position",
        "message": "{name} open",
        "title": "Heads up",
        "severity": "critical",
        "icon": "mdi:window-open",
        "people": ["person.a"],
        "dismissible": True,
        "enabled": False,
    }
    result = await hass.config_entries.subentries.async_configure(flow_id, given)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (subentry,) = entry.subentries.values()
    assert dict(subentry.data) == {k: v for k, v in given.items() if k != "name"}


async def test_unknown_entity_is_an_error(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    flow_id = await start(hass, entry)
    result = await hass.config_entries.subentries.async_configure(
        flow_id, {"name": "Window", "entity_id": WINDOW, "message": "x"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"entity_id": "entity_not_found"}
    assert not entry.subentries


async def test_blank_message_is_an_error(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(WINDOW, "off")
    flow_id = await start(hass, entry)
    result = await hass.config_entries.subentries.async_configure(
        flow_id, {"name": "Window", "entity_id": WINDOW, "message": "   "}
    )
    assert result["errors"] == {"message": "message_required"}


async def test_empty_state_list_falls_back_to_on(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    flow_id = await start(hass, entry)
    await hass.config_entries.subentries.async_configure(
        flow_id, {"name": "W", "entity_id": WINDOW, "message": "x", "state": []}
    )
    (subentry,) = entry.subentries.values()
    assert subentry.data["state"] == ["on"]


async def test_two_rules_may_watch_the_same_entity(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    for name in ("One", "Two"):
        flow_id = await start(hass, entry)
        result = await hass.config_entries.subentries.async_configure(
            flow_id, {"name": name, "entity_id": WINDOW, "message": name}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
    assert len(entry.subentries) == 2


async def test_reconfigure_changes_data_and_title(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "on")
    flow_id = await start(hass, entry)
    await hass.config_entries.subentries.async_configure(
        flow_id, {"name": "Old", "entity_id": WINDOW, "message": "old"}
    )
    (subentry,) = entry.subentries.values()

    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"),
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "subentry_id": subentry.subentry_id,
        },
    )
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "reconfigure"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"name": "New", "entity_id": WINDOW, "message": "new", "severity": "info"},
    )
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "reconfigure_successful"
    assert subentry.title == "New"
    assert subentry.data["message"] == "new" and subentry.data["severity"] == "info"
