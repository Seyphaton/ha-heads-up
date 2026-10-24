"""Actions: create_banner, clear_banner, clear_all (DESIGN §7)."""

from __future__ import annotations

from datetime import timedelta

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import VolSchemaType

from .const import (
    DISMISS_SCOPES,
    DOMAIN,
    ID_PATTERN,
    MAX_MESSAGE,
    MAX_TIMEOUT_DAYS,
    MAX_TITLE,
    SEVERITIES,
)
from .manager import BannerManager


def _timeout(value: timedelta) -> timedelta:
    if value < timedelta(0) or value > timedelta(days=MAX_TIMEOUT_DAYS):
        raise vol.Invalid(f"timeout must be 0 or between 1 second and {MAX_TIMEOUT_DAYS} days")
    return value


SLUG = vol.All(cv.string, vol.Match(ID_PATTERN))

CREATE_SCHEMA = vol.Schema(
    {
        vol.Optional("id"): SLUG,
        vol.Required("message"): vol.All(cv.string, vol.Length(min=1, max=MAX_MESSAGE)),
        vol.Optional("title"): vol.All(cv.string, vol.Length(max=MAX_TITLE)),
        vol.Optional("severity"): vol.In(SEVERITIES),
        vol.Optional("icon"): cv.icon,
        vol.Optional("timeout"): vol.All(cv.time_period, _timeout),
        vol.Optional("dismissible"): cv.boolean,
        vol.Optional("dismiss_scope"): vol.In(DISMISS_SCOPES),
        vol.Optional("tag"): SLUG,
        # Passed to the card unchanged (D-015).
        vol.Optional("tap_action"): vol.Schema(
            {vol.Required("action"): cv.string}, extra=vol.ALLOW_EXTRA
        ),
    }
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
