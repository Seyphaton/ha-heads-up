"""Which policies apply to a message (DESIGN §23.14).

A policy applies when the message severity is among its severities and the message tag among
its tags; an empty list means any. A rule message has the tag `rule`. The call's `policy` field
names one policy (used whatever its filters say), is omitted to use every policy that applies,
or is `none`.
"""

from __future__ import annotations

from ...const import POLICY_NONE
from ...models import Banner
from .models import Policy


def applies(policy: Policy, severity: str, tag: str | None) -> bool:
    if policy.severities and severity not in policy.severities:
        return False
    return not policy.tags or tag in policy.tags


def select(policies: list[Policy], message: Banner) -> list[Policy]:
    enabled = [p for p in policies if p.enabled]
    if message.policy == POLICY_NONE:
        return []
    if message.policy:
        return [p for p in enabled if p.name == message.policy]
    return [p for p in enabled if applies(p, message.severity, message.tag)]


def duplicate_of(policies: list[Policy], candidate: Policy) -> Policy | None:
    """Another policy of the same type, applies-to and trigger (the form refuses it)."""
    for other in policies:
        if (
            other.subentry_id != candidate.subentry_id
            and other.type == candidate.type
            and other.severities == candidate.severities
            and other.tags == candidate.tags
            and other.trigger == candidate.trigger
        ):
            return other
    return None
