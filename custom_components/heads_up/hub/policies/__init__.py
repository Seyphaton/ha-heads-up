"""The catalog of policies: read from subentries, queried by the engine and the flows."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.config_entries import ConfigSubentry

from ...const import GROUP_SUFFIX, OPT_POLICY_MODE, OPT_POLICY_ORDER, POLICY_MODES
from ...models import Banner
from .matching import select
from .models import Policy, parse_policy

ACKNOWLEDGING = ("escalation", "reminder")  # types that make an Acknowledge button useful
# The starting order of policies that have none yet: what limits a message first, then what adds
# deliveries (D-149). Within a type, by name.
TYPE_RANK = {
    "summarize": 0,
    "quiet_hours": 1,
    "away": 2,
    "escalation": 3,
    "reminder": 4,
    "fallback": 5,
    "deliver": 6,
}


class PolicyBook:
    """Implements the `PolicyCatalog` interface of H1."""

    def __init__(self, options: Mapping[str, Any] | None = None) -> None:
        self._policies: dict[str, Policy] = {}  # by subentry id
        # The live options of the entry: the mode and the order are read when they are used.
        self._options: Mapping[str, Any] = options if options is not None else {}
        # Set by the integration: the policy a switch of its own stands for (D-186).
        # Every policy name with the entity ID of its switch; a call names a policy by it (D-198).
        self.policy_entities: Callable[[], dict[str, str]] = lambda: {}

    @property
    def mode(self) -> str:
        mode = self._options.get(OPT_POLICY_MODE)
        return str(mode) if mode in POLICY_MODES else "first"

    def initial_order(self) -> list[str]:
        """Subentry ids in the starting order, for an installation that has none stored."""
        ranked = sorted(
            self._policies.values(), key=lambda p: (TYPE_RANK.get(p.type, 9), p.name.casefold())
        )
        return [p.subentry_id for p in ranked]

    def ordered(self) -> list[Policy]:
        """The policies in the order of the list: the stored order, then new ones in the order
        they were created. Without a stored order, the starting order."""
        stored = self._options.get(OPT_POLICY_ORDER)
        if not isinstance(stored, list):
            return [self._policies[i] for i in self.initial_order()]
        listed = [self._policies[i] for i in stored if i in self._policies]
        known = set(stored)
        return listed + [p for i, p in self._policies.items() if i not in known]

    def sync(self, subentries: Mapping[str, ConfigSubentry]) -> None:
        parsed = (parse_policy(s) for s in subentries.values())
        self._policies = {p.subentry_id: p for p in parsed if p is not None}

    def names(self) -> list[str]:
        return sorted({p.name for p in self._policies.values()})

    def all(self) -> list[Policy]:
        return self.ordered()

    def by_key(self, key: str) -> Policy | None:
        return next((p for p in self._policies.values() if p.key == key), None)

    def for_message(self, message: Banner) -> list[Policy]:
        return select(self.ordered(), message, first_only=self.mode == "first")

    def timed_for(self, message: Banner) -> list[Policy]:
        return [p for p in self.for_message(message) if p.type in ACKNOWLEDGING]

    def usage(self, name: str) -> list[str]:
        """Policies that name this audience or recipient group (D-111: so a panel can warn
        before it is deleted; Home Assistant itself cannot block a subentry deletion)."""
        group = f"{name}{GROUP_SUFFIX}"
        users = []
        for policy in self._policies.values():
            for target in policy.targets.values():
                if target.get("audience") == name or group in target.get("recipients", []):
                    users.append(policy.name)
                    break
        return sorted(users)
