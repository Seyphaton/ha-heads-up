"""People targeting, filtered server-side (D-008)."""

from typing import Any

from homeassistant.auth.models import User
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .conftest import CreateBanner


async def view(client: Any, **extra: Any) -> list[str]:
    await client.send_json_auto_id({"type": "heads_up/subscribe", **extra})
    assert (await client.receive_json())["success"]
    return sorted(b["id"] for b in (await client.receive_json())["event"]["banners"])


async def test_targeted_banner_reaches_only_that_person(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
    hass_read_only_user: User,
    hass_read_only_access_token: str,
) -> None:
    hass.states.async_set("person.admin", "home", {"user_id": hass_admin_user.id})
    hass.states.async_set("person.reader", "home", {"user_id": hass_read_only_user.id})
    await create(id="all", message="x")
    await create(id="for_reader", message="x", people=["person.reader"])
    await create(id="for_both", message="x", people=["person.admin", "person.reader"])

    admin = await hass_ws_client(hass)
    reader = await hass_ws_client(hass, hass_read_only_access_token)
    assert await view(admin) == ["all", "for_both"]
    assert await view(reader) == ["all", "for_both", "for_reader"]
    assert await view(admin, show_all=True) == ["all", "for_both", "for_reader"]


async def test_user_without_person_sees_untargeted_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    hass.states.async_set("person.someone", "home", {"user_id": "another-user"})
    await create(id="all", message="x")
    await create(id="targeted", message="x", people=["person.someone"])
    assert await view(await hass_ws_client(hass)) == ["all"]


async def test_person_created_later_matches(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
) -> None:
    await create(id="t", message="x", people=["person.new"])
    client = await hass_ws_client(hass)
    assert await view(client) == []

    hass.states.async_set("person.new", "home", {"user_id": hass_admin_user.id})
    await hass.async_block_till_done()
    msg = await client.receive_json()
    assert [b["id"] for b in msg["event"]["banners"]] == ["t"]


async def test_payload_does_not_expose_targeting(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
) -> None:
    hass.states.async_set("person.admin", "home", {"user_id": hass_admin_user.id})
    await create(
        id="t",
        message="x",
        people=["person.admin"],
        condition={"entity_id": "person.admin", "state": "home"},
    )
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/subscribe"})
    await client.receive_json()
    item = (await client.receive_json())["event"]["banners"][0]
    assert "people" not in item and "condition" not in item and "dismissed_by" not in item
