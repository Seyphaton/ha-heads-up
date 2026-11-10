"""Identities of the things a user names (D-199).

A policy, a custom audience and a recipient group are known inside by their subentry ID, a
built-in audience by its kind, an area by its area ID. The name is for display. A reference read
from storage may still be a name (stored by earlier versions); `IdentityMaps` turns it into the
key. `name:<text>` marks a name that matched nothing: it is kept, reported as dangling, and
resolves again if an object with that title appears.

Every function here is pure and idempotent: a value already in the new form is returned as it is,
so the migration can run twice, or on data that is half migrated, without changing anything.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar

from ..const import (
    AUDIENCE_SUBENTRY,
    BUILTIN_AUDIENCES,
    GROUP_SUBENTRY,
    GROUP_SUFFIX,
    POLICY_AUTOMATIC,
    POLICY_NONE,
    POLICY_SUBENTRY,
    POLICY_TYPES,
    SUMMARY_PREFIX,
)

NAME_PREFIX = "name:"  # a name that matched nothing when it was migrated
GROUP_PREFIX = "group:"
AREA_PREFIX = "area:"
KEYWORDS = (POLICY_NONE, POLICY_AUTOMATIC)


def is_dangling(ref: str) -> bool:
    return ref.startswith(NAME_PREFIX)


def dangling_name(ref: str) -> str:
    return ref[len(NAME_PREFIX) :] if ref.startswith(NAME_PREFIX) else ref


@dataclass(slots=True)
class IdentityMaps:
    """The current objects, read from the subentries, as lookups from a name to a key."""

    policies: dict[str, str] = field(default_factory=dict)  # casefolded name to subentry ID
    audiences: dict[str, str] = field(default_factory=dict)  # casefolded name to key
    groups: dict[str, str] = field(default_factory=dict)  # casefolded name to subentry ID
    areas: dict[str, str] = field(default_factory=dict)  # casefolded name to area ID
    area_ids: frozenset[str] = frozenset()
    audience_keys: frozenset[str] = frozenset()
    policy_ids: frozenset[str] = frozenset()
    group_ids: frozenset[str] = frozenset()

    @classmethod
    def from_subentries(
        cls,
        subentries: Iterable[ConfigSubentry],
        areas: Mapping[str, str] | None = None,
    ) -> IdentityMaps:
        """`areas` is area ID to area name."""
        policies: dict[str, str] = {}
        audiences = {name.casefold(): kind for name, kind in BUILTIN_AUDIENCES.items()}
        groups: dict[str, str] = {}
        for sub in subentries:
            key = sub.title.casefold()
            if sub.subentry_type == POLICY_SUBENTRY:
                policies[key] = sub.subentry_id
            elif sub.subentry_type == AUDIENCE_SUBENTRY:
                audiences[key] = sub.subentry_id
            elif sub.subentry_type == GROUP_SUBENTRY:
                groups[key] = sub.subentry_id
        area_names = {name.casefold(): area_id for area_id, name in (areas or {}).items()}
        return cls(
            policies=policies,
            audiences=audiences,
            groups=groups,
            areas=area_names,
            area_ids=frozenset(areas or ()),
            audience_keys=frozenset(audiences.values()),
            policy_ids=frozenset(policies.values()),
            group_ids=frozenset(groups.values()),
        )

    # References ---------------------------------------------------------------------------

    def policy(self, value: str) -> str:
        """The policy key for an ID, a legacy name or a legacy `type:name` key. Keywords stay."""
        if value in KEYWORDS or value in self.policy_ids:
            return value
        name = dangling_name(value)
        found = self.policies.get(name.casefold())
        if found is None:
            kind, _, rest = name.partition(":")
            if kind in POLICY_TYPES and rest:  # the key of a timer row of an earlier version
                name = rest
                found = self.policies.get(rest.casefold())
        return found if found is not None else f"{NAME_PREFIX}{name}"

    def policy_list(self, value: str | list[str] | None) -> str | list[str] | None:
        """The `policy` of a message or a rule: one value, a list, or nothing."""
        if value is None or value == "":
            return value
        if isinstance(value, str):
            return self.policy(value)
        return [self.policy(v) for v in value]

    def audience(self, value: str) -> str:
        if value in self.audience_keys:
            return value
        name = dangling_name(value)
        found = self.audiences.get(name.casefold())
        return found if found is not None else f"{NAME_PREFIX}{name}"

    def group(self, value: str) -> str | None:
        """The `group:<id>` token for a group named by ID token or `Name (group)`, else None."""
        if value.startswith(GROUP_PREFIX):
            return value
        if value.casefold().endswith(GROUP_SUFFIX.casefold()):
            name = value[: -len(GROUP_SUFFIX)]
            found = self.groups.get(name.strip().casefold())
            return f"{GROUP_PREFIX}{found}" if found else None
        return None

    def recipient(self, value: str) -> str:
        """A recipient of a target: entities, devices and persons stay; a group and an area
        become tokens when they exist. Anything unknown stays as it was written."""
        if value.startswith((GROUP_PREFIX, AREA_PREFIX)):
            return value
        if (token := self.group(value)) is not None:
            return token
        if "." in value or ":" in value:
            return value
        if value in self.area_ids:
            return f"{AREA_PREFIX}{value}"
        found = self.areas.get(value.casefold())
        return f"{AREA_PREFIX}{found}" if found else value

    def target(self, target: Mapping[str, Any]) -> dict[str, Any]:
        out = dict(target)
        if isinstance(out.get("audience"), str):
            out["audience"] = self.audience(out["audience"])
        if isinstance(out.get("recipients"), list):
            out["recipients"] = [
                self.recipient(r) if isinstance(r, str) else r for r in out["recipients"]
            ]
        return out

    def targets(self, targets: Mapping[str, Any] | None) -> dict[str, Any]:
        return {k: self.target(v) for k, v in (targets or {}).items() if isinstance(v, Mapping)}

    # Stored data --------------------------------------------------------------------------

    def banner(self, data: dict[str, Any]) -> dict[str, Any]:
        """A stored banner with its references as keys."""
        out = dict(data)
        if "policy" in out:
            out["policy"] = self.policy_list(out["policy"])
        if isinstance(out.get("targets"), dict):
            out["targets"] = self.targets(out["targets"])
        return out

    def held(self, data: dict[str, Any]) -> dict[str, Any]:
        out = dict(data)
        if isinstance(out.get("policy"), str):
            out["policy"] = self.policy(out["policy"])
        if isinstance(out.get("targets"), dict):
            out["targets"] = self.targets(out["targets"])
        return out

    def timer_row(self, data: dict[str, Any]) -> dict[str, Any]:
        """A ledger row of channel `timer`: the policy key in `recipient`, and in the message id
        of a summary."""
        out = dict(data)
        recipient = str(out.get("recipient", ""))
        if recipient.startswith("held:"):  # a held delivery: `held:<channel>:<recipient>`
            return out
        out["recipient"] = self.policy(recipient)
        message_id = str(out.get("message_id", ""))
        if message_id.startswith(SUMMARY_PREFIX):
            out["message_id"] = SUMMARY_PREFIX + self.policy(message_id[len(SUMMARY_PREFIX) :])
        return out

    def policy_data(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """A policy subentry's data with the targets as keys."""
        out = dict(data)
        if isinstance(out.get("targets"), dict):
            out["targets"] = self.targets(out["targets"])
        return out

    def rule_data(self, data: Mapping[str, Any]) -> dict[str, Any]:
        out = dict(data)
        if out.get("policy"):
            out["policy"] = self.policy(str(out["policy"]).strip())
        return out

    def disabled_audiences(self, names: Iterable[str]) -> list[str]:
        return list(dict.fromkeys(self.audience(n) for n in names))


def maps_for(hass: HomeAssistant, subentries: Iterable[ConfigSubentry]) -> IdentityMaps:
    """The maps of the objects that exist now, areas included."""
    areas = {a.id: a.name for a in ar.async_get(hass).async_list_areas()}
    return IdentityMaps.from_subentries(subentries, areas)


def count_changes(before: Any, after: Any) -> int:
    """How many leaf values differ, for the line the migration logs."""
    if isinstance(before, dict) and isinstance(after, dict):
        return sum(count_changes(before.get(k), after.get(k)) for k in {*before, *after})
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return sum(count_changes(a, b) for a, b in zip(before, after, strict=True))
    return 0 if before == after else 1
