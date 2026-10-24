"""Config flow for Heads Up: one entry, no input; options flow for limits and defaults (D-026)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    BooleanSelector,
    DurationSelector,
    DurationSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    DEFAULT_OPTIONS,
    DISMISS_SCOPES,
    DOMAIN,
    OPT_DEFAULT_DISMISS_SCOPE,
    OPT_DEFAULT_TIMEOUT,
    OPT_EVICT,
    OPT_MAX_BANNERS,
)


class HeadsUpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single Heads Up entry."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # Duplicate entries are prevented by "single_config_entry" in manifest.json.
        if user_input is not None:
            return self.async_create_entry(title="Heads Up", data={})
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HeadsUpOptionsFlow:
        return HeadsUpOptionsFlow()


def _seconds_to_duration(seconds: int) -> dict[str, int]:
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, secs = divmod(rest, 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": secs}


class HeadsUpOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            # An empty duration field means "no default timeout" (D-031).
            duration = user_input.get(OPT_DEFAULT_TIMEOUT)
            seconds = int(cv.time_period_dict(duration).total_seconds()) if duration else 0
            return self.async_create_entry(
                data={
                    OPT_MAX_BANNERS: int(user_input[OPT_MAX_BANNERS]),
                    OPT_EVICT: user_input[OPT_EVICT],
                    OPT_DEFAULT_DISMISS_SCOPE: user_input[OPT_DEFAULT_DISMISS_SCOPE],
                    OPT_DEFAULT_TIMEOUT: seconds,
                }
            )

        current = {**DEFAULT_OPTIONS, **self.config_entry.options}
        timeout_field = (
            vol.Optional(
                OPT_DEFAULT_TIMEOUT,
                description={"suggested_value": _seconds_to_duration(current[OPT_DEFAULT_TIMEOUT])},
            )
            if current[OPT_DEFAULT_TIMEOUT]
            else vol.Optional(OPT_DEFAULT_TIMEOUT)
        )
        schema = vol.Schema(
            {
                vol.Required(OPT_MAX_BANNERS, default=current[OPT_MAX_BANNERS]): NumberSelector(
                    NumberSelectorConfig(min=1, max=200, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(OPT_EVICT, default=current[OPT_EVICT]): BooleanSelector(),
                vol.Required(
                    OPT_DEFAULT_DISMISS_SCOPE, default=current[OPT_DEFAULT_DISMISS_SCOPE]
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(DISMISS_SCOPES), translation_key="dismiss_scope"
                    )
                ),
                timeout_field: DurationSelector(DurationSelectorConfig(enable_day=True)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
