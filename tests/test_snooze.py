"""Snooze: per user and global, expiry, resets, restart, options (DESIGN §21, D-069)."""

from datetime import timedelta
from typing import Any

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.auth.models import User
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN

from .conftest import CreateBanner, banners
from .test_restart import restart
from .test_websocket import subscribe


async def snooze(client: Any, banner_id: str, seconds: int) -> dict[str, Any]:
    await client.send_json_auto_id(
        {"type": "heads_up/snooze", "banner_id": banner_id, "seconds": seconds}
    )
    return await client.receive_json()


async def tick(hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: int) -> None:
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_banner_is_not_snoozable_by_default(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x")
    client = await hass_ws_client(hass)
    result = await snooze(client, "a", 900)
    assert result["error"]["code"] == "not_snoozable"


async def test_snooze_hides_for_that_user_then_banner_returns(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", snoozable=True)
    events = async_capture_events(hass, f"{DOMAIN}_banner_snoozed")
    client = await hass_ws_client(hass)
    await subscribe(client)

    await client.send_json_auto_id({"type": "heads_up/snooze", "banner_id": "a", "seconds": 900})
    assert (await client.receive_json())["event"]["banners"] == []  # pushed before the result
    assert (await client.receive_json())["success"]
    assert events[0].data["id"] == "a" and events[0].data["scope"] == "user"

    await tick(hass, freezer, 901)
    update = await client.receive_json()
    assert [b["id"] for b in update["event"]["banners"]] == ["a"]
    assert banners(entry)["a"].snoozed_until == {}


async def test_user_snooze_does_not_hide_the_banner_from_others(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    await create(id="a", message="x", snoozable=True)
    admin = await hass_ws_client(hass)
    other = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await snooze(admin, "a", 900))["success"]
    _, seen_by_other = await subscribe(other)
    assert [b["id"] for b in seen_by_other] == ["a"]


async def test_global_snooze_hides_the_banner_from_everyone(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    await create(id="a", message="x", snoozable=True, snooze_scope="global")
    admin = await hass_ws_client(hass)
    other = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await snooze(admin, "a", 900))["success"]
    _, seen_by_other = await subscribe(other)
    assert seen_by_other == []


async def test_snooze_must_be_one_of_the_banner_choices(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", snoozable=True, snooze_options=[{"minutes": 10}])
    client = await hass_ws_client(hass)
    assert (await snooze(client, "a", 900))["error"]["code"] == "invalid_snooze"
    assert (await snooze(client, "a", 600))["success"]


async def test_snooze_of_unknown_banner_fails(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await snooze(client, "nope", 900))["error"]["code"] == "not_found"


async def test_not_dismissible_banner_cannot_be_snoozable(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    with pytest.raises(Exception, match="snoozable"):
        await create(id="a", message="x", snoozable=True, dismissible=False)


async def test_not_dismissible_banner_ignores_the_option_default(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    hass.config_entries.async_update_entry(entry, options={"default_snoozable": True})
    await create(id="a", message="x", dismissible=False)
    await create(id="b", message="x")
    assert not banners(entry)["a"].snoozable
    assert banners(entry)["b"].snoozable


@pytest.mark.parametrize(
    "choices", [[{"seconds": 30}], [{"days": 8}], [{"minutes": n} for n in range(1, 8)]]
)
async def test_snooze_choices_are_limited(
    entry: MockConfigEntry, create: CreateBanner, choices: list[dict[str, int]]
) -> None:
    with pytest.raises(Exception, match="snooze"):
        await create(id="a", message="x", snoozable=True, snooze_options=choices)


async def test_upsert_clears_snoozes(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", snoozable=True)
    client = await hass_ws_client(hass)
    assert (await snooze(client, "a", 900))["success"]
    await create(id="a", message="again", snoozable=True)
    _, shown = await subscribe(client)
    assert [b["id"] for b in shown] == ["a"]
    assert entry.runtime_data._snooze_timers == {}


async def test_recurring_condition_flip_clears_snoozes(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    hass.states.async_set("binary_sensor.d", "on")
    await create(
        id="w",
        message="x",
        snoozable=True,
        mode="recurring",
        condition={"entity_id": "binary_sensor.d", "state": "on"},
    )
    client = await hass_ws_client(hass)
    assert (await snooze(client, "w", 900))["success"]
    hass.states.async_set("binary_sensor.d", "off")
    await hass.async_block_till_done()
    hass.states.async_set("binary_sensor.d", "on")
    await hass.async_block_till_done()
    _, shown = await subscribe(client)
    assert [b["id"] for b in shown] == ["w"]


async def test_snooze_survives_restart_and_still_ends_on_time(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: User,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", snoozable=True, timeout=0)
    client = await hass_ws_client(hass)
    assert (await snooze(client, "a", 3600))["success"]
    await hass.async_block_till_done()
    await restart(hass, entry)

    client = await hass_ws_client(hass)
    _, shown = await subscribe(client)
    assert shown == []

    await tick(hass, freezer, 3601)
    assert [b["id"] for b in entry.runtime_data.visible(hass_admin_user.id)] == ["a"]


async def test_snooze_that_ended_during_downtime_is_dropped_on_load(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
    freezer: FrozenDateTimeFactory,
) -> None:
    await create(id="a", message="x", snoozable=True, timeout=0)
    client = await hass_ws_client(hass)
    assert (await snooze(client, "a", 900))["success"]
    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(entry.entry_id)
    freezer.tick(timedelta(hours=1))
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert banners(entry)["a"].snoozed_until == {}


async def test_snoozed_banner_is_flagged_for_show_all(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    create: CreateBanner,
    hass_ws_client: WebSocketGenerator,
) -> None:
    await create(id="a", message="x", snoozable=True)
    client = await hass_ws_client(hass)
    assert (await snooze(client, "a", 900))["success"]
    _, shown = await subscribe(client, show_all=True)
    assert shown[0]["snoozed"] is True
    assert "snoozed_until" not in shown[0]


async def test_snooze_choices_come_from_the_options(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "max_banners": 50,
            "evict": True,
            "default_dismiss_scope": "user",
            "default_snoozable": True,
            "default_snooze_scope": "global",
            "default_snooze_options": ["5", "60"],
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    await create(id="a", message="x")
    banner = banners(entry)["a"]
    assert banner.snoozable and banner.snooze_scope == "global"
    assert banner.snooze_options == [300, 3600]


async def test_empty_snooze_choices_in_options_fall_back_to_defaults(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "max_banners": 50,
            "evict": True,
            "default_dismiss_scope": "user",
            "default_snooze_options": [],
        },
    )
    assert entry.options["default_snooze_options"] == [900, 3600, 14400]


async def test_create_without_response_still_validates_snooze_scope(
    entry: MockConfigEntry, create: CreateBanner
) -> None:
    with pytest.raises((ServiceValidationError, Exception)):
        await create(id="a", message="x", snooze_scope="nobody")
