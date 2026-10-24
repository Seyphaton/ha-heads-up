"""Timeouts and restart safety (D-023, D-031, quality gate: survives a simulated restart)."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners


async def restart(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Unload and set up the entry again; state must come back from the store."""
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_banner_expires_after_timeout(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="t", message="x", timeout=300, tag="g")
    events = async_capture_events(hass, f"{DOMAIN}_banner_expired")

    freezer.tick(timedelta(seconds=299))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert "t" in banners(entry)

    freezer.tick(timedelta(seconds=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert "t" not in banners(entry)
    assert [e.data for e in events] == [{"id": "t", "tag": "g"}]


async def test_state_survives_restart(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="kept", severity="critical", timeout=0, tag="x")
    await create(id="b", message="dismissed by one user")
    entry.runtime_data.dismiss("b", "user-1")
    before = {k: v.to_dict() for k, v in banners(entry).items()}

    await restart(hass, entry)

    assert {k: v.to_dict() for k, v in banners(entry).items()} == before


async def test_timeout_keeps_running_across_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="t", message="x", timeout=300)
    freezer.tick(timedelta(seconds=200))
    await restart(hass, entry)
    assert "t" in banners(entry)

    freezer.tick(timedelta(seconds=101))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert "t" not in banners(entry)


async def test_banner_expired_while_down_is_dropped_on_start(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="t", message="x", timeout=60)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    freezer.tick(timedelta(hours=1))
    events = async_capture_events(hass, f"{DOMAIN}_banner_expired")
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert banners(entry) == {}
    assert [e.data["id"] for e in events] == ["t"]


async def test_removing_entry_deletes_storage(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: dict
) -> None:
    await create(id="a", message="x")
    await hass.config_entries.async_unload(entry.entry_id)
    assert "heads_up.banners" in hass_storage

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()
    assert "heads_up.banners" not in hass_storage
