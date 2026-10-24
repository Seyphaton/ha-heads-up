"""Count sensor (D-013) and options flow (D-026, D-031)."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import CreateBanner, banners

SENSOR = "sensor.heads_up_active_banners"


async def test_count_sensor_follows_banners(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    assert hass.states.get(SENSOR).state == "0"
    await create(id="a", message="x")
    await create(id="b", message="x")
    await hass.async_block_till_done()
    assert hass.states.get(SENSOR).state == "2"
    assert set(hass.states.get(SENSOR).attributes) <= {"friendly_name", "icon"}

    await hass.services.async_call("heads_up", "clear_all", {}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get(SENSOR).state == "0"


async def test_options_flow_sets_defaults_for_new_banners(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="before", message="x")

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "max_banners": 10,
            "evict": False,
            "default_dismiss_scope": "global",
            "default_timeout": {"hours": 1},
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.options == {
        "max_banners": 10,
        "evict": False,
        "default_dismiss_scope": "global",
        "default_timeout": 3600,
    }

    await create(id="after", message="x")
    after = banners(entry)["after"]
    assert after.dismiss_scope == "global"
    assert after.expires_at == after.updated_at + timedelta(hours=1)
    before = banners(entry)["before"]
    assert before.dismiss_scope == "user"  # options apply to new banners only


async def test_cleared_default_timeout_means_no_expiry(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"max_banners": 50, "evict": True, "default_dismiss_scope": "user"},
    )
    await hass.async_block_till_done()
    await create(id="a", message="x")
    assert banners(entry)["a"].expires_at is None
