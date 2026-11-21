"""The Activity card's data: periods, the four numbers, the matrix, the sources (plan 19.3)."""

from datetime import UTC, date, datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub.stats import StatsReader, StatsStore

from ..test_rules import add_rule

NOW = datetime(2026, 11, 21, 18, 30, tzinfo=UTC)  # a Saturday


def day(stats: StatsStore, key: str, **fill: Any) -> None:
    stats.days[key] = {"h": [0] * 24, **fill}


async def ask(client: Any, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": "heads_up/panel_stats", **data})
    return dict(await client.receive_json())


async def test_the_command_and_the_clear_are_for_admins_only(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    assert (await ask(client))["error"]["code"] == "unauthorized"
    await client.send_json_auto_id({"type": "heads_up/stats_clear"})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"


async def test_an_unknown_period_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    assert (await ask(client, period="decade"))["error"]["code"] == "invalid_format"


def test_the_24_hour_period_has_24_hourly_buckets_split_by_severity() -> None:
    today = [0] * 24
    today[18] = 3
    today[19] = 7  # later than the current hour: not part of the last 24 hours
    yesterday = [0] * 24
    yesterday[18] = 2
    stats = {
        "2026-11-21": {
            "h": today,
            "hs": {
                "critical": [1 if h == 18 else 0 for h in range(24)],
                "info": [2 if h == 18 else 0 for h in range(24)],
            },
        },
        "2026-11-20": {"h": yesterday, "hs": {"info": [2 if h == 18 else 0 for h in range(24)]}},
    }
    result = StatsReader(stats).read("24h", NOW)
    buckets = result["buckets"]
    assert len(buckets) == 24 and buckets[-1]["total"] == 3
    assert buckets[-1]["by"] == {"critical": 1, "info": 2}
    assert result["numbers"]["notifications"] == 3
    assert result["numbers"]["previous"] == 2 and result["numbers"]["change"] == 50
    assert result["matrix"] is None


def test_week_and_month_have_daily_buckets_and_year_and_two_years_monthly_ones() -> None:
    stats = {
        "2026-11-21": {"h": [0] * 24, "sev": {"info": 5}},
        "2026-10-03": {"h": [0] * 24, "sev": {"info": 7}},
    }
    reader = StatsReader(stats)
    week = reader.read("week", NOW)
    assert len(week["buckets"]) == 7 and week["buckets"][-1]["start"] == "2026-11-21"
    assert week["numbers"]["notifications"] == 5
    assert len(reader.read("month", NOW)["buckets"]) == 30
    year = reader.read("year", NOW)
    assert len(year["buckets"]) == 12 and year["buckets"][-1]["by"] == {"info": 5}
    assert year["buckets"][-2]["by"] == {"info": 7} and year["numbers"]["notifications"] == 12
    two = reader.read("2y", NOW)
    assert len(two["buckets"]) == 24 and two["numbers"]["previous"] is None


def test_the_change_is_empty_without_a_previous_period_to_compare() -> None:
    stats = {"2026-11-21": {"h": [0] * 24, "sev": {"info": 5}}}
    assert StatsReader(stats).read("week", NOW)["numbers"]["change"] is None


def test_delivered_is_sent_divided_by_sent_plus_failed_and_ignores_held_and_skipped() -> None:
    stats = {
        "2026-11-21": {
            "h": [0] * 24,
            "ch": {"push": {"sent": 6, "held": 9, "skipped": 4}, "mail": {"sent": 2, "failed": 2}},
        }
    }
    numbers = StatsReader(stats).read("week", NOW)["numbers"]
    assert (numbers["sent"], numbers["failed"], numbers["delivered"]) == (8, 2, 80)
    assert StatsReader({}).read("week", NOW)["numbers"]["delivered"] is None


def test_the_median_time_to_acknowledge_and_the_quiet_holds_come_from_the_period() -> None:
    stats = {
        "2026-11-21": {
            "h": [0] * 24,
            "ack": {"critical": [0, 0, 0, 5] + [0] * 8, "warning": [0] * 12},
            "rs": {
                "push|held|quiet_hours": 3,
                "mail|held|quiet_hours": 1,
                "push|skipped|quiet_hours": 9,
            },
        }
    }
    numbers = StatsReader(stats).read("week", NOW)["numbers"]
    assert numbers["median_ack_seconds"] == 210 and numbers["held_quiet"] == 4
    assert StatsReader({}).read("week", NOW)["numbers"]["median_ack_seconds"] is None


def test_the_matrix_counts_messages_by_weekday_and_hour() -> None:
    saturday = [0] * 24
    saturday[9] = 4
    stats = {"2026-11-21": {"h": saturday}, "2026-11-14": {"h": saturday}}
    matrix = StatsReader(stats).read("month", NOW)["matrix"]
    assert matrix[date(2026, 11, 21).weekday()][9] == 8 and sum(map(sum, matrix)) == 8


def test_the_sources_are_sorted_by_count() -> None:
    stats = {"2026-11-21": {"h": [0] * 24, "src": {"action": 5, "rule_x": 9, "rule_y": 5}}}
    sources = StatsReader(stats).read("week", NOW)["sources"]
    assert sources == [("rule_x", 9), ("action", 5), ("rule_y", 5)]


async def test_a_rule_source_is_named_by_its_title_and_a_deleted_rule_has_no_name(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    rule = add_rule(hass, entry)
    await hass.async_block_till_done()
    hub = entry.runtime_data.hub
    today = (datetime.now(UTC)).date().isoformat()
    day(
        hub.stats,
        today,
        src={
            f"rule_{rule.subentry_id}": 4,
            "rule_gone": 2,
            "action": 1,
            "id:water_leak": 3,
            "tag:door": 2,
            "test": 1,
        },
    )
    client = await hass_ws_client(hass)
    reply = await ask(client, period="week")
    assert reply["success"], reply
    sources = {s["key"]: s for s in reply["result"]["sources"]}
    assert sources[f"rule_{rule.subentry_id}"]["name"] == rule.title
    assert sources["rule_gone"]["name"] is None and sources["rule_gone"]["kind"] == "rule"
    assert sources["action"]["kind"] == "action" and reply["result"]["info"]["days"] >= 1
    assert (sources["id:water_leak"]["kind"], sources["id:water_leak"]["name"]) == (
        "id",
        "water_leak",
    )
    assert (sources["tag:door"]["kind"], sources["tag:door"]["name"]) == ("tag", "door")
    assert sources["test"]["kind"] == "test"


async def test_clear_history_deletes_every_day_and_reports_the_empty_store(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hub = entry.runtime_data.hub
    day(hub.stats, "2026-11-20", src={"action": 1})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heads_up/stats_clear"})
    reply = await client.receive_json()
    assert reply["success"] and reply["result"]["days"] == 0
    assert hub.stats.days == {}


def test_a_period_reads_the_last_days_only() -> None:
    far = (NOW - timedelta(days=100)).date().isoformat()
    stats = {
        far: {"h": [0] * 24, "sev": {"info": 50}},
        "2026-11-21": {"h": [0] * 24, "sev": {"info": 1}},
    }
    assert StatsReader(stats).read("month", NOW)["numbers"]["notifications"] == 1
