"""Push appearance fields: icon, color, sender icon URL and subtitle (D-255, N-112)."""

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_rules import USER, add_rule, rule_id, set_state
from ..test_rules_flow import WINDOW, _submit
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
    entry.runtime_data.options["push_severity_look"] = False
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


async def test_a_watch_rule_carries_the_fields(entry: MockConfigEntry, hass: HomeAssistant) -> None:
    await set_state(hass, "on")
    sub = add_rule(
        hass, entry, color="#03a9f4", icon_url=PICTURE, subtitle="Front", icon="mdi:door"
    )
    await hass.async_block_till_done()
    shown = next(b for b in entry.runtime_data.visible(USER) if b["id"] == rule_id(sub))
    assert (shown["color"], shown["icon_url"], shown["subtitle"]) == ("#03a9f4", PICTURE, "Front")


async def test_the_rule_form_checks_and_trims_the_fields(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "off")
    bad = await _submit(hass, entry, entity_id=WINDOW, color="blue", icon_url="x")
    assert bad["errors"] == {"color": "color_invalid", "icon_url": "icon_url_invalid"}
    good = await _submit(
        hass, entry, entity_id=WINDOW, color=" #03A9F4 ", subtitle=" Front ", icon_url=" /a.png "
    )
    assert good["type"].value == "create_entry"
    (subentry,) = entry.subentries.values()
    assert subentry.data["color"] == "#03a9f4"
    assert subentry.data["subtitle"] == "Front"
    assert subentry.data["icon_url"] == "/a.png"


async def test_a_push_looks_as_before_by_default(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    await push(hass, entry, severity="critical")
    data = sent(anna)["data"]
    assert "notification_icon" not in data and "color" not in data
    assert "title" not in sent(anna)


async def test_with_the_option_on_a_push_uses_the_icon_of_its_severity(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_severity_look"] = True
    await push(hass, entry, severity="critical")
    data = sent(anna)["data"]
    assert data["notification_icon"] == "mdi:alert-octagon"
    assert "color" not in data  # the built-in severity colors are theme variables, no hex


async def test_the_icon_and_hex_color_of_the_severities_page_are_used(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_severity_look"] = True
    entry.runtime_data.options["severity_display"] = {
        "warning": {"icon": "mdi:lamp", "color": "#ff9800"}
    }
    await push(hass, entry, severity="warning")
    data = sent(anna)["data"]
    assert (data["notification_icon"], data["color"]) == ("mdi:lamp", "#ff9800")


async def test_a_severity_color_that_is_not_hex_is_not_sent(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_severity_look"] = True
    entry.runtime_data.options["severity_display"] = {"warning": {"color": "var(--x)"}}
    await push(hass, entry, severity="warning")
    assert "color" not in sent(anna)["data"]


async def test_the_message_icon_and_color_win_over_the_severity(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_severity_look"] = True
    entry.runtime_data.options["severity_display"] = {
        "warning": {"icon": "mdi:lamp", "color": "#ff9800"}
    }
    await push(hass, entry, severity="warning", icon="mdi:door", color="#112233")
    data = sent(anna)["data"]
    assert (data["notification_icon"], data["color"]) == ("mdi:door", "#112233")


async def test_with_the_option_off_only_the_message_values_are_sent(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice
) -> None:
    entry.runtime_data.options["push_severity_look"] = False
    entry.runtime_data.options["severity_display"] = {
        "warning": {"icon": "mdi:lamp", "color": "#ff9800"}
    }
    await push(hass, entry, severity="warning", icon="mdi:door")
    data = sent(anna)["data"]
    assert data["notification_icon"] == "mdi:door"
    assert "color" not in data


@pytest.mark.parametrize(
    ("given", "stored"),
    [("#03A9F4", "#03a9f4"), ([3, 169, 244], "#03a9f4"), ((255, 0, 0), "#ff0000")],
)
async def test_a_color_is_stored_as_lowercase_hex(
    hass: HomeAssistant, entry: MockConfigEntry, anna: FakeDevice, given: object, stored: str
) -> None:
    await push(hass, entry, color=given)
    assert sent(anna)["data"]["color"] == stored


@pytest.mark.parametrize(
    "color", [[1, 2], [1, 2, 3, 4], [256, 0, 0], [-1, 0, 0], [1.5, 2, 3], [True, 0, 0], 5]
)
async def test_a_bad_color_list_is_rejected(
    hass: HomeAssistant, entry: MockConfigEntry, color: object
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN,
            "notify",
            {"message": "x", "channels": ["banner"], "color": color},
            blocking=True,
        )
