"""The personal inbox (Phase 22, D-264, D-268, D-270): one item per message and person.

Items are kept in memory and written to the store `heads_up.inbox` from a copy, in a thread,
after a delay. Item text is stored in plain text, so it is also in backups (SECURITY.md).

Read state: an item is unread until the person opens it, marks it read, or acknowledges or
dismisses the message. A message that ends while its item is unread leaves the item unread.
Nothing here decides who gets an item or when; the channel and the engine call these methods.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE, EVENT_STATE_CHANGED
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.util import dt as dt_util

from ..const import (
    DEFAULT_INBOX_RETENTION_MONTHS,
    INBOX_MAX_ITEMS,
    INBOX_MAX_TIMELINE,
    INBOX_PURGE_GRACE,
    INBOX_SAVE_DELAY,
    SEVERITIES,
)
from ..storage import inbox_store

_LOGGER = logging.getLogger(__name__)

TEXT_FIELDS = ("title", "text", "icon", "color", "image", "source", "tag")
DAYS_PER_MONTH = 30.4375


def _when(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    parsed = dt_util.parse_datetime(value)
    return dt_util.as_utc(parsed) if parsed is not None else None


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


@dataclass(slots=True)
class InboxItem:
    message_id: str
    person: str
    title: str
    text: str
    severity: str
    created: datetime
    updated: datetime
    icon: str | None = None
    color: str | None = None
    image: str | None = None  # the reference only, never fetched
    source: str | None = None  # `source_key`, a key and never a name
    tag: str | None = None
    read_at: datetime | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    resolved_reason: str | None = None
    via: list[str] = field(default_factory=list)
    timeline: list[dict[str, str]] = field(default_factory=list)
    reminders: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "text": self.text,
            "severity": self.severity,
            "icon": self.icon,
            "color": self.color,
            "image": self.image,
            "source": self.source,
            "tag": self.tag,
            "created": _iso(self.created),
            "updated": _iso(self.updated),
            "read_at": _iso(self.read_at),
            "acknowledged_at": _iso(self.acknowledged_at),
            "resolved_at": _iso(self.resolved_at),
            "resolved_reason": self.resolved_reason,
            "via": list(self.via),
            "timeline": [dict(entry) for entry in self.timeline],
            "reminders": self.reminders,
        }

    @classmethod
    def from_dict(cls, person: str, message_id: str, data: Any) -> InboxItem | None:
        """None for a row that cannot be trusted: it is dropped, the others are kept."""
        if not isinstance(data, Mapping):
            return None
        created, updated = _when(data.get("created")), _when(data.get("updated"))
        severity = data.get("severity")
        if created is None or updated is None or severity not in SEVERITIES:
            return None
        texts = {key: data.get(key) for key in TEXT_FIELDS}
        if not isinstance(texts["title"], str) or not isinstance(texts["text"], str):
            return None

        def text_or_none(key: str) -> str | None:
            return texts[key] if isinstance(texts[key], str) else None

        via = [c for c in data.get("via") or [] if isinstance(c, str)]
        timeline = [
            {k: str(v) for k, v in entry.items() if isinstance(v, str)}
            for entry in data.get("timeline") or []
            if isinstance(entry, Mapping)
            and isinstance(entry.get("kind"), str)
            and _when(entry.get("at")) is not None
        ]
        reason = data.get("resolved_reason")
        reminders = data.get("reminders")
        return cls(
            message_id=message_id,
            person=person,
            title=texts["title"],
            text=texts["text"],
            severity=str(severity),
            created=created,
            updated=updated,
            read_at=_when(data.get("read_at")),
            acknowledged_at=_when(data.get("acknowledged_at")),
            resolved_at=_when(data.get("resolved_at")),
            resolved_reason=reason if isinstance(reason, str) else None,
            via=via,
            timeline=timeline[-INBOX_MAX_TIMELINE:],
            reminders=reminders if isinstance(reminders, int) and reminders >= 0 else 0,
            icon=text_or_none("icon"),
            color=text_or_none("color"),
            image=text_or_none("image"),
            source=text_or_none("source"),
            tag=text_or_none("tag"),
        )

    @property
    def unread(self) -> bool:
        return self.read_at is None

    @property
    def needs_action(self) -> bool:
        """An open critical item nobody acknowledged (D-264)."""
        return (
            self.severity == "critical"
            and self.acknowledged_at is None
            and self.resolved_at is None
        )

    def to_client(self) -> dict[str, Any]:
        """What the card gets. The internal `source` key stays here."""
        return {
            "message_id": self.message_id,
            "person": self.person,
            "title": self.title,
            "text": self.text,
            "severity": self.severity,
            "icon": self.icon,
            "color": self.color,
            "image": self.image,
            "tag": self.tag,
            "created": _iso(self.created),
            "updated": _iso(self.updated),
            "unread": self.unread,
            "read_at": _iso(self.read_at),
            "acknowledged": self.acknowledged_at is not None,
            "needs_action": self.needs_action,
            "resolved": self.resolved_at is not None,
            "resolved_at": _iso(self.resolved_at),
            "resolved_reason": self.resolved_reason,
            "via": list(self.via),
            "timeline": [dict(entry) for entry in self.timeline],
            "reminders": self.reminders,
        }


@callback
def _is_person(data: EventStateChangedData | Mapping[str, Any]) -> bool:
    return str(data["entity_id"]).startswith("person.")


def _entry(kind: str, now: datetime, channel: str | None) -> dict[str, str]:
    entry = {"kind": kind, "at": now.isoformat()}
    if channel:
        entry["channel"] = channel
    return entry


class InboxStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store = inbox_store(hass)
        self._items: dict[str, dict[str, InboxItem]] = {}
        self.retention_months = DEFAULT_INBOX_RETENTION_MONTHS
        self._started = False
        self._save_handle: CALLBACK_TYPE | None = None
        self._daily: CALLBACK_TYPE | None = None
        self._unsub_people: CALLBACK_TYPE | None = None
        self._unsub_final: CALLBACK_TYPE | None = None
        self._gone: dict[str, CALLBACK_TYPE] = {}  # a removed person to the pending purge
        self._listeners: list[Callable[[], None]] = []

    # Storage ----------------------------------------------------------------------------

    async def async_load(self) -> None:
        data = await self._store.async_load()
        table = data.get("items") if isinstance(data, dict) else None
        if not isinstance(table, dict):
            if data:
                _LOGGER.error("Ignoring the stored inbox: unexpected layout")
            return
        dropped = 0
        for person, rows in table.items():
            if not isinstance(rows, dict):
                dropped += 1
                continue
            for message_id, row in rows.items():
                item = InboxItem.from_dict(str(person), str(message_id), row)
                if item is None:
                    dropped += 1
                    continue
                self._items.setdefault(str(person), {})[str(message_id)] = item
        if dropped:
            _LOGGER.error("Skipped %d unreadable inbox rows", dropped)
        self.prune(dt_util.utcnow(), self.retention_months)

    @callback
    def async_start(self) -> None:
        """Write after changes, and prune once a day."""
        self._started = True
        self._daily = async_track_time_interval(self._hass, self._prune_due, timedelta(days=1))
        self._unsub_people = self._hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_person, event_filter=_is_person
        )
        # Our own delay is not Store's, so Home Assistant's last write would miss it (stop).
        self._unsub_final = self._hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_FINAL_WRITE, self._final_write
        )

    async def async_stop(self) -> None:
        self._started = False
        if self._daily is not None:
            self._daily()
            self._daily = None
        if self._unsub_people is not None:
            self._unsub_people()
            self._unsub_people = None
        if self._unsub_final is not None:
            self._unsub_final()
            self._unsub_final = None
        for cancel in self._gone.values():
            cancel()
        self._gone.clear()
        if self._save_handle is not None:
            self._save_handle()
            self._save_handle = None
        await self.async_save()

    async def async_save(self) -> None:
        # A copy made here, in the event loop; the file is serialized in a thread (N-117).
        snapshot = {
            "items": {
                person: {mid: item.to_dict() for mid, item in rows.items()}
                for person, rows in self._items.items()
                if rows
            }
        }
        await self._store.async_save(snapshot)

    def _changed(self) -> None:
        for listener in list(self._listeners):
            listener()
        if self._started and self._save_handle is None:
            self._save_handle = async_call_later(self._hass, INBOX_SAVE_DELAY, self._save_due)

    async def _final_write(self, _event: Event) -> None:
        self._unsub_final = None
        if self._save_handle is not None:
            self._save_handle()
            self._save_handle = None
            await self.async_save()

    async def _save_due(self, _now: datetime) -> None:
        self._save_handle = None
        await self.async_save()

    async def _prune_due(self, now: datetime) -> None:
        self.prune(now, self.retention_months)

    @callback
    def _on_person(self, event: Event[EventStateChangedData]) -> None:
        """A person that is removed loses the inbox after a grace time: a reload of the person
        integration removes and adds the entity again, and that must not wipe anything."""
        entity_id = event.data["entity_id"]
        if event.data["new_state"] is not None:
            if (cancel := self._gone.pop(entity_id, None)) is not None:
                cancel()
            return
        if entity_id in self._gone or entity_id not in self._items:
            return

        @callback
        def purge(_now: datetime) -> None:
            self._gone.pop(entity_id, None)
            if self._hass.states.get(entity_id) is None:
                self.purge_person(entity_id)

        self._gone[entity_id] = async_call_later(self._hass, INBOX_PURGE_GRACE, purge)

    @callback
    def subscribe(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        """Called after every change, for the sensors and the card (later steps)."""
        self._listeners.append(listener)

        @callback
        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    # Writing ----------------------------------------------------------------------------

    def upsert(
        self,
        person: str,
        message_id: str,
        data: Mapping[str, Any],
        channel: str | None,
        now: datetime,
    ) -> InboxItem:
        """The message reached this person. New text or a higher severity makes it unread; the
        same content again only adds the channel."""
        rows = self._items.setdefault(person, {})
        item = rows.get(message_id)
        title, text, severity = str(data["title"]), str(data["text"]), str(data["severity"])
        shown = {key: data.get(key) for key in ("icon", "color", "image", "source", "tag")}
        if item is None:
            item = InboxItem(
                message_id=message_id,
                person=person,
                title=title,
                text=text,
                severity=severity,
                created=now,
                updated=now,
                via=[channel] if channel else [],
                timeline=[_entry("sent", now, channel)],
                icon=shown["icon"],
                color=shown["color"],
                image=shown["image"],
                source=shown["source"],
                tag=shown["tag"],
            )
            rows[message_id] = item
            self._changed()
            return item
        reopened = item.resolved_at is not None
        higher = SEVERITIES.index(severity) > SEVERITIES.index(item.severity)
        edited = (item.title, item.text) != (title, text)
        if severity != item.severity:
            item.acknowledged_at = None  # a new severity starts again, like the policies do
        item.title, item.text, item.severity = title, text, severity
        for key, value in shown.items():
            setattr(item, key, value)
        if channel and channel not in item.via:
            item.via.append(channel)
        if reopened:
            item.resolved_at = item.resolved_reason = None
            item.acknowledged_at = None
            item.read_at = None
            item.updated = now
            self._log(item, "sent", now, channel)
        elif edited or higher:
            item.read_at = None
            item.updated = now
            self._log(item, "updated", now, channel)
        self._changed()
        return item

    def add_event(
        self,
        person: str,
        message_id: str,
        kind: str,
        channel: str | None,
        now: datetime,
        reminder_unread: bool,
    ) -> None:
        """A reminder or an escalation: one more timeline entry, never a second row. With
        `reminder_unread` it brings a read item back to the unread count."""
        item = self.get(person, message_id)
        if item is None:
            return
        if kind == "reminder":
            item.reminders += 1
        self._log(item, kind, now, channel)
        if reminder_unread and kind in ("reminder", "escalation"):
            item.read_at = None
        self._changed()

    def mark_read(self, person: str, message_id: str, now: datetime) -> bool:
        item = self.get(person, message_id)
        if item is None or item.read_at is not None:
            return False
        item.read_at = now
        self._changed()
        return True

    def mark_read_all(self, person: str, now: datetime) -> int:
        count = 0
        for item in self._items.get(person, {}).values():
            if item.read_at is None:
                item.read_at = now
                count += 1
        if count:
            self._changed()
        return count

    def acknowledged(self, message_id: str, person: str, now: datetime) -> None:
        """`person` acknowledged the message. Their item is read; the others only log it."""
        for owner, rows in self._items.items():
            item = rows.get(message_id)
            if item is None:
                continue
            if owner == person:
                item.acknowledged_at = now
                if item.read_at is None:
                    item.read_at = now
                self._log(item, "acknowledged", now, None)
            else:
                self._log(item, "acknowledged_by_other", now, None)
        self._changed()

    def dismissed(self, message_id: str, person: str, now: datetime) -> None:
        """`person` dismissed it for themself: read and resolved. Other people's items stay."""
        item = self.get(person, message_id)
        if item is None:
            return
        if item.read_at is None:
            item.read_at = now
        self._resolve_item(item, "dismissed", now)
        self._changed()

    def resolve(self, message_id: str, reason: str, now: datetime) -> int:
        """The message ended for everyone. Items stay and keep their read state."""
        count = 0
        for rows in self._items.values():
            item = rows.get(message_id)
            if item is not None and item.resolved_at is None:
                self._resolve_item(item, reason, now)
                count += 1
        if count:
            self._changed()
        return count

    def _resolve_item(self, item: InboxItem, reason: str, now: datetime) -> None:
        if item.resolved_at is not None:
            return
        item.resolved_at, item.resolved_reason = now, reason
        self._log(item, "resolved", now, None)

    @staticmethod
    def _log(item: InboxItem, kind: str, now: datetime, channel: str | None) -> None:
        item.timeline.append(_entry(kind, now, channel))
        if len(item.timeline) > INBOX_MAX_TIMELINE:
            # The first entry says how it began; keep it and the latest ones.
            del item.timeline[1 : len(item.timeline) - INBOX_MAX_TIMELINE + 1]

    def rename_person(self, old: str, new: str) -> int:
        """The person's entity ID changed: the inbox moves with it."""
        rows = self._items.pop(old, None)
        if not rows:
            return 0
        target = self._items.setdefault(new, {})
        for message_id, item in rows.items():
            item.person = new
            target.setdefault(message_id, item)
        if cancel := self._gone.pop(old, None):
            cancel()
        self._changed()
        return len(rows)

    def delete(self, person: str, message_id: str) -> bool:
        rows = self._items.get(person, {})
        if rows.pop(message_id, None) is None:
            return False
        if not rows:
            self._items.pop(person, None)
        self._changed()
        return True

    def purge_person(self, person: str) -> int:
        removed = len(self._items.pop(person, {}))
        if removed:
            self._changed()
        return removed

    def clear(self) -> int:
        """Every item of every person (Clear inbox)."""
        removed = sum(len(rows) for rows in self._items.values())
        self._items.clear()
        if removed:
            self._changed()
        return removed

    def prune(self, now: datetime, months: int) -> int:
        """Drop what is older than the retention, then the oldest over the cap of one person:
        read and resolved items first, then read ones, then the rest."""
        cutoff = now - timedelta(days=round(months * DAYS_PER_MONTH))
        removed = 0
        for person, rows in list(self._items.items()):
            for mid in [m for m, i in rows.items() if i.updated < cutoff]:
                del rows[mid]
                removed += 1
            over = len(rows) - INBOX_MAX_ITEMS
            if over > 0:
                order = sorted(
                    rows.values(),
                    key=lambda i: (
                        0
                        if i.read_at is not None and i.resolved_at is not None
                        else 1
                        if i.read_at is not None
                        else 2,
                        i.updated,
                    ),
                )
                for item in order[:over]:
                    del rows[item.message_id]
                    removed += 1
            if not rows:
                del self._items[person]
        if removed:
            self._changed()
        return removed

    # Reading ----------------------------------------------------------------------------

    def get(self, person: str, message_id: str) -> InboxItem | None:
        return self._items.get(person, {}).get(message_id)

    def items(self, person: str, limit: int | None = None, offset: int = 0) -> list[InboxItem]:
        """The person's items, the latest change first."""
        ordered = sorted(
            self._items.get(person, {}).values(),
            key=lambda i: (i.updated, i.created, i.message_id),
            reverse=True,
        )
        return ordered[offset:] if limit is None else ordered[offset : offset + limit]

    def people(self) -> list[str]:
        return sorted(p for p, rows in self._items.items() if rows)

    def unread_count(self, person: str) -> int:
        return sum(1 for i in self._items.get(person, {}).values() if i.unread)

    def unread_critical(self, person: str) -> int:
        return sum(
            1 for i in self._items.get(person, {}).values() if i.unread and i.severity == "critical"
        )

    def needs_action(self, person: str) -> int:
        """Open critical items nobody acknowledged for this person (D-264)."""
        return sum(1 for i in self._items.get(person, {}).values() if i.needs_action)

    # Several persons (a user may be linked to more than one) --------------------------------

    def items_of(
        self,
        persons: list[str],
        *,
        unread_only: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> tuple[list[InboxItem], int]:
        """The latest change first, and how many there are in all. A message that reached two
        persons of one user is listed once."""
        found: dict[str, InboxItem] = {}
        for person in persons:
            for item in self._items.get(person, {}).values():
                if unread_only and not item.unread:
                    continue
                known = found.get(item.message_id)
                if known is None or item.updated > known.updated:
                    found[item.message_id] = item
        ordered = sorted(
            found.values(), key=lambda i: (i.updated, i.created, i.message_id), reverse=True
        )
        page = ordered[offset:] if limit is None else ordered[offset : offset + limit]
        return page, len(ordered)

    def counts_of(self, persons: list[str]) -> dict[str, int]:
        """Unread, needing action and unread critical, over the items of these persons."""
        items = {i.message_id: i for p in persons for i in self._items.get(p, {}).values()}
        return {
            "unread": sum(1 for i in items.values() if i.unread),
            "needs_action": sum(1 for i in items.values() if i.needs_action),
            "unread_critical": sum(
                1 for i in items.values() if i.unread and i.severity == "critical"
            ),
        }
