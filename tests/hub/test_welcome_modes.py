"""The introduction asks how policies interact and offers a set that fits (D-148, D-150)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator


@pytest.fixture
def options() -> dict[str, Any]:  # type: ignore[override]
    return {}  # the default mode: only the first policy runs


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


def policies(entry: MockConfigEntry) -> dict[str, dict[str, Any]]:
    return {s.title: dict(s.data) for s in entry.subentries.values() if s.subentry_type == "policy"}


async def test_the_introduction_offers_the_list_of_the_current_mode_and_both_lists(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    result = (await ask(client, "welcome_get"))["result"]
    assert result["policy_mode"] == "first"
    assert [i["id"] for i in result["items"]] == ["critical", "warnings", "digest", "quiet"]
    assert [i["id"] for i in result["items_by_mode"]["all"]] == [
        "quiet",
        "digest",
        "critical",
        "warnings",
    ]
    first = {i["id"]: i for i in result["items_by_mode"]["first"]}
    assert first["critical"]["policies"] == ["Critical delivery"]  # no reminder, no escalation


async def test_the_first_mode_creates_four_policies_that_do_not_overlap_in_this_order(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(
        client, "welcome_apply", items=["quiet", "digest", "critical", "warnings"], mode="first"
    )
    assert reply["result"]["added"] == [
        "Critical delivery",
        "Warning reminders",
        "Evening summary",
        "Night quiet",
    ]
    made = policies(entry)
    assert made["Critical delivery"]["severities"] == ["critical"]
    assert made["Warning reminders"]["severities"] == ["warning"]
    assert made["Evening summary"]["severities"] == ["info", "success"]
    assert made["Evening summary"]["tags"] == ["digest"]
    assert made["Night quiet"]["severities"] == ["info", "success"]
    assert entry.options["policy_mode"] == "first" and entry.options["welcome_seen"] is True
    listed = [p.name for p in entry.runtime_data.hub.policies.ordered()]
    assert listed == ["Critical delivery", "Warning reminders", "Evening summary", "Night quiet"]


async def test_each_kind_of_message_meets_exactly_one_of_the_four(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    from datetime import UTC, datetime

    from custom_components.heads_up.models import Banner

    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["quiet", "digest", "critical", "warnings"])
    book = entry.runtime_data.hub.policies
    now = datetime(2026, 11, 4, 12, tzinfo=UTC)

    def used(severity: str, tag: str | None = None) -> list[str]:
        banner = Banner(
            id="m",
            message="x",
            severity=severity,
            dismissible=True,
            dismiss_scope="user",
            created_at=now,
            updated_at=now,
            tag=tag,
        )
        return [p.name for p in book.for_message(banner)]

    assert used("critical") == ["Critical delivery"]
    assert used("warning") == ["Warning reminders"]
    assert used("info", "digest") == ["Evening summary"]
    assert used("success", "digest") == ["Evening summary"]
    assert used("info") == ["Night quiet"]
    assert used("warning", "digest") == ["Warning reminders"]  # the order, not the lists, decides


async def test_the_all_mode_keeps_the_four_items_as_before(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=["critical", "quiet"], mode="all")
    assert reply["result"]["added"] == [
        "Night quiet",
        "Critical delivery",
        "Critical reminder",
    ]
    assert entry.options["policy_mode"] == "all"
    assert policies(entry)["Night quiet"]["severities"] == []


async def test_an_unknown_mode_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=[], mode="some")
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"
