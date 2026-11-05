"""Restart hardening (H10): overdue timers fire once, acknowledged stays acknowledged, damaged or
unknown stored data never stops the hub."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState, ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    QUIET,
    REMINDER,
    add_policy,
    make_household,
    pushes,
    send,
    wait,
)

KEY = "heads_up.deliveries"


async def down_for(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory, seconds: float
) -> None:
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(seconds)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)


async def test_an_overdue_reminder_fires_once_and_the_count_goes_on(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)  # every 10 minutes, at most 2
    await send(hass, entry)
    await down_for(hass, entry, freezer, 3600)
    assert len(pushes(home.anna)) == 2  # the original and one reminder, not six
    await wait(hass, entry, freezer, 10.1)
    assert len(pushes(home.anna)) == 3
    await wait(hass, entry, freezer, 60)
    assert len(pushes(home.anna)) == 3  # the maximum holds across the restart


async def test_an_acknowledged_message_stays_quiet_after_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    await settle(hass, entry)
    await down_for(hass, entry, freezer, 3600)
    assert len(pushes(home.anna)) == 1
    assert entry.runtime_data.banners["m"].acknowledged_by == ["anna-id"]


async def test_a_held_push_whose_window_ended_while_down_is_sent_once_at_startup(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    assert not pushes(home.anna)
    await down_for(hass, entry, freezer, 9 * 3600)  # until 08:00
    assert len(pushes(home.anna)) == 1
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1


async def test_a_message_that_expired_while_down_is_taken_back_and_not_resent(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning", timeout=60)
    assert len(pushes(home.anna)) == 1
    await down_for(hass, entry, freezer, 600)
    assert len(pushes(home.anna)) == 1
    assert home.anna.calls[-1].data["message"] == "clear_notification"
    assert entry.runtime_data.hub.ledger.for_message("m") == []


@pytest.mark.parametrize(
    "bad",
    [
        ["not", "a", "dict"],
        {"deliveries": "junk", "held": 5},
        {"deliveries": [None, 3], "held": [None, "x"]},
    ],
)
async def test_a_stored_ledger_of_the_wrong_shape_does_not_stop_the_hub(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    bad: Any,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning")
    assert await hass.config_entries.async_unload(entry.entry_id)
    hass_storage[KEY]["data"] = bad
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)
    assert entry.state is ConfigEntryState.LOADED
    await send(hass, entry, id="after", severity="warning")
    assert len(pushes(home.anna)) == 2


async def test_a_subentry_of_an_unknown_type_is_ignored(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    """A later version may add a type; going back to this one must not break (downgrade)."""
    home = await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(data={"x": 1}, subentry_type="future_type", title="Later", unique_id=None),
    )
    await hass.async_block_till_done()
    await restart(hass, entry)
    assert entry.state is ConfigEntryState.LOADED
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1
    assert hass.services.has_service(DOMAIN, "notify")


async def test_the_bell_entry_of_an_active_message_comes_back_after_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    persistent_capture: Any,
) -> None:
    """Home Assistant keeps its notification bell in memory, so a restart empties it."""
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "bell", "message": "Leak", "channels": ["banner", "persistent"]},
        blocking=True,
    )
    await settle(hass, entry)
    created = len(persistent_capture.create)
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(persistent_capture.create) == created + 1
    assert persistent_capture.create[-1].data["notification_id"] == "hu_bell"
    await hass.services.async_call(DOMAIN, "clear_notifications", {"id": "bell"}, blocking=True)
    await restart(hass, entry)
    assert len(persistent_capture.create) == created + 1  # a cleared message stays away
