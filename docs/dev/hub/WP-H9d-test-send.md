# H9d: Panel: Test send

Size: medium. Status: built on branch `hub/h9d-test-send` (see `ROADMAP.md`). Marker and no what-if time: D-120. Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the Test send page: content, the call, a simulated result per recipient and channel from the engine's dry run, the generated call, and the one real send.

## Dependencies and parallel work
- Needs: H9a, H1 (dry run), H2, H4a (policies in the result)
- Can run at the same time as: H9b, H9c, H9e, H9f
- Files this package owns (create): `frontend/panel/test_send.js`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `websocket.py` (`heads_up/hub_plan` dry run, `heads_up/hub_test_send`), `strings.json`, `translations/*.json`

## Scope
- Inputs per UX_SPEC; result table, response summary, policies applied, later steps; generated `heads_up.notify` YAML with Copy; Send test is the only real send and carries a test marker (marker decided here). No compose form for real messages (D-101).
- The backend dry run uses the same engine as real delivery so the preview cannot drift; the mockup's simulation (time, presence) maps to a 'what if' option later.

## Out of scope
Real compose form.

## Tests
Dry run equals the real plan for a matrix of calls; Send test sends exactly one real message with the marker; admin only; vitest for the YAML generator.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, UX_SPEC, STATE.

## Parity (CLAUDE.md rule 9)
Both sources in the result (rule messages shown with the policies that apply).

## Blast radius (rule 5)
One real send on demand by an admin.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
The test marker; whether a 'what if' time is offered. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Page built and tested; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
