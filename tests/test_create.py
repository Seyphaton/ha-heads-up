"""create_banner: defaults, validation, upsert (DESIGN §4, D-010, D-030, D-031)."""

from datetime import timedelta

import pytest
import voluptuous as vol  # probatio shim once homeassistant is imported (HA_API_NOTES N-24)
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners


async def test_minimal_call_creates_banner_with_defaults(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    result = await create(message="Hello")

    assert result["status"] == "created"
    assert result["id"].startswith("hu_") and len(result["id"]) == 13
    banner = banners(entry)[result["id"]]
    assert banner.severity == "warning"
    assert banner.icon is None  # card resolves the per-severity default
    assert banner.dismissible is True
    assert banner.dismiss_scope == "user"
    assert banner.expires_at == banner.updated_at + timedelta(hours=24)


async def test_call_without_return_response_works(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await hass.services.async_call(
        DOMAIN, "create_banner", {"id": "plain", "message": "x"}, blocking=True
    )
    assert "plain" in banners(entry)


async def test_all_fields_are_stored(entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(
        id="leak",
        message="Water leak",
        title="Basement",
        severity="critical",
        icon="mdi:water-alert",
        timeout=600,
        dismissible=False,
        dismiss_scope="global",
        tag="safety",
        tap_action={"action": "navigate", "navigation_path": "/lovelace/0"},
    )
    b = banners(entry)["leak"]
    assert (b.title, b.severity, b.icon, b.tag) == (
        "Basement",
        "critical",
        "mdi:water-alert",
        "safety",
    )
    assert (b.dismissible, b.dismiss_scope) == (False, "global")
    assert b.tap_action == {"action": "navigate", "navigation_path": "/lovelace/0"}
    assert b.expires_at == b.updated_at + timedelta(seconds=600)


async def test_duration_timeout(entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(id="d", message="x", timeout={"minutes": 5})
    b = banners(entry)["d"]
    assert b.expires_at == b.updated_at + timedelta(minutes=5)


async def test_timeout_zero_means_no_expiry(entry: MockConfigEntry, create: CreateBanner) -> None:
    await create(id="forever", message="x", timeout=0)
    assert banners(entry)["forever"].expires_at is None


@pytest.mark.parametrize(
    "data",
    [
        {"message": ""},
        {"message": "x" * 1001},
        {"message": "x", "title": "t" * 101},
        {"message": "x", "id": "Has Space"},
        {"message": "x", "id": "a" * 65},
        {"message": "x", "tag": "UPPER"},
        {"message": "x", "severity": "fatal"},
        {"message": "x", "icon": "no-prefix"},
        {"message": "x", "timeout": -1},
        {"message": "x", "timeout": {"days": 366}},
        {"message": "x", "dismiss_scope": "device"},
        {"message": "x", "tap_action": {"navigation_path": "/x"}},
        {"title": "no message"},
    ],
)
async def test_invalid_input_is_rejected(
    hass: HomeAssistant, entry: MockConfigEntry, data: dict[str, object]
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "create_banner", data, blocking=True)
    assert banners(entry) == {}


async def test_upsert_replaces_fields_keeps_created_at_and_resets_dismissals(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    created = await create(id="w", message="first", severity="info", timeout=60)
    first = banners(entry)["w"]
    created_at = first.created_at
    entry.runtime_data.dismiss("w", "user-1")
    events = async_capture_events(hass, f"{DOMAIN}_banner_updated")

    freezer.tick(timedelta(seconds=30))
    result = await create(id="w", message="second")

    assert created["status"] == "created"
    assert result == {"id": "w", "status": "updated"}
    b = banners(entry)["w"]
    assert b.message == "second"
    assert b.severity == "warning"  # replaced, not merged
    assert b.created_at == created_at
    assert b.updated_at == dt_util.utcnow()
    assert b.expires_at == b.updated_at + timedelta(hours=24)
    assert b.dismissed_by == []
    assert len(events) == 1
    assert events[0].data == {"id": "w", "severity": "warning", "tag": None}


async def test_created_event(hass: HomeAssistant, create: CreateBanner) -> None:
    events = async_capture_events(hass, f"{DOMAIN}_banner_created")
    await create(id="e", message="x", severity="critical", tag="t")
    assert [e.data for e in events] == [{"id": "e", "severity": "critical", "tag": "t"}]


async def test_actions_fail_when_entry_not_loaded(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(DOMAIN, "create_banner", {"message": "x"}, blocking=True)
    assert err.value.translation_key == "not_loaded"
