"""A message's progress bar: an entity value scaled to a percentage (D-256, D-258)."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

DEFAULT_MIN = 0.0
DEFAULT_MAX = 100.0


def percent(raw: str, spec: Mapping[str, Any]) -> int | None:
    """The state text as 0 to 100 within the spec's min and max, or None when it is no number.
    Values outside the range stop at the ends."""
    try:
        value = float(raw)
    except TypeError, ValueError:
        return None
    low = float(spec.get("min", DEFAULT_MIN))
    high = float(spec.get("max", DEFAULT_MAX))
    if not math.isfinite(value) or high <= low:
        return None
    return round(100 * min(max((value - low) / (high - low), 0.0), 1.0))
