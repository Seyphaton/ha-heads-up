"""Shared fixtures."""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

type CreateBanner = Callable[..., Awaitable[dict[str, Any]]]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom_components/ in every test."""


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
