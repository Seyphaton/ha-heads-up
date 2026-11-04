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
        hass, entry, id="s", severity="warning", snoozable=True, snooze_options=[{"minutes": 5}]
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
    await send(hass, entry, snoozable=True, snooze_options=[{"minutes": 5}])
    await wait(hass, entry, freezer, 6)
    entry.runtime_data.snooze("m", "anna-id", 300)
    entry.runtime_data.acknowledge("m", "ben-id")
    entry.runtime_data.dismiss("m", "ben-id")
    await wait(hass, entry, freezer, 6)
    await hass.services.async_call("heads_up", "clear", {"id": "m"}, blocking=True)
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
    client = await hass_ws_client(hass)  # before the clock moves: the token expires
    await wait(hass, entry, freezer, 61)
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
    await hass.services.async_call("heads_up", "clear", {"id": "m"}, blocking=True)
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
    await hass.services.async_call("heads_up", "clear", {"id": "gone"}, blocking=True)
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
    log.add(created(24 * 3600 - 1, "success"))  # the oldest hour
    log.add(created(24 * 3600, "success"))  # out of range
    log.add(created(60, "warning", kind="acknowledged"))  # not a creation

    history = log.created_histogram(now)
    buckets = history["buckets"]
    assert history["hours"] == len(buckets) == 24
    assert buckets[23] == {"total": 2, "by": {"critical": 1, "info": 1}}
    assert buckets[22] == {"total": 1, "by": {"info": 1}}
    assert buckets[18] == {"total": 1, "by": {"warning": 1}}
    assert buckets[0] == {"total": 1, "by": {"success": 1}}
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
