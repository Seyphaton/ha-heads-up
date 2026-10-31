"""Quiet hours: a window of the local day in which messages are held, quieted or dropped (D-112).

The window is on the wall clock of the Home Assistant time zone, so on a clock-change day it is
an hour shorter or longer; a time that does not exist or occurs twice uses its first occurrence.
`days` names the day a window starts on.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.util import dt as dt_util

from ...const import CHANNEL_BANNER, HOLD_QUIET, WEEKDAYS
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


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    try:
        if _time(str(data.get("from_time"))) == _time(str(data.get("to_time"))):
            errors["to_time"] = "window_empty"
    except ValueError:
        errors["from_time"] = "time_invalid"
    return errors


class QuietHoursStage:
    """Quiet hours in the precedence chain. Only the channels outside the dashboard are affected."""

    name = "quiet_hours"

    def __init__(self, policies: PolicyBook) -> None:
        self._policies = policies

    def apply(self, step: Step) -> Step | Skip | Hold:
        if step.channel == CHANNEL_BANNER:
            return step
        message = step.banner
        now = dt_util.now()
        active: list[tuple[Policy, datetime]] = []
        for policy in self._policies.for_message(message):
            if policy.type != "quiet_hours":
                continue
            if policy.critical_passes and message.severity == "critical":
                continue
            if (end := window_end(policy, now)) is not None:
                active.append((policy, end))
        actions = {p.action: end for p, end in active}
        if "drop" in actions:
            return Skip("quiet_hours")
        if "wait" in actions:
            if step.origin == "reminder":
                return Skip("quiet_hours")  # a reminder is not worth holding until morning
            return Hold(
                "quiet_hours",
                HOLD_QUIET,
                dt_util.as_utc(max(end for p, end in active if p.action == "wait")),
            )
        if "quiet" in actions:
            return replace(step, target=replace(step.target, quiet=True))
        return step
