"""Conditions: once/recurring, wait_for_condition, unavailable, restart (D-005, D-006, D-038)."""

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners

WINDOW = "binary_sensor.window"
SENSOR = "sensor.heads_up_active_banners"


def cond(**extra: object) -> dict[str, object]:
    return {"entity_id": WINDOW, **extra}


def is_active(entry: MockConfigEntry, banner_id: str) -> bool:
    return entry.runtime_data.is_active(banners(entry)[banner_id])


async def set_state(hass: HomeAssistant, state: str, **attrs: object) -> None:
    hass.states.async_set(WINDOW, state, attrs)
    await hass.async_block_till_done()


async def test_true_at_creation_is_active(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    assert await create(id="w", message="x", condition=cond()) == {"id": "w", "status": "created"}
    assert is_active(entry, "w")


async def test_once_is_removed_when_condition_turns_false(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond(), tag="t")
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")

    await set_state(hass, "off")
    assert "w" not in banners(entry)
    assert [e.data for e in events] == [{"id": "w", "tag": "t", "reason": "condition"}]

    await set_state(hass, "on")
    assert "w" not in banners(entry)


async def test_once_waits_for_first_true_when_false_at_creation(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "off")
    assert (await create(id="w", message="x", condition=cond()))["status"] == "waiting"
    assert not is_active(entry, "w")
    assert hass.states.get(SENSOR).state == "0"

    await set_state(hass, "on")
    assert is_active(entry, "w")
    assert hass.states.get(SENSOR).state == "1"

    await set_state(hass, "off")
    assert "w" not in banners(entry)


async def test_wait_for_condition_false_rejects_when_false(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "off")
    result = await create(id="w", message="x", condition=cond(), wait_for_condition=False)
    assert result == {"id": "w", "status": "condition_false"}
    assert banners(entry) == {}


async def test_wait_for_condition_false_upsert_removes_existing(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="w", message="old")
    await set_state(hass, "off")
    events = async_capture_events(hass, f"{DOMAIN}_banner_cleared")

    result = await create(id="w", message="new", condition=cond(), wait_for_condition=False)
    assert result["status"] == "condition_false"
    assert banners(entry) == {}
    assert events[0].data["reason"] == "condition"


async def test_recurring_hides_and_reshows_with_dismissals_reset(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond(), mode="recurring")
    entry.runtime_data.dismiss("w", "user-1")

    await set_state(hass, "off")
    assert "w" in banners(entry) and not is_active(entry, "w")
    assert entry.runtime_data.visible("user-2") == []

    await set_state(hass, "on")
    assert is_active(entry, "w")
    assert banners(entry)["w"].dismissed_by == []
    assert [b["id"] for b in entry.runtime_data.visible("user-1")] == ["w"]


@pytest.mark.parametrize("bad", ["unavailable", "unknown"])
async def test_unavailable_keeps_visibility(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner, bad: str
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond())
    await set_state(hass, bad)
    assert is_active(entry, "w")
    await set_state(hass, "on")
    assert is_active(entry, "w")


async def test_unavailable_at_creation_counts_as_not_true(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "unavailable")
    assert (await create(id="w", message="x", condition=cond()))["status"] == "waiting"
    await set_state(hass, "on")
    assert is_active(entry, "w")


async def test_entity_removed_keeps_banner(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond())
    hass.states.async_remove(WINDOW)
    await hass.async_block_till_done()
    assert is_active(entry, "w")


async def test_missing_entity_at_creation_fails(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await create(id="w", message="x", condition={"entity_id": "binary_sensor.nope"})
    assert err.value.translation_key == "entity_not_found"


async def test_state_list_and_attribute_match(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "away", mode="night")
    await create(id="list", message="x", condition=cond(state=["home", "away"]))
    await create(id="attr", message="x", condition=cond(attribute="mode", state="night"))
    assert is_active(entry, "list") and is_active(entry, "attr")

    await set_state(hass, "away", mode="day")
    assert "attr" not in banners(entry)
    assert is_active(entry, "list")


async def test_upsert_reevaluates_condition(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "off")
    await create(id="w", message="x", condition=cond())
    await create(id="w", message="x")  # replaced without condition
    assert is_active(entry, "w")
    await set_state(hass, "on")
    await set_state(hass, "off")
    assert "w" in banners(entry)  # no longer bound to the entity


async def test_condition_survives_restart_and_is_reevaluated(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond())
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    await set_state(hass, "off")  # changed while not loaded
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert "w" not in banners(entry)


async def test_restart_with_entity_not_yet_loaded_keeps_state(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond())
    assert await hass.config_entries.async_unload(entry.entry_id)
    hass.states.async_remove(WINDOW)  # as at HA start, before the entity's integration loads
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert is_active(entry, "w")

    await set_state(hass, "off")
    assert "w" not in banners(entry)


async def test_listeners_are_released(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    await create(id="w", message="x", condition=cond())
    assert entry.runtime_data.tracked_entities == {WINDOW}
    await hass.services.async_call(DOMAIN, "clear_all", {}, blocking=True)
    assert entry.runtime_data.tracked_entities == set()


@pytest.mark.parametrize(
    "data",
    [
        {"condition": {"state": "on"}},
        {"condition": {"entity_id": "not an id"}},
        {"condition": cond(), "mode": "sometimes"},
        {"people": ["light.kitchen"]},
    ],
)
async def test_invalid_condition_or_people(
    hass: HomeAssistant, entry: MockConfigEntry, data: dict
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "create_banner", {"message": "x", **data}, blocking=True
        )
