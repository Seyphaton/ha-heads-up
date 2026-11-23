"""A progress bar bound to an entity: scaling, card data, push updates (D-256, D-258)."""

from datetime import timedelta
from typing import Any

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.progress import percent

from ..test_rules import USER, add_rule, rule_id
from .conftest import AddDevice
from .helpers import FakeDevice, set_person, settle
from .test_push_payload import push, sent

SENSOR = "sensor.printer_progress"
SPEC = {"entity_id": SENSOR}


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def tick(hass: HomeAssistant, entry: MockConfigEntry, value: str) -> None:
    hass.states.async_set(SENSOR, value)
    await settle(hass, entry)


@pytest.mark.parametrize(
    ("raw", "spec", "expected"),
    [
        ("40", {}, 40),
        ("0", {}, 0),
        ("150", {}, 100),
        ("-5", {}, 0),
        ("50", {"min": 20, "max": 80}, 50),
        ("20", {"min": 20, "max": 80}, 0),
        ("0.5", {"max": 1}, 50),
        ("abc", {}, None),
        ("nan", {}, None),
        ("inf", {}, None),
        ("5", {"min": 10, "max": 10}, None),
    ],
)
def test_the_value_is_scaled_to_percent(
    raw: str, spec: dict[str, Any], expected: int | None
) -> None:
    assert percent(raw, spec) == expected


async def test_the_first_push_has_the_bar_and_a_title(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "40")
    await push(hass, entry, progress=SPEC)
    message = sent(anna)
    data = message["data"]
    assert (data["live_update"], data["progress"], data["progress_max"]) == (True, 40, 100)
    assert message["title"] == "Heads Up"
    assert "alert_once" not in data  # iOS device: no such key


async def test_android_updates_do_not_ring_again(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.config_entries.async_update_entry(
        anna.entry, data={**anna.entry.data, "os_name": "Android"}
    )
    hass.states.async_set(SENSOR, "10")
    await push(hass, entry, progress=SPEC)
    assert sent(anna)["data"]["alert_once"] is True


async def test_a_message_without_progress_has_no_live_keys(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry)
    assert not {"live_update", "progress", "progress_max"} & set(sent(anna)["data"])


async def test_an_unavailable_entity_sends_no_bar(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "unavailable")
    await push(hass, entry, progress=SPEC)
    assert "live_update" not in sent(anna)["data"]


async def test_a_change_updates_the_push_in_place(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "10")
    await push(hass, entry, progress=SPEC)
    first = sent(anna)
    await tick(hass, entry, "70")
    assert len(anna.calls) == 2
    second = sent(anna)
    assert second["data"]["progress"] == 70
    assert second["data"]["tag"] == first["data"]["tag"]


async def test_quick_changes_wait_and_the_newest_value_goes_out(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "10")
    await push(hass, entry, progress=SPEC)
    await tick(hass, entry, "20")  # goes out at once, nothing was sent for a tick yet
    await tick(hass, entry, "30")
    await tick(hass, entry, "40")
    assert len(anna.calls) == 2
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=6))
    await settle(hass, entry)
    assert len(anna.calls) == 3
    assert sent(anna)["data"]["progress"] == 40


async def test_the_end_is_not_held_back(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "10")
    await push(hass, entry, progress=SPEC)
    await tick(hass, entry, "20")
    await tick(hass, entry, "100")
    assert sent(anna)["data"]["progress"] == 100


async def test_the_card_gets_the_percent_and_not_the_entity(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(SENSOR, "25")
    await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "p", "message": "Printing", "channels": ["banner"], "progress": SPEC},
        blocking=True,
    )
    shown = next(b for b in entry.runtime_data.visible(USER) if b["id"] == "p")
    assert shown["progress_value"] == 25
    assert "progress" not in shown
    await tick(hass, entry, "60")
    shown = next(b for b in entry.runtime_data.visible(USER) if b["id"] == "p")
    assert shown["progress_value"] == 60


async def test_a_watch_rule_follows_the_bar(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    from ..test_rules import set_state

    hass.states.async_set(SENSOR, "30")
    await set_state(hass, "on")
    sub = add_rule(hass, entry, progress=SPEC)
    await hass.async_block_till_done()
    find = lambda: next(  # noqa: E731
        b for b in entry.runtime_data.visible(USER) if b["id"] == rule_id(sub)
    )
    assert find()["progress_value"] == 30
    await tick(hass, entry, "90")
    assert find()["progress_value"] == 90


@pytest.mark.parametrize(
    "progress", [{"entity_id": SENSOR, "min": 5, "max": 5}, {"entity_id": SENSOR, "max": -1}, {}]
)
async def test_a_bad_progress_is_rejected(
    hass: HomeAssistant, entry: MockConfigEntry, progress: dict[str, Any]
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "notify", {"message": "x", "progress": progress}, blocking=True
        )


async def test_the_rule_form_checks_the_progress_bar(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from ..test_rules_flow import WINDOW, _submit

    hass.states.async_set(WINDOW, "off")
    bad = await _submit(hass, entry, entity_id=WINDOW, progress={"entity_id": SENSOR, "max": -1})
    assert bad["errors"] == {"progress": "progress_invalid"}
    good = await _submit(
        hass, entry, entity_id=WINDOW, progress={"entity_id": SENSOR, "min": "10", "max": "90"}
    )
    assert good["type"].value == "create_entry"
    (subentry,) = entry.subentries.values()
    assert subentry.data["progress"] == {"entity_id": SENSOR, "min": 10.0, "max": 90.0}


async def test_an_open_popup_is_refreshed_when_the_value_changes(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.states.async_set(SENSOR, "10")
    await push(
        hass,
        entry,
        channels=["popup"],
        to={"popup": {"recipients": ["person.anna"]}},
        progress=SPEC,
    )
    popup = entry.runtime_data.hub.channels.get("popup")
    seen: list[int] = []
    popup.subscribe(lambda: seen.append(popup.messages_for("anna-id")[0]["progress_value"]))
    await tick(hass, entry, "55")
    assert seen == [55]
