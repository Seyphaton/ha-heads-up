"""Test send: the dry run equals what a real delivery does, and the one real send (D-120)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import (
    ESCALATION,
    FALLBACK,
    QUIET,
    REMINDER,
    SUMMARIZE,
    add_audience,
    add_policy,
    make_household,
    move,
    pushes,
)

ANNA = {"push": {"recipients": ["person.anna"]}}


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


def call(**extra: Any) -> dict[str, Any]:
    return {
        "message": "Door open",
        "channels": ["banner", "push"],
        "to": ANNA,
        "severity": "warning",
        **extra,
    }


async def preview(client: Any, **extra: Any) -> dict[str, Any]:
    reply = await ask(client, "hub_plan", **call(**extra))
    assert reply["success"], reply
    return dict(reply["result"])


def shown(result: dict[str, Any]) -> dict[tuple[str, str], str]:
    return {(r["channel"], r["recipient"]): r["result"] for r in result["rows"] if not r["via"]}


async def real(
    hass: HomeAssistant, entry: MockConfigEntry, **extra: Any
) -> dict[tuple[str, str], str]:
    """The same call really sent, as the ledger recorded it."""
    await hass.services.async_call(DOMAIN, "notify", {"id": "real", **call(**extra)}, blocking=True)
    await settle(hass, entry)
    return {
        (r.channel, r.recipient): r.state.value
        for r in entry.runtime_data.hub.ledger.for_message("real")
    }


async def test_both_commands_are_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "hub_plan", **call()))["error"]["code"] == "unauthorized"
    assert (await ask(client, "hub_test_send", **call()))["error"]["code"] == "unauthorized"
    assert not entry.runtime_data.banners


async def test_the_dry_run_sends_stores_and_records_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    home = await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    result = await preview(client)
    assert shown(result)[("banner", "")] == "sent"
    await settle(hass, entry)
    assert not pushes(home.anna) and not entry.runtime_data.banners
    assert not entry.runtime_data.hub.ledger.rows and len(entry.runtime_data.hub.trace) == 0
    assert len(entry.runtime_data.hub.log) == 0


async def test_the_preview_equals_what_a_normal_delivery_does(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    expected = shown(await preview(client))
    assert await real(hass, entry) == expected
    assert expected[("push", "device:dev_anna_s_phone")] == "sent"


async def test_the_preview_equals_a_delivery_for_a_person_without_a_device(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    client = await hass_ws_client(hass)
    expected = shown(await preview(client))
    assert expected[("push", "person.anna")] == "skipped"
    assert await real(hass, entry) == expected


async def test_quiet_hours_show_in_the_preview_as_they_act(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)  # before the clock moves: the token expires
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await make_household(hass, mobile_app_device)
    sub = await add_policy(hass, entry, "Night", **QUIET)
    quiet = await preview(client)
    row = next(r for r in quiet["rows"] if r["channel"] == "push")
    assert row["result"] == "sent" and row["note"] == "quiet"
    assert await real(hass, entry) == shown(quiet)
    hass.config_entries.async_update_subentry(entry, sub, data={**QUIET, "action": "wait"})
    await hass.async_block_till_done()
    held = await preview(client)
    row = next(r for r in held["rows"] if r["channel"] == "push")
    assert row["result"] == "held" and row["reason"] == "quiet_hours" and row["until"]
    hass.config_entries.async_update_subentry(entry, sub, data={**QUIET, "action": "drop"})
    await hass.async_block_till_done()
    dropped = await preview(client)
    assert next(r for r in dropped["rows"] if r["channel"] == "push")["result"] == "skipped"
    banner = next(r for r in dropped["rows"] if r["channel"] == "banner")
    assert banner["result"] == "sent"  # the banner is never affected


async def test_a_held_preview_equals_a_held_delivery(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    assert await real(hass, entry) == shown(await preview(client))


async def test_a_person_who_is_away_is_held_in_the_preview_and_in_a_delivery(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])
    await add_policy(hass, entry, "Back", type="away")
    move(hass, "person.ben", "not_home")
    client = await hass_ws_client(hass)
    audience = {"to": {"push": {"audience": "Family"}}}
    result = await preview(client, **audience)
    states = {r["person"]: r["result"] for r in result["rows"] if r["channel"] == "push"}
    assert states == {"person.anna": "sent", "person.ben": "held"}
    assert await real(hass, entry, **audience) == shown(result)


async def test_a_summarize_policy_holds_every_channel_in_the_preview_and_in_a_delivery(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    client = await hass_ws_client(hass)
    result = await preview(client)
    assert result["held_for_summary"] == "Digest"
    assert {r["result"] for r in result["rows"]} == {"held"}
    assert all(r["reason"] == "summarize" for r in result["rows"])
    await real(hass, entry)
    assert entry.runtime_data.hub.is_held("real")


async def test_the_policy_field_none_removes_the_policies_from_the_preview(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    client = await hass_ws_client(hass)
    none = await preview(client, policy="none")
    assert none["policies"] == [] and none["held_for_summary"] is None
    named = await preview(client, policy="Digest")
    assert [p["name"] for p in named["policies"]] == ["Digest"]


async def test_a_fallback_that_would_fire_shows_its_rows_marked_with_its_name(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(hass, entry, "Nobody", **FALLBACK)
    client = await hass_ws_client(hass)
    result = await preview(client, to={"push": {"audience": "At home"}}, channels=["push"])
    plain = [r for r in result["rows"] if not r["via"]]
    via = [r for r in result["rows"] if r["via"] == "Nobody"]
    assert [r["result"] for r in plain] == ["skipped"]
    assert via and via[0]["channel"] == "push" and via[0]["recipient"] == "device:dev_ben_s_phone"
    assert via[0]["result"] == "sent"


async def test_the_later_steps_list_the_policies_that_apply(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await add_policy(hass, entry, "Night", **QUIET)
    client = await hass_ws_client(hass)
    later = {step["type"]: step for step in (await preview(client))["later"]}
    assert set(later) == {"escalation", "reminder"}  # quiet hours already show in the rows
    assert later["escalation"] == {
        "type": "escalation",
        "policy": "Water",
        "after_minutes": 5,
        "channels": ["push"],
    }
    assert later["reminder"]["every_minutes"] == 10 and later["reminder"]["max_count"] == 2


async def test_a_call_with_a_wrong_name_or_shape_is_refused_like_notify_would(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    client = await hass_ws_client(hass)
    bad_audience = await ask(client, "hub_plan", **call(to={"push": {"audience": "Nobody"}}))
    assert bad_audience["error"]["code"] == "unknown_audience"
    bad_policy = await ask(client, "hub_plan", **call(policy="Missing"))
    assert bad_policy["error"]["code"] == "unknown_policy"
    no_target = await ask(client, "hub_plan", message="x", channels=["push"])
    assert no_target["error"]["code"] == "invalid_format"
    both = await ask(
        client,
        "hub_plan",
        **call(to={"push": {"audience": "Everyone", "recipients": ["person.a"]}}),
    )
    assert both["error"]["code"] == "invalid_format"


async def test_send_test_sends_exactly_one_real_message_with_the_marker(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    home = await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_test_send", **call(title="Door"))
    assert reply["success"], reply
    await settle(hass, entry)
    (banner,) = entry.runtime_data.banners.values()
    assert banner.id.startswith("hu_test_") and banner.id == reply["result"]["id"]
    assert banner.title == "Test: Door" and banner.tag == "test"
    assert (banner.expires_at - banner.created_at).total_seconds() == 600
    assert reply["result"]["channels"]["push"]["sent"] == 1
    (push,) = pushes(home.anna)
    assert push.data["title"] == "Test: Door"


async def test_a_test_message_without_a_title_gets_the_title_test(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    await ask(client, "hub_test_send", **call())
    (banner,) = entry.runtime_data.banners.values()
    assert banner.title == "Test"


async def test_a_test_message_follows_the_policies_like_any_other(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_test_send", **call())
    await settle(hass, entry)
    (row,) = entry.runtime_data.hub.ledger.timers(reply["result"]["id"])
    assert row.recipient == "escalation:Water"


async def test_a_test_message_can_be_cleared_from_the_page(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_test_send", **call())
    cleared = await ask(client, "admin_clear", banner_id=reply["result"]["id"])
    assert cleared["success"] and not entry.runtime_data.banners


async def test_an_invalid_call_sends_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_test_send", **call(to={"push": {"audience": "Nobody"}}))
    assert reply["error"]["code"] == "unknown_audience"
    assert not entry.runtime_data.banners


async def test_the_preview_accepts_the_dismiss_and_snooze_choices_of_a_call(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    open_choices = await preview(
        client, dismissible=True, dismiss_scope="global", snoozable=True, snooze_scope="global"
    )
    assert shown(open_choices)[("banner", "")] == "sent"
    pinned = await preview(client, dismissible=False)
    assert shown(pinned)[("banner", "")] == "sent"
    refused = await ask(client, "hub_plan", **call(dismissible=False, snoozable=True))
    assert refused["error"]["code"] == "invalid_format"


async def test_the_preview_names_the_policies_that_make_acknowledging_matter(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    assert (await preview(client))["acknowledge"] == []
    await add_policy(hass, entry, "Water escalation", **ESCALATION)
    await add_policy(hass, entry, "Quiet night", **QUIET)
    assert (await preview(client))["acknowledge"] == ["Water escalation"]
    assert (await preview(client, policy="none"))["acknowledge"] == []
