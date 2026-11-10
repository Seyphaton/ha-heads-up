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
    POLICY_SUBENTRY,
    RULE_SUBENTRY,
    STORAGE_KEY,
    TRACE_KEY,
)
from .identity import IdentityMaps, count_changes, maps_for

_LOGGER = logging.getLogger(__name__)

ENTRY_VERSION = 2
BACKUP_KEY = "heads_up.migration_v2"
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


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version > ENTRY_VERSION:
        return False  # Home Assistant refuses this before it gets here; kept for clarity
    if entry.version == ENTRY_VERSION:
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
    return True
