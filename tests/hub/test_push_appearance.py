"""Push appearance fields: icon, color, sender icon URL and subtitle (D-255, N-112)."""

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from .conftest import AddDevice
from .helpers import FakeDevice, set_person
from .test_push_payload import push, sent

PICTURE = "/local/icons/door.png"


@pytest.fixture
async def anna(hass: HomeAssistant, mobile_app_device: AddDevice) -> FakeDevice:
    set_person(hass, "person.anna", "home", user_id="anna-id")
    return await mobile_app_device(
        "Anna's phone", user_id="anna-id", person_entity_id="person.anna"
    )


async def test_icon_and_color_become_the_companion_keys(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, title="Door", icon="mdi:door", color="#03a9f4")
    data = sent(anna)["data"]
    assert data["notification_icon"] == "mdi:door"
    assert data["color"] == "#03a9f4"


async def test_a_push_without_them_has_no_such_keys(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry)
    data = sent(anna)["data"]
    assert not {"notification_icon", "color", "icon_url", "subtitle", "subject"} & set(data)


async def test_the_subtitle_is_subtitle_on_ios_and_subject_on_android(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, title="Door", subtitle="Front")
    assert sent(anna)["data"]["subtitle"] == "Front"
    assert "subject" not in sent(anna)["data"]
    hass.config_entries.async_update_entry(
        anna.entry, data={**anna.entry.data, "os_name": "Android"}
    )
    await push(hass, entry, id="m2", title="Door", subtitle="Front")
    assert sent(anna)["data"]["subject"] == "Front"
    assert "subtitle" not in sent(anna)["data"]


async def test_an_ios_icon_without_a_title_gets_a_sender_name(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, icon="mdi:door")
    assert sent(anna)["title"] == "Heads Up"


async def test_an_android_icon_without_a_title_keeps_no_title(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    hass.config_entries.async_update_entry(
        anna.entry, data={**anna.entry.data, "os_name": "Android"}
    )
    await push(hass, entry, icon="mdi:door")
    assert "title" not in sent(anna)


async def test_the_sender_icon_url_goes_out_on_full(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_lockscreen"] = "full"
    await push(hass, entry, title="Door", icon_url=PICTURE)
    assert sent(anna)["data"]["icon_url"] == PICTURE


@pytest.mark.parametrize("mode", ["title_only", "generic"])
async def test_sender_icon_url_and_subtitle_are_left_out_when_the_text_is_hidden(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, mode: str
) -> None:
    entry.runtime_data.options["push_lockscreen"] = mode
    await push(hass, entry, title="Door", icon_url=PICTURE, subtitle="Front", color="#112233")
    data = sent(anna)["data"]
    assert not {"icon_url", "subtitle", "subject"} & set(data)
    assert data["color"] == "#112233"
    reason = entry.runtime_data.hub.trace.entries("m")[0]["reason"]
    assert "icon_url_hidden" in reason and "subtitle_hidden" in reason


@pytest.mark.parametrize("color", ["blue", "#12345", "#gggggg", "03a9f4"])
async def test_a_color_must_be_a_hex_value(
    hass: HomeAssistant, entry: MockConfigEntry, color: str
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "notify", {"message": "x", "color": color}, blocking=True
        )


async def test_the_push_shortcut_takes_the_fields(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_lockscreen"] = "full"
    await hass.services.async_call(
        DOMAIN,
        "push",
        {
            "message": "Door",
            "title": "Door",
            "recipients": ["person.anna"],
            "icon": "mdi:door",
            "color": "#03a9f4",
            "subtitle": "Front",
            "icon_url": PICTURE,
        },
        blocking=True,
    )
    data = sent(anna)["data"]
    assert (data["notification_icon"], data["color"], data["subtitle"], data["icon_url"]) == (
        "mdi:door",
        "#03a9f4",
        "Front",
        PICTURE,
    )
