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

DEFAULT_AFTER_MINUTES = 5
DEFAULT_EVERY_MINUTES = 30
DEFAULT_MAX_REMINDERS = 3
DEFAULT_QUIET_FROM = "22:00:00"
DEFAULT_QUIET_TO = "07:00:00"


@dataclass(slots=True)
class Policy:
    name: str
    type: str
    subentry_id: str = ""
    severities: frozenset[str] = frozenset()  # empty means any
    tags: frozenset[str] = frozenset()  # empty means any
    enabled: bool = True
    # Escalation and Fallback
    after_minutes: int = 0
    channels: tuple[str, ...] = ()  # a reminder may limit itself to these; empty means all
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
        return (self.type,)

    @property
    def key(self) -> str:
        return f"{self.type}:{self.name}"


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
        after_minutes=int(data.get("after_minutes", 0)),
        channels=tuple(data.get("channels") or ()),
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
    )


def parse_policy(subentry: ConfigSubentry) -> Policy | None:
    if subentry.subentry_type != POLICY_SUBENTRY:
        return None
    return policy_from_data(subentry.title, subentry.subentry_id, subentry.data)
