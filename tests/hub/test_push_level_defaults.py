"""Default push levels (D-230): new setups get the new ones, existing setups keep theirs."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DEFAULT_PUSH_LEVELS, DOMAIN, PUSH_LEVELS_1_0


def test_the_defaults_for_new_setups() -> None:
    assert DEFAULT_PUSH_LEVELS == {
        "critical": "critical",
        "warning": "time-sensitive",
        "info": "normal",
        "passive": "passive",
    }


async def setup(hass: HomeAssistant, **kw: object) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, **kw)  # type: ignore[arg-type]
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_a_new_setup_stores_no_levels_and_uses_the_new_defaults(hass: HomeAssistant) -> None:
    entry = await setup(hass, version=2, minor_version=4, options={})
    assert "push_levels" not in entry.options
    push = entry.runtime_data.hub.channels.get("push")
    assert push._opt("push_levels") == DEFAULT_PUSH_LEVELS


async def test_an_existing_setup_keeps_the_levels_it_had(hass: HomeAssistant) -> None:
    entry = await setup(hass, version=2, minor_version=2, options={})
    assert (entry.version, entry.minor_version) == (3, 2)
    assert entry.options["push_levels"] == PUSH_LEVELS_1_0


async def test_levels_an_existing_setup_saved_stay(hass: HomeAssistant) -> None:
    saved = {"passive": "passive", "info": "passive", "warning": "normal", "critical": "critical"}
    entry = await setup(hass, version=2, minor_version=2, options={"push_levels": saved})
    assert entry.options["push_levels"] == saved
