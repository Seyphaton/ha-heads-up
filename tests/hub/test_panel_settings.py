"""Settings commands: admin only, read, write, presets (D-117)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import AddDevice
from .helpers import set_person


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


def policies(entry: MockConfigEntry) -> dict[str, dict[str, Any]]:
    return {s.title: dict(s.data) for s in entry.subentries.values() if s.subentry_type == "policy"}


async def test_every_settings_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    for command, data in (
        ("settings_get", {}),
        ("settings_set", {"show_panel": True}),
    ):
        assert (await ask(client, command, **data))["error"]["code"] == "unauthorized"
    assert not policies(entry)


async def test_get_returns_every_option_the_layout_and_the_token(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_get"))["result"]
    assert result["options"] == {
        "show_panel": False,
        "max_banners": 50,
        "evict": True,
        "default_dismiss_scope": "user",
        "default_timeout": 86400,
        "default_snoozable": False,
        "default_snooze_scope": "user",
        "default_snooze_options": [15, 60, 240],
        "quick_snooze_minutes": 15,
        "disable_ended_buttons": True,
        "presence_debounce_seconds": 60,
        "speak_max_length": 200,
        "speak_cooldown_seconds": 60,
        "speak_tts_entity": "",
        "rate_per_device_per_minute": 5,
        "rate_total_per_minute": 60,
        "dedupe_seconds": 30,
        "trace_entries": 500,
        "recent_messages": 100,
    }
    assert [s["name"] for s in result["layout"]] == [
        "sidebar",
        "dismiss",
        "snooze",
        "snooze_banner",
        "snooze_push",
        "presence",
        "speech",
        "limits",
        "history",
    ]
    trace = next(e for s in result["layout"] for e in s["entries"] if e["key"] == "trace_entries")
    assert trace == {"key": "trace_entries", "kind": "int", "range": [50, 5000]}
    assert result["install_token"] == entry.options["install_token"]


async def test_the_banner_defaults_and_speech_settings_are_set_in_panel_units(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "settings_set",
        max_banners=10,
        evict=False,
        default_dismiss_scope="global",
        default_timeout=3600,
        default_snooze_options=[30, 5],
        speak_tts_entity="tts.home",
        presence_debounce_seconds=0,
    )
    assert reply["success"]
    assert reply["result"]["options"]["default_snooze_options"] == [5, 30]  # minutes, sorted
    assert entry.options["default_snooze_options"] == [300, 1800]  # stored in seconds
    assert entry.options["default_timeout"] == 3600 and entry.options["max_banners"] == 10
    assert entry.options["speak_tts_entity"] == "tts.home"
    assert entry.runtime_data.options["max_banners"] == 10  # applied live


async def test_an_empty_snooze_choice_falls_back_to_the_defaults(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "settings_set", default_snooze_options=[])
    assert entry.options["default_snooze_options"] == [900, 3600, 14400]


async def test_values_the_options_screen_would_refuse_are_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    for bad in (
        {"max_banners": 0},
        {"default_dismiss_scope": "nobody"},
        {"default_timeout": 366 * 86400},
        {"default_snooze_options": [7]},
        {"speak_tts_entity": "media_player.kitchen"},
        {"speak_max_length": 10},
    ):
        reply = await ask(client, "settings_set", **bad)
        assert not reply["success"] and reply["error"]["code"] == "invalid_format", bad


async def test_set_writes_the_integration_options_and_keeps_the_others(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_set", show_panel=True, trace_entries=800)
    assert reply["success"] and reply["result"]["options"]["trace_entries"] == 800
    assert entry.options["show_panel"] is True and entry.options["trace_entries"] == 800
    assert entry.options["install_token"]
    assert entry.runtime_data.hub.trace.entries("x") == []  # the trace buffer was resized live


async def test_a_value_outside_its_range_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_set", trace_entries=10)
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"
    assert entry.options.get("trace_entries", 500) == 500


async def test_the_hub_cannot_be_switched_off_from_settings(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_set", hub_enabled=False)
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"
    await hass.async_block_till_done()
    assert entry.runtime_data.hub is not None


async def test_the_people_summary_counts_usable_devices_and_users(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home")
    await mobile_app_device("Anna's phone", user_id="anna-id", person_entity_id="person.anna")
    client = await hass_ws_client(hass)
    people = {p["person"]: p for p in (await ask(client, "settings_get"))["result"]["people"]}
    assert people["person.anna"]["devices"] == 1 and people["person.anna"]["user"] is True
    assert people["person.ben"]["devices_total"] == 0 and people["person.ben"]["user"] is False


def test_strings_json_lists_the_sections_and_entries_of_the_layout_in_order() -> None:
    import json
    from pathlib import Path

    from custom_components.heads_up.hub import settings

    strings = json.loads(
        (Path(settings.__file__).parents[1] / "strings.json").read_text(encoding="utf-8")
    )
    sections = strings["options"]["step"]["init"]["sections"]
    assert list(sections) == [name for name, _ in settings.SECTIONS]
    for name, items in settings.SECTIONS:
        assert list(sections[name]["data"]) == [key for key, _ in items], name
        assert list(sections[name]["data_description"]) == [key for key, _ in items], name
