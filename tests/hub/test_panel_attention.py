"""The checks of "Needs attention": each is a pure function over plain data (D-118)."""

from datetime import UTC, datetime

from custom_components.heads_up.hub.panel_data import (
    check_critical_escalation,
    check_devices,
    check_failures,
    check_groups,
    check_people,
    check_policies,
    check_rule_entities,
)
from custom_components.heads_up.hub.policies.models import Policy


def kinds(items: list) -> list[str]:
    return [i.kind for i in items]


def test_a_rule_on_an_unavailable_unknown_or_missing_entity_is_an_error() -> None:
    rules = [
        {"name": "A", "entity_id": "binary_sensor.a"},
        {"name": "B", "entity_id": "binary_sensor.b"},
        {"name": "C", "entity_id": "binary_sensor.c"},
        {"name": "D", "entity_id": "binary_sensor.d"},
    ]
    states = {
        "binary_sensor.a": "unavailable",
        "binary_sensor.b": "unknown",
        "binary_sensor.d": "on",
    }
    found = check_rule_entities(rules, states)
    assert [(i.subject, i.level, i.page) for i in found] == [
        ("A", "error", "rules"),
        ("B", "error", "rules"),
        ("C", "error", "rules"),
    ]
    assert found[0].detail == "binary_sensor.a"


def test_a_disabled_rule_and_a_template_rule_are_not_checked() -> None:
    rules = [
        {"name": "Off", "entity_id": "x.y", "enabled": False},
        {"name": "T", "template": "{{ 1 }}"},
    ]
    assert check_rule_entities(rules, {}) == []


def device(name: str | None, found: bool) -> dict:
    return {"name": name, "device_id": "id1", "service_found": found}


def test_a_device_without_its_notify_service_is_an_error_naming_the_device() -> None:
    profiles = [
        {"name": "Anna", "devices": [device("Anna's phone", False), device("Tablet", True)]}
    ]
    (item,) = check_devices(profiles)
    assert (item.kind, item.level, item.subject, item.detail) == (
        "device_service",
        "error",
        "Anna",
        "Anna's phone",
    )


def test_a_device_whose_registration_is_gone_is_named_by_its_id() -> None:
    (item,) = check_devices([{"name": "Anna", "devices": [device(None, False)]}])
    assert item.detail == "id1"


def test_a_person_without_a_usable_device_is_a_warning() -> None:
    profiles = [
        {"name": "Anna", "devices": [device("Phone", True)]},
        {"name": "Ben", "devices": []},
        {"name": "Cy", "devices": [device("Old", False)]},
    ]
    found = check_people(profiles)
    assert [(i.subject, i.level) for i in found] == [("Ben", "warning"), ("Cy", "warning")]


def test_a_group_that_reaches_no_speaker_is_an_error() -> None:
    found = check_groups(
        [{"name": "Hall", "reachable": False}, {"name": "Kitchen", "reachable": True}]
    )
    assert [(i.subject, i.level, i.page) for i in found] == [("Hall", "error", "recipients")]


def test_an_invalid_policy_gives_its_reason_and_a_deleted_target_is_another_error() -> None:
    found = check_policies(
        [
            {"name": "Bad", "invalid": "after_required", "problem": None},
            {"name": "Gone", "invalid": None, "problem": "audience_missing"},
            {"name": "Fine", "invalid": None, "problem": None},
        ]
    )
    assert [(i.kind, i.subject, i.detail) for i in found] == [
        ("policy_invalid", "Bad", "after_required"),
        ("policy_target", "Gone", "audience_missing"),
    ]


def escalation(**kw: object) -> Policy:
    return Policy(name="E", type="escalation", after_minutes=5, **kw)  # type: ignore[arg-type]


def test_a_missing_escalation_for_critical_is_a_warning() -> None:
    assert kinds(check_critical_escalation([])) == ["no_critical_escalation"]


def test_an_escalation_for_all_or_for_critical_covers_it() -> None:
    assert check_critical_escalation([escalation()]) == []
    assert check_critical_escalation([escalation(severities=frozenset({"critical"}))]) == []


def test_an_escalation_that_does_not_cover_critical_does_not_count() -> None:
    only_warning = escalation(severities=frozenset({"warning"}))
    assert kinds(check_critical_escalation([only_warning])) == ["no_critical_escalation"]
    assert kinds(check_critical_escalation([escalation(tags=frozenset({"water"}))])) == [
        "no_critical_escalation"
    ]
    assert kinds(check_critical_escalation([escalation(enabled=False)])) == [
        "no_critical_escalation"
    ]
    reminder = Policy(name="R", type="reminder", every_minutes=30, max_count=3)
    assert kinds(check_critical_escalation([reminder])) == ["no_critical_escalation"]


def test_a_person_who_does_not_accept_push_is_not_flagged_for_a_missing_device() -> None:
    profiles = [
        {"name": "Ben", "channels": ["banner", "popup"], "devices": []},
        {"name": "Cy", "channels": ["banner", "push"], "devices": []},
        {"name": "Di", "channels": ["banner", "popup"], "devices": [device("Old", False)]},
    ]
    assert [(i.subject) for i in check_people(profiles)] == ["Cy"]
    assert check_devices(profiles) == []


def test_only_warnings_can_be_dismissed_and_the_key_names_problem_and_object() -> None:
    (warning,) = check_critical_escalation([])
    assert warning.as_dict()["dismissible"] is True
    assert warning.key == "no_critical_escalation||"
    (error,) = check_groups([{"name": "Hall", "reachable": False}])
    assert error.as_dict()["dismissible"] is False
    assert error.key == "group_empty|Hall|"


def test_failed_sends_of_the_last_day_are_counted_per_channel_and_reason() -> None:
    now = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
    log = [
        {"time": "2026-11-04T11:00:00+00:00", "kind": "failed", "detail": "push|send_failed"},
        {"time": "2026-11-04T10:00:00+00:00", "kind": "failed", "detail": "push|send_failed"},
        {"time": "2026-11-04T09:00:00+00:00", "kind": "failed", "detail": "speak|no_tts_engine"},
        {"time": "2026-11-04T08:00:00+00:00", "kind": "skipped", "detail": "push|quiet_hours"},
        {"time": "2026-11-03T11:00:00+00:00", "kind": "failed", "detail": "mail|send_failed"},
    ]
    found = check_failures(log, now)
    assert [(i.subject, i.detail, i.count, i.level, i.page) for i in found] == [
        ("push", "send_failed", 2, "warning", "messages"),
        ("speak", "no_tts_engine", 1, "warning", "messages"),
    ]
    assert found[0].key == "delivery_failed|push|send_failed"  # the count is not part of the key
    assert found[0].as_dict()["dismissible"] is True
    assert check_failures([], now) == []
