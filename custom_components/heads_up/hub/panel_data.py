"""What the panel's Overview and Messages pages show (D-118).

The server sends structured fields and no text: the panel words them in four languages. The
checks of "Needs attention" are pure functions over plain data, so each one has a test.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..const import POLICY_SUBENTRY, POLICY_TYPES, RULE_SUBENTRY
from ..manager import BannerManager
from .ledger import State
from .policies import away, deliver, escalation, fallback, quiet, reminder, summarize
from .policies.matching import applies
from .policies.models import Policy, parse_policy
from .presence import UNKNOWN_STATES
from .recipients import area_speakers

CHECKS = {
    "escalation": escalation.check,
    "reminder": reminder.check,
    "quiet_hours": quiet.check,
    "away": away.check,
    "fallback": fallback.check,
    "summarize": summarize.check,
    "deliver": deliver.check,
}


@dataclass(frozen=True, slots=True)
class Attention:
    kind: str  # a stable code the panel words
    level: str  # error or warning
    subject: str  # the object: a rule, person, group, policy or device
    detail: str | None = None  # a reason code or a name
    page: str = ""  # the panel page that fixes it

    def as_dict(self) -> dict[str, str | None]:
        return {
            "kind": self.kind,
            "level": self.level,
            "subject": self.subject,
            "detail": self.detail,
            "page": self.page,
        }


# Needs attention: pure checks --------------------------------------------------------------


def check_rule_entities(
    rules: list[dict[str, Any]], states: Mapping[str, str | None]
) -> list[Attention]:
    """A rule that watches an entity that is unavailable, unknown or gone (error)."""
    found = []
    for rule in rules:
        entity = rule.get("entity_id")
        if not rule.get("enabled", True) or not entity:
            continue
        state = states.get(entity)
        if state is None or state in UNKNOWN_STATES:
            found.append(Attention("rule_entity", "error", rule["name"], entity, "rules"))
    return found


def check_devices(profiles: list[dict[str, Any]]) -> list[Attention]:
    """A device whose notify service Home Assistant does not have (error)."""
    return [
        Attention("device_service", "error", p["name"], d["name"] or d["device_id"], "recipients")
        for p in profiles
        for d in p["devices"]
        if not d["service_found"]
    ]


def check_people(profiles: list[dict[str, Any]]) -> list[Attention]:
    """A person with no usable device: push is skipped (warning)."""
    return [
        Attention("person_no_device", "warning", p["name"], None, "recipients")
        for p in profiles
        if not any(d["service_found"] for d in p["devices"])
    ]


def check_groups(groups: list[dict[str, Any]]) -> list[Attention]:
    """A recipient group that reaches no speaker (error)."""
    return [
        Attention("group_empty", "error", g["name"], None, "recipients")
        for g in groups
        if not g["reachable"]
    ]


def check_policies(
    policies: list[dict[str, Any]],
) -> list[Attention]:
    """A policy with invalid data, or one that names an audience or group that is gone (error)."""
    found = []
    for policy in policies:
        if (reason := policy["invalid"]) is not None:
            found.append(Attention("policy_invalid", "error", policy["name"], reason, "policies"))
        elif (problem := policy["problem"]) is not None:
            found.append(Attention("policy_target", "error", policy["name"], problem, "policies"))
    return found


def check_critical_escalation(policies: list[Policy]) -> list[Attention]:
    """No enabled escalation covers critical messages without a tag (warning)."""
    for policy in policies:
        if policy.enabled and policy.type == "escalation" and applies(policy, "critical", None):
            return []
    return [Attention("no_critical_escalation", "warning", "", None, "policies")]


def check_hub(enabled: bool) -> list[Attention]:
    return [] if enabled else [Attention("hub_off", "warning", "", None, "general")]


# Collectors --------------------------------------------------------------------------------


def _rule_data(entry: Any) -> list[dict[str, Any]]:
    return [
        {"id": f"rule_{s.subentry_id}", "name": s.title, **dict(s.data)}
        for s in entry.subentries.values()
        if s.subentry_type == RULE_SUBENTRY
    ]


def attention(hass: HomeAssistant, manager: BannerManager, entry: Any) -> list[dict[str, Any]]:
    hub = manager.hub
    states = {s.entity_id: s.state for s in hass.states.async_all()}
    found = check_hub(hub is not None)
    found += check_rule_entities(_rule_data(entry), states)
    if hub is not None:
        profiles = []
        for state in sorted(hass.states.async_all("person"), key=lambda s: s.entity_id):
            profile = hub.resolver.profile(state.entity_id)
            profiles.append(
                {
                    "name": state.attributes.get("friendly_name") or state.entity_id,
                    "devices": [
                        {"name": d.name, "device_id": d.device_id, "service_found": d.service_found}
                        for d in profile.devices
                    ],
                }
            )
        found += check_devices(profiles) + check_people(profiles)
        groups = [
            {
                "name": g.name,
                "reachable": any(hass.states.get(m) is not None for m in g.members)
                or any(area_speakers(hass, a) for a in g.areas),
            }
            for g in hub.resolver.groups()
        ]
        found += check_groups(groups)
        found += check_policies(_policy_inputs(entry, hub))
        found += check_critical_escalation(hub.policies.all())
    return [item.as_dict() for item in found]


def _policy_inputs(entry: Any, hub: Any) -> list[dict[str, Any]]:
    out = []
    for sub in entry.subentries.values():
        if sub.subentry_type != POLICY_SUBENTRY:
            continue
        data = dict(sub.data)
        kind = data.get("type")
        invalid = None
        if kind not in POLICY_TYPES:
            invalid = "unknown_type"
        else:
            errors = CHECKS[kind](data)
            invalid = next(iter(errors.values()), None)
        policy = parse_policy(sub)
        problem = hub.policy_problem(policy) if policy is not None and invalid is None else None
        out.append({"name": sub.title, "invalid": invalid, "problem": problem})
    return out


# Overview ----------------------------------------------------------------------------------


def _messages(manager: BannerManager) -> list[Any]:
    return [b for b in [*manager.banners.values(), *manager.rules.values()] if b.active]


def message_states(manager: BannerManager, banner: Any) -> list[dict[str, Any]]:
    """Why a message is in the list: the states the Overview badges count."""
    hub = manager.hub
    states: list[dict[str, Any]] = []
    now = dt_util.utcnow()
    if hub is not None:
        held = hub.ledger.held.get(banner.id)
        if held is not None and not held.resolved:
            states.append({"state": "held", "policy": held.policy.split(":", 1)[-1]})
        for row in hub.ledger.timers(banner.id):
            kind, _, name = row.recipient.partition(":")
            if kind == "escalation" and not banner.acknowledged_by:
                if row.state is State.PLANNED:
                    states.append(
                        {
                            "state": "escalating",
                            "phase": "pending",
                            "policy": name,
                            "due": row.due.isoformat() if row.due else None,
                        }
                    )
                elif row.state is State.SENT:
                    states.append({"state": "escalating", "phase": "sent", "policy": name})
            elif kind == "reminder" and row.state is State.PLANNED and not banner.acknowledged_by:
                states.append(
                    {
                        "state": "reminding",
                        "policy": name,
                        "due": row.due.isoformat() if row.due else None,
                        "count": row.count,
                    }
                )
    ends = [until for until in banner.snoozed_until.values() if until > now]
    if ends:
        states.append({"state": "snoozed", "until": max(ends).isoformat()})
    if banner.acknowledged_by:
        states.append({"state": "acknowledged", "count": len(banner.acknowledged_by)})
    return states


def rule_item(manager: BannerManager, rule: dict[str, Any]) -> dict[str, Any]:
    shown = manager.rules.get(rule["id"])
    return {
        "id": rule["id"],
        "name": rule["name"],
        "enabled": rule.get("enabled", True),
        "showing": bool(shown and shown.active),
        "severity": rule.get("severity", "warning"),
        "message": rule.get("message", ""),
        "entity_id": rule.get("entity_id"),
        "template": rule.get("template"),
        "operator": rule.get("operator", "equals"),
        "state": rule.get("state"),
        "attribute": rule.get("attribute"),
        "for": rule.get("for"),
    }


def overview(hass: HomeAssistant, manager: BannerManager, entry: Any) -> dict[str, Any]:
    items = []
    for banner in _messages(manager):
        items.append(
            {
                "id": banner.id,
                "title": banner.title,
                "message": banner.message,
                "severity": banner.severity,
                "source": banner.source,
                "states": message_states(manager, banner),
            }
        )
    counts = {
        key: sum(1 for i in items if any(s["state"] == key for s in i["states"]))
        for key in ("escalating", "reminding", "snoozed", "held", "acknowledged")
    }
    rules = [rule_item(manager, r) for r in _rule_data(entry)]
    hub = manager.hub
    return {
        "active": {"count": len(items), "counts": counts, "items": items},
        "rules": {
            "total": len(rules),
            "enabled": sum(1 for r in rules if r["enabled"]),
            "disabled": sum(1 for r in rules if not r["enabled"]),
            "showing": sum(1 for r in rules if r["showing"]),
            "items": rules,
        },
        "attention": attention(hass, manager, entry),
        "log": hub.log.latest(50) if hub is not None else [],
        "first_run": hub is not None and not hub.policies.all(),
    }


# Messages ----------------------------------------------------------------------------------


def messages(manager: BannerManager) -> list[dict[str, Any]]:
    """The recent messages with their delivery results counted from the trace."""
    hub = manager.hub
    if hub is None:
        return []
    out = []
    for item in hub.recent.listed():
        counts: dict[str, int] = {}
        for entry in hub.trace.entries(item["id"]):
            if entry["result"] in ("sent", "held", "skipped", "failed"):
                counts[entry["result"]] = counts.get(entry["result"], 0) + 1
        live = manager.banners.get(item["id"]) or manager.rules.get(item["id"])
        out.append(
            {
                **item,
                "active": live is not None and live.active,
                "results": counts,
                "states": message_states(manager, live) if live is not None else [],
            }
        )
    return out


def trace(hass: HomeAssistant, manager: BannerManager, message_id: str) -> dict[str, Any] | None:
    """The delivery trace of one message: entries, deliveries, timers, acknowledgements."""
    hub = manager.hub
    if hub is None:
        return None
    live = manager.banners.get(message_id) or manager.rules.get(message_id)
    known = next((m for m in hub.recent.listed() if m["id"] == message_id), None)
    if live is None and known is None:
        return None
    return {
        "id": message_id,
        "message": known,
        "entries": hub.trace.entries(message_id),
        "deliveries": [
            {
                "channel": r.channel,
                "recipient": r.recipient,
                "state": r.state.value,
                "person": r.person,
                "due": r.due.isoformat() if r.due else None,
                "hold": r.hold,
            }
            for r in hub.ledger.for_message(message_id)
        ],
        "timers": [
            {
                "type": r.recipient.partition(":")[0],
                "policy": r.recipient.partition(":")[2],
                "state": r.state.value,
                "due": r.due.isoformat() if r.due else None,
                "count": r.count,
            }
            for r in hub.ledger.timers(message_id)
        ],
        "acknowledged_by": [
            name
            for user in (live.acknowledged_by if live else [])
            if (name := manager._first_name(user))
        ],
        "acknowledged_count": len(live.acknowledged_by) if live else 0,
        "held": hub.is_held(message_id),
    }
