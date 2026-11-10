"""Config flow for Heads Up: one entry, no input; options flow for limits and defaults (D-026).

Watch rules are subentries of that entry (DESIGN §17, D-052).
"""

from __future__ import annotations

from typing import Any

import probatio as vol
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
from homeassistant.data_entry_flow import section
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
    ObjectSelector,
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
)
from homeassistant.helpers.template import Template

from .conditions import DEFAULT_OPERATOR, NO_STATE_OPERATORS, OPERATORS, check_state
from .const import (
    AUDIENCE_SUBENTRY,
    DEFAULT_OPTIONS,
    DEFAULT_SEVERITY,
    DISMISS_SCOPES,
    DOMAIN,
    GROUP_SUBENTRY,
    MAX_FOR_SECONDS,
    MAX_MESSAGE,
    MAX_TITLE,
    OPT_DEFAULT_SNOOZE_OPTIONS,
    OPT_DEFAULT_TIMEOUT,
    OPT_INSTALL_TOKEN,
    OPT_SHOW_PANEL,
    POLICY_AUTOMATIC,
    POLICY_NONE,
    POLICY_SUBENTRY,
    PROFILE_SUBENTRY,
    RULE_SUBENTRY,
    SEVERITIES,
    SNOOZE_PRESET_MINUTES,
    SNOOZE_SCOPES,
)
from .hub import settings
from .hub.flows import (
    AudienceSubentryFlow,
    PolicySubentryFlow,
    RecipientGroupSubentryFlow,
    RecipientProfileSubentryFlow,
)
from .services import ACTIONS_SCHEMA, IMAGE, TAP_ACTION_SCHEMA


class HeadsUpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single Heads Up entry."""

    VERSION = 2  # 2: stored references are keys, not names (D-200)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # Duplicate entries are prevented by "single_config_entry" in manifest.json.
        if user_input is not None:
            # The sidebar entry is the user's choice at setup (D-107, D-117).
            return self.async_create_entry(
                title="Heads Up",
                data={},
                options={OPT_SHOW_PANEL: bool(user_input.get(OPT_SHOW_PANEL, True))},
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(OPT_SHOW_PANEL, default=True): BooleanSelector()}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HeadsUpOptionsFlow:
        return HeadsUpOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        # The order of the "Add ..." buttons on the integration page: who (audience, recipient
        # group, recipient profile), then when (policy), then watch rules, as in the panel (D-132).
        return {
            AUDIENCE_SUBENTRY: AudienceSubentryFlow,
            GROUP_SUBENTRY: RecipientGroupSubentryFlow,
            PROFILE_SUBENTRY: RecipientProfileSubentryFlow,
            POLICY_SUBENTRY: PolicySubentryFlow,
            RULE_SUBENTRY: RuleSubentryFlow,
        }


def _seconds_to_duration(seconds: int) -> dict[str, int]:
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, secs = divmod(rest, 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": secs}


class HeadsUpOptionsFlow(OptionsFlow):
    """The same sections, order and wording as the panel's Settings page (D-122)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            flat: dict[str, Any] = {}
            for name, _ in settings.SECTIONS:
                flat.update(user_input.get(name) or {})
            for key in settings.RANGES:
                if key in flat:
                    flat[key] = int(flat[key])  # number selectors return floats
            # An empty duration field means "no default timeout" (D-031).
            duration = flat.get(OPT_DEFAULT_TIMEOUT)
            flat[OPT_DEFAULT_TIMEOUT] = (
                int(cv.time_period_dict(duration).total_seconds()) if duration else 0
            )
            if flat[OPT_DEFAULT_TIMEOUT] > settings.MAX_TIMEOUT_SECONDS:
                return self._show(errors={OPT_DEFAULT_TIMEOUT: "timeout_too_long"})
            flat[OPT_DEFAULT_SNOOZE_OPTIONS] = settings.snooze_seconds(
                flat.get(OPT_DEFAULT_SNOOZE_OPTIONS)
            )
            kept = {
                key: flat[key] if key in flat else DEFAULT_OPTIONS[key]
                for key in settings.EDITABLE
                if key in flat or key in DEFAULT_OPTIONS
            }
            # Everything else (install token, push and popup settings, welcome_seen) stays.
            return self.async_create_entry(data={**self.config_entry.options, **kept})
        return self._show()

    def _show(self, errors: dict[str, str] | None = None) -> ConfigFlowResult:
        current = {**DEFAULT_OPTIONS, **self.config_entry.options}
        sections: dict[Any, Any] = {}
        for name, items in settings.SECTIONS:
            fields: dict[Any, Any] = {}
            for key, kind in items:
                field, selector = _option_field(key, kind, current)
                fields[field] = selector
            sections[vol.Required(name)] = section(vol.Schema(fields), {"collapsed": False})
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(sections),
            errors=errors,
            description_placeholders={
                "install_token": str(self.config_entry.options.get(OPT_INSTALL_TOKEN) or "")
            },
        )


