"""What the trace records so the Overview can tell what happened (origin, person, holds)."""

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    SUMMARIZE,
    add_policy,
    make_household,
    send,
    wait,
)


def entries(entry: MockConfigEntry, message_id: str = "m") -> list[dict[str, Any]]:
    return [dict(e) for e in reversed(entry.runtime_data.hub.trace.entries(message_id))]


async def test_the_first_delivery_has_the_origin_message_and_names_the_person_behind_a_phone(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    push = [e for e in entries(entry) if e["channel"] == "push"]
    assert push and all(e["origin"] == "message" for e in push)
    assert {e["person"] for e in push} == {"person.anna"}
    assert all(e["recipient"].startswith("device:") for e in push)


async def test_reminders_and_escalations_are_marked_with_their_origin(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    await wait(hass, entry, freezer, 11)
    origins = {e["origin"] for e in entries(entry) if e["channel"] in ("push", "banner")}
    assert {"message", "reminder", "escalation"} <= origins


async def test_a_quiet_send_names_the_policy_that_made_it_quiet(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **QUIET)
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await send(hass, entry, severity="warning")
    (push,) = [e for e in entries(entry) if e["channel"] == "push"]
    assert push["result"] == "sent" and push["by"] == "Night"


async def test_a_message_held_for_a_summary_and_its_summary_are_in_its_trace(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE, tags=["digest"])
    await send(hass, entry, severity="warning", tag="digest")
    held = [e for e in entries(entry) if e["result"] == "held"]
    assert [(e["channel"], e["reason"], e["by"]) for e in held] == [("", "summarize", "Digest")]
    await wait(hass, entry, freezer, 61)
    summarized = [e for e in entries(entry) if e["result"] == "summarized"]
    assert summarized and all(e["origin"] == "summary" and e["by"] == "Digest" for e in summarized)
    assert {e["channel"] for e in summarized} >= {"push"}


async def test_trace_entries_stored_by_an_earlier_version_still_load(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub.trace import TraceBuffer

    buffer = TraceBuffer(10)
    buffer.load(
        [
            {
                "time": "2026-11-01T10:00:00+00:00",
                "message_id": "m",
                "channel": "push",
                "recipient": "device:x",
                "result": "sent",
                "reason": None,
                "by": None,
            }
        ]
    )
    (found,) = buffer.entries("m")
    assert found["origin"] is None and found["person"] is None
