"""Messages from one person to others (Phase 23, D-265, D-279).

The one place a message gets a sender. The sender is the person of the logged-in user, passed in
by the WebSocket command; no schema of any action accepts a sender or the `person` source, so a
caller cannot write one. The message then goes through the same engine path as `notify`, so the
recipient profiles and the policies decide what is delivered.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Any

from homeassistant.util import dt as dt_util

from ..const import (
    CHANNEL_BANNER,
    MESSAGE_RATE_LIMIT,
    MESSAGE_RATE_WINDOW,
    PERSON_MESSAGE_ICON,
    SOURCE_PERSON,
)
from .channels.inbox import item_fields

if TYPE_CHECKING:
    from ..manager import BannerManager
    from .engine import HubEngine


def _is_picture(value: Any) -> bool:
    """An address the phone can load: an http(s) URL or a path of this instance."""
    return isinstance(value, str) and value.startswith(("/", "http://", "https://"))


class MessageLimiter:
    """At most `MESSAGE_RATE_LIMIT` calls per sender in a rolling `MESSAGE_RATE_WINDOW` seconds.
    A call counts once, however many people it names."""

    def __init__(self) -> None:
        self._calls: dict[str, deque[float]] = {}

    def take(self, sender: str) -> int:
        """0 when the call may go on (and is counted), else the seconds to wait."""
        now = dt_util.utcnow().timestamp()
        calls = self._calls.setdefault(sender, deque())
        while calls and calls[0] <= now - MESSAGE_RATE_WINDOW:
            calls.popleft()
        if len(calls) >= MESSAGE_RATE_LIMIT:
            return max(1, int(calls[0] + MESSAGE_RATE_WINDOW - now) + 1)
        calls.append(now)
        return 0


async def send(
    manager: BannerManager,
    hub: HubEngine,
    sender: str,
    to: list[str],
    text: str,
    channels: list[str],
) -> dict[str, Any]:
    """Create the message, deliver it, and keep the sender's copy. Returns what was skipped."""
    people = list(dict.fromkeys(to))
    # A chat look on push and popup (D-285): the sender's name as title and picture as sender icon.
    state = manager.hass.states.get(sender)
    name = str(state.attributes.get("friendly_name") or state.name) if state else sender
    picture = state.attributes.get("entity_picture") if state else None
    chosen = list(dict.fromkeys(["inbox", *channels]))
    result = manager.create(
        {
            "message": text,
            "severity": "info",
            "channels": chosen,
            "targets": {channel: {"recipients": people} for channel in chosen},
            "source": SOURCE_PERSON,
            "sender": sender,
            "title": name,
            "icon": PERSON_MESSAGE_ICON,
            "icon_url": picture if _is_picture(picture) else None,
            # A message between people is never a card banner, so it needs no dismissal there.
            "dismissible": True,
        }
    )
    banner = manager.banners[result["id"]]
    assert CHANNEL_BANNER not in banner.channels
    planned = await hub.plan(banner)
    hub.inbox.add_sent(sender, banner.id, item_fields(banner), people, dt_util.utcnow())
    return {
        "id": banner.id,
        "channels": hub.counts(planned),
        "skipped": [
            {"person": r["recipient"], "channel": r["channel"], "reason": r["reason"]}
            for r in hub.reasons(planned)
            if r["result"] == "skipped"
        ],
    }
