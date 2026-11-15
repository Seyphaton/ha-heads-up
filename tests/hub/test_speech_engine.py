"""A speaker group with a media player needs a text-to-speech engine, or the panel warns."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub.panel_data import check_speech_engine


def kinds(found: list[Any]) -> list[str]:
    return [a.kind for a in found]


def test_no_speaker_means_no_warning() -> None:
    assert check_speech_engine(False, [], "") == []


def test_one_engine_is_used_by_itself() -> None:
    assert check_speech_engine(True, ["tts.cloud"], "") == []


def test_no_engine_is_reported() -> None:
    assert kinds(check_speech_engine(True, [], "")) == ["speech_engine_none"]


def test_several_engines_without_a_choice_are_reported_with_their_names() -> None:
    found = check_speech_engine(True, ["tts.a", "tts.b"], "")
    assert kinds(found) == ["speech_engine_choose"]
    assert found[0].subject == "tts.a, tts.b"
    assert found[0].page == "general"


def test_a_chosen_engine_that_exists_is_fine_and_one_that_is_gone_is_reported() -> None:
    assert check_speech_engine(True, ["tts.a", "tts.b"], "tts.a") == []
    assert kinds(check_speech_engine(True, ["tts.a"], "tts.gone")) == ["speech_engine_missing"]


async def test_the_welcome_stores_the_chosen_engine(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.states.async_set("tts.cloud", "unknown")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/welcome_get"})
    assert (await client.receive_json())["result"]["tts_engines"] == ["tts.cloud"]
    await client.send_json_auto_id(
        {"type": "heads_up/welcome_apply", "items": [], "tts_engine": "tts.missing"}
    )
    assert (await client.receive_json())["error"]["code"] == "unknown_tts_engine"
    await client.send_json_auto_id(
        {"type": "heads_up/welcome_apply", "items": [], "tts_engine": "tts.cloud"}
    )
    assert (await client.receive_json())["success"] is True
    assert entry.options["speak_tts_entity"] == "tts.cloud"
