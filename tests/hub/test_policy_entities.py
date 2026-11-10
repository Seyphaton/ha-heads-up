"""One switch per policy, and a call may name it (D-186)."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..conftest import banners
from .conftest import AddDevice
from .policy_support import ESCALATION, add_policy, make_household, send


def switch_of(hass: HomeAssistant, subentry_id: str) -> str | None:
    for registered in er.async_get(hass).entities.values():
        if registered.platform == DOMAIN and registered.unique_id.endswith(
            f"_policy_{subentry_id}"
        ):
            return registered.entity_id
    return None


async def test_a_policy_has_a_switch_that_follows_and_sets_enabled(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    subentry = await add_policy(hass, entry, "Water", **ESCALATION)
    found = switch_of(hass, subentry.subentry_id)
    assert found is not None
    assert hass.states.get(found).state == "on"  # type: ignore[union-attr]
    await hass.services.async_call("switch", "turn_off", {"entity_id": found}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get(found).state == "off"  # type: ignore[union-attr]
    assert entry.subentries[subentry.subentry_id].data["enabled"] is False
    assert [p.name for p in entry.runtime_data.hub.policies.all() if p.enabled] == []


async def test_a_deleted_policy_loses_its_switch(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    subentry = await add_policy(hass, entry, "Water", **ESCALATION)
    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    await hass.async_block_till_done()
    assert switch_of(hass, subentry.subentry_id) is None


async def test_a_call_can_name_the_switch_of_a_manual_policy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    subentry = await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    found = switch_of(hass, subentry.subentry_id)
    assert found is not None
    await send(hass, entry, policy=[found])
    assert banners(entry)["m"].policy == ["automatic", subentry.subentry_id]
