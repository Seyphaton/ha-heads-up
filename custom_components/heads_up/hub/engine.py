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

from ..const import CHANNEL_BANNER, DEFAULT_OPTIONS, OPT_TRACE_ENTRIES
from ..models import Banner
from .channels import ChannelRegistry, Outcome, Result
from .interfaces import (
    AudienceResolver,
    EntityRecipients,
    NoAudiences,
    NoPolicies,
    PolicyCatalog,
    RecipientResolver,
)
from .ledger import Delivery, DeliveryLedger, State
from .trace import TraceBuffer, TraceEntry
from .transitions import BannerTransition, Kind

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


def _recipients(message: Banner, channel: str) -> list[str]:
    if channel == CHANNEL_BANNER:
        return [""]  # the card applies its own targeting (`people`)
    target = message.targets.get(channel) or {}
    if "recipients" in target:
        return list(target["recipients"])
    if "audience" in target:
        return [f"audience:{target['audience']}"]
    return [""]


class HubEngine:
    def __init__(
        self, hass: HomeAssistant, options: dict[str, Any], create_task: TaskFactory
    ) -> None:
        self.hass = hass
        self.channels = ChannelRegistry()
        self.ledger = DeliveryLedger(hass)
        self.trace = TraceBuffer(options.get(OPT_TRACE_ENTRIES, DEFAULT_OPTIONS[OPT_TRACE_ENTRIES]))
        self.audiences: AudienceResolver = NoAudiences()
        self.recipients: RecipientResolver = EntityRecipients(hass)
        self.policies: PolicyCatalog = NoPolicies()
        self._create_task = create_task
        self._tails: dict[str, asyncio.Task[None]] = {}
        self._gate = asyncio.Semaphore(MAX_CONCURRENT)
        self._closed = False
        self._ready = asyncio.Event()  # set once the ledger is loaded

    async def async_start(self, known_ids: set[str]) -> None:
        """Load the ledger and forget what no longer exists, without re-sending anything."""
        await self.ledger.async_load()
        for message_id in self.ledger.message_ids() - known_ids:
            for row in self.ledger.for_message(message_id):
                self._trace(message_id, row.channel, row.recipient, "cleared", "gone_at_startup")
            self.ledger.drop_message(message_id)
        self._ready.set()

    async def async_unload(self) -> None:
        self._closed = True
        tasks = list(self._tails.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tails.clear()
        await self.ledger.async_save()

    async def async_wait_idle(self) -> None:
        """Wait until the queued deliveries are done (tests, and a clean unload)."""
        while self._tails:
            await asyncio.wait(list(self._tails.values()))
            await asyncio.sleep(0)  # lets the done callbacks drop finished tasks

    # Planning ---------------------------------------------------------------------------

    def plan(self, message: Banner, *, waiting: bool = False) -> list[Planned]:
        """What delivering this message would do now. Sends nothing."""
        planned: list[Planned] = []
        for channel in message.channels:
            for recipient in _recipients(message, channel):
                if channel == CHANNEL_BANNER and waiting:
                    planned.append(
                        Planned(channel, recipient, Result.HELD, "waiting_for_condition")
                    )
                elif self.channels.get(channel).available:
                    planned.append(Planned(channel, recipient, Result.SENT))
                else:
                    planned.append(
                        Planned(channel, recipient, Result.SKIPPED, "channel_unavailable")
                    )
        return planned

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
        if transition.ends_message:
            await self._end(banner)
        elif transition.kind in (Kind.APPEARED, Kind.BECAME_VISIBLE, Kind.UPDATED):
            await self._deliver(
                banner, update=transition.kind is Kind.UPDATED, resume=transition.silent
            )

    async def _deliver(self, banner: Banner, *, update: bool, resume: bool = False) -> None:
        for item in self.plan(banner, waiting=not banner.active):
            row = self.ledger.rows.get((banner.id, item.channel, item.recipient))
            if resume and row is not None and row.state is State.SENT:
                continue  # sent before the restart: never send twice
            channel = self.channels.get(item.channel)
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                call = channel.update if update else channel.deliver
                outcome = await call(banner, item.recipient)
            self._record(banner.id, item.channel, item.recipient, outcome)

    async def _end(self, banner: Banner) -> None:
        for row in self.ledger.for_message(banner.id):
            if row.state is State.SENT:
                await self.channels.get(row.channel).clear(banner, row.recipient)
            self._trace(banner.id, row.channel, row.recipient, "cleared", None)
        self.ledger.drop_message(banner.id)

    async def send_once(self, message: Banner) -> list[Planned]:
        """Deliver a message that has no record (shortcuts without an id)."""
        planned = self.plan(message)
        for item in planned:
            outcome = Outcome(item.result, item.reason)
            if item.result is Result.SENT:
                outcome = await self.channels.get(item.channel).deliver(message, item.recipient)
            self._trace(
                message.id, item.channel, item.recipient, outcome.result.value, outcome.reason
            )
        return planned

    def _record(self, message_id: str, channel: str, recipient: str, outcome: Outcome) -> None:
        state = State(outcome.result.value)
        self.ledger.put(
            Delivery(message_id, channel, recipient, state, dt_util.utcnow(), ref=outcome.ref)
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
