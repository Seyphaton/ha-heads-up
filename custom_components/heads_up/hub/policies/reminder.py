"""Reminder: while unacknowledged, repeat every N minutes, at most M times (D-079, D-081)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ...const import POLICY_CHANNELS
from .models import Policy


def next_due(policy: Policy, after: datetime) -> datetime:
    return after + timedelta(minutes=policy.every_minutes)


def finished(policy: Policy, count: int) -> bool:
    return count >= policy.max_count


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if int(data.get("every_minutes") or 0) < 1:
        errors["every_minutes"] = "every_required"
    if int(data.get("max_count") or 0) < 1:
        errors["max_count"] = "max_required"
    if any(c not in POLICY_CHANNELS for c in data.get("channels") or []):
        errors["channels"] = "channel_unknown"
    return errors
