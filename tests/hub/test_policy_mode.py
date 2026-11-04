"""How automatic policies interact: the first that applies, or all (D-148), and the list order."""

from datetime import UTC, datetime
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub.policies import PolicyBook
from custom_components.heads_up.hub.policies.matching import select
from custom_components.heads_up.hub.policies.models import Policy
from custom_components.heads_up.models import Banner

from ..conftest import options_input
from .conftest import AddDevice
from .policy_support import ESCALATION, REMINDER, add_policy, make_household, send

NOW = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


@pytest.fixture
def options() -> dict[str, Any]:  # type: ignore[override]
    return {}  # the default mode


def message(severity: str = "critical", policy: str | None = None) -> Banner:
    return Banner(
        id="m",
        message="x",
        severity=severity,
        dismissible=True,
        dismiss_scope="user",
        created_at=NOW,
        updated_at=NOW,
        policy=policy,
    )


def policy(name: str, type: str = "reminder", **kw: Any) -> Policy:
    return Policy(name=name, type=type, subentry_id=name, every_minutes=5, **kw)


def test_the_first_automatic_policy_that_applies_is_the_only_one() -> None:
    found = [policy("A"), policy("B"), policy("C", severities=frozenset({"info"}))]
    assert [p.name for p in select(found, message(), first_only=True)] == ["A"]
    assert [p.name for p in select(found, message(), first_only=False)] == ["A", "B"]


def test_a_disabled_or_non_matching_policy_is_passed_over() -> None:
    found = [
        policy("A", enabled=False),
        policy("B", severities=frozenset({"info"})),
        policy("C", apply="manual"),
        policy("D"),
    ]
    assert [p.name for p in select(found, message(), first_only=True)] == ["D"]


def test_a_named_policy_runs_alone_whatever_the_mode() -> None:
    found = [policy("A"), policy("M", apply="manual")]
    assert [p.name for p in select(found, message(policy="M"), first_only=True)] == ["M"]


def book(options: dict[str, Any], *policies: Policy) -> PolicyBook:
    result = PolicyBook(options)
    result._policies = {p.subentry_id: p for p in policies}
    return result


def test_the_default_mode_is_first_and_an_unknown_value_falls_back_to_it() -> None:
    assert book({}).mode == "first"
    assert book({"policy_mode": "nonsense"}).mode == "first"
    assert book({"policy_mode": "all"}).mode == "all"


def test_without_a_stored_order_the_starting_order_is_by_type_then_name() -> None:
    items = [
        policy("Deliver B", "deliver"),
        policy("Reminder", "reminder"),
        policy("Quiet", "quiet_hours"),
        policy("Summary", "summarize"),
        policy("Away", "away"),
        policy("Deliver A", "deliver"),
        policy("Escalate", "escalation"),
        policy("Fallback", "fallback"),
    ]
    names = [p.name for p in book({}, *items).ordered()]
    assert names == [
        "Summary",
        "Quiet",
        "Away",
        "Escalate",
        "Reminder",
        "Fallback",
        "Deliver A",
        "Deliver B",
    ]


def test_a_stored_order_wins_and_new_policies_go_to_the_bottom() -> None:
    a, b, c = policy("A"), policy("B"), policy("C")
    ordered = book({"policy_order": ["B", "gone", "A"]}, a, b, c).ordered()
    assert [p.name for p in ordered] == ["B", "A", "C"]


def test_the_mode_first_uses_the_order_of_the_list() -> None:
    a, b = policy("A"), policy("B")
    first = book({"policy_order": ["B", "A"], "policy_mode": "first"}, a, b)
    assert [p.name for p in first.for_message(message())] == ["B"]
    everything = book({"policy_order": ["B", "A"], "policy_mode": "all"}, a, b)
    assert [p.name for p in everything.for_message(message())] == ["B", "A"]


async def test_a_new_installation_stores_the_starting_order_and_keeps_a_chosen_one(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert entry.options["policy_order"] == []
    await add_policy(hass, entry, "Critical reminder", **REMINDER)
    await add_policy(hass, entry, "Water", **ESCALATION)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.options["policy_order"] == []  # stored once, not rewritten at the next start
    names = [p.name for p in entry.runtime_data.hub.policies.ordered()]
    assert names == ["Critical reminder", "Water"]  # new policies at the bottom


async def test_the_default_mode_runs_only_the_first_matching_policy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "First", **REMINDER, severities=["critical"])
    await add_policy(hass, entry, "Second", **ESCALATION, severities=["critical"])
    await send(hass, entry, severity="critical")
    used = entry.runtime_data.hub.policies.for_message(entry.runtime_data.banners["m"])
    assert [p.name for p in used] == ["First"]
    assert entry.runtime_data.hub.policies.mode == "first"


async def test_an_options_form_save_keeps_the_mode_and_the_order(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "policy_mode": "all", "policy_order": ["x"]}
    )
    await hass.async_block_till_done()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(result["flow_id"], options_input({}))
    assert entry.options["policy_mode"] == "all" and entry.options["policy_order"] == ["x"]


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def test_the_mode_and_the_order_are_set_by_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "policy_mode_set", mode="all"))["error"]["code"] == "unauthorized"
    assert (await ask(client, "policy_order_set", order=[]))["error"]["code"] == "unauthorized"


async def test_the_mode_can_be_set_and_an_unknown_mode_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, "policy_mode_set", mode="all"))["success"]
    assert entry.options["policy_mode"] == "all"
    assert entry.runtime_data.hub.policies.mode == "all"  # applied at once
    bad = await ask(client, "policy_mode_set", mode="some")
    assert not bad["success"] and bad["error"]["code"] == "invalid_format"


async def test_the_order_must_list_every_policy_once(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    first = await add_policy(hass, entry, "A", **REMINDER)
    second = await add_policy(hass, entry, "B", **REMINDER)
    client = await hass_ws_client(hass)
    ids = [second.subentry_id, first.subentry_id]
    assert (await ask(client, "policy_order_set", order=ids))["success"]
    assert [p.name for p in entry.runtime_data.hub.policies.ordered()] == ["B", "A"]
    for bad in ([first.subentry_id], [*ids, ids[0]], [*ids, "other"]):
        reply = await ask(client, "policy_order_set", order=bad)
        assert not reply["success"] and reply["error"]["code"] == "invalid_order"
    assert entry.options["policy_order"] == ids


async def test_the_panel_config_has_the_mode_and_the_policies_in_order(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    first = await add_policy(hass, entry, "A", **REMINDER)
    second = await add_policy(hass, entry, "B", **REMINDER)
    client = await hass_ws_client(hass)
    await ask(client, "policy_order_set", order=[second.subentry_id, first.subentry_id])
    config = (await ask(client, "panel_config"))["result"]
    assert config["policy_mode"] == "first"
    assert [p["name"] for p in config["policies"]] == ["B", "A"]
