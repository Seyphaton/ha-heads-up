"""`heads_up/send_message`: a message from a person to other people (Phase 23, D-265, D-279)."""

from datetime import timedelta
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.auth.models import User
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import MAX_MESSAGE, MESSAGE_RATE_LIMIT
from custom_components.heads_up.hub.inbox import SENT_PREFIX

ADMIN = "person.admin"
READER = "person.reader"
NOBODY = "person.nobody"  # no user: can be a recipient, cannot send


@pytest.fixture
def options() -> dict[str, Any]:
    return {"inbox_messages": True}


@pytest.fixture
async def people(hass: HomeAssistant, hass_admin_user: User, hass_read_only_user: User) -> None:
    hass.states.async_set(ADMIN, "home", {"user_id": hass_admin_user.id})
    hass.states.async_set(READER, "home", {"user_id": hass_read_only_user.id})
    hass.states.async_set(NOBODY, "home", {})


async def send(client: Any, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/send_message", **data})
    return dict(await client.receive_json())


def code(reply: dict[str, Any]) -> str:
    assert reply["success"] is False
    return str(reply["error"]["code"])


async def test_a_message_reaches_the_recipient_inbox_with_the_sender_from_the_connection(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    reader = await hass_ws_client(hass, hass_read_only_access_token)
    reply = await send(reader, to=[ADMIN], text="Dinner is ready")
    assert reply["success"] is True
    await hass.async_block_till_done()
    item = entry.runtime_data.hub.inbox.get(ADMIN, reply["result"]["id"])
    assert item is not None and item.text == "Dinner is ready"
    assert item.sender == READER and item.severity == "info" and item.unread


async def test_the_call_has_no_sender_field(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    reader = await hass_ws_client(hass, hass_read_only_access_token)
    for extra in ({"sender": ADMIN}, {"severity": "critical"}, {"title": "x"}):
        reply = await send(reader, to=[ADMIN], text="hi", **extra)
        assert code(reply) == "invalid_format"
    assert entry.runtime_data.hub.inbox.items(ADMIN) == []


async def test_a_user_without_a_person_cannot_send(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    hass.states.async_set(NOBODY, "home", {})
    client = await hass_ws_client(hass)  # the admin user has no person here
    assert code(await send(client, to=[NOBODY], text="hi")) == "no_person"


async def test_a_user_linked_to_two_persons_cannot_send(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_admin_user: User,
    hass_ws_client: WebSocketGenerator,
) -> None:
    hass.states.async_set("person.second", "home", {"user_id": hass_admin_user.id})
    client = await hass_ws_client(hass)
    assert code(await send(client, to=[READER], text="hi")) == "ambiguous_person"


@pytest.mark.parametrize("options", [{}, {"inbox_messages": False}])
async def test_the_switch_off_refuses_every_call(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    assert code(await send(client, to=[READER], text="hi")) == "messages_off"
    assert entry.runtime_data.hub.inbox.items(READER) == []


async def test_speech_and_mail_are_refused_and_unknown_people_too(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    for channels in (["speak"], ["mail"], ["inbox", "banner"], ["persistent"]):
        reply = await send(client, to=[READER], text="hi", channels=channels)
        assert code(reply) == "invalid_format"
    assert code(await send(client, to=["person.ghost"], text="hi")) == "unknown_recipient"
    assert code(await send(client, to=["light.kitchen"], text="hi")) == "invalid_format"
    assert code(await send(client, to=[], text="hi")) == "invalid_format"


async def test_the_text_is_trimmed_and_limited(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    assert code(await send(client, to=[READER], text="   ")) == "invalid_format"
    assert code(await send(client, to=[READER], text="x" * (MAX_MESSAGE + 1))) == "invalid_format"
    reply = await send(client, to=[READER], text="  hello \n")
    item = entry.runtime_data.hub.inbox.get(READER, reply["result"]["id"])
    assert item is not None and item.text == "hello"


async def test_the_sender_gets_a_sent_item_with_the_recipients_and_no_count(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    reply = await send(client, to=[READER, NOBODY], text="Dinner")
    inbox = entry.runtime_data.hub.inbox
    sent = inbox.get(ADMIN, f"{SENT_PREFIX}{reply['result']['id']}")
    assert sent is not None and sent.sent and sorted(sent.recipients) == [NOBODY, READER]
    assert inbox.unread_count(ADMIN) == 0
    assert inbox.items(NOBODY)[0].sender == ADMIN


async def test_a_message_to_oneself_makes_both_an_inbox_item_and_a_sent_item(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    reply = await send(client, to=[ADMIN], text="Buy milk")
    inbox = entry.runtime_data.hub.inbox
    mid = reply["result"]["id"]
    assert inbox.get(ADMIN, mid) is not None and inbox.get(ADMIN, f"{SENT_PREFIX}{mid}")
    assert inbox.unread_count(ADMIN) == 1


async def test_a_channel_the_recipient_does_not_accept_is_skipped_and_reported(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    hub = entry.runtime_data.hub
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": READER, "channels": ["inbox"], "channels_v": 2},
            subentry_type="recipient_profile",
            title=READER,
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    reply = await send(client, to=[READER], text="hi", channels=["inbox", "push", "popup"])
    skipped = reply["result"]["skipped"]
    assert {"person": READER, "channel": "push", "reason": "channel_not_accepted"} in skipped
    assert {"person": READER, "channel": "popup", "reason": "channel_not_accepted"} in skipped
    assert hub.inbox.items(READER)  # the inbox item is still made


async def test_a_forged_item_cannot_name_another_sender_through_the_other_actions(
    hass: HomeAssistant, entry: MockConfigEntry, people: None
) -> None:
    for data in ({"sender": ADMIN}, {"source": "person"}):
        with pytest.raises(Exception):  # noqa: B017
            await hass.services.async_call(
                "heads_up",
                "notify",
                {"message": "hi", "to": {"inbox": {"recipients": [READER]}}, **data},
                blocking=True,
            )
    assert entry.runtime_data.hub.inbox.items(READER) == []


async def test_the_eleventh_call_in_a_minute_is_refused_and_the_window_moves_on(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
    freezer: FrozenDateTimeFactory,
) -> None:
    client = await hass_ws_client(hass)
    for _ in range(MESSAGE_RATE_LIMIT):
        assert (await send(client, to=[READER], text="x"))["success"] is True
    assert code(await send(client, to=[READER], text="x")) == "rate_limited"
    freezer.tick(timedelta(seconds=61))
    assert (await send(client, to=[READER], text="x"))["success"] is True


async def test_the_limit_is_per_sender(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    admin = await hass_ws_client(hass)
    reader = await hass_ws_client(hass, hass_read_only_access_token)
    for _ in range(MESSAGE_RATE_LIMIT):
        await send(admin, to=[READER], text="x")
    assert (await send(reader, to=[ADMIN], text="x"))["success"] is True


async def test_the_message_log_and_diagnostics_hold_no_text(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    people: None,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = await hass_ws_client(hass)
    await send(client, to=[READER], text="a secret plan")
    await hass.async_block_till_done()
    from custom_components.heads_up.diagnostics import async_get_config_entry_diagnostics

    assert "a secret plan" not in str(await async_get_config_entry_diagnostics(hass, entry))
