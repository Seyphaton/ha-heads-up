"""Which policies apply to a message (DESIGN §25.3, D-224).

An automatic policy fits when the message severity is among its severities and its tag among its
tags (an empty list means any), neither is in Not for, a watch-rule message comes from one of its
rules (when it names rules), and no policy it links to fits while that one is enabled (links come
only from the 1.x conversion, §25.6). Every fitting policy acts; there is no order and no mode.
A manual policy never applies by itself. The call's `policy` field names policies (manual or
automatic, used whatever their filters say), is omitted to use every automatic policy that fits,
or is `none`. A list names several; `automatic` in the list adds the fitting automatic policies
(D-184). Only if (D-216) is checked by the engine at each step, not here.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...const import POLICY_AUTOMATIC, POLICY_NONE, RULE_ID_PREFIX
from ...models import Banner
from .models import Policy


def matches_for(policy: Policy, severity: str, tag: str | None, message_id: str = "") -> bool:
    """For alone: severities, tags and the watch-rule source."""
    if policy.severities and severity not in policy.severities:
        return False
    if policy.tags and tag not in policy.tags:
        return False
    if policy.rules:
        rule = message_id[len(RULE_ID_PREFIX) :] if message_id.startswith(RULE_ID_PREFIX) else None
        if rule not in policy.rules:
            return False
    return True


def matches(policy: Policy, severity: str, tag: str | None, message_id: str = "") -> bool:
    """For and Not for; links are checked by `fits`."""
    if severity in policy.not_severities or (tag is not None and tag in policy.not_tags):
        return False
    return matches_for(policy, severity, tag, message_id)


def applies(policy: Policy, severity: str, tag: str | None) -> bool:
    """An automatic policy by severity and tag alone (no message ID: watch-rule filters fail)."""
    return policy.apply != "manual" and matches(policy, severity, tag)


def fits(policy: Policy, message: Banner, by_id: Mapping[str, Policy]) -> bool:
    if policy.apply == "manual":
        return False
    if not matches(policy, message.severity, message.tag, message.id):
        return False
    for linked_id in policy.links:
        linked = by_id.get(linked_id)
        # A link to a deleted policy no longer holds anything back. A link looks at the linked
        # policy's For only, as the 1.x order did: the conversion adds Not for critical to
        # Presence, and that must not free the policies below it (DESIGN §25.6).
        if (
            linked is not None
            and linked.enabled
            and matches_for(linked, message.severity, message.tag, message.id)
        ):
            return False
    return True


def select(
    policies: list[Policy], message: Banner, by_id: Mapping[str, Policy] | None = None
) -> list[Policy]:
    enabled = [p for p in policies if p.enabled]
    names = policy_names(message.policy)
    if names == [POLICY_NONE]:
        return []
    named = [p for p in enabled if any(p.is_named(n) for n in names)]
    if names and POLICY_AUTOMATIC not in names:
        return named
    known = by_id if by_id is not None else {p.subentry_id: p for p in policies}
    found = [p for p in enabled if fits(p, message, known)]
    # `automatic` next to names: the policies that fit, plus the named ones (D-184).
    return found + [p for p in named if p not in found]


def policy_names(value: str | list[str] | None) -> list[str]:
    """The policy field as a list: one name (stored by earlier versions) or several."""
    if not value:
        return []
    return [value] if isinstance(value, str) else list(value)


def duplicate_of(policies: list[Policy], candidate: Policy) -> Policy | None:
    """Another policy of the same type, applies-to and trigger (the form refuses it)."""
    for other in policies:
        # A manual policy never attaches by itself, so it cannot do the same thing twice.
        if candidate.apply == "manual" or other.apply == "manual":
            continue
        if (
            other.subentry_id != candidate.subentry_id
            and other.type == candidate.type
            and other.severities == candidate.severities
            and other.tags == candidate.tags
            and other.not_severities == candidate.not_severities
            and other.not_tags == candidate.not_tags
            and other.rules == candidate.rules
            and other.trigger == candidate.trigger
        ):
            return other
    return None
