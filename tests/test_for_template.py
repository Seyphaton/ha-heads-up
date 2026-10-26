"""Condition `for` and template conditions (DESIGN §19, D-066, D-067)."""

from datetime import timedelta

import pytest
import voluptuous as vol
from freezegun.api import FrozenDateTimeFactory
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.heads_up.services import CONDITION_SCHEMA

from .conftest import CreateBanner, banners
from .test_rules import WINDOW, add_rule, rule_id, set_state, shown

OTHER = "sensor.other"


async def advance(hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float) -> None:
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


# Schema ----------------------------------------------------------------------------------


def test_schema_converts_for_to_seconds() -> None:
    result = CONDITION_SCHEMA({"entity_id": WINDOW, "for": {"minutes": 5}})
    assert result["for"] == 300


def test_schema_accepts_for_as_text_and_seconds() -> None:
    assert CONDITION_SCHEMA({"entity_id": WINDOW, "for": "00:01:30"})["for"] == 90
    assert CONDITION_SCHEMA({"entity_id": WINDOW, "for": 45})["for"] == 45


def test_schema_drops_a_zero_for() -> None:
    assert "for" not in CONDITION_SCHEMA({"entity_id": WINDOW, "for": 0})


@pytest.mark.parametrize("bad", [-1, {"hours": 25}, "soon"])
def test_schema_rejects_bad_for(bad: object) -> None:
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA({"entity_id": WINDOW, "for": bad})


def test_schema_accepts_a_template_condition() -> None:
    result = CONDITION_SCHEMA({"template": "{{ is_state('binary_sensor.window', 'on') }}"})
    assert result == {"template": "{{ is_state('binary_sensor.window', 'on') }}"}


@pytest.mark.parametrize(
    "bad",
    [
        {"template": "{{ true }}", "entity_id": WINDOW},
        {"template": "{{ true }}", "state": "on"},
        {"template": "{{ true }}", "operator": "equals"},
        {"template": "{{ true }}", "attribute": "x"},
        {"template": "{{ 1 + }}"},
        {"template": ""},
        {"for": 60},
    ],
)
def test_schema_rejects_bad_template_conditions(bad: dict[str, object]) -> None:
    with pytest.raises(vol.Invalid):
        CONDITION_SCHEMA(bad)


def test_schema_template_condition_may_have_for() -> None:
    result = CONDITION_SCHEMA({"template": "{{ true }}", "for": {"seconds": 30}})
    assert result == {"template": "{{ true }}", "for": 30}


# Action: for -----------------------------------------------------------------------------


