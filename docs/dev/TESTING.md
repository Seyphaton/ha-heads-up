# Testing

| What | How | Command |
|---|---|---|
| Integration logic | pytest + `pytest-homeassistant-custom-component` 0.13.367 (HA 2026.9.4) | `make test` |
| One test | | `make test ARGS="tests/test_config_flow.py::test_second_entry_aborts"` |
| Restart safety | unload + reload entry from persisted store; `freezer` moves time past `expires_at` | `tests/test_restart.py` |
| Real instance | `dev/smoke.py`: REST actions with response, sensor, per-user dismiss over WebSocket as `dev-admin`/`dev-user`, admin-only clear, container restart, persistence; condition on `input_boolean.test_window` + `people: [person.dev_user]`; watch rule added through the REST subentry flow, seen by both users, `not_dismissible` / `rule_banner`, container restart, rule deleted over WebSocket | `make dev-smoke` (calls `clear_all`, so it removes every banner on the dev instance; it deletes only the rule named "Smoke window") |
| Lint / types | ruff, mypy strict on `custom_components/heads_up` | `make lint`, `make typecheck` |
| Manifest / translations | hassfest Docker image | `make hassfest` (needs Docker) |
| Docs | banned words, placeholders; YAML examples in user docs validated against action schemas; fields: schema == services.yaml == docs/actions.md; card options: `CONFIG_KEYS` == `docs/card.md` table, card examples use only those | `make docs-check` |
| Card logic | vitest 3.2.4 on the card module's exported pure functions (65 tests; needs Node 22, `npm install` runs inside the target) | `make test-card` |
| Documented examples | the YAML of `docs/examples.md` is installed on the dev HA through the config API (entity IDs swapped for `input_boolean.test_window`, `person.dev_user`), run, and the banners checked per user; REST and WebSocket calls with a dev token. Not scripted in the repo | manual, see N-43, N-44 |
| Card in browser | manual matrix against dev HA (sections/masonry/panel, light/dark, 768×1024 and 1280×800, admin and `dev-user`, dismiss, tap with confirmation, restart, empty card); results in DESIGN §11; a six-card dashboard view on the dev HA covers the Phase 7 options | manual |

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
| `tests/test_rules.py` | watch rules: visibility, state list/attribute, unavailable/removed, disabled, edit/delete, `{name}`, people, reload without store writes, limits and sensor, clear actions, dismissal rules, `rule_banner`, events, no events at setup, WebSocket |
| `tests/test_empty_operators.py` | `empty` and `not_empty`: matcher, schema, banners and rules (attribute, unavailable, `for`), rule form without a prefilled State |
| `tests/test_for_template.py` | condition `for` (schema, wait, reset, reload, replace, clear, operators) and template conditions (show/hide, recurring, errors, `now()`, reload, tracking), rules with `for`, rule flow `for` |
| `tests/test_operators.py` | condition operators: matcher per operator and boundary, `check_state` codes, action schema (defaults, rejections), stored banners and rules with `not_equals`, numeric on attribute, unavailable, old rule without `operator`, rule flow with operator and error codes |
| `tests/test_rules_flow.py` | rule subentry flow: defaults, all fields, `entity_not_found`, blank message, empty state list, same entity twice, reconfigure |
| `tests/test_dismiss_many.py` | `heads_up/dismiss_many`: per-user dismissal in one update, global scope removal, skipped IDs, empty list, `not_loaded` |
| `tests/test_storage_corruption.py` | a damaged banner entry in readable storage is skipped and logged; the others load (undecodable files: N-45, checked on the dev HA) |
| `tests/hub/helpers.py`, `tests/hub/conftest.py` | hub fakes (H0a): `mobile_app_device` (a Companion registration: `mobile_app` config entry with `device_name`, `device_id`, `user_id`; device with identifier `(mobile_app, device_id)`; `device_tracker` entity with `unique_id` = `device_id`; the person's `device_trackers`; the recording notify service `notify.mobile_app_<slug>`, N-70, N-71), `fake_notify` (a recording `notify` service), `fake_speakers` (players with and without the announce feature, an Assist satellite, tts; recorded `play_media`, `tts.speak`, `announce`, `volume_set`, N-65, N-66), `persistent_capture` (N-67); helpers `set_person` (`home`, `not_home`, a zone, `unavailable`, `None` stored as `unknown`, N-63), `fire_app_action` (`mobile_app_notification_action` with `context.user_id`, N-72), `tick` (freezer plus timers) |
| `tests/hub/test_scaffolding.py` | the fakes behave like the Home Assistant facts they stand for |
| `tests/hub/test_core_transitions.py` | every manager mutation path emits its typed transition (create, update, severity, each removal reason, user and global dismissal, snooze, elapsed snooze, condition flips, rules incl. delete); bus event payloads unchanged |
| `tests/hub/test_core_notify.py` | `notify` and the shortcuts: banner-only like `create_banner`, response counts, channel and target shapes, unknown names, `clear` versus `clear_banner`, banner recipients, hub off |
| `tests/hub/test_core_engine.py` | ledger and trace bookkeeping, dry-run `plan`, per-message ordering, a failing channel, cancellation on unload, restart without re-sending, vanished messages, hub switched on and off at runtime. `settle()` in `helpers.py` waits for the background deliveries, which `async_block_till_done` does not |
| `tests/hub/test_core_ledger.py` | deliveries store: key and versions, migration hook, damaged rows, removal with the entry |
| `tests/hub/test_core_options.py` | `hub_enabled`, install token, limit and history defaults, options flow keeps the token |
| `tests/hub/test_audiences_resolution.py` | built-in and custom audiences (every kind), admins, zones, unknown presence per severity |
| `tests/hub/test_audiences_presence.py` | Last to leave and First home sequences, debounce with the time freezer, unknown states, new entity at startup, deleted person, restart |
| `tests/hub/test_recipients_profiles.py` | profile detection with the fake registration (other-integration tracker, missing service, manual add and remove, missing device, rename, channels), push expansion |
| `tests/hub/test_recipients_groups.py` | groups, area expansion, deduplication, empty group and unknown names |
| `tests/hub/test_audiences_flows.py` | the three subentry flows: add, reconfigure, errors, duplicates |
| `tests/hub/test_audiences_notify.py` | `notify` with real audiences, groups and profiles; restart; hub off |
| `tests/hub/test_audiences_ws.py` | `heads_up/hub_preview_audience`: members, skipped, not found, admin only |
| `tests/hub/test_push_payload.py` | push payload: tag and group, level and importance per severity, iOS critical opt-in, lock-screen modes, language, sticky, click action, button order and ids, platform button limits |
| `tests/hub/test_push_lifecycle.py` | replace by tag, all devices of a person, clear on every end, per-user dismissal, snooze and remind, waiting message, ledger tag and person, missing and failing services, no device, restart, startup clear, hub off |
| `tests/hub/test_push_actions.py` | press round trip: dismiss, snooze, own button, user from the person or the event, mismatch, stale, wrong recipient, foreign actions, untrusted tag, listener removed on unload |
| `tests/hub/test_policy_matching.py` | severity and tag matching, empty lists, `policy` field (name, none, disabled), duplicates |
| `tests/hub/test_policy_chain.py` | stage order, skip stops the chain, stubs pass, unknown stage |
| `tests/hub/test_policy_flow.py` | policy form: both types, targets per channel, unknown names, duplicates, reserved name, reconfigure |
| `tests/hub/test_policy_escalation.py` | timing with the freezer, ledger timer row, acknowledge, dismiss counts or not, chain of two, severity change, clear and condition end, overdue step after a restart (once), pending step after a restart, deleted audience reported, disabled, `policy` field, tags |
| `tests/hub/test_policy_reminder.py` | repeat and maximum, acknowledge, snooze pause and resume, everyone dismissed, channel limit, severity filter |
| `tests/hub/test_policy_quiet.py` | window boundaries, midnight, days, clock-change days (Europe/Berlin), quiet marker in the push, critical passes, wait and release once, restart while held, cleared meanwhile, drop with trace, banner unaffected, reminder skipped, escalation of a rule message |
| `tests/hub/test_policy_away.py` | held for a person away and sent on arrival once, recipients and unknown presence not held, cleared, acknowledged and dismissed meanwhile, maximum wait, restart while held |
| `tests/hub/test_policy_fallback.py` | no_audience, failed, both, not when someone was notified, once per message, no loop, deleted audience reported, waiting message, `policy: none` |
| `tests/hub/test_popup_channel.py` | delivery per person with a user, payload and style per severity, `off`, no user, dismiss and snooze per user, end, update, quiet card, Acknowledge flag, restart, audience, rule message through an escalation, config command (and hub off), subscription events |
| `tests/card/popup.test.js` | queue order, current message, style, focus rule, buttons, texts per language (vitest) |
| `tests/test_frontend.py` (loader) | loader registered and removed, under 1 KB, loader and popup module served with cache headers |
| `tests/hub/test_speak_channel.py` | each speaker kind's service, volume never set, text order and shortening (option), groups, cooldown (and zero), update not repeated, nothing on clear, quiet skip, failures and reasons, engine choice, queue on a plain player, rule message through an escalation |
| `tests/hub/test_policy_summarize.py` | hold (hidden, not pushed, not counted), one summary per recipient and channel with only their messages, banner summary, highest severity, cut at ten, resolved marking, nothing held sends nothing, interval from the first held message, critical excluded or included, release when a message becomes critical, daily time, restart (held and overdue), quiet hours, 24 hour lifetime, summary not held or escalated, policy deleted releases, `policy: none`, changed or unchanged update, rule message, text per language |
| `tests/hub/test_policy_acknowledge.py` | Acknowledge button only with a policy, press on the push, banner stays, idempotent, unknown message, rule messages (tag `rule`, reset when the condition flips), usage lookup |
| `tests/test_frontend.py` | module URL with `?v=<version>-<file hash>` registered, changes with the file, removed on unload (the URL that was added) and added on reload, file served at `/heads_up/heads-up-card.js` |
| `tests/card/heads-up-card.test.js` | `normalizeConfig` (all options), `sortBanners`, `visibleBanners`, `controlsFor`, `retryDelay`, `relativeTime`, `collapse`, `emptyView`, `resolveColors`, `colorParts`, `swipeOutcome`, `clearableIds` (vitest) |

## Notes

`make check` runs lint, types, pytest, docs-check and `make test-card`. CI (`.github/workflows/ci.yml`) runs python checks, the same pytest on HA 2026.10.4 (`python-ha-2026-10`; locally: throwaway venv with `pytest-homeassistant-custom-component==0.13.375` and `home-assistant-frontend==20260930.5`), the card tests (`npm ci`, vitest); `.github/workflows/validate.yml` runs hassfest (with checkout) and the HACS action on push, pull request, daily and on demand. The repository is on GitHub (private); the first workflow results have not been read yet.

HA logs an `ERROR ... Unauthorized` line when a non-admin calls `heads_up/admin_clear`; that is HA's `require_admin` behaviour, not a failure.
