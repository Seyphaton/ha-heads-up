"""The admin preview command and the options of the hub objects."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .helpers import set_person


async def preview(client: Any, audience: str, severity: str | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"type": "heads_up/hub_preview_audience", "audience": audience}
    if severity:
        msg["severity"] = severity
    await client.send_json_auto_id(msg)
    return dict(await client.receive_json())


async def test_preview_lists_members_and_skipped_with_reasons(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", None)
    client = await hass_ws_client(hass)
    reply = await preview(client, "At home")
    assert reply["success"]
    assert reply["result"] == {
        "members": [{"person": "person.anna", "reason": "state:home"}],
        "skipped": [{"person": "person.ben", "reason": "presence_unknown"}],
    }
    critical = await preview(client, "At home", "critical")
    assert {m["person"] for m in critical["result"]["members"]} == {"person.anna", "person.ben"}


async def test_preview_of_an_unknown_audience_is_not_found(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await preview(client, "Nobody")
    assert reply["error"]["code"] == "not_found"


async def test_preview_needs_an_admin(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    reply = await preview(client, "Everyone")
    assert reply["error"]["code"] == "unauthorized"


async def test_the_debounce_option_has_a_default_and_a_range(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert entry.runtime_data.options["presence_debounce_seconds"] == 60
