"""Config flow for Heads Up: one entry, no input; options flow for limits and defaults (D-026).

Watch rules are subentries of that entry (DESIGN §17, D-052).
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentry,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    BooleanSelector,
    DurationSelector,
    DurationSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
)
from homeassistant.helpers.template import Template

from .conditions import DEFAULT_OPERATOR, NO_STATE_OPERATORS, OPERATORS, check_state
from .const import (
    DEFAULT_OPTIONS,
    DEFAULT_SEVERITY,
    DEFAULT_SNOOZE_SECONDS,
    DISMISS_SCOPES,
    DOMAIN,
    MAX_FOR_SECONDS,
    MAX_MESSAGE,
    MAX_TITLE,
    OPT_DEFAULT_DISMISS_SCOPE,
    OPT_DEFAULT_SNOOZABLE,
    OPT_DEFAULT_SNOOZE_OPTIONS,
    OPT_DEFAULT_SNOOZE_SCOPE,
    OPT_DEFAULT_TIMEOUT,
    OPT_EVICT,
    OPT_MAX_BANNERS,
    RULE_SUBENTRY,
    SEVERITIES,
    SNOOZE_PRESET_MINUTES,
    SNOOZE_SCOPES,
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

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {RULE_SUBENTRY: RuleSubentryFlow}


def _seconds_to_duration(seconds: int) -> dict[str, int]:
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, secs = divmod(rest, 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": secs}


def _snooze_seconds(minutes: list[str] | None) -> list[int]:
    # An empty choice falls back to the defaults, so a snoozable banner always has a menu.
    chosen = sorted({int(m) * 60 for m in minutes or []})
    return chosen or list(DEFAULT_SNOOZE_SECONDS)


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
                    OPT_DEFAULT_SNOOZABLE: user_input.get(
                        OPT_DEFAULT_SNOOZABLE, DEFAULT_OPTIONS[OPT_DEFAULT_SNOOZABLE]
                    ),
                    OPT_DEFAULT_SNOOZE_SCOPE: user_input.get(
                        OPT_DEFAULT_SNOOZE_SCOPE, DEFAULT_OPTIONS[OPT_DEFAULT_SNOOZE_SCOPE]
                    ),
                    OPT_DEFAULT_SNOOZE_OPTIONS: _snooze_seconds(
                        user_input.get(OPT_DEFAULT_SNOOZE_OPTIONS)
                    ),
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
                vol.Required(
                    OPT_DEFAULT_SNOOZABLE, default=current[OPT_DEFAULT_SNOOZABLE]
                ): BooleanSelector(),
                vol.Required(
                    OPT_DEFAULT_SNOOZE_SCOPE, default=current[OPT_DEFAULT_SNOOZE_SCOPE]
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=list(SNOOZE_SCOPES), translation_key="snooze_scope"
                    )
                ),
                vol.Required(
                    OPT_DEFAULT_SNOOZE_OPTIONS,
                    default=[str(s // 60) for s in current[OPT_DEFAULT_SNOOZE_OPTIONS]],
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[str(m) for m in SNOOZE_PRESET_MINUTES],
                        multiple=True,
                        translation_key="snooze_minutes",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


_RULE_SCHEMA = vol.Schema(
    {
        vol.Required("name"): TextSelector(),
        vol.Required("entity_id"): EntitySelector(),
        vol.Required("operator", default=DEFAULT_OPERATOR): SelectSelector(
            SelectSelectorConfig(options=list(OPERATORS), translation_key="operator")
        ),
        # No prefilled value: an empty field means "on" for equals and not_equals (D-068).
        vol.Optional("state"): TextSelector(TextSelectorConfig(multiple=True)),
        vol.Optional("attribute"): TextSelector(),
        vol.Optional("for"): DurationSelector(DurationSelectorConfig(enable_day=True)),
        vol.Required("message"): TextSelector(TextSelectorConfig(multiline=True)),
        vol.Optional("title"): TextSelector(),
        vol.Required("severity", default=DEFAULT_SEVERITY): SelectSelector(
            SelectSelectorConfig(options=list(SEVERITIES), translation_key="severity")
        ),
        vol.Optional("icon"): IconSelector(),
        vol.Optional("people", default=[]): EntitySelector(
            EntitySelectorConfig(domain="person", multiple=True)
        ),
        vol.Required("dismissible", default=False): BooleanSelector(),
        vol.Required("enabled", default=True): BooleanSelector(),
    }
)


def _states(user_input: dict[str, Any]) -> list[str]:
    operator = user_input.get("operator", DEFAULT_OPERATOR)
    if operator in NO_STATE_OPERATORS:
        return []
    states = [s.strip() for s in user_input.get("state") or [] if s.strip()]
    if not states and operator in ("equals", "not_equals"):
        return ["on"]
    return states


def _rule_data(user_input: dict[str, Any]) -> dict[str, Any]:
    """Subentry data: everything but the name; empty optional fields are left out."""
    data = {key: value for key, value in user_input.items() if key != "name"}
    if states := _states(user_input):
        data["state"] = states
    else:
        data.pop("state", None)
    data["message"] = data["message"].strip()
    for key in ("attribute", "title", "icon"):
        if not (data.get(key) or "").strip():
            data.pop(key, None)
    # The duration selector gives a dict; the rule stores seconds, none when empty (D-066).
    seconds = _for_seconds(data.pop("for", None))
    if seconds:
        data["for"] = seconds
    return data


def _for_seconds(value: Any) -> int:
    if not value:
        return 0
    if isinstance(value, dict):
        return int(cv.time_period_dict(value).total_seconds())
    return int(value)


class RuleSubentryFlow(ConfigSubentryFlow):
    """Add or change a watch rule (D-052)."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return self._rule_step("user", user_input, None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return self._rule_step("reconfigure", user_input, self._get_reconfigure_subentry())

    def _rule_step(
        self, step_id: str, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = self._validate(user_input)
            if not errors:
                data = _rule_data(user_input)
                if subentry is None:
                    return self.async_create_entry(title=user_input["name"], data=data)
                return self.async_update_and_abort(
                    self._get_entry(), subentry, title=user_input["name"], data=data
                )
        suggested = user_input or (
            {"name": subentry.title, **subentry.data} if subentry is not None else None
        )
        if suggested and isinstance(suggested.get("for"), int):
            suggested = {**suggested, "for": _seconds_to_duration(suggested["for"])}
        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(_RULE_SCHEMA, suggested),
            errors=errors,
            # The frontend reads a literal {name} in a translation as a missing placeholder.
            description_placeholders={"name_token": "{name}"},
        )

    def _validate(self, user_input: dict[str, Any]) -> dict[str, str]:
        errors: dict[str, str] = {}
        if self.hass.states.get(user_input["entity_id"]) is None:
            errors["entity_id"] = "entity_not_found"
        if error := check_state(user_input.get("operator", DEFAULT_OPERATOR), _states(user_input)):
            errors["state"] = error
        message = user_input["message"].strip()
        if not message:
            errors["message"] = "message_required"
        elif len(message) > MAX_MESSAGE:
            errors["message"] = "message_too_long"
        else:
            try:
                Template(message, self.hass).ensure_valid()
            except TemplateError:
                errors["message"] = "message_template_invalid"
        if _for_seconds(user_input.get("for")) > MAX_FOR_SECONDS:
            errors["for"] = "for_too_long"
        if len(user_input.get("title") or "") > MAX_TITLE:
            errors["title"] = "title_too_long"
        return errors
