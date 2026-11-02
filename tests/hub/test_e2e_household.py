"""A day in a household, end to end with stub devices (H10): a notification, an escalation that
somebody acknowledges from the phone, a digest summary, quiet night hours and a restart."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..test_restart import restart
from .conftest import AddDevice
from .helpers import fire_app_action, settle
from .policy_support import (
    ESCALATION,
    QUIET,
    REMINDER,
    SUMMARIZE,
    add_policy,
    make_household,
    pushes,
    send,
    summaries,
    wait,
)

ANNA = {"push": {"recipients": ["person.anna"]}}


async def test_a_day_in_the_household(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    mobile_app_device: AddDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    home = await make_household(hass, mobile_app_device)
    await add_policy(hass, entry, "Water", **{**ESCALATION, "severities": ["critical"]})
    await add_policy(hass, entry, "Nag", **{**REMINDER, "severities": ["critical"]})
    await add_policy(hass, entry, "Digest", **{**SUMMARIZE, "tags": ["digest"]})
    await add_policy(hass, entry, "Night", **{**QUIET, "action": "wait"})

    # Evening: an ordinary message reaches Anna at once, on the banner and on her phone.
    freezer.move_to("2026-11-02 19:00:00+01:00")
    await send(hass, entry, id="door", severity="info", message="Front door open", to=ANNA)
    assert len(pushes(home.anna)) == 1 and not pushes(home.ben)

    # A critical message: Anna gets it, nobody reacts, Ben is told after five minutes.
    await send(hass, entry, id="leak", message="Water leak", to=ANNA)
    assert len(pushes(home.anna)) == 2
    await wait(hass, entry, freezer, 5.1)
    assert [c.data["message"] for c in pushes(home.ben)] == ["Water leak"]

    # Ben acknowledges on his phone: the reminders stop and the banner shows who did.
    await fire_app_action(hass, "hu:leak:person.ben:ack", user_id="ben-id")
    await settle(hass, entry)
    assert entry.runtime_data.banners["leak"].acknowledged_by == ["ben-id"]
    count = len(pushes(home.anna))
    await wait(hass, entry, freezer, 60)
    assert len(pushes(home.anna)) == count

    # A digest message is held and arrives as one summary.
    await send(
        hass, entry, id="digest-1", severity="info", tag="digest", message="Washer done", to=ANNA
    )
    assert len(pushes(home.anna)) == count
    await wait(hass, entry, freezer, 61)
    assert len([b for b in summaries(entry) if b.channels == ["banner"]]) == 1
    assert len(pushes(home.anna)) == count + 1

    # The leak dries: everything is taken back, on both phones.
    await hass.services.async_call(DOMAIN, "clear", {"id": "leak"}, blocking=True)
    await settle(hass, entry)
    assert home.anna.calls[-1].data["message"] == "clear_notification"
    assert home.ben.calls[-1].data["message"] == "clear_notification"

    # Night: a warning waits for the morning; a restart in between changes nothing.
    freezer.move_to("2026-11-02 23:30:00+01:00")
    sent_before = len(pushes(home.anna))
    await send(hass, entry, id="mail", severity="warning", message="Mail is here", to=ANNA)
    assert len(pushes(home.anna)) == sent_before
    freezer.move_to("2026-11-03 03:00:00+01:00")
    await restart(hass, entry)
    await settle(hass, entry)
    assert len(pushes(home.anna)) == sent_before
    freezer.move_to("2026-11-03 07:05:00+01:00")
    await wait(hass, entry, freezer, 1)
    assert len(pushes(home.anna)) == sent_before + 1
    await wait(hass, entry, freezer, 120)
    assert len(pushes(home.anna)) == sent_before + 1
