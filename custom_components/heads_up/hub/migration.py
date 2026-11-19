"""One-time move of stored names to keys (D-200, docs/dev/hub/IDENTITY.md section 3.3).

The config entry goes from version 1 to 2 in `async_migrate_entry`: rules, policy targets and two
options get keys instead of names. Home Assistant saves the entry once afterwards, so the move is
all or nothing. The stores of banners and deliveries are rewritten when they load (the same pure
functions, `IdentityMaps`), and their version is raised so older code refuses them. A backup of
everything before the first change is written once.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from ..const import (
    DELIVERIES_KEY,
    DOMAIN,
    OPT_ATTENTION_DISMISSED,
    OPT_AUDIENCES_DISABLED,
    OPT_POPUP_STYLES,
    OPT_PUSH_LEVELS,
    OPT_SEVERITY_DISPLAY,
    OPT_SPEAK_SEVERITY_VOLUME,
    POLICY_SUBENTRY,
    PUSH_LEVELS_1_0,
    RULE_SUBENTRY,
    STORAGE_KEY,
    TRACE_KEY,
    TYPE_AWAY_OLD,
    canonical_severity,
)
from .identity import IdentityMaps, count_changes, maps_for

_LOGGER = logging.getLogger(__name__)

ENTRY_VERSION = 2
# 2.2: Away became Presence (D-214); 2.3: push levels kept (D-230); 2.4: success is passive (D-231)
ENTRY_MINOR_VERSION = 4
PUSH_LEVELS_MINOR_VERSION = 3
PRESENCE_MINOR_VERSION = 2
BACKUP_KEY = "heads_up.migration_v2"
PRESENCE_BACKUP_KEY = "heads_up.migration_v2_2"
OLD_STORE_VERSIONS = {STORAGE_KEY: 1, DELIVERIES_KEY: 1, TRACE_KEY: 1}


async def _read_old(hass: HomeAssistant, key: str) -> Any:
    """The stored file as it is on disk, through a store of its old version (so nothing is
    migrated or saved by reading it)."""
    return await Store(hass, OLD_STORE_VERSIONS[key], key).async_load()


async def write_backup(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Everything the migration may change, saved once before the first change. An existing
    backup is never overwritten. Returns whether one was written."""
    store: Store[dict[str, Any]] = Store(hass, 1, BACKUP_KEY)
    if await store.async_load() is not None:
        return False
    await store.async_save(
        {
            "entry": {
                "version": entry.version,
                "options": dict(entry.options),
                "subentries": [
                    {
                        "subentry_id": s.subentry_id,
                        "subentry_type": s.subentry_type,
                        "title": s.title,
                        "unique_id": s.unique_id,
                        "data": dict(s.data),
                    }
                    for s in entry.subentries.values()
                ],
            },
            "stores": {key: await _read_old(hass, key) for key in OLD_STORE_VERSIONS},
        }
    )
    return True


def migrate_options(
    options: dict[str, Any], maps: IdentityMaps, person_names: dict[str, str]
) -> dict[str, Any]:
    """`audiences_disabled` holds kinds; a hidden warning of a person remembers the entity ID."""
    out = dict(options)
    if OPT_AUDIENCES_DISABLED in out:
        out[OPT_AUDIENCES_DISABLED] = maps.disabled_audiences(out[OPT_AUDIENCES_DISABLED])
    if isinstance(out.get(OPT_ATTENTION_DISMISSED), list):
        out[OPT_ATTENTION_DISMISSED] = list(
            dict.fromkeys(
                _dismissed_key(str(k), person_names) for k in out[OPT_ATTENTION_DISMISSED]
            )
        )
    return out


def _dismissed_key(key: str, person_names: dict[str, str]) -> str:
    kind, _, rest = key.partition("|")
    subject, _, detail = rest.partition("|")
    if kind == "person_no_device" and subject in person_names:
        return f"{kind}|{person_names[subject]}|{detail}"
    return key


def presence_from_away(data: dict[str, Any]) -> dict[str, Any]:
    """A 1.0 Away policy as Presence with its 1.0 behaviour: push, popup and mail, the
    recipient not in Home, hold, and the delivery dropped when the wait ends (D-213, D-214)."""
    if data.get("type") != TYPE_AWAY_OLD:
        return data
    return {**data, "type": "presence", "after_wait": data.get("after_wait") or "drop"}


async def _write_presence_backup(hass: HomeAssistant, entry: ConfigEntry) -> None:
    store: Store[dict[str, Any]] = Store(hass, 1, PRESENCE_BACKUP_KEY)
    if await store.async_load() is not None:
        return
    await store.async_save(
        {
            "entry": {
                "version": entry.version,
                "minor_version": entry.minor_version,
                "subentries": [
                    {
                        "subentry_id": s.subentry_id,
                        "subentry_type": s.subentry_type,
                        "title": s.title,
                        "unique_id": s.unique_id,
                        "data": dict(s.data),
                    }
                    for s in entry.subentries.values()
                    if s.subentry_type == POLICY_SUBENTRY
                ],
            }
        }
    )


