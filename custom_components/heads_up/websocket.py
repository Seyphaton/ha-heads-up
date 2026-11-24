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
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .binary_sensor import audience_entity_id, audience_entity_ids
from .const import (
    BUILTIN_AUDIENCES,
    DOMAIN,
    GROUP_SUFFIX,
    LIMITABLE_AUDIENCES,
    MAX_ATTENTION_DISMISSED,
    MAX_PROGRESS_INTERVAL,
    MIN_PROGRESS_INTERVAL,
    OPT_ATTENTION_DISMISSED,
    OPT_AUDIENCE_EDITS,
    OPT_AUDIENCES_DISABLED,
    OPT_INBOX_ALL,
    OPT_MAIL_ADDRESS,
    OPT_MAIL_SERVICE,
    OPT_SPEAK_TTS_ENTITY,
    SEVERITIES,
    canonical_severity,
)
from .frontend import async_popup_url
from .hub import checker, panel_config, panel_data, panel_test, reach, settings, welcome
from .hub.engine import HubEngine
from .hub.identity import GROUP_PREFIX
from .hub.policies.convert import OPT_CONVERSION_ITEMS
from .hub.recipients import speaker_entities
from .manager import BannerManager, HeadsUpError
from .switch import policy_entity_id


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
            "welcome_seen": bool(entry.options.get(welcome.OPT_WELCOME_SEEN, False)),
        },
    )


@websocket_command({vol.Required("type"): "heads_up/inbox_clear_all"})
@require_admin
@callback
def ws_inbox_clear_all(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Clear inbox (Settings): every item of every person. The only inbox command that is not
    the caller's own, so it is for administrators (D-264)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    hub = entry.runtime_data.hub
    if hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is off")
        return
    count = hub.inbox.clear()
    connection.send_result(msg["id"], {"count": count, "info": hub.inbox.info()})


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
            "speaker_names": panel_config.speaker_names(hass),
            "areas": panel_config.area_choices(hass),
            "tts_engines": sorted(s.entity_id for s in hass.states.async_all("tts")),
            "tts_engine": str(entry.options.get(OPT_SPEAK_TTS_ENTITY) or ""),
            # Step 2 of the tour: the mail settings it can change (saved with channels_set).
            "notify_services": panel_config.notify_services(hass),
            "mail_service": str(entry.options.get(OPT_MAIL_SERVICE) or ""),
            "mail_global_address": str(entry.options.get(OPT_MAIL_ADDRESS) or ""),
            "inbox_all_notifications": bool(entry.options.get(OPT_INBOX_ALL, False)),
        },
    )


