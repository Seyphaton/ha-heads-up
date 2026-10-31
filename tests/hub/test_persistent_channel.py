"""Persistent notification channel: one bell entry per message, with the id hu_<id> (N-67)."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import PersistentCapture, settle, tick
from .policy_support import ESCALATION, add_policy, make_household


async def bell(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> dict[str, Any]:
    body = {"id": "m", "message": "Water leak", "channels": ["persistent"], **data}
    result = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert result is not None
    return dict(result)


def reasons(entry: MockConfigEntry) -> list[str | None]:
    return [e["reason"] for e in entry.runtime_data.hub.trace.entries("m")]


async def test_a_message_creates_one_entry_with_the_id_hu_message(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    result = await bell(hass, entry, title="Leak")
    assert result["channels"]["persistent"]["sent"] == 1
    (call,) = persistent_capture.create
    assert call.data == {"notification_id": "hu_m", "message": "Water leak", "title": "Leak"}


async def test_without_a_title_none_is_sent(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry)
    assert "title" not in persistent_capture.create[0].data


async def test_an_update_replaces_the_entry_with_the_same_id(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry)
    await bell(hass, entry, message="Still leaking")
    assert [c.data["notification_id"] for c in persistent_capture.create] == ["hu_m", "hu_m"]
    assert persistent_capture.create[1].data["message"] == "Still leaking"
    assert not persistent_capture.dismiss


async def test_the_entry_is_dismissed_when_the_message_is_cleared(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry)
    await hass.services.async_call(DOMAIN, "clear", {"id": "m"}, blocking=True)
    await settle(hass, entry)
    assert [c.data for c in persistent_capture.dismiss] == [{"notification_id": "hu_m"}]


async def test_the_entry_is_dismissed_when_the_message_expires(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    persistent_capture: PersistentCapture,
    freezer: FrozenDateTimeFactory,
) -> None:
    await bell(hass, entry, timeout=60)
    await tick(hass, freezer, 61)
    await settle(hass, entry)
    assert len(persistent_capture.dismiss) == 1


async def test_the_entry_is_dismissed_when_the_condition_ends(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    hass.states.async_set("binary_sensor.leak", "on")
    await bell(hass, entry, condition={"entity_id": "binary_sensor.leak", "state": "on"})
    hass.states.async_set("binary_sensor.leak", "off")
    await settle(hass, entry)
    assert len(persistent_capture.dismiss) == 1


async def test_a_dismissal_by_one_user_leaves_the_bell_alone(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry, channels=["banner", "persistent"])
    entry.runtime_data.dismiss("m", "some-user")
    await settle(hass, entry)
    assert (
        not persistent_capture.dismiss
    )  # the bell is shared; only the end of the message clears it


async def test_a_message_waiting_for_its_condition_creates_nothing_yet(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    hass.states.async_set("binary_sensor.leak", "off")
    await bell(hass, entry, condition={"entity_id": "binary_sensor.leak", "state": "on"})
    assert not persistent_capture.create
    hass.states.async_set("binary_sensor.leak", "on")
    await settle(hass, entry)
    assert len(persistent_capture.create) == 1


async def test_a_restart_does_not_create_the_entry_again(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry)
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(persistent_capture.create) == 1 and not persistent_capture.dismiss


async def test_an_entry_of_a_message_that_ended_while_stopped_is_dismissed_at_startup(
    hass: HomeAssistant, entry: MockConfigEntry, persistent_capture: PersistentCapture
) -> None:
    await bell(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    from homeassistant.helpers.storage import Store

    await Store(hass, 1, "heads_up.banners").async_save({"banners": []})
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await settle(hass, entry)
    assert [c.data for c in persistent_capture.dismiss] == [{"notification_id": "hu_m"}]


async def test_a_missing_service_is_reported_once_in_the_trace(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await bell(hass, entry)
    assert "service_not_found" in reasons(entry)


async def test_a_failing_service_is_a_failed_delivery(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    async def boom(call: ServiceCall) -> None:
        raise HomeAssistantError("no")

    hass.services.async_register("persistent_notification", "create", boom)
    await bell(hass, entry)
    assert "send_failed" in reasons(entry)


async def test_a_call_that_names_a_target_for_it_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(Exception):  # noqa: B017
        await bell(hass, entry, to={"persistent": {"recipients": ["person.anna"]}})


async def test_a_rule_message_reaches_the_bell_through_an_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    persistent_capture: PersistentCapture,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    from ..test_rules import WINDOW, add_rule

    await make_household(hass, mobile_app_device)
    escalation = {**ESCALATION, "channels": ["persistent"], "targets": {}, "tags": ["rule"]}
    await add_policy(hass, entry, "Rules", **escalation)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="critical")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    assert not persistent_capture.create
    await tick(hass, freezer, 6 * 60)
    await settle(hass, entry)
    assert len(persistent_capture.create) == 1
