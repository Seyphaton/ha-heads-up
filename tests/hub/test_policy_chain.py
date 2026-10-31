"""The precedence chain runs the stages in the fixed order of D-106."""

import pytest

from custom_components.heads_up.hub.channels import Target
from custom_components.heads_up.hub.policies.chain import STAGE_ORDER, Chain, Skip, Step

from .test_policy_matching import message


class Recorder:
    def __init__(self, name: str, log: list[str], result: Skip | None = None) -> None:
        self.name = name
        self._log = log
        self._result = result

    def apply(self, step: Step) -> Step | Skip:
        self._log.append(self.name)
        return self._result or step


def step() -> Step:
    return Step(message(), "push", Target("person.anna"), "message")


def test_the_order_is_summarize_quiet_hours_away_fallback() -> None:
    assert STAGE_ORDER == ("summarize", "quiet_hours", "away", "fallback")


def test_stubs_that_are_not_built_yet_let_a_step_pass_unchanged() -> None:
    first = step()
    assert Chain().run(first) is first


def test_stages_run_in_order_whatever_the_order_they_were_replaced_in() -> None:
    log: list[str] = []
    chain = Chain()
    for name in ("fallback", "summarize", "away", "quiet_hours"):
        chain.replace(Recorder(name, log))
    chain.run(step())
    assert log == list(STAGE_ORDER)


def test_a_stage_that_skips_stops_the_later_ones_and_gives_its_reason() -> None:
    log: list[str] = []
    chain = Chain()
    chain.replace(Recorder("quiet_hours", log, Skip("quiet_hours")))
    chain.replace(Recorder("away", log))
    result = chain.run(step())
    assert result == Skip("quiet_hours")
    assert log == ["quiet_hours"]


def test_an_unknown_stage_cannot_be_added() -> None:
    with pytest.raises(ValueError):
        Chain().replace(Recorder("other", []))
