# State

Updated 2026-10-25. Read this first in a new session, then `docs/DESIGN.md` §0 and §8. Start each phase session with the prompt in `docs/dev/PHASE_PROMPT.md`; its documentation checklist is the definition of done.

## Where we are
- Phases 0–5 delivered (gate log: end of `docs/DECISIONS.md`). Phases 0–4 are committed. Phase 5 is in the working tree, **not committed** (docs, dev config, Makefile).
- Phase 6 (hardening, docs, packaging, release) is **not approved yet**. Ask the maintainer for explicit approval before starting it.
- Nothing pushed or published (D-020). No git remote configured.

## Verified state
- `make check` green: 76 pytest, 21 vitest, ruff, mypy strict, docs-check (10 YAML examples, card option parity). `make hassfest` and `make dev-smoke` passed after Phase 4; `make dev-smoke` passed again after Phase 5.
- Phase 5 on the dev HA 2026.9.4: REST and WebSocket calls (N-43); the three YAML examples of `docs/examples.md` ran as automation, script and banner (N-44); `perform-action` with `confirmation` runs after OK, not before.
- Not verified: `show_all` rendering in the card with a banner for another person; the editor's visual appearance; keyboard activation; screen readers; N-42 (one failed first load after a restart); corrupt storage file (DESIGN §10); domain collision on the HACS default list (N-22).

## Before starting work
1. `make setup` (uv, Python 3.14). Node 22 for `make test-card`.
2. Docker Desktop must run. If `docker` is not found: `export PATH="$HOME/.docker/bin:$PATH"`.
3. `make dev-up` (also creates empty `automations.yaml` and `scripts.yaml`). Dev HA state lives in `dev/ha-config/` (gitignored), credentials in `dev/dev-credentials.env`. The dev HA holds a `hu-test` dashboard from the Phase 4 checks; `make dev-reset` + `make dev-onboard` gives a clean instance.
4. `make check` green before and after each change.

## Phase 6 plan (hardening, docs, packaging, release), once approved
- Hardening: test the corrupt-storage case and decide behaviour; repeat the N-42 restart test; re-check N-14 and `show_all` rendering; keyboard and editor checks in the browser.
- Human docs still missing: README (intro, install via HACS, restart warning, quick start, screenshots: light, dark, GIF), `troubleshooting.md`, `limitations.md`, `uninstall.md`, `upgrading.md`.
- Packaging: `brand/icon.png`, `hacs.json` check against the HACS action, manifest version, `RELEASE.md` runbook, CI matrix adding HA 2026.10.x, domain collision check (N-22).
- Release only on the maintainer's explicit approval (D-020): remote, push, tag, GitHub release.

## Open items
`docs/OPEN_QUESTIONS.md`.
