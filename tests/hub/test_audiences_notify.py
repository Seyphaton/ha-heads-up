"""`notify` with real audiences, recipients and groups (H2 replaces the null resolver of H1)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import FakeSpeakers, set_person, settle


async def notify(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    response = await hass.services.async_call(
        DOMAIN, "notify", data, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def test_a_built_in_audience_is_accepted_and_resolved_per_recipient(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    result = await notify(
        hass, id="a", message="x", channels=["push"], to={"push": {"audience": "At home"}}
    )
    # Anna has a device and gets the push; Ben has none and is skipped with a reason.
    assert result["channels"]["push"] == {"sent": 1, "held": 0, "skipped": 1, "failed": 0}
    await settle(hass, entry)
    reasons = {t["recipient"]: t["reason"] for t in entry.runtime_data.hub.trace.entries("a")}
    assert reasons["person.ben"] == "no_usable_device"


async def test_an_audience_that_is_empty_right_now_is_skipped_as_no_recipients(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    result = await notify(
        hass, id="a", message="x", channels=["popup"], to={"popup": {"audience": "Not home"}}
    )
    assert result["channels"]["popup"]["skipped"] == 1
    await settle(hass, entry)
    (entry_,) = entry.runtime_data.hub.trace.entries("a")[:1]
    assert entry_["reason"] == "no_recipients"


async def test_a_custom_audience_and_a_group_can_be_used_in_a_call(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    set_person(hass, "person.anna", "home")
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"kind": "persons", "persons": ["person.anna"]},
            subentry_type="audience",
            title="Parents",
            unique_id=None,
        ),
    )
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"members": [fake_speakers.announce_player], "areas": []},
            subentry_type="recipient_group",
            title="Ground floor",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    result = await notify(
        hass,
        id="a",
        message="x",
        channels=["popup", "speak"],
        to={
            "popup": {"audience": "Parents"},
            "speak": {"recipients": ["Ground floor (group)"]},
        },
    )
    assert result["channels"]["popup"]["skipped"] == 1  # one person; popup is not built yet
    assert result["channels"]["speak"]["sent"] == 1  # one speaker
    assert set(result["channels"]) == {"popup", "speak"}


async def test_audiences_groups_and_profiles_survive_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"kind": "presence", "presence": "at_home"},
            subentry_type="audience",
            title="Home crowd",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await restart(hass, entry)
    assert "Home crowd" in entry.runtime_data.hub.resolver.names()


async def test_subentries_of_the_hub_are_ignored_while_the_hub_is_off(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "hub_enabled": False})
    await hass.async_block_till_done()
    assert entry.runtime_data.hub is None
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"kind": "presence", "presence": "at_home"},
            subentry_type="audience",
            title="Home crowd",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()  # no hub: nothing to sync, nothing raises
    assert entry.runtime_data.rules == {}
