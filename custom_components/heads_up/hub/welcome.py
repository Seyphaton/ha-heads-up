"""The welcome: default policies an admin switches on or off on the first opening (D-121).

Each item creates the policies it names that do not exist yet, and never changes or deletes one. The
audience of Critical and the speakers are chosen in the welcome: a policy cannot mean "the people of
the original call".
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant

from ..const import DEFAULT_OPTIONS, OPT_POLICY_MODE, OPT_PUSH_LEVELS, POLICY_SUBENTRY
from .policies.matching import duplicate_of
from .policies.models import parse_policy, policy_from_data

ITEMS = ("quiet", "digest", "critical", "warnings")
# The items offered per mode, in the order their policies are created (and so listed). Under "first"
# only one policy runs per message, so each item stands alone and they do not overlap (D-150).
ITEMS_BY_MODE = {
    "first": ("critical", "warnings", "digest", "quiet"),
    "all": ("quiet", "digest", "critical", "warnings"),
}
DEFAULT_AUDIENCE = "Admins"
OPT_WELCOME_SEEN = "welcome_seen"
_COMMON = {"severities": [], "tags": [], "enabled": True}


def _alone(item: str, audience: str) -> dict[str, dict[str, Any]]:
    """The policies of an item under the mode "first": one policy for one kind of message."""
    quiet_severities = ["info", "success"]
    if item == "quiet":
        return {
            "Night quiet": {
                **_COMMON,
                "type": "quiet_hours",
                "severities": quiet_severities,
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
                "severities": quiet_severities,
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
    return {
        "Critical delivery": {
            **_COMMON,
            "type": "deliver",
            "severities": ["critical"],
            "channels": ["push"],
            "targets": {"push": {"audience": audience}},
        }
    }


def policies_for(
    item: str, audience: str, speakers: list[str], mode: str = "all"
) -> dict[str, dict[str, Any]]:
    """The policies an item creates, by name."""
    if mode == "first":
        return _alone(item, audience)
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


def overview(entry: ConfigEntry[Any], mode: str = "all") -> list[dict[str, Any]]:
    """Each item of the mode with its policies and which of them do not exist yet."""
    names = {
        s.title.casefold() for s in entry.subentries.values() if s.subentry_type == POLICY_SUBENTRY
    }
    out = []
    for item in ITEMS_BY_MODE[mode]:
        wanted = list(policies_for(item, DEFAULT_AUDIENCE, ["speaker"], mode))
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
    mode: str = "all",
) -> dict[str, Any]:
    """Create the policies of the chosen items, in the order of the mode, and store the mode. One
    that exists by name, or does the same as one that exists, is skipped. Critical also sets the
    push level of critical to iOS critical."""
    added: list[str] = []
    skipped: list[dict[str, str]] = []
    for item in [i for i in ITEMS_BY_MODE[mode] if i in items]:
        for name, data in policies_for(item, audience, speakers, mode).items():
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
    options = {**entry.options, OPT_WELCOME_SEEN: True, OPT_POLICY_MODE: mode}
    if "critical" in items:
        levels = {**DEFAULT_OPTIONS[OPT_PUSH_LEVELS], **entry.options.get(OPT_PUSH_LEVELS, {})}  # type: ignore[dict-item]
        options[OPT_PUSH_LEVELS] = {**levels, "critical": "critical"}
    hass.config_entries.async_update_entry(entry, options=options)
    return {"added": added, "skipped": skipped}
