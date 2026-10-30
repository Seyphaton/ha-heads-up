# Session prompts for the hub work packages

Paste the generic prompt into a new Claude Code session started in this repository (best in its own git worktree), replacing `<ID>` with a package id from `ROADMAP.md` and `<FILE>` with its brief. The brief holds everything specific to the package.

## Generic prompt

You are continuing Heads Up (`heads_up`), a standalone Home Assistant custom integration with the Lovelace card `custom:heads-up-card`. Work on hub work package **<ID>** only: `docs/dev/hub/<FILE>`.

Read in this order before anything else: `CLAUDE.md`, `docs/dev/STATE.md` (end of file), `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, `docs/dev/hub/<FILE>`, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/PHASE_PROMPT.md`, and the `docs/dev/HA_API_NOTES.md` rows named in the brief. The mockup `docs/dev/mockups/hub-panel-mockup.html` shows the intended panel behavior with sample data.

Rules (from CLAUDE.md, they matter most):
- One package per approval; no work beyond it. Nothing is pushed, merged or tagged without explicit approval. Work on branch `hub/<id>` created from the branch named in the roadmap.
- Parity (rule 9): every banner feature works for action messages and rule messages, or the gap is a listed exception with a decision number in DESIGN 22.2 (D-100 covers hub delivery for rules).
- Work only against unit tests and the local dev instance (`make dev-up`, http://127.0.0.1:8124; Docker needs `export PATH="$HOME/.docker/bin:$PATH"`). Never touch another Home Assistant instance. The dev instance has no real devices; use the stubs from H0a.
- Tracked files stay installation-independent and in English. Nothing about other products in any tracked file, commit message, comment or test. Decisions go to `docs/DECISIONS.md` immediately; out-of-scope ideas to `docs/OPEN_QUESTIONS.md`.
- Use AskUserQuestion for decisions (recommended first), core tools only. The maintainer may read on a phone: put anything a decision needs in a short file and send it with SendUserFile; avoid tables in chat.
- If the current decisions conflict with an older line anywhere, `docs/dev/hub/DECISION_INDEX.md` wins.

First step: run `make check` and report anything red. Then ask the maintainer, with AskUserQuestion, the open items listed under "Ask the maintainer first" in the brief. Then present a plan for this package only and wait for explicit approval. Then build in small commits (one logical change each, tests first for behavior), run `make check`, `make hassfest` and `make dev-smoke`, complete the documentation checklist of `docs/dev/PHASE_PROMPT.md`, update `docs/dev/STATE.md`, `docs/dev/hub/ROADMAP.md` (status of this package) and CLAUDE.md if commands or layout changed. End with a summary (done, decided, open, next) and stop. Commit locally; push only if the maintainer says so.

## Package prompts
Use the generic prompt with these values.
- H0a: `WP-H0a-test-scaffolding.md`
- H0b: `WP-H0b-verify-ha-facts.md`
- H1: `WP-H1-core.md` (needs H0a merged; branch from `design/notification-hub`)
- H2: `WP-H2-audiences-recipients.md` (needs H1)
- H3: `WP-H3-push-channel.md` (needs H1 and H2)
- H4a: `WP-H4a-policy-framework.md` (needs H1)
- H4b: `WP-H4b-quiet-away-fallback.md` (needs H4a)
- H4c: `WP-H4c-summarize.md` (needs H4a)
- H5: `WP-H5-speak-channel.md` (needs H1 and H2)
- H6: `WP-H6-popup-channel.md` (needs H1)
- H7: `WP-H7-persistent-channel.md` (needs H1)
- H8: `WP-H8-card-acknowledgement.md` (needs H1 and H4a)
- H9a: `WP-H9a-panel-shell.md` (needs H1)
- H9b: `WP-H9b-overview-messages.md` (needs H9a, H1, H4a)
- H9c: `WP-H9c-editors.md` (needs H9a, H2, H4a, H3)
- H9d: `WP-H9d-test-send.md` (needs H9a, H1, H2, H4a)
- H9e: `WP-H9e-wizard.md` (needs H9a, H2, H4a)
- H9f: `WP-H9f-faq-examples.md` (needs H9a, H1)
- H10: `WP-H10-hardening-release.md` (needs everything)

## Parallel sessions
When two packages run at the same time, give each its own worktree (`git worktree add ../hub-<id> -b hub/<id> <base branch>`), tell it which files the other package owns (see "Files this package owns" in the briefs), and remind it to keep edits to shared files (`strings.json`, translations, `config_flow.py`, `__init__.py`) in a delimited block.

## Session that only coordinates
To merge finished packages, check the graph in `ROADMAP.md`, merge in dependency order, rebase the second branch before merging, rerun `make check`, `make hassfest`, `make dev-smoke`, and update the status column. Merge only on the maintainer's explicit go.
