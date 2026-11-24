"""Delivery engine: turns transitions into deliveries (DESIGN §23.11).

Work runs in background tasks, serialized per message and bounded overall. `plan` is the dry run
that the action response and the panel's Test send both use, so what is reported is what is done.
"""

from __future__ import annotations

import asyncio
import logging
import re
import secrets
from collections.abc import Callable, Coroutine, Mapping
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from ..const import (
    BANNER_NOBODY,
    CHANNEL_BANNER,
    CHANNEL_INBOX,
    CHANNEL_PERSISTENT,
    DEFAULT_INBOX_RETENTION_MONTHS,
    DEFAULT_OPTIONS,
    EVENT_DELIVERY_FAILED,
    GLOBAL_SNOOZE_KEY,
    HOLD_AWAY,
    HOLD_QUIET,
    OPT_INBOX_MIRROR,
    OPT_INBOX_RETENTION_MONTHS,
    OPT_PRESENCE_DEBOUNCE,
    OPT_RECENT_MESSAGES,
    OPT_TRACE_ENTRIES,
    SAVE_DELAY,
    SOURCE_RULE,
    SOURCE_SUMMARY,
    SUMMARY_LIFETIME_HOURS,
    SUMMARY_PREFIX,
    TARGET_CHANNELS,
    TEST_ID_PREFIX,
    TIMER_CHANNEL,
)
from ..models import Banner
from ..storage import trace_store
from .activity import Activity, ActivityLog, RecentMessages
from .channels import ChannelRegistry, Outcome, Result, Target
from .channels.inbox import item_fields
from .channels.persistent import warn_speech
from .channels.speak import NO_SPEAKER
from .identity import IdentityMaps, maps_for
from .inbox import InboxStore
from .interfaces import AudienceResolver, RecipientResolver
from .ledger import Delivery, DeliveryLedger, HeldMessage, State
from .limits import DUPLICATE, RATE_LIMITED, Limiter
from .policies import PolicyBook, escalation, fallback, only_if, reminder, summarize
from .policies.chain import Chain, Hold, Skip, Step
from .policies.models import Policy
from .policies.presence import PresenceStage
from .policies.quiet import QuietHoursStage
from .resolver import HubResolver, Recipient
from .stats import StatsStore
from .trace import TraceBuffer, TraceEntry
from .transitions import BannerTransition, Kind, Reason
from .usage import AudienceUsage

_LOGGER = logging.getLogger(__name__)
MAX_CONCURRENT = 8

type TaskFactory = Callable[[Coroutine[Any, Any, None], str], asyncio.Task[None]]


# Skips that mean a message reached nobody on a channel, as opposed to a choice (quiet hours,
# a duplicate, a cooldown). They fire the delivery-failed event with every failed send (D-128).
NOBODY_REASONS = frozenset(
    {
        "no_recipients",
        "no_usable_device",
        "service_not_found",
        "device_missing",
        "channel_not_accepted",
        "group_empty",
        "unknown_audience",
        "unknown_recipient",
        "person_not_found",
        "no_user",
        "presence_unknown",
        "no_mail_address",
        RATE_LIMITED,
    }
)


# Channels whose `update` does not deliver again to a recipient that already got the message, with
# the reason the trace shows (speech: said once; mail: cannot be replaced).
NOT_REPEATED_ON_UPDATE = {"speak": "already_spoken", "mail": "already_sent"}


@dataclass(frozen=True, slots=True)
class Planned:
    """One delivery a message would produce."""

    channel: str
    recipient: str  # "" for channels without recipients
    result: Result
    reason: str | None = None
    who: Recipient | None = None  # what the resolver knows about the recipient


AUTO_ID = re.compile(r"^hu_[0-9a-f]{10}$")


def source_key(banner: Banner) -> str:
    """What made a message, as a stable key for the history: a watch rule by its rule ID; a call
    by the ID its author chose, else by its tag, else just `action`; Test send is `test`."""
    if banner.source == SOURCE_RULE:
        return banner.id
    if banner.id.startswith(TEST_ID_PREFIX):
        return "test"
    if not AUTO_ID.match(banner.id):
        return f"id:{banner.id[:64]}"
    return f"tag:{banner.tag[:64]}" if banner.tag else "action"


# The channels that deliver to a person and so leave a copy (the banner too, by its people).
MIRROR_CHANNELS = ("push", "popup", "mail")

# How the reason a message ended is kept on an inbox item (the rest is `cleared`).
INBOX_REASONS = {
    str(Reason.EXPIRED): "expired",
    str(Reason.CONDITION): "condition",
    str(Reason.DISMISSED_GLOBAL): "dismissed",
}

# The log kinds that are an action of a policy, and how the history counts them.
POLICY_LOG_ACTIONS = {
    "escalation_sent": "escalated",
    "reminder_sent": "reminded",
    "fallback_sent": "fallback",
    "deliver_sent": "delivered",
}


