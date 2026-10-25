"""A readable file with a damaged banner must not stop the integration (D-044, DESIGN §10).

Undecodable files are handled by HA's Store (N-45); the test plugin mocks storage, so that
case is checked on the dev HA, not here.
"""

from typing import Any

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import CreateBanner, banners

KEY = "heads_up.banners"


@pytest.mark.parametrize(
    "bad",
    [
        {"id": "no-times", "message": "x"},
        "not an object",
        {"id": "extra", "message": "x", "unknown_field": 1, "created_at": "x", "updated_at": "x"},
        {"id": "bad-time", "message": "x", "created_at": "yesterday", "updated_at": "now"},
    ],
)
async def test_malformed_banner_in_storage_is_skipped_and_logged(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    entry: MockConfigEntry,
    create: CreateBanner,
    bad: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    await create(id="good", message="kept", timeout=0)
    good = entry.runtime_data.banners["good"].to_dict()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    hass_storage[KEY] = {
        "version": 1,
        "minor_version": 1,
        "key": KEY,
        "data": {"banners": [bad, good]},
    }

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert set(banners(entry)) == {"good"}
    assert "Skipping unreadable banner" in caplog.text
