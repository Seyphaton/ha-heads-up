"""Delivery ledger: what was sent where, in `.storage/heads_up.deliveries` (DESIGN §23.11).

Its own store with a `minor_version` migration hook (the banner store has none). Rows are
data, not behaviour; the engine decides what a row means after a restart.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
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

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        for raw in data.get("deliveries", []):
            try:
                row = Delivery.from_dict(raw)
            except (TypeError, KeyError, ValueError, AttributeError) as err:
                # One damaged row must not take the others down (like the banner store).
                _LOGGER.error("Skipping unreadable delivery %r in storage: %s", raw, err)
                continue
            self.rows[row.key] = row

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
        return {"deliveries": [r.to_dict() for r in self.rows.values()]}

    def _save(self) -> None:
        self._store.async_delay_save(self._data, SAVE_DELAY)


async def remove_ledger(hass: HomeAssistant) -> None:
    await LedgerStore(
        hass, DELIVERIES_VERSION, DELIVERIES_KEY, minor_version=DELIVERIES_MINOR_VERSION
    ).async_remove()
