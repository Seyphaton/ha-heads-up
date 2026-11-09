"""Actions: create_banner, clear_notifications, clear_banner, clear_all (DESIGN §7)."""

from __future__ import annotations

import difflib
import logging
import re
import secrets
from collections.abc import Callable, Coroutine
from datetime import timedelta
from typing import Any, cast

import probatio as vol
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import issue_registry as ir
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
    POLICY_AUTOMATIC,
    POLICY_NONE,
    SEVERITIES,
    SNOOZE_SCOPES,
    SOURCE_ACTION,
)
from .hub.channels.mail import check_body, check_subject
from .hub.engine import HubEngine, Planned
from .hub.policies.matching import policy_names
from .manager import BannerManager
from .models import Banner

UNAVAILABLE_AS = ("met", "not_met")
REMOVED_WAIT = "wait_for_condition"
ISSUE_WAIT_REMOVED = "wait_for_condition_removed"

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
        # Push only: iOS shows the title red; both platforms ask for an unlocked device (D-195).
        vol.Optional("destructive"): cv.boolean,
        vol.Optional("require_auth"): cv.boolean,
    }
)
ACTIONS_SCHEMA = vol.All(cv.ensure_list, [ACTION_SCHEMA], _check_actions)


def _check_create(data: dict[str, Any]) -> dict[str, Any]:
    # A message that comes back when its condition is true again has no meaning without one.
    if data.get("mode") == "recurring" and "condition" not in data:
        raise vol.Invalid("mode recurring needs a condition", path=["condition"])
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
        for key in ("entity_id", "operator", "state", "attribute", "treat_unavailable_as"):
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
            # What an unavailable or unknown entity counts as; left out, it changes nothing (D-195).
            vol.Optional("treat_unavailable_as"): vol.In(UNAVAILABLE_AS),
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


_MAIL_TEMPLATE_ERRORS = {
    "mail_template_empty": "a mail template must not be empty",
    "mail_template_too_long": "a mail template is too long",
    "mail_template_placeholder": (
        "a mail template allows only {severity}, {title}, {message}, {person}, {person_id},"
        " {id} and {tag}"
    ),
}


def _mail_template(check: Callable[[str], str | None]) -> Callable[[Any], str]:
    def validate(value: Any) -> str:
        text = cv.string(value)
        if (code := check(text)) is not None:
            raise vol.Invalid(_MAIL_TEMPLATE_ERRORS[code])
        return text

    return validate


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
    for field_name in ("mail_subject", "mail_body"):
        if field_name in data and "mail" not in channels:
            raise vol.Invalid(f"{field_name} needs mail in channels", path=[field_name])
    for channel in ("push", "popup", "speak", "mail"):
        if channel in channels and channel not in to:
            hint = "speakers" if channel == "speak" else "recipients or audience"
            raise vol.Invalid(f"{channel} needs a target: give {hint} or to.{channel}", path=["to"])
    return data


def _map_interaction(data: dict[str, Any]) -> dict[str, Any]:
    """`dismiss` and `snooze` (off, user, everyone) become the four stored fields (D-184).
    Left out, a field keeps the default from the integration options."""
    data = dict(data)
    if (dismiss := data.pop("dismiss", None)) is not None:
        data["dismissible"] = dismiss != "off"
        if dismiss != "off":
            data["dismiss_scope"] = "global" if dismiss == "everyone" else "user"
    if (snooze := data.pop("snooze", None)) is not None:
        data["snoozable"] = snooze != "off"
        if snooze != "off":
            data["snooze_scope"] = "global" if snooze == "everyone" else "user"
    return data


def _map_policies(data: dict[str, Any]) -> dict[str, Any]:
    """The policies of a call (D-187, D-189). Named policies are manual ones: they apply next to
    the automatic policies that match, unless `match_policies_automatically` is off. Stored as
    the list `matching.select` reads: `automatic` plus the names, the names alone, or `none`."""
    data = dict(data)
    disable = not data.pop("match_policies_automatically", True)
    names: list[str] = list(data.get("policy", []))
    if names == [POLICY_NONE]:
        return data
    if disable:
        if POLICY_AUTOMATIC in names:
            raise vol.Invalid(
                "automatic cannot be combined with match_policies_automatically: false",
                path=["match_policies_automatically"],
            )
        data["policy"] = names or [POLICY_NONE]
    elif names and POLICY_AUTOMATIC not in names:
        data["policy"] = [POLICY_AUTOMATIC, *names]
    return data


