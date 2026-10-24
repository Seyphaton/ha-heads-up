"""clear_banner and clear_all (DESIGN §7, D-025, D-030)."""

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners


async def clear(hass: HomeAssistant, service: str, **data: object) -> dict[str, object]:
    response = await hass.services.async_call(
        DOMAIN, service, data, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def test_clear_by_id(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", tag="t")
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")

    assert await clear(hass, "clear_banner", id="a") == {"cleared": 1}
    assert banners(entry) == {}
    assert [e.data for e in events] == [{"id": "a", "tag": "t", "reason": "action"}]


async def test_clear_unknown_id_returns_zero(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert await clear(hass, "clear_banner", id="nope") == {"cleared": 0}


async def test_clear_by_tag(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", tag="laundry")
    await create(id="b", message="x", tag="laundry")
    await create(id="c", message="x", tag="other")

    assert await clear(hass, "clear_banner", tag="laundry") == {"cleared": 2}
    assert set(banners(entry)) == {"c"}


async def test_clear_by_id_and_tag_requires_both_to_match(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", tag="one")
    assert await clear(hass, "clear_banner", id="a", tag="two") == {"cleared": 0}
    assert await clear(hass, "clear_banner", id="a", tag="one") == {"cleared": 1}


async def test_clear_banner_needs_id_or_tag(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "clear_banner", {}, blocking=True)


async def test_clear_all(hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(id="a", message="x")
    await create(id="b", message="x", dismissible=False, timeout=0)
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")

    assert await clear(hass, "clear_all") == {"cleared": 2}
    assert banners(entry) == {}
    assert {e.data["reason"] for e in events} == {"clear_all"}
