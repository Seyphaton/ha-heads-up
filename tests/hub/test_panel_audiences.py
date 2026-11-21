"""The six built-in audiences with who is in them now, in one call (plan 18.3)."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.auth.models import User
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from .helpers import set_person


@pytest.fixture
def options() -> dict[str, Any]:
    return {"presence_debounce_seconds": 0}


async def ask(client: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/panel_audiences"})
    reply = await client.receive_json()
    assert reply["success"], reply
    return dict(reply["result"])


def by_key(result: dict[str, Any]) -> dict[str, Any]:
    return {a["key"]: a for a in result["audiences"]}


def members(audience: dict[str, Any]) -> list[str]:
    return [m["person"] for m in audience["members"]]


async def test_the_command_is_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "heads_up/panel_audiences"})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"


async def test_the_six_audiences_come_in_the_order_of_the_tour_with_the_people_and_their_state(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
) -> None:
    set_person(hass, "person.anna", "home", user_id=hass_admin_user.id)
    set_person(hass, "person.ben", "not_home")
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    result = await ask(client)
    assert [a["key"] for a in result["audiences"]] == [
        "everyone",
        "admins",
        "at_home",
        "not_home",
        "last_to_leave",
        "first_home",
    ]
    assert {p["person"]: p["home"] for p in result["people"]} == {
        "person.anna": True,
        "person.ben": False,
    }
    audiences = by_key(result)
    assert members(audiences["everyone"]) == ["person.anna", "person.ben"]
    assert members(audiences["admins"]) == ["person.anna"]
    assert members(audiences["at_home"]) == ["person.anna"]
    assert members(audiences["not_home"]) == ["person.ben"]
    assert members(audiences["last_to_leave"]) == [] == members(audiences["first_home"])
    assert all(a["enabled"] for a in result["audiences"])
    assert audiences["everyone"]["members"][0]["reason"] == "everyone"


async def test_last_to_leave_and_first_home_carry_their_times(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    freezer: FrozenDateTimeFactory,
) -> None:
    client = await hass_ws_client(hass)  # before the clock moves: tokens expire in frozen time
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    freezer.move_to("2026-11-02 17:40:00+00:00")
    set_person(hass, "person.anna", "not_home")
    await hass.async_block_till_done()
    audiences = by_key(await ask(client))
    assert audiences["last_to_leave"]["at"].startswith("2026-11-02T17:40:00")
    assert members(audiences["last_to_leave"]) == ["person.anna"]
    assert audiences["first_home"]["at"] is None and audiences["everyone"]["at"] is None
    freezer.move_to("2026-11-03 07:12:00+00:00")
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    audiences = by_key(await ask(client))
    assert audiences["first_home"]["at"].startswith("2026-11-03T07:12:00")
    assert audiences["last_to_leave"]["at"] is None


async def test_a_switched_off_audience_is_listed_as_disabled(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    entry.runtime_data.options["audiences_disabled"] = ["not_home"]
    client = await hass_ws_client(hass)
    audiences = by_key(await ask(client))
    assert audiences["not_home"]["enabled"] is False and audiences["everyone"]["enabled"] is True
