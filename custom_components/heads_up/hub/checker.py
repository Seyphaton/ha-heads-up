"""The checker "What happens to a message?" (DESIGN §25.8, D-224).

It runs the real planning and the real stages for a message that does not exist, at a chosen time
and with chosen people at home, and plans the escalations and reminders of the next 24 hours.
Nothing is stored, sent or traced. Presence and the time are assumed through `policies.clock`;
who an audience resolves to is asked as it is now.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.util import dt as dt_util

from ..const import CHANNEL_BANNER, RULE_ID_PREFIX
from .channels.base import Result
from .policies import clock, escalation
from .policies.chain import Hold, Skip, Step
from .policies.models import Policy

if TYPE_CHECKING:
    from ..models import Banner
    from .engine import HubEngine

HORIZON = timedelta(hours=24)


async def check(
    hub: HubEngine,
    message: Banner,
    at: datetime | None,
    people_home: dict[str, bool],
    ack_after: int | None,
) -> dict[str, Any]:
    start = dt_util.as_utc(at) if at is not None else dt_util.utcnow()
    message.created_at = message.updated_at = start
    with clock.assumed(start, people_home):
        first = await hub.preview(message)
    end = start + (timedelta(minutes=ack_after) if ack_after is not None else HORIZON)
    steps: list[dict[str, Any]] = []
    if first["held_for_summary"] is None:
        timed = hub.policies.timed_for(message)
        for policy in timed:
            if policy.type == "escalation":
                when = start + timedelta(minutes=policy.after_minutes)
                if when < end:
                    steps.append(await _escalation_step(hub, message, policy, when, people_home))
        sent = [
            r for r in first["rows"] if r["result"] == "sent" and r["channel"] != CHANNEL_BANNER
        ]
        steps += _reminder_steps(hub, message, timed, sent, start, end, people_home)
    steps.sort(key=lambda s: s["time"])
    band_off = [
        p.name
        for p in hub.policies.all()
        if p.type == "get_through" and not p.enabled and _would_fit(hub, p, message)
    ]
    return {**first, "steps": steps, "band_off": band_off, "at": start.isoformat()}


def _would_fit(hub: HubEngine, entry: Policy, message: Banner) -> bool:
    from .policies.matching import matches

    return entry.apply == "auto" and matches(entry, message.severity, message.tag)


async def _escalation_step(
    hub: HubEngine, message: Banner, policy: Policy, when: datetime, people_home: dict[str, bool]
) -> dict[str, Any]:
    extra = escalation.message_for(message, policy)
    rows = []
    with clock.assumed(when, people_home):
        if not hub.policies.only_if_ok(policy):
            return _step(when, policy, [], "only_if")
        for item in await hub.plan(extra):
            rows.append(
                _row(
                    hub,
                    extra,
                    item.channel,
                    item.recipient,
                    item.who,
                    item.result,
                    item.reason,
                    "escalation",
                )
            )
    return _step(when, policy, rows)


def _reminder_steps(
    hub: HubEngine,
    message: Banner,
    timed: list[Policy],
    sent: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    people_home: dict[str, bool],
) -> list[dict[str, Any]]:
    """The repeats of the next 24 hours, with the rhythm rules of the engine (one rhythm per
    channel, the shortest wins, Runs alongside keeps its own, each reminder its own count),
    the conditions as they are now."""
    reminders = [p for p in timed if p.type == "reminder" and hub.policies.only_if_ok(p)]
    if not sent or not reminders:
        return []
    every = {p.key: timedelta(minutes=hub.policies.every_minutes(p)) for p in reminders}
    due = {p.key: start + every[p.key] for p in reminders}
    count = dict.fromkeys(due, 0)
    last = start
    steps = []
    while due:
        key = min(due, key=lambda k: (due[k], k))
        when = due[key]
        if when >= end:
            break
        policy = next(p for p in reminders if p.key == key)
        if not policy.alongside:
            shorter = [
                o
                for o in reminders
                if o.key != key
                and o.key in due
                and not o.alongside
                and (every[o.key], o.key) < (every[key], key)
            ]
            if shorter:
                due[key] = when + every[key]
                continue
            if when < last + every[key]:
                due[key] = last + every[key]
                continue
            last = when
        rows = []
        with clock.assumed(when, people_home):
            for row in sent:
                if policy.channels and row["channel"] not in policy.channels:
                    continue
                rows.append(_replay(hub, message, row, "reminder"))
        steps.append(_step(when, policy, rows))
        count[key] += 1
        if count[key] >= policy.max_count:
            del due[key]
        else:
            due[key] = when + every[key]
    return steps


def _row(
    hub: HubEngine,
    message: Banner,
    channel: str,
    recipient: str,
    who: Any,
    result: Result,
    reason: str | None,
    origin: str,
) -> dict[str, Any]:
    from .channels.base import Target

    out: dict[str, Any] = {
        "channel": channel,
        "recipient": recipient,
        "person": who.person if who is not None else None,
        "result": result.value,
        "reason": reason,
        "by": None,
    }
    if result is not Result.SENT:
        return out
    target = Target(recipient) if who is None else Target(who.key, who.kind, who.person)
    return _through_chain(hub, message, channel, target, origin, out)


def _replay(hub: HubEngine, message: Banner, row: dict[str, Any], origin: str) -> dict[str, Any]:
    from .channels.base import Target

    out = {
        "channel": row["channel"],
        "recipient": row["recipient"],
        "person": row.get("person"),
        "result": "sent",
        "reason": None,
        "by": None,
    }
    target = Target(row["recipient"], "", row.get("person"))
    return _through_chain(hub, message, row["channel"], target, origin, out)


def _through_chain(
    hub: HubEngine, message: Banner, channel: str, target: Any, origin: str, out: dict[str, Any]
) -> dict[str, Any]:
    step = hub.chain.run(Step(message, channel, target, origin))
    if isinstance(step, Skip):
        return {**out, "result": "skipped", "reason": step.reason, "by": step.policy or None}
    if isinstance(step, Hold):
        until = step.until.isoformat() if step.until else None
        return {
            **out,
            "result": "held",
            "reason": step.reason,
            "by": step.policy or None,
            "until": until,
        }
    if step.target.quiet:
        return {**out, "note": "quiet", "by": step.target.quiet_by}
    return out


def _step(
    when: datetime, policy: Policy, rows: list[dict[str, Any]], skipped: str | None = None
) -> dict[str, Any]:
    return {
        "time": when.isoformat(),
        "policy": policy.name,
        "type": policy.type,
        "rows": rows,
        "skipped": skipped,
    }


def message_id_for(rule: str | None) -> str:
    """A watch-rule message has the ID of its rule, so From watch rule can fit it."""
    return f"{RULE_ID_PREFIX}{rule}" if rule else "preview"
