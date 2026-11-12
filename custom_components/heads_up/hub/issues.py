"""Repairs notices for policies whose audience or speaker group was deleted (D-204).

Home Assistant gives an integration no way to refuse the delete of a subentry, so the delete goes
through and this notice names the policy that no longer works and how to fix it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from ..const import DOMAIN

if TYPE_CHECKING:
    from .engine import HubEngine

ISSUE_PREFIX = "policy_target_"
WHAT = {"audience_missing": "an audience", "group_missing": "a speaker group"}


def sync_policy_issues(hass: HomeAssistant, hub: HubEngine) -> None:
    """One notice per policy that names a missing audience or group; resolved ones are removed."""
    wanted: dict[str, tuple[str, str]] = {}
    for policy in hub.policies.all():
        if policy.subentry_id and (problem := hub.policy_problem(policy)) in WHAT:
            wanted[f"{ISSUE_PREFIX}{policy.subentry_id}"] = (policy.name, WHAT[str(problem)])
    registry = ir.async_get(hass)
    for domain, issue_id in list(registry.issues):
        if domain == DOMAIN and issue_id.startswith(ISSUE_PREFIX) and issue_id not in wanted:
            ir.async_delete_issue(hass, DOMAIN, issue_id)
    for issue_id, (name, what) in wanted.items():
        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="policy_target_missing",
            translation_placeholders={"policy": name, "what": what},
        )


def clear_policy_issues(hass: HomeAssistant) -> None:
    """The integration is unloaded or removed: its notices go with it."""
    for domain, issue_id in list(ir.async_get(hass).issues):
        if domain == DOMAIN and issue_id.startswith(ISSUE_PREFIX):
            ir.async_delete_issue(hass, DOMAIN, issue_id)
