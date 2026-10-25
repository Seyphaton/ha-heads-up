# State

Updated 2026-10-25. Read this first in a new session, then `docs/DESIGN.md` §0 and §8.

## Where we are
- Phases 0–3 complete (gate log: end of `docs/DECISIONS.md`).
- Phase 4 (card) is **not approved yet**. Ask the maintainer for explicit approval before writing card code.
- Nothing pushed or published (D-020). No git remote configured. Working tree clean at handoff.

## Verified state
- 73 pytest tests green; ruff, mypy strict, hassfest (0 invalid), docs-check (7 examples) clean.
- `make dev-smoke` passes on the dev HA 2026.9.4: actions over REST with response data, sensor, per-user dismiss, admin-only clear, persistence across container restart, condition on `input_boolean.test_window` with `people: [person.dev_user]`.
- Not verified on the real instance: condition re-evaluation across a container restart (unit tests `test_condition_survives_restart_and_is_reevaluated`, `test_restart_with_entity_not_yet_loaded_keeps_state` cover it).

## Before starting work
1. `make setup` (uv, Python 3.14).
2. Docker Desktop must run. If `docker` is not found: `export PATH="$HOME/.docker/bin:$PATH"`.
3. `make dev-up`. Dev HA state lives in `dev/ha-config/` (gitignored), credentials in `dev/dev-credentials.env`. After `make dev-reset`, run `make dev-onboard`.
4. `make check` green before and after each change.

## Phase 4 plan (card), once approved
Spikes first, against the dev HA; record results in `docs/dev/HA_API_NOTES.md`:
1. N-14: does a card that renders nothing leave a gap in sections view on 2026.9.4? Decide `show_empty` behaviour and whether docs recommend a visibility condition on `sensor.heads_up_active_banners`.
2. Tap action: check the `hass-action` event (`{config: {tap_action}, action: "tap"}`, bubbles + composed) and `confirmation` handling in the 2026.9 frontend source (`home-assistant-frontend==20260826.7` is in `.venv`).
3. Reconnect: does `hass.connection.subscribeMessage` re-subscribe after an HA restart? Restart the container with the card open.

Then build, per DESIGN §8 and `.claude/rules/frontend-card.md`:
- `custom_components/heads_up/frontend.py`: `async_register_static_paths` + `add_extra_js_url` with `?v=<manifest version>` (N-8, N-9), from `async_setup_entry`, removed on unload.
- `custom_components/heads_up/frontend/heads-up-card.js`: `heads-up-card` + `heads-up-card-editor`, `window.customCards`, config keys of DESIGN §8; sort/filter as exported pure functions.
- vitest for those functions (dev-only `package.json`, no runtime npm deps), `make test-card`, CI step.
- `docs/card.md` (config reference) and card-key parity in `docs-check`.
- Manual matrix: sections/masonry/panel, light/dark, 768×1024 and 1280×800, admin vs `dev-user`, `show_all`, reconnect.
- Confirm SECURITY.md "Tap actions" matches what the card does.

## Open items
`docs/OPEN_QUESTIONS.md`.
