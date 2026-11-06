"""Shared recipients and a policy list in `notify` (D-184)."""

from typing import Any

import probatio as vol
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.services import SCHEMAS

from ..conftest import banners
from .conftest import AddDevice
from .policy_support import ESCALATION, add_policy, make_household, send

NOTIFY = SCHEMAS["notify"]


def check(**data: Any) -> dict[str, Any]:
    return dict(NOTIFY({"message": "x", **data}))


def test_recipients_become_the_target_of_every_channel_that_takes_people() -> None:
    data = check(channels=["banner", "push", "popup", "mail"], recipients=["person.anna"])
    assert data["to"] == {
        c: {"recipients": ["person.anna"]} for c in ("banner", "push", "popup", "mail")
    }
    assert "recipients" not in data


def test_an_audience_is_shared_the_same_way() -> None:
    data = check(channels=["push", "popup"], audience="At home")
    assert data["to"] == {"push": {"audience": "At home"}, "popup": {"audience": "At home"}}


def test_a_persistent_notification_takes_no_shared_target() -> None:
    data = check(channels=["banner", "persistent"], audience="At home")
    assert list(data["to"]) == ["banner"]


def test_speech_takes_speakers_not_the_shared_recipients() -> None:
    data = check(
        channels=["push", "speak"], recipients=["person.anna"], speakers=["media_player.kitchen"]
    )
    assert data["to"]["speak"] == {"recipients": ["media_player.kitchen"]}
    assert data["to"]["push"] == {"recipients": ["person.anna"]}


def test_speech_without_speakers_is_refused_even_with_shared_recipients() -> None:
    with pytest.raises(vol.Invalid):
        check(channels=["speak"], recipients=["person.anna"])


def test_a_to_entry_wins_over_the_shared_recipients() -> None:
    data = check(
        channels=["push", "popup"],
        recipients=["person.anna"],
        to={"push": {"recipients": ["person.ben"]}},
    )
    assert data["to"]["push"] == {"recipients": ["person.ben"]}
    assert data["to"]["popup"] == {"recipients": ["person.anna"]}


def test_audience_and_recipients_together_are_refused() -> None:
    with pytest.raises(vol.Invalid):
        check(channels=["push"], audience="At home", recipients=["person.anna"])


def test_named_policies_apply_next_to_the_automatic_ones() -> None:
    assert check(channels=["banner"], policy="Night")["policy"] == ["automatic", "Night"]
    assert check(channels=["banner"], policy=["Night", "Day"])["policy"] == [
        "automatic",
        "Night",
        "Day",
    ]
    assert "policy" not in check(channels=["banner"])


def test_matching_policies_automatically_off_keeps_the_named_ones() -> None:
    assert check(channels=["banner"], policy="Night", match_policies_automatically=False)[
        "policy"
    ] == ["Night"]
    assert check(channels=["banner"], match_policies_automatically=False)["policy"] == ["none"]
    assert "match_policies_automatically" not in check(
        channels=["banner"], match_policies_automatically=True
    )


def test_none_stands_alone_and_keywords_ignore_case() -> None:
    assert check(channels=["banner"], policy="None")["policy"] == ["none"]
    with pytest.raises(vol.Invalid):
        check(channels=["banner"], policy=["none", "Night"])
    with pytest.raises(vol.Invalid):
        check(channels=["banner"], policy=["automatic"], match_policies_automatically=False)


async def test_a_manual_policy_applies_next_to_the_automatic_ones_unless_they_are_disabled(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Auto", **ESCALATION)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    book = entry.runtime_data.hub.policies

    def used() -> list[str]:
        return [p.name for p in book.for_message(banners(entry)["m"])]

    await send(hass, entry)
    assert used() == ["Auto"]
    await send(hass, entry, policy="By hand")
    assert used() == ["Auto", "By hand"]
    await send(hass, entry, policy="By hand", match_policies_automatically=False)
    assert used() == ["By hand"]
    await send(hass, entry, match_policies_automatically=False)
    assert used() == []


def test_the_hub_actions_default_to_info() -> None:
    assert check(channels=["banner"])["severity"] == "info"
    for channel in ("push", "popup"):
        assert SCHEMAS[channel]({"message": "x", "audience": "At home"})["severity"] == "info"
    assert (
        SCHEMAS["speak"]({"message": "x", "recipients": ["media_player.k"]})["severity"] == "info"
    )


async def test_create_banner_keeps_warning_as_its_default(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await hass.services.async_call(
        "heads_up", "create_banner", {"id": "a", "message": "x"}, blocking=True
    )
    assert banners(entry)["a"].severity == "warning"
