"""Subentry flows for audiences, recipient groups and recipient profiles (D-088, D-097).

Same pattern as the watch rule flow: one form to add, one to reconfigure, errors as translation
keys. Storage stays in config subentries; the panel will use these same flows (UX_SPEC).
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigSubentry, ConfigSubentryFlow, SubentryFlowResult
from homeassistant.helpers.selector import (
    AreaSelector,
    AreaSelectorConfig,
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TimeSelector,
)

from ..const import (
    AUDIENCE_KINDS,
    AUDIENCE_SUBENTRY,
    FALLBACK_WHEN,
    GROUP_SUBENTRY,
    GROUP_SUFFIX,
    POLICY_CHANNELS,
    POLICY_NONE,
    POLICY_SUBENTRY,
    POLICY_TYPES,
    PRESENCE_KINDS,
    PROFILE_CHANNELS,
    PROFILE_SUBENTRY,
    QUIET_ACTIONS,
    SEVERITIES,
    WEEKDAYS,
    ZONE_KINDS,
)
from .audiences import BUILTINS
from .policies import away, escalation, fallback, quiet, reminder, summarize
from .policies.matching import duplicate_of
from .policies.models import (
    DEFAULT_AFTER_MINUTES,
    DEFAULT_EVERY_MINUTES,
    DEFAULT_MAX_REMINDERS,
    DEFAULT_QUIET_FROM,
    DEFAULT_QUIET_TO,
    DEFAULT_SUMMARY_EVERY,
    Policy,
    parse_policy,
    policy_from_data,
)
from .recipients import SPEAKER_DOMAINS, area_exists, registrations


def _names_taken(flow: ConfigSubentryFlow, subentry_type: str, own: str | None) -> set[str]:
    """Lowercase titles of the other subentries of this type."""
    return {
        s.title.casefold()
        for s in flow._get_entry().subentries.values()
        if s.subentry_type == subentry_type and s.subentry_id != own
    }


class _HubFlow(ConfigSubentryFlow):
    """Add and reconfigure share one form; subclasses give schema, checks and data."""

    subentry_type = ""

    def _schema(self, reconfigure: bool) -> vol.Schema:
        raise NotImplementedError

    def _check(self, user_input: dict[str, Any], own: str | None) -> dict[str, str]:
        raise NotImplementedError

    def _title(self, user_input: dict[str, Any], subentry: ConfigSubentry | None) -> str:
        return str(user_input["name"]).strip()

    def _data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def _suggested(self, subentry: ConfigSubentry) -> dict[str, Any]:
        return {"name": subentry.title, **subentry.data}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return self._step("user", user_input, None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return self._step("reconfigure", user_input, self._get_reconfigure_subentry())

    def _step(
        self, step_id: str, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        own = subentry.subentry_id if subentry else None
        if user_input is not None:
            errors = self._check(user_input, own)
            if not errors:
                title = self._title(user_input, subentry)
                data = self._data(user_input)
                if subentry is None:
                    return self.async_create_entry(title=title, data=data)
                return self.async_update_and_abort(
                    self._get_entry(), subentry, title=title, data=data
                )
        suggested = user_input or (self._suggested(subentry) if subentry is not None else None)
        return self.async_show_form(
            step_id=step_id,
            data_schema=self.add_suggested_values_to_schema(
                self._schema(subentry is not None), suggested
            ),
            errors=errors,
        )


class AudienceSubentryFlow(_HubFlow):
    subentry_type = AUDIENCE_SUBENTRY

    def _schema(self, reconfigure: bool) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): TextSelector(),
                vol.Required("kind", default="persons"): SelectSelector(
                    SelectSelectorConfig(
                        options=list(AUDIENCE_KINDS), translation_key="audience_kind"
                    )
                ),
                vol.Optional("persons"): EntitySelector(
                    EntitySelectorConfig(domain="person", multiple=True)
                ),
                vol.Optional("presence"): SelectSelector(
                    SelectSelectorConfig(
                        options=list(PRESENCE_KINDS), translation_key="presence_kind"
                    )
                ),
                vol.Optional("zone"): EntitySelector(EntitySelectorConfig(domain="zone")),
            }
        )

    def _check(self, user_input: dict[str, Any], own: str | None) -> dict[str, str]:
        errors: dict[str, str] = {}
        name = str(user_input["name"]).strip()
        if not name:
            errors["name"] = "name_required"
        elif name.casefold() in {b.casefold() for b in BUILTINS} | _names_taken(
            self, AUDIENCE_SUBENTRY, own
        ):
            errors["name"] = "name_exists"
        if user_input["kind"] == "persons":
            if not user_input.get("persons"):
                errors["persons"] = "persons_required"
        else:
            presence = user_input.get("presence")
            if not presence:
                errors["presence"] = "presence_required"
            elif presence in ZONE_KINDS and not user_input.get("zone"):
                errors["zone"] = "zone_required"
        return errors

    def _data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        if user_input["kind"] == "persons":
            return {"kind": "persons", "persons": list(user_input["persons"])}
        data: dict[str, Any] = {"kind": "presence", "presence": user_input["presence"]}
        if user_input["presence"] in ZONE_KINDS:
            data["zone"] = user_input["zone"]
        return data


class RecipientGroupSubentryFlow(_HubFlow):
    subentry_type = GROUP_SUBENTRY

    def _schema(self, reconfigure: bool) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): TextSelector(),
                vol.Optional("members"): EntitySelector(
                    EntitySelectorConfig(domain=list(SPEAKER_DOMAINS), multiple=True)
                ),
                vol.Optional("areas"): AreaSelector(AreaSelectorConfig(multiple=True)),
            }
        )

    def _check(self, user_input: dict[str, Any], own: str | None) -> dict[str, str]:
        errors: dict[str, str] = {}
        name = str(user_input["name"]).strip()
        if not name:
            errors["name"] = "name_required"
        elif name.casefold().endswith(GROUP_SUFFIX.casefold()):
            errors["name"] = "name_has_suffix"  # calls add " (group)" themselves
        elif name.casefold() in _names_taken(self, GROUP_SUBENTRY, own):
            errors["name"] = "name_exists"
        members = user_input.get("members") or []
        areas = user_input.get("areas") or []
        if not members and not areas:
            errors["members"] = "group_empty"
        elif any(self.hass.states.get(m) is None for m in members):
            errors["members"] = "member_not_found"
        elif any(not area_exists(self.hass, a) for a in areas):
            errors["areas"] = "area_not_found"
        return errors

    def _data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        return {
            "members": list(user_input.get("members") or []),
            "areas": list(user_input.get("areas") or []),
        }


class RecipientProfileSubentryFlow(_HubFlow):
    """Changes on top of the detected devices of one person. A person without a profile subentry
    still has a profile, derived from the detected devices (D-109)."""

    subentry_type = PROFILE_SUBENTRY

    def _devices(self) -> list[SelectOptionDict]:
        return [
            SelectOptionDict(value=device_id, label=name or device_id)
            for device_id, name in registrations(self.hass).items()
        ]

    def _schema(self, reconfigure: bool) -> vol.Schema:
        devices = SelectSelectorConfig(options=self._devices(), multiple=True, custom_value=False)
        fields: dict[Any, Any] = {}
        if not reconfigure:
            fields[vol.Required("person")] = EntitySelector(EntitySelectorConfig(domain="person"))
        fields.update(
            {
                vol.Optional("devices"): SelectSelector(devices),
                vol.Optional("removed_devices"): SelectSelector(devices),
                vol.Optional("primary"): SelectSelector(
                    SelectSelectorConfig(options=self._devices(), custom_value=False)
                ),
                vol.Required("channels", default=list(PROFILE_CHANNELS)): SelectSelector(
                    SelectSelectorConfig(
                        options=list(PROFILE_CHANNELS),
                        multiple=True,
                        translation_key="profile_channel",
                    )
                ),
            }
        )
        return vol.Schema(fields)

    def _person(self, user_input: dict[str, Any], own: str | None) -> str:
        if own is not None:
            return str(self._get_reconfigure_subentry().data["person"])
        return str(user_input["person"])

    def _check(self, user_input: dict[str, Any], own: str | None) -> dict[str, str]:
        errors: dict[str, str] = {}
        person = self._person(user_input, own)
        if own is None:
            if self.hass.states.get(person) is None:
                errors["person"] = "person_not_found"
            elif any(
                s.data.get("person") == person
                for s in self._get_entry().subentries.values()
                if s.subentry_type == PROFILE_SUBENTRY
            ):
                errors["person"] = "profile_exists"
        known = set(registrations(self.hass))
        for field in ("devices", "removed_devices"):
            if any(d not in known for d in user_input.get(field) or []):
                errors[field] = "device_unknown"
        if set(user_input.get("devices") or []) & set(user_input.get("removed_devices") or []):
            errors["removed_devices"] = "device_added_and_removed"
        if not user_input.get("channels"):
            errors["channels"] = "channels_required"
        return errors

    def _title(self, user_input: dict[str, Any], subentry: ConfigSubentry | None) -> str:
        person = self._person(user_input, subentry.subentry_id if subentry else None)
        state = self.hass.states.get(person)
        return str((state.attributes.get("friendly_name") if state else None) or person)

    def _data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        own = self._reconfigure_id()
        data: dict[str, Any] = {
            "person": self._person(user_input, own),
            "channels": list(user_input["channels"]),
        }
        for field in ("devices", "removed_devices"):
            if user_input.get(field):
                data[field] = list(user_input[field])
        if user_input.get("primary"):
            data["primary"] = user_input["primary"]
        return data

    def _reconfigure_id(self) -> str | None:
        return (
            self._get_reconfigure_subentry().subentry_id if self.source == "reconfigure" else None
        )

    def _suggested(self, subentry: ConfigSubentry) -> dict[str, Any]:
        return dict(subentry.data)


TARGET_CHANNELS_WITH_FIELDS = ("push", "popup", "speak")  # a persistent notification has no target
_MINUTES = NumberSelector(
    NumberSelectorConfig(
        min=1, max=1440, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="min"
    )
)


class PolicySubentryFlow(_HubFlow):
    """The policy types: Escalation, Reminder, Quiet hours, Away, Fallback and Summarize
    (D-079, D-081, D-112, D-113).

    One form for every type; the fields of the other types are ignored and not stored.
    """

    subentry_type = POLICY_SUBENTRY

    def _hub(self) -> Any:
        return getattr(getattr(self._get_entry(), "runtime_data", None), "hub", None)

    def _options(self, names: list[str]) -> SelectSelectorConfig:
        return SelectSelectorConfig(
            options=[SelectOptionDict(value=n, label=n) for n in names],
            custom_value=True,
            multiple=True,
        )

    def _schema(self, reconfigure: bool) -> vol.Schema:
        hub = self._hub()
        audiences = hub.audiences.names() if hub else []
        fields: dict[Any, Any] = {
            vol.Required("name"): TextSelector(),
            vol.Required("type", default=POLICY_TYPES[0]): SelectSelector(
                SelectSelectorConfig(options=list(POLICY_TYPES), translation_key="policy_type")
            ),
            vol.Optional("severities"): SelectSelector(
                SelectSelectorConfig(
                    options=list(SEVERITIES), multiple=True, translation_key="severity"
                )
            ),
            vol.Optional("tags"): SelectSelector(
                SelectSelectorConfig(options=[], custom_value=True, multiple=True)
            ),
            vol.Required("enabled", default=True): BooleanSelector(),
            vol.Optional("after_minutes", default=DEFAULT_AFTER_MINUTES): _MINUTES,
            vol.Optional("channels"): SelectSelector(
                SelectSelectorConfig(
                    options=list(POLICY_CHANNELS), multiple=True, translation_key="channel"
                )
            ),
            vol.Optional("dismiss_acks", default=False): BooleanSelector(),
            vol.Optional("every_minutes", default=DEFAULT_EVERY_MINUTES): _MINUTES,
            vol.Optional("max_count", default=DEFAULT_MAX_REMINDERS): NumberSelector(
                NumberSelectorConfig(min=1, max=20, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional("from_time", default=DEFAULT_QUIET_FROM): TimeSelector(),
            vol.Optional("to_time", default=DEFAULT_QUIET_TO): TimeSelector(),
            vol.Optional("days"): SelectSelector(
                SelectSelectorConfig(
                    options=list(WEEKDAYS), multiple=True, translation_key="weekday"
                )
            ),
            vol.Optional("action", default=QUIET_ACTIONS[0]): SelectSelector(
                SelectSelectorConfig(options=list(QUIET_ACTIONS), translation_key="quiet_action")
            ),
            vol.Optional("critical_passes", default=True): BooleanSelector(),
            vol.Optional("max_wait", default=0): NumberSelector(
                NumberSelectorConfig(min=0, max=10080, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional("summary_every", default=DEFAULT_SUMMARY_EVERY): _MINUTES,
            vol.Optional("summary_at"): TimeSelector(),
            vol.Optional("include_critical", default=False): BooleanSelector(),
            vol.Optional("when", default=FALLBACK_WHEN[0]): SelectSelector(
                SelectSelectorConfig(options=list(FALLBACK_WHEN), translation_key="fallback_when")
            ),
        }
        for channel in TARGET_CHANNELS_WITH_FIELDS:
            if channel != "speak":  # speech takes recipients, not an audience (D-098)
                fields[vol.Optional(f"{channel}_audience")] = SelectSelector(
                    # custom_value: a policy that names a deleted audience must still open (D-111).
                    SelectSelectorConfig(
                        options=[SelectOptionDict(value=n, label=n) for n in audiences],
                        custom_value=True,
                    )
                )
            known = hub.recipients.known(channel) if hub else []
            fields[vol.Optional(f"{channel}_recipients")] = SelectSelector(self._options(known))
        return vol.Schema(fields)

    def _targets(self, user_input: dict[str, Any]) -> dict[str, dict[str, Any]]:
        targets: dict[str, dict[str, Any]] = {}
        for channel in user_input.get("channels") or []:
            target: dict[str, Any] = {}
            if audience := user_input.get(f"{channel}_audience"):
                target["audience"] = audience
            if recipients := user_input.get(f"{channel}_recipients"):
                target["recipients"] = list(recipients)
            if target:
                targets[channel] = target
        return targets

    def _candidate(self, user_input: dict[str, Any], own: str | None) -> Policy:
        candidate = policy_from_data(
            str(user_input["name"]).strip(), own or "", self._data(user_input)
        )
        assert candidate is not None  # the type comes from a selector
        return candidate

    def _check(self, user_input: dict[str, Any], own: str | None) -> dict[str, str]:
        errors: dict[str, str] = {}
        name = str(user_input["name"]).strip()
        if not name:
            errors["name"] = "name_required"
        elif name.casefold() == POLICY_NONE or name.casefold() in _names_taken(
            self, POLICY_SUBENTRY, own
        ):
            errors["name"] = "name_exists"  # `none` means no policy in a call
        kind = user_input["type"]
        if kind == "escalation":
            errors.update(escalation.check(user_input))
            errors.update(self._check_targets(user_input))
        elif kind == "reminder":
            errors.update(reminder.check(user_input))
        elif kind == "quiet_hours":
            errors.update(quiet.check(user_input))
        elif kind == "away":
            errors.update(away.check(user_input))
        elif kind == "summarize":
            errors.update(summarize.check(user_input))
        else:
            errors.update(fallback.check(user_input))
            errors.update(self._check_targets(user_input))
        if not errors:
            existing = [
                p
                for sub in self._get_entry().subentries.values()
                if (p := parse_policy(sub)) is not None
            ]
            if duplicate_of(existing, self._candidate(user_input, own)) is not None:
                errors["base"] = "policy_duplicate"
        return errors

    def _check_targets(self, user_input: dict[str, Any]) -> dict[str, str]:
        """Same rules as the `to` of `notify` (DESIGN §23.5)."""
        errors: dict[str, str] = {}
        hub = self._hub()
        for channel in user_input.get("channels") or []:
            if channel == "persistent":
                continue
            audience = user_input.get(f"{channel}_audience")
            recipients = user_input.get(f"{channel}_recipients")
            field = f"{channel}_recipients" if channel == "speak" else f"{channel}_audience"
            if bool(audience) == bool(recipients):
                errors[field] = "target_exclusive"
            elif hub is not None and audience and audience not in hub.audiences.names():
                errors[field] = "audience_unknown"
            elif hub is not None and any(
                r not in hub.recipients.known(channel) for r in recipients or []
            ):
                errors[f"{channel}_recipients"] = "recipient_unknown"
        return errors

    def _data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": user_input["type"],
            "severities": list(user_input.get("severities") or []),
            "tags": list(user_input.get("tags") or []),
            "enabled": bool(user_input.get("enabled", True)),
        }
        channels = list(user_input.get("channels") or [])
        kind = user_input["type"]
        if kind == "escalation":
            data.update(
                after_minutes=int(user_input["after_minutes"]),
                channels=channels,
                targets=self._targets(user_input),
                dismiss_acks=bool(user_input.get("dismiss_acks", False)),
            )
        elif kind == "reminder":
            data.update(
                every_minutes=int(user_input["every_minutes"]),
                max_count=int(user_input["max_count"]),
                channels=channels,
            )
        elif kind == "quiet_hours":
            data.update(
                from_time=str(user_input.get("from_time") or DEFAULT_QUIET_FROM),
                to_time=str(user_input.get("to_time") or DEFAULT_QUIET_TO),
                days=list(user_input.get("days") or []),
                action=user_input.get("action", QUIET_ACTIONS[0]),
                critical_passes=bool(user_input.get("critical_passes", True)),
            )
        elif kind == "away":
            data["max_wait"] = int(user_input.get("max_wait") or 0)
        elif kind == "summarize":
            data["include_critical"] = bool(user_input.get("include_critical", False))
            if user_input.get("summary_at"):
                data["summary_at"] = str(user_input["summary_at"])
            else:
                data["summary_every"] = int(user_input["summary_every"])
        else:
            data.update(
                when=user_input.get("when", FALLBACK_WHEN[0]),
                channels=channels,
                targets=self._targets(user_input),
            )
        return data

    def _suggested(self, subentry: ConfigSubentry) -> dict[str, Any]:
        suggested = {"name": subentry.title, **subentry.data}
        for channel, target in (subentry.data.get("targets") or {}).items():
            if "audience" in target:
                suggested[f"{channel}_audience"] = target["audience"]
            if "recipients" in target:
                suggested[f"{channel}_recipients"] = target["recipients"]
        return suggested
