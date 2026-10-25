"""In-memory banner state, persistence, timers, events and subscriber fan-out (DESIGN §5-§6).

All mutating methods are synchronous callbacks: no await between read and write, so
parallel action calls cannot interleave (DESIGN §3, Concurrency).
"""

from __future__ import annotations

import logging
import secrets
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_state_change_event,
)
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

_LOGGER = logging.getLogger(__name__)
_NO_STATE = {STATE_UNAVAILABLE, STATE_UNKNOWN}


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
        self.tracked_entities: set[str] = set()
        self._untrack: CALLBACK_TYPE | None = None

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        now = dt_util.utcnow()
        dropped = False
        for raw in data.get("banners", []):
            try:
                banner = Banner.from_dict(raw)
            except (TypeError, KeyError, ValueError, AttributeError) as err:
                # One damaged entry must not take the other banners or the integration down.
                banner_id = raw.get("id") if isinstance(raw, dict) else None
                _LOGGER.error("Skipping unreadable banner %r in storage: %s", banner_id, err)
                dropped = True
                continue
            if banner.expires_at is not None and banner.expires_at <= now:
                # Expired while HA was down (D-023).
                self._fire(EVENT_EXPIRED, banner)
                dropped = True
                continue
            self.banners[banner.id] = banner
            self._schedule(banner)
        # Conditions may have changed while not loaded. Entities that are not loaded yet
        # evaluate to None and keep their stored result (D-006).
        for banner in list(self.banners.values()):
            if banner.condition is not None:
                dropped |= self._apply_condition(banner)
        self._refresh_tracking()
        if dropped:
            self._save()

    async def async_unload(self) -> None:
        for cancel in self._timers.values():
            cancel()
        self._timers.clear()
        self._listeners.clear()
        if self._untrack:
            self._untrack()
            self._untrack = None
        self.tracked_entities = set()
        await self._store.async_save(self._data())

    # Mutations -------------------------------------------------------------------------

    @callback
    def create(self, data: Mapping[str, Any]) -> dict[str, Any]:
        now = dt_util.utcnow()
        banner_id = data.get("id") or self._new_id()
        existing = self.banners.get(banner_id)
        condition: dict[str, Any] | None = data.get("condition")
        met: bool | None = None
        if condition is not None:
            if self.hass.states.get(condition["entity_id"]) is None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="entity_not_found",
                    translation_placeholders={"entity_id": condition["entity_id"]},
                )
            met = self._evaluate(condition)
            if met is not True and not data.get("wait_for_condition", True):
                if existing:
                    # The caller replaced this ID with a banner that must not show (D-038).
                    self._remove(banner_id, EVENT_CLEARED, reason="condition")
                    self._changed()
                return {"id": banner_id, "status": "condition_false"}

        result: dict[str, Any] = {"id": banner_id, "status": "updated" if existing else "created"}
        if condition is not None and met is not True:
            result["status"] = "waiting"
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
            condition=condition,
            mode=data.get("mode", "once"),
            people=list(data.get("people", [])),
            condition_met=met,
            ever_met=met is True,
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
        self._dismiss_one(banner_id, user_id)
        self._changed()

    @callback
    def dismiss_many(self, banner_ids: list[str], user_id: str) -> tuple[int, int]:
        """Dismiss for one user; unknown and non-dismissible banners are skipped (D-048).

        Subscribers get one update for the whole batch.
        """
        dismissed = 0
        for banner_id in dict.fromkeys(banner_ids):
            try:
                self._dismiss_one(banner_id, user_id)
            except HeadsUpError:
                continue
            dismissed += 1
        if dismissed:
            self._changed()
        return dismissed, len(dict.fromkeys(banner_ids)) - dismissed

    def _dismiss_one(self, banner_id: str, user_id: str) -> None:
        banner = self._get(banner_id)
        if not banner.dismissible:
            raise HeadsUpError("not_dismissible", f"Banner {banner_id} is not dismissible")
        if banner.dismiss_scope == "global":
            self._remove(banner_id, EVENT_DISMISSED, scope="global", user_id=user_id)
        elif user_id not in banner.dismissed_by:
            banner.dismissed_by.append(user_id)
            self._fire(EVENT_DISMISSED, banner, scope="user", user_id=user_id)

    @callback
    def admin_clear(self, banner_id: str) -> None:
        self._get(banner_id)
        self._remove(banner_id, EVENT_CLEARED, reason="admin")
        self._changed()

    # Reads and subscriptions -----------------------------------------------------------

    @callback
    def is_active(self, banner: Banner) -> bool:
        return banner.active

    @callback
    def active_count(self) -> int:
        return sum(1 for b in self.banners.values() if b.active)

    @callback
    def visible(self, user_id: str, show_all: bool = False) -> list[dict[str, Any]]:
        # show_all (admin) also returns waiting, dismissed and untargeted banners (D-008).
        return [
            b.to_client(user_id)
            for b in self.banners.values()
            if show_all
            or (b.active and user_id not in b.dismissed_by and self._targets(b, user_id))
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

    def _targets(self, banner: Banner, user_id: str) -> bool:
        if not banner.people:
            return True
        # Person entities carry the linked user in their user_id attribute (HA_API_NOTES N-10).
        for person in banner.people:
            if (state := self.hass.states.get(person)) and state.attributes.get(
                "user_id"
            ) == user_id:
                return True
        return False

    def _evaluate(self, condition: Mapping[str, Any]) -> bool | None:
        state = self.hass.states.get(condition["entity_id"])
        if state is None or state.state in _NO_STATE:
            return None
        if (attribute := condition.get("attribute")) is not None:
            raw = state.attributes.get(attribute)
            value = None if raw is None else str(raw)
        else:
            value = state.state
        wanted = condition["state"]
        return value in ([wanted] if isinstance(wanted, str) else wanted)

    def _apply_condition(self, banner: Banner) -> bool:
        """Re-evaluate one banner's condition. Returns True if anything changed."""
        assert banner.condition is not None
        met = self._evaluate(banner.condition)
        if met is None or met == banner.condition_met:
            return False
        previous, banner.condition_met = banner.condition_met, met
        if met:
            if banner.mode == "recurring" and previous is False:
                banner.dismissed_by.clear()
            banner.ever_met = True
        elif banner.mode == "once" and banner.ever_met:
            self._remove(banner.id, EVENT_CLEARED, reason="condition")
        return True

    @callback
    def _on_state_change(self, event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        old, new = event.data["old_state"], event.data["new_state"]
        changed = False
        if entity_id.startswith("person."):
            old_user = old.attributes.get("user_id") if old else None
            new_user = new.attributes.get("user_id") if new else None
            changed = old_user != new_user
        for banner in list(self.banners.values()):
            if banner.condition is None or banner.condition["entity_id"] != entity_id:
                continue
            if new is None:
                _LOGGER.warning(
                    "Condition entity %s was removed; banner %s keeps its visibility",
                    entity_id,
                    banner.id,
                )
                continue
            changed |= self._apply_condition(banner)
        if changed:
            self._changed()

    def _refresh_tracking(self) -> None:
        wanted = {b.condition["entity_id"] for b in self.banners.values() if b.condition}
        wanted |= {p for b in self.banners.values() for p in b.people}
        if wanted == self.tracked_entities:
            return
        if self._untrack:
            self._untrack()
            self._untrack = None
        self.tracked_entities = wanted
        if wanted:
            # One listener for all condition and person entities (HA_API_NOTES N-7).
            self._untrack = async_track_state_change_event(
                self.hass, list(wanted), self._on_state_change
            )

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
        self._refresh_tracking()
        self._save()
        for listener in list(self._listeners):
            listener()
