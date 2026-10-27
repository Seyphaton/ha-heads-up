"""Condition operators shared by the action schema, watch rules and the manager (DESIGN §18)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any, Final

OPERATORS: Final = (
    "equals",
    "not_equals",
    "above",
    "below",
    "between",
    "contains",
    "not_contains",
    "empty",
    "not_empty",
)
DEFAULT_OPERATOR: Final = "equals"
_NUMERIC_COUNT: Final = {"above": 1, "below": 1, "between": 2}
# Operators that look at the value only; a `state` given with them is ignored (D-068).
NO_STATE_OPERATORS: Final = ("empty", "not_empty")


def _number(text: str) -> float | None:
    try:
        number = float(text)
    except ValueError:
        return None
    return number if isfinite(number) else None


def check_state(operator: str, states: Sequence[str]) -> str | None:
    """Return an error code if `states` does not fit `operator`, else None."""
    if operator in _NUMERIC_COUNT:
        if len(states) != _NUMERIC_COUNT[operator]:
            return "state_count"
        if any(_number(s) is None for s in states):
            return "state_not_numeric"
    elif operator in ("contains", "not_contains") and not states:
        return "state_required"
    return None


def matches(condition: Mapping[str, Any], value: str | None) -> bool | None:
    """Evaluate a condition against the state or attribute text.

    None means there is no real value to judge (D-061): the caller leaves the result unchanged.
    """
    operator = condition.get("operator", DEFAULT_OPERATOR)
    if operator in NO_STATE_OPERATORS:
        # A missing attribute has no value, so it is empty (D-068).
        is_empty = value is None or not value.strip()
        return is_empty is (operator == "empty")
    wanted = condition["state"]
    wanted = [wanted] if isinstance(wanted, str) else list(wanted)
    if operator == "equals":
        return value in wanted
    if value is None:
        return None
    if operator == "not_equals":
        return value not in wanted
    if operator == "contains":
        return any(w in value for w in wanted)
    if operator == "not_contains":
        return not any(w in value for w in wanted)
    number = _number(value)
    if number is None:
        return None
    limits = [float(w) for w in wanted]
    if operator == "above":
        return number > limits[0]
    if operator == "below":
        return number < limits[0]
    return limits[0] <= number <= limits[1]  # between
