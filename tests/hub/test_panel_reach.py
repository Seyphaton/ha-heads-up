"""The table "What would a message do right now?": every cell from the real engine (plan 18.2)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import AddDevice
from .helpers import FakeSpeakers, set_person
from .policy_support import QUIET, SUMMARIZE, add_policy, make_household


async def table(client: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/panel_reach"})
    reply = await client.receive_json()
    assert reply["success"], reply
    return dict(reply["result"])


def cell(result: dict[str, Any], channel: str, severity: str) -> dict[str, Any]:
    return dict(result["cells"][channel][severity])


async def test_the_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "heads_up/panel_reach"})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"


async def test_the_table_has_six_channels_and_four_severities_most_urgent_first(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    result = await table(client)
    assert result["severities"] == ["critical", "warning", "info", "passive"]
    assert result["channels"] == ["banner", "push", "popup", "speak", "persistent", "mail"]
    assert all(len(result["cells"][c]) == 4 for c in result["channels"])
    banner = cell(result, "banner", "info")
    assert banner["state"] == "shown" and banner["total"] == 1
    push = cell(result, "push", "info")
    assert push["state"] == "shown" and push["count"] == push["total"] == 2
    assert sorted(w["name"] for w in push["who"]) == ["person.anna", "person.ben"]


async def test_a_push_is_sound_only_when_its_level_is_critical(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    entry.runtime_data.options["push_levels"] = {"critical": "critical", "warning": "normal"}
    client = await hass_ws_client(hass)
    result = await table(client)
    assert cell(result, "push", "critical")["state"] == "sound"
    assert cell(result, "push", "warning")["state"] == "shown"
    entry.runtime_data.options["push_levels"] = {"critical": "time-sensitive"}
    assert cell(await table(client), "push", "critical")["state"] == "shown"


async def test_quiet_hours_quiet_wait_and_drop_each_show_what_the_engine_does(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)  # before the clock moves: tokens expire in frozen time
    await make_household(hass, mobile_app_device)
    night = await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    result = await table(client)
    assert cell(result, "banner", "warning")["state"] == "shown"  # quiet hours never hide it
    assert cell(result, "push", "warning")["state"] == "quiet"
    assert cell(result, "popup", "warning")["state"] == "quiet"
    assert result["context"]["quiet"]["policies"] == ["Night"]
    until = dt_util.parse_datetime(result["context"]["quiet"]["until"])
    assert until == dt_util.parse_datetime("2026-11-03T07:00:00+01:00")
    for action, expected in (("wait", "held"), ("drop", "skipped")):
        hass.config_entries.async_update_subentry(
            entry, night, data={**night.data, "action": action}
        )
        await hass.async_block_till_done()
        cells = await table(client)
        assert cell(cells, "push", "warning")["state"] == expected
        assert cell(cells, "mail", "warning")["state"] != "quiet"
    freezer.move_to("2026-11-03 12:00:00+01:00")
    outside = await table(client)
    assert cell(outside, "push", "warning")["state"] == "shown"
    assert outside["context"]["quiet"] is None


async def test_a_band_entry_that_covers_only_some_people_gives_a_count(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    client = await hass_ws_client(hass)
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    await add_policy(
        hass,
        entry,
        "Anna wakes",
        type="get_through",
        severities=["critical"],
        covers="only",
        covers_recipients=["person.anna"],
    )
    freezer.move_to("2026-11-02 23:00:00+01:00")
    push = cell(await table(client), "push", "critical")
    assert (push["count"], push["total"]) == (1, 2)
    assert push["counts"] == {"shown": 1, "held": 1}
    by_name = {w["name"]: w["state"] for w in push["who"]}
    assert by_name == {"person.anna": "shown", "person.ben": "held"}
    assert next(w for w in push["who"] if w["name"] == "person.ben")["until"]


async def test_popup_off_a_person_without_a_user_and_a_person_without_a_device(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.cleo", "home")  # no user, no device
    entry.runtime_data.options["popup_styles"] = {"passive": "off"}
    client = await hass_ws_client(hass)
    result = await table(client)
    passive = cell(result, "popup", "passive")
    assert passive["state"] == "not_set_up" and passive["reason"] == "popup_off"
    popup = cell(result, "popup", "info")
    assert (popup["state"], popup["count"], popup["total"]) == ("shown", 2, 3)
    assert {w["name"]: w["reason"] for w in popup["who"] if w["state"] == "skipped"} == {
        "person.cleo": "no_user"
    }
    push = cell(result, "push", "info")
    assert (push["count"], push["total"]) == (2, 3)
    assert {w["name"]: w["reason"] for w in push["who"] if w["state"] == "skipped"} == {
        "person.cleo": "no_usable_device"
    }


async def test_a_disabled_recipient_is_skipped_with_its_reason(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": "person.ben", "enabled": False},
            subentry_type="recipient_profile",
            title="Ben",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    push = cell(await table(client), "push", "info")
    assert {w["name"]: w["reason"] for w in push["who"] if w["state"] == "skipped"} == {
        "person.ben": "recipient_disabled"
    }


async def test_mail_is_not_set_up_without_a_service_and_counts_addresses_with_one(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    assert cell(await table(client), "mail", "info")["state"] == "not_set_up"
    entry.runtime_data.options["mail_service"] = "smtp_house"
    for who, address in (("person.anna", "anna@example.com"), ("person.ben", "")):
        hass.config_entries.async_add_subentry(
            entry,
            ConfigSubentry(
                data={"person": who, "mail_address": address, "channels": ["banner", "mail"]},
                subentry_type="recipient_profile",
                title=who,
                unique_id=None,
            ),
        )
    await hass.async_block_till_done()
    mail = cell(await table(client), "mail", "info")
    assert mail["state"] != "not_set_up" and mail["total"] >= 1
    assert any(w["state"] == "skipped" and w["reason"] == "no_mail_address" for w in mail["who"])


async def test_speech_without_a_speaker_is_not_set_up(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    assert cell(await table(client), "speak", "critical")["state"] == "not_set_up"


async def test_speech_is_sound_with_speakers_and_needs_an_engine_for_players(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
    fake_speakers: FakeSpeakers,
) -> None:
    await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    speech = cell(await table(client), "speak", "critical")
    assert speech["state"] == "sound" and speech["total"] == 3  # two players and a satellite
    hass.states.async_set("tts.second", "unknown")
    again = cell(await table(client), "speak", "critical")
    # Two engines and none chosen: the players cannot speak, the satellite still can.
    assert again["counts"] == {"sound": 1, "not_set_up": 2}
    assert {w["reason"] for w in again["who"] if w["state"] == "not_set_up"} == {"no_tts_engine"}


async def test_a_summary_holds_a_message_with_its_tag_only_and_is_listed_in_the_context(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    client = await hass_ws_client(hass)
    result = await table(client)
    # The dry-run message has no tag, so the summary does not apply to it.
    assert cell(result, "push", "warning")["state"] == "shown"
    (summary,) = result["context"]["summaries"]
    assert summary["policy"] == "Digest" and summary["tags"] == ["digest"] and summary["due"]


async def test_who_is_away_is_named_in_the_context(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.ben", "not_home", user_id="ben-id")
    client = await hass_ws_client(hass)
    assert (await table(client))["context"]["away"] == ["person.ben"]


async def test_a_cell_says_how_the_people_who_are_reached_get_it_not_what_most_people_miss(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    await make_household(hass, mobile_app_device)  # Anna and Ben have phones
    set_person(hass, "person.cleo", "home")
    set_person(hass, "person.dan", "home")
    entry.runtime_data.options["mail_service"] = "smtp_house"
    for who, address in (("person.anna", "anna@example.com"),):
        hass.config_entries.async_add_subentry(
            entry,
            ConfigSubentry(
                data={"person": who, "mail_address": address, "channels": ["banner", "mail"]},
                subentry_type="recipient_profile",
                title=who,
                unique_id=None,
            ),
        )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    mail = cell(await table(client), "mail", "critical")
    assert mail["total"] == 4 and mail["counts"] == {"shown": 1, "skipped": 3}
    assert (mail["state"], mail["count"]) == ("shown", 1)  # Anna gets it; three others do not
