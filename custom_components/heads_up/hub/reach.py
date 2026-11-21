"""The table "What would a message do right now?" (D-244, plan 18.2).

Every cell comes from the real engine: one dry-run message per severity, addressed to the people of
the Everyone audience (speech: to every speaker), goes through the same planning and the same
precedence chain as a real delivery (`HubEngine.preview`). Nothing is sent or stored. What the
preview cannot know before sending (popup style off, a person without a user, mail without a
service) is read from the same settings the channels read.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..const import CHANNEL_BANNER, CHANNELS, OPT_MAIL_SERVICE, SEVERITIES
from .channels.popup import PopupChannel
from .channels.speak import SpeakChannel
from .panel_test import banner_from
from .policies import quiet
from .presence import is_home
from .recipients import speaker_entities

if TYPE_CHECKING:
    from .engine import HubEngine

EVERYONE = "everyone"
SPEAK = "speak"
# What a cell can say, loudest first: a person reached by two rows counts for the louder one.
STATES = ("sound", "shown", "quiet", "held", "skipped", "not_set_up")
_RANK = {state: len(STATES) - i for i, state in enumerate(STATES)}
# Columns of the table, most urgent first.
SEVERITY_ORDER = tuple(reversed(SEVERITIES))


def _person(row: dict[str, Any]) -> str | None:
    """The person behind a row; a device row without one is a detail of a person's own row."""
    if row.get("person"):
        return str(row["person"])
    recipient = str(row.get("recipient") or "")
    return recipient if recipient.startswith("person.") else None


def cell_of(
    hub: HubEngine, options: Mapping[str, Any], channel: str, severity: str, row: dict[str, Any]
) -> tuple[str, str | None]:
    """One row of the preview as a state and the reason behind it."""
    result, reason = row["result"], row.get("reason")
    if channel == "mail" and not options.get(OPT_MAIL_SERVICE):
        return "not_set_up", "no_mail_service"
    if result == "held":
        return "held", reason
    if result != "sent":
        return ("not_set_up" if reason == "channel_unavailable" else "skipped"), reason
    quiet_now = row.get("note") == "quiet"
    if channel == "push":
        if row.get("push_level") == "critical":
            return "sound", None
        return ("quiet", "quiet_hours") if quiet_now else ("shown", None)
    if channel == "popup":
        if cast(PopupChannel, hub.channels.get("popup")).styles().get(severity) == "off":
            return "not_set_up", "popup_off"
        person = row.get("person")
        if not person or hub.resolver.user_of_person(person) is None:
            return "skipped", "no_user"
        return ("quiet", "quiet_hours") if quiet_now else ("shown", None)
    if channel == SPEAK:
        # A media player needs a text-to-speech engine; a satellite announces by itself.
        engine = cast(SpeakChannel, hub.channels.get(SPEAK)).tts_entity()
        if engine is None and str(row.get("recipient", "")).startswith("media_player."):
            return "not_set_up", "no_tts_engine"
        return ("skipped", "quiet_hours") if quiet_now else ("sound", None)
    return "shown", None


def _cell(
    hass: HomeAssistant,
    hub: HubEngine,
    options: Mapping[str, Any],
    channel: str,
    severity: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    who: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["channel"] != channel:
            continue
        key = row["recipient"] if channel == SPEAK else _person(row)
        if key is None or not key:
            continue
        state, reason = cell_of(hub, options, channel, severity, row)
        found = who.get(key)
        if found is None or _RANK[state] > _RANK[found["state"]]:
            who[key] = {"key": key, "state": state, "reason": reason, "until": row.get("until")}
    if channel in (CHANNEL_BANNER, "persistent"):
        # No target: the message goes to everyone who has the dashboard or the bell.
        first: dict[str, Any] | None = next((r for r in rows if r["channel"] == channel), None)
        state, reason = (
            cell_of(hub, options, channel, severity, first) if first else ("skipped", None)
        )
        return {
            "state": state,
            "reason": reason,
            "count": 1,
            "total": 1,
            "counts": {state: 1},
            "who": [],
        }
    entries = list(who.values())
    for entry in entries:
        state_ = hass.states.get(entry["key"])
        entry["name"] = state_.attributes.get("friendly_name") if state_ else None
        entry["name"] = entry["name"] or entry["key"]
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["state"]] = counts.get(entry["state"], 0) + 1
    if not entries:
        # Nobody to reach: speech without a speaker was never set up, the rest is skipped.
        no_speaker = channel == SPEAK and not speaker_entities(hass)
        state = "not_set_up" if no_speaker else "skipped"
        reasons = [r.get("reason") for r in rows if r["channel"] == channel and r.get("reason")]
        return {
            "state": state,
            "reason": reasons[0] if reasons else "no_recipients",
            "count": 0,
            "total": 0,
            "counts": {},
            "who": [],
        }
    state = max(counts, key=lambda s: (counts[s], _RANK[s]))
    reason = next(e["reason"] for e in entries if e["state"] == state)
    return {
        "state": state,
        "reason": reason,
        "count": counts[state],
        "total": len(entries),
        "counts": counts,
        "who": sorted(entries, key=lambda e: (-_RANK[e["state"]], e["name"])),
    }


def _context(hass: HomeAssistant, hub: HubEngine, now: datetime) -> dict[str, Any]:
    """The facts the table is read against: the time, quiet hours now, who is away, summaries."""
    ends: list[datetime] = []
    names: list[str] = []
    for policy in hub.policies.all():
        if policy.type != "quiet_hours" or not policy.enabled:
            continue
        if policy.quiet_entity:
            on, end = quiet.entity_window(hass, policy.quiet_entity)
            window = end if on else None
        else:
            window = quiet.window_end(policy, dt_util.as_local(now))
        if window is not None or (policy.quiet_entity and on):
            names.append(policy.name)
            if window is not None:
                ends.append(window)
    away = sorted(
        state.attributes.get("friendly_name") or state.entity_id
        for state in hass.states.async_all("person")
        if hub.resolver.profile(state.entity_id).enabled
        and is_home(hass, state.entity_id, hub.resolver.home_entity(state.entity_id)) is False
    )
    summaries = [
        {
            "policy": p.name,
            "tags": sorted(p.tags),
            "due": hub._summary_due(p).isoformat(),
        }
        for p in hub.policies.all()
        if p.type == "summarize" and p.enabled
    ]
    return {
        "now": now.isoformat(),
        "quiet": {"policies": names, "until": max(ends).isoformat() if ends else None}
        if names
        else None,
        "away": away,
        "summaries": summaries,
    }


async def reach(hass: HomeAssistant, hub: HubEngine, options: Mapping[str, Any]) -> dict[str, Any]:
    now = dt_util.utcnow()
    speakers = speaker_entities(hass)
    targets: dict[str, dict[str, Any]] = {
        channel: {"audience": EVERYONE} for channel in ("push", "popup", "mail")
    }
    targets[SPEAK] = {"recipients": speakers}
    cells: dict[str, dict[str, Any]] = {channel: {} for channel in CHANNELS}
    for severity in SEVERITY_ORDER:
        message = await banner_from(
            hub,
            {
                "message": "What would a message do right now?",
                "severity": severity,
                "channels": list(CHANNELS),
                "to": targets,
            },
        )
        rows = (await hub.preview(message))["rows"]
        for channel in CHANNELS:
            cells[channel][severity] = _cell(hass, hub, options, channel, severity, rows)
    return {
        "severities": list(SEVERITY_ORDER),
        "channels": list(CHANNELS),
        "cells": cells,
        "context": _context(hass, hub, now),
    }
