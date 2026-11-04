"""Scenario: a message to everyone at home; when nobody is home, to every household member.

The household fallback is a Fallback policy with the audience Everyone. These tests record what it
does and where it stops.
"""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import AddDevice
from .policy_support import add_policy, make_household, move, pushes, send, trace

EVERYONE_PUSH = {
    "type": "fallback",
    "when": "no_audience",
    "channels": ["push"],
    "targets": {"push": {"audience": "Everyone"}},
}
AT_HOME = {"push": {"audience": "At home"}}


async def empty_house(hass: HomeAssistant) -> None:
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")


async def test_with_someone_home_only_those_at_home_are_notified(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    await add_policy(hass, entry, "Household", **EVERYONE_PUSH)
    await send(hass, entry, severity="warning", to=AT_HOME)
    assert len(pushes(home.ben)) == 1 and not pushes(home.anna)


async def test_with_nobody_home_the_audience_everyone_is_notified(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await empty_house(hass)
    await add_policy(hass, entry, "Household", **EVERYONE_PUSH)
    await send(hass, entry, severity="warning", to=AT_HOME)
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1
    assert any(e["result"] == "fallback" for e in trace(entry))


async def test_an_away_policy_holds_the_fallback_to_an_audience_until_arrival(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await empty_house(hass)
    await add_policy(hass, entry, "Back", type="away")
    await add_policy(hass, entry, "Household", **EVERYONE_PUSH)
    await send(hass, entry, severity="warning", to=AT_HOME)
    # Everyone is away, so Away holds the fallback until each person arrives.
    assert not pushes(home.anna) and not pushes(home.ben)


async def test_the_fallback_with_named_recipients_is_not_held_by_away(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await empty_house(hass)
    await add_policy(hass, entry, "Back", type="away")
    await add_policy(
        hass,
        entry,
        "Household",
        **{**EVERYONE_PUSH, "targets": {"push": {"recipients": ["person.anna", "person.ben"]}}},
    )
    await send(hass, entry, severity="warning", to=AT_HOME)
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1


async def test_the_fallback_uses_its_own_channels_not_those_of_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await empty_house(hass)
    await add_policy(hass, entry, "Household", **EVERYONE_PUSH)
    # The call asked for a popup; nobody is home, so the fallback sends a push, not a popup.
    await send(
        hass, entry, severity="warning", channels=["popup"], to={"popup": {"audience": "At home"}}
    )
    assert len(pushes(home.anna)) == 1
