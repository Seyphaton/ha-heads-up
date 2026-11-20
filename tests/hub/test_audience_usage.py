"""How often an audience was used and when last, one count per message (D-227)."""

from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.usage import RECENT_IDS, AudienceUsage

from ..test_restart import restart
from .helpers import set_person, settle
from .policy_support import ESCALATION, add_policy
from .test_audiences_notify import notify

NOW = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)


def usage_of(entry: MockConfigEntry, key: str) -> dict[str, Any]:
    return dict(entry.runtime_data.hub.usage.of(key))


async def test_a_message_counts_once_for_its_audience_however_often_it_is_sent(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    for text in ("first", "replaced"):
        await notify(
            hass, id="a", message=text, channels=["popup"], to={"popup": {"audience": "At home"}}
        )
        await settle(hass, entry)
    await notify(
        hass, id="b", message="x", channels=["popup"], to={"popup": {"audience": "At home"}}
    )
    await settle(hass, entry)
    assert usage_of(entry, "at_home")["count"] == 2
    assert usage_of(entry, "at_home")["last"] is not None
    assert usage_of(entry, "everyone") == {"count": 0, "last": None}


async def test_a_policy_that_addresses_an_audience_counts_it(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    policy = {
        **ESCALATION,
        "type": "deliver",
        "channels": ["popup"],
        "targets": {"popup": {"audience": "Admins"}},
    }
    policy.pop("after_minutes", None)
    await add_policy(hass, entry, "Also admins", **policy)
    await notify(hass, id="a", message="x", severity="warning", channels=["banner"])
    await settle(hass, entry)
    assert usage_of(entry, "admins")["count"] == 1


async def test_the_count_survives_a_restart(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home")
    await notify(
        hass, id="a", message="x", channels=["popup"], to={"popup": {"audience": "Everyone"}}
    )
    await settle(hass, entry)
    await restart(hass, entry)
    assert usage_of(entry, "everyone")["count"] == 1
    # The same message after the restart is still the same message.
    await notify(
        hass, id="a", message="y", channels=["popup"], to={"popup": {"audience": "Everyone"}}
    )
    await settle(hass, entry)
    assert usage_of(entry, "everyone")["count"] == 1


async def test_the_message_log_lists_the_audiences_a_message_went_to(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await notify(
        hass, id="a", message="x", channels=["popup"], to={"popup": {"audience": "At home"}}
    )
    await settle(hass, entry)
    (listed,) = [m for m in entry.runtime_data.hub.recent.listed() if m["id"] == "a"]
    assert listed["audiences"] == ["at_home"]


async def test_only_the_newest_message_ids_are_kept_per_audience(hass: HomeAssistant) -> None:
    usage = AudienceUsage(hass)
    for n in range(RECENT_IDS + 5):
        usage.record(f"m{n}", ["everyone"], NOW)
    assert usage.of("everyone") == {"count": RECENT_IDS + 5, "last": NOW.isoformat()}
    assert len(usage._data["everyone"]["recent"]) == RECENT_IDS


async def test_damaged_stored_counts_are_dropped(hass: HomeAssistant, hass_storage: Any) -> None:
    hass_storage["heads_up.audience_usage"] = {
        "version": 1,
        "key": "heads_up.audience_usage",
        "data": {
            "audiences": {
                "everyone": {"count": "x"},
                "admins": {"count": 3, "last": None},
                "bad": 1,
            }
        },
    }
    usage = AudienceUsage(hass)
    await usage.async_load()
    assert usage.of("everyone")["count"] == 0
    assert usage.of("admins")["count"] == 3
