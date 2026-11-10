"""Count of active banners (D-013): stored, not waiting for a condition. Global, not per user.

Also one sensor per recipient group (D-201): a call names a group by the entity ID of its
sensor, whose unique ID holds the subentry ID, so renaming the group does not break the call.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, GROUP_SUBENTRY, SIGNAL_AUDIENCES
from .manager import BannerManager

UNIQUE_MARK = "_group_"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([ActiveBannersSensor(entry)])
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    added: set[str] = set()

    @callback
    def sync() -> None:
        for subentry_id, subentry in entry.subentries.items():
            if subentry.subentry_type == GROUP_SUBENTRY and f"{prefix}{subentry_id}" not in added:
                added.add(f"{prefix}{subentry_id}")
                async_add_entities(
                    [GroupSensor(entry, f"{prefix}{subentry_id}", subentry_id)],
                    config_subentry_id=subentry_id,
                )

    sync()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_AUDIENCES, sync))


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


class GroupSensor(SensorEntity):
    """The speakers a recipient group reaches now. No device, for the reason given in
    binary_sensor.py."""

    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, unique_id: str, subentry_id: str) -> None:
        self._entry = entry
        self._subentry_id = subentry_id
        self._attr_unique_id = unique_id
        self._read()

    def _read(self) -> None:
        subentry = self._entry.subentries.get(self._subentry_id)
        hub = getattr(getattr(self._entry, "runtime_data", None), "hub", None)
        group = hub.resolver.group(f"group:{self._subentry_id}") if hub is not None else None
        self._attr_available = subentry is not None and group is not None
        if subentry is not None:
            self._attr_name = f"Heads Up group {subentry.title}"
        if group is not None and hub is not None:
            speakers = hub.resolver.group_speakers(group)
            self._attr_native_value = len(speakers)
            self._attr_extra_state_attributes = {"group": group.name, "speakers": speakers}

    @callback
    def _changed(self, *_: Any) -> None:
        self._read()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_AUDIENCES, self._changed))


def group_entity_ids(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Subentry ID of every group to the entity ID of its sensor."""
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    return {
        registered.unique_id[len(prefix) :]: registered.entity_id
        for registered in er.async_entries_for_config_entry(registry, entry.entry_id)
        if registered.domain == "sensor" and registered.unique_id.startswith(prefix)
    }


def group_entity_id(
    hass: HomeAssistant, entry: ConfigEntry, subentry_id: str | None, name: str
) -> str:
    """The entity ID of a group's sensor: the registered one, or the one a new group will get."""
    registry = er.async_get(hass)
    if subentry_id and (
        found := registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}{UNIQUE_MARK}{subentry_id}"
        )
    ):
        return found
    generate = (
        getattr(registry, "async_get_available_entity_id", None)
        or registry.async_generate_entity_id
    )
    return str(generate("sensor", f"Heads Up group {name}"))
