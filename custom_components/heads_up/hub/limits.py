"""Rate limits and duplicate suppression for deliveries (D-123).

Pushes are capped per device and in total per minute; an update that repeats the last one is
ignored for a while. Critical messages are counted but never suppressed. The caps come from the
options, so a change in Settings applies at once (`configure`).
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from ..const import (
    DEFAULT_OPTIONS,
    OPT_DEDUPE_SECONDS,
    OPT_RATE_PER_DEVICE,
    OPT_RATE_TOTAL,
)
from ..models import Banner

WINDOW = timedelta(seconds=60)
RATE_LIMITED = "rate_limited"
DUPLICATE = "duplicate"
# What makes two updates identical: the content a recipient sees.
Signature = tuple[Any, ...]


def signature(banner: Banner) -> Signature:
    actions = tuple((a.get("key"), a.get("label")) for a in banner.actions)
    return (banner.title, banner.message, banner.severity, banner.icon, banner.image, actions)


class Limiter:
    def __init__(self, options: dict[str, Any]) -> None:
        self.per_device = 0
        self.total = 0
        self.dedupe = timedelta(0)
        self._device_times: dict[str, deque[datetime]] = {}
        self._all_times: deque[datetime] = deque()
        self._last: dict[tuple[str, str, str], tuple[datetime, Signature]] = {}
        self.configure(options)

    def configure(self, options: dict[str, Any]) -> None:
        def number(key: str) -> int:
            return int(options.get(key, DEFAULT_OPTIONS[key]))

        self.per_device = number(OPT_RATE_PER_DEVICE)
        self.total = number(OPT_RATE_TOTAL)
        self.dedupe = timedelta(seconds=number(OPT_DEDUPE_SECONDS))

    def duplicate(self, banner: Banner, channel: str, recipient: str) -> bool:
        """An update that repeats what this recipient got within the dedupe time. Never critical."""
        if banner.severity == "critical":
            return False
        last = self._last.get((banner.id, channel, recipient))
        if last is None or not self.dedupe:
            return False
        return last[1] == signature(banner) and dt_util.utcnow() - last[0] < self.dedupe

    def push_allowed(self, banner: Banner, device: str) -> bool:
        """Count one push to a device. False when the device or the whole house is over its cap."""
        now = dt_util.utcnow()
        times = self._device_times.setdefault(device, deque())
        for queue in (times, self._all_times):
            while queue and now - queue[0] >= WINDOW:
                queue.popleft()
        over = len(times) >= self.per_device or len(self._all_times) >= self.total
        if over and banner.severity != "critical":
            return False
        times.append(now)
        self._all_times.append(now)
        return True

    def sent(self, banner: Banner, channel: str, recipient: str) -> None:
        self._last[(banner.id, channel, recipient)] = (dt_util.utcnow(), signature(banner))

    def forget(self, message_id: str) -> None:
        for key in [k for k in self._last if k[0] == message_id]:
            del self._last[key]
