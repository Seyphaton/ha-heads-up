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
0. Design (done) · 1. Scaffold + dev env (done) · 2. Backend core (done) · 3. Conditions + people (done) · 4. Card (done) · 5. External call paths + examples (done) · 6. Hardening, docs, packaging, release (done except release) · 7. Card design (done) · 8. Watch rules (done) · 9. Condition operators (done) · 10. Condition `for` + template conditions (done) · 11. `empty`/`not_empty` operators + rule form State (done) · 12. Banner buttons + snooze (done, released in 0.4.0).
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
- `docs/dev/` — PHASE_PROMPT, STATE, HA_API_NOTES, DEV_ENVIRONMENT, TESTING, RELEASE
- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/*.md` user pages — human docs

## Docs rules
Two audiences, never mixed. Full rules: `.claude/rules/docs-style.md` (loads for Markdown files).
