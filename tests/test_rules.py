"""Watch rules: virtual banners built from config subentries (DESIGN §17, D-052 to D-058)."""

from typing import Any

import pytest
import voluptuous as vol
from homeassistant.auth.models import User
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.manager import HeadsUpError

from .conftest import CreateBanner

WINDOW = "binary_sensor.window"
SENSOR = "sensor.heads_up_active_banners"
USER = "some-user-id"

RULE_DEFAULTS: dict[str, Any] = {
    "entity_id": WINDOW,
    "state": ["on"],
    "message": "Window open",
    "severity": "warning",
    "people": [],
    "dismissible": False,
    "enabled": True,
}


def add_rule(hass: HomeAssistant, entry: MockConfigEntry, **data: Any) -> ConfigSubentry:
    subentry = ConfigSubentry(
        data={**RULE_DEFAULTS, **data}, subentry_type="rule", title="Rule", unique_id=None
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    return subentry


def rule_id(subentry: ConfigSubentry) -> str:
    return f"rule_{subentry.subentry_id}"


def shown(entry: MockConfigEntry, user_id: str = USER) -> list[str]:
    return [b["id"] for b in entry.runtime_data.visible(user_id)]


async def set_state(hass: HomeAssistant, state: str, **attrs: object) -> None:
    hass.states.async_set(WINDOW, state, attrs)
    await hass.async_block_till_done()


async def test_banner_shows_while_condition_is_true(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "off")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()
    assert shown(entry) == []

    await set_state(hass, "on")
    assert shown(entry) == [rule_id(subentry)]
    item = entry.runtime_data.visible(USER)[0]
    assert item["message"] == "Window open" and item["severity"] == "warning"
    assert item["dismissible"] is False and item["expires_at"] is None
    assert item["icon"] == "mdi:alert" and item["tag"] == "rule"
    assert "condition" not in item and "dismissed_by" not in item
    assert item["rule"] is True  # tells the card to hide "Clear for everyone"

    await set_state(hass, "off")
    assert shown(entry) == []


async def test_rule_is_active_when_entity_is_already_in_state(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(subentry)]


async def test_state_list_and_attribute(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "idle", mode="eco")
    both = add_rule(hass, entry, state=["on", "idle"])
    attr = add_rule(hass, entry, state=["eco"], attribute="mode")
    miss = add_rule(hass, entry, state=["sport"], attribute="mode")
    await hass.async_block_till_done()
    assert sorted(shown(entry)) == sorted([rule_id(both), rule_id(attr)])
    assert rule_id(miss) not in shown(entry)


@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_unavailable_or_unknown_hides_the_banner(
    hass: HomeAssistant, entry: MockConfigEntry, state: str
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    assert len(shown(entry)) == 1

    await set_state(hass, state)
    assert shown(entry) == []
    await set_state(hass, "on")
    assert len(shown(entry)) == 1


async def test_removed_entity_hides_the_banner(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    hass.states.async_remove(WINDOW)
    await hass.async_block_till_done()
    assert shown(entry) == []


async def test_disabled_rule_shows_nothing_even_with_show_all(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, enabled=False)
    await hass.async_block_till_done()
    assert shown(entry) == []
    assert entry.runtime_data.visible(USER, show_all=True) == []

    hass.config_entries.async_update_subentry(
        entry, subentry, data={**subentry.data, "enabled": True}
    )
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(subentry)]


async def test_deleting_a_rule_removes_the_banner_and_notifies(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()
    updates: list[int] = []
    entry.runtime_data.subscribe(lambda: updates.append(len(shown(entry))))

    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    await hass.async_block_till_done()
    assert shown(entry) == [] and updates[-1] == 0


async def test_editing_a_rule_updates_the_banner(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()

    hass.config_entries.async_update_subentry(
        entry, subentry, data={**subentry.data, "message": "New text", "severity": "critical"}
    )
    await hass.async_block_till_done()
    item = entry.runtime_data.visible(USER)[0]
    assert item["message"] == "New text" and item["severity"] == "critical"


async def test_other_subentry_types_are_ignored(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(data=dict(RULE_DEFAULTS), subentry_type="other", title="x", unique_id=None),
    )
    await hass.async_block_till_done()
    assert shown(entry) == []


async def test_name_placeholder_follows_the_friendly_name(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on", friendly_name="Kitchen window")
    add_rule(hass, entry, message="{name} is open")
    await hass.async_block_till_done()
    assert entry.runtime_data.visible(USER)[0]["message"] == "Kitchen window is open"

    await set_state(hass, "on", friendly_name="Pantry window")
    assert entry.runtime_data.visible(USER)[0]["message"] == "Pantry window is open"


async def test_name_placeholder_falls_back_to_the_entity_id(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry, message="{name} is open")
    await hass.async_block_till_done()
    assert entry.runtime_data.visible(USER)[0]["message"] == f"{WINDOW} is open"


async def test_braces_other_than_name_stay_literal(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry, message="Set {x} and {")
    await hass.async_block_till_done()
    assert entry.runtime_data.visible(USER)[0]["message"] == "Set {x} and {"


async def test_people_targeting(
    hass: HomeAssistant, entry: MockConfigEntry, hass_admin_user: User
) -> None:
    hass.states.async_set("person.admin", "home", {"user_id": hass_admin_user.id})
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, people=["person.admin"])
    await hass.async_block_till_done()
    assert shown(entry, hass_admin_user.id) == [rule_id(subentry)]
    assert shown(entry, "someone-else") == []

    hass.states.async_set("person.admin", "home", {"user_id": "changed"})
    await hass.async_block_till_done()
    assert shown(entry, hass_admin_user.id) == []


async def test_rule_banner_survives_a_reload_without_touching_the_store(
    hass: HomeAssistant, entry: MockConfigEntry, hass_storage: dict[str, Any]
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(subentry)]
    assert hass_storage["heads_up.banners"]["data"] == {"banners": []}


async def test_rule_banners_do_not_count_against_max_banners(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    entry.runtime_data.options["max_banners"] = 1
    await set_state(hass, "on")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    assert (await create(id="a", message="x"))["status"] == "created"
    assert "evicted" not in await create(id="a", message="y")
    assert len(shown(entry)) == 2


async def test_sensor_counts_active_rule_banners(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    assert hass.states.get(SENSOR).state == "1"

    await set_state(hass, "on")
    await hass.async_block_till_done()
    assert hass.states.get(SENSOR).state == "2"


async def test_clear_actions_leave_rule_banners_alone(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await create(id="a", message="x", tag="rule")
    await hass.async_block_till_done()

    await hass.services.async_call(DOMAIN, "clear_banner", {"tag": "rule"}, blocking=True)
    await hass.services.async_call(DOMAIN, "clear_all", {}, blocking=True)
    assert shown(entry) == [rule_id(subentry)]


async def test_rule_ids_cannot_be_used_in_actions(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    # Subentry IDs are uppercase ULIDs, which the lowercase action ID pattern rejects, so a
    # caller can neither clear nor overwrite a rule banner.
    subentry = add_rule(hass, entry)
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "create_banner", {"id": rule_id(subentry), "message": "x"}, blocking=True
        )
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "clear_banner", {"id": rule_id(subentry)}, blocking=True
        )


async def test_non_dismissible_rule_cannot_be_dismissed(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry)
    await hass.async_block_till_done()
    with pytest.raises(HeadsUpError) as err:
        entry.runtime_data.dismiss(rule_id(subentry), USER)
    assert err.value.code == "not_dismissible"
    assert entry.runtime_data.dismiss_many([rule_id(subentry)], USER) == (0, 1)
    assert shown(entry) == [rule_id(subentry)]


async def test_dismissal_is_per_user_and_ends_when_the_condition_flips(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    assert entry.runtime_data.visible(USER)[0]["dismissible"] is True

    entry.runtime_data.dismiss(rule_id(subentry), USER)
    assert shown(entry) == []
    assert shown(entry, "other") == [rule_id(subentry)]

    await set_state(hass, "off")
    await set_state(hass, "on")
    assert shown(entry) == [rule_id(subentry)]


async def test_dismissal_is_lost_on_reload(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    entry.runtime_data.dismiss(rule_id(subentry), USER)

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert shown(entry) == [rule_id(subentry)]


async def test_admin_clear_is_rejected(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    with pytest.raises(HeadsUpError) as err:
        entry.runtime_data.admin_clear(rule_id(subentry))
    assert err.value.code == "rule_banner"
    assert shown(entry) == [rule_id(subentry)]


async def test_events_follow_the_condition_and_the_rule(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    created = async_capture_events(hass, f"{DOMAIN}_banner_created")
    cleared = async_capture_events(hass, f"{DOMAIN}_banner_cleared")
    dismissed = async_capture_events(hass, f"{DOMAIN}_banner_dismissed")
    await set_state(hass, "on")
    subentry = add_rule(hass, entry, dismissible=True)
    await hass.async_block_till_done()
    rid = rule_id(subentry)
    assert [e.data for e in created] == [{"id": rid, "tag": "rule", "severity": "warning"}]

    entry.runtime_data.dismiss(rid, USER)
    assert [e.data for e in dismissed] == [
        {"id": rid, "tag": "rule", "scope": "user", "user_id": USER}
    ]

    await set_state(hass, "off")
    assert [e.data for e in cleared] == [{"id": rid, "tag": "rule", "reason": "rule"}]
    await set_state(hass, "on")
    assert len(created) == 2

    hass.config_entries.async_update_subentry(
        entry, subentry, data={**subentry.data, "enabled": False}
    )
    await hass.async_block_till_done()
    assert len(cleared) == 2
    hass.config_entries.async_update_subentry(
        entry, subentry, data={**subentry.data, "enabled": True}
    )
    await hass.async_block_till_done()
    assert len(created) == 3
    hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    await hass.async_block_till_done()
    assert len(cleared) == 3


async def test_no_events_for_the_state_found_at_setup(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    created = async_capture_events(hass, f"{DOMAIN}_banner_created")
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert created == []


async def test_websocket_payload_and_errors(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await set_state(hass, "on")
    plain = add_rule(hass, entry)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "heads_up/subscribe"})
    assert (await client.receive_json())["success"]
    banners = (await client.receive_json())["event"]["banners"]
    assert [b["id"] for b in banners] == [rule_id(plain)]
    assert banners[0]["dismissed"] is False

    await client.send_json_auto_id({"type": "heads_up/dismiss", "banner_id": rule_id(plain)})
    assert (await client.receive_json())["error"]["code"] == "not_dismissible"
    await client.send_json_auto_id({"type": "heads_up/admin_clear", "banner_id": rule_id(plain)})
    assert (await client.receive_json())["error"]["code"] == "rule_banner"

    await set_state(hass, "off")
    assert (await client.receive_json())["event"]["banners"] == []


async def test_only_rule_banners_carry_the_rule_flag(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await set_state(hass, "on")
    add_rule(hass, entry)
    await create(id="a", message="x", dismissible=False)
    await hass.async_block_till_done()
    flags = {b["id"]: b.get("rule") for b in entry.runtime_data.visible(USER)}
    assert flags["a"] is None
    assert [v for k, v in flags.items() if k != "a"] == [True]
