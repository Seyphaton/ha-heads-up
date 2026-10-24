"""Overflow: eviction order and too_many_banners (D-016, D-030)."""

from datetime import timedelta

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners


@pytest.fixture
def options() -> dict[str, object]:
    return {"max_banners": 3, "evict": True}


async def test_evicts_lowest_severity_then_oldest(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="info_old", message="x", severity="info")
    freezer.tick(timedelta(seconds=1))
    await create(id="success", message="x", severity="success")
    freezer.tick(timedelta(seconds=1))
    await create(id="info_new", message="x", severity="info")
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")

    result = await create(id="d", message="x")
    assert result == {"id": "d", "status": "created", "evicted": "success"}
    result = await create(id="e", message="x")
    assert result["evicted"] == "info_old"
    assert set(banners(entry)) == {"info_new", "d", "e"}
    assert [e.data["reason"] for e in events] == ["evicted", "evicted"]


async def test_critical_is_never_evicted(entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(id="c1", message="x", severity="critical")
    await create(id="c2", message="x", severity="critical")
    await create(id="w", message="x", severity="warning")

    result = await create(id="c3", message="x", severity="critical")
    assert result["evicted"] == "w"

    with pytest.raises(ServiceValidationError) as err:
        await create(id="c4", message="x", severity="info")
    assert err.value.translation_key == "too_many_banners"
    assert set(banners(entry)) == {"c1", "c2", "c3"}


async def test_upsert_at_limit_does_not_evict(entry: MockConfigEntry, create: CreateBanner) -> None:
    for i in range(3):
        await create(id=f"b{i}", message="x", severity="info")
    result = await create(id="b0", message="changed")
    assert result == {"id": "b0", "status": "updated"}
    assert len(banners(entry)) == 3


@pytest.mark.parametrize("options", [{"max_banners": 2, "evict": False}])
async def test_eviction_off_rejects(entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(id="a", message="x", severity="success")
    await create(id="b", message="x", severity="success")
    with pytest.raises(ServiceValidationError) as err:
        await create(id="c", message="x")
    assert err.value.translation_key == "too_many_banners"
