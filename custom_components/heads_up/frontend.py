"""Serves the card, the popup loader and the popup module and registers them (N-8, N-9)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http.server import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN
from .hub.panel import async_register_panel_paths

CARD_URL_PATH = "/heads_up/heads-up-card.js"
CARD_FILE = Path(__file__).parent / "frontend" / "heads-up-card.js"
LOADER_URL_PATH = "/heads_up/heads-up-loader.js"
LOADER_FILE = Path(__file__).parent / "frontend" / "heads-up-loader.js"
POPUP_URL_PATH = "/heads_up/heads-up-popup.js"
POPUP_FILE = Path(__file__).parent / "frontend" / "heads-up-popup.js"
_ADDED_URL: HassKey[str] = HassKey("heads_up_card_url")
_ADDED_LOADER: HassKey[str] = HassKey("heads_up_loader_url")


async def async_register_card_path(hass: HomeAssistant) -> None:
    """Serve the module. Static paths cannot be removed, so this runs once per HA run.

    Cached by the browser: the URL carries a hash of the file, so a changed file has a new URL
    (D-064).
    """
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(CARD_URL_PATH, str(CARD_FILE), cache_headers=True),
            StaticPathConfig(LOADER_URL_PATH, str(LOADER_FILE), cache_headers=True),
            StaticPathConfig(POPUP_URL_PATH, str(POPUP_FILE), cache_headers=True),
        ]
    )
    await async_register_panel_paths(hass)


def _digest(path: Path = CARD_FILE) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


async def _versioned_url(hass: HomeAssistant, url_path: str, file: Path) -> str:
    """Module URL; the cache buster is the manifest version plus a hash of the file.

    The hash makes the URL change whenever the file changes, even if the version was not bumped
    (a browser may keep a module for a long time when the URL is the same, N-52).
    """
    integration = await async_get_integration(hass, DOMAIN)
    digest = await hass.async_add_executor_job(_digest, file)
    return f"{url_path}?v={integration.version}-{digest}"


async def async_card_url(hass: HomeAssistant) -> str:
    return await _versioned_url(hass, CARD_URL_PATH, CARD_FILE)


async def async_popup_url(hass: HomeAssistant) -> str:
    """The popup module, imported by the loader when the first popup is due (D-115)."""
    return await _versioned_url(hass, POPUP_URL_PATH, POPUP_FILE)


async def async_add_card(hass: HomeAssistant) -> None:
    url = await async_card_url(hass)
    hass.data[_ADDED_URL] = url
    add_extra_js_url(hass, url)
    # The loader runs on every page for every user; it is under 1 KB and does nothing unless
    # popups are enabled for the user (D-115).
    loader = await _versioned_url(hass, LOADER_URL_PATH, LOADER_FILE)
    hass.data[_ADDED_LOADER] = loader
    add_extra_js_url(hass, loader)


async def async_remove_card(hass: HomeAssistant) -> None:
    # Remove the URL that was added, not a recomputed one: the file may have changed since.
    if (url := hass.data.pop(_ADDED_URL, None)) is not None:
        remove_extra_js_url(hass, url)
    if (loader := hass.data.pop(_ADDED_LOADER, None)) is not None:
        remove_extra_js_url(hass, loader)
