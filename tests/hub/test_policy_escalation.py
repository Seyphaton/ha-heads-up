"""Escalation: more channels after N minutes without acknowledgement (D-079, D-081)."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .policy_support import (
    ESCALATION,
    add_policy,
    make_household,
    pushes,
    send,
    trace,
    wait,
)


async def test_it_delivers_to_the_policy_target_after_the_time(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)
    await wait(hass, entry, freezer, 4)
    assert not pushes(home.ben)
    await wait(hass, entry, freezer, 1.1)
    assert len(pushes(home.ben)) == 1
    assert len(pushes(home.anna)) == 1  # the first recipient is not notified again


async def test_the_timer_is_a_row_in_the_ledger_with_its_due_time(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    (row,) = entry.runtime_data.hub.ledger.timers("m")
    assert row.recipient == "escalation:Water" and row.state.value == "planned"
    assert row.due is not None and row.due > row.updated_at


async def test_acknowledging_stops_it(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: object,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/acknowledge", "banner_id": "m"})
    assert (await client.receive_json())["success"]
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
    assert any(e["result"] == "acknowledged" for e in trace(entry))


async def test_dismissing_does_not_stop_it_by_default(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    entry.runtime_data.dismiss("m", "anna-id")
    await wait(hass, entry, freezer, 6)
    assert len(pushes(home.ben)) == 1


async def test_dismissing_stops_it_when_the_policy_says_so(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION, dismiss_acks=True)
    await send(hass, entry)
    entry.runtime_data.dismiss("m", "anna-id")
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)


async def test_two_escalations_form_a_chain_by_their_times(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "First", **ESCALATION)
    second = {**ESCALATION, "after_minutes": 15, "targets": {"push": {"recipients": ["person.cy"]}}}
    cy = await mobile_app_device("Cy's phone", user_id="cy-id", person_entity_id="person.cy")
    await add_policy(hass, entry, "Second", **second)
    await send(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert len(pushes(home.ben)) == 1 and not pushes(cy)
    await wait(hass, entry, freezer, 10)
    assert len(pushes(cy)) == 1


async def test_a_severity_change_restarts_the_policies_of_the_new_severity(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical", **ESCALATION, severities=["critical"])
    slower = {**ESCALATION, "after_minutes": 10, "severities": ["warning"]}
    await add_policy(hass, entry, "Warning", **slower)
    await send(hass, entry)
    await wait(hass, entry, freezer, 3)
    await send(hass, entry, severity="warning")
    await wait(hass, entry, freezer, 8)  # past the old 5 minutes, before the new 10
    assert not pushes(home.ben)
    await wait(hass, entry, freezer, 3)
    assert len(pushes(home.ben)) == 1


async def test_a_severity_change_clears_the_acknowledgement(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    await send(hass, entry, message="Still leaking")
    assert entry.runtime_data.banners["m"].acknowledged_by == ["anna-id"]
    await send(hass, entry, severity="warning")
    assert entry.runtime_data.banners["m"].acknowledged_by == []


async def test_ending_the_message_cancels_the_timers(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await hass.services.async_call(DOMAIN, "clear", {"id": "m"}, blocking=True)
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
    assert not entry.runtime_data.hub.ledger.timers()


async def test_the_condition_ending_cancels_the_timers(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    hass.states.async_set("binary_sensor.leak", "on")
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry, condition={"entity_id": "binary_sensor.leak", "state": "on"})
    hass.states.async_set("binary_sensor.leak", "off")
    await settle_all(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)


async def settle_all(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    from .helpers import settle

    await settle(hass, entry)


async def test_an_overdue_step_fires_once_after_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(600)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    from .helpers import settle

    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1
    assert len(pushes(home.anna)) == 1  # never re-sent after the restart
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1


async def test_a_pending_step_waits_the_rest_of_its_time_after_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry)
    await wait(hass, entry, freezer, 3)
    await restart(hass, entry)
    await wait(hass, entry, freezer, 1)
    assert not pushes(home.ben)
    await wait(hass, entry, freezer, 2)
    assert len(pushes(home.ben)) == 1


async def test_a_policy_naming_a_deleted_audience_is_reported_and_skipped(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    missing = {**ESCALATION, "targets": {"push": {"audience": "Gone"}}}
    await add_policy(hass, entry, "Water", **missing)
    await send(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
    assert any(e["reason"] == "audience_missing" for e in trace(entry))


async def test_a_disabled_policy_does_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION, enabled=False)
    await send(hass, entry)
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)


async def test_the_call_can_name_one_policy_or_none(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await send(hass, entry, policy="none")
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
    await send(hass, entry, policy="Water")
    await wait(hass, entry, freezer, 6)
    assert len(pushes(home.ben)) == 1


async def test_a_tag_list_limits_it_to_those_messages(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION, tags=["water"])
    await send(hass, entry, tag="door")
    await wait(hass, entry, freezer, 6)
    assert not pushes(home.ben)
    await send(hass, entry, id="n", tag="water")
    await wait(hass, entry, freezer, 6)
    assert len(pushes(home.ben)) == 1
