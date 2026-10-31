"""Recipient profiles, devices and groups (DESIGN §23.7, D-088, N-70, N-71, N-78).

A person's Companion devices are found from `person.device_trackers` through the entity registry
to the `mobile_app` registration. The hub keeps the registration's `device_id`, never the notify
service name: the app can rename a device, which renames the service (N-78), so the service is
worked out from the registration's `device_name` when it is needed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from ..const import GROUP_SUBENTRY, PROFILE_CHANNELS, PROFILE_SUBENTRY

MOBILE_APP = "mobile_app"
SPEAKER_DOMAINS = ("media_player", "assist_satellite")


@dataclass(frozen=True, slots=True)
class Device:
    device_id: str  # the registration's id
    name: str | None  # None: the registration no longer exists
    service: str | None
    service_found: bool
    source: str  # "detected" or "manual"


@dataclass(frozen=True, slots=True)
class StoredProfile:
    """What the user changed on top of the detected devices."""

    person: str
    manual: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    primary: str | None = None
    channels: tuple[str, ...] = PROFILE_CHANNELS


@dataclass(slots=True)
class Profile:
    person: str
    devices: list[Device] = field(default_factory=list)
    primary: str | None = None
    channels: tuple[str, ...] = PROFILE_CHANNELS
    customized: bool = False

    @property
    def usable(self) -> list[Device]:
        return [d for d in self.devices if d.service_found]


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    members: tuple[str, ...] = ()
    areas: tuple[str, ...] = ()


def notify_service(device_name: str) -> str:
    """Name of the legacy notify service of a `mobile_app` registration (N-70)."""
    return slugify(f"{MOBILE_APP}_{device_name}")


def registrations(hass: HomeAssistant) -> dict[str, str]:
    """Every Companion registration: device_id to device_name."""
    return {
        str(e.data["device_id"]): str(e.data.get("device_name", ""))
        for e in hass.config_entries.async_entries(MOBILE_APP)
        if e.data.get("device_id")
    }


def registration_data(hass: HomeAssistant, device_id: str) -> Mapping[str, Any] | None:
    """Data of a `mobile_app` registration (device_name, os_name, ...), or None."""
    for entry in hass.config_entries.async_entries(MOBILE_APP):
        if entry.data.get("device_id") == device_id:
            return entry.data
    return None


def _device(hass: HomeAssistant, device_id: str, names: Mapping[str, str], source: str) -> Device:
    if (name := names.get(device_id)) is None:
        return Device(device_id, None, None, False, source)
    service = notify_service(name)
    return Device(device_id, name, service, hass.services.has_service("notify", service), source)


def detect_device_ids(hass: HomeAssistant, person_entity_id: str) -> list[str]:
    """Registrations behind the person's trackers; trackers of other integrations are skipped."""
    state = hass.states.get(person_entity_id)
    if state is None:
        return []
    registry = er.async_get(hass)
    found: list[str] = []
    for tracker in state.attributes.get("device_trackers") or []:
        entry = registry.async_get(tracker)
        # A `mobile_app` tracker's unique_id is the registration's device_id (N-71).
        if entry is None or entry.platform != MOBILE_APP or entry.unique_id in found:
            continue
        found.append(entry.unique_id)
    return found


def build_profile(
    hass: HomeAssistant, person_entity_id: str, stored: StoredProfile | None
) -> Profile:
    names = registrations(hass)
    ids = [
        i
        for i in detect_device_ids(hass, person_entity_id)
        if i not in (stored.removed if stored else ())
    ]
    devices = [_device(hass, i, names, "detected") for i in ids]
    if stored:
        devices += [_device(hass, i, names, "manual") for i in stored.manual if i not in ids]
    primary = stored.primary if stored else None
    if primary is None and devices:
        primary = devices[0].device_id
    return Profile(
        person=person_entity_id,
        devices=devices,
        primary=primary,
        channels=stored.channels if stored else PROFILE_CHANNELS,
        customized=stored is not None,
    )


def parse_profile(subentry: ConfigSubentry) -> StoredProfile | None:
    data = subentry.data
    if subentry.subentry_type != PROFILE_SUBENTRY or not data.get("person"):
        return None
    channels = tuple(c for c in data.get("channels", PROFILE_CHANNELS) if c in PROFILE_CHANNELS)
    return StoredProfile(
        person=str(data["person"]),
        manual=tuple(data.get("devices", ())),
        removed=tuple(data.get("removed_devices", ())),
        primary=data.get("primary") or None,
        channels=channels,
    )


def parse_group(subentry: ConfigSubentry) -> Group | None:
    if subentry.subentry_type != GROUP_SUBENTRY:
        return None
    return Group(
        subentry.title,
        tuple(subentry.data.get("members", ())),
        tuple(subentry.data.get("areas", ())),
    )


def area_speakers(hass: HomeAssistant, area_id: str) -> list[str]:
    """Speakers and satellites of an area: the entity's own area, else its device's."""
    entities, devices = er.async_get(hass), dr.async_get(hass)
    found: list[str] = []
    for entry in entities.entities.values():
        if entry.domain not in SPEAKER_DOMAINS:
            continue
        area = entry.area_id
        if area is None and entry.device_id and (device := devices.async_get(entry.device_id)):
            area = device.area_id
        if area == area_id:
            found.append(entry.entity_id)
    return sorted(found)


def area_exists(hass: HomeAssistant, area_id: str) -> bool:
    return ar.async_get(hass).async_get_area(area_id) is not None


def speaker_entities(hass: HomeAssistant) -> list[str]:
    return sorted(s.entity_id for d in SPEAKER_DOMAINS for s in hass.states.async_all(d))


def unique(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))
