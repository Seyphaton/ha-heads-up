"""The panel sidebar entry: off by default, added and removed with the option (D-117)."""

from typing import Any

from homeassistant import config_entries
from homeassistant.components.frontend import DATA_PANELS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.heads_up.const import DOMAIN


def panel(hass: HomeAssistant) -> Any:
    return hass.data.get(DATA_PANELS, {}).get("heads-up")


async def switch(hass: HomeAssistant, entry: MockConfigEntry, show: bool) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "show_panel": show})
    await hass.async_block_till_done()


async def test_there_is_no_sidebar_entry_by_default(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert panel(hass) is None


async def test_switching_it_on_adds_an_admin_only_entry_without_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await switch(hass, entry, True)
    found = panel(hass)
    assert found is not None
    assert found.sidebar_title == "Heads Up" and found.sidebar_icon == "mdi:bell-ring-outline"
    assert found.require_admin is True and found.component_name == "custom"


async def test_the_panel_config_names_the_element_and_a_hashed_module(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await switch(hass, entry, True)
    config = panel(hass).config
    custom = config["_panel_custom"]
    assert custom["name"] == "heads-up-panel" and custom["embed_iframe"] is False
    assert custom["module_url"].startswith("/heads_up/heads-up-panel.js?v=")
    assert config["base"] == "/heads_up/panel" and config["v"] in custom["module_url"]


async def test_switching_it_off_removes_the_entry(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await switch(hass, entry, True)
    await switch(hass, entry, False)
    assert panel(hass) is None


async def test_unloading_removes_the_entry_and_reloading_brings_it_back(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await switch(hass, entry, True)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert panel(hass) is None
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert panel(hass) is not None


async def test_saving_the_same_value_twice_does_not_register_twice(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await switch(hass, entry, True)
    hass.config_entries.async_update_entry(entry, options={**entry.options, "trace_entries": 600})
    await hass.async_block_till_done()
    assert panel(hass) is not None


async def test_the_shell_and_a_page_are_served_and_cached(
    hass: HomeAssistant, entry: MockConfigEntry, hass_client: ClientSessionGenerator
) -> None:
    client = await hass_client()
    for path, marker in (
        ("/heads_up/heads-up-panel.js", "heads-up-panel"),
        ("/heads_up/panel/settings.js", "export function mount"),
    ):
        response = await client.get(path)
        assert response.status == 200 and marker in await response.text()
        assert "max-age" in response.headers["Cache-Control"]


async def test_the_setup_flow_asks_about_the_sidebar_and_starts_on(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["data_schema"] is not None
    assert [str(k) for k in result["data_schema"].schema] == ["show_panel"]
    created = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert created["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert panel(hass) is not None


async def test_the_setup_flow_can_leave_the_sidebar_off(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    created = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"show_panel": False}
    )
    assert created["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert panel(hass) is None


async def test_the_options_form_has_the_switch(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "show_panel" in [str(k) for k in result["data_schema"].schema]
    done = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"show_panel": True, "max_banners": 50, "evict": True, "default_dismiss_scope": "user"},
    )
    assert done["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert panel(hass) is not None
