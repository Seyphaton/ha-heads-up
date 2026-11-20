"""Decided cells of the interaction matrix (docs/dev/policy-redesign/04-interaction-matrix.md,
D-235): one behaviour per test, named by its cell."""

from __future__ import annotations

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.panel_data import (
    check_escalation_log,
    check_escalation_traps,
    check_presence_conflicts,
)
from custom_components.heads_up.hub.policies.models import policy_from_data

from .conftest import AddDevice
from .policy_support import (
    CRITICAL_THROUGH,
    ESCALATION,
    FALLBACK,
    QUIET,
    SUMMARIZE,
    add_policy,
    make_household,
    move,
    pushes,
    send,
    shown,
    summaries,
    wait,
)

TO_BEN = {"push": {"recipients": ["person.ben"]}}


@pytest.fixture(autouse=True)
async def berlin(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")


def kinds(entry: MockConfigEntry) -> list[str]:
    return [e["kind"] for e in entry.runtime_data.hub.log.latest()]


async def test_o8_an_escalation_sends_again_to_people_who_already_have_the_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(
        hass, entry, "Again", **{**ESCALATION, "targets": {"push": {"recipients": ["person.anna"]}}}
    )
    await send(hass, entry)
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.anna)) == 2


async def test_o9_no_fallback_when_deliver_reached_someone(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(
        hass,
        entry,
        "To Ben",
        type="deliver",
        severities=["warning"],
        channels=["push"],
        targets=TO_BEN,
    )
    await add_policy(
        hass, entry, "Nobody", **{**FALLBACK, "targets": {"push": {"recipients": ["person.anna"]}}}
    )
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    assert len(pushes(home.ben)) == 1
    assert not pushes(home.anna)  # the Fallback did not step in


async def test_o1_deliver_recipients_get_the_summary(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await add_policy(hass, entry, "To Ben", type="deliver", channels=["push"], targets=TO_BEN)
    await send(hass, entry, severity="info")
    assert not pushes(home.ben)
    await wait(hass, entry, freezer, 61)
    assert any(s.channels == ["push"] for s in summaries(entry))
    assert len(pushes(home.ben)) == 1


async def test_o1b_a_summary_that_reaches_nobody_triggers_the_fallback(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await add_policy(hass, entry, "Failed", **{**FALLBACK, "when": "failed"})
    await send(hass, entry, severity="info")
    # Anna's phone refuses the summary: sending it fails.

    async def refuse(call: ServiceCall) -> None:
        raise HomeAssistantError("refused")

    hass.services.async_register("notify", home.anna.notify_service, refuse)
    await wait(hass, entry, freezer, 61)
    assert len(pushes(home.ben)) == 1


async def test_o2_a_band_entry_that_switches_on_takes_messages_out_of_the_summary(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await send(hass, entry)  # critical, no band entry yet: collected
    assert shown(entry) == [] and not pushes(home.anna)
    await add_policy(hass, entry, "Critical", **CRITICAL_THROUGH)
    assert shown(entry) == ["m"] and len(pushes(home.anna)) == 1


async def test_o2_a_band_entry_that_switches_on_releases_quiet_holds_it_covers(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry)
    assert not pushes(home.anna)
    await add_policy(hass, entry, "Critical", **CRITICAL_THROUGH)
    assert len(pushes(home.anna)) == 1


async def test_o3_an_escalation_caught_by_quiet_hours_is_logged_for_needs_attention(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    await add_policy(hass, entry, "Water", **ESCALATION)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    await wait(hass, entry, freezer, 5.1)
    assert "escalation_held" in kinds(entry)
    log = entry.runtime_data.hub.log.latest()
    from homeassistant.util import dt as dt_util

    (item,) = check_escalation_log(log, dt_util.utcnow())
    assert (item.kind, item.subject) == ("escalation_held", "Water")


async def test_o4_an_escalation_that_reaches_nobody_is_logged_and_no_fallback_steps_in(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Away", type="presence")
    await add_policy(
        hass,
        entry,
        "Nobody",
        **{**FALLBACK, "when": "both", "targets": {"push": {"recipients": ["person.anna"]}}},
    )
    await add_policy(hass, entry, "Water", **ESCALATION)
    move(hass, "person.ben", "not_home")
    await send(hass, entry, severity="warning")
    before = len(pushes(home.anna))
    await wait(hass, entry, freezer, 5.1)
    assert "escalation_unreached" in kinds(entry)
    assert len(pushes(home.anna)) == before


def made(name: str, **data: object):
    policy = policy_from_data(name, name, data)
    assert policy is not None
    return policy


def test_the_page_warns_before_an_escalation_runs_into_quiet_hours_or_presence() -> None:
    esc = made("Water", type="escalation", severities=["warning"], channels=["push"])
    night = made("Night", type="quiet_hours")
    away = made("Away", type="presence")
    found = {(a.kind, a.subject, a.detail) for a in check_escalation_traps([esc, night, away])}
    assert found == {
        ("escalation_quiet", "Water", "Night"),
        ("escalation_presence", "Water", "Away"),
    }
    band = made("Warnings", type="get_through", severities=["warning"])
    found = {a.kind for a in check_escalation_traps([esc, night, band])}
    assert found == set()  # a band entry for everyone covers the escalation's messages


def test_the_page_warns_about_presence_policies_that_contradict() -> None:
    first = made("Shopping", type="presence", tags=["shopping"], presence_when="in")
    second = made("Away", type="presence")
    (item,) = check_presence_conflicts([first, second])
    assert (item.kind, item.subject, item.detail) == ("presence_conflict", "Shopping", "Away")
    other_zone = made("Work", type="presence", zone="zone.work", presence_when="in")
    assert check_presence_conflicts([other_zone, second]) == []
