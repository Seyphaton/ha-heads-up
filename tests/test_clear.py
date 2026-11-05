"""clear_notifications and the deprecated clear_banner and clear_all (DESIGN §7, D-158)."""

import logging

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


async def three(hass: HomeAssistant, create: CreateBanner) -> None:
    """A banner, a bell-only message (no banner channel) and a banner plus bell message."""
    await create(id="card", message="x", severity="info", tag="t")
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "bell", "message": "x", "severity": "critical", "channels": ["persistent"]},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "both",
            "message": "x",
            "severity": "critical",
            "tag": "t",
            "channels": ["banner", "persistent"],
        },
        blocking=True,
    )


async def test_clear_notifications_removes_messages_without_a_banner_too(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await three(hass, create)
    assert await clear(hass, "clear_notifications", id="bell") == {"cleared": 1}
    assert set(banners(entry)) == {"card", "both"}


async def test_clear_notifications_filters_combine_with_and(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await three(hass, create)
    assert await clear(hass, "clear_notifications", severity="critical", tag="t") == {"cleared": 1}
    assert set(banners(entry)) == {"card", "bell"}
    assert await clear(hass, "clear_notifications", severity=["info", "warning"]) == {"cleared": 1}
    assert set(banners(entry)) == {"bell"}


async def test_clear_notifications_by_channel(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await three(hass, create)
    assert await clear(hass, "clear_notifications", channels=["persistent"]) == {"cleared": 2}
    assert set(banners(entry)) == {"card"}
    assert await clear(hass, "clear_notifications", channels=["push", "popup"]) == {"cleared": 0}


async def test_clear_notifications_all(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await three(hass, create)
    assert await clear(hass, "clear_notifications", all=True) == {"cleared": 3}
    assert banners(entry) == {}


@pytest.mark.parametrize(
    "data",
    [{}, {"all": False}, {"all": True, "tag": "t"}, {"severity": "urgent"}, {"channels": []}],
)
async def test_clear_notifications_needs_a_filter_or_all(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, data: dict[str, object]
) -> None:
    await three(hass, create)
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "clear_notifications", data, blocking=True)
    assert len(banners(entry)) == 3


async def test_clear_action_no_longer_exists(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert not hass.services.has_service(DOMAIN, "clear")


async def test_deprecated_actions_warn_once_and_keep_working(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING)
    await three(hass, create)
    await clear(hass, "clear_banner", id="card")
    await clear(hass, "clear_banner", id="both")
    assert await clear(hass, "clear_all") == {"cleared": 1}
    warnings = [r.getMessage() for r in caplog.records if "deprecated" in r.getMessage()]
    assert len(warnings) == 2
    assert "heads_up.clear_banner" in warnings[0] and "clear_notifications" in warnings[0]
    assert "heads_up.clear_all" in warnings[1]
