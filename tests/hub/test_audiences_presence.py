"""Last to leave and First home: sequences, debounce, restart (D-080, D-109)."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..test_restart import restart
from .helpers import set_person, tick
from .policy_support import add_audience


def audience_members(entry: MockConfigEntry, name: str) -> Any:
    r = entry.runtime_data.hub.resolver

    async def run() -> list[str]:
        result = await r.members(r.audience(name), "warning")
        return [m.key for m in result.recipients]

    return run()


@pytest.fixture
def options() -> dict[str, Any]:
    return {"presence_debounce_seconds": 0}


async def test_last_to_leave_is_the_person_who_emptied_the_house(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await hass.async_block_till_done()
    set_person(hass, "person.anna", "not_home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == []  # Ben is still home
    set_person(hass, "person.ben", "not_home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == ["person.ben"]


async def test_last_to_leave_is_empty_once_someone_is_home_again(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    set_person(hass, "person.anna", "not_home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == ["person.anna"]
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == []


async def test_first_home_is_the_first_arrival_after_an_empty_house(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "not_home")
    set_person(hass, "person.ben", "not_home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "First home") == []  # nobody is home
    set_person(hass, "person.ben", "home")
    await hass.async_block_till_done()
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "First home") == ["person.ben"]


async def test_unknown_states_change_nothing(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    set_person(hass, "person.anna", None)
    await hass.async_block_till_done()
    assert entry.runtime_data.hub.resolver.presence.home == {"person.anna"}
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    assert entry.runtime_data.hub.resolver.presence.home == {"person.anna"}


async def test_a_person_appearing_at_startup_is_not_an_arrival(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")  # first state of a new entity: old_state is None
    await hass.async_block_till_done()
    assert await audience_members(entry, "First home") == []
    presence = entry.runtime_data.hub.resolver.presence
    assert presence.home == {"person.anna"} and presence.first_home is None


async def test_deleting_a_home_person_counts_as_leaving(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    hass.states.async_remove("person.anna")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == []  # the entity is gone


class TestDebounce:
    @pytest.fixture
    def options(self) -> dict[str, Any]:  # type: ignore[override]
        return {"presence_debounce_seconds": 60}

    async def test_a_short_absence_is_ignored(
        self, hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
    ) -> None:
        set_person(hass, "person.anna", "home")
        await hass.async_block_till_done()
        set_person(hass, "person.anna", "not_home")
        await hass.async_block_till_done()
        await tick(hass, freezer, 30)
        set_person(hass, "person.anna", "home")  # the GPS flapped back
        await hass.async_block_till_done()
        await tick(hass, freezer, 120)
        presence = entry.runtime_data.hub.resolver.presence
        assert presence.home == {"person.anna"}
        assert await audience_members(entry, "Last to leave") == []

    async def test_a_lasting_absence_counts_after_the_delay(
        self, hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
    ) -> None:
        set_person(hass, "person.anna", "home")
        await hass.async_block_till_done()
        set_person(hass, "person.anna", "not_home")
        await hass.async_block_till_done()
        await tick(hass, freezer, 59)
        assert entry.runtime_data.hub.resolver.presence.home == {"person.anna"}
        await tick(hass, freezer, 2)
        assert entry.runtime_data.hub.resolver.presence.home == set()
        assert await audience_members(entry, "Last to leave") == ["person.anna"]


async def test_last_to_leave_survives_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await hass.async_block_till_done()
    set_person(hass, "person.anna", "not_home")
    await hass.async_block_till_done()
    await restart(hass, entry)
    assert await audience_members(entry, "Last to leave") == ["person.anna"]


async def test_a_limited_last_to_leave_names_the_person_only_when_they_are_in_the_limit(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    set_person(hass, "person.ben", "home")
    await add_audience(
        hass, entry, "Anna last", kind="presence", presence="last_to_leave", limit=["person.anna"]
    )
    await add_audience(
        hass, entry, "Ben last", kind="presence", presence="last_to_leave", limit=["person.ben"]
    )
    set_person(hass, "person.anna", "not_home")
    await hass.async_block_till_done()
    set_person(hass, "person.ben", "not_home")
    await hass.async_block_till_done()
    assert await audience_members(entry, "Last to leave") == ["person.ben"]
    assert await audience_members(entry, "Anna last") == []
    assert await audience_members(entry, "Ben last") == ["person.ben"]
