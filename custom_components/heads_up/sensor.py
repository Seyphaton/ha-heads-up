"""Count of active banners (D-013): stored, not waiting for a condition. Global, not per user.

Also one sensor per recipient group (D-201): a call names a group by the entity ID of its
sensor, whose unique ID holds the subentry ID, so renaming the group does not break the call.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN, GROUP_SUBENTRY, INBOX_PURGE_GRACE, SIGNAL_AUDIENCES
from .manager import BannerManager

UNIQUE_MARK = "_group_"
INBOX_MARK = "_inbox_"


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
    _setup_inbox_sensors(hass, entry, async_add_entities)


def _setup_inbox_sensors(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """One unread-count sensor per person entity (D-264): added when the person appears, and
    removed when the person has been gone for a while (a reload of the person integration removes
    and adds the entity again)."""
    manager: BannerManager = entry.runtime_data
    if manager.hub is None:
        return
    inbox = manager.hub.inbox
    added: set[str] = set()
    leaving: dict[str, CALLBACK_TYPE] = {}

    @callback
    def add(person: str) -> None:
        if person not in added:
            added.add(person)
            state = hass.states.get(person)
            name = state.attributes.get("friendly_name") if state else None
            async_add_entities(
                [InboxSensor(entry, inbox, person, str(name or person.split(".", 1)[1]))]
            )

    @callback
    def remove(person: str) -> None:
        added.discard(person)
        registry = er.async_get(hass)
        if found := registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}{INBOX_MARK}{person}"
        ):
            registry.async_remove(found)

    @callback
    def person_changed(event: Event[EventStateChangedData]) -> None:
        person = event.data["entity_id"]
        if event.data["new_state"] is not None:
            if (cancel := leaving.pop(person, None)) is not None:
                cancel()
            add(person)
            return
        if person in leaving or person not in added:
            return

        @callback
        def gone(_now: datetime) -> None:
            leaving.pop(person, None)
            if hass.states.get(person) is None:
                remove(person)

        leaving[person] = async_call_later(hass, INBOX_PURGE_GRACE, gone)

    for state in hass.states.async_all("person"):
        add(state.entity_id)
    entry.async_on_unload(
        hass.bus.async_listen(EVENT_STATE_CHANGED, person_changed, event_filter=_is_person)
    )

    @callback
    def stop() -> None:
        for cancel in leaving.values():
            cancel()
        leaving.clear()

    entry.async_on_unload(stop)


@callback
def _is_person(data: EventStateChangedData | Any) -> bool:
    return str(data["entity_id"]).startswith("person.")


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


class InboxSensor(SensorEntity):
    """The unread count of one person's inbox. Counts only: every user can read entity states,
    so no title or text is ever here (D-264)."""

    _attr_has_entity_name = True
    _attr_translation_key = "inbox"
    _attr_should_poll = False
    _attr_icon = "mdi:inbox"

    def __init__(self, entry: ConfigEntry, inbox: Any, person: str, name: str) -> None:
        self._inbox = inbox
        self._person = person
        self._attr_unique_id = f"{entry.entry_id}{INBOX_MARK}{person}"
        self._attr_translation_placeholders = {"person": name}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Heads Up",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _state(self) -> Any:
        return self.hass.states.get(self._person)

    @property
    def available(self) -> bool:
        return self._state() is not None

    @property
    def native_value(self) -> int:
        return int(self._inbox.unread_count(self._person))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "person": self._person,
            "needs_action": self._inbox.needs_action(self._person),
            "unread_critical": self._inbox.unread_critical(self._person),
        }

    def _name(self) -> str:
        state = self._state()
        return str(
            (state.attributes.get("friendly_name") if state else None)
            or self._person.split(".", 1)[1]
        )

    @callback
    def _changed(self, *_: Any) -> None:
        self._attr_translation_placeholders = {"person": self._name()}
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self._attr_translation_placeholders = {"person": self._name()}
        self.async_on_remove(self._inbox.subscribe(self._changed))
        person = self._person

        @callback
        def mine(data: Any) -> bool:
            return bool(data["entity_id"] == person)

        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_STATE_CHANGED, self._changed, event_filter=mine)
        )
