"""The daily history store: records, 24 months, restart, damage, size (plan 19.1)."""

import random
from datetime import UTC, date, datetime
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import STATS_KEY
from custom_components.heads_up.hub.stats import StatsStore, bucket_of, median_seconds

from ..test_restart import restart

NOW = datetime(2026, 11, 21, 18, 30, tzinfo=UTC)


async def store(hass: HomeAssistant) -> StatsStore:
    await hass.config.async_set_time_zone("UTC")
    found = StatsStore(hass)
    await found.async_load()
    return found


async def test_a_created_message_counts_in_its_hour_severity_tag_and_source(
    hass: HomeAssistant,
) -> None:
    stats = await store(hass)
    stats.created(NOW, "critical", "water", "rule_abc")
    stats.created(NOW, "info", None, "action")
    day = stats.days["2026-11-21"]
    assert day["h"][18] == 2 and sum(day["h"]) == 2
    assert day["sev"] == {"critical": 1, "info": 1}
    assert day["tag"] == {"water": 1} and day["src"] == {"rule_abc": 1, "action": 1}


async def test_the_hour_follows_the_home_assistant_time_zone(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    stats = StatsStore(hass)
    stats.created(datetime(2026, 11, 21, 23, 30, tzinfo=UTC), "info", None, "action")
    assert stats.days["2026-11-22"]["h"][0] == 1  # 00:30 in Berlin, the next local day


async def test_a_day_with_a_clock_change_still_counts_every_message(hass: HomeAssistant) -> None:
    await hass.config.async_set_time_zone("Europe/Berlin")
    stats = StatsStore(hass)
    for hour in range(24):  # 2026-10-25 has 25 hours: the repeated 02:00 lands in one slot
        stats.created(
            datetime(2026, 10, 24, 22, 0, tzinfo=UTC).replace(
                hour=(22 + hour) % 24, day=24 + (22 + hour) // 24
            ),
            "info",
            None,
            "action",
        )
    assert sum(sum(d["h"]) for d in stats.days.values()) == 24


async def test_deliveries_count_per_channel_reason_person_and_policy(hass: HomeAssistant) -> None:
    stats = await store(hass)
    stats.delivery(NOW, "push", "sent", None, None, "person.anna")
    stats.delivery(NOW, "push", "held", "quiet_hours", "pol1", "person.ben")
    stats.delivery(NOW, "mail", "failed", "no_mail_service", None, None)
    stats.delivery(NOW, "push", "cleared", None, None, None)  # not an outcome: ignored
    day = stats.days["2026-11-21"]
    assert day["ch"] == {"push": {"sent": 1, "held": 1}, "mail": {"failed": 1}}
    assert day["rs"] == {"push|held|quiet_hours": 1, "mail|failed|no_mail_service": 1}
    assert day["per"] == {"person.anna": {"push|sent": 1}, "person.ben": {"push|held": 1}}
    assert day["pol"] == {"pol1": {"held": 1}}


async def test_acknowledge_and_end_times_fall_into_coarse_buckets(hass: HomeAssistant) -> None:
    stats = await store(hass)
    stats.acknowledged(NOW, "critical", 45, avoided_escalations=1)
    stats.acknowledged(NOW, "critical", 3000)
    stats.ended(NOW, "expired", 90000)
    day = stats.days["2026-11-21"]
    assert day["ack"]["critical"][bucket_of(45)] == 1 and day["avoid"] == 1
    assert sum(day["ack"]["critical"]) == 2 and day["end"] == {"expired": 1}
    assert day["te"][-1] == 1


def test_the_median_is_the_middle_of_its_bucket() -> None:
    assert median_seconds([0] * 12) is None
    hist = [0] * 12
    hist[3] = 5  # 120 to 300 s
    assert median_seconds(hist) == 210
    hist = [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    assert median_seconds(hist) == 15


async def test_the_store_keeps_24_months_and_prunes_older_days(hass: HomeAssistant) -> None:
    stats = await store(hass)
    for key in ("2024-11-21", "2024-11-01", "2024-10-31", "2023-01-01", "2026-11-21"):
        stats.days[key] = {"h": [0] * 24}
    removed = stats.prune(date(2026, 11, 21))
    assert removed == 3 and sorted(stats.days) == ["2024-11-21", "2026-11-21"]


async def test_old_days_go_when_a_new_day_starts(hass: HomeAssistant) -> None:
    stats = await store(hass)
    stats.days["2024-01-01"] = {"h": [0] * 24}
    stats.created(NOW, "info", None, "action")
    assert "2024-01-01" not in stats.days


async def test_counts_survive_a_restart(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    hub = entry.runtime_data.hub
    hub.stats.created(dt_util.utcnow(), "warning", None, "action")
    await restart(hass, entry)
    days = entry.runtime_data.hub.stats.days
    assert sum(sum(d["h"]) for d in days.values()) == 1


@pytest.mark.parametrize(
    "stored",
    [
        "not an object",
        {"days": "no"},
        {"days": {"yesterday": {"h": [0] * 24}}},
        {"days": {"2026-11-20": {"h": [1, 2]}}},
        {"days": {"2026-11-20": "x"}},
    ],
)
async def test_a_damaged_store_is_ignored_and_rebuilt_empty(
    hass: HomeAssistant, hass_storage: dict[str, Any], stored: Any
) -> None:
    hass_storage[STATS_KEY] = {"version": 1, "minor_version": 1, "key": STATS_KEY, "data": stored}
    stats = StatsStore(hass)
    await stats.async_load()
    assert stats.days == {}
    stats.created(NOW, "info", None, "action")
    assert stats.days


async def test_a_fault_while_recording_is_swallowed_and_logged_once(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    stats = await store(hass)
    stats.created(NOW, "info", None, None)  # type: ignore[arg-type]
    stats.created(NOW, "info", None, "action")
    stats.created("bad", "info", None, "action")  # type: ignore[arg-type]
    assert caplog.text.count("Recording the history failed") == 1


async def test_clear_empties_the_store_and_info_reports_size_and_range(
    hass: HomeAssistant,
) -> None:
    stats = await store(hass)
    assert stats.info() == {"days": 0, "first": None, "last": None, "bytes": 2}
    stats.created(NOW, "info", None, "action")
    info = stats.info()
    assert (
        info["days"] == 1 and info["first"] == info["last"] == "2026-11-21" and info["bytes"] > 50
    )
    await stats.async_clear()
    assert stats.days == {} and stats.info()["days"] == 0


def synthetic_year(stats: StatsStore, start: date, days: int) -> None:
    """A busy household: 200 messages a day, 5 people, 6 channels, 12 policies, 25 sources."""
    rng = random.Random(1)
    sources = [f"rule_{n:026d}" for n in range(15)] + ["action"] * 10
    policies = [f"01{n:024d}" for n in range(12)]
    people = [f"person.person_{n}" for n in range(5)]
    channels = ["banner", "push", "popup", "speak", "persistent", "mail"]
    tags = [f"tag_{n}" for n in range(30)]
    for offset in range(days):
        day = date.fromordinal(start.toordinal() + offset)
        moment = datetime(day.year, day.month, day.day, 12, tzinfo=UTC)
        for n in range(200):
            moment = moment.replace(hour=rng.randrange(24))
            severity = rng.choice(["critical", "warning", "info", "passive"])
            stats.created(moment, severity, rng.choice(tags), rng.choice(sources))
            for channel in channels:
                for person in people if channel != "banner" else [None]:
                    result = rng.choice(["sent", "sent", "sent", "held", "skipped", "failed"])
                    reason = (
                        None
                        if result == "sent"
                        else rng.choice(
                            [
                                "quiet_hours",
                                "no_usable_device",
                                "channel_not_accepted",
                                "rate_limited",
                            ]
                        )
                    )
                    policy = rng.choice(policies) if result != "sent" else None
                    stats.delivery(moment, channel, result, reason, policy, person)
            if n % 3 == 0:
                stats.acknowledged(moment, severity, rng.choice([20, 100, 400, 2000]), 1)
            stats.ended(
                moment, rng.choice(["expired", "cleared", "dismissed"]), rng.random() * 90000
            )
            for policy in rng.sample(policies, 3):
                stats.policy_action(moment, policy, rng.choice(["escalated", "reminded"]))


async def test_a_busy_household_stays_under_the_size_limit_over_730_days(
    hass: HomeAssistant,
) -> None:
    await hass.config.async_set_time_zone("UTC")
    stats = StatsStore(hass)
    stats._pruned_on = "2026-11-21"
    stats.prune = lambda *_a, **_k: 0  # type: ignore[method-assign]
    synthetic_year(stats, date(2024, 11, 22), 730)
    info = stats.info()
    print(
        f"history size: {info['bytes']} bytes for {info['days']} days "
        f"({info['bytes'] // info['days']} per day)"
    )
    assert info["days"] == 730
    assert info["bytes"] // info["days"] <= 12_000
