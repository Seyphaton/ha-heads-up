"""The catalog of policies: read from subentries, queried by the engine and the flows."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.config_entries import ConfigSubentry

from ...const import POLICY_TYPES
from ...models import Banner
from ..channels.base import Target
from ..identity import NAME_PREFIX
from .matching import select
from .models import Policy, parse_policy

ACKNOWLEDGING = ("escalation", "reminder")  # types that make an Acknowledge button useful
# The page order: the lane "Keep it calm", the band, the lane "Make sure it arrives" (DESIGN
# §25.2). Only for display; which policies act does not depend on it.
TYPE_RANK = {
    "summarize": 0,
    "quiet_hours": 1,
    "presence": 2,
    "get_through": 3,
    "deliver": 4,
    "escalation": 5,
    "reminder": 6,
    "fallback": 7,
}


class PolicyBook:
    """Implements the `PolicyCatalog` interface of H1."""

    def __init__(self, options: Mapping[str, Any] | None = None) -> None:
        self._policies: dict[str, Policy] = {}  # by subentry id
        self._options: Mapping[str, Any] = options if options is not None else {}
        # Set by the engine: the persons of an audience key, for band entries that cover
        # only some people.
        self.household: Callable[[str], list[str]] = lambda audience: []
        # Set by the integration: the policy a switch of its own stands for (D-186).
        # Every policy name with the entity ID of its switch; a call names a policy by it (D-198).
        self.policy_entities: Callable[[], dict[str, str]] = lambda: {}

    def ordered(self) -> list[Policy]:
        """The policies in page order: by lane and type, then by name."""
        return sorted(
            self._policies.values(), key=lambda p: (TYPE_RANK.get(p.type, 9), p.name.casefold())
        )

    def sync(self, subentries: Mapping[str, ConfigSubentry]) -> None:
        parsed = (parse_policy(s) for s in subentries.values())
        self._policies = {p.subentry_id: p for p in parsed if p is not None}

    def names(self) -> list[str]:
        return sorted({p.name for p in self._policies.values()})

    def all(self) -> list[Policy]:
        return self.ordered()

    def by_key(self, key: str) -> Policy | None:
        """The policy a stored key means: its subentry ID, or a name or `type:name` key written
        before D-199 (the migration rewrites those; this keeps a missed one working)."""
        if (found := self._policies.get(key)) is not None:
            return found
        by_name = {p.name.casefold(): p for p in self._policies.values()}
        name = key[len(NAME_PREFIX) :] if key.startswith(NAME_PREFIX) else key
        if (found := by_name.get(name.casefold())) is not None:
            return found
        kind, _, rest = name.partition(":")
        if kind in POLICY_TYPES and rest:
            return by_name.get(rest.casefold())
        return None

    def get(self, ref: str) -> Policy | None:
        return self.by_key(ref)

    def by_name(self, name: str) -> Policy | None:
        return next(
            (p for p in self._policies.values() if p.name.casefold() == name.casefold()), None
        )

    def for_message(self, message: Banner) -> list[Policy]:
        return select(self.ordered(), message, self._policies)

    def band_for(self, message: Banner) -> list[Policy]:
        return [p for p in self.for_message(message) if p.type == "get_through"]

    def covers(self, entry: Policy, target: Target) -> bool:
        if entry.covers != "only":
            return True
        if target.key in entry.covers_recipients or (
            target.person is not None and target.person in entry.covers_recipients
        ):
            return True
        return target.person is not None and any(
            target.person in self.household(a) for a in entry.covers_audiences
        )

    def passes(self, message: Banner, target: Target | None = None) -> bool:
        """Whether a band entry lets this message past a hold (DESIGN §25.3 rule 3): Summarize
        asks without a target (the whole message), Quiet hours per recipient. The caller checks
        `holds_anyway` on its own policy."""
        entries = self.band_for(message)
        if target is None:
            return bool(entries)
        return any(self.covers(e, target) for e in entries)

    def timed_for(self, message: Banner) -> list[Policy]:
        return [p for p in self.for_message(message) if p.type in ACKNOWLEDGING]

    def usage(self, *refs: str) -> list[str]:
        """Policies whose targets name this audience or recipient group, given every way it is
        written: its key and, for data of earlier versions, its name (D-111: so a panel can
        warn before it is deleted; Home Assistant cannot block a subentry deletion)."""
        wanted = {r.casefold() for r in refs}
        users = []
        for policy in self._policies.values():
            for target in policy.targets.values():
                named = [target.get("audience"), *target.get("recipients", [])]
                if any(isinstance(n, str) and n.casefold() in wanted for n in named):
                    users.append(policy.name)
                    break
        return sorted(users)
