"""Actions: create_banner, clear_banner, clear_all (DESIGN §7)."""

from __future__ import annotations

import re
import secrets
from collections.abc import Callable, Coroutine
from datetime import timedelta
from typing import Any

import probatio as vol
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import VolSchemaType
from homeassistant.util import dt as dt_util
from jinja2 import Environment, TemplateSyntaxError

from .conditions import DEFAULT_OPERATOR, NO_STATE_OPERATORS, OPERATORS, check_state
from .const import (
    CHANNEL_BANNER,
    CHANNELS,
    DEFAULT_SEVERITY,
    DISMISS_SCOPES,
    DOMAIN,
    ID_PATTERN,
    MAX_ACTION_LABEL,
    MAX_ACTIONS,
    MAX_FOR_SECONDS,
    MAX_IMAGE,
    MAX_MESSAGE,
    MAX_SNOOZE_OPTIONS,
    MAX_SNOOZE_SECONDS,
    MAX_TIMEOUT_DAYS,
    MAX_TITLE,
    MIN_SNOOZE_SECONDS,
    MODES,
    POLICY_NONE,
    SEVERITIES,
    SNOOZE_SCOPES,
    SOURCE_ACTION,
)
from .hub.engine import HubEngine, Planned
from .manager import BannerManager
from .models import Banner

SLUG = vol.All(
    cv.string,
    vol.Match(ID_PATTERN, msg="must be 1 to 64 characters: lowercase letters a-z, digits, _ or -"),
)


def _timeout(value: timedelta) -> timedelta:
    if value < timedelta(0) or value > timedelta(days=MAX_TIMEOUT_DAYS):
        raise vol.Invalid(f"timeout must be 0 or between 1 second and {MAX_TIMEOUT_DAYS} days")
    return value


def _snooze_seconds(value: timedelta) -> int:
    seconds = round(value.total_seconds())
    if seconds < MIN_SNOOZE_SECONDS or seconds > MAX_SNOOZE_SECONDS:
        raise vol.Invalid("a snooze choice must be between 1 minute and 7 days")
    return seconds


def _snooze_options(value: list[int]) -> list[int]:
    unique = list(dict.fromkeys(value))
    if len(unique) > MAX_SNOOZE_OPTIONS:
        raise vol.Invalid(f"at most {MAX_SNOOZE_OPTIONS} snooze choices")
    return unique


def _check_actions(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(value) > MAX_ACTIONS:
        raise vol.Invalid(f"at most {MAX_ACTIONS} buttons")
    keys = [a["key"] for a in value]
    if len(set(keys)) != len(keys):
        raise vol.Invalid("button keys must be unique")
    return value


# Also used by the watch rule form, so both banner sources accept the same input (DESIGN §22).
TAP_ACTION_SCHEMA = vol.Schema({vol.Required("action"): cv.string}, extra=vol.ALLOW_EXTRA)

ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("key"): SLUG,
        vol.Required("label"): vol.All(cv.string, vol.Length(min=1, max=MAX_ACTION_LABEL)),
        vol.Optional("action"): TAP_ACTION_SCHEMA,
        vol.Optional("dismiss", default=False): cv.boolean,
    }
)
ACTIONS_SCHEMA = vol.All(cv.ensure_list, [ACTION_SCHEMA], _check_actions)


