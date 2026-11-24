"""One unread-count sensor per person: counts only, never text (Phase 22, D-264)."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.heads_up.const import DOMAIN, INBOX_PURGE_GRACE

from ..test_restart import restart
from .policy_support import send

ANNA = "person.anna"
BEN = "person.ben"


def entity_id(hass: HomeAssistant, entry: MockConfigEntry, person: str) -> str | None:
    return er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_inbox_{person}"
    )


async def person(
    hass: HomeAssistant, entry: MockConfigEntry, name: str, state: str = "home"
) -> str:
    hass.states.async_set(f"person.{name}", state, {"friendly_name": name.title()})
    await hass.async_block_till_done()
    found = entity_id(hass, entry, f"person.{name}")
    assert found is not None
    return found


async def deliver(
    hass: HomeAssistant, entry: MockConfigEntry, who: str, mid: str, **kw: object
) -> None:
    await send(
        hass,
        entry,
        id=mid,
        channels=["inbox"],
        to={"inbox": {"recipients": [who]}},
        severity=kw.pop("severity", "info"),
        title="Secret title",
        message="Secret text",
        **kw,
    )


async def test_every_person_has_a_sensor_that_starts_at_zero(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    sensor = await person(hass, entry, "anna")
    assert sensor == "sensor.heads_up_inbox_anna"
    state = hass.states.get(sensor)
    assert state is not None and state.state == "0"
    assert state.attributes["person"] == ANNA
    assert state.attributes["needs_action"] == 0 and state.attributes["unread_critical"] == 0


async def test_the_state_is_the_unread_count_and_follows_reading(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    sensor = await person(hass, entry, "anna")
    await deliver(hass, entry, ANNA, "a")
    await deliver(hass, entry, ANNA, "b", severity="critical")
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "2"
    assert (state.attributes["needs_action"], state.attributes["unread_critical"]) == (1, 1)
    entry.runtime_data.hub.inbox.mark_read(ANNA, "a", dt_util.utcnow())
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "1"
    entry.runtime_data.acknowledge("b", "anna-id", any_message=True)
    entry.runtime_data.hub.inbox.acknowledged("b", ANNA, dt_util.utcnow())
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "0" and state.attributes["needs_action"] == 0


async def test_a_message_that_ended_is_still_counted_until_it_is_read(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    sensor = await person(hass, entry, "anna")
    await deliver(hass, entry, ANNA, "a")
    await hass.services.async_call(DOMAIN, "clear_notifications", {"id": "a"}, blocking=True)
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "1"


async def test_each_sensor_counts_only_its_own_person(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    anna, ben = await person(hass, entry, "anna"), await person(hass, entry, "ben")
    await deliver(hass, entry, ANNA, "a")
    await hass.async_block_till_done()
    assert hass.states.get(anna).state == "1"  # type: ignore[union-attr]
    assert hass.states.get(ben).state == "0"  # type: ignore[union-attr]


async def test_the_state_and_attributes_never_hold_the_title_or_the_text(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    sensor = await person(hass, entry, "anna")
    await deliver(hass, entry, ANNA, "a", severity="critical")
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None
    shown = repr((state.state, dict(state.attributes)))
    assert "Secret" not in shown and "inbox" not in state.attributes
    assert set(state.attributes) <= {
        "person",
        "needs_action",
        "unread_critical",
        "friendly_name",
        "icon",
    }


async def test_a_person_added_later_gets_a_sensor(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert entity_id(hass, entry, "person.late") is None
    assert await person(hass, entry, "late") == "sensor.heads_up_inbox_late"


async def test_a_person_who_leaves_makes_the_sensor_unavailable_and_then_removes_it(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    sensor = await person(hass, entry, "anna")
    hass.states.async_remove(ANNA)
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "unavailable"
    freezer.tick(timedelta(seconds=INBOX_PURGE_GRACE + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(sensor) is None and entity_id(hass, entry, ANNA) is None


async def test_a_person_who_comes_back_in_time_keeps_the_sensor(
    hass: HomeAssistant, entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    sensor = await person(hass, entry, "anna")
    hass.states.async_remove(ANNA)
    await hass.async_block_till_done()
    hass.states.async_set(ANNA, "home", {"friendly_name": "Anna"})
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=INBOX_PURGE_GRACE + 1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    state = hass.states.get(sensor)
    assert state is not None and state.state == "0"


async def test_the_count_survives_a_restart(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    sensor = await person(hass, entry, "anna")
    await deliver(hass, entry, ANNA, "a")
    await restart(hass, entry)
    state = hass.states.get(sensor)
    assert state is not None and state.state == "1"


async def test_a_person_with_an_entity_id_change_keeps_the_inbox(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from custom_components.heads_up.hub.rename import apply_rename

    await person(hass, entry, "anna")
    await deliver(hass, entry, ANNA, "a")
    hass.states.async_set("person.annie", "home", {"friendly_name": "Annie"})
    apply_rename(hass, entry, ANNA, "person.annie")
    inbox = entry.runtime_data.hub.inbox
    assert inbox.items(ANNA) == [] and [i.message_id for i in inbox.items("person.annie")] == ["a"]
    item = inbox.get("person.annie", "a")
    assert item is not None and item.person == "person.annie"
    await hass.async_block_till_done()
    sensor = entity_id(hass, entry, "person.annie")
    assert sensor is not None and hass.states.get(sensor).state == "1"  # type: ignore[union-attr]
