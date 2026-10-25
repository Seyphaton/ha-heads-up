# State

Updated 2026-10-25. Read this first in a new session, then `docs/DESIGN.md` §0 and §8. Start each phase session with the prompt in `docs/dev/PHASE_PROMPT.md`; its documentation checklist is the definition of done.

## Where we are
- Phases 0–7 delivered, except the release itself. Phases 0–6 are committed. Phase 7 (card design, D-048, D-049) is in the working tree, **not committed**.
- The first release is the maintainer's call (D-020): nothing is pushed, tagged or published, and there is no remote.
- No further phase is planned. Remaining work: "Before the first release" in `docs/dev/RELEASE.md` and `docs/OPEN_QUESTIONS.md`.

## Verified state
- `make check`: 85 pytest, 62 vitest, ruff, mypy strict, docs-check (11 YAML examples, card option parity for 17 options). `make hassfest` and `make dev-smoke` pass.
- Phase 7 on the dev HA 2026.9.4 (browser pane, admin, dashboard `hu-test`, view `design` with six cards): compact one-liners, time text and its 30 s refresh, title, `show_severity` default off, `colorize` and `colors`, clear all, collapsed items, swipe with a mouse (and cancel on a short drag, no tap action), empty message, editor fields with defaults and nested colors. The same 80 tests as before pass on HA 2026.10.4 (not re-run for Phase 7).
- Not verified: swipe on a touch screen (R-10), keyboard activation, screen readers, compact layout at phone width, `show_all` rendering with another person's banner, the editor inside HA's own card dialog (checked as a floating element), CI (never run), mypy and the dev HA on 2026.10, UI wording in README and troubleshooting (Settings > Devices & services, Configure, Delete), an unlisted custom repository with the domain `heads_up`.

## Before starting work
1. `make setup` (uv, Python 3.14). Node 22 for `make test-card`.
2. Docker Desktop must run. If `docker` is not found: `export PATH="$HOME/.docker/bin:$PATH"`.
3. `make dev-up` (creates empty `automations.yaml` and `scripts.yaml`). Dev HA state lives in `dev/ha-config/` (gitignored), credentials in `dev/dev-credentials.env`. The dev HA holds the `hu-test` dashboard with views from Phases 4–7; `make dev-reset` + `make dev-onboard` gives a clean instance.
4. `make check` green before and after each change.

## If the maintainer approves a release
Follow `docs/dev/RELEASE.md`, "Before the first release". Needs the maintainer: repository creation and remote, push, screenshots (the card now has more looks worth showing), the first version number, HACS steps for the README.

## Open items
`docs/OPEN_QUESTIONS.md`.
