"""Built-in and custom audiences resolve to persons with a reason (DESIGN §23.7, D-080)."""

from typing import Any

import pytest
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, MockUser

from custom_components.heads_up.hub.audiences import BUILTINS

from .helpers import set_person


def resolver(entry: MockConfigEntry) -> Any:
    return entry.runtime_data.hub.resolver


async def members(entry: MockConfigEntry, name: str, severity: str = "warning") -> dict[str, str]:
    r = resolver(entry)
    result = await r.members(r.audience(name), severity)
    return {m.key: m.reason for m in result.recipients}


async def skipped(entry: MockConfigEntry, name: str, severity: str = "warning") -> dict[str, str]:
    r = resolver(entry)
    result = await r.members(r.audience(name), severity)
    return {s.who: s.reason for s in result.skipped}


def add_audience(hass: HomeAssistant, entry: MockConfigEntry, name: str, **data: Any) -> None:
    hass.config_entries.async_add_subentry(
        entry, ConfigSubentry(data=data, subentry_type="audience", title=name, unique_id=None)
    )


@pytest.fixture
def household(hass: HomeAssistant) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "not_home")
    set_person(hass, "person.cleo", "work")  # a zone


async def test_names_list_the_built_ins_then_custom_audiences(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    add_audience(hass, entry, "Parents", kind="persons", persons=["person.anna"])
    await hass.async_block_till_done()
    assert resolver(entry).names() == [*BUILTINS, "Parents"]
    assert list(BUILTINS) == [
        "Everyone",
        "Admins",
        "At home",
        "Not home",
        "Last to leave",
        "First home",
    ]


@pytest.mark.usefixtures("household")
async def test_everyone_is_every_person(entry: MockConfigEntry) -> None:
    assert set(await members(entry, "Everyone")) == {"person.anna", "person.ben", "person.cleo"}


@pytest.mark.usefixtures("household")
async def test_at_home_and_not_home_follow_the_person_state(entry: MockConfigEntry) -> None:
    assert set(await members(entry, "At home")) == {"person.anna"}
    assert await members(entry, "At home") == {"person.anna": "state:home"}
    assert set(await members(entry, "Not home")) == {"person.ben", "person.cleo"}


async def test_admins_are_persons_whose_user_is_an_admin(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_admin_user: MockUser,
    hass_read_only_user: MockUser,
) -> None:
    set_person(hass, "person.anna", "home", user_id=hass_admin_user.id)
    set_person(hass, "person.ben", "home", user_id=hass_read_only_user.id)
    set_person(hass, "person.guest", "home")
    assert await members(entry, "Admins") == {"person.anna": "admin"}
    # A person without a user is not an administrator; it is not listed as skipped either.
    assert await skipped(entry, "Admins") == {}


@pytest.mark.usefixtures("household")
async def test_persons_audience_lists_its_persons_and_skips_missing_ones(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    add_audience(hass, entry, "Parents", kind="persons", persons=["person.anna", "person.ghost"])
    await hass.async_block_till_done()
    assert await members(entry, "Parents") == {"person.anna": "listed"}
    assert await skipped(entry, "Parents") == {"person.ghost": "person_not_found"}


@pytest.mark.usefixtures("household")
async def test_zone_audiences_use_in_zones(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.cleo", "work")
    hass.states.async_set("person.cleo", "work", {"in_zones": ["zone.work"], "device_trackers": []})
    add_audience(hass, entry, "At work", kind="presence", presence="in_zone", zone="zone.work")
    add_audience(
        hass, entry, "Away from work", kind="presence", presence="not_in_zone", zone="zone.work"
    )
    await hass.async_block_till_done()
    assert set(await members(entry, "At work")) == {"person.cleo"}
    assert set(await members(entry, "Away from work")) == {"person.anna", "person.ben"}


@pytest.mark.parametrize("unknown", [None, "unavailable"])
async def test_unknown_presence_notifies_critical_and_skips_lower_severities(
    hass: HomeAssistant, entry: MockConfigEntry, unknown: str | None
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", unknown)
    assert await members(entry, "Not home", "critical") == {
        "person.ben": "presence_unknown_critical"
    }
    assert await members(entry, "Not home", "warning") == {}
    assert await skipped(entry, "Not home", "warning") == {"person.ben": "presence_unknown"}
    assert await members(entry, "At home", "critical") == {
        "person.anna": "state:home",
        "person.ben": "presence_unknown_critical",
    }


async def test_unknown_presence_does_not_apply_to_fixed_audiences(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", None)
    assert set(await members(entry, "Everyone")) == {"person.ben"}


@pytest.mark.usefixtures("household")
async def test_a_presence_audience_can_be_limited_to_chosen_persons(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.dora", "home")
    add_audience(
        hass, entry, "Anna home", kind="presence", presence="at_home", limit=["person.anna"]
    )
    add_audience(
        hass,
        entry,
        "Two away",
        kind="presence",
        presence="not_home",
        limit=["person.ben", "person.dora"],
    )
    add_audience(hass, entry, "Anyone home", kind="presence", presence="at_home")
    await hass.async_block_till_done()
    assert set(await members(entry, "Anna home")) == {"person.anna"}
    assert set(await members(entry, "Two away")) == {"person.ben"}  # Dora is home, Cleo not listed
    assert set(await members(entry, "Anyone home")) == {"person.anna", "person.dora"}


async def test_a_switched_off_built_in_audience_is_not_offered_and_not_found(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "audiences_disabled": ["Not home"]}
    )
    await hass.async_block_till_done()
    assert "Not home" not in resolver(entry).names() and "At home" in resolver(entry).names()
    assert resolver(entry).audience("Not home") is None
    assert resolver(entry).audience("At home") is not None