def _check_policy(names: list[str]) -> list[str]:
    """Keywords in any case; `none` stands alone, `automatic` may stand next to names (D-184)."""
    names = [n.casefold() if n.casefold() in (POLICY_NONE, POLICY_AUTOMATIC) else n for n in names]
    if len(set(names)) != len(names):
        raise vol.Invalid("policy must not repeat a name", path=["policy"])
    if POLICY_NONE in names and len(names) > 1:
        raise vol.Invalid("none cannot be combined with other policies", path=["policy"])
    return names


def _expand_targets(data: dict[str, Any]) -> dict[str, Any]:
    """`recipients` or `audience` of the call become the target of every channel that takes people
    and has no `to` entry of its own; `speakers` is the target of speech (D-184)."""
    if "audience" in data and "recipients" in data:
        raise vol.Invalid("give either audience or recipients, not both", path=["recipients"])
    data = dict(data)
    to = dict(data.get("to", {}))
    shared = {k: data[k] for k in ("audience", "recipients") if k in data}
    for channel in data["channels"]:
        if channel in to or channel == "persistent":
            continue
        if channel == "speak":
            if "speakers" in data:
                to[channel] = {"recipients": data["speakers"]}
        elif shared:
            to[channel] = dict(shared)
    for key in ("audience", "recipients", "speakers"):
        data.pop(key, None)
    if to:
        data["to"] = to
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
    # Removed in 1.0.0 (D-188): accepted and ignored so an old automation does not fail.
    vol.Optional(REMOVED_WAIT): cv.boolean,
    vol.Optional("people"): vol.All(cv.ensure_list, [cv.entity_domain("person")]),
    vol.Optional("actions"): ACTIONS_SCHEMA,
    vol.Optional("tap_action"): TAP_ACTION_SCHEMA,
    vol.Optional("image"): IMAGE,
}


def _banner_target(data: dict[str, Any]) -> dict[str, Any]:
    """`audience`, `recipients` and `people` name who sees the banner: one of them (D-195)."""
    if len([k for k in ("audience", "recipients", "people") if k in data]) > 1:
        raise vol.Invalid("give only one of audience, recipients and people", path=["recipients"])
    return data


CREATE_SCHEMA = vol.All(
    vol.Schema(
        {
            **_CREATE_FIELDS,
            vol.Optional("audience"): NAME,
            vol.Optional("recipients"): vol.All(cv.ensure_list, [cv.entity_domain("person")]),
        }
    ),
    _check_create,
    _banner_target,
)

# `notify` takes the lifecycle of `create_banner` (D-087). Banner recipients replace `people`.
_NOTIFY_FIELDS = {
    k: v
    for k, v in _CREATE_FIELDS.items()
    if str(k)
    not in ("people", "dismissible", "dismiss_scope", "snoozable", "snooze_scope", "severity")
}
# `notify` has no default severity: a caller states it (D-192). The shortcuts default to info
# (D-189); `create_banner` and the rules keep warning.
ACTION_SEVERITY = "info"
_NOTIFY_FIELDS[vol.Required("severity")] = vol.In(SEVERITIES)


def _who_can(value: Any) -> Any:
    # YAML 1.1 reads an unquoted `off` as false, which is what a hand-written call gives.
    return "off" if value is False else value


