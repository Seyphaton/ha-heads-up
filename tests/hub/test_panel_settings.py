"""Settings commands: admin only, read, write, presets (D-117)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import AddDevice
from .helpers import set_person
from .policy_support import QUIET, add_policy


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
        ("settings_apply_preset", {"preset": "quiet"}),
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


async def test_the_presets_list_what_each_would_add(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(hass, entry, "Night quiet", **QUIET)
    client = await hass_ws_client(hass)
    overview = {p["id"]: p for p in (await ask(client, "settings_get"))["result"]["presets"]}
    assert overview["quiet"]["missing"] == []
    assert overview["balanced"]["missing"] == ["Water escalation", "Evening summary"]
    assert len(overview["loud"]["policies"]) == 5


async def test_applying_a_preset_adds_its_policies(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_apply_preset", preset="balanced"))["result"]
    assert result == {
        "added": ["Night quiet", "Water escalation", "Evening summary"],
        "skipped": [],
    }
    await hass.async_block_till_done()
    assert set(policies(entry)) == {"Night quiet", "Water escalation", "Evening summary"}
    assert set(entry.runtime_data.hub.policies.names()) == set(policies(entry))


async def test_applying_a_preset_never_changes_an_existing_policy(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    custom = {**QUIET, "from_time": "23:30:00", "action": "drop"}
    await add_policy(hass, entry, "Night quiet", **custom)
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_apply_preset", preset="quiet"))["result"]
    assert result == {"added": [], "skipped": [{"name": "Night quiet", "reason": "exists"}]}
    assert policies(entry)["Night quiet"]["from_time"] == "23:30:00"


async def test_a_policy_that_does_the_same_under_another_name_is_skipped(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(
        hass,
        entry,
        "My nights",
        type="quiet_hours",
        from_time="22:00:00",
        to_time="07:00:00",
        days=[],
    )
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_apply_preset", preset="quiet"))["result"]
    assert result["skipped"] == [{"name": "Night quiet", "reason": "duplicate"}]


async def test_a_loud_preset_adds_all_five_and_a_second_run_adds_none(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    first = (await ask(client, "settings_apply_preset", preset="loud"))["result"]
    assert len(first["added"]) == 5
    await hass.async_block_till_done()
    second = (await ask(client, "settings_apply_preset", preset="loud"))["result"]
    assert second["added"] == [] and len(second["skipped"]) == 5


async def test_the_presets_are_valid_for_the_policy_form(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub.policies.models import policy_from_data
    from custom_components.heads_up.hub.presets import POLICIES

    for name, data in POLICIES.items():
        policy = policy_from_data(name, "x", data)
        assert policy is not None and policy.type == data["type"]
