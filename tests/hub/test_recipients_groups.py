"""Recipient groups and areas for speech (DESIGN §23.5, §23.7)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .helpers import FakeSpeakers


def resolver(entry: MockConfigEntry) -> Any:
    return entry.runtime_data.hub.resolver


def add_group(hass: HomeAssistant, entry: MockConfigEntry, name: str, **data: Any) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(data=data, subentry_type="recipient_group", title=name, unique_id=None),
    )


async def test_a_speaker_is_a_valid_recipient_and_a_group_is_named_with_a_suffix(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speakers = fake_speakers
    add_group(hass, entry, "Ground floor", members=[speakers.announce_player], areas=[])
    await hass.async_block_till_done()
    known = resolver(entry).known("speak")
    assert speakers.announce_player in known and "Ground floor (group)" in known


async def test_a_group_expands_to_its_members(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speakers = fake_speakers
    add_group(
        hass,
        entry,
        "Ground floor",
        members=[speakers.announce_player, speakers.plain_player],
        areas=[],
    )
    await hass.async_block_till_done()
    result = await resolver(entry).resolve(
        {"recipients": ["Ground floor (group)"]}, "speak", "warning"
    )
    assert [r.key for r in result.recipients] == [speakers.announce_player, speakers.plain_player]
    assert result.recipients[0].reason == "group:Ground floor"


async def test_a_speaker_named_twice_is_delivered_once(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speakers = fake_speakers
    add_group(hass, entry, "G", members=[speakers.announce_player], areas=[])
    await hass.async_block_till_done()
    result = await resolver(entry).resolve(
        {"recipients": [speakers.announce_player, "G (group)"]}, "speak", "warning"
    )
    assert [r.key for r in result.recipients] == [speakers.announce_player]


async def test_an_area_expands_to_the_speakers_assigned_to_it(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speakers = fake_speakers
    area = ar.async_get(hass).async_create("Kitchen")
    registry = er.async_get(hass)
    hass.states.async_remove(speakers.announce_player)  # free the entity id for the registry
    entity = registry.async_get_or_create(
        "media_player", "fake", "kitchen", suggested_object_id="kitchen"
    )
    assert entity.entity_id == speakers.announce_player
    hass.states.async_set(entity.entity_id, "idle")
    registry.async_update_entity(entity.entity_id, area_id=area.id)
    add_group(hass, entry, "Rooms", members=[], areas=[area.id])
    await hass.async_block_till_done()
    by_group = await resolver(entry).resolve({"recipients": ["Rooms (group)"]}, "speak", "warning")
    by_area = await resolver(entry).resolve({"recipients": [area.id]}, "speak", "warning")
    assert [r.key for r in by_group.recipients] == [speakers.announce_player]
    assert [r.key for r in by_area.recipients] == [speakers.announce_player]


async def test_an_empty_group_and_unknown_names_are_skipped_with_a_reason(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    add_group(hass, entry, "Nobody", members=["media_player.gone"], areas=[])
    await hass.async_block_till_done()
    result = await resolver(entry).resolve(
        {"recipients": ["Nobody (group)", "media_player.unknown"]}, "speak", "warning"
    )
    assert {(s.who, s.reason) for s in result.skipped} == {
        ("Nobody (group)", "group_empty"),
        ("media_player.unknown", "unknown_recipient"),
    }


async def test_a_group_has_a_sensor_that_keeps_its_entity_id_when_the_group_is_renamed(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    speakers = fake_speakers
    add_group(hass, entry, "Ground floor", members=[speakers.announce_player], areas=[])
    await hass.async_block_till_done()
    state = hass.states.get("sensor.heads_up_group_ground_floor")
    assert state is not None and state.state == "1"
    assert state.attributes["speakers"] == [speakers.announce_player]
    (group,) = [s for s in entry.subentries.values() if s.subentry_type == "recipient_group"]
    hass.config_entries.async_update_subentry(entry, group, title="Downstairs")
    await hass.async_block_till_done()
    renamed = hass.states.get("sensor.heads_up_group_ground_floor")
    assert renamed is not None and renamed.attributes["group"] == "Downstairs"
    result = await resolver(entry).resolve(
        {"recipients": ["sensor.heads_up_group_ground_floor"]}, "speak", "warning"
    )
    assert [r.key for r in result.recipients] == [speakers.announce_player]


async def test_a_group_written_as_text_is_refused_with_its_sensor(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: FakeSpeakers
) -> None:
    import pytest
    from homeassistant.exceptions import ServiceValidationError

    add_group(hass, entry, "Ground floor", members=[fake_speakers.announce_player], areas=[])
    await hass.async_block_till_done()
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            "heads_up",
            "notify",
            {
                "message": "x",
                "severity": "info",
                "channels": ["speak"],
                "speakers": ["Ground floor (group)"],
            },
            blocking=True,
        )
    assert err.value.translation_key == "group_needs_entity"
    assert err.value.translation_placeholders["entity_id"] == "sensor.heads_up_group_ground_floor"  # type: ignore[index]
