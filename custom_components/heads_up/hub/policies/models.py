"""Policy objects read from `policy` subentries (DESIGN §23.14, D-079, D-097).

One class for every type: the fields a type does not use stay at their defaults. Types live in
their own modules so H4c adds its own without touching these.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigSubentry

from ...const import POLICY_SUBENTRY, POLICY_TYPES
from ..identity import NAME_PREFIX

DEFAULT_AFTER_MINUTES = 5
DEFAULT_EVERY_MINUTES = 30
DEFAULT_MAX_REMINDERS = 3
DEFAULT_SUMMARY_EVERY = 60
DEFAULT_SUMMARY_AT = "20:00:00"
DEFAULT_QUIET_FROM = "22:00:00"
DEFAULT_QUIET_TO = "07:00:00"


# The fields each type uses, for `Policy.describe`.
DESCRIBED = {
    "escalation": ("after_minutes", "channels"),
    "reminder": ("every_minutes", "max_count", "channels"),
    "quiet_hours": ("from_time", "to_time", "days", "action", "critical_passes"),
    "away": ("max_wait", "critical_passes"),
    "fallback": ("when", "channels"),
    "deliver": ("channels",),
    "summarize": ("summary_every", "summary_at", "include_critical"),
}


@dataclass(slots=True)
class Policy:
    name: str
    type: str
    subentry_id: str = ""
    severities: frozenset[str] = frozenset()  # empty means any
    tags: frozenset[str] = frozenset()  # empty means any
    enabled: bool = True
    apply: str = "auto"  # auto: by severity and tag; manual: only when a call names the policy
    # Escalation and Fallback
    after_minutes: int = 0
    channels: tuple[str, ...] = ()  # a reminder may limit itself to these; empty means all
    # Escalation, Deliver and Fallback: take the channels and the recipients from the policy
    # (default) or from the call (D-181). "failed": only the channels that reached nobody.
    channels_from: str = "policy"
    targets_from: str = "policy"
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)
    dismiss_acks: bool = False
    when: str = ""  # Fallback: no_audience, failed or both
    # Reminder
    every_minutes: int = 0
    max_count: int = 0
    # Quiet hours
    from_time: str = DEFAULT_QUIET_FROM
    to_time: str = DEFAULT_QUIET_TO
    days: tuple[str, ...] = ()  # empty means every day
    action: str = "quiet"
    critical_passes: bool = True
    # Away: minutes to wait for arrival; 0 means as long as the message lives
    max_wait: int = 0
    # Summarize: every N minutes, or daily at a time of day when `summary_at` is set
    summary_every: int = 0
    summary_at: str = ""
    include_critical: bool = False

    @property
    def trigger(self) -> tuple[Any, ...]:
        """What makes a policy fire; two policies of one type with the same applies-to and
        trigger would do the same thing twice, so the form refuses the second."""
        if self.type == "escalation":
            return ("after", self.after_minutes)
        if self.type == "reminder":
            return ("every", self.every_minutes)
        if self.type == "quiet_hours":
            return ("window", self.from_time, self.to_time, tuple(sorted(self.days)))
        if self.type == "fallback":
            return ("when", self.when)
        if self.type == "summarize":
            return ("summary", self.summary_every, self.summary_at)
        if self.type == "deliver":
            return ("deliver", tuple(sorted(self.channels)), self.channels_from, self.targets_from)
        return (self.type,)

    @property
    def key(self) -> str:
        """What timer rows, held messages and stored messages call this policy: the subentry ID,
        which a rename does not change (D-199)."""
        return self.subentry_id or f"{self.type}:{self.name}"

    def is_named(self, ref: str) -> bool:
        """Whether a stored reference means this policy: its ID, or a name from before D-199."""
        if ref == self.key or ref == self.subentry_id:
            return bool(ref)
        name = ref[len(NAME_PREFIX) :] if ref.startswith(NAME_PREFIX) else ref
        return name.casefold() == self.name.casefold()

    def describe(self) -> dict[str, Any]:
        """What the policy does, as plain values for entity attributes (D-194)."""
        out: dict[str, Any] = {
            "policy": self.name,
            "type": self.type,
            "apply": self.apply,
            "severities": sorted(self.severities),
            "tags": sorted(self.tags),
        }
        for name in DESCRIBED.get(self.type, ()):
            value = getattr(self, name)
            out[name] = list(value) if isinstance(value, tuple) else value
        return out


def policy_from_data(name: str, subentry_id: str, data: Mapping[str, Any]) -> Policy | None:
    if data.get("type") not in POLICY_TYPES:
        return None
    return Policy(
        name=name,
        type=str(data["type"]),
        subentry_id=subentry_id,
        severities=frozenset(data.get("severities") or ()),
        tags=frozenset(data.get("tags") or ()),
        enabled=bool(data.get("enabled", True)),
        apply="manual" if data.get("apply") == "manual" else "auto",
        after_minutes=int(data.get("after_minutes", 0)),
        channels=tuple(data.get("channels") or ()),
        channels_from=str(data.get("channels_from") or "policy"),
        targets_from=str(data.get("targets_from") or "policy"),
        targets={k: dict(v) for k, v in (data.get("targets") or {}).items()},
        dismiss_acks=bool(data.get("dismiss_acks", False)),
        when=str(data.get("when", "")),
        every_minutes=int(data.get("every_minutes", 0)),
        max_count=int(data.get("max_count", 0)),
        from_time=str(data.get("from_time", DEFAULT_QUIET_FROM)),
        to_time=str(data.get("to_time", DEFAULT_QUIET_TO)),
        days=tuple(data.get("days") or ()),
        action=str(data.get("action", "quiet")),
        critical_passes=bool(data.get("critical_passes", True)),
        max_wait=int(data.get("max_wait", 0)),
        summary_every=int(data.get("summary_every", 0)),
        summary_at=str(data.get("summary_at", "")),
        include_critical=bool(data.get("include_critical", False)),
    )


def parse_policy(subentry: ConfigSubentry) -> Policy | None:
    if subentry.subentry_type != POLICY_SUBENTRY:
        return None
    return policy_from_data(subentry.title, subentry.subentry_id, subentry.data)
