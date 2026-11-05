"""Dismiss, snooze and unsnooze act only for people the banner is addressed to (D-156)."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.manager import HeadsUpError

from .conftest import CreateBanner
from .test_rules import add_rule, rule_id, set_state

TARGET = "target-user"
STRANGER = "stranger-user"


@pytest.fixture(autouse=True)
def person(hass: HomeAssistant) -> None:
    hass.states.async_set("person.target", "home", {"user_id": TARGET})


async def stored(create: CreateBanner, entry: MockConfigEntry, scope: str) -> str:
    await create(
        id="b",
        message="x",
        people=["person.target"],
        dismissible=True,
        dismiss_scope=scope,
        snoozable=True,
        snooze_scope=scope,
    )
    return "b"


async def rule(hass: HomeAssistant, entry: MockConfigEntry, scope: str) -> str:
    await set_state(hass, "on")
    sub = add_rule(
        hass,
        entry,
        people=["person.target"],
        dismissible=True,
        dismiss_scope=scope,
        snoozable=True,
        snooze_scope=scope,
    )
    await hass.async_block_till_done()
    return rule_id(sub)


@pytest.mark.parametrize("kind", ["stored", "rule"])
@pytest.mark.parametrize("scope", ["user", "global"])
async def test_a_stranger_cannot_change_a_banner(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    kind: str,
    scope: str,
) -> None:
    banner_id = (
        await stored(create, entry, scope) if kind == "stored" else await rule(hass, entry, scope)
    )
    manager = entry.runtime_data
    seconds = manager.quick_snooze_seconds

    with pytest.raises(HeadsUpError) as err:
        manager.dismiss(banner_id, STRANGER)
    assert err.value.code == "not_targeted"
    with pytest.raises(HeadsUpError) as err:
        manager.snooze(banner_id, STRANGER, seconds)
    assert err.value.code == "not_targeted"
    assert manager.dismiss_many([banner_id], STRANGER) == (0, 1)
    assert [b["id"] for b in manager.visible(TARGET)] == [banner_id]

    manager.snooze(banner_id, TARGET, seconds)  # the target can, for any scope
    with pytest.raises(HeadsUpError) as err:
        manager.unsnooze(banner_id, STRANGER)
    assert err.value.code == "not_targeted"
    assert manager.visible(TARGET) == []  # still snoozed
    manager.unsnooze(banner_id, TARGET)
    manager.dismiss(banner_id, TARGET)
    assert manager.visible(TARGET) == []


async def test_untargeted_banner_is_open_to_everyone(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="open", message="x", dismissible=True)
    entry.runtime_data.dismiss("open", STRANGER)
    assert entry.runtime_data.visible(STRANGER) == []


async def test_dismiss_many_skips_only_untargeted(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="open", message="x", dismissible=True)
    await create(id="private", message="x", dismissible=True, people=["person.target"])
    assert entry.runtime_data.dismiss_many(["open", "private"], STRANGER) == (1, 1)
    assert entry.runtime_data.visible(STRANGER) == []  # "open" dismissed for them
    assert [b["id"] for b in entry.runtime_data.visible(TARGET)] == ["open", "private"]
