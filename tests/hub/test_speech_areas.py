"""Speech to any area by id or name, and the bell entry when nobody can speak (D-126)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.channels import speak
from custom_components.heads_up.hub.channels.persistent import warn_speech

from .helpers import FakeSpeakers, capture_persistent, settle
from .test_recipients_groups import add_group


@pytest.fixture(autouse=True)
def fake_media_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(speak, "media_source_id", lambda hass, text, engine, lang: f"tts://{text}")


def kitchen(hass: HomeAssistant, speakers: FakeSpeakers) -> str:
    """An area named Kitchen with the announce player assigned to it; returns the area id."""
    area = ar.async_get(hass).async_create("Kitchen")
    registry = er.async_get(hass)
    hass.states.async_remove(speakers.announce_player)
    entity = registry.async_get_or_create(
        "media_player", "fake", "kitchen", suggested_object_id="kitchen"
    )
    hass.states.async_set(entity.entity_id, "idle", {"supported_features": 1 << 12})
    registry.async_update_entity(entity.entity_id, area_id=area.id)
    return area.id


async def say(hass: HomeAssistant, entry: MockConfigEntry, *names: str) -> dict[str, Any]:
    result = await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "m",
            "message": "Water leak",
            "channels": ["speak"],
            "to": {"speak": {"recipients": list(names)}},
        },
        blocking=True,
        return_response=True,
    )
    await settle(hass, entry)
    assert result is not None
    return dict(result)


async def test_an_area_without_a_group_is_accepted_by_id(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    area_id = kitchen(hass, fake_speakers)
    result = await say(hass, entry, area_id)
    assert result["channels"]["speak"]["sent"] == 1


@pytest.mark.parametrize("written", ["Kitchen", "kitchen", "KITCHEN"])
async def test_an_area_is_accepted_by_name_in_any_case(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers, written: str
) -> None:
    kitchen(hass, fake_speakers)
    result = await say(hass, entry, written)
    assert result["channels"]["speak"]["sent"] == 1


async def test_an_unknown_area_fails_the_call_with_the_valid_names(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    kitchen(hass, fake_speakers)
    with pytest.raises(ServiceValidationError) as err:
        await say(hass, entry, "Attic")
    assert err.value.translation_key == "unknown_recipient"


async def test_an_area_without_a_speaker_leaves_one_bell_entry_without_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    bell = capture_persistent(hass)
    area = ar.async_get(hass).async_create("Garage")
    result = await say(hass, entry, area.id)
    assert result["channels"]["speak"]["skipped"] == 1
    (created,) = bell.create
    assert created.data["notification_id"] == "heads_up_warning_garage"
    assert "Garage" in created.data["message"]
    assert "Water leak" not in created.data["message"] and "Water leak" not in created.data["title"]


async def test_a_repeat_uses_the_same_entry_id_so_it_replaces(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    bell = capture_persistent(hass)
    area = ar.async_get(hass).async_create("Garage")
    await say(hass, entry, area.id)
    await say(hass, entry, "Garage")
    assert [c.data["notification_id"] for c in bell.create] == ["heads_up_warning_garage"] * 2


async def test_a_group_that_resolves_to_nothing_leaves_a_bell_entry(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    bell = capture_persistent(hass)
    add_group(hass, entry, "Nobody", members=["media_player.gone"], areas=[])
    await hass.async_block_till_done()
    await say(hass, entry, "Nobody (group)")
    (created,) = bell.create
    assert created.data["notification_id"] == "heads_up_warning_nobody_group"


async def test_a_missing_speaker_entity_leaves_a_bell_entry(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    bell = capture_persistent(hass)
    await warn_speech(hass, "media_player.gone", "entity_missing")
    (created,) = bell.create
    assert created.data["notification_id"] == "heads_up_warning_media_player_gone"
    assert "media_player.gone" in created.data["message"]


async def test_a_working_speaker_leaves_no_bell_entry(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    bell = capture_persistent(hass)
    await say(hass, entry, fake_speakers.satellite)
    assert bell.create == []


async def test_the_dry_run_does_not_touch_the_bell(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    hass_ws_client: WebSocketGenerator,
) -> None:
    bell = capture_persistent(hass)
    area = ar.async_get(hass).async_create("Garage")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {
            "type": "heads_up/hub_plan",
            "message": "Water leak",
            "severity": "info",
            "channels": ["speak"],
            "to": {"speak": {"recipients": [area.id]}},
        }
    )
    assert (await client.receive_json())["success"]
    assert bell.create == []
