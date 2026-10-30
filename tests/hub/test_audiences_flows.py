"""Subentry flows for audiences, recipient groups and recipient profiles."""

from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .helpers import FakeSpeakers, set_person


async def run(
    hass: HomeAssistant, entry: MockConfigEntry, kind: str, data: dict[str, Any]
) -> dict[str, Any]:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, kind), context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return dict(await hass.config_entries.subentries.async_configure(result["flow_id"], data))


def subentries(entry: MockConfigEntry, kind: str) -> list[Any]:
    return [s for s in entry.subentries.values() if s.subentry_type == kind]


# Audiences -------------------------------------------------------------------------------


async def test_add_a_persons_audience(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home")
    result = await run(
        hass, entry, "audience", {"name": "Parents", "kind": "persons", "persons": ["person.anna"]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "audience")
    assert sub.title == "Parents"
    assert dict(sub.data) == {"kind": "persons", "persons": ["person.anna"]}
    await hass.async_block_till_done()
    assert "Parents" in entry.runtime_data.hub.resolver.names()


async def test_add_a_zone_audience_keeps_only_the_fields_of_its_kind(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await run(
        hass,
        entry,
        "audience",
        {
            "name": "At work",
            "kind": "presence",
            "presence": "in_zone",
            "zone": "zone.work",
            "persons": ["person.anna"],
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "audience")
    assert dict(sub.data) == {"kind": "presence", "presence": "in_zone", "zone": "zone.work"}


async def test_audience_errors(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    cases = [
        ({"name": " ", "kind": "persons", "persons": ["person.a"]}, {"name": "name_required"}),
        (
            {"name": "at home", "kind": "persons", "persons": ["person.a"]},
            {"name": "name_exists"},  # a built-in name, case-insensitive
        ),
        ({"name": "X", "kind": "persons"}, {"persons": "persons_required"}),
        ({"name": "X", "kind": "presence"}, {"presence": "presence_required"}),
        ({"name": "X", "kind": "presence", "presence": "in_zone"}, {"zone": "zone_required"}),
    ]
    for data, errors in cases:
        result = await run(hass, entry, "audience", data)
        assert result["type"] is FlowResultType.FORM and result["errors"] == errors, data


async def test_an_audience_name_cannot_repeat(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    data = {"name": "Parents", "kind": "presence", "presence": "at_home"}
    await run(hass, entry, "audience", data)
    result = await run(hass, entry, "audience", {**data, "name": "PARENTS"})
    assert result["errors"] == {"name": "name_exists"}


async def test_reconfigure_an_audience_may_keep_its_own_name(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await run(
        hass, entry, "audience", {"name": "Parents", "kind": "presence", "presence": "at_home"}
    )
    (sub,) = subentries(entry, "audience")
    result = await entry.start_subentry_reconfigure_flow(hass, sub.subentry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Parents", "kind": "presence", "presence": "not_home"}
    )
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "reconfigure_successful"
    assert subentries(entry, "audience")[0].data["presence"] == "not_home"


# Recipient groups -------------------------------------------------------------------------


async def test_add_a_recipient_group(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    result = await run(
        hass,
        entry,
        "recipient_group",
        {"name": "Ground floor", "members": [fake_speakers.announce_player]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "recipient_group")
    assert dict(sub.data) == {"members": [fake_speakers.announce_player], "areas": []}


async def test_recipient_group_errors(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speaker = fake_speakers.announce_player
    cases = [
        ({"name": "", "members": [speaker]}, {"name": "name_required"}),
        ({"name": "Floor (group)", "members": [speaker]}, {"name": "name_has_suffix"}),
        ({"name": "Floor"}, {"members": "group_empty"}),
        ({"name": "Floor", "members": ["media_player.gone"]}, {"members": "member_not_found"}),
        ({"name": "Floor", "areas": ["nowhere"]}, {"areas": "area_not_found"}),
    ]
    for data, errors in cases:
        result = await run(hass, entry, "recipient_group", data)
        assert result["errors"] == errors, data


async def test_a_group_name_cannot_repeat(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    data = {"name": "Floor", "members": [fake_speakers.announce_player]}
    await run(hass, entry, "recipient_group", data)
    assert (await run(hass, entry, "recipient_group", data))["errors"] == {"name": "name_exists"}


# Recipient profiles -----------------------------------------------------------------------


async def test_add_a_recipient_profile(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    spare = await mobile_app_device("Spare phone")
    result = await run(
        hass,
        entry,
        "recipient_profile",
        {
            "person": "person.anna",
            "devices": [spare.device_id],
            "primary": spare.device_id,
            "channels": ["push", "popup"],
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "recipient_profile")
    assert dict(sub.data) == {
        "person": "person.anna",
        "channels": ["push", "popup"],
        "devices": [spare.device_id],
        "primary": spare.device_id,
    }
    await hass.async_block_till_done()
    profile = entry.runtime_data.hub.resolver.profile("person.anna")
    assert profile.channels == ("push", "popup") and profile.customized


async def test_a_person_has_one_profile(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home")
    data = {"person": "person.anna", "channels": ["push"]}
    await run(hass, entry, "recipient_profile", data)
    assert (await run(hass, entry, "recipient_profile", data))["errors"] == {
        "person": "profile_exists"
    }


async def test_recipient_profile_errors(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    spare = await mobile_app_device("Spare phone")
    base = {"person": "person.anna", "channels": ["push"]}
    cases = [
        ({**base, "person": "person.ghost"}, {"person": "person_not_found"}),
        (
            {**base, "devices": [spare.device_id], "removed_devices": [spare.device_id]},
            {"removed_devices": "device_added_and_removed"},
        ),
        ({**base, "channels": []}, {"channels": "channels_required"}),
    ]
    for data, errors in cases:
        result = await run(hass, entry, "recipient_profile", data)
        assert result["errors"] == errors, data


async def test_reconfigure_a_profile_keeps_its_person(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await run(hass, entry, "recipient_profile", {"person": "person.anna", "channels": ["push"]})
    (sub,) = subentries(entry, "recipient_profile")
    result = await entry.start_subentry_reconfigure_flow(hass, sub.subentry_id)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"channels": ["banner"]}
    )
    assert result["type"] is FlowResultType.ABORT
    data = subentries(entry, "recipient_profile")[0].data
    assert data["person"] == "person.anna" and data["channels"] == ["banner"]
