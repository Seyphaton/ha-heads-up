"""Renaming anything the user named changes nothing that is running (D-199).

One household: policies of three types, a custom audience, a recipient group, a watch rule and
messages with a running escalation, a running reminder and a message held for a summary. Every
named thing is renamed, in a random order (the seed is the test id), once before time passes and
once while the timers run, with case-only changes among them. The outcome must be the one of a
household nobody renamed (the seed `None`).
"""

import random
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub import panel_data

from .conftest import AddDevice
from .policy_support import (
    ESCALATION,
    REMINDER,
    SUMMARIZE,
    add_audience,
    add_policy,
    make_household,
    pushes,
    send,
    summaries,
    wait,
)
from .test_policy_entities import switch_of
from .test_recipients_groups import add_group

BAD_REASONS = {
    "policy_deleted",
    "policy_disabled",
    "policy_gone",
    "no_longer_applies",
    "audience_missing",
    "group_missing",
    "unknown_audience",
    "unknown_recipient",
}


def renames(entry: MockConfigEntry, hass: HomeAssistant, rng: random.Random, tag: str) -> None:
    """Give every named thing a new name, a case-only change for half of them."""
    things = [s for s in entry.subentries.values() if s.subentry_type != "recipient_profile"]
    rng.shuffle(things)
    for sub in things:
        title = sub.title.upper() if rng.random() < 0.5 else f"{sub.title} {tag}"
        hass.config_entries.async_update_subentry(entry, sub, title=title)
    # A person's friendly name is shown in lists; nothing keys on it.
    for state in hass.states.async_all("person"):
        hass.states.async_set(
            state.entity_id,
            state.state,
            {**state.attributes, "friendly_name": f"{tag} {state.entity_id}"},
        )


@pytest.mark.parametrize("seed", [None, 0, 1, 2, 3, 4, 5, 6, 7])
async def test_nothing_that_runs_changes_when_everything_is_renamed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
    freezer: FrozenDateTimeFactory,
    seed: int | None,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_audience(hass, entry, "Parents", kind="persons", persons=["person.ben"])
    (audience,) = [s for s in entry.subentries.values() if s.subentry_type == "audience"]
    add_group(hass, entry, "Hall", members=[fake_speakers.announce_player], areas=[])
    water = await add_policy(
        hass,
        entry,
        "Water",
        **{
            **ESCALATION,
            "apply": "manual",
            "targets": {"push": {"audience": audience.subentry_id}},
        },
    )
    nag = await add_policy(hass, entry, "Nag", **REMINDER, apply="manual")
    await add_policy(hass, entry, "Digest", **SUMMARIZE, severities=["info"])
    hass.states.async_set("binary_sensor.w", "off")
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={
                "entity_id": "binary_sensor.w",
                "message": "open",
                "people": ["person.anna"],
                "policy": nag.subentry_id,
            },
            subentry_type="rule",
            title="Window",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    hass.states.async_set("binary_sensor.w", "on")
    await send(
        hass,
        entry,
        policy=[switch_of(hass, water.subentry_id), switch_of(hass, nag.subentry_id)],
    )
    await send(hass, entry, id="h", severity="info", message="Digest me")
    (rule_id,) = entry.runtime_data.rules
    before = {
        "timers": sorted(
            (r.message_id, r.recipient, r.state.value, r.due)
            for r in entry.runtime_data.hub.ledger.timers()
        ),
        "held": sorted(
            (h.message_id, h.policy) for h in entry.runtime_data.hub.ledger.held.values()
        ),
    }
    assert any(t[0] == rule_id for t in before["timers"]) and before["held"]

    rng = random.Random(seed)
    if seed is not None:
        renames(entry, hass, rng, "A")
        await hass.async_block_till_done()
    assert {
        "timers": sorted(
            (r.message_id, r.recipient, r.state.value, r.due)
            for r in entry.runtime_data.hub.ledger.timers()
        ),
        "held": sorted(
            (h.message_id, h.policy) for h in entry.runtime_data.hub.ledger.held.values()
        ),
    } == before

    await wait(hass, entry, freezer, 5.1)
    if seed is not None:
        renames(entry, hass, rng, "B")  # again while the timers run
        await hass.async_block_till_done()
    assert len(pushes(home.ben)) == 1  # the escalation to the audience
    await wait(hass, entry, freezer, 5)
    assert len(pushes(home.anna)) == 2  # the message, then its reminder
    await wait(hass, entry, freezer, 55)
    # The held message came out in its summaries: one on the dashboard, one push to Anna.
    assert [b.message for b in summaries(entry)] == ["• Digest me"] * 2
    reasons = {e["reason"] for e in entry.runtime_data.hub.trace.entries()}
    assert not BAD_REASONS & reasons
    kinds = {i["kind"] for i in panel_data.attention(hass, entry.runtime_data, entry)}
    assert not {"reference_missing", "policy_target", "policy_invalid"} & kinds
    assert not any(
        p for p in entry.runtime_data.hub.policies.all() if entry.runtime_data.hub.policy_problem(p)
    )
