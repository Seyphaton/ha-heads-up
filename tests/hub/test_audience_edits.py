"""Editing a built-in audience in place (D-257)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .helpers import set_person


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def members(hass: HomeAssistant, entry: MockConfigEntry, kind: str) -> list[str]:
    resolver = entry.runtime_data.hub.resolver
    found = await resolver.members(resolver.audience(kind), "warning")
    return [r.key for r in found.recipients]


async def test_leaving_a_person_out_changes_who_the_audience_reaches(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="a")
    set_person(hass, "person.ben", "home", user_id="b")
    assert await members(hass, entry, "everyone") == ["person.anna", "person.ben"]
    client = await hass_ws_client(hass)
    reply = await ask(client, "audience_edit", name="Everyone", exclude=["person.ben"])
    assert reply["success"], reply
    await hass.async_block_till_done()
    assert await members(hass, entry, "everyone") == ["person.anna"]


async def test_a_presence_audience_can_be_limited_to_named_people(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="a")
    set_person(hass, "person.ben", "home", user_id="b")
    client = await hass_ws_client(hass)
    assert (await ask(client, "audience_edit", name="At home", limit=["person.anna"]))["success"]
    await hass.async_block_till_done()
    assert await members(hass, entry, "at_home") == ["person.anna"]


async def test_only_presence_audiences_take_a_limit(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "audience_edit", name="Everyone", limit=["person.anna"])
    assert reply["error"]["code"] == "invalid_format"
    assert "audience_edits" not in entry.options


async def test_an_unknown_audience_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "audience_edit", name="Nope"))["error"]["code"] == "not_found"
    assert (await ask(client, "audience_reset", name="Nope"))["error"]["code"] == "not_found"


async def test_reset_restores_the_shipped_audience(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="a")
    set_person(hass, "person.ben", "home", user_id="b")
    client = await hass_ws_client(hass)
    await ask(client, "audience_edit", name="Everyone", exclude=["person.ben"])
    assert (await ask(client, "audience_reset", name="Everyone"))["success"]
    await hass.async_block_till_done()
    assert await members(hass, entry, "everyone") == ["person.anna", "person.ben"]
    assert entry.options["audience_edits"] == {}


async def test_an_empty_edit_is_the_shipped_audience(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "audience_edit", name="Everyone", exclude=["person.ben"])
    await ask(client, "audience_edit", name="Everyone")
    assert entry.options["audience_edits"] == {}


async def test_the_panel_config_marks_an_edited_built_in_and_its_sensor_follows(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="a")
    set_person(hass, "person.ben", "home", user_id="b")
    client = await hass_ws_client(hass)
    await ask(client, "audience_edit", name="Everyone", exclude=["person.ben"])
    await hass.async_block_till_done()
    reply = await ask(client, "panel_config")
    audiences = {a["name"]: a for a in reply["result"]["audiences"]}
    assert audiences["Everyone"]["edited"] is True
    assert audiences["Everyone"]["edit"] == {"exclude": ["person.ben"], "limit": []}
    assert audiences["Everyone"]["members"] == ["person.anna"]
    assert audiences["Everyone"]["limitable"] is False and audiences["At home"]["limitable"] is True
    assert audiences["Admins"]["edited"] is False
    state = hass.states.get("binary_sensor.heads_up_audience_everyone")
    assert state is not None and state.attributes["members"] == ["person.anna"]
