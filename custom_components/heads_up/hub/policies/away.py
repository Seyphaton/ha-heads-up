"""Away: hold a delivery for a person who is not home and send it on arrival (D-081)."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ...const import CHANNEL_BANNER, HOLD_AWAY
from ..presence import is_unknown
from .chain import Hold, Skip, Step

if TYPE_CHECKING:
    from . import PolicyBook


def check(data: dict[str, Any]) -> dict[str, str]:
    if int(data.get("max_wait") or 0) < 0:
        return {"max_wait": "wait_invalid"}
    return {}


class AwayStage:
    """Away in the precedence chain: a person who is known to be away is sent the message when
    they arrive. Audience targets only; unknown presence is sent at once (fail safe, D-080)."""

    name = "away"

    def __init__(self, hass: HomeAssistant, policies: PolicyBook) -> None:
        self._hass = hass
        self._policies = policies

    def apply(self, step: Step) -> Step | Skip | Hold:
        person = step.target.person
        if step.channel == CHANNEL_BANNER or person is None or step.origin == "reminder":
            return step
        if "audience" not in step.banner.targets.get(step.channel, {}):
            return step
        state = self._hass.states.get(person)
        if state is None or is_unknown(state) or state.state == "home":
            return step
        for policy in self._policies.for_message(step.banner):
            if policy.type == "away":
                until = (
                    dt_util.utcnow() + timedelta(minutes=policy.max_wait)
                    if policy.max_wait
                    else None
                )
                return Hold("away", HOLD_AWAY, until)
        return step
