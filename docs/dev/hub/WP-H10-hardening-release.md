# H10: Hardening, documentation, 2026.10 and release preparation

Size: large, last. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Make the hub safe to ship: enforce the limits, harden restarts, run the end-to-end checks, move the dev instance to Home Assistant 2026.10, finish the documentation and prepare the release (release steps stay the maintainer's).

## Dependencies and parallel work
- Needs: all other packages
- Can run at the same time as: none
- Files this package owns (create): `hub/limits.py`, `tests/hub/test_e2e_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): everything for fixes; `README.md`, `docs/*.md`, `CHANGELOG.md`, `manifest.json` version, `dev/` (2026.10), `pyproject.toml` (mypy and test pins), `docs/dev/RELEASE.md`

## Scope
- Rate limits: per device and global caps per minute and duplicate suppression from the options (proposed defaults 10, 60, 30 seconds); suppressed counts in the trace; tests with the freezer.
- Restart hardening: reconciliation (clear pushes and persistent entries of messages that no longer exist, never re-send, fire overdue escalations and reminders once, release held deliveries), corrupt store handling, downgrade check for unknown subentry types.
- End to end: `dev/smoke.py` phases with stub services covering notify, push, escalation with acknowledgement, quiet hours, summary and a container restart; panel check in the browser pane (admin, phone width, keyboard, dark theme).
- Move the dev instance and mypy to Home Assistant 2026.10 (the code must run on 2026.9.4 and 2026.10); run the hub tests on both.
- Documentation: README sales pitch from the approved text in `docs/dev/HUB_DESIGN.md` (problem statement, vocabulary, journeys; neutral wording, no product names), `docs/how-to.md`, `docs/actions.md`, `docs/limitations.md`, `docs/upgrading.md`, `docs/troubleshooting.md`, `docs/uninstall.md`; CHANGELOG; the amendment of the 'no push delivery' non-goal in DESIGN section 1 and in the README.
- Release preparation per `docs/dev/RELEASE.md`: version, changelog, README status; the tag, the GitHub release and any push stay the maintainer's step (D-020).

## Out of scope
A produced video; native-speaker review of translations; repository settings.

## Tests
The e2e suite; the full existing suite on both Home Assistant versions; `make hassfest`; `make dev-smoke`.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
All of the above; STATE; CLAUDE.md phase line.

## Parity (CLAUDE.md rule 9)
Final audit of DESIGN 22.2 rows for the hub.

## Blast radius (rule 5)
Restart: the usual one. Everything of the hub is now visible to users who enable it.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Release version number; wording of the non-goal amendment. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-74 on a real 2026.10 dev instance. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
All gates green on both versions; docs complete; release prepared (not published); STATE updated; summary to the maintainer.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
