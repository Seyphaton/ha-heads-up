"""Banner buttons: validation, event, dismiss, permissions (DESIGN §21, D-070)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners
from .test_websocket import subscribe

BUTTONS = [
    {"key": "ack", "label": "Got it", "dismiss": True},
    {"key": "later", "label": "Later", "action": {"action": "navigate", "navigation_path": "/x"}},
]


async def press(client: Any, banner_id: str, key: str) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/action", "banner_id": banner_id, "key": key})
    return await client.receive_json()


async def test_buttons_reach_the_card_with_defaults(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    client = await hass_ws_client(hass)
    _, shown = await subscribe(client)
    assert shown[0]["actions"] == [
        {"key": "ack", "label": "Got it", "dismiss": True},
        {
            "key": "later",
            "label": "Later",
            "dismiss": False,
            "action": {"action": "navigate", "navigation_path": "/x"},
        },
    ]


async def test_pressing_a_button_fires_an_event_with_the_user(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    await create(id="a", message="x", tag="g", actions=BUTTONS)
    events = async_capture_events(hass, f"{DOMAIN}_banner_action")
    client = await hass_ws_client(hass)
    assert (await press(client, "a", "later"))["success"]
    await hass.async_block_till_done()
    assert [e.data for e in events] == [
        {"id": "a", "tag": "g", "key": "later", "user_id": hass_admin_user.id}
    ]
    assert "a" in banners(entry)  # a button without dismiss keeps the banner


async def test_dismiss_button_dismisses_for_the_user(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    dismissed = async_capture_events(hass, f"{DOMAIN}_banner_dismissed")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/action", "banner_id": "a", "key": "ack"})
    assert (await client.receive_json())["success"]
    await hass.async_block_till_done()
    assert banners(entry)["a"].dismissed_by == [hass_admin_user.id]
    assert len(dismissed) == 1


async def test_unknown_button_key_fails(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    client = await hass_ws_client(hass)
    assert (await press(client, "a", "nope"))["error"]["code"] == "unknown_action"
    assert (await press(client, "missing", "ack"))["error"]["code"] == "not_found"


async def test_user_cannot_press_a_button_of_a_banner_targeted_at_someone_else(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", actions=BUTTONS, people=["person.nobody"])
    events = async_capture_events(hass, f"{DOMAIN}_banner_action")
    client = await hass_ws_client(hass)
    assert (await press(client, "a", "ack"))["error"]["code"] == "not_found"
    assert events == []


async def test_upsert_replaces_the_buttons(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", actions=BUTTONS)
    await create(id="a", message="x")
    client = await hass_ws_client(hass)
    assert (await press(client, "a", "ack"))["error"]["code"] == "unknown_action"


@pytest.mark.parametrize(
    "actions",
    [
        [{"key": "k", "label": ""}],
        [{"key": "Bad Key", "label": "x"}],
        [{"key": "k", "label": "x" * 41}],
        [{"key": "k", "label": "x"}, {"key": "k", "label": "y"}],
        [{"key": f"k{n}", "label": "x"} for n in range(4)],
        [{"key": "k", "label": "x", "action": {"navigation_path": "/x"}}],
    ],
)
async def test_invalid_buttons_are_rejected(
    entry: MockConfigEntry, create: CreateBanner, actions: list[dict[str, Any]]
) -> None:
    with pytest.raises(Exception, match=r"actions|key|label|action|buttons|length"):
        await create(id="a", message="x", actions=actions)


async def test_dismiss_button_needs_a_dismissible_banner(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    with pytest.raises(Exception, match="dismiss"):
        await create(id="a", message="x", dismissible=False, actions=BUTTONS)
    await create(id="a", message="x", dismissible=False, actions=[BUTTONS[1]])


async def test_buttons_survive_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    from .test_restart import restart

    await create(id="a", message="x", timeout=0, actions=BUTTONS)
    await restart(hass, entry)
    assert [b["key"] for b in banners(entry)["a"].actions] == ["ack", "later"]
