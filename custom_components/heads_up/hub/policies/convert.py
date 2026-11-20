"""Conversion of stored policies from the 1.x list to the 2.0 lanes (DESIGN §25.6, D-224, D-234).

A pure function: it reads the policy subentries and the options of a version 2 entry (after the
2.4 step) and returns what to write. Nothing here touches Home Assistant, so the migration and
the tests share it.

1.x "only the first" used the first enabled automatic policy in list order that matched a
message. 2.0 has no order: every fitting policy acts. To keep 1.x behaviour, every automatic
policy gets `links` to the automatic policies above it whose "Which messages" can overlap; a link
is checked live against the linked policy's switch, so the 1.x result is reproduced exactly for
automatic matching. "All that apply" setups get no links (D-235).

The 1.x "Critical messages pass" (`critical_passes` on Quiet hours and Presence) and
`include_critical` on Summarize become one band entry "Critical" (D-224).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from ...const import SEVERITIES

OPT_POLICY_MODE_OLD = "policy_mode"
OPT_POLICY_ORDER_OLD = "policy_order"
OPT_CONVERSION_ITEMS = "conversion_items"
CRITICAL_ENTRY_NAME = "Critical"
REMOVED_FIELDS = ("critical_passes", "include_critical")

ITEM_LINKS = "links"
ITEM_NEVER_ACTS = "never_acts"
ITEM_HOLDS_ANYWAY = "holds_anyway"


@dataclass(frozen=True, slots=True)
class StoredPolicy:
    subentry_id: str
    title: str
    data: Mapping[str, Any]


@dataclass(slots=True)
class Converted:
    """What the migration writes: changed policy data by subentry ID, new policies (title,
    data), the new options, and the check-list items."""

    updates: dict[str, dict[str, Any]] = field(default_factory=dict)
    added: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    items: list[dict[str, str]] = field(default_factory=list)


def _automatic(data: Mapping[str, Any]) -> bool:
    return data.get("apply") != "manual"


def _enabled(data: Mapping[str, Any]) -> bool:
    return bool(data.get("enabled", True))


def _set(data: Mapping[str, Any], key: str) -> frozenset[str]:
    return frozenset(str(v) for v in data.get(key) or ())


def can_overlap(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Whether one message can fit both: a severity in both and a tag in both, where an empty
    list means any."""
    sa, sb = _set(a, "severities"), _set(b, "severities")
    ta, tb = _set(a, "tags"), _set(b, "tags")
    severities = not sa or not sb or bool(sa & sb)
    tags = not ta or not tb or bool(ta & tb)
    return severities and tags


def covered(policy: Mapping[str, Any], by: Iterable[Mapping[str, Any]]) -> bool:
    """Whether every (severity, tag) the policy fits is fitted by one of `by`. A message has one
    severity and at most one tag; a policy without tags also fits messages with an unknown tag
    or none, which only a policy without tags covers."""
    others = list(by)
    severities = _set(policy, "severities") or frozenset(SEVERITIES)
    tags = _set(policy, "tags")
    for severity in severities:
        fitting = [
            o for o in others if not _set(o, "severities") or severity in _set(o, "severities")
        ]
        if not tags:
            if not any(not _set(o, "tags") for o in fitting):
                return False
            continue
        for tag in tags:
            if not any(not _set(o, "tags") or tag in _set(o, "tags") for o in fitting):
                return False
    return True


def ordered(policies: list[StoredPolicy], order: Any) -> list[StoredPolicy]:
    """The 1.x list order: the stored order, then policies missing from it in subentry order."""
    if not isinstance(order, list):
        return list(policies)
    by_id = {p.subentry_id: p for p in policies}
    listed = [by_id[i] for i in order if i in by_id]
    known = set(order)
    return listed + [p for p in policies if p.subentry_id not in known]


def _unique_name(wanted: str, taken: set[str]) -> str:
    name, n = wanted, 2
    while name.casefold() in taken:
        name, n = f"{wanted} {n}", n + 1
    return name


def convert_v3(policies: list[StoredPolicy], options: Mapping[str, Any]) -> Converted:
    out = Converted()
    mode = options.get(OPT_POLICY_MODE_OLD)
    mode = mode if mode in ("first", "all") else "first"
    listed = ordered(policies, options.get(OPT_POLICY_ORDER_OLD))
    new: dict[str, dict[str, Any]] = {p.subentry_id: dict(p.data) for p in listed}

    # 1. Links and 2. never acts (mode first only).
    if mode == "first":
        automatic = [p for p in listed if _automatic(p.data)]
        for i, policy in enumerate(automatic):
            above = [q for q in automatic[:i] if can_overlap(policy.data, q.data)]
            if not above:
                continue
            new[policy.subentry_id]["links"] = [q.subentry_id for q in above]
            live = [q.data for q in above if _enabled(q.data)]
            if _enabled(policy.data) and live and covered(policy.data, live):
                out.items.append(_item(policy, ITEM_NEVER_ACTS))
            else:
                out.items.append(_item(policy, ITEM_LINKS))

    # 4. Critical: one band entry instead of the per-hold settings.
    wants_entry = False
    for policy in listed:
        data, kind = policy.data, policy.data.get("type")
        target = new[policy.subentry_id]
        if kind == "quiet_hours":
            passes = bool(data.get("critical_passes", True))
            wants_entry = wants_entry or passes
            if not passes and _fits_critical(data):
                target["holds_anyway"] = True
                out.items.append(_item(policy, ITEM_HOLDS_ANYWAY))
        elif kind == "summarize":
            holds = bool(data.get("include_critical", False))
            wants_entry = wants_entry or not holds
            if holds and _fits_critical(data):
                target["holds_anyway"] = True
                out.items.append(_item(policy, ITEM_HOLDS_ANYWAY))
        elif kind == "presence" and bool(data.get("critical_passes", True)):
            excluded = list(data.get("not_severities") or [])
            if "critical" not in excluded:
                target["not_severities"] = [*excluded, "critical"]
        for name in REMOVED_FIELDS:
            target.pop(name, None)

    if wants_entry:
        taken = {p.title.casefold() for p in policies}
        out.added.append(
            (
                _unique_name(CRITICAL_ENTRY_NAME, taken),
                {
                    "type": "get_through",
                    "severities": ["critical"],
                    "tags": [],
                    "enabled": True,
                    "covers": "everyone",
                },
            )
        )

    out.updates = {i: d for i, d in new.items() if d != dict(_by_id(policies, i).data)}
    options_out = {
        k: v for k, v in options.items() if k not in (OPT_POLICY_MODE_OLD, OPT_POLICY_ORDER_OLD)
    }
    if out.items:
        options_out[OPT_CONVERSION_ITEMS] = out.items
    out.options = options_out
    return out


def _fits_critical(data: Mapping[str, Any]) -> bool:
    severities = _set(data, "severities")
    return not severities or "critical" in severities


def _by_id(policies: list[StoredPolicy], subentry_id: str) -> StoredPolicy:
    return next(p for p in policies if p.subentry_id == subentry_id)


def _item(policy: StoredPolicy, kind: str) -> dict[str, str]:
    return {"policy": policy.subentry_id, "kind": kind, "state": "open"}
