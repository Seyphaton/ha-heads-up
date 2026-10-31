"""Delivery engine: turns transitions into deliveries (DESIGN §23.11).

Work runs in background tasks, serialized per message and bounded overall. `plan` is the dry run
that the action response and the panel's Test send both use, so what is reported is what is done.
"""

from __future__ import annotations

import asyncio
import logging
import secrets
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from ..const import (
    CHANNEL_BANNER,
    DEFAULT_OPTIONS,
    GLOBAL_SNOOZE_KEY,
    GROUP_SUFFIX,
    HOLD_AWAY,
    OPT_TRACE_ENTRIES,
    SOURCE_SUMMARY,
    SUMMARY_LIFETIME_HOURS,
    SUMMARY_PREFIX,
    TARGET_CHANNELS,
    TIMER_CHANNEL,
)
from ..models import Banner
from .channels import ChannelRegistry, Outcome, Result, Target
from .interfaces import AudienceResolver, RecipientResolver
from .ledger import Delivery, DeliveryLedger, HeldMessage, State
from .policies import PolicyBook, escalation, fallback, reminder, summarize
from .policies.away import AwayStage
from .policies.chain import Chain, Hold, Skip, Step
from .policies.models import Policy
from .policies.quiet import QuietHoursStage
from .resolver import HubResolver, Recipient
from .trace import TraceBuffer, TraceEntry
from .transitions import BannerTransition, Kind, Reason

_LOGGER = logging.getLogger(__name__)
MAX_CONCURRENT = 8

type TaskFactory = Callable[[Coroutine[Any, Any, None], str], asyncio.Task[None]]


@dataclass(frozen=True, slots=True)
class Planned:
    """One delivery a message would produce."""

    channel: str
    recipient: str  # "" for channels without recipients
    result: Result
    reason: str | None = None
    who: Recipient | None = None  # what the resolver knows about the recipient


