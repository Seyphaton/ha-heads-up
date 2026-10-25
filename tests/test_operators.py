"""Condition operators: matcher, action schema, stored banners, rules (DESIGN §18, D-060, D-061)."""

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
from .test_rules import WINDOW, add_rule, set_state, shown

SENSOR_ENTITY = "sensor.temperature"


@pytest.mark.parametrize(
    ("operator", "wanted", "value", "expected"),
    [
        (None, ["on"], "on", True),
        ("equals", ["on", "tilted"], "tilted", True),
        ("equals", ["on"], "off", False),
        ("not_equals", ["on"], "off", True),
        ("not_equals", ["on"], "on", False),
        ("not_equals", ["on", "idle"], "idle", False),
        ("not_equals", ["on", "idle"], "off", True),
        ("above", ["25"], "25.1", True),
        ("above", ["25"], "25", False),
        ("below", ["25"], "24.9", True),
        ("below", ["25"], "25", False),
        ("between", ["10", "20"], "10", True),
        ("between", ["10", "20"], "20", True),
        ("between", ["10", "20"], "20.1", False),
        ("between", ["10", "20"], "9.9", False),
        ("contains", ["err", "fail"], "disk failure", True),
        ("contains", ["err"], "ok", False),
        ("not_contains", ["err", "fail"], "ok", True),
        ("not_contains", ["err", "fail"], "an error", False),
        ("above", ["25"], "warm", None),
        ("between", ["10", "20"], None, None),
        ("not_equals", ["on"], None, None),
        ("contains", ["x"], None, None),
        ("equals", ["on"], None, False),
    ],
)
def test_matches(operator: str | None, wanted: list[str], value: str | None, expected: Any) -> None:
    condition: dict[str, Any] = {"entity_id": "x.y", "state": wanted}
    if operator:
        condition["operator"] = operator
    assert matches(condition, value) is expected


@pytest.mark.parametrize(
    ("operator", "states", "error"),
    [
        ("equals", ["on"], None),
        ("not_equals", ["a", "b"], None),
        ("contains", ["a"], None),
        ("above", ["1.5"], None),
        ("below", ["-3"], None),
        ("between", ["1", "2"], None),
        ("above", ["1", "2"], "state_count"),
        ("below", [], "state_count"),
        ("between", ["1"], "state_count"),
        ("between", ["1", "2", "3"], "state_count"),
        ("above", ["warm"], "state_not_numeric"),
        ("between", ["1", "x"], "state_not_numeric"),
        ("above", ["nan"], "state_not_numeric"),
    ],
)
def test_check_state(operator: str, states: list[str], error: str | None) -> None:
    assert check_state(operator, states) == error


def test_schema_keeps_old_conditions_unchanged() -> None:
    assert CONDITION_SCHEMA({"entity_id": WINDOW}) == {"entity_id": WINDOW, "state": "on"}


def test_schema_accepts_operator() -> None:
    assert CONDITION_SCHEMA({"entity_id": WINDOW, "operator": "not_equals", "state": "on"}) == {
        "entity_id": WINDOW,
        "operator": "not_equals",
        "state": "on",
    }
    assert CONDITION_SCHEMA(
        {"entity_id": SENSOR_ENTITY, "operator": "between", "state": [10, 20.5]}
    )["state"] == ["10", "20.5"]


def test_schema_defaults_state_only_for_equality_operators() -> None:
    assert CONDITION_SCHEMA({"entity_id": WINDOW, "operator": "not_equals"})["state"] == "on"
    for operator in ("above", "below", "between", "contains", "not_contains"):
        with pytest.raises(vol.Invalid):
            CONDITION_SCHEMA({"entity_id": WINDOW, "operator": operator})


def test_schema_rejects_unknown_operator() -> None:
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA({"entity_id": WINDOW, "operator": "regex", "state": "x"})


def test_schema_rejects_bad_state_for_numeric_operator() -> None:
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA({"entity_id": WINDOW, "operator": "above", "state": "warm"})
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA({"entity_id": WINDOW, "operator": "between", "state": ["1"]})


