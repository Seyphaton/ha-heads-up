"""The `notify` action and the shortcuts (D-087, D-098, DESIGN §23.5)."""

from typing import Any

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..conftest import banners
from .helpers import set_person


async def notify(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    response = await hass.services.async_call(
        DOMAIN, "notify", data, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def test_banner_only_notify_behaves_like_create_banner(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await notify(hass, id="a", message="hello", channels=["banner"], severity="info")
    assert result["status"] == "created"
    assert result["channels"] == {"banner": {"sent": 1, "held": 0, "skipped": 0, "failed": 0}}
    assert banners(entry)["a"].channels == ["banner"]
    assert banners(entry)["a"].source == "action"


async def test_unavailable_channel_is_reported_as_skipped(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    result = await notify(
        hass,
        id="a",
        message="x",
        channels=["banner", "push"],
        to={"push": {"recipients": ["person.anna"]}},
    )
    assert result["channels"]["push"]["skipped"] == 1
    assert result["channels"]["banner"]["sent"] == 1


async def test_waiting_message_reports_the_banner_as_held(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("binary_sensor.w", "off")
    result = await notify(
        hass,
        id="a",
        message="x",
        channels=["banner"],
        condition={"entity_id": "binary_sensor.w", "state": "on"},
    )
    assert result["status"] == "waiting"
    assert result["channels"]["banner"]["held"] == 1


async def test_message_without_banner_channel_is_stored_but_not_shown(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    await notify(
        hass,
        id="a",
        message="x",
        channels=["push"],
        to={"push": {"recipients": ["person.anna"]}},
    )
    assert "a" in banners(entry)
    assert entry.runtime_data.visible("anyone", show_all=True) == []
    assert entry.runtime_data.active_count() == 0


async def test_clear_banner_leaves_messages_without_the_banner_channel(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    await notify(
        hass, id="a", message="x", channels=["push"], to={"push": {"recipients": ["person.anna"]}}
    )
    await hass.services.async_call(DOMAIN, "clear_banner", {"id": "a"}, blocking=True)
    assert "a" in banners(entry)
    result = await hass.services.async_call(
        DOMAIN, "clear_notifications", {"id": "a"}, blocking=True, return_response=True
    )
    assert result == {"cleared": 1}
    assert "a" not in banners(entry)


async def test_clear_removes_a_banner_message_too(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await notify(hass, id="a", message="x", channels=["banner"], tag="g")
    result = await hass.services.async_call(
        DOMAIN, "clear_notifications", {"tag": "g"}, blocking=True, return_response=True
    )
    assert result == {"cleared": 1}


@pytest.mark.parametrize(
    "data",
    [
        {"channels": []},
        {"channels": ["banner", "banner"]},
        {"channels": ["fax"]},
        {"channels": ["push"]},  # push needs a target
        {"channels": ["popup"]},
        {"channels": ["speak"]},
        {"channels": ["banner"], "to": {"push": {"audience": "x"}}},  # channel not in channels
        {
            "channels": ["push"],
            "to": {"push": {"audience": "x", "recipients": ["person.a"]}},
        },  # both
        {"channels": ["push"], "to": {"push": {}}},  # neither
        {"channels": ["speak"], "to": {"speak": {"audience": "x"}}},  # speech has no audience
        {"channels": ["persistent"], "to": {"persistent": {"recipients": ["person.a"]}}},
    ],
)
async def test_invalid_channel_and_target_shapes_are_rejected(
    hass: HomeAssistant, entry: MockConfigEntry, data: dict[str, Any]
) -> None:
    with pytest.raises(vol.Invalid):
        await notify(hass, message="x", **data)


async def test_persistent_and_banner_need_no_target(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await notify(hass, id="a", message="x", channels=["banner", "persistent"])
    assert result["channels"]["persistent"]["sent"] == 1


async def test_unknown_audience_lists_the_valid_names(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, message="x", channels=["push"], to={"push": {"audience": "Nobody"}})
    assert err.value.translation_key == "unknown_audience"
    assert err.value.translation_placeholders["name"] == "Nobody"  # type: ignore[index]


async def test_unknown_recipient_lists_the_valid_names(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    with pytest.raises(ServiceValidationError) as err:
        await notify(
            hass,
            message="x",
            channels=["push"],
            to={"push": {"recipients": ["person.ghost"]}},
        )
    assert err.value.translation_key == "unknown_recipient"
    assert "person.anna" in err.value.translation_placeholders["valid"]  # type: ignore[index]


async def test_unknown_policy_is_rejected_but_none_is_accepted(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, message="x", channels=["banner"], policy="night")
    assert err.value.translation_key == "unknown_policy"
    result = await notify(hass, id="a", message="x", channels=["banner"], policy="none")
    assert result["status"] == "created"


async def test_banner_recipients_become_the_cards_targeting(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home", {"user_id": "anna-id"})
    await notify(
        hass,
        id="a",
        message="x",
        channels=["banner"],
        to={"banner": {"recipients": ["person.anna"]}},
    )
    manager = entry.runtime_data
    assert [b["id"] for b in manager.visible("anna-id")] == ["a"]
    assert manager.visible("other") == []


async def test_notify_replaces_a_message_with_the_same_id(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await notify(hass, id="a", message="one", channels=["banner"])
    result = await notify(hass, id="a", message="two", channels=["banner"])
    assert result["status"] == "updated"
    assert banners(entry)["a"].message == "two"


async def test_tts_message_is_stored_and_never_sent_to_the_card(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await notify(hass, id="a", message="x", channels=["banner"], tts_message="spoken")
    assert banners(entry)["a"].tts_message == "spoken"
    payload = entry.runtime_data.visible("u")[0]
    assert "tts_message" not in payload and "channels" not in payload


async def test_push_shortcut_with_an_id_tracks_the_message(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    result = await hass.services.async_call(
        DOMAIN,
        "push",
        {"id": "p", "message": "x", "recipients": ["person.anna"]},
        blocking=True,
        return_response=True,
    )
    assert result is not None and result["channels"]["push"]["skipped"] == 1
    assert banners(entry)["p"].channels == ["push"]


async def test_push_shortcut_without_an_id_keeps_no_record(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set("person.anna", "home")
    result = await hass.services.async_call(
        DOMAIN,
        "popup",
        {"message": "x", "recipients": ["person.anna"]},
        blocking=True,
        return_response=True,
    )
    assert result is not None and result["status"] == "sent_once"
    assert banners(entry) == {}
    assert entry.runtime_data.hub.trace.entries()[0]["channel"] == "popup"


async def test_speak_shortcut_takes_no_audience(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "speak", {"message": "x", "audience": "x"}, blocking=True
        )


async def test_shortcut_needs_a_target(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "push", {"message": "x"}, blocking=True)


@pytest.fixture
def options() -> dict[str, Any]:
    return {}


async def test_the_response_says_why_a_delivery_is_skipped_or_held(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    result = await hass.services.async_call(
        DOMAIN,
        "notify",
        {
            "id": "why",
            "message": "x",
            "channels": ["banner", "push"],
            "to": {"push": {"recipients": ["person.anna"]}},
        },
        blocking=True,
        return_response=True,
    )
    assert result["channels"]["push"]["skipped"] == 1
    assert result["reasons"] == [
        {
            "channel": "push",
            "recipient": "person.anna",
            "result": "skipped",
            "reason": "no_usable_device",
        }
    ]


async def test_the_response_has_no_reasons_when_everything_is_sent(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await hass.services.async_call(
        DOMAIN,
        "notify",
        {"id": "ok", "message": "x", "channels": ["banner"]},
        blocking=True,
        return_response=True,
    )
    assert result["reasons"] == []


async def test_an_audience_name_in_another_case_is_accepted_and_stored_as_written(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    set_person(hass, "person.anna", "home")
    await notify(
        hass,
        id="case",
        message="x",
        channels=["banner"],
        to={"banner": {"audience": "at HOME"}},
    )
    assert banners(entry)["case"].targets["banner"]["audience"] == "At home"


async def test_a_close_audience_name_gets_a_suggestion(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, message="x", channels=["push"], to={"push": {"audience": "At hom"}})
    assert err.value.translation_key == "unknown_audience_hint"
    placeholders = err.value.translation_placeholders
    assert placeholders["suggestion"] == "At home"  # type: ignore[index]


async def test_a_policy_name_in_another_case_is_accepted(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from .policy_support import add_policy

    await add_policy(hass, entry, "Night", type="reminder", every_minutes=30, max_count=3)
    result = await notify(hass, id="p", message="x", channels=["banner"], policy="night")
    assert result["status"] == "created"
    assert banners(entry)["p"].policy == "Night"
    with pytest.raises(ServiceValidationError) as err:
        await notify(hass, message="x", channels=["banner"], policy="Nigh")
    assert err.value.translation_key == "unknown_policy_hint"
