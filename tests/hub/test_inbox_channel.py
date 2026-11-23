"""The inbox channel: delivery, lifecycle, reminders, policies (Phase 22, D-264, D-268)."""

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    QUIET,
    REMINDER,
    add_policy,
    make_household,
    pushes,
    send,
    trace,
    wait,
)

ANNA = "person.anna"
BEN = "person.ben"
TO_ANNA = {"inbox": {"recipients": [ANNA]}}
TO_BOTH = {"inbox": {"recipients": [ANNA, BEN]}}


def inbox(entry: MockConfigEntry):  # type: ignore[no-untyped-def]
    return entry.runtime_data.hub.inbox


async def inbox_only(
    hass: HomeAssistant, entry: MockConfigEntry, to: dict | None = None, **kw: object
) -> None:
    await send(hass, entry, channels=["inbox"], to=to or TO_ANNA, **kw)


@pytest.fixture(autouse=True)
async def berlin(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")


# Delivery --------------------------------------------------------------------------------


async def test_a_message_to_the_inbox_makes_an_item_and_nothing_else(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await inbox_only(hass, entry, title="Leak", message="Water in the cellar", icon="mdi:water")
    item = inbox(entry).get(ANNA, "m")
    assert item is not None
    assert (item.title, item.text, item.severity) == ("Leak", "Water in the cellar", "critical")
    assert item.icon == "mdi:water" and item.via == ["inbox"] and item.read_at is None
    assert not pushes(home.anna) and not pushes(home.ben)
    assert inbox(entry).get(BEN, "m") is None
    assert any(e["channel"] == "inbox" and e["result"] == "sent" for e in trace(entry))


async def test_a_person_without_a_phone_still_gets_the_item(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await inbox_only(hass, entry)
    assert inbox(entry).get(ANNA, "m") is not None


async def test_an_audience_reaches_every_member(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    everyone = {"inbox": {"audience": "binary_sensor.heads_up_audience_everyone"}}
    await inbox_only(hass, entry, to=everyone)
    assert inbox(entry).get(ANNA, "m") is not None and inbox(entry).get(BEN, "m") is not None


async def test_the_inbox_keeps_the_text_of_a_message_that_also_went_to_push_and_banner(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(
        hass,
        entry,
        channels=["banner", "push", "inbox"],
        to={"push": {"recipients": [ANNA]}, "inbox": {"recipients": [ANNA]}},
    )
    assert len(pushes(home.anna)) == 1
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.text == "Water leak"


async def test_a_call_that_names_the_inbox_needs_a_target(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(Exception, match="inbox needs a target"):
        await hass.services.async_call(
            DOMAIN,
            "notify",
            {"id": "x", "message": "hi", "channels": ["inbox"]},
            blocking=True,
        )


async def test_the_inbox_is_not_limited_by_the_push_caps(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    for n in range(12):
        await inbox_only(hass, entry, id=f"m{n}", message=f"text {n}")
    assert len(inbox(entry).items(ANNA)) == 12


# Updates and the end ------------------------------------------------------------------------


async def test_an_update_changes_the_same_item_and_marks_it_unread(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await inbox_only(hass, entry, message="first")
    inbox(entry).mark_read(ANNA, "m", dt_util.utcnow())
    await inbox_only(hass, entry, message="second")
    items = inbox(entry).items(ANNA)
    assert len(items) == 1 and items[0].text == "second" and items[0].read_at is None


async def test_clearing_the_message_resolves_the_item_and_keeps_it_unread(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await inbox_only(hass, entry)
    await hass.services.async_call(DOMAIN, "clear_notifications", {"id": "m"}, blocking=True)
    await hass.async_block_till_done()
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.resolved_reason == "cleared" and item.read_at is None


async def test_a_timeout_resolves_the_item_as_expired(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await inbox_only(hass, entry, timeout=300)
    await wait(hass, entry, freezer, 6)
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.resolved_reason == "expired"


async def test_acknowledging_reads_the_acknowledgers_item_and_only_logs_it_for_others(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await inbox_only(hass, entry, to=TO_BOTH)
    entry.runtime_data.acknowledge("m", "anna-id", any_message=True)
    await hass.async_block_till_done()
    anna, ben = inbox(entry).get(ANNA, "m"), inbox(entry).get(BEN, "m")
    assert anna is not None and anna.acknowledged_at is not None and anna.read_at is not None
    assert ben is not None and ben.acknowledged_at is None and ben.read_at is None
    assert ben.timeline[-1]["kind"] == "acknowledged_by_other"


async def test_dismissing_resolves_only_the_dismissers_item(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, channels=["banner", "inbox"], to=TO_BOTH, dismiss="user")
    entry.runtime_data.dismiss("m", "anna-id")
    await hass.async_block_till_done()
    anna, ben = inbox(entry).get(ANNA, "m"), inbox(entry).get(BEN, "m")
    assert anna is not None and anna.resolved_reason == "dismissed" and anna.read_at is not None
    assert ben is not None and ben.resolved_at is None and ben.read_at is None


async def test_a_dismissal_for_everyone_resolves_all_items_and_reads_the_dismissers(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, channels=["banner", "inbox"], to=TO_BOTH, dismiss="everyone")
    entry.runtime_data.dismiss("m", "anna-id")
    await hass.async_block_till_done()
    anna, ben = inbox(entry).get(ANNA, "m"), inbox(entry).get(BEN, "m")
    assert anna is not None and anna.resolved_reason == "dismissed" and anna.read_at is not None
    assert ben is not None and ben.resolved_reason == "dismissed" and ben.read_at is None


async def test_a_snooze_changes_nothing_in_the_inbox(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(
        hass,
        entry,
        channels=["banner", "inbox"],
        to=TO_ANNA,
        snooze="user",
        snooze_options=[{"minutes": 15}],
    )
    entry.runtime_data.snooze("m", "anna-id", 900)
    await hass.async_block_till_done()
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.resolved_at is None and item.read_at is None


async def test_a_message_that_ended_while_stopped_is_resolved_at_the_start(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    fields = {"title": "Old", "text": "gone", "severity": "info"}
    inbox(entry).upsert(ANNA, "ghost", fields, "inbox", dt_util.utcnow())
    await restart(hass, entry)
    item = inbox(entry).get(ANNA, "ghost")
    assert item is not None and item.resolved_reason == "cleared" and item.read_at is None


# Reminders and escalations -----------------------------------------------------------------


async def test_a_reminder_adds_a_timeline_entry_and_brings_a_read_item_back(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await add_policy(hass, entry, "Nag", **REMINDER)
    await inbox_only(hass, entry)
    inbox(entry).mark_read(ANNA, "m", dt_util.utcnow())
    await wait(hass, entry, freezer, 10.1)
    items = inbox(entry).items(ANNA)
    assert len(items) == 1 and items[0].reminders == 1 and items[0].read_at is None
    assert [e["kind"] for e in items[0].timeline] == ["sent", "reminder"]


async def test_the_setting_can_keep_a_read_item_read_through_a_reminder(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    entry.runtime_data.options["inbox_reminder_unread"] = False
    await add_policy(hass, entry, "Nag", **REMINDER)
    await inbox_only(hass, entry)
    inbox(entry).mark_read(ANNA, "m", dt_util.utcnow())
    await wait(hass, entry, freezer, 10.1)
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.reminders == 1 and item.read_at is not None


async def test_an_escalation_to_the_inbox_makes_an_item_for_the_other_person(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(
        hass,
        entry,
        "Up",
        type="escalation",
        after_minutes=5,
        channels=["inbox"],
        targets={"inbox": {"recipients": [BEN]}},
    )
    await inbox_only(hass, entry)
    assert inbox(entry).get(BEN, "m") is None
    await wait(hass, entry, freezer, 5.1)
    ben = inbox(entry).get(BEN, "m")
    assert ben is not None and ben.via == ["inbox"]


# Policies --------------------------------------------------------------------------------


async def test_quiet_hours_with_wait_hold_the_inbox_like_any_channel(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await inbox_only(hass, entry, severity="warning")
    assert inbox(entry).get(ANNA, "m") is None
    await wait(hass, entry, freezer, 8 * 60 + 1)
    assert inbox(entry).get(ANNA, "m") is not None


async def test_leaving_the_inbox_out_of_quiet_hours_delivers_it_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"}, channels=["push"])
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await inbox_only(hass, entry, severity="warning")
    assert inbox(entry).get(ANNA, "m") is not None


async def test_quiet_hours_with_drop_leave_no_item(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "drop"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await inbox_only(hass, entry, severity="warning")
    assert inbox(entry).get(ANNA, "m") is None


# Parity of the banner sources (DESIGN §22, D-073) ------------------------------------------

DELIVER_INBOX = {
    "type": "deliver",
    "channels": ["inbox"],
    "targets": {"inbox": {"recipients": [ANNA]}},
}


async def test_an_action_message_reaches_the_inbox_through_a_deliver_policy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "To the inbox", **DELIVER_INBOX)
    await send(hass, entry, channels=["banner"], to={})
    assert inbox(entry).get(ANNA, "m") is not None


async def test_a_rule_message_reaches_the_inbox_through_a_deliver_policy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "To the inbox", **DELIVER_INBOX)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="warning")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    (item,) = inbox(entry).items(ANNA)
    assert item.severity == "warning" and item.source is not None and item.via == ["inbox"]


async def test_a_rule_that_triggers_again_reopens_the_same_item(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "To the inbox", **DELIVER_INBOX)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="warning")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    hass.states.async_set(WINDOW, "off")
    await settle(hass, entry)
    (item,) = inbox(entry).items(ANNA)
    assert item.resolved_reason == "condition"
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    (again,) = inbox(entry).items(ANNA)
    assert again.resolved_at is None and again.read_at is None


async def test_quiet_hours_with_send_quietly_do_not_mark_the_inbox_quiet(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    # Quiet means no sound, which an inbox item has none of: the row says sent, not quiet.
    hass.states.async_set(ANNA, "home", {"user_id": "anna-id"})
    await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    result = await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "message": "x",
            "severity": "warning",
            "channels": ["inbox"],
            "recipients": [ANNA],
            "dry_run": True,
        },
        blocking=True,
        return_response=True,
    )
    (row,) = [r for r in result["rows"] if r["channel"] == "inbox"]
    assert row["result"] == "sent" and row.get("note") != "quiet"
