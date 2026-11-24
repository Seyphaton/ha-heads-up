"""3.1 to 3.2: Not for severities and From watch rule leave the policies (D-280)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.migration import fold_back, fold_filters


def test_not_for_severities_leave_for_and_an_empty_for_means_the_others() -> None:
    out = fold_filters(
        {
            "a": {"type": "quiet_hours", "not_severities": ["critical"]},
            "b": {"type": "deliver", "severities": ["info", "warning"], "not_severities": ["info"]},
            "c": {"type": "deliver", "severities": ["info"]},
        }
    )
    assert out["a"] == {"type": "quiet_hours", "severities": ["passive", "info", "warning"]}
    assert out["b"]["severities"] == ["warning"] and "not_severities" not in out["b"]
    assert out["c"] == {"type": "deliver", "severities": ["info"]}


def test_a_policy_with_nothing_left_is_switched_off_and_keeps_no_severity_list() -> None:
    out = fold_filters(
        {"a": {"type": "deliver", "severities": ["info"], "not_severities": ["info"]}}
    )
    assert out["a"] == {"type": "deliver", "enabled": False}


def test_all_four_severities_are_stored_as_any() -> None:
    out = fold_filters({"a": {"type": "deliver", "severities": ["info"], "not_severities": []}})
    assert out["a"]["severities"] == ["info"]
    assert fold_back(["passive", "info", "warning"], ["critical"]) == []


def test_a_linked_policy_loses_the_severities_the_link_used_to_block() -> None:
    # The link looked at For alone, so Not for critical on the Presence policy still blocked
    # critical messages below it. Now the policy below leaves critical out itself.
    out = fold_filters(
        {
            "presence": {"type": "presence", "not_severities": ["critical"]},
            "below": {"type": "quiet_hours", "links": ["presence"]},
        }
    )
    assert out["presence"]["severities"] == ["passive", "info", "warning"]
    assert out["below"]["severities"] == ["passive", "info", "warning"]


def test_from_watch_rule_becomes_the_tag_rule_unless_a_tag_is_set() -> None:
    out = fold_filters(
        {
            "a": {"type": "deliver", "rules": ["r1"]},
            "b": {"type": "deliver", "rules": ["r1"], "tags": ["rule", "door"]},
            "c": {"type": "deliver", "rules": []},
        }
    )
    assert out["a"] == {"type": "deliver", "tags": ["rule"]}
    assert out["b"]["tags"] == ["rule", "door"] and "rules" not in out["b"]
    assert out["c"] == {"type": "deliver"}


async def test_the_entry_migrates_once_and_keeps_a_backup(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        minor_version=1,
        subentries_data=[
            {
                "subentry_type": "policy",
                "title": "Night",
                "unique_id": None,
                "data": {"type": "quiet_hours", "not_severities": ["critical"], "rules": ["x"]},
            }
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    (sub,) = [s for s in entry.subentries.values() if s.subentry_type == "policy"]
    assert (entry.version, entry.minor_version) == (3, 2)
    assert dict(sub.data)["severities"] == ["passive", "info", "warning"]
    assert dict(sub.data)["tags"] == ["rule"] and "rules" not in sub.data
    backup = hass_storage["heads_up.migration_v3_2"]["data"]["entry"]["subentries"]
    assert backup[0]["data"]["not_severities"] == ["critical"]
