"""The welcome: default policies an admin switches on or off on the first opening (D-121).

Each item creates the policies it names that do not exist yet, and never changes or deletes one. The
audience of Critical and the speakers are chosen in the welcome: a policy cannot mean "the people of
the original call".
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant

from ..const import DEFAULT_OPTIONS, OPT_PUSH_LEVELS, POLICY_SUBENTRY
from .policies.matching import duplicate_of
from .policies.models import parse_policy, policy_from_data

ITEMS = ("quiet", "digest", "critical", "warnings")
DEFAULT_AUDIENCE = "Admins"
OPT_WELCOME_SEEN = "welcome_seen"
_COMMON = {"severities": [], "tags": [], "enabled": True}


def policies_for(item: str, audience: str, speakers: list[str]) -> dict[str, dict[str, Any]]:
    """The policies an item creates, by name."""
    if item == "quiet":
        return {
            "Night quiet": {
                **_COMMON,
                "type": "quiet_hours",
                "from_time": "22:00:00",
                "to_time": "07:00:00",
                "days": [],
                "action": "quiet",
                "critical_passes": True,
            }
        }
    if item == "digest":
        return {
            "Evening summary": {
                **_COMMON,
                "type": "summarize",
                "tags": ["digest"],
                "summary_at": "20:00:00",
                "include_critical": False,
            }
        }
    if item == "warnings":
        return {
            "Warning reminders": {
                **_COMMON,
                "type": "reminder",
                "severities": ["warning"],
                "every_minutes": 30,
                "max_count": 3,
                "channels": [],
            }
        }
    critical = {
        "Critical delivery": {
            **_COMMON,
            "type": "deliver",
            "severities": ["critical"],
            "channels": ["push"],
            "targets": {"push": {"audience": audience}},
        },
        "Critical reminder": {
            **_COMMON,
            "type": "reminder",
            "severities": ["critical"],
            "every_minutes": 10,
            "max_count": 3,
            "channels": ["push"],
        },
    }
    if speakers:  # without speakers there is nothing to say anything on
        critical["Critical escalation"] = {
            **_COMMON,
            "type": "escalation",
            "severities": ["critical"],
            "after_minutes": 10,
            "channels": ["speak"],
            "targets": {"speak": {"recipients": list(speakers)}},
            "dismiss_acks": True,
        }
    return critical


def overview(entry: ConfigEntry[Any]) -> list[dict[str, Any]]:
    """Each item with its policies and which of them do not exist yet."""
    names = {
        s.title.casefold() for s in entry.subentries.values() if s.subentry_type == POLICY_SUBENTRY
    }
    out = []
    for item in ITEMS:
        wanted = list(policies_for(item, DEFAULT_AUDIENCE, ["speaker"]))
        out.append(
            {
                "id": item,
                "policies": wanted,
                "missing": [p for p in wanted if p.casefold() not in names],
            }
        )
    return out


def apply(
    hass: HomeAssistant,
    entry: ConfigEntry[Any],
    items: list[str],
    audience: str,
    speakers: list[str],
) -> dict[str, Any]:
    """Create the policies of the chosen items. One that exists by name, or does the same as one
    that exists, is skipped. Critical also sets the push level of critical to iOS critical."""
    added: list[str] = []
    skipped: list[dict[str, str]] = []
    for item in items:
        for name, data in policies_for(item, audience, speakers).items():
            existing = [
                p
                for s in entry.subentries.values()
                if s.subentry_type == POLICY_SUBENTRY and (p := parse_policy(s)) is not None
            ]
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
    options = {**entry.options, OPT_WELCOME_SEEN: True}
    if "critical" in items:
        levels = {**DEFAULT_OPTIONS[OPT_PUSH_LEVELS], **entry.options.get(OPT_PUSH_LEVELS, {})}  # type: ignore[dict-item]
        options[OPT_PUSH_LEVELS] = {**levels, "critical": "critical"}
    hass.config_entries.async_update_entry(entry, options=options)
    return {"added": added, "skipped": skipped}
