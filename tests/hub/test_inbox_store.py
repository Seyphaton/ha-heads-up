"""The personal inbox store: items, read state, retention, cap, damage (Phase 22, D-264, D-270)."""

from datetime import UTC, datetime, timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.heads_up.const import (
    INBOX_KEY,
    INBOX_MAX_ITEMS,
    INBOX_PURGE_GRACE,
    INBOX_SAVE_DELAY,
)
from custom_components.heads_up.hub.inbox import InboxStore

from ..test_restart import restart

NOW = datetime(2026, 11, 23, 12, 0, tzinfo=UTC)
ANNA = "person.anna"
BEN = "person.ben"


def fields(**kw: Any) -> dict[str, Any]:
    return {
        "title": "Washer",
        "text": "The washing machine is done",
        "severity": "info",
        "icon": "mdi:washing-machine",
        "color": None,
        "image": None,
        "source": "tag:washer",
        "tag": "washer",
        **kw,
    }


def put(inbox: InboxStore, person: str = ANNA, mid: str = "m", **kw: Any) -> Any:
    now = kw.pop("now", NOW)
    channel = kw.pop("channel", "push")
    return inbox.upsert(person, mid, fields(**kw), channel, now)


async def make(hass: HomeAssistant) -> InboxStore:
    inbox = InboxStore(hass)
    await inbox.async_load()
    return inbox


# Items -----------------------------------------------------------------------------------


