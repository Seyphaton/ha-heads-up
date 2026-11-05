"""A disabled recipient gets nothing on any channel (D-147)."""

from typing import Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import BANNER_NOBODY, DOMAIN, EVENT_DELIVERY_FAILED
from custom_components.heads_up.hub.panel_data import check_devices, check_people

from .conftest import AddDevice
from .helpers import set_person, settle
from .test_audiences_flows import run, subentries


async def notify(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    response = await hass.services.async_call(
        DOMAIN, "notify", data, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


def disable(hass: HomeAssistant, entry: MockConfigEntry, person: str) -> None:
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": person, "enabled": False, "channels": ["banner", "push", "popup"]},
            subentry_type="recipient_profile",
            title=person,
            unique_id=None,
        ),
    )


def reasons(entry: MockConfigEntry, message_id: str) -> dict[str, str]:
    return {t["recipient"]: t["reason"] for t in entry.runtime_data.hub.trace.entries(message_id)}


async def test_a_disabled_person_is_skipped_in_an_audience(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    await mobile_app_device("Ben's phone", person_entity_id="person.ben")
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    result = await notify(
        hass, id="a", message="x", channels=["push"], to={"push": {"audience": "Everyone"}}
    )
    assert result["channels"]["push"] == {"sent": 1, "held": 0, "skipped": 1, "failed": 0}
    await settle(hass, entry)
    assert reasons(entry, "a")["person.anna"] == "recipient_disabled"


async def test_a_disabled_person_is_skipped_when_named_and_for_critical_messages(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    set_person(hass, "person.anna", "home", user_id="user-anna")
    await mobile_app_device("Anna's phone", person_entity_id="person.anna")
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    result = await notify(
        hass,
        id="c",
        message="x",
        severity="critical",
        channels=["push", "popup"],
        to={"push": {"recipients": ["person.anna"]}, "popup": {"recipients": ["person.anna"]}},
    )
    assert result["channels"]["push"]["sent"] == 0 and result["channels"]["popup"]["sent"] == 0
    await settle(hass, entry)
    assert {t["reason"] for t in entry.runtime_data.hub.trace.entries("c")} == {
        "recipient_disabled"
    }


async def test_a_banner_for_named_persons_skips_the_disabled_ones(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    banners = entry.runtime_data.banners
    await notify(
        hass,
        id="both",
        message="x",
        channels=["banner"],
        to={"banner": {"recipients": ["person.anna", "person.ben"]}},
    )
    assert banners["both"].people == ["person.ben"]
    # Only disabled persons: the banner is for nobody, not for everyone.
    await notify(
        hass,
        id="only",
        message="x",
        channels=["banner"],
        to={"banner": {"recipients": ["person.anna"]}},
    )
    assert banners["only"].people == [BANNER_NOBODY]


async def test_a_rule_banner_skips_disabled_persons_and_follows_the_profile(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from ..test_rules import add_rule, rule_id, set_state

    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await set_state(hass, "on")
    sub = add_rule(hass, entry, people=["person.anna", "person.ben"])
    await hass.async_block_till_done()
    manager = entry.runtime_data
    assert manager.rules[rule_id(sub)].people == ["person.anna", "person.ben"]

    disable(hass, entry, "person.anna")  # the profile changes after the rule exists
    await hass.async_block_till_done()
    assert manager.rules[rule_id(sub)].people == ["person.ben"]

    disable(hass, entry, "person.ben")
    await hass.async_block_till_done()
    assert manager.rules[rule_id(sub)].people == [BANNER_NOBODY]
    assert manager.visible("anyone") == []


async def test_a_rule_without_people_stays_visible_to_everyone(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from ..test_rules import add_rule, rule_id, set_state

    await set_state(hass, "on")
    sub = add_rule(hass, entry)
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    assert entry.runtime_data.rules[rule_id(sub)].people == []
    assert [b["id"] for b in entry.runtime_data.visible("anyone")] == [rule_id(sub)]


async def test_a_banner_without_a_target_stays_visible(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    await notify(
        hass, id="all", message="x", channels=["banner"], to={"banner": {"audience": "Everyone"}}
    )
    assert entry.runtime_data.banners["all"].people == []


async def test_the_profile_form_stores_enabled_only_when_it_is_off(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    off = await run(
        hass,
        entry,
        "recipient_profile",
        {"person": "person.anna", "enabled": False, "channels": ["push"]},
    )
    assert off["type"] is FlowResultType.CREATE_ENTRY
    await run(hass, entry, "recipient_profile", {"person": "person.ben", "channels": ["push"]})
    stored = {s.data["person"]: dict(s.data) for s in subentries(entry, "recipient_profile")}
    assert stored["person.anna"]["enabled"] is False
    assert "enabled" not in stored["person.ben"]
    await hass.async_block_till_done()
    resolver = entry.runtime_data.hub.resolver
    assert resolver.profile("person.anna").enabled is False
    assert resolver.profile("person.ben").enabled is True


def test_a_disabled_person_is_not_flagged_for_a_missing_device() -> None:
    profiles = [
        {"name": "Anna", "enabled": False, "channels": ["push"], "devices": []},
        {"name": "Ben", "enabled": True, "channels": ["push"], "devices": []},
    ]
    assert [i.subject for i in check_people(profiles)] == ["Ben"]
    broken = [{"name": "Phone", "device_id": "d", "service_found": False}]
    assert check_devices([{**profiles[0], "devices": broken}]) == []


async def test_skipping_a_disabled_person_is_a_choice_not_a_failure(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    disable(hass, entry, "person.anna")
    await hass.async_block_till_done()
    failures = async_capture_events(hass, EVENT_DELIVERY_FAILED)
    await notify(
        hass, id="f", message="x", channels=["push"], to={"push": {"recipients": ["person.anna"]}}
    )
    await settle(hass, entry)
    assert failures == []
