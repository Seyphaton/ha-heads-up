"""Loudness presets of the Settings page (UX_SPEC, D-117). Sample content: each preset adds the
policies it names that do not exist yet and never changes or deletes one."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant

from ..const import POLICY_SUBENTRY
from .policies.matching import duplicate_of
from .policies.models import parse_policy, policy_from_data

_COMMON = {"severities": [], "tags": [], "enabled": True}

POLICIES: dict[str, dict[str, Any]] = {
    "Night quiet": {
        **_COMMON,
        "type": "quiet_hours",
        "from_time": "22:00:00",
        "to_time": "07:00:00",
        "days": [],
        "action": "quiet",
        "critical_passes": True,
    },
    "Water escalation": {
        **_COMMON,
        "type": "escalation",
        "severities": ["critical"],
        "tags": ["water"],
        "after_minutes": 5,
        "channels": ["push"],
        "targets": {"push": {"audience": "Admins"}},
        "dismiss_acks": False,
    },
    # Only messages tagged "digest" are collected, so nothing is hidden by surprise.
    "Evening summary": {
        **_COMMON,
        "type": "summarize",
        "severities": ["info", "success"],
        "tags": ["digest"],
        "summary_at": "20:00:00",
        "include_critical": False,
    },
    "Warning reminders": {
        **_COMMON,
        "type": "reminder",
        "severities": ["warning"],
        "every_minutes": 30,
        "max_count": 3,
        "channels": [],
    },
    "Push failed fallback": {
        **_COMMON,
        "type": "fallback",
        "when": "failed",
        "channels": ["persistent"],
        "targets": {},
    },
}
PRESETS: dict[str, list[str]] = {
    "quiet": ["Night quiet"],
    "balanced": ["Night quiet", "Water escalation", "Evening summary"],
    "loud": [
        "Night quiet",
        "Water escalation",
        "Evening summary",
        "Warning reminders",
        "Push failed fallback",
    ],
}


def _existing(entry: ConfigEntry[Any]) -> list[ConfigSubentry]:
    return [s for s in entry.subentries.values() if s.subentry_type == POLICY_SUBENTRY]


def overview(entry: ConfigEntry[Any]) -> list[dict[str, Any]]:
    """Each preset with its policies and which of them are missing."""
    names = {s.title.casefold() for s in _existing(entry)}
    return [
        {
            "id": preset,
            "policies": policies,
            "missing": [p for p in policies if p.casefold() not in names],
        }
        for preset, policies in PRESETS.items()
    ]


def apply(hass: HomeAssistant, entry: ConfigEntry[Any], preset: str) -> dict[str, Any]:
    """Add the missing policies of a preset. A policy that exists by name, or one identical in
    type, applies-to and trigger, is skipped."""
    added: list[str] = []
    skipped: list[dict[str, str]] = []
    for name in PRESETS[preset]:
        existing = [p for s in _existing(entry) if (p := parse_policy(s)) is not None]
        data = POLICIES[name]
        if any(p.name.casefold() == name.casefold() for p in existing):
            skipped.append({"name": name, "reason": "exists"})
            continue
        candidate = policy_from_data(name, "", data)
        if candidate is not None and duplicate_of(existing, candidate) is not None:
            skipped.append({"name": name, "reason": "duplicate"})
            continue
        hass.config_entries.async_add_subentry(
            entry,
            ConfigSubentry(
                data=data,  # type: ignore[arg-type]
                subentry_type=POLICY_SUBENTRY,
                title=name,
                unique_id=None,
            ),
        )
        added.append(name)
    return {"added": added, "skipped": skipped}
