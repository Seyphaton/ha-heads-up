"""Names stored by earlier versions become keys, once, without losing a delivery (D-200)."""

from copy import deepcopy
from datetime import timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.models import Banner

from ..test_restart import restart
from .conftest import AddDevice
from .policy_support import ESCALATION, make_household, pushes, settle, wait

BANNERS = "heads_up.banners"
LEDGER = "heads_up.deliveries"
BACKUP = "heads_up.migration_v2"


def sub(kind: str, title: str, sid: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "subentry_id": sid,
        "subentry_type": kind,
        "title": title,
        "unique_id": None,
        "data": data,
    }


def stored(key: str, data: dict[str, Any], version: int = 1, minor: int = 1) -> dict[str, Any]:
    return {"version": version, "minor_version": minor, "key": key, "data": data}


def old_entry(version: int = 1, **options: Any) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        version=version,
        options={"policy_mode": "all", **options},
        subentries_data=[
            sub(
                "policy",
                "Water",
                "POL1",
                {**ESCALATION, "targets": {"push": {"audience": "Parents"}}},
            ),
            sub("policy", "Nag", "POL2", {"type": "reminder", "every_minutes": 10, "max_count": 2}),
            sub("audience", "Parents", "AUD1", {"kind": "persons", "persons": ["person.ben"]}),
            sub("recipient_group", "Hall", "GRP1", {"members": ["media_player.hall"], "areas": []}),
            sub(
                "rule",
                "Window",
                "RUL1",
                {"entity_id": "binary_sensor.window", "message": "open", "policy": "Nag"},
            ),
            sub(
                "policy",
                "Spoken",
                "POL3",
                {**ESCALATION, "targets": {"speak": {"recipients": ["Hall (group)"]}}},
            ),
        ],
    )


def old_banner(now: Any) -> dict[str, Any]:
    banner = Banner(
        id="m",
        message="Water leak",
        severity="critical",
        dismissible=True,
        dismiss_scope="user",
        created_at=now,
        updated_at=now,
        channels=["banner", "push"],
        targets={
            "push": {"recipients": ["person.anna"]},
            "speak": {"recipients": ["Hall (group)"]},
        },
        policy=["automatic", "Water", "Nag"],
    )
    return banner.to_dict()


def old_ledger(now: Any) -> dict[str, Any]:
    due = (now + timedelta(minutes=5)).isoformat()
    return {
        "deliveries": [
            {
                "message_id": "m",
                "channel": "timer",
                "recipient": "escalation:Water",
                "state": "planned",
                "updated_at": now.isoformat(),
                "due": due,
                "count": 0,
            },
            {
                "message_id": "m",
                "channel": "timer",
                "recipient": "reminder:Nag",
                "state": "planned",
                "updated_at": now.isoformat(),
                "due": (now + timedelta(minutes=10)).isoformat(),
                "count": 1,
            },
            {
                "message_id": "summary:summarize:Digest",
                "channel": "timer",
                "recipient": "summarize:Digest",
                "state": "planned",
                "updated_at": now.isoformat(),
                "due": due,
                "count": 0,
            },
        ],
        "held": [],
    }


async def start(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice, **options: Any
) -> tuple[MockConfigEntry, dict[str, Any], Any]:
    home = await make_household(hass, mobile_app_device)
    anna = hass.states.get("person.anna")
    assert anna is not None
    hass.states.async_set("person.anna", anna.state, {**anna.attributes, "friendly_name": "Anna"})
    now = dt_util.utcnow()
    hass_storage[BANNERS] = stored(BANNERS, {"banners": [old_banner(now)]})
    hass_storage[LEDGER] = stored(LEDGER, old_ledger(now))
    before = deepcopy(dict(hass_storage))
    entry = old_entry(**options)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry, before, home


