"""The policy subentry form: both types, the checks, duplicates and reconfigure."""

from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.policies import escalation, reminder

from .helpers import set_person
from .test_audiences_flows import run, subentries

ESCALATION: dict[str, Any] = {
    "name": "Water escalation",
    "type": "escalation",
    "severities": ["critical"],
    "after_minutes": 5,
    "channels": ["push"],
    "push_recipients": ["person.ben"],
}


async def test_add_an_escalation_stores_its_targets_per_channel(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    result = await run(hass, entry, "policy", ESCALATION)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert sub.title == "Water escalation"
    assert dict(sub.data) == {
        "type": "escalation",
        "severities": ["critical"],
        "tags": [],
        "enabled": True,
        "after_minutes": 5,
        "channels": ["push"],
        "targets": {"push": {"recipients": ["person.ben"]}},
        "dismiss_acks": False,
    }
    await hass.async_block_till_done()
    assert "Water escalation" in entry.runtime_data.hub.policies.names()


async def test_add_a_reminder_with_the_defaults_confirmed_by_the_maintainer(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await run(hass, entry, "policy", {"name": "Nag", "type": "reminder"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert sub.data["every_minutes"] == 30 and sub.data["max_count"] == 3
    assert sub.data["enabled"] is True


async def test_an_escalation_needs_channels_and_a_target_for_each(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    result = await run(hass, entry, "policy", {**ESCALATION, "channels": [], "push_recipients": []})
    assert result["errors"]["channels"] == "channels_required"
    result = await run(hass, entry, "policy", {**ESCALATION, "push_recipients": []})
    assert result["errors"]["push_audience"] == "target_exclusive"


async def test_audience_and_recipients_together_are_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    result = await run(hass, entry, "policy", {**ESCALATION, "push_audience": "Everyone"})
    assert result["errors"]["push_audience"] == "target_exclusive"


async def test_an_unknown_audience_or_recipient_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    bad_audience = {**ESCALATION, "push_recipients": [], "push_audience": "Nobody"}
    result = await run(hass, entry, "policy", bad_audience)
    assert result["errors"]["push_audience"] == "audience_unknown"
    result = await run(hass, entry, "policy", {**ESCALATION, "push_recipients": ["person.zed"]})
    assert result["errors"]["push_recipients"] == "recipient_unknown"


async def test_speech_takes_recipients_only(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    result = await run(
        hass, entry, "policy", {**ESCALATION, "channels": ["speak"], "speak_recipients": []}
    )
    assert result["errors"]["speak_recipients"] == "target_exclusive"


async def test_a_second_policy_with_the_same_type_applies_to_and_trigger_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    await run(hass, entry, "policy", ESCALATION)
    result = await run(hass, entry, "policy", {**ESCALATION, "name": "Another"})
    assert result["errors"]["base"] == "policy_duplicate"
    assert len(subentries(entry, "policy")) == 1


async def test_none_and_taken_names_are_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    result = await run(hass, entry, "policy", {**ESCALATION, "name": "None"})
    assert result["errors"]["name"] == "name_exists"
    await run(hass, entry, "policy", ESCALATION)
    other = {**ESCALATION, "name": "water escalation", "after_minutes": 9}
    assert (await run(hass, entry, "policy", other))["errors"]["name"] == "name_exists"


def test_the_checks_refuse_a_zero_interval_count_or_unknown_channel() -> None:
    assert reminder.check({"every_minutes": 0, "max_count": 0, "channels": ["banner"]}) == {
        "every_minutes": "every_required",
        "max_count": "max_required",
        "channels": "channel_unknown",
    }
    assert escalation.check({"after_minutes": 0, "channels": []}) == {
        "after_minutes": "after_required",
        "channels": "channels_required",
    }


async def test_reconfigure_changes_a_policy_without_being_its_own_duplicate(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    await run(hass, entry, "policy", ESCALATION)
    (sub,) = subentries(entry, "policy")
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, "policy"),
        context={"source": config_entries.SOURCE_RECONFIGURE, "subentry_id": sub.subentry_id},
    )
    assert result["type"] is FlowResultType.FORM
    done = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**ESCALATION, "dismiss_acks": True}
    )
    assert done["type"] is FlowResultType.ABORT and done["reason"] == "reconfigure_successful"
    assert entry.subentries[sub.subentry_id].data["dismiss_acks"] is True


async def test_add_quiet_hours_with_the_confirmed_defaults(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await run(hass, entry, "policy", {"name": "Night", "type": "quiet_hours"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert dict(sub.data) == {
        "type": "quiet_hours",
        "severities": [],
        "tags": [],
        "enabled": True,
        "from_time": "22:00:00",
        "to_time": "07:00:00",
        "days": [],
        "action": "quiet",
        "critical_passes": True,
    }


async def test_a_quiet_hours_window_needs_different_start_and_end(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    same = {"name": "Night", "type": "quiet_hours", "from_time": "08:00:00", "to_time": "08:00:00"}
    assert (await run(hass, entry, "policy", same))["errors"]["to_time"] == "window_empty"


async def test_the_same_quiet_window_for_the_same_messages_is_a_duplicate(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await run(hass, entry, "policy", {"name": "Night", "type": "quiet_hours"})
    again = await run(hass, entry, "policy", {"name": "Night 2", "type": "quiet_hours"})
    assert again["errors"]["base"] == "policy_duplicate"
    other = {"name": "Night 3", "type": "quiet_hours", "days": ["sat"]}
    assert (await run(hass, entry, "policy", other))["type"] is FlowResultType.CREATE_ENTRY


async def test_add_away_with_a_maximum_wait(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    result = await run(hass, entry, "policy", {"name": "Back", "type": "away", "max_wait": 45})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert sub.data["max_wait"] == 45 and "targets" not in sub.data


async def test_add_a_fallback_with_a_target_per_channel(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.ben", "home")
    data = {
        "name": "Backup",
        "type": "fallback",
        "when": "both",
        "channels": ["push"],
        "push_recipients": ["person.ben"],
    }
    assert (await run(hass, entry, "policy", data))["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert sub.data["when"] == "both"
    assert dict(sub.data["targets"]) == {"push": {"recipients": ["person.ben"]}}


async def test_a_fallback_needs_channels_and_targets(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await run(hass, entry, "policy", {"name": "Backup", "type": "fallback"})
    assert result["errors"]["channels"] == "channels_required"


async def test_add_a_summarize_policy_with_the_confirmed_defaults(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await run(hass, entry, "policy", {"name": "Digest", "type": "summarize"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert sub.data["summary_every"] == 60 and sub.data["include_critical"] is False
    assert "summary_at" not in sub.data


async def test_a_time_of_day_replaces_the_interval(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    data = {"name": "Evening", "type": "summarize", "summary_at": "20:00:00"}
    await run(hass, entry, "policy", data)
    (sub,) = subentries(entry, "policy")
    assert sub.data["summary_at"] == "20:00:00" and "summary_every" not in sub.data


async def test_two_summaries_with_the_same_schedule_for_the_same_messages_are_a_duplicate(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await run(hass, entry, "policy", {"name": "Digest", "type": "summarize"})
    again = await run(hass, entry, "policy", {"name": "Digest 2", "type": "summarize"})
    assert again["errors"]["base"] == "policy_duplicate"


async def test_add_a_deliver_policy_with_a_target_per_channel(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    data = {
        "name": "Critical delivery",
        "type": "deliver",
        "severities": ["critical"],
        "channels": ["push"],
        "push_audience": "Admins",
    }
    assert (await run(hass, entry, "policy", data))["type"] is FlowResultType.CREATE_ENTRY
    (sub,) = subentries(entry, "policy")
    assert dict(sub.data["targets"]) == {"push": {"audience": "Admins"}}
    assert "after_minutes" not in sub.data and sub.data["channels"] == ["push"]


async def test_a_deliver_policy_needs_channels_and_a_target(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    none = await run(hass, entry, "policy", {"name": "D", "type": "deliver"})
    assert none["errors"]["channels"] == "channels_required"
    no_target = await run(
        hass, entry, "policy", {"name": "D", "type": "deliver", "channels": ["push"]}
    )
    assert no_target["errors"]["push_audience"] == "target_exclusive"
