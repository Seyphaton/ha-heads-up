"""Banner record as stored in `.storage/heads_up.banners` (DESIGN §4.2)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    CHANNEL_BANNER,
    DEFAULT_ICONS,
    GLOBAL_SNOOZE_KEY,
    SOURCE_ACTION,
    canonical_severity,
)


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
    # The viewer may also choose another duration (D-219).
    snooze_custom: bool = False
    # Snooze end by user ID, or GLOBAL_SNOOZE_KEY for everyone (D-069).
    snoozed_until: dict[str, datetime] = field(default_factory=dict)
    # Hub fields (DESIGN §23). The defaults are what `create_banner` produces, so stored banners
    # of earlier versions load unchanged.
    channels: list[str] = field(default_factory=lambda: [CHANNEL_BANNER])
    # Channel to {"audience": name} or {"recipients": [...]} (D-098).
    targets: dict[str, dict[str, Any]] = field(default_factory=dict)
    # One name or `none` (older calls and rules), or a list of names (a call, D-184).
    policy: str | list[str] | None = None
    tts_message: str | None = None
    # Volume 0 to 1 set on a media player before it speaks; None leaves the volume alone.
    volume: float | None = None
    acknowledged_by: list[str] = field(default_factory=list)
    source: str = SOURCE_ACTION
    # Picture under the message: an http(s) URL or a path starting with `/` (D-127).
    image: str | None = None
    # Push only (D-255): `#rrggbb`, a sender icon URL and a subtitle. `icon` is the status bar icon.
    color: str | None = None
    icon_url: str | None = None
    subtitle: str | None = None
    # One message's own mail subject and body templates; empty: the Channels page templates.
    mail_subject: str | None = None
    mail_body: str | None = None

    @property
    def on_card(self) -> bool:
        """A message without the banner channel exists as a record but is not shown."""
        return CHANNEL_BANNER in self.channels

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
        # Written only when set, so a banner without it still loads in 1.0 (D-213).
        if not data["snooze_custom"]:
            del data["snooze_custom"]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Banner:
        # A key of a later version is ignored, so a downgrade keeps the banner.
        known = {f.name for f in fields(cls)}
        return cls(
            **{
                **{k: v for k, v in data.items() if k in known},
                "severity": canonical_severity(data.get("severity")),
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

    def to_client(
        self, user_id: str, display: Mapping[str, Mapping[str, str]] | None = None
    ) -> dict[str, Any]:
        """Payload for one viewer. Never includes dismissals or targeting of other users.
        `display` is the label, icon and color per severity from the Severities page."""
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
            "channels",
            "targets",
            "policy",
            "tts_message",
            "volume",
            "acknowledged_by",
            "source",
            "mail_subject",
            "mail_body",
        ):
            del data[key]
        snoozed_until = self.snoozed_for(user_id)
        data["snoozed_until"] = snoozed_until.isoformat() if snoozed_until else None
        data["active"] = self.active
        shown = (display or {}).get(self.severity) or {}
        data["icon"] = self.icon or shown.get("icon") or DEFAULT_ICONS[self.severity]
        if label := shown.get("label"):
            data["severity_label"] = label
        if color := shown.get("color"):
            data["severity_color"] = color
        data["dismissed"] = user_id in self.dismissed_by or GLOBAL_SNOOZE_KEY in self.dismissed_by
        data["snoozed"] = snoozed_until is not None
        return data
