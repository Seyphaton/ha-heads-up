"""Who is home, who left last, who came first (DESIGN §23.7, D-080, D-109).

Built on the `person` states, or for a person whose recipient profile names one, on an on/off
entity: `on` means home (D-220). A change must hold for the debounce before it counts, so a flapping
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
from homeassistant.util import dt as dt_util

from ..const import HOME_ZONE, PRESENCE_KEY, SAVE_DELAY, SIGNAL_AUDIENCES

UNKNOWN_STATES = {STATE_UNKNOWN, STATE_UNAVAILABLE}


def is_unknown(state: State | None) -> bool:
    return state is None or state.state in UNKNOWN_STATES


def home_of(state: State | None, from_entity: bool) -> bool | None:
    """Whether a source state says home: a person state `home`, or an entity `on`. None: unknown."""
    if is_unknown(state):
        return None
    assert state is not None
    return state.state == "on" if from_entity else state.state == STATE_HOME


def is_home(hass: HomeAssistant, person: str, home_entity: str = "") -> bool | None:
    """Whether a person is home now, from their home entity if they have one (D-220)."""
    return home_of(hass.states.get(home_entity or person), bool(home_entity))


def in_zone(hass: HomeAssistant, person: str, zone: str, entity: str = "") -> bool | None:
    """Whether a person is in a zone now; None when it is unknown.

    With an override entity for the zone (D-220, D-229): in the zone while it is `on`. Without
    one, as Home Assistant says it: the person's state is the zone's name (`home` for Home), or
    the zone is in the person's `in_zones` attribute."""
    if entity:
        return home_of(hass.states.get(entity), True)
    if zone == HOME_ZONE:
        return is_home(hass, person)
    state = hass.states.get(person)
    if is_unknown(state):
        return None
    assert state is not None
    zones = state.attributes.get("in_zones") or []
    return zone in zones or state.state == zone.split(".", 1)[1]


class PresenceTracker:
    def __init__(
        self,
        hass: HomeAssistant,
        debounce: Callable[[], int],
        home_entity: Callable[[str], str] = lambda person: "",
    ) -> None:
        self._hass = hass
        self._debounce = debounce
        self._home_entity = home_entity
        self._store: Store[dict[str, Any]] = Store(hass, 1, PRESENCE_KEY)
        self.home: set[str] = set()
        self._last_to_leave: str | None = None
        self._first_home: str | None = None
        # When they happened, for the Overview; optional, so a store of an earlier shape loads.
        self._last_to_leave_at: datetime | None = None
        self._first_home_at: datetime | None = None
        self._pending: dict[str, CALLBACK_TYPE] = {}
        self._unsub: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        data = await self._store.async_load() or {}
        self._last_to_leave = data.get("last_to_leave")
        self._first_home = data.get("first_home")
        self._last_to_leave_at = dt_util.parse_datetime(str(data.get("last_to_leave_at") or ""))
        self._first_home_at = dt_util.parse_datetime(str(data.get("first_home_at") or ""))
        # What happened while Home Assistant was stopped is unknown: take the states as they are.
        self.home = {
            s.entity_id
            for s in self._hass.states.async_all("person")
            if is_home(self._hass, s.entity_id, self._home_entity(s.entity_id))
        }
        self._unsub = self._hass.bus.async_listen(
            "state_changed", self._on_change, event_filter=self._is_source
        )

    def refresh(self) -> None:
        """Take who is home from the sources as they are now, for example after a recipient
        profile changed its home entity. Last to leave and First home stay as they were."""
        if self._unsub is None:
            return  # not started yet: async_start reads them
        self.home = {
            s.entity_id
            for s in self._hass.states.async_all("person")
            if is_home(self._hass, s.entity_id, self._home_entity(s.entity_id))
        }

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

    @property
    def last_to_leave_at(self) -> datetime | None:
        return None if self.home else self._last_to_leave_at

    @property
    def first_home_at(self) -> datetime | None:
        return self._first_home_at if self.home else None

    def persons_of(self, entity_id: str) -> list[str]:
        """The persons whose presence this entity gives: a person without a home entity, or
        every person whose home entity it is."""
        if entity_id.startswith("person.") and not self._home_entity(entity_id):
            return [entity_id]
        return [
            s.entity_id
            for s in self._hass.states.async_all("person")
            if self._home_entity(s.entity_id) == entity_id
        ]

    @callback
    def _is_source(self, data: Any) -> bool:  # HA requires a callback as an event filter
        entity_id = str(data["entity_id"])
        return entity_id.startswith("person.") or bool(self.persons_of(entity_id))

    @callback
    def _on_change(self, event: Event[Any]) -> None:
        entity_id: str = event.data["entity_id"]
        if entity_id.startswith("person.") and event.data["new_state"] is None:
            if cancel := self._pending.pop(entity_id, None):
                cancel()
            if entity_id in self.home:  # the person was deleted
                self._commit(entity_id, False)
            return
        for person in self.persons_of(entity_id):
            self._person_changed(person, event)

    def _person_changed(self, entity_id: str, event: Event[Any]) -> None:
        new: State | None = event.data["new_state"]
        from_entity = bool(self._home_entity(entity_id))
        if cancel := self._pending.pop(entity_id, None):
            cancel()
        if event.data["old_state"] is None:
            # The entity just appeared (startup, a new person): not an arrival.
            if home_of(new, from_entity):
                self.home.add(entity_id)
            return
        is_home = home_of(new, from_entity)
        if is_home is None:
            return
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
                self._first_home_at = dt_util.utcnow()
            self.home.add(entity_id)
        else:
            self.home.discard(entity_id)
            if not self.home:
                self._last_to_leave = entity_id
                self._last_to_leave_at = dt_util.utcnow()
        self._store.async_delay_save(self._data, SAVE_DELAY)
        async_dispatcher_send(self._hass, SIGNAL_AUDIENCES)

    def _data(self) -> dict[str, Any]:
        return {
            "last_to_leave": self._last_to_leave,
            "first_home": self._first_home,
            "last_to_leave_at": self._last_to_leave_at.isoformat()
            if self._last_to_leave_at
            else None,
            "first_home_at": self._first_home_at.isoformat() if self._first_home_at else None,
        }