@websocket_command(
    {
        vol.Required("type"): "heads_up/welcome_apply",
        vol.Required("items"): [vol.In(list(welcome.ITEMS))],
        vol.Optional("audience", default=welcome.DEFAULT_AUDIENCE): str,
        vol.Optional("speakers", default=list): [str],
        vol.Optional("tts_engine", default=""): vol.Any("", vol.Match(r"^tts\.[a-z0-9_]+$")),
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
    if (chosen := hub.resolver.audience(msg["audience"])) is None:
        connection.send_error(
            msg["id"], "unknown_audience", f"Audience {msg['audience']} not found"
        )
        return
    if unknown := [s for s in msg["speakers"] if not hub.recipients.accepts("speak", s)]:
        connection.send_error(msg["id"], "unknown_recipient", f"Unknown speaker {unknown[0]}")
        return
    if msg["tts_engine"] and hass.states.get(msg["tts_engine"]) is None:
        connection.send_error(msg["id"], "unknown_tts_engine", f"Unknown {msg['tts_engine']}")
        return
    connection.send_result(
        msg["id"],
        welcome.apply(hass, entry, msg["items"], chosen.key, msg["speakers"], msg["tts_engine"]),
    )


@websocket_command({vol.Required("type"): "heads_up/panel_reach"})
@require_admin
@async_response
async def ws_panel_reach(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The Overview table "What would a message do right now?": a dry run per severity."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    connection.send_result(msg["id"], await reach.reach(hass, manager.hub, manager.options))


@websocket_command({vol.Required("type"): "heads_up/panel_audiences"})
@require_admin
@async_response
async def ws_panel_audiences(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The six built-in audiences with their members now, for the tour's step 3."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    connection.send_result(msg["id"], await panel_data.audiences(hass, manager.hub))


@websocket_command(
    {
        vol.Required("type"): "heads_up/panel_stats",
        vol.Optional("period", default="week"): vol.In(["24h", "week", "month", "year", "2y"]),
    }
)
@require_admin
@callback
def ws_panel_stats(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """The Activity card of the Overview: a period of the history (D-244, plan 19.3)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    connection.send_result(msg["id"], panel_data.stats(entry.runtime_data, entry, msg["period"]))


@websocket_command({vol.Required("type"): "heads_up/stats_clear"})
@require_admin
@async_response
async def ws_stats_clear(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Delete the whole history. The Settings page asks for a confirmation first (decision 12)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    await manager.hub.stats.async_clear()
    connection.send_result(msg["id"], manager.hub.stats.info())


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


@websocket_command(
    {
        vol.Required("type"): "heads_up/attention_dismiss",
        vol.Required("key"): vol.All(str, vol.Length(min=1, max=300)),
    }
)
@require_admin
@callback
def ws_attention_dismiss(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Hide one warning of Needs attention until it is shown again (D-135)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    keys = [k for k in entry.options.get(OPT_ATTENTION_DISMISSED, []) if k != msg["key"]]
    keys = [*keys, msg["key"]][-MAX_ATTENTION_DISMISSED:]
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_ATTENTION_DISMISSED: keys}
    )
    connection.send_result(msg["id"], {"hidden": len(keys)})


@websocket_command(
    {
        vol.Required("type"): "heads_up/audience_enable",
        vol.Required("name"): str,
        vol.Required("enabled"): bool,
    }
)
@require_admin
@callback
def ws_audience_enable(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Switch a built-in audience on or off (D-136). One that a policy uses stays on."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    hub = entry.runtime_data.hub
    if hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    name = msg["name"]
    if name not in BUILTIN_AUDIENCES:
        connection.send_error(msg["id"], "not_found", f"{name} is not a built-in audience")
        return
    kind = BUILTIN_AUDIENCES[name]
    disabled = [
        n
        for n in entry.options.get(OPT_AUDIENCES_DISABLED, [])
        if BUILTIN_AUDIENCES.get(n, n) != kind
    ]
    disabled = [BUILTIN_AUDIENCES.get(n, n) for n in disabled]  # kinds, not names (D-199)
    if not msg["enabled"]:
        if users := hub.policies.usage(kind, name):
            connection.send_error(msg["id"], "in_use", f"{name} is used by {', '.join(users)}")
            return
        disabled.append(kind)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_AUDIENCES_DISABLED: disabled}
    )
    connection.send_result(msg["id"], {"disabled": disabled})


@websocket_command(
    {
        vol.Required("type"): "heads_up/audience_edit",
        vol.Required("name"): str,
        vol.Optional("exclude", default=list): [cv.entity_domain("person")],
        vol.Optional("limit", default=list): [cv.entity_domain("person")],
    }
)
@require_admin
@callback
def ws_audience_edit(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Edit a built-in audience in place (D-257): persons left out, and for the presence
    audiences the persons it is limited to. Empty lists are the shipped audience."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    kind = BUILTIN_AUDIENCES.get(msg["name"])
    if kind is None:
        connection.send_error(msg["id"], "not_found", f"{msg['name']} is not a built-in audience")
        return
    if msg["limit"] and kind not in LIMITABLE_AUDIENCES:
        connection.send_error(msg["id"], "invalid_format", f"{msg['name']} cannot be limited")
        return
    edits = {k: v for k, v in (entry.options.get(OPT_AUDIENCE_EDITS) or {}).items() if k != kind}
    exclude = list(dict.fromkeys(msg["exclude"]))
    limit = list(dict.fromkeys(msg["limit"]))
    if exclude or limit:
        edits[kind] = {"exclude": exclude, "limit": limit}
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_AUDIENCE_EDITS: edits}
    )
    connection.send_result(msg["id"], {"exclude": exclude, "limit": limit})


@websocket_command({vol.Required("type"): "heads_up/audience_reset", vol.Required("name"): str})
@require_admin
@callback
def ws_audience_reset(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Back to the shipped audience (D-257)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    kind = BUILTIN_AUDIENCES.get(msg["name"])
    if kind is None:
        connection.send_error(msg["id"], "not_found", f"{msg['name']} is not a built-in audience")
        return
    edits = {k: v for k, v in (entry.options.get(OPT_AUDIENCE_EDITS) or {}).items() if k != kind}
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_AUDIENCE_EDITS: edits}
    )
    connection.send_result(msg["id"], {})


@websocket_command({vol.Required("type"): "heads_up/attention_restore"})
@require_admin
@callback
def ws_attention_restore(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Show every hidden warning of Needs attention again (D-135)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_ATTENTION_DISMISSED: []}
    )
    connection.send_result(msg["id"], {"hidden": 0})


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


@websocket_command({vol.Required("type"): "heads_up/severity_display"})
@require_admin
@callback
def ws_severity_display(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Label, icon and color per severity, for the panel's own lists (D-223)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    connection.send_result(
        msg["id"], dict(entry.runtime_data.options.get("severity_display") or {})
    )


@websocket_command(
    {
        vol.Required("type"): "heads_up/channels_set",
        vol.Optional("severity_display"): {str: {str: str}},
        vol.Optional("push_levels"): {str: str},
        vol.Optional("popup_styles"): {str: str},
        vol.Optional("push_lockscreen"): str,
        vol.Optional("push_sticky"): bool,
        vol.Optional("push_severity_look"): bool,
        vol.Optional("push_progress_interval"): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_PROGRESS_INTERVAL, max=MAX_PROGRESS_INTERVAL)
        ),
        vol.Optional("push_channel_id"): str,
        vol.Optional("speak_language"): vol.All(str, vol.Length(max=20)),
        vol.Optional("mail_service"): str,
        vol.Optional("mail_global_address"): str,
        vol.Optional("mail_subject"): str,
        vol.Optional("mail_body"): str,
        vol.Optional("inbox_retention_months"): vol.All(int, vol.Range(min=1, max=36)),
        vol.Optional("inbox_reminder_unread"): bool,
        vol.Optional("inbox_all_notifications"): bool,
        **{
            vol.Optional(key): vol.All(int, vol.Range(min=low, max=high))
            for key, (low, high) in panel_config.CHANNEL_RANGES.items()
        },
        vol.Optional("speak_tts_entity"): vol.Any("", vol.Match(r"^tts\.[a-z0-9_]+$")),
        vol.Optional("speak_restore_volume"): bool,
        vol.Optional("speak_volume_bands"): settings.check_bands,
        vol.Optional("speak_severity_volume"): settings.check_severity_volume,
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
    if "severity_display" in changes:
        changes["severity_display"] = panel_config.clean_display(changes["severity_display"])
    hass.config_entries.async_update_entry(entry, options={**entry.options, **changes})
    connection.send_result(msg["id"], panel_config.channel_settings(entry.runtime_data))


_TEST_CALL: dict[Any, Any] = {
    vol.Required("message"): str,
    vol.Required("channels"): [str],
    vol.Optional("title"): str,
    vol.Optional("tts_message"): str,
    vol.Optional("volume"): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
    vol.Optional("mail_subject"): str,
    vol.Optional("mail_body"): str,
    vol.Optional("severity"): str,
    vol.Optional("tag"): str,
    vol.Optional("policy"): vol.Any(str, [str]),
    vol.Optional("match_policies_automatically"): bool,
    vol.Optional("to"): {str: dict},
    vol.Optional("audience"): str,
    vol.Optional("recipients"): [str],
    vol.Optional("speakers"): [str],
    vol.Optional("dismiss"): str,
    vol.Optional("snooze"): str,
    # The other fields of `notify` (D-260): the schema of the action checks them.
    **{
        vol.Optional(key): object
        for key in (
            "icon",
            "image",
            "color",
            "icon_url",
            "subtitle",
            "progress",
            "timeout",
            "actions",
            "tap_action",
            "snooze_options",
            "snooze_custom",
            "condition",
            "mode",
        )
    },
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
        message = await panel_test.build(manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], await manager.hub.preview(message))


@websocket_command(
    {
        vol.Required("type"): "heads_up/policy_check",
        vol.Required("severity"): str,
        vol.Optional("tag"): vol.Any(None, str),
        vol.Optional("rule"): vol.Any(None, str),
        vol.Optional("channels", default=["banner", "push"]): [str],
        vol.Optional("to"): dict,
        vol.Optional("audience"): vol.Any(None, str),
        vol.Optional("at"): vol.Any(None, str),
        vol.Optional("home", default=dict): {str: bool},
        vol.Optional("ack_after"): vol.Any(None, vol.All(int, vol.Range(min=0, max=1440))),
    }
)
@require_admin
@async_response
async def ws_policy_check(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The checker "What happens to a message?" (DESIGN §25.8): sends nothing, stores nothing."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    payload: dict[str, Any] = {
        "message": "What happens to a message?",
        "severity": msg["severity"],
        "channels": msg["channels"],
    }
    tag = msg.get("tag") or ("rule" if msg.get("rule") else None)
    if tag:
        payload["tag"] = tag
    if "speak" in msg["channels"] and "speak" not in (msg.get("to") or {}):
        # Speech has no audience: the checker speaks on every speaker, as the Overview table does.
        # With none, speech is left out instead of failing the whole check.
        speakers = speaker_entities(hass)
        if speakers:
            payload["to"] = {**(msg.get("to") or {}), "speak": {"recipients": speakers}}
        else:
            payload["channels"] = [c for c in msg["channels"] if c != "speak"]
    if msg.get("to"):
        payload["to"] = msg["to"]
    if msg.get("audience"):
        # The panel offers audiences by key; a call names them by the entity ID of their sensor.
        found = manager.hub.resolver.audience(msg["audience"])
        entities = audience_entity_ids(hass, hass.config_entries.async_loaded_entries(DOMAIN)[0])
        payload["audience"] = (
            entities.get(found.name, msg["audience"]) if found else msg["audience"]
        )
    at = dt_util.parse_datetime(msg["at"]) if msg.get("at") else None
    if msg.get("at") and at is None:
        connection.send_error(msg["id"], "invalid_format", "at is not a date and time")
        return
    try:
        message = await panel_test.build(manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    message.id = checker.message_id_for(msg.get("rule"))
    result = await checker.check(manager.hub, message, at, msg["home"], msg.get("ack_after"))
    connection.send_result(msg["id"], result)


@websocket_command(
    {
        vol.Required("type"): "heads_up/conversion_item",
        vol.Required("policy"): str,
        vol.Required("kind"): vol.In(["not_for", "links", "never_acts", "holds_anyway"]),
        vol.Required("choice"): vol.In(["keep", "change"]),
    }
)
@require_admin
@callback
def ws_conversion_item(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Answer one item of the check list after the update (DESIGN §25.7). "change" lets the
    policy act (its links go) or lets Critical through a hold (Holds these anyway goes)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    items = [dict(i) for i in entry.options.get(OPT_CONVERSION_ITEMS) or []]
    found = [i for i in items if i["policy"] == msg["policy"] and i["kind"] == msg["kind"]]
    sub = entry.subentries.get(msg["policy"])
    if not found or sub is None:
        connection.send_error(msg["id"], "not_found", "No such item on the check list")
        return
    if msg["choice"] == "change":
        data = dict(sub.data)
        if msg["kind"] == "holds_anyway":
            data.pop("holds_anyway", None)
        else:
            # Take back what the conversion wrote: its Not for values and its links.
            for item in found:
                for key, values in (item.get("added") or {}).items():
                    kept = [v for v in data.get(key) or [] if v not in values]
                    if kept:
                        data[key] = kept
                    else:
                        data.pop(key, None)
            if msg["kind"] in ("links", "never_acts"):
                data.pop("links", None)
        hass.config_entries.async_update_subentry(entry, sub, data=data)
    for item in found:
        item["state"] = "kept" if msg["choice"] == "keep" else "changed"
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, OPT_CONVERSION_ITEMS: items}
    )
    connection.send_result(msg["id"], {"items": items})


@websocket_command({vol.Required("type"): "heads_up/conversion_items_dismiss"})
@require_admin
@callback
def ws_conversion_items_dismiss(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Hide the check list; open items keep their 1.x behaviour."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    options = {k: v for k, v in entry.options.items() if k != OPT_CONVERSION_ITEMS}
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], {})


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


@websocket_command(
    {
        vol.Required("type"): "heads_up/hub_plan_yaml",
        vol.Required("yaml"): str,
        vol.Optional("variables", default=""): str,
    }
)
@require_admin
@async_response
async def ws_hub_plan_yaml(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The dry run of a pasted call, templates rendered with sample values (D-194)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    try:
        payload = panel_test.render_call(hass, msg["yaml"], msg["variables"])
        message = await panel_test.build(manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], {**await manager.hub.preview(message), "call": payload})


@websocket_command({vol.Required("type"): "heads_up/hub_parse_yaml", vol.Required("yaml"): str})
@require_admin
@callback
def ws_hub_parse_yaml(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The `notify` input of a call in YAML, templates left as they are, so the visual editor can
    take over what was typed in the YAML editor (D-260)."""
    try:
        call = panel_test.parse_call(msg["yaml"])
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], {"call": call})


@websocket_command({vol.Required("type"): "heads_up/rule_parse_yaml", vol.Required("yaml"): str})
@require_admin
@callback
def ws_rule_parse_yaml(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """A watch rule in YAML as a mapping, for the form's YAML editor (D-260)."""
    try:
        rule = panel_test.parse_rule(msg["yaml"])
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], {"rule": rule})


@websocket_command(
    {
        vol.Required("type"): "heads_up/hub_test_send_yaml",
        vol.Required("yaml"): str,
        vol.Optional("variables", default=""): str,
    }
)
@require_admin
@async_response
async def ws_hub_test_send_yaml(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The one real send of a pasted call, with the test marker (D-194)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    if manager.hub is None:
        connection.send_error(msg["id"], "hub_off", "The hub is switched off")
        return
    try:
        payload = panel_test.render_call(hass, msg["yaml"], msg["variables"])
        result = await panel_test.send(hass, manager.hub, payload)
    except panel_test.TestSendError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_command(
    {
        vol.Required("type"): "heads_up/policy_entity_id",
        vol.Required("name"): str,
        vol.Optional("subentry_id"): str,
    }
)
@require_admin
@callback
def ws_policy_entity_id(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The entity ID of a policy's switch, or the one a new policy will get (D-197)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    entity_id = policy_entity_id(hass, entry, msg.get("subentry_id"), msg["name"].strip())
    connection.send_result(msg["id"], {"entity_id": entity_id})


@websocket_command(
    {
        vol.Required("type"): "heads_up/audience_entity_id",
        vol.Required("name"): str,
        vol.Optional("subentry_id"): str,
    }
)
@require_admin
@callback
def ws_audience_entity_id(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The entity ID of a custom audience's sensor, or the one a new audience will get (D-198)."""
    if (entry := _entry(hass, connection, msg["id"])) is None:
        return
    entity_id = audience_entity_id(hass, entry, msg.get("subentry_id"), msg["name"].strip())
    connection.send_result(msg["id"], {"entity_id": entity_id})


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
    hub = manager.hub
    refs = [msg["name"], f"{msg['name']}{GROUP_SUFFIX}"]
    if (audience := hub.resolver.audience(msg["name"])) is not None:
        refs.append(audience.key)
    if (group := hub.resolver.group(msg["name"])) is not None:
        refs += [f"{GROUP_PREFIX}{group.key}", f"{group.name}{GROUP_SUFFIX}"]
    connection.send_result(msg["id"], {"policies": hub.policies.usage(*refs)})


@websocket_command(
    {
        vol.Required("type"): "heads_up/action",
        vol.Required("banner_id"): str,
        vol.Required("key"): str,
        vol.Optional("channel", default="banner"): vol.In(("banner", "popup")),
    }
)
@callback
def ws_action(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.press(msg["banner_id"], connection.user.id, msg["key"], msg["channel"])
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


@websocket_command({vol.Required("type"): "heads_up/panel_clear", vol.Required("message_id"): str})
@require_admin
@callback
def ws_panel_clear(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Overview: take one message back from every channel (D-204)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.panel_clear(msg["message_id"])
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


@websocket_command(
    {vol.Required("type"): "heads_up/panel_acknowledge", vol.Required("message_id"): str}
)
@require_admin
@callback
def ws_panel_acknowledge(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Overview: acknowledge one message as the administrator, targeted or not (D-204)."""
    if (manager := _manager(hass, connection, msg["id"])) is None:
        return
    try:
        manager.acknowledge(msg["message_id"], connection.user.id, any_message=True)
    except HeadsUpError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])


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
        vol.Optional("severity", default="warning"): vol.All(
            canonical_severity, vol.In(SEVERITIES)
        ),
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


# The inbox (D-264): the caller's own, whoever the caller is. The person comes from the logged-in
# user, never from the message, so no command can name another person's items.

INBOX_PAGE = 100


def _inbox(
    hass: HomeAssistant, connection: ActiveConnection, msg_id: int
) -> tuple[HubEngine, list[str]] | None:
    if (manager := _manager(hass, connection, msg_id)) is None:
        return None
    if manager.hub is None:
        connection.send_error(msg_id, "hub_off", "The hub is off")
        return None
    return manager.hub, manager.hub.resolver.persons_of_user(connection.user.id)


def _inbox_state(hub: HubEngine, persons: list[str], limit: int = INBOX_PAGE) -> dict[str, Any]:
    inbox = hub.inbox
    items, total = inbox.items_of(persons, limit=limit)
    return {
        "has_person": bool(persons),
        "all_notifications": hub.inbox_all,
        "items": [i.to_client() for i in items],
        "total": total,
        "more": total > len(items),
        **inbox.counts_of(persons),
    }


@websocket_command(
    {
        vol.Required("type"): "heads_up/inbox_list",
        vol.Optional("limit", default=50): vol.All(int, vol.Range(min=1, max=INBOX_PAGE)),
        vol.Optional("offset", default=0): vol.All(int, vol.Range(min=0)),
        vol.Optional("unread_only", default=False): bool,
        vol.Optional("view", default="inbox"): vol.In(("inbox", "all")),
    }
)
@callback
def ws_inbox_list(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """The caller's inbox items, the latest change first, with the counts."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, persons = found
    inbox = hub.inbox
    items, total = inbox.items_of(
        persons,
        unread_only=msg["unread_only"],
        copies=msg["view"] == "all",
        limit=msg["limit"],
        offset=msg["offset"],
    )
    connection.send_result(
        msg["id"],
        {
            "has_person": bool(persons),
            "all_notifications": hub.inbox_all,
            "items": [i.to_client() for i in items],
            "total": total,
            "more": msg["offset"] + len(items) < total,
            **inbox.counts_of(persons),
        },
    )


@websocket_command({vol.Required("type"): "heads_up/inbox_subscribe"})
@callback
def ws_inbox_subscribe(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """The caller's counts and first page now, and again after every change of their items."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, _ = found
    inbox = hub.inbox
    user_id = connection.user.id
    last: list[str] = []

    @callback
    def forward() -> None:
        # Persons are looked up each time: a person may be linked to the user later.
        state = _inbox_state(hub, hub.resolver.persons_of_user(user_id))
        digest = repr(state)
        if last and last[0] == digest:
            return  # a change of somebody else's items
        last[:] = [digest]
        connection.send_event(msg["id"], state)

    connection.subscriptions[msg["id"]] = inbox.subscribe(forward)
    connection.send_result(msg["id"])
    forward()


@websocket_command(
    {vol.Required("type"): "heads_up/inbox_read", vol.Required("message_id"): cv.string}
)
@callback
def ws_inbox_read(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Mark one item read: the person opened it."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, persons = found
    inbox = hub.inbox
    owned = [p for p in persons if inbox.get(p, msg["message_id"]) is not None]
    if not owned:
        connection.send_error(msg["id"], "not_found", "No such inbox item")
        return
    now = dt_util.utcnow()
    for person in owned:
        inbox.mark_read(person, msg["message_id"], now)
    connection.send_result(msg["id"])


@websocket_command({vol.Required("type"): "heads_up/inbox_read_all"})
@callback
def ws_inbox_read_all(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Mark every unread item of the caller read."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, persons = found
    inbox = hub.inbox
    now = dt_util.utcnow()
    connection.send_result(
        msg["id"], {"count": sum(inbox.mark_read_all(person, now) for person in persons)}
    )


@websocket_command(
    {vol.Required("type"): "heads_up/inbox_delete", vol.Required("message_id"): cv.string}
)
@callback
def ws_inbox_delete(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Remove one item from the caller's inbox."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, persons = found
    inbox = hub.inbox
    if not any([inbox.delete(person, msg["message_id"]) for person in persons]):
        connection.send_error(msg["id"], "not_found", "No such inbox item")
        return
    connection.send_result(msg["id"])


@websocket_command({vol.Required("type"): "heads_up/inbox_clear"})
@callback
def ws_inbox_clear(hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]) -> None:
    """Remove every item of the caller. Other people's inboxes are not touched."""
    if (found := _inbox(hass, connection, msg["id"])) is None:
        return
    hub, persons = found
    inbox = hub.inbox
    connection.send_result(msg["id"], {"count": sum(inbox.purge_person(p) for p in persons)})


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (
        ws_subscribe,
        ws_dismiss,
        ws_dismiss_many,
        ws_acknowledge,
        ws_hub_usage,
        ws_policy_entity_id,
        ws_audience_entity_id,
        ws_hub_plan,
        ws_policy_check,
        ws_conversion_item,
        ws_conversion_items_dismiss,
        ws_hub_test_send,
        ws_hub_plan_yaml,
        ws_hub_parse_yaml,
        ws_rule_parse_yaml,
        ws_hub_test_send_yaml,
        ws_panel_config,
        ws_channels_set,
        ws_severity_display,
        ws_panel_overview,
        ws_panel_reach,
        ws_audience_edit,
        ws_audience_reset,
        ws_panel_audiences,
        ws_panel_stats,
        ws_stats_clear,
        ws_attention_dismiss,
        ws_attention_restore,
        ws_audience_enable,
        ws_panel_messages,
        ws_panel_trace,
        ws_settings_get,
        ws_settings_set,
        ws_welcome_get,
        ws_welcome_apply,
        ws_popup_config,
        ws_popup_subscribe,
        ws_inbox_list,
        ws_inbox_subscribe,
        ws_inbox_read,
        ws_inbox_read_all,
        ws_inbox_delete,
        ws_inbox_clear,
        ws_inbox_clear_all,
        ws_snooze,
        ws_unsnooze,
        ws_action,
        ws_admin_clear,
        ws_panel_clear,
        ws_panel_acknowledge,
        ws_hub_trace,
        ws_hub_preview_audience,
    ):
        async_register_command(hass, command)
