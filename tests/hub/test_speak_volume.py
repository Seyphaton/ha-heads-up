"""Speech volume: time bands, severity volume, Sonos clip volume and putting it back (D-217)."""

from datetime import datetime
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.channels import speak
from custom_components.heads_up.hub.channels.speak import (
    band_volume,
    resolve_volume,
    speech_seconds,
)
from custom_components.heads_up.models import Banner

from .helpers import FakeSpeakers, settle, tick

NIGHT = [
    {"from": "22:00", "to": "07:00", "volume": 20},
    {"from": "07:00", "to": "12:00", "volume": 50},
]


@pytest.fixture(autouse=True)
def fake_media_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(speak, "media_source_id", lambda hass, text, engine, lang: f"tts://{text}")


@pytest.fixture
def levels(hass: HomeAssistant, fake_speakers: FakeSpeakers) -> list[tuple[str, float]]:
    """`volume_set` that changes the player's state like a real one, and records the calls."""
    calls: list[tuple[str, float]] = []

    async def handle(call: ServiceCall) -> None:
        entity, level = call.data["entity_id"], call.data["volume_level"]
        calls.append((entity, level))
        state = hass.states.get(entity)
        assert state is not None
        hass.states.async_set(entity, state.state, {**state.attributes, "volume_level": level})

    hass.services.async_register("media_player", "volume_set", handle)
    for entity in (fake_speakers.plain_player, fake_speakers.announce_player):
        state = hass.states.get(entity)
        assert state is not None
        hass.states.async_set(entity, "idle", {**state.attributes, "volume_level": 0.7})
    return calls


async def say(hass: HomeAssistant, entry: MockConfigEntry, *speakers: str, **data: Any) -> None:
    body = {
        "id": data.pop("id", "m"),
        "message": data.pop("message", "Water leak"),
        "channels": ["speak"],
        "to": {"speak": {"recipients": list(speakers)}},
        **data,
    }
    await hass.services.async_call(DOMAIN, "notify", body, blocking=True, return_response=True)
    await settle(hass, entry)


def message(**fields: Any) -> Banner:
    now = datetime(2026, 11, 18, 12, 0)
    base: dict[str, Any] = {
        "id": "m",
        "message": "x",
        "severity": "info",
        "dismissible": True,
        "dismiss_scope": "user",
        "created_at": now,
        "updated_at": now,
    }
    return Banner(**{**base, **fields})


def test_a_band_over_midnight_and_an_empty_band() -> None:
    assert band_volume(NIGHT, datetime(2026, 11, 18, 23, 30)) == 0.2
    assert band_volume(NIGHT, datetime(2026, 11, 18, 6, 59)) == 0.2
    assert band_volume(NIGHT, datetime(2026, 11, 18, 7, 0)) == 0.5
    assert band_volume(NIGHT, datetime(2026, 11, 18, 15, 0)) is None
    assert (
        band_volume([{"from": "08:00", "to": "08:00", "volume": 10}], datetime(2026, 1, 1, 8))
        is None
    )


def test_the_call_beats_the_severity_which_beats_the_band() -> None:
    options = {"speak_volume_bands": NIGHT, "speak_severity_volume": {"critical": 80}}
    night = datetime(2026, 11, 18, 23, 0)
    assert resolve_volume(message(severity="info"), options, night) == 0.2
    assert resolve_volume(message(severity="critical"), options, night) == 0.8
    assert resolve_volume(message(severity="critical", volume=0.1), options, night) == 0.1
    assert resolve_volume(message(), {}, night) is None  # 1.0 behaviour: no change


def test_the_speech_estimate_is_bounded() -> None:
    assert speech_seconds("short") == 4
    assert speech_seconds("x" * 150) == 12
    assert speech_seconds("x" * 5000) == 60


async def test_a_plain_player_gets_its_volume_back_after_speaking(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    await say(hass, entry, fake_speakers.plain_player, volume=0.3)
    assert levels == [(fake_speakers.plain_player, 0.3)]
    await tick(hass, freezer, 5)
    assert levels == [(fake_speakers.plain_player, 0.3), (fake_speakers.plain_player, 0.7)]


async def test_an_announce_player_gets_its_volume_back_after_the_estimate(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    await say(hass, entry, fake_speakers.announce_player, volume=0.3)
    await tick(hass, freezer, 3)
    assert levels == [(fake_speakers.announce_player, 0.3)]  # still speaking
    await tick(hass, freezer, 2)
    assert levels[-1] == (fake_speakers.announce_player, 0.7)


async def test_a_volume_changed_meanwhile_is_left_alone(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    await say(hass, entry, fake_speakers.announce_player, volume=0.3)
    state = hass.states.get(fake_speakers.announce_player)
    assert state is not None
    hass.states.async_set(state.entity_id, "idle", {**state.attributes, "volume_level": 0.5})
    await tick(hass, freezer, 10)
    assert levels == [(fake_speakers.announce_player, 0.3)]


async def test_two_messages_put_the_volume_back_once_to_the_first_level(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    await say(hass, entry, fake_speakers.announce_player, volume=0.3)
    await say(hass, entry, fake_speakers.announce_player, id="n", message="Door open", volume=0.4)
    await tick(hass, freezer, 10)
    player = fake_speakers.announce_player
    assert levels == [(player, 0.3), (player, 0.4), (player, 0.7)]


async def test_no_restore_when_it_is_switched_off(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    entry.runtime_data.options["speak_restore_volume"] = False
    await say(hass, entry, fake_speakers.plain_player, volume=0.3)
    await tick(hass, freezer, 70)
    assert levels == [(fake_speakers.plain_player, 0.3)]


async def test_the_severity_volume_applies_without_a_call_volume(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    entry.runtime_data.options["speak_severity_volume"] = {"critical": 90}
    await say(hass, entry, fake_speakers.plain_player, severity="critical")
    assert levels[0] == (fake_speakers.plain_player, 0.9)
    await tick(hass, freezer, 10)
    assert levels[-1] == (fake_speakers.plain_player, 0.7)


async def test_a_sonos_player_gets_a_clip_volume_and_keeps_its_own(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    levels: list[tuple[str, float]],
    freezer: FrozenDateTimeFactory,
) -> None:
    registry = er.async_get(hass)
    sonos = registry.async_get_or_create("media_player", "sonos", "living-1").entity_id
    kitchen = hass.states.get(fake_speakers.announce_player)
    assert kitchen is not None
    hass.states.async_set(sonos, "idle", dict(kitchen.attributes))
    await say(hass, entry, sonos, volume=0.3)
    (call,) = fake_speakers.play_media
    assert call.data["announce"] is True and call.data["extra"] == {"volume": 0.3}
    assert not fake_speakers.tts_speak
    await tick(hass, freezer, 70)
    assert levels == []
