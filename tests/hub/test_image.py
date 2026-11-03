"""An image under the message: validation, card and popup payloads, push data (D-127)."""

from typing import Any

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..conftest import CreateBanner
from ..test_rules import USER, add_rule, rule_id, set_state
from ..test_rules_flow import WINDOW, _submit
from .conftest import AddDevice
from .helpers import FakeDevice, set_person, settle
from .test_push_payload import push, sent

PICTURE = "/media/local/door.jpg"


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def test_a_push_carries_the_image_as_data_image(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, image=PICTURE)
    assert sent(anna)["data"]["image"] == PICTURE


async def test_a_push_without_an_image_has_no_image_key(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry)
    assert "image" not in sent(anna)["data"]


@pytest.mark.parametrize("mode", ["title_only", "generic"])
async def test_the_image_is_left_out_when_the_lock_screen_hides_the_text(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, mode: str
) -> None:
    entry.runtime_data.options["push_lockscreen"] = mode
    await push(hass, entry, image=PICTURE)
    assert "image" not in sent(anna)["data"]
    assert entry.runtime_data.hub.trace.entries("m")[0]["reason"] == "image_hidden"


async def test_the_push_shortcut_takes_an_image(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await hass.services.async_call(
        DOMAIN,
        "push",
        {"message": "Person at the door", "recipients": ["person.anna"], "image": PICTURE},
        blocking=True,
    )
    await settle(hass, entry)
    assert sent(anna)["data"]["image"] == PICTURE


@pytest.mark.parametrize(
    "value",
    [
        "javascript:alert(1)",
        "//evil.example/x.png",
        "file:///etc/passwd",
        "relative/x.png",
        "https://example.com/a b.png",
        "",
        "https://example.com/" + "a" * 2048,
    ],
)
async def test_an_image_that_is_not_a_url_or_a_path_is_rejected(
    hass: HomeAssistant, entry: MockConfigEntry, value: str
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "create_banner", {"message": "x", "image": value}, blocking=True
        )


@pytest.mark.parametrize(
    "value", ["/local/x.jpg", "https://example.com/x.jpg", "http://nas.lan/x.png", PICTURE]
)
async def test_urls_and_paths_are_accepted(
    entry: MockConfigEntry, create: CreateBanner, value: str
) -> None:
    await create(id="a", message="x", image=value)
    assert entry.runtime_data.banners["a"].image == value


async def test_the_card_and_popup_payload_carry_the_image(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", image=PICTURE)
    (shown,) = entry.runtime_data.visible(USER)
    assert shown["image"] == PICTURE


async def test_a_banner_without_an_image_has_none(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    (shown,) = entry.runtime_data.visible(USER)
    assert shown["image"] is None


async def test_a_stored_banner_from_before_loads_without_an_image(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    data: dict[str, Any] = entry.runtime_data.banners["a"].to_dict()
    del data["image"]
    from custom_components.heads_up.models import Banner

    assert Banner.from_dict(data).image is None


async def test_an_update_that_only_changes_the_image_is_not_a_duplicate(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, image="/local/a.jpg")
    await push(hass, entry, image="/local/a.jpg")
    assert len(anna.calls) == 1  # identical within the dedupe time
    await push(hass, entry, image="/local/b.jpg")
    assert len(anna.calls) == 2
    assert sent(anna)["data"]["image"] == "/local/b.jpg"


async def test_a_rule_stores_and_shows_an_image(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    sub = add_rule(hass, entry, image=PICTURE)
    await hass.async_block_till_done()
    shown = next(b for b in entry.runtime_data.visible(USER) if b["id"] == rule_id(sub))
    assert shown["image"] == PICTURE


async def test_the_rule_form_checks_and_trims_the_image(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    bad = await _submit(hass, entry, entity_id=WINDOW, image="not a path")
    assert bad["errors"] == {"image": "image_invalid"}
    good = await _submit(hass, entry, entity_id=WINDOW, image="  /local/x.jpg ")
    assert good["type"].value == "create_entry"
    (subentry,) = entry.subentries.values()
    assert subentry.data["image"] == "/local/x.jpg"
