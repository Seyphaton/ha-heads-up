# Dev environment

## Python (tests, lint)
- Python 3.14 via `uv` (HA 2026.9.4 requires `>=3.14.2`, N-23).
- `make setup` creates `.venv/` from `pyproject.toml` + `uv.lock`.
- `home-assistant-frontend==20260826.7` is a dev dependency because the manifest depends on `frontend`; without it the `frontend` component fails to set up in tests (`No module named 'hass_frontend'`, N-26).

## Local Home Assistant (Docker)
- Requires Docker. Not started once yet, so the steps below are unverified.
- `make dev-up` starts `homeassistant/home-assistant:2026.9.4` as container `heads-up-dev`.
- URL: http://127.0.0.1:8124 (loopback only).
- Config: `dev/ha-config/configuration.yaml` (committed). Runtime state (`.storage`, DB, logs) is gitignored.
- The integration is mounted read-only from `custom_components/heads_up`. After a code change: `docker restart heads-up-dev`.
- Test entities: `input_boolean.test_window`, `input_boolean.test_leak`, `input_select.test_mode`.
- Test users: created in onboarding on first start: one admin (`dev-admin`), one non-admin (`dev-user`), each with a person entity. Credentials exist only in the dev instance's gitignored `.storage`.
- `make dev-reset` deletes runtime state; next start runs onboarding again.
- `make dev-logs` follows the container log.
