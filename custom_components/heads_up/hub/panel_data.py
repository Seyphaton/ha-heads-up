"""What the panel's Overview and Messages pages show (D-118).

The server sends structured fields and no text: the panel words them in four languages. The
checks of "Needs attention" are pure functions over plain data, so each one has a test.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..const import (
    AUDIENCE_SUBENTRY,
    BUILTIN_AUDIENCES,
    CHANNELS,
    OPT_ATTENTION_DISMISSED,
    OPT_MAIL_SERVICE,
    POLICY_SUBENTRY,
    POLICY_TYPES,
    RULE_SUBENTRY,
)
from ..manager import BannerManager
from .activity import ActivityLog
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
    count: int | None = None  # how often, for a problem that repeats
    ref: str = ""  # the object's key when its name can change; a dismissal remembers it (D-199)

    @property
    def key(self) -> str:
        """What a dismissal remembers: the same problem on the same object."""
        return f"{self.kind}|{self.ref or self.subject}|{self.detail or ''}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "level": self.level,
            "subject": self.subject,
            "detail": self.detail,
            "page": self.page,
            "count": self.count,
            "key": self.key,
            # Warnings can be hidden; an error means something is broken and stays.
            "dismissible": self.level == "warning",
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


def _accepts_push(profile: dict[str, Any]) -> bool:
    if not profile.get("enabled", True):
        return False
    channels = profile.get("channels")
    return channels is None or "push" in channels


def check_devices(profiles: list[dict[str, Any]]) -> list[Attention]:
    """A device whose notify service Home Assistant does not have (error). A person who does not
    accept push is not checked: nothing is pushed to their devices."""
    return [
        Attention("device_service", "error", p["name"], d["name"] or d["device_id"], "recipients")
        for p in profiles
        if _accepts_push(p)
        for d in p["devices"]
        if not d["service_found"]
    ]


def check_people(profiles: list[dict[str, Any]]) -> list[Attention]:
    """A person with no usable device: push is skipped (warning). Not for a person whose profile
    does not accept push."""
    return [
        Attention(
            "person_no_device", "warning", p["name"], None, "recipients", ref=p.get("person", "")
        )
        for p in profiles
        if _accepts_push(p) and not any(d["service_found"] for d in p["devices"])
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


FAILURE_WINDOW = timedelta(hours=24)


def check_failures(log: list[dict[str, Any]], now: datetime) -> list[Attention]:
    """Sends that failed in the last 24 hours, one item per channel and reason (warning).

    The log is memory only, so after a restart this starts empty. Skipped deliveries are
    choices (quiet hours, a limit) and are not counted here.
    """
    counts: dict[tuple[str, str], int] = {}
    for entry in log:
        if entry["kind"] != "failed":
            continue
        if now - dt_util.parse_datetime(entry["time"]) > FAILURE_WINDOW:  # type: ignore[operator]
            continue
        channel, _, reason = str(entry.get("detail") or "").partition("|")
        counts[(channel, reason or "unknown")] = counts.get((channel, reason or "unknown"), 0) + 1
    return [
        Attention("delivery_failed", "warning", channel, reason, "messages", count)
        for (channel, reason), count in sorted(counts.items())
    ]


def check_critical_escalation(policies: list[Policy]) -> list[Attention]:
    """No enabled escalation covers critical messages without a tag (warning)."""
    for policy in policies:
        if policy.enabled and policy.type == "escalation" and applies(policy, "critical", None):
            return []
    return [Attention("no_critical_escalation", "warning", "", None, "policies")]


# Collectors --------------------------------------------------------------------------------


def _rule_data(entry: Any) -> list[dict[str, Any]]:
    return [
        {"id": f"rule_{s.subentry_id}", "name": s.title, **dict(s.data)}
        for s in entry.subentries.values()
        if s.subentry_type == RULE_SUBENTRY
    ]


def check_references(policy_refs: list[tuple[str, str, str, str]], known: Any) -> list[Attention]:
    """A rule or a stored message that names a policy that no longer exists (error). Each item
    is (page, subject, ref of the owner, policy reference); `known(ref)` says whether it exists.
    Nothing is re-linked by name: a new policy with the old name is a different policy (D-199)."""
    found = []
    for page, subject, owner, ref in policy_refs:
        if ref in ("none", "automatic") or known(ref):
            continue
        shown = ref[len("name:") :] if ref.startswith("name:") else ref
        found.append(Attention("reference_missing", "error", subject, shown, page, ref=owner))
    return found


def check_mail_service(service: str, exists: bool) -> list[Attention]:
    """The notify service that sends mail is not registered (error): it was renamed or removed
    in the integration that provides it. Nothing here can repair another integration's name."""
    return [] if not service or exists else [Attention("mail_service_missing", "error", service)]


