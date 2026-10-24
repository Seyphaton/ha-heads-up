# Testing

| What | How | Command |
|---|---|---|
| Integration logic | pytest + `pytest-homeassistant-custom-component` 0.13.367 (HA 2026.9.4) | `make test` |
| One test | | `make test ARGS="tests/test_config_flow.py::test_second_entry_aborts"` |
| Restart safety | unload + reload entry from persisted store; `freezer` moves time past `expires_at` | part of `make test` (from Phase 2) |
| Lint / types | ruff, mypy strict on `custom_components/heads_up` | `make lint`, `make typecheck` |
| Manifest / translations | hassfest Docker image | `make hassfest` (needs Docker) |
| Docs | banned words, placeholders; examples and field parity from Phase 2 | `make docs-check` |
| Card logic | vitest on exported pure functions | from Phase 4 |
| Card in browser | manual matrix against dev HA (sections/masonry/panel, light/dark, narrow viewport, non-admin) | from Phase 4 |

CI (`.github/workflows/ci.yml`) runs python checks, hassfest and the HACS action on push/PR. Not run yet: the repo is not on GitHub.
