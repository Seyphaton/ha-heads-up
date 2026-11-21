"""What the engine records into the history, and that a fault never reaches a delivery (19.2)."""

from datetime import timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.stats import StatsStore, bucket_of

from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    SUMMARIZE,
    add_policy,
    make_household,
    send,
    wait,
)


def today(entry: MockConfigEntry) -> dict[str, Any]:
    days = entry.runtime_data.hub.stats.days
    assert len(days) == 1, days
    return next(iter(days.values()))


async def test_a_message_from_an_action_counts_as_created_with_its_severity_and_tag(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, id="a", severity="warning", tag="door")
    day = today(entry)
    assert sum(day["h"]) == 1 and day["sev"] == {"warning": 1}
    assert day["tag"] == {"door": 1} and day["src"] == {"action": 1}


async def test_a_message_from_a_watch_rule_is_recorded_under_its_rule_id(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    rule = add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    day = today(entry)
    assert sum(day["h"]) == 1 and day["sev"] == {"critical": 1}
    assert list(day["src"]) == [f"rule_{rule.subentry_id}"]


async def test_deliveries_count_per_channel_person_and_reason(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, to={"push": {"recipients": ["person.anna"]}})
    day = today(entry)
    assert day["ch"]["push"]["sent"] == 1
    assert day["per"]["person.anna"] == {"push|sent": 1}
    assert day["ch"]["banner"]["sent"] == 1


async def test_a_quiet_hours_hold_counts_as_held_with_the_policy_key_not_its_name(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    await make_household(hass, mobile_app_device)
    night = await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    day = today(entry)
    assert day["rs"]["push|held|quiet_hours"] == 1
    assert day["pol"] == {night.subentry_id: {"held": 1}}
    hass.config_entries.async_update_subentry(entry, night, title="Renamed", data=night.data)
    await hass.async_block_till_done()
    await send(hass, entry, id="b", severity="warning")
    assert list(today(entry)["pol"]) == [night.subentry_id]  # a rename does not split the history


async def test_an_acknowledgement_counts_its_time_and_the_escalation_it_avoided(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await wait(hass, entry, freezer, 2)
    entry.runtime_data.acknowledge("m", "anna-id")
    await settle(hass, entry)
    day = today(entry)
    assert day["ack"]["critical"][bucket_of(120)] == 1 and day["avoid"] == 1


async def test_an_acknowledgement_after_the_escalation_fired_avoids_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    water = await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await wait(hass, entry, freezer, 6)
    entry.runtime_data.acknowledge("m", "anna-id")
    await settle(hass, entry)
    day = today(entry)
    assert "avoid" not in day and day["pol"][water.subentry_id]["escalated"] == 1


async def test_reminders_snoozes_dismissals_and_the_end_of_a_message_are_counted(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    nag = await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, id="r", severity="warning", snooze="user", timeout={"minutes": 30})
    await wait(hass, entry, freezer, 11)
    entry.runtime_data.snooze("r", "anna-id", 900)
    await send(hass, entry, id="d", severity="info")
    entry.runtime_data.dismiss("d", "anna-id")
    await wait(hass, entry, freezer, 40)
    day = today(entry)
    assert day["pol"][nag.subentry_id]["reminded"] >= 1
    assert day["snz"] == 1 and day.get("dis") == 1
    assert day["end"].get("expired", 0) >= 1 and sum(day["te"]) >= 1


async def test_messages_held_for_a_summary_count_as_summarized_for_the_policy(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    digest = await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(hass, entry, id="h1", severity="warning", tag="digest")
    await send(hass, entry, id="h2", severity="warning", tag="digest")
    await wait(hass, entry, freezer, 61)
    day = today(entry)
    assert day["pol"][digest.subentry_id]["summarized"] == 2
    assert day["src"] == {"action": 2}  # the summary itself is not a created message


async def test_a_fault_in_the_history_does_not_stop_a_delivery(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    monkeypatch: Any,
) -> None:
    home = await make_household(hass, mobile_app_device)

    def broken(self: StatsStore, now: Any) -> Any:
        raise RuntimeError("history is broken")

    monkeypatch.setattr(StatsStore, "_day", broken)
    await send(hass, entry)
    assert len(home.anna.calls) == 1
    assert entry.runtime_data.banners["m"].active


async def test_the_day_is_the_local_day_of_the_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    key = dt_util.now().date().isoformat()
    assert list(entry.runtime_data.hub.stats.days) == [key]
    assert dt_util.now() - timedelta(0) is not None