WHO_CAN = vol.All(_who_can, vol.In(("off", "user", "everyone")))
TARGET_SCHEMA = vol.Schema(
    {
        vol.Optional("audience"): NAME,
        vol.Optional("recipients"): vol.All(cv.ensure_list, [cv.string]),
    }
)
# In the schema, not in services.yaml or docs/actions.md.
HIDDEN_FIELDS = {"notify": {"to", REMOVED_WAIT}, "create_banner": {REMOVED_WAIT}}
NOTIFY_SCHEMA = vol.All(
    vol.Schema(
        {
            **_NOTIFY_FIELDS,
            vol.Optional("tts_message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
            vol.Required("channels"): vol.All(
                cv.ensure_list, [vol.In(CHANNELS)], vol.Length(min=1)
            ),
            # Accepted but not offered in the form or the docs (D-185): Test send, tests and the
            # stored messages use it. Open: a per-channel target for callers (OPEN_QUESTIONS).
            vol.Optional("to"): {vol.In(CHANNELS): TARGET_SCHEMA},
            vol.Optional("dismiss"): WHO_CAN,
            vol.Optional("snooze"): WHO_CAN,
            vol.Optional("audience"): NAME,
            vol.Optional("recipients"): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional("speakers"): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional("policy"): vol.All(
                cv.ensure_list, [vol.All(cv.string, vol.Length(min=1))], _check_policy
            ),
            vol.Optional("match_policies_automatically"): cv.boolean,
            vol.Optional("dry_run"): cv.boolean,
            vol.Optional("mail_subject"): _mail_template(check_subject),
            vol.Optional("mail_body"): _mail_template(check_body),
        }
    ),
    _map_interaction,
    _map_policies,
    _check_create,
    _expand_targets,
    _check_notify,
)


# Shortcuts: one fixed channel, a target, no policies (D-083).
def _shortcut_schema(channel: str) -> VolSchemaType:
    fields: dict[Any, Any] = {
        vol.Optional("id"): SLUG,
        **_CONTENT_FIELDS,
        vol.Optional("severity", default=ACTION_SEVERITY): vol.In(SEVERITIES),
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


_LOGGER = logging.getLogger(__name__)

CLEAR_SCHEMA = vol.All(
    vol.Schema({vol.Optional("id"): SLUG, vol.Optional("tag"): SLUG}),
    cv.has_at_least_one_key("id", "tag"),
)
CLEAR_ALL_SCHEMA = vol.Schema({})


def _check_clear_notifications(data: dict[str, Any]) -> dict[str, Any]:
    """A call names what to clear: at least one filter, or `all: true` alone (D-158)."""
    filters = [key for key in ("id", "tag", "severity", "channels") if key in data]
    if data.get("all"):
        if filters:
            raise vol.Invalid("all cannot be combined with other fields", path=["all"])
    elif not filters:
        raise vol.Invalid("give at least one of id, tag, severity, channels, or all: true")
    return data


CLEAR_NOTIFICATIONS_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional("id"): SLUG,
            vol.Optional("tag"): SLUG,
            vol.Optional("severity"): vol.All(
                cv.ensure_list, [vol.In(SEVERITIES)], vol.Length(min=1)
            ),
            vol.Optional("channels"): vol.All(
                cv.ensure_list, [vol.In(CHANNELS)], vol.Length(min=1)
            ),
            vol.Optional("all"): bool,
        }
    ),
    _check_clear_notifications,
)
SHORTCUT_CHANNELS = ("push", "popup", "speak")
GET_TRACE_SCHEMA = vol.Schema(
    {
        vol.Optional("message_id"): vol.All(cv.string, vol.Length(min=1, max=100)),
        vol.Optional("limit", default=100): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
    }
)

SCHEMAS: dict[str, VolSchemaType] = {
    "create_banner": CREATE_SCHEMA,
    "clear_banner": CLEAR_SCHEMA,
    "clear_all": CLEAR_ALL_SCHEMA,
    "clear_notifications": CLEAR_NOTIFICATIONS_SCHEMA,
    "notify": NOTIFY_SCHEMA,
    "get_trace": GET_TRACE_SCHEMA,
    **{channel: _shortcut_schema(channel) for channel in SHORTCUT_CHANNELS},
}


def _where(path: list[Any]) -> str:
    """`channels[0]` as the field name and place a person can find."""
    text = ""
    for part in path:
        text += f"[{part}]" if isinstance(part, int) else (f".{part}" if text else str(part))
    return text or "the call"


def _sentence(error: vol.Invalid) -> str:
    """One validation error as a sentence a person can act on (D-168). Messages this does not
    know pass through unchanged."""
    field = _where(list(error.path))
    msg = error.msg
    if msg == "required key not provided":
        return f"The field {field} is required."
    if msg == "not a valid option":
        return f"{field} is not a field of this action."
    if msg.startswith("value must be one of "):
        options = re.findall(r"'([^']*)'", msg)
        return f"{field} must be one of: {', '.join(options)}."
    if match := re.fullmatch(r"length of value must be at (most|least) (\d+)", msg):
        limit = match.group(2)
        word = "at most" if match.group(1) == "most" else "at least"
        return f"{field} must have {word} {limit} characters or entries."
    return f"{field}: {msg}" if error.path else msg


class _Readable:
    """A call schema that reports its errors as sentences. The raw schema stays in `SCHEMAS`,
    because docs-check reads its fields."""

    def __init__(self, schema: VolSchemaType) -> None:
        self.schema = schema

    def __call__(self, data: Any) -> Any:
        try:
            return self.schema(data)
        except vol.Invalid as err:
            errors = getattr(err, "errors", None) or [err]
            text = " ".join(_sentence(e) for e in errors)
            raise vol.Invalid(text, path=list(errors[0].path)) from err


