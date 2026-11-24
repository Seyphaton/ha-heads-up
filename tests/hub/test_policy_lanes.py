"""Policies without an order (DESIGN §25.3, D-224): which policies fit a message, the band, and
the conversion from 1.x reproducing "only the first"."""

from __future__ import annotations

from datetime import UTC, datetime
from itertools import product
from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.const import DOMAIN, SEVERITIES
from custom_components.heads_up.hub.channels.base import Target
from custom_components.heads_up.hub.migration import fold_filters
from custom_components.heads_up.hub.policies import PolicyBook
from custom_components.heads_up.hub.policies.convert import StoredPolicy, convert_v3
from custom_components.heads_up.hub.policies.models import Policy, policy_from_data
from custom_components.heads_up.models import Banner

NOW = datetime(2026, 11, 20, 12, tzinfo=UTC)


def message(
    severity: str = "info", tag: str | None = None, id: str = "m", policy: Any = None
) -> Banner:
    banner = Banner(
        id=id,
        message="x",
        severity=severity,
        dismissible=True,
        dismiss_scope="global",
        created_at=NOW,
        updated_at=NOW,
        tag=tag,
    )
    if policy is not None:
        banner.policy = policy
    return banner


class Book(PolicyBook):
    def __init__(self, *policies: Policy) -> None:
        super().__init__()
        self._policies = {p.subentry_id: p for p in policies}


def policy(id: str, kind: str = "reminder", **data: Any) -> Policy:
    made = policy_from_data(id, id, {"type": kind, **data})
    assert made is not None
    return made


def names(book: PolicyBook, banner: Banner) -> set[str]:
    return {p.name for p in book.for_message(banner)}


def test_every_fitting_policy_acts() -> None:
    book = Book(
        policy("fast", every_minutes=15),
        policy("slow", every_minutes=60),
        policy("night", "quiet_hours"),
    )
    assert names(book, message()) == {"fast", "slow", "night"}


def test_not_for_tags_wins_over_for() -> None:
    book = Book(policy("night", "quiet_hours", not_tags=["digest"]))
    assert names(book, message(tag="digest")) == set()
    assert names(book, message("critical")) == {"night"}
    assert names(book, message(tag="doorbell")) == {"night"}


def test_a_link_holds_back_only_while_the_linked_policy_is_on_and_fits() -> None:
    summary = policy("eve", "summarize", tags=["digest"])
    night = policy("night", "quiet_hours", links=["eve"])
    book = Book(summary, night)
    assert names(book, message(tag="digest")) == {"eve"}
    assert names(book, message(tag="other")) == {"night"}
    summary.enabled = False
    assert names(book, message(tag="digest")) == {"night"}


def test_a_link_to_a_deleted_policy_holds_nothing_back() -> None:
    book = Book(policy("night", "quiet_hours", links=["gone"]))
    assert names(book, message()) == {"night"}


def test_a_named_policy_runs_alone_and_a_manual_one_only_when_named() -> None:
    book = Book(policy("auto"), policy("man", apply="manual"))
    assert names(book, message(policy=["man"])) == {"man"}
    assert names(book, message(policy=["automatic", "man"])) == {"auto", "man"}
    assert names(book, message(policy=["none"])) == set()
    assert names(book, message()) == {"auto"}


def test_a_band_entry_covers_everyone_or_only_its_people() -> None:
    everyone = policy("all", "get_through", severities=["critical"])
    book = Book(everyone)
    assert book.passes(message("critical"))
    assert book.passes(message("critical"), Target("person.anna", "person", "person.anna"))
    assert not book.passes(message("warning"))
    only = policy(
        "admins",
        "get_through",
        tags=["alarm"],
        covers="only",
        covers_audiences=["admins"],
        covers_recipients=["media_player.kitchen"],
    )
    book = Book(only)
    book.household = lambda audience: ["person.chris"] if audience == "admins" else []
    leak = message("warning", "alarm")
    assert book.passes(leak)  # Summarize: the whole message (D-235)
    assert book.passes(leak, Target("person.chris", "person", "person.chris"))
    assert not book.passes(leak, Target("person.anna", "person", "person.anna"))
    assert book.passes(leak, Target("media_player.kitchen", "speaker"))


def test_several_band_entries_add_up() -> None:
    book = Book(
        policy(
            "admins",
            "get_through",
            tags=["alarm"],
            covers="only",
            covers_recipients=["person.chris"],
        ),
        policy(
            "anna", "get_through", tags=["alarm"], covers="only", covers_recipients=["person.anna"]
        ),
    )
    leak = message("warning", "alarm")
    for person in ("person.chris", "person.anna"):
        assert book.passes(leak, Target(person, "person", person))
    assert not book.passes(leak, Target("person.ben", "person", "person.ben"))


def test_the_page_order_follows_the_lanes() -> None:
    book = Book(
        policy("r"), policy("g", "get_through"), policy("q", "quiet_hours"), policy("d", "deliver")
    )
    assert [p.type for p in book.ordered()] == ["quiet_hours", "get_through", "deliver", "reminder"]


