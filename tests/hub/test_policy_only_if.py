"""Only if on policies, Faster while and one repeat rhythm (D-216, D-234, D-235, DESIGN §25)."""

from __future__ import annotations

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    AWAY,
    CRITICAL_THROUGH,
    ESCALATION,
    QUIET,
    add_policy,
    make_household,
    move,
    pushes,
    send,
    wait,
)

X = "input_boolean.window"
WHEN_X = {"entity_id": X, "state": "on"}


@pytest.fixture(autouse=True)
async def berlin(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")


async def switch(hass: HomeAssistant, entry: MockConfigEntry, state: str, entity: str = X) -> None:
    hass.states.async_set(entity, state)
    await hass.async_block_till_done()
    await settle(hass, entry)


async def test_a_hold_with_a_false_only_if_does_not_hold(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "off")
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait", "only_if": WHEN_X})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1
    await switch(hass, entry, "on")
    await send(hass, entry, id="n", severity="warning")
    assert len(pushes(home.anna)) == 1  # held now


async def test_unknown_only_if_holds_step_aside_and_senders_act(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    unknown = {"entity_id": "input_boolean.missing", "state": "on"}
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait", "only_if": unknown})
    await add_policy(
        hass,
        entry,
        "To Ben",
        type="deliver",
        channels=["push"],
        targets={"push": {"recipients": ["person.ben"]}},
        only_if=unknown,
    )
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1


async def test_a_held_delivery_is_released_when_its_only_if_turns_false(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "on")
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait", "only_if": WHEN_X})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert not pushes(home.anna)
    await switch(hass, entry, "off")
    assert len(pushes(home.anna)) == 1


async def test_guests_through_only_if_presence_steps_aside_while_guest_mode_is_on(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    guests = "input_boolean.guests"
    hass.states.async_set(guests, "off")
    await add_policy(
        hass, entry, "Away", **{**AWAY, "only_if": {"entity_id": guests, "state": "off"}}
    )
    move(hass, "person.anna", "not_home")
    await send(hass, entry, severity="warning")
    assert not pushes(home.anna)
    await switch(hass, entry, "on", guests)
    assert len(pushes(home.anna)) == 1


async def test_two_reminders_share_one_rhythm_and_keep_their_own_counts(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Scenario 5 with two policies: 15 min only if X (at most 8), 60 min (at most 3)."""
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "off")
    await add_policy(
        hass, entry, "Urgent", type="reminder", every_minutes=15, max_count=8, only_if=WHEN_X
    )
    await add_policy(hass, entry, "Hourly", type="reminder", every_minutes=60, max_count=3)
    freezer.move_to("2026-11-02 00:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 14)
    await switch(hass, entry, "on")  # 00:14
    await wait(hass, entry, freezer, 1.1)  # 00:15
    assert len(pushes(home.anna)) == 2
    await wait(hass, entry, freezer, 15)  # 00:30
    await wait(hass, entry, freezer, 15)  # 00:45
    assert len(pushes(home.anna)) == 4
    await wait(hass, entry, freezer, 5)  # 00:50
    await switch(hass, entry, "off")
    await wait(hass, entry, freezer, 50)  # 01:40: Hourly waits for 00:45 + 60
    assert len(pushes(home.anna)) == 4
    await wait(hass, entry, freezer, 6)  # 01:46
    assert len(pushes(home.anna)) == 5


async def test_faster_while_repeats_at_once_when_the_faster_rhythm_is_already_due(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "off")
    await add_policy(
        hass,
        entry,
        "Warnings",
        type="reminder",
        every_minutes=60,
        max_count=12,
        faster_while={"condition": WHEN_X, "every_minutes": 15},
    )
    freezer.move_to("2026-11-02 00:00:00+01:00")
    await send(hass, entry, severity="warning")
    await wait(hass, entry, freezer, 16)
    assert len(pushes(home.anna)) == 1
    await switch(hass, entry, "on")  # 00:16: 00:00 + 15 is past, so repeat now
    await wait(hass, entry, freezer, 0.1)
    assert len(pushes(home.anna)) == 2
    await wait(hass, entry, freezer, 15.1)
    assert len(pushes(home.anna)) == 3


async def test_runs_alongside_keeps_its_own_rhythm(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Fast", type="reminder", every_minutes=10, max_count=5)
    await add_policy(
        hass, entry, "Slow", type="reminder", every_minutes=30, max_count=5, alongside=True
    )
    await send(hass, entry, severity="warning")
    for _ in range(3):
        await wait(hass, entry, freezer, 10.05)
    # Fast at 10, 20, 30 and Slow at 30 next to it.
    assert len(pushes(home.anna)) == 1 + 3 + 1


async def test_an_escalation_waits_for_its_only_if_and_fires_when_it_turns_true(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "off")
    await add_policy(hass, entry, "Water", **{**ESCALATION, "only_if": WHEN_X})
    await send(hass, entry)
    await wait(hass, entry, freezer, 10)
    assert not pushes(home.ben)
    await switch(hass, entry, "on")
    assert len(pushes(home.ben)) == 1


async def test_a_band_entry_whose_only_if_turns_true_releases_the_quiet_hold(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set(X, "off")
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    await add_policy(hass, entry, "Critical", **{**CRITICAL_THROUGH, "only_if": WHEN_X})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry)
    assert not pushes(home.anna)
    await switch(hass, entry, "on")
    assert len(pushes(home.anna)) == 1
