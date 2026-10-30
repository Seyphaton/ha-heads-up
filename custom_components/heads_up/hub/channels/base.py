"""Channel protocol (DESIGN §23.10)."""

from __future__ import annotations

from dataclasses import dataclass
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
class Outcome:
    result: Result
    reason: str | None = None
    ref: str | None = None  # push tag or notification id, kept in the ledger


class Channel(Protocol):
    name: str
    available: bool  # False for a placeholder whose package is not built yet
    capabilities: Capabilities

    async def deliver(self, message: Banner, recipient: str) -> Outcome: ...
    async def update(self, message: Banner, recipient: str) -> Outcome: ...
    async def clear(self, message: Banner, recipient: str) -> Outcome: ...
