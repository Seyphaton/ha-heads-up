"""Typed lifecycle transitions of a message (DESIGN §23.11).

The manager emits one of these from every mutation point, including the silent ones that fire no
bus event. The engine keys on transitions, never on bus events: a `created` event also fires for
a banner that is still waiting for its condition.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from ..models import Banner


class Kind(StrEnum):
    APPEARED = "appeared"  # a record was created (it may still wait for its condition)
    UPDATED = "updated"  # content or settings changed while the record exists
    BECAME_VISIBLE = "became_visible"  # condition turned true, a waiting banner became active
    HIDDEN = "hidden"  # see Reason; for a user-scoped dismissal the record stays
    SNOOZED = "snoozed"
    UNSNOOZED = "unsnoozed"  # reason "elapsed" when the timer ended it
    SEVERITY_CHANGED = "severity_changed"
    ACKNOWLEDGED = "acknowledged"  # emitted from H4a and H8


class Reason(StrEnum):
    CLEARED = "cleared"
    EXPIRED = "expired"
    CONDITION = "condition"
    DISMISSED = "dismissed"  # one user hid it; the record stays
    DISMISSED_GLOBAL = "dismissed_global"  # a global dismissal removed the record
    EVICTED = "evicted"
    RULE = "rule"
    ADMIN = "admin"
    CLEAR_ALL = "clear_all"
    ELAPSED = "elapsed"


@dataclass(frozen=True, slots=True)
class BannerTransition:
    kind: Kind
    banner: Banner  # snapshot taken when the transition was emitted
    reason: str | None = None
    user_id: str | None = None
    # True for paths that fire no bus event: startup, rules rebuilt at setup (D-058).
    silent: bool = False

    @property
    def ends_message(self) -> bool:
        """The message is gone from every channel (not just hidden for one user)."""
        return self.kind is Kind.HIDDEN and self.reason != Reason.DISMISSED


type TransitionListener = Callable[[BannerTransition], None]
