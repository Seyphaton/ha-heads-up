"""`empty` and `not_empty` operators and the rule form's State field (DESIGN §20, D-068)."""

from typing import Any

import pytest
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.conditions import check_state, matches
from custom_components.heads_up.services import CONDITION_SCHEMA

from .conftest import CreateBanner, banners
from .test_operators import start
from .test_rules import WINDOW, add_rule, set_state, shown

TEXT = "input_text.note"


@pytest.mark.parametrize(
    ("operator", "value", "expected"),
    [
        ("not_empty", "hello", True),
        ("not_empty", "0", True),
        ("not_empty", "", False),
        ("not_empty", "   ", False),
        ("not_empty", None, False),
        ("empty", "", True),
        ("empty", "  \n", True),
        ("empty", None, True),
        ("empty", "hello", False),
    ],
)
def test_matches(operator: str, value: str | None, expected: bool) -> None:
    assert matches({"operator": operator}, value) is expected


def test_matches_ignores_a_state_value() -> None:
    assert matches({"operator": "not_empty", "state": ["on"]}, "off") is True


@pytest.mark.parametrize("operator", ["empty", "not_empty"])
def test_check_state_needs_no_value(operator: str) -> None:
    assert check_state(operator, []) is None
    assert check_state(operator, ["anything"]) is None


@pytest.mark.parametrize("operator", ["empty", "not_empty"])
def test_schema_accepts_the_operator_without_state(operator: str) -> None:
    result = CONDITION_SCHEMA({"entity_id": TEXT, "operator": operator})
    assert result == {"entity_id": TEXT, "operator": operator}


def test_schema_drops_a_state_given_with_the_operator() -> None:
    result = CONDITION_SCHEMA({"entity_id": TEXT, "operator": "not_empty", "state": "on"})
    assert "state" not in result


def test_schema_still_needs_a_state_for_other_operators() -> None:
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA({"entity_id": TEXT, "operator": "contains"})


# Action ----------------------------------------------------------------------------------


async def test_banner_shows_while_the_value_is_not_empty(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(TEXT, "")
    result = await create(
        id="note",
        message="Note set",
        mode="recurring",
        condition={"entity_id": TEXT, "operator": "not_empty"},
    )
    assert result["status"] == "waiting"
    assert shown(entry) == []

    hass.states.async_set(TEXT, "call back")
    await hass.async_block_till_done()
    assert shown(entry) == ["note"]

    hass.states.async_set(TEXT, "")
    await hass.async_block_till_done()
    assert shown(entry) == []


async def test_empty_operator_shows_while_the_value_is_empty(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(TEXT, "x")
    await create(
        id="blank",
        message="Note missing",
        mode="recurring",
        condition={"entity_id": TEXT, "operator": "empty"},
    )
    assert shown(entry) == []
    hass.states.async_set(TEXT, "")
    await hass.async_block_till_done()
    assert shown(entry) == ["blank"]


@pytest.mark.parametrize("operator", ["empty", "not_empty"])
async def test_unavailable_changes_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, operator: str
) -> None:
    hass.states.async_set(TEXT, "" if operator == "empty" else "x")
    await create(
        id="t", message="m", mode="recurring", condition={"entity_id": TEXT, "operator": operator}
    )
    assert shown(entry) == ["t"]
    hass.states.async_set(TEXT, "unavailable")
    await hass.async_block_till_done()
    assert shown(entry) == ["t"]
    assert banners(entry)["t"].condition_met is True


async def test_missing_attribute_counts_as_empty(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(TEXT, "on", {})
    await create(
        id="a",
        message="m",
        mode="recurring",
        condition={"entity_id": TEXT, "operator": "not_empty", "attribute": "reason"},
    )
    assert shown(entry) == []
    hass.states.async_set(TEXT, "on", {"reason": "rain"})
    await hass.async_block_till_done()
    assert shown(entry) == ["a"]
    hass.states.async_set(TEXT, "on", {"reason": []})
    await hass.async_block_till_done()
    assert shown(entry) == []  # an empty list is empty


async def test_empty_operator_with_for(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(TEXT, "x")
    result = await create(
        id="w",
        message="m",
        mode="recurring",
        condition={"entity_id": TEXT, "operator": "empty", "for": 60},
    )
    assert result["status"] == "waiting"


# Watch rules -----------------------------------------------------------------------------


async def test_rule_with_not_empty(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "")
    add_rule(hass, entry, operator="not_empty", state=[])
    await hass.async_block_till_done()
    assert shown(entry) == []
    await set_state(hass, "something")
    assert len(shown(entry)) == 1
    await set_state(hass, "")
    assert shown(entry) == []
    await set_state(hass, "unavailable")
    assert shown(entry) == []


async def test_rule_with_empty_on_an_attribute(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(WINDOW, "on", {"note": "x"})
    add_rule(hass, entry, operator="empty", state=[], attribute="note")
    await hass.async_block_till_done()
    assert shown(entry) == []
    hass.states.async_set(WINDOW, "on", {})
    await hass.async_block_till_done()
    assert len(shown(entry)) == 1


# Rule form -------------------------------------------------------------------------------


async def _submit(hass: HomeAssistant, entry: MockConfigEntry, **fields: Any) -> Any:
    hass.states.async_set(WINDOW, "off")
    return await hass.config_entries.subentries.async_configure(
        await start(hass, entry),
        {"name": "W", "entity_id": WINDOW, "message": "Open", **fields},
    )


@pytest.mark.parametrize("operator", ["empty", "not_empty"])
async def test_flow_stores_no_state_for_the_empty_operators(
    hass: HomeAssistant, entry: MockConfigEntry, operator: str
) -> None:
    result = await _submit(hass, entry, operator=operator)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (subentry,) = entry.subentries.values()
    assert subentry.data["operator"] == operator
    assert "state" not in subentry.data


async def test_flow_drops_a_state_entered_with_an_empty_operator(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await _submit(hass, entry, operator="not_empty", state=["on"])
    (subentry,) = entry.subentries.values()
    assert "state" not in subentry.data


async def test_flow_form_does_not_prefill_the_state(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    state_key = next(k for k in result["data_schema"].schema if k == "state")
    assert state_key.default is vol.UNDEFINED
    assert "suggested_value" not in (state_key.description or {})


async def test_flow_equals_without_a_state_still_means_on(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await _submit(hass, entry)
    (subentry,) = entry.subentries.values()
    assert subentry.data["state"] == ["on"]


async def test_reconfigure_from_equals_to_not_empty_removes_the_state(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "off")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"),
        context={"source": config_entries.SOURCE_RECONFIGURE, "subentry_id": subentry.subentry_id},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"name": "W", "entity_id": WINDOW, "operator": "not_empty", "message": "Open"},
    )
    assert result["type"] is FlowResultType.ABORT
    updated = entry.subentries[subentry.subentry_id]
    assert updated.data["operator"] == "not_empty" and "state" not in updated.data
