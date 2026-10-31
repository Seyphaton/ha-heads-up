"""Shared set-up for the policy tests: two people with phones, policies, a message to Anna."""

from dataclasses import dataclass
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant, ServiceCall
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import FakeDevice, set_person, settle, tick

ESCALATION: dict[str, Any] = {
    "type": "escalation",
    "after_minutes": 5,
    "channels": ["push"],
    "targets": {"push": {"recipients": ["person.ben"]}},
}
REMINDER: dict[str, Any] = {"type": "reminder", "every_minutes": 10, "max_count": 2}


@dataclass
class Household:
    anna: FakeDevice
    ben: FakeDevice


async def make_household(hass: HomeAssistant, mobile_app_device: AddDevice) -> Household:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home", user_id="ben-id")
    anna = await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )
    ben = await mobile_app_device("Ben's phone", user_id="ben-id", person_entity_id="person.ben")
    return Household(anna, ben)


async def add_policy(
    hass: HomeAssistant, entry: MockConfigEntry, name: str, **data: Any
) -> ConfigSubentry:
    subentry = ConfigSubentry(data=data, subentry_type="policy", title=name, unique_id=None)
    hass.config_entries.async_add_subentry(entry, subentry)
    await hass.async_block_till_done()
    return subentry


async def send(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> None:
    body = {
        "id": "m",
        "message": "Water leak",
        "severity": "critical",
        "channels": ["banner", "push"],
        "to": {"push": {"recipients": ["person.anna"]}},
        **data,
    }
    await hass.services.async_call(DOMAIN, "notify", body, blocking=True)
    await settle(hass, entry)


async def wait(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory, minutes: float
) -> None:
    await tick(hass, freezer, minutes * 60)
    await settle(hass, entry)


def pushes(phone: FakeDevice) -> list[ServiceCall]:
    return [c for c in phone.calls if c.data.get("message") != "clear_notification"]


def trace(entry: MockConfigEntry) -> list[dict[str, Any]]:
    return [dict(e) for e in entry.runtime_data.hub.trace.entries("m")]


QUIET: dict[str, Any] = {
    "type": "quiet_hours",
    "from_time": "22:00:00",
    "to_time": "07:00:00",
    "action": "quiet",
}
AWAY: dict[str, Any] = {"type": "away"}
FALLBACK: dict[str, Any] = {
    "type": "fallback",
    "when": "no_audience",
    "channels": ["push"],
    "targets": {"push": {"recipients": ["person.ben"]}},
}


async def add_audience(hass: HomeAssistant, entry: MockConfigEntry, name: str, **data: Any) -> None:
    hass.config_entries.async_add_subentry(
        entry, ConfigSubentry(data=data, subentry_type="audience", title=name, unique_id=None)
    )
    await hass.async_block_till_done()


def move(hass: HomeAssistant, person: str, state: str) -> None:
    """Change a person's state, keeping their user and trackers (`set_person` resets them)."""
    current = hass.states.get(person)
    hass.states.async_set(person, state, dict(current.attributes) if current else {})
