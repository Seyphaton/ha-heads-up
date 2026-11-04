"""Count sensor (D-013) and options flow (D-026, D-031)."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import CreateBanner, banners, options_input

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
        options_input(
            {
                "limits": {"max_banners": 10, "evict": False},
                "dismiss": {"default_dismiss_scope": "global", "default_timeout": {"hours": 1}},
                "snooze": {"default_snoozable": False, "default_snooze_scope": "user"},
                "snooze_banner": {"default_snooze_options": ["15", "60", "240"]},
            }
        ),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    token = entry.options["install_token"]
    assert len(token) == 6  # generated at setup, kept by the options flow
    assert entry.options == {
        "install_token": token,
        "policy_order": [],
        "presence_debounce_seconds": 60,
        "show_panel": False,
        "speak_max_length": 200,
        "speak_cooldown_seconds": 60,
        "speak_tts_entity": "",
        "max_banners": 10,
        "evict": False,
        "default_dismiss_scope": "global",
        "default_timeout": 3600,
        "default_snoozable": False,
        "default_snooze_scope": "user",
        "default_snooze_options": [900, 3600, 14400],
        "quick_snooze_minutes": 15,
        "disable_ended_buttons": True,
        "rate_per_device_per_minute": 5,
        "rate_total_per_minute": 60,
        "dedupe_seconds": 30,
        "trace_entries": 500,
        "recent_messages": 100,
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
        options_input(
            {
                "limits": {"max_banners": 50, "evict": True},
                "dismiss": {"default_dismiss_scope": "user"},
            }
        ),
    )
    await hass.async_block_till_done()
    await create(id="a", message="x")
    assert banners(entry)["a"].expires_at is None


async def test_options_screen_has_the_sections_and_entries_of_the_panel_in_the_same_order(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub import settings

    result = await hass.config_entries.options.async_init(entry.entry_id)
    schema = result["data_schema"].schema
    assert [str(name) for name in schema] == [name for name, _ in settings.SECTIONS]
    for (name, items), section in zip(settings.SECTIONS, schema.values(), strict=True):
        assert [str(key) for key in section.schema.schema] == [key for key, _ in items], name
    assert entry.options["install_token"] in result["description_placeholders"]["install_token"]


async def test_options_screen_refuses_a_timeout_over_the_limit(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], options_input({"dismiss": {"default_timeout": {"days": 366}}})
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"default_timeout": "timeout_too_long"}
    assert "default_timeout" not in entry.options  # nothing was saved


async def test_a_value_saved_in_the_options_screen_shows_in_the_panel_data(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub import settings

    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"],
        options_input(
            {
                "speech": {"speak_max_length": 120},
                "limits": {"rate_total_per_minute": 90},
                "history": {"trace_entries": 700},
            }
        ),
    )
    await hass.async_block_till_done()
    values = settings.read_options(entry.runtime_data)
    assert (
        values["speak_max_length"],
        values["rate_total_per_minute"],
        values["trace_entries"],
    ) == (
        120,
        90,
        700,
    )
