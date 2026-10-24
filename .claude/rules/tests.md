---
paths:
  - "tests/**"
---

# Tests

- `pytest-homeassistant-custom-component==0.13.367` = HA 2026.9.4 (HA_API_NOTES N-20). `enable_custom_integrations` is autouse in `tests/conftest.py`.
- Lifecycle semantics get tests before implementation (Phase 2): upsert, each removal reason, eviction, limits, response data, events, permissions.
- Restart safety: set up entry → mutate → unload → reload from the persisted store; use `freezer` to move time past `expires_at` across the restart.
- Time: never `sleep`; use `freezer.tick()` + `async_fire_time_changed`.
- Assert on error codes / translation keys, not message text (probatio wording, N-1).
- One behaviour per test; test name states the behaviour.
- Run one test: `make test ARGS="tests/test_x.py::test_name"`.
