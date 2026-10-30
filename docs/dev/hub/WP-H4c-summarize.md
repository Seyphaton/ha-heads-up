# H4c: Summarize policy

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Add the Summarize type: hold matching messages on every channel and send one summary per recipient and channel.

## Dependencies and parallel work
- Needs: H4a, H1 ledger
- Can run at the same time as: H4b, H3, H5, H6, H7
- Files this package owns (create): `hub/policies/summarize.py`, `tests/hub/test_policy_summarize.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `config_flow.py` (type fields), `hub/engine.py` (hold stage), `hub/ledger.py`, `strings.json`, `translations/*.json`, `manager.py` visibility (held banner)

## Scope
- Hold: messages the policy applies to are held on every channel including the banner (D-105); the banner is not shown, `visible()` respects the hold; critical messages are held only if `include_critical` is set (default off; the form warns).
- Timing: `every` N minutes or `at` a time of day (local time); a timer per policy persisted in the ledger; nothing is sent when nothing was collected.
- Summary message: a new message created by the hub with its own id; severity is the highest of its messages; channels and targets are those the held messages would have used, one summary per recipient and channel listing the messages meant for that recipient; content: count and titles, resolved ones marked, cut at 10 with 'and N more'; stays until dismissed or 24 hours; passes through quiet hours, away and fallback like any delivery (D-106).
- A held message that is cleared before the summary appears in it as resolved; a message acknowledged or dismissed by a recipient before the summary is still listed unless cleared for that recipient (decide and document).
- The Overview 'in a summary' state is derived from the hold; the transition seam reports held and released.

## Out of scope
Panel forms (H9c); a digest that merges several policies' summaries.

## Tests
Collection per recipient and channel; highest severity; cut at 10; resolved marking; every N minutes and at a time with the freezer; nothing collected sends nothing; critical excluded or included; banner held; restart between hold and summary; summary through quiet hours; summary lifetime 24 hours.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md`, CHANGELOG, DESIGN 23.6 if details change, TESTING, STATE.

## Parity (CLAUDE.md rule 9)
Both message sources, tested; rule messages are held like any other.

## Blast radius (rule 5)
Dashboard: a held message is not visible until the summary (only for users who create a Summarize policy).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Handling of acknowledged or dismissed messages in a summary. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None new. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Summarize built and tested; `make check`, `make hassfest`, `make dev-smoke` green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
