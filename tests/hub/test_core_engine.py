"""Hub engine: ledger bookkeeping, dry run, serialization, unload, hub off."""

import asyncio
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.channels.base import Outcome, Result
from custom_components.heads_up.hub.engine import HubEngine
from custom_components.heads_up.hub.ledger import State

from ..conftest import CreateBanner
from ..test_restart import restart
from .helpers import settle, tick


async def test_delivery_is_recorded_in_ledger_and_trace(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    hub = entry.runtime_data.hub
    row = hub.ledger.rows[("a", "banner", "")]
    assert row.state is State.SENT
    entries = hub.trace.entries("a")
    assert entries[0]["channel"] == "banner" and entries[0]["result"] == "sent"


async def test_waiting_banner_is_held_until_its_condition_is_true(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set("binary_sensor.w", "off")
    await create(id="a", message="x", condition={"entity_id": "binary_sensor.w", "state": "on"})
    await settle(hass, entry)
    hub = entry.runtime_data.hub
    assert hub.ledger.rows[("a", "banner", "")].state is State.HELD
    hass.states.async_set("binary_sensor.w", "on")
    await settle(hass, entry)
    assert hub.ledger.rows[("a", "banner", "")].state is State.SENT


async def test_removing_a_message_clears_its_ledger_rows(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    await hass.services.async_call(DOMAIN, "clear", {"id": "a"}, blocking=True)
    await settle(hass, entry)
    hub = entry.runtime_data.hub
    assert hub.ledger.for_message("a") == []
    assert hub.trace.entries("a")[0]["result"] == "cleared"


async def test_plan_is_a_dry_run_that_sends_and_records_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    hub = entry.runtime_data.hub
    before = len(hub.trace), dict(hub.ledger.rows)
    banner = entry.runtime_data.banners["a"]
    banner.channels = ["banner", "popup"]
    planned = await hub.plan(banner)
    assert [(p.channel, p.result) for p in planned] == [
        ("banner", Result.SENT),
        ("popup", Result.SKIPPED),
    ]
    assert (len(hub.trace), hub.ledger.rows) == before
    assert HubEngine.counts(planned)["popup"]["skipped"] == 1


async def test_deliveries_of_one_message_run_in_order(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hub = entry.runtime_data.hub
    order: list[str] = []

    class Slow:
        name = "banner"
        available = True
        capabilities = hub.channels.get("banner").capabilities

        async def deliver(self, message: Any, target: Any) -> Outcome:
            await asyncio.sleep(0.05)
            order.append(f"deliver:{message.message}")
            return Outcome(Result.SENT)

        async def update(self, message: Any, target: Any) -> Outcome:
            order.append(f"update:{message.message}")
            return Outcome(Result.SENT)

        async def clear(self, message_id: str, target: Any, ref: Any) -> Outcome:
            order.append("clear")
            return Outcome(Result.SENT)

    hub.channels.register(Slow())  # type: ignore[arg-type]
    await create(id="a", message="one")
    await create(id="a", message="two")
    await hass.services.async_call(DOMAIN, "clear", {"id": "a"}, blocking=True)
    await settle(hass, entry)
    assert order == ["deliver:one", "update:two", "clear"]


async def test_a_failing_channel_does_not_stop_the_engine(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hub = entry.runtime_data.hub

    class Broken:
        name = "banner"
        available = True
        capabilities = hub.channels.get("banner").capabilities

        async def deliver(self, message: Any, target: Any) -> Outcome:
            raise RuntimeError("boom")

        update = clear = deliver

    good = hub.channels.get("banner")
    hub.channels.register(Broken())  # type: ignore[arg-type]
    await create(id="a", message="x")
    await settle(hass, entry)
    hub.channels.register(good)
    await create(id="b", message="x")
    await settle(hass, entry)
    assert hub.ledger.rows[("b", "banner", "")].state is State.SENT


async def test_unload_cancels_pending_work_and_leaves_no_task(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hub = entry.runtime_data.hub

    class Stuck:
        name = "banner"
        available = True
        capabilities = hub.channels.get("banner").capabilities

        async def deliver(self, message: Any, target: Any) -> Outcome:
            await asyncio.sleep(3600)
            return Outcome(Result.SENT)

        update = clear = deliver

    hub.channels.register(Stuck())  # type: ignore[arg-type]
    await create(id="a", message="x")
    await asyncio.sleep(0)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await settle(hass, entry)
    assert hub._tails == {}


async def test_ledger_survives_a_restart_and_nothing_is_sent_twice(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    calls: list[str] = []
    await restart(hass, entry)
    hub = entry.runtime_data.hub
    assert hub.ledger.rows[("a", "banner", "")].state is State.SENT

    class Counting:
        name = "banner"
        available = True
        capabilities = hub.channels.get("banner").capabilities

        async def deliver(self, message: Any, target: Any) -> Outcome:
            calls.append(message.id)
            return Outcome(Result.SENT)

        update = clear = deliver

    hub.channels.register(Counting())  # type: ignore[arg-type]
    await settle(hass, entry)
    assert calls == []


async def test_ledger_rows_of_vanished_messages_are_dropped_at_startup(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, hass_storage: Any
) -> None:
    await create(id="a", message="x")
    await settle(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    hass_storage["heads_up.banners"]["data"]["banners"] = []  # gone while HA was down
    assert await hass.config_entries.async_setup(entry.entry_id)
    await settle(hass, entry)
    assert entry.runtime_data.hub.ledger.for_message("a") == []


async def test_expiry_clears_the_ledger(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", timeout=60)
    await tick(hass, freezer, 61)
    await settle(hass, entry)
    assert entry.runtime_data.hub.ledger.for_message("a") == []