async def test_stored_banner_with_not_equals(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "off")
    await create(
        id="w",
        message="x",
        mode="recurring",
        condition={"entity_id": WINDOW, "operator": "not_equals", "state": "on"},
    )
    assert entry.runtime_data.is_active(banners(entry)["w"])
    await set_state(hass, "on")
    assert not entry.runtime_data.is_active(banners(entry)["w"])
    await set_state(hass, "off")
    assert entry.runtime_data.is_active(banners(entry)["w"])


async def test_not_equals_ignores_unavailable(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    assert (
        await create(
            id="w",
            message="x",
            condition={"entity_id": WINDOW, "operator": "not_equals", "state": "on"},
        )
    )["status"] == "waiting"
    await set_state(hass, "unavailable")
    assert not entry.runtime_data.is_active(banners(entry)["w"])
    await set_state(hass, "unknown")
    assert not entry.runtime_data.is_active(banners(entry)["w"])


async def test_stored_banner_with_above(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(SENSOR_ENTITY, "20")
    await create(
        id="t",
        message="x",
        mode="recurring",
        condition={"entity_id": SENSOR_ENTITY, "operator": "above", "state": 25},
    )
    assert not entry.runtime_data.is_active(banners(entry)["t"])
    hass.states.async_set(SENSOR_ENTITY, "26.5")
    await hass.async_block_till_done()
    assert entry.runtime_data.is_active(banners(entry)["t"])
    hass.states.async_set(SENSOR_ENTITY, "warm")
    await hass.async_block_till_done()
    assert entry.runtime_data.is_active(banners(entry)["t"])  # not a number: unchanged


async def test_rule_with_not_equals(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "off")
    add_rule(hass, entry, operator="not_equals", state=["on"])
    await hass.async_block_till_done()
    assert len(shown(entry)) == 1
    await set_state(hass, "on")
    assert shown(entry) == []
    await set_state(hass, "unavailable")
    assert shown(entry) == []


async def test_rule_with_between_on_attribute(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(WINDOW, "on", {"position": 50})
    add_rule(hass, entry, operator="between", state=["40", "60"], attribute="position")
    await hass.async_block_till_done()
    assert len(shown(entry)) == 1
    hass.states.async_set(WINDOW, "on", {"position": 70})
    await hass.async_block_till_done()
    assert shown(entry) == []
    hass.states.async_set(WINDOW, "on", {})
    await hass.async_block_till_done()
    assert shown(entry) == []


async def test_old_rule_without_operator_still_equals(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry)  # no "operator" key, as saved by Phase 8
    await hass.async_block_till_done()
    assert len(shown(entry)) == 1


async def start(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    return str(result["flow_id"])


async def test_flow_stores_operator(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hass.states.async_set(SENSOR_ENTITY, "20")
    result = await hass.config_entries.subentries.async_configure(
        await start(hass, entry),
        {
            "name": "Hot",
            "entity_id": SENSOR_ENTITY,
            "operator": "above",
            "state": ["25"],
            "message": "{name} is high",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (subentry,) = entry.subentries.values()
    assert subentry.data["operator"] == "above" and subentry.data["state"] == ["25"]


async def test_flow_operator_defaults_to_equals(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    await hass.config_entries.subentries.async_configure(
        await start(hass, entry), {"name": "W", "entity_id": WINDOW, "message": "open"}
    )
    (subentry,) = entry.subentries.values()
    assert subentry.data["operator"] == "equals" and subentry.data["state"] == ["on"]


@pytest.mark.parametrize(
    ("operator", "state", "error"),
    [
        ("above", ["1", "2"], "state_count"),
        ("between", ["1"], "state_count"),
        ("below", ["warm"], "state_not_numeric"),
        ("contains", [], "state_required"),
    ],
)
async def test_flow_rejects_bad_state_for_operator(
    hass: HomeAssistant, entry: MockConfigEntry, operator: str, state: list[str], error: str
) -> None:
    hass.states.async_set(WINDOW, "off")
    result = await hass.config_entries.subentries.async_configure(
        await start(hass, entry),
        {
            "name": "W",
            "entity_id": WINDOW,
            "operator": operator,
            "state": state,
            "message": "x",
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"state": error}
    assert not entry.subentries