def attention(hass: HomeAssistant, manager: BannerManager, entry: Any) -> list[dict[str, Any]]:
    hub = manager.hub
    states = {s.entity_id: s.state for s in hass.states.async_all()}
    found = check_rule_entities(_rule_data(entry), states)
    if hub is not None:
        profiles = []
        for state in sorted(hass.states.async_all("person"), key=lambda s: s.entity_id):
            profile = hub.resolver.profile(state.entity_id)
            profiles.append(
                {
                    "name": state.attributes.get("friendly_name") or state.entity_id,
                    "person": state.entity_id,
                    "enabled": profile.enabled,
                    "channels": list(profile.channels),
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
        refs = [
            ("rules", s.title, f"rule_{s.subentry_id}", str(s.data["policy"]))
            for s in entry.subentries.values()
            if s.subentry_type == RULE_SUBENTRY and s.data.get("policy")
        ]
        for banner in manager.banners.values():
            policy = banner.policy if isinstance(banner.policy, list) else [banner.policy]
            refs += [("messages", banner.title or banner.id, banner.id, p) for p in policy if p]
        found += check_references(refs, lambda ref: hub.policies.get(ref) is not None)
        service = str(manager.options.get(OPT_MAIL_SERVICE) or "")
        found += check_mail_service(service, hass.services.has_service("notify", service))
        found += check_critical_escalation(hub.policies.all())
        found += check_failures(hub.log.latest(), dt_util.utcnow())
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


def _policy_kind_name(hub: Any, key: str) -> tuple[str, str]:
    """The type and the current name of the policy a timer row holds; a deleted one keeps what
    the key shows (an ID is not a name, so its name is unknown)."""
    policy = hub.policies.by_key(key)
    if policy is not None:
        return policy.type, policy.name
    kind, _, name = key.partition(":")
    return (kind, name) if name else ("", "")


def _policy_label(hub: Any, key: str) -> str:
    return _policy_kind_name(hub, key)[1]


def message_states(manager: BannerManager, banner: Any) -> list[dict[str, Any]]:
    """Why a message is in the list: the states the Overview badges count."""
    hub = manager.hub
    states: list[dict[str, Any]] = []
    now = dt_util.utcnow()
    if hub is not None:
        held = hub.ledger.held.get(banner.id)
        if held is not None and not held.resolved:
            states.append({"state": "held", "policy": _policy_label(hub, held.policy)})
        for row in hub.ledger.timers(banner.id):
            kind, name = _policy_kind_name(hub, row.recipient)
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


def shortcuts(entry: Any, manager: BannerManager) -> dict[str, Any]:
    """The numbers on the Overview's shortcut cards."""
    subs = list(entry.subentries.values())
    policies = [s for s in subs if s.subentry_type == POLICY_SUBENTRY]
    return {
        "channels": {"total": len(CHANNELS), "mail": bool(manager.options.get(OPT_MAIL_SERVICE))},
        "audiences": {
            "builtin": len(BUILTIN_AUDIENCES),
            "custom": sum(1 for s in subs if s.subentry_type == AUDIENCE_SUBENTRY),
        },
        "policies": {
            "total": len(policies),
            "enabled": sum(1 for s in policies if s.data.get("enabled", True)),
        },
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
    dismissed = set(entry.options.get(OPT_ATTENTION_DISMISSED, []))
    found = attention(hass, manager, entry)
    shown = [a for a in found if not (a["dismissible"] and a["key"] in dismissed)]
    hidden = len(found) - len(shown)
    return {
        "active": {"count": len(items), "counts": counts, "items": items},
        "rules": {
            "total": len(rules),
            "enabled": sum(1 for r in rules if r["enabled"]),
            "disabled": sum(1 for r in rules if not r["enabled"]),
            "showing": sum(1 for r in rules if r["showing"]),
            "items": rules,
        },
        "attention": shown,
        "attention_hidden": hidden,
        "shortcuts": shortcuts(entry, manager),
        "log": hub.log.latest(50) if hub is not None else [],
        "activity": (hub.log if hub is not None else ActivityLog(1)).created_histogram(
            dt_util.utcnow().timestamp()
        ),
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
                "type": _policy_kind_name(hub, r.recipient)[0],
                "policy": _policy_kind_name(hub, r.recipient)[1],
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
