"""Banner record as stored in `.storage/heads_up.banners` (DESIGN §4.2)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util

from .const import DEFAULT_ICONS, GLOBAL_SNOOZE_KEY


def _parse(value: str | None) -> datetime | None:
    return dt_util.parse_datetime(value) if value else None


@dataclass(slots=True)
class Banner:
    id: str
    message: str
    severity: str
    dismissible: bool
    dismiss_scope: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None
    title: str | None = None
    icon: str | None = None
    tag: str | None = None
    tap_action: dict[str, Any] | None = None
    condition: dict[str, Any] | None = None
    mode: str = "once"
    people: list[str] = field(default_factory=list)
    # Last evaluated condition result; None = never evaluated with a real state.
    condition_met: bool | None = None
    # Condition was true at least once since the last upsert; drives `once` removal.
    ever_met: bool = False
    dismissed_by: list[str] = field(default_factory=list)
    snoozable: bool = False
    snooze_scope: str = "user"
    # Choices offered to the viewer, in seconds.
    # Buttons: {key, label, dismiss, action?}; `action` is run by the card (DESIGN §21).
    actions: list[dict[str, Any]] = field(default_factory=list)
    snooze_options: list[int] = field(default_factory=list)
    # Snooze end by user ID, or GLOBAL_SNOOZE_KEY for everyone (D-069).
    snoozed_until: dict[str, datetime] = field(default_factory=dict)

    @property
    def active(self) -> bool:
        return self.condition is None or self.condition_met is True

    def snoozed_for(self, user_id: str, now: datetime | None = None) -> datetime | None:
        """End of the snooze that hides this banner from the user, or None."""
        now = now or dt_util.utcnow()
        ends = [
            until
            for key, until in self.snoozed_until.items()
            if key in (user_id, GLOBAL_SNOOZE_KEY) and until > now
        ]
        return max(ends) if ends else None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("created_at", "updated_at", "expires_at"):
            data[key] = data[key].isoformat() if data[key] else None
        data["snoozed_until"] = {k: v.isoformat() for k, v in self.snoozed_until.items()}
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Banner:
        return cls(
            **{
                **data,
                "created_at": _parse(data["created_at"]),
                "updated_at": _parse(data["updated_at"]),
                "expires_at": _parse(data.get("expires_at")),
                "snoozed_until": {
                    k: parsed
                    for k, v in (data.get("snoozed_until") or {}).items()
                    if (parsed := _parse(v)) is not None
                },
            }
        )

    def to_client(self, user_id: str) -> dict[str, Any]:
        """Payload for one viewer. Never includes dismissals or targeting of other users."""
        data = self.to_dict()
        for key in (
            "dismissed_by",
            "people",
            "condition",
            "mode",
            "condition_met",
            "ever_met",
            "snoozed_until",
            "snooze_scope",
        ):
            del data[key]
        data["active"] = self.active
        data["icon"] = self.icon or DEFAULT_ICONS[self.severity]
        data["dismissed"] = user_id in self.dismissed_by
        data["snoozed"] = self.snoozed_for(user_id) is not None
        return data
