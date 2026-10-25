"""Heads Up: dismissible dashboard banners created by actions."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .frontend import async_add_card, async_register_card_path, async_remove_card
from .manager import BannerManager, banner_store
from .services import async_setup_services
from .websocket import async_setup_websocket

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.SENSOR]

type HeadsUpConfigEntry = ConfigEntry[BannerManager]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_setup_services(hass)
    async_setup_websocket(hass)
    await async_register_card_path(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> bool:
    manager = BannerManager(hass, entry.options)
    await manager.async_load()
    manager.sync_rules(entry.subentries, silent=True)
    entry.runtime_data = manager
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_add_card(hass)
    return True


async def _async_entry_updated(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> None:
    # Options apply to banners created from now on; no reload needed (D-030). The listener
    # also runs when a rule subentry is added, changed or removed (HA_API_NOTES N-57).
    entry.runtime_data.options.update(entry.options)
    entry.runtime_data.sync_rules(entry.subentries)


async def async_unload_entry(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await async_remove_card(hass)
        await entry.runtime_data.async_unload()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> None:
    await banner_store(hass).async_remove()
