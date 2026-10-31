"""Delivery engine: turns transitions into deliveries (DESIGN §23.11).

Work runs in background tasks, serialized per message and bounded overall. `plan` is the dry run
that the action response and the panel's Test send both use, so what is reported is what is done.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from ..const import CHANNEL_BANNER, DEFAULT_OPTIONS, OPT_TRACE_ENTRIES, TARGET_CHANNELS
from ..models import Banner
from .channels import ChannelRegistry, Outcome, Result, Target
from .interfaces import AudienceResolver, NoPolicies, PolicyCatalog, RecipientResolver
from .ledger import Delivery, DeliveryLedger, State
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
        # The names a call may use come from the resolver (H2); policies arrive with H4.
        self.audiences: AudienceResolver = self.resolver
        self.recipients: RecipientResolver = self.resolver
        self.policies: PolicyCatalog = NoPolicies()
        self._create_task = create_task
        self._tails: dict[str, asyncio.Task[None]] = {}
        self._gate = asyncio.Semaphore(MAX_CONCURRENT)
        self._closed = False
        self._ready = asyncio.Event()  # set once the ledger is loaded

    async def async_start(self, known_ids: set[str]) -> None:
        """Load the ledger and forget what no longer exists, without re-sending anything."""
        await self.ledger.async_load()
        await self.resolver.async_start()
        for message_id in self.ledger.message_ids() - known_ids:
            for row in self.ledger.for_message(message_id):
                if row.state is State.SENT and row.channel != CHANNEL_BANNER:
                    # The message ended while Home Assistant was stopped: take its push back.
                    target = Target(row.recipient, "", row.person)
                    await self.channels.get(row.channel).clear(message_id, target, row.ref)
                self._trace(message_id, row.channel, row.recipient, "cleared", "gone_at_startup")
            self.ledger.drop_message(message_id)
        self._ready.set()

    async def async_unload(self) -> None:
        self._closed = True
        self.channels.stop_all()
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
        elif kind is Kind.SNOOZED:
            everyone = banner.snooze_scope == "global"
            await self._take_back(banner, None if everyone else transition.user_id)
        elif kind is Kind.UNSNOOZED:
            await self._resend(banner, transition.user_id)
        elif kind in (Kind.APPEARED, Kind.BECAME_VISIBLE, Kind.UPDATED):
            await self._deliver(banner, update=kind is Kind.UPDATED, resume=transition.silent)

    def _target(self, item: Planned) -> Target:
        who = item.who
        if who is None:
            return Target(item.recipient)
        return Target(who.key, who.kind, who.person)

    async def _deliver(self, banner: Banner, *, update: bool, resume: bool = False) -> None:
        for item in await self.plan(banner, waiting=not banner.active):
            row = self.ledger.rows.get((banner.id, item.channel, item.recipient))
            if resume and row is not None and row.state is State.SENT:
                continue  # sent before the restart: never send twice
            channel = self.channels.get(item.channel)
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                call = channel.update if update else channel.deliver
                outcome = await call(banner, self._target(item))
            self._record(
                banner.id,
                item.channel,
                item.recipient,
                outcome,
                item.who.person if item.who else None,
            )

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
            target = Target(
                row.recipient, "device" if row.recipient.startswith("device:") else "", row.person
            )
            outcome = await self.channels.get(row.channel).deliver(banner, target)
            self._record(banner.id, row.channel, row.recipient, outcome, row.person)

    async def _end(self, banner: Banner) -> None:
        for row in self.ledger.for_message(banner.id):
            if row.state is State.SENT:
                target = Target(row.recipient, "", row.person)
                await self.channels.get(row.channel).clear(banner.id, target, row.ref)
            self._trace(banner.id, row.channel, row.recipient, "cleared", None)
        self.ledger.drop_message(banner.id)

    async def send_once(self, message: Banner) -> list[Planned]:
        """Deliver a message that has no record (shortcuts without an id)."""
        planned = await self.plan(message)
        for item in planned:
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                outcome = await self.channels.get(item.channel).deliver(message, self._target(item))
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
                ref=outcome.ref,
                person=person,
            )
        )
        self._trace(message_id, channel, recipient, outcome.result.value, outcome.reason)

    def _trace(
        self, message_id: str, channel: str, recipient: str, result: str, reason: str | None
    ) -> None:
        self.trace.add(
            TraceEntry(
                dt_util.utcnow().isoformat(), message_id, channel, recipient or None, result, reason
            )
        )
