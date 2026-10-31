"""The acknowledgement fields of the card payload, for action and rule messages (D-116)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import REMINDER, add_policy, make_household, send


def banner(entry: MockConfigEntry, user: str, mid: str = "m") -> dict[str, Any]:
    (found,) = [b for b in entry.runtime_data.visible(user) if b["id"] == mid]
    return dict(found)


async def test_without_a_policy_there_is_nothing_to_acknowledge(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry)
    payload = banner(entry, "anna-id")
    assert payload["can_acknowledge"] is False
    assert payload["acknowledged"] is False and payload["acknowledged_by"] == []


async def test_with_a_policy_the_viewer_can_acknowledge(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    assert banner(entry, "anna-id")["can_acknowledge"] is True


async def test_after_acknowledging_the_first_name_is_shown_and_the_button_goes(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry)
    entry.runtime_data.acknowledge("m", "anna-id")
    for user in ("anna-id", "ben-id"):
        payload = banner(entry, user)
        assert payload["acknowledged"] is True and payload["can_acknowledge"] is False
        assert payload["acknowledged_by"] == [] or payload["acknowledged_by"] == ["Anna"]
    assert banner(entry, "ben-id")["acknowledged_count"] == 1


async def test_the_name_is_the_first_word_of_the_persons_name(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(
        "person.anna", "home", {"user_id": "anna-id", "friendly_name": "Anna Schmidt"}
    )
    await send(hass, entry, channels=["banner"], to={})
    entry.runtime_data.acknowledge("m", "anna-id")
    assert banner(entry, "anna-id")["acknowledged_by"] == ["Anna"]


async def test_two_people_are_counted_in_order(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    for name, user in (("Anna", "anna-id"), ("Ben", "ben-id")):
        hass.states.async_set(
            f"person.{name.lower()}", "home", {"user_id": user, "friendly_name": name}
        )
    await send(hass, entry, channels=["banner"], to={})
    entry.runtime_data.acknowledge("m", "anna-id")
    entry.runtime_data.acknowledge("m", "ben-id")
    payload = banner(entry, "anna-id")
    assert payload["acknowledged_by"] == ["Anna", "Ben"] and payload["acknowledged_count"] == 2


async def test_a_user_without_a_person_is_counted_but_has_no_name(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await send(hass, entry, channels=["banner"], to={})
    entry.runtime_data.acknowledge("m", "stranger")
    payload = banner(entry, "stranger")
    assert payload["acknowledged_by"] == [] and payload["acknowledged_count"] == 1


async def test_a_viewer_who_is_not_a_target_cannot_acknowledge(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, channels=["banner"], to={"banner": {"recipients": ["person.anna"]}})
    (shown,) = entry.runtime_data.visible("other-id", show_all=True)
    assert shown["can_acknowledge"] is False


async def test_a_rule_message_has_the_same_fields(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home", {"user_id": "anna-id", "friendly_name": "Anna"})
    await add_policy(hass, entry, "Rules", **REMINDER, tags=["rule"])
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    (rule_id,) = entry.runtime_data.rules
    payload = banner(entry, "anna-id", rule_id)
    assert payload["can_acknowledge"] is True and payload["acknowledged"] is False
    entry.runtime_data.acknowledge(rule_id, "anna-id")
    payload = banner(entry, "anna-id", rule_id)
    assert payload["acknowledged_by"] == ["Anna"] and payload["can_acknowledge"] is False


async def test_the_websocket_subscription_carries_the_fields(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    await add_policy(hass, entry, "Nag", **REMINDER)
    await send(hass, entry, channels=["banner"], to={})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/subscribe"})
    assert (await client.receive_json())["success"]
    (shown,) = (await client.receive_json())["event"]["banners"]
    assert shown["can_acknowledge"] is True and shown["acknowledged"] is False
