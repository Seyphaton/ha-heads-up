# H9b: Panel: Overview and Messages

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the dashboard-like Overview and the Messages page (recent messages and the delivery trace).

## Dependencies and parallel work
- Needs: H9a, H1, H4a (states escalating, reminding)
- Can run at the same time as: H9c, H9d, H9e, H9f
- Files this package owns (create): `frontend/panel/overview.js`, `frontend/panel/messages.js`, `hub/panel_data.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `websocket.py` (commands for counts, the log, messages, trace), `strings.json`, `translations/*.json`

## Scope
- Overview per UX_SPEC: active notifications tile with states (escalating, reminding, snoozed, in a summary) and a drill-down list, watch rules tile (enabled out of all, disabled, showing now) with list, needs attention list with fix links, last actions log.
- Needs attention checks: unavailable rule entity, missing notify service for a device, person without a usable device, empty recipient group, invalid policy, policy naming a deleted audience, no escalation for critical, hub off. Each is a pure function with a test.
- Messages page: recent messages with outcome, and the delivery trace of a selected message (recipient, channel, result with reason, acknowledgements, escalation due times); decide whether the list survives a restart (stored or ring buffer).
- Log of last actions: kinds as listed in UX_SPEC; size from the History setting.

## Out of scope
Editors; Test send.

## Tests
Each needs-attention check; counts and states from fake ledger data; log ordering and bounds; admin-only commands; vitest for formatters.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, UX_SPEC if changed, STATE.

## Parity (CLAUDE.md rule 9)
Reads both message sources, tested.

## Blast radius (rule 5)
None beyond H9a.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Whether recent messages survive a restart; log size defaults. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Both pages built and tested; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
