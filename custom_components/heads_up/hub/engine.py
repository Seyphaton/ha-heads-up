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
    BANNER_NOBODY,
    CHANNEL_BANNER,
    CHANNEL_PERSISTENT,
    DEFAULT_OPTIONS,
    EVENT_DELIVERY_FAILED,
    GLOBAL_SNOOZE_KEY,
    GROUP_SUFFIX,
    HOLD_AWAY,
    OPT_RECENT_MESSAGES,
    OPT_TRACE_ENTRIES,
    SOURCE_SUMMARY,
    SUMMARY_LIFETIME_HOURS,
    SUMMARY_PREFIX,
    TARGET_CHANNELS,
    TIMER_CHANNEL,
)
from ..models import Banner
from .activity import Activity, ActivityLog, RecentMessages
from .channels import ChannelRegistry, Outcome, Result, Target
from .channels.persistent import warn_speech
from .channels.speak import NO_SPEAKER
from .interfaces import AudienceResolver, RecipientResolver
from .ledger import Delivery, DeliveryLedger, HeldMessage, State
from .limits import DUPLICATE, RATE_LIMITED, Limiter
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


class HubEngine:
    def __init__(
        self, hass: HomeAssistant, options: dict[str, Any], create_task: TaskFactory
    ) -> None:
        self.hass = hass
        self.channels = ChannelRegistry()
        self.ledger = DeliveryLedger(hass)
        self.trace = TraceBuffer(options.get(OPT_TRACE_ENTRIES, DEFAULT_OPTIONS[OPT_TRACE_ENTRIES]))
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
        for message_id in sorted(known_ids):
            if (loaded := self.lookup(message_id)) is not None:
                self.recent.seen(message_id, self._info(loaded))
        await self._restore_bell()
        self._restore_timers()
        # Arrival releases the deliveries held by Away.
        self._unsub_arrival = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._on_state_change, event_filter=self._is_person
        )
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
            classes = self._unreached(results)
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
                other = escalation.message_for(message, policy)
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
            return {**row, "result": "held", "reason": "summarize", "note": summary.name}
        if item.result is Result.SENT:
            step = self.chain.run(
                Step(message, item.channel, self._target(item, message, ack=False), "message")
            )
            if isinstance(step, Skip):
                return {**row, "result": "skipped", "reason": step.reason}
            if isinstance(step, Hold):
                until = step.until.isoformat() if step.until else None
                return {**row, "result": "held", "reason": step.reason, "until": until}
            if step.target.quiet:
                row["note"] = "quiet"
        return row

    @staticmethod
    def _later(policy: Policy) -> dict[str, Any]:
        """The timing of a policy, as fields the panel words."""
        fields = {
            "escalation": ("after_minutes", "channels"),
            "reminder": ("every_minutes", "max_count", "channels"),
            "away": ("max_wait",),
            "fallback": ("when", "channels"),
            "deliver": ("channels",),
            "summarize": ("summary_every", "summary_at", "include_critical"),
        }
        out: dict[str, Any] = {"type": policy.type, "policy": policy.name}
        for key in fields.get(policy.type, ()):
            value = getattr(policy, key)
            out[key] = list(value) if isinstance(value, tuple) else value
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

    def _remember(self, transition: BannerTransition) -> None:
        banner, kind = transition.banner, transition.kind
        if kind in (Kind.APPEARED, Kind.BECAME_VISIBLE):
            self.recent.seen(banner.id, self._info(banner))
            if not transition.silent and banner.source != SOURCE_SUMMARY:
                self._log("created", banner.id, ",".join(banner.channels))
            return
        if transition.silent:
            return
        who = self._user_name(transition.user_id)
        if kind is Kind.ACKNOWLEDGED:
            self._log("acknowledged", banner.id, who)
        elif kind is Kind.SNOOZED:
            self._log("snoozed", banner.id, who)
        elif kind is Kind.UNSNOOZED:
            self._log("unsnoozed", banner.id, who)
        elif kind is Kind.HIDDEN and transition.reason == Reason.DISMISSED:
            self._log("dismissed", banner.id, who)
        elif transition.ends_message:
            now = dt_util.utcnow().isoformat()
            self.recent.ended(banner.id, now, transition.reason)
            expired = transition.reason == Reason.EXPIRED
            self._log("expired" if expired else "cleared", banner.id, transition.reason)

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
                await self._apply_deliver(banner)
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
    ) -> list[tuple[Planned, Outcome]]:
        """Run planned deliveries through the precedence chain and the channels."""
        results: list[tuple[Planned, Outcome]] = []
        # `resume` also means "skip what was sent" for escalations and fallbacks; only the
        # first delivery after a restart is silent about problems (D-126, D-128).
        startup = resume and origin == "message"
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
            )
            results.append((item, outcome))
        if not startup:
            self._report(
                banner,
                origin,
                [(i.channel, i.recipient, i.who.person if i.who else None, o) for i, o in results],
            )
        return results

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
        if item.channel == "push" and not self.limiter.push_allowed(banner, target.key):
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
        self._log("escalation_sent", banner.id, policy.name)

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
        report: list[tuple[str, str, str | None, Outcome]] = []
        for target_row in sent:
            step = self.chain.run(
                Step(banner, target_row.channel, self._row_target(target_row, banner), "reminder")
            )
            if isinstance(step, Skip | Hold):  # a reminder is never held, only skipped
                reason = step.reason
                self._trace(banner.id, target_row.channel, target_row.recipient, "skipped", reason)
                continue
            if target_row.channel == "push" and not self.limiter.push_allowed(
                step.banner, step.target.key
            ):
                self._trace(banner.id, "push", target_row.recipient, "skipped", RATE_LIMITED)
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
                "reminder",
            )
        self._report(banner, "reminder", report)
        self._log("reminder_sent", banner.id, policy.name)
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
            elif channel == "push" and not self.limiter.push_allowed(step.banner, step.target.key):
                outcome = Outcome(Result.SKIPPED, RATE_LIMITED)
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

    async def _apply_deliver(self, banner: Banner) -> None:
        """Deliver policies add channels and targets to the first delivery (D-121). Once per
        message; a recipient that already has the message on that channel is left out."""
        if banner.source == SOURCE_SUMMARY or self.is_held(banner.id):
            return
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
            await self._send(message, await self.plan(message), resume=True, origin="deliver")
            self._log("deliver_sent", banner.id, policy.name)

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
            self._log("fallback_sent", banner.id, policy.name)

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
            summary_id = str(result.get("id", data["id"]))
            self._trace(summary_id, channel, recipient, "summary", f"{len(members)}")
            self._log("summary_sent", summary_id, f"{channel}|{len(members)}")
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
        if (
            outcome.result in (Result.SKIPPED, Result.FAILED)
            and outcome.reason not in fallback.UNLOGGED_REASONS
        ):
            self._log(outcome.result.value, message_id, f"{channel}|{outcome.reason}")
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
