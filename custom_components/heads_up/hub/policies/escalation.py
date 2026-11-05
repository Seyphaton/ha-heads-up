"""Escalation: after N minutes without acknowledgement, deliver on more channels (D-079, D-081)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ...models import Banner
from . import sources
from .models import Policy


def due(policy: Policy, start: datetime) -> datetime:
    return start + timedelta(minutes=policy.after_minutes)


def message_for(banner: Banner, policy: Policy, unreached: set[str] | None = None) -> Banner:
    """The message as the escalation delivers it: the policy's channels and targets, or the
    call's, as the policy says (D-181)."""
    return sources.message_for(banner, policy, unreached)


def check(data: dict[str, Any]) -> dict[str, str]:
    """Shape errors of the escalation fields, as translation keys."""
    errors: dict[str, str] = {}
    if int(data.get("after_minutes") or 0) < 1:
        errors["after_minutes"] = "after_required"
    errors.update(sources.check(data, "escalation"))
    return errors
