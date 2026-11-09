"""Dry run as an action and Test send from a pasted call (D-194)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import settle
from .policy_support import make_household, pushes


async def dry(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    body = {"message": "Door open", "severity": "warning", "channels": ["push"], **data}
    response = await hass.services.async_call(
        DOMAIN, "notify", {**body, "dry_run": True}, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def test_a_dry_run_reports_the_plan_and_sends_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    result = await dry(hass, id="x", recipients=["person.anna"])
    await settle(hass, entry)
    assert result["status"] == "dry_run"
    (row,) = [r for r in result["rows"] if r["channel"] == "push"]
    assert row["result"] == "sent" and row["push_level"] == "normal"
    assert not pushes(home.anna) and not entry.runtime_data.banners
    assert len(entry.runtime_data.hub.trace) == 0 and not entry.runtime_data.hub.ledger.rows


@pytest.mark.parametrize(
    ("severity", "level"),
    [
        ("success", "passive"),
        ("info", "passive"),
        ("warning", "normal"),
        ("critical", "time-sensitive"),
    ],
)
async def test_the_dry_run_names_the_push_level_of_each_severity(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    severity: str,
    level: str,
) -> None:
    await make_household(hass, mobile_app_device)
    result = await dry(hass, severity=severity, recipients=["person.anna"])
    assert {r["push_level"] for r in result["rows"] if r["channel"] == "push"} == {level}


async def test_a_dry_run_takes_an_audience_by_its_sensor(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    result = await dry(hass, audience="binary_sensor.heads_up_audience_everyone")
    assert any(r["channel"] == "push" and r["result"] == "sent" for r in result["rows"])


@pytest.mark.no_default_severity
async def test_a_dry_run_still_needs_a_valid_call(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(Exception, match=r"severity|required"):
        await hass.services.async_call(
            DOMAIN,
            "notify",
            {"message": "x", "channels": ["banner"], "dry_run": True},
            blocking=True,
            return_response=True,
        )


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


STEP = """
action: heads_up.notify
data:
  message: "Door {{ trigger.name }} is open"
  severity: warning
  channels: [push]
  recipients: [person.anna]
"""


async def test_a_pasted_call_renders_its_templates_and_shows_the_plan(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    home = await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_plan_yaml", yaml=STEP, variables="trigger:\n  name: Garage")
    assert reply["success"], reply
    assert reply["result"]["call"]["message"] == "Door Garage is open"
    assert any(r["channel"] == "push" and r["result"] == "sent" for r in reply["result"]["rows"])
    assert not pushes(home.anna) and not entry.runtime_data.banners


async def test_a_pasted_call_may_be_the_data_alone(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    text = "message: x\nseverity: info\nchannels: [push]\nrecipients: [person.anna]\n"
    reply = await ask(client, "hub_plan_yaml", yaml=text)
    assert reply["success"], reply


@pytest.mark.parametrize(
    ("text", "variables", "code"),
    [
        ("message: [", "", "yaml_invalid"),
        ("just text", "", "call_not_found"),
        ("action: light.turn_on\ndata: {}", "", "not_notify"),
        ("message: '{{ 1 / 0 }}'\nseverity: info\nchannels: [banner]", "", "template_error"),
        ("message: x\nseverity: info\nchannels: [banner]", "a: [", "variables_invalid"),
        ("message: x\nchannels: [banner]", "", "invalid_format"),
        (
            "message: x\nseverity: info\nchannels: [push]\nrecipients: [person.nobody]",
            "",
            "unknown_recipient",
        ),
    ],
)
async def test_a_pasted_call_that_cannot_run_says_why(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    text: str,
    variables: str,
    code: str,
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "hub_plan_yaml", yaml=text, variables=variables)
    assert reply["success"] is False and reply["error"]["code"] == code


async def test_a_pasted_call_is_sent_as_a_marked_test_and_never_as_a_dry_run(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    home = await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    text = STEP + "  dry_run: true\n"
    reply = await ask(client, "hub_test_send_yaml", yaml=text, variables="trigger: {name: Garage}")
    assert reply["success"], reply
    await settle(hass, entry)
    assert reply["result"]["id"].startswith("hu_test_")
    assert len(pushes(home.anna)) == 1
    assert pushes(home.anna)[0].data["message"] == "Door Garage is open"


async def test_the_pasted_call_commands_are_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    for command in ("hub_plan_yaml", "hub_test_send_yaml"):
        reply = await ask(client, command, yaml=STEP)
        assert reply["error"]["code"] == "unauthorized"
