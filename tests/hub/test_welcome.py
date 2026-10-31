"""The welcome: default policies switched on or off on the first opening (D-121)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub.policies.models import policy_from_data
from custom_components.heads_up.hub.welcome import ITEMS, policies_for

from .helpers import FakeSpeakers
from .policy_support import QUIET, add_policy


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


def policies(entry: MockConfigEntry) -> dict[str, dict[str, Any]]:
    return {s.title: dict(s.data) for s in entry.subentries.values() if s.subentry_type == "policy"}


async def test_both_commands_are_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client, "welcome_get"))["error"]["code"] == "unauthorized"
    assert (await ask(client, "welcome_apply", items=["quiet"]))["error"]["code"] == "unauthorized"
    assert not policies(entry)


async def test_the_welcome_shows_until_it_was_seen(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    first = (await ask(client, "welcome_get"))["result"]
    assert first["show"] is True and [i["id"] for i in first["items"]] == list(ITEMS)
    assert first["default_audience"] == "Admins" and "Admins" in first["audiences"]
    await ask(client, "welcome_apply", items=[])
    assert entry.options["welcome_seen"] is True
    assert (await ask(client, "welcome_get"))["result"]["show"] is False


async def test_the_items_name_their_policies_and_what_is_missing(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(hass, entry, "Night quiet", **QUIET)
    client = await hass_ws_client(hass)
    items = {i["id"]: i for i in (await ask(client, "welcome_get"))["result"]["items"]}
    assert items["quiet"] == {"id": "quiet", "policies": ["Night quiet"], "missing": []}
    assert items["digest"]["missing"] == ["Evening summary"]
    assert items["critical"]["policies"] == [
        "Critical delivery",
        "Critical reminder",
        "Critical escalation",
    ]
    assert items["warnings"]["policies"] == ["Warning reminders"]


async def test_the_quiet_item_creates_night_quiet_as_decided(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=["quiet"])
    assert reply["result"] == {"added": ["Night quiet"], "skipped": []}
    data = policies(entry)["Night quiet"]
    assert data["type"] == "quiet_hours" and (data["from_time"], data["to_time"]) == (
        "22:00:00",
        "07:00:00",
    )
    assert data["action"] == "quiet" and data["critical_passes"] is True and data["days"] == []


async def test_the_digest_item_summarizes_tagged_messages_at_eight_in_the_evening(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["digest"])
    data = policies(entry)["Evening summary"]
    assert data["type"] == "summarize" and data["tags"] == ["digest"] and data["severities"] == []
    assert data["summary_at"] == "20:00:00" and data["include_critical"] is False


async def test_the_warning_item_creates_the_reminder(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["warnings"])
    data = policies(entry)["Warning reminders"]
    assert data["type"] == "reminder" and data["severities"] == ["warning"]
    assert (data["every_minutes"], data["max_count"]) == (30, 3)


async def test_the_critical_item_creates_delivery_reminder_and_escalation(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    fake_speakers: FakeSpeakers,
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(
        client,
        "welcome_apply",
        items=["critical"],
        audience="Everyone",
        speakers=[fake_speakers.satellite],
    )
    assert reply["result"]["added"] == [
        "Critical delivery",
        "Critical reminder",
        "Critical escalation",
    ]
    made = policies(entry)
    assert made["Critical delivery"]["type"] == "deliver"
    assert made["Critical delivery"]["targets"] == {"push": {"audience": "Everyone"}}
    assert (
        made["Critical reminder"]["every_minutes"] == 10
        and made["Critical reminder"]["max_count"] == 3
    )
    assert made["Critical reminder"]["channels"] == ["push"]
    escalation = made["Critical escalation"]
    assert escalation["after_minutes"] == 10 and escalation["dismiss_acks"] is True
    assert escalation["targets"] == {"speak": {"recipients": [fake_speakers.satellite]}}
    for data in made.values():
        assert data["severities"] == ["critical"]


async def test_the_critical_item_also_uses_the_ios_critical_push_level(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["critical"])
    levels = entry.options["push_levels"]
    assert levels["critical"] == "critical" and levels["warning"] == "normal"


async def test_without_speakers_there_is_no_speech_escalation_and_the_default_audience_is_admins(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=["critical"])
    assert reply["result"]["added"] == ["Critical delivery", "Critical reminder"]
    assert policies(entry)["Critical delivery"]["targets"] == {"push": {"audience": "Admins"}}


async def test_the_critical_policies_make_the_card_and_pushes_offer_acknowledge(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["critical"])
    await hass.async_block_till_done()
    await hass.services.async_call(
        "heads_up",
        "create_banner",
        {"id": "c", "message": "Leak", "severity": "critical"},
        blocking=True,
    )
    assert entry.runtime_data.hub.ack_applies(entry.runtime_data.banners["c"]) is True


async def test_nothing_that_is_switched_off_is_created(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    await ask(client, "welcome_apply", items=["digest", "warnings"])
    assert set(policies(entry)) == {"Evening summary", "Warning reminders"}


async def test_it_never_changes_or_deletes_an_existing_policy_and_is_idempotent(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    custom = {**QUIET, "from_time": "23:30:00", "action": "drop"}
    await add_policy(hass, entry, "Night quiet", **custom)
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=["quiet", "warnings"])
    assert reply["result"] == {
        "added": ["Warning reminders"],
        "skipped": [{"name": "Night quiet", "reason": "exists"}],
    }
    assert policies(entry)["Night quiet"]["from_time"] == "23:30:00"
    await hass.async_block_till_done()
    again = await ask(client, "welcome_apply", items=["quiet", "warnings"])
    assert again["result"]["added"] == [] and len(policies(entry)) == 2


async def test_a_policy_that_does_the_same_under_another_name_is_skipped(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await add_policy(
        hass,
        entry,
        "My nights",
        type="quiet_hours",
        from_time="22:00:00",
        to_time="07:00:00",
        days=[],
    )
    client = await hass_ws_client(hass)
    reply = await ask(client, "welcome_apply", items=["quiet"])
    assert reply["result"]["skipped"] == [{"name": "Night quiet", "reason": "duplicate"}]


async def test_an_unknown_audience_or_speaker_is_refused_and_nothing_is_created(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    bad = await ask(client, "welcome_apply", items=["critical"], audience="Nobody")
    assert bad["error"]["code"] == "unknown_audience"
    bad = await ask(client, "welcome_apply", items=["critical"], speakers=["media_player.gone"])
    assert bad["error"]["code"] == "unknown_recipient"
    assert not policies(entry) and "welcome_seen" not in entry.options


async def test_every_default_policy_is_valid_for_the_policy_form(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    for item in ITEMS:
        for name, data in policies_for(item, "Admins", ["media_player.k"]).items():
            policy = policy_from_data(name, "x", data)
            assert policy is not None and policy.type == data["type"], name


async def test_the_defaults_together_behave_as_decided_for_a_critical_message(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    fake_speakers: FakeSpeakers,
    mobile_app_device: Any,
    freezer: Any,
) -> None:
    from .policy_support import make_household, pushes, wait

    home = await make_household(hass, mobile_app_device)
    client = await hass_ws_client(hass)
    await ask(
        client,
        "welcome_apply",
        items=list(ITEMS),
        audience="Everyone",
        speakers=[fake_speakers.satellite],
    )
    await hass.async_block_till_done()
    await hass.services.async_call(
        "heads_up",
        "create_banner",
        {"id": "leak", "message": "Water leak", "severity": "critical"},
        blocking=True,
    )
    await wait(hass, entry, freezer, 0)
    # at once: pushed to the chosen audience at the iOS critical level, with Acknowledge
    assert len(pushes(home.anna)) == 1 and len(pushes(home.ben)) == 1
    assert pushes(home.anna)[0].data["data"]["push"]["interruption-level"] == "critical"
    assert any(a["action"].endswith(":ack") for a in pushes(home.anna)[0].data["data"]["actions"])
    assert not fake_speakers.announce
    await wait(hass, entry, freezer, 10.5)
    # after 10 minutes: pushed again to the same people, and said on the speaker
    assert len(pushes(home.anna)) == 2 and len(pushes(home.ben)) == 2
    assert len(fake_speakers.announce) == 1
    entry.runtime_data.acknowledge("leak", "anna-id")
    await wait(hass, entry, freezer, 30)
    assert (
        len(pushes(home.anna)) == 2 and len(fake_speakers.announce) == 1
    )  # acknowledged: it stops
