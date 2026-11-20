"""Quiet hours: a window of the local day in which messages are held, quieted or dropped (D-112).

The window is on the wall clock of the Home Assistant time zone, so on a clock-change day it is
an hour shorter or longer; a time that does not exist or occurs twice uses its first occurrence.
`days` names the day a window starts on.

Instead of times, a policy can follow an on/off entity (D-218, D-220): quiet while it is `on`.
A held delivery is released when the entity turns off, or at a schedule's `next_event` if that
comes first (N-103). A missing or unavailable entity is not quiet: the message goes out.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ...const import CHANNEL_BANNER, HOLD_QUIET, WEEKDAYS
from . import clock
from .chain import Hold, Skip, Step
from .models import Policy

if TYPE_CHECKING:
    from . import PolicyBook


def _time(value: str) -> time:
    parsed = dt_util.parse_time(value)
    if parsed is None:
        raise ValueError(value)
    return parsed


def window_end(policy: Policy, now: datetime) -> datetime | None:
    """The end of the window `now` (local time) is in, or None when it is outside every window."""
    start, end = _time(policy.from_time), _time(policy.to_time)
    if start == end:
        return None
    days = set(policy.days) or set(WEEKDAYS)
    today: date = now.date()
    here = now.time().replace(tzinfo=None)

    def starts_on(day: date) -> bool:
        return WEEKDAYS[day.weekday()] in days

    if start < end:
        end_day = today if start <= here < end and starts_on(today) else None
    elif here >= start and starts_on(today):
        end_day = today + timedelta(days=1)
    elif here < end and starts_on(today - timedelta(days=1)):
        end_day = today
    else:
        end_day = None
    if end_day is None:
        return None
    return datetime.combine(end_day, end, tzinfo=now.tzinfo)


# The domains whose state is on or off and that Quiet hours can follow.
QUIET_ENTITY_DOMAINS = ("schedule", "input_boolean", "binary_sensor")


def entity_window(hass: HomeAssistant, entity_id: str) -> tuple[bool, datetime | None]:
    """Whether the entity says quiet now, and when that ends if it knows (a schedule)."""
    state = hass.states.get(entity_id)
    if state is None or state.state != "on":
        return False, None
    end = dt_util.parse_datetime(str(state.attributes.get("next_event") or ""))
    if end is not None and end <= dt_util.utcnow():
        end = None  # a stale end would release and hold again at once; wait for "off" instead
    return True, end


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if entity := data.get("quiet_entity"):
        if str(entity).split(".", 1)[0] not in QUIET_ENTITY_DOMAINS:
            errors["quiet_entity"] = "quiet_entity_invalid"
        return errors
    try:
        if _time(str(data.get("from_time"))) == _time(str(data.get("to_time"))):
            errors["to_time"] = "window_empty"
    except ValueError:
        errors["from_time"] = "time_invalid"
    return errors


class QuietHoursStage:
    """Quiet hours in the precedence chain. Only the channels outside the dashboard are affected."""

    name = "quiet_hours"

    def __init__(self, policies: PolicyBook, hass: HomeAssistant | None = None) -> None:
        self._policies = policies
        self._hass = hass

    def apply(self, step: Step) -> Step | Skip | Hold:
        if step.channel == CHANNEL_BANNER:
            return step
        message = step.banner
        now = clock.now()
        active: list[tuple[Policy, datetime | None]] = []
        for policy in self._policies.for_message(message):
            if policy.type != "quiet_hours":
                continue
            # A band entry lets the message through for the people it covers (D-224).
            if not policy.holds_anyway and self._policies.passes(message, step.target):
                continue
            if policy.quiet_entity:
                if self._hass is None:
                    continue
                quiet, until = entity_window(self._hass, policy.quiet_entity)
                if quiet:
                    active.append((policy, until))
            elif (end := window_end(policy, now)) is not None:
                active.append((policy, end))

        def first(action: str) -> str:
            return next(p.name for p, _ in active if p.action == action)

        actions = {p.action for p, _ in active}
        if "drop" in actions:
            return Skip("quiet_hours", first("drop"))
        if "wait" in actions:
            if step.origin == "reminder":
                # A reminder is not worth holding until morning.
                return Skip("quiet_hours", first("wait"))
            waits = [(p, end) for p, end in active if p.action == "wait"]
            ends = [end for _, end in waits]
            # An entity without a known end holds until it turns off (the engine listens).
            until = None if None in ends else max(e for e in ends if e is not None)
            last = max(waits, key=lambda w: w[1] or datetime.max.replace(tzinfo=UTC))[0].name
            return Hold("quiet_hours", HOLD_QUIET, dt_util.as_utc(until) if until else None, last)
        if "quiet" in actions:
            return replace(step, target=replace(step.target, quiet=True, quiet_by=first("quiet")))
        return step
