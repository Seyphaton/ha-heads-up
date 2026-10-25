# State

Updated 2026-10-25. Read this first in a new session, then `docs/DESIGN.md` §0 and §8. Start each phase session with the prompt in `docs/dev/PHASE_PROMPT.md`; its documentation checklist is the definition of done.

## Where we are
- Phases 0–6 delivered, except the release itself. Phases 0–5 are committed; Phase 6 is in the working tree unless the gate log says otherwise.
- The first release is the maintainer's call (D-020): nothing is pushed, tagged or published, and there is no remote.
- No further phase is planned. Remaining work is the "Before the first release" list in `docs/dev/RELEASE.md` and `docs/OPEN_QUESTIONS.md`.

## Verified state
- `make check`: 80 pytest, 21 vitest, ruff, mypy strict, docs-check (11 YAML examples, card option parity). `make hassfest` and `make dev-smoke` pass.
- Same 80 tests pass on HA 2026.10.4 in a throwaway venv (N-46).
- Dev HA 2026.9.4: card, call paths and examples (Phases 4–5); corrupt storage file (N-45); the card-missing window after a restart measured (N-42).
- Not verified: CI (never run); mypy and the dev HA on 2026.10; `show_all` rendering in the card; the editor's appearance; keyboard activation; screen readers; the exact UI wording used in the README and troubleshooting page (Settings > Devices & services, Configure, Delete); an unlisted custom repository with the domain `heads_up`.

## Before starting work
1. `make setup` (uv, Python 3.14). Node 22 for `make test-card`.
2. Docker Desktop must run. If `docker` is not found: `export PATH="$HOME/.docker/bin:$PATH"`.
3. `make dev-up` (creates empty `automations.yaml` and `scripts.yaml`). Dev HA state lives in `dev/ha-config/` (gitignored), credentials in `dev/dev-credentials.env`. The dev HA holds a `hu-test` dashboard from the Phase 4 checks; `make dev-reset` + `make dev-onboard` gives a clean instance.
4. `make check` green before and after each change.

## If the maintainer approves a release
Follow `docs/dev/RELEASE.md`, "Before the first release". Needs the maintainer: repository creation and remote, push, screenshots, the first version number, HACS steps for the README.

## Open items
`docs/OPEN_QUESTIONS.md`.
