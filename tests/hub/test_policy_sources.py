"""Escalation, Deliver and Fallback can take their channels or recipients from the call (D-181)."""

from datetime import UTC, datetime
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.policies import sources
from custom_components.heads_up.hub.policies.models import Policy
from custom_components.heads_up.models import Banner

from .conftest import AddDevice
from .helpers import set_person
from .policy_support import add_policy, make_household, move, pushes, send, trace, wait


def banner(**kw: Any) -> Banner:
    now = datetime(2026, 11, 5, tzinfo=UTC)
    base = {
        "id": "m",
        "message": "x",
        "severity": "warning",
        "dismissible": True,
        "dismiss_scope": "user",
        "created_at": now,
        "updated_at": now,
        "channels": ["banner", "push", "speak"],
        "targets": {
            "push": {"audience": "At home"},
            "speak": {"recipients": ["media_player.kitchen"]},
        },
    }
    return Banner(**{**base, **kw})


def policy(**kw: Any) -> Policy:
    return Policy(name="p", type="fallback", **kw)


# -- the rule itself -------------------------------------------------------------------------


def test_the_policy_names_both_by_default() -> None:
    result = sources.message_for(
        banner(), policy(channels=("popup",), targets={"popup": {"audience": "Admins"}})
    )
    assert result.channels == ["popup"] and result.targets == {"popup": {"audience": "Admins"}}


def test_same_channels_new_people_uses_the_people_target_for_people_channels_only() -> None:
    both = policy(
        channels_from="call",
        targets={
            "people": {"audience": "Everyone"},
            "speak": {"recipients": ["media_player.hall"]},
        },
    )
    result = sources.message_for(banner(channels=["banner", "push", "speak", "mail"]), both)
    assert result.channels == ["push", "speak", "mail"]
    assert result.targets == {
        "push": {"audience": "Everyone"},
        "speak": {"recipients": ["media_player.hall"]},
        "mail": {"audience": "Everyone"},
    }
    only_people = policy(channels_from="call", targets={"people": {"audience": "Everyone"}})
    assert sources.message_for(banner(), only_people).targets == {"push": {"audience": "Everyone"}}


def test_only_the_failed_channels_when_the_policy_says_so() -> None:
    failed = policy(channels_from="failed", targets={"people": {"audience": "Everyone"}})
    result = sources.message_for(banner(), failed, {"push"})
    assert result.channels == ["push"]
    assert sources.message_for(banner(), failed, set()).channels == []


def test_new_channels_same_recipients_reuse_the_calls_people_and_speakers() -> None:
    same = policy(channels=("popup", "speak", "persistent"), targets_from="call")
    result = sources.message_for(banner(), same)
    assert result.channels == ["popup", "speak", "persistent"]
    assert result.targets == {
        "popup": {"audience": "At home"},
        "speak": {"recipients": ["media_player.kitchen"]},
    }  # the Persistent Notification takes no target


def test_a_speech_channel_without_speakers_in_the_call_gets_no_target() -> None:
    same = policy(channels=("speak",), targets_from="call")
    assert (
        sources.message_for(banner(targets={"push": {"audience": "At home"}}), same).targets == {}
    )


@pytest.mark.parametrize(
    ("data", "kind", "errors"),
    [
        ({"channels": ["push"]}, "fallback", {}),
        ({}, "fallback", {"channels": "channels_required"}),
        ({"channels_from": "call"}, "escalation", {}),
        ({"channels_from": "failed"}, "fallback", {}),
        ({"channels_from": "failed"}, "escalation", {"channels_from": "channels_from_unknown"}),
        ({"channels_from": "nope"}, "deliver", {"channels_from": "channels_from_unknown"}),
        (
            {"targets_from": "nope", "channels": ["push"]},
            "deliver",
            {"targets_from": "targets_from_unknown"},
        ),
        (
            {"channels_from": "call", "targets_from": "call"},
            "fallback",
            {"targets_from": "nothing_new"},
        ),
        ({"targets_from": "call", "channels": ["popup"]}, "deliver", {}),
        ({"targets_from": "call"}, "deliver", {"channels": "channels_required"}),
    ],
)
def test_the_two_sources_are_checked(
    data: dict[str, Any], kind: str, errors: dict[str, str]
) -> None:
    assert sources.check(data, kind) == errors


# -- in the engine ---------------------------------------------------------------------------


async def test_a_fallback_can_take_the_channels_of_the_call_and_new_people(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    move(hass, "person.anna", "not_home")
    move(hass, "person.ben", "not_home")
    await add_policy(
        hass,
        entry,
        "Everyone instead",
        type="fallback",
        when="no_audience",
        channels_from="call",
        targets={"people": {"audience": "Everyone"}},
    )
    await send(hass, entry, severity="warning", to={"push": {"audience": "At home"}})
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1
    assert any(e["result"] == "fallback" for e in trace(entry))


async def test_a_fallback_can_try_other_channels_for_the_same_people(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.cy", "home", user_id="cy-id")  # a user, but no phone
    await add_policy(
        hass,
        entry,
        "Popup instead",
        type="fallback",
        when="failed",
        channels=["popup"],
        targets_from="call",
    )
    await send(hass, entry, severity="warning", to={"push": {"recipients": ["person.cy"]}})
    popup = [e for e in trace(entry) if e["channel"] == "popup"]
    assert [(e["recipient"], e["result"]) for e in popup] == [("person.cy", "sent")]


async def test_an_escalation_can_repeat_the_calls_channels_to_other_people(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(
        hass,
        entry,
        "Backup",
        type="escalation",
        after_minutes=5,
        channels_from="call",
        targets={"people": {"recipients": ["person.ben"]}},
    )
    await send(hass, entry)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)
    await wait(hass, entry, freezer, 5.1)
    assert len(pushes(home.ben)) == 1


async def test_a_deliver_policy_can_add_channels_for_the_calls_own_people(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(
        hass,
        entry,
        "Also a popup",
        type="deliver",
        severities=["critical"],
        channels=["popup"],
        targets_from="call",
    )
    await send(hass, entry)
    popup = [e for e in trace(entry) if e["channel"] == "popup"]
    assert [(e["recipient"], e["result"]) for e in popup] == [("person.anna", "sent")]