def _check_create(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("dismissible") is False and any(a["dismiss"] for a in data.get("actions", [])):
        raise vol.Invalid(
            "a button cannot dismiss a banner that is not dismissible", path=["actions"]
        )
    # An unhideable banner cannot be snoozed either (D-069).
    if data.get("snoozable") and data.get("dismissible") is False:
        raise vol.Invalid(
            "a banner that is not dismissible cannot be snoozable", path=["snoozable"]
        )
    return data


_STATE_ERRORS = {
    "state_count": "state needs one number for above and below, two for between",
    "state_not_numeric": "state must be a number for above, below and between",
    "state_required": "state is required for contains and not_contains",
}


def _for_seconds(value: timedelta) -> int:
    seconds = round(value.total_seconds())
    if seconds < 0 or seconds > MAX_FOR_SECONDS:
        raise vol.Invalid("for must be between 1 second and 24 hours")
    return seconds


def _check_condition(condition: dict[str, Any]) -> dict[str, Any]:
    if condition.get("for") == 0:
        condition = {k: v for k, v in condition.items() if k != "for"}
    if "template" in condition:
        for key in ("entity_id", "operator", "state", "attribute"):
            if key in condition:
                raise vol.Invalid(f"{key} cannot be used together with template", path=[key])
        return condition
    if "entity_id" not in condition:
        raise vol.Invalid("a condition needs entity_id or template", path=["entity_id"])
    operator = condition.get("operator", DEFAULT_OPERATOR)
    if operator in NO_STATE_OPERATORS:
        return {k: v for k, v in condition.items() if k != "state"}
    if "state" not in condition:
        if operator not in ("equals", "not_equals"):
            raise vol.Invalid("state is required for this operator", path=["state"])
        condition = {**condition, "state": "on"}
    state = condition["state"]
    error = check_state(operator, [state] if isinstance(state, str) else state)
    if error:
        raise vol.Invalid(_STATE_ERRORS[error], path=["state"])
    return condition


def _template_text(value: str) -> str:
    # Syntax only, so the schema needs no running Home Assistant (also used by docs-check).
    try:
        Environment().parse(value)
    except TemplateSyntaxError as err:
        raise vol.Invalid(f"template is not valid: {err.message}") from err
    return value


CONDITION_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional("entity_id"): cv.entity_id,
            vol.Optional("template"): vol.All(cv.string, vol.Length(min=1), _template_text),
            vol.Optional("operator"): vol.In(OPERATORS),
            # List first: cv.string would turn a list into its repr.
            vol.Optional("state"): vol.Any(vol.All(list, [cv.string]), cv.string),
            vol.Optional("attribute"): cv.string,
            vol.Optional("for"): vol.All(cv.time_period, _for_seconds),
        }
    ),
    _check_condition,
)

_IMAGE_REF = re.compile(r"^(https?://\S+|/(?!/)\S*)$")


def _image(value: str) -> str:
    """An http(s) URL or a path on this Home Assistant; nothing is fetched or checked (D-127)."""
    if not _IMAGE_REF.match(value):
        raise vol.Invalid("image must be an http(s) URL or a path starting with /")
    return value


IMAGE = vol.All(cv.string, vol.Length(min=1, max=MAX_IMAGE), _image)

NAME = vol.All(cv.string, vol.Length(min=1, max=100))  # audience, recipient and policy names


def _check_notify(data: dict[str, Any]) -> dict[str, Any]:
    """Shape of channels and targets (DESIGN §23.5). Names are checked in the handler."""
    channels = data["channels"]
    if len(set(channels)) != len(channels):
        raise vol.Invalid("channels must not repeat", path=["channels"])
    to = data.get("to", {})
    for channel, target in to.items():
        if channel not in channels:
            raise vol.Invalid(f"to.{channel} names a channel that is not in channels", path=["to"])
        if channel == "persistent":
            raise vol.Invalid("a persistent notification takes no target", path=["to", channel])
        if ("audience" in target) == ("recipients" in target):
            raise vol.Invalid(
                "give either audience or recipients, not both and not neither",
                path=["to", channel],
            )
        if channel == "speak" and "audience" in target:
            raise vol.Invalid("speech takes recipients, not an audience", path=["to", channel])
    for channel in ("push", "popup", "speak", "mail"):
        if channel in channels and channel not in to:
            raise vol.Invalid(f"{channel} needs a target in to.{channel}", path=["to"])
    return data


def _exclusive_target(data: dict[str, Any]) -> dict[str, Any]:
    if "audience" in data and "recipients" in data:
        raise vol.Invalid("give either audience or recipients, not both", path=["recipients"])
    return data


