"""Bounded record of delivery decisions: the answer to "why did I not get this?"."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TraceEntry:
    time: str  # ISO 8601, UTC
    message_id: str
    channel: str
    recipient: str | None
    result: str
    reason: str | None = None


class TraceBuffer:
    def __init__(self, size: int) -> None:
        self._entries: deque[TraceEntry] = deque(maxlen=max(1, size))

    def resize(self, size: int) -> None:
        self._entries = deque(self._entries, maxlen=max(1, size))

    def add(self, entry: TraceEntry) -> None:
        self._entries.append(entry)

    def entries(
        self, message_id: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Newest first."""
        found = [asdict(e) for e in reversed(self._entries) if message_id in (None, e.message_id)]
        return found[:limit] if limit else found

    def __len__(self) -> int:
        return len(self._entries)
