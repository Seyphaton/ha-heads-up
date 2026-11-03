"""Heads Up: dismissible dashboard banners created by actions."""

from __future__ import annotations

import secrets

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    OPT_HUB_ENABLED,
    OPT_INSTALL_TOKEN,
    OPT_RECENT_MESSAGES,
    OPT_TRACE_ENTRIES,
)
from .frontend import async_add_card, async_register_card_path, async_remove_card
from .hub.channels.mail import MailChannel
from .hub.channels.persistent import PersistentChannel
from .hub.channels.popup import PopupChannel
from .hub.channels.push import PushChannel
from .hub.channels.speak import SpeakChannel
from .hub.engine import HubEngine
from .hub.ledger import remove_ledger
from .hub.panel import async_sync_panel
from .hub.panel import wanted as panel_wanted
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
    if not entry.options.get(OPT_INSTALL_TOKEN):
        # Generated once; part of push tags so two servers never clear each other's pushes (D-080).
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, OPT_INSTALL_TOKEN: secrets.token_hex(3)}
        )
    manager = BannerManager(hass, entry.options)
    # The engine listens before the load, so the silent transitions of startup reach it.
    _start_hub(hass, entry, manager)
    await manager.async_load()
    manager.sync_rules(entry.subentries, silent=True)
    if manager.hub is not None:
        await manager.hub.async_start(set(manager.banners) | set(manager.rules))
    entry.runtime_data = manager
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_add_card(hass)
    await async_sync_panel(hass, panel_wanted(manager.options))
    return True


def _start_hub(hass: HomeAssistant, entry: HeadsUpConfigEntry, manager: BannerManager) -> None:
    """Create the engine when the hub is on (D-107). Nothing is created while it is off."""
    if manager.hub is not None or not manager.options[OPT_HUB_ENABLED]:
        return
    hub = HubEngine(
        hass,
        manager.options,
        lambda work, name: entry.async_create_background_task(hass, work, name),
    )
    manager.hub = hub
    hub.lookup = lambda message_id: manager.banners.get(message_id) or manager.rules.get(message_id)
    hub.create_message = manager.create
    hub.visibility_changed = manager.refresh
    hub.resolver.sync(entry.subentries)
    hub.policies.sync(entry.subentries)
    hub.channels.register(PushChannel(hass, hub, manager))
    hub.channels.register(SpeakChannel(hass, hub, manager))
    hub.channels.register(PopupChannel(hass, hub, manager))
    hub.channels.register(PersistentChannel(hass))
    hub.channels.register(MailChannel(hass, hub, manager))
    manager.subscribe_transitions(hub.on_transition)


async def _async_entry_updated(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> None:
    # Options apply to banners created from now on; no reload needed (D-030). The listener
    # also runs when a rule subentry is added, changed or removed (HA_API_NOTES N-57).
    manager = entry.runtime_data
    manager.options.update(entry.options)
    if manager.options[OPT_HUB_ENABLED]:
        if manager.hub is None:
            _start_hub(hass, entry, manager)
            assert manager.hub is not None
            await manager.hub.async_start(set(manager.banners) | set(manager.rules))
        else:
            manager.hub.trace.resize(manager.options[OPT_TRACE_ENTRIES])
            manager.hub.log.resize(manager.options[OPT_TRACE_ENTRIES])
            manager.hub.recent.resize(manager.options[OPT_RECENT_MESSAGES])
            manager.hub.limiter.configure(manager.options)
    elif (hub := manager.hub) is not None:
        manager.hub = None
        await hub.async_unload()
    if manager.hub is not None:
        manager.hub.resolver.sync(entry.subentries)
        manager.hub.policies.sync(entry.subentries)
        manager.hub.on_policies_changed()
    manager.sync_rules(entry.subentries)
    await async_sync_panel(hass, panel_wanted(manager.options))


async def async_unload_entry(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await async_remove_card(hass)
        await async_sync_panel(hass, False)
        if entry.runtime_data.hub is not None:
            await entry.runtime_data.hub.async_unload()
        await entry.runtime_data.async_unload()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: HeadsUpConfigEntry) -> None:
    await banner_store(hass).async_remove()
    await remove_ledger(hass)