def _manager(hass: HomeAssistant) -> BannerManager:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")
    manager: BannerManager = entries[0].runtime_data
    return manager


def _drop_removed(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Remove `wait_for_condition` from a call and raise the repair issue once (D-192). The field
    is ignored: a banner whose condition is false now waits."""
    if REMOVED_WAIT in data:
        data = {k: v for k, v in data.items() if k != REMOVED_WAIT}
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_WAIT_REMOVED,
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_WAIT_REMOVED,
        )
    return data


async def _create(call: ServiceCall) -> ServiceResponse:
    manager = _manager(call.hass)
    data = _drop_removed(call.hass, dict(call.data))
    target: dict[str, Any] = {k: data.pop(k) for k in ("audience", "recipients") if k in data}
    if target:
        if (hub := manager.hub) is None:
            raise _hub_off()
        target = _check_names(hub, {CHANNEL_BANNER: target}, None)[0][CHANNEL_BANNER]
        if people := await banner_people(hub, target, data.get("severity")):
            data["people"] = people  # the audience as of now, like `notify` (D-131)
    return manager.create(data)


def _warn_deprecated(hass: HomeAssistant, name: str) -> None:
    """One log warning per action and Home Assistant start (D-158)."""
    warned: set[str] = hass.data.setdefault(f"{DOMAIN}_deprecation_warned", set())
    if name not in warned:
        warned.add(name)
        _LOGGER.warning(
            "The action %s.%s is deprecated and will be removed in a future major version;"
            " use %s.clear_notifications",
            DOMAIN,
            name,
            DOMAIN,
        )


async def _clear(call: ServiceCall) -> ServiceResponse:
    _warn_deprecated(call.hass, "clear_banner")
    return {"cleared": _manager(call.hass).clear(call.data.get("id"), call.data.get("tag"))}


async def _clear_all(call: ServiceCall) -> ServiceResponse:
    _warn_deprecated(call.hass, "clear_all")
    return {"cleared": _manager(call.hass).clear_all()}


async def _clear_notifications(call: ServiceCall) -> ServiceResponse:
    # Any message, also one without the banner channel; clear_banner skips those (D-108, D-158).
    data = call.data
    cleared = _manager(call.hass).clear(
        data.get("id"),
        data.get("tag"),
        all_channels=True,
        severities=data.get("severity"),
        channels=data.get("channels"),
    )
    return {"cleared": cleared}


async def _get_trace(call: ServiceCall) -> ServiceResponse:
    """The delivery trace, newest first: why a message did or did not arrive (D-194)."""
    if (hub := _manager(call.hass).hub) is None:
        raise _hub_off()
    entries = hub.trace.entries(call.data.get("message_id"), call.data["limit"])
    return cast(ServiceResponse, {"entries": entries})


def _hub_off() -> ServiceValidationError:
    return ServiceValidationError(translation_domain=DOMAIN, translation_key="hub_off")


def _unknown(key: str, name: str, valid: list[str]) -> ServiceValidationError:
    shown = ", ".join(valid[:20]) + (" ..." if len(valid) > 20 else "")
    placeholders = {"name": name, "valid": shown or "none exist yet"}
    lowered = {v.lower(): v for v in valid}
    if close := difflib.get_close_matches(name.lower(), list(lowered), n=1, cutoff=0.7):
        placeholders["suggestion"] = lowered[close[0]]
        key = f"{key}_hint"  # the same message with "Did you mean ...?" (D-167)
    return ServiceValidationError(
        translation_domain=DOMAIN, translation_key=key, translation_placeholders=placeholders
    )


def _canonical(name: str, valid: list[str]) -> str | None:
    """The stored spelling of a name: exact, or the only one that differs in case (D-167)."""
    if name in valid:
        return name
    same = [v for v in valid if v.lower() == name.lower()]
    return same[0] if len(same) == 1 else None


def _check_names(
    hub: HubEngine, to: dict[str, dict[str, Any]], policy: str | list[str] | None
) -> tuple[dict[str, dict[str, Any]], str | list[str] | None]:
    """Check the names of a call and return them in their stored spelling (D-167).

    A name that differs only in case is accepted; one that matches nothing fails with the valid
    names and, when a close one exists, a suggestion."""
    fixed: dict[str, dict[str, Any]] = {}
    for channel, target in to.items():
        target = dict(target)
        if (audience := target.get("audience")) is not None:
            audience = hub.resolver.audience_for_entity(audience) or audience
            names = hub.audiences.names()
            if (stored := _canonical(audience, names)) is None:
                raise _unknown("unknown_audience", audience, names)
            target["audience"] = stored
        if "recipients" in target:
            known = hub.recipients.known(channel)
            recipients = []
            for recipient in target["recipients"]:
                if hub.recipients.accepts(channel, recipient):
                    recipients.append(recipient)
                elif (stored := _canonical(recipient, known)) is not None:
                    recipients.append(stored)
                else:
                    raise _unknown("unknown_recipient", recipient, known)
            target["recipients"] = recipients
        fixed[channel] = target
    return fixed, _check_policy_names(hub, policy)


def _check_policy_names(hub: HubEngine, policy: str | list[str] | None) -> str | list[str] | None:
    """Policy names in their stored spelling. One name stays a string, as stored before D-184;
    `automatic` alone is the same as no policy."""
    wanted = [hub.policies.policy_for_entity(n) or n for n in policy_names(policy)]
    if wanted in ([], [POLICY_AUTOMATIC]) or wanted == [POLICY_NONE]:
        return POLICY_NONE if wanted == [POLICY_NONE] else None
    known = hub.policies.names()
    fixed: list[str] = []
    for name in wanted:
        if name == POLICY_AUTOMATIC:
            fixed.append(name)
        elif (stored := _canonical(name, known)) is None:
            raise _unknown("unknown_policy", name, known)
        else:
            fixed.append(stored)
    return fixed[0] if len(fixed) == 1 else fixed


def _response(result: dict[str, Any], planned: list[Planned] | None) -> dict[str, Any]:
    counts = HubEngine.counts(planned) if planned is not None else {}
    reasons = HubEngine.reasons(planned) if planned is not None else []
    return {**result, "channels": counts, "reasons": reasons}


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
    data = _drop_removed(call.hass, dict(call.data))
    to: dict[str, dict[str, Any]] = data.pop("to", {})
    if (hub := manager.hub) is None:
        raise _hub_off()
    dry_run = data.pop("dry_run", False)
    to, policy = _check_names(hub, to, data.get("policy"))
    if policy is not None:
        data["policy"] = policy
    if dry_run:
        # Imported here: panel_test imports this module for the schema (D-194).
        from .hub import panel_test

        draft = await panel_test.banner_from(hub, {**data, "to": to})
        return {"status": "dry_run", **await hub.preview(draft)}
    if people := await banner_people(hub, to.get(CHANNEL_BANNER, {}), data.get("severity")):
        data["people"] = people  # the card's own targeting (D-008, D-131)
    data["targets"] = to
    delivered = hub.delivered(data.get("id"))
    result = manager.create(data)
    banner = manager.banners.get(result["id"])
    if banner is None:
        return _response(result, [])
    return _response(
        result,
        await hub.plan(banner, waiting=result["status"] == "waiting", delivered=delivered),
    )


def _shortcut(channel: str) -> Callable[[ServiceCall], Coroutine[Any, Any, ServiceResponse]]:
    async def handler(call: ServiceCall) -> ServiceResponse:
        manager = _manager(call.hass)
        if (hub := manager.hub) is None:
            raise _hub_off()
        data = dict(call.data)
        target: dict[str, Any] = {k: data.pop(k) for k in ("audience", "recipients") if k in data}
        target = _check_names(hub, {channel: target}, None)[0][channel]
        if "id" in data:
            data.update(channels=[channel], targets={channel: target}, source=SOURCE_ACTION)
            delivered = hub.delivered(data["id"])
            result = manager.create(data)
            banner = manager.banners[result["id"]]
            return _response(result, await hub.plan(banner, delivered=delivered))
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
        ("clear_notifications", _clear_notifications),
        ("notify", _notify),
        ("get_trace", _get_trace),
        *((c, _shortcut(c)) for c in SHORTCUT_CHANNELS),
    ):
        hass.services.async_register(
            DOMAIN,
            name,
            handler,
            schema=cast(VolSchemaType, _Readable(SCHEMAS[name])),
            supports_response=(
                SupportsResponse.ONLY if name == "get_trace" else SupportsResponse.OPTIONAL
            ),
        )
