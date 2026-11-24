"""The inbox settings: retention, the reminder toggle, Clear inbox and diagnostics (Phase 22)."""

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.diagnostics import async_get_config_entry_diagnostics

from .test_panel_settings import ask

ANNA = "person.anna"
BEN = "person.ben"


def put(entry: MockConfigEntry, person: str, mid: str, days_ago: int = 0, **kw: Any) -> None:
    fields = {"title": "Secret title", "text": "Secret text", "severity": "info", **kw}
    now = dt_util.utcnow() - timedelta(days=days_ago)
    entry.runtime_data.hub.inbox.upsert(person, mid, fields, "inbox", now)


# The settings ----------------------------------------------------------------------------


async def test_the_defaults_are_twelve_months_and_a_reminder_that_brings_items_back(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "settings_get"))["result"]
    assert result["options"]["inbox_retention_months"] == 12
    assert result["options"]["inbox_reminder_unread"] is True
    section = next(s for s in result["layout"] if s["name"] == "inbox")
    kinds = {e["key"]: e for e in section["entries"]}
    assert kinds["inbox_retention_months"]["range"] == [1, 36]
    assert kinds["inbox_reminder_unread"]["kind"] == "bool"


async def test_the_retention_is_one_to_thirty_six_months(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    for bad in (0, 37, -1):
        reply = await ask(client, "settings_set", inbox_retention_months=bad)
        assert not reply["success"] and reply["error"]["code"] == "invalid_format", bad
    for good in (1, 36):
        assert (await ask(client, "settings_set", inbox_retention_months=good))["success"]


async def test_a_shorter_retention_removes_older_items_at_once(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    put(entry, ANNA, "old", days_ago=100)
    put(entry, ANNA, "new", days_ago=5)
    client = await hass_ws_client(hass)
    assert (await ask(client, "settings_set", inbox_retention_months=1))["success"]
    await hass.async_block_till_done()
    assert [i.message_id for i in entry.runtime_data.hub.inbox.items(ANNA)] == ["new"]
    assert entry.runtime_data.hub.inbox.retention_months == 1


async def test_the_retention_is_applied_when_the_integration_starts(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from ..test_restart import restart

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "inbox_retention_months": 2}
    )
    await hass.async_block_till_done()
    put(entry, ANNA, "old", days_ago=100)
    put(entry, ANNA, "new", days_ago=5)
    await restart(hass, entry)
    assert [i.message_id for i in entry.runtime_data.hub.inbox.items(ANNA)] == ["new"]


async def test_the_reminder_toggle_is_used_by_the_channel(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "settings_set", inbox_reminder_unread=False))["success"]
    await hass.async_block_till_done()
    assert entry.runtime_data.options["inbox_reminder_unread"] is False
    put(entry, ANNA, "a")
    inbox = entry.runtime_data.hub.inbox
    inbox.mark_read(ANNA, "a", dt_util.utcnow())
    channel = entry.runtime_data.hub.channels.get("inbox")
    from custom_components.heads_up.hub.channels.base import Target

    from custom_components.heads_up.models import Banner

    message = Banner(
        id="a",
        message="x",
        severity="info",
        dismissible=True,
        dismiss_scope="user",
        created_at=dt_util.utcnow(),
        updated_at=dt_util.utcnow(),
    )
    await channel.deliver(message, Target(ANNA, "person", ANNA, origin="reminder"))
    item = inbox.get(ANNA, "a")
    assert item is not None and item.read_at is not None  # a reminder did not bring it back


# Clear inbox ------------------------------------------------------------------------------


async def test_clear_inbox_is_for_administrators_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    put(entry, ANNA, "a")
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "inbox_clear_all"))["error"]["code"] == "unauthorized"
    assert entry.runtime_data.hub.inbox.items(ANNA)


async def test_clear_inbox_removes_every_persons_items_and_reports_the_new_state(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    put(entry, ANNA, "a")
    put(entry, BEN, "b")
    put(entry, BEN, "c")
    client = await hass_ws_client(hass)
    result = (await ask(client, "inbox_clear_all"))["result"]
    assert result["count"] == 3
    assert result["info"] == {"items": 0, "people": 0, "oldest": None}
    assert entry.runtime_data.hub.inbox.people() == []


async def test_the_settings_show_how_much_is_stored_without_any_text(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    put(entry, ANNA, "a", days_ago=3)
    put(entry, BEN, "b")
    put(entry, BEN, "c")
    client = await hass_ws_client(hass)
    reply = await ask(client, "settings_get")
    info = reply["result"]["inbox"]
    assert info["items"] == 3 and info["people"] == 2 and info["oldest"]
    assert "Secret" not in repr(reply)


# Diagnostics ------------------------------------------------------------------------------


async def test_diagnostics_have_counts_per_person_and_the_oldest_date_but_no_text(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    put(entry, ANNA, "a", days_ago=3)
    put(entry, BEN, "b")
    put(entry, BEN, "c")
    data = await async_get_config_entry_diagnostics(hass, entry)
    inbox = data["inbox"]
    assert inbox["items"] == 3 and inbox["people"] == 2
    assert inbox["per_person"] == {ANNA: 1, BEN: 2}
    assert inbox["oldest"]
    assert "Secret" not in repr(data)
