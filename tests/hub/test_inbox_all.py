"""All notifications: a copy of what other channels delivered, in the inbox, as history (D-276)."""

from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import set_person, settle
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    add_policy,
    make_household,
    move,
    send,
    wait,
)

ANNA = "person.anna"
BEN = "person.ben"


@pytest.fixture
def options() -> dict[str, Any]:
    return {"inbox_all_notifications": True, "presence_debounce_seconds": 0}


def inbox(entry: MockConfigEntry) -> Any:
    return entry.runtime_data.hub.inbox


async def push_to_anna(hass: HomeAssistant, entry: MockConfigEntry, **kw: Any) -> None:
    await send(
        hass,
        entry,
        channels=["push"],
        to={"push": {"recipients": [ANNA]}},
        **{"severity": "warning", **kw},
    )


# Which messages --------------------------------------------------------------------------


async def test_a_push_leaves_a_copy_that_is_history(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry, title="Leak", message="Water in the cellar")
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.copy is True
    assert (item.title, item.text, item.severity) == ("Leak", "Water in the cellar", "warning")
    assert item.via == ["push"] and item.read_at is not None and item.unread is False
    assert inbox(entry).get(BEN, "m") is None


@pytest.mark.parametrize("options", [{}], ids=["default"])
async def test_nothing_is_kept_by_default(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry, severity="critical")
    assert inbox(entry).people() == []


async def test_a_copy_is_never_counted_and_never_needs_action(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry, severity="critical")
    store = inbox(entry)
    assert store.get(ANNA, "m") is not None
    assert store.unread_count(ANNA) == 0 and store.needs_action(ANNA) == 0
    assert store.unread_critical(ANNA) == 0
    assert store.counts_of([ANNA]) == {"unread": 0, "needs_action": 0, "unread_critical": 0}
    assert store.mark_read_all(ANNA, dt_util.utcnow()) == 0


# Which channels --------------------------------------------------------------------------


async def test_popup_and_mail_deliveries_add_their_channel_to_the_same_copy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(
        hass,
        entry,
        severity="warning",
        channels=["push", "popup"],
        to={"push": {"recipients": [ANNA]}, "popup": {"recipients": [ANNA]}},
    )
    (item,) = inbox(entry).items(ANNA)
    assert item.copy and item.via == ["push", "popup"]


