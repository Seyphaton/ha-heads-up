"""Rate limits and duplicate suppression (D-123): caps and identical updates."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import settle
from .policy_support import make_household, pushes, send, wait


def reasons(entry: MockConfigEntry, message_id: str) -> list[str | None]:
    return [e["reason"] for e in entry.runtime_data.hub.trace.entries(message_id)]


async def set_options(hass: HomeAssistant, entry: MockConfigEntry, **options: Any) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, **options})
    await hass.async_block_till_done()


async def test_the_default_is_five_pushes_per_device_per_minute(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    for n in range(7):
        await send(hass, entry, id=f"m{n}", severity="warning")
    assert len(pushes(home.anna)) == 5
    assert "rate_limited" in reasons(entry, "m5") and "rate_limited" in reasons(entry, "m6")


async def test_the_cap_is_per_device_not_per_house(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, rate_per_device_per_minute=1)
    await send(hass, entry, id="a", severity="warning")
    await send(hass, entry, id="b", severity="warning")
    await send(hass, entry, id="c", severity="warning", to={"push": {"recipients": ["person.ben"]}})
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1
    assert "rate_limited" in reasons(entry, "b")


async def test_the_cap_for_all_devices_counts_every_push(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, rate_total_per_minute=2)
    await send(hass, entry, id="a", severity="warning")
    await send(hass, entry, id="b", severity="warning", to={"push": {"recipients": ["person.ben"]}})
    await send(hass, entry, id="c", severity="warning")
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1
    assert "rate_limited" in reasons(entry, "c")


async def test_the_window_slides_so_pushes_resume_after_a_minute(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, rate_per_device_per_minute=1)
    await send(hass, entry, id="a", severity="warning")
    await send(hass, entry, id="b", severity="warning")
    assert len(pushes(home.anna)) == 1
    await wait(hass, entry, freezer, 1.1)
    await send(hass, entry, id="c", severity="warning")
    assert len(pushes(home.anna)) == 2


async def test_critical_messages_are_never_held_back(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, rate_per_device_per_minute=1, rate_total_per_minute=1)
    for n in range(4):
        await send(hass, entry, id=f"c{n}", severity="critical")
    assert len(pushes(home.anna)) == 4


async def test_a_changed_setting_applies_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, rate_per_device_per_minute=1)
    await send(hass, entry, id="a", severity="warning")
    await send(hass, entry, id="b", severity="warning")
    await set_options(hass, entry, rate_per_device_per_minute=10)
    await send(hass, entry, id="c", severity="warning")
    assert len(pushes(home.anna)) == 2


async def test_an_identical_update_is_ignored_and_a_changed_one_is_sent(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning")
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 1
    assert "duplicate" in reasons(entry, "m")
    await send(hass, entry, severity="warning", message="Water leak, kitchen")
    assert len(pushes(home.anna)) == 2


async def test_the_same_update_is_sent_again_after_the_dedupe_time(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning")
    await wait(hass, entry, freezer, 0.6)
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 2


async def test_dedupe_can_be_switched_off(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, dedupe_seconds=0)
    await send(hass, entry, severity="warning")
    await send(hass, entry, severity="warning")
    assert len(pushes(home.anna)) == 2


async def test_a_critical_update_is_never_ignored(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry)
    await send(hass, entry)
    assert len(pushes(home.anna)) == 2


async def test_a_suppressed_update_leaves_the_push_clearable(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning")
    await send(hass, entry, severity="warning")
    await hass.services.async_call(DOMAIN, "clear", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert home.anna.calls[-1].data["message"] == "clear_notification"


async def test_a_suppressed_push_is_in_the_activity_log_and_does_not_start_a_fallback(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    from .policy_support import FALLBACK, add_policy

    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Backup", **FALLBACK)
    await set_options(hass, entry, rate_per_device_per_minute=1)
    await send(hass, entry, id="a", severity="warning")
    await send(hass, entry, id="b", severity="warning")
    assert not pushes(home.ben)  # being over the cap says nothing about the audience
    kinds = [(e["kind"], e["detail"]) for e in entry.runtime_data.hub.log.latest()]
    assert ("skipped", "push|rate_limited") in kinds
