"""An audience and a policy are named by their entity ID, not by their text name (D-198)."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..conftest import banners
from .policy_support import ESCALATION, add_policy

pytestmark = pytest.mark.names_as_given


async def notify(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    body = {"message": "x", "severity": "warning", "channels": ["banner"], **data}
    response = await hass.services.async_call(
        DOMAIN, "notify", body, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def test_an_audience_name_is_refused_with_the_entity_id_to_use(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    for written in ("At home", "at HOME"):
        with pytest.raises(ServiceValidationError) as err:
            await notify(hass, audience=written)
        assert err.value.translation_key == "audience_needs_entity"
        placeholders = err.value.translation_placeholders
        assert placeholders["entity_id"] == "binary_sensor.heads_up_audience_at_home"  # type: ignore[index]


async def test_a_policy_name_is_refused_with_the_entity_id_to_use(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await add_policy(hass, entry, "Night", **ESCALATION)
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, policy="Night")
    assert err.value.translation_key == "policy_needs_entity"
    assert err.value.translation_placeholders["entity_id"] == "switch.heads_up_policy_night"  # type: ignore[index]


async def test_the_entity_ids_and_the_keywords_are_accepted(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    night = await add_policy(hass, entry, "Night", **ESCALATION)
    await notify(
        hass,
        id="a",
        audience="binary_sensor.heads_up_audience_everyone",
        policy="switch.heads_up_policy_night",
    )
    assert banners(entry)["a"].policy == ["automatic", night.subentry_id]
    await notify(hass, id="b", policy="none")
    assert banners(entry)["b"].policy == "none"
    await notify(hass, id="c", policy=["automatic", "switch.heads_up_policy_night"])


async def test_after_a_rename_the_entity_id_still_works_and_the_old_name_does_not(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    subentry = await add_policy(hass, entry, "Night", **ESCALATION)
    hass.config_entries.async_update_subentry(entry, subentry, title="Evening")
    await hass.async_block_till_done()
    await notify(hass, id="a", policy="switch.heads_up_policy_night")
    # The stored key is the ID, so the rename changed nothing that is stored (D-199).
    assert banners(entry)["a"].policy == ["automatic", subentry.subentry_id]
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, policy="Night")
    assert err.value.translation_key.startswith("unknown_policy")


@pytest.mark.parametrize("service", ["push", "popup"])
async def test_the_shortcuts_refuse_an_audience_name_too(
    hass: HomeAssistant, entry: MockConfigEntry, service: str
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, service, {"message": "x", "audience": "At home"}, blocking=True
        )
    assert err.value.translation_key == "audience_needs_entity"


async def test_create_banner_refuses_an_audience_name_too(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "create_banner", {"message": "x", "audience": "At home"}, blocking=True
        )
    assert err.value.translation_key == "audience_needs_entity"
