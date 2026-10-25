"""Serving the card module (N-8, N-9, D-021)."""

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.heads_up.const import DOMAIN


async def _card_url(hass: HomeAssistant) -> str:
    integration = await async_get_integration(hass, DOMAIN)
    return f"/heads_up/heads-up-card.js?v={integration.version}"


async def test_module_registered_with_version_query(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert await _card_url(hass) in hass.data[DATA_EXTRA_MODULE_URL].urls


async def test_module_removed_on_unload_and_readded_on_reload(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    url = await _card_url(hass)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert url not in hass.data[DATA_EXTRA_MODULE_URL].urls

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert url in hass.data[DATA_EXTRA_MODULE_URL].urls


async def test_module_is_served(
    hass: HomeAssistant, entry: MockConfigEntry, hass_client: ClientSessionGenerator
) -> None:
    client = await hass_client()
    response = await client.get("/heads_up/heads-up-card.js")
    assert response.status == 200
    body = await response.text()
    assert 'customElements.define("heads-up-card"' in body
