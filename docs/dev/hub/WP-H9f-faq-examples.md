# H9f: Panel: FAQ and Examples page

Size: small. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the FAQ and Examples page with real, tested examples.

## Dependencies and parallel work
- Needs: H9a, H1 (examples must validate)
- Can run at the same time as: H9b to H9e
- Files this package owns (create): `frontend/panel/help.js`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `strings.json`, `translations/*.json`, `scripts/docs_check.py` (validate the examples against the real schemas)

## Scope
- Six examples and eleven answers as in UX_SPEC; examples are validated by `make docs-check` against the `notify` and shortcut schemas; the same text is the source for the README sections and `docs/how-to.md` at H10.

## Out of scope
Marketing text.

## Tests
docs-check validates every example; translation parity.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, STATE.

## Parity (CLAUDE.md rule 9)
Not applicable.

## Blast radius (rule 5)
None.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Page built; examples validated by docs-check; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
