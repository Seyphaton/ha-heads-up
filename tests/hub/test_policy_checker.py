"""The checker "What happens to a message?" (DESIGN §25.8): real planning and stages, at a chosen
time and presence, nothing sent or stored."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import AddDevice
from .policy_support import ESCALATION, QUIET, add_policy, make_household, pushes

NIGHT = "2026-11-03T03:00:00+01:00"
TO_ANNA = {"push": {"recipients": ["person.anna"]}}


@pytest.fixture(autouse=True)
async def berlin(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")


async def check(client: Any, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/policy_check", **data})
    return dict(await client.receive_json())


async def test_only_admins_may_ask(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    reply = await check(client, severity="info")
    assert reply["error"]["code"] == "unauthorized"


async def test_a_leak_at_night_wakes_the_admins_and_stays_quiet_for_anna(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    hass_ws_client: WebSocketGenerator,
) -> None:
    """Scenario 1, asked of the checker; nothing is sent or stored."""
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night quiet", **QUIET)
    await add_policy(
        hass,
        entry,
        "Alarms wake Admins",
        type="get_through",
        tags=["alarm"],
        covers="only",
        covers_recipients=["person.ben"],
    )
    await add_policy(
        hass,
        entry,
        "Alarms to Admins",
        type="deliver",
        tags=["alarm"],
        channels=["push"],
        targets={"push": {"recipients": ["person.ben"]}},
    )
    client = await hass_ws_client(hass)
    reply = await check(client, severity="warning", tag="alarm", at=NIGHT, to=TO_ANNA)
    rows = {
        (r["person"], r["channel"]): r for r in reply["result"]["rows"] if r["channel"] == "push"
    }
    anna, ben = rows[("person.anna", "push")], rows[("person.ben", "push")]
    assert anna["result"] == "sent" and anna["note"] == "quiet" and anna["by"] == "Night quiet"
    assert ben["result"] == "sent" and ben.get("note") is None
    assert ben["through"] == ["Alarms wake Admins"] and ben["via"] == "Alarms to Admins"
    assert not pushes(home.anna) and not pushes(home.ben)
    assert entry.runtime_data.banners == {}


async def test_the_plan_shows_escalations_and_reminders_with_what_holds_them(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", type="reminder", every_minutes=10, max_count=3)
    client = await hass_ws_client(hass)
    reply = await check(client, severity="warning", at="2026-11-03T12:00:00+01:00", to=TO_ANNA)
    steps = reply["result"]["steps"]
    assert [(s["policy"], s["time"][11:16]) for s in steps] == [
        ("Water", "11:05"),
        ("Nag", "11:10"),
        ("Nag", "11:20"),
        ("Nag", "11:30"),
    ]
    reply = await check(client, severity="warning", at=NIGHT, to=TO_ANNA, ack_after=8)
    (water,) = reply["result"]["steps"]  # acknowledged after 8 minutes: no reminders
    assert water["rows"][0]["result"] == "held" and water["rows"][0]["by"] == "Night"


async def test_who_is_home_can_be_chosen(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Wait for home", type="presence")
    client = await hass_ws_client(hass)
    reply = await check(client, severity="info", to=TO_ANNA, home={"person.anna": False})
    (push,) = [r for r in reply["result"]["rows"] if r["channel"] == "push"]
    assert push["result"] == "held" and push["by"] == "Wait for home"
    reply = await check(client, severity="info", to=TO_ANNA, home={"person.anna": True})
    (push,) = [r for r in reply["result"]["rows"] if r["channel"] == "push"]
    assert push["result"] == "sent"


async def test_a_band_entry_that_is_off_is_named(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(
        hass, entry, "Critical", type="get_through", severities=["critical"], enabled=False
    )
    client = await hass_ws_client(hass)
    reply = await check(client, severity="critical", channels=["banner"])
    assert reply["result"]["band_off"] == ["Critical"]


async def test_a_watch_rule_source_fits_from_watch_rule(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(
        hass, entry, "Leak rule", type="reminder", rules=["abc"], every_minutes=5, max_count=1
    )
    client = await hass_ws_client(hass)
    reply = await check(client, severity="warning", rule="abc", channels=["banner"])
    assert [p["name"] for p in reply["result"]["policies"]] == ["Leak rule"]
    reply = await check(client, severity="warning", channels=["banner"])
    assert reply["result"]["policies"] == []
