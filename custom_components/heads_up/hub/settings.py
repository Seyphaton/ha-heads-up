"""Settings page data: the options it edits, the people summary and the layout (D-117, D-122)."""

from __future__ import annotations

from typing import Any

import probatio as vol
from homeassistant.core import HomeAssistant

from ..const import (
    DEFAULT_OPTIONS,
    DEFAULT_SNOOZE_SECONDS,
    DISMISS_SCOPES,
    MAX_TIMEOUT_DAYS,
    OPT_DEDUPE_SECONDS,
    OPT_DEFAULT_DISMISS_SCOPE,
    OPT_DEFAULT_SNOOZABLE,
    OPT_DEFAULT_SNOOZE_OPTIONS,
    OPT_DEFAULT_SNOOZE_SCOPE,
    OPT_DEFAULT_TIMEOUT,
    OPT_DISABLE_ENDED_BUTTONS,
    OPT_EVICT,
    OPT_INSTALL_TOKEN,
    OPT_MAX_BANNERS,
    OPT_PRESENCE_DEBOUNCE,
    OPT_QUICK_SNOOZE,
    OPT_RATE_PER_DEVICE,
    OPT_RATE_TOTAL,
    OPT_RECENT_MESSAGES,
    OPT_SHOW_PANEL,
    OPT_SPEAK_COOLDOWN,
    OPT_SPEAK_MAX_LENGTH,
    OPT_SPEAK_TTS_ENTITY,
    OPT_TRACE_ENTRIES,
    SNOOZE_PRESET_MINUTES,
    SNOOZE_SCOPES,
)
from ..manager import BannerManager

# The one definition of the settings that the integration's options form and the panel's Settings
# page are both built from: sections in order, then the entries of a section in order, each with
# its kind. Texts live in strings.json (options.step.init.sections); the panel keeps the same
# wording in its own tables and a test compares them.
SECTIONS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("sidebar", ((OPT_SHOW_PANEL, "bool"),)),
    (
        "dismiss",
        (
            (OPT_DEFAULT_DISMISS_SCOPE, "choice"),
            (OPT_DEFAULT_TIMEOUT, "duration"),
            (OPT_DISABLE_ENDED_BUTTONS, "bool"),
        ),
    ),
    ("snooze", ((OPT_DEFAULT_SNOOZABLE, "bool"), (OPT_DEFAULT_SNOOZE_SCOPE, "choice"))),
    ("snooze_banner", ((OPT_DEFAULT_SNOOZE_OPTIONS, "minutes"),)),
    ("snooze_push", ((OPT_QUICK_SNOOZE, "int"),)),
    ("presence", ((OPT_PRESENCE_DEBOUNCE, "int"),)),
    (
        "speech",
        ((OPT_SPEAK_MAX_LENGTH, "int"), (OPT_SPEAK_COOLDOWN, "int"), (OPT_SPEAK_TTS_ENTITY, "tts")),
    ),
    (
        "limits",
        (
            (OPT_MAX_BANNERS, "int"),
            (OPT_EVICT, "bool"),
            (OPT_RATE_PER_DEVICE, "int"),
            (OPT_RATE_TOTAL, "int"),
            (OPT_DEDUPE_SECONDS, "int"),
        ),
    ),
    ("history", ((OPT_TRACE_ENTRIES, "int"), (OPT_RECENT_MESSAGES, "int"))),
)

# option -> (minimum, maximum) for numbers
RANGES: dict[str, tuple[int, int]] = {
    OPT_MAX_BANNERS: (1, 200),
    OPT_QUICK_SNOOZE: (1, 1440),
    OPT_PRESENCE_DEBOUNCE: (0, 600),
    OPT_SPEAK_MAX_LENGTH: (20, 1000),
    OPT_SPEAK_COOLDOWN: (0, 3600),
    OPT_RATE_PER_DEVICE: (1, 600),
    OPT_RATE_TOTAL: (1, 6000),
    OPT_DEDUPE_SECONDS: (0, 3600),
    OPT_TRACE_ENTRIES: (50, 5000),
    OPT_RECENT_MESSAGES: (10, 1000),
}
CHOICES: dict[str, tuple[str, ...]] = {
    OPT_DEFAULT_DISMISS_SCOPE: DISMISS_SCOPES,
    OPT_DEFAULT_SNOOZE_SCOPE: SNOOZE_SCOPES,
}
BOOLEANS = tuple(key for _, items in SECTIONS for key, kind in items if kind == "bool")
EDITABLE = tuple(key for _, items in SECTIONS for key, _ in items)
MAX_TIMEOUT_SECONDS = MAX_TIMEOUT_DAYS * 86400


def layout() -> list[dict[str, Any]]:
    """The sections for the panel: kind, range or choices per entry."""
    sections = []
    for name, items in SECTIONS:
        entries = []
        for key, kind in items:
            entry: dict[str, Any] = {"key": key, "kind": kind}
            if key in RANGES:
                entry["range"] = list(RANGES[key])
            if key in CHOICES:
                entry["choices"] = list(CHOICES[key])
            if kind == "minutes":
                entry["choices"] = list(SNOOZE_PRESET_MINUTES)
            if kind == "duration":
                entry["range"] = [0, MAX_TIMEOUT_SECONDS]
            entries.append(entry)
        sections.append({"name": name, "entries": entries})
    return sections


def schema_fields() -> dict[Any, Any]:
    """Voluptuous keys of settings_set, in the units the panel uses (snooze choices in minutes)."""
    fields: dict[Any, Any] = {vol.Optional(key): bool for key in BOOLEANS}
    for key, (low, high) in RANGES.items():
        fields[vol.Optional(key)] = vol.All(int, vol.Range(min=low, max=high))
    for key, choices in CHOICES.items():
        fields[vol.Optional(key)] = vol.In(choices)
    fields[vol.Optional(OPT_DEFAULT_TIMEOUT)] = vol.All(
        int, vol.Range(min=0, max=MAX_TIMEOUT_SECONDS)
    )
    fields[vol.Optional(OPT_DEFAULT_SNOOZE_OPTIONS)] = [vol.In(SNOOZE_PRESET_MINUTES)]
    fields[vol.Optional(OPT_SPEAK_TTS_ENTITY)] = vol.Any("", vol.Match(r"^tts\.[a-z0-9_]+$"))
    return fields


def snooze_seconds(minutes: list[Any] | None) -> list[int]:
    # An empty choice falls back to the defaults, so a snoozable banner always has a menu.
    chosen = sorted({int(m) * 60 for m in minutes or []})
    return chosen or list(DEFAULT_SNOOZE_SECONDS)


def to_stored(changes: dict[str, Any]) -> dict[str, Any]:
    """Panel units to stored units."""
    out = dict(changes)
    if OPT_DEFAULT_SNOOZE_OPTIONS in out:
        out[OPT_DEFAULT_SNOOZE_OPTIONS] = snooze_seconds(out[OPT_DEFAULT_SNOOZE_OPTIONS])
    return out


def read_options(manager: BannerManager) -> dict[str, Any]:
    values = {key: manager.options.get(key, DEFAULT_OPTIONS[key]) for key in EDITABLE}
    values[OPT_DEFAULT_SNOOZE_OPTIONS] = [m // 60 for m in values[OPT_DEFAULT_SNOOZE_OPTIONS]]
    return values


def token(manager: BannerManager) -> str:
    return str(manager.options.get(OPT_INSTALL_TOKEN) or "")


def people(hass: HomeAssistant, manager: BannerManager) -> list[dict[str, Any]]:
    """Persons with their usable devices, for the summary table."""
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
