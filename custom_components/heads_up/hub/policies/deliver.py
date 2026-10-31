"""Deliver: send matching messages to a chosen audience on chosen channels at once (D-121).

A call names the channels of its first delivery. A Deliver policy adds channels and targets to it
for the messages it applies to, so a critical watch-rule message, which has only the banner, can
reach phones the moment it appears.
"""

from __future__ import annotations

from typing import Any

from ...const import POLICY_CHANNELS


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    channels = data.get("channels") or []
    if not channels:
        errors["channels"] = "channels_required"
    elif any(c not in POLICY_CHANNELS for c in channels):
        errors["channels"] = "channel_unknown"
    return errors
