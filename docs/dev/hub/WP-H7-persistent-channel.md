# H7: Persistent notification channel

Size: small. Status: built on branch `hub/h7-persistent` (see `ROADMAP.md`). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Mirror messages to Home Assistant's notification bell.

## Dependencies and parallel work
- Needs: H1
- Can run at the same time as: all
- Files this package owns (create): `hub/channels/persistent.py`, `tests/hub/test_persistent_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `strings.json`, `translations/*.json`, `docs/actions.md`

## Scope
- `persistent_notification.create` and `dismiss` with `notification_id` derived from the message id (`hu_<id>`); update replaces; resolve dismisses. It targets everyone and takes no target (D-082, D-090, N-67). Never list `persistent_notification` in the manifest dependencies (hassfest rejects it).
- Opt-in per call or policy; no warning or validation about visibility (maintainer decision 25). A dismissal in the bell is not reported back.

## Out of scope
Per-user bell entries (not possible).

## Tests
Create, update, dismiss on every hide reason; id derivation; restart (stale entries dismissed); hub off.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md`, CHANGELOG, STATE.

## Parity (CLAUDE.md rule 9)
Policy driven for rules.

## Blast radius (rule 5)
Notification path: touched (persistent notification of Home Assistant core).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-67. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Channel built and tested; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
