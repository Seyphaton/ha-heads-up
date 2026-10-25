"""WebSocket commands for the card (DESIGN §6; patterns: HA_API_NOTES N-4, N-5).

Banner IDs travel as `banner_id` because `id` is the WebSocket message ID.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.websocket_api import async_register_command
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.const import ERR_UNAUTHORIZED
from homeassistant.components.websocket_api.decorators import require_admin, websocket_command
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .manager import BannerManager, HeadsUpError


def _manager(
    hass: HomeAssistant, connection: ActiveConnection, msg_id: int
) -> BannerManager | None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        connection.send_error(msg_id, "not_loaded", "Heads Up is not set up")
        return None
    manager: BannerManager = entries[0].runtime_data
    return manager


@websocket_command(
    {vol.Required("type"): "heads_up/subscribe", vol.Optional("show_all", default=False): bool}
)
@callback
def ws_subscribe(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    show_all: bool = msg["show_all"]
    if show_all and not connection.user.is_admin:
        connection.send_error(msg["id"], ERR_UNAUTHORIZED, "show_all requires admin")
        return
    user_id = connection.user.id

    @callback
    def forward() -> None:
        connection.send_event(msg["id"], {"banners": manager.visible(user_id, show_all)})

    connection.subscriptions[msg["id"]] = manager.subscribe(forward)
    connection.send_result(msg["id"])
    forward()


@websocket_command({vol.Required("type"): "heads_up/dismiss", vol.Required("banner_id"): str})
@callback
def ws_dismiss(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.dismiss(msg["banner_id"], connection.user.id)
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@websocket_command(
    {
        vol.Required("type"): "heads_up/dismiss_many",
        vol.Required("banner_ids"): [str],
    }
)
@callback
def ws_dismiss_many(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    dismissed, skipped = manager.dismiss_many(msg["banner_ids"], connection.user.id)
    connection.send_result(msg["id"], {"dismissed": dismissed, "skipped": skipped})


@websocket_command({vol.Required("type"): "heads_up/admin_clear", vol.Required("banner_id"): str})
@require_admin
@callback
def ws_admin_clear(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.admin_clear(msg["banner_id"])
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (ws_subscribe, ws_dismiss, ws_dismiss_many, ws_admin_clear):
        async_register_command(hass, command)
