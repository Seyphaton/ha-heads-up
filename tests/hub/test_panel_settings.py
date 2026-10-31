"""Settings commands: admin only, read, write, presets (D-117)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import AddDevice
from .helpers import set_person


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


def policies(entry: MockConfigEntry) -> dict[str, dict[str, Any]]:
    return {s.title: dict(s.data) for s in entry.subentries.values() if s.subentry_type == "policy"}


async def test_every_settings_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    for command, data in (
        ("settings_get", {}),
        ("settings_set", {"hub_enabled": True}),
    ):
        assert (await ask(client, command, **data))["error"]["code"] == "unauthorized"
    assert not policies(entry)


async def test_get_returns_the_editable_options_ranges_and_the_token(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_get"))["result"]
    assert result["options"] == {
        "hub_enabled": True,
        "show_panel": False,
        "rate_per_device_per_minute": 10,
        "rate_total_per_minute": 60,
        "dedupe_seconds": 30,
        "trace_entries": 500,
        "recent_messages": 100,
    }
    assert result["ranges"]["trace_entries"] == [50, 5000]
    assert result["install_token"] == entry.options["install_token"]


async def test_set_writes_the_integration_options_and_keeps_the_others(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_set", show_panel=True, trace_entries=800)
    assert reply["success"] and reply["result"]["options"]["trace_entries"] == 800
    assert entry.options["show_panel"] is True and entry.options["trace_entries"] == 800
    assert entry.options["install_token"]
    assert entry.runtime_data.hub.trace.entries("x") == []  # the trace buffer was resized live


async def test_a_value_outside_its_range_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_set", trace_entries=10)
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"
    assert entry.options.get("trace_entries", 500) == 500


async def test_the_hub_switch_works_from_settings(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "settings_set", hub_enabled=False)
    await hass.async_block_till_done()
    assert entry.runtime_data.hub is None
    await ask(client, "settings_set", hub_enabled=True)
    await hass.async_block_till_done()
    assert entry.runtime_data.hub is not None


async def test_the_people_summary_counts_usable_devices_and_users(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    mobile_app_device: AddDevice,
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    set_person(hass, "person.ben", "home")
    await mobile_app_device("Anna's phone", user_id="anna-id", person_entity_id="person.anna")
    client = await hass_ws_client(hass)
    people = {p["person"]: p for p in (await ask(client, "settings_get"))["result"]["people"]}
    assert people["person.anna"]["devices"] == 1 and people["person.anna"]["user"] is True
    assert people["person.ben"]["devices_total"] == 0 and people["person.ben"]["user"] is False
