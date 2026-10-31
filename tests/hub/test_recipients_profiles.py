"""Recipient profiles: detected devices, manual changes, resolution per channel (D-088, N-71)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .helpers import set_person


def resolver(entry: MockConfigEntry) -> Any:
    return entry.runtime_data.hub.resolver


def add_profile(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data=data, subentry_type="recipient_profile", title="Profile", unique_id=None
        ),
    )


async def test_every_person_has_a_profile_with_the_detected_devices(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    profile = resolver(entry).profile("person.anna")
    assert [(d.device_id, d.name, d.source) for d in profile.devices] == [
        (phone.device_id, "Anna's phone", "detected")
    ]
    assert profile.devices[0].service == phone.notify_service
    assert profile.devices[0].service_found is True
    assert profile.primary == phone.device_id
    assert profile.channels == ("banner", "push", "popup")
    assert profile.customized is False


async def test_all_devices_of_a_person_are_detected(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    await mobile_app_device("Anna's tablet", person_entity_id="person.anna")
    assert len(resolver(entry).profile("person.anna").devices) == 2


async def test_a_tracker_from_another_integration_is_skipped(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    tracker = er.async_get(hass).async_get_or_create("device_tracker", "router", "aa:bb")
    set_person(hass, "person.anna", "home", device_trackers=[tracker.entity_id])
    assert resolver(entry).profile("person.anna").devices == []


async def test_a_device_whose_notify_service_is_missing_is_flagged(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    hass.services.async_remove("notify", phone.notify_service)
    (device,) = resolver(entry).profile("person.anna").devices
    assert device.service_found is False
    result = await resolver(entry).resolve({"recipients": ["person.anna"]}, "push", "warning")
    assert result.recipients == []
    assert {(s.who, s.reason) for s in result.skipped} == {
        (f"device:{phone.device_id}", "service_not_found"),
        ("person.anna", "no_usable_device"),
    }


async def test_a_manual_device_is_added_and_a_detected_one_removed(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    old = await mobile_app_device("Old phone", person_entity_id="person.anna")
    spare = await mobile_app_device("Spare phone")  # not tied to any person
    add_profile(
        hass,
        entry,
        person="person.anna",
        devices=[spare.device_id],
        removed_devices=[old.device_id],
        primary=spare.device_id,
        channels=["push"],
    )
    await hass.async_block_till_done()
    profile = resolver(entry).profile("person.anna")
    assert [(d.device_id, d.source) for d in profile.devices] == [
        (phone.device_id, "detected"),
        (spare.device_id, "manual"),
    ]
    assert profile.primary == spare.device_id
    assert profile.channels == ("push",) and profile.customized is True


async def test_a_stored_device_that_no_longer_exists_is_reported_missing(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    add_profile(hass, entry, person="person.anna", devices=["gone"])
    await hass.async_block_till_done()
    result = await resolver(entry).resolve({"recipients": ["person.anna"]}, "push", "warning")
    assert ("device:gone", "device_missing") in {(s.who, s.reason) for s in result.skipped}


async def test_push_goes_to_every_device_with_the_service_worked_out_now(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    tablet = await mobile_app_device("Anna's tablet", person_entity_id="person.anna")
    result = await resolver(entry).resolve({"recipients": ["person.anna"]}, "push", "warning")
    assert {(r.key, r.service, r.person) for r in result.recipients} == {
        (f"device:{phone.device_id}", phone.notify_service, "person.anna"),
        (f"device:{tablet.device_id}", tablet.notify_service, "person.anna"),
    }


async def test_a_renamed_device_changes_the_service_but_not_the_stored_id(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    hass.config_entries.async_update_entry(
        phone.entry, data={**phone.entry.data, "device_name": "Anna's new phone"}
    )
    fake_notify = hass.services.async_register  # the renamed service is registered by the app
    fake_notify("notify", "mobile_app_anna_s_new_phone", lambda call: None)
    result = await resolver(entry).resolve({"recipients": ["person.anna"]}, "push", "warning")
    (recipient,) = result.recipients
    assert recipient.key == f"device:{phone.device_id}"
    assert recipient.service == "mobile_app_anna_s_new_phone"


async def test_a_person_without_a_device_is_skipped_on_push_only(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    push = await resolver(entry).resolve({"recipients": ["person.anna"]}, "push", "warning")
    assert [(s.who, s.reason) for s in push.skipped] == [("person.anna", "no_usable_device")]
    popup = await resolver(entry).resolve({"recipients": ["person.anna"]}, "popup", "warning")
    assert [r.key for r in popup.recipients] == ["person.anna"]


async def test_a_channel_the_profile_does_not_accept_is_skipped(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    add_profile(hass, entry, person="person.anna", channels=["banner"])
    await hass.async_block_till_done()
    popup = await resolver(entry).resolve({"recipients": ["person.anna"]}, "popup", "warning")
    assert [(s.who, s.reason) for s in popup.skipped] == [("person.anna", "channel_not_accepted")]


async def test_push_to_an_audience_expands_to_devices(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "not_home")
    phone = await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    await mobile_app_device("Ben's phone", person_entity_id="person.ben")
    result = await resolver(entry).resolve({"audience": "At home"}, "push", "warning")
    assert [r.key for r in result.recipients] == [f"device:{phone.device_id}"]


async def test_a_registration_id_is_a_valid_push_recipient(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    spare = await mobile_app_device("Spare phone")
    assert spare.device_id in resolver(entry).known("push")
    result = await resolver(entry).resolve({"recipients": [spare.device_id]}, "push", "warning")
    assert [r.service for r in result.recipients] == [spare.notify_service]


async def test_an_audience_in_a_call_reaches_the_device(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    from custom_components.heads_up.const import DOMAIN

    set_person(hass, "person.anna", "home")
    await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    response = await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "a", "message": "x", "channels": ["push"], "to": {"push": {"audience": "At home"}}},
        blocking=True,
        return_response=True,
    )
    assert response is not None
    assert response["channels"]["push"] == {"sent": 1, "held": 0, "skipped": 0, "failed": 0}
