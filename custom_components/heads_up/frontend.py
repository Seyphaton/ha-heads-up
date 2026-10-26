"""Serves the card module and registers it with the frontend (N-8, N-9)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http.server import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN

CARD_URL_PATH = "/heads_up/heads-up-card.js"
CARD_FILE = Path(__file__).parent / "frontend" / "heads-up-card.js"
_ADDED_URL: HassKey[str] = HassKey("heads_up_card_url")


async def async_register_card_path(hass: HomeAssistant) -> None:
    """Serve the module. Static paths cannot be removed, so this runs once per HA run.

    Cached by the browser: the URL carries a hash of the file, so a changed file has a new URL
    (D-064).
    """
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL_PATH, str(CARD_FILE), cache_headers=True)]
    )


def _digest() -> str:
    return hashlib.sha256(CARD_FILE.read_bytes()).hexdigest()[:8]


async def async_card_url(hass: HomeAssistant) -> str:
    """Module URL; the cache buster is the manifest version plus a hash of the file.

    The hash makes the URL change whenever the file changes, even if the version was not bumped
    (a browser may keep a module for a long time when the URL is the same, N-52).
    """
    integration = await async_get_integration(hass, DOMAIN)
    digest = await hass.async_add_executor_job(_digest)
    return f"{CARD_URL_PATH}?v={integration.version}-{digest}"


async def async_add_card(hass: HomeAssistant) -> None:
    url = await async_card_url(hass)
    hass.data[_ADDED_URL] = url
    add_extra_js_url(hass, url)


async def async_remove_card(hass: HomeAssistant) -> None:
    # Remove the URL that was added, not a recomputed one: the file may have changed since.
    if (url := hass.data.pop(_ADDED_URL, None)) is not None:
        remove_extra_js_url(hass, url)
