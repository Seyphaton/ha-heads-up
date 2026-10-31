"""Summarize: hold on every channel, then one summary per recipient and channel (D-105, D-113)."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.policies.models import Policy
from custom_components.heads_up.hub.policies.summarize import build, next_due

from ..test_restart import restart
from ..test_rules import WINDOW, add_rule
from .conftest import AddDevice
from .helpers import settle
from .policy_support import (
    ESCALATION,
    QUIET,
    SUMMARIZE,
    add_policy,
    make_household,
    pushes,
    send,
    shown,
    summaries,
    wait,
)

ANNA = {"push": {"recipients": ["person.anna"]}}
BEN = {"push": {"recipients": ["person.ben"]}}


async def hold(hass: HomeAssistant, entry: MockConfigEntry, mid: str, **kw: object) -> None:
    await send(hass, entry, id=mid, severity="warning", message=f"Message {mid}", **kw)


async def test_a_matching_message_is_hidden_and_not_pushed(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a")
    assert shown(entry) == [] and not pushes(home.anna)
    assert entry.runtime_data.active_count() == 0
    assert entry.runtime_data.hub.is_held("a")


async def test_one_summary_per_recipient_lists_only_their_messages(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", to=ANNA)
    await hold(hass, entry, "b", to=BEN)
    both = {"push": {"recipients": ["person.anna", "person.ben"]}}
    await hold(hass, entry, "c", to=both)
    await wait(hass, entry, freezer, 61)
    (anna_push,) = pushes(home.anna)
    (ben_push,) = pushes(home.ben)
    assert "Message a" in anna_push.data["message"] and "Message c" in anna_push.data["message"]
    assert "Message b" not in anna_push.data["message"]
    assert "Message b" in ben_push.data["message"] and "Message a" not in ben_push.data["message"]
    assert anna_push.data["title"] == "Summary: 2 messages"


async def test_the_banner_gets_one_summary_listing_the_messages(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", to=ANNA)
    await hold(hass, entry, "b", to=BEN)
    await wait(hass, entry, freezer, 61)
    (banner,) = [s for s in summaries(entry) if s.channels == ["banner"]]
    assert "Message a" in banner.message and "Message b" in banner.message
    assert shown(entry) == [banner.id]  # the originals stay hidden; the summary stands for them


async def test_the_summary_has_the_highest_severity(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await send(hass, entry, id="a", severity="info")
    await send(hass, entry, id="b", severity="warning")
    await wait(hass, entry, freezer, 61)
    assert {s.severity for s in summaries(entry)} == {"warning"}


async def test_a_summary_lists_ten_and_counts_the_rest(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    for i in range(13):
        await hold(hass, entry, f"m{i:02}", channels=["banner"], to={})
    await wait(hass, entry, freezer, 61)
    (banner,) = summaries(entry)
    lines = banner.message.split("\n")
    assert len(lines) == 11 and lines[-1] == "and 3 more"
    assert banner.title == "Summary: 13 messages"


async def test_a_message_cleared_before_the_summary_is_listed_as_resolved(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a")
    await hold(hass, entry, "b")
    entry.runtime_data.admin_clear("a")
    await wait(hass, entry, freezer, 61)
    banner = next(s for s in summaries(entry) if s.channels == ["banner"])
    assert "• Message a (resolved)" in banner.message and "• Message b\n" not in banner.message
    assert "Message b" in banner.message


async def test_nothing_is_sent_when_nothing_was_held(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await wait(hass, entry, freezer, 130)
    assert summaries(entry) == []
    await hold(hass, entry, "a")
    await wait(hass, entry, freezer, 61)
    count = len(summaries(entry))
    await wait(hass, entry, freezer, 130)  # nothing new was held
    assert len(summaries(entry)) == count


async def test_the_interval_counts_from_the_first_message_held_after_a_summary(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a")
    await wait(hass, entry, freezer, 30)
    await hold(hass, entry, "b")
    await wait(hass, entry, freezer, 31)  # 61 after "a"
    banner = next(s for s in summaries(entry) if s.channels == ["banner"])
    assert "Message a" in banner.message and "Message b" in banner.message
    await hold(hass, entry, "c")
    await wait(hass, entry, freezer, 61)
    later = [s for s in summaries(entry) if s.channels == ["banner"]][-1]
    assert "Message c" in later.message and "Message a" not in later.message


async def test_critical_messages_are_delivered_at_once_unless_the_policy_includes_them(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await send(hass, entry, id="crit")
    assert len(pushes(home.anna)) == 1 and shown(entry) == ["crit"]
    (sub,) = [s for s in entry.subentries.values() if s.title == "Digest"]
    hass.config_entries.async_update_subentry(
        entry, sub, data={**SUMMARIZE, "include_critical": True}
    )
    await hass.async_block_till_done()
    await send(hass, entry, id="crit2")
    assert len(pushes(home.anna)) == 1 and "crit2" not in shown(entry)


async def test_a_held_message_that_becomes_critical_is_released(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a")
    assert shown(entry) == []
    await send(hass, entry, id="a", severity="critical", message="Now critical")
    assert shown(entry) == ["a"] and len(pushes(home.anna)) == 1


async def test_a_daily_summary_comes_at_the_time_of_day(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    await make_household(hass, mobile_app_device)
    freezer.move_to("2026-11-02 19:00:00+01:00")
    await add_policy(hass, entry, "Evening", type="summarize", summary_at="20:00:00")
    await hold(hass, entry, "a")
    await wait(hass, entry, freezer, 59)
    assert summaries(entry) == []
    await wait(hass, entry, freezer, 2)
    assert len([s for s in summaries(entry) if s.channels == ["banner"]]) == 1


async def test_a_held_message_and_its_timer_survive_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", to=ANNA)
    await restart(hass, entry)
    await settle(hass, entry)
    assert shown(entry) == [] and not pushes(home.anna)
    await wait(hass, entry, freezer, 61)
    assert len(pushes(home.anna)) == 1


async def test_an_overdue_summary_is_sent_once_after_a_restart(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", to=ANNA)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    freezer.tick(7200)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(pushes(home.anna)) == 1


async def test_the_summary_passes_quiet_hours(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    home = await make_household(hass, mobile_app_device)
    freezer.move_to("2026-11-02 21:30:00+01:00")
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await add_policy(hass, entry, "Night", **QUIET)
    await hold(hass, entry, "a", to=ANNA)
    await wait(hass, entry, freezer, 61)  # 22:31, inside the window
    (call,) = pushes(home.anna)
    assert call.data["data"]["importance"] == "low"


async def test_a_summary_stays_for_24_hours(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", channels=["banner"], to={})
    await wait(hass, entry, freezer, 61)
    assert len(summaries(entry)) == 1
    await wait(hass, entry, freezer, 23 * 60)
    assert len(summaries(entry)) == 1
    await wait(hass, entry, freezer, 2 * 60)
    assert summaries(entry) == []


async def test_a_summary_is_not_held_escalated_or_summarized_again(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await add_policy(hass, entry, "Water", **ESCALATION)
    await hold(hass, entry, "a", to=ANNA)
    await wait(hass, entry, freezer, 61)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)
    await wait(hass, entry, freezer, 130)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)
    assert not entry.runtime_data.hub.ledger.timers(summaries(entry)[0].id)


async def test_deleting_the_policy_releases_the_held_messages(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    sub = await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", to=ANNA)
    assert shown(entry) == []
    hass.config_entries.async_remove_subentry(entry, sub.subentry_id)
    await settle(hass, entry)
    assert shown(entry) == ["a"] and len(pushes(home.anna)) == 1


async def test_the_call_can_leave_a_message_out_with_policy_none(
    hass: HomeAssistant, entry: MockConfigEntry, mobile_app_device: AddDevice
) -> None:
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await send(hass, entry, id="a", severity="warning", policy="none")
    assert shown(entry) == ["a"] and len(pushes(home.anna)) == 1


async def test_a_changed_message_is_listed_again_an_unchanged_one_is_not(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Digest", **SUMMARIZE)
    await hold(hass, entry, "a", channels=["banner"], to={})
    await wait(hass, entry, freezer, 61)
    await hold(hass, entry, "a", channels=["banner"], to={})  # same text again
    await wait(hass, entry, freezer, 61)
    assert len(summaries(entry)) == 1
    await send(
        hass, entry, id="a", severity="warning", message="Different", channels=["banner"], to={}
    )
    await wait(hass, entry, freezer, 61)
    assert len(summaries(entry)) == 2


async def test_a_rule_message_is_held_like_any_other(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Rules", **SUMMARIZE, tags=["rule"])
    hass.states.async_set(WINDOW, "off")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await settle(hass, entry)
    assert shown(entry) == []
    await wait(hass, entry, freezer, 61)
    (banner,) = summaries(entry)
    assert "Window open" in banner.message and shown(entry) == [banner.id]


def test_the_text_of_a_summary_follows_the_language() -> None:
    from homeassistant.util import dt as dt_util

    from custom_components.heads_up.hub.ledger import HeldMessage

    entry = HeldMessage("a", "summarize:P", "Fenster offen", "info", dt_util.utcnow())
    assert build([entry], "de")[0] == "Zusammenfassung: 1 Meldung"
    assert build([entry], "xx")[0] == "Summary: 1 message"


def test_the_next_summary_time() -> None:
    from datetime import UTC, datetime

    from homeassistant.util import dt as dt_util

    now = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
    assert next_due(Policy("P", "summarize", summary_every=45), now).minute == 45
    daily = next_due(Policy("P", "summarize", summary_at="20:00:00"), now)
    assert daily > now and dt_util.as_local(daily).hour == 20