async def test_a_new_message_is_an_unread_item_with_one_timeline_entry(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    item = put(inbox)
    assert item.read_at is None and item.resolved_at is None
    assert item.via == ["push"] and item.created == NOW and item.updated == NOW
    assert [e["kind"] for e in item.timeline] == ["sent"]
    assert inbox.unread_count(ANNA) == 1


async def test_the_same_message_again_adds_the_channel_and_keeps_the_read_state(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.mark_read(ANNA, "m", NOW)
    item = put(inbox, channel="popup", now=NOW + timedelta(seconds=5))
    assert item.via == ["push", "popup"]
    assert item.read_at == NOW
    assert len(item.timeline) == 1  # the same content is not a new event


async def test_changed_text_or_a_higher_severity_marks_the_item_unread(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.mark_read(ANNA, "m", NOW)
    later = NOW + timedelta(minutes=1)
    item = put(inbox, text="Now it is spinning again", now=later)
    assert item.read_at is None and item.updated == later and item.text.startswith("Now")
    inbox.mark_read(ANNA, "m", later)
    item = put(inbox, text="Now it is spinning again", severity="critical", now=later)
    assert item.read_at is None and item.severity == "critical"
    assert [e["kind"] for e in item.timeline][-1] == "updated"


async def test_a_lower_severity_does_not_mark_a_read_item_unread(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, severity="critical")
    inbox.mark_read(ANNA, "m", NOW)
    item = put(inbox, severity="info")  # same text, lower severity
    assert item.read_at == NOW and item.severity == "info"


async def test_a_resolved_message_that_comes_back_is_the_same_item_unread_again(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.resolve("m", "condition", NOW)
    inbox.mark_read(ANNA, "m", NOW)
    item = put(inbox, now=NOW + timedelta(hours=1))
    assert item.resolved_at is None and item.resolved_reason is None and item.read_at is None
    assert len(inbox.items(ANNA)) == 1


async def test_two_people_have_separate_items(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, ANNA)
    put(inbox, BEN)
    inbox.mark_read(ANNA, "m", NOW)
    assert inbox.unread_count(ANNA) == 0 and inbox.unread_count(BEN) == 1
    assert inbox.items("person.nobody") == []


# Reminders, acknowledgement, ending ------------------------------------------------------


async def test_a_reminder_adds_a_timeline_entry_and_may_mark_the_item_unread(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.mark_read(ANNA, "m", NOW)
    inbox.add_event(ANNA, "m", "reminder", "push", NOW, reminder_unread=False)
    item = inbox.get(ANNA, "m")
    assert item is not None and item.read_at == NOW and item.reminders == 1
    inbox.add_event(ANNA, "m", "reminder", "push", NOW, reminder_unread=True)
    item = inbox.get(ANNA, "m")
    assert item is not None and item.read_at is None and item.reminders == 2
    assert [e["kind"] for e in item.timeline] == ["sent", "reminder", "reminder"]
    assert len(inbox.items(ANNA)) == 1  # never a second row


async def test_an_escalation_follows_the_same_unread_setting_as_a_reminder(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.mark_read(ANNA, "m", NOW)
    inbox.add_event(ANNA, "m", "escalation", "push", NOW, reminder_unread=True)
    item = inbox.get(ANNA, "m")
    assert item is not None and item.read_at is None and item.reminders == 0
    assert item.timeline[-1]["kind"] == "escalation"


async def test_the_timeline_keeps_the_first_entry_and_the_latest_nine(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox)
    for n in range(20):
        inbox.add_event(ANNA, "m", "reminder", "push", NOW + timedelta(minutes=n), True)
    item = inbox.get(ANNA, "m")
    assert item is not None and len(item.timeline) == 10
    assert item.timeline[0]["kind"] == "sent"
    assert item.timeline[-1]["at"] == (NOW + timedelta(minutes=19)).isoformat()


async def test_acknowledging_marks_that_persons_item_read_and_only_logs_it_for_others(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox, ANNA)
    put(inbox, BEN)
    inbox.acknowledged("m", ANNA, NOW)
    anna, ben = inbox.get(ANNA, "m"), inbox.get(BEN, "m")
    assert anna is not None and anna.acknowledged_at == NOW and anna.read_at == NOW
    assert ben is not None and ben.acknowledged_at is None and ben.read_at is None
    assert ben.timeline[-1]["kind"] == "acknowledged_by_other"


async def test_an_ended_message_stays_resolved_and_unread(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox)
    inbox.resolve("m", "expired", NOW + timedelta(minutes=5))
    item = inbox.get(ANNA, "m")
    assert item is not None and item.resolved_reason == "expired" and item.read_at is None
    assert inbox.unread_count(ANNA) == 1
    assert item.timeline[-1]["kind"] == "resolved"


async def test_dismissing_marks_the_persons_item_read_and_resolved(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, ANNA)
    put(inbox, BEN)
    inbox.dismissed("m", ANNA, NOW)
    anna, ben = inbox.get(ANNA, "m"), inbox.get(BEN, "m")
    assert anna is not None and anna.read_at == NOW and anna.resolved_reason == "dismissed"
    assert ben is not None and ben.resolved_at is None and ben.read_at is None


async def test_a_global_dismissal_resolves_everyones_item_but_reads_only_the_dismissers(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox, ANNA)
    put(inbox, BEN)
    inbox.resolve("m", "dismissed", NOW)
    inbox.mark_read(ANNA, "m", NOW)
    ben = inbox.get(BEN, "m")
    assert ben is not None and ben.resolved_reason == "dismissed" and ben.read_at is None


async def test_mark_all_read_changes_only_that_persons_unread_items(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    for n in range(3):
        put(inbox, ANNA, f"m{n}")
    put(inbox, BEN, "m0")
    inbox.mark_read(ANNA, "m0", NOW)
    assert inbox.mark_read_all(ANNA, NOW) == 2
    assert inbox.unread_count(ANNA) == 0 and inbox.unread_count(BEN) == 1


# Counts ----------------------------------------------------------------------------------


async def test_needs_action_counts_open_critical_items_nobody_acknowledged(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    put(inbox, mid="leak", severity="critical")
    put(inbox, mid="door", severity="critical")
    put(inbox, mid="washer")
    inbox.acknowledged("door", ANNA, NOW)
    assert inbox.needs_action(ANNA) == 1
    assert inbox.unread_critical(ANNA) == 1
    inbox.resolve("leak", "cleared", NOW)
    assert inbox.needs_action(ANNA) == 0  # an ended message needs nothing
    assert inbox.unread_count(ANNA) == 2  # the resolved one is still unread


# Retention and cap -----------------------------------------------------------------------


async def test_items_older_than_the_retention_are_removed(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, mid="old", now=NOW - timedelta(days=400))
    put(inbox, mid="new", now=NOW - timedelta(days=100))
    assert inbox.prune(NOW, months=12) == 1
    assert [i.message_id for i in inbox.items(ANNA)] == ["new"]
    assert inbox.prune(NOW, months=1) == 1 and inbox.items(ANNA) == []


async def test_over_the_cap_the_oldest_read_and_resolved_items_go_first(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    base = NOW - timedelta(days=30)
    for n in range(INBOX_MAX_ITEMS):
        put(inbox, mid=f"m{n}", now=base + timedelta(seconds=n))
    inbox.mark_read(ANNA, "m5", NOW)
    inbox.resolve("m5", "cleared", NOW)  # read and resolved, but not the oldest
    put(inbox, mid="extra", now=NOW)  # one over the cap
    assert inbox.prune(NOW, months=12) == 1
    ids = {i.message_id for i in inbox.items(ANNA)}
    assert "m5" not in ids and "m0" in ids and "extra" in ids
    assert len(ids) == INBOX_MAX_ITEMS


async def test_over_the_cap_with_only_unread_items_the_oldest_goes(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    base = NOW - timedelta(days=30)
    for n in range(INBOX_MAX_ITEMS + 2):
        put(inbox, mid=f"m{n}", now=base + timedelta(seconds=n))
    assert inbox.prune(NOW, months=12) == 2
    ids = {i.message_id for i in inbox.items(ANNA, limit=INBOX_MAX_ITEMS + 5)}
    assert "m0" not in ids and "m1" not in ids and "m2" in ids


async def test_the_cap_is_per_person(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    for n in range(INBOX_MAX_ITEMS):
        put(inbox, ANNA, f"m{n}")
    put(inbox, BEN)
    assert inbox.prune(NOW, months=12) == 0


async def test_removing_a_person_or_clearing_deletes_their_items(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, ANNA)
    put(inbox, BEN)
    assert inbox.purge_person(ANNA) == 1 and inbox.items(ANNA) == []
    assert inbox.purge_person(ANNA) == 0
    put(inbox, ANNA)
    assert inbox.clear() == 2 and inbox.items(BEN) == []


async def test_deleting_one_item_leaves_the_rest(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, mid="a")
    put(inbox, mid="b")
    assert inbox.delete(ANNA, "a") is True and inbox.delete(ANNA, "a") is False
    assert [i.message_id for i in inbox.items(ANNA)] == ["b"]


async def test_items_are_listed_newest_first_in_pages(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    for n in range(5):
        put(inbox, mid=f"m{n}", now=NOW + timedelta(minutes=n))
    assert [i.message_id for i in inbox.items(ANNA, limit=2)] == ["m4", "m3"]
    assert [i.message_id for i in inbox.items(ANNA, limit=2, offset=2)] == ["m2", "m1"]


# Storage ---------------------------------------------------------------------------------


async def test_items_survive_a_restart_with_every_field(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    put(inbox, severity="critical", image="/local/x.png", color="#ff0000")
    inbox.add_event(ANNA, "m", "reminder", "push", NOW, True)
    inbox.acknowledged("m", ANNA, NOW)
    inbox.resolve("m", "cleared", NOW)
    await inbox.async_save()
    again = await make(hass)
    before, after = inbox.get(ANNA, "m"), again.get(ANNA, "m")
    assert before is not None and after is not None and after == before


async def test_a_damaged_item_is_dropped_and_the_rest_is_kept(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    good = {
        "title": "T",
        "text": "x",
        "severity": "info",
        "created": NOW.isoformat(),
        "updated": NOW.isoformat(),
        "via": ["push"],
        "timeline": [],
        "reminders": 0,
    }
    hass_storage[INBOX_KEY] = {
        "version": 1,
        "minor_version": 1,
        "key": INBOX_KEY,
        "data": {
            "items": {
                ANNA: {
                    "ok": good,
                    "no_time": {**good, "created": "not a time"},
                    "no_severity": {**good, "severity": "loud"},
                    "not_a_dict": 5,
                },
                BEN: "broken",
            }
        },
    }
    inbox = await make(hass)
    assert [i.message_id for i in inbox.items(ANNA)] == ["ok"]
    assert inbox.items(BEN) == []


async def test_an_unreadable_layout_is_ignored(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    hass_storage[INBOX_KEY] = {"version": 1, "minor_version": 1, "key": INBOX_KEY, "data": [1, 2]}
    inbox = await make(hass)
    assert inbox.items(ANNA) == []


async def test_many_changes_make_one_delayed_write(
    hass: HomeAssistant, hass_storage: dict[str, Any], freezer: FrozenDateTimeFactory
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    for n in range(5):
        put(inbox, mid=f"m{n}")
    assert INBOX_KEY not in hass_storage
    freezer.tick(timedelta(seconds=INBOX_SAVE_DELAY + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(hass_storage[INBOX_KEY]["data"]["items"][ANNA]) == 5
    await inbox.async_stop()


async def test_stopping_saves_what_is_waiting(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    put(inbox)
    await inbox.async_stop()
    assert "m" in hass_storage[INBOX_KEY]["data"]["items"][ANNA]


# A removed person --------------------------------------------------------------------------


async def test_a_removed_person_loses_the_inbox_after_the_grace_time(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    hass.states.async_set(ANNA, "home")
    hass.states.async_set(BEN, "home")
    put(inbox, ANNA)
    put(inbox, BEN)
    hass.states.async_remove(ANNA)
    await hass.async_block_till_done()
    assert len(inbox.items(ANNA)) == 1  # a reload of the person integration must not wipe it
    freezer.tick(timedelta(seconds=INBOX_PURGE_GRACE + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert inbox.items(ANNA) == [] and len(inbox.items(BEN)) == 1
    await inbox.async_stop()


async def test_a_person_who_comes_back_within_the_grace_time_keeps_the_inbox(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    hass.states.async_set(ANNA, "home")
    put(inbox, ANNA)
    hass.states.async_remove(ANNA)
    await hass.async_block_till_done()
    hass.states.async_set(ANNA, "home")
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=INBOX_PURGE_GRACE + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(inbox.items(ANNA)) == 1
    await inbox.async_stop()


async def test_other_entities_leaving_do_not_touch_the_inbox(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    put(inbox, ANNA)
    hass.states.async_set("sensor.x", "1")
    hass.states.async_remove("sensor.x")
    freezer.tick(timedelta(seconds=INBOX_PURGE_GRACE + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(inbox.items(ANNA)) == 1
    await inbox.async_stop()


# In the hub ------------------------------------------------------------------------------


async def test_the_inbox_survives_a_restart_of_the_integration(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(ANNA, "home")
    inbox = entry.runtime_data.hub.inbox
    put(inbox, now=dt_util.utcnow())
    await restart(hass, entry)
    again = entry.runtime_data.hub.inbox
    assert again is not inbox
    item = again.get(ANNA, "m")
    assert item is not None and item.title == "Washer"


async def test_an_old_inbox_is_pruned_when_the_integration_starts(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    inbox = entry.runtime_data.hub.inbox
    put(inbox, mid="old", now=dt_util.utcnow() - timedelta(days=500))
    put(inbox, mid="new", now=dt_util.utcnow())
    await restart(hass, entry)
    assert [i.message_id for i in entry.runtime_data.hub.inbox.items(ANNA)] == ["new"]


async def test_the_final_write_of_home_assistant_saves_what_is_waiting(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    inbox = await make(hass)
    inbox.async_start()
    put(inbox)
    assert INBOX_KEY not in hass_storage  # the delay has not passed
    hass.bus.async_fire(EVENT_HOMEASSISTANT_FINAL_WRITE)
    await hass.async_block_till_done()
    assert "m" in hass_storage[INBOX_KEY]["data"]["items"][ANNA]
    await inbox.async_stop()
