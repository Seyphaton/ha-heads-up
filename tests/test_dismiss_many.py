"""heads_up/dismiss_many: the card's "Clear all" button (D-048)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners
from .test_websocket import next_list, subscribe


async def dismiss_many(
    client: Any, ids: list[str], updates: list[list[dict[str, Any]]] | None = None
) -> dict[str, Any]:
    """Send the command; list updates that arrive before the result go into `updates`."""
    await client.send_json_auto_id({"type": "heads_up/dismiss_many", "banner_ids": ids})
    msg: dict[str, Any] = await client.receive_json()
    while msg["type"] == "event":
        if updates is not None:
            updates.append(msg["event"]["banners"])
        msg = await client.receive_json()
    return msg


async def test_dismisses_for_the_caller_only_and_notifies_once(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    for banner_id in ("a", "b", "c"):
        await create(id=banner_id, message="x")
    client = await hass_ws_client(hass)
    await subscribe(client)
    events = async_capture_events(hass, f"{DOMAIN}_banner_dismissed")

    updates: list[list[dict[str, Any]]] = []
    result = await dismiss_many(client, ["a", "b"], updates)
    assert result["success"] and result["result"] == {"dismissed": 2, "skipped": 0}
    assert len(updates) == 1  # one update for the whole batch
    assert [b["id"] for b in updates[0]] == ["c"]  # the viewer no longer receives dismissed ones
    assert sorted(e.data["id"] for e in events) == ["a", "b"]
    assert set(banners(entry)) == {"a", "b", "c"}  # per-user scope keeps them stored

    await create(id="d", message="later")
    assert {b["id"] for b in await next_list(client)} == {"c", "d"}  # no extra message in between


async def test_global_scope_banners_are_removed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="g", message="x", dismiss_scope="global")
    await create(id="u", message="x")
    client = await hass_ws_client(hass)
    await dismiss_many(client, ["g", "u"])
    assert set(banners(entry)) == {"u"}


async def test_skips_non_dismissible_and_unknown_ids(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="fixed", message="x", dismissible=False)
    await create(id="ok", message="x")
    client = await hass_ws_client(hass)

    result = await dismiss_many(client, ["fixed", "missing", "ok"])
    assert result["success"] and result["result"] == {"dismissed": 1, "skipped": 2}
    assert "fixed" in banners(entry) and not banners(entry)["fixed"].dismissed_by


async def test_empty_list_changes_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    result = await dismiss_many(client, [])
    assert result["success"] and result["result"] == {"dismissed": 0, "skipped": 0}


async def test_requires_a_loaded_entry(
    hass: HomeAssistant, hass_ws_client: WebSocketGenerator, entry: MockConfigEntry
) -> None:
    assert await hass.config_entries.async_unload(entry.entry_id)
    client = await hass_ws_client(hass)
    result = await dismiss_many(client, ["a"])
    assert not result["success"] and result["error"]["code"] == "not_loaded"
