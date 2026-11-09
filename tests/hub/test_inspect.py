"""Diagnostics, policy switch attributes, the trace action and the stored trace (D-194)."""

from typing import Any

import pytest
from homeassistant.components.diagnostics import REDACTED
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.diagnostics import async_get_config_entry_diagnostics

from ..test_restart import restart
from .conftest import AddDevice
from .policy_support import QUIET, REMINDER, add_policy, make_household, send


async def trace_of(hass: HomeAssistant, **data: Any) -> list[dict[str, Any]]:
    response = await hass.services.async_call(
        DOMAIN, "get_trace", data, blocking=True, return_response=True
    )
    assert response is not None
    return list(response["entries"])


async def test_get_trace_returns_the_entries_of_a_message_newest_first(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, id="m")
    await send(hass, entry, id="other")
    entries = await trace_of(hass, message_id="m")
    assert entries and {e["message_id"] for e in entries} == {"m"}
    assert [e["time"] for e in entries] == sorted((e["time"] for e in entries), reverse=True)
    assert len(await trace_of(hass, message_id="m", limit=1)) == 1
    assert {e["message_id"] for e in await trace_of(hass)} == {"m", "other"}


async def test_get_trace_refuses_a_limit_outside_the_range(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(Exception):  # noqa: B017  # probatio Invalid: the code is not part of the contract
        await trace_of(hass, limit=0)


async def test_the_trace_survives_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, id="m")
    before = [(e["message_id"], e["channel"], e["result"]) for e in await trace_of(hass)]
    assert before
    await restart(hass, entry)
    after = [(e["message_id"], e["channel"], e["result"]) for e in await trace_of(hass)]
    assert after[-len(before) :] == before or set(before) <= set(after)


async def test_a_damaged_stored_entry_is_dropped(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    trace = entry.runtime_data.hub.trace
    trace.load([{"nonsense": 1}, "text", None])
    assert len(trace) == 0


async def test_a_policy_switch_shows_what_the_policy_does(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await add_policy(
        hass, entry, "Night", **QUIET, severities=["info"], tags=["digest"], critical_passes=True
    )
    await add_policy(hass, entry, "Nag", **REMINDER, severities=["warning"])
    registry = er.async_get(hass)
    states = {}
    for name in ("night", "nag"):
        entity_id = next(
            e.entity_id
            for e in registry.entities.values()
            if e.platform == DOMAIN and e.domain == "switch" and name in e.entity_id
        )
        state = hass.states.get(entity_id)
        assert state is not None
        states[name] = state.attributes
    night = states["night"]
    assert night["type"] == "quiet_hours" and night["severities"] == ["info"]
    assert night["tags"] == ["digest"] and night["from_time"] == "22:00:00"
    assert night["action"] == "quiet" and night["critical_passes"] is True
    nag = states["nag"]
    assert nag["every_minutes"] == 10 and nag["max_count"] == 2
    assert {night["order"], nag["order"]} == {1, 2}


async def test_diagnostics_hide_addresses_and_message_texts(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "mail_global_address": "house@example.com"}
    )
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": "person.anna", "mail_address": "anna@example.com"},
            subentry_type="recipient_profile",
            title="Anna",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await send(hass, entry, id="m", message="A private text", title="A private title")
    data = await async_get_config_entry_diagnostics(hass, entry)
    text = str(data)
    for secret in ("house@example.com", "anna@example.com", "A private text", "A private title"):
        assert secret not in text
    assert data["options"]["mail_global_address"] == REDACTED
    (profile,) = [s for s in data["subentries"] if s["type"] == "recipient_profile"]
    assert profile["data"]["mail_address"] == REDACTED
    assert data["counts"]["messages"] == 1 and data["trace"] and data["recent_messages"]


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def test_the_panel_lists_the_entity_id_of_each_policy_and_a_rename_keeps_it(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    subentry = await add_policy(hass, entry, "Night", **QUIET)
    client = await hass_ws_client(hass)

    async def listed() -> dict[str, str]:
        reply = await ask(client, "panel_config")
        return {p["name"]: p["entity_id"] for p in reply["result"]["policies"]}

    assert await listed() == {"Night": "switch.heads_up_policy_night"}
    hass.config_entries.async_update_subentry(entry, subentry, title="Evening")
    await hass.async_block_till_done()
    # The registered ID stays; a call that names the switch keeps working after the rename.
    assert await listed() == {"Evening": "switch.heads_up_policy_night"}


async def test_a_new_policy_is_shown_the_id_it_will_get(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(hass, entry, "Night", **QUIET)
    client = await hass_ws_client(hass)
    free = await ask(client, "policy_entity_id", name="Weekend watch")
    assert free["result"]["entity_id"] == "switch.heads_up_policy_weekend_watch"
    taken = await ask(client, "policy_entity_id", name="Night")
    assert taken["result"]["entity_id"] == "switch.heads_up_policy_night_2"


async def test_the_entity_id_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    reply = await ask(client, "policy_entity_id", name="x")
    assert reply["error"]["code"] == "unauthorized"


async def test_the_panel_lists_the_entity_id_of_each_audience_and_a_new_one_gets_a_free_id(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    from .policy_support import add_audience

    await add_audience(hass, entry, "Family", kind="persons", persons=["person.anna"])
    client = await hass_ws_client(hass)
    reply = await ask(client, "panel_config")
    ids = {a["name"]: a["entity_id"] for a in reply["result"]["audiences"]}
    assert ids["At home"] == "binary_sensor.heads_up_audience_at_home"
    assert ids["Family"] == "binary_sensor.heads_up_audience_family"
    free = await ask(client, "audience_entity_id", name="Neighbours")
    assert free["result"]["entity_id"] == "binary_sensor.heads_up_audience_neighbours"
    taken = await ask(client, "audience_entity_id", name="Family")
    assert taken["result"]["entity_id"] == "binary_sensor.heads_up_audience_family_2"
