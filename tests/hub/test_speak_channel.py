"""Speak channel: the service for each kind of speaker, the text, groups, queue and cooldown."""

import asyncio
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.channels import speak
from custom_components.heads_up.hub.channels.speak import speech_text
from custom_components.heads_up.models import Banner

from .helpers import FakeSpeakers, settle, tick
from .policy_support import ESCALATION, QUIET, add_policy, make_household


@pytest.fixture(autouse=True)
def fake_media_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(speak, "media_source_id", lambda hass, text, engine, lang: f"tts://{text}")


async def say(
    hass: HomeAssistant, entry: MockConfigEntry, *speakers: str, **data: Any
) -> dict[str, Any]:
    body = {
        "id": "m",
        "message": "Water leak",
        "channels": ["speak"],
        "to": {"speak": {"recipients": list(speakers)}},
        **data,
    }
    result = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert result is not None
    return dict(result)


def reasons(entry: MockConfigEntry) -> list[str | None]:
    return [e["reason"] for e in entry.runtime_data.hub.trace.entries("m")]


async def test_a_satellite_is_announced_to(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    result = await say(hass, entry, fake_speakers.satellite)
    assert result["channels"]["speak"]["sent"] == 1
    (call,) = fake_speakers.announce
    assert call.data == {"entity_id": fake_speakers.satellite, "message": "Water leak"}


async def test_a_player_with_announce_is_spoken_to_through_tts_speak(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    await say(hass, entry, fake_speakers.announce_player)
    (call,) = fake_speakers.tts_speak
    assert call.data["entity_id"] == fake_speakers.tts_entity
    assert call.data["media_player_entity_id"] == fake_speakers.announce_player
    assert call.data["message"] == "Water leak" and call.data["language"] == "en"
    assert not fake_speakers.play_media


async def test_a_player_without_announce_gets_plain_playback_at_its_volume(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    await say(hass, entry, fake_speakers.plain_player)
    (call,) = fake_speakers.play_media
    assert call.data["media_content_id"] == "tts://Water leak"
    assert "announce" not in call.data
    assert not fake_speakers.tts_speak


async def test_the_hub_never_changes_the_volume(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    await say(
        hass,
        entry,
        fake_speakers.plain_player,
        fake_speakers.announce_player,
        fake_speakers.satellite,
    )
    assert not fake_speakers.volume_set


async def test_the_text_is_tts_message_then_title_then_message(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    await say(hass, entry, fake_speakers.satellite, id="a", title="Leak", tts_message="Water!")
    await say(hass, entry, fake_speakers.satellite, id="b", title="Leak")
    await say(hass, entry, fake_speakers.satellite, id="c")
    assert [c.data["message"] for c in fake_speakers.announce] == ["Water!", "Leak", "Water leak"]


def make(message: str = "m", **kw: Any) -> Banner:
    from datetime import UTC, datetime

    now = datetime(2026, 11, 1, tzinfo=UTC)
    return Banner(
        id="x", message=message, severity="info", dismissible=True, dismiss_scope="user",
        created_at=now, updated_at=now, **kw,
    )  # fmt: skip


def test_a_long_text_is_cut_at_a_word_and_ends_with_an_ellipsis() -> None:
    text = make(message="The garage door has been open for more than ten minutes now")
    assert speech_text(text, 30) == "The garage door has been open…"
    assert speech_text(text, 200) == text.message


def test_a_text_without_spaces_is_cut_hard() -> None:
    assert speech_text(make(message="a" * 50), 10) == "a" * 9 + "…"


async def test_the_limit_is_an_option(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    entry.runtime_data.options["speak_max_length"] = 12
    await say(hass, entry, fake_speakers.satellite, message="Water on the kitchen floor")
    assert fake_speakers.announce[0].data["message"] == "Water on…"


async def test_a_group_and_an_area_speak_on_all_their_members(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"members": [fake_speakers.satellite, fake_speakers.plain_player], "areas": []},
            subentry_type="recipient_group",
            title="Downstairs",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    result = await say(hass, entry, "Downstairs (group)")
    assert result["channels"]["speak"]["sent"] == 2
    assert len(fake_speakers.announce) == 1 and len(fake_speakers.play_media) == 1


async def test_the_same_text_is_not_repeated_on_a_speaker_within_the_cooldown(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    freezer: FrozenDateTimeFactory,
) -> None:
    await say(hass, entry, fake_speakers.satellite, id="a")
    await say(hass, entry, fake_speakers.satellite, id="b")
    assert len(fake_speakers.announce) == 1
    await say(hass, entry, fake_speakers.satellite, id="c", message="Something else")
    assert len(fake_speakers.announce) == 2  # a different text is never blocked
    await tick(hass, freezer, 61)
    await say(hass, entry, fake_speakers.satellite, id="d")
    assert len(fake_speakers.announce) == 3


async def test_a_cooldown_of_zero_speaks_every_time(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    entry.runtime_data.options["speak_cooldown_seconds"] = 0
    await say(hass, entry, fake_speakers.satellite, id="a")
    await say(hass, entry, fake_speakers.satellite, id="b")
    assert len(fake_speakers.announce) == 2


async def test_an_update_does_not_say_it_again(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    first = await say(hass, entry, fake_speakers.satellite)
    second = await say(hass, entry, fake_speakers.satellite, message="Water leak, now worse")
    assert len(fake_speakers.announce) == 1
    assert "already_spoken" in reasons(entry)
    assert first["channels"]["speak"]["sent"] == 1 and first["reasons"] == []
    # The response of the update says what the delivery does: it is not said again.
    assert second["channels"]["speak"] == {"sent": 0, "held": 0, "skipped": 1, "failed": 0}
    assert second["reasons"] == [
        {
            "channel": "speak",
            "recipient": fake_speakers.satellite,
            "result": "skipped",
            "reason": "already_spoken",
        }
    ]


async def test_nothing_is_said_when_the_message_ends(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    await say(hass, entry, fake_speakers.satellite)
    await hass.services.async_call(DOMAIN, "clear_notifications", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert len(fake_speakers.announce) == 1 and not fake_speakers.tts_speak


async def test_quiet_hours_skip_speech(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await add_policy(hass, entry, "Night", **QUIET)
    await say(hass, entry, fake_speakers.satellite, severity="warning")
    assert not fake_speakers.announce
    assert "quiet_hours" in reasons(entry)


async def test_a_speaker_that_does_not_exist_is_refused_by_the_call(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    hass.states.async_remove(fake_speakers.satellite)
    with pytest.raises(ServiceValidationError):
        await say(hass, entry, fake_speakers.satellite)


async def test_a_service_that_fails_is_a_failed_delivery_with_a_reason(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    async def boom(call: ServiceCall) -> None:
        raise HomeAssistantError("no network")

    hass.services.async_register("assist_satellite", "announce", boom)
    await say(hass, entry, fake_speakers.satellite)
    assert "send_failed" in reasons(entry)


async def test_a_missing_service_is_reported(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    hass.services.async_remove("assist_satellite", "announce")
    await say(hass, entry, fake_speakers.satellite)
    assert "service_not_found" in reasons(entry)


async def test_a_player_needs_a_text_to_speech_engine(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    caplog: pytest.LogCaptureFixture,
) -> None:
    hass.states.async_remove(fake_speakers.tts_entity)
    await say(hass, entry, fake_speakers.announce_player)
    assert "no_tts_engine" in reasons(entry) and not fake_speakers.tts_speak
    assert "no text-to-speech engine is chosen" in caplog.text  # the log says why


async def test_several_engines_need_the_option(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    caplog: pytest.LogCaptureFixture,
) -> None:
    hass.states.async_set("tts.other", "unknown", {})
    await say(hass, entry, fake_speakers.announce_player)
    assert "no_tts_engine" in reasons(entry)
    assert "Found 2" in caplog.text and "tts.other" in caplog.text  # the log names the engines
    entry.runtime_data.options["speak_tts_entity"] = "tts.other"
    await say(hass, entry, fake_speakers.announce_player, id="n")
    assert fake_speakers.tts_speak[-1].data["entity_id"] == "tts.other"


async def test_two_messages_do_not_cut_each_other_off_on_a_plain_player(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    player = fake_speakers.plain_player
    calls: list[ServiceCall] = []

    async def play(call: ServiceCall) -> None:
        calls.append(call)
        hass.states.async_set(player, "playing", dict(hass.states.get(player).attributes))  # type: ignore[union-attr]

    hass.services.async_register("media_player", "play_media", play)
    body = {"channels": ["speak"], "to": {"speak": {"recipients": [player]}}}
    await hass.services.async_call(
        DOMAIN, "notify", {"id": "a", "message": "One", **body}, blocking=True
    )
    await hass.services.async_call(
        DOMAIN, "notify", {"id": "b", "message": "Two", **body}, blocking=True
    )
    await hass.async_block_till_done()
    assert len(calls) == 1  # the second waits while the first is playing
    idle = dict(hass.states.get(player).attributes)  # type: ignore[union-attr]
    hass.states.async_set(player, "idle", idle)
    for _ in range(50):
        await asyncio.sleep(0)
    assert len(calls) == 2
    hass.states.async_set(player, "idle", idle)  # the second message finished too
    await settle(hass, entry)


async def test_rule_messages_reach_speech_through_an_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    fake_speakers: FakeSpeakers,
    mobile_app_device: Any,
    freezer: FrozenDateTimeFactory,
) -> None:
    from ..test_rules import WINDOW, add_rule

    await make_household(hass, mobile_app_device)
    escalation = {
        **ESCALATION,
        "channels": ["speak"],
        "targets": {"speak": {"recipients": [fake_speakers.satellite]}},
        "tags": ["rule"],
    }
    await add_policy(hass, entry, "Rules", **escalation)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    assert not fake_speakers.announce
    await tick(hass, freezer, 6 * 60)
    await settle(hass, entry)
    assert len(fake_speakers.announce) == 1
