"""Every mutation path of the manager emits a typed transition (DESIGN §23.11)."""

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.hub.transitions import BannerTransition, Kind, Reason

from ..conftest import CreateBanner
from ..test_restart import restart
from .helpers import tick

WINDOW = "binary_sensor.window"


def record(entry: MockConfigEntry) -> list[BannerTransition]:
    seen: list[BannerTransition] = []
    entry.runtime_data.subscribe_transitions(seen.append)
    return seen


def kinds(seen: list[BannerTransition]) -> list[tuple[Kind, str | None]]:
    return [(t.kind, t.reason) for t in seen]


async def test_create_emits_appeared_and_update_emits_updated(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    seen = record(entry)
    await create(id="a", message="one")
    await create(id="a", message="two")
    assert kinds(seen) == [(Kind.APPEARED, None), (Kind.UPDATED, None)]
    assert seen[1].banner.message == "two"
    assert not any(t.silent for t in seen)


async def test_severity_change_emits_severity_changed(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", severity="info")
    seen = record(entry)
    await create(id="a", message="x", severity="critical")
    assert (Kind.SEVERITY_CHANGED, None) in kinds(seen)


async def test_clear_emits_hidden_cleared(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    seen = record(entry)
    await hass.services.async_call("heads_up", "clear_banner", {"id": "a"}, blocking=True)
    assert kinds(seen) == [(Kind.HIDDEN, Reason.CLEARED)]
    assert seen[0].ends_message


async def test_clear_all_and_admin_clear_have_their_own_reasons(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    await create(id="b", message="x")
    seen = record(entry)
    entry.runtime_data.admin_clear("a")
    await hass.services.async_call("heads_up", "clear_all", {}, blocking=True)
    assert kinds(seen) == [(Kind.HIDDEN, Reason.ADMIN), (Kind.HIDDEN, Reason.CLEAR_ALL)]


async def test_expiry_emits_hidden_expired(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", timeout=60)
    seen = record(entry)
    await tick(hass, freezer, 61)
    assert kinds(seen) == [(Kind.HIDDEN, Reason.EXPIRED)]


async def test_eviction_emits_hidden_evicted(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    entry.runtime_data.options["max_banners"] = 1
    await create(id="a", message="x", severity="info")
    seen = record(entry)
    await create(id="b", message="x", severity="warning")
    assert (Kind.HIDDEN, Reason.EVICTED) in kinds(seen)


async def test_user_dismissal_hides_for_one_user_and_does_not_end_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x")
    seen = record(entry)
    entry.runtime_data.dismiss("a", "user-1")
    assert kinds(seen) == [(Kind.HIDDEN, Reason.DISMISSED)]
    assert seen[0].user_id == "user-1"
    assert not seen[0].ends_message


async def test_global_dismissal_ends_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="a", message="x", dismiss_scope="global")
    seen = record(entry)
    entry.runtime_data.dismiss("a", "user-1")
    assert kinds(seen) == [(Kind.HIDDEN, Reason.DISMISSED_GLOBAL)]
    assert seen[0].ends_message


async def test_snooze_unsnooze_and_elapsed_snooze_emit_transitions(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", snoozable=True)
    seen = record(entry)
    manager = entry.runtime_data
    manager.snooze("a", "user-1", 900)
    manager.unsnooze("a", "user-1")
    manager.snooze("a", "user-1", 900)
    await tick(hass, freezer, 901)  # the timer ends it; no bus event fires for that
    assert kinds(seen) == [
        (Kind.SNOOZED, None),
        (Kind.UNSNOOZED, None),
        (Kind.SNOOZED, None),
        (Kind.UNSNOOZED, Reason.ELAPSED),
    ]
    assert seen[-1].user_id == "user-1"


async def test_condition_turning_true_emits_became_visible_once_it_waited(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(WINDOW, "off")
    seen = record(entry)
    result = await create(id="a", message="x", condition={"entity_id": WINDOW, "state": "on"})
    assert result["status"] == "waiting"
    assert not seen[0].banner.active
    hass.states.async_set(WINDOW, "on")
    await hass.async_block_till_done()
    assert kinds(seen) == [(Kind.APPEARED, None), (Kind.BECAME_VISIBLE, None)]
    assert seen[1].banner.active


async def test_recurring_condition_flip_emits_hidden_condition(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(WINDOW, "on")
    await create(
        id="a", message="x", mode="recurring", condition={"entity_id": WINDOW, "state": "on"}
    )
    seen = record(entry)
    hass.states.async_set(WINDOW, "off")
    await hass.async_block_till_done()
    assert kinds(seen) == [(Kind.HIDDEN, Reason.CONDITION)]


async def test_once_condition_flip_removes_the_message(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.states.async_set(WINDOW, "on")
    await create(id="a", message="x", condition={"entity_id": WINDOW, "state": "on"})
    seen = record(entry)
    hass.states.async_set(WINDOW, "off")
    await hass.async_block_till_done()
    assert kinds(seen) == [(Kind.HIDDEN, Reason.CONDITION)]
    assert seen[0].ends_message


def add_rule(hass: HomeAssistant, entry: MockConfigEntry) -> ConfigSubentry:
    subentry = ConfigSubentry(
        data={
            "entity_id": WINDOW,
            "state": ["on"],
            "message": "Window open",
            "severity": "warning",
            "people": [],
            "dismissible": False,
            "enabled": True,
        },
        subentry_type="rule",
        title="Rule",
        unique_id=None,
    )
    hass.config_entries.async_add_subentry(entry, subentry)
    return subentry


async def test_rule_messages_emit_the_same_transitions_as_action_messages(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    seen = record(entry)
    hass.states.async_set(WINDOW, "off")
    rule = add_rule(hass, entry)
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "on")
    await hass.async_block_till_done()
    hass.states.async_set(WINDOW, "off")
    await hass.async_block_till_done()
    assert kinds(seen) == [(Kind.BECAME_VISIBLE, None), (Kind.HIDDEN, Reason.CONDITION)]
    assert seen[0].banner.source == "rule"
    assert seen[0].banner.id == f"rule_{rule.subentry_id}"


async def test_deleting_a_showing_rule_emits_hidden_rule(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "on")
    rule = add_rule(hass, entry)
    await hass.async_block_till_done()
    seen = record(entry)
    hass.config_entries.async_remove_subentry(entry, rule.subentry_id)
    await hass.async_block_till_done()
    assert kinds(seen) == [(Kind.HIDDEN, Reason.RULE)]


async def test_showing_rule_is_recorded_in_the_ledger_after_a_restart(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.states.async_set(WINDOW, "on")
    add_rule(hass, entry)
    await hass.async_block_till_done()
    await restart(hass, entry)
    ledger_rows = entry.runtime_data.hub.ledger.rows
    assert any(r.message_id.startswith("rule_") for r in ledger_rows.values())


async def test_existing_bus_event_payloads_are_unchanged(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    from pytest_homeassistant_custom_component.common import async_capture_events

    created = async_capture_events(hass, "heads_up_banner_created")
    await create(id="a", message="x", tag="g")
    assert created[0].data == {"id": "a", "tag": "g", "severity": "warning"}
