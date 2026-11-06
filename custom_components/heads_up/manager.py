"""In-memory banner state, persistence, timers, events and subscriber fan-out (DESIGN §5-§6).

All mutating methods are synchronous callbacks: no await between read and write, so
parallel action calls cannot interleave (DESIGN §3, Concurrency).
"""

from __future__ import annotations

import logging
import secrets
from collections.abc import Callable, Iterator, Mapping
from copy import deepcopy
from datetime import datetime, timedelta
from functools import partial
from itertools import chain
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError, TemplateError
from homeassistant.helpers.event import (
    TrackTemplate,
    TrackTemplateResult,
    TrackTemplateResultInfo,
    async_call_later,
    async_track_point_in_utc_time,
    async_track_state_change_event,
    async_track_template_result,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.template import Template, result_as_boolean
from homeassistant.util import dt as dt_util

from .conditions import DEFAULT_OPERATOR, NO_STATE_OPERATORS, matches
from .const import (
    CHANNEL_BANNER,
    DEFAULT_OPTIONS,
    DEFAULT_SEVERITY,
    DOMAIN,
    EVENT_ACTION,
    EVENT_CLEARED,
    EVENT_CREATED,
    EVENT_DISMISSED,
    EVENT_EXPIRED,
    EVENT_SNOOZED,
    EVENT_UNSNOOZED,
    EVENT_UPDATED,
    GLOBAL_SNOOZE_KEY,
    OPT_DEFAULT_DISMISS_SCOPE,
    OPT_DEFAULT_SNOOZABLE,
    OPT_DEFAULT_SNOOZE_OPTIONS,
    OPT_DEFAULT_SNOOZE_SCOPE,
    OPT_DEFAULT_TIMEOUT,
    OPT_DISABLE_ENDED_BUTTONS,
    OPT_EVICT,
    OPT_MAX_BANNERS,
    OPT_QUICK_SNOOZE,
    RULE_ID_PREFIX,
    RULE_SUBENTRY,
    RULE_TAG,
    SAVE_DELAY,
    SEVERITIES,
    SOURCE_ACTION,
    SOURCE_RULE,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .hub.engine import HubEngine
from .hub.transitions import BannerTransition, Kind, Reason, TransitionListener
from .models import Banner

_LOGGER = logging.getLogger(__name__)
_NO_STATE = {STATE_UNAVAILABLE, STATE_UNKNOWN}
# `reason` values of the bus events mapped to transition reasons.
_REASONS = {
    "action": Reason.CLEARED,
    "condition": Reason.CONDITION,
    "admin": Reason.ADMIN,
    "clear_all": Reason.CLEAR_ALL,
    "evicted": Reason.EVICTED,
    "rule": Reason.RULE,
    Reason.EXPIRED: Reason.EXPIRED,
    Reason.DISMISSED_GLOBAL: Reason.DISMISSED_GLOBAL,
}


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
        # The hub engine while the hub is on (set by setup); None when it is switched off.
        self.hub: HubEngine | None = None
        self._rule_sources: dict[str, dict[str, Any]] = {}
        # Entities a rule's message template reads, so state changes re-render it (D-063).
        self._rule_template_entities: dict[str, set[str]] = {}
        self._store = banner_store(hass)
        self._timers: dict[str, CALLBACK_TYPE] = {}
        self._listeners: list[Callable[[], None]] = []
        # Typed transitions for the hub engine, apart from `_listeners` (DESIGN §23.11).
        self._transition_listeners: list[TransitionListener] = []
        # True while loading: transitions are flagged silent.
        self._silent = False
        self.tracked_entities: set[str] = set()
        self._untrack: CALLBACK_TYPE | None = None
        # Pending `for` waits and template trackers, by banner or rule ID (DESIGN §19).
        self._for_timers: dict[str, CALLBACK_TYPE] = {}
        self._template_trackers: dict[str, TrackTemplateResultInfo] = {}
        # One timer per snooze, by (banner ID, user ID or GLOBAL_SNOOZE_KEY) (DESIGN §21).
        self._snooze_timers: dict[tuple[str, str], CALLBACK_TYPE] = {}

    async def async_load(self) -> None:
        self._silent = True
        try:
            await self._load()
        finally:
            self._silent = False

    async def _load(self) -> None:
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
                self._emit(Kind.HIDDEN, banner, Reason.EXPIRED)
                dropped = True
                continue
            self.banners[banner.id] = banner
            self._schedule(banner)
            dropped |= self._restore_snoozes(banner, now)
        # Conditions may have changed while not loaded. Entities that are not loaded yet
        # evaluate to None and keep their stored result (D-006).
        for banner in list(self.banners.values()):
            if banner.condition is not None:
                self._track_template(banner)
                dropped |= self._apply_condition(banner)
        self._refresh_tracking()
        if dropped:
            self._save()

    async def async_unload(self) -> None:
        for cancel in self._timers.values():
            cancel()
        self._timers.clear()
        for cancel in self._snooze_timers.values():
            cancel()
        self._snooze_timers.clear()
        for banner_id in [*self._for_timers, *self._template_trackers]:
            self._cancel_wait(banner_id)
            self._untrack_template(banner_id)
        self._listeners.clear()
        self._transition_listeners.clear()
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
        waits = False
        if condition is not None:
            if "entity_id" in condition and self.hass.states.get(condition["entity_id"]) is None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="entity_not_found",
                    translation_placeholders={"entity_id": condition["entity_id"]},
                )
            met = self._evaluate(condition)
            # A true result waits `for` seconds before it counts (D-066).
            waits = met is True and bool(condition.get("for"))
            if waits:
                met = False

        self._cancel_wait(banner_id)
        self._untrack_template(banner_id)
        result: dict[str, Any] = {"id": banner_id, "status": "updated" if existing else "created"}
        if condition is not None and met is not True:
            result["status"] = "waiting"
        if existing is None and len(self.banners) >= self.options[OPT_MAX_BANNERS]:
            result["evicted"] = self._evict_one()

        timeout: timedelta | None = data.get("timeout")
        if timeout is None:
            timeout = timedelta(seconds=self.options[OPT_DEFAULT_TIMEOUT])
        was_active = existing.active if existing else False
        self._cancel_snoozes(banner_id)  # an upsert starts from no snoozes, like dismissals (D-010)
        dismissible = data.get("dismissible", True)
        banner = Banner(
            id=banner_id,
            message=data["message"],
            title=data.get("title"),
            severity=data.get("severity", DEFAULT_SEVERITY),
            icon=data.get("icon"),
            dismissible=dismissible,
            dismiss_scope=data.get("dismiss_scope") or self.options[OPT_DEFAULT_DISMISS_SCOPE],
            snoozable=dismissible and data.get("snoozable", self.options[OPT_DEFAULT_SNOOZABLE]),
            snooze_scope=data.get("snooze_scope") or self.options[OPT_DEFAULT_SNOOZE_SCOPE],
            snooze_options=list(
                data.get("snooze_options") or self.options[OPT_DEFAULT_SNOOZE_OPTIONS]
            ),
            tag=data.get("tag"),
            tap_action=data.get("tap_action"),
            image=data.get("image"),
            actions=[dict(a) for a in data.get("actions", [])],
            condition=condition,
            mode=data.get("mode", "once"),
            people=list(data.get("people", [])),
            condition_met=met,
            ever_met=met is True,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            expires_at=now + timeout if timeout > timedelta(0) else None,
            channels=list(data.get("channels") or [CHANNEL_BANNER]),
            targets={k: dict(v) for k, v in data.get("targets", {}).items()},
            policy=data.get("policy"),
            tts_message=data.get("tts_message"),
            source=data.get("source", SOURCE_ACTION),
            # Kept across an update with the same severity; a new severity starts again (D-081).
            acknowledged_by=(
                list(existing.acknowledged_by)
                if existing and existing.severity == data.get("severity", DEFAULT_SEVERITY)
                else []
            ),
        )
        self.banners[banner_id] = banner
        self._schedule(banner)
        if waits:
            self._start_wait(banner)
        self._track_template(banner)
        self._fire(EVENT_UPDATED if existing else EVENT_CREATED, banner, severity=banner.severity)
        if existing is None:
            self._emit(Kind.APPEARED, banner)
        else:
            self._emit(Kind.UPDATED, banner)
            if existing.severity != banner.severity:
                self._emit(Kind.SEVERITY_CHANGED, banner)
            if banner.active and not was_active:
                self._emit(Kind.BECAME_VISIBLE, banner)
        self._changed()
        return result

    @callback
    def clear(
        self,
        banner_id: str | None = None,
        tag: str | None = None,
        all_channels: bool = False,
        severities: list[str] | None = None,
        channels: list[str] | None = None,
    ) -> int:
        """Remove messages that match every filter given; no filter matches every message.

        `clear_banner` leaves messages without the banner channel alone (`all_channels` false);
        `clear_notifications` removes any message (D-108, D-158). `channels` selects messages the
        call sent on at least one of those channels. Rule banners are never touched.
        """
        matches = [
            b
            for b in self.banners.values()
            if (banner_id is None or b.id == banner_id)
            and (tag is None or b.tag == tag)
            and (not severities or b.severity in severities)
            and (not channels or any(c in b.channels for c in channels))
            and (all_channels or b.on_card)
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
        """Dismiss for one user; unknown, non-dismissible, untargeted banners are skipped (D-156).

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
        self._require_target(banner, user_id)
        if not banner.dismissible:
            raise HeadsUpError("not_dismissible", f"Banner {banner_id} is not dismissible")
        if banner.dismiss_scope == "global" and banner_id in self.rules:
            # A rule banner cannot be removed: it stays hidden for everyone until its condition
            # turns false, like a per-user dismissal (D-056, D-073).
            if GLOBAL_SNOOZE_KEY not in banner.dismissed_by:
                banner.dismissed_by.append(GLOBAL_SNOOZE_KEY)
                self._fire(EVENT_DISMISSED, banner, scope="global", user_id=user_id)
                self._emit(Kind.HIDDEN, banner, Reason.DISMISSED, user_id)
        elif banner.dismiss_scope == "global":
            self._remove(banner_id, EVENT_DISMISSED, scope="global", user_id=user_id)
        elif user_id not in banner.dismissed_by:
            banner.dismissed_by.append(user_id)
            self._fire(EVENT_DISMISSED, banner, scope="user", user_id=user_id)
            self._emit(Kind.HIDDEN, banner, Reason.DISMISSED, user_id)

    @callback
    def press(self, banner_id: str, user_id: str, key: str) -> None:
        """A viewer pressed a banner button: fire the event, then dismiss if the button says so."""
        banner = self.rules.get(banner_id) or self._get(banner_id)
        button = next((a for a in banner.actions if a["key"] == key), None)
        if button is None:
            raise HeadsUpError("unknown_action", f"Banner {banner_id} has no button {key}")
        if not self._targets(banner, user_id):
            raise HeadsUpError("not_found", f"Banner {banner_id} not found")
        if self.options.get(OPT_DISABLE_ENDED_BUTTONS, True) and self._ended(banner, user_id):
            raise HeadsUpError("message_ended", f"Banner {banner_id} has ended")
        self._fire(EVENT_ACTION, banner, key=key, user_id=user_id)
        if button["dismiss"]:
            self._dismiss_one(banner_id, user_id)
            self._changed()

    def _ended(self, banner: Banner, user_id: str) -> bool:
        """A message whose buttons no longer act (D-125): dismissed for this user or for all,
        acknowledged by anyone, or its condition is not true. A snooze does not end it."""
        return (
            user_id in banner.dismissed_by
            or GLOBAL_SNOOZE_KEY in banner.dismissed_by
            or bool(banner.acknowledged_by)
            or not banner.active
        )

    @property
    def quick_snooze_seconds(self) -> int:
        """The one snooze time of the push and popup buttons (D-142)."""
        return int(self.options[OPT_QUICK_SNOOZE]) * 60

    @callback
    def snooze(self, banner_id: str, user_id: str, seconds: int) -> None:
        banner = self.rules.get(banner_id) or self._get(banner_id)
        self._require_target(banner, user_id)
        if not banner.snoozable:
            raise HeadsUpError("not_snoozable", f"Banner {banner_id} cannot be snoozed")
        if seconds not in banner.snooze_options and seconds != self.quick_snooze_seconds:
            raise HeadsUpError(
                "invalid_snooze", f"{seconds} s is not a choice of banner {banner_id}"
            )
        key = GLOBAL_SNOOZE_KEY if banner.snooze_scope == "global" else user_id
        until = dt_util.utcnow() + timedelta(seconds=seconds)
        banner.snoozed_until[key] = until
        self._schedule_snooze(banner.id, key, until)
        self._fire(
            EVENT_SNOOZED,
            banner,
            scope=banner.snooze_scope,
            user_id=user_id,
            until=until.isoformat(),
        )
        self._emit(Kind.SNOOZED, banner, user_id=user_id)
        self._changed()

    @callback
    def acknowledge(self, banner_id: str, user_id: str) -> None:
        """Someone saw it: escalations and reminders stop for everyone (D-081). The banner stays."""
        banner = self.rules.get(banner_id) or self._get(banner_id)
        if not self._targets(banner, user_id):
            raise HeadsUpError("not_found", f"Banner {banner_id} not found")
        if user_id in banner.acknowledged_by:
            return
        banner.acknowledged_by.append(user_id)
        self._emit(Kind.ACKNOWLEDGED, banner, user_id=user_id)
        self._changed()

    @callback
    def unsnooze(self, banner_id: str, user_id: str) -> None:
        """Ends the snooze that hides the banner from this user (a global one ends for all)."""
        banner = self.rules.get(banner_id) or self._get(banner_id)
        self._require_target(banner, user_id)
        if banner.snoozed_for(user_id) is None:
            raise HeadsUpError("not_snoozed", f"Banner {banner_id} is not snoozed")
        for key in (user_id, GLOBAL_SNOOZE_KEY):
            if banner.snoozed_until.pop(key, None) is not None and (
                cancel := self._snooze_timers.pop((banner.id, key), None)
            ):
                cancel()
        self._fire(EVENT_UNSNOOZED, banner, user_id=user_id)
        self._emit(Kind.UNSNOOZED, banner, user_id=user_id)
        self._changed()

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
        return sum(1 for b in self._all() if b.active and b.on_card and not self._held(b))

    @callback
    def visible(
        self, user_id: str, show_all: bool = False, show_snoozed: bool = False
    ) -> list[dict[str, Any]]:
        # show_all (admin) also returns waiting, dismissed and untargeted banners (D-008).
        # show_snoozed adds the viewer's snoozed banners, flagged, so the card can offer to end
        # the snooze (D-074).
        return [
            self._client(b, user_id)
            for b in self._all()
            if b.on_card
            and (
                show_all
                or (
                    b.active
                    and not self._held(b)
                    and user_id not in b.dismissed_by
                    and GLOBAL_SNOOZE_KEY not in b.dismissed_by
                    and (show_snoozed or b.snoozed_for(user_id) is None)
                    and self._targets(b, user_id)
                )
            )
        ]

    @callback
    def refresh(self) -> None:
        """Tell viewers to read the list again (a hold changed)."""
        self._notify()

    def _held(self, banner: Banner) -> bool:
        """A Summarize policy holds the message until its summary (D-105): not shown to viewers."""
        return self.hub is not None and self.hub.is_held(banner.id)

    @callback
    def subscribe(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        self._listeners.append(listener)

        @callback
        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    @callback
    def subscribe_transitions(self, listener: TransitionListener) -> CALLBACK_TYPE:
        self._transition_listeners.append(listener)

        @callback
        def unsubscribe() -> None:
            if listener in self._transition_listeners:
                self._transition_listeners.remove(listener)

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
                self._cancel_wait(banner_id)
                self._cancel_snoozes(banner_id)
                self._untrack_template(banner_id)
                self._rule_sources.pop(banner_id, None)
                self._rule_template_entities.pop(banner_id, None)
                if gone.condition_met:
                    if not silent:
                        self._fire(EVENT_CLEARED, gone, reason="rule")
                    self._emit(Kind.HIDDEN, gone, Reason.RULE, silent=silent)
                changed = True
        for banner_id, sub in wanted.items():
            # The rule name stands in for {name} when there is no entity (template rules).
            source = {**sub.data, "rule_name": sub.title}
            if self.hub is not None and source.get("people"):
                # A switched-off recipient is not shown the banner; all of them off means nobody
                # (D-147, D-161). Part of the source, so a changed profile rebuilds the rule.
                source["people"] = self.hub.resolver.enabled_people(list(source["people"]))
            if self._rule_sources.get(banner_id) == source:
                continue
            old = self.rules.get(banner_id)
            self._rule_sources[banner_id] = source
            banner = self._build_rule(banner_id, source, old)
            self.rules[banner_id] = banner
            self._track_template(banner)
            if banner.condition_met != bool(old and old.condition_met):
                if banner.condition_met:
                    if not silent:
                        self._fire(EVENT_CREATED, banner, severity=banner.severity)
                    self._emit(Kind.BECAME_VISIBLE, banner, silent=silent)
                else:
                    if not silent:
                        self._fire(EVENT_CLEARED, banner, reason="rule")
                    self._emit(Kind.HIDDEN, banner, Reason.RULE, silent=silent)
            elif banner.condition_met and old is not None and old.severity != banner.severity:
                # An edited rule that stays visible: its policies restart, as for an action (D-081).
                self._emit(Kind.SEVERITY_CHANGED, banner, silent=silent)
            elif banner.condition_met and old is not None and old.policy != banner.policy:
                # A changed policy choice must drop timers of the old one (a reminder that
                # kept showing after the rule was set to "none").
                self._emit(Kind.UPDATED, banner, silent=silent)
            changed = True
        self._refresh_tracking()
        if changed and not silent:
            self._notify()

    def _build_rule(self, banner_id: str, source: Mapping[str, Any], old: Banner | None) -> Banner:
        now = dt_util.utcnow()
        condition: dict[str, Any]
        if source.get("template"):
            condition = {"template": source["template"]}
        else:
            condition = {"entity_id": source["entity_id"]}
            if source.get("operator", DEFAULT_OPERATOR) not in NO_STATE_OPERATORS:
                condition["state"] = list(source.get("state") or ["on"])
            if source.get("operator", DEFAULT_OPERATOR) != DEFAULT_OPERATOR:
                condition["operator"] = source["operator"]
            if source.get("attribute"):
                condition["attribute"] = source["attribute"]
        if source.get("for"):
            condition["for"] = int(source["for"])
        self._cancel_wait(banner_id)
        self._cancel_snoozes(banner_id)
        self._untrack_template(banner_id)
        met = self._evaluate(condition) is True
        if met and condition.get("for"):
            # True now, but it counts only after `for` seconds; the timer restarts on load (D-066).
            met = False
            self._start_wait_for(banner_id, condition["for"])
        dismissible = source.get("dismissible", False)
        return Banner(
            id=banner_id,
            message=self._rule_message(banner_id, source),
            title=source.get("title") or None,
            severity=source.get("severity", DEFAULT_SEVERITY),
            icon=source.get("icon") or None,
            dismissible=dismissible,
            # A rule without the field keeps the per-user dismissal of earlier versions, whatever
            # the option default says (D-073).
            dismiss_scope=source.get("dismiss_scope") or "user",
            actions=[{"dismiss": False, **a} for a in source.get("actions", [])],
            tap_action=source.get("tap_action"),
            image=source.get("image") or None,
            snoozable=dismissible and source.get("snoozable", self.options[OPT_DEFAULT_SNOOZABLE]),
            snooze_scope=source.get("snooze_scope") or self.options[OPT_DEFAULT_SNOOZE_SCOPE],
            snooze_options=list(
                source.get("snooze_options") or self.options[OPT_DEFAULT_SNOOZE_OPTIONS]
            ),
            tag=RULE_TAG,
            policy=(source.get("policy") or None),
            source=SOURCE_RULE,
            acknowledged_by=(
                list(old.acknowledged_by)
                if old and old.severity == source.get("severity", DEFAULT_SEVERITY)
                else []
            ),
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
        entity_id = source.get("entity_id")
        state = self.hass.states.get(entity_id) if entity_id else None
        name = (state.attributes.get("friendly_name") if state else None) or (
            entity_id or source.get("rule_name", "")
        )
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

    def _apply_rule(self, banner: Banner, elapsed: bool = False) -> bool:
        # Unavailable, unknown and removed entities hide the banner (D-053).
        assert banner.condition is not None
        raw = self._evaluate(banner.condition) is True
        met = self._effective(banner, raw, elapsed)
        if met is None:
            met = banner.condition_met is True
        message = self._rule_message(banner.id, self._rule_sources[banner.id])
        changed = message != banner.message
        banner.message = message
        if met != banner.condition_met:
            banner.condition_met = met
            changed = True
            if met:
                banner.updated_at = dt_util.utcnow()  # the card's "time ago" counts from the flip
                self._fire(EVENT_CREATED, banner, severity=banner.severity)
                self._emit(Kind.BECAME_VISIBLE, banner)
            else:
                banner.dismissed_by.clear()  # a dismissal lasts until the condition flips (D-056)
                banner.acknowledged_by.clear()  # a new occurrence needs a new acknowledgement
                self._cancel_snoozes(banner.id)
                self._fire(EVENT_CLEARED, banner, reason="rule")
                self._emit(Kind.HIDDEN, banner, Reason.CONDITION)
        elif changed and banner.condition_met:
            self._emit(Kind.UPDATED, banner)  # same rule, new message text
        return changed

    # Internals -------------------------------------------------------------------------

    def _client(self, banner: Banner, user_id: str) -> dict[str, Any]:
        data = banner.to_client(user_id)
        # Who acknowledged is shown as first names (D-116); a user without a person is counted only.
        data["acknowledged"] = bool(banner.acknowledged_by)
        data["acknowledged_by"] = [
            name for user in banner.acknowledged_by if (name := self._first_name(user))
        ]
        data["acknowledged_count"] = len(banner.acknowledged_by)
        # The Acknowledge button: a policy applies, nobody acknowledged yet, the viewer is a target.
        data["can_acknowledge"] = (
            self.hub is not None
            and not banner.acknowledged_by
            and self._targets(banner, user_id)
            and self.hub.ack_applies(banner)
        )
        if banner.id in self.rules:
            # The card hides "Clear for everyone": a rule banner is disabled or deleted instead.
            data["rule"] = True
        return data

    def _first_name(self, user_id: str) -> str | None:
        for state in self.hass.states.async_all("person"):
            if state.attributes.get("user_id") == user_id:
                words = str(state.attributes.get("friendly_name") or "").split()
                return words[0] if words else None
        return None

    def _all(self) -> Iterator[Banner]:
        return chain(self.banners.values(), self.rules.values())

    def _require_target(self, banner: Banner, user_id: str) -> None:
        """Dismiss, snooze and unsnooze act only for a person the banner is addressed to (D-156)."""
        if not self._targets(banner, user_id):
            raise HeadsUpError("not_targeted", f"Banner {banner.id} is not addressed to you")

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
        if "template" in condition:
            return self._render_condition(condition["template"])
        state = self.hass.states.get(condition["entity_id"])
        if state is None or state.state in _NO_STATE:
            return None
        if (attribute := condition.get("attribute")) is not None:
            raw = state.attributes.get(attribute)
            # None and empty containers have no value; everything else is compared as text.
            value = None if raw is None else "" if raw in ([], {}, ()) else str(raw)
        else:
            value = state.state
        return matches(condition, value)

    def _render_condition(self, source: str) -> bool | None:
        """Truth of a template condition; None if it cannot be rendered (D-067)."""
        try:
            return result_as_boolean(Template(source, self.hass).async_render())
        except TemplateError as err:
            _LOGGER.debug("Condition template failed: %s", err)
            return None

    def _effective(self, banner: Banner, raw: bool | None, elapsed: bool) -> bool | None:
        """Result to apply now, or None for no change. Handles the `for` wait (D-066).

        A true result with `for` first reports False (never evaluated) or nothing (already
        false) and starts a timer; the timer's own call comes back with `elapsed`.
        """
        assert banner.condition is not None
        delay = banner.condition.get("for")
        if raw is None:
            return None
        if not delay or raw is False:
            self._cancel_wait(banner.id)
            return raw
        if elapsed:
            return True
        if banner.condition_met is True:
            return None
        if banner.id not in self._for_timers:
            self._start_wait(banner)
        return False if banner.condition_met is None else None

    def _apply_condition(self, banner: Banner, elapsed: bool = False) -> bool:
        """Re-evaluate one banner's condition. Returns True if anything changed."""
        assert banner.condition is not None
        met = self._effective(banner, self._evaluate(banner.condition), elapsed)
        if met is None or met == banner.condition_met:
            return False
        previous, banner.condition_met = banner.condition_met, met
        if met:
            if banner.mode == "recurring" and previous is False:
                banner.dismissed_by.clear()
                banner.acknowledged_by.clear()
                self._cancel_snoozes(banner.id)
            banner.ever_met = True
            if previous is not True:
                self._emit(Kind.BECAME_VISIBLE, banner)
        elif banner.mode == "once" and banner.ever_met:
            self._remove(banner.id, EVENT_CLEARED, reason="condition")
        elif previous is True:
            self._emit(Kind.HIDDEN, banner, Reason.CONDITION)
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
            if banner.condition is None or banner.condition.get("entity_id") != entity_id:
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
                banner.condition is not None and banner.condition.get("entity_id") == entity_id
            ) or entity_id in self._rule_template_entities.get(banner.id, ()):
                changed |= self._apply_rule(banner)
        if changed:
            self._changed()

    def _refresh_tracking(self) -> None:
        wanted = {
            b.condition["entity_id"]
            for b in self.banners.values()
            if b.condition and "entity_id" in b.condition
        }
        wanted |= {
            b.condition["entity_id"]
            for b in self.rules.values()
            if b.condition and "entity_id" in b.condition
        }
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
        self._cancel_wait(banner_id)
        self._cancel_snoozes(banner_id)
        self._untrack_template(banner_id)
        self._fire(event, banner, **extra)
        reason = extra.get("reason")
        if event == EVENT_EXPIRED:
            reason = Reason.EXPIRED
        elif event == EVENT_DISMISSED:
            reason = Reason.DISMISSED_GLOBAL
        self._emit(Kind.HIDDEN, banner, _REASONS.get(reason or "", Reason.CLEARED))

    def _start_wait(self, banner: Banner) -> None:
        assert banner.condition is not None
        self._start_wait_for(banner.id, banner.condition["for"])

    def _start_wait_for(self, banner_id: str, seconds: float) -> None:
        self._cancel_wait(banner_id)
        self._for_timers[banner_id] = async_call_later(
            self.hass, seconds, partial(self._for_elapsed, banner_id)
        )

    def _cancel_wait(self, banner_id: str) -> None:
        if cancel := self._for_timers.pop(banner_id, None):
            cancel()

    @callback
    def _for_elapsed(self, banner_id: str, _now: datetime) -> None:
        self._for_timers.pop(banner_id, None)
        if banner_id in self.banners:
            changed = self._apply_condition(self.banners[banner_id], elapsed=True)
        elif banner_id in self.rules:
            changed = self._apply_rule(self.rules[banner_id], elapsed=True)
        else:
            return
        if changed:
            self._changed()

    def _track_template(self, banner: Banner) -> None:
        """Re-evaluate a template condition when what it reads changes (HA_API_NOTES N-67)."""
        if banner.condition is None or "template" not in banner.condition:
            return
        self._untrack_template(banner.id)
        template = Template(banner.condition["template"], self.hass)
        self._template_trackers[banner.id] = async_track_template_result(
            self.hass,
            [TrackTemplate(template, None)],
            partial(self._template_changed, banner.id),
        )

    def _untrack_template(self, banner_id: str) -> None:
        if tracker := self._template_trackers.pop(banner_id, None):
            tracker.async_remove()

    @callback
    def _template_changed(
        self,
        banner_id: str,
        _event: Event[EventStateChangedData] | None,
        _updates: list[TrackTemplateResult],
    ) -> None:
        if (banner := self.banners.get(banner_id)) is not None:
            changed = self._apply_condition(banner)
        elif (rule := self.rules.get(banner_id)) is not None:
            changed = self._apply_rule(rule)
        else:
            return
        if changed:
            self._changed()

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

    def _schedule_snooze(self, banner_id: str, key: str, until: datetime) -> None:
        if cancel := self._snooze_timers.pop((banner_id, key), None):
            cancel()
        # HA_API_NOTES N-7
        self._snooze_timers[(banner_id, key)] = async_track_point_in_utc_time(
            self.hass, partial(self._snooze_elapsed, banner_id, key), until
        )

    @callback
    def _snooze_elapsed(self, banner_id: str, key: str, _now: datetime) -> None:
        self._snooze_timers.pop((banner_id, key), None)
        banner = self.banners.get(banner_id) or self.rules.get(banner_id)
        if banner is not None and banner.snoozed_until.pop(key, None) is not None:
            # No bus event fires for an ended snooze; the engine still needs to know (D-078).
            self._emit(
                Kind.UNSNOOZED,
                banner,
                Reason.ELAPSED,
                None if key == GLOBAL_SNOOZE_KEY else key,
            )
            self._changed()

    def _cancel_snoozes(self, banner_id: str) -> None:
        for timer_key in [k for k in self._snooze_timers if k[0] == banner_id]:
            self._snooze_timers.pop(timer_key)()
        banner = self.banners.get(banner_id) or self.rules.get(banner_id)
        if banner is not None:
            banner.snoozed_until.clear()

    def _restore_snoozes(self, banner: Banner, now: datetime) -> bool:
        """Re-arm stored snoozes; returns True if ended ones were dropped."""
        ended = [key for key, until in banner.snoozed_until.items() if until <= now]
        for key in ended:
            del banner.snoozed_until[key]
        for key, until in banner.snoozed_until.items():
            self._schedule_snooze(banner.id, key, until)
        return bool(ended)

    def _emit(
        self,
        kind: Kind,
        banner: Banner,
        reason: str | None = None,
        user_id: str | None = None,
        silent: bool = False,
    ) -> None:
        if not self._transition_listeners:
            return
        transition = BannerTransition(
            kind, deepcopy(banner), reason, user_id, silent or self._silent
        )
        for listener in list(self._transition_listeners):
            listener(transition)

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
