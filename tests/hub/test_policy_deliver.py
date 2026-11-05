"""Deliver: matching messages go to a chosen audience at once, in addition to the call (D-121)."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..test_restart import restart
from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    QUIET,
    SUMMARIZE,
    add_policy,
    make_household,
    pushes,
    send,
    trace,
)

DELIVER = {
    "type": "deliver",
    "severities": ["critical"],
    "channels": ["push"],
    "targets": {"push": {"audience": "Everyone"}},
}


async def banner_only(hass: HomeAssistant, entry: MockConfigEntry, **kw: object) -> None:
    await send(hass, entry, channels=["banner"], to={}, **kw)


async def test_a_critical_banner_message_reaches_phones_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry)
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1


async def test_a_critical_rule_message_reaches_phones_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1


async def test_a_rule_that_triggers_again_delivers_again(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    for _ in range(2):
        hass.states.async_set(WINDOW, "on")
        await settle(hass, entry)
        hass.states.async_set(WINDOW, "off")
        await settle(hass, entry)
    assert len(pushes(home.anna)) == 2


async def test_other_severities_are_left_alone(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry, severity="warning")
    assert not pushes(home.anna)


async def test_it_fires_once_per_message_and_not_on_an_update(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry)
    await banner_only(hass, entry, message="Still leaking")
    assert (
        len(pushes(home.anna)) == 2 and len(pushes(home.ben)) == 2
    )  # the first push and its update
    assert home.ben.calls[-1].data["message"] == "Still leaking"
    kinds = [e["kind"] for e in entry.runtime_data.hub.log.latest()]
    assert kinds.count("deliver_sent") == 1  # delivered once, then only replaced


async def test_someone_who_already_has_it_on_that_channel_is_not_notified_twice(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await send(hass, entry)  # the call already pushes to Anna
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1


async def test_it_passes_quiet_hours_like_any_delivery(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    freezer.move_to("2026-11-02 23:00:00+01:00")
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    await add_policy(hass, entry, "Warning delivery", **{**DELIVER, "severities": ["warning"]})
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry, id="c")
    await banner_only(hass, entry, id="w", severity="warning")
    (critical, warning) = pushes(home.anna)
    assert critical.data["data"]["importance"] == "high"  # critical passes quiet hours
    assert warning.data["data"]["importance"] == "low"


async def test_a_message_held_for_a_summary_is_not_delivered(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **{**SUMMARIZE, "include_critical": True})
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry)
    assert not pushes(home.anna)


async def test_a_deleted_audience_is_reported_and_nothing_is_sent(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(
        hass, entry, "Gone", **{**DELIVER, "targets": {"push": {"audience": "Deleted"}}}
    )
    await banner_only(hass, entry)
    assert not pushes(home.anna)
    assert any(e["reason"] == "audience_missing" for e in trace(entry))


async def test_the_push_is_taken_back_when_the_message_ends(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry)
    await hass.services.async_call("heads_up", "clear_notifications", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert home.anna.calls[-1].data["message"] == "clear_notification"


async def test_a_restart_does_not_deliver_again(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry)
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1


async def test_the_policy_field_none_switches_it_off_for_a_call(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Critical delivery", **DELIVER)
    await banner_only(hass, entry, policy="none")
    assert not pushes(home.anna)
