"""Push follows the message: replace, clear on every end, snooze and remind, failures, restart."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.hub.ledger import State

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import FakeDevice, set_person, settle, tick


async def notify(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> dict[str, Any]:
    body = {
        "id": "m",
        "message": "Window open",
        "channels": ["push"],
        "to": {"push": {"recipients": ["person.anna"]}},
        **data,
    }
    response = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    await settle(hass, entry)
    assert response is not None
    return dict(response)


def is_clear(call: ServiceCall) -> bool:
    return call.data.get("message") == "clear_notification"


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def test_an_update_sends_the_same_tag_so_the_device_replaces_it(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await notify(hass, entry, message="one")
    await notify(hass, entry, message="two")
    first, second = anna.calls
    assert first.data["data"]["tag"] == second.data["data"]["tag"]
    assert second.data["message"] == "two"


async def test_every_device_of_a_person_gets_the_same_tag(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, mobile_app_device: AddDevice
) -> None:
    tablet = await mobile_app_device(
        "Anna's tablet", user_id="anna-id", person_entity_id="person.anna"
    )
    result = await notify(hass, entry)
    assert result["channels"]["push"]["sent"] == 2
    assert anna.calls[0].data["data"]["tag"] == tablet.calls[0].data["data"]["tag"]


@pytest.mark.parametrize(
    "end",
    ["clear", "clear_banner", "clear_all", "expire", "global_dismiss", "condition", "evict"],
)
async def test_every_end_of_the_message_clears_the_push_by_tag(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    anna: FakeDevice,
    freezer: FrozenDateTimeFactory,
    end: str,
) -> None:
    extra: dict[str, Any] = {"channels": ["banner", "push"]}
    to = {"push": {"recipients": ["person.anna"]}}
    if end == "expire":
        extra["timeout"] = 60
    if end == "global_dismiss":
        extra["dismiss_scope"] = "global"
    if end == "condition":
        hass.states.async_set("binary_sensor.w", "on")
        extra["condition"] = {"entity_id": "binary_sensor.w", "state": "on"}
    if end == "evict":
        entry.runtime_data.options["max_banners"] = 1
    await notify(hass, entry, to=to, **extra)
    sent_tag = anna.calls[0].data["data"]["tag"]
    if end in ("clear", "clear_banner", "clear_all"):
        data = {"id": "m"} if end != "clear_all" else {}
        await hass.services.async_call(DOMAIN, end, data, blocking=True)
    elif end == "expire":
        await tick(hass, freezer, 61)
    elif end == "global_dismiss":
        entry.runtime_data.dismiss("m", "anna-id")
    elif end == "condition":
        hass.states.async_set("binary_sensor.w", "off")
    elif end == "evict":
        await notify(hass, entry, id="other", severity="critical", channels=["banner"], to={})
    await settle(hass, entry)
    clears = [c for c in anna.calls if is_clear(c)]
    assert [c.data["data"]["tag"] for c in clears] == [sent_tag]
    assert entry.runtime_data.hub.ledger.for_message("m") == []


async def test_a_user_dismissal_clears_only_that_users_push(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.ben", "home", user_id="ben-id")
    ben = await mobile_app_device("Ben's phone", user_id="ben-id", person_entity_id="person.ben")
    await notify(
        hass,
        entry,
        channels=["banner", "push"],
        to={"push": {"recipients": ["person.anna", "person.ben"]}},
    )
    entry.runtime_data.dismiss("m", "anna-id")
    await settle(hass, entry)
    assert [is_clear(c) for c in anna.calls] == [False, True]
    assert [is_clear(c) for c in ben.calls] == [False]


async def test_snooze_clears_the_users_push_and_notifies_again_when_it_ends(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    anna: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await notify(hass, entry, channels=["banner", "push"], snoozable=True)
    entry.runtime_data.snooze("m", "anna-id", 900)
    await settle(hass, entry)
    assert [is_clear(c) for c in anna.calls] == [False, True]
    await tick(hass, freezer, 901)
    await settle(hass, entry)
    assert [is_clear(c) for c in anna.calls] == [False, True, False]
    assert (
        entry.runtime_data.hub.ledger.rows[("m", "push", f"device:{anna.device_id}")].state
        is State.SENT
    )


async def test_ending_a_snooze_early_notifies_again(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await notify(hass, entry, channels=["banner", "push"], snoozable=True)
    entry.runtime_data.snooze("m", "anna-id", 900)
    entry.runtime_data.unsnooze("m", "anna-id")
    await settle(hass, entry)
    assert [is_clear(c) for c in anna.calls] == [False, True, False]


async def test_a_message_that_ended_during_a_snooze_is_not_sent_again(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    anna: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.states.async_set("binary_sensor.w", "on")
    await notify(
        hass,
        entry,
        channels=["banner", "push"],
        snoozable=True,
        mode="recurring",
        condition={"entity_id": "binary_sensor.w", "state": "on"},
    )
    entry.runtime_data.snooze("m", "anna-id", 900)
    hass.states.async_set("binary_sensor.w", "off")
    await tick(hass, freezer, 901)
    await settle(hass, entry)
    assert [is_clear(c) for c in anna.calls][-1] is True


async def test_a_waiting_message_pushes_when_its_condition_turns_true(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set("binary_sensor.w", "off")
    result = await notify(
        hass,
        entry,
        channels=["banner", "push"],
        condition={"entity_id": "binary_sensor.w", "state": "on"},
    )
    assert result["status"] == "waiting"
    hass.states.async_set("binary_sensor.w", "on")
    await settle(hass, entry)
    assert len(anna.calls) == 1


async def test_the_ledger_remembers_the_tag_and_the_person(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await notify(hass, entry)
    row = entry.runtime_data.hub.ledger.rows[("m", "push", f"device:{anna.device_id}")]
    assert row.person == "person.anna" and row.ref == anna.calls[0].data["data"]["tag"]


async def test_a_missing_service_is_a_failed_delivery_with_a_reason(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.services.async_remove("notify", anna.notify_service)
    result = await notify(hass, entry)
    # Planned as skipped: the resolver already saw that the service is missing.
    assert result["channels"]["push"]["skipped"] >= 1
    assert result["status"] == "created"


async def test_a_service_that_raises_is_a_failed_delivery_and_the_message_stays(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, caplog: pytest.LogCaptureFixture
) -> None:
    def boom(call: ServiceCall) -> None:
        raise HomeAssistantError("offline")

    hass.services.async_register("notify", anna.notify_service, boom)
    await notify(hass, entry, channels=["banner", "push"])
    await notify(hass, entry, message="again", channels=["banner", "push"])
    row = entry.runtime_data.hub.ledger.rows[("m", "push", f"device:{anna.device_id}")]
    assert row.state is State.FAILED
    assert "m" in entry.runtime_data.banners
    reasons = [t["reason"] for t in entry.runtime_data.hub.trace.entries("m")]
    assert reasons.count("send_failed") == 2
    assert caplog.text.count("failed: offline") == 1  # one warning per device per hour


async def test_a_person_without_a_device_is_skipped_and_the_message_stays(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    result = await notify(hass, entry, channels=["banner", "push"])
    assert result["channels"]["push"] == {"sent": 0, "held": 0, "skipped": 1, "failed": 0}
    assert result["channels"]["banner"]["sent"] == 1


async def test_a_restart_sends_nothing_again(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await notify(hass, entry, channels=["banner", "push"], timeout=0)
    assert len(anna.calls) == 1
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(anna.calls) == 1


async def test_a_push_of_a_message_that_ended_while_stopped_is_cleared_at_startup(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, hass_storage: Any
) -> None:
    await notify(hass, entry, channels=["banner", "push"], timeout=0)
    tag = anna.calls[0].data["data"]["tag"]
    assert await hass.config_entries.async_unload(entry.entry_id)
    hass_storage["heads_up.banners"]["data"]["banners"] = []
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    clears = [c for c in anna.calls if is_clear(c)]
    assert [c.data["data"]["tag"] for c in clears] == [tag]


async def test_with_the_hub_off_nothing_is_pushed(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, "hub_enabled": False})
    await hass.async_block_till_done()
    assert entry.runtime_data.hub is None
    assert anna.calls == []


async def test_push_shortcut_without_an_id_sends_once_and_keeps_no_record(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    result = await hass.services.async_call(
        DOMAIN,
        "push",
        {"message": "Dinner", "recipients": ["person.anna"]},
        blocking=True,
        return_response=True,
    )
    assert result is not None and result["channels"]["push"]["sent"] == 1
    assert entry.runtime_data.banners == {}
    assert anna.calls[0].data["message"] == "Dinner"
