"""WebSocket API: subscribe, dismiss, admin clear (DESIGN §6, D-007, D-011, D-029)."""

from typing import Any

from homeassistant.auth.models import User
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners


async def subscribe(client: Any, **extra: Any) -> tuple[int, list[dict[str, Any]]]:
    await client.send_json_auto_id({"type": "heads_up/subscribe", **extra})
    result = await client.receive_json()
    assert result["success"], result
    event = await client.receive_json()
    return result["id"], event["event"]["banners"]


async def next_list(client: Any) -> list[dict[str, Any]]:
    msg = await client.receive_json()
    assert msg["type"] == "event"
    return msg["event"]["banners"]


async def test_subscribe_sends_list_then_updates(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="hello", title="T", severity="info", tag="g")
    client = await hass_ws_client(hass)

    _, initial = await subscribe(client)
    assert [b["id"] for b in initial] == ["a"]
    item = initial[0]
    assert item["message"] == "hello" and item["title"] == "T" and item["severity"] == "info"
    assert item["icon"] == "mdi:information"  # per-severity default resolved for the card
    assert "dismissed_by" not in item  # other users' IDs are never sent

    await create(id="b", message="second")
    assert {b["id"] for b in await next_list(client)} == {"a", "b"}


async def test_user_dismiss_hides_only_for_that_user(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
    hass_read_only_access_token: str,
) -> None:
    await create(id="a", message="x")
    events = async_capture_events(hass, f"{DOMAIN}_banner_dismissed")
    admin = await hass_ws_client(hass)
    other = await hass_ws_client(hass, hass_read_only_access_token)
    await subscribe(other)

    await admin.send_json_auto_id({"type": "heads_up/dismiss", "banner_id": "a"})
    assert (await admin.receive_json())["success"]

    assert "a" in banners(entry)
    assert banners(entry)["a"].dismissed_by == [hass_admin_user.id]
    _, admin_view = await subscribe(admin)
    assert admin_view == []
    assert [b["id"] for b in await next_list(other)] == ["a"]
    assert events[0].data == {
        "id": "a",
        "tag": None,
        "scope": "user",
        "user_id": hass_admin_user.id,
    }


async def test_global_dismiss_removes_banner(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    await create(id="a", message="x", dismiss_scope="global")
    other = await hass_ws_client(hass, hass_read_only_access_token)

    await other.send_json_auto_id({"type": "heads_up/dismiss", "banner_id": "a"})
    assert (await other.receive_json())["success"]
    assert banners(entry) == {}


async def test_dismiss_errors(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="fixed", message="x", dismissible=False)
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "heads_up/dismiss", "banner_id": "fixed"})
    assert (await client.receive_json())["error"]["code"] == "not_dismissible"
    await client.send_json_auto_id({"type": "heads_up/dismiss", "banner_id": "missing"})
    assert (await client.receive_json())["error"]["code"] == "not_found"


async def test_admin_clear_requires_admin(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    await create(id="fixed", message="x", dismissible=False, timeout=0)
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")
    other = await hass_ws_client(hass, hass_read_only_access_token)
    admin = await hass_ws_client(hass)

    await other.send_json_auto_id({"type": "heads_up/admin_clear", "banner_id": "fixed"})
    assert (await other.receive_json())["error"]["code"] == "unauthorized"
    assert "fixed" in banners(entry)

    await admin.send_json_auto_id({"type": "heads_up/admin_clear", "banner_id": "fixed"})
    assert (await admin.receive_json())["success"]
    assert banners(entry) == {}
    assert events[0].data["reason"] == "admin"


async def test_show_all_requires_admin_and_includes_dismissed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
    hass_read_only_access_token: str,
) -> None:
    await create(id="a", message="x")
    entry.runtime_data.dismiss("a", hass_admin_user.id)

    other = await hass_ws_client(hass, hass_read_only_access_token)
    await other.send_json_auto_id({"type": "heads_up/subscribe", "show_all": True})
    assert (await other.receive_json())["error"]["code"] == "unauthorized"

    admin = await hass_ws_client(hass)
    _, view = await subscribe(admin, show_all=True)
    assert [(b["id"], b["dismissed"]) for b in view] == [("a", True)]


async def test_subscription_ends_with_connection(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    await subscribe(client)
    assert len(entry.runtime_data._listeners) == 2  # sensor + this subscription
    await client.close()
    await hass.async_block_till_done()
    assert len(entry.runtime_data._listeners) == 1
