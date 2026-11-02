---
paths:
  - "custom_components/**/*.py"
---

# Backend (Home Assistant integration)

- Develop on HA 2026.10.4 (dev venv, Docker image, mypy). Code must also run on the minimum tested version 2026.9.4 (CI).
- Everything async, in the event loop. No blocking I/O; use `hass.async_add_executor_job` if unavoidable.
- Mutations of banner state are synchronous between read and write (no `await` in between), so parallel action calls cannot interleave.
- Schemas: `import probatio as vol` + `homeassistant.helpers.config_validation as cv` (HA_API_NOTES N-1, N-91): probatio type-checks on 2026.10 and runs on 2026.9.4. Assert on error codes / translation keys in tests, never on message text.
- Every non-trivial HA API use has a source: a row in `docs/dev/HA_API_NOTES.md` or a URL comment. Unverified → say so in the comment.
- Errors raised to callers: `ServiceValidationError` with `translation_domain=DOMAIN` and a key in `strings.json`; copy `strings.json` to `translations/en.json` in the same commit.
- Every listener/timer returns an unsub stored for cleanup on unload (`entry.async_on_unload`).
- Comments explain why, not what. No docstrings that repeat the function name.
