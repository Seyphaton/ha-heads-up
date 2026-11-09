"""Diagnostics: the configuration and the recent delivery trace, without addresses (D-194)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Mail addresses are household data; the install token is part of push tags.
TO_REDACT = {"mail_global_address", "mail_address", "install_token"}
TRACE_ENTRIES = 200


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    manager = entry.runtime_data
    hub = manager.hub
    data: dict[str, Any] = {
        "options": dict(entry.options),
        "subentries": [
            {"type": s.subentry_type, "title": s.title, "data": dict(s.data)}
            for s in entry.subentries.values()
        ],
        "counts": {
            "messages": len(manager.banners),
            "rules": len(manager.rules),
            "delivery_rows": len(hub.ledger.rows) if hub else 0,
        },
    }
    if hub is not None:
        data["policy_order"] = [p.name for p in hub.policies.ordered()]
        data["trace"] = hub.trace.entries(limit=TRACE_ENTRIES)
        # Titles and texts stay out: they are what the household wrote.
        data["recent_messages"] = [
            {k: m.get(k) for k in ("id", "severity", "channels", "source", "created_at", "ended")}
            for m in hub.recent.listed()
        ]
    return async_redact_data(data, TO_REDACT)
