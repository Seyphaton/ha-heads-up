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
MAX_SOURCES_PER_DAY = 60
RESULTS = ("sent", "held", "skipped", "failed")
POLICY_ACTIONS = (
    "held",
    "quieted",
    "escalated",
    "reminded",
    "summarized",
    "fallback",
    "delivered",
    "dropped",
)


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

    def read(self, period: str) -> dict[str, Any]:
        return StatsReader(self.days).read(period, dt_util.now())

    # Recording --------------------------------------------------------------------------

    @safe
    def created(self, now: datetime, severity: str, tag: str | None, source: str) -> None:
        day, hour = self._day(now)
        day["h"][hour] += 1
        day.setdefault("hs", {}).setdefault(severity, [0] * 24)[hour] += 1
        _bump(day.setdefault("sev", {}), severity)
        if tag:
            _bump(day.setdefault("tag", {}), tag)
        sources = day.setdefault("src", {})
        # A call with a new ID for every message must not grow the record without a limit.
        if source not in sources and len(sources) >= MAX_SOURCES_PER_DAY:
            source = "action"
        _bump(sources, source)
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
        # A send with a policy behind it went out quietly (Quiet hours): count it as such.
        reason = reason or ("quiet_hours" if result == "sent" and policy else None)
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
    def dismissed(self, now: datetime) -> None:
        day, _ = self._day(now)
        _bump(day, "dis")
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


PERIODS = ("24h", "week", "month", "year", "2y")
SEVERITIES = ("critical", "warning", "info", "passive")


