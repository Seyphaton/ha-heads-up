"""Memory-only record for the panel: the log of last actions and the recent messages (D-118).

Both are bounded by the History setting and start empty after a restart. The log answers "what
happened lately"; the delivery trace of `trace.py` answers "why did this not arrive".
"""

from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

# The newest messages that the hourly chart counts; a busier house undercounts the oldest hours.
CREATED_KEEP = 5000

KINDS = (
    "created",
    "escalation_sent",
    "reminder_sent",
    "acknowledged",
    "dismissed",
    "snoozed",
    "unsnoozed",
    "summary_sent",
    "fallback_sent",
    "deliver_sent",
    "skipped",
    "failed",
    "expired",
    "cleared",
)


@dataclass(frozen=True, slots=True)
class Activity:
    time: str  # ISO 8601, UTC
    kind: str
    message_id: str
    title: str | None = None
    severity: str | None = None
    detail: str | None = None  # channels, a name, a reason: the panel words it


class ActivityLog:
    def __init__(self, size: int) -> None:
        self._entries: deque[Activity] = deque(maxlen=max(1, size))
        self._created: deque[tuple[float, str]] = deque(maxlen=CREATED_KEEP)

    def resize(self, size: int) -> None:
        self._entries = deque(self._entries, maxlen=max(1, size))

    def add(self, entry: Activity) -> None:
        self._entries.append(entry)
        if entry.kind == "created":
            stamp = datetime.fromisoformat(entry.time).timestamp()
            self._created.append((stamp, entry.severity or "info"))

    def created_histogram(self, now: float, hours: int = 24) -> dict[str, Any]:
        """Messages created per hour over the last `hours` hours, oldest hour first.

        Hours are rolling: the last bucket holds the last 60 minutes before `now`. Each bucket
        counts by severity so the panel can stack it. Memory only, like the log.
        """
        buckets: list[dict[str, Any]] = [{"total": 0, "by": {}} for _ in range(hours)]
        for stamp, severity in self._created:
            age = now - stamp
            if age < 0 or age >= hours * 3600:
                continue
            bucket = buckets[hours - 1 - int(age // 3600)]
            bucket["total"] += 1
            bucket["by"][severity] = bucket["by"].get(severity, 0) + 1
        return {
            "hours": hours,
            "buckets": buckets,
            "total": sum(b["total"] for b in buckets),
            "peak": max(b["total"] for b in buckets),
        }

    def latest(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Newest first."""
        found = [asdict(e) for e in reversed(self._entries)]
        return found[:limit] if limit else found

    def __len__(self) -> int:
        return len(self._entries)


class RecentMessages:
    """The messages the hub has seen lately, newest first; an id is listed once."""

    def __init__(self, size: int) -> None:
        self._size = max(1, size)
        self._items: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def resize(self, size: int) -> None:
        self._size = max(1, size)
        self._trim()

    def seen(self, message_id: str, info: dict[str, Any]) -> None:
        """Add a message, or refresh one that is listed (its ended state is cleared)."""
        known = self._items.pop(message_id, {})
        self._items[message_id] = {**known, **info, "ended": None, "reason": None}
        self._trim()

    def ended(self, message_id: str, when: str, reason: str | None) -> None:
        if (item := self._items.get(message_id)) is not None:
            item["ended"], item["reason"] = when, reason

    def listed(self) -> list[dict[str, Any]]:
        return [dict(item, id=key) for key, item in reversed(self._items.items())]

    def _trim(self) -> None:
        while len(self._items) > self._size:
            self._items.popitem(last=False)
