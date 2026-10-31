"""Which policies apply to a message, and which duplicates the form refuses (D-079, D-097)."""

from datetime import UTC, datetime

from custom_components.heads_up.hub.policies.matching import applies, duplicate_of, select
from custom_components.heads_up.hub.policies.models import Policy
from custom_components.heads_up.models import Banner

NOW = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)


def message(severity: str = "warning", tag: str | None = None, policy: str | None = None) -> Banner:
    return Banner(
        id="m",
        message="x",
        severity=severity,
        dismissible=True,
        dismiss_scope="user",
        created_at=NOW,
        updated_at=NOW,
        tag=tag,
        policy=policy,
    )


def policy(name: str = "P", type: str = "escalation", **kw: object) -> Policy:
    return Policy(name=name, type=type, subentry_id=name, after_minutes=5, **kw)  # type: ignore[arg-type]


def test_empty_severities_and_tags_mean_any() -> None:
    assert applies(policy(), "info", None)
    assert applies(policy(), "critical", "water")


def test_a_severity_list_limits_the_policy() -> None:
    p = policy(severities=frozenset({"critical"}))
    assert applies(p, "critical", None)
    assert not applies(p, "warning", None)


def test_a_tag_list_limits_the_policy_and_an_untagged_message_does_not_match() -> None:
    p = policy(tags=frozenset({"water"}))
    assert applies(p, "warning", "water")
    assert not applies(p, "warning", "door")
    assert not applies(p, "warning", None)


def test_a_rule_message_matches_the_tag_rule() -> None:
    assert applies(policy(tags=frozenset({"rule"})), "warning", "rule")


def test_without_a_policy_field_every_policy_that_applies_is_used() -> None:
    both = [policy("A", severities=frozenset({"warning"})), policy("B"), policy("C", enabled=False)]
    assert [p.name for p in select(both, message())] == ["A", "B"]


def test_the_policy_field_names_one_policy_whatever_its_filters_say() -> None:
    both = [policy("A", severities=frozenset({"critical"})), policy("B")]
    assert [p.name for p in select(both, message("info", policy="A"))] == ["A"]


def test_the_policy_none_selects_nothing() -> None:
    assert select([policy()], message(policy="none")) == []


def test_a_disabled_policy_is_not_used_even_when_named() -> None:
    assert select([policy(enabled=False)], message(policy="P")) == []


def test_same_type_applies_to_and_trigger_is_a_duplicate() -> None:
    other = policy("Other")
    assert duplicate_of([other], policy("New")) is other


def test_a_different_trigger_type_or_applies_to_is_not_a_duplicate() -> None:
    existing = [policy("A")]
    later = policy("B")
    later.after_minutes = 10
    assert duplicate_of(existing, later) is None
    assert duplicate_of(existing, policy("C", severities=frozenset({"info"}))) is None
    assert duplicate_of(existing, policy("D", type="reminder")) is None


def test_a_policy_is_not_a_duplicate_of_itself() -> None:
    only = policy("A")
    assert duplicate_of([only], only) is None
