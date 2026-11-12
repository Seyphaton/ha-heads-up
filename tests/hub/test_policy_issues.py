"""A deleted audience or group that a policy names raises a Repairs notice (D-204)."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .policy_support import add_policy

DELIVER = {
    "type": "deliver",
    "severities": ["critical"],
    "channels": ["push"],
}


def policy_issues(hass: HomeAssistant) -> list[str]:
    return [i for d, i in ir.async_get(hass).issues if d == "heads_up" and i.startswith("policy_")]


async def test_a_policy_naming_a_missing_audience_raises_one_notice(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await add_policy(
        hass, entry, "Gone", **{**DELIVER, "targets": {"push": {"audience": "Deleted"}}}
    )
    (issue_id,) = policy_issues(hass)
    issue = ir.async_get(hass).async_get_issue("heads_up", issue_id)
    assert issue is not None and issue.translation_key == "policy_target_missing"
    assert issue.translation_placeholders == {"policy": "Gone", "what": "an audience"}


async def test_the_notice_goes_when_the_policy_is_deleted(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await add_policy(
        hass, entry, "Gone", **{**DELIVER, "targets": {"push": {"audience": "Deleted"}}}
    )
    (sub_id,) = [s.subentry_id for s in entry.subentries.values() if s.title == "Gone"]
    hass.config_entries.async_remove_subentry(entry, sub_id)
    await hass.async_block_till_done()
    assert policy_issues(hass) == []


async def test_a_policy_naming_a_built_in_audience_raises_no_notice(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await add_policy(
        hass, entry, "Fine", **{**DELIVER, "targets": {"push": {"audience": "Everyone"}}}
    )
    assert policy_issues(hass) == []
