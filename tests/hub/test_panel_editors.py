"""The editors' data command and the channel settings command (D-119)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from ..test_rules import add_rule
from .conftest import AddDevice
from .helpers import FakeSpeakers, set_person
from .policy_support import ESCALATION, add_audience, add_policy, make_household


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def config(hass: HomeAssistant, client: Any) -> dict[str, Any]:
    reply = await ask(client, "panel_config")
    assert reply["success"], reply
    return dict(reply["result"])


async def test_both_commands_are_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "panel_config"))["error"]["code"] == "unauthorized"
    assert (await ask(client, "channels_set", push_sticky=True))["error"]["code"] == "unauthorized"


async def test_the_built_in_and_custom_audiences_come_with_their_members_and_users(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "not_home", user_id="ben-id")
    await add_audience(hass, entry, "Parents", kind="persons", persons=["person.anna"])
    policy = {**ESCALATION, "targets": {"push": {"audience": "Parents"}}}
    await add_policy(hass, entry, "Water", **policy)
    client = await hass_ws_client(hass)
    audiences = {a["name"]: a for a in (await config(hass, client))["audiences"]}
    assert audiences["At home"]["builtin"] is True and audiences["At home"]["members"] == [
        "person.anna"
    ]
    assert audiences["Not home"]["members"] == ["person.ben"]
    parents = audiences["Parents"]
    assert parents["builtin"] is False and parents["subentry_id"]
    assert parents["data"] == {"kind": "persons", "persons": ["person.anna"]}
    assert parents["members"] == ["person.anna"] and parents["used_by"] == ["Water"]
    assert audiences["Everyone"]["used_by"] == []


async def test_groups_list_their_speakers_the_call_name_and_the_policies_using_them(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    fake_speakers: FakeSpeakers,
) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"members": [fake_speakers.satellite, "media_player.gone"], "areas": []},
            subentry_type="recipient_group",
            title="Hall",
            unique_id=None,
        ),
    )
    uses = {
        **ESCALATION,
        "channels": ["speak"],
        "targets": {"speak": {"recipients": ["Hall (group)"]}},
    }
    await add_policy(hass, entry, "Spoken", **uses)
    client = await hass_ws_client(hass)
    (group,) = (await config(hass, client))["groups"]
    assert group["call_name"] == "Hall (group)" and group["speakers"] == [fake_speakers.satellite]
    assert group["used_by"] == ["Spoken"] and group["subentry_id"]


async def test_profiles_show_devices_badges_primary_and_what_was_changed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home")
    phone = await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={
                "person": "person.anna",
                "channels": ["banner", "push"],
                "primary": phone.device_id,
            },
            subentry_type="recipient_profile",
            title="anna",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    profiles = {p["person"]: p for p in (await config(hass, client))["profiles"]}
    anna = profiles["person.anna"]
    assert anna["customized"] is True and anna["primary"] == phone.device_id
    assert anna["channels"] == ["banner", "push"] and anna["subentry_id"]
    assert anna["devices"] == [
        {
            "device_id": phone.device_id,
            "name": "Anna's phone",
            "service_found": True,
            "source": "detected",
        }
    ]
    assert profiles["person.ben"]["devices"] == [] and profiles["person.ben"]["subentry_id"] is None
    assert profiles["person.ben"]["user"] is False


async def test_policies_come_with_their_stored_data(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(hass, entry, "Water", **ESCALATION)
    client = await hass_ws_client(hass)
    (policy,) = (await config(hass, client))["policies"]
    assert (
        policy["name"] == "Water" and policy["data"]["after_minutes"] == 5 and policy["subentry_id"]
    )


async def test_the_choices_list_what_a_form_can_pick(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    fake_speakers: FakeSpeakers,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    hass.states.async_set("zone.work", "0", {"friendly_name": "Work"})
    client = await hass_ws_client(hass)
    choices = (await config(hass, client))["choices"]
    assert {p["id"] for p in choices["persons"]} == {"person.anna", "person.ben"}
    assert {"id": "zone.work", "name": "Work"} in choices["zones"]
    assert fake_speakers.satellite in choices["speakers"]
    assert {r["name"] for r in choices["registrations"]} == {"Anna's phone", "Ben's phone"}
    assert "Admins" in choices["audience_names"] and "person.anna" in choices["recipients"]["push"]
    assert fake_speakers.announce_player in choices["recipients"]["speak"]


async def test_the_config_has_the_entry_id_and_the_channel_settings(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = await config(hass, client)
    assert result["entry_id"] == entry.entry_id and result["hub"] is True
    assert result["channels"] == {
        "push_levels": {
            "success": "passive",
            "info": "passive",
            "warning": "normal",
            "critical": "time-sensitive",
        },
        "popup_styles": {"success": "card", "info": "card", "warning": "card", "critical": "modal"},
        "push_lockscreen": "full",
        "push_sticky": False,
        "push_channel_id": "heads_up",
        "speak_language": "",
        "mail_service": "",
        "mail_global_address": "",
        "mail_subject": "{severity}: {title}",
        "mail_body": "{message}",
    }


async def test_with_the_hub_off_the_editors_have_no_hub_data(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "hub_enabled": False})
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    result = await config(hass, client)
    assert result["hub"] is False and result["audiences"] == [] and result["profiles"] == []


async def test_channel_settings_are_written_to_the_options_and_used(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    levels = {
        "success": "passive",
        "info": "normal",
        "warning": "time-sensitive",
        "critical": "critical",
    }
    reply = await ask(
        client,
        "channels_set",
        push_levels=levels,
        popup_styles={"info": "off", "critical": "modal"},
        push_lockscreen="title_only",
        push_sticky=True,
        push_channel_id="house_alerts",
        speak_language="de",
    )
    assert reply["success"]
    assert (
        entry.options["push_levels"] == levels and entry.options["push_lockscreen"] == "title_only"
    )
    assert (
        entry.options["push_sticky"] is True and entry.options["push_channel_id"] == "house_alerts"
    )
    popup = entry.runtime_data.hub.channels.get("popup")
    assert popup.styles()["info"] == "off" and popup.styles()["warning"] == "card"  # type: ignore[attr-defined]


async def test_invalid_channel_settings_are_refused_and_change_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    for bad in (
        {"push_levels": {"info": "loud"}},
        {"push_levels": {"urgent": "normal"}},
        {"popup_styles": {"info": "banner"}},
        {"push_lockscreen": "nothing"},
        {"push_channel_id": "Has Spaces"},
        {"push_channel_id": ""},
    ):
        reply = await ask(client, "channels_set", **bad)
        assert not reply["success"] and reply["error"]["code"] == "invalid_format", bad
    assert "push_lockscreen" not in entry.options and "push_channel_id" not in entry.options


async def test_rules_come_with_their_stored_data_and_whether_they_show_now(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.states.async_set("binary_sensor.door", "on")
    hass.states.async_set("binary_sensor.window", "off")
    showing = add_rule(hass, entry, entity_id="binary_sensor.door", state=["on"])
    idle = add_rule(hass, entry, entity_id="binary_sensor.window", state=["on"])
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    rules = {r["subentry_id"]: r for r in (await config(hass, client))["rules"]}
    assert rules[showing.subentry_id]["showing"] is True
    assert rules[idle.subentry_id]["showing"] is False
    assert rules[showing.subentry_id]["data"]["entity_id"] == "binary_sensor.door"
    assert rules[showing.subentry_id]["name"] == "Rule"
