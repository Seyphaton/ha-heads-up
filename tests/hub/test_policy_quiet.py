"""Quiet hours: a window on the local clock; quiet, wait or drop (D-112)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.policies.models import Policy
from custom_components.heads_up.hub.policies.quiet import window_end

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    add_policy,
    make_household,
    pushes,
    send,
    trace,
    wait,
)

BERLIN = ZoneInfo("Europe/Berlin")


def policy(**kw: object) -> Policy:
    return Policy(name="Q", type="quiet_hours", **kw)  # type: ignore[arg-type]


def at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=BERLIN)


# The window itself -----------------------------------------------------------------------


def test_a_window_inside_one_day_ends_the_same_day() -> None:
    p = policy(from_time="13:00:00", to_time="15:00:00")
    assert window_end(p, at("2026-11-02T14:00:00")) == at("2026-11-02T15:00:00")
    assert window_end(p, at("2026-11-02T15:00:00")) is None  # the end itself is outside
    assert window_end(p, at("2026-11-02T12:59:00")) is None


def test_a_window_across_midnight_ends_the_next_morning_or_the_same_morning() -> None:
    p = policy()
    assert window_end(p, at("2026-11-02T23:00:00")) == at("2026-11-03T07:00:00")
    assert window_end(p, at("2026-11-03T06:59:00")) == at("2026-11-03T07:00:00")
    assert window_end(p, at("2026-11-03T07:00:00")) is None
    assert window_end(p, at("2026-11-02T21:59:00")) is None


def test_days_name_the_day_a_window_starts_on() -> None:
    p = policy(days=("fri",))  # Friday night to Saturday morning
    assert window_end(p, at("2026-11-06T23:00:00")) is not None  # Friday 23:00
    assert window_end(p, at("2026-11-07T03:00:00")) is not None  # Saturday 03:00
    assert window_end(p, at("2026-11-07T23:00:00")) is None  # Saturday night
    assert window_end(p, at("2026-11-06T03:00:00")) is None  # Friday morning belongs to Thursday


def test_equal_start_and_end_is_no_window() -> None:
    assert (
        window_end(policy(from_time="08:00:00", to_time="08:00:00"), at("2026-11-02T08:00:00"))
        is None
    )


def test_on_the_day_the_clocks_go_forward_the_window_keeps_its_wall_clock_times() -> None:
    # Europe/Berlin, 2027-03-28: 02:00 becomes 03:00, so the night is an hour shorter.
    end = window_end(policy(), at("2027-03-27T23:00:00"))
    assert end is not None and end.hour == 7 and end.date().isoformat() == "2027-03-28"
    hours = end.astimezone(ZoneInfo("UTC")) - at("2027-03-27T23:00:00").astimezone(ZoneInfo("UTC"))
    assert hours.total_seconds() == 7 * 3600  # 8 wall-clock hours minus the skipped one


def test_on_the_day_the_clocks_go_back_the_window_is_an_hour_longer() -> None:
    end = window_end(policy(), at("2026-10-24T23:00:00"))
    assert end is not None and end.hour == 7 and end.date().isoformat() == "2026-10-25"
    span = end.astimezone(ZoneInfo("UTC")) - at("2026-10-24T23:00:00").astimezone(ZoneInfo("UTC"))
    assert span.total_seconds() == 9 * 3600


def test_a_time_that_does_not_exist_or_occurs_twice_uses_its_first_occurrence() -> None:
    utc = ZoneInfo("UTC")
    skipped = window_end(
        policy(from_time="01:00:00", to_time="02:30:00"), at("2027-03-28T01:30:00")
    )
    assert (
        skipped is not None and skipped.astimezone(utc).isoformat() == "2027-03-28T01:30:00+00:00"
    )
    repeated = window_end(
        policy(from_time="01:00:00", to_time="02:30:00"), at("2026-10-25T01:30:00")
    )
    assert (
        repeated is not None and repeated.astimezone(utc).isoformat() == "2026-10-25T00:30:00+00:00"
    )


# In the hub ------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def berlin(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")


async def test_quiet_sends_a_passive_push(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    (call,) = pushes(home.anna)
    assert call.data["data"]["importance"] == "low"
    assert call.data["data"]["channel"].endswith("passive")


async def test_outside_the_window_a_push_is_normal(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 12:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert pushes(home.anna)[0].data["data"]["importance"] == "default"


async def test_critical_passes_by_default_and_not_when_the_policy_says_so(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry)
    assert pushes(home.anna)[0].data["data"]["importance"] == "high"
    quiet_critical = {**QUIET, "critical_passes": False}
    (sub,) = [s for s in entry.subentries.values() if s.title == "Night"]
    hass.config_entries.async_update_subentry(entry, sub, data=quiet_critical)
    await hass.async_block_till_done()
    await send(hass, entry, id="n")
    assert pushes(home.anna)[1].data["data"]["importance"] == "low"


async def test_wait_holds_the_push_until_the_end_of_the_window_then_sends_it_once(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert not pushes(home.anna)
    await wait(hass, entry, freezer, 8 * 60 - 1)  # 06:59
    assert not pushes(home.anna)
    await wait(hass, entry, freezer, 2)  # 07:01
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 60)
    assert len(pushes(home.anna)) == 1


async def test_a_held_push_survives_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    await restart(hass, entry)
    await settle(hass, entry)
    assert not pushes(home.anna)
    await wait(hass, entry, freezer, 8 * 60 + 1)  # 07:01
    assert len(pushes(home.anna)) == 1


async def test_a_held_push_is_not_sent_when_the_message_was_cleared_meanwhile(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    entry.runtime_data.admin_clear("m")
    await wait(hass, entry, freezer, 9 * 60)
    assert not pushes(home.anna)


async def test_drop_skips_the_delivery_and_the_trace_says_why(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "drop"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert not pushes(home.anna)
    assert any(e["reason"] == "quiet_hours" and e["result"] == "skipped" for e in trace(entry))


async def test_the_banner_is_not_affected(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "drop"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert [b["id"] for b in entry.runtime_data.visible("anna-id")] == ["m"]


async def test_a_reminder_in_the_window_is_skipped_not_held(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    freezer.move_to("2026-11-02 21:55:00+01:00")
    await add_policy(hass, entry, "Nag", **REMINDER)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 10)  # 22:05, inside the window
    assert len(pushes(home.anna)) == 1
    assert any(e["reason"] == "quiet_hours" for e in trace(entry))


async def test_an_escalation_of_a_rule_message_follows_quiet_hours(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    from ..test_rules import WINDOW, add_rule

    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Rules", **ESCALATION, tags=["rule"])
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "drop", "critical_passes": False})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
