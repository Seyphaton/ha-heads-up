"""One binary sensor per audience (D-186).

The action form can only offer a dropdown of things that exist as entities, so every audience is
one: on while at least one person is in it. A call may name the entity instead of the audience;
the entity's unique ID holds the built-in kind or the subentry ID, so a renamed audience keeps
working. Built-in audiences the admin switched off have no entity.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import AUDIENCE_SUBENTRY, BUILTIN_AUDIENCES, DOMAIN, SIGNAL_AUDIENCES
from .hub.audiences import parse_audience

UNIQUE_MARK = "_audience_"
# The state of an audience entity is for display: it uses the severity that skips unknown
# presence, as most messages do.
DISPLAY_SEVERITY = "warning"


@callback
def _is_person(data: Any) -> bool:
    return str(data.get("entity_id", "")).startswith("person.")


@callback
def notify_audiences_changed(hass: HomeAssistant) -> None:
    """Tell the entities that audiences, options or presence changed."""
    async_dispatcher_send(hass, SIGNAL_AUDIENCES)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    hub = entry.runtime_data.hub
    if hub is None:
        return
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    added: set[str] = set()

    @callback
    def sync() -> None:
        wanted: dict[str, tuple[str, str | None]] = {}  # unique ID: key, subentry ID
        for name, kind in BUILTIN_AUDIENCES.items():
            if name not in hub.resolver.disabled_audiences():
                wanted[f"{prefix}{kind}"] = (kind, None)
        for subentry_id, subentry in entry.subentries.items():
            if subentry.subentry_type == AUDIENCE_SUBENTRY and parse_audience(subentry):
                wanted[f"{prefix}{subentry_id}"] = (subentry_id, subentry_id)
        for unique_id, (key, owner) in wanted.items():
            if unique_id not in added:
                added.add(unique_id)
                async_add_entities(
                    [AudienceSensor(entry, unique_id, key, owner)],
                    config_subentry_id=owner,
                )
        # A deleted subentry is cleared by Home Assistant; a switched-off built-in is not.
        registry = er.async_get(hass)
        for registered in er.async_entries_for_config_entry(registry, entry.entry_id):
            if (
                registered.domain == "binary_sensor"
                and registered.unique_id.startswith(prefix)
                and registered.unique_id not in wanted
            ):
                registry.async_remove(registered.entity_id)
                added.discard(registered.unique_id)

    sync()
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_AUDIENCES, sync))


class AudienceSensor(BinarySensorEntity):
    # No device: entities of several subentries must not share one, because Home Assistant moves
    # the device to the last subentry and drops the entities of the others (seen on the dev
    # instance). The name carries the prefix instead.
    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(
        self, entry: ConfigEntry, unique_id: str, key: str, subentry_id: str | None
    ) -> None:
        self._entry = entry
        self._key = key
        self._subentry_id = subentry_id
        self._attr_unique_id = unique_id
        self._attr_name = f"Heads Up audience {self._name() or key}"
        self._refreshing = False

    def _name(self) -> str | None:
        if self._subentry_id is not None:
            subentry = self._entry.subentries.get(self._subentry_id)
            return subentry.title if subentry else None
        return next((n for n, kind in BUILTIN_AUDIENCES.items() if kind == self._key), None)

    async def _refresh(self) -> None:
        hub = self._entry.runtime_data.hub
        name = self._name()
        audience = hub.resolver.audience(name) if hub is not None and name else None
        if audience is None:
            self._attr_available = False
        else:
            members = await hub.resolver.members(audience, DISPLAY_SEVERITY)
            self._attr_available = True
            self._attr_is_on = bool(members.recipients)
            self._attr_extra_state_attributes = {
                "audience": name,
                "members": [m.key for m in members.recipients],
            }
            self._attr_name = f"Heads Up audience {name}"

    @callback
    def _schedule(self, *_: Any) -> None:
        self._entry.async_create_background_task(
            self.hass, self._refresh_and_write(), f"{DOMAIN}_audience_{self._key}"
        )

    async def _refresh_and_write(self) -> None:
        await self._refresh()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await self._refresh()
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_AUDIENCES, self._schedule))
        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_STATE_CHANGED,
                self._schedule,
                event_filter=_is_person,
            )
        )


def audience_entity_id(
    hass: HomeAssistant, entry: ConfigEntry, subentry_id: str | None, name: str
) -> str:
    """The entity ID of a custom audience's sensor: the registered one, which a rename does not
    change, or the one Home Assistant will give a new audience (D-198)."""
    registry = er.async_get(hass)
    if subentry_id and (
        found := registry.async_get_entity_id(
            "binary_sensor", DOMAIN, f"{entry.entry_id}{UNIQUE_MARK}{subentry_id}"
        )
    ):
        return found
    generate = (
        getattr(registry, "async_get_available_entity_id", None)
        or registry.async_generate_entity_id
    )
    return str(generate("binary_sensor", f"Heads Up audience {name}"))


def audience_entity_ids(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Audience name to the entity ID of its sensor, for every audience that has one."""
    registry = er.async_get(hass)
    found: dict[str, str] = {}
    for registered in er.async_entries_for_config_entry(registry, entry.entry_id):
        if registered.domain == "binary_sensor" and (
            name := audience_name_for_entity(hass, entry, registered.entity_id)
        ):
            found[name] = registered.entity_id
    return found


def audience_name_for_entity(hass: HomeAssistant, entry: ConfigEntry, entity_id: str) -> str | None:
    """The audience an entity of this integration stands for, by its unique ID, or None."""
    registered = er.async_get(hass).async_get(entity_id)
    prefix = f"{entry.entry_id}{UNIQUE_MARK}"
    if (
        registered is None
        or registered.platform != DOMAIN
        or registered.config_entry_id != entry.entry_id
        or not registered.unique_id.startswith(prefix)
    ):
        return None
    key = registered.unique_id[len(prefix) :]
    for name, kind in BUILTIN_AUDIENCES.items():
        if kind == key:
            return name
    subentry = entry.subentries.get(key)
    return subentry.title if subentry else None


__all__ = [
    "AudienceSensor",
    "async_setup_entry",
    "audience_entity_id",
    "audience_entity_ids",
    "audience_name_for_entity",
    "notify_audiences_changed",
]
