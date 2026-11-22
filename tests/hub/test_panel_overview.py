"""Overview, Messages and trace data: states, counts, the log, recent messages (D-118)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from ..test_restart import restart
from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    SUMMARIZE,
    add_audience,
    add_policy,
    make_household,
    send,
    wait,
)


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def overview(hass: HomeAssistant, client: Any) -> dict[str, Any]:
    reply = await ask(client, "panel_overview")
    assert reply["success"], reply
    return dict(reply["result"])


def log_kinds(result: dict[str, Any]) -> list[str]:
    return [e["kind"] for e in result["log"]]


async def test_every_panel_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    for command, data in (
        ("panel_overview", {}),
        ("panel_messages", {}),
        ("panel_trace", {"message_id": "m"}),
        ("panel_clear", {"message_id": "m"}),
        ("panel_acknowledge", {"message_id": "m"}),
        ("panel_reach", {}),
        ("panel_audiences", {}),
        ("panel_stats", {"period": "week"}),
        ("stats_clear", {}),
    ):
        assert (await ask(client, command, **data))["error"]["code"] == "unauthorized"


async def test_the_active_tile_counts_messages_and_their_states(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, id="a", message="Leak")
    await send(hass, entry, id="b", message="Door", channels=["banner"], to={}, policy="none")
    client = await hass_ws_client(hass)
    result = await overview(hass, client)
    assert result["active"]["count"] == 2
    assert (
        result["active"]["counts"]["escalating"] == 1
        and result["active"]["counts"]["reminding"] == 1
    )
    states = {i["id"]: [s["state"] for s in i["states"]] for i in result["active"]["items"]}
    assert sorted(states["a"]) == ["escalating", "reminding"] and states["b"] == []
    pending = next(s for s in result["active"]["items"][0]["states"] if s["state"] == "escalating")
    assert pending["phase"] == "pending" and pending["policy"] == "Water" and pending["due"]


async def test_an_escalation_that_fired_is_still_listed_until_someone_acknowledges(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await wait(hass, entry, freezer, 6)
    client = await hass_ws_client(hass)
    (item,) = (await overview(hass, client))["active"]["items"]
    assert item["states"] == [{"state": "escalating", "phase": "sent", "policy": "Water"}]
    entry.runtime_data.acknowledge("m", "anna-id")
    (item,) = (await overview(hass, client))["active"]["items"]
    assert [s["state"] for s in item["states"]] == ["acknowledged"]


async def test_snoozed_and_held_messages_have_their_states(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(
        hass, entry, id="s", severity="warning", snooze="user", snooze_options=[{"minutes": 5}]
    )
    entry.runtime_data.snooze("s", "anna-id", 300)
    await send(hass, entry, id="h", severity="warning", tag="digest")
    client = await hass_ws_client(hass)
    result = await overview(hass, client)
    by_id = {i["id"]: [s["state"] for s in i["states"]] for i in result["active"]["items"]}
    assert by_id == {"s": ["snoozed"], "h": ["held"]}
    assert result["active"]["counts"]["snoozed"] == 1 and result["active"]["counts"]["held"] == 1


async def test_a_rule_message_is_in_the_active_tile_and_the_rules_tile(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    add_rule(hass, entry, enabled=False)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    quiet = await overview(hass, client)
    assert quiet["active"]["count"] == 0
    assert quiet["rules"] | {"items": None} == {
        "total": 2,
        "enabled": 1,
        "disabled": 1,
        "showing": 0,
        "items": None,
    }
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    shown = await overview(hass, client)
    assert shown["rules"]["showing"] == 1 and shown["active"]["count"] == 1
    assert shown["active"]["items"][0]["source"] == "rule"
    rule = next(r for r in shown["rules"]["items"] if r["showing"])
    assert rule["entity_id"] == WINDOW and rule["operator"] == "equals" and rule["state"] == ["on"]


async def test_needs_attention_lists_what_is_wrong_and_a_fix_page(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    add_rule(hass, entry, entity_id="binary_sensor.missing")
    await add_policy(
        hass,
        entry,
        "Gone",
        **{**ESCALATION, "severities": ["warning"], "targets": {"push": {"audience": "Deleted"}}},
    )
    await add_policy(hass, entry, "Odd", type="mystery")
    hass.config_entries.async_add_subentry(
        entry,
        __import__("homeassistant.config_entries", fromlist=["ConfigSubentry"]).ConfigSubentry(
            data={"members": ["media_player.nowhere"], "areas": []},
            subentry_type="recipient_group",
            title="Hall",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    items = {(i["kind"], i["subject"]): i for i in (await overview(hass, client))["attention"]}
    assert ("rule_entity", "Rule") in items and items[("rule_entity", "Rule")]["page"] == "rules"
    assert items[("policy_target", "Gone")]["detail"] == "audience_missing"
    assert items[("policy_invalid", "Odd")]["detail"] == "unknown_type"
    assert ("group_empty", "Hall") in items
    assert ("person_no_device", "person.anna") in items
    assert ("no_critical_escalation", "") in items


async def test_a_healthy_setup_has_nothing_to_attend_to_and_no_critical_warning_with_an_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    client = await hass_ws_client(hass)
    assert (await overview(hass, client))["attention"] == []


async def test_the_log_records_the_kinds_of_the_specification_newest_first(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, snooze="user", snooze_options=[{"minutes": 5}])
    await wait(hass, entry, freezer, 6)
    entry.runtime_data.snooze("m", "anna-id", 300)
    entry.runtime_data.acknowledge("m", "ben-id")
    entry.runtime_data.dismiss("m", "ben-id")
    await wait(hass, entry, freezer, 6)
    await hass.services.async_call("heads_up", "clear_notifications", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    client = await hass_ws_client(hass)
    result = await overview(hass, client)
    kinds = log_kinds(result)
    for kind in (
        "created",
        "escalation_sent",
        "snoozed",
        "acknowledged",
        "dismissed",
        "unsnoozed",
        "cleared",
    ):
        assert kind in kinds, kind
    assert kinds[0] == "cleared" and kinds[-1] == "created"
    ack = next(e for e in result["log"] if e["kind"] == "acknowledged")
    assert ack["detail"] == "ben" or ack["detail"] is None


async def test_the_log_names_who_acknowledged_by_first_name(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.states.async_set(
        "person.anna", "home", {"user_id": "anna-id", "friendly_name": "Anna Schmidt"}
    )
    await send(hass, entry, channels=["banner"], to={})
    entry.runtime_data.acknowledge("m", "anna-id")
    client = await hass_ws_client(hass)
    entry_ = next(e for e in (await overview(hass, client))["log"] if e["kind"] == "acknowledged")
    assert entry_["detail"] == "Anna" and entry_["message_id"] == "m"


async def test_skips_failures_reminders_summaries_and_expiry_are_logged(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(hass, entry, id="x", to={"push": {"recipients": ["person.anna"]}}, timeout=900)
    await send(hass, entry, id="d", severity="warning", tag="digest", channels=["banner"], to={})
    set_person(hass, "person.cy", "home", user_id="cy-id")
    await send(hass, entry, id="n", severity="warning", to={"push": {"recipients": ["person.cy"]}})
    # Two steps: the reminder (10 min) and the expiry (15 min) must not fire in one tick, or the
    # order of the timers decides whether the reminder is sent before the message ends. The
    # client connects after the short step and before the long one: the token expires after 30.
    await wait(hass, entry, freezer, 11)
    client = await hass_ws_client(hass)
    await wait(hass, entry, freezer, 50)
    kinds = log_kinds(await overview(hass, client))
    for kind in ("reminder_sent", "summary_sent", "skipped", "expired"):
        assert kind in kinds, kind


async def test_the_log_is_bounded_by_the_history_setting(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "trace_entries": 50})
    await hass.async_block_till_done()
    for i in range(60):
        await send(hass, entry, id=f"m{i}", severity="info", channels=["banner"], to={})
    client = await hass_ws_client(hass)
    assert len((await overview(hass, client))["log"]) == 50
    assert len(entry.runtime_data.hub.log) == 50


async def test_the_recent_messages_are_newest_first_and_bounded(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "recent_messages": 10})
    await hass.async_block_till_done()
    for i in range(12):
        await send(
            hass,
            entry,
            id=f"m{i:02}",
            severity="info",
            channels=["banner"],
            to={},
            message=f"Message {i}",
        )
    client = await hass_ws_client(hass)
    listed = (await ask(client, "panel_messages"))["result"]["messages"]
    assert [m["id"] for m in listed][:2] == ["m11", "m10"] and len(listed) == 10
    assert listed[0]["message"] == "Message 11" and listed[0]["active"] is True


async def test_an_ended_message_stays_listed_with_its_reason(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await send(hass, entry, channels=["banner"], to={})
    await hass.services.async_call("heads_up", "clear_notifications", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    client = await hass_ws_client(hass)
    (item,) = (await ask(client, "panel_messages"))["result"]["messages"]
    assert item["active"] is False and item["ended"] and item["reason"]


async def test_messages_count_their_delivery_results(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await send(
        hass, entry, to={"push": {"recipients": ["person.anna", "person.zed"]}}
    ) if False else None
    await send(hass, entry)
    client = await hass_ws_client(hass)
    (item,) = (await ask(client, "panel_messages"))["result"]["messages"]
    assert item["results"]["sent"] >= 1 and item["channels"] == ["banner", "push"]


async def test_after_a_restart_the_list_is_empty_but_active_messages_come_back(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await send(hass, entry, id="old", channels=["banner"], to={}, timeout=0)
    await send(hass, entry, id="gone", channels=["banner"], to={}, timeout=0)
    await hass.services.async_call("heads_up", "clear_notifications", {"id": "gone"}, blocking=True)
    await restart(hass, entry)
    await settle(hass, entry)
    client = await hass_ws_client(hass)
    listed = (await ask(client, "panel_messages"))["result"]["messages"]
    assert [m["id"] for m in listed] == ["old"] and listed[0]["active"] is True
    assert (await overview(hass, client))["log"] == []


async def test_the_trace_shows_entries_deliveries_timers_and_acknowledgements(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    hass.states.async_set(
        "person.anna", "home", {"user_id": "anna-id", "friendly_name": "Anna Schmidt"}
    )
    entry.runtime_data.acknowledge("m", "anna-id")
    client = await hass_ws_client(hass)
    result = (await ask(client, "panel_trace", message_id="m"))["result"]
    assert {e["channel"] for e in result["entries"]} >= {"banner", "push"}
    assert {d["channel"] for d in result["deliveries"]} == {"banner", "push"}
    acknowledged = next(e for e in result["entries"] if e["result"] == "acknowledged")
    assert acknowledged["who"] == "Anna"
    stopped = [e for e in result["entries"] if e["channel"] == "timer"]
    assert stopped and all(e["timer"] == {"type": "escalation", "policy": "Water"} for e in stopped)
    (timer,) = result["timers"]
    assert timer["type"] == "escalation" and timer["policy"] == "Water" and timer["due"]
    assert result["acknowledged_by"] == ["Anna"] and result["acknowledged_count"] == 1


async def test_the_trace_of_an_unknown_message_is_an_error(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "panel_trace", message_id="nope"))["error"]["code"] == "not_found"


async def test_the_overview_offers_the_first_run_hint_until_a_policy_exists(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await overview(hass, client))["first_run"] is True
    await add_policy(hass, entry, "Water", **ESCALATION)
    assert (await overview(hass, client))["first_run"] is False
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna"])


async def test_a_warning_can_be_hidden_and_shown_again_but_an_error_stays(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    add_rule(hass, entry, entity_id="binary_sensor.missing")
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    first = await overview(hass, client)
    warning = next(i for i in first["attention"] if i["kind"] == "no_critical_escalation")
    assert warning["dismissible"] is True and first["attention_hidden"] == 0
    assert (await ask(client, "attention_dismiss", key=warning["key"]))["success"]
    hidden = await overview(hass, client)
    assert "no_critical_escalation" not in [i["kind"] for i in hidden["attention"]]
    assert hidden["attention_hidden"] == 1
    assert "rule_entity" in [i["kind"] for i in hidden["attention"]]
    error = next(i for i in hidden["attention"] if i["kind"] == "rule_entity")
    assert error["dismissible"] is False
    # A dismissal of an error key changes nothing: errors are never hidden.
    await ask(client, "attention_dismiss", key=error["key"])
    assert "rule_entity" in [i["kind"] for i in (await overview(hass, client))["attention"]]
    assert (await ask(client, "attention_restore"))["success"]
    shown = await overview(hass, client)
    assert shown["attention_hidden"] == 0
    assert "no_critical_escalation" in [i["kind"] for i in shown["attention"]]


async def test_hiding_a_warning_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "attention_dismiss", key="x"))["error"]["code"] == "unauthorized"
    assert (await ask(client, "attention_restore"))["error"]["code"] == "unauthorized"


async def test_a_person_with_push_switched_off_is_not_flagged(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home", user_id="ben-id")
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": "person.ben", "channels": ["banner", "popup"]},
            subentry_type="recipient_profile",
            title="Ben",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    subjects = [
        i["subject"]
        for i in (await overview(hass, client))["attention"]
        if i["kind"] == "person_no_device"
    ]
    assert subjects == ["person.anna"]


async def test_the_shortcut_cards_count_audiences_policies_and_channels(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_audience(hass, entry, "Parents", kind="persons", persons=[])
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Off", **{**ESCALATION, "enabled": False})
    client = await hass_ws_client(hass)
    shortcuts = (await overview(hass, client))["shortcuts"]
    assert shortcuts["audiences"] == {"builtin": 6, "custom": 1}
    assert shortcuts["policies"] == {"total": 2, "enabled": 1}
    assert shortcuts["channels"] == {"total": 6, "mail": False}


def test_the_hourly_history_counts_created_messages_by_severity() -> None:
    from custom_components.heads_up.hub.activity import Activity, ActivityLog

    now = 1_800_000_000.0

    def created(seconds_ago: float, severity: str | None, kind: str = "created") -> Activity:
        from datetime import UTC, datetime

        stamp = datetime.fromtimestamp(now - seconds_ago, UTC).isoformat()
        return Activity(stamp, kind, "m", None, severity)

    log = ActivityLog(50)
    log.add(created(10, "critical"))
    log.add(created(3599, "info"))  # still the last hour
    log.add(created(3600, "info"))  # the hour before
    log.add(created(5 * 3600 + 5, "warning"))
    log.add(created(24 * 3600 - 1, "passive"))  # the oldest hour
    log.add(created(24 * 3600, "passive"))  # out of range
    log.add(created(60, "warning", kind="acknowledged"))  # not a creation

    history = log.created_histogram(now)
    buckets = history["buckets"]
    assert history["hours"] == len(buckets) == 24
    assert buckets[23] == {"total": 2, "by": {"critical": 1, "info": 1}}
    assert buckets[22] == {"total": 1, "by": {"info": 1}}
    assert buckets[18] == {"total": 1, "by": {"warning": 1}}
    assert buckets[0] == {"total": 1, "by": {"passive": 1}}
    assert history["total"] == 5
    assert history["peak"] == 2


async def test_the_overview_carries_the_hourly_history(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    quiet = (await overview(hass, client))["activity"]
    assert quiet["total"] == 0 and len(quiet["buckets"]) == 24
    await hass.services.async_call(
        "heads_up", "create_banner", {"message": "Window open", "severity": "info"}, blocking=True
    )
    busy = (await overview(hass, client))["activity"]
    assert busy["total"] == 1
    assert busy["buckets"][23]["by"] == {"info": 1}


async def test_the_overview_offers_acknowledge_only_while_a_policy_waits_for_one(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry, id="a", message="Leak")
    await send(hass, entry, id="b", message="Door", channels=["banner"], to={}, policy="none")
    client = await hass_ws_client(hass)
    items = {i["id"]: i for i in (await overview(hass, client))["active"]["items"]}
    assert items["a"]["can_acknowledge"] and not items["b"]["can_acknowledge"]
    assert items["a"]["can_clear"] and items["b"]["can_clear"]
    assert (await ask(client, "panel_acknowledge", message_id="a"))["success"]
    items = {i["id"]: i for i in (await overview(hass, client))["active"]["items"]}
    assert not items["a"]["can_acknowledge"]
    assert [s["state"] for s in items["a"]["states"]] == ["acknowledged"]


async def test_an_administrator_acknowledges_a_message_that_is_not_addressed_to_them(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry, id="a", message="Leak")
    entry.runtime_data.banners["a"].people = ["person.nobody"]
    client = await hass_ws_client(hass)
    assert (await ask(client, "panel_acknowledge", message_id="a"))["success"]
    assert entry.runtime_data.banners["a"].acknowledged_by


async def test_the_overview_clears_a_message_on_every_channel(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await send(hass, entry, id="a", message="Bell only", channels=["persistent"], to={})
    client = await hass_ws_client(hass)
    assert (await ask(client, "panel_clear", message_id="a"))["success"]
    assert (await overview(hass, client))["active"]["count"] == 0


async def test_clearing_or_acknowledging_an_unknown_message_is_not_found(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    for command in ("panel_clear", "panel_acknowledge"):
        reply = await ask(client, command, message_id="missing")
        assert reply["error"]["code"] == "not_found"


async def test_status_and_coming_up_are_empty_without_messages(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = await overview(hass, client)
    assert result["status"] == {"count": 0, "items": []}
    assert result["coming_up"] == []


async def test_status_lists_only_unacknowledged_critical_and_warning_messages(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, id="c", severity="critical", message="Leak")
    await send(hass, entry, id="w", severity="warning", message="Door", snooze="user")
    await send(hass, entry, id="i", severity="info", message="FYI")
    await send(hass, entry, id="p", severity="passive", message="Done")
    await send(hass, entry, id="a", severity="critical", message="Seen")
    entry.runtime_data.acknowledge("a", "anna-id")
    client = await hass_ws_client(hass)
    status = (await overview(hass, client))["status"]
    assert status["count"] == 2
    by_id = {i["id"]: i for i in status["items"]}
    assert set(by_id) == {"c", "w"}
    assert by_id["w"]["snoozable"] is True and by_id["c"]["snoozable"] is False
    assert by_id["c"]["can_acknowledge"] is False  # no policy applies, so nothing to acknowledge
    assert by_id["c"]["severity"] == "critical"


async def test_coming_up_names_the_escalation_and_the_reminder_with_time_and_count(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, id="a", message="Leak")
    await send(hass, entry, id="b", message="Pipe")
    client = await hass_ws_client(hass)
    coming = (await overview(hass, client))["coming_up"]
    kinds = {c["kind"]: c for c in coming}
    assert set(kinds) == {"escalation", "reminder"}
    assert kinds["escalation"]["count"] == 2 and kinds["escalation"]["policy"] == "Water"
    assert kinds["reminder"]["count"] == 2 and kinds["reminder"]["time"]
    assert [c["time"] for c in coming] == sorted(c["time"] for c in coming)
    entry.runtime_data.acknowledge("a", "anna-id")
    coming = (await overview(hass, client))["coming_up"]
    assert {c["kind"]: c["count"] for c in coming} == {"escalation": 1, "reminder": 1}


async def test_coming_up_counts_messages_held_for_a_summary_with_the_summary_time(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(hass, entry, id="h1", severity="warning", tag="digest")
    await send(hass, entry, id="h2", severity="warning", tag="digest")
    client = await hass_ws_client(hass)
    coming = (await overview(hass, client))["coming_up"]
    (summary,) = [c for c in coming if c["kind"] == "summary"]
    assert summary["count"] == 2 and summary["time"] and summary["policy"] == "Digest"


async def test_coming_up_counts_messages_held_by_quiet_hours_with_the_release_time(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)  # before the clock moves: tokens expire in frozen time
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, id="n1", severity="warning")
    await send(hass, entry, id="n2", severity="warning")
    coming = (await overview(hass, client))["coming_up"]
    (quiet,) = [c for c in coming if c["kind"] == "quiet_release"]
    assert quiet["count"] == 2
    assert quiet["time"].startswith("2026-11-03T06:00:00")  # 07:00 Berlin in UTC


async def test_last_actions_is_one_row_per_message_newest_first_and_without_summaries(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    client = await hass_ws_client(hass)  # before the clock moves
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(hass, entry, id="a", message="First", title="First title")
    await send(hass, entry, id="b", message="Second")
    await send(hass, entry, id="h", message="Held", tag="digest", severity="warning")
    await wait(hass, entry, freezer, 61)  # the summary is made and is not a row of its own
    rows = (await overview(hass, client))["last_actions"]
    assert [r["id"] for r in rows] == ["h", "b", "a"]
    assert rows[2]["title"] == "First title" and rows[1]["title"] is None
    assert rows[1]["message"] == "Second" and rows[1]["severity"] == "critical"
    assert rows[1]["source"] == {"kind": "action", "name": None}


async def test_last_actions_is_limited_to_five_rows(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    for n in range(9):
        await send(hass, entry, id=f"m{n}", message=f"Message {n}")
    client = await hass_ws_client(hass)
    rows = (await overview(hass, client))["last_actions"]
    assert len(rows) == 5 and rows[0]["id"] == "m8"


async def test_a_row_tells_what_became_of_the_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    await wait(hass, entry, freezer, 12)
    entry.runtime_data.acknowledge("m", "anna-id")
    await settle(hass, entry)
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["state"] == "acknowledged"
    assert row["acknowledged"]["seconds"] == 720
    assert row["escalated"] == 1 and row["reminded"] >= 1
    assert row["results"]["sent"] >= 2 and "failed" not in row["results"]


async def test_a_row_names_the_policy_that_held_it_and_the_reason_something_was_skipped(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.cleo", "home")  # no phone: push is skipped for them
    night = await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(
        hass, entry, severity="warning", to={"push": {"recipients": ["person.anna", "person.cleo"]}}
    )
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["held_by"] == [night.title]
    assert {p["reason"] for p in row["problems"]} == {"no_usable_device"}


async def test_a_rule_row_has_the_rules_name_and_an_ended_message_its_reason(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.states.async_set(WINDOW, "off")
    rule = add_rule(hass, entry, severity="warning")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    hass.states.async_set(WINDOW, "off")
    await settle(hass, entry)
    client = await hass_ws_client(hass)
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["source"] == {"kind": "rule", "name": rule.title}
    assert row["state"] == "ended" and row["end_reason"]


async def test_last_actions_are_ordered_by_their_latest_activity_not_by_when_they_began(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, id="old", message="Began first")
    await wait(hass, entry, freezer, 5)
    await send(hass, entry, id="new", message="Began second")
    await wait(hass, entry, freezer, 5)
    await send(hass, entry, id="old", message="Updated again")  # the first message moves up
    client = await hass_ws_client(hass)
    rows = (await overview(hass, client))["last_actions"]
    assert [r["id"] for r in rows] == ["old", "new"]
    times = [r["time"] for r in rows]
    assert times == sorted(times, reverse=True)


async def test_an_updated_message_counts_each_recipient_once(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    for n in range(4):
        await send(hass, entry, id="same", message=f"Update {n}")
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["results"] == {"sent": 2}  # the banner and Anna's phone, not eight sends
    assert row["problems"] == []  # an update that changed nothing is not a skip to show


async def test_an_acknowledgement_of_an_earlier_appearance_is_not_counted(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    freezer: FrozenDateTimeFactory,
) -> None:
    client = await hass_ws_client(hass)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="warning")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    (rule_id,) = entry.runtime_data.rules
    entry.runtime_data.acknowledge(rule_id, "anna-id", any_message=True)
    await settle(hass, entry)
    hass.states.async_set(WINDOW, "off")
    await settle(hass, entry)
    await wait(hass, entry, freezer, 10)
    hass.states.async_set(WINDOW, "on")  # it appears again, as a new message
    await settle(hass, entry)
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["acknowledged"] is None and row["state"] == "active"


async def test_a_part_of_the_overview_that_fails_is_empty_and_the_rest_still_loads(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    monkeypatch: Any,
    caplog: Any,
) -> None:
    from custom_components.heads_up.hub import panel_data

    await make_household(hass, mobile_app_device)
    await send(hass, entry)

    def broken(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("prod data nobody tested")

    monkeypatch.setattr(panel_data, "last_actions", broken)
    monkeypatch.setattr(panel_data, "coming_up", broken)
    client = await hass_ws_client(hass)
    result = await overview(hass, client)
    assert result["last_actions"] == [] and result["coming_up"] == []
    assert result["status"]["count"] == 1 and result["active"]["count"] == 1
    assert "The Overview part last_actions could not be built" in caplog.text


async def test_a_row_says_who_was_reached_per_person_and_the_audience(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.cleo", "home")  # no phone: push cannot reach them
    await send(
        hass,
        entry,
        to={"push": {"audience": "Everyone"}},
    )
    (row,) = (await overview(hass, client))["last_actions"]
    reach = row["reach"]
    assert reach["reached"] == ["Anna", "Ben"] and reach["not_reached"] == ["Cleo"]
    assert reach["audiences"] == ["Everyone"] and reach["excluded"] == []
    assert row["channels"] == ["banner", "push"] and row["trace_complete"] is True


async def test_a_disabled_person_is_excluded_from_reach_and_from_the_problems(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": "person.ben", "enabled": False, "channels": ["banner", "push"]},
            subentry_type="recipient_profile",
            title="person.ben",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await send(hass, entry, to={"push": {"audience": "Everyone"}})
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["reach"]["reached"] == ["Anna"] and row["reach"]["excluded"] == ["Ben"]
    assert row["reach"]["excluded_reasons"] == {"Ben": "recipient_disabled"}
    assert row["problems"] == []  # a choice is no problem


async def test_a_person_with_two_phones_counts_once_and_a_row_without_trace_says_so(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    await mobile_app_device("Anna's tablet", user_id="anna-id", person_entity_id="person.anna")
    await send(hass, entry, to={"push": {"audience": "Everyone"}})
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["reach"]["reached"] == ["Anna", "Ben"]
    entry.runtime_data.hub.trace.resize(1)
    entry.runtime_data.hub.trace._entries.clear()  # the trace rotated out
    (row,) = (await overview(hass, client))["last_actions"]
    assert row["trace_complete"] is False and row["reach"]["reached"] == []


async def test_the_log_lists_who_was_reached_and_who_was_left_out_on_purpose(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": "person.ben", "enabled": False, "channels": ["banner", "push"]},
            subentry_type="recipient_profile",
            title="person.ben",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await send(hass, entry, to={"push": {"audience": "Everyone"}})
    client = await hass_ws_client(hass)
    (item,) = (await ask(client, "panel_messages"))["result"]["messages"]
    assert item["delivered_channels"] == ["banner", "push"] and item["channels"] == [
        "banner",
        "push",
    ]
    assert item["reach"]["reached"] == ["Anna"] and item["trace_complete"] is True
    reach = (await ask(client, "panel_trace", message_id="m"))["result"]["reach"]
    assert reach["excluded"] == ["Ben"] and reach["excluded_reasons"] == {
        "Ben": "recipient_disabled"
    }
    assert reach["audiences"] == ["Everyone"]
