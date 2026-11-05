"""One binary sensor per audience, and a call may name it (D-186)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import BUILTIN_AUDIENCES, DOMAIN

from ..conftest import banners
from .helpers import set_person


def entity_id(hass: HomeAssistant, unique_suffix: str) -> str | None:
    registry = er.async_get(hass)
    for registered in registry.entities.values():
        if registered.platform == DOMAIN and registered.unique_id.endswith(unique_suffix):
            return registered.entity_id
    return None


async def add_audience(
    hass: HomeAssistant, entry: MockConfigEntry, title: str, **data: Any
) -> ConfigSubentry:
    subentry = ConfigSubentry(
        data={"kind": "persons", **data}, subentry_type="audience", title=title, unique_id=None
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    await hass.async_block_till_done()
    return subentry


async def test_every_built_in_audience_has_a_sensor(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    for kind in BUILTIN_AUDIENCES.values():
        assert entity_id(hass, f"_audience_{kind}") is not None


async def test_a_new_audience_gets_a_sensor_and_a_deleted_one_loses_it(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    subentry = await add_audience(hass, entry, "Parents", persons=["person.anna"])
    found = entity_id(hass, f"_audience_{subentry.subentry_id}")
    assert found is not None
    state = hass.states.get(found)
    assert state is not None and state.state == "on"
    assert state.attributes["members"] == ["person.anna"]
    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    await hass.async_block_till_done()
    assert entity_id(hass, f"_audience_{subentry.subentry_id}") is None


async def test_the_sensor_follows_the_people(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "not_home")
    subentry = await add_audience(hass, entry, "Parents", persons=["person.anna"])
    found = entity_id(hass, f"_audience_{subentry.subentry_id}")
    assert found is not None
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    state = hass.states.get(found)
    assert state is not None and state.state == "on"


async def test_a_call_can_name_the_sensor_of_an_audience(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    found = entity_id(hass, "_audience_everyone")
    assert found is not None
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "a", "message": "x", "channels": ["banner"], "audience": found},
        blocking=True,
    )
    assert banners(entry)["a"].targets == {"banner": {"audience": "Everyone"}}


async def test_a_renamed_audience_keeps_its_sensor(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    subentry = await add_audience(hass, entry, "Parents", persons=["person.anna"])
    found = entity_id(hass, f"_audience_{subentry.subentry_id}")
    hass.config_entries.async_update_subentry(entry, subentry, title="Adults")
    await hass.async_block_till_done()
    assert found is not None
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "a", "message": "x", "channels": ["banner"], "audience": found},
        blocking=True,
    )
    assert banners(entry)["a"].targets == {"banner": {"audience": "Adults"}}


async def test_a_switched_off_built_in_audience_loses_its_sensor(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert entity_id(hass, "_audience_not_home") is not None
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "audiences_disabled": ["Not home"]}
    )
    await hass.async_block_till_done()
    assert entity_id(hass, "_audience_not_home") is None
