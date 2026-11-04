"""Popup channel: a ledger row per person, a subscription per user, and the config command."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import set_person, settle, tick
from .policy_support import ESCALATION, QUIET, REMINDER, add_policy, make_household, move, wait

ANNA = {"popup": {"recipients": ["person.anna"]}}


async def pop(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> dict[str, Any]:
    body = {"id": "m", "message": "Door open", "channels": ["popup"], "to": ANNA, **data}
    result = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert result is not None
    return dict(result)


def popups(entry: MockConfigEntry, user: str = "anna-id") -> list[dict[str, Any]]:
    return entry.runtime_data.hub.channels.get("popup").messages_for(user)  # type: ignore[no-any-return]


def ids(entry: MockConfigEntry, user: str = "anna-id") -> list[str]:
    return [p["id"] for p in popups(entry, user)]


async def test_a_person_with_a_user_gets_the_popup_and_nobody_else(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home", user_id="ben-id")
    result = await pop(hass, entry)
    assert result["channels"]["popup"]["sent"] == 1
    assert ids(entry) == ["m"] and ids(entry, "ben-id") == []


async def test_the_payload_has_the_message_the_style_and_the_buttons(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await pop(
        hass,
        entry,
        title="Door",
        severity="critical",
        snoozable=True,
        snooze_options=[{"minutes": 10}],
        actions=[{"key": "seen", "label": "Seen"}],
    )
    (payload,) = popups(entry)
    assert payload["title"] == "Door" and payload["message"] == "Door open"
    assert payload["style"] == "modal" and payload["snoozable"] is True
    assert payload["actions"][0]["key"] == "seen" and payload["ack"] is False
    assert "dismissed_by" not in payload and "targets" not in payload


async def test_the_style_follows_the_severity(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    for severity in ("info", "warning", "critical"):
        await pop(hass, entry, id=severity, severity=severity)
    styles = {p["id"]: p["style"] for p in popups(entry)}
    assert styles == {"info": "card", "warning": "card", "critical": "modal"}


async def test_a_severity_set_to_off_shows_no_popup(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    entry.runtime_data.options["popup_styles"] = {"info": "off"}
    await pop(hass, entry, severity="info")
    assert ids(entry) == []


async def test_a_person_without_a_user_is_skipped_at_delivery(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await pop(hass, entry)
    trace = entry.runtime_data.hub.trace.entries("m")
    assert any(e["reason"] == "no_user" for e in trace)


async def test_dismissing_removes_it_for_that_user_only(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home", user_id="ben-id")
    both = {"popup": {"recipients": ["person.anna", "person.ben"]}}
    await pop(hass, entry, to=both)
    entry.runtime_data.dismiss("m", "anna-id")
    await settle(hass, entry)
    assert ids(entry) == [] and ids(entry, "ben-id") == ["m"]


async def test_a_snooze_hides_it_and_its_end_shows_it_again(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await pop(hass, entry, snoozable=True, snooze_options=[{"minutes": 10}])
    entry.runtime_data.snooze("m", "anna-id", 600)
    await settle(hass, entry)
    assert ids(entry) == []
    await tick(hass, freezer, 601)
    await settle(hass, entry)
    assert ids(entry) == ["m"]


async def test_it_goes_when_the_message_ends(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await pop(hass, entry)
    await hass.services.async_call(DOMAIN, "clear", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert ids(entry) == []


async def test_an_update_changes_the_text(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await pop(hass, entry)
    await pop(hass, entry, message="Door still open")
    (payload,) = popups(entry)
    assert payload["message"] == "Door still open"


async def test_a_quiet_popup_is_a_card_even_when_critical(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to("2026-11-02 23:00:00+01:00")
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await add_policy(hass, entry, "Night", **{**QUIET, "critical_passes": False})
    await pop(hass, entry, severity="critical")
    assert popups(entry)[0]["style"] == "card"


async def test_the_acknowledge_button_is_offered_when_a_policy_applies(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await add_policy(hass, entry, "Nag", **REMINDER)
    await pop(hass, entry)
    assert popups(entry)[0]["ack"] is True


async def test_the_popup_survives_a_restart(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await pop(hass, entry)
    await restart(hass, entry)
    await settle(hass, entry)
    assert ids(entry) == ["m"]


async def test_an_audience_of_people_at_home_pops_up_only_for_them(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "not_home", user_id="ben-id")
    await pop(hass, entry, to={"popup": {"audience": "At home"}})
    assert ids(entry) == ["m"] and ids(entry, "ben-id") == []


async def test_a_rule_message_pops_up_through_an_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    from ..test_rules import WINDOW, add_rule

    await make_household(hass, mobile_app_device)
    policy = {
        **ESCALATION,
        "channels": ["popup"],
        "targets": {"popup": {"recipients": ["person.ben"]}},
        "tags": ["rule"],
    }
    await add_policy(hass, entry, "Rules", **policy)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    assert ids(entry, "ben-id") == []
    await wait(hass, entry, freezer, 6)
    assert len(ids(entry, "ben-id")) == 1
    move(hass, "person.ben", "home")


async def test_the_config_says_how_each_severity_looks_and_where_the_module_is(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/popup_config"})
    result = (await client.receive_json())["result"]
    assert result["enabled"] is True
    assert result["styles"]["critical"] == "modal" and result["styles"]["info"] == "card"
    assert result["module"].startswith("/heads_up/heads-up-popup.js?v=")


async def test_a_user_gets_the_list_now_and_again_when_it_changes(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    set_person(hass, "person.anna", "home", user_id=hass_admin_user.id)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/popup_subscribe"})
    assert (await client.receive_json())["success"]
    first = await client.receive_json()
    assert first["event"] == {"messages": []}
    await pop(hass, entry)
    await hass.async_block_till_done()
    event = await client.receive_json()
    assert [m["id"] for m in event["event"]["messages"]] == ["m"]
    entry.runtime_data.dismiss("m", hass_admin_user.id)
    await settle(hass, entry)
    assert (await client.receive_json())["event"] == {"messages": []}
