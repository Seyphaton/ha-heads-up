# Dev environment

## Python (tests, lint)
- Python 3.14 via `uv` (HA 2026.9.4 requires `>=3.14.2`, N-23).
- `make setup` creates `.venv/` from `pyproject.toml` + `uv.lock`.
- `home-assistant-frontend==20260826.7` is a dev dependency because the manifest depends on `frontend`; without it the `frontend` component fails to set up in tests (`No module named 'hass_frontend'`, N-26).

## Card tests (Node)
- Node 22 and npm. `package.json` holds only the dev dependency vitest 3.2.4; the card has no runtime npm dependencies (D-021). `node_modules/` is gitignored.
- `make test-card` runs `npm install` and `npx vitest run`.

## Local Home Assistant (Docker)
- Requires Docker (verified with Docker Desktop 29.9.2 on macOS arm64, 2026-10-25). The Docker Desktop CLI lives in `~/.docker/bin`; add it to `PATH` if `docker` is not found.
- `make dev-up` starts `homeassistant/home-assistant:2026.9.4` as container `heads-up-dev`.
- URL: http://127.0.0.1:8124 (loopback only).
- Config: `dev/ha-config/configuration.yaml` (committed). Runtime state (`.storage`, DB, logs) is gitignored.
- The integration is mounted read-only from `custom_components/heads_up`. After a Python change: `docker restart heads-up-dev`. The card file is read from disk on each request; reload the dashboard after editing `heads-up-card.js`.
- To try the card by hand, create a dashboard with `type: custom:heads-up-card` (admin WebSocket `lovelace/dashboards/create`, then `lovelace/config/save`) and create banners with `heads_up.create_banner`. For the browser pane, log in as a dev user and set `hassTokens` in localStorage instead of typing the password.
- Test entities: `input_boolean.test_window`, `input_boolean.test_leak`, `input_select.test_mode`.
- First start: `make dev-onboard` runs onboarding via the HA API, creates `dev-admin` (admin) and `dev-user` (non-admin), links a person to each, and adds the Heads Up entry through its config flow. Generated passwords go to `dev/dev-credentials.env` (gitignored).
- `make dev-reset` deletes runtime state; run `make dev-onboard` again after the next start.
- Only `dev/ha-config/configuration.yaml` is tracked; everything else in `dev/ha-config/` is gitignored.
- `make dev-logs` follows the container log.

## hassfest
- `make hassfest` runs `ghcr.io/home-assistant/hassfest` with `--platform linux/amd64`; the image has no arm64 variant (N-30).
