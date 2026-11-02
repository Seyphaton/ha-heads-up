"""Delivery ledger: what was sent where, in `.storage/heads_up.deliveries` (DESIGN §23.11).

Its own store with a `minor_version` migration hook (the banner store has none). Rows are
data, not behaviour; the engine decides what a row means after a restart.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from ..const import (
    DELIVERIES_KEY,
    DELIVERIES_MINOR_VERSION,
    DELIVERIES_VERSION,
    SAVE_DELAY,
    TIMER_CHANNEL,
)
from ..models import Banner

_LOGGER = logging.getLogger(__name__)


class State(StrEnum):
    PLANNED = "planned"
    HELD = "held"
    SENT = "sent"
    SKIPPED = "skipped"
    FAILED = "failed"
    CLEARED = "cleared"


@dataclass(slots=True)
class Delivery:
    message_id: str
    channel: str
    recipient: str  # "" when the channel has no recipient (banner, persistent)
    state: State
    updated_at: datetime
    due: datetime | None = None  # next step (escalation, reminder, summary), from H4
    ref: str | None = None  # push tag or notification id, from H3 and H7
    person: str | None = None  # the person behind a device or person recipient
    # Timer rows (channel "timer", recipient "<type>:<policy>"): state planned = pending, sent =
    # done, cleared = cancelled; `count` is the reminders sent so far. Rows of earlier layouts
    # have no count, so no migration is needed.
    count: int = 0
    # Why a delivery in state held waits: "quiet_hours" (due = release time) or "away" (due =
    # deadline, released on arrival). Rows of earlier layouts have none.
    hold: str | None = None

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.message_id, self.channel, self.recipient)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = str(self.state)
        data["updated_at"] = self.updated_at.isoformat()
        data["due"] = self.due.isoformat() if self.due else None
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Delivery:
        updated = dt_util.parse_datetime(raw["updated_at"])
        if updated is None:
            raise ValueError("updated_at")
        due = dt_util.parse_datetime(raw["due"]) if raw.get("due") else None
        return cls(
            message_id=str(raw["message_id"]),
            channel=str(raw["channel"]),
            recipient=str(raw.get("recipient", "")),
            state=State(raw["state"]),
            updated_at=updated,
            due=due,
            ref=raw.get("ref"),
            person=raw.get("person"),
            count=int(raw.get("count", 0)),
            hold=raw.get("hold"),
        )


@dataclass(slots=True)
class HeldMessage:
    """A message a Summarize policy holds until its summary (D-105, D-113). It keeps what the
    summary needs, so a message cleared meanwhile can still be listed, marked resolved."""

    message_id: str
    policy: str  # the policy key, "summarize:<name>"
    message: str
    severity: str
    held_at: datetime
    title: str | None = None
    channels: list[str] = field(default_factory=list)
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)
    people: list[str] = field(default_factory=list)
    summarized: bool = False
    resolved: bool = False  # the message was removed before it was summarized

    @classmethod
    def from_banner(cls, banner: Banner, policy: str, now: datetime) -> HeldMessage:
        return cls(
            banner.id,
            policy,
            banner.message,
            banner.severity,
            now,
            banner.title,
            list(banner.channels),
            {k: dict(v) for k, v in banner.targets.items()},
            list(banner.people),
        )

    def as_banner(self) -> Banner:
        """Enough of a message to resolve its recipients again."""
        return Banner(
            id=self.message_id,
            message=self.message,
            severity=self.severity,
            dismissible=True,
            dismiss_scope="user",
            created_at=self.held_at,
            updated_at=self.held_at,
            title=self.title,
            channels=list(self.channels),
            targets={k: dict(v) for k, v in self.targets.items()},
            people=list(self.people),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["held_at"] = self.held_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> HeldMessage:
        held_at = dt_util.parse_datetime(raw["held_at"])
        if held_at is None:
            raise ValueError("held_at")
        return cls(**{**raw, "held_at": held_at})


class LedgerStore(Store[dict[str, Any]]):
    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        # Version 1.1 is the first. A later layout change converts old_data here.
        # Store API: HA_API_NOTES N-81.
        if old_major_version > DELIVERIES_VERSION:
            raise NotImplementedError
        return old_data


class DeliveryLedger:
    def __init__(self, hass: HomeAssistant) -> None:
        self._store = LedgerStore(
            hass, DELIVERIES_VERSION, DELIVERIES_KEY, minor_version=DELIVERIES_MINOR_VERSION
        )
        self.rows: dict[tuple[str, str, str], Delivery] = {}
        self.held: dict[str, HeldMessage] = {}

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        if not isinstance(data, dict):
            _LOGGER.error("Ignoring the stored deliveries: unexpected layout")
            return
        deliveries, held = data.get("deliveries", []), data.get("held", [])
        if not isinstance(deliveries, list):
            _LOGGER.error("Ignoring the stored deliveries: not a list")
            deliveries = []
        if not isinstance(held, list):
            _LOGGER.error("Ignoring the stored held messages: not a list")
            held = []
        for raw in deliveries:
            try:
                row = Delivery.from_dict(raw)
            except (TypeError, KeyError, ValueError, AttributeError) as err:
                # One damaged row must not take the others down (like the banner store).
                _LOGGER.error("Skipping unreadable delivery %r in storage: %s", raw, err)
                continue
            self.rows[row.key] = row
        for raw_held in held:
            try:
                kept = HeldMessage.from_dict(raw_held)
            except (TypeError, KeyError, ValueError, AttributeError) as err:
                _LOGGER.error("Skipping unreadable held message %r in storage: %s", raw_held, err)
                continue
            self.held[kept.message_id] = kept

    def put_held(self, held: HeldMessage) -> None:
        self.held[held.message_id] = held
        self._save()

    def drop_held(self, message_id: str) -> None:
        if self.held.pop(message_id, None) is not None:
            self._save()

    def put(self, row: Delivery) -> None:
        self.rows[row.key] = row
        self._save()

    def for_message(self, message_id: str) -> list[Delivery]:
        """Deliveries of a message, without its timer rows."""
        return [
            r
            for r in self.rows.values()
            if r.message_id == message_id and r.channel != TIMER_CHANNEL
        ]

    def timers(self, message_id: str | None = None) -> list[Delivery]:
        return [
            r
            for r in self.rows.values()
            if r.channel == TIMER_CHANNEL and (message_id is None or r.message_id == message_id)
        ]

    def drop_timers(self, message_id: str) -> None:
        for row in self.timers(message_id):
            del self.rows[row.key]
        self._save()

    def drop_message(self, message_id: str) -> None:
        for row in [*self.for_message(message_id), *self.timers(message_id)]:
            del self.rows[row.key]
        self._save()

    def message_ids(self) -> set[str]:
        return {r.message_id for r in self.rows.values()}

    async def async_save(self) -> None:
        await self._store.async_save(self._data())

    async def async_remove(self) -> None:
        await self._store.async_remove()

    def _data(self) -> dict[str, Any]:
        return {
            "deliveries": [r.to_dict() for r in self.rows.values()],
            "held": [h.to_dict() for h in self.held.values()],
        }

    def _save(self) -> None:
        self._store.async_delay_save(self._data, SAVE_DELAY)


async def remove_ledger(hass: HomeAssistant) -> None:
    await LedgerStore(
        hass, DELIVERIES_VERSION, DELIVERIES_KEY, minor_version=DELIVERIES_MINOR_VERSION
    ).async_remove()