async def test_a_banner_for_named_people_leaves_a_copy_for_them_only(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(
        hass, entry, severity="warning", channels=["banner"], to={"banner": {"recipients": [ANNA]}}
    )
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.copy and item.via == ["banner"]
    assert inbox(entry).get(BEN, "m") is None


async def test_a_banner_for_everyone_leaves_a_copy_for_every_person_with_a_user(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    set_person(hass, "person.cara", "home")  # no Home Assistant user: cannot see a banner
    await send(hass, entry, severity="warning", channels=["banner"], to={})
    assert inbox(entry).people() == [ANNA, BEN]


async def test_speech_and_the_persistent_notification_leave_no_copy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(hass, entry, severity="warning", channels=["persistent"], to={})
    assert inbox(entry).people() == []


async def test_a_message_that_also_goes_to_the_inbox_stays_one_real_item(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await send(
        hass,
        entry,
        severity="warning",
        channels=["push", "inbox"],
        to={"push": {"recipients": [ANNA]}, "inbox": {"recipients": [ANNA]}},
    )
    (item,) = inbox(entry).items(ANNA)
    assert item.copy is False and item.unread is True
    assert sorted(item.via) == ["inbox", "push"]


async def test_the_inbox_channel_turns_a_copy_into_a_real_item(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry)
    assert inbox(entry).get(ANNA, "m").copy is True  # type: ignore[union-attr]
    await send(
        hass,
        entry,
        severity="warning",
        channels=["push", "inbox"],
        to={"push": {"recipients": [ANNA]}, "inbox": {"recipients": [ANNA]}},
    )
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.copy is False and item.unread is True


# What happens to a copy --------------------------------------------------------------------


async def test_a_new_text_updates_the_copy_and_it_stays_read(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry, message="first")
    await push_to_anna(hass, entry, message="second")
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.text == "second" and item.copy and item.unread is False


async def test_the_end_of_the_message_resolves_the_copy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    await push_to_anna(hass, entry)
    await hass.services.async_call("heads_up", "clear_notifications", {"id": "m"}, blocking=True)
    await hass.async_block_till_done()
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.resolved_reason == "cleared" and item.copy


async def test_a_reminder_neither_makes_nor_changes_a_copy(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Nag", **REMINDER)
    await push_to_anna(hass, entry)
    await wait(hass, entry, freezer, 10.1)
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.copy and item.reminders == 0 and item.unread is False


async def test_an_escalation_that_reaches_another_person_leaves_a_copy_for_them(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Up", **ESCALATION)  # a push to Ben after five minutes
    await push_to_anna(hass, entry)
    assert inbox(entry).get(BEN, "m") is None
    await wait(hass, entry, freezer, 5.1)
    ben = inbox(entry).get(BEN, "m")
    assert ben is not None and ben.copy and ben.via == ["push"]


async def test_a_held_push_makes_its_copy_when_it_is_sent(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"}, channels=["push"])
    freezer.move_to("2026-11-02 23:00:00+01:00")
    await push_to_anna(hass, entry)
    assert inbox(entry).get(ANNA, "m") is None
    await wait(hass, entry, freezer, 8 * 60 + 1)
    assert inbox(entry).get(ANNA, "m") is not None


# Who -------------------------------------------------------------------------------------


async def test_a_person_who_switched_the_inbox_off_gets_no_copy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={"person": ANNA, "channels": ["banner", "push"], "channels_v": 2},
            subentry_type="recipient_profile",
            title=ANNA,
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await push_to_anna(hass, entry)
    assert inbox(entry).get(ANNA, "m") is None


async def test_a_disabled_recipient_gets_no_copy(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={
                "person": ANNA,
                "enabled": False,
                "channels": ["banner", "push", "inbox"],
                "channels_v": 2,
            },
            subentry_type="recipient_profile",
            title=ANNA,
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()
    await send(hass, entry, severity="warning", channels=["banner"], to={})
    assert inbox(entry).get(ANNA, "m") is None and inbox(entry).get(BEN, "m") is not None


# Parity (DESIGN §22) -----------------------------------------------------------------------


async def test_a_rule_message_leaves_a_copy_through_the_mirror(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry, severity="warning")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    items = inbox(entry).items(ANNA)
    assert len(items) == 1 and items[0].copy and items[0].via == ["banner"]
    assert items[0].source is not None


# The cap ---------------------------------------------------------------------------------


async def test_over_the_cap_copies_go_before_real_items(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    from datetime import timedelta

    from custom_components.heads_up.const import INBOX_MAX_ITEMS

    store = inbox(entry)
    now = dt_util.utcnow()
    fields = {"title": "T", "text": "x", "severity": "info"}
    store.upsert(ANNA, "real", fields, "inbox", now - timedelta(days=20))
    store.mark_read(ANNA, "real", now - timedelta(days=19))
    store.resolve("real", "cleared", now - timedelta(days=19))  # read and resolved
    for n in range(INBOX_MAX_ITEMS):
        store.upsert(ANNA, f"c{n}", fields, "push", now - timedelta(seconds=n), copy=True)
    assert store.prune(now, months=12) == 1
    ids = {i.message_id for i in store.items(ANNA, limit=INBOX_MAX_ITEMS + 5)}
    assert "real" in ids  # a copy of the oldest went instead, though "real" is read and resolved


# The commands ------------------------------------------------------------------------------


async def ask(client: Any, kind: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/inbox_{kind}", **data})
    return dict(await client.receive_json())


async def test_the_list_has_the_views_inbox_and_all_notifications_and_says_whether_the_switch_is_on(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    set_person(hass, ANNA, "home", user_id=hass_admin_user.id)
    await send(
        hass,
        entry,
        id="copy",
        severity="warning",
        channels=["banner"],
        to={"banner": {"recipients": [ANNA]}},
    )
    store = inbox(entry)
    store.upsert(
        ANNA, "real", {"title": "R", "text": "r", "severity": "info"}, "inbox", dt_util.utcnow()
    )
    client = await hass_ws_client(hass)
    both = (await ask(client, "list", view="all"))["result"]
    only = (await ask(client, "list", view="inbox"))["result"]
    default = (await ask(client, "list"))["result"]
    assert sorted(i["message_id"] for i in both["items"]) == ["copy", "real"] and both["total"] == 2
    assert [i["message_id"] for i in only["items"]] == ["real"] and only["total"] == 1
    assert default["total"] == 1
    assert next(i for i in both["items"] if i["message_id"] == "copy")["copy"] is True
    assert both["all_notifications"] is True and both["unread"] == 1 and both["needs_action"] == 0


async def test_the_subscription_carries_copies_and_the_switch(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    set_person(hass, ANNA, "home", user_id=hass_admin_user.id)
    await send(
        hass,
        entry,
        id="copy",
        severity="warning",
        channels=["banner"],
        to={"banner": {"recipients": [ANNA]}},
    )
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/inbox_subscribe"})
    assert (await client.receive_json())["success"]
    event = (await client.receive_json())["event"]
    assert event["all_notifications"] is True and [i["message_id"] for i in event["items"]] == [
        "copy"
    ]
    assert event["unread"] == 0


# The setting -------------------------------------------------------------------------------


async def test_the_setting_is_a_channel_setting_that_takes_a_boolean(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)

    async def call(**data: Any) -> dict[str, Any]:
        await client.send_json_auto_id(data)
        return dict(await client.receive_json())

    config = (await call(type="heads_up/panel_config"))["result"]
    assert config["channels"]["inbox_all_notifications"] is True  # this module's options
    assert (await call(type="heads_up/channels_set", inbox_all_notifications=False))["success"]
    await hass.async_block_till_done()
    assert entry.options["inbox_all_notifications"] is False
    reply = await call(type="heads_up/channels_set", inbox_all_notifications="yes")
    assert not reply["success"] and reply["error"]["code"] == "invalid_format"


async def test_switching_it_off_stops_new_copies(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    await make_household(hass, mobile_app_device)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "inbox_all_notifications": False}
    )
    await hass.async_block_till_done()
    await push_to_anna(hass, entry)
    assert inbox(entry).people() == []


# Speech: for the people at home when it is spoken (D-276) ----------------------------------


@pytest.fixture(autouse=True)
def fake_media_source(monkeypatch: pytest.MonkeyPatch) -> None:
    from custom_components.heads_up.hub.channels import speak

    monkeypatch.setattr(speak, "media_source_id", lambda hass, text, engine, lang: f"tts://{text}")


async def say(hass: HomeAssistant, entry: MockConfigEntry, speakers: Any, **kw: Any) -> None:
    await send(
        hass,
        entry,
        severity="warning",
        channels=["speak"],
        to={"speak": {"recipients": [speakers.plain_player]}},
        **kw,
    )


async def test_a_spoken_message_is_listed_for_the_people_at_home(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
) -> None:
    await make_household(hass, mobile_app_device)
    move(hass, BEN, "not_home")
    await say(hass, entry, fake_speakers)
    assert fake_speakers.play_media
    item = inbox(entry).get(ANNA, "m")
    assert item is not None and item.copy and item.via == ["speak"] and item.unread is False
    assert inbox(entry).get(BEN, "m") is None


async def test_a_person_whose_presence_is_unknown_does_not_count_as_home(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
) -> None:
    await make_household(hass, mobile_app_device)
    move(hass, ANNA, "unknown")
    move(hass, BEN, "home")
    await say(hass, entry, fake_speakers)
    assert inbox(entry).people() == [BEN]


async def test_speech_that_nobody_heard_leaves_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
) -> None:
    await make_household(hass, mobile_app_device)
    move(hass, ANNA, "not_home")
    move(hass, BEN, "not_home")
    await say(hass, entry, fake_speakers)
    assert inbox(entry).people() == []


async def test_speech_that_was_skipped_leaves_nothing(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
) -> None:
    await make_household(hass, mobile_app_device)
    await say(hass, entry, fake_speakers)  # said
    await say(hass, entry, fake_speakers, id="again")  # the same text within the pause: skipped
    assert len(fake_speakers.play_media) == 1
    assert inbox(entry).get(ANNA, "m") is not None and inbox(entry).get(ANNA, "again") is None


async def test_speech_and_push_share_one_entry_with_both_channels(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    fake_speakers: Any,
) -> None:
    await make_household(hass, mobile_app_device)
    move(hass, BEN, "not_home")
    await send(
        hass,
        entry,
        severity="warning",
        channels=["push", "speak"],
        to={
            "push": {"recipients": [ANNA]},
            "speak": {"recipients": [fake_speakers.plain_player]},
        },
    )
    (item,) = inbox(entry).items(ANNA)
    assert item.copy and sorted(item.via) == ["push", "speak"]
