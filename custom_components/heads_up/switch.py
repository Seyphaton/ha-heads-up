"""One switch per policy (D-186): the action form lists them, and an automation can turn a
policy on or off. The switch is the policy's `enabled` setting, stored in its subentry, so the
panel and the switch always agree. A call may name the switch instead of the policy; the unique
ID holds the subentry ID, so a renamed policy keeps working."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, POLICY_SUBENTRY, SIGNAL_POLICIES
from .hub.policies.models import parse_policy

UNIQUE_MARK = "_policy_"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    added: set[str] = set()

    @callback
    def sync() -> None:
        wanted = {
            f"{prefix}{sid}": sid
            for sid, subentry in entry.subentries.items()
            if subentry.subentry_type == POLICY_SUBENTRY and parse_policy(subentry)
        }
        for unique_id, subentry_id in wanted.items():
            if unique_id not in added:
                added.add(unique_id)
                async_add_entities(
                    [PolicySwitch(entry, unique_id, subentry_id)], config_subentry_id=subentry_id
                )

    sync()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_POLICIES, sync))


class PolicySwitch(SwitchEntity):
    # No device, for the reason given in binary_sensor.py.
    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, unique_id: str, subentry_id: str) -> None:
        self._entry = entry
        self._subentry_id = subentry_id
        self._attr_unique_id = unique_id
        self._read()

    def _read(self) -> None:
        subentry = self._entry.subentries.get(self._subentry_id)
        policy = parse_policy(subentry) if subentry else None
        self._attr_available = policy is not None
        if policy is not None:
            self._attr_is_on = policy.enabled
            self._attr_name = f"Heads Up policy {policy.name}"
            attributes = policy.describe()
            # Position in the list of policies; "first" mode uses the first one that matches.
            hub = getattr(getattr(self._entry, "runtime_data", None), "hub", None)
            if hub is not None:
                ids = [p.subentry_id for p in hub.policies.ordered()]
                if self._subentry_id in ids:
                    attributes["order"] = ids.index(self._subentry_id) + 1
            self._attr_extra_state_attributes = attributes

    @callback
    def _changed(self) -> None:
        self._read()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_POLICIES, self._changed))

    def _set(self, enabled: bool) -> None:
        subentry = self._entry.subentries.get(self._subentry_id)
        if subentry is not None:
            self.hass.config_entries.async_update_subentry(
                self._entry, subentry, data={**subentry.data, "enabled": enabled}
            )

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._set(False)


def policy_name_for_entity(hass: HomeAssistant, entry: ConfigEntry, entity_id: str) -> str | None:
    """The policy a switch of this integration stands for, by its unique ID, or None."""
    registered = er.async_get(hass).async_get(entity_id)
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    if (
        registered is None
        or registered.platform != DOMAIN
        or registered.config_entry_id != entry.entry_id
        or not registered.unique_id.startswith(prefix)
    ):
        return None
    subentry = entry.subentries.get(registered.unique_id[len(prefix) :])
    return subentry.title if subentry else None
