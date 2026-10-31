"""Channel protocol (DESIGN §23.10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from ...models import Banner


class Result(StrEnum):
    SENT = "sent"
    HELD = "held"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Capabilities:
    title: bool
    buttons: bool
    clear: bool  # can take a delivered message back
    replace: bool  # an update replaces in place
    per_user: bool


@dataclass(frozen=True, slots=True)
class Target:
    """One recipient of one delivery, with the context the engine and policies add."""

    key: str  # ledger key: "" for banner and persistent, `device:<id>`, a person or an entity id
    kind: str = ""  # person, device or speaker
    person: str | None = None
    quiet: bool = False  # set by a Quiet hours policy (H4b): passive, no sound
    ack_button: bool = False  # set when an escalation or reminder policy applies (H4a)


@dataclass(frozen=True, slots=True)
class Outcome:
    result: Result
    reason: str | None = None
    ref: str | None = None  # push tag or notification id, kept in the ledger
    due: datetime | None = None  # a held delivery: release time or deadline
    hold: str | None = None  # a held delivery: why (quiet_hours, away)


class Channel(Protocol):
    name: str
    available: bool  # False for a placeholder whose package is not built yet
    capabilities: Capabilities

    async def deliver(self, message: Banner, target: Target) -> Outcome: ...
    async def update(self, message: Banner, target: Target) -> Outcome: ...
    # The message may be gone already (startup), so clearing needs only its id and the stored ref.
    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome: ...
