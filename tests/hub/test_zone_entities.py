"""A zone from an entity per person (D-229): audiences by zone, Presence, the profile form."""

from typing import Any

import pytest
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.rename import rewrite

from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import add_audience, add_policy, make_household, move, pushes, send

AT_WORK = "binary_sensor.anna_at_work"


@pytest.fixture
def options() -> dict[str, Any]:
    return {"presence_debounce_seconds": 0, "policy_mode": "all"}


async def members(entry: MockConfigEntry, name: str) -> list[str]:
    resolver = entry.runtime_data.hub.resolver
    result = await resolver.members(resolver.audience(name), "warning")
    return [m.key for m in result.recipients]


async def anna_profile(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> None:
    subentry = ConfigSubentry(
        data={"person": "person.anna", "channels": ["banner", "push", "popup"], **data},
        subentry_type="recipient_profile",
        title="Anna",
        unique_id=None,
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    await hass.async_block_till_done()


async def test_a_zone_follows_its_entity_and_other_zones_keep_the_person_state(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "not_home")  # Home Assistant: not at work
    hass.states.async_set(AT_WORK, "on")
    await anna_profile(hass, entry, zone_entities={"zone.work": AT_WORK})
    await add_audience(
        hass, entry, "At work", kind="presence", presence="in_zone", zone="zone.work"
    )
    await add_audience(hass, entry, "At gym", kind="presence", presence="in_zone", zone="zone.gym")
    assert await members(entry, "At work") == ["person.anna"]
    assert await members(entry, "At gym") == []
    hass.states.async_set(AT_WORK, "off")
    await hass.async_block_till_done()
    assert await members(entry, "At work") == []


async def test_without_an_entity_a_zone_is_where_home_assistant_puts_the_person(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "not_home")
    hass.states.async_set(
        "person.anna", "not_home", {"in_zones": ["zone.work"], "device_trackers": []}
    )
    await add_audience(
        hass, entry, "At work", kind="presence", presence="in_zone", zone="zone.work"
    )
    assert await members(entry, "At work") == ["person.anna"]


async def test_the_home_entity_also_counts_for_an_audience_by_the_zone_home(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    hass.states.async_set("input_boolean.anna_home", "off")
    await anna_profile(hass, entry, home_entity="input_boolean.anna_home")
    await add_audience(
        hass, entry, "In Home", kind="presence", presence="in_zone", zone="zone.home"
    )
    assert await members(entry, "In Home") == []


async def test_an_unavailable_zone_entity_is_unknown_presence(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "work")
    hass.states.async_set(AT_WORK, "unavailable")
    await anna_profile(hass, entry, zone_entities={"zone.work": AT_WORK})
    await add_audience(
        hass, entry, "At work", kind="presence", presence="in_zone", zone="zone.work"
    )
    resolver = entry.runtime_data.hub.resolver
    result = await resolver.members(resolver.audience("At work"), "warning")
    assert [s.reason for s in result.skipped] == ["presence_unknown"]


async def test_presence_for_a_zone_releases_when_its_entity_turns_on(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(AT_WORK, "off")
    await anna_profile(hass, entry, zone_entities={"zone.work": AT_WORK})
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])
    await add_policy(hass, entry, "At work", type="presence", zone="zone.work")
    move(hass, "person.anna", "work")  # ignored for zone.work: the entity decides
    await send(hass, entry, severity="warning", to={"push": {"audience": "Family"}})
    assert not pushes(home.anna)
    hass.states.async_set(AT_WORK, "on")
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1


async def test_the_profile_form_stores_zone_entities_and_keeps_home_under_its_own_key(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "recipient_profile"), context={"source": "user"}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "person": "person.anna",
            "channels": ["banner"],
            "zone_entities": {
                "zone.work": AT_WORK,
                "zone.home": "input_boolean.anna_home",
                "zone.gym": "",
            },
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = [s for s in entry.subentries.values() if s.subentry_type == "recipient_profile"]
    assert sub.data["home_entity"] == "input_boolean.anna_home"
    assert sub.data["zone_entities"] == {"zone.work": AT_WORK}
    resolver = entry.runtime_data.hub.resolver
    assert resolver.zone_entity("person.anna", "zone.work") == AT_WORK
    assert resolver.zone_entity("person.anna", "zone.gym") == ""


@pytest.mark.parametrize(
    "zones",
    [{"work": AT_WORK}, {"zone.work": "sensor.temperature"}, ["zone.work"]],
)
async def test_the_profile_form_refuses_a_bad_zone_entity(
    hass: HomeAssistant, entry: MockConfigEntry, zones: Any
) -> None:
    set_person(hass, "person.anna", "home")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "recipient_profile"), context={"source": "user"}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"person": "person.anna", "channels": ["banner"], "zone_entities": zones},
    )
    assert result["errors"] == {"zone_entities": "zone_entities_invalid"}


def test_a_renamed_zone_or_entity_is_rewritten_in_zone_entities() -> None:
    data = {"person": "person.anna", "zone_entities": {"zone.work": AT_WORK}}
    renamed = rewrite(data, "zone.work", "zone.office")
    assert renamed["zone_entities"] == {"zone.office": AT_WORK}
    renamed = rewrite(renamed, AT_WORK, "binary_sensor.anna_office")
    assert renamed["zone_entities"] == {"zone.office": "binary_sensor.anna_office"}
