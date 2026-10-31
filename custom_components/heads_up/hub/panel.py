"""The admin panel: a custom panel registered with the frontend (N-69, N-77, N-88, D-117).

The sidebar entry exists only while the option `show_panel` is on. Registration is a function of
the option, so it is added and removed without a restart. The panel is a shell (`heads-up-panel.js`)
and one module per page under `frontend/panel/`, loaded when a page is opened.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel
from homeassistant.components.http.server import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from ..const import DOMAIN, OPT_SHOW_PANEL, PANEL_ICON, PANEL_TITLE, PANEL_URL_PATH

FRONTEND = Path(__file__).parent.parent / "frontend"
SHELL_FILE = FRONTEND / "heads-up-panel.js"
PAGES_DIR = FRONTEND / "panel"
SHELL_URL_PATH = "/heads_up/heads-up-panel.js"
PAGES_URL_PATH = "/heads_up/panel"
ELEMENT = "heads-up-panel"
_REGISTERED: HassKey[bool] = HassKey("heads_up_panel_registered")


async def async_register_panel_paths(hass: HomeAssistant) -> None:
    """Serve the shell and the pages. Static paths cannot be removed: this runs once per run."""
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(SHELL_URL_PATH, str(SHELL_FILE), cache_headers=True),
            StaticPathConfig(PAGES_URL_PATH, str(PAGES_DIR), cache_headers=True),
        ]
    )


def _digest() -> str:
    """One hash over the shell and every page, so a changed file changes every URL (N-52)."""
    sha = hashlib.sha256()
    for path in [SHELL_FILE, *sorted(PAGES_DIR.glob("*.js"))]:
        sha.update(path.name.encode())
        sha.update(path.read_bytes())
    return sha.hexdigest()[:8]


async def _version(hass: HomeAssistant) -> str:
    integration = await async_get_integration(hass, DOMAIN)
    digest = await hass.async_add_executor_job(_digest)
    return f"{integration.version}-{digest}"


async def async_sync_panel(hass: HomeAssistant, show: bool) -> None:
    """Add or remove the sidebar entry so it matches the option."""
    registered = hass.data.get(_REGISTERED, False)
    if show and not registered:
        version = await _version(hass)
        async_register_built_in_panel(
            hass,
            component_name="custom",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            frontend_url_path=PANEL_URL_PATH,
            config={
                "base": PAGES_URL_PATH,
                "v": version,
                "_panel_custom": {
                    "name": ELEMENT,
                    "embed_iframe": False,
                    "trust_external": False,
                    "handle_safe_area": False,
                    "module_url": f"{SHELL_URL_PATH}?v={version}",
                },
            },
            require_admin=True,  # hides the entry; the commands check admin themselves (N-69)
        )
        hass.data[_REGISTERED] = True
    elif not show and registered:
        async_remove_panel(hass, PANEL_URL_PATH)
        hass.data[_REGISTERED] = False


def wanted(options: dict[str, object]) -> bool:
    return bool(options.get(OPT_SHOW_PANEL, False))
