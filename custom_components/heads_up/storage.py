"""Stores of version 2 (D-200): references are keys, not names.

The data of version 1 is the same shape; its names are turned into keys when the data is loaded
(`hub/identity.py`), so the migration of a store only raises the version. That makes older code,
which reads names, refuse the file instead of reading keys as names.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    DELIVERIES_KEY,
    DELIVERIES_MINOR_VERSION,
    DELIVERIES_VERSION,
    STORAGE_KEY,
    STORAGE_VERSION,
    TRACE_KEY,
    TRACE_VERSION,
)


class KeyedStore(Store[dict[str, Any]]):
    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        # Store API: HA_API_NOTES N-81, N-99.
        if old_major_version > self.version:
            raise NotImplementedError
        return old_data


def banner_store(hass: HomeAssistant) -> KeyedStore:
    return KeyedStore(hass, STORAGE_VERSION, STORAGE_KEY)


def trace_store(hass: HomeAssistant) -> KeyedStore:
    return KeyedStore(hass, TRACE_VERSION, TRACE_KEY)


def ledger_store(hass: HomeAssistant) -> KeyedStore:
    return KeyedStore(
        hass, DELIVERIES_VERSION, DELIVERIES_KEY, minor_version=DELIVERIES_MINOR_VERSION
    )
