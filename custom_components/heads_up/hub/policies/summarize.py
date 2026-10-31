"""Summarize: hold matching messages and send one summary per recipient and channel (D-105, D-113).

This module has the pure parts: when the next summary is due and what it says. The engine holds
the messages and sends the summaries.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from ...const import SEVERITIES, SUMMARY_MAX_LISTED
from ..ledger import HeldMessage
from .models import Policy

TEXT: dict[str, dict[str, str]] = {
    "title_one": {
        "en": "Summary: 1 message",
        "de": "Zusammenfassung: 1 Meldung",
        "fr": "Résumé : 1 message",
        "es": "Resumen: 1 mensaje",
    },
    "title_many": {
        "en": "Summary: {n} messages",
        "de": "Zusammenfassung: {n} Meldungen",
        "fr": "Résumé : {n} messages",
        "es": "Resumen: {n} mensajes",
    },
    "resolved": {"en": "(resolved)", "de": "(erledigt)", "fr": "(résolu)", "es": "(resuelto)"},
    "more": {
        "en": "and {n} more",
        "de": "und {n} weitere",
        "fr": "et {n} autres",
        "es": "y {n} más",
    },
}
MAX_LINE = 80


def _text(key: str, language: str) -> str:
    table = TEXT[key]
    return table.get(language, table["en"])


def holds(policy: Policy, severity: str) -> bool:
    """Critical messages are held only when the policy says so (D-097)."""
    return policy.include_critical or severity != "critical"


def next_due(policy: Policy, now: datetime) -> datetime:
    """When the next summary is due: `summary_every` minutes from now, or the next occurrence of
    `summary_at` on the local clock."""
    if policy.summary_at:
        at = dt_util.parse_time(policy.summary_at)
        assert at is not None
        local = dt_util.as_local(now)
        day = local.date()
        due = datetime.combine(day, at, tzinfo=local.tzinfo)
        if due <= local:
            due = datetime.combine(day + timedelta(days=1), at, tzinfo=local.tzinfo)
        return dt_util.as_utc(due)
    return now + timedelta(minutes=policy.summary_every)


def highest(severities: list[str]) -> str:
    return max(severities, key=SEVERITIES.index)


def build(entries: list[HeldMessage], language: str) -> tuple[str, str, str]:
    """Title, text and severity of one summary: a count, then the messages, resolved ones marked,
    cut at ten."""
    ordered = sorted(entries, key=lambda e: e.held_at)
    n = len(ordered)
    title = _text("title_one", language) if n == 1 else _text("title_many", language).format(n=n)
    lines = []
    for entry in ordered[:SUMMARY_MAX_LISTED]:
        shown = (entry.title or entry.message).strip()
        if len(shown) > MAX_LINE:
            shown = shown[: MAX_LINE - 1] + "…"
        mark = f" {_text('resolved', language)}" if entry.resolved else ""
        lines.append(f"• {shown}{mark}")
    if n > SUMMARY_MAX_LISTED:
        lines.append(_text("more", language).format(n=n - SUMMARY_MAX_LISTED))
    return title, "\n".join(lines), highest([e.severity for e in ordered])


def check(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if data.get("summary_at"):
        if dt_util.parse_time(str(data["summary_at"])) is None:
            errors["summary_at"] = "time_invalid"
    elif int(data.get("summary_every") or 0) < 1:
        errors["summary_every"] = "every_required"
    return errors


__all__ = ["TEXT", "build", "check", "highest", "holds", "next_due", "time"]
