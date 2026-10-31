"""Reminder: repeat while unacknowledged, up to M times (D-079, D-081, D-078)."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .policy_support import REMINDER, add_policy, make_household, pushes, send, trace, wait


async def test_it_repeats_every_interval_up_to_the_maximum(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 10.1)
    assert len(pushes(home.anna)) == 2
    await wait(hass, entry, freezer, 10)
    assert len(pushes(home.anna)) == 3
    await wait(hass, entry, freezer, 30)
    assert len(pushes(home.anna)) == 3


async def test_acknowledging_stops_the_reminders(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    await wait(hass, entry, freezer, 25)
    assert len(pushes(home.anna)) == 1


async def test_a_snoozed_person_is_not_reminded_and_is_notified_when_it_ends(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, snoozable=True, snooze_options=[{"minutes": 15}])
    entry.runtime_data.snooze("m", "anna-id", 900)
    await wait(hass, entry, freezer, 11)
    assert len(pushes(home.anna)) == 1  # no reminder during the snooze
    await wait(hass, entry, freezer, 5)
    assert len(pushes(home.anna)) == 2  # the snooze ended: notified again (D-078)


async def test_it_stops_when_everyone_has_dismissed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    entry.runtime_data.dismiss("m", "anna-id")
    await wait(hass, entry, freezer, 11)
    assert len(pushes(home.anna)) == 1
    assert any(e["reason"] == "nobody_left" for e in trace(entry))


async def test_it_can_be_limited_to_some_channels(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER, channels=["speak"])
    await send(hass, entry)
    await wait(hass, entry, freezer, 11)
    assert len(pushes(home.anna)) == 1


async def test_a_severity_filter_leaves_other_messages_alone(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER, severities=["critical"])
    await send(hass, entry, severity="info")
    await wait(hass, entry, freezer, 11)
    assert len(pushes(home.anna)) == 1