async def test_the_entry_and_the_stores_get_keys_instead_of_names(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> None:
    entry, _, _home = await start(hass, hass_storage, mobile_app_device)
    assert entry.state is ConfigEntryState.LOADED and entry.version == 2
    data = {s.title: dict(s.data) for s in entry.subentries.values()}
    assert data["Water"]["targets"] == {"push": {"audience": "AUD1"}}
    assert data["Spoken"]["targets"] == {"speak": {"recipients": ["group:GRP1"]}}
    assert data["Window"]["policy"] == "POL2"
    banner = entry.runtime_data.banners["m"]
    assert banner.policy == ["automatic", "POL1", "POL2"]
    assert banner.targets["speak"] == {"recipients": ["group:GRP1"]}
    rows = {(r.message_id, r.recipient): r for r in entry.runtime_data.hub.ledger.timers()}
    assert set(rows) == {("m", "POL1"), ("m", "POL2"), ("summary:name:Digest", "name:Digest")}
    assert rows["m", "POL2"].count == 1  # a reminder already sent keeps its count


async def test_no_timer_is_lost_or_duplicated_and_the_escalation_still_fires(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    entry, before, home = await start(hass, hass_storage, mobile_app_device)
    old_due = {
        r["recipient"].split(":")[-1]: r["due"] for r in before[LEDGER]["data"]["deliveries"]
    }
    new_due = {
        r.recipient: r.due.isoformat() for r in entry.runtime_data.hub.ledger.timers() if r.due
    }
    assert new_due["POL1"] == old_due["Water"] and new_due["POL2"] == old_due["Nag"]
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.ben)) == 1  # the escalation to Parents (Ben) came once
    reasons = {e["reason"] for e in entry.runtime_data.hub.trace.entries("m")}
    assert not {"policy_deleted", "policy_disabled"} & reasons


async def test_the_backup_holds_the_old_data_and_is_written_once(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> None:
    entry, before, _home = await start(hass, hass_storage, mobile_app_device)
    backup = hass_storage[BACKUP]["data"]
    assert backup["entry"]["version"] == 1
    assert backup["stores"][BANNERS] == before[BANNERS]["data"]
    assert backup["stores"][LEDGER] == before[LEDGER]["data"]
    titles = {s["title"]: s["data"] for s in backup["entry"]["subentries"]}
    assert titles["Window"]["policy"] == "Nag"  # the names, as they were
    saved = deepcopy(hass_storage[BACKUP])
    await restart(hass, entry)
    assert hass_storage[BACKUP] == saved


async def test_a_second_start_changes_nothing(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> None:
    entry, _, _home = await start(hass, hass_storage, mobile_app_device)
    await settle(hass, entry)
    await restart(hass, entry)
    first = (
        {s.title: dict(s.data) for s in entry.subentries.values()},
        deepcopy(hass_storage[BANNERS]["data"]),
        deepcopy(hass_storage[LEDGER]["data"]),
    )
    await restart(hass, entry)
    assert first == (
        {s.title: dict(s.data) for s in entry.subentries.values()},
        hass_storage[BANNERS]["data"],
        hass_storage[LEDGER]["data"],
    )
    assert entry.version == 2


async def test_a_name_that_matches_nothing_is_kept_and_reported_not_dropped(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    now = dt_util.utcnow()
    banner = old_banner(now)
    banner["policy"] = ["automatic", "Deleted long ago"]
    hass_storage[BANNERS] = stored(BANNERS, {"banners": [banner]})
    entry = old_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.runtime_data.banners["m"].policy == ["automatic", "name:Deleted long ago"]


async def test_the_options_hold_kinds_and_a_hidden_warning_remembers_the_person(
    hass: HomeAssistant, hass_storage: dict[str, Any], mobile_app_device: AddDevice
) -> None:
    entry, _, _home = await start(
        hass,
        hass_storage,
        mobile_app_device,
        audiences_disabled=["Not home", "first_home"],
        attention_dismissed=["person_no_device|Anna|", "delivery_failed|push|x"],
    )
    assert entry.options["audiences_disabled"] == ["not_home", "first_home"]
    assert entry.options["attention_dismissed"] == [
        "person_no_device|person.anna|",
        "delivery_failed|push|x",
    ]
    assert "Not home" not in entry.runtime_data.hub.resolver.names()


async def test_an_entry_of_a_newer_version_is_not_set_up(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, version=3)
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.MIGRATION_ERROR


async def test_stores_that_were_not_rewritten_before_a_crash_still_resolve(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """The entry was saved at version 2, the stores still hold names: nothing is lost."""
    home = await make_household(hass, mobile_app_device)
    now = dt_util.utcnow()
    hass_storage[BANNERS] = stored(BANNERS, {"banners": [old_banner(now)]})
    hass_storage[LEDGER] = stored(LEDGER, old_ledger(now))
    entry = old_entry(version=2)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert {r.recipient for r in entry.runtime_data.hub.ledger.timers("m")} == {"POL1", "POL2"}
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.ben)) == 1