class HubEngine:
    def __init__(
        self, hass: HomeAssistant, options: dict[str, Any], create_task: TaskFactory
    ) -> None:
        self.hass = hass
        self._options = options  # the live options of the entry
        self.channels = ChannelRegistry()
        self.ledger = DeliveryLedger(hass)
        self.trace = TraceBuffer(options.get(OPT_TRACE_ENTRIES, DEFAULT_OPTIONS[OPT_TRACE_ENTRIES]))
        self._trace_store = trace_store(hass)
        self.usage = AudienceUsage(hass)
        self.stats = StatsStore(hass)
        self.inbox = InboxStore(hass)
        self.inbox.retention_months = int(
            options.get(OPT_INBOX_RETENTION_MONTHS, DEFAULT_INBOX_RETENTION_MONTHS)
        )
        self.resolver = HubResolver(hass, options)
        self.limiter = Limiter(options)
        self.log = ActivityLog(options.get(OPT_TRACE_ENTRIES, DEFAULT_OPTIONS[OPT_TRACE_ENTRIES]))
        self.recent = RecentMessages(
            options.get(OPT_RECENT_MESSAGES, DEFAULT_OPTIONS[OPT_RECENT_MESSAGES])
        )
        # The names a call may use come from the resolver (H2) and the policy book (H4a).
        self.audiences: AudienceResolver = self.resolver
        self.recipients: RecipientResolver = self.resolver
        self.policies = PolicyBook(options)
        self.policies.household = self.resolver.household
        self.policies.condition = lambda condition: only_if.evaluate(hass, condition)
        self._unsub_conditions: CALLBACK_TYPE | None = None
        self._condition_waits: list[CALLBACK_TYPE] = []
        # The objects that exist now, to turn a name stored by an earlier version into a key.
        self.identity = IdentityMaps()
        self.chain = Chain()
        self.chain.replace(QuietHoursStage(self.policies, hass))
        self.chain.replace(
            PresenceStage(hass, self.policies, self.resolver.zone_entity, self.resolver.household)
        )
        self._unsub_arrival: CALLBACK_TYPE | None = None
        self._unsub_quiet: CALLBACK_TYPE | None = None
        self._presence_waits: dict[str, CALLBACK_TYPE] = {}  # person to the presence delay
        # Set by the manager: make a message (the summaries), and tell viewers a hold changed.
        self.create_message: Callable[[dict[str, Any]], dict[str, Any]] = lambda data: {}
        self.visibility_changed: Callable[[], None] = lambda: None
        self._released: set[str] = set()  # held messages that become normal messages again
        # The live message by id; the manager sets it. Timers read the message when they fire.
        self.lookup: Callable[[str], Banner | None] = lambda _id: None
        self._timers: dict[tuple[str, str], CALLBACK_TYPE] = {}
        self._create_task = create_task
        self._tails: dict[str, asyncio.Task[None]] = {}
        self._gate = asyncio.Semaphore(MAX_CONCURRENT)
        self._closed = False
        self._ready = asyncio.Event()  # set once the ledger is loaded

    async def async_start(self, known_ids: set[str]) -> None:
        """Load the ledger and forget what no longer exists, without re-sending anything."""
        self.ledger.identity = self.identity
        await self.ledger.async_load()
        await self.stats.async_load()
        await self.inbox.async_load()
        if self.ledger.migrated:
            _LOGGER.info("Stored deliveries: %d names became keys", self.ledger.migrated)
            await self.ledger.async_save()
        stored = await self._trace_store.async_load() or {}
        self.trace.load(stored.get("entries"))
        await self.usage.async_load()
        await self.resolver.async_start()
        for held in list(self.ledger.held.values()):
            if held.message_id not in known_ids:  # it ended while Home Assistant was stopped
                self._message_gone(held.message_id)
        for message_id in self.ledger.message_ids() - known_ids:
            if message_id.startswith(SUMMARY_PREFIX):
                continue  # the timer of a Summarize policy, not a message
            for row in self.ledger.for_message(message_id):
                if row.state is State.SENT and row.channel != CHANNEL_BANNER:
                    # The message ended while Home Assistant was stopped: take its push back.
                    target = Target(row.recipient, "", row.person)
                    await self.channels.get(row.channel).clear(message_id, target, row.ref)
                self._trace(message_id, row.channel, row.recipient, "cleared", "gone_at_startup")
            self.ledger.drop_message(message_id)
        for message_id in sorted(known_ids):
            # A rule or conditional banner whose condition is false at the start is not showing:
            # listing it would mark it Active, as nothing will ever end it (silent startup).
            if (loaded := self.lookup(message_id)) is not None and loaded.active:
                self.recent.seen(message_id, self._info(loaded))
        self._resolve_gone_inbox_items()
        await self._restore_bell()
        self._restore_timers()
        # Arrival releases the deliveries held by Away.
        self._unsub_arrival = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_state_change, event_filter=self._is_presence_source
        )
        # The end of a Quiet hours entity releases what it held (D-218, D-220).
        self._unsub_quiet = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_quiet_entity, event_filter=self._is_quiet_entity
        )
        # Only if and Faster while: a change releases holds and re-plans timers (D-216).
        self._unsub_conditions = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_condition_entity, event_filter=self._is_condition_entity
        )
        self.inbox.async_start()
        self._plan_condition_waits()
        if self.policies.watched():
            # A condition may have changed while Home Assistant was stopped: check the holds and
            # timers once, as a change would; what still holds is held again (DESIGN §25.16).
            self.conditions_changed()
        self._ready.set()

    async def _restore_bell(self) -> None:
        """The notification bell of Home Assistant lives in memory only. A message that is still
        active and was shown there gets its entry back after a restart; the same id replaces."""
        channel = self.channels.get(CHANNEL_PERSISTENT)
        for row in list(self.ledger.rows.values()):
            if row.channel != CHANNEL_PERSISTENT or row.state is not State.SENT:
                continue
            banner = self.lookup(row.message_id)
            if banner is None or not banner.active or self.is_held(row.message_id):
                continue
            outcome = await channel.deliver(banner, Target(row.recipient))
            self._trace(row.message_id, row.channel, row.recipient, "sent", "restored_at_startup")
            if outcome.result is not Result.SENT:
                self._record(row.message_id, row.channel, row.recipient, outcome)

    async def async_unload(self) -> None:
        self._closed = True
        self.channels.stop_all()
        self._cancel_all_timers()
        if self._unsub_arrival is not None:
            self._unsub_arrival()
            self._unsub_arrival = None
        if self._unsub_quiet is not None:
            self._unsub_quiet()
            self._unsub_quiet = None
        if self._unsub_conditions is not None:
            self._unsub_conditions()
            self._unsub_conditions = None
        for cancel in self._condition_waits:
            cancel()
        self._condition_waits.clear()
        for cancel in self._presence_waits.values():
            cancel()
        self._presence_waits.clear()
        tasks = list(self._tails.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tails.clear()
        await self.resolver.async_stop()
        await self.ledger.async_save()
        await self._trace_store.async_save(self._trace_data())
        await self.usage.async_save()
        await self.stats.async_save()
        await self.inbox.async_stop()

    async def async_wait_idle(self) -> None:
        """Wait until the queued deliveries are done (tests, and a clean unload)."""
        while self._tails:
            await asyncio.wait(list(self._tails.values()))
            await asyncio.sleep(0)  # lets the done callbacks drop finished tasks

    # Planning ---------------------------------------------------------------------------

    def delivered(self, message_id: str | None) -> frozenset[tuple[str, str]]:
        """The channel and recipient pairs a message has already been sent to. Taken before a
        call replaces the message, because the update changes the rows (D-166)."""
        if not message_id:
            return frozenset()
        return frozenset(
            (row.channel, row.recipient)
            for (mid, _channel, _key), row in self.ledger.rows.items()
            if mid == message_id and row.state.value == "sent"
        )

    async def plan(
        self,
        message: Banner,
        *,
        waiting: bool = False,
        delivered: frozenset[tuple[str, str]] = frozenset(),
    ) -> list[Planned]:
        """What delivering this message would do now. Sends nothing.

        `delivered` holds what the message had already been sent to before a call replaced it:
        speech and mail are not repeated for those recipients, as `update` of the channel
        decides at delivery (D-166)."""
        planned: list[Planned] = []
        for channel in message.channels:
            available = self.channels.get(channel).available
            if channel == CHANNEL_BANNER:
                result = Result.HELD if waiting else Result.SENT
                reason = "waiting_for_condition" if waiting else None
                if message.people == [BANNER_NOBODY]:  # the audience was empty at creation (D-131)
                    result, reason = Result.SKIPPED, "no_recipients"
                planned.append(Planned(channel, "", result, reason))
                continue
            if channel not in TARGET_CHANNELS:  # persistent: no target, goes to everyone
                if waiting:
                    planned.append(Planned(channel, "", Result.HELD, "waiting_for_condition"))
                else:
                    planned.append(self._planned(channel, "", available))
                continue
            resolution = await self.resolver.resolve(
                message.targets.get(channel), channel, message.severity
            )
            if waiting:
                # Nothing is delivered before the condition is true; resolution still shows who.
                planned += [
                    Planned(channel, r.key, Result.HELD, "waiting_for_condition", r)
                    for r in resolution.recipients
                ]
            else:
                planned += [
                    self._planned_update(channel, r, available, delivered)
                    for r in resolution.recipients
                ]
            planned += [
                Planned(channel, s.who, Result.SKIPPED, s.reason) for s in resolution.skipped
            ]
            if not resolution.recipients and not resolution.skipped:
                planned.append(Planned(channel, "", Result.SKIPPED, "no_recipients"))
        return planned

    def _planned_update(
        self,
        channel: str,
        who: Recipient,
        available: bool,
        delivered: frozenset[tuple[str, str]],
    ) -> Planned:
        """A recipient that speech or mail already reached is skipped on an update (D-166)."""
        reason = NOT_REPEATED_ON_UPDATE.get(channel)
        if available and reason and (channel, who.key) in delivered:
            return Planned(channel, who.key, Result.SKIPPED, reason, who)
        return self._planned(channel, who.key, available, who)

    @staticmethod
    def _planned(
        channel: str, recipient: str, available: bool, who: Recipient | None = None
    ) -> Planned:
        if available:
            return Planned(channel, recipient, Result.SENT, who=who)
        return Planned(channel, recipient, Result.SKIPPED, "channel_unavailable", who)

    async def preview(self, message: Banner) -> dict[str, Any]:
        """What the first delivery of this message would do now, chain included, sending nothing.

        The same planning and the same precedence chain as a real delivery, so the preview cannot
        drift (D-120). The message is never stored."""
        summary = self._summary_policy(message)
        planned = await self.plan(message)
        rows: list[dict[str, Any]] = []
        results: list[tuple[Planned, Outcome]] = []
        for item in planned:
            row = self._preview_row(message, item, summary)
            rows.append(row)
            results.append((item, Outcome(Result(row["result"]), row["reason"])))
        if summary is None:
            for policy in self.policies.for_message(message):
                if policy.type != "deliver":
                    continue
                if (problem := self.policy_problem(policy)) is not None:
                    rows.append(
                        {
                            "channel": "",
                            "recipient": "",
                            "result": "skipped",
                            "reason": problem,
                            "via": policy.name,
                        }
                    )
                    continue
                extra = escalation.message_for(message, policy)
                for item in await self.plan(extra):
                    rows.append({**self._preview_row(extra, item, None), "via": policy.name})
            by_channel = self._unreached(results)
            classes = set().union(*by_channel.values()) if by_channel else set()
            # As the engine: no Fallback when a Deliver reached someone (D-235 O9).
            if any(
                r.get("via") and r["channel"] != CHANNEL_BANNER and r["result"] in ("sent", "held")
                for r in rows
            ):
                classes = set()
            for policy in self.policies.for_message(message):
                if policy.type != "fallback" or not fallback.matches(policy.when, classes):
                    continue
                if (problem := self.policy_problem(policy)) is not None:
                    rows.append(
                        {
                            "channel": "",
                            "recipient": "",
                            "result": "skipped",
                            "reason": problem,
                            "via": policy.name,
                        }
                    )
                    continue
                other = escalation.message_for(
                    message, policy, self._channels_matching(policy.when, by_channel)
                )
                for item in await self.plan(other):
                    rows.append({**self._preview_row(other, item, None), "via": policy.name})
        applied = self.policies.for_message(message)
        return {
            "rows": rows,
            "policies": [{"name": p.name, "type": p.type} for p in applied],
            "later": [self._later(p) for p in applied if p.type not in ("quiet_hours", "deliver")],
            "held_for_summary": summary.name if summary else None,
            "banner_people": [p for p in message.people if p != BANNER_NOBODY],
            # Acknowledging is not a field of the call: it matters when an escalation or a
            # reminder applies, so the panel shows which ones do.
            "acknowledge": [p.name for p in self.policies.timed_for(message)],
        }

    def _preview_row(
        self, message: Banner, item: Planned, summary: Policy | None
    ) -> dict[str, Any]:
        row: dict[str, Any] = {
            "channel": item.channel,
            "recipient": item.recipient,
            "person": item.who.person if item.who else None,
            "result": item.result.value,
            "reason": item.reason,
            "note": None,
            "until": None,
            "via": None,
        }
        mail = self.channels.get("mail")
        if item.channel == "mail" and item.result is Result.SENT and hasattr(mail, "check"):
            # Where the mail would go, and whether it would fail for want of an address (D-178).
            address, problem = mail.check(self._target(item, message, ack=False))
            row["address"] = address or None
            if problem:
                return {**row, "result": "failed", "reason": problem}
        if summary is not None:
            return {
                **row,
                "result": "held",
                "reason": "summarize",
                "note": summary.name,
                "by": summary.name,
            }
        if item.result is Result.SENT:
            step = self.chain.run(
                Step(message, item.channel, self._target(item, message, ack=False), "message")
            )
            if isinstance(step, Skip):
                return {**row, "result": "skipped", "reason": step.reason, "by": step.policy}
            if isinstance(step, Hold):
                until = step.until.isoformat() if step.until else None
                return {
                    **row,
                    "result": "held",
                    "reason": step.reason,
                    "until": until,
                    "by": step.policy,
                }
            push = self.channels.get("push")
            if item.channel == "push" and hasattr(push, "level_for"):
                row["push_level"] = push.level_for(step.banner, step.target)
            if step.target.quiet:
                row["note"] = "quiet"
                row["by"] = step.target.quiet_by
            # A band entry that let it past quiet hours for this recipient (DESIGN §25.8).
            through = [
                e.name
                for e in self.policies.band_for(message)
                if self.policies.covers(e, step.target)
            ]
            if through:
                row["through"] = through
        return row

    @staticmethod
    def _later(policy: Policy) -> dict[str, Any]:
        """The timing of a policy, as fields the panel words."""
        fields = {
            "escalation": ("after_minutes", "channels"),
            "reminder": ("every_minutes", "max_count", "channels"),
            "presence": ("max_wait",),
            "fallback": ("when", "channels"),
            "deliver": ("channels",),
            "summarize": ("summary_every", "summary_at", "holds_anyway"),
        }
        out: dict[str, Any] = {"type": policy.type, "policy": policy.name}
        for key in fields.get(policy.type, ()):
            value = getattr(policy, key)
            out[key] = list(value) if isinstance(value, tuple) else value
        # Where the channels and recipients come from, only when not the policy itself (D-181).
        for key in ("channels_from", "targets_from"):
            if (
                policy.type in ("escalation", "fallback", "deliver")
                and getattr(policy, key) != "policy"
            ):
                out[key] = getattr(policy, key)
        return out

    @staticmethod
    def counts(planned: list[Planned]) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for item in planned:
            per = out.setdefault(item.channel, {"sent": 0, "held": 0, "skipped": 0, "failed": 0})
            per[item.result.value] += 1
        return out

    @staticmethod
    def reasons(planned: list[Planned]) -> list[dict[str, str]]:
        """Why a planned delivery is held or skipped, for the response of a call (D-165). Only
        the reasons known when the plan is made; later ones (rate limit, quiet hours, a repeated
        speech) are in the trace."""
        return [
            {
                "channel": item.channel,
                "recipient": (item.who.person if item.who and item.who.person else item.recipient),
                "result": item.result.value,
                "reason": item.reason,
            }
            for item in planned
            if item.reason and item.result in (Result.HELD, Result.SKIPPED, Result.FAILED)
        ]

    # Transitions ------------------------------------------------------------------------

    @callback
    def on_transition(self, transition: BannerTransition) -> None:
        if self._closed:
            return
        banner = transition.banner
        self._remember(transition)
        self._inbox_transition(transition)
        if self._ready.is_set():
            # Decided here, in the same call that created the message, so a viewer is never shown a
            # message that is about to be held (D-105).
            if transition.kind in (Kind.APPEARED, Kind.BECAME_VISIBLE):
                self._try_hold(banner)
            elif transition.kind is Kind.UPDATED:
                self._update_held(banner)
        self._enqueue(banner.id, lambda: self._handle(transition), f"heads_up hub {banner.id}")

    # The panel's log and recent messages (D-118) -----------------------------------------

    def _user_name(self, user_id: str | None) -> str | None:
        """First name of the person behind a user, for "acknowledged by"."""
        for person in self.resolver.persons_of_user(user_id) if user_id else []:
            state = self.hass.states.get(person)
            words = str((state.attributes.get("friendly_name") if state else None) or "").split()
            if words:
                return words[0]
        return None

    def _info(self, banner: Banner) -> dict[str, Any]:
        return {
            "title": banner.title,
            "message": banner.message,
            "severity": banner.severity,
            "channels": list(banner.channels),
            "source": banner.source,
            "created_at": banner.created_at.isoformat(),
        }

    def _count_audiences(self, banner: Banner) -> None:
        """Count the audiences this message is sent to, once per message (D-227). A summary
        counts for its own message id; the messages it summarizes were counted when held."""
        keys = []
        for target in banner.targets.values():
            if "audience" in target and (found := self.resolver.audience(str(target["audience"]))):
                keys.append(found.key)
        if not keys:
            return
        self.usage.record(banner.id, keys, dt_util.utcnow())
        self.recent.audiences(banner.id, keys)

    def _log(self, kind: str, message_id: str, detail: str | None = None) -> None:
        banner = self.lookup(message_id)
        known = next((m for m in self.recent.listed() if m["id"] == message_id), {})
        title = banner.title if banner else known.get("title")
        severity = banner.severity if banner else known.get("severity")
        self.log.add(
            Activity(
                dt_util.utcnow().isoformat(), kind, message_id, title or None, severity, detail
            )
        )
        # The same call counts what a policy did, by its key: a rename keeps the history.
        action = POLICY_LOG_ACTIONS.get(kind)
        if action and detail and (policy := self.policies.by_name(detail.split("|")[0])):
            self.stats.policy_action(dt_util.utcnow(), policy.key, action)

    def _remember(self, transition: BannerTransition) -> None:
        banner, kind = transition.banner, transition.kind
        now = dt_util.utcnow()
        if kind in (Kind.APPEARED, Kind.BECAME_VISIBLE):
            self.recent.seen(banner.id, self._info(banner))
            if not transition.silent and banner.source != SOURCE_SUMMARY:
                self._log("created", banner.id, ",".join(banner.channels))
                self.stats.created(now, banner.severity, banner.tag, source_key(banner))
            return
        if transition.silent:
            return
        who = self._user_name(transition.user_id)
        if kind is Kind.ACKNOWLEDGED:
            self._log("acknowledged", banner.id, who)
            self.stats.acknowledged(
                now,
                banner.severity,
                (now - banner.created_at).total_seconds(),
                self._pending_escalations(banner.id),
            )
        elif kind is Kind.SNOOZED:
            self._log("snoozed", banner.id, who)
            self.stats.snoozed(now)
        elif kind is Kind.UNSNOOZED:
            self._log("unsnoozed", banner.id, who)
        elif kind is Kind.HIDDEN and transition.reason == Reason.DISMISSED:
            self._log("dismissed", banner.id, who)
            self.stats.dismissed(now)
        elif transition.ends_message:
            self.recent.ended(banner.id, now.isoformat(), transition.reason)
            expired = transition.reason == Reason.EXPIRED
            self._log("expired" if expired else "cleared", banner.id, transition.reason)
            if banner.source != SOURCE_SUMMARY:
                self.stats.ended(
                    now, str(transition.reason), (now - banner.created_at).total_seconds()
                )

    def _inbox_transition(self, transition: BannerTransition) -> None:
        """What happens to the inbox items of a message: acknowledged, dismissed or ended. The
        channel cannot know why it is asked to clear, so the transitions say it (D-264)."""
        if transition.silent:
            return
        banner, kind, reason = transition.banner, transition.kind, transition.reason
        now = dt_util.utcnow()
        people = self.resolver.persons_of_user(transition.user_id) if transition.user_id else []
        if kind is Kind.ACKNOWLEDGED:
            for person in people or [""]:
                self.inbox.acknowledged(banner.id, person, now)
        elif kind is Kind.HIDDEN and reason == Reason.DISMISSED:
            for person in people:
                self.inbox.dismissed(banner.id, person, now)
        elif transition.ends_message:
            if reason == Reason.DISMISSED_GLOBAL:
                for person in people:
                    self.inbox.mark_read(person, banner.id, now)
            self.inbox.resolve(banner.id, INBOX_REASONS.get(str(reason), "cleared"), now)

    def _resolve_gone_inbox_items(self) -> None:
        """A message that ended while Home Assistant was stopped: its items are resolved."""
        now = dt_util.utcnow()
        for person in self.inbox.people():
            for item in self.inbox.items(person):
                if item.resolved_at is not None:
                    continue
                banner = self.lookup(item.message_id)
                if banner is None or not banner.active:
                    self.inbox.resolve(item.message_id, "cleared", now)

    def _pending_escalations(self, message_id: str) -> int:
        """Escalations still waiting to fire: an acknowledgement is about to stop them."""
        count = 0
        for row in self.ledger.timers(message_id):
            policy = self.policies.by_key(row.recipient)
            if policy is not None and policy.type == "escalation" and row.state is State.PLANNED:
                count += 1
        return count

    def _enqueue(
        self, message_id: str, work: Callable[[], Coroutine[Any, Any, None]], name: str
    ) -> None:
        previous = self._tails.get(message_id)

        async def run() -> None:
            await self._ready.wait()
            if previous is not None:
                await asyncio.wait({previous})
            async with self._gate:
                try:
                    await work()  # created here, so a cancelled task leaves no unawaited coroutine
                except asyncio.CancelledError:
                    raise
                except Exception:
                    _LOGGER.exception("Hub delivery for %s failed", message_id)

        task = self._create_task(run(), name)
        self._tails[message_id] = task

        def forget(done: asyncio.Task[None]) -> None:
            if self._tails.get(message_id) is done:
                del self._tails[message_id]

        task.add_done_callback(forget)

    async def _handle(self, transition: BannerTransition) -> None:
        banner = transition.banner
        kind = transition.kind
        if transition.ends_message:
            await self._end(banner)
        elif kind is Kind.HIDDEN and transition.reason == Reason.DISMISSED:
            self.note(banner.id, "", self._user_name(transition.user_id) or "", "dismissed", "")
            await self._take_back(banner, transition.user_id)
            self._dismissed(banner)
        elif kind is Kind.ACKNOWLEDGED:
            self._stop_timers(banner.id, "acknowledged")
            self.note(banner.id, "", transition.user_id or "", "acknowledged", "ok")
        elif kind is Kind.PROGRESS:
            # Only the push follows the bar; speech, popup and mail would repeat the message.
            if banner.active and not self.is_held(banner.id):
                planned = [p for p in await self.plan(banner) if p.channel == "push"]
                await self._send(banner, planned, update=True, origin="message")
                # An open popup reads the live message, so it only needs the nudge.
                if refresh := getattr(self.channels.get("popup"), "refresh", None):
                    refresh()
        elif kind is Kind.SEVERITY_CHANGED:
            self._restart_timers(banner)
        elif kind is Kind.SNOOZED:
            everyone = banner.snooze_scope == "global"
            self.note(banner.id, "", self._user_name(transition.user_id) or "", "snoozed", "")
            await self._take_back(banner, None if everyone else transition.user_id)
        elif kind is Kind.UNSNOOZED:
            self.note(banner.id, "", self._user_name(transition.user_id) or "", "unsnoozed", "")
            await self._resend(banner, transition.user_id)
        elif kind in (Kind.APPEARED, Kind.BECAME_VISIBLE, Kind.UPDATED):
            if kind is not Kind.UPDATED:
                self._try_hold(banner)  # the startup transitions come before the ledger is loaded
            if self.is_held(banner.id):
                return  # the summary stands for it
            released = banner.id in self._released
            self._released.discard(banner.id)
            results = await self._deliver(
                banner, update=kind is Kind.UPDATED and not released, resume=transition.silent
            )
            kind = Kind.APPEARED if released else kind
            if kind is not Kind.UPDATED and not transition.silent and banner.active:
                delivered = await self._apply_deliver(banner)
                # A Fallback steps in only when the call and every Deliver reached nobody (O9).
                if not any(
                    o.result in (Result.SENT, Result.HELD)
                    for i, o in delivered
                    if i.channel != CHANNEL_BANNER
                ):
                    await self._fallback(banner, results)
            if kind is Kind.UPDATED and banner.active:
                await self._update_deliver(banner, {(i.channel, i.recipient) for i, _ in results})
            if kind is Kind.UPDATED:
                self._drop_inapplicable_timers(
                    banner
                )  # the policy field or the tag may have changed
            self._arm(banner)

    def _target(self, item: Planned, banner: Banner, *, ack: bool | None = None) -> Target:
        who = item.who
        ack = self.ack_applies(banner) if ack is None else ack
        if who is None:
            return Target(item.recipient, ack_button=ack)
        return Target(who.key, who.kind, who.person, ack_button=ack)

    def ack_applies(self, banner: Banner) -> bool:
        """An escalation or reminder applies, so acknowledging is meaningful (the Acknowledge
        button of a push)."""
        return banner.source != SOURCE_SUMMARY and bool(self.policies.timed_for(banner))

    async def _deliver(
        self, banner: Banner, *, update: bool, resume: bool = False
    ) -> list[tuple[Planned, Outcome]]:
        planned = await self.plan(banner, waiting=not banner.active)
        return await self._send(banner, planned, update=update, resume=resume, origin="message")

    async def _send(
        self,
        banner: Banner,
        planned: list[Planned],
        *,
        update: bool = False,
        resume: bool = False,
        origin: str,
        resend: bool = False,
        caught: list[str] | None = None,
    ) -> list[tuple[Planned, Outcome]]:
        """Run planned deliveries through the precedence chain and the channels. `resend`: send
        again to a recipient who already has the message (escalations, D-235 O8). `caught`
        collects why a hold changed a delivery: held, dropped or sent quietly."""
        results: list[tuple[Planned, Outcome]] = []
        self._count_audiences(banner)
        # `resume` also means "skip what was sent" for escalations and fallbacks; only the
        # first delivery after a restart is silent about problems (D-126, D-128).
        startup = resume and origin == "message"
        for item in planned:
            row = self.ledger.rows.get((banner.id, item.channel, item.recipient))
            if (
                resume
                and row is not None
                and (row.hold or (row.state is State.SENT and not resend))
            ):
                continue  # sent or held before the restart: never send twice
            channel = self.channels.get(item.channel)
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                step = self.chain.run(
                    Step(banner, item.channel, self._target(item, banner), origin)
                )
                if isinstance(step, Skip):
                    outcome = Outcome(Result.SKIPPED, step.reason, by=step.policy or None)
                    if caught is not None and step.reason in ("quiet_hours", "presence"):
                        caught.append(step.reason)
                elif isinstance(step, Hold):
                    outcome = Outcome(
                        Result.HELD,
                        step.reason,
                        due=step.until,
                        hold=step.kind,
                        by=step.policy or None,
                    )
                    if caught is not None:
                        caught.append(step.reason)
                else:
                    if caught is not None and step.target.quiet:
                        caught.append("quiet_hours")
                    held_back = self._held_back(step.banner, item, step.target, update)
                    if held_back is not None:
                        outcome = Outcome(Result.SKIPPED, held_back)
                        if row is not None and row.state is State.SENT:
                            # The earlier delivery stays: a later clear still takes it back.
                            self._suppressed(banner.id, item, held_back)
                            results.append((item, outcome))
                            continue
                    else:
                        call = channel.update if update else channel.deliver
                        outcome = await call(step.banner, step.target)
                        if step.target.quiet_by:
                            outcome = replace(outcome, by=step.target.quiet_by)
                        self._sent(step.banner, item.channel, item.recipient, outcome)
            if (
                item.channel == "mail"
                and not startup
                and item.result is Result.SKIPPED
                and outcome.reason == "no_mail_address"
            ):
                channel.warn_missing(item.recipient)  # type: ignore[attr-defined]
            if item.channel == "speak" and not startup and outcome.reason in NO_SPEAKER:
                await warn_speech(self.hass, item.recipient, outcome.reason or "")
            self._record(
                banner.id,
                item.channel,
                item.recipient,
                outcome,
                item.who.person if item.who else None,
                origin,
            )
            results.append((item, outcome))
        if not startup:
            self._report(
                banner,
                origin,
                [(i.channel, i.recipient, i.who.person if i.who else None, o) for i, o in results],
            )
            self._mirror(banner, results)
        return results

    @property
    def mirror_severities(self) -> list[str]:
        return list(self._options.get(OPT_INBOX_MIRROR) or ())

    # The mirror: a copy of what other channels delivered, as history (D-275) -------------------

    def _mirror(self, banner: Banner, results: list[tuple[Planned, Outcome]]) -> None:
        """Keep a copy in the inbox of every person another channel just delivered to, when the
        message's severity is one the setting names. Policies already acted on the real
        channels; the copy records what was delivered."""
        if banner.severity not in (self._options.get(OPT_INBOX_MIRROR) or ()):
            return
        for person, channels in self._reached(banner, results).items():
            for channel in channels:
                self._mirror_one(banner, channel, person)

    def _reached(
        self, banner: Banner, results: list[tuple[Planned, Outcome]]
    ) -> dict[str, list[str]]:
        reached: dict[str, list[str]] = {}
        for item, outcome in results:
            if outcome.result is not Result.SENT:
                continue
            if item.channel in MIRROR_CHANNELS and item.who is not None and item.who.person:
                reached.setdefault(item.who.person, []).append(item.channel)
            elif item.channel == CHANNEL_BANNER:
                for person in self._banner_persons(banner):
                    reached.setdefault(person, []).append(CHANNEL_BANNER)
        return {p: list(dict.fromkeys(c)) for p, c in reached.items()}

    def _banner_persons(self, banner: Banner) -> list[str]:
        """Who sees a banner: the persons it names, or everyone who has a Home Assistant user."""
        if banner.people:
            return [p for p in banner.people if p.startswith("person.") and p != BANNER_NOBODY]
        return [
            s.entity_id for s in self.hass.states.async_all("person") if s.attributes.get("user_id")
        ]

    def _mirror_one(self, banner: Banner, channel: str, person: str) -> None:
        if banner.severity not in (self._options.get(OPT_INBOX_MIRROR) or ()):
            return
        profile = self.resolver.profile(person)
        if not profile.enabled or CHANNEL_INBOX not in profile.channels:
            return  # switched off, or a disabled recipient (D-147, D-273)
        self.inbox.upsert(
            person, banner.id, item_fields(banner), channel, dt_util.utcnow(), copy=True
        )

    def _report(
        self, banner: Banner, origin: str, rows: list[tuple[str, str, str | None, Outcome]]
    ) -> None:
        """Fire `heads_up_delivery_failed` once per channel that had a failed send or reached
        nobody in this step (D-128). Choices such as quiet hours and duplicates are not failures."""
        channels: dict[str, tuple[int, list[dict[str, str]]]] = {}
        for channel, recipient, person, outcome in rows:
            if channel == CHANNEL_BANNER:
                continue
            reached, failed = channels.setdefault(channel, (0, []))
            if outcome.result is Result.SENT:
                channels[channel] = (reached + 1, failed)
            elif outcome.result is Result.FAILED or (
                outcome.result is Result.SKIPPED and outcome.reason in NOBODY_REASONS
            ):
                entry = {"recipient": recipient, "reason": outcome.reason or "unknown"}
                if person:
                    entry["person"] = person
                failed.append(entry)
        for channel, (reached, failed) in channels.items():
            if failed:
                self.hass.bus.async_fire(
                    EVENT_DELIVERY_FAILED,
                    {
                        "id": banner.id,
                        "tag": banner.tag,
                        "channel": channel,
                        "origin": origin,
                        "reached": reached,
                        "failed": failed,
                    },
                )

    def _held_back(self, banner: Banner, item: Planned, target: Target, update: bool) -> str | None:
        """Why a delivery is suppressed: an identical update, or a push over its cap (D-123)."""
        if item.channel == CHANNEL_BANNER:
            return None
        if update and self.limiter.duplicate(banner, item.channel, item.recipient):
            return DUPLICATE
        # A progress bar has its own interval (D-263); the caps would drop updates, the last too.
        if (
            item.channel == "push"
            and banner.progress is None
            and not self.limiter.push_allowed(banner, target.key)
        ):
            return RATE_LIMITED
        return None

    def _sent(self, banner: Banner, channel: str, recipient: str, outcome: Outcome) -> None:
        if outcome.result is Result.SENT and channel != CHANNEL_BANNER:
            self.limiter.sent(banner, channel, recipient)

    def _suppressed(self, message_id: str, item: Planned, reason: str) -> None:
        self._trace(message_id, item.channel, item.recipient, "skipped", reason)
        self._log("skipped", message_id, f"{item.channel}|{reason}")

    async def _take_back(self, banner: Banner, user_id: str | None) -> None:
        """Clear what one user (or everyone) sees on the per-user channels, keeping the rows."""
        persons = set(self.resolver.persons_of_user(user_id)) if user_id else None
        for row in self.ledger.for_message(banner.id):
            if row.state is not State.SENT or row.person is None:
                continue
            if persons is not None and row.person not in persons:
                continue
            channel = self.channels.get(row.channel)
            outcome = await channel.clear(banner.id, Target(row.recipient, "", row.person), row.ref)
            self._trace(banner.id, row.channel, row.recipient, "cleared", outcome.reason)
            row.state = State.CLEARED
            self.ledger.put(row)

    async def _resend(self, banner: Banner, user_id: str | None) -> None:
        """A snooze ended: notify again the people it was cleared for (D-078)."""
        if not banner.active:
            return
        persons = set(self.resolver.persons_of_user(user_id)) if user_id else None
        for row in self.ledger.for_message(banner.id):
            if row.state is not State.CLEARED or row.person is None:
                continue
            if persons is not None and row.person not in persons:
                continue
            outcome = await self.channels.get(row.channel).deliver(
                banner, self._row_target(row, banner)
            )
            self._record(banner.id, row.channel, row.recipient, outcome, row.person)

    async def _end(self, banner: Banner) -> None:
        self._cancel_timers(banner.id)
        self._message_gone(banner.id)
        for row in self.ledger.for_message(banner.id):
            if row.state is State.SENT:
                target = Target(row.recipient, "", row.person)
                await self.channels.get(row.channel).clear(banner.id, target, row.ref)
            self._trace(banner.id, row.channel, row.recipient, "cleared", None)
        self.ledger.drop_message(banner.id)
        self.limiter.forget(banner.id)

    # Policies: escalation and reminder timers --------------------------------------------

    def _row_target(self, row: Delivery, banner: Banner) -> Target:
        kind = "device" if row.recipient.startswith("device:") else ""
        return Target(row.recipient, kind, row.person, ack_button=self.ack_applies(banner))

    def policy_problem(self, policy: Policy) -> str | None:
        """Why a policy cannot run now, as a stable reason code (D-111). Home Assistant cannot
        stop a user from deleting an audience or group a policy names, so this is checked when
        the policy fires and reported instead."""
        for target in policy.targets.values():
            audience = target.get("audience")
            if audience is not None and self.resolver.audience(audience) is None:
                return "audience_missing"
            for name in target.get("recipients", []):
                if self.resolver.is_group_ref(name) and self.resolver.group(name) is None:
                    return "group_missing"
        return None

    def record(self, kind: str, detail: str) -> None:
        """A line in the log and the trace that belongs to no message."""
        self._log(kind, "", detail)
        self._trace("", "", "", kind, detail)

    def rename_entity(self, old: str, new: str) -> int:
        """An entity ID changed: the ledger and held messages follow (D-201)."""
        changed = self.ledger.rename_entity(old, new) + self.inbox.rename_person(old, new)
        for kept in self.ledger.held.values():
            moved = kept.rename_entity(old, new)
            changed += moved
            if moved:
                self.ledger.put_held(kept)
        return changed

    def sync_identity(self, subentries: Mapping[str, ConfigSubentry]) -> None:
        self.identity = maps_for(self.hass, subentries.values())

    def _arm(self, banner: Banner) -> None:
        """Start the timers of the escalations and reminders that apply, once per message."""
        if (
            self._closed
            or not banner.active
            or banner.acknowledged_by
            or banner.source == SOURCE_SUMMARY  # a summary has no escalation or reminder
            or self.is_held(banner.id)
        ):
            return
        now = dt_util.utcnow()
        for policy in self.policies.timed_for(banner):
            row = self.ledger.rows.get((banner.id, TIMER_CHANNEL, policy.key))
            if row is None:
                due = (
                    escalation.due(policy, now)
                    if policy.type == "escalation"
                    else now + timedelta(minutes=self.policies.every_minutes(policy))
                )
                row = Delivery(banner.id, TIMER_CHANNEL, policy.key, State.PLANNED, now, due=due)
                self.ledger.put(row)
            if row.state is State.PLANNED and (banner.id, policy.key) not in self._timers:
                self._schedule(row)

    def _drop_inapplicable_timers(self, banner: Banner) -> None:
        applicable = {p.key for p in self.policies.timed_for(banner)}
        for row in self.ledger.timers(banner.id):
            if row.state is State.PLANNED and row.recipient not in applicable:
                if cancel := self._timers.pop((banner.id, row.recipient), None):
                    cancel()
                self._finish(row, State.CLEARED, "no_longer_applies")

    def _schedule(self, row: Delivery) -> None:
        key = (row.message_id, row.recipient)
        if cancel := self._timers.pop(key, None):
            cancel()
        # HA_API_NOTES N-7: a time in the past runs at once, which is how an overdue step fires
        # once after a restart (D-081).
        self._timers[key] = async_track_point_in_utc_time(
            self.hass,
            partial(self._timer_due, row.message_id, row.recipient),
            row.due or dt_util.utcnow(),
        )

    @callback
    def _timer_due(self, message_id: str, key: str, _now: datetime) -> None:
        self._timers.pop((message_id, key), None)
        if self._closed:
            return
        self._enqueue(message_id, lambda: self._run_timer(message_id, key), f"heads_up timer {key}")

    def _restore_timers(self) -> None:
        for row in self.ledger.timers():
            if row.state is State.PLANNED:
                self._schedule(row)
        for held in [r for r in self.ledger.rows.values() if r.state is State.HELD and r.hold]:
            self._schedule_held(held.message_id, held.channel, held.recipient)
        # Held by an entity that may have turned off while stopped: try again; still quiet holds
        # it again.
        self._release_quiet(lambda row: row.due is None, "heads_up quiet restart")

    def _quiet_entities(self) -> set[str]:
        return {
            p.quiet_entity
            for p in self.policies.all()
            if p.type == "quiet_hours" and p.quiet_entity and p.enabled
        }

    @callback
    def _is_quiet_entity(self, data: Any) -> bool:  # HA requires a callback as an event filter
        return str(data["entity_id"]) in self._quiet_entities()

    @callback
    def _on_quiet_entity(self, event: Event[Any]) -> None:
        new, old = event.data["new_state"], event.data["old_state"]
        if self._closed or old is None or old.state != "on":
            return
        if new is not None and new.state == "on":
            return
        self._release_quiet(lambda row: True, f"heads_up quiet end {event.data['entity_id']}")

    def _release_quiet(self, wanted: Any, name: str) -> None:
        """Send the deliveries quiet hours hold again through the chain: those no quiet policy
        holds any more go out, the others are held again."""
        for row in list(self.ledger.rows.values()):
            if row.state is State.HELD and row.hold == HOLD_QUIET and wanted(row):
                self._enqueue(
                    row.message_id,
                    partial(self._release, row.message_id, row.channel, row.recipient),
                    name,
                )

    def _condition_entities(self) -> set[str]:
        found: set[str] = set()
        for condition in self.policies.watched():
            found |= only_if.entities(self.hass, condition)
        return found

    @callback
    def _is_condition_entity(self, data: Any) -> bool:  # HA requires a callback as a filter
        return str(data["entity_id"]) in self._condition_entities()

    @callback
    def _on_condition_entity(self, event: Event[Any]) -> None:
        if not self._closed:
            self.conditions_changed()

    def _plan_condition_waits(self) -> None:
        """A condition with "for at least" turns true later without a state change: check
        again then (HA_API_NOTES N-7)."""
        for cancel in self._condition_waits:
            cancel()
        self._condition_waits.clear()
        now = dt_util.utcnow()
        for condition in self.policies.watched():
            if (due := only_if.due_after_wait(self.hass, condition)) is not None and due > now:
                self._condition_waits.append(
                    async_track_point_in_utc_time(
                        self.hass, lambda _now: self.conditions_changed(), due
                    )
                )

    def conditions_changed(self) -> None:
        """An Only if or Faster while may have changed (D-216): summaries and holds of
        policies that no longer apply let go, a band entry that now fits releases what it
        covers, Presence holds go through the chain again, and timers are planned again."""
        self.on_policies_changed()
        self._release_quiet(lambda row: True, "heads_up condition changed")
        for row in list(self.ledger.rows.values()):
            if row.state is State.HELD and row.hold == HOLD_AWAY:
                self._enqueue(
                    row.message_id,
                    partial(self._release, row.message_id, row.channel, row.recipient),
                    "heads_up condition changed",
                )
        now = dt_util.utcnow()
        for row in self.ledger.timers():
            if row.state is not State.PLANNED or row.message_id.startswith(SUMMARY_PREFIX):
                continue
            policy = self.policies.by_key(row.recipient)
            if policy is None:
                continue
            if policy.type == "reminder":
                # Faster while: the next repeat follows the rhythm in force now.
                banner = self.lookup(row.message_id)
                if banner is None:
                    continue
                start = row.updated_at if row.count else banner.created_at
                due = start + timedelta(minutes=self.policies.every_minutes(policy))
                row.due = max(due, now)
                self.ledger.put(row)
                self._schedule(row)
            elif (
                row.due is not None
                and row.due <= now
                and (row.message_id, row.recipient) not in self._timers
            ):
                self._schedule(row)  # an escalation that waited for its Only if
        self._plan_condition_waits()

    def _cancel_timer_callbacks(self, message_id: str) -> None:
        for key in [k for k in self._timers if k[0] == message_id]:
            self._timers.pop(key)()

    def _cancel_all_timers(self) -> None:
        for cancel in self._timers.values():
            cancel()
        self._timers.clear()

    def _cancel_timers(self, message_id: str) -> None:
        """The message is gone: forget its timers."""
        self._cancel_timer_callbacks(message_id)
        self.ledger.drop_timers(message_id)

    def _stop_timers(self, message_id: str, reason: str, *, only: Policy | None = None) -> None:
        for row in self.ledger.timers(message_id):
            if row.state is not State.PLANNED or (only is not None and row.recipient != only.key):
                continue
            if cancel := self._timers.pop((message_id, row.recipient), None):
                cancel()
            self._finish(row, State.CLEARED, reason)

    def _restart_timers(self, banner: Banner) -> None:
        """The severity changed: the policies of the new severity start from now (D-081)."""
        self._cancel_timers(banner.id)
        self._trace(banner.id, TIMER_CHANNEL, "", "restarted", "severity_changed")
        self._arm(banner)

    def _dismissed(self, banner: Banner) -> None:
        for row in self.ledger.timers(banner.id):
            policy = self.policies.by_key(row.recipient)
            if row.state is State.PLANNED and policy is not None and policy.dismiss_acks:
                self._stop_timers(banner.id, "dismissed_counts_as_acknowledged", only=policy)

    def _finish(self, row: Delivery, state: State, reason: str) -> None:
        row.state = state
        row.updated_at = dt_util.utcnow()
        self.ledger.put(row)
        self._trace(row.message_id, TIMER_CHANNEL, row.recipient, state.value, reason)

    async def _run_timer(self, message_id: str, key: str) -> None:
        if message_id.startswith(SUMMARY_PREFIX):
            await self._run_summary(key)
            return
        if key.startswith("held:"):
            await self._run_held(message_id, key)
            return
        row = self.ledger.rows.get((message_id, TIMER_CHANNEL, key))
        if row is None or row.state is not State.PLANNED:
            return
        banner = self.lookup(message_id)
        policy = self.policies.by_key(key)
        if banner is None or not banner.active or banner.acknowledged_by:
            self._finish(row, State.CLEARED, "no_longer_needed")
        elif policy is None:
            self._finish(row, State.CLEARED, "policy_deleted")
        elif not policy.enabled:
            self._finish(row, State.CLEARED, "policy_disabled")
        elif not self.policies.only_if_ok(policy):
            # A false Only if skips this firing only (D-216). An escalation waits for the
            # condition (a change of it schedules the row again); a reminder tries again
            # after its rhythm.
            self._trace(message_id, TIMER_CHANNEL, key, "skipped", "only_if")
            if policy.type == "reminder":
                row.due = dt_util.utcnow() + timedelta(minutes=self.policies.every_minutes(policy))
                self.ledger.put(row)
                self._schedule(row)
        elif policy.type == "escalation":
            await self._escalate(banner, policy, row)
        else:
            await self._remind(banner, policy, row)

    async def _escalate(self, banner: Banner, policy: Policy, row: Delivery) -> None:
        if (problem := self.policy_problem(policy)) is not None:
            self._finish(row, State.SKIPPED, problem)  # D-111: reported, never silent
            return
        message = escalation.message_for(banner, policy)
        # An escalation always does something visible: it sends again to whoever already has
        # the message (D-235 O8). A hold that catches it, or reaching nobody, is a setup mistake
        # shown under Needs attention (O3, O4); no Fallback steps in.
        caught: list[str] = []
        results = await self._send(
            message,
            await self.plan(message),
            resume=True,
            origin="escalation",
            resend=True,
            caught=caught,
        )
        self._finish(row, State.SENT, "escalated")
        self._log("escalation_sent", banner.id, policy.name)
        if caught:
            self._log("escalation_held", banner.id, f"{policy.name}|{caught[0]}")
        if not any(o.result is Result.SENT for i, o in results if i.channel != CHANNEL_BANNER):
            self._log("escalation_unreached", banner.id, policy.name)

    def _repeat_delay(self, banner: Banner, policy: Policy) -> datetime | None:
        """One repeat rhythm per channel (D-234, DESIGN §25.3 rule 2): a reminder that runs
        alongside keeps its own. Otherwise a reminder waits while another fitting reminder on
        a shared channel has a shorter rhythm now, and repeats no sooner than its own rhythm
        after the last repeat on those channels. Returns when to try again, or None to repeat."""
        if policy.alongside:
            return None
        now = dt_util.utcnow()
        every = timedelta(minutes=self.policies.every_minutes(policy))
        mine = set(policy.channels)

        def sharing(candidates: list[Policy]) -> list[Policy]:
            return [
                o
                for o in candidates
                if o.type == "reminder"
                and o.key != policy.key
                and not o.alongside
                and not (mine and o.channels and not mine & set(o.channels))
            ]

        # Competitors are the reminders that act now; the last repeat counts whoever made it,
        # also a reminder whose Only if has turned false since.
        others = sharing(self.policies.for_message(banner))
        sharers = sharing(self.policies.for_message(banner, only_if=False))
        rows = {r.recipient: r for r in self.ledger.timers(banner.id)}
        for other in others:
            other_row = rows.get(other.key)
            if other_row is None or other_row.state is not State.PLANNED:
                continue  # finished or not planned: it does not set the rhythm
            other_every = self.policies.every_minutes(other)
            shorter = other_every < self.policies.every_minutes(policy)
            # Same rhythm: the reminder created first counts (subentry IDs sort by time).
            tie = other_every == self.policies.every_minutes(policy) and other.key < policy.key
            if shorter or tie:
                return now + every
        repeated = [
            rows[k].updated_at
            for k in [policy.key, *(o.key for o in sharers)]
            if k in rows and rows[k].count > 0
        ]
        if repeated and (last := max(repeated)) + every > now + timedelta(seconds=1):
            return last + every
        return None

    async def _remind(self, banner: Banner, policy: Policy, row: Delivery) -> None:
        # Cleared rows (dismissed or snoozed) are left out: a snooze pauses the person's
        # reminders and the notification after it brings them back (D-078).
        sent = [
            r
            for r in self.ledger.for_message(banner.id)
            if r.state is State.SENT
            and r.channel != CHANNEL_BANNER
            and (not policy.channels or r.channel in policy.channels)
        ]
        if not sent:
            self._finish(row, State.CLEARED, "nobody_left")
            return
        if (later := self._repeat_delay(banner, policy)) is not None:
            row.due = later
            self.ledger.put(row)
            self._schedule(row)
            return
        report: list[tuple[str, str, str | None, Outcome]] = []
        for target_row in sent:
            step = self.chain.run(
                Step(banner, target_row.channel, self._row_target(target_row, banner), "reminder")
            )
            if isinstance(step, Skip | Hold):  # a reminder is never held, only skipped
                reason = step.reason
                self._trace(
                    banner.id,
                    target_row.channel,
                    target_row.recipient,
                    "skipped",
                    reason,
                    step.policy or None,
                    "reminder",
                    target_row.person,
                )
                continue
            if target_row.channel == "push" and not self.limiter.push_allowed(
                step.banner, step.target.key
            ):
                self._trace(
                    banner.id,
                    "push",
                    target_row.recipient,
                    "skipped",
                    RATE_LIMITED,
                    None,
                    "reminder",
                    target_row.person,
                )
                limited = Outcome(Result.SKIPPED, RATE_LIMITED)
                report.append(("push", target_row.recipient, target_row.person, limited))
                continue
            outcome = await self.channels.get(target_row.channel).deliver(step.banner, step.target)
            report.append((target_row.channel, target_row.recipient, target_row.person, outcome))
            self._trace(
                banner.id,
                target_row.channel,
                target_row.recipient,
                outcome.result.value,
                outcome.reason,
                None,
                "reminder",
                target_row.person,
            )
        self._report(banner, "reminder", report)
        self._log("reminder_sent", banner.id, policy.name)
        row.count += 1
        row.updated_at = dt_util.utcnow()  # the last repeat: other reminders keep the rhythm
        if reminder.finished(policy, row.count):
            self._finish(row, State.SENT, "reminders_done")
            return
        row.due = row.updated_at + timedelta(minutes=self.policies.every_minutes(policy))
        self.ledger.put(row)
        self._schedule(row)

    # Held deliveries: quiet hours and away ------------------------------------------------

    @staticmethod
    def _held_key(channel: str, recipient: str) -> str:
        return f"held:{channel}:{recipient}"

    def _schedule_held(self, message_id: str, channel: str, recipient: str) -> None:
        key = (message_id, self._held_key(channel, recipient))
        if cancel := self._timers.pop(key, None):
            cancel()
        row = self.ledger.rows.get((message_id, channel, recipient))
        if row is None or row.due is None:
            return  # an away delivery without a deadline waits for the arrival only
        self._timers[key] = async_track_point_in_utc_time(
            self.hass, partial(self._timer_due, message_id, key[1]), row.due
        )

    @callback
    def _is_presence_source(self, data: Any) -> bool:  # HA requires a callback as a filter
        return bool(self.resolver.location_persons(str(data["entity_id"])))

    @callback
    def _on_state_change(self, event: Event[Any]) -> None:
        """A change of where someone is: what Presence holds for that person, and what it holds
        for the household (speech), goes through the chain again after the presence delay; those
        it no longer holds go out (D-212). A zone may come from an entity of the profile (D-229)."""
        if self._closed:
            return
        new, old = event.data["new_state"], event.data["old_state"]
        if (
            new is not None
            and old is not None
            and new.state == old.state
            and new.attributes.get("in_zones") == old.attributes.get("in_zones")
        ):
            return  # only other attributes changed
        for person in self.resolver.location_persons(str(event.data["entity_id"])):
            delay = int(self._options.get(OPT_PRESENCE_DEBOUNCE, 60))
            if cancel := self._presence_waits.pop(person, None):
                cancel()
            if delay <= 0:
                self._release_away(person)
                continue

            @callback
            def settled(_now: Any, person: str = person) -> None:
                self._presence_waits.pop(person, None)
                if not self._closed:
                    self._release_away(person)

            self._presence_waits[person] = async_call_later(self.hass, delay, settled)

    def _release_away(self, person: str) -> None:
        for row in list(self.ledger.rows.values()):
            if (
                row.state is State.HELD
                and row.hold == HOLD_AWAY
                and row.person in (person, None, "")
            ):
                self._enqueue(
                    row.message_id,
                    partial(self._release, row.message_id, row.channel, row.recipient),
                    f"heads_up arrival {row.person}",
                )

    async def _run_held(self, message_id: str, key: str) -> None:
        _, channel, recipient = key.split(":", 2)
        row = self.ledger.rows.get((message_id, channel, recipient))
        if row is None or row.state is not State.HELD or not row.hold:
            return
        if row.hold == HOLD_AWAY:  # the timer of a Presence hold is its deadline
            banner = self.lookup(message_id)
            send = banner is not None and any(
                p.type == "presence" and p.after_wait == "send"
                for p in self.policies.for_message(banner)
            )
            if not send:
                self._end_held(row, State.SKIPPED, "max_wait_exceeded")
                return
            await self._release(message_id, channel, recipient, skip_presence=True)
        else:
            await self._release(message_id, channel, recipient)

    def _end_held(self, row: Delivery, state: State, reason: str) -> None:
        if cancel := self._timers.pop(
            (row.message_id, self._held_key(row.channel, row.recipient)), None
        ):
            cancel()
        row.state = state
        row.hold = None
        row.updated_at = dt_util.utcnow()
        self.ledger.put(row)
        self._trace(row.message_id, row.channel, row.recipient, state.value, reason)

    async def _release(
        self, message_id: str, channel: str, recipient: str, skip_presence: bool = False
    ) -> None:
        """Send a held delivery now, if the message still needs it. `skip_presence`: the wait of
        a Presence hold ended with "send anyway"."""
        row = self.ledger.rows.get((message_id, channel, recipient))
        if row is None or row.state is not State.HELD or not row.hold:
            return
        deadline = row.due if row.hold == HOLD_AWAY else None
        banner = self.lookup(message_id)
        user = self.resolver.user_of_person(row.person) if row.person else None
        if banner is None or not banner.active or banner.acknowledged_by:
            self._end_held(row, State.SKIPPED, "no_longer_needed")
        elif user and (user in banner.dismissed_by or GLOBAL_SNOOZE_KEY in banner.dismissed_by):
            self._end_held(row, State.SKIPPED, "dismissed")
        elif user and banner.snoozed_for(user):
            self._end_held(row, State.SKIPPED, "snoozed")
        else:
            self._end_held(row, State.PLANNED, "released")
            target = self._row_target(row, banner)
            skip = ("presence",) if skip_presence else ()
            step = self.chain.run(Step(banner, channel, target, "message"), skip=skip)
            if isinstance(step, Skip):
                outcome = Outcome(Result.SKIPPED, step.reason, by=step.policy or None)
            elif isinstance(step, Hold):
                # Held again by Presence: the first deadline stays, a new one would never end.
                until = deadline if step.kind == HOLD_AWAY and deadline else step.until
                outcome = Outcome(
                    Result.HELD, step.reason, due=until, hold=step.kind, by=step.policy or None
                )
            elif channel == "push" and not self.limiter.push_allowed(step.banner, step.target.key):
                outcome = Outcome(Result.SKIPPED, RATE_LIMITED)
            else:
                outcome = await self.channels.get(channel).deliver(step.banner, step.target)
                if outcome.result is Result.SENT and row.person and channel in MIRROR_CHANNELS:
                    self._mirror_one(banner, channel, row.person)  # a held delivery, now sent
            self._record(message_id, channel, recipient, outcome, row.person, "released")

    # Fallback ---------------------------------------------------------------------------

    @staticmethod
    def _channels_matching(when: str, by_channel: dict[str, set[str]]) -> set[str]:
        """The channels that reached nobody for the reason a Fallback policy waits for."""
        return {c for c, classes in by_channel.items() if fallback.matches(when, classes)}

    @staticmethod
    def _unreached(results: list[tuple[Planned, Outcome]]) -> dict[str, set[str]]:
        """Why a requested channel reached nobody: `no_audience` or `failed`, per channel."""
        classes: dict[str, set[str]] = {}
        channels = {item.channel for item, _ in results if item.channel != CHANNEL_BANNER}
        for channel in channels:
            mine = [(i, o) for i, o in results if i.channel == channel]
            if any(o.result in (Result.SENT, Result.HELD) for _, o in mine):
                continue
            for _, outcome in mine:
                reason = outcome.reason
                if reason in fallback.IGNORED_REASONS:
                    continue
                failed = outcome.result is Result.FAILED or reason in fallback.DEVICE_REASONS
                classes.setdefault(channel, set()).add("failed" if failed else "no_audience")
        return classes

    async def _apply_deliver(self, banner: Banner) -> list[tuple[Planned, Outcome]]:
        """Deliver policies add channels and targets to the first delivery (D-121). Once per
        message; a recipient that already has the message on that channel is left out."""
        results: list[tuple[Planned, Outcome]] = []
        if banner.source == SOURCE_SUMMARY or self.is_held(banner.id):
            return results
        for policy in self.policies.for_message(banner):
            if (
                policy.type != "deliver"
                or (banner.id, TIMER_CHANNEL, policy.key) in self.ledger.rows
            ):
                continue
            marker = Delivery(banner.id, TIMER_CHANNEL, policy.key, State.SENT, dt_util.utcnow())
            self.ledger.put(marker)
            if (problem := self.policy_problem(policy)) is not None:
                self._finish(marker, State.SKIPPED, problem)
                continue
            message = escalation.message_for(banner, policy)
            results += await self._send(
                message, await self.plan(message), resume=True, origin="deliver"
            )
            self._log("deliver_sent", banner.id, policy.name)
        return results

    async def _update_deliver(self, banner: Banner, own: set[tuple[str, str]]) -> None:
        """An update replaces what a Deliver policy sent, like it replaces the call's own."""
        for policy in self.policies.for_message(banner):
            row = self.ledger.rows.get((banner.id, TIMER_CHANNEL, policy.key))
            if policy.type != "deliver" or row is None or row.state is not State.SENT:
                continue
            message = escalation.message_for(banner, policy)
            planned = [
                item
                for item in await self.plan(message)
                if (item.channel, item.recipient) not in own
                and (r := self.ledger.rows.get((banner.id, item.channel, item.recipient)))
                and r.state is State.SENT
            ]
            await self._send(message, planned, update=True, origin="deliver")

    async def _fallback(self, banner: Banner, results: list[tuple[Planned, Outcome]]) -> None:
        """After the first delivery: other channels and targets when it reached nobody (D-079).
        It fires once per message and a fallback never triggers another."""
        by_channel = self._unreached(results)
        classes = set().union(*by_channel.values()) if by_channel else set()
        for policy in self.policies.for_message(banner):
            if policy.type != "fallback" or not fallback.matches(policy.when, classes):
                continue
            if (banner.id, TIMER_CHANNEL, policy.key) in self.ledger.rows:
                continue
            now = dt_util.utcnow()
            marker = Delivery(banner.id, TIMER_CHANNEL, policy.key, State.SENT, now)
            self.ledger.put(marker)
            if (problem := self.policy_problem(policy)) is not None:
                self._finish(marker, State.SKIPPED, problem)
                continue
            self._trace(banner.id, TIMER_CHANNEL, policy.key, "fallback", "+".join(sorted(classes)))
            message = escalation.message_for(
                banner, policy, self._channels_matching(policy.when, by_channel)
            )
            await self._send(message, await self.plan(message), resume=True, origin="fallback")
            self._log("fallback_sent", banner.id, policy.name)

    # Summarize: hold, then one summary per recipient and channel (D-105, D-113) ---------------

    def is_held(self, message_id: str) -> bool:
        held = self.ledger.held.get(message_id)
        return held is not None and not held.resolved

    def _summary_policy(self, banner: Banner) -> Policy | None:
        if banner.source == SOURCE_SUMMARY:
            return None  # a summary is never held itself
        passes = self.policies.passes(banner)
        found = [
            p
            for p in self.policies.for_message(banner)
            if p.type == "summarize" and summarize.holds(p, passes)
        ]
        # Two summaries fit: the one due next collects the message, never both (D-235, O5).
        return min(found, key=lambda p: (self._summary_due(p), p.name)) if found else None

    def _summary_due(self, policy: Policy) -> datetime:
        row = self.ledger.rows.get((SUMMARY_PREFIX + policy.key, TIMER_CHANNEL, policy.key))
        if row is not None and row.state is State.PLANNED and row.due is not None:
            return row.due
        return summarize.next_due(policy, dt_util.utcnow())

    def _try_hold(self, banner: Banner) -> None:
        """Hold a message that appears while a Summarize policy applies. Decided once, when the
        message first appears; a message already delivered is not taken back."""
        if self.is_held(banner.id) or self.ledger.for_message(banner.id):
            return
        if (policy := self._summary_policy(banner)) is None:
            return
        self.ledger.put_held(HeldMessage.from_banner(banner, policy.key, dt_util.utcnow()))
        self._trace(banner.id, "", "", "held", "summarize", policy.name)
        self._arm_summary(policy)

    def _update_held(self, banner: Banner) -> None:
        held = self.ledger.held.get(banner.id)
        if held is None or held.resolved:
            return
        policy = self.policies.by_key(held.policy)
        if (
            policy is None
            or not policy.enabled
            or not summarize.holds(policy, self.policies.passes(banner))
        ):
            # For example a message that became critical: it must not stay hidden.
            self.ledger.drop_held(banner.id)
            self._released.add(banner.id)
            return
        changed = (held.message, held.title, held.severity) != (
            banner.message,
            banner.title,
            banner.severity,
        )
        held.message, held.title, held.severity = banner.message, banner.title, banner.severity
        held.channels, held.targets = list(banner.channels), dict(banner.targets)
        held.people = list(banner.people)
        if changed:
            held.summarized = False  # listed again in the next summary
            self._arm_summary(policy)
        self.ledger.put_held(held)

    def _message_gone(self, message_id: str) -> None:
        """A held message was removed: its summary lists it once more, marked resolved."""
        held = self.ledger.held.get(message_id)
        if held is None:
            return
        if held.summarized:
            self.ledger.drop_held(message_id)
        else:
            held.resolved = True
            self.ledger.put_held(held)

    def on_policies_changed(self) -> None:
        """A policy was added, changed, deleted or switched: the messages a summary holds become
        normal when their policy is gone or off, or when a band entry now fits them (D-235 O2).
        Deliveries quiet hours hold go through the chain again, so a band entry that now covers
        their recipient releases them."""
        for held in list(self.ledger.held.values()):
            policy = self.policies.by_key(held.policy)
            if held.resolved:
                continue
            if policy is not None and policy.enabled:
                banner = self.lookup(held.message_id)
                if banner is None or policy.holds_anyway or not self.policies.passes(banner):
                    continue
            self.ledger.drop_held(held.message_id)
            self._released.add(held.message_id)
            banner = self.lookup(held.message_id)
            if banner is not None:
                self._enqueue(
                    banner.id,
                    partial(self._release_held, banner.id),
                    f"heads_up release {banner.id}",
                )
        if any(p.type == "get_through" and p.enabled for p in self.policies.all()):
            self._release_quiet(lambda row: True, "heads_up band changed")
        self.visibility_changed()

    async def _release_held(self, message_id: str) -> None:
        banner = self.lookup(message_id)
        self._released.discard(message_id)
        if banner is None:
            return
        # Released from a summary, the message runs as a new one: Deliver and Fallback act, and
        # its clocks start now (D-235 O2).
        results = await self._deliver(banner, update=False)
        if banner.active:
            delivered = await self._apply_deliver(banner)
            if not any(
                o.result in (Result.SENT, Result.HELD)
                for i, o in delivered
                if i.channel != CHANNEL_BANNER
            ):
                await self._fallback(banner, results)
        self._arm(banner)

    def _arm_summary(self, policy: Policy) -> None:
        """One timer per policy, started by the first message held after the last summary."""
        message_id = SUMMARY_PREFIX + policy.key
        row = self.ledger.rows.get((message_id, TIMER_CHANNEL, policy.key))
        if row is not None and row.state is State.PLANNED:
            return
        now = dt_util.utcnow()
        row = Delivery(
            message_id,
            TIMER_CHANNEL,
            policy.key,
            State.PLANNED,
            now,
            due=summarize.next_due(policy, now),
        )
        self.ledger.put(row)
        self._schedule(row)

    async def _run_summary(self, key: str) -> None:
        row = self.ledger.rows.get((SUMMARY_PREFIX + key, TIMER_CHANNEL, key))
        if row is None or row.state is not State.PLANNED:
            return
        policy = self.policies.by_key(key)
        entries = [h for h in self.ledger.held.values() if h.policy == key and not h.summarized]
        # Finished first: a message held while the summary is sent starts the next timer.
        self._finish(
            row,
            State.SENT if entries else State.CLEARED,
            "summarized" if entries else "nothing_held",
        )
        if policy is None or not policy.enabled or not entries:
            return
        await self._send_summaries(entries)

    async def _send_summaries(self, entries: list[HeldMessage]) -> None:
        groups: dict[tuple[str, str], list[HeldMessage]] = {}
        for entry in entries:
            held = entry.as_banner()
            planned = await self.plan(held)
            # Deliver's recipients get the summary too (D-235 O1).
            for policy in self.policies.for_message(held):
                if policy.type == "deliver" and self.policy_problem(policy) is None:
                    planned += await self.plan(escalation.message_for(held, policy))
            for item in planned:
                if item.result is not Result.SENT:
                    continue
                who = item.who.person if item.who and item.who.person else item.recipient
                group = groups.setdefault(
                    (item.channel, "" if item.channel == CHANNEL_BANNER else who), []
                )
                if entry not in group:
                    group.append(entry)
        language = self.hass.config.language
        for (channel, recipient), members in groups.items():
            title, text, severity = summarize.build(members, language)
            data: dict[str, Any] = {
                "id": f"hu_sum_{secrets.token_hex(5)}",
                "title": title,
                "message": text,
                "severity": severity,
                "channels": [channel],
                "timeout": timedelta(hours=SUMMARY_LIFETIME_HOURS),
                "dismissible": True,
                "source": SOURCE_SUMMARY,
            }
            if channel == CHANNEL_BANNER:
                data["people"] = (
                    []
                    if any(not m.people for m in members)
                    else sorted({p for m in members for p in m.people})
                )
            elif recipient:
                data["targets"] = {channel: {"recipients": [recipient.removeprefix("device:")]}}
            result = self.create_message(data)
            summary_id = str(result.get("id", data["id"]))
            self._trace(summary_id, channel, recipient, "summary", f"{len(members)}")
            self._log("summary_sent", summary_id, f"{channel}|{len(members)}")
            for member in members:
                held_by = self.policies.by_key(member.policy)
                self._trace(
                    member.message_id,
                    channel,
                    recipient,
                    "summarized",
                    str(len(members)),
                    held_by.name if held_by else None,
                    "summary",
                )
        for entry in entries:
            if entry.resolved:
                self.ledger.drop_held(entry.message_id)
            else:
                entry.summarized = True
                self.stats.policy_action(dt_util.utcnow(), entry.policy, "summarized")
                self.ledger.put_held(entry)

    async def send_once(self, message: Banner) -> list[Planned]:
        """Deliver a message that has no record (shortcuts without an id)."""
        planned = await self.plan(message)
        for item in planned:
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                outcome = await self.channels.get(item.channel).deliver(
                    message,
                    self._target(item, message, ack=False),  # no record to acknowledge
                )
            self._trace(
                message.id, item.channel, item.recipient, outcome.result.value, outcome.reason
            )
        return planned

    def note(self, message_id: str, channel: str, recipient: str, result: str, reason: str) -> None:
        """A trace entry for something that is not a delivery (a press, for example)."""
        self._trace(message_id, channel, recipient, result, reason)

    def _record(
        self,
        message_id: str,
        channel: str,
        recipient: str,
        outcome: Outcome,
        person: str | None = None,
        origin: str | None = None,
    ) -> None:
        state = State(outcome.result.value)
        self.ledger.put(
            Delivery(
                message_id,
                channel,
                recipient,
                state,
                dt_util.utcnow(),
                due=outcome.due,
                ref=outcome.ref,
                person=person,
                hold=outcome.hold,
            )
        )
        self._trace(
            message_id,
            channel,
            recipient,
            outcome.result.value,
            outcome.reason,
            outcome.by,
            origin,
            person,
        )
        by = self.policies.by_name(outcome.by) if outcome.by else None
        self.stats.delivery(
            dt_util.utcnow(),
            channel,
            outcome.result.value,
            outcome.reason,
            by.key if by else None,
            person,
        )
        if (
            outcome.result in (Result.SKIPPED, Result.FAILED)
            and outcome.reason not in fallback.UNLOGGED_REASONS
        ):
            self._log(outcome.result.value, message_id, f"{channel}|{outcome.reason}")
        if outcome.hold:
            self._schedule_held(message_id, channel, recipient)

    def _trace(
        self,
        message_id: str,
        channel: str,
        recipient: str,
        result: str,
        reason: str | None,
        by: str | None = None,
        origin: str | None = None,
        person: str | None = None,
    ) -> None:
        self.trace.add(
            TraceEntry(
                dt_util.utcnow().isoformat(),
                message_id,
                channel,
                recipient or None,
                result,
                reason,
                by,
                origin,
                person,
            )
        )
        self._trace_store.async_delay_save(self._trace_data, SAVE_DELAY)

    def _trace_data(self) -> dict[str, Any]:
        return {"entries": self.trace.dump()}
