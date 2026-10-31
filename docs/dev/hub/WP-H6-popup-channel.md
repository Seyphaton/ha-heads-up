# H6: Popup channel (loader and popup)

Size: medium. Status: built on branch `hub/h6-popup` (see `ROADMAP.md`). Popups are ledger rows read through `heads_up/popup_subscribe`; decisions in D-115. Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Show popups on every dashboard for the audience a policy or call names, with a global resource under 1 KB and the popup code loaded only when needed.

## Dependencies and parallel work
- Needs: H1
- Can run at the same time as: H2, H3, H4a, H5, H7
- Files this package owns (create): `custom_components/heads_up/frontend/heads-up-loader.js`, `frontend/heads-up-popup.js`, `hub/channels/popup.py`, `tests/hub/test_popup_*.py`, `tests/card/popup.test.js`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `frontend.py` (second static path and extra JS URL with its own `HassKey`), `websocket.py` (`heads_up/popup_config`), `.claude/rules/frontend-card.md` (the 'one module' rule is amended by a decision), `strings.json`, `translations/*.json`, `docs/card.md` or a popup page

## Scope
- Loader: a second extra JS URL registered like the card (hashed, cached, `?v=<version>-<hash>`, D-050, D-064), removed on unload with its own `HassKey`, waits for the `home-assistant` element like the card (D-072); under 1 KB (a test measures the bytes); it does nothing unless the hub says popups are enabled for this user, subscribes lazily, and imports the popup module on the first matching message. Re-check on `visibilitychange` and reconnect because extra JS is missing for about 0.6 s after a start (N-42).
- Popup: corner card up to warning, centered modal for critical (settings per severity); one at a time in a queue by severity then age; buttons as in the card (message buttons, Dismiss, Snooze, Acknowledge when a policy applies); closes when the message is resolved; accessible (focus trap for the modal, Escape, 48 px targets, reduced motion); never on the login or onboarding pages; does not steal focus from an input unless critical.
- Backend: `heads_up/popup_config` (is popup enabled for this user and which severities) and delivery of popup messages through the existing subscription; persons only as recipients in the first version (D-091).
- Decision to record: amend `.claude/rules/frontend-card.md` ('one plain-JS ES module') for a loader and a popup module next to the card; the cards stay one module.

## Out of scope
Area recipients for popups; the panel (separate module in H9).

## Tests
Loader byte budget; registration and removal like `tests/test_frontend.py`; config command; popup queue, severity order, close on resolve, buttons call the right commands, modal versus card; vitest for the pure functions; restart.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/card.md` or a new popup section, `docs/troubleshooting.md`, CHANGELOG, `.claude/rules/frontend-card.md`, DESIGN 23.8, STATE.

## Parity (CLAUDE.md rule 9)
Rule messages reach popups through policies; the popup reads the same payload for both sources.

## Blast radius (rule 5)
Dashboard: popups appear on every dashboard for configured audiences. A script runs on every page for every user (under 1 KB).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Panel and popup module layout rule; how a popup knows it is on a login page. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-8, N-9, N-41, N-42, N-52. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Loader and popup built and tested; byte budget enforced; `make check`, `make hassfest`, `make dev-smoke` green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
