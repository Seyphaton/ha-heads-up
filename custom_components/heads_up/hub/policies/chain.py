"""Precedence chain of one delivery (D-106).

Every delivery, whether the first one, an escalation, a reminder or a summary, passes the
stages in a fixed order: Summarize, Quiet hours, Away, Fallback. A stage may let the step pass,
change it, or stop it with a reason. H4a only defines the interface; the stages that are not
built yet pass everything, and H4b and H4c replace theirs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ...models import Banner
from ..channels import Target

STAGE_ORDER = ("summarize", "quiet_hours", "away", "fallback")


@dataclass(slots=True)
class Step:
    banner: Banner
    channel: str
    target: Target
    origin: str  # message, escalation, reminder or summary


@dataclass(frozen=True, slots=True)
class Skip:
    reason: str


class Stage(Protocol):
    name: str

    def apply(self, step: Step) -> Step | Skip: ...


class PassThrough:
    def __init__(self, name: str) -> None:
        self.name = name

    def apply(self, step: Step) -> Step | Skip:
        return step


class Chain:
    def __init__(self) -> None:
        self.stages: dict[str, Stage] = {name: PassThrough(name) for name in STAGE_ORDER}

    def replace(self, stage: Stage) -> None:
        if stage.name not in self.stages:
            raise ValueError(stage.name)
        self.stages[stage.name] = stage

    def run(self, step: Step) -> Step | Skip:
        for name in STAGE_ORDER:
            result = self.stages[name].apply(step)
            if isinstance(result, Skip):
                return result
            step = result
        return step
