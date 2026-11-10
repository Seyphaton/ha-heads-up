"""Which policies apply to a message (DESIGN §23.14).

An automatic policy applies when the message severity is among its severities and the message tag
among its tags; an empty list means any. A rule message has the tag `rule`. A manual policy never
applies by itself. The call's `policy` field names one policy (manual or automatic, used whatever
its filters say), is omitted to use every automatic policy that applies, or is `none`. A list
names several policies; `automatic` in the list adds the automatic policies that apply (D-184).
In the mode "first" only the first automatic policy that applies is used (D-148).
"""

from __future__ import annotations

from ...const import POLICY_AUTOMATIC, POLICY_NONE
from ...models import Banner
from .models import Policy


def applies(policy: Policy, severity: str, tag: str | None) -> bool:
    if policy.apply == "manual":
        return False
    if policy.severities and severity not in policy.severities:
        return False
    return not policy.tags or tag in policy.tags


def select(policies: list[Policy], message: Banner, first_only: bool = False) -> list[Policy]:
    enabled = [p for p in policies if p.enabled]
    names = policy_names(message.policy)
    if names == [POLICY_NONE]:
        return []
    named = [p for p in enabled if any(p.is_named(n) for n in names)]
    if names and POLICY_AUTOMATIC not in names:
        return named
    found = [p for p in enabled if applies(p, message.severity, message.tag)]
    found = found[:1] if first_only else found
    # `automatic` next to names: the policies that apply, plus the named ones (D-184).
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
            and other.trigger == candidate.trigger
        ):
            return other
    return None
