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
    dismissed_by: list[str] = field(default_factory=list)

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
        """Payload for one viewer. Never includes other users' dismissals."""
        data = self.to_dict()
        del data["dismissed_by"]
        data["icon"] = self.icon or DEFAULT_ICONS[self.severity]
        data["dismissed"] = user_id in self.dismissed_by
        return data
