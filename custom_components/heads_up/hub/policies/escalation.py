"""Escalation: after N minutes without acknowledgement, deliver on more channels (D-079, D-081)."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any

from ...const import POLICY_CHANNELS
from ...models import Banner
from .models import Policy


def due(policy: Policy, start: datetime) -> datetime:
    return start + timedelta(minutes=policy.after_minutes)


def message_for(banner: Banner, policy: Policy) -> Banner:
    """The message as the escalation delivers it: the policy's channels and targets."""
    return replace(
        banner,
        channels=list(policy.channels),
        targets={c: dict(policy.targets[c]) for c in policy.channels if c in policy.targets},
    )


def check(data: dict[str, Any]) -> dict[str, str]:
    """Shape errors of the escalation fields, as translation keys."""
    errors: dict[str, str] = {}
    if int(data.get("after_minutes") or 0) < 1:
        errors["after_minutes"] = "after_required"
    channels = data.get("channels") or []
    if not channels:
        errors["channels"] = "channels_required"
    elif any(c not in POLICY_CHANNELS for c in channels):
        errors["channels"] = "channel_unknown"
    return errors
