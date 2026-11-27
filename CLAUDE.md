# CLAUDE.md

Heads Up (`heads_up`): custom Home Assistant integration + one Lovelace card (`custom:heads-up-card`). Automations call actions (`create_banner`, `clear_banner`, `clear_all`); the card shows banners until dismissed, condition false, or timeout.
Standalone: no knowledge of any caller. Everything in English: code, comments, docs and UI strings (D-037).

## Hard rules
1. One phase per approval. No work beyond the approved phase.
2. Development and tests run only against unit tests and the local dev instance (`make dev-up`). Never connect to any other Home Assistant instance (D-003).
3. Purely additive: the integration never modifies other integrations, automations or scripts.
4. Verify HA APIs against current docs/source; record in `docs/dev/HA_API_NOTES.md` or a URL comment. Unsure → say so.
5. Flag blast radius: restart needed, notification path touched, changes what a dashboard shows.
6. Tracked files stay installation-independent: no hosts, addresses, device names, household details or tool configuration (D-036). Local-only material goes to `.private/` or `.claude/local/` (gitignored).
7. Nothing is pushed or published without explicit maintainer approval (D-020).
8. Small reversible steps, one logical change per commit. Ask before anything irreversible or scope-expanding.
9. Parity: banners from actions and from watch rules offer the same features to viewers and producers. A new banner feature ships for both in the same phase, or its absence for one source is a listed exception with a decision number in `docs/DESIGN.md` §22.

## Phases (one approval each)
0. Design (done) · 1. Scaffold + dev env (done) · 2. Backend core (done) · 3. Conditions + people (done) · 4. Card (done) · 5. External call paths + examples (done) · 6. Hardening, docs, packaging, release (done except release) · 7. Card design (done) · 8. Watch rules (done) · 9. Condition operators (done) · 10. Condition `for` + template conditions (done) · 11. `empty`/`not_empty` operators + rule form State (done) · 12. Banner buttons + snooze (done, released in 0.4.0) · 15. Notification hub (D-107): built on the branch `hub/h9e-wizard` (H0 to H10 and later changes); the branch and the pre-releases `v1.0.0-alpha.2` to `v1.0.0-alpha.8` are pushed (D-133, D-154, D-175, D-190, D-196); alpha.9 and alpha.10 are tagged and pushed, `1.0.0-beta.1` is prepared (not tagged); not merged to `main`, no 1.0.0 (maintainer: merge and tag only when told, `docs/dev/RELEASE.md`); plan in `docs/dev/hub/ROADMAP.md`. · 16. 1.1.0 features (speech volume, Presence, quiet hours and home from an entity, snooze, severities): built on `release/1.1`, not released on its own; part of 2.0.0, breaking changes allowed (D-231); DESIGN §24. · 17. 2.0.0 policies in two lanes (D-224, D-234, D-235, D-242): built on `release/2.0` (merged with `release/1.1`), done 2026-11-21; `release/2.0` and the pre-release tag `v2.0.0-beta.1` pushed (D-243), `v2.0.0-beta.2` to `v2.0.0-beta.6` pushed (D-247 to D-253); 2.0.0 released 2026-11-23 (D-254): merged to `main`, tag `v2.0.0` pushed, GitHub release published by the maintainer; DESIGN §25, checklist §25.15, release steps in `docs/dev/RELEASE.md`. · 18. Overview redesign: built and pushed (D-244, D-245, D-250, D-251, DESIGN §26; plan in `docs/dev/overview-redesign/PLAN.md`), in `2.0.0-beta.5`. · 19. Overview history store: built and pushed (D-246, DESIGN §27), in `2.0.0-beta.5`. · 20. 2.1.0 richer push: scoped 2026-11-23 (D-255, D-256, DESIGN §28), not built, waiting for phase approval. · 22. Personal inbox: built on `release/3.0` (from `main`; D-264 to D-277, DESIGN §29, plan `docs/dev/inbox/PLAN.md`): channel `inbox`, store `heads_up.inbox`, WebSocket commands, a sensor per person, the card `custom:heads-up-inbox-card`, the switch All notifications, and the channel settings of speech, push and inbox on the Channels page; approved 2026-11-24; `release/3.0` pushed, `3.0.0-beta.1` prepared (D-278), tag pushed; Phase 23 (messages between people, D-279, D-283, D-284, DESIGN §29.10): approved 2026-11-24, built on `release/3.0`; `3.0.0-beta.2` (D-288) is tagged and pushed; `release/3.0` was merged into `main` on 2026-11-24 on the maintainer's order ; 3.0.0 prepared 2026-11-25 (D-290): manifest `3.0.0`, CHANGELOG `[3.0.0]`, tag `v3.0.0` on `main` after CI.
- Read `docs/dev/STATE.md` first: current phase, gate status, setup steps, next plan. Update it at the end of every session.
- Ask decisions with the AskUserQuestion tool (options, recommended first). Use only core Claude Code tools plus read-only web for HA docs/source (D-028); no connectors or MCP servers.
- Decisions → `docs/DECISIONS.md` immediately. Out of scope → `docs/OPEN_QUESTIONS.md`.
- End of phase: summary (done / decided / open / next), then stop and wait.
- Session prompt and documentation definition of done for every phase: `docs/dev/PHASE_PROMPT.md`. A phase is not done until its checklist is complete.

## Commands
- `make setup` — uv venv, Python 3.14, dev deps
- `make test` (`ARGS="tests/x.py::test_y"` for one), `make lint`, `make typecheck`, `make docs-check`, `make test-card` (vitest, needs Node 22), `make check` (all five)
- `make hassfest` — needs Docker
- `make dev-up` / `dev-onboard` (first start) / `dev-smoke` (end-to-end, restarts the container) / `dev-down` / `dev-reset` / `dev-logs` — local HA at http://127.0.0.1:8124 (needs Docker; CLI may need `export PATH="$HOME/.docker/bin:$PATH"`)

## Repo map
- `custom_components/heads_up/` — integration (runtime files only); `frontend/heads-up-card.js` is the card
- `tests/` — pytest; `tests/card/` — vitest for the card's pure functions (`package.json` is dev-only)
- `dev/` — docker-compose + dev HA config
- `scripts/docs_check.py` — docs checks
- `.claude/rules/` — path-scoped rules
- `docs/DESIGN.md` (requirements + design), `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`
- `docs/brand/` — brand package as supplied (reference, do not edit); the integration's icons in `custom_components/heads_up/brand/` are copies from it (D-292, D-296)
- `docs/dev/` — PHASE_PROMPT, STATE, HA_API_NOTES, DEV_ENVIRONMENT, TESTING, RELEASE
- `docs/dev/hub/` — notification hub design set (README, ROADMAP, work package briefs, decision index, UI spec, test plan); `docs/dev/mockups/` — standalone panel mockup
- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/*.md` user pages — human docs

## Docs rules
Two audiences, never mixed. Full rules: `.claude/rules/docs-style.md` (loads for Markdown files).
