"""Data for the panel's editors (D-119): what exists, who uses it, what can be chosen.

Saving goes through the integration's own subentry flows (the panel drives them over the REST
API of Home Assistant) and, for the channel settings, through `channels_set`. So the panel adds
no second copy of the validation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar

from ..binary_sensor import audience_entity_ids
from ..const import (
    AUDIENCE_SUBENTRY,
    DEFAULT_OPTIONS,
    GROUP_SUBENTRY,
    GROUP_SUFFIX,
    MAX_MAIL_ADDRESS,
    OPT_MAIL_ADDRESS,
    OPT_MAIL_BODY,
    OPT_MAIL_SERVICE,
    OPT_MAIL_SUBJECT,
    OPT_POPUP_STYLES,
    OPT_PUSH_CHANNEL_ID,
    OPT_PUSH_LEVELS,
    OPT_PUSH_LOCKSCREEN,
    OPT_PUSH_STICKY,
    OPT_SPEAK_LANGUAGE,
    POLICY_SUBENTRY,
    POPUP_STYLES,
    PROFILE_SUBENTRY,
    PUSH_LEVELS,
    PUSH_LOCKSCREEN,
    RULE_SUBENTRY,
    SEVERITIES,
)
from ..manager import BannerManager
from ..switch import policy_entity_id
from .audiences import BUILTINS
from .channels import mail
from .identity import GROUP_PREFIX
from .recipients import area_speakers, registrations, speaker_entities


def speaker_names(hass: HomeAssistant) -> dict[str, str]:
    """Entity id to friendly name of every speaker, so a list can show what a person recognises."""
    names = {}
    for entity_id in speaker_entities(hass):
        state = hass.states.get(entity_id)
        names[entity_id] = (state.attributes.get("friendly_name") if state else None) or entity_id
    return names


def area_choices(hass: HomeAssistant) -> list[dict[str, str]]:
    return [{"id": a.id, "name": a.name} for a in ar.async_get(hass).async_list_areas()]


CHANNEL_KEYS = (
    OPT_PUSH_LEVELS,
    OPT_POPUP_STYLES,
    OPT_PUSH_LOCKSCREEN,
    OPT_PUSH_STICKY,
    OPT_PUSH_CHANNEL_ID,
    OPT_SPEAK_LANGUAGE,
    OPT_MAIL_SERVICE,
    OPT_MAIL_ADDRESS,
    OPT_MAIL_SUBJECT,
    OPT_MAIL_BODY,
)


def notify_services(hass: HomeAssistant) -> list[str]:
    """Names of the notify services a mail channel can call."""
    return sorted(hass.services.async_services_for_domain("notify"))


def channel_settings(manager: BannerManager) -> dict[str, Any]:
    """The options of the Channels page, with their defaults filled in."""
    out: dict[str, Any] = {}
    for key in CHANNEL_KEYS:
        value = manager.options.get(key, DEFAULT_OPTIONS[key])
        out[key] = dict(value) if isinstance(value, dict) else value
    return out


def check_channels(changes: dict[str, Any], hass: HomeAssistant | None = None) -> dict[str, str]:
    """Problems of a channel settings change, as {field: code}."""
    errors: dict[str, str] = {}
    service = changes.get(OPT_MAIL_SERVICE)
    if service and hass is not None and service not in notify_services(hass):
        errors[OPT_MAIL_SERVICE] = "mail_service_unknown"
    address = changes.get(OPT_MAIL_ADDRESS)
    if address is not None and len(address.strip()) > MAX_MAIL_ADDRESS:
        errors[OPT_MAIL_ADDRESS] = "mail_address_too_long"
    for key, check in ((OPT_MAIL_SUBJECT, mail.check_subject), (OPT_MAIL_BODY, mail.check_body)):
        if key in changes and (code := check(changes[key])) is not None:
            errors[key] = code
    levels = changes.get(OPT_PUSH_LEVELS)
    if levels is not None and (
        set(levels) - set(SEVERITIES) or any(v not in PUSH_LEVELS for v in levels.values())
    ):
        errors[OPT_PUSH_LEVELS] = "level_unknown"
    styles = changes.get(OPT_POPUP_STYLES)
    if styles is not None and (
        set(styles) - set(SEVERITIES) or any(v not in POPUP_STYLES for v in styles.values())
    ):
        errors[OPT_POPUP_STYLES] = "style_unknown"
    if (lock := changes.get(OPT_PUSH_LOCKSCREEN)) is not None and lock not in PUSH_LOCKSCREEN:
        errors[OPT_PUSH_LOCKSCREEN] = "lockscreen_unknown"
    channel = changes.get(OPT_PUSH_CHANNEL_ID)
    if channel is not None and not (
        channel and len(channel) <= 40 and channel.replace("_", "").isalnum() and channel.islower()
    ):
        errors[OPT_PUSH_CHANNEL_ID] = "channel_id_invalid"
    return errors


async def editors(hass: HomeAssistant, manager: BannerManager, entry: Any) -> dict[str, Any]:
    hub = manager.hub
    subs = list(entry.subentries.values())

    def of(kind: str) -> list[Any]:
        return [s for s in subs if s.subentry_type == kind]

    usage: Callable[..., list[str]] = hub.policies.usage if hub is not None else (lambda *refs: [])
    audiences: list[dict[str, Any]] = []
    if hub is not None:
        for name, audience in BUILTINS.items():
            now = await hub.resolver.members(audience, "warning")
            audiences.append(
                {
                    "name": name,
                    "kind": audience.kind,
                    "builtin": True,
                    "enabled": audience.key not in hub.resolver.disabled_audiences(),
                    "subentry_id": None,
                    "data": {},
                    "members": [r.key for r in now.recipients],
                    "used_by": usage(audience.key, name),
                }
            )
        for sub in of(AUDIENCE_SUBENTRY):
            found = hub.resolver.audience(sub.subentry_id)
            members = await hub.resolver.members(found, "warning") if found else None
            audiences.append(
                {
                    "name": sub.title,
                    "kind": found.kind if found else "invalid",
                    "builtin": False,
                    "subentry_id": sub.subentry_id,
                    "data": dict(sub.data),
                    "members": [r.key for r in members.recipients] if members else [],
                    "used_by": usage(sub.subentry_id, sub.title),
                }
            )
    ids = audience_entity_ids(hass, entry)
    for listed in audiences:
        listed["entity_id"] = ids.get(listed["name"])
    groups = [
        {
            "name": sub.title,
            "subentry_id": sub.subentry_id,
            "data": dict(sub.data),
            "call_name": f"{sub.title}{GROUP_SUFFIX}",
            "speakers": sorted(
                {m for m in sub.data.get("members", []) if hass.states.get(m) is not None}
                | {s for a in sub.data.get("areas", []) for s in area_speakers(hass, a)}
            ),
            "used_by": usage(f"{GROUP_PREFIX}{sub.subentry_id}", f"{sub.title}{GROUP_SUFFIX}"),
        }
        for sub in of(GROUP_SUBENTRY)
    ]
    stored = {s.data.get("person"): s for s in of(PROFILE_SUBENTRY)}
    profiles = []
    persons = sorted(hass.states.async_all("person"), key=lambda s: s.entity_id)
    for state in persons:
        if hub is None:
            break
        profile = hub.resolver.profile(state.entity_id)
        sub = stored.get(state.entity_id)
        profiles.append(
            {
                "person": state.entity_id,
                "name": state.attributes.get("friendly_name") or state.entity_id,
                "user": bool(state.attributes.get("user_id")),
                "subentry_id": sub.subentry_id if sub else None,
                "customized": profile.customized,
                "primary": profile.primary,
                "enabled": profile.enabled,
                "channels": list(profile.channels),
                "mail_address": profile.mail_address,
                "devices": [
                    {
                        "device_id": d.device_id,
                        "name": d.name,
                        "service_found": d.service_found,
                        "source": d.source,
                    }
                    for d in profile.devices
                ],
                "removed": list(sub.data.get("removed_devices", [])) if sub else [],
            }
        )
    in_order = {p.subentry_id: n for n, p in enumerate(hub.policies.ordered())} if hub else {}
    policies = [
        {
            "name": s.title,
            "subentry_id": s.subentry_id,
            "data": dict(s.data),
            "entity_id": policy_entity_id(hass, entry, s.subentry_id, s.title),
        }
        for s in sorted(
            of(POLICY_SUBENTRY), key=lambda s: in_order.get(s.subentry_id, len(in_order))
        )
    ]
    rules = [
        {
            "name": s.title,
            "subentry_id": s.subentry_id,
            "data": dict(s.data),
            "showing": bool(
                (shown := manager.rules.get(f"rule_{s.subentry_id}")) is not None and shown.active
            ),
        }
        for s in of(RULE_SUBENTRY)
    ]
    known = (
        {c: hub.recipients.known(c) for c in ("banner", "push", "popup", "speak", "mail")}
        if hub
        else {}
    )
    if hub:
        # The persons of the "people" target of a policy whose channels come from the call (D-181).
        known["people"] = hub.recipients.known("popup")
        # Speech is offered by key: a group and an area are not undone by a rename (D-199).
        known["speak"] = [value for value, _label in hub.resolver.speak_choices()]
    return {
        "entry_id": entry.entry_id,
        "audiences": audiences,
        "groups": groups,
        "profiles": profiles,
        "policies": policies,
        "policy_mode": hub.policies.mode if hub else "first",
        "rules": rules,
        "channels": channel_settings(manager),
        "choices": {
            "persons": [
                {"id": s.entity_id, "name": s.attributes.get("friendly_name") or s.entity_id}
                for s in persons
            ],
            "zones": [
                {"id": s.entity_id, "name": s.attributes.get("friendly_name") or s.entity_id}
                for s in hass.states.async_all("zone")
            ],
            "speakers": speaker_entities(hass),
            "speaker_names": speaker_names(hass),
            "areas": area_choices(hass),
            "registrations": [{"id": k, "name": v or k} for k, v in registrations(hass).items()],
            "audience_names": hub.audiences.names() if hub else [],
            "audience_choices": (
                [{"id": k, "name": n} for k, n in hub.resolver.audience_choices()] if hub else []
            ),
            "group_labels": (
                {f"{GROUP_PREFIX}{g.key}": g.name for g in hub.resolver.groups()} if hub else {}
            ),
            "recipients": known,
            "notify_services": notify_services(hass),
        },
    }
