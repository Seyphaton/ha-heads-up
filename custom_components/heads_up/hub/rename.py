"""Follow an entity ID the user changed in Home Assistant (D-201).

Audiences, groups, profiles, rules, policy targets and stored messages hold entity IDs of persons,
speakers, zones and watched entities. When one of them is renamed, Home Assistant updates its own
automations and dashboards but not other integrations' settings, so the integration rewrites its
own copies once and records it in the trace. It never touches anything of another integration.
"""

from __future__ import annotations

import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from ..const import OPT_ATTENTION_DISMISSED, OPT_SPEAK_TTS_ENTITY

# Fields that hold text with entity IDs inside it (a template, a message), not a bare ID.
TEXT_KEYS = ("template", "message")


def _token(old: str) -> re.Pattern[str]:
    # An entity ID inside text: not part of a longer ID (`sensor.a` is not in `sensor.ab`).
    return re.compile(rf"(?<![\w.]){re.escape(old)}(?![\w])")


def rewrite(value: Any, old: str, new: str, key: str = "") -> Any:
    """`value` with every bare entity ID `old` replaced by `new`, and in text fields too."""
    if isinstance(value, str):
        if value == old:
            return new
        if key in TEXT_KEYS and old in value:
            return _token(old).sub(new, value)
        return value
    if isinstance(value, list):
        return [rewrite(v, old, new, key) for v in value]
    if isinstance(value, dict):
        return {k: rewrite(v, old, new, str(k)) for k, v in value.items()}
    return value


def _dismissed(keys: list[str], old: str, new: str) -> list[str]:
    return [k.replace(f"|{old}|", f"|{new}|") for k in keys]


@callback
def follow_renames(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Listen for entity ID changes for as long as the entry is loaded."""

    @callback
    def _changed(event: Event[Any]) -> None:
        data: Any = event.data
        old = data.get("old_entity_id")
        if data.get("action") != "update" or not old:
            return
        apply_rename(hass, entry, str(old), str(data["entity_id"]))

    entry.async_on_unload(hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, _changed))


def apply_rename(hass: HomeAssistant, entry: ConfigEntry, old: str, new: str) -> int:
    """Rewrite the integration's own references; returns how many places changed."""
    changed = 0
    for sub in list(entry.subentries.values()):
        rewritten = rewrite(dict(sub.data), old, new)
        if rewritten != dict(sub.data):
            hass.config_entries.async_update_subentry(entry, sub, data=rewritten)
            changed += 1
    options = dict(entry.options)
    if options.get(OPT_SPEAK_TTS_ENTITY) == old:
        options[OPT_SPEAK_TTS_ENTITY] = new
    if isinstance(options.get(OPT_ATTENTION_DISMISSED), list):
        options[OPT_ATTENTION_DISMISSED] = _dismissed(options[OPT_ATTENTION_DISMISSED], old, new)
    if options != dict(entry.options):
        hass.config_entries.async_update_entry(entry, options=options)
        changed += 1
    manager = getattr(entry, "runtime_data", None)
    if manager is not None:
        changed += manager.rename_entity(old, new)
        if manager.hub is not None:
            changed += manager.hub.rename_entity(old, new)
    if changed and manager is not None and manager.hub is not None:
        manager.hub.record("entity_renamed", f"{old} > {new}")
    return changed