def _required(key: str, value: Any) -> Any:
    # Both: the default fills a missing value, the suggested value fills the form (the frontend
    # does not apply defaults inside sections).
    return vol.Required(key, default=value, description={"suggested_value": value})


def _option_field(key: str, kind: str, current: dict[str, Any]) -> tuple[Any, Any]:
    if kind == "bool":
        return _required(key, current[key]), BooleanSelector()
    if kind == "int":
        low, high = settings.RANGES[key]
        return (
            _required(key, current[key]),
            NumberSelector(
                NumberSelectorConfig(min=low, max=high, step=1, mode=NumberSelectorMode.BOX)
            ),
        )
    if kind == "choice":
        return (
            _required(key, current[key]),
            SelectSelector(
                SelectSelectorConfig(
                    options=list(settings.CHOICES[key]),
                    translation_key=key.removeprefix("default_"),
                )
            ),
        )
    if kind == "duration":
        field = (
            vol.Optional(key, description={"suggested_value": _seconds_to_duration(current[key])})
            if current[key]
            else vol.Optional(key)
        )
        return field, DurationSelector(DurationSelectorConfig(enable_day=True))
    if kind == "minutes":
        return (
            _required(key, [str(s // 60) for s in current[key]]),
            SelectSelector(
                SelectSelectorConfig(
                    options=[str(m) for m in SNOOZE_PRESET_MINUTES],
                    multiple=True,
                    translation_key="snooze_minutes",
                )
            ),
        )
    field = (
        vol.Optional(key, description={"suggested_value": current[key]})
        if current[key]
        else vol.Optional(key)
    )
    return field, EntitySelector(EntitySelectorConfig(domain="tts"))


_RULE_SCHEMA = vol.Schema(
    {
        vol.Required("name"): TextSelector(),
        # Exactly one of entity_id and template (DESIGN §22).
        vol.Optional("entity_id"): EntitySelector(),
        vol.Required("operator", default=DEFAULT_OPERATOR): SelectSelector(
            SelectSelectorConfig(options=list(OPERATORS), translation_key="operator")
        ),
        # No prefilled value: an empty field means "on" for equals and not_equals (D-068).
        vol.Optional("state"): TextSelector(TextSelectorConfig(multiple=True)),
        vol.Optional("attribute"): TextSelector(),
        # Plain text, not TemplateSelector: that one rejects a bad template before our own error.
        vol.Optional("template"): TextSelector(TextSelectorConfig(multiline=True)),
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
        vol.Optional("dismiss_scope"): SelectSelector(
            SelectSelectorConfig(options=list(DISMISS_SCOPES), translation_key="dismiss_scope")
        ),
        vol.Optional("snoozable"): BooleanSelector(),
        vol.Optional("snooze_scope"): SelectSelector(
            SelectSelectorConfig(options=list(SNOOZE_SCOPES), translation_key="snooze_scope")
        ),
        vol.Optional("snooze_options"): SelectSelector(
            SelectSelectorConfig(
                options=[str(m) for m in SNOOZE_PRESET_MINUTES],
                multiple=True,
                translation_key="snooze_minutes",
            )
        ),
        vol.Optional("actions"): ObjectSelector(),
        vol.Optional("tap_action"): ObjectSelector(),
        vol.Optional("image"): TextSelector(),
        # A policy name, or none; empty means every automatic policy that applies (D-145).
        vol.Optional("policy"): TextSelector(),
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
    template = (data.pop("template", None) or "").strip()
    if template:
        # A template replaces the entity and everything compared on it.
        for key in ("entity_id", "operator", "state", "attribute"):
            data.pop(key, None)
        data["template"] = template
    elif states := _states(user_input):
        data["state"] = states
    else:
        data.pop("state", None)
    data["message"] = data["message"].strip()
    for key in ("attribute", "title", "icon", "policy"):
        if not (data.get(key) or "").strip():
            data.pop(key, None)
    if "policy" in data:
        data["policy"] = data["policy"].strip()
    # Buttons and tap action go through the same schemas as the action (DESIGN §22).
    if data.get("actions"):
        data["actions"] = ACTIONS_SCHEMA(data["actions"])
    else:
        data.pop("actions", None)
    if data.get("tap_action"):
        data["tap_action"] = TAP_ACTION_SCHEMA(data["tap_action"])
    else:
        data.pop("tap_action", None)
    if (data.get("image") or "").strip():
        data["image"] = IMAGE(data["image"].strip())
    else:
        data.pop("image", None)
    # The duration selector gives a dict; the rule stores seconds, none when empty (D-066).
    seconds = _for_seconds(data.pop("for", None))
    if seconds:
        data["for"] = seconds
    # The form offers minutes; the rule stores seconds. Unset fields use the option defaults.
    if minutes := data.pop("snooze_options", None):
        data["snooze_options"] = settings.snooze_seconds(minutes)
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
        if suggested and suggested.get("snooze_options"):
            suggested = {
                **suggested,
                "snooze_options": [str(s // 60) for s in suggested["snooze_options"]],
            }
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
        template = (user_input.get("template") or "").strip()
        entity_id = user_input.get("entity_id")
        if entity_id and template:
            errors["template"] = "entity_and_template"
        elif template:
            try:
                Template(template, self.hass).ensure_valid()
            except TemplateError:
                errors["template"] = "template_invalid"
        elif not entity_id:
            errors["entity_id"] = "entity_or_template_required"
        else:
            if self.hass.states.get(entity_id) is None:
                errors["entity_id"] = "entity_not_found"
            operator = user_input.get("operator", DEFAULT_OPERATOR)
            if error := check_state(operator, _states(user_input)):
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
        if user_input.get("snoozable") and not user_input.get("dismissible"):
            errors["snoozable"] = "snoozable_needs_dismissible"
        if image := (user_input.get("image") or "").strip():
            try:
                IMAGE(image)
            except vol.Invalid:
                errors["image"] = "image_invalid"
        for field, schema in (("actions", ACTIONS_SCHEMA), ("tap_action", TAP_ACTION_SCHEMA)):
            if user_input.get(field):
                try:
                    checked = schema(user_input[field])
                except vol.Invalid:
                    errors[field] = f"{field}_invalid"
                    continue
                dismisses = field == "actions" and any(button["dismiss"] for button in checked)
                if dismisses and not user_input.get("dismissible"):
                    errors[field] = "actions_dismiss_needs_dismissible"
        if len(user_input.get("title") or "") > MAX_TITLE:
            errors["title"] = "title_too_long"
        if policy := (user_input.get("policy") or "").strip():
            hub = getattr(getattr(self._get_entry(), "runtime_data", None), "hub", None)
            if (
                policy.casefold() not in (POLICY_NONE, POLICY_AUTOMATIC)
                and hub is not None
                and policy not in hub.policies.names()
            ):
                errors["policy"] = "policy_unknown"
        return errors
