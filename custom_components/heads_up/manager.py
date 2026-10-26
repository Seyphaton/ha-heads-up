"""In-memory banner state, persistence, timers, events and subscriber fan-out (DESIGN §5-§6).

All mutating methods are synchronous callbacks: no await between read and write, so
parallel action calls cannot interleave (DESIGN §3, Concurrency).
"""

from __future__ import annotations

import logging
import secrets
from collections.abc import Callable, Iterator, Mapping
from datetime import datetime, timedelta
from functools import partial
from itertools import chain
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import (
    async_track_point_in_utc_time,
    async_track_state_change_event,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util

from .conditions import DEFAULT_OPERATOR, matches
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
    RULE_ID_PREFIX,
    RULE_SUBENTRY,
    RULE_TAG,
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
        # Watch rules as virtual banners; never stored (DESIGN §17).
        self.rules: dict[str, Banner] = {}
        self._rule_sources: dict[str, dict[str, Any]] = {}
        # Entities a rule's message template reads, so state changes re-render it (D-063).
        self._rule_template_entities: dict[str, set[str]] = {}
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
        self.rules.clear()
        self._rule_sources.clear()
        self._rule_template_entities.clear()
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
        banner = self.rules.get(banner_id) or self._get(banner_id)
        if not banner.dismissible:
            raise HeadsUpError("not_dismissible", f"Banner {banner_id} is not dismissible")
        if banner.dismiss_scope == "global":
            self._remove(banner_id, EVENT_DISMISSED, scope="global", user_id=user_id)
        elif user_id not in banner.dismissed_by:
            banner.dismissed_by.append(user_id)
            self._fire(EVENT_DISMISSED, banner, scope="user", user_id=user_id)

    @callback
    def admin_clear(self, banner_id: str) -> None:
        if banner_id in self.rules:
            raise HeadsUpError(
                "rule_banner", f"Banner {banner_id} comes from a rule; disable or delete the rule"
            )
        self._get(banner_id)
        self._remove(banner_id, EVENT_CLEARED, reason="admin")
        self._changed()

    # Reads and subscriptions -----------------------------------------------------------

    @callback
    def is_active(self, banner: Banner) -> bool:
        return banner.active

    @callback
    def active_count(self) -> int:
        return sum(1 for b in self._all() if b.active)

    @callback
    def visible(self, user_id: str, show_all: bool = False) -> list[dict[str, Any]]:
        # show_all (admin) also returns waiting, dismissed and untargeted banners (D-008).
        return [
            self._client(b, user_id)
            for b in self._all()
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

    # Watch rules -----------------------------------------------------------------------

    @callback
    def sync_rules(self, subentries: Mapping[str, ConfigSubentry], silent: bool = False) -> None:
        """Make the virtual banners match the enabled rule subentries (DESIGN §17).

        `silent` is used at setup: the state found then fires no events (D-058).
        """
        wanted = {
            f"{RULE_ID_PREFIX}{sub.subentry_id}": sub
            for sub in subentries.values()
            if sub.subentry_type == RULE_SUBENTRY and sub.data.get("enabled", True)
        }
        changed = False
        for banner_id in list(self.rules):
            if banner_id not in wanted:
                gone = self.rules.pop(banner_id)
                self._rule_sources.pop(banner_id, None)
                self._rule_template_entities.pop(banner_id, None)
                if gone.condition_met and not silent:
                    self._fire(EVENT_CLEARED, gone, reason="rule")
                changed = True
        for banner_id, sub in wanted.items():
            source = dict(sub.data)
            if self._rule_sources.get(banner_id) == source:
                continue
            old = self.rules.get(banner_id)
            self._rule_sources[banner_id] = source
            banner = self._build_rule(banner_id, source, old)
            self.rules[banner_id] = banner
            if not silent and banner.condition_met != bool(old and old.condition_met):
                if banner.condition_met:
                    self._fire(EVENT_CREATED, banner, severity=banner.severity)
                else:
                    self._fire(EVENT_CLEARED, banner, reason="rule")
            changed = True
        self._refresh_tracking()
        if changed and not silent:
            self._notify()

    def _build_rule(self, banner_id: str, source: Mapping[str, Any], old: Banner | None) -> Banner:
        now = dt_util.utcnow()
        condition: dict[str, Any] = {
            "entity_id": source["entity_id"],
            "state": list(source.get("state") or ["on"]),
        }
        if source.get("operator", DEFAULT_OPERATOR) != DEFAULT_OPERATOR:
            condition["operator"] = source["operator"]
        if source.get("attribute"):
            condition["attribute"] = source["attribute"]
        met = self._evaluate(condition) is True
        return Banner(
            id=banner_id,
            message=self._rule_message(banner_id, source),
            title=source.get("title") or None,
            severity=source.get("severity", DEFAULT_SEVERITY),
            icon=source.get("icon") or None,
            dismissible=source.get("dismissible", False),
            dismiss_scope="user",
            tag=RULE_TAG,
            condition=condition,
            mode="recurring",
            people=list(source.get("people", [])),
            condition_met=met,
            ever_met=met,
            created_at=old.created_at if old else now,
            updated_at=now,
        )

    def _rule_message(self, banner_id: str, source: Mapping[str, Any]) -> str:
        # `{name}` first, then the template (D-055, D-063).
        state = self.hass.states.get(source["entity_id"])
        name = (state.attributes.get("friendly_name") if state else None) or source["entity_id"]
        message = str(source["message"]).replace("{name}", str(name))
        self._rule_template_entities.pop(banner_id, None)
        if not any(token in message for token in ("{{", "{%", "{#")):
            return message
        info = Template(message, self.hass).async_render_to_info(parse_result=False)
        if info.exception:
            _LOGGER.warning("Rule message of %s failed to render: %s", banner_id, info.exception)
            return message
        self._rule_template_entities[banner_id] = set(info.entities)
        return str(info.result())

    def _apply_rule(self, banner: Banner) -> bool:
        # Unavailable, unknown and removed entities hide the banner (D-053).
        assert banner.condition is not None
        met = self._evaluate(banner.condition) is True
        message = self._rule_message(banner.id, self._rule_sources[banner.id])
        changed = message != banner.message
        banner.message = message
        if met != banner.condition_met:
            banner.condition_met = met
            changed = True
            if met:
                banner.updated_at = dt_util.utcnow()  # the card's "time ago" counts from the flip
                self._fire(EVENT_CREATED, banner, severity=banner.severity)
            else:
                banner.dismissed_by.clear()  # a dismissal lasts until the condition flips (D-056)
                self._fire(EVENT_CLEARED, banner, reason="rule")
        return changed

    # Internals -------------------------------------------------------------------------

    def _client(self, banner: Banner, user_id: str) -> dict[str, Any]:
        data = banner.to_client(user_id)
        if banner.id in self.rules:
            # The card hides "Clear for everyone": a rule banner is disabled or deleted instead.
            data["rule"] = True
        return data

    def _all(self) -> Iterator[Banner]:
        return chain(self.banners.values(), self.rules.values())

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
        return matches(condition, value)

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
        for banner in list(self.rules.values()):
            if (
                banner.condition is not None and banner.condition["entity_id"] == entity_id
            ) or entity_id in self._rule_template_entities.get(banner.id, ()):
                changed |= self._apply_rule(banner)
        if changed:
            self._changed()

    def _refresh_tracking(self) -> None:
        wanted = {b.condition["entity_id"] for b in self.banners.values() if b.condition}
        wanted |= {b.condition["entity_id"] for b in self.rules.values() if b.condition}
        wanted |= {e for entities in self._rule_template_entities.values() for e in entities}
        wanted |= {p for b in self._all() for p in b.people}
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
        self._save()
        self._notify()

    def _notify(self) -> None:
        self._refresh_tracking()
        for listener in list(self._listeners):
            listener()