def _old_first(stored: list[StoredPolicy], order: list[str], banner: Banner) -> set[str]:
    """The 1.x selection under "only the first": the first enabled automatic policy that
    matches, in list order."""
    by_id = {p.subentry_id: p for p in stored}
    listed = [by_id[i] for i in order if i in by_id] + [
        p for p in stored if p.subentry_id not in order
    ]
    for item in listed:
        made = policy_from_data(item.title, item.subentry_id, item.data)
        assert made is not None
        if (
            made.enabled
            and made.apply != "manual"
            and (not made.severities or banner.severity in made.severities)
            and (not made.tags or banner.tag in made.tags)
        ):
            # A 1.x Presence that let critical pass did nothing to it: 2.0 says so with Not for
            # critical, so the policy does not fit at all (same behaviour).
            if (
                made.type == "presence"
                and banner.severity == "critical"
                and item.data.get("critical_passes", True)
            ):
                return set()
            return {made.name}
    return set()


WELCOME = [
    StoredPolicy("crit", "Critical delivery", {"type": "deliver", "severities": ["critical"]}),
    StoredPolicy("warn", "Warning reminder", {"type": "reminder", "severities": ["warning"]}),
    StoredPolicy(
        "eve",
        "Evening summary",
        {"type": "summarize", "severities": ["passive", "info"], "tags": ["digest"]},
    ),
    StoredPolicy(
        "night", "Night quiet", {"type": "quiet_hours", "severities": ["passive", "info"]}
    ),
    StoredPolicy("away", "Away", {"type": "presence"}),
    StoredPolicy("tagged", "Doorbell", {"type": "deliver", "tags": ["doorbell"]}),
]


def test_converted_links_reproduce_only_the_first_for_every_message_and_switch_state() -> None:
    """The equivalence test of DESIGN §25.6 for selection: every severity, tag and combination
    of switches, for the later Away at the end and at the top of the stored order."""
    for order in (
        ["crit", "warn", "eve", "night", "tagged"],
        ["away", "crit", "warn", "eve", "night", "tagged"],
    ):
        for switches in product((True, False), repeat=len(WELCOME)):
            stored = [
                StoredPolicy(p.subentry_id, p.title, {**p.data, "enabled": on})
                for p, on in zip(WELCOME, switches, strict=True)
            ]
            # Converted with the switches as stored at the update (Not for is written then).
            result = convert_v3(stored, {"policy_mode": "first", "policy_order": order})
            # 3.2 then writes Not for severities as For (D-280).
            folded = fold_filters(
                {
                    p.subentry_id: {
                        **result.updates.get(p.subentry_id, p.data),
                        "enabled": p.data["enabled"],
                    }
                    for p in stored
                }
            )
            converted = [
                policy_from_data(p.title, p.subentry_id, folded[p.subentry_id]) for p in stored
            ]
            book = Book(*[p for p in converted if p is not None and p.type != "get_through"])
            for severity, tag in product(SEVERITIES, (None, "digest", "doorbell", "other")):
                banner = message(severity, tag)
                assert names(book, banner) == _old_first(stored, order, banner), (
                    order,
                    switches,
                    severity,
                    tag,
                )


async def test_a_2_4_entry_moves_to_the_lanes_at_start(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        minor_version=4,
        options={"policy_mode": "first", "policy_order": ["crit", "eve", "night"]},
        subentries_data=[
            {
                "subentry_id": p.subentry_id,
                "subentry_type": "policy",
                "title": p.title,
                "data": dict(p.data),
                "unique_id": None,
            }
            for p in WELCOME[:4]
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert (entry.version, entry.minor_version) == (3, 2)
    data = {s.title: dict(s.data) for s in entry.subentries.values()}
    assert data["Night quiet"]["not_tags"] == ["digest"]
    assert data["Critical"]["type"] == "get_through"
    assert "policy_mode" not in entry.options and "policy_order" not in entry.options
    assert entry.options["conversion_items"] == [
        {"policy": "night", "kind": "not_for", "state": "open", "added": {"not_tags": ["digest"]}}
    ]


async def test_the_mode_and_order_commands_are_gone(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    for command in ("heads_up/policy_mode_set", "heads_up/policy_order_set"):
        await client.send_json_auto_id({"type": command, "mode": "all", "order": []})
        reply = await client.receive_json()
        assert reply["error"]["code"] == "unknown_command"


async def test_the_check_list_keeps_or_lets_a_converted_policy_act(
    hass: HomeAssistant, hass_ws_client: WebSocketGenerator
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        minor_version=4,
        options={"policy_mode": "first", "policy_order": ["eve", "night"]},
        subentries_data=[
            {
                "subentry_id": p.subentry_id,
                "subentry_type": "policy",
                "title": p.title,
                "data": dict(p.data),
                "unique_id": None,
            }
            for p in WELCOME[2:4]
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/panel_config"})
    assert (await client.receive_json())["result"]["conversion_items"] == [
        {"policy": "night", "kind": "not_for", "state": "open", "added": {"not_tags": ["digest"]}}
    ]
    await client.send_json_auto_id(
        {
            "type": "heads_up/conversion_item",
            "policy": "night",
            "kind": "not_for",
            "choice": "change",
        }
    )
    reply = await client.receive_json()
    assert reply["result"]["items"][0]["state"] == "changed"
    assert "not_tags" not in entry.subentries["night"].data
    await client.send_json_auto_id({"type": "heads_up/conversion_items_dismiss"})
    await client.receive_json()
    assert "conversion_items" not in entry.options
