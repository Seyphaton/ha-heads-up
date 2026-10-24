"""In-memory banner state, persistence, timers, events and subscriber fan-out (DESIGN §5-§6).

All mutating methods are synchronous callbacks: no await between read and write, so
parallel action calls cannot interleave (DESIGN §3, Concurrency).
"""

from __future__ import annotations

import secrets
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_OPTIONS,
    DEFAULT_SEVERITY,
    DOMAIN,
    EVENT_CLEARED,
    EVENT_CREATED,
    EVENT_DISMISSED,
    EVENT_EXPIRED,
    EVENT_UPDATED,
    OPT_DEFAULT_DISMISS_SCOPE,
    OPT_DEFAULT_TIMEOUT,
    OPT_EVICT,
    OPT_MAX_BANNERS,
    SAVE_DELAY,
    SEVERITIES,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .models import Banner


class HeadsUpError(Exception):
    """Error with a WebSocket error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def banner_store(hass: HomeAssistant) -> Store[dict[str, Any]]:
    # Store API: HA_API_NOTES N-6
    return Store(hass, STORAGE_VERSION, STORAGE_KEY)


class BannerManager:
    def __init__(self, hass: HomeAssistant, options: Mapping[str, Any]) -> None:
        self.hass = hass
        self.options: dict[str, Any] = {**DEFAULT_OPTIONS, **options}
        self.banners: dict[str, Banner] = {}
        self._store = banner_store(hass)
        self._timers: dict[str, CALLBACK_TYPE] = {}
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        now = dt_util.utcnow()
        dropped = False
        for raw in data.get("banners", []):
            banner = Banner.from_dict(raw)
            if banner.expires_at is not None and banner.expires_at <= now:
                # Expired while HA was down (D-023).
                self._fire(EVENT_EXPIRED, banner)
                dropped = True
                continue
            self.banners[banner.id] = banner
            self._schedule(banner)
        if dropped:
            self._save()

    async def async_unload(self) -> None:
        for cancel in self._timers.values():
            cancel()
        self._timers.clear()
        self._listeners.clear()
        await self._store.async_save(self._data())

    # Mutations -------------------------------------------------------------------------

    @callback
    def create(self, data: Mapping[str, Any]) -> dict[str, Any]:
        now = dt_util.utcnow()
        banner_id = data.get("id") or self._new_id()
        existing = self.banners.get(banner_id)
        result: dict[str, Any] = {"id": banner_id, "status": "updated" if existing else "created"}
        if existing is None and len(self.banners) >= self.options[OPT_MAX_BANNERS]:
            result["evicted"] = self._evict_one()

        timeout: timedelta | None = data.get("timeout")
        if timeout is None:
            timeout = timedelta(seconds=self.options[OPT_DEFAULT_TIMEOUT])
        banner = Banner(
            id=banner_id,
            message=data["message"],
            title=data.get("title"),
            severity=data.get("severity", DEFAULT_SEVERITY),
            icon=data.get("icon"),
            dismissible=data.get("dismissible", True),
            dismiss_scope=data.get("dismiss_scope") or self.options[OPT_DEFAULT_DISMISS_SCOPE],
            tag=data.get("tag"),
            tap_action=data.get("tap_action"),
            created_at=existing.created_at if existing else now,
            updated_at=now,
            expires_at=now + timeout if timeout > timedelta(0) else None,
        )
        self.banners[banner_id] = banner
        self._schedule(banner)
        self._fire(EVENT_UPDATED if existing else EVENT_CREATED, banner, severity=banner.severity)
        self._changed()
        return result

    @callback
    def clear(self, banner_id: str | None = None, tag: str | None = None) -> int:
        matches = [
            b
            for b in self.banners.values()
            if (banner_id is None or b.id == banner_id) and (tag is None or b.tag == tag)
        ]
        for banner in matches:
            self._remove(banner.id, EVENT_CLEARED, reason="action")
        if matches:
            self._changed()
        return len(matches)

    @callback
    def clear_all(self) -> int:
        count = len(self.banners)
        for banner_id in list(self.banners):
            self._remove(banner_id, EVENT_CLEARED, reason="clear_all")
        if count:
            self._changed()
        return count

    @callback
    def dismiss(self, banner_id: str, user_id: str) -> None:
        banner = self._get(banner_id)
        if not banner.dismissible:
            raise HeadsUpError("not_dismissible", f"Banner {banner_id} is not dismissible")
        if banner.dismiss_scope == "global":
            self._remove(banner_id, EVENT_DISMISSED, scope="global", user_id=user_id)
        elif user_id not in banner.dismissed_by:
            banner.dismissed_by.append(user_id)
            self._fire(EVENT_DISMISSED, banner, scope="user", user_id=user_id)
        self._changed()

    @callback
    def admin_clear(self, banner_id: str) -> None:
        self._get(banner_id)
        self._remove(banner_id, EVENT_CLEARED, reason="admin")
        self._changed()

    # Reads and subscriptions -----------------------------------------------------------

    @callback
    def visible(self, user_id: str, show_all: bool = False) -> list[dict[str, Any]]:
        return [
            b.to_client(user_id)
            for b in self.banners.values()
            if show_all or user_id not in b.dismissed_by
        ]

    @callback
    def subscribe(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)

        @callback
        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    # Internals -------------------------------------------------------------------------

    def _new_id(self) -> str:
        while (banner_id := f"hu_{secrets.token_hex(5)}") in self.banners:
            pass
        return banner_id

    def _get(self, banner_id: str) -> Banner:
        if (banner := self.banners.get(banner_id)) is None:
            raise HeadsUpError("not_found", f"Banner {banner_id} not found")
        return banner

    def _evict_one(self) -> str:
        candidates = [b for b in self.banners.values() if b.severity != "critical"]
        if not self.options[OPT_EVICT] or not candidates:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="too_many_banners",
                translation_placeholders={"max": str(self.options[OPT_MAX_BANNERS])},
            )
        victim = min(candidates, key=lambda b: (SEVERITIES.index(b.severity), b.updated_at))
        self._remove(victim.id, EVENT_CLEARED, reason="evicted")
        return victim.id

    def _remove(self, banner_id: str, event: str, **extra: Any) -> None:
        banner = self.banners.pop(banner_id)
        if cancel := self._timers.pop(banner_id, None):
            cancel()
        self._fire(event, banner, **extra)

    def _schedule(self, banner: Banner) -> None:
        if cancel := self._timers.pop(banner.id, None):
            cancel()
        if banner.expires_at is not None:
            # HA_API_NOTES N-7
            self._timers[banner.id] = async_track_point_in_utc_time(
                self.hass, partial(self._expire, banner.id), banner.expires_at
            )

    @callback
    def _expire(self, banner_id: str, _now: datetime) -> None:
        self._timers.pop(banner_id, None)
        if banner_id in self.banners:
            self._remove(banner_id, EVENT_EXPIRED)
            self._changed()

    def _fire(self, event: str, banner: Banner, **extra: Any) -> None:
        self.hass.bus.async_fire(event, {"id": banner.id, "tag": banner.tag, **extra})

    def _data(self) -> dict[str, Any]:
        return {"banners": [b.to_dict() for b in self.banners.values()]}

    def _save(self) -> None:
        self._store.async_delay_save(self._data, SAVE_DELAY)

    def _changed(self) -> None:
        self._save()
        for listener in list(self._listeners):
            listener()
