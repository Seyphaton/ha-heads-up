# H9c: Panel: editors for audiences, recipients, policies and channel settings

Size: large. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the Configuration pages with working forms that save to the subentries and options.

## Dependencies and parallel work
- Needs: H9a, H2, H4a (and H4b, H4c for those types), H3 (Channels settings store)
- Can run at the same time as: H9b, H9d, H9e, H9f
- Files this package owns (create): `frontend/panel/audiences.js`, `recipients.js`, `policies.js`, `channels.js`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `websocket.py` (helpers for subentry flows if needed), `strings.json`, `translations/*.json`

## Scope
- Audiences, Recipients (profiles and groups), Policies (all six types as in UX_SPEC), Channels (settings by severity). Forms use `ha-form` and the subentry flow APIs (N-57, N-58); a plain-sentence description and the stored YAML under each editor; problems listed before Save is enabled; delete refused while in use.
- Per-channel target blocks shared by Escalation and Fallback and Test send (one component), following DESIGN 23.5.
- Watch rules are not edited here (D-100).

## Out of scope
Overview, Messages, Test send, wizard.

## Tests
Pure form logic in vitest (validation, target normalization, sentences); flow round trips against the dev instance in `dev/smoke.py`; translation parity.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, UX_SPEC if changed, STATE.

## Parity (CLAUDE.md rule 9)
Not a banner feature; policies apply to both sources.

## Blast radius (rule 5)
None beyond H9a.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-57, N-58 on the dev instance. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
All four editors built and tested; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
