"""Away: hold for a person who is not home, send on arrival while the message is active."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    AWAY,
    add_audience,
    add_policy,
    make_household,
    move,
    pushes,
    send,
    trace,
    wait,
)


async def family(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna", "person.ben"])


def away(hass: HomeAssistant, person: str, user: str, state: str = "not_home") -> None:
    move(hass, person, state)


async def notify_family(hass: HomeAssistant, entry: MockConfigEntry, **kw: object) -> None:
    await send(
        hass,
        entry,
        severity="warning",
        to={"push": {"audience": "Family"}},
        **kw,
    )


async def test_a_person_who_is_away_gets_it_on_arrival_and_the_one_at_home_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1
    away(hass, "person.ben", "ben-id", "not_home")
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1  # once


async def test_without_the_policy_the_person_away_is_sent_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    assert len(pushes(home.ben)) == 1


async def test_explicit_recipients_are_not_held(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await send(hass, entry, severity="warning", to={"push": {"recipients": ["person.ben"]}})
    assert len(pushes(home.ben)) == 1


async def test_unknown_presence_is_sent_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id", "unavailable")
    await notify_family(hass, entry)
    assert len(pushes(home.ben)) == 1


async def test_a_cleared_message_is_not_sent_on_arrival(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    entry.runtime_data.admin_clear("m")
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert not pushes(home.ben)


async def test_an_acknowledged_message_is_not_sent_on_arrival(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert not pushes(home.ben)
    assert any(e["reason"] == "no_longer_needed" for e in trace(entry))


async def test_a_message_the_person_dismissed_meanwhile_is_not_sent_on_arrival(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    entry.runtime_data.dismiss("m", "ben-id")
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert not pushes(home.ben)


async def test_the_wait_ends_after_the_maximum(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY, max_wait=30)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    await wait(hass, entry, freezer, 31)
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert not pushes(home.ben)
    assert any(e["reason"] == "max_wait_exceeded" for e in trace(entry))


async def test_a_held_delivery_survives_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await notify_family(hass, entry)
    await restart(hass, entry)
    await settle(hass, entry)
    assert not pushes(home.ben)
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1
    assert len(pushes(home.anna)) == 1  # nothing is sent twice after the restart


async def test_critical_passes_away_by_default(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **AWAY)
    away(hass, "person.ben", "ben-id")
    await send(hass, entry, severity="critical", to={"push": {"audience": "Family"}})
    assert len(pushes(home.ben)) == 1
    await send(hass, entry, id="w", severity="warning", to={"push": {"audience": "Family"}})
    assert len(pushes(home.ben)) == 1  # a warning waits for the arrival


async def test_critical_waits_for_arrival_when_the_policy_says_so(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await family(hass, entry)
    await add_policy(hass, entry, "Away", **{**AWAY, "critical_passes": False})
    away(hass, "person.ben", "ben-id")
    await send(hass, entry, severity="critical", to={"push": {"audience": "Family"}})
    assert not pushes(home.ben)
    away(hass, "person.ben", "ben-id", "home")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1
