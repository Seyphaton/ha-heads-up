"""Data for the panel's editors (D-119): what exists, who uses it, what can be chosen.

Saving goes through the integration's own subentry flows (the panel drives them over the REST
API of Home Assistant) and, for the channel settings, through `channels_set`. So the panel adds
no second copy of the validation.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar

from ..const import (
    AUDIENCE_SUBENTRY,
    DEFAULT_OPTIONS,
    GROUP_SUBENTRY,
    GROUP_SUFFIX,
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
    SEVERITIES,
)
from ..manager import BannerManager
from .audiences import BUILTINS
from .recipients import area_speakers, registrations, speaker_entities

CHANNEL_KEYS = (
    OPT_PUSH_LEVELS,
    OPT_POPUP_STYLES,
    OPT_PUSH_LOCKSCREEN,
    OPT_PUSH_STICKY,
    OPT_PUSH_CHANNEL_ID,
    OPT_SPEAK_LANGUAGE,
)


def channel_settings(manager: BannerManager) -> dict[str, Any]:
    """The options of the Channels page, with their defaults filled in."""
    out: dict[str, Any] = {}
    for key in CHANNEL_KEYS:
        value = manager.options.get(key, DEFAULT_OPTIONS[key])
        out[key] = dict(value) if isinstance(value, dict) else value
    return out


def check_channels(changes: dict[str, Any]) -> dict[str, str]:
    """Problems of a channel settings change, as {field: code}."""
    errors: dict[str, str] = {}
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

    usage = hub.policies.usage if hub is not None else (lambda name: [])
    audiences: list[dict[str, Any]] = []
    if hub is not None:
        for name, audience in BUILTINS.items():
            now = await hub.resolver.members(audience, "warning")
            audiences.append(
                {
                    "name": name,
                    "kind": audience.kind,
                    "builtin": True,
                    "subentry_id": None,
                    "data": {},
                    "members": [r.key for r in now.recipients],
                    "used_by": usage(name),
                }
            )
        for sub in of(AUDIENCE_SUBENTRY):
            found = hub.resolver.audience(sub.title)
            members = await hub.resolver.members(found, "warning") if found else None
            audiences.append(
                {
                    "name": sub.title,
                    "kind": found.kind if found else "invalid",
                    "builtin": False,
                    "subentry_id": sub.subentry_id,
                    "data": dict(sub.data),
                    "members": [r.key for r in members.recipients] if members else [],
                    "used_by": usage(sub.title),
                }
            )
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
            "used_by": usage(sub.title),
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
                "channels": list(profile.channels),
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
    policies = [
        {"name": s.title, "subentry_id": s.subentry_id, "data": dict(s.data)}
        for s in of(POLICY_SUBENTRY)
    ]
    areas = ar.async_get(hass).async_list_areas()
    known = (
        {c: hub.recipients.known(c) for c in ("banner", "push", "popup", "speak")} if hub else {}
    )
    return {
        "entry_id": entry.entry_id,
        "hub": hub is not None,
        "audiences": audiences,
        "groups": groups,
        "profiles": profiles,
        "policies": policies,
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
            "areas": [{"id": a.id, "name": a.name} for a in areas],
            "registrations": [{"id": k, "name": v or k} for k, v in registrations(hass).items()],
            "audience_names": hub.audiences.names() if hub else [],
            "recipients": known,
        },
    }
