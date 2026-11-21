"""A watch rule may name an audience: its banner goes to the people of the audience as of the
moment it appears, as for a call (D-131, D-242)."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import BANNER_NOBODY

from .helpers import set_person, settle
from .policy_support import add_audience

WINDOW = "binary_sensor.window"


async def add_rule(hass: HomeAssistant, entry: MockConfigEntry, **data: object) -> dict:
    flow = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "rule"), context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "Window", "entity_id": WINDOW, "message": "Window open", **data}
    )
    await hass.async_block_till_done()
    return dict(result)


def audience_key(entry: MockConfigEntry, name: str) -> str:
    return next(s.subentry_id for s in entry.subentries.values() if s.title == name)


async def test_the_banner_goes_to_the_people_of_the_audience(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await add_audience(hass, entry, "Parents", kind="persons", persons=["person.anna"])
    hass.states.async_set(WINDOW, "on")
    result = await add_rule(hass, entry, audience=audience_key(entry, "Parents"))
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await settle(hass, entry)
    (banner,) = entry.runtime_data.rules.values()
    assert banner.people == ["person.anna"]
    rule = next(s for s in entry.subentries.values() if s.subentry_type == "rule")
    assert "people" not in rule.data


async def test_an_audience_that_is_empty_now_shows_the_banner_to_nobody(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "not_home")
    hass.states.async_set(WINDOW, "on")
    await add_rule(hass, entry, audience="at_home")
    await settle(hass, entry)
    (banner,) = entry.runtime_data.rules.values()
    assert banner.people == [BANNER_NOBODY]


async def test_an_audience_and_people_together_are_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    hass.states.async_set(WINDOW, "off")
    result = await add_rule(hass, entry, audience="everyone", people=["person.anna"])
    assert result["errors"] == {"audience": "audience_or_people"}
