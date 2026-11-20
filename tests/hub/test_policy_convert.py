"""Conversion of 1.x policies to the 2.0 lanes (DESIGN §25.6, `convert_v3`)."""

from __future__ import annotations

from custom_components.heads_up.hub.policies.convert import (
    StoredPolicy,
    can_overlap,
    convert_v3,
    covered,
)

CRIT_DELIVERY = StoredPolicy(
    "crit", "Critical delivery", {"type": "deliver", "severities": ["critical"]}
)
WARN_REMINDER = StoredPolicy(
    "warn", "Warning reminder", {"type": "reminder", "severities": ["warning"], "every_minutes": 30}
)
EVENING = StoredPolicy(
    "eve",
    "Evening summary",
    {"type": "summarize", "severities": ["passive", "info"], "tags": ["digest"]},
)
NIGHT = StoredPolicy(
    "night",
    "Night quiet",
    {"type": "quiet_hours", "severities": ["passive", "info"], "action": "quiet"},
)
AWAY = StoredPolicy("away", "Away", {"type": "presence"})
WELCOME = [CRIT_DELIVERY, WARN_REMINDER, EVENING, NIGHT]


def kinds(result, policy_id):
    return sorted(i["kind"] for i in result.items if i["policy"] == policy_id)


def test_overlap_and_cover_treat_empty_as_any() -> None:
    assert can_overlap({"severities": ["info"]}, {"tags": ["digest"]})
    assert not can_overlap({"severities": ["info"]}, {"severities": ["warning"]})
    assert not can_overlap({"tags": ["a"]}, {"tags": ["b"]})
    assert covered({"severities": ["info"], "tags": ["digest"]}, [{"severities": ["info"]}])
    # A policy without tags also fits messages with other tags: only a tagless one covers it.
    assert not covered({"severities": ["info"]}, [{"severities": ["info"], "tags": ["digest"]}])
    assert covered({}, [{}])


def test_welcome_list_with_a_later_away_at_the_end() -> None:
    result = convert_v3(
        [*WELCOME, AWAY], {"policy_mode": "first", "policy_order": ["crit", "warn", "eve", "night"]}
    )
    assert result.updates["night"]["links"] == ["eve"]
    assert kinds(result, "night") == ["links"]
    # Away comes last in 1.x (missing from the order) and every message is taken first.
    assert result.updates["away"]["links"] == ["crit", "warn", "eve", "night"]
    assert kinds(result, "away") == ["never_acts"]
    assert "links" not in result.updates.get("crit", {})
    assert "policy_mode" not in result.options and "policy_order" not in result.options


def test_away_stored_first_takes_the_links_instead() -> None:
    result = convert_v3(
        [AWAY, *WELCOME],
        {"policy_mode": "first", "policy_order": ["away", "crit", "warn", "eve", "night"]},
    )
    assert "links" not in result.updates.get("away", {})
    assert result.updates["crit"]["links"] == ["away"]
    assert result.updates["warn"]["links"] == ["away"]
    assert kinds(result, "crit") == ["never_acts"]


def test_missing_mode_counts_as_first() -> None:
    result = convert_v3(WELCOME, {})
    assert result.updates["night"]["links"] == ["eve"]


def test_mode_all_gets_no_links() -> None:
    reminders = [
        StoredPolicy(
            "r1", "Fast", {"type": "reminder", "severities": ["warning"], "every_minutes": 30}
        ),
        StoredPolicy(
            "r2", "Slow", {"type": "reminder", "severities": ["warning"], "every_minutes": 60}
        ),
    ]
    result = convert_v3(reminders, {"policy_mode": "all", "policy_order": ["r1", "r2"]})
    assert not any("links" in d or "alongside" in d for d in result.updates.values())
    assert result.items == []


def test_manual_policies_get_no_links_and_give_none() -> None:
    manual = StoredPolicy("man", "Manual", {"type": "escalation", "apply": "manual"})
    after = StoredPolicy("esc", "Escalate", {"type": "escalation"})
    result = convert_v3([manual, after], {"policy_mode": "first"})
    assert "links" not in result.updates.get("man", {})
    assert "links" not in result.updates.get("esc", {})


def test_a_disabled_policy_above_links_but_does_not_make_it_never_act() -> None:
    off = StoredPolicy("off", "Off", {"type": "deliver", "enabled": False})
    below = StoredPolicy("below", "Below", {"type": "reminder"})
    result = convert_v3([off, below], {"policy_mode": "first"})
    assert result.updates["below"]["links"] == ["off"]
    assert kinds(result, "below") == ["links"]


def test_critical_passes_becomes_one_band_entry() -> None:
    result = convert_v3([NIGHT], {"policy_mode": "first"})
    assert result.added == [
        (
            "Critical",
            {
                "type": "get_through",
                "severities": ["critical"],
                "tags": [],
                "enabled": True,
                "covers": "everyone",
            },
        )
    ]
    assert "critical_passes" not in result.updates.get("night", NIGHT.data)


def test_quiet_hours_that_held_critical_hold_anyway() -> None:
    strict = StoredPolicy(
        "q", "Strict", {"type": "quiet_hours", "critical_passes": False, "action": "wait"}
    )
    result = convert_v3([strict], {})
    assert result.updates["q"]["holds_anyway"] is True
    assert "critical_passes" not in result.updates["q"]
    assert result.added == []  # nothing passed critical in 1.x
    assert kinds(result, "q") == ["holds_anyway"]


def test_summarize_with_include_critical_holds_anyway_and_without_adds_the_entry() -> None:
    holds = StoredPolicy("s1", "All", {"type": "summarize", "include_critical": True})
    result = convert_v3([holds], {})
    assert result.updates["s1"]["holds_anyway"] is True
    assert result.added == []
    result = convert_v3(
        [StoredPolicy("s2", "Digest", {"type": "summarize", "tags": ["digest"]})], {}
    )
    assert [name for name, _ in result.added] == ["Critical"]


def test_presence_that_let_critical_pass_is_not_for_critical() -> None:
    result = convert_v3([AWAY], {})
    assert result.updates["away"]["not_severities"] == ["critical"]
    strict = StoredPolicy("p", "Strict", {"type": "presence", "critical_passes": False})
    assert "not_severities" not in convert_v3([strict], {}).updates["p"]


def test_the_entry_name_does_not_clash() -> None:
    clash = StoredPolicy("c", "Critical", {"type": "deliver", "severities": ["critical"]})
    result = convert_v3([clash, NIGHT], {})
    assert result.added[0][0] == "Critical 2"


def test_conversion_items_are_stored_in_the_options() -> None:
    result = convert_v3([*WELCOME, AWAY], {"policy_mode": "first", "install_token": "x"})
    assert result.options["install_token"] == "x"
    assert result.options["conversion_items"] == result.items
    assert all(i["state"] == "open" for i in result.items)
