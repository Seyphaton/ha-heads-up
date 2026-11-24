"""The speech and push settings live on the Channels page, not on the Settings page (D-276)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub import settings

MOVED = (
    "speak_max_length",
    "speak_cooldown_seconds",
    "speak_tts_entity",
    "speak_restore_volume",
    "speak_severity_volume",
    "speak_volume_bands",
    "rate_per_device_per_minute",
    "rate_total_per_minute",
)


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def test_they_are_channel_settings_with_their_defaults(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    channels = (await ask(client, "panel_config"))["result"]["channels"]
    assert {key: channels[key] for key in MOVED} == {
        "speak_max_length": 200,
        "speak_cooldown_seconds": 60,
        "speak_tts_entity": "",
        "speak_restore_volume": True,
        "speak_severity_volume": {},
        "speak_volume_bands": [],
        "rate_per_device_per_minute": 5,
        "rate_total_per_minute": 60,
    }


async def test_they_are_not_on_the_settings_page_or_the_options_screen(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_get"))["result"]
    assert not set(MOVED) & set(result["options"])
    assert "speech" not in [s["name"] for s in result["layout"]]
    assert "speech_volume" not in [s["name"] for s in result["layout"]]
    assert not set(MOVED) & {key for _, items in settings.SECTIONS for key, _ in items}
    for key in MOVED:
        reply = await ask(client, "settings_set", **{key: 5})
        assert not reply["success"] and reply["error"]["code"] == "invalid_format", key


async def test_the_numbers_have_their_ranges(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    ranges = {
        "speak_max_length": (20, 1000),
        "speak_cooldown_seconds": (0, 3600),
        "rate_per_device_per_minute": (1, 600),
        "rate_total_per_minute": (1, 6000),
    }
    for key, (low, high) in ranges.items():
        for good in (low, high):
            assert (await ask(client, "channels_set", **{key: good}))["success"], (key, good)
            assert entry.options[key] == good
        for bad in (low - 1, high + 1):
            reply = await ask(client, "channels_set", **{key: bad})
            assert not reply["success"] and reply["error"]["code"] == "invalid_format", (key, bad)


async def test_the_engine_is_a_tts_entity_or_empty(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "channels_set", speak_tts_entity="tts.home"))["success"]
    assert entry.options["speak_tts_entity"] == "tts.home"
    assert (await ask(client, "channels_set", speak_tts_entity=""))["success"]
    reply = await ask(client, "channels_set", speak_tts_entity="media_player.kitchen")
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"


async def test_the_push_limits_apply_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "channels_set", rate_per_device_per_minute=2))["success"]
    await hass.async_block_till_done()
    assert entry.runtime_data.options["rate_per_device_per_minute"] == 2


async def test_they_are_for_administrators_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    reply = await ask(client, "channels_set", speak_max_length=100)
    assert reply["error"]["code"] == "unauthorized"


async def test_volume_bands_and_severity_volumes_are_set_and_checked(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    bands = [
        {"from": "22:00", "to": "07:00", "volume": 20},
        {"from": "7:00", "to": "9:30", "volume": 45},
    ]
    reply = await ask(
        client,
        "channels_set",
        speak_volume_bands=bands,
        speak_severity_volume={"critical": 90, "info": None},
        speak_restore_volume=False,
    )
    assert reply["success"], reply
    assert entry.options["speak_volume_bands"][1] == {"from": "07:00", "to": "09:30", "volume": 45}
    assert entry.options["speak_severity_volume"] == {"critical": 90}
    assert entry.options["speak_restore_volume"] is False
    for bad in (
        {"speak_volume_bands": [{"from": "08:00", "to": "08:00", "volume": 10}]},
        {"speak_volume_bands": [{"from": "25:00", "to": "08:00", "volume": 10}]},
        {"speak_volume_bands": [{"from": "08:00", "to": "09:00", "volume": 101}]},
        {
            "speak_volume_bands": [
                {"from": f"0{i}:00", "to": f"0{i}:30", "volume": 5} for i in range(5)
            ]
        },
        {"speak_volume_bands": [*bands, {"from": "23:00", "to": "23:30", "volume": 5}]},
        {"speak_severity_volume": {"urgent": 50}},
        {"speak_severity_volume": {"critical": 150}},
    ):
        reply = await ask(client, "channels_set", **bad)
        assert not reply["success"], bad
