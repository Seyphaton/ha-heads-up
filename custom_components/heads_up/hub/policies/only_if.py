"""Only if on policies and Faster while on reminders (D-216, DESIGN §25.5).

The condition has the shape of the `condition` of `notify` (`conditions.py`): one entity with an
operator, a value, an optional attribute and an optional `for` (seconds), or a template. It is
checked whenever the policy would act. None means unknown; the caller decides what that means
("whatever delivers more", D-216).
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template, result_as_boolean
from homeassistant.util import dt as dt_util

from ...conditions import matches

_NO_STATE = ("unknown", "unavailable")


def evaluate(
    hass: HomeAssistant, condition: Mapping[str, Any], now: datetime | None = None
) -> bool | None:
    if "template" in condition:
        try:
            return result_as_boolean(Template(str(condition["template"]), hass).async_render())
        except TemplateError:
            return None
    state = hass.states.get(str(condition.get("entity_id") or ""))
    if state is None or state.state in _NO_STATE:
        return None
    if (attribute := condition.get("attribute")) is not None:
        raw = state.attributes.get(attribute)
        value = None if raw is None else "" if raw in ([], {}, ()) else str(raw)
    else:
        value = state.state
    met = matches(condition, value)
    if met and (wait := int(condition.get("for") or 0)):
        # "For at least": true only once the state has not changed for that long.
        changed = state.last_changed if attribute is None else state.last_updated
        return (now or dt_util.utcnow()) - changed >= timedelta(seconds=wait)
    return met


def due_after_wait(hass: HomeAssistant, condition: Mapping[str, Any]) -> datetime | None:
    """When a condition with `for` becomes true if nothing changes, or None."""
    wait = int(condition.get("for") or 0)
    if not wait or "template" in condition:
        return None
    state = hass.states.get(str(condition.get("entity_id") or ""))
    if state is None:
        return None
    return state.last_changed + timedelta(seconds=wait)


def entities(hass: HomeAssistant, condition: Mapping[str, Any]) -> set[str]:
    """The entities whose changes can change the result."""
    if "template" in condition:
        try:
            info = Template(str(condition["template"]), hass).async_render_to_info()
        except TemplateError:
            return set()
        return set(info.entities)
    entity = condition.get("entity_id")
    return {str(entity)} if entity else set()
