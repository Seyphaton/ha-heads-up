# Testing

| What | How | Command |
|---|---|---|
| Integration logic | pytest + `pytest-homeassistant-custom-component` 0.13.367 (HA 2026.9.4) | `make test` |
| One test | | `make test ARGS="tests/test_config_flow.py::test_second_entry_aborts"` |
| Restart safety | unload + reload entry from persisted store; `freezer` moves time past `expires_at` | `tests/test_restart.py` |
| Real instance | `dev/smoke.py`: REST actions with response, sensor, per-user dismiss over WebSocket as `dev-admin`/`dev-user`, admin-only clear, container restart, persistence; condition on `input_boolean.test_window` + `people: [person.dev_user]` | `make dev-smoke` |
| Lint / types | ruff, mypy strict on `custom_components/heads_up` | `make lint`, `make typecheck` |
| Manifest / translations | hassfest Docker image | `make hassfest` (needs Docker) |
| Docs | banned words, placeholders; YAML examples in user docs validated against action schemas; fields: schema == services.yaml == docs/actions.md | `make docs-check` |
| Card logic | vitest on exported pure functions | from Phase 4 |
| Card in browser | manual matrix against dev HA (sections/masonry/panel, light/dark, narrow viewport, non-admin) | from Phase 4 |

CI (`.github/workflows/ci.yml`) runs python checks, hassfest and the HACS action on push/PR. Not run yet: the repo is not on GitHub.

HA logs an `ERROR ... Unauthorized` line when a non-admin calls `heads_up/admin_clear`; that is HA's `require_admin` behaviour, not a failure.
