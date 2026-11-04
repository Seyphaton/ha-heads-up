"""The cap on stored messages and the push rate limits are separate guards (D-141)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..conftest import banners
from .conftest import AddDevice
from .policy_support import make_household, pushes, send


async def set_options(hass: HomeAssistant, entry: MockConfigEntry, **options: Any) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, **options})
    await hass.async_block_till_done()


def clears(phone: Any) -> list[Any]:
    return [c for c in phone.calls if c.data.get("message") == "clear_notification"]


def reasons(entry: MockConfigEntry, message_id: str) -> list[str | None]:
    return [e["reason"] for e in entry.runtime_data.hub.trace.entries(message_id)]


async def test_a_flood_of_new_messages_is_limited_twice_in_different_ways(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, max_banners=3, rate_per_device_per_minute=2)
    for n in range(5):
        await send(hass, entry, id=f"m{n}", severity="warning")
    # The cap on stored messages evicted the two oldest, whatever their delivery.
    assert set(banners(entry)) == {"m2", "m3", "m4"}
    # The rate limit let two pushes through; the three that were over the cap were skipped.
    assert len(pushes(home.anna)) == 2
    assert all("rate_limited" in reasons(entry, f"m{n}") for n in (2, 3, 4))
    # An evicted message ends everywhere: its push was taken back, and taking back is not limited.
    assert len(clears(home.anna)) == 2
    # The messages that stayed were never pushed, but they are on the dashboard.
    assert all(banners(entry)[f"m{n}"].active for n in (2, 3, 4))


async def test_an_update_does_not_count_toward_the_cap_but_counts_toward_the_rate(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await set_options(hass, entry, max_banners=1, rate_per_device_per_minute=2, dedupe_seconds=0)
    for n in range(3):
        await send(hass, entry, id="same", severity="warning", message=f"Version {n}")
    assert set(banners(entry)) == {"same"}  # one message, however often it is updated
    assert len(pushes(home.anna)) == 2  # but every update is a push to count
    assert "rate_limited" in reasons(entry, "same")
