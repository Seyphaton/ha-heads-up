"""Settings page data: the options it edits, the people summary and the presets (D-117)."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from ..const import (
    DEFAULT_OPTIONS,
    OPT_DEDUPE_SECONDS,
    OPT_HUB_ENABLED,
    OPT_INSTALL_TOKEN,
    OPT_RATE_PER_DEVICE,
    OPT_RATE_TOTAL,
    OPT_RECENT_MESSAGES,
    OPT_SHOW_PANEL,
    OPT_TRACE_ENTRIES,
)
from ..manager import BannerManager

# option -> (minimum, maximum) for numbers; booleans have no range
RANGES: dict[str, tuple[int, int]] = {
    OPT_RATE_PER_DEVICE: (1, 600),
    OPT_RATE_TOTAL: (1, 6000),
    OPT_DEDUPE_SECONDS: (0, 3600),
    OPT_TRACE_ENTRIES: (50, 5000),
    OPT_RECENT_MESSAGES: (10, 1000),
}
BOOLEANS = (OPT_HUB_ENABLED, OPT_SHOW_PANEL)
EDITABLE = (*BOOLEANS, *RANGES)


def read_options(manager: BannerManager) -> dict[str, Any]:
    return {key: manager.options.get(key, DEFAULT_OPTIONS[key]) for key in EDITABLE}


def token(manager: BannerManager) -> str:
    return str(manager.options.get(OPT_INSTALL_TOKEN) or "")


def people(hass: HomeAssistant, manager: BannerManager) -> list[dict[str, Any]]:
    """Persons with their usable devices, for the summary table. Empty while the hub is off."""
    hub = manager.hub
    if hub is None:
        return []
    rows = []
    for state in sorted(hass.states.async_all("person"), key=lambda s: s.entity_id):
        profile = hub.resolver.profile(state.entity_id)
        rows.append(
            {
                "person": state.entity_id,
                "name": state.attributes.get("friendly_name") or state.entity_id,
                "user": bool(state.attributes.get("user_id")),
                "devices": len(profile.usable),
                "devices_total": len(profile.devices),
                "channels": list(profile.channels),
            }
        )
    return rows
