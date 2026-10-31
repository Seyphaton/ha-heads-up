"""Fallback: other channels and targets when the first delivery reached nobody (D-079)."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import settle
from .policy_support import FALLBACK, add_policy, make_household, move, pushes, send, trace


async def test_it_sends_to_its_target_when_the_audience_resolved_to_nobody(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(
        hass, entry, "Nobody", **{**FALLBACK, "targets": {"push": {"recipients": ["person.ben"]}}}
    )
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    assert not pushes(home.anna) and len(pushes(home.ben)) == 1
    assert any(e["result"] == "fallback" for e in trace(entry))


async def test_it_does_not_fire_when_someone_was_notified(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nobody", **FALLBACK)
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)


async def test_a_person_without_a_usable_device_is_a_failure_not_a_missing_audience(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.cy", "home")
    await add_policy(hass, entry, "Nobody", **FALLBACK)  # when: no_audience
    await send(hass, entry, severity="warning", to={"push": {"recipients": ["person.cy"]}})
    assert not pushes(home.ben)
    await add_policy(hass, entry, "Failed", **{**FALLBACK, "when": "failed"})
    await send(hass, entry, id="n", severity="warning", to={"push": {"recipients": ["person.cy"]}})
    assert len(pushes(home.ben)) == 1


async def test_both_fires_for_either(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    await add_policy(hass, entry, "Either", **{**FALLBACK, "when": "both"})
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    # Ben is home, so the audience is not empty: nothing to fall back from.
    assert len(pushes(home.ben)) == 1  # Ben was in the audience himself
    move(hass, "person.ben", "not_home")
    await send(hass, entry, id="n", severity="warning", to={"push": {"audience": "At home"}})
    assert len(pushes(home.ben)) == 2


async def test_it_fires_once_per_message_and_not_on_an_update(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(hass, entry, "Nobody", **FALLBACK)
    for text in ("one", "two"):
        await send(
            hass, entry, message=text, severity="warning", to={"push": {"audience": "At home"}}
        )
    assert len(pushes(home.ben)) == 1


async def test_a_fallback_that_reaches_nobody_does_not_start_another(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    first = {**FALLBACK, "targets": {"push": {"audience": "At home"}}}
    await add_policy(hass, entry, "Loop", **first)
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    assert not pushes(home.anna) and not pushes(home.ben)
    assert sum(1 for e in trace(entry) if e["result"] == "fallback") == 1


async def test_a_deleted_audience_in_a_fallback_is_reported(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(
        hass, entry, "Gone", **{**FALLBACK, "targets": {"push": {"audience": "Deleted"}}}
    )
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    assert not pushes(home.ben)
    assert any(e["reason"] == "audience_missing" for e in trace(entry))


async def test_a_message_waiting_for_its_condition_does_not_trigger_it(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    hass.states.async_set("binary_sensor.leak", "off")
    await add_policy(hass, entry, "Nobody", **FALLBACK)
    await send(
        hass,
        entry,
        severity="warning",
        to={"push": {"audience": "At home"}},
        condition={"entity_id": "binary_sensor.leak", "state": "on"},
    )
    assert not pushes(home.ben)
    hass.states.async_set("binary_sensor.leak", "on")
    await settle(hass, entry)
    assert len(pushes(home.ben)) == 1


async def test_the_call_can_switch_it_off_with_policy_none(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(hass, entry, "Nobody", **FALLBACK)
    await send(hass, entry, severity="warning", policy="none", to={"push": {"audience": "At home"}})
    assert not pushes(home.ben)
    assert DOMAIN  # keep the import used
