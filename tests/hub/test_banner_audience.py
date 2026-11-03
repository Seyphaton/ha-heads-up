"""A banner aimed at an audience: the members are worked out when the message is created (D-131)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, MockUser

from custom_components.heads_up.const import BANNER_NOBODY, DOMAIN

from .helpers import set_person


async def notify(hass: HomeAssistant, audience: str, **extra: Any) -> dict[str, Any]:
    response = await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "a",
            "message": "x",
            "channels": ["banner"],
            "to": {"banner": {"audience": audience}},
            **extra,
        },
        blocking=True,
        return_response=True,
    )
    assert response is not None
    return dict(response)


async def test_admins_audience_shows_the_banner_to_administrators_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_admin_user: MockUser,
    hass_read_only_user: MockUser,
) -> None:
    set_person(hass, "person.anna", "home", user_id=hass_admin_user.id)
    set_person(hass, "person.ben", "home", user_id=hass_read_only_user.id)
    set_person(hass, "person.guest", "home")
    await notify(hass, "Admins")
    manager = entry.runtime_data
    assert [b["id"] for b in manager.visible(hass_admin_user.id)] == ["a"]
    assert manager.visible(hass_read_only_user.id) == []
    assert manager.banners["a"].people == ["person.anna"]


async def test_everyone_audience_does_not_limit_the_banner(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    await notify(hass, "Everyone")
    manager = entry.runtime_data
    assert manager.banners["a"].people == []
    assert [b["id"] for b in manager.visible("anyone")] == ["a"]


async def test_an_audience_that_is_empty_gives_a_banner_nobody_sees(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    result = await notify(hass, "Not home")
    manager = entry.runtime_data
    assert manager.banners["a"].people == [BANNER_NOBODY]
    assert manager.visible("anna-id") == []
    assert result["channels"]["banner"] == {"sent": 0, "held": 0, "skipped": 1, "failed": 0}
