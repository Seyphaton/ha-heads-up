# H0a: Test fixtures and dev stubs

Size: small. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Give every later hub work package the same fakes: notify services, a fake `mobile_app` registration with its tracker and person, fake text-to-speech, media player and Assist satellite entities, and a capture for persistent notifications. Decide how the dev instance gets stub services, since it has no notify platforms and no real devices (rule 2: only the dev instance may be used).

## Dependencies and parallel work
- Needs: none
- Can run at the same time as: H0b
- Files this package owns (create): `tests/hub/__init__.py`, `tests/hub/conftest.py`, `tests/hub/helpers.py`, dev stub files under `dev/` (location decided in the session)
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `tests/conftest.py` (only if a shared fixture must move), `dev/ha-config/configuration.yaml`, `dev/smoke.py` (helpers only), `docs/dev/TESTING.md`, `docs/dev/DEV_ENVIRONMENT.md`

## Scope
- Fixture `fake_notify`: registers `notify.mobile_app_<slug>` services with `async_mock_service` and returns the recorded calls (N-70 pattern: `notify.mobile_app_<slugify(device_name)>`).
- Fixture `mobile_app_device`: creates a `mobile_app` config entry (data: `device_name`, `device_id`, `user_id`, `webhook_id`), the `device_tracker` entity with `unique_id` = `device_id`, and links it to a `person` entity (`device_trackers`, `user_id`) so the person to device path (N-71) can be tested without a real device.
- Fixtures for a fake `tts` entity with `tts.speak`, a `media_player` entity with `play_media` (with and without the announce feature), an `assist_satellite` entity with `announce`, and `persistent_notification.create` and `dismiss` capture.
- Helper to fire `mobile_app_notification_action` events with a given `action`, `tag` and `context.user_id`.
- Helper to set a person's state (`home`, `not_home`, a zone name, `None`, `unavailable`) and to move the time forward with the freezer (existing `freezer` pattern from `tests/test_snooze.py`).
- Decide and record how the dev instance gets stub notify and speech services (for example a dev-only stub component or `smoke.py` helpers); the dev instance must never need a real device. Document it in `docs/dev/DEV_ENVIRONMENT.md`.

## Out of scope
Any hub behavior. No changes to `custom_components/`.

## Tests
A test per fixture proving it records what is expected; `make test` stays green.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/dev/TESTING.md` (new fixtures and how to use them), `docs/dev/DEV_ENVIRONMENT.md` (stubs).

## Parity (CLAUDE.md rule 9)
Not applicable (no banner feature).

## Blast radius (rule 5)
None for users; test and dev tooling only.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
How the dev instance gets stub services. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-70, N-71 (fake registration shape). (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
All fixtures documented and used by at least one test; `make check` green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
