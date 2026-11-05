"""Who is home, who left last, who came first (DESIGN §23.7, D-080, D-109).

Built on the `person` states. A change must hold for the debounce before it counts, so a flapping
GPS fix does not move "Last to leave". `None`, `unknown` and `unavailable` (N-63) are no
information: they change nothing. The result is stored so it is right after a restart.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import partial
from typing import Any

from homeassistant.const import STATE_HOME, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, State, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.storage import Store

from ..const import PRESENCE_KEY, SAVE_DELAY, SIGNAL_AUDIENCES

UNKNOWN_STATES = {STATE_UNKNOWN, STATE_UNAVAILABLE}


def is_unknown(state: State | None) -> bool:
    return state is None or state.state in UNKNOWN_STATES


class PresenceTracker:
    def __init__(self, hass: HomeAssistant, debounce: Callable[[], int]) -> None:
        self._hass = hass
        self._debounce = debounce
        self._store: Store[dict[str, Any]] = Store(hass, 1, PRESENCE_KEY)
        self.home: set[str] = set()
        self._last_to_leave: str | None = None
        self._first_home: str | None = None
        self._pending: dict[str, CALLBACK_TYPE] = {}
        self._unsub: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        data = await self._store.async_load() or {}
        self._last_to_leave = data.get("last_to_leave")
        self._first_home = data.get("first_home")
        # What happened while Home Assistant was stopped is unknown: take the states as they are.
        self.home = {
            s.entity_id for s in self._hass.states.async_all("person") if s.state == STATE_HOME
        }
        self._unsub = self._hass.bus.async_listen(
            "state_changed", self._on_change, event_filter=self._is_person
        )

    async def async_stop(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None
        for cancel in self._pending.values():
            cancel()
        self._pending.clear()
        await self._store.async_save(self._data())

    @property
    def last_to_leave(self) -> str | None:
        """The person whose departure emptied the house; none while anyone is home."""
        return None if self.home else self._last_to_leave

    @property
    def first_home(self) -> str | None:
        """The first person home after the house was empty; none while nobody is home."""
        return self._first_home if self.home else None

    @staticmethod
    @callback
    def _is_person(data: Any) -> bool:
        return str(data["entity_id"]).startswith("person.")

    @callback
    def _on_change(self, event: Event[Any]) -> None:
        entity_id: str = event.data["entity_id"]
        new: State | None = event.data["new_state"]
        if cancel := self._pending.pop(entity_id, None):
            cancel()
        if new is None:
            if entity_id in self.home:  # the person was deleted
                self._commit(entity_id, False)
            return
        if event.data["old_state"] is None:
            # The entity just appeared (startup, a new person): not an arrival.
            if new.state == STATE_HOME:
                self.home.add(entity_id)
            return
        if new.state in UNKNOWN_STATES:
            return
        is_home = new.state == STATE_HOME
        if is_home == (entity_id in self.home):
            return
        delay = self._debounce()
        if delay <= 0:
            self._commit(entity_id, is_home)
            return
        self._pending[entity_id] = async_call_later(
            self._hass, delay, partial(self._settle, entity_id, is_home)
        )

    @callback
    def _settle(self, entity_id: str, is_home: bool, _now: datetime) -> None:
        self._pending.pop(entity_id, None)
        self._commit(entity_id, is_home)

    def _commit(self, entity_id: str, is_home: bool) -> None:
        if is_home:
            if not self.home:
                self._first_home = entity_id
            self.home.add(entity_id)
        else:
            self.home.discard(entity_id)
            if not self.home:
                self._last_to_leave = entity_id
        self._store.async_delay_save(self._data, SAVE_DELAY)
        async_dispatcher_send(self._hass, SIGNAL_AUDIENCES)

    def _data(self) -> dict[str, Any]:
        return {"last_to_leave": self._last_to_leave, "first_home": self._first_home}
