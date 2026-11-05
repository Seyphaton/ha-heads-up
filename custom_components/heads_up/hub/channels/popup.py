"""Popup channel: a card or modal on every dashboard of a person (DESIGN §23.8, D-090, D-115).

Nothing is sent to a browser from here. A popup is a ledger row in state sent for the person; the
loader in the browser subscribes with `heads_up/popup_subscribe` and gets, for its user, the
messages that have such a row. Dismissing or snoozing clears the row, an ended message clears all
rows, so the popup follows the message like a push does. Persons only in this version (D-091).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback

from ...const import DEFAULT_POPUP_STYLES, OPT_POPUP_STYLES
from ...models import Banner
from ..ledger import State
from .base import Capabilities, Outcome, Result, Target

if TYPE_CHECKING:
    from ...manager import BannerManager
    from ..engine import HubEngine

QUIET = "quiet"  # kept in the ledger ref: a quiet popup is always a corner card


class PopupChannel:
    name = "popup"
    available = True
    capabilities = Capabilities(title=True, buttons=True, clear=True, replace=True, per_user=True)

    def __init__(self, hass: HomeAssistant, hub: HubEngine, manager: BannerManager) -> None:
        self._hass = hass
        self._hub = hub
        self._manager = manager
        self._listeners: list[Callable[[], None]] = []

    def stop(self) -> None:
        self._listeners.clear()

    # Settings ---------------------------------------------------------------------------

    def styles(self) -> dict[str, str]:
        return {**DEFAULT_POPUP_STYLES, **self._manager.options.get(OPT_POPUP_STYLES, {})}

    # Delivery ---------------------------------------------------------------------------

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        if self.styles().get(message.severity) == "off":
            return Outcome(Result.SKIPPED, "popup_off")
        if target.person is None or self._hub.resolver.user_of_person(target.person) is None:
            return Outcome(Result.SKIPPED, "no_user")  # a popup needs a Home Assistant user
        self._changed()
        return Outcome(Result.SENT, ref=QUIET if target.quiet else None)

    async def update(self, message: Banner, target: Target) -> Outcome:
        return await self.deliver(message, target)

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        self._changed()
        return Outcome(Result.SENT)

    # Subscription -----------------------------------------------------------------------

    @callback
    def subscribe(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)

        @callback
        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    def _changed(self) -> None:
        # The engine records the row after the channel returns; tell viewers after that.
        self._hass.loop.call_soon(self._notify)

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def messages_for(self, user_id: str) -> list[dict[str, Any]]:
        """The popups this user should see now."""
        persons = set(self._hub.resolver.persons_of_user(user_id))
        found: dict[str, dict[str, Any]] = {}
        for row in self._hub.ledger.rows.values():
            if row.channel != self.name or row.state is not State.SENT or row.person not in persons:
                continue
            message = self._hub.lookup(row.message_id)
            if message is None or not message.active or message.id in found:
                continue
            payload = message.to_client(user_id)
            quiet = row.ref == QUIET
            style = self.styles().get(message.severity, "card")
            # A quiet message is always a card: in its corner, or at the bottom right when the
            # severity is shown in the middle.
            payload["style"] = "card" if quiet and not style.startswith("card") else style
            payload["ack"] = self._hub.ack_applies(message) and not message.acknowledged_by
            payload["snooze_seconds"] = self._manager.quick_snooze_seconds
            found[message.id] = payload
        return list(found.values())
