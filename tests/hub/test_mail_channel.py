"""Mail channel: one notify service call per recipient, templates, opt-in, no stand-in (D-129)."""

import logging
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .helpers import set_person, settle
from .policy_support import add_policy, wait

EVENT = f"{DOMAIN}_delivery_failed"


def opt_in(hass: HomeAssistant, entry: MockConfigEntry, person: str, address: str = "") -> None:
    data: dict[str, Any] = {"person": person, "channels": ["banner", "mail"]}
    if address:
        data["mail_address"] = address
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(data=data, subentry_type="recipient_profile", title=person, unique_id=None),
    )


@pytest.fixture
def mailbox(hass: HomeAssistant, entry: MockConfigEntry) -> list[ServiceCall]:
    entry.runtime_data.options["mail_service"] = "smtp_house"
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home", user_id="ben-id")
    return async_mock_service(hass, "notify", "smtp_house")


async def mail(
    hass: HomeAssistant, entry: MockConfigEntry, *recipients: str, **data: Any
) -> dict[str, Any]:
    body = {
        "id": "m",
        "message": "Door open",
        "channels": ["mail"],
        "to": {"mail": {"recipients": list(recipients)}},
        "severity": "critical",
        **data,
    }
    result = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert result is not None
    return dict(result)


async def test_a_person_with_the_channel_on_gets_one_call_with_subject_body_and_address(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    result = await mail(hass, entry, "person.anna", title="Front door")
    assert result["channels"]["mail"]["sent"] == 1
    (call,) = mailbox
    assert call.data == {
        "title": "Critical: Front door",
        "message": "Door open",
        "target": ["anna@example.com"],
    }


async def test_the_title_falls_back_to_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    await mail(hass, entry, "person.anna")
    assert mailbox[0].data["title"] == "Critical: Door open"


async def test_the_templates_take_the_placeholders(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    entry.runtime_data.options["mail_subject"] = "{person}"
    entry.runtime_data.options["mail_body"] = "{severity} {id} {tag}: {message} {unknown}"
    state = hass.states.get("person.anna")
    assert state is not None
    hass.states.async_set(
        "person.anna", state.state, {**state.attributes, "friendly_name": "Anna Lee"}
    )
    opt_in(hass, entry, "person.anna", "box@example.com")
    await mail(hass, entry, "person.anna", tag="doors")
    assert mailbox[0].data["title"] == "Anna Lee"
    assert mailbox[0].data["message"] == "Critical m doors: Door open {unknown}"


async def test_mail_is_off_for_everyone_until_switched_on(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    result = await mail(hass, entry, "person.anna")
    assert result["channels"]["mail"]["skipped"] == 1
    assert mailbox == []
    reasons = [e["reason"] for e in entry.runtime_data.hub.trace.entries("m")]
    assert reasons == ["channel_not_accepted"]


async def test_a_person_without_an_address_fails_loudly_and_gets_no_stand_in(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    caplog: pytest.LogCaptureFixture,
) -> None:
    entry.runtime_data.options["mail_global_address"] = "house@example.com"
    opt_in(hass, entry, "person.anna")
    events = async_capture_events(hass, EVENT)
    with caplog.at_level(logging.WARNING):
        await mail(hass, entry, "person.anna")
    assert mailbox == []  # the global address is not a fallback for a person
    assert [f["reason"] for f in events[0].data["failed"]] == ["no_mail_address"]
    assert "No mail address for person.anna" in caplog.text


async def test_the_global_address_is_a_recipient_of_its_own(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    entry.runtime_data.options["mail_global_address"] = "house@example.com"
    await mail(hass, entry, "Global address", title="Alarm")
    (call,) = mailbox
    assert call.data["target"] == ["house@example.com"]
    assert call.data["title"] == "Critical: Alarm"


async def test_the_global_address_without_a_setting_is_skipped(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    result = await mail(hass, entry, "Global address")
    assert result["channels"]["mail"]["skipped"] == 1 and mailbox == []


async def test_no_service_chosen_is_a_failure(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    entry.runtime_data.options["mail_service"] = ""
    opt_in(hass, entry, "person.anna", "anna@example.com")
    events = async_capture_events(hass, EVENT)
    await mail(hass, entry, "person.anna")
    assert entry.runtime_data.hub.trace.entries("m")[0]["reason"] == "no_mail_service"
    assert [f["reason"] for f in events[0].data["failed"]] == ["no_mail_service"]


async def test_a_missing_service_and_a_failing_service_are_failures(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    entry.runtime_data.options["mail_service"] = "gone"
    await mail(hass, entry, "person.anna", id="a")
    assert entry.runtime_data.hub.trace.entries("a")[0]["reason"] == "service_not_found"

    async def broken(call: ServiceCall) -> None:
        raise HomeAssistantError("smtp down")

    hass.services.async_register("notify", "broken", broken)
    entry.runtime_data.options["mail_service"] = "broken"
    await mail(hass, entry, "person.anna", id="b")
    assert entry.runtime_data.hub.trace.entries("b")[0]["reason"] == "send_failed"


async def test_an_update_does_not_send_the_mail_again(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    await mail(hass, entry, "person.anna")
    second = await mail(hass, entry, "person.anna", message="Door still open")
    assert len(mailbox) == 1
    assert second["channels"]["mail"]["skipped"] == 1
    assert [r["reason"] for r in second["reasons"]] == ["already_sent"]


async def test_clearing_the_message_takes_nothing_back(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    await mail(hass, entry, "person.anna")
    await hass.services.async_call(DOMAIN, "clear_notifications", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert len(mailbox) == 1


async def test_an_audience_reaches_the_persons_who_opted_in(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "m",
            "message": "x",
            "channels": ["mail"],
            "to": {"mail": {"audience": "Everyone"}},
        },
        blocking=True,
    )
    await settle(hass, entry)
    assert [c.data["target"] for c in mailbox] == [["anna@example.com"]]


async def test_a_call_naming_mail_needs_a_target(
    hass: HomeAssistant, entry: MockConfigEntry, mailbox: list[ServiceCall]
) -> None:
    with pytest.raises(Exception, match="mail needs a target"):
        await hass.services.async_call(
            DOMAIN, "notify", {"message": "x", "channels": ["mail"]}, blocking=True
        )


async def test_an_escalation_can_add_mail(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    freezer: FrozenDateTimeFactory,
) -> None:
    opt_in(hass, entry, "person.ben", "ben@example.com")
    await add_policy(
        hass,
        entry,
        "Mail later",
        type="escalation",
        after_minutes=5,
        channels=["mail"],
        targets={"mail": {"recipients": ["person.ben"]}},
    )
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "m", "message": "Leak", "severity": "critical", "channels": ["banner"]},
        blocking=True,
    )
    await settle(hass, entry)
    assert mailbox == []
    await wait(hass, entry, freezer, 5.1)
    assert [c.data["target"] for c in mailbox] == [["ben@example.com"]]


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def test_the_channels_page_saves_valid_mail_settings(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "channels_set",
        mail_service="smtp_house",
        mail_global_address="house@example.com",
        mail_subject="{person}",
        mail_body="{message} ({severity})",
    )
    assert reply["success"], reply
    assert entry.options["mail_service"] == "smtp_house"
    assert entry.options["mail_subject"] == "{person}"
    config = (await ask(client, "panel_config"))["result"]
    assert "smtp_house" in config["choices"]["notify_services"]
    assert config["channels"]["mail_global_address"] == "house@example.com"


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"mail_service": "nope"}, "mail_service"),
        ({"mail_subject": "{nothing}"}, "mail_subject"),
        ({"mail_subject": " "}, "mail_subject"),
        ({"mail_subject": "x" * 201}, "mail_subject"),
        ({"mail_body": "{message} {who}"}, "mail_body"),
        ({"mail_body": "x" * 2001}, "mail_body"),
        ({"mail_global_address": "a" * 255}, "mail_global_address"),
    ],
)
async def test_the_channels_page_refuses_bad_mail_settings(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
    changes: dict[str, str],
    field: str,
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "channels_set", **changes)
    assert reply["error"]["code"] == "invalid_format"
    assert field in reply["error"]["message"]


async def test_the_dry_run_shows_the_mail_rows_and_sends_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "hub_plan",
        message="x",
        channels=["mail"],
        to={"mail": {"recipients": ["person.anna", "person.ben"]}},
    )
    assert reply["success"], reply
    rows = {(r["recipient"], r["result"]): r.get("reason") for r in reply["result"]["rows"]}
    assert rows[("person.anna", "sent")] is None
    assert rows[("person.ben", "skipped")] == "channel_not_accepted"
    assert mailbox == []


async def test_the_preview_names_the_address_and_flags_a_missing_one(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    set_person(hass, "person.cy", "home", user_id="cy-id")
    opt_in(hass, entry, "person.anna", "anna@example.com")
    opt_in(hass, entry, "person.cy")  # Mail on, no address
    entry.runtime_data.options["mail_global_address"] = "house@example.com"
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "hub_plan",
        message="x",
        channels=["mail"],
        to={"mail": {"recipients": ["person.anna", "person.cy", "Global address"]}},
    )
    rows = {r["recipient"]: r for r in reply["result"]["rows"]}
    assert rows["person.anna"]["address"] == "anna@example.com"
    assert rows["person.anna"]["result"] == "sent"
    assert rows["mail:global"]["address"] == "house@example.com"
    # The plan already skips a person without an address; the preview adds no address for the row.
    assert (rows["person.cy"]["result"], rows["person.cy"]["reason"]) == (
        "skipped",
        "no_mail_address",
    )
    assert rows["person.cy"].get("address") is None
    assert mailbox == []


async def test_the_preview_flags_a_missing_mail_service(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mailbox: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    opt_in(hass, entry, "person.anna", "anna@example.com")
    entry.runtime_data.options["mail_service"] = ""
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "hub_plan",
        message="x",
        channels=["mail"],
        to={"mail": {"recipients": ["person.anna"]}},
    )
    (row,) = [r for r in reply["result"]["rows"] if r["channel"] == "mail"]
    assert (row["result"], row["reason"]) == ("failed", "no_mail_service")
