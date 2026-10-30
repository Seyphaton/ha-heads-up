# H4a: Policy framework, Escalation and Reminder

Size: large. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the policy subentry type, matching, the precedence chain and the timer machinery, and implement the Escalation and Reminder types with acknowledgement. Quiet hours, Away, Fallback and Summarize are separate packages that plug into the chain.

## Dependencies and parallel work
- Needs: H1 (H2 for real audiences; fakes until then)
- Can run at the same time as: H2, H3, H5, H6, H7
- Files this package owns (create): `hub/policies/__init__.py`, `hub/policies/models.py`, `hub/policies/matching.py`, `hub/policies/chain.py`, `hub/policies/escalation.py`, `hub/policies/reminder.py`, `tests/hub/test_policy_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `config_flow.py` (policy subentry flow), `hub/engine.py` (chain hooks), `hub/ledger.py` (due times), `strings.json`, `translations/*.json`, `websocket.py`, `docs/actions.md`

## Scope
- Subentry type `policy` with a typed form: name, type, applies to (severities, tags), enabled, then the type's fields (DESIGN 23.14). Types are separate modules so H4b and H4c can add theirs without touching each other.
- Matching: a policy applies when the message severity is in its severities (empty means any) and its tag is in its tags (empty means any). The call's `policy` field names one policy, omits to use all that apply, or `none`. Refuse a second policy of the same type with identical applies to and identical trigger. Rule messages have the tag `rule`.
- Precedence chain on one delivery (D-106): Summarize, Quiet hours, Away, Fallback. The chain is a list of stages with a fixed order; H4a defines the stage interface and a pass-through for the stages not built yet. Escalations, reminders and the summary are deliveries that pass through the same chain.
- Escalation: after N minutes (more than 0) without acknowledgement, deliver on the policy's channels with a target per channel (same validation as `notify`); setting: dismissing counts as acknowledging; several escalation policies form a chain by their times; due times are stored in the ledger (restart safe); an overdue step fires once after a restart if the message is active and unacknowledged.
- Reminder: while unacknowledged, repeat every N minutes up to M times; stops on acknowledgement, dismissal by everyone, snooze (per user), clear.
- Acknowledgement: manager state `acknowledged_by`; any recipient stops escalation and reminders; a WebSocket command `heads_up/acknowledge` and the transition `acknowledged` (no separate action, D-083). A severity change restarts escalation and reminders with the policies of the new severity. A snooze pauses that user's reminders and notifies again at its end. If the lifecycle condition ends the message every channel is cleared and its timers are cancelled.
- Policy usage lookup for audiences and recipient groups (so H2 and H9 can refuse deletion).
- Expose to channels whether an escalation or reminder policy applies to a message (the Acknowledge button of H3).

## Out of scope
Quiet hours, Away, Fallback, Summarize (H4b, H4c); the panel forms (H9c); the card's acknowledgement line (H8).

## Tests
Matching matrix (severity, tag, empty lists, `policy` field, `none`, rule messages); duplicate refusal; escalation timing with the freezer; chain of two escalations; acknowledgement stops both; dismiss counts or not; severity change restart; snooze pause and resume; condition end cancels timers; restart with an overdue step; ledger persistence; the chain order with stub stages.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md` (policy behavior in user words, once forms exist), CHANGELOG, DESIGN 23.6 if details change, TESTING, STATE.

## Parity (CLAUDE.md rule 9)
Policies apply to action and rule messages by severity and tag; test both sources.

## Blast radius (rule 5)
Restart: the usual one. Notification path: touched through channels only when they exist. Storage: new subentry type; ledger rows with due times.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Policy usage rules for deletion; defaults of fields (proposed in DEFAULTS_AND_PROPOSALS). Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
Subentry pattern N-57, N-58. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Policy type, matching, chain, Escalation and Reminder, acknowledgement built and tested; stages for the other types are pass-through; `make check`, `make hassfest`, `make dev-smoke` green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
