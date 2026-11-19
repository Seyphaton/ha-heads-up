"""Home from an entity per person (D-220): audiences, Last to leave, Away, the profile form."""

from typing import Any

import pytest
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import AWAY, add_audience, add_policy, make_household, pushes, send

ANNA_HOME = "binary_sensor.anna_really_home"


@pytest.fixture
def options() -> dict[str, Any]:
    return {"presence_debounce_seconds": 0, "policy_mode": "all"}


async def members(entry: MockConfigEntry, name: str) -> list[str]:
    resolver = entry.runtime_data.hub.resolver
    result = await resolver.members(resolver.audience(name), "warning")
    return [m.key for m in result.recipients]


async def anna_home_from_entity(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    subentry = ConfigSubentry(
        data={
            "person": "person.anna",
            "channels": ["banner", "push", "popup"],
            "home_entity": ANNA_HOME,
        },
        subentry_type="recipient_profile",
        title="Anna",
        unique_id=None,
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    await hass.async_block_till_done()


async def test_at_home_follows_the_home_entity_and_other_zones_keep_the_person_state(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")  # the GPS says home
    hass.states.async_set(ANNA_HOME, "off")  # the better rule says not
    await anna_home_from_entity(hass, entry)
    await add_audience(hass, entry, "In Work zone", presence="in_zone", zone="zone.work")
    assert await members(entry, "At home") == []
    assert await members(entry, "Not home") == ["person.anna"]
    assert await members(entry, "In Work zone") == []
    hass.states.async_set(ANNA_HOME, "on")
    await hass.async_block_till_done()
    assert await members(entry, "At home") == ["person.anna"]


async def test_an_unavailable_home_entity_is_unknown_presence(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    hass.states.async_set(ANNA_HOME, "unavailable")
    await anna_home_from_entity(hass, entry)
    resolver = entry.runtime_data.hub.resolver
    result = await resolver.members(resolver.audience("At home"), "warning")
    assert [s.reason for s in result.skipped] == ["presence_unknown"]


async def test_last_to_leave_and_first_home_follow_the_home_entity(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    hass.states.async_set(ANNA_HOME, "on")
    await anna_home_from_entity(hass, entry)
    set_person(hass, "person.anna", "not_home")  # ignored: the entity decides
    await hass.async_block_till_done()
    assert await members(entry, "Last to leave") == []
    hass.states.async_set(ANNA_HOME, "off")
    await hass.async_block_till_done()
    assert await members(entry, "Last to leave") == ["person.anna"]
    hass.states.async_set(ANNA_HOME, "on")
    await hass.async_block_till_done()
    assert await members(entry, "First home") == ["person.anna"]


async def test_away_holds_while_the_home_entity_is_off_and_sends_when_it_turns_on(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)  # both persons are "home" by GPS
    hass.states.async_set(ANNA_HOME, "off")
    await anna_home_from_entity(hass, entry)
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])
    await add_policy(hass, entry, "Away", **AWAY)
    await send(hass, entry, severity="warning", to={"push": {"audience": "Family"}})
    assert not pushes(home.anna) and len(pushes(home.ben)) == 1
    hass.states.async_set(ANNA_HOME, "on")
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1


async def test_the_profile_form_stores_a_home_entity_and_refuses_other_domains(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "recipient_profile"), context={"source": "user"}
    )
    with pytest.raises(InvalidData):  # the entity selector allows only on/off domains
        await hass.config_entries.subentries.async_configure(
            result["flow_id"],
            {"person": "person.anna", "channels": ["banner"], "home_entity": "sensor.temperature"},
        )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"person": "person.anna", "channels": ["banner"], "home_entity": "input_boolean.anna"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = [s for s in entry.subentries.values() if s.subentry_type == "recipient_profile"]
    assert sub.data["home_entity"] == "input_boolean.anna"
    assert (
        entry.runtime_data.hub.resolver.profile("person.anna").home_entity == "input_boolean.anna"
    )
