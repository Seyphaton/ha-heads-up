"""Hub options: switch, install token, limits (D-107, D-080)."""

import re

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..conftest import options_input


async def test_hub_is_on_by_default(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert entry.runtime_data.options["hub_enabled"] is True
    assert entry.runtime_data.hub is not None


async def test_install_token_is_six_hex_characters_generated_once(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    token = entry.options["install_token"]
    assert re.fullmatch(r"[0-9a-f]{6}", token)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.options["install_token"] == token


async def test_limit_and_history_defaults_are_stored(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    options = entry.runtime_data.options
    assert (options["rate_per_device_per_minute"], options["rate_total_per_minute"]) == (10, 60)
    assert options["dedupe_seconds"] == 30
    assert (options["trace_entries"], options["recent_messages"]) == (500, 100)


async def test_options_flow_switches_the_hub_off_and_keeps_the_token(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    token = entry.options["install_token"]
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        options_input({"hub": {"hub_enabled": False}}),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options["install_token"] == token
    assert entry.options["hub_enabled"] is False
    assert entry.runtime_data.hub is None
