"""How often each audience was used and when last: one count per message (D-227).

Stored, unlike the Message Log (D-118), so the count means something after a restart. A message
counts once per audience, however often it is escalated, reminded or replaced: the newest
message ids are kept per audience to tell a repeat from a new message. When the Message Log
itself is stored, this record may be derived from it instead.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from ..const import AUDIENCE_USAGE_KEY, SAVE_DELAY

# Message ids kept per audience to recognise a repeat; older ones count again if they return.
RECENT_IDS = 50


class AudienceUsage:
    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, 1, AUDIENCE_USAGE_KEY)
        self._data: dict[str, dict[str, Any]] = {}

    async def async_load(self) -> None:
        raw = await self._store.async_load() or {}
        audiences = raw.get("audiences") if isinstance(raw, dict) else None
        self._data = {}
        for key, item in (audiences or {}).items():
            if not isinstance(item, dict):
                continue
            try:
                count = max(0, int(item.get("count", 0)))
            except TypeError, ValueError:
                continue
            ids = [str(i) for i in item.get("recent", []) if isinstance(i, str)][-RECENT_IDS:]
            self._data[str(key)] = {"count": count, "last": item.get("last"), "recent": ids}

    async def async_save(self) -> None:
        await self._store.async_save(self._dump())

    def record(self, message_id: str, keys: Iterable[str], now: datetime) -> list[str]:
        """Count a message for each audience it has not been counted for; returns those keys."""
        counted: list[str] = []
        for key in dict.fromkeys(keys):
            item = self._data.setdefault(key, {"count": 0, "last": None, "recent": []})
            item["last"] = now.isoformat()
            if message_id in item["recent"]:
                continue
            item["count"] += 1
            item["recent"] = [*item["recent"], message_id][-RECENT_IDS:]
            counted.append(key)
        if keys:
            self._store.async_delay_save(self._dump, SAVE_DELAY)
        return counted

    def of(self, key: str) -> dict[str, Any]:
        item = self._data.get(key) or {}
        return {"count": item.get("count", 0), "last": item.get("last")}

    def _dump(self) -> dict[str, Any]:
        return {"audiences": self._data}
