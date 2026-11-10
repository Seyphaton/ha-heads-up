"""An entity ID changed in Home Assistant is followed in the integration's own copies (D-201)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.panel_data import (
    Attention,
    check_mail_service,
    check_references,
)
from custom_components.heads_up.hub.rename import rewrite

from ..conftest import banners
from .conftest import AddDevice
from .helpers import set_person
from .policy_support import ESCALATION, add_policy, make_household, send
from .test_recipients_groups import add_group


def test_rewrite_replaces_whole_entity_ids_only() -> None:
    data = {
        "people": ["person.anna", "person.annabel"],
        "template": "{{ is_state('sensor.a', 'on') or is_state('sensor.ab', 'on') }}",
        "message": "sensor.a is open",
        "title": "sensor.a is open",
        "nested": {"recipients": ["sensor.a"]},
    }
    assert rewrite(data, "person.anna", "person.ann") == {
        **data,
        "people": ["person.ann", "person.annabel"],
    }
    moved = rewrite(data, "sensor.a", "sensor.z")
    assert moved["template"] == "{{ is_state('sensor.z', 'on') or is_state('sensor.ab', 'on') }}"
    assert moved["message"] == "sensor.z is open"
    assert moved["title"] == "sensor.a is open"  # only text fields that hold templates change
    assert moved["nested"] == {"recipients": ["sensor.z"]}


async def test_a_renamed_speaker_is_followed_by_groups_and_policy_targets(
    hass: HomeAssistant, entry: MockConfigEntry, fake_speakers: Any
) -> None:
    registry = er.async_get(hass)
    speaker = registry.async_get_or_create("media_player", "fake", "den", suggested_object_id="den")
    hass.states.async_set(speaker.entity_id, "idle", {"supported_features": 1 << 12})
    add_group(hass, entry, "Rooms", members=[speaker.entity_id], areas=[])
    await add_policy(
        hass,
        entry,
        "Spoken",
        **{
            **ESCALATION,
            "channels": ["speak"],
            "targets": {"speak": {"recipients": [speaker.entity_id]}},
        },
    )
    registry.async_update_entity(speaker.entity_id, new_entity_id="media_player.lounge")
    await hass.async_block_till_done()
    subs = {s.title: dict(s.data) for s in entry.subentries.values()}
    assert subs["Rooms"]["members"] == ["media_player.lounge"]
    assert subs["Spoken"]["targets"] == {"speak": {"recipients": ["media_player.lounge"]}}
    assert any(e["result"] == "entity_renamed" for e in entry.runtime_data.hub.trace.entries())


async def test_a_renamed_person_is_followed_in_audiences_rules_messages_and_rows(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    registry = er.async_get(hass)
    person = registry.async_get_or_create("person", "test", "anna", suggested_object_id="anna")
    assert person.entity_id == "person.anna"
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"kind": "persons", "persons": ["person.anna", "person.ben"]},
            subentry_type="audience",
            title="Parents",
            unique_id=None,
        ),
    )
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"entity_id": "binary_sensor.w", "message": "open", "people": ["person.anna"]},
            subentry_type="rule",
            title="Window",
            unique_id=None,
        ),
    )
    await send(hass, entry, to={"push": {"recipients": ["person.anna"]}})
    assert any(
        r.recipient == "person.anna" or r.person == "person.anna"
        for r in entry.runtime_data.hub.ledger.for_message("m")
    )

    registry.async_update_entity("person.anna", new_entity_id="person.anne")
    await hass.async_block_till_done()
    subs = {s.title: dict(s.data) for s in entry.subentries.values()}
    assert subs["Parents"]["persons"] == ["person.anne", "person.ben"]
    assert subs["Window"]["people"] == ["person.anne"]
    assert banners(entry)["m"].targets == {"push": {"recipients": ["person.anne"]}}
    rows = entry.runtime_data.hub.ledger.for_message("m")
    assert rows and not any("person.anna" in (r.recipient, r.person) for r in rows)


def test_a_missing_policy_is_reported_for_a_rule_and_for_a_stored_message() -> None:
    exists = {"P1"}
    found = check_references(
        [
            ("rules", "Window", "rule_1", "P1"),
            ("rules", "Door", "rule_2", "P9"),
            ("messages", "Leak", "m", "name:Gone"),
            ("messages", "Leak", "m", "none"),
        ],
        lambda ref: ref in exists,
    )
    assert [(a.kind, a.subject, a.detail, a.page) for a in found] == [
        ("reference_missing", "Door", "P9", "rules"),
        ("reference_missing", "Leak", "Gone", "messages"),
    ]
    assert all(isinstance(a, Attention) and a.level == "error" for a in found)


def test_a_mail_service_that_does_not_exist_is_reported() -> None:
    assert [a.kind for a in check_mail_service("smtp_x", False)] == ["mail_service_missing"]
    assert check_mail_service("smtp_x", True) == [] and check_mail_service("", False) == []


async def test_the_overview_lists_a_rule_whose_policy_was_deleted(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub import panel_data

    set_person(hass, "person.anna", "home")
    night = await add_policy(hass, entry, "Night", **ESCALATION)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"entity_id": "binary_sensor.w", "message": "open", "policy": night.subentry_id},
            subentry_type="rule",
            title="Window",
            unique_id=None,
        ),
    )
    hass.config_entries.async_remove_subentry(entry, night.subentry_id)
    await hass.async_block_till_done()
    items = panel_data.attention(hass, entry.runtime_data, entry)
    assert ("reference_missing", "Window") in [(i["kind"], i["subject"]) for i in items]
