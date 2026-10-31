"""The catalog of policies: read from subentries, queried by the engine and the flows."""

from __future__ import annotations

from collections.abc import Mapping

from homeassistant.config_entries import ConfigSubentry

from ...const import GROUP_SUFFIX
from ...models import Banner
from .matching import select
from .models import Policy, parse_policy

ACKNOWLEDGING = ("escalation", "reminder")  # types that make an Acknowledge button useful


class PolicyBook:
    """Implements the `PolicyCatalog` interface of H1."""

    def __init__(self) -> None:
        self._policies: dict[str, Policy] = {}  # by subentry id

    def sync(self, subentries: Mapping[str, ConfigSubentry]) -> None:
        parsed = (parse_policy(s) for s in subentries.values())
        self._policies = {p.subentry_id: p for p in parsed if p is not None}

    def names(self) -> list[str]:
        return sorted({p.name for p in self._policies.values()})

    def all(self) -> list[Policy]:
        return list(self._policies.values())

    def by_key(self, key: str) -> Policy | None:
        return next((p for p in self._policies.values() if p.key == key), None)

    def for_message(self, message: Banner) -> list[Policy]:
        return select(self.all(), message)

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
