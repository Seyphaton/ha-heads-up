"""Inbox channel: an item in a person's inbox that survives a restart (D-264, D-268).

Nothing is sent. A delivery writes an item in `hub/inbox.py` for the person; the card and the
sensor read it from there. A reminder or an escalation that reaches a person who already has the
item adds a timeline entry instead of a second row. The end, an acknowledgement and a dismissal
are applied by the engine from the transitions of the message, because `clear` does not say why
it was called (a snooze clears too and must not resolve anything).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.util import dt as dt_util

from ...const import OPT_INBOX_REMINDER_UNREAD, SOURCE_PERSON
from ...models import Banner
from .base import Capabilities, Outcome, Result, Target

if TYPE_CHECKING:
    from ...manager import BannerManager
    from ..engine import HubEngine

CHANNEL = "inbox"


def item_fields(message: Banner) -> dict[str, str | None]:
    """What an inbox item keeps of a message; the mirror uses the same (D-275)."""
    from ..engine import source_key  # the engine imports the channels

    # A message between people shows who wrote it in the row, not as a title (D-285).
    person = message.source == SOURCE_PERSON
    return {
        "title": "" if person else message.title or "",
        "text": message.message,
        "severity": message.severity,
        "icon": None if person else message.icon,
        "color": message.color,
        "image": message.image,
        "source": source_key(message),
        "tag": message.tag,
        "sender": message.sender,
    }


class InboxChannel:
    name = CHANNEL
    available = True
    capabilities = Capabilities(title=True, buttons=False, clear=True, replace=True, per_user=True)

    def __init__(self, hub: HubEngine, manager: BannerManager) -> None:
        self._hub = hub
        self._manager = manager

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        person = target.person
        if person is None:
            return Outcome(Result.SKIPPED, "no_person")
        inbox = self._hub.inbox
        now = dt_util.utcnow()
        existing = inbox.get(person, message.id)
        if target.origin in ("reminder", "escalation") and existing and not existing.copy:
            # The person already has it: one more entry in the timeline, never a second row.
            inbox.add_event(
                person,
                message.id,
                target.origin,
                CHANNEL,
                now,
                bool(self._manager.options.get(OPT_INBOX_REMINDER_UNREAD, True)),
            )
            return Outcome(Result.SENT)
        inbox.upsert(person, message.id, item_fields(message), CHANNEL, now)
        return Outcome(Result.SENT)

    async def update(self, message: Banner, target: Target) -> Outcome:
        return await self.deliver(message, target)

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        return Outcome(Result.SENT)  # the item stays; the engine resolves it from the transition
