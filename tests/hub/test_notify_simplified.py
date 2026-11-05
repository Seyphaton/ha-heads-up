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


def test_a_policy_is_one_name_or_a_list() -> None:
    assert check(channels=["banner"], policy="Night")["policy"] == ["Night"]
    assert check(channels=["banner"], policy=["Night", "Day"])["policy"] == ["Night", "Day"]


def test_none_stands_alone_and_keywords_ignore_case() -> None:
    assert check(channels=["banner"], policy="None")["policy"] == ["none"]
    with pytest.raises(vol.Invalid):
        check(channels=["banner"], policy=["none", "Night"])


async def test_automatic_next_to_a_name_adds_the_policies_that_apply(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Auto", **ESCALATION)
    await add_policy(hass, entry, "By hand", **ESCALATION, apply="manual")
    book = entry.runtime_data.hub.policies
    await send(hass, entry, policy="By hand")
    assert [p.name for p in book.for_message(banners(entry)["m"])] == ["By hand"]
    await send(hass, entry, policy=["automatic", "By hand"])
    assert [p.name for p in book.for_message(banners(entry)["m"])] == ["Auto", "By hand"]
    await send(hass, entry, policy="automatic")
    assert [p.name for p in book.for_message(banners(entry)["m"])] == ["Auto"]


def test_dismiss_and_snooze_map_to_the_stored_fields() -> None:
    data = check(channels=["banner"], dismiss="everyone", snooze="user")
    assert (data["dismissible"], data["dismiss_scope"]) == (True, "global")
    assert (data["snoozable"], data["snooze_scope"]) == (True, "user")
    assert "dismiss" not in data and "snooze" not in data


def test_an_unquoted_off_in_yaml_means_nobody() -> None:
    assert check(channels=["banner"], dismiss=False)["dismissible"] is False


def test_snoozing_a_message_nobody_can_dismiss_is_refused() -> None:
    with pytest.raises(vol.Invalid):
        check(channels=["banner"], dismiss="off", snooze="user")


def test_an_omitted_dismiss_keeps_the_option_defaults() -> None:
    data = check(channels=["banner"])
    assert not {"dismissible", "dismiss_scope", "snoozable", "snooze_scope"} & set(data)


def test_no_policy_is_policy_none() -> None:
    assert check(channels=["banner"], no_policy=True)["policy"] == ["none"]
    assert "no_policy" not in check(channels=["banner"], no_policy=False)
    with pytest.raises(vol.Invalid):
        check(channels=["banner"], no_policy=True, policy="Night")
