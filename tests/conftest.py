"""Shared fixtures."""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceRegistry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

type CreateBanner = Callable[..., Awaitable[dict[str, Any]]]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom_components/ in every test."""


@pytest.fixture(autouse=True)
def notify_default_severity(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`heads_up.notify` requires `severity` (D-192). Most tests are about something else, so a
    call without one gets `info`. A test of the requirement uses `no_default_severity`."""
    if request.node.get_closest_marker("no_default_severity"):
        return
    original = ServiceRegistry.async_call

    async def call(self: ServiceRegistry, domain: str, service: str, data: Any = None, **kw: Any):  # type: ignore[no-untyped-def]
        if domain == DOMAIN and service == "notify" and isinstance(data, dict):
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
