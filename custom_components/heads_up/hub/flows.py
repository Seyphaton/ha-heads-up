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
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
)

from ..const import (
    AUDIENCE_KINDS,
    AUDIENCE_SUBENTRY,
    GROUP_SUBENTRY,
    GROUP_SUFFIX,
    PRESENCE_KINDS,
    PROFILE_CHANNELS,
    PROFILE_SUBENTRY,
    ZONE_KINDS,
)
from .audiences import BUILTINS
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
