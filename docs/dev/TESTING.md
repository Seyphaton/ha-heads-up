# Testing

| What | How | Command |
|---|---|---|
| Integration logic | pytest + `pytest-homeassistant-custom-component` 0.13.367 (HA 2026.9.4) | `make test` |
| One test | | `make test ARGS="tests/test_config_flow.py::test_second_entry_aborts"` |
| Restart safety | unload + reload entry from persisted store; `freezer` moves time past `expires_at` | `tests/test_restart.py` |
| Real instance | `dev/smoke.py`: REST actions with response, sensor, per-user dismiss over WebSocket as `dev-admin`/`dev-user`, admin-only clear, container restart, persistence; condition on `input_boolean.test_window` + `people: [person.dev_user]` | `make dev-smoke` |
| Lint / types | ruff, mypy strict on `custom_components/heads_up` | `make lint`, `make typecheck` |
| Manifest / translations | hassfest Docker image | `make hassfest` (needs Docker) |
| Docs | banned words, placeholders; YAML examples in user docs validated against action schemas; fields: schema == services.yaml == docs/actions.md; card options: `CONFIG_KEYS` == `docs/card.md` table, card examples use only those | `make docs-check` |
| Card logic | vitest 3.2.4 on the card module's exported pure functions (21 tests; needs Node 22, `npm install` runs inside the target) | `make test-card` |
| Documented examples | the YAML of `docs/examples.md` is installed on the dev HA through the config API (entity IDs swapped for `input_boolean.test_window`, `person.dev_user`), run, and the banners checked per user; REST and WebSocket calls with a dev token. Not scripted in the repo | manual, see N-43, N-44 |
| Card in browser | manual matrix against dev HA (sections/masonry/panel, light/dark, 768×1024 and 1280×800, admin and `dev-user`, dismiss, tap with confirmation, restart, empty card); results in DESIGN §11 | manual |

## Test files

| File | Covers |
|---|---|
| `tests/conftest.py` | `entry` (loaded entry, `options` fixture overridable per module), `create` (calls `create_banner` with response), `banners(entry)` |
| `tests/test_config_flow.py` | single entry, setup/unload |
| `tests/test_create.py` | defaults, all fields, timeout forms, validation, upsert, created event, `not_loaded` |
| `tests/test_clear.py` | `clear_banner` by id/tag/both, `clear_all`, cleared events |
| `tests/test_limits.py` | eviction order, critical never evicted, `too_many_banners` |
| `tests/test_restart.py` | timeout expiry, persistence across reload, expiry while down, storage removal |
| `tests/test_websocket.py` | subscribe/updates, per-user and global dismiss, errors, admin clear, `show_all`, subscription cleanup |
| `tests/test_sensor_options.py` | count sensor, options flow, cleared default timeout |
| `tests/test_conditions.py` | once/recurring, `wait_for_condition`, unavailable, removed entity, state list/attribute, restart re-evaluation, tracker release |
| `tests/test_people.py` | targeting per user, users without person, person created later, payload privacy |
| `tests/test_frontend.py` | module URL with `?v=<version>` registered, removed on unload and added on reload, file served at `/heads_up/heads-up-card.js` |
| `tests/card/heads-up-card.test.js` | `normalizeConfig`, `sortBanners`, `visibleBanners`, `controlsFor`, `retryDelay` (vitest) |

## Notes

`make check` runs lint, types, pytest, docs-check and `make test-card`. CI (`.github/workflows/ci.yml`) runs python checks, the card tests (`npm ci`, vitest), hassfest and the HACS action on push/PR. Not run yet: the repo is not on GitHub.

HA logs an `ERROR ... Unauthorized` line when a non-admin calls `heads_up/admin_clear`; that is HA's `require_admin` behaviour, not a failure.
