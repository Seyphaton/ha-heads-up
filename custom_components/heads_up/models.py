"""Banner record as stored in `.storage/heads_up.banners` (DESIGN §4.2)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util

from .const import DEFAULT_ICONS


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

    @property
    def active(self) -> bool:
        return self.condition is None or self.condition_met is True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("created_at", "updated_at", "expires_at"):
            data[key] = data[key].isoformat() if data[key] else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Banner:
        return cls(
            **{
                **data,
                "created_at": _parse(data["created_at"]),
                "updated_at": _parse(data["updated_at"]),
                "expires_at": _parse(data.get("expires_at")),
            }
        )

    def to_client(self, user_id: str) -> dict[str, Any]:
        """Payload for one viewer. Never includes dismissals or targeting of other users."""
        data = self.to_dict()
        for key in ("dismissed_by", "people", "condition", "mode", "condition_met", "ever_met"):
            del data[key]
        data["active"] = self.active
        data["icon"] = self.icon or DEFAULT_ICONS[self.severity]
        data["dismissed"] = user_id in self.dismissed_by
        return data
