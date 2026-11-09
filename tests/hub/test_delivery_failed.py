"""The event heads_up_delivery_failed: one per channel and delivery step (D-128)."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import area_registry as ar
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import FakeDevice, capture_persistent, set_person, settle
from .policy_support import REMINDER, add_policy, make_household, send, wait
from .test_recipients_groups import add_group

EVENT = f"{DOMAIN}_delivery_failed"


async def push(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> None:
    body = {
        "id": "m",
        "message": "Window open",
        "channels": ["push"],
        "to": {"push": {"recipients": ["person.anna"]}},
        **data,
    }
    await hass.services.async_call(DOMAIN, "notify", body, blocking=True)
    await settle(hass, entry)


def fail_sends(hass: HomeAssistant, phone: FakeDevice) -> None:
    async def broken(call: ServiceCall) -> None:
        raise HomeAssistantError("app unreachable")

    hass.services.async_register("notify", phone.notify_service, broken)


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def test_a_failed_send_fires_the_event_with_the_reason(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    fail_sends(hass, anna)
    events = async_capture_events(hass, EVENT)
    await push(hass, entry, tag="windows")
    (event,) = events
    assert event.data == {
        "id": "m",
        "tag": "windows",
        "channel": "push",
        "origin": "message",
        "reached": 0,
        "failed": [
            {
                "recipient": event.data["failed"][0]["recipient"],
                "reason": "send_failed",
                "person": "person.anna",
            }
        ],
    }


async def test_a_person_without_a_device_fires_it_as_nobody_to_deliver_to(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    events = async_capture_events(hass, EVENT)
    await push(hass, entry)
    (event,) = events
    assert event.data["reached"] == 0
    assert [f["reason"] for f in event.data["failed"]] == ["no_usable_device"]


async def test_an_audience_with_nobody_in_it_fires_it(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    set_person(hass, "person.anna", "not_home", user_id="anna-id")
    events = async_capture_events(hass, EVENT)
    await push(hass, entry, to={"push": {"audience": "At home"}})
    (event,) = events
    assert event.data["failed"] == [{"recipient": "", "reason": "no_recipients"}]


async def test_one_failing_device_among_two_reports_the_other_as_reached(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    fail_sends(hass, home.ben)
    events = async_capture_events(hass, EVENT)
    await push(hass, entry, to={"push": {"recipients": ["person.anna", "person.ben"]}})
    (event,) = events
    assert event.data["reached"] == 1
    assert [f["person"] for f in event.data["failed"]] == ["person.ben"]


async def test_a_push_over_the_rate_limit_fires_it(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.hub.limiter.per_device = 1
    await push(hass, entry, id="first")
    events = async_capture_events(hass, EVENT)
    await push(hass, entry, id="second")
    (event,) = events
    assert [f["reason"] for f in event.data["failed"]] == ["rate_limited"]


async def test_a_duplicate_update_is_not_a_failure(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry)
    events = async_capture_events(hass, EVENT)
    await push(hass, entry)
    assert events == []


async def test_a_working_delivery_fires_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    events = async_capture_events(hass, EVENT)
    await push(hass, entry)
    assert events == []


async def test_the_dry_run_fires_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    events = async_capture_events(hass, EVENT)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {
            "type": "heads_up/hub_plan",
            "message": "x",
            "severity": "info",
            "channels": ["push"],
            "to": {"push": {"recipients": ["person.anna"]}},
        }
    )
    assert (await client.receive_json())["success"]
    assert events == []


async def test_a_reminder_that_fails_fires_it_with_its_origin(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Again", **REMINDER)
    await send(hass, entry)
    fail_sends(hass, home.anna)
    events = async_capture_events(hass, EVENT)
    await wait(hass, entry, freezer, 10.1)
    assert [e.data["origin"] for e in events] == ["reminder"]
    assert events[0].data["failed"][0]["reason"] == "send_failed"


async def test_an_escalation_to_an_empty_group_fires_it_and_leaves_a_bell_entry(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    add_group(hass, entry, "Nobody", members=["media_player.gone"], areas=[])
    await add_policy(
        hass,
        entry,
        "Speak up",
        type="escalation",
        after_minutes=5,
        channels=["speak"],
        targets={"speak": {"recipients": ["Nobody (group)"]}},
    )
    bell = capture_persistent(hass)
    await send(hass, entry)
    events = async_capture_events(hass, EVENT)
    await wait(hass, entry, freezer, 5.1)
    assert [e.data["origin"] for e in events] == ["escalation"]
    assert events[0].data["channel"] == "speak"
    assert [c.data["notification_id"] for c in bell.create] == ["heads_up_warning_nobody_group"]


async def test_a_speech_area_without_a_speaker_fires_it(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    area = ar.async_get(hass).async_create("Garage")
    events = async_capture_events(hass, EVENT)
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "m",
            "message": "x",
            "channels": ["speak"],
            "to": {"speak": {"recipients": [area.id]}},
        },
        blocking=True,
    )
    await settle(hass, entry)
    assert [f["reason"] for f in events[0].data["failed"]] == ["group_empty"]
