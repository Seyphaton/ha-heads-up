"""Actions: create_banner, clear_banner, clear_all (DESIGN §7)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import VolSchemaType
from jinja2 import Environment, TemplateSyntaxError

from .conditions import DEFAULT_OPERATOR, NO_STATE_OPERATORS, OPERATORS, check_state
from .const import (
    DISMISS_SCOPES,
    DOMAIN,
    ID_PATTERN,
    MAX_FOR_SECONDS,
    MAX_MESSAGE,
    MAX_SNOOZE_OPTIONS,
    MAX_SNOOZE_SECONDS,
    MAX_TIMEOUT_DAYS,
    MAX_TITLE,
    MIN_SNOOZE_SECONDS,
    MODES,
    SEVERITIES,
    SNOOZE_SCOPES,
)
from .manager import BannerManager


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


def _check_create(data: dict[str, Any]) -> dict[str, Any]:
    # An unhideable banner cannot be snoozed either (D-069).
    if data.get("snoozable") and data.get("dismissible") is False:
        raise vol.Invalid(
            "a banner that is not dismissible cannot be snoozable", path=["snoozable"]
        )
    return data


SLUG = vol.All(cv.string, vol.Match(ID_PATTERN))

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

CREATE_SCHEMA = vol.All(
    vol.Schema(
        {
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
            vol.Optional("tap_action"): vol.Schema(
                {vol.Required("action"): cv.string}, extra=vol.ALLOW_EXTRA
            ),
        }
    ),
    _check_create,
)
CLEAR_SCHEMA = vol.All(
    vol.Schema({vol.Optional("id"): SLUG, vol.Optional("tag"): SLUG}),
    cv.has_at_least_one_key("id", "tag"),
)
CLEAR_ALL_SCHEMA = vol.Schema({})

SCHEMAS: dict[str, VolSchemaType] = {
    "create_banner": CREATE_SCHEMA,
    "clear_banner": CLEAR_SCHEMA,
    "clear_all": CLEAR_ALL_SCHEMA,
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


def async_setup_services(hass: HomeAssistant) -> None:
    # Registered in async_setup so calls fail with not_loaded instead of "unknown action"
    # while the entry is not loaded. SupportsResponse: HA_API_NOTES N-3.
    for name, handler in (
        ("create_banner", _create),
        ("clear_banner", _clear),
        ("clear_all", _clear_all),
    ):
        hass.services.async_register(
            DOMAIN, name, handler, schema=SCHEMAS[name], supports_response=SupportsResponse.OPTIONAL
        )
