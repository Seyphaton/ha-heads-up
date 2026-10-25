"""Serves the card module and registers it with the frontend (N-8, N-9)."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http.server import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

CARD_URL_PATH = "/heads_up/heads-up-card.js"
CARD_FILE = Path(__file__).parent / "frontend" / "heads-up-card.js"


async def async_register_card_path(hass: HomeAssistant) -> None:
    """Serve the module. Static paths cannot be removed, so this runs once per HA run."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL_PATH, str(CARD_FILE), cache_headers=False)]
    )


async def async_card_url(hass: HomeAssistant) -> str:
    """Module URL with the manifest version as cache buster."""
    integration = await async_get_integration(hass, DOMAIN)
    return f"{CARD_URL_PATH}?v={integration.version}"


async def async_add_card(hass: HomeAssistant) -> None:
    add_extra_js_url(hass, await async_card_url(hass))


async def async_remove_card(hass: HomeAssistant) -> None:
    remove_extra_js_url(hass, await async_card_url(hass))
