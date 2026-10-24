"""Count of active banners (D-013): stored, not waiting for a condition. Global, not per user."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .manager import BannerManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ActiveBannersSensor(entry)])


class ActiveBannersSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "active_banners"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._manager: BannerManager = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_active_banners"
        # A service device gives the entity the "heads_up_" prefix in its entity_id.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Heads Up",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int:
        return self._manager.active_count()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._manager.subscribe(self.async_write_ha_state))
