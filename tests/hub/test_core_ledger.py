"""Delivery ledger store: layout, migration hook, damaged rows."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..conftest import CreateBanner
from ..test_restart import restart
from .helpers import settle

KEY = "heads_up.deliveries"


async def test_store_is_saved_with_its_own_key_and_versions(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: Any
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    saved = hass_storage[KEY]
    assert saved["version"] == 2 and saved["minor_version"] == 1
    row = saved["data"]["deliveries"][0]
    assert (row["message_id"], row["channel"], row["state"]) == ("a", "banner", "sent")


async def test_older_minor_version_goes_through_the_migration_hook(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: Any
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    hass_storage[KEY]["minor_version"] = 0
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)
    assert ("a", "banner", "") in entry.runtime_data.hub.ledger.rows


async def test_damaged_rows_are_skipped_and_the_rest_load(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: Any
) -> None:
    await create(id="a", message="x")
    await create(id="b", message="x")
    await settle(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    rows = hass_storage[KEY]["data"]["deliveries"]
    rows.append({"message_id": "a"})  # missing keys
    rows.append("junk")
    rows.append({**rows[0], "state": "exploded"})
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)
    ledger = entry.runtime_data.hub.ledger
    assert {k[0] for k in ledger.rows} == {"a", "b"}


async def test_removing_the_entry_removes_the_ledger(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: Any
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    await hass.config_entries.async_remove(entry.entry_id)
    await settle(hass, entry)
    assert KEY not in hass_storage


async def test_a_second_restart_keeps_the_rows(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    await restart(hass, entry)
    await restart(hass, entry)
    assert ("a", "banner", "") in entry.runtime_data.hub.ledger.rows
