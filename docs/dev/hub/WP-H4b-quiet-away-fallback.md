# H4b: Quiet hours, Away and Fallback policies

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Add three policy types to the chain built in H4a.

## Dependencies and parallel work
- Needs: H4a (H2 for Away and Fallback targets)
- Can run at the same time as: H4c, H3, H5, H6, H7
- Files this package owns (create): `hub/policies/quiet.py`, `hub/policies/away.py`, `hub/policies/fallback.py`, `tests/hub/test_policy_quiet.py`, `test_policy_away.py`, `test_policy_fallback.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `config_flow.py` (type fields), `strings.json`, `translations/*.json`

## Scope
- Quiet hours: when sent between `from` and `to` (times, days, default all days, DST safe, time zone from the Home Assistant configuration); action `wait` (hold until the end), `quiet` (push passive without sound, speech skipped, popup as corner card), `drop`; setting critical passes (default on). The `quiet` marker is passed to channels in the delivery context.
- Away: when a recipient is not home at send time, hold their delivery and send on arrival while the message is active (not cleared, expired, acknowledged or dismissed); `max_wait` defaults to the message lifetime; applies to audience targets; arrival is a person state change to home.
- Fallback: trigger `no_audience` (the audience resolved to nobody), `failed` (all deliveries of the call failed or the person has no usable device), or `both`; sends on its own channels with a target per channel instead. Critical messages: a fallback exists in the sense that unknown presence notifies anyway (D-080).
- Held deliveries are stored in the ledger and survive a restart; they are released at the end of quiet hours or on arrival, once.

## Out of scope
Summarize (H4c); panel forms (H9c).

## Tests
Quiet hours boundaries, midnight crossing, days, DST day, critical passes or not, each action, restart while held; Away: person leaves and returns, message cleared meanwhile, acknowledged meanwhile, restart; Fallback: each trigger, fallback target kinds, no loop (a fallback does not trigger a fallback); chain order with Summarize stub.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md`, CHANGELOG, DESIGN 23.6/23.14 if details change, TESTING, STATE.

## Parity (CLAUDE.md rule 9)
Both message sources, tested.

## Blast radius (rule 5)
As H4a.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
DST behavior wording; the debounce (from H2). Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None new. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Three types built and tested; `make check`, `make hassfest`, `make dev-smoke` green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
