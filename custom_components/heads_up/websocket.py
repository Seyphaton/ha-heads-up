"""WebSocket commands for the card (DESIGN §6; patterns: HA_API_NOTES N-4, N-5).

Banner IDs travel as `banner_id` because `id` is the WebSocket message ID.
"""

from __future__ import annotations

from typing import Any

import probatio as vol
from homeassistant.components.websocket_api import async_register_command
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.const import ERR_UNAUTHORIZED
from homeassistant.components.websocket_api.decorators import (
    async_response,
    require_admin,
    websocket_command,
)
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, SEVERITIES
from .frontend import async_popup_url
from .hub import panel_config, panel_data, panel_test, settings, welcome
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
    {
        vol.Required("type"): "heads_up/subscribe",
        vol.Optional("show_all", default=False): bool,
        vol.Optional("show_snoozed", default=False): bool,
    }
)
@callback
def ws_subscribe(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    show_all: bool = msg["show_all"]
    if show_all and not connection.user.is_admin:
        connection.send_error(msg["id"], ERR_UNAUTHORIZED, "show_all requires admin")
        return
    show_snoozed: bool = msg["show_snoozed"]
    user_id = connection.user.id

    @callback
    def forward() -> None:
        connection.send_event(
            msg["id"], {"banners": manager.visible(user_id, show_all, show_snoozed)}
        )

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


@websocket_command({vol.Required("type"): "heads_up/acknowledge", vol.Required("banner_id"): str})
@callback
def ws_acknowledge(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.acknowledge(msg["banner_id"], connection.user.id)
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@websocket_command({vol.Required("type"): "heads_up/popup_config"})
@async_response
async def ws_popup_config(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Whether popups are on, how each severity looks, and the popup module (D-115)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    channel = manager.hub.channels.get("popup") if manager.hub is not None else None
    if channel is None or not channel.available:
        connection.send_result(msg["id"], {"enabled": False})
        return
    connection.send_result(
        msg["id"],
        {
            "enabled": True,
            "styles": channel.styles(),  # type: ignore[attr-defined]
            "module": await async_popup_url(hass),
        },
    )


@websocket_command({vol.Required("type"): "heads_up/popup_subscribe"})
@callback
def ws_popup_subscribe(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The popups of the calling user, now and whenever they change."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    channel = manager.hub.channels.get("popup") if manager.hub is not None else None
    if channel is None or not channel.available:
        connection.send_error(msg["id"], "hub_off", "Popups are switched off")
        return
    user_id = connection.user.id

    @callback
    def forward() -> None:
        connection.send_event(msg["id"], {"messages": channel.messages_for(user_id)})  # type: ignore[attr-defined]

    connection.subscriptions[msg["id"]] = channel.subscribe(forward)  # type: ignore[attr-defined]
    connection.send_result(msg["id"])
    forward()


def _entry(hass: HomeAssistant, connection: ActiveConnection, msg_id: int) -> Any:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        connection.send_error(msg_id, "not_loaded", "Heads Up is not set up")
        return None
    return entries[0]


@websocket_command({vol.Required("type"): "heads_up/settings_get"})
@require_admin
@callback
def ws_settings_get(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Everything the Settings page shows (D-117)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    manager: BannerManager = entry.runtime_data
    connection.send_result(
        msg["id"],
        {
            "options": settings.read_options(manager),
            "layout": settings.layout(),
            "install_token": settings.token(manager),
            "people": settings.people(hass, manager),
            "welcome_seen": bool(entry.options.get(welcome.OPT_WELCOME_SEEN, False)),
        },
    )


@websocket_command(
    {
        vol.Required("type"): "heads_up/settings_set",
        **settings.schema_fields(),
    }
)
@require_admin
@callback
def ws_settings_set(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Change options. The integration's own options form keeps working (D-117)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    changes = settings.to_stored({key: msg[key] for key in settings.EDITABLE if key in msg})
    hass.config_entries.async_update_entry(entry, options={**entry.options, **changes})
    connection.send_result(msg["id"], {"options": settings.read_options(entry.runtime_data)})


@websocket_command({vol.Required("type"): "heads_up/welcome_get"})
@require_admin
@callback
def ws_welcome_get(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """What the welcome shows: the default policies, what is missing and what can be chosen."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    hub = entry.runtime_data.hub
    connection.send_result(
        msg["id"],
        {
            "show": hub is not None and not entry.options.get(welcome.OPT_WELCOME_SEEN, False),
            "hub": hub is not None,
            "items": welcome.overview(entry),
            "audiences": hub.audiences.names() if hub else [],
            "default_audience": welcome.DEFAULT_AUDIENCE,
            "speakers": hub.recipients.known("speak") if hub else [],
        },
    )


@websocket_command(
    {
        vol.Required("type"): "heads_up/welcome_apply",
        vol.Required("items"): [vol.In(list(welcome.ITEMS))],
        vol.Optional("audience", default=welcome.DEFAULT_AUDIENCE): str,
        vol.Optional("speakers", default=list): [str],
    }
)
@require_admin
@callback
def ws_welcome_apply(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Create the default policies of the chosen items and remember the welcome was seen."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    hub = entry.runtime_data.hub
    if hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    if msg["audience"] not in hub.audiences.names():
        connection.send_error(
            msg["id"], "unknown_audience", f"Audience {msg['audience']} not found"
        )
        return
    if unknown := [s for s in msg["speakers"] if not hub.recipients.accepts("speak", s)]:
        connection.send_error(msg["id"], "unknown_recipient", f"Unknown speaker {unknown[0]}")
        return
    connection.send_result(
        msg["id"], welcome.apply(hass, entry, msg["items"], msg["audience"], msg["speakers"])
    )


@websocket_command({vol.Required("type"): "heads_up/panel_overview"})
@require_admin
@callback
def ws_panel_overview(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The Overview page: active messages and their states, rules, needs attention, the log."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    connection.send_result(msg["id"], panel_data.overview(hass, entry.runtime_data, entry))


@websocket_command({vol.Required("type"): "heads_up/panel_messages"})
@require_admin
@callback
def ws_panel_messages(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The Messages page: recent messages with their delivery results."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    connection.send_result(msg["id"], {"messages": panel_data.messages(entry.runtime_data)})


@websocket_command({vol.Required("type"): "heads_up/panel_trace", vol.Required("message_id"): str})
@require_admin
@callback
def ws_panel_trace(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """The delivery trace of one message: entries, deliveries, timers, acknowledgements."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    result = panel_data.trace(hass, entry.runtime_data, msg["message_id"])
    if result is None:
        connection.send_error(msg["id"], "not_found", f"Message {msg['message_id']} not found")
        return
    connection.send_result(msg["id"], result)


@websocket_command({vol.Required("type"): "heads_up/panel_config"})
@require_admin
@async_response
async def ws_panel_config(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Everything the editors show: audiences, groups, profiles, policies, choices, channels."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    connection.send_result(msg["id"], await panel_config.editors(hass, entry.runtime_data, entry))


@websocket_command(
    {
        vol.Required("type"): "heads_up/channels_set",
        vol.Optional("push_levels"): {str: str},
        vol.Optional("popup_styles"): {str: str},
        vol.Optional("push_lockscreen"): str,
        vol.Optional("push_sticky"): bool,
        vol.Optional("push_channel_id"): str,
        vol.Optional("speak_language"): vol.All(str, vol.Length(max=20)),
        vol.Optional("mail_service"): str,
        vol.Optional("mail_global_address"): str,
        vol.Optional("mail_subject"): str,
        vol.Optional("mail_body"): str,
    }
)
@require_admin
@callback
def ws_channels_set(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """The settings of the Channels page (D-119); the same options the options form keeps."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    changes = {key: msg[key] for key in panel_config.CHANNEL_KEYS if key in msg}
    if errors := panel_config.check_channels(changes, hass):
        connection.send_error(
            msg["id"], "invalid_format", ", ".join(f"{k}: {v}" for k, v in errors.items())
        )
        return
    hass.config_entries.async_update_entry(entry, options={**entry.options, **changes})
    connection.send_result(msg["id"], panel_config.channel_settings(entry.runtime_data))


_TEST_CALL: dict[Any, Any] = {
    vol.Required("message"): str,
    vol.Required("channels"): [str],
    vol.Optional("title"): str,
    vol.Optional("tts_message"): str,
    vol.Optional("severity"): str,
    vol.Optional("tag"): str,
    vol.Optional("policy"): str,
    vol.Optional("to"): {str: dict},
}


@websocket_command({vol.Required("type"): "heads_up/hub_plan", **_TEST_CALL})
@require_admin
@async_response
async def ws_hub_plan(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The dry run of Test send: what a call would do now. Sends nothing (D-120)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    payload = {k: v for k, v in msg.items() if k not in ("id", "type")}
    try:
        message = panel_test.build(manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], await manager.hub.preview(message))


@websocket_command({vol.Required("type"): "heads_up/hub_test_send", **_TEST_CALL})
@require_admin
@async_response
async def ws_hub_test_send(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The one real send of the panel: the call with the test marker (D-120)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    payload = {k: v for k, v in msg.items() if k not in ("id", "type")}
    try:
        result = await panel_test.send(hass, manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_command({vol.Required("type"): "heads_up/hub_usage", vol.Required("name"): str})
@require_admin
@callback
def ws_hub_usage(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Policies that name an audience or recipient group, so a panel can warn before a delete
    (D-111). Home Assistant cannot block the deletion of a subentry."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    connection.send_result(msg["id"], {"policies": manager.hub.policies.usage(msg["name"])})


@websocket_command(
    {
        vol.Required("type"): "heads_up/action",
        vol.Required("banner_id"): str,
        vol.Required("key"): str,
    }
)
@callback
def ws_action(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.press(msg["banner_id"], connection.user.id, msg["key"])
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@websocket_command(
    {
        vol.Required("type"): "heads_up/snooze",
        vol.Required("banner_id"): str,
        vol.Required("seconds"): vol.All(int, vol.Range(min=1)),
    }
)
@callback
def ws_snooze(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.snooze(msg["banner_id"], connection.user.id, msg["seconds"])
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@websocket_command({vol.Required("type"): "heads_up/unsnooze", vol.Required("banner_id"): str})
@callback
def ws_unsnooze(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.unsnooze(msg["banner_id"], connection.user.id)
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


@websocket_command(
    {
        vol.Required("type"): "heads_up/hub_trace",
        vol.Optional("message_id"): str,
        vol.Optional("limit"): vol.All(int, vol.Range(min=1, max=1000)),
    }
)
@require_admin
@callback
def ws_hub_trace(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    connection.send_result(
        msg["id"],
        {"entries": manager.hub.trace.entries(msg.get("message_id"), msg.get("limit"))},
    )


@websocket_command(
    {
        vol.Required("type"): "heads_up/hub_preview_audience",
        vol.Required("audience"): str,
        vol.Optional("severity", default="warning"): vol.In(SEVERITIES),
    }
)
@require_admin
@async_response
async def ws_hub_preview_audience(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Who an audience is right now, with the reason for each person (and each skipped one)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    resolver = manager.hub.resolver
    if (audience := resolver.audience(msg["audience"])) is None:
        connection.send_error(msg["id"], "not_found", f"Audience {msg['audience']} not found")
        return
    result = await resolver.members(audience, msg["severity"])
    connection.send_result(
        msg["id"],
        {
            "members": [{"person": r.key, "reason": r.reason} for r in result.recipients],
            "skipped": [{"person": s.who, "reason": s.reason} for s in result.skipped],
        },
    )


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (
        ws_subscribe,
        ws_dismiss,
        ws_dismiss_many,
        ws_acknowledge,
        ws_hub_usage,
        ws_hub_plan,
        ws_hub_test_send,
        ws_panel_config,
        ws_channels_set,
        ws_panel_overview,
        ws_panel_messages,
        ws_panel_trace,
        ws_settings_get,
        ws_settings_set,
        ws_welcome_get,
        ws_welcome_apply,
        ws_popup_config,
        ws_popup_subscribe,
        ws_snooze,
        ws_unsnooze,
        ws_action,
        ws_admin_clear,
        ws_hub_trace,
        ws_hub_preview_audience,
    ):
        async_register_command(hass, command)
