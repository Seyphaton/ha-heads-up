# State

- Phase: 2 (Backend core) — complete, waiting for review and Phase 3 approval
- Gates: Phase 0 approved 2026-10-24; Phase 1 complete and Phase 2 approved 2026-10-25
- Done in Phase 2: store + restore, `create_banner`/`clear_banner`/`clear_all` with response data, timeout via absolute `expires_at`, eviction, events, count sensor, options flow, WebSocket `heads_up/subscribe`/`dismiss`/`admin_clear`, English-only strings (D-037), `docs/actions.md`, docs-check example validation + field parity
- Verified: 49 pytest tests, ruff, mypy strict, hassfest, docs-check, `make dev-smoke` on HA 2026.9.4 (incl. container restart)
- Not in Phase 2 (Phase 3): `condition`, `mode`, `wait_for_condition`, `people`
- Not verified: CI workflow (repo not published)
- Publishing: not approved; nothing pushed (D-020)
