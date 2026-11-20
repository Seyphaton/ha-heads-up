"""The time and the presence the checker asks about (DESIGN §25.8).

"What happens to a message?" runs the real stages for another time of day and other people at
home, without sending anything. The stages read the time and a person's presence through this
module; outside the checker it is the clock and the house as they are now.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime

from homeassistant.const import STATE_HOME
from homeassistant.util import dt as dt_util

_NOW: ContextVar[datetime | None] = ContextVar("heads_up_checker_now", default=None)
_HOME: ContextVar[Mapping[str, bool] | None] = ContextVar("heads_up_checker_home", default=None)


def now() -> datetime:
    """Local time now, or the checker's time."""
    override = _NOW.get()
    return dt_util.as_local(override) if override is not None else dt_util.now()


def home(person: str, zone: str) -> bool | None:
    """Whether the checker says the person is in Home; None: ask Home Assistant. The checker
    only knows Home, so other zones are asked as usual."""
    known = _HOME.get()
    if known is None or person not in known or zone.split(".", 1)[-1] != STATE_HOME:
        return None
    return known[person]


@contextmanager
def assumed(at: datetime | None, people_home: Mapping[str, bool] | None) -> Iterator[None]:
    now_token = _NOW.set(at)
    home_token = _HOME.set(people_home)
    try:
        yield
    finally:
        _NOW.reset(now_token)
        _HOME.reset(home_token)
