# State

Updated 2026-10-25. Read this first in a new session, then `docs/DESIGN.md` §0 and §8. Start each phase session with the prompt in `docs/dev/PHASE_PROMPT.md`; its documentation checklist is the definition of done.

## Where we are
- Phases 0–4 delivered (gate log: end of `docs/DECISIONS.md`). Phase 4 (card) is waiting for the maintainer's review.
- Phase 5 (external call paths + examples) is **not approved yet**. Ask the maintainer for explicit approval before starting it.
- Nothing pushed or published (D-020). No git remote configured.
- Phase 4 is committed on `main` in three commits (card and serving; card tests, tooling and `docs/card.md`; notes and docs). Not pushed.

## Verified state
- 76 pytest tests, 21 vitest tests, ruff, mypy strict and docs-check (7 examples, card option parity) are green via `make check`.
- `make hassfest` (0 invalid integrations) and `make dev-smoke` (restarts the container) pass with the Phase 4 changes.
- On the dev HA 2026.9.4 (built-in browser, dashboard `hu-test` with sections, masonry and panel views): banners render with icon + label; dismiss; admin clear button only for admins on non-dismissible banners; tap with `navigate` and `confirmation`; empty card leaves no gap; light and dark; 1280×800 and 768×1024; `dev-user` sees no clear button; after `docker restart` the open page shows persisted and new banners without a reload (N-40, D-041).
- Not verified: `show_all` with a banner for another person; the editor's visual appearance (only its form data and `config-changed` were checked); keyboard activation; screen readers; N-42 (one "Custom element doesn't exist" after a restart, not reproduced).

## Before starting work
1. `make setup` (uv, Python 3.14). Node 22 for `make test-card`.
2. Docker Desktop must run. If `docker` is not found: `export PATH="$HOME/.docker/bin:$PATH"`.
3. `make dev-up`. Dev HA state lives in `dev/ha-config/` (gitignored), credentials in `dev/dev-credentials.env`. The dev HA currently holds a `hu-test` dashboard and a few banners from the Phase 4 checks; `make dev-reset` + `make dev-onboard` gives a clean instance.
4. `make check` green before and after each change.

## Phase 5 plan (external call paths + examples), once approved
- Read `docs/DESIGN.md` §7 (external call paths) and D-022.
- Verify on the dev HA: REST `POST /api/services/heads_up/create_banner?return_response` (already used by `dev/smoke.py`), WebSocket `call_service`, and one automation and one script calling the actions; blueprint examples only if the maintainer wants them.
- `docs/examples.md` with YAML validated by `make docs-check`; README quick start; the tap-action and `confirmation` example from `docs/card.md`.
- Ask the maintainer which example set is wanted before writing (door/window, water leak, per-person, REST).

## Open items
`docs/OPEN_QUESTIONS.md`.