_CONTENT_FIELDS: dict[Any, Any] = {
    vol.Required("message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
    vol.Optional("title"): vol.All(cv.string, vol.Length(max=MAX_TITLE)),
    vol.Optional("icon"): cv.icon,
}
_CREATE_FIELDS: dict[Any, Any] = {
    vol.Optional("id"): SLUG,
    vol.Required("message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
    vol.Optional("title"): vol.All(cv.string, vol.Length(max=MAX_TITLE)),
    vol.Optional("severity"): vol.In(SEVERITIES),
    vol.Optional("icon"): cv.icon,
    vol.Optional("timeout"): vol.All(cv.time_period, _timeout),
    vol.Optional("dismissible"): cv.boolean,
    vol.Optional("dismiss_scope"): vol.In(DISMISS_SCOPES),
    vol.Optional("snoozable"): cv.boolean,
    vol.Optional("snooze_scope"): vol.In(SNOOZE_SCOPES),
    vol.Optional("snooze_options"): vol.All(
        cv.ensure_list, [vol.All(cv.time_period, _snooze_seconds)], _snooze_options
    ),
    vol.Optional("tag"): SLUG,
    # Passed to the card unchanged (D-015).
    vol.Optional("condition"): CONDITION_SCHEMA,
    vol.Optional("mode"): vol.In(MODES),
    vol.Optional("wait_for_condition"): cv.boolean,
    vol.Optional("people"): vol.All(cv.ensure_list, [cv.entity_domain("person")]),
    vol.Optional("actions"): ACTIONS_SCHEMA,
    vol.Optional("tap_action"): TAP_ACTION_SCHEMA,
    vol.Optional("image"): IMAGE,
}
CREATE_SCHEMA = vol.All(vol.Schema(_CREATE_FIELDS), _check_create)

# `notify` takes the lifecycle of `create_banner` (D-087). Banner recipients replace `people`.
_NOTIFY_FIELDS = {k: v for k, v in _CREATE_FIELDS.items() if str(k) != "people"}
TARGET_SCHEMA = vol.Schema(
    {
        vol.Optional("audience"): NAME,
        vol.Optional("recipients"): vol.All(cv.ensure_list, [cv.string]),
    }
)
NOTIFY_SCHEMA = vol.All(
    vol.Schema(
        {
            **_NOTIFY_FIELDS,
            vol.Optional("tts_message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
            vol.Required("channels"): vol.All(
                cv.ensure_list, [vol.In(CHANNELS)], vol.Length(min=1)
            ),
            vol.Optional("to"): {vol.In(CHANNELS): TARGET_SCHEMA},
            vol.Optional("policy"): vol.All(cv.string, vol.Length(min=1)),
        }
    ),
    _check_create,
    _check_notify,
)


# Shortcuts: one fixed channel, a target, no policies (D-083).
def _shortcut_schema(channel: str) -> VolSchemaType:
    fields: dict[Any, Any] = {
        vol.Optional("id"): SLUG,
        **_CONTENT_FIELDS,
        vol.Optional("severity"): vol.In(SEVERITIES),
        vol.Optional("tts_message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
        vol.Optional("tag"): SLUG,
        vol.Optional("timeout"): vol.All(cv.time_period, _timeout),
        vol.Optional("actions"): ACTIONS_SCHEMA,
        vol.Optional("tap_action"): TAP_ACTION_SCHEMA,
        vol.Optional("recipients"): vol.All(cv.ensure_list, [cv.string]),
    }
    if channel != "speak":  # speech takes speakers, not an audience (D-098)
        fields[vol.Optional("audience")] = NAME
        fields[vol.Optional("image")] = IMAGE
    needs = ("recipients",) if channel == "speak" else ("audience", "recipients")
    return vol.All(vol.Schema(fields), cv.has_at_least_one_key(*needs), _exclusive_target)


CLEAR_SCHEMA = vol.All(
    vol.Schema({vol.Optional("id"): SLUG, vol.Optional("tag"): SLUG}),
    cv.has_at_least_one_key("id", "tag"),
)
CLEAR_ALL_SCHEMA = vol.Schema({})
SHORTCUT_CHANNELS = ("push", "popup", "speak")

SCHEMAS: dict[str, VolSchemaType] = {
    "create_banner": CREATE_SCHEMA,
    "clear_banner": CLEAR_SCHEMA,
    "clear_all": CLEAR_ALL_SCHEMA,
    "clear": CLEAR_SCHEMA,
    "notify": NOTIFY_SCHEMA,
    **{channel: _shortcut_schema(channel) for channel in SHORTCUT_CHANNELS},
}


def _manager(hass: HomeAssistant) -> BannerManager:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")
    manager: BannerManager = entries[0].runtime_data
    return manager


async def _create(call: ServiceCall) -> ServiceResponse:
    return _manager(call.hass).create(call.data)


async def _clear(call: ServiceCall) -> ServiceResponse:
    return {"cleared": _manager(call.hass).clear(call.data.get("id"), call.data.get("tag"))}


async def _clear_all(call: ServiceCall) -> ServiceResponse:
    return {"cleared": _manager(call.hass).clear_all()}


async def _clear_everywhere(call: ServiceCall) -> ServiceResponse:
    # Removes any message, also one without the banner channel; clear_banner skips those (D-108).
    cleared = _manager(call.hass).clear(
        call.data.get("id"), call.data.get("tag"), all_channels=True
    )
    return {"cleared": cleared}


def _hub_off() -> ServiceValidationError:
    return ServiceValidationError(translation_domain=DOMAIN, translation_key="hub_off")


def _unknown(key: str, name: str, valid: list[str]) -> ServiceValidationError:
    shown = ", ".join(valid[:20]) + (" ..." if len(valid) > 20 else "")
    return ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key=key,
        translation_placeholders={"name": name, "valid": shown or "none exist yet"},
    )


def _check_names(hub: HubEngine, to: dict[str, dict[str, Any]], policy: str | None) -> None:
    for channel, target in to.items():
        if (
            audience := target.get("audience")
        ) is not None and audience not in hub.audiences.names():
            raise _unknown("unknown_audience", audience, hub.audiences.names())
        known = hub.recipients.known(channel)
        for recipient in target.get("recipients", []):
            if not hub.recipients.accepts(channel, recipient):
                raise _unknown("unknown_recipient", recipient, known)
    if policy not in (None, POLICY_NONE) and policy not in hub.policies.names():
        raise _unknown("unknown_policy", str(policy), hub.policies.names())


def _response(result: dict[str, Any], planned: list[Planned] | None) -> dict[str, Any]:
    counts = HubEngine.counts(planned) if planned is not None else {}
    return {**result, "channels": counts}


async def banner_people(
    hub: HubEngine | None, target: dict[str, Any], severity: str | None
) -> list[str]:
    """The `people` of a banner for its target: the persons named, or the members of the audience
    as of now (D-131). Empty means everyone."""
    if audience := target.get("audience"):
        if hub is None:
            return []
        return await hub.resolver.banner_people(audience, severity or DEFAULT_SEVERITY)
    people = list(target.get("recipients", []))
    return hub.resolver.enabled_people(people) if hub is not None else people


async def _notify(call: ServiceCall) -> ServiceResponse:
    manager = _manager(call.hass)
    data = dict(call.data)
    to: dict[str, dict[str, Any]] = data.pop("to", {})
    if (hub := manager.hub) is None:
        raise _hub_off()
    _check_names(hub, to, data.get("policy"))
    if people := await banner_people(hub, to.get(CHANNEL_BANNER, {}), data.get("severity")):
        data["people"] = people  # the card's own targeting (D-008, D-131)
    data["targets"] = to
    result = manager.create(data)
    banner = manager.banners.get(result["id"])
    if banner is None:
        return _response(result, [])
    return _response(result, await hub.plan(banner, waiting=result["status"] == "waiting"))


def _shortcut(channel: str) -> Callable[[ServiceCall], Coroutine[Any, Any, ServiceResponse]]:
    async def handler(call: ServiceCall) -> ServiceResponse:
        manager = _manager(call.hass)
        if (hub := manager.hub) is None:
            raise _hub_off()
        data = dict(call.data)
        target: dict[str, Any] = {k: data.pop(k) for k in ("audience", "recipients") if k in data}
        _check_names(hub, {channel: target}, None)
        if "id" in data:
            data.update(channels=[channel], targets={channel: target}, source=SOURCE_ACTION)
            result = manager.create(data)
            banner = manager.banners[result["id"]]
            return _response(result, await hub.plan(banner))
        # No id: deliver once and keep no record, so a later clear cannot take it back.
        now = dt_util.utcnow()
        message = Banner(
            id=f"hu_{secrets.token_hex(5)}",
            message=data["message"],
            severity=data.get("severity", DEFAULT_SEVERITY),
            dismissible=False,
            dismiss_scope="user",
            created_at=now,
            updated_at=now,
            title=data.get("title"),
            icon=data.get("icon"),
            tag=data.get("tag"),
            tap_action=data.get("tap_action"),
            image=data.get("image"),
            actions=[dict(a) for a in data.get("actions", [])],
            tts_message=data.get("tts_message"),
            channels=[channel],
            targets={channel: target},
        )
        planned = await hub.send_once(message)
        return _response({"id": message.id, "status": "sent_once"}, planned)

    return handler


def async_setup_services(hass: HomeAssistant) -> None:
    # Registered in async_setup so calls fail with not_loaded instead of "unknown action"
    # while the entry is not loaded. SupportsResponse: HA_API_NOTES N-3.
    for name, handler in (
        ("create_banner", _create),
        ("clear_banner", _clear),
        ("clear_all", _clear_all),
        ("clear", _clear_everywhere),
        ("notify", _notify),
        *((c, _shortcut(c)) for c in SHORTCUT_CHANNELS),
    ):
        hass.services.async_register(
            DOMAIN, name, handler, schema=SCHEMAS[name], supports_response=SupportsResponse.OPTIONAL
        )
