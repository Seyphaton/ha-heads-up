"""Fallback: other channels and targets when the first delivery reached nobody (D-079)."""

from __future__ import annotations

from typing import Any

from ...const import FALLBACK_WHEN, POLICY_CHANNELS

# Skip reasons that mean the person exists but cannot be reached: the delivery "failed".
DEVICE_REASONS = frozenset({"no_usable_device", "service_not_found", "channel_not_accepted"})
# Skip reasons that say nothing about the audience (the channel is simply not built).
IGNORED_REASONS = frozenset({"channel_unavailable", "waiting_for_condition"})


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if data.get("when") not in FALLBACK_WHEN:
        errors["when"] = "when_required"
    channels = data.get("channels") or []
    if not channels:
        errors["channels"] = "channels_required"
    elif any(c not in POLICY_CHANNELS for c in channels):
        errors["channels"] = "channel_unknown"
    return errors


def matches(when: str, classes: set[str]) -> bool:
    return bool(classes) and (when == "both" or when in classes)
