"""`create_banner` takes an audience or recipients, like `notify` (D-195)."""

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import CreateBanner, banners


@pytest.fixture(autouse=True)
def persons(hass: HomeAssistant) -> None:
    for name in ("anna", "ben"):
        hass.states.async_set(f"person.{name}", "home" if name == "anna" else "not_home")


async def test_recipients_limit_the_banner_to_those_persons(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="r", message="x", recipients=["person.anna"])
    assert banners(entry)["r"].people == ["person.anna"]


async def test_an_audience_is_resolved_when_the_banner_is_created(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", audience="At home")
    assert banners(entry)["a"].people == ["person.anna"]


async def test_an_audience_can_be_given_by_its_sensor(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", audience="binary_sensor.heads_up_audience_not_home")
    assert banners(entry)["a"].people == ["person.ben"]


async def test_the_everyone_audience_limits_nothing(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="e", message="x", audience="Everyone")
    assert banners(entry)["e"].people == []


async def test_people_still_works_as_before(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="p", message="x", people=["person.ben"])
    assert banners(entry)["p"].people == ["person.ben"]


@pytest.mark.parametrize(
    "extra",
    [
        {"audience": "At home", "recipients": ["person.anna"]},
        {"audience": "At home", "people": ["person.anna"]},
        {"recipients": ["person.anna"], "people": ["person.ben"]},
    ],
)
async def test_only_one_way_to_name_the_people(
    create: CreateBanner, extra: dict[str, object]
) -> None:
    with pytest.raises(vol.Invalid):
        await create(id="x", message="x", **extra)
