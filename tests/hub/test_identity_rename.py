"""Renaming a policy, an audience or a group changes nothing that is running (D-199)."""

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..conftest import banners
from .conftest import AddDevice
from .policy_support import (
    ESCALATION,
    REMINDER,
    add_audience,
    add_policy,
    make_household,
    pushes,
    send,
    wait,
)
from .test_policy_entities import switch_of
from .test_recipients_groups import add_group


def timers(entry: MockConfigEntry) -> list[tuple[str, str, str, object]]:
    rows = entry.runtime_data.hub.ledger.timers("m")
    return sorted((r.message_id, r.recipient, r.state.value, r.due) for r in rows)  # type: ignore[return-value]


@pytest.mark.parametrize("new_name", ["Flood", "WATER", "  Water  ", "Überschwemmung"])
async def test_a_policy_rename_keeps_running_timers_and_the_stored_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
    new_name: str,
) -> None:
    home = await make_household(hass, mobile_app_device)
    water = await add_policy(hass, entry, "Water", **ESCALATION, apply="manual")
    nag = await add_policy(hass, entry, "Nag", **REMINDER, apply="manual")
    await send(
        hass,
        entry,
        policy=[switch_of(hass, water.subentry_id), switch_of(hass, nag.subentry_id)],
    )
    before = timers(entry)
    stored = banners(entry)["m"].policy
    assert len(before) == 2

    hass.config_entries.async_update_subentry(entry, water, title=new_name.strip())
    hass.config_entries.async_update_subentry(entry, nag, title="Nag again")
    await hass.async_block_till_done()

    assert timers(entry) == before
    assert banners(entry)["m"].policy == stored
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.ben)) == 1  # the escalation was not ended by the rename
    await wait(hass, entry, freezer, 5)
    assert len(pushes(home.anna)) == 2  # the reminder still came
    reasons = {e["reason"] for e in entry.runtime_data.hub.trace.entries("m")}
    assert not {"policy_deleted", "policy_disabled", "no_longer_applies"} & reasons


async def test_deleting_a_policy_ends_its_timer_and_a_new_one_with_the_name_does_not_inherit_it(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    water = await add_policy(hass, entry, "Water", **ESCALATION, apply="manual")
    await send(hass, entry, policy=[switch_of(hass, water.subentry_id)])
    hass.config_entries.async_remove_subentry(entry, water.subentry_id)
    await hass.async_block_till_done()
    await add_policy(hass, entry, "Water", **ESCALATION, apply="manual")
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)  # the old timer ended: the new policy is a different thing
    reasons = [e["reason"] for e in entry.runtime_data.hub.trace.entries("m")]
    assert "policy_deleted" in reasons


async def test_an_audience_rename_keeps_a_policy_target_and_a_stored_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_audience(hass, entry, "Parents", kind="persons", persons=["person.ben"])
    (audience,) = [s for s in entry.subentries.values() if s.title == "Parents"]
    water = await add_policy(
        hass,
        entry,
        "Water",
        **{**ESCALATION, "targets": {"push": {"audience": audience.subentry_id}}},
    )
    await send(hass, entry)
    hass.config_entries.async_update_subentry(entry, audience, title="Adults")
    await hass.async_block_till_done()
    assert (
        entry.runtime_data.hub.policy_problem(
            entry.runtime_data.hub.policies.by_key(water.subentry_id)
        )
        is None
    )  # type: ignore[arg-type]
    assert entry.runtime_data.hub.policies.usage(audience.subentry_id) == ["Water"]
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.ben)) == 1


async def test_a_group_rename_keeps_its_speakers_for_a_stored_reference(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: object
) -> None:
    speaker = fake_speakers.announce_player  # type: ignore[attr-defined]
    add_group(hass, entry, "Ground floor", members=[speaker], areas=[])
    await hass.async_block_till_done()
    (group,) = [s for s in entry.subentries.values() if s.subentry_type == "recipient_group"]
    resolver = entry.runtime_data.hub.resolver
    token = resolver.stored_recipient("speak", "Ground floor (group)")
    assert token == f"group:{group.subentry_id}"
    hass.config_entries.async_update_subentry(entry, group, title="Downstairs")
    await hass.async_block_till_done()
    result = await resolver.resolve({"recipients": [token]}, "speak", "warning")
    assert [r.key for r in result.recipients] == [speaker]
