"""Fallback: other channels and targets when the first delivery reached nobody (D-079)."""

from __future__ import annotations

from typing import Any

from ...const import FALLBACK_WHEN
from . import sources

# Skip reasons that mean the person exists but cannot be reached: the delivery "failed".
DEVICE_REASONS = frozenset({"no_usable_device", "service_not_found", "channel_not_accepted"})
# Skip reasons that say nothing about the audience (the channel is simply not built).
UNLOGGED_REASONS = frozenset({"channel_unavailable", "waiting_for_condition"})
# Also not about the audience: a delivery held back by a limit (D-123).
IGNORED_REASONS = UNLOGGED_REASONS | {"rate_limited", "duplicate"}


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if data.get("when") not in FALLBACK_WHEN:
        errors["when"] = "when_required"
    errors.update(sources.check(data, "fallback"))
    return errors


def matches(when: str, classes: set[str]) -> bool:
    return bool(classes) and (when == "both" or when in classes)
