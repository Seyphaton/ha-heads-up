"""Where a policy takes its channels and its recipients from (D-181).

Escalation, Deliver and Fallback add a delivery to a call. Each can name its own channels and
recipients (the default), or take either from the call:

- channels from the call, recipients from the policy: the same channels, other people;
- channels from the policy, recipients from the call: other channels, the same people;
- Fallback only: the channels that reached nobody, other people.

Taking both from the call would add nothing, so it is refused.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ...const import CHANNEL_BANNER, POLICY_CHANNELS
from ...models import Banner
from .models import Policy

CHANNELS_FROM = ("policy", "call", "failed")
TARGETS_FROM = ("policy", "call")
PEOPLE_CHANNELS = ("push", "popup", "mail")  # these take an audience or persons
PEOPLE_KEY = "people"  # the target of every people channel when the channels come from the call
SPEAK_KEY = "speak"  # the speakers, when the channels come from the call


def check(data: dict[str, Any], kind: str) -> dict[str, str]:
    """Shape errors of the two source fields, as translation keys. Channels are required only
    when the policy names them itself."""
    errors: dict[str, str] = {}
    channels_from = data.get("channels_from") or "policy"
    targets_from = data.get("targets_from") or "policy"
    if channels_from not in CHANNELS_FROM or (channels_from == "failed" and kind != "fallback"):
        errors["channels_from"] = "channels_from_unknown"
    if targets_from not in TARGETS_FROM:
        errors["targets_from"] = "targets_from_unknown"
    if not errors and channels_from != "policy" and targets_from != "policy":
        errors["targets_from"] = "nothing_new"
    if not errors and channels_from == "policy":
        channels = data.get("channels") or []
        if not channels:
            errors["channels"] = "channels_required"
        elif any(c not in POLICY_CHANNELS for c in channels):
            errors["channels"] = "channel_unknown"
    return errors


def target_keys(data: dict[str, Any]) -> list[str]:
    """The target fields of a policy form that apply, by key: none when the recipients come from
    the call, the people and speakers targets when the channels do, else one per channel."""
    if (data.get("targets_from") or "policy") == "call":
        return []
    if (data.get("channels_from") or "policy") != "policy":
        return [PEOPLE_KEY, SPEAK_KEY]
    return [c for c in data.get("channels") or [] if c != "persistent"]


def _call_people(banner: Banner) -> dict[str, Any] | None:
    for channel in PEOPLE_CHANNELS:
        if target := banner.targets.get(channel):
            return dict(target)
    return None


def message_for(banner: Banner, policy: Policy, unreached: set[str] | None = None) -> Banner:
    """The message as the policy delivers it. `unreached` holds the channels of the call that
    reached nobody; a policy that takes only the failed channels uses them."""
    if policy.channels_from == "policy":
        channels = list(policy.channels)
    else:
        channels = [c for c in banner.channels if c != CHANNEL_BANNER]
        if policy.channels_from == "failed":
            channels = [c for c in channels if unreached is None or c in unreached]
    targets: dict[str, dict[str, Any]] = {}
    if policy.targets_from == "call":
        people = _call_people(banner)
        speakers = banner.targets.get("speak")
        for channel in channels:
            if channel in PEOPLE_CHANNELS and people:
                targets[channel] = dict(people)
            elif channel == "speak" and speakers:
                targets[channel] = dict(speakers)
    elif policy.channels_from == "policy":
        targets = {c: dict(policy.targets[c]) for c in channels if c in policy.targets}
    else:
        for channel in channels:
            key = PEOPLE_KEY if channel in PEOPLE_CHANNELS else SPEAK_KEY
            target = policy.targets.get(key) if channel in (*PEOPLE_CHANNELS, "speak") else None
            if target:
                targets[channel] = dict(target)
    return replace(banner, channels=channels, targets=targets)