async def test_banner_waits_for_the_duration(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    result = await create(
        id="open", message="Window open", condition={"entity_id": WINDOW, "for": {"minutes": 5}}
    )
    assert result["status"] == "waiting"
    assert shown(entry) == []

    await advance(hass, freezer, 299)
    assert shown(entry) == []
    await advance(hass, freezer, 2)
    assert shown(entry) == ["open"]


async def test_banner_with_for_stays_when_the_condition_goes_false(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 61)
    assert shown(entry) == ["open"]
    await set_state(hass, "off")
    assert shown(entry) == []


async def test_going_false_before_the_duration_restarts_the_wait(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "off")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await set_state(hass, "on")
    await advance(hass, freezer, 40)
    await set_state(hass, "off")
    await advance(hass, freezer, 40)
    await set_state(hass, "on")
    await advance(hass, freezer, 40)
    assert shown(entry) == []  # 40 s since the last flip, not 120
    await advance(hass, freezer, 21)
    assert shown(entry) == ["open"]


async def test_same_value_updates_do_not_restart_the_wait(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on", note="a")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 40)
    await set_state(hass, "on", note="b")  # attribute change, still matching
    await advance(hass, freezer, 21)
    assert shown(entry) == ["open"]


async def test_unavailable_during_the_wait_changes_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 30)
    await set_state(hass, "unavailable")
    await advance(hass, freezer, 31)
    assert shown(entry) == []  # no real value when the wait ends: nothing is shown (D-066)
    await set_state(hass, "on")
    await advance(hass, freezer, 61)
    assert shown(entry) == ["open"]  # a matching state starts the wait again


async def test_for_works_with_an_operator(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.states.async_set(OTHER, "20")
    await create(
        id="hot",
        message="Hot",
        condition={"entity_id": OTHER, "operator": "above", "state": "25", "for": 120},
    )
    hass.states.async_set(OTHER, "26")
    await hass.async_block_till_done()
    await advance(hass, freezer, 121)
    assert shown(entry) == ["hot"]


async def test_replacing_a_banner_cancels_its_wait(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await create(id="open", message="m2")
    assert shown(entry) == ["open"]
    await advance(hass, freezer, 61)
    assert shown(entry) == ["open"] and banners(entry)["open"].message == "m2"


async def test_clearing_a_banner_cancels_its_wait(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    entry.runtime_data.clear("open")
    await advance(hass, freezer, 61)
    assert banners(entry) == {}


async def test_once_mode_banner_with_for_is_removed_when_it_ends(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 61)
    await set_state(hass, "off")
    assert banners(entry) == {}


async def test_wait_restarts_after_a_reload(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 40)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert shown(entry) == []
    await advance(hass, freezer, 40)
    assert shown(entry) == []  # the timer started again at the reload (D-066)
    await advance(hass, freezer, 21)
    assert shown(entry) == ["open"]


async def test_a_banner_already_shown_stays_after_a_reload(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await set_state(hass, "on")
    await create(id="open", message="m", condition={"entity_id": WINDOW, "for": 60})
    await advance(hass, freezer, 61)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert shown(entry) == ["open"]


# Action: template ------------------------------------------------------------------------


async def test_template_condition_shows_and_hides(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "20")
    result = await create(
        id="warm",
        message="Warm",
        condition={"template": f"{{{{ states('{OTHER}') | float > 25 }}}}"},
    )
    assert result["status"] == "waiting"
    assert shown(entry) == []

    hass.states.async_set(OTHER, "26")
    await hass.async_block_till_done()
    assert shown(entry) == ["warm"]

    hass.states.async_set(OTHER, "24")
    await hass.async_block_till_done()
    assert shown(entry) == []  # mode once: the banner ends when the template turns false
    assert banners(entry) == {}


async def test_template_condition_recurring(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "26")
    await create(
        id="warm",
        message="Warm",
        mode="recurring",
        condition={"template": f"{{{{ states('{OTHER}') | float > 25 }}}}"},
    )
    assert shown(entry) == ["warm"]
    hass.states.async_set(OTHER, "20")
    await hass.async_block_till_done()
    assert shown(entry) == []
    hass.states.async_set(OTHER, "30")
    await hass.async_block_till_done()
    assert shown(entry) == ["warm"]


async def test_template_with_several_entities(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "off")
    hass.states.async_set(WINDOW, "off")
    await create(
        id="both",
        message="Both",
        mode="recurring",
        condition={
            "template": f"{{{{ is_state('{OTHER}', 'on') and is_state('{WINDOW}', 'on') }}}}"
        },
    )
    hass.states.async_set(OTHER, "on")
    await hass.async_block_till_done()
    assert shown(entry) == []
    hass.states.async_set(WINDOW, "on")
    await hass.async_block_till_done()
    assert shown(entry) == ["both"]


async def test_template_that_cannot_render_keeps_the_banner_waiting(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    result = await create(
        id="broken",
        message="m",
        mode="recurring",
        condition={"template": f"{{{{ states('{OTHER}') | float > 25 }}}}"},
    )
    assert result["status"] == "waiting"  # float of "unknown" with no default raises
    assert shown(entry) == []
    hass.states.async_set(OTHER, "30")
    await hass.async_block_till_done()
    assert shown(entry) == ["broken"]


async def test_template_condition_with_for(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.states.async_set(OTHER, "20")
    await create(
        id="warm",
        message="Warm",
        mode="recurring",
        condition={"template": f"{{{{ states('{OTHER}') | float(0) > 25 }}}}", "for": 120},
    )
    hass.states.async_set(OTHER, "26")
    await hass.async_block_till_done()
    assert shown(entry) == []
    await advance(hass, freezer, 121)
    assert shown(entry) == ["warm"]


async def test_template_condition_survives_a_reload(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "26")
    await create(
        id="warm",
        message="Warm",
        mode="recurring",
        condition={"template": f"{{{{ states('{OTHER}') | float(0) > 25 }}}}"},
    )
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert shown(entry) == ["warm"]
    hass.states.async_set(OTHER, "10")
    await hass.async_block_till_done()
    assert shown(entry) == []  # the reloaded banner is tracked again


async def test_template_tracking_stops_when_the_banner_is_cleared(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "26")
    await create(
        id="warm",
        message="m",
        mode="recurring",
        condition={"template": f"{{{{ states('{OTHER}') | float(0) > 25 }}}}"},
    )
    entry.runtime_data.clear("warm")
    hass.states.async_set(OTHER, "10")
    await hass.async_block_till_done()
    assert banners(entry) == {}


async def test_template_is_not_exposed_to_the_card(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(OTHER, "26")
    await create(id="warm", message="m", condition={"template": "{{ true }}"})
    item = entry.runtime_data.visible("u")[0]
    assert "condition" not in item


# Watch rules: for ------------------------------------------------------------------------


async def test_rule_waits_for_the_duration(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    await set_state(hass, "off")
    subentry = add_rule(hass, entry, **{"for": 300})
    await hass.async_block_till_done()
    await set_state(hass, "on")
    assert shown(entry) == []
    await advance(hass, freezer, 301)
    assert shown(entry) == [rule_id(subentry)]


async def test_rule_time_counts_from_the_end_of_the_wait(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    from homeassistant.util import dt as dt_util

    await set_state(hass, "off")
    add_rule(hass, entry, **{"for": 300})
    await hass.async_block_till_done()
    await set_state(hass, "on")
    await advance(hass, freezer, 301)
    item = entry.runtime_data.visible("u")[0]
    assert item["updated_at"] == dt_util.utcnow().isoformat()


async def test_rule_going_false_cancels_the_wait(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    await set_state(hass, "off")
    add_rule(hass, entry, **{"for": 300})
    await hass.async_block_till_done()
    await set_state(hass, "on")
    await advance(hass, freezer, 200)
    await set_state(hass, "off")
    await advance(hass, freezer, 200)
    assert shown(entry) == []


async def test_rule_true_at_setup_waits_again_without_events(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    from pytest_homeassistant_custom_component.common import async_capture_events

    created = async_capture_events(hass, "heads_up_banner_created")
    await set_state(hass, "on")
    add_rule(hass, entry, **{"for": 60})
    await hass.async_block_till_done()
    assert shown(entry) == [] and created == []
    await advance(hass, freezer, 61)
    assert len(shown(entry)) == 1 and len(created) == 1


async def test_deleting_a_rule_cancels_its_wait(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, **{"for": 60})
    await hass.async_block_till_done()
    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    await hass.async_block_till_done()
    await advance(hass, freezer, 61)
    assert shown(entry) == []


async def test_editing_a_rule_restarts_the_wait(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, **{"for": 60})
    await hass.async_block_till_done()
    await advance(hass, freezer, 40)
    hass.config_entries.async_update_subentry(
        entry, subentry, data={**subentry.data, "message": "New text"}
    )
    await hass.async_block_till_done()
    await advance(hass, freezer, 40)
    assert shown(entry) == []
    await advance(hass, freezer, 21)
    assert shown(entry) == [rule_id(subentry)]


# Rule flow -------------------------------------------------------------------------------


async def _flow_input(**extra: object) -> dict[str, object]:
    return {
        "name": "Window",
        "entity_id": WINDOW,
        "operator": "equals",
        "state": ["on"],
        "message": "Window open",
        "severity": "warning",
        "people": [],
        "dismissible": False,
        "enabled": True,
        **extra,
    }


async def test_flow_stores_for_as_seconds(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "off")
    flow = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], await _flow_input(**{"for": {"hours": 0, "minutes": 5, "seconds": 0}})
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["for"] == 300


async def test_flow_leaves_for_out_when_omitted_or_zero(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "off")
    for extra in ({}, {"for": {"hours": 0, "minutes": 0, "seconds": 0}}):
        flow = await hass.config_entries.subentries.async_init(
            (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.subentries.async_configure(
            flow["flow_id"], await _flow_input(**extra)
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert "for" not in result["data"]


async def test_flow_rejects_a_duration_over_24_hours(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "off")
    flow = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], await _flow_input(**{"for": {"days": 2}})
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"for": "for_too_long"}


async def test_template_with_now_follows_the_clock(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    freezer.move_to("2026-10-26 10:00:00+00:00")
    await create(
        id="late",
        message="Late",
        mode="recurring",
        condition={"template": "{{ now().minute >= 30 }}"},
    )
    assert shown(entry) == []
    await advance(hass, freezer, 31 * 60)
    assert shown(entry) == ["late"]
