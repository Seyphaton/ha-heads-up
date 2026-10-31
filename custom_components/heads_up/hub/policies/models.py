"""Policy objects read from `policy` subentries (DESIGN §23.14, D-079, D-097).

One class for every type: the fields a type does not use stay at their defaults. Types live in
their own modules so H4b and H4c add theirs without touching these.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigSubentry

from ...const import POLICY_SUBENTRY, POLICY_TYPES

DEFAULT_AFTER_MINUTES = 5
DEFAULT_EVERY_MINUTES = 30
DEFAULT_MAX_REMINDERS = 3


@dataclass(slots=True)
class Policy:
    name: str
    type: str
    subentry_id: str = ""
    severities: frozenset[str] = frozenset()  # empty means any
    tags: frozenset[str] = frozenset()  # empty means any
    enabled: bool = True
    # Escalation
    after_minutes: int = 0
    channels: tuple[str, ...] = ()  # a reminder may limit itself to these; empty means all
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)
    dismiss_acks: bool = False
    # Reminder
    every_minutes: int = 0
    max_count: int = 0

    @property
    def trigger(self) -> tuple[str, int]:
        """What makes a policy fire; two policies of one type with the same applies-to and
        trigger would do the same thing twice, so the form refuses the second."""
        if self.type == "escalation":
            return ("after", self.after_minutes)
        return ("every", self.every_minutes)

    @property
    def key(self) -> str:
        return f"{self.type}:{self.name}"


def parse_policy(subentry: ConfigSubentry) -> Policy | None:
    if subentry.subentry_type != POLICY_SUBENTRY:
        return None
    data = subentry.data
    if data.get("type") not in POLICY_TYPES:
        return None
    return Policy(
        name=subentry.title,
        type=str(data["type"]),
        subentry_id=subentry.subentry_id,
        severities=frozenset(data.get("severities") or ()),
        tags=frozenset(data.get("tags") or ()),
        enabled=bool(data.get("enabled", True)),
        after_minutes=int(data.get("after_minutes", 0)),
        channels=tuple(data.get("channels") or ()),
        targets={k: dict(v) for k, v in (data.get("targets") or {}).items()},
        dismiss_acks=bool(data.get("dismiss_acks", False)),
        every_minutes=int(data.get("every_minutes", 0)),
        max_count=int(data.get("max_count", 0)),
    )