class HubEngine:
    def __init__(
        self, hass: HomeAssistant, options: dict[str, Any], create_task: TaskFactory
    ) -> None:
        self.hass = hass
        self.channels = ChannelRegistry()
        self.ledger = DeliveryLedger(hass)
        self.trace = TraceBuffer(options.get(OPT_TRACE_ENTRIES, DEFAULT_OPTIONS[OPT_TRACE_ENTRIES]))
        self.resolver = HubResolver(hass, options)
        # The names a call may use come from the resolver (H2) and the policy book (H4a).
        self.audiences: AudienceResolver = self.resolver
        self.recipients: RecipientResolver = self.resolver
        self.policies = PolicyBook()
        self.chain = Chain()
        self.chain.replace(QuietHoursStage(self.policies))
        self.chain.replace(AwayStage(hass, self.policies))
        self._unsub_arrival: CALLBACK_TYPE | None = None
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
        await self.ledger.async_load()
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
        self._restore_timers()
        # Arrival releases the deliveries held by Away.
        self._unsub_arrival = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_state_change, event_filter=self._is_person
        )
        self._ready.set()

    async def async_unload(self) -> None:
        self._closed = True
        self.channels.stop_all()
        self._cancel_all_timers()
        if self._unsub_arrival is not None:
            self._unsub_arrival()
            self._unsub_arrival = None
        tasks = list(self._tails.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tails.clear()
        await self.resolver.async_stop()
        await self.ledger.async_save()

    async def async_wait_idle(self) -> None:
        """Wait until the queued deliveries are done (tests, and a clean unload)."""
        while self._tails:
            await asyncio.wait(list(self._tails.values()))
            await asyncio.sleep(0)  # lets the done callbacks drop finished tasks

    # Planning ---------------------------------------------------------------------------

    async def plan(self, message: Banner, *, waiting: bool = False) -> list[Planned]:
        """What delivering this message would do now. Sends nothing."""
        planned: list[Planned] = []
        for channel in message.channels:
            available = self.channels.get(channel).available
            if channel == CHANNEL_BANNER:
                result = Result.HELD if waiting else Result.SENT
                reason = "waiting_for_condition" if waiting else None
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
                    self._planned(channel, r.key, available, r) for r in resolution.recipients
                ]
            planned += [
                Planned(channel, s.who, Result.SKIPPED, s.reason) for s in resolution.skipped
            ]
            if not resolution.recipients and not resolution.skipped:
                planned.append(Planned(channel, "", Result.SKIPPED, "no_recipients"))
        return planned

    @staticmethod
    def _planned(
        channel: str, recipient: str, available: bool, who: Recipient | None = None
    ) -> Planned:
        if available:
            return Planned(channel, recipient, Result.SENT, who=who)
        return Planned(channel, recipient, Result.SKIPPED, "channel_unavailable", who)

    @staticmethod
    def counts(planned: list[Planned]) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for item in planned:
            per = out.setdefault(item.channel, {"sent": 0, "held": 0, "skipped": 0, "failed": 0})
            per[item.result.value] += 1
        return out

    # Transitions ------------------------------------------------------------------------

    @callback
    def on_transition(self, transition: BannerTransition) -> None:
        if self._closed:
            return
        banner = transition.banner
        if self._ready.is_set():
            # Decided here, in the same call that created the message, so a viewer is never shown a
            # message that is about to be held (D-105).
            if transition.kind in (Kind.APPEARED, Kind.BECAME_VISIBLE):
                self._try_hold(banner)
            elif transition.kind is Kind.UPDATED:
                self._update_held(banner)
        self._enqueue(banner.id, lambda: self._handle(transition), f"heads_up hub {banner.id}")

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
            await self._take_back(banner, transition.user_id)
            self._dismissed(banner)
        elif kind is Kind.ACKNOWLEDGED:
            self._stop_timers(banner.id, "acknowledged")
            self.note(banner.id, "", transition.user_id or "", "acknowledged", "ok")
        elif kind is Kind.SEVERITY_CHANGED:
            self._restart_timers(banner)
        elif kind is Kind.SNOOZED:
            everyone = banner.snooze_scope == "global"
            await self._take_back(banner, None if everyone else transition.user_id)
        elif kind is Kind.UNSNOOZED:
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
                await self._fallback(banner, results)
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
    ) -> list[tuple[Planned, Outcome]]:
        """Run planned deliveries through the precedence chain and the channels."""
        results: list[tuple[Planned, Outcome]] = []
        for item in planned:
            row = self.ledger.rows.get((banner.id, item.channel, item.recipient))
            if resume and row is not None and (row.state is State.SENT or row.hold):
                continue  # sent or held before the restart: never send twice
            channel = self.channels.get(item.channel)
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                step = self.chain.run(
                    Step(banner, item.channel, self._target(item, banner), origin)
                )
                if isinstance(step, Skip):
                    outcome = Outcome(Result.SKIPPED, step.reason)
                elif isinstance(step, Hold):
                    outcome = Outcome(Result.HELD, step.reason, due=step.until, hold=step.kind)
                else:
                    call = channel.update if update else channel.deliver
                    outcome = await call(step.banner, step.target)
            self._record(
                banner.id,
                item.channel,
                item.recipient,
                outcome,
                item.who.person if item.who else None,
            )
            results.append((item, outcome))
        return results

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

    # Policies: escalation and reminder timers --------------------------------------------

    def _row_target(self, row: Delivery, banner: Banner) -> Target:
        kind = "device" if row.recipient.startswith("device:") else ""
        return Target(row.recipient, kind, row.person, ack_button=self.ack_applies(banner))

    def policy_problem(self, policy: Policy) -> str | None:
        """Why a policy cannot run now, as a stable reason code (D-111). Home Assistant cannot
        stop a user from deleting an audience or group a policy names, so this is checked when
        the policy fires and reported instead."""
        for channel, target in policy.targets.items():
            audience = target.get("audience")
            if audience is not None and audience not in self.audiences.names():
                return "audience_missing"
            known = self.recipients.known(channel)
            for name in target.get("recipients", []):
                if name.endswith(GROUP_SUFFIX) and name not in known:
                    return "group_missing"
        return None

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
                    else reminder.next_due(policy, now)
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
        elif policy is None or not policy.enabled:
            self._finish(row, State.CLEARED, "policy_gone")
        elif policy.type == "escalation":
            await self._escalate(banner, policy, row)
        else:
            await self._remind(banner, policy, row)

    async def _escalate(self, banner: Banner, policy: Policy, row: Delivery) -> None:
        if (problem := self.policy_problem(policy)) is not None:
            self._finish(row, State.SKIPPED, problem)  # D-111: reported, never silent
            return
        message = escalation.message_for(banner, policy)
        # Whoever already has the message on that channel is not notified a second time.
        await self._send(message, await self.plan(message), resume=True, origin="escalation")
        self._finish(row, State.SENT, "escalated")

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
        for target_row in sent:
            step = self.chain.run(
                Step(banner, target_row.channel, self._row_target(target_row, banner), "reminder")
            )
            if isinstance(step, Skip | Hold):  # a reminder is never held, only skipped
                reason = step.reason
                self._trace(banner.id, target_row.channel, target_row.recipient, "skipped", reason)
                continue
            outcome = await self.channels.get(target_row.channel).deliver(step.banner, step.target)
            self._trace(
                banner.id,
                target_row.channel,
                target_row.recipient,
                outcome.result.value,
                "reminder",
            )
        row.count += 1
        if reminder.finished(policy, row.count):
            self._finish(row, State.SENT, "reminders_done")
            return
        row.due = reminder.next_due(policy, dt_util.utcnow())
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

    @staticmethod
    @callback
    def _is_person(data: Any) -> bool:  # HA requires a callback as an event filter
        return str(data["entity_id"]).startswith("person.")

    @callback
    def _on_state_change(self, event: Event[Any]) -> None:
        new, old = event.data["new_state"], event.data["old_state"]
        if self._closed or new is None or new.state != "home" or (old and old.state == "home"):
            return
        for row in list(self.ledger.rows.values()):
            if row.state is State.HELD and row.hold == HOLD_AWAY and row.person == new.entity_id:
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
        if row.hold == HOLD_AWAY:  # the timer of an away delivery is its deadline
            self._end_held(row, State.SKIPPED, "max_wait_exceeded")
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

    async def _release(self, message_id: str, channel: str, recipient: str) -> None:
        """Send a held delivery now, if the message still needs it."""
        row = self.ledger.rows.get((message_id, channel, recipient))
        if row is None or row.state is not State.HELD or not row.hold:
            return
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
            step = self.chain.run(Step(banner, channel, target, "message"))
            if isinstance(step, Skip):
                outcome = Outcome(Result.SKIPPED, step.reason)
            elif isinstance(step, Hold):
                outcome = Outcome(Result.HELD, step.reason, due=step.until, hold=step.kind)
            else:
                outcome = await self.channels.get(channel).deliver(step.banner, step.target)
            self._record(message_id, channel, recipient, outcome, row.person)

    # Fallback ---------------------------------------------------------------------------

    @staticmethod
    def _unreached(results: list[tuple[Planned, Outcome]]) -> set[str]:
        """Why a requested channel reached nobody: `no_audience` or `failed`."""
        classes: set[str] = set()
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
                classes.add("failed" if failed else "no_audience")
        return classes

    async def _fallback(self, banner: Banner, results: list[tuple[Planned, Outcome]]) -> None:
        """After the first delivery: other channels and targets when it reached nobody (D-079).
        It fires once per message and a fallback never triggers another."""
        classes = self._unreached(results)
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
            message = escalation.message_for(banner, policy)
            await self._send(message, await self.plan(message), resume=True, origin="fallback")

    # Summarize: hold, then one summary per recipient and channel (D-105, D-113) ---------------

    def is_held(self, message_id: str) -> bool:
        held = self.ledger.held.get(message_id)
        return held is not None and not held.resolved

    def _summary_policy(self, banner: Banner) -> Policy | None:
        if banner.source == SOURCE_SUMMARY:
            return None  # a summary is never held itself
        found = [
            p
            for p in self.policies.for_message(banner)
            if p.type == "summarize" and summarize.holds(p, banner.severity)
        ]
        return min(found, key=lambda p: p.name) if found else None

    def _try_hold(self, banner: Banner) -> None:
        """Hold a message that appears while a Summarize policy applies. Decided once, when the
        message first appears; a message already delivered is not taken back."""
        if self.is_held(banner.id) or self.ledger.for_message(banner.id):
            return
        if (policy := self._summary_policy(banner)) is None:
            return
        self.ledger.put_held(HeldMessage.from_banner(banner, policy.key, dt_util.utcnow()))
        self._arm_summary(policy)

    def _update_held(self, banner: Banner) -> None:
        held = self.ledger.held.get(banner.id)
        if held is None or held.resolved:
            return
        policy = self.policies.by_key(held.policy)
        if policy is None or not policy.enabled or not summarize.holds(policy, banner.severity):
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
        """A policy was deleted, disabled or renamed: the messages it holds become normal."""
        for held in list(self.ledger.held.values()):
            policy = self.policies.by_key(held.policy)
            if held.resolved or (policy is not None and policy.enabled):
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
        self.visibility_changed()

    async def _release_held(self, message_id: str) -> None:
        banner = self.lookup(message_id)
        self._released.discard(message_id)
        if banner is None:
            return
        await self._deliver(banner, update=False)
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
            for item in await self.plan(entry.as_banner()):
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
            self._trace(
                str(result.get("id", data["id"])), channel, recipient, "summary", f"{len(members)}"
            )
        for entry in entries:
            if entry.resolved:
                self.ledger.drop_held(entry.message_id)
            else:
                entry.summarized = True
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
        self._trace(message_id, channel, recipient, outcome.result.value, outcome.reason)
        if outcome.hold:
            self._schedule_held(message_id, channel, recipient)

    def _trace(
        self, message_id: str, channel: str, recipient: str, result: str, reason: str | None
    ) -> None:
        self.trace.add(
            TraceEntry(
                dt_util.utcnow().isoformat(), message_id, channel, recipient or None, result, reason
            )
        )