def _sum_tables(days: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for day in days:
        for name, count in (day.get(key) or {}).items():
            out[name] = out.get(name, 0) + count
    return out


def _month_start(today: date, back: int) -> date:
    return months_back(today, back)


def _totals(records: list[dict[str, Any]]) -> dict[str, int]:
    """The sums the numbers of the Activity card are made of, from daily records."""
    reasons = _sum_tables(records, "rs")
    channels: dict[str, dict[str, int]] = {}
    for record in records:
        for channel, results in (record.get("ch") or {}).items():
            into = channels.setdefault(channel, {})
            for result, n in results.items():
                into[result] = into.get(result, 0) + n
    quiet = sum(
        n
        for key, n in reasons.items()
        if key.endswith(("|held|quiet_hours", "|skipped|quiet_hours", "|sent|quiet_hours"))
    )
    # Deliveries quiet hours could touch: a banner is never touched, and a skip for another reason
    # (no phone, a disabled person) was never going to go out.
    attempted = sum(
        results.get("sent", 0) + results.get("held", 0) + results.get("failed", 0)
        for channel, results in channels.items()
        if channel != "banner"
    )
    dropped = sum(n for key, n in reasons.items() if key.endswith("|skipped|quiet_hours"))
    pol = [(d.get("pol") or {}).values() for d in records]
    return {
        "failed": sum(results.get("failed", 0) for results in channels.values()),
        "critical": sum((d.get("sev") or {}).get("critical", 0) for d in records),
        "escalations": sum(a.get("escalated", 0) for group in pol for a in group),
        "summarized": sum(a.get("summarized", 0) for group in pol for a in group),
        "created": sum(sum(d.get("h", [])) for d in records),
        "quiet": quiet,
        "basis": attempted + dropped,
    }


def _count(value: int, previous: int | None) -> dict[str, Any]:
    """A count with the one of the period before and the change in percent (none when there is
    nothing to compare with)."""
    change = round((value - previous) * 100 / previous) if previous else None
    return {"value": value, "previous": previous, "change": change}


def _share(part: int, whole: int, before: tuple[int, int] | None) -> dict[str, Any]:
    """A share in percent with the one of the period before and the change in percentage points."""
    value = round(part * 100 / whole) if whole else None
    previous = round(before[0] * 100 / before[1]) if before and before[1] else None
    change = value - previous if value is not None and previous is not None else None
    return {"value": value, "previous": previous, "change": change}


class StatsReader:
    """The numbers of one period from the daily records (plan 19.3)."""

    def __init__(self, days: dict[str, dict[str, Any]]) -> None:
        self._days = days

    def _slice(self, first: date, last: date) -> list[tuple[date, dict[str, Any]]]:
        found = []
        for key in days_between(first, last):
            if key in self._days:
                found.append((date.fromisoformat(key), self._days[key]))
        return found

    def _hours(self, local_now: datetime, back: int) -> list[dict[str, Any]]:
        """Hourly buckets for the `back` hours that end `back` hours before the current hour."""
        buckets = []
        current = local_now.replace(minute=0, second=0, microsecond=0)
        for offset in range(23, -1, -1):
            moment = current - timedelta(hours=offset + back)
            record = self._days.get(moment.date().isoformat())
            by = {
                sev: counts[moment.hour]
                for sev, counts in ((record or {}).get("hs") or {}).items()
                if counts[moment.hour]
            }
            total = (record or {"h": [0] * 24})["h"][moment.hour]
            buckets.append({"start": moment.isoformat(), "total": total, "by": by})
        return buckets

    def _bucketed(self, first: date, last: date, step: str) -> list[dict[str, Any]]:
        """Daily buckets, or monthly ones when `step` is month, between two dates."""
        buckets: list[dict[str, Any]] = []
        if step == "day":
            for key in days_between(first, last):
                record = self._days.get(key) or {}
                buckets.append(
                    {
                        "start": key,
                        "total": sum((record.get("sev") or {}).values()),
                        "by": dict(record.get("sev") or {}),
                    }
                )
            return buckets
        month = first
        while month <= last:
            nxt = months_back(month, -1)
            records = [r for d, r in self._slice(month, nxt - timedelta(days=1))]
            by = _sum_tables(records, "sev")
            buckets.append({"start": month.isoformat(), "total": sum(by.values()), "by": by})
            month = nxt
        return buckets

    def read(self, period: str, local_now: datetime) -> dict[str, Any]:
        today = local_now.date()
        if period == "24h":
            buckets = self._hours(local_now, 0)
            before = self._hours(local_now, 24)
            first, last = today - timedelta(days=1), today
        elif period in ("week", "month"):
            length = 7 if period == "week" else 30
            first = today - timedelta(days=length - 1)
            last = today
            buckets = self._bucketed(first, last, "day")
            before = self._bucketed(
                first - timedelta(days=length), first - timedelta(days=1), "day"
            )
        else:
            length = 12 if period == "year" else 24
            first = months_back(today, length - 1)
            last = today
            buckets = self._bucketed(first, last, "month")
            before = (
                self._bucketed(months_back(first, length), months_back(first, 1), "month")
                if period == "year"
                else []
            )
        records = [r for _, r in self._slice(first, last)]
        total = sum(b["total"] for b in buckets)
        previous = sum(b["total"] for b in before)
        # The days before the period, for the change of every number (none for two years).
        before_days = {
            "24h": (today - timedelta(days=3), today - timedelta(days=2)),
            "week": (first - timedelta(days=7), first - timedelta(days=1)),
            "month": (first - timedelta(days=30), first - timedelta(days=1)),
            "year": (months_back(first, 12), first - timedelta(days=1)),
        }.get(period)
        now_t = _totals(records)
        then_t = _totals([r for _, r in self._slice(*before_days)]) if before_days else None
        numbers: dict[str, Any] = {
            "notifications": _count(total, previous if before else None),
            "failed": _count(now_t["failed"], then_t["failed"] if then_t else None),
            "critical": _count(now_t["critical"], then_t["critical"] if then_t else None),
            "escalations": _count(now_t["escalations"], then_t["escalations"] if then_t else None),
            "quiet_share": _share(
                now_t["quiet"],
                now_t["basis"],
                (then_t["quiet"], then_t["basis"]) if then_t else None,
            ),
            "summary_share": _share(
                now_t["summarized"],
                now_t["created"],
                (then_t["summarized"], then_t["created"]) if then_t else None,
            ),
            # The whole days the numbers other than Notifications come from; for 24 hours these are
            # two days.
            "from": first.isoformat(),
            "to": last.isoformat(),
        }
        matrix = None
        if period != "24h":
            matrix = [[0] * 24 for _ in range(7)]
            for day_date, record in self._slice(first, last):
                row = matrix[day_date.weekday()]
                for hour, count in enumerate(record["h"]):
                    row[hour] += count
        return {
            "period": period,
            "buckets": buckets,
            "numbers": numbers,
            "matrix": matrix,
            "sources": sorted(_sum_tables(records, "src").items(), key=lambda kv: (-kv[1], kv[0])),
        }
