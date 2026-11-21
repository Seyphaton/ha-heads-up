"""The daily history behind the Overview's Activity card (D-244, plan 19.1).

One record per local day, kept for the last 24 months. It holds counts only: no title, no message
text, no address. Every recording call is wrapped by `safe`, so a fault here is logged once and
never reaches a delivery. Sources, policies and people are keyed by IDs or entity IDs, never by a
name that a rename would change.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..const import STATS_MONTHS, STATS_SAVE_DELAY
from ..storage import stats_store

_LOGGER = logging.getLogger(__name__)

# Time to acknowledge or to end, in seconds: the upper edges of the buckets. The last bucket is
# everything above the last edge.
EDGES = (30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 21600, 86400)
RESULTS = ("sent", "held", "skipped", "failed")
POLICY_ACTIONS = ("held", "quieted", "escalated", "reminded", "summarized", "fallback", "dropped")


def bucket_of(seconds: float) -> int:
    for index, edge in enumerate(EDGES):
        if seconds < edge:
            return index
    return len(EDGES)


def median_seconds(histogram: list[int]) -> float | None:
    """The median of a histogram of EDGES buckets, as the middle of its bucket."""
    total = sum(histogram)
    if not total:
        return None
    seen = 0
    for index, count in enumerate(histogram):
        seen += count
        if seen * 2 >= total:
            low = EDGES[index - 1] if index else 0
            high = EDGES[index] if index < len(EDGES) else EDGES[-1]
            return (low + high) / 2 if index < len(EDGES) else float(EDGES[-1])
    return None


def safe[F: Callable[..., Any]](method: F) -> F:
    """A recording call never raises into the notification path; the first fault is logged."""

    @wraps(method)
    def wrapper(self: StatsStore, *args: Any, **kwargs: Any) -> Any:
        try:
            return method(self, *args, **kwargs)
        except Exception:
            if not self._faulted:
                self._faulted = True
                _LOGGER.exception("Recording the history failed; it is skipped from now on")
            return None

    return wrapper  # type: ignore[return-value]


def new_day() -> dict[str, Any]:
    return {"h": [0] * 24}


def _bump(table: dict[str, Any], key: str, by: int = 1) -> None:
    table[key] = table.get(key, 0) + by


class StatsStore:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store = stats_store(hass)
        self.days: dict[str, dict[str, Any]] = {}
        self._faulted = False
        self._pruned_on = ""

    # Storage ----------------------------------------------------------------------------

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        days = data.get("days") if isinstance(data, dict) else None
        if not isinstance(days, dict):
            if data:
                _LOGGER.error("Ignoring the stored history: unexpected layout")
            return
        for key, record in days.items():
            if not isinstance(record, dict) or not self._valid(key, record):
                _LOGGER.error("Skipping the unreadable history of %s", key)
                continue
            self.days[key] = record
        self.prune()

    @staticmethod
    def _valid(key: str, record: dict[str, Any]) -> bool:
        try:
            date.fromisoformat(key)
        except TypeError, ValueError:
            return False
        hours = record.get("h")
        return (
            isinstance(hours, list) and len(hours) == 24 and all(isinstance(n, int) for n in hours)
        )

    def _data(self) -> dict[str, Any]:
        return {"days": self.days}

    async def async_save(self) -> None:
        await self._store.async_save(self._data())

    def _changed(self) -> None:
        self._store.async_delay_save(self._data, STATS_SAVE_DELAY)

    async def async_clear(self) -> None:
        self.days.clear()
        await self._store.async_save(self._data())

    # Days -------------------------------------------------------------------------------

    def _day(self, now: datetime) -> tuple[dict[str, Any], int]:
        local = dt_util.as_local(now)
        key = local.date().isoformat()
        if key != self._pruned_on:
            self.prune(local.date())
        return self.days.setdefault(key, new_day()), local.hour

    def prune(self, today: date | None = None) -> int:
        """Remove the days before the last 24 months; done at start and once a day."""
        today = today or dt_util.now().date()
        self._pruned_on = today.isoformat()
        months = today.year * 12 + today.month - 1 - STATS_MONTHS
        cutoff = date(months // 12, months % 12 + 1, min(today.day, 28))
        old = [key for key in self.days if date.fromisoformat(key) < cutoff]
        for key in old:
            del self.days[key]
        if old:
            self._changed()
        return len(old)

    def info(self) -> dict[str, Any]:
        """The size and the date range, for diagnostics and the Settings page."""
        keys = sorted(self.days)
        return {
            "days": len(keys),
            "first": keys[0] if keys else None,
            "last": keys[-1] if keys else None,
            "bytes": len(json.dumps(self.days, separators=(",", ":"))),
        }

    # Recording --------------------------------------------------------------------------

    @safe
    def created(self, now: datetime, severity: str, tag: str | None, source: str) -> None:
        day, hour = self._day(now)
        day["h"][hour] += 1
        _bump(day.setdefault("sev", {}), severity)
        if tag:
            _bump(day.setdefault("tag", {}), tag)
        _bump(day.setdefault("src", {}), source)
        self._changed()

    @safe
    def delivery(
        self,
        now: datetime,
        channel: str,
        result: str,
        reason: str | None,
        policy: str | None,
        person: str | None,
    ) -> None:
        if result not in RESULTS:
            return
        day, _ = self._day(now)
        _bump(day.setdefault("ch", {}).setdefault(channel, {}), result)
        if reason:
            _bump(day.setdefault("rs", {}), f"{channel}|{result}|{reason}")
        if person:
            _bump(day.setdefault("per", {}).setdefault(person, {}), f"{channel}|{result}")
        if policy:
            action = {"held": "held", "skipped": "dropped", "sent": "quieted"}.get(result)
            if action:
                _bump(day.setdefault("pol", {}).setdefault(policy, {}), action)
        self._changed()

    @safe
    def policy_action(self, now: datetime, policy: str, action: str) -> None:
        day, _ = self._day(now)
        _bump(day.setdefault("pol", {}).setdefault(policy, {}), action)
        self._changed()

    @safe
    def acknowledged(
        self, now: datetime, severity: str, seconds: float, avoided_escalations: int = 0
    ) -> None:
        day, _ = self._day(now)
        histogram = day.setdefault("ack", {}).setdefault(severity, [0] * (len(EDGES) + 1))
        histogram[bucket_of(seconds)] += 1
        if avoided_escalations:
            _bump(day, "avoid", avoided_escalations)
        self._changed()

    @safe
    def ended(self, now: datetime, reason: str, seconds: float) -> None:
        day, _ = self._day(now)
        _bump(day.setdefault("end", {}), reason)
        histogram = day.setdefault("te", [0] * (len(EDGES) + 1))
        histogram[bucket_of(seconds)] += 1
        self._changed()

    @safe
    def snoozed(self, now: datetime) -> None:
        day, _ = self._day(now)
        _bump(day, "snz")
        self._changed()


def months_back(today: date, months: int) -> date:
    """The first day of the month `months` before the month of `today`."""
    index = today.year * 12 + today.month - 1 - months
    return date(index // 12, index % 12 + 1, 1)


def days_between(start: date, end: date) -> list[str]:
    return [(start + timedelta(days=n)).isoformat() for n in range((end - start).days + 1)]
