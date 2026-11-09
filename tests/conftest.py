"""Shared fixtures."""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceRegistry
from homeassistant.util import slugify
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

type CreateBanner = Callable[..., Awaitable[dict[str, Any]]]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom_components/ in every test."""


def with_entity_ids(data: dict[str, Any]) -> dict[str, Any]:
    """A call written with audience and policy names, with the entity IDs the action needs
    (D-198). The IDs follow from the names: `At home` is the sensor
    `binary_sensor.heads_up_audience_at_home`."""

    def audience(value: Any) -> Any:
        if isinstance(value, str) and "." not in value:
            return f"binary_sensor.heads_up_audience_{slugify(value)}"
        return value

    def policy(value: Any) -> Any:
        if isinstance(value, list):
            return [policy(v) for v in value]
        if isinstance(value, str) and "." not in value and value.casefold() not in KEYWORDS:
            return f"switch.heads_up_policy_{slugify(value)}"
        return value

    out = dict(data)
    if "audience" in out:
        out["audience"] = audience(out["audience"])
    if "policy" in out:
        out["policy"] = policy(out["policy"])
    if isinstance(out.get("to"), dict):
        out["to"] = {
            channel: {**t, "audience": audience(t["audience"])} if "audience" in t else t
            for channel, t in out["to"].items()
        }
    return out


KEYWORDS = ("none", "automatic")


@pytest.fixture(autouse=True)
def notify_default_severity(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`heads_up.notify` requires `severity` (D-192) and names an audience and a policy by entity
    ID (D-198). Most tests are about something else, so a call without a severity gets `info`
    and a name becomes its entity ID. A test of either rule uses `no_default_severity` or
    `names_as_given`."""
    default_severity = not request.node.get_closest_marker("no_default_severity")
    ids = not request.node.get_closest_marker("names_as_given")
    if not (default_severity or ids):
        return
    original = ServiceRegistry.async_call

    async def call(self: ServiceRegistry, domain: str, service: str, data: Any = None, **kw: Any):  # type: ignore[no-untyped-def]
        if domain == DOMAIN and isinstance(data, dict):
            if ids and service in ("notify", "push", "popup", "speak", "create_banner"):
                data = with_entity_ids(data)
            if default_severity and service == "notify":
                data = {"severity": "info", **data}
        return await original(self, domain, service, data, **kw)

    monkeypatch.setattr(ServiceRegistry, "async_call", call)


@pytest.fixture
def options() -> dict[str, Any]:
    """Entry options; override in a test module to change limits or defaults."""
    return {}


@pytest.fixture
async def entry(hass: HomeAssistant, options: dict[str, Any]) -> MockConfigEntry:
    """A loaded Heads Up config entry."""
    entry = MockConfigEntry(domain=DOMAIN, options=options)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.fixture
def create(hass: HomeAssistant, entry: MockConfigEntry) -> CreateBanner:
    """Call heads_up.create_banner and return its response data."""

    async def _create(**data: Any) -> dict[str, Any]:
        response = await hass.services.async_call(
            DOMAIN, "create_banner", data, blocking=True, return_response=True
        )
        assert response is not None
        return dict(response)

    return _create


def banners(entry: MockConfigEntry) -> dict[str, Any]:
    """Current banners by id, as stored by the manager."""
    return {b.id: b for b in entry.runtime_data.banners.values()}


def options_input(sections: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """The options form always sends every section; fields left out keep their stored value."""
    from custom_components.heads_up.hub import settings

    return {name: dict(sections.get(name, {})) for name, _ in settings.SECTIONS}
