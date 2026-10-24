# CLAUDE.md

Heads Up (`heads_up`): custom Home Assistant integration + one Lovelace card (`custom:heads-up-card`). Automations call actions (`create_banner`, `clear_banner`, `clear_all`); the card shows banners until dismissed, condition false, or timeout.
Standalone: no knowledge of any caller. Code, comments, docs in English; end-user UI strings in en + de.

## Hard rules
1. One phase per approval. No work beyond the approved phase.
2. Development and tests run only against unit tests and the local dev instance (`make dev-up`). Never connect to any other Home Assistant instance (D-003).
3. Purely additive: the integration never modifies other integrations, automations or scripts.
4. Verify HA APIs against current docs/source; record in `docs/dev/HA_API_NOTES.md` or a URL comment. Unsure → say so.
5. Flag blast radius: restart needed, notification path touched, changes what a dashboard shows.
6. Tracked files stay installation-independent: no hosts, addresses, device names, household details or tool configuration (D-036). Local-only material goes to `.private/` or `.claude/local/` (gitignored).
7. Nothing is pushed or published without explicit maintainer approval (D-020).
8. Small reversible steps, one logical change per commit. Ask before anything irreversible or scope-expanding.

## Phases (one approval each)
0. Design (done) · 1. Scaffold + dev env (done, Docker steps unverified) · 2. Backend core: store, actions, dismiss, events, count sensor, WebSocket, timeout, restore · 3. Conditions + people · 4. Card · 5. External call paths + examples · 6. Hardening, docs, packaging, release.
- Read `docs/dev/STATE.md` first; update it at the end of every session.
- Decisions → `docs/DECISIONS.md` immediately. Out of scope → `docs/OPEN_QUESTIONS.md`.
- End of phase: summary (done / decided / open / next), then stop and wait.

## Commands
- `make setup` — uv venv, Python 3.14, dev deps
- `make test` (`ARGS="tests/x.py::test_y"` for one), `make lint`, `make typecheck`, `make docs-check`, `make check` (all four)
- `make hassfest` — needs Docker
- `make dev-up` / `dev-down` / `dev-reset` / `dev-logs` — local HA at http://127.0.0.1:8124 (needs Docker)

## Repo map
- `custom_components/heads_up/` — integration (runtime files only)
- `tests/` — pytest
- `dev/` — docker-compose + dev HA config
- `scripts/docs_check.py` — docs checks
- `.claude/rules/` — path-scoped rules
- `docs/DESIGN.md` (requirements + design), `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`
- `docs/dev/` — HA_API_NOTES, STATE, DEV_ENVIRONMENT, TESTING, RELEASE
- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/*.md` user pages — human docs

## Docs rules
Two audiences, never mixed. Full rules: `.claude/rules/docs-style.md` (loads for Markdown files).
