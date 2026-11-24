"""Presence (D-212, D-214): the 1.0.0 upgrade, per-recipient and household rules, the delay."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.channels import speak

from .conftest import AddDevice
from .helpers import FakeSpeakers, settle
from .policy_support import add_audience, add_policy, make_household, move, pushes, send, wait

SETUP_1_0_0 = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "setup_1_0_0.json").read_text(encoding="utf-8")
)
CAPTURED = "2026-11-19T12:24:00+00:00"  # just after the 1.0.0 setup was written


@pytest.fixture(autouse=True)
def fake_media_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(speak, "media_source_id", lambda hass, text, engine, lang: f"tts://{text}")


# The upgrade from 1.0.0 ----------------------------------------------------------------------


async def upgrade(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> tuple[MockConfigEntry, Any]:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.ben", "not_home")
    stored = SETUP_1_0_0["entry"]
    for key, value in deepcopy(SETUP_1_0_0["stores"]).items():
        hass_storage[key] = value
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=stored["version"],
        minor_version=stored["minor_version"],
        options=dict(stored["options"]),
        subentries_data=deepcopy(stored["subentries"]),
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)
    return entry, home


def policy_data(entry: MockConfigEntry) -> dict[str, dict[str, Any]]:
    return {s.title: dict(s.data) for s in entry.subentries.values() if s.subentry_type == "policy"}


async def test_away_policies_become_presence_with_their_1_0_behaviour(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    freezer.move_to(CAPTURED)
    entry, _ = await upgrade(hass, hass_storage, mobile_app_device)
    data = policy_data(entry)
    assert (entry.version, entry.minor_version) == (3, 2)
    # 3.1 adds Not for critical (1.0 Away let critical messages pass, D-224); 3.2 writes that
    # as For without critical (D-280).
    assert data["Away"] == {
        **_old("Away"),
        "type": "presence",
        "after_wait": "drop",
        "severities": ["passive", "info", "warning"],
    }
    assert data["Away short"]["type"] == "presence" and data["Away short"]["max_wait"] == 30
    others = ("Escalate", "Remind", "Night", "Backup", "Digest")
    assert all(data[name] == _old(name) for name in others)  # nothing else changes
    backup = hass_storage["heads_up.migration_v2_2"]["data"]["entry"]["subentries"]
    assert {s["title"]: s["data"]["type"] for s in backup}["Away"] == "away"


def _old(title: str) -> dict[str, Any]:
    (sub,) = [s for s in SETUP_1_0_0["entry"]["subentries"] if s["title"] == title]
    return dict(sub["data"])


async def test_a_push_held_by_1_0_away_goes_out_when_the_person_arrives(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    freezer.move_to(CAPTURED)
    entry, home = await upgrade(hass, hass_storage, mobile_app_device)
    assert not pushes(home.ben)
    move(hass, "person.ben", "home")
    await wait(hass, entry, freezer, 0.5)
    assert not pushes(home.ben)  # the presence delay (60 s) has not passed
    await wait(hass, entry, freezer, 1)
    assert len(pushes(home.ben)) == 1


async def test_a_converted_away_still_drops_when_its_wait_ends(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])
    await add_policy(hass, entry, "Away", type="away", max_wait=30)  # read as 1.0 Away
    move(hass, "person.ben", "not_home")
    await send(hass, entry, severity="warning", to={"push": {"audience": "Family"}})
    await wait(hass, entry, freezer, 31)
    move(hass, "person.ben", "home")
    await wait(hass, entry, freezer, 2)
    assert not pushes(home.ben)


# Presence rules -------------------------------------------------------------------------------


@pytest.fixture
def options() -> dict[str, Any]:
    return {"policy_mode": "all", "presence_debounce_seconds": 0}


async def family(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])


async def to_family(hass: HomeAssistant, entry: MockConfigEntry, **kw: Any) -> None:
    await send(hass, entry, severity="warning", to={"push": {"audience": "Family"}}, **kw)


async def test_hold_until_the_recipient_leaves(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "On leaving", type="presence", presence_when="in", tags=["shop"])
    await to_family(hass, entry, tag="shop")
    assert not pushes(home.anna) and not pushes(home.ben)
    move(hass, "person.anna", "not_home")
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)


async def test_drop_while_the_recipient_is_in_the_zone(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(
        hass, entry, "Not at home", type="presence", presence_when="in", presence_then="drop"
    )
    move(hass, "person.ben", "not_home")
    await to_family(hass, entry)
    assert not pushes(home.anna) and len(pushes(home.ben)) == 1


async def test_another_zone_uses_the_person_state(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "At work", type="presence", zone="zone.work")
    move(hass, "person.anna", "work")
    await to_family(hass, entry)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)  # Ben is not at work: held
    move(hass, "person.ben", "work")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1


async def test_send_anyway_when_the_wait_ends(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", type="presence", max_wait=30, after_wait="send")
    move(hass, "person.ben", "not_home")
    await to_family(hass, entry)
    await wait(hass, entry, freezer, 29)
    assert not pushes(home.ben)
    move(hass, "person.anna", "home")  # someone else moves: Ben's deadline must not reset
    await wait(hass, entry, freezer, 2)
    assert len(pushes(home.ben)) == 1


async def test_speech_is_dropped_while_nobody_is_home_and_said_when_somebody_is(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: FakeSpeakers,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(
        hass,
        entry,
        "Quiet house",
        type="presence",
        channels=["speak"],
        household_who="nobody",
        presence_then="drop",
    )
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    say = {"channels": ["speak"], "to": {"speak": {"recipients": [fake_speakers.plain_player]}}}
    await send(hass, entry, severity="warning", **say)
    assert not fake_speakers.play_media
    move(hass, "person.ben", "home")
    await send(hass, entry, id="n", severity="warning", **say)
    assert len(fake_speakers.play_media) == 1


async def test_speech_waits_until_somebody_comes_home(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: FakeSpeakers,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Say on arrival", type="presence", channels=["speak"])
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    say = {"channels": ["speak"], "to": {"speak": {"recipients": [fake_speakers.plain_player]}}}
    await send(hass, entry, severity="warning", **say)
    assert not fake_speakers.play_media
    move(hass, "person.anna", "home")
    await settle(hass, entry)
    assert len(fake_speakers.play_media) == 1


async def test_a_push_policy_leaves_speech_alone(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: FakeSpeakers,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Away", type="presence")  # push, popup, mail
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    say = {"channels": ["speak"], "to": {"speak": {"recipients": [fake_speakers.plain_player]}}}
    await send(hass, entry, severity="warning", **say)
    assert len(fake_speakers.play_media) == 1


async def test_a_quick_return_within_the_delay_releases_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "On leaving", type="presence", presence_when="in")
    entry.runtime_data.options["presence_debounce_seconds"] = 60  # after the subentries settle
    await to_family(hass, entry)
    move(hass, "person.anna", "not_home")
    await wait(hass, entry, freezer, 0.5)
    move(hass, "person.anna", "home")  # a GPS flip at the zone edge
    await wait(hass, entry, freezer, 2)
    assert not pushes(home.anna)
