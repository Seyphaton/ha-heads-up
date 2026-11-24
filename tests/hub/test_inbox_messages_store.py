"""Messages between people, store: `sender`, Sent items, no read state (Phase 23, D-265)."""

from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant

from custom_components.heads_up.const import INBOX_MAX_ITEMS
from custom_components.heads_up.hub.inbox import SENT_PREFIX, InboxItem, InboxStore

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
ANNA = "person.anna"
BEN = "person.ben"


def fields(**kw: Any) -> dict[str, Any]:
    return {
        "title": "",
        "text": "Dinner is ready",
        "severity": "info",
        "icon": None,
        "color": None,
        "image": None,
        "source": "person",
        "tag": None,
        **kw,
    }


async def make(hass: HomeAssistant) -> InboxStore:
    inbox = InboxStore(hass)
    await inbox.async_load()
    return inbox


async def test_an_item_keeps_the_sender_and_tells_the_card(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    item = inbox.upsert(BEN, "m", fields(sender=ANNA), "inbox", NOW)
    assert item.sender == ANNA
    client = item.to_client()
    assert client["sender"] == ANNA and client["sent"] is False and client["unread"] is True


async def test_a_message_without_a_sender_has_none(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    item = inbox.upsert(BEN, "m", fields(), "push", NOW)
    assert item.sender is None and item.to_client()["sender"] is None


async def test_a_sent_item_is_the_senders_copy_with_the_recipients_and_no_read_state(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    item = inbox.add_sent(ANNA, "m", fields(), [BEN, ANNA], NOW)
    assert item.message_id == f"{SENT_PREFIX}m" and item.sent is True
    assert item.recipients == [BEN, ANNA] and item.sender == ANNA
    client = item.to_client()
    assert client["sent"] is True and client["recipients"] == [BEN, ANNA]
    assert client["unread"] is False and client["read_at"] is None
    assert client["needs_action"] is False and client["resolved"] is False


async def test_a_sent_item_is_never_counted(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    inbox.add_sent(ANNA, "m", fields(severity="critical"), [BEN], NOW)
    assert inbox.unread_count(ANNA) == 0 and inbox.needs_action(ANNA) == 0
    assert inbox.unread_critical(ANNA) == 0
    assert inbox.counts_of([ANNA]) == {"unread": 0, "needs_action": 0, "unread_critical": 0}


async def test_a_message_to_oneself_makes_an_inbox_item_and_a_sent_item(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    inbox.upsert(ANNA, "m", fields(sender=ANNA), "inbox", NOW)
    inbox.add_sent(ANNA, "m", fields(), [ANNA], NOW)
    assert inbox.unread_count(ANNA) == 1
    assert {i.message_id for i in inbox.items(ANNA)} == {"m", f"{SENT_PREFIX}m"}


async def test_the_views_never_mix_sent_with_the_inbox_or_all_notifications(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    inbox.upsert(ANNA, "got", fields(sender=BEN), "inbox", NOW)
    inbox.upsert(ANNA, "copy", fields(), "push", NOW, copy=True)
    inbox.add_sent(ANNA, "out", fields(), [BEN], NOW + timedelta(minutes=1))
    inbox_view, _ = inbox.items_of([ANNA], copies=False)
    all_view, _ = inbox.items_of([ANNA])
    sent_view, total = inbox.items_of([ANNA], sent=True)
    assert [i.message_id for i in inbox_view] == ["got"]
    assert sorted(i.message_id for i in all_view) == ["copy", "got"]
    assert [i.message_id for i in sent_view] == [f"{SENT_PREFIX}out"] and total == 1


async def test_a_sent_item_is_not_touched_by_the_lifecycle_of_the_message(
    hass: HomeAssistant,
) -> None:
    inbox = await make(hass)
    inbox.upsert(BEN, "m", fields(sender=ANNA), "inbox", NOW)
    inbox.add_sent(ANNA, "m", fields(), [BEN], NOW)
    inbox.resolve("m", "cleared", NOW)
    inbox.acknowledged("m", ANNA, NOW)
    inbox.dismissed("m", ANNA, NOW)
    sent = inbox.get(ANNA, f"{SENT_PREFIX}m")
    assert sent is not None and sent.resolved_at is None and sent.acknowledged_at is None
    assert [e["kind"] for e in sent.timeline] == ["sent"]


async def test_mark_read_all_leaves_sent_items_alone(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    item = inbox.add_sent(ANNA, "m", fields(), [BEN], NOW)
    assert inbox.mark_read_all(ANNA, NOW) == 0
    assert item.read_at is None


async def test_delete_removes_only_the_senders_copy(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    inbox.upsert(BEN, "m", fields(sender=ANNA), "inbox", NOW)
    inbox.add_sent(ANNA, "m", fields(), [BEN], NOW)
    assert inbox.delete(ANNA, f"{SENT_PREFIX}m") is True
    assert inbox.get(ANNA, f"{SENT_PREFIX}m") is None
    assert inbox.get(BEN, "m") is not None


async def test_sender_and_sent_items_survive_a_save_and_load(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    inbox.upsert(BEN, "m", fields(sender=ANNA), "inbox", NOW)
    inbox.add_sent(ANNA, "m", fields(), [BEN], NOW)
    await inbox.async_save()
    again = await make(hass)
    got = again.get(BEN, "m")
    sent = again.get(ANNA, f"{SENT_PREFIX}m")
    assert got is not None and got.sender == ANNA and got.sent is False
    assert sent is not None and sent.sent is True and sent.recipients == [BEN]
    assert sent.read_at is None


async def test_rows_from_before_this_phase_load_without_a_sender(hass: HomeAssistant) -> None:
    row = {
        "title": "t",
        "text": "x",
        "severity": "info",
        "created": NOW.isoformat(),
        "updated": NOW.isoformat(),
    }
    item = InboxItem.from_dict(ANNA, "m", row)
    assert item is not None and item.sender is None and item.sent is False
    assert item.recipients == []


async def test_a_damaged_recipient_list_is_ignored_not_trusted(hass: HomeAssistant) -> None:
    row = {
        "title": "t",
        "text": "x",
        "severity": "info",
        "created": NOW.isoformat(),
        "updated": NOW.isoformat(),
        "sent": True,
        "recipients": [BEN, 5, None],
        "sender": 7,
    }
    item = InboxItem.from_dict(ANNA, "m", row)
    assert item is not None and item.recipients == [BEN] and item.sender is None


async def test_when_over_the_cap_sent_items_go_first(hass: HomeAssistant) -> None:
    inbox = await make(hass)
    for n in range(INBOX_MAX_ITEMS):
        inbox.upsert(ANNA, f"u{n}", fields(), "inbox", NOW + timedelta(seconds=n))
    inbox.add_sent(ANNA, "out", fields(), [BEN], NOW + timedelta(days=1))
    inbox.prune(NOW + timedelta(days=1), 12)
    assert inbox.get(ANNA, f"{SENT_PREFIX}out") is None
    assert inbox.get(ANNA, "u0") is not None
