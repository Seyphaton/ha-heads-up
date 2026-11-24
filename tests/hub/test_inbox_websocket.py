"""The inbox commands are the caller's own, for everyone, an administrator included (D-264)."""

from datetime import timedelta
from typing import Any

import pytest
from homeassistant.auth.models import User
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import INBOX_MAX_ITEMS

ADMIN = "person.admin"
READER = "person.reader"


@pytest.fixture
async def people(hass: HomeAssistant, hass_admin_user: User, hass_read_only_user: User) -> None:
    hass.states.async_set(ADMIN, "home", {"user_id": hass_admin_user.id})
    hass.states.async_set(READER, "home", {"user_id": hass_read_only_user.id})


def put(entry: MockConfigEntry, person: str, mid: str, offset: int = 0, **kw: Any) -> None:
    fields = {
        "title": f"Title {mid}",
        "text": f"Text {mid}",
        "severity": kw.pop("severity", "info"),
        "icon": "mdi:bell",
        "source": "tag:x",
        "tag": "x",
        **kw,
    }
    now = dt_util.utcnow() + timedelta(seconds=offset)
    entry.runtime_data.hub.inbox.upsert(person, mid, fields, "inbox", now)


async def ask(client: Any, kind: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/inbox_{kind}", **data})
    return dict(await client.receive_json())


# Privacy ---------------------------------------------------------------------------------


async def test_each_user_lists_only_their_own_items_and_so_does_an_administrator(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    put(entry, ADMIN, "mine")
    put(entry, READER, "hers")
    admin = await hass_ws_client(hass)
    reader = await hass_ws_client(hass, hass_read_only_access_token)
    assert [i["message_id"] for i in (await ask(admin, "list"))["result"]["items"]] == ["mine"]
    assert [i["message_id"] for i in (await ask(reader, "list"))["result"]["items"]] == ["hers"]


async def test_nobody_can_read_delete_or_open_another_persons_item(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, READER, "hers")
    admin = await hass_ws_client(hass)
    for kind in ("read", "delete"):
        reply = await ask(admin, kind, message_id="hers")
        assert reply["success"] is False and reply["error"]["code"] == "not_found"
    inbox = entry.runtime_data.hub.inbox
    item = inbox.get(READER, "hers")
    assert item is not None and item.read_at is None


async def test_read_all_and_clear_touch_only_the_callers_items(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, ADMIN, "a1")
    put(entry, READER, "r1")
    admin = await hass_ws_client(hass)
    assert (await ask(admin, "read_all"))["result"] == {"count": 1}
    inbox = entry.runtime_data.hub.inbox
    assert inbox.unread_count(READER) == 1
    assert (await ask(admin, "clear"))["result"] == {"count": 1}
    assert inbox.items(ADMIN) == [] and len(inbox.items(READER)) == 1


async def test_a_user_without_a_person_gets_an_empty_inbox_and_can_change_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, "person.someone", "x")
    client = await hass_ws_client(hass)
    result = (await ask(client, "list"))["result"]
    assert result["items"] == [] and result["has_person"] is False and result["unread"] == 0
    assert (await ask(client, "read_all"))["result"] == {"count": 0}
    assert (await ask(client, "clear"))["result"] == {"count": 0}
    reply = await ask(client, "read", message_id="x")
    assert reply["success"] is False and reply["error"]["code"] == "not_found"


async def test_a_user_who_is_not_logged_in_as_a_person_cannot_pick_one(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, READER, "hers")
    admin = await hass_ws_client(hass)
    reply = await ask(admin, "list", person=READER)  # there is no such field
    assert reply["success"] is False and reply["error"]["code"] == "invalid_format"


# The commands ------------------------------------------------------------------------------


async def test_the_list_has_the_item_fields_the_counts_and_no_text_of_others(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, ADMIN, "leak", severity="critical", image="/local/x.png", color="#ff0000")
    put(entry, ADMIN, "washer", offset=5)
    admin = await hass_ws_client(hass)
    result = (await ask(admin, "list"))["result"]
    assert result["has_person"] is True and result["total"] == 2
    assert (result["unread"], result["needs_action"], result["unread_critical"]) == (2, 1, 1)
    first = result["items"][0]  # the latest change first
    assert first["message_id"] == "washer"
    leak = result["items"][1]
    assert leak["title"] == "Title leak" and leak["text"] == "Text leak"
    assert (
        leak["severity"] == "critical" and leak["unread"] is True and leak["needs_action"] is True
    )
    assert leak["resolved"] is False and leak["acknowledged"] is False
    assert leak["via"] == ["inbox"] and leak["timeline"][0]["kind"] == "sent"
    assert leak["image"] == "/local/x.png" and leak["color"] == "#ff0000"
    assert "source" not in leak  # an internal key, not for the card


async def test_the_list_is_paged_and_can_show_only_unread_items(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    for n in range(5):
        put(entry, ADMIN, f"m{n}", offset=n)
    entry.runtime_data.hub.inbox.mark_read(ADMIN, "m4", dt_util.utcnow())
    admin = await hass_ws_client(hass)
    page = (await ask(admin, "list", limit=2, offset=1))["result"]
    assert [i["message_id"] for i in page["items"]] == ["m3", "m2"]
    assert page["total"] == 5 and page["more"] is True
    unread = (await ask(admin, "list", unread_only=True))["result"]
    assert [i["message_id"] for i in unread["items"]] == ["m3", "m2", "m1", "m0"]
    assert unread["total"] == 4 and unread["more"] is False


async def test_the_page_size_is_limited(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    admin = await hass_ws_client(hass)
    reply = await ask(admin, "list", limit=INBOX_MAX_ITEMS)
    assert reply["success"] is False and reply["error"]["code"] == "invalid_format"


async def test_read_marks_one_item_and_a_second_read_is_not_an_error(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, ADMIN, "a")
    put(entry, ADMIN, "b")
    admin = await hass_ws_client(hass)
    assert (await ask(admin, "read", message_id="a"))["success"] is True
    assert (await ask(admin, "read", message_id="a"))["success"] is True
    inbox = entry.runtime_data.hub.inbox
    assert inbox.unread_count(ADMIN) == 1


async def test_delete_removes_one_item(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, ADMIN, "a")
    put(entry, ADMIN, "b")
    admin = await hass_ws_client(hass)
    assert (await ask(admin, "delete", message_id="a"))["success"] is True
    assert [i.message_id for i in entry.runtime_data.hub.inbox.items(ADMIN)] == ["b"]


async def test_subscribe_sends_the_state_now_and_after_every_change(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    put(entry, ADMIN, "a")
    admin = await hass_ws_client(hass)
    await admin.send_json_auto_id({"type": "heads_up/inbox_subscribe"})
    assert (await admin.receive_json())["success"] is True
    first = (await admin.receive_json())["event"]
    assert first["unread"] == 1 and [i["message_id"] for i in first["items"]] == ["a"]
    put(entry, ADMIN, "b", offset=1)
    second = (await admin.receive_json())["event"]
    assert second["unread"] == 2 and [i["message_id"] for i in second["items"]] == ["b", "a"]


async def test_subscribe_does_not_send_events_for_other_peoples_items(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    admin = await hass_ws_client(hass)
    await admin.send_json_auto_id({"type": "heads_up/inbox_subscribe"})
    await admin.receive_json()
    await admin.receive_json()  # the first state
    put(entry, READER, "hers")
    put(entry, ADMIN, "mine", offset=1)
    event = (await admin.receive_json())["event"]
    assert [i["message_id"] for i in event["items"]] == ["mine"]