async def migrate_presence(hass: HomeAssistant, entry: ConfigEntry) -> int:
    """2.1 to 2.2: every Away policy becomes Presence; the policy subentries are backed up
    first. Returns how many policies changed."""
    await _write_presence_backup(hass, entry)
    changed = 0
    for sub in list(entry.subentries.values()):
        if sub.subentry_type != POLICY_SUBENTRY:
            continue
        new = presence_from_away(dict(sub.data))
        if new != dict(sub.data):
            hass.config_entries.async_update_subentry(entry, sub, data=new)
            changed += 1
    hass.config_entries.async_update_entry(entry, minor_version=PRESENCE_MINOR_VERSION)
    _LOGGER.info("%s: %d Away policies became Presence", DOMAIN, changed)
    return changed


def migrate_push_levels(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """2.2 to 2.3: new setups get other default push levels (D-230). An existing setup keeps the
    levels it had: the old defaults, with what it saved on top, are written into its options."""
    stored = entry.options.get(OPT_PUSH_LEVELS) or {}
    options = {**entry.options, OPT_PUSH_LEVELS: {**PUSH_LEVELS_1_0, **stored}}
    hass.config_entries.async_update_entry(
        entry, options=options, minor_version=PUSH_LEVELS_MINOR_VERSION
    )


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version > ENTRY_VERSION:
        return False  # Home Assistant refuses this before it gets here; kept for clarity
    if entry.version == ENTRY_VERSION:
        await _migrate_minor(hass, entry)
        return True
    await write_backup(hass, entry)
    maps = maps_for(hass, entry.subentries.values())
    changed = 0
    for sub in list(entry.subentries.values()):
        if sub.subentry_type == POLICY_SUBENTRY:
            new = maps.policy_data(sub.data)
        elif sub.subentry_type == RULE_SUBENTRY:
            new = maps.rule_data(sub.data)
        else:
            continue
        changed += count_changes(dict(sub.data), new)
        if new != dict(sub.data):
            hass.config_entries.async_update_subentry(entry, sub, data=new)
    person_names = {
        str(s.attributes.get("friendly_name") or s.entity_id): s.entity_id
        for s in hass.states.async_all("person")
    }
    options = migrate_options(dict(entry.options), maps, person_names)
    changed += count_changes(dict(entry.options), options)
    hass.config_entries.async_update_entry(entry, options=options, version=ENTRY_VERSION)
    _LOGGER.info("%s: stored names became keys (%d values in the entry)", DOMAIN, changed)
    await _migrate_minor(hass, entry)
    return True


async def _migrate_minor(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if entry.minor_version < PRESENCE_MINOR_VERSION:
        await migrate_presence(hass, entry)
    if entry.minor_version < PUSH_LEVELS_MINOR_VERSION:
        migrate_push_levels(hass, entry)
    if entry.minor_version < ENTRY_MINOR_VERSION:
        migrate_severity_names(hass, entry)


# Options that hold one value per severity.
SEVERITY_KEYED_OPTIONS = (
    OPT_PUSH_LEVELS,
    OPT_POPUP_STYLES,
    OPT_SEVERITY_DISPLAY,
    OPT_SPEAK_SEVERITY_VOLUME,
)


def severity_names(data: Any) -> Any:
    """`data` with every stored severity by its current name: a `severity` value and the
    entries of a `severities` list (policies, watch rules)."""
    if isinstance(data, dict):
        out = {}
        for key, value in data.items():
            if key == "severity":
                out[key] = canonical_severity(value)
            elif key == "severities" and isinstance(value, list):
                out[key] = list(dict.fromkeys(canonical_severity(v) for v in value))
            else:
                out[key] = severity_names(value)
        return out
    if isinstance(data, list):
        return [severity_names(v) for v in data]
    return data


def migrate_severity_names(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """2.3 to 2.4: the severity `success` is called `passive` (D-231), in the options keyed by
    severity and in policy and watch rule subentries. Stored messages are read with the new
    name when they load (`Banner.from_dict`)."""
    for sub in list(entry.subentries.values()):
        if sub.subentry_type not in (POLICY_SUBENTRY, RULE_SUBENTRY):
            continue
        new = severity_names(dict(sub.data))
        if new != dict(sub.data):
            hass.config_entries.async_update_subentry(entry, sub, data=new)
    options = dict(entry.options)
    for key in SEVERITY_KEYED_OPTIONS:
        values = options.get(key)
        if isinstance(values, dict) and "success" in values:
            values = dict(values)
            values["passive"] = values.pop("success")
            options[key] = values
    hass.config_entries.async_update_entry(
        entry, options=options, minor_version=ENTRY_MINOR_VERSION
    )
