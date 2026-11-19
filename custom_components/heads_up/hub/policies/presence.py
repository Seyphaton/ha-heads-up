"""Presence: hold or drop a delivery by where people are (D-212, was Away, D-081).

Push, popup and mail are checked per recipient: "the recipient is (not) in the zone". Speech is
checked for the household: "nobody / somebody of an audience is in the zone". Then the delivery
is held until that changes, or dropped. Unknown presence is sent at once (fail safe, D-080), the
banner is never held and a reminder is never held. "Home" may come from a person's home entity
(D-220); other zones use the person state.

A 1.0 Away policy reads as Presence with its 1.0 behaviour: push, popup and mail, the recipient
not in Home, hold, and the delivery dropped when the wait ends.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ...const import (
    AFTER_WAIT,
    CHANNEL_BANNER,
    HOLD_AWAY,
    PRESENCE_CHANNELS,
    PRESENCE_PEOPLE_CHANNELS,
    PRESENCE_THEN,
    PRESENCE_WHEN,
    PRESENCE_WHO,
)
from ..presence import is_home, is_unknown
from .chain import Hold, Skip, Step
from .models import Policy, presence_channels

if TYPE_CHECKING:
    from . import PolicyBook

HOME_ZONE = "zone.home"


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if int(data.get("max_wait") or 0) < 0:
        errors["max_wait"] = "wait_invalid"
    if any(c not in PRESENCE_CHANNELS for c in data.get("channels") or []):
        errors["channels"] = "channel_unknown"
    zone = str(data.get("zone") or HOME_ZONE)
    if not zone.startswith("zone."):
        errors["zone"] = "zone_invalid"
    for key, allowed in (
        ("presence_when", PRESENCE_WHEN),
        ("household_who", PRESENCE_WHO),
        ("presence_then", PRESENCE_THEN),
        ("after_wait", AFTER_WAIT),
    ):
        if data.get(key) and data[key] not in allowed:
            errors[key] = "choice_invalid"
    return errors


def in_zone(hass: HomeAssistant, person: str, zone: str, home_entity: str = "") -> bool | None:
    """Whether a person is in a zone now; None when it is unknown."""
    if zone == HOME_ZONE:
        return is_home(hass, person, home_entity)
    state = hass.states.get(person)
    if is_unknown(state):
        return None
    assert state is not None
    zones = state.attributes.get("in_zones") or []
    return zone in zones or state.state == zone.split(".", 1)[1]


class PresenceStage:
    """Presence in the precedence chain (the place of Away)."""

    name = "presence"

    def __init__(
        self,
        hass: HomeAssistant,
        policies: PolicyBook,
        home_entity: Callable[[str], str] = lambda person: "",
        household: Callable[[str], list[str]] = lambda audience: [],
    ) -> None:
        self._hass = hass
        self._policies = policies
        self._home_entity = home_entity
        self._household = household

    def applies(self, policy: Policy, step: Step) -> bool | None:
        """Whether the policy's condition holds for this delivery; None: not for it or unknown."""
        channel = step.channel
        if channel not in presence_channels(policy):
            return None
        if channel in PRESENCE_PEOPLE_CHANNELS:
            person = step.target.person
            # Audience targets only, as Away in 1.0: a named person is meant to get it now.
            if person is None or "audience" not in step.banner.targets.get(channel, {}):
                return None
            inside = in_zone(self._hass, person, policy.zone, self._home_entity(person))
            if inside is None:
                return None
            return not inside if policy.presence_when == "not_in" else inside
        if channel == "speak":
            known = [
                inside
                for person in self._household(policy.household_audience)
                if (inside := in_zone(self._hass, person, policy.zone, self._home_entity(person)))
                is not None
            ]
            if not known:
                return None  # nobody's presence is known: speak (fail safe)
            somebody = any(known)
            return not somebody if policy.household_who == "nobody" else somebody
        return None

    def apply(self, step: Step) -> Step | Skip | Hold:
        if step.channel == CHANNEL_BANNER or step.origin == "reminder":
            return step
        for policy in self._policies.for_message(step.banner):
            if policy.type != "presence":
                continue
            if policy.critical_passes and step.banner.severity == "critical":
                continue
            if not self.applies(policy, step):
                continue
            if policy.presence_then == "drop":
                return Skip("presence")
            until = (
                dt_util.utcnow() + timedelta(minutes=policy.max_wait) if policy.max_wait else None
            )
            return Hold("presence", HOLD_AWAY, until)
        return step
