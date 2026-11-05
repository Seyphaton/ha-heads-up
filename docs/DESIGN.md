# Design: Heads Up

Living design document: requirements and architecture. Decisions are referenced as D-nnn (`docs/DECISIONS.md`), API facts as N-nn (row in `docs/dev/HA_API_NOTES.md`), risks as R-n (§14). Where code and this document disagree, fix one of them in the same commit.

## 0. Implementation status (2026-11-05)

| Part | Status |
|---|---|
| §4 data model, §5 lifecycle, §6 backend, §7 actions, §9 targeting | implemented and tested (Phases 2–3) |
| §17 watch rules (config subentries, virtual banners) | implemented and tested (Phase 8); card unchanged |
| §18 condition operators (shared matcher for actions and rules) | implemented and tested (Phase 9); card unchanged |
| §19 condition `for` and template conditions | implemented and tested (Phase 10); card unchanged |
| §20 `empty` and `not_empty` operators, rule form without a prefilled State | implemented and tested (Phase 11); card unchanged |
| §21 banner buttons and snooze | implemented and tested (Phase 12); card checked on the dev HA with a mouse |
| §22 parity of banner sources, rule buttons, tap action, dismiss scope and template conditions | implemented and tested (Phase 12 follow-up) |
| §23 notification hub | built (Phase 15, H0 to H10 and the later maintainer changes) on the branch `hub/h9e-wizard`; pre-releases 1.0.0-alpha.2 to 1.0.0-alpha.5 are tagged and pushed (D-133, D-154); not merged to `main`, no 1.0.0 |
| §8 frontend (card, editor, serving the JS file) | implemented; pure functions tested with vitest, behaviour checked on the dev HA (Phases 4 and 7) |
| Human docs | README, `actions.md`, `card.md`, `examples.md`, `troubleshooting.md`, `limitations.md`, `uninstall.md`, `upgrading.md` done (Phase 6) |
| Packaging, release, CI run | icon, CI jobs (HA 2026.10.4, HA 2026.9.4, card), HACS and hassfest validation, `docs/dev/RELEASE.md`; the repository is public, CI was reported green on `main` (maintainer, 2026-10-26, `docs/OPEN_QUESTIONS.md`), the README has screenshots (`docs/images`); versions 0.1.0 to 0.4.0 are tagged, the last stable version is 0.4.0 |

## 1. Goals, non-goals, scope cut

Goals
- One backend that holds every in-dashboard banner; producers call actions, one card displays.
- Banner lifecycle (timeout, condition, dismiss, clear) survives HA restarts.
- No caller-specific code; the action schema is the only contract.

Non-goals
- Heads Up is a central hub for notifications (D-107, D-123). The banner is the core and push, popup, speech and the notification bell are channels on the same level; the user documentation (README, `docs/hub.md`) starts from the problems this solves and lists the banner first. Phone calls, SMS, e-mail and chat services stay out of scope.
- Access control. Server-side targeting limits what a user's session receives, but admins and anyone with file access can read all banners (D-008).
- Changing other integrations, automations, scripts or blueprints.

MVP (Phases 2–4)
- Actions `create_banner`, `clear_banner`, `clear_all`; dismiss and admin clear over WebSocket.
- Fields of §4, entity/state condition with `once`/`recurring`, per-user/global dismiss, person targeting, tag, tap action, timeout, limits with eviction.
- Count sensor, events, options flow.
- Card with custom editor, sort/filter options.

Later (recorded in `docs/OPEN_QUESTIONS.md`)
- Popup for critical banners, template and full HA conditions, absolute expiry input, per-severity binary sensors, persistent-notification mirror, other channels (toasts).

## 2. Glossary and personas

| Term | Meaning |
|---|---|
| Banner | One stored message with the fields in §4. |
| Producer | Anything that calls `heads_up.*` actions: automation, script, blueprint, REST/WebSocket client. |
| Viewer | A logged-in HA user whose browser shows the card. |
| Admin | HA user with `is_admin`. Can clear any banner from the card and use `show_all`. |
| Active | Stored, not expired, condition true or absent. |
| Waiting | Stored, condition currently false (not yet true for `once`; false phase for `recurring`). |
| Visible to user U | Active, not dismissed globally, not dismissed by U, targeted at U (or untargeted). |

## 3. Requirements

Functional: §1 goals and §4–§9; resolved details in D-004–D-031.

Non-functional
| Area | Requirement |
|---|---|
| Restart safety | Banners, dismissals and `expires_at` persist in `.storage/heads_up.banners`. Banners that expired while HA was down are removed on start and fire `heads_up_banner_expired`. |
| Latency | A banner created by an action appears in an open card within one WebSocket round trip (no polling). |
| Load | At most 50 banners by default (option, max 200), one state listener covering all condition and person entities, one timer per banner with a timeout. |
| Concurrency | Actions run in the event loop and mutate state synchronously (no `await` between read and write), so parallel callers cannot interleave a single upsert. |
| Accessibility | Severity shown by icon shape and color; the text label is optional (`show_severity`, D-048) and always present for screen readers; not color only; `aria-live` region; dismiss button 48×48 px with translated `aria-label`; keyboard reachable. |
| i18n | English is the source (D-037). German, French and Spanish are added files (D-071): `translations/de.json`, `fr.json`, `es.json` for the integration, and a `TRANSLATIONS` table in the card chosen by `hass.language` (`setLanguage`). Missing keys fall back to English. Banner text is caller-supplied and not translated. |
| Security | Non-admin users can create, clear and dismiss (D-029). `show_all` and admin clear are rejected server-side for non-admins. |
| Compatibility | HA ≥ 2026.9.0 (D-019). Tested versions are stated only after tests ran. |

## 4. Data model

### 4.1 `create_banner` input

| Field | Type | Default | Validation |
|---|---|---|---|
| `id` | string | generated `hu_` + 10 hex chars, returned in response | `^[a-z0-9_-]{1,64}$` |
| `message` | string | required | 1–1000 chars |
| `title` | string | none | ≤ 100 chars |
| `severity` | `info` \| `success` \| `warning` \| `critical` | `warning` | enum |
| `icon` | mdi string | per severity: `mdi:information`, `mdi:check-circle`, `mdi:alert`, `mdi:alert-octagon` | `cv.icon` (N-2) |
| `timeout` | seconds or duration; `0` = no timeout | option `default_timeout` (shipped: 24 h, D-031) | `cv.time_period`, 0 or 1 s – 365 days |
| `condition` | object `{entity_id, state, attribute}` | none | `entity_id` must exist at creation (`entity_not_found`); `state` string or list of strings, default `"on"`; `attribute` optional string |
| `mode` | `once` \| `recurring` | `once` | ignored without `condition` |
| `wait_for_condition` | bool | `true` | ignored without `condition` |
| `dismissible` | bool | `true` | |
| `dismiss_scope` | `user` \| `global` | option `default_dismiss_scope` (shipped: `user`) | |
| `people` | list of `person.*` entity IDs | empty = everyone | each must be a `person` entity ID; not required to exist (a later-created person matches) |
| `tag` | string | none | `^[a-z0-9_-]{1,64}$` |
| `tap_action` | HA action config object | none | must be a mapping with key `action`; passed to the frontend unchanged (D-015) |

Condition match: the compared value is the entity state, or `str(attributes[attribute])` if `attribute` is set; it matches if it equals `state` (or any item of the list). `state` accepting a list is a proposed default (D-030).

### 4.2 Stored record (`Store` version 1, minor 1)

All input fields after defaults, plus:

| Field | Type | Meaning |
|---|---|---|
| `created_at` | ISO 8601 UTC | first creation; kept on upsert |
| `updated_at` | ISO 8601 UTC | last upsert |
| `expires_at` | ISO 8601 UTC or null | `updated_at + timeout` |
| `condition_met` | bool or null | last evaluated result; null = never evaluated with a real state |
| `ever_met` | bool | condition was true at least once since last upsert (drives `once` removal) |
| `dismissed_by` | list of user IDs | per-user dismissals |

### 4.3 Upsert (D-010)
`create_banner` with an existing `id`: all input fields replaced, `updated_at` = now, `expires_at` recomputed, `dismissed_by` = [], `ever_met` re-evaluated from the current entity state; `created_at` kept. Fires `heads_up_banner_updated`.

### 4.4 Limits and overflow (D-016)
- `max_banners` option, default 50, range 1–200.
- New ID when full and `evict` on: remove the banner with the lowest severity (`success` < `info` < `warning`), oldest `updated_at` first; `critical` is never evicted. Fires `heads_up_banner_cleared` with `reason: evicted`.
- No candidate or `evict` off: fails with `too_many_banners`. Upserts of existing IDs never evict.

## 5. Lifecycle

```
                create_banner
                     │
        ┌────────────┴──────────────┐
  condition false                no condition / condition true
  wait_for_condition=false              │
        │                               ▼
  status condition_false        ┌──── ACTIVE ◄───────────┐
  (nothing stored)              │      │                 │ recurring: false→true
                                │      │ condition       │ (dismissals reset)
  condition false,              │      ▼ true→false      │
  wait_for_condition=true ──► WAITING ─┴─ once: REMOVED (reason condition)
                                │        recurring: back to WAITING
                                │
  any state ── timeout ──► REMOVED (expired)
  any state ── clear_banner / clear_all / admin clear / evicted ──► REMOVED (cleared)
  ACTIVE ── dismiss (global scope) ──► REMOVED (dismissed)
  ACTIVE ── dismiss (user scope) ──► stays ACTIVE, hidden for that user
```

Semantics

| Situation | Result |
|---|---|
| Timeout + condition + dismiss | Whichever happens first removes the banner. |
| Global dismiss | Banner removed from storage; fires `dismissed`. |
| User dismiss | User ID added to `dismissed_by`; fires `dismissed` with `user_id`. |
| `dismissible: false` | Card shows no X; WebSocket dismiss rejected with `not_dismissible`. Admin clear still works (D-011), except for rule banners (`rule_banner`, D-056). |
| Condition entity `unavailable` / `unknown` | `condition_met` unchanged (D-006). |
| Condition entity removed after creation | Treated like `unavailable`; banner kept; timeout still applies. Logged at warning level. |
| HA was down past `expires_at` | Removed during setup, `expired` event fired. |
| Restart with condition | Re-evaluated when the entity reports a state other than `unavailable`/`unknown`; until then `condition_met` keeps its stored value. |
| `once` banner, condition never becomes true | Removed by the 24 h default timeout unless the caller passed `timeout: 0` or the option was cleared (R-4, D-031). |

History: no stored history; events only (D-012).

## 6. Backend architecture

```
custom_components/heads_up/
  __init__.py      async_setup: register actions + WebSocket commands; async_setup_entry: load store, start manager, forward sensor platform
  manager.py       BannerManager: in-memory dict, mutations, condition evaluation, targeting, state tracker, timers, events, subscriber fan-out; banner_store(); watch rules as virtual banners (`sync_rules`, `rules`, §17)
  models.py        Banner dataclass, (de)serialisation, per-viewer payload (to_client)
  services.py      action schemas (SCHEMAS, also used by docs-check) + handlers
  websocket.py     heads_up/subscribe, heads_up/dismiss, heads_up/admin_clear
  sensor.py        count sensor
  config_flow.py   single-instance config flow + options flow + `RuleSubentryFlow` (watch rules, §17)
  const.py, strings.json, translations/en.json, services.yaml, icons.json, manifest.json
  frontend.py                static path (async_setup) + add_extra_js_url per entry, `?v=<manifest version>-<8 hex of the file's SHA-256>` (D-050)
  frontend/heads-up-card.js  card, editor, pure functions (`normalizeConfig`, `visibleBanners`, `sortBanners`, `controlsFor`, `retryDelay`, `CONFIG_KEYS`)
```

No `Store` subclass yet: storage is version 1 and has no migration. Add one with `_async_migrate_func` on the first breaking storage change (§13).

Data flow: action → `BannerManager` mutates dict synchronously → `Store.async_delay_save(…, 1)` (D-023, N-6) → fires event → notifies WebSocket subscribers and the sensor.

Trackers
- Conditions: one `async_track_state_change_event` (N-7) over the set of all condition entity IDs; rebuilt when that set changes. Unsubscribed on unload.
- Person changes: same tracker also watches `person.*` IDs referenced in `people`, so a changed `user_id` (N-10) re-filters subscribers.
- Timeouts: one `async_track_point_in_utc_time` per banner with `expires_at` (N-7); cancelled on removal/upsert/unload.

Schemas: written with `voluptuous`-compatible API via `homeassistant.helpers.config_validation`; on 2026.9+ this runs on probatio (N-1). Tests assert on error codes, not message text (N-1 wording differences).

Entity: `sensor.heads_up_active_banners`, state = number of active banners (stored, condition true or absent; D-013); no attributes beyond defaults. Globally dismissed banners are removed, so they are not counted.

Events (D-012)

| `event_type` | Data |
|---|---|
| `heads_up_banner_created` | `id`, `severity`, `tag` |
| `heads_up_banner_updated` | `id`, `severity`, `tag` |
| `heads_up_banner_dismissed` | `id`, `tag`, `scope`, `user_id` |
| `heads_up_banner_expired` | `id`, `tag` |
| `heads_up_banner_cleared` | `id`, `tag`, `reason` (`action`, `clear_all`, `condition`, `evicted`, `admin`) |

WebSocket API (N-4, N-5)

| Type | Auth | Payload | Result |
|---|---|---|---|
| `heads_up/subscribe` | user; `show_all: true` requires admin (`unauthorized`) | `show_all?` | result, then events `{banners: [...]}` (full visible list per change; each item has `dismissed` for the viewer; `dismissed_by` is never sent; `icon` resolved to the severity default) |
| `heads_up/dismiss` | user, only for a banner addressed to them | `banner_id` | `{}` or error `not_found` / `not_dismissible` / `not_targeted` (D-156) |
| `heads_up/dismiss_many` | user | `banner_ids` (list) | `{dismissed, skipped}`; unknown, non-dismissible and untargeted IDs count as skipped (D-156); one subscriber update for the batch (D-048) |
| `heads_up/admin_clear` | admin (`require_admin`) | `banner_id` | `{}` or `not_found` / `unauthorized` / `rule_banner` (D-056) |

Banner IDs travel as `banner_id` because `id` is the WebSocket message ID.

Visibility is computed per connection from `connection.user.id`; the person whose `user_id` equals it decides targeting. Sending the full list (≤ 200 items) per change is chosen over diffs: fewer states to get wrong.

Config flow: one entry, no input (D-026). Options: `max_banners`, `evict`, `default_dismiss_scope`, `default_timeout`. Option change applies to new banners only. Removing the entry deletes `.storage/heads_up.banners` (`Store.async_remove`, N-6) in `async_remove_entry`.

## 7. Action reference

| Action | Fields | Response (`SupportsResponse.OPTIONAL`, N-3) | Errors |
|---|---|---|---|
| `heads_up.create_banner` | §4.1 | `{id, status}` with `status` `created` \| `updated` \| `waiting` \| `condition_false`; `evicted` ID if any | schema errors (`vol.Invalid`), `entity_not_found`, `too_many_banners`, `not_loaded` |
| `heads_up.clear_notifications` | `id`, `tag`, `severity` (list), `channels` (list), `all`; at least one, or `all: true` alone (D-158) | `{cleared: n}` | schema errors (`vol.Invalid`); unknown id → `cleared: 0`; removes any message of any channel, never a rule banner |
| `heads_up.clear_banner` | `id` or `tag` (at least one) | `{cleared: n}` | deprecated (D-158), one log warning per start; none (unknown id → `cleared: 0`) |
| `heads_up.clear_all` | none | `{cleared: n}` | deprecated (D-158); removes every stored message of every channel |

Errors are `ServiceValidationError` with translation keys in `strings.json`. Actions are registered in `async_setup`; called without a loaded config entry they fail with `not_loaded`.

Examples (illustration only; the validated user examples are in `docs/actions.md`)
```yaml
# automation action: warning until window closes
- action: heads_up.create_banner
  data:
    id: window_bedroom
    title: Window open
    message: Bedroom window is open and it is raining.
    condition:
      entity_id: binary_sensor.bedroom_window
      state: "on"

# script: critical, 10 minutes, only for one person
- action: heads_up.create_banner
  data:
    message: Water leak in the basement.
    severity: critical
    timeout: {minutes: 10}
    people: [person.example]
    dismissible: false
  response_variable: banner

- action: heads_up.clear_banner
  data: {tag: laundry}
```
External call paths (D-022, D-043): REST `POST /api/services/heads_up/create_banner` (with `?return_response` for response data: `{"changed_states": [], "service_response": {...}}`; without it `[]`) and WebSocket `call_service` with `return_response: true` (data under `result.response`) work through HA core; no own endpoints. An invalid field gives REST `400: Bad Request` and WebSocket `success: false`, `error.code: invalid_format` (N-43). Both verified on the dev HA; examples in `docs/examples.md` ran there (N-44).

## 8. Frontend architecture

- One plain-JS ES module `heads-up-card.js`, no build (D-021). Served at `/heads_up/heads-up-card.js` via `async_register_static_paths` (N-9) and registered with `add_extra_js_url(hass, "/heads_up/heads-up-card.js?v=<manifest version>-<file hash>")` (N-8); the query changes with the version and with the file's content, which busts the browser cache on upgrade and whenever the file changes (D-050, N-52). No manual resource step. Not loaded in safe mode (N-8).
- Elements: `heads-up-card` and `heads-up-card-editor` (`getConfigElement`, `config-changed`, N-13); `window.customCards` entry.
- Data: on `connectedCallback` the card calls `hass.connection.subscribeMessage(cb, {type: "heads_up/subscribe", show_all}, {resubscribe: false})`; unsubscribes in `disconnectedCallback`. `show_all` is sent only when `hass.user.is_admin`. The card listens to the connection event `ready` and subscribes again itself; a failed subscribe shows a one-line error and is retried after 1, 2, 5, 10 and then every 30 s (D-041, N-39, N-40). Stale callbacks of an older subscription are ignored.

Card config

| Key | Type | Default |
|---|---|---|
| `type` | `custom:heads-up-card` | required |
| `severity` | list of severities | all |
| `tag` | list of tags | all |
| `max_items` | int ≥ 1 | unlimited |
| `sort` | `severity` \| `time` | `severity` (D-017) |
| `layout` | `comfortable` \| `compact` | `comfortable` |
| `show_all` | bool (admins only; ignored for others) | `false` |
| `show_empty` | bool | `false` (render nothing) |
| `title` | string | none (header above the banners) |
| `collapsed_items` | int ≥ 1 | off (D-048) |
| `show_time` | bool | `false` (relative time from `updated_at`, refreshed every 30 s) |
| `show_severity` | bool | `false` (hides the text label only) |
| `colorize` | `all` \| `background` \| `icon` \| `bar` | `all` |
| `colors` | map severity → CSS color or `var(--x)` | theme variables; invalid values fall back |
| `clear_all` | bool | `false` ("Clear all" button, `heads_up/dismiss_many` with the shown dismissible IDs) |
| `swipe_to_dismiss` | bool | `false` (pointer events, `touch-action: pan-y`, 80 px or 30% of width) |
| `empty_message` | string | none (icon + text when no banner; shows the card) |
| `empty_icon` | icon | `mdi:bell-check-outline` |

Rendering: banner = icon, severity label, title, message, optional tap target, X button if dismissible, admin clear button for admins on non-dismissible banners that are not rule banners (`rule: true`). When some banner has a button and another has none, the latter gets an `aria-hidden` 48 px spacer (`reservesActionSpace`), so times align. Banner text is written with `textContent` only. `ha-form` builds the editor. Colors: per severity `colors[severity]` or the theme variable (`--info-color`, `--success-color`, `--warning-color`, `--error-color`) as `--accent`; `colorize` decides whether background (tinted with `color-mix`), icon and label, and left bar use it; uncolored parts use `--secondary-background-color`, `--primary-text-color` and `--secondary-text-color`. The `compact` layout is one truncated line with the full text in the `title` attribute. The severity label is always in the DOM (visually hidden unless `show_severity`). Critical banners in an `aria-live="assertive"` region, others `polite`. Tap action: dispatch `hass-action` (bubbles, composed) with `{config: {tap_action}, action: "tap"}` only for banners that have a `tap_action`; Home Assistant's `handleAction` runs it and handles `confirmation` (N-38). Sizing: `getCardSize` = number of rendered banners (at least 1); `getGridOptions` → `{columns: 12, rows: "auto"}` (N-12). Empty card: `display: none` on the host; no extra gap in a sections view (N-14, D-040). The count sensor stays available for a global visibility condition.

Touch and kiosk use: 48 px touch targets (the compact row is 40 px, the button keeps 48 px with a negative margin); no hover-only controls; the Phase 4 matrix used 768×1024 and 1280×800 viewports. A dismissal belongs to the user, so a banner dismissed in one card disappears from all of that user's cards.

## 9. People and targeting

- `people` lists person entity IDs. For viewer U, a banner is targeted if `people` is empty or any listed person's `user_id` attribute equals U's ID (N-10).
- A user with no linked person sees only untargeted banners. A person with no user matches nobody.
- Filtering happens in `heads_up/subscribe` (D-008); the browser never receives banners not targeted at its user unless `show_all` and admin.
- No built-in roles or groups; callers resolve groups themselves.

## 10. Error handling and edge cases

| Case | Behaviour |
|---|---|
| Invalid `id`/`tag` characters | schema error, nothing stored |
| `message` > 1000 chars | schema error |
| Condition entity missing at creation | `entity_not_found` |
| Condition entity unavailable/unknown | visibility unchanged (stored banners); a rule banner is hidden (D-053) |
| Person ID in `people` does not exist | accepted; matches nobody until created |
| Full and no evictable banner | `too_many_banners` |
| Two parallel `create_banner` with same `id` | serialized in event loop; last call wins; two events |
| Clock change / DST | all times UTC; DST has no effect. A manual system-clock jump forward expires banners early (HA timer semantics). |
| Corrupt storage file (undecodable) | HA's `Store` renames it to `.corrupt.<time>`, logs an error and returns no data; Heads Up starts empty (N-45, D-044). Checked on the dev HA, not unit-tested. |
| Storage file readable, one banner damaged | that banner is skipped with an error log naming its `id`; the others load; the file is rewritten (`tests/test_storage_corruption.py`). |
| Page loaded in the first second after an HA start | `index.html` has no card URL yet; the page shows "Custom element doesn't exist" until reloaded (N-42, D-045). |
| Card on HA without the integration loaded, or before it has loaded during a start | card shows "Heads Up is not available…" and retries (D-041); HA answers `unknown_command` until `heads_up` is set up. |
| Huge `tap_action` | limited by WebSocket message size; not validated beyond being a mapping (R-1). |

## 11. Test strategy

Status: Python tests implemented (121, files listed in `docs/dev/TESTING.md`); card pure functions tested (65 vitest tests); CI matrix job for 2026.10.4 written, all 121 tests also pass on HA 2026.10.4 in a throwaway venv (2026-10-25); the CI jobs are not read yet.

- Python: `pytest-homeassistant-custom-component` 0.13.375 = HA 2026.10.4, the development version (N-46, D-123); CI runs the same tests on the minimum tested version 2026.9.4 (0.13.367, N-25). mypy runs on 2026.10.4 (N-91).
- Lifecycle tests first (Phase 2): upsert, each removal reason, eviction order, limits, response data, events, permission checks for `show_all`/`admin_clear`.
- Restart tests: create → unload/reload entry with persisted store → assert banners, dismissals, `expires_at`; freeze time past expiry across restart → `expired` event.
- Condition tests (Phase 3): flips, `once` vs `recurring`, `wait_for_condition`, unavailable, entity removed, person `user_id` changes.
- WebSocket tests with the HA test client: per-user filtering, subscription cleanup on close (N-5).
- Card: vitest on pure functions extracted into the same module (sorting, filtering, visibility of controls) — exported for tests; DOM checked manually.
- Manual matrix (Phase 4, dev HA 2026.9.4, built-in browser): sections, masonry and panel views; light and dark theme; 1280×800 and 768×1024; admin and `dev-user`; dismiss; tap with `confirmation`; reconnect after a container restart; empty card. Phase 7 (same setup, one dashboard view with six differently configured cards, admin): default, compact with time and label, title with clear all and collapse, background-only with custom colors, icon-only, empty message; show more; swipe (mouse drag) and cancel on a short drag, no tap action fired; clear all; time text moving from "just now" to "1 min ago"; editor fields, nested colors and minimal saved config. Not covered: `show_all` rendering with a banner targeted at another person, keyboard activation of a tappable banner, screen readers, swipe on a touch screen.
- Docs: `docs-check` validates every YAML example against the real action schemas and compares documented fields with schema fields.

## 12. Packaging, CI, versioning, runbook

- Public GitHub repo (D-020); layout `custom_components/heads_up/` with `brand/icon.png` inside it (N-47), `hacs.json` `{name: "Heads Up", homeassistant: "2026.9.0"}` (N-18, N-19).
- manifest: `domain`, `name`, `version`, `documentation`, `issue_tracker`, `codeowners`, `config_flow: true`, `integration_type: service`, `iot_class: local_push`, `dependencies: [frontend, http, person]`, `single_config_entry: true` (verified, N-27).
- SemVer; CHANGELOG (Keep a Changelog); GitHub releases, not only tags (N-18).
- CI (D-027): `ci.yml` runs ruff, mypy, pytest (HA 2026.10.4 and 2026.9.4), vitest and docs-check; `validate.yml` runs hassfest and the HACS action, also daily and on demand (D-051).
- Dev environment: Docker `homeassistant/home-assistant:2026.10.4` (N-28, N-92), config from `dev/ha-config/`, no notify services; see `docs/dev/DEV_ENVIRONMENT.md`.
- Install runbook (Phase 6, for users): backup, HACS custom repo install, restart (all automations pause for the restart duration), add integration, open dashboard, smoke test with one `create_banner`, rollback = remove integration + HACS uninstall + restart.

## 13. External callability and API stability

- Contract = action names, field names, defaults, response keys, event types and data keys, card `type` and config keys.
- Additions are minor versions; removals or meaning changes are major versions with one minor release of deprecation warning in the log.
- `condition` is an object so new forms (`template`, `conditions`) can be added without breaking existing calls (D-005).
- `Store` minor version for additive storage changes, major + `_async_migrate_func` for breaking ones (N-6).

## 14. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-1 | `tap_action` with `perform-action` runs any action when tapped, including on a shared display (D-015). | Caller responsibility; stated in SECURITY.md and `docs/actions.md`; Phase 4 documents HA's `confirmation` option in `docs/card.md`. |
| R-2 | Installing requires an HA restart, which pauses all automations, including security-related ones. | Install docs state this before the restart step. |
| R-3 | Empty card leaves a grid gap in sections view (N-14). | Checked on 2026.9.4: no extra gap with `display: none` (D-040). Re-check on upgrade. |
| R-4 | `once` banner with an entity that never turns true and no timeout stays waiting forever. | `default_timeout` ships as 24 h (D-031); clearing it shows a warning in the options form; documented in limitations. |
| R-5 | HA API drift (probatio switch in 2026.9 shows how fast). | Dev image pinned to the minimum supported minor; monthly release-note check; `stale-check-on-upgrade` rows in HA_API_NOTES. |
| R-6 | `hass-action` event and websocket re-subscribe behaviour can change in the frontend. | Verified in the 2026.9.4 bundle and live (N-38, N-39, N-40); `stale-check-on-upgrade`. |
| R-7 | Domain `heads_up` collision (N-22). | Check the HACS default list before the first release. |
| R-8 | Per-user dismiss on a shared login hides the banner for everyone on it (D-007). | Documented; callers choose `dismiss_scope`. |
| R-9 | A page loaded in the first second after an HA start misses the card (N-42). | Cannot be fixed inside an integration (D-045); documented in limitations and troubleshooting. |
| R-10 | Swipe to dismiss was tried with a mouse only; on touch screens it may conflict with scrolling or with HA's own swipe gestures. | Off by default (D-048); `touch-action: pan-y`; test on a real touch device before relying on it. |

## 15. Verified facts

All in `docs/dev/HA_API_NOTES.md` with source, version, date, status. Phase 4 facts N-14, N-38 to N-41 are verified; N-42 (one failed first load after a restart) has no known cause. Unverified but not needed: N-17, N-21. N-22 (domain collision) open until release.

## 16. Documentation plan

Claude-facing: `CLAUDE.md`, `.claude/rules/{backend-python,frontend-card,docs-style,tests}.md` (`paths:` frontmatter, verified syntax: YAML list of globs, only field read), `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`, `docs/dev/{HA_API_NOTES,STATE,DEV_ENVIRONMENT,TESTING,RELEASE}.md`.

Human-facing: `README.md`, `docs/{actions,card,examples,troubleshooting,limitations,uninstall,upgrading}.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`.

README screenshots (from dev HA): one image with a warning and a critical banner in light theme, one in dark theme, one GIF of a banner disappearing when its condition entity turns off.

HA documentation rules covered: `docs-high-level-description` (README intro), `docs-installation-instructions` (README), `docs-removal-instructions` (`uninstall.md`), `docs-actions` (`actions.md`), `docs-configuration-parameters` (`card.md`, options in README), `docs-installation-parameters` (none: config flow has no input; stated), `docs-examples` (`examples.md`), `docs-known-limitations` (`limitations.md`), `docs-troubleshooting` (`troubleshooting.md`), `docs-use-cases` (`examples.md`), `docs-data-update` (README: push via WebSocket, no polling).

`docs-check`: banned-word and placeholder grep over all Markdown (done); YAML examples in user docs validated against action schemas (done); field parity schema == `services.yaml` == `docs/actions.md` (done); card config keys (`CONFIG_KEYS` in the card module) vs. the options table in `docs/card.md`, and card YAML examples use only those keys (done).

Adopted style elements: D-002.

## 17. Watch rules (Phase 8)

Status: implemented 2026-10-25 (tests `tests/test_rules.py`, `tests/test_rules_flow.py`; dev HA 2026.9.4 via `dev/smoke.py rules`). Details that §17.3 did not fix: rule banner IDs are `rule_<subentry_id>`; subentry IDs are uppercase ULIDs, which the lowercase `id` pattern of the actions rejects, so no action can overwrite or clear a rule banner (`tests/test_rules.py`). Editing a rule rebuilds its banner (dismissals reset, `created_at` kept); no event fires when an edit leaves the banner active. `show_all` also lists enabled rules whose condition is false (`active: false`), like waiting stored banners. Setup fires no events. Design choices are D-052 to D-058; remaining open details are in `docs/OPEN_QUESTIONS.md` ("Phase 8: watch rules").

### 17.1 Problem
A banner exists only after `create_banner` ran, and `condition` belongs to a stored banner. "Show a message while entity X is on" therefore needs an automation (§1). Putting the rule in card YAML means repeating it on every card and dashboard. The goal is a rule defined once, shown on every Heads Up card.

### 17.2 Requirements
| ID | Requirement |
|---|---|
| W-1 | A rule names one entity, the state(s) that trigger it (default `on`, optional attribute, same matching as §4.1 `condition`), a message, a severity, and optional person targeting. |
| W-2 | While the condition is true, every targeted user sees the banner on every Heads Up card, with no card configuration. |
| W-3 | A rule banner has no timeout. By default it has no X button and no swipe dismissal; a rule with `dismissible: true` can be dismissed per user (D-056). It leaves when the condition is false, the rule is disabled or the rule is deleted. |
| W-4 | Rules are created, edited and deleted in the integration's UI. No automation, script or YAML. |
| W-5 | Rules survive restarts without extra storage and need no restart when changed. |
| W-6 | Purely additive: no other integration, automation or script is touched. |

### 17.3 Design
- **Storage:** one config subentry per rule (type `rule`) of the single config entry. HA keeps `entry.subentries` in `.core.config_entries`; `.storage/heads_up.banners` is unchanged. Subentry fields: `entity_id`, `state` (string or list, default `on`), `attribute?`, `message`, `title?`, `severity` (default `warning`), `icon?`, `people?` (person entities), `dismissible` (default false, D-056), `enabled` (default true). `message` may contain `{name}` (D-055) and Home Assistant templates (D-063). The subentry `title` is the rule name shown in the UI. `unique_id` is not set, so two rules may watch the same entity.
- **Flow:** `HeadsUpConfigFlow.async_get_supported_subentry_types` returns `{"rule": RuleSubentryFlow}`. `RuleSubentryFlow` has `async_step_user` (add) and `async_step_reconfigure` (edit); delete is HA's built-in subentry menu entry. Validation reuses the `condition` rules of §4.1 (entity must exist when the rule is saved). Strings go under `config_subentries.rule` in `strings.json` and `translations/en.json`.
- **Virtual banners:** the manager builds one in-memory `Banner` per enabled rule with `id = "rule_<subentry_id>"`, `dismissible` from the rule, `dismiss_scope = "user"`, `expires_at = None`, `condition = {entity_id, state, attribute}`, `tag = "rule"`, and `condition_met` evaluated from the live state. They are never written to the store, never evicted and never counted against `max_banners`. They are rebuilt on setup and when the update listener reports a subentry change.
- **Condition tracking:** `_refresh_tracking` adds the rule entities and rule `people` to its entity set (still one listener, N-7). `_on_state_change` re-evaluates rule banners the same way as stored ones, without the `once` removal branch.
- **Delivery:** `visible()` returns stored banners plus active rule banners that target the viewer. `to_client` is reused; rule banners add `rule: true` to the payload, and the card hides "Clear for everyone" for them (`controlsFor`). `heads_up/dismiss` and `dismiss_many` on a rule ID follow the rule's `dismissible` flag (`not_dismissible` / skipped when false). A dismissal is added to the in-memory `dismissed_by` of the virtual banner and cleared when the condition turns false (D-056); it is not stored. `heads_up/admin_clear` on a rule ID is rejected with a new error `rule_banner` (message: disable or delete the rule). `clear_banner` and `clear_all` do not touch rule banners.
- **Sensor:** `sensor.heads_up_active_banners` counts active rule banners too (D-054).
- **Unavailable or unknown entity:** the rule banner is hidden (D-053).
- **Events:** `heads_up_banner_created` when the condition turns true, `heads_up_banner_cleared` with `reason: rule` when it turns false or the rule is disabled or deleted, `heads_up_banner_dismissed` (`scope: user`) on a dismissal (D-058).
- **Card:** no change required. Disabled and deleted rules produce no banner, also with `show_all`.

### 17.4 Blast radius
Restart: not needed for rule changes; a code update needs the usual restart. Notification path: not touched (the banner stream is the same). Dashboard: every Heads Up card shows rule banners once a rule exists. New files: `rule_flow` code in `config_flow.py`, a `Rule` model, changes in `manager.py`, `websocket.py` (error code) and `sensor.py`. Reversible: deleting all rules returns the previous behaviour.

### 17.5 Test plan
Tests are written before the code, in `tests/test_rules.py` unless noted.
- Flow: add a rule (defaults), add with all fields, entity missing → `entity_not_found`, reconfigure, delete, second rule on the same entity, abort when the entry is not loaded (`tests/test_config_flow.py`).
- Visibility: condition true → banner in `visible()` for an untargeted user; false → gone; state list and `attribute`; `people` targeting (user with and without a person, as in `tests/test_people.py`).
- Lifecycle: disabled rule shows nothing; deleting a rule removes the banner and updates subscribers; editing the message updates it without reload; entity removed or unavailable → hidden; `{name}` replaced; dismissible rule: dismissal hides it for that user only, it returns after the condition goes false and true again, and it returns after a reload; events (created on true, cleared with `reason: rule` on false, disabled and deleted, dismissed).
- Restart: reload the entry with the entity already on → banner present, nothing written to `.storage/heads_up.banners`.
- Interplay: stored banners and rule banners in one `visible()` list; `max_banners` eviction ignores rule banners; the count sensor includes active rule banners.
- WebSocket: payload shape equals a stored non-dismissible banner; `dismiss` and `dismiss_many` on a non-dismissible rule → `not_dismissible` / skipped, on a dismissible rule → dismissed for that user; `admin_clear` → `rule_banner`; `clear_all` and `clear_banner` leave rule banners.
- Real instance: extend `dev/smoke.py` with a rule on `input_boolean.test_window`: turn on → banner for admin and `dev-user` over WebSocket, no X in the card, turn off → gone, container restart with the helper on → banner returns. Card check in the browser pane on one existing dashboard view (no card edit needed).
- Gates: `make check`, `make hassfest` (new `config_subentries` strings), `make docs-check` (new user page section and any YAML example).

### 17.6 Documentation to change when built
`docs/DESIGN.md` §0, §4, §6, §8, §10; `docs/DECISIONS.md`; `docs/dev/HA_API_NOTES.md`; `docs/dev/TESTING.md`; `README.md` and a "Watch rules" section in `docs/examples.md` (set up in the UI); `docs/limitations.md` (rule banners cannot be cleared by admins; dismissals reset on restart); `docs/uninstall.md` (rules are removed with the entry); `CHANGELOG.md`; `docs/dev/STATE.md`.

### 17.7 Alternatives not chosen
Label-based watching (a label on an entity adds a banner with the entity name): not in Phase 8 (D-057), kept in `docs/OPEN_QUESTIONS.md`. Card-level rules: repeated per card. YAML in `configuration.yaml`: needs a reload and breaks D-026.

## 18. Condition operators (Phase 9)

Status: implemented 2026-10-25 (`tests/test_operators.py`). Decisions D-060, D-061. Rule subentries store `operator` (new rules always, `equals` by default); the virtual banner condition carries it only when it is not `equals`. Rule flow error codes: `state_count`, `state_not_numeric`, `state_required`.

### 18.1 Problem
A condition matches only when the state (or attribute) equals one of the listed values. "State is not on", "temperature above 25" and "message contains error" need an automation with a template, or cannot be expressed in a rule at all.

### 18.2 Design
- **Field:** `condition.operator`, one of `equals` (default), `not_equals`, `above`, `below`, `between`, `contains`, `not_contains`. The action schema and the rule form both have it. A condition without `operator` is stored and evaluated as before; the key is not added.
- **State by operator:** `equals`, `not_equals`, `contains`, `not_contains` take a string or a list (default `on` only for `equals` and `not_equals`; `contains` and `not_contains` require a value). `above` and `below` take exactly one number. `between` takes exactly two numbers, low then high, both inclusive. Numbers are accepted as numbers or numeric strings.
- **Matching:** the value is the state, or the attribute as text. `equals`: in the list. `not_equals`: not in the list. `contains`: any listed text is a substring. `not_contains`: no listed text is a substring. Numeric operators parse the value as a float.
- **No real value:** `unavailable`, `unknown`, missing entity: not evaluated (unchanged). For the new operators a missing attribute, and for numeric operators a non-numeric value, are also not evaluated (D-061). `equals` with a missing attribute stays false.
- **Validation:** one function checks the operator against `state` and returns an error code (`state_count`, `state_not_numeric`). The action schema turns it into `vol.Invalid`; the rule flow shows it on the `state` field.
- **Module:** `custom_components/heads_up/conditions.py` holds `OPERATORS`, `check_state` and `matches`; `Manager._evaluate` calls `matches`. `_build_rule` copies `operator` into the virtual banner's condition.
- **Card:** no change; conditions are evaluated in the backend.

### 18.3 Blast radius
Restart: a code update needs the usual restart. Notification path: not touched. Dashboard: none by itself. Existing banners and rules are unchanged (no `operator` means `equals`). New rule field is stored in subentry data; old subentries without it keep working.

### 18.4 Tests
`tests/test_operators.py`: matcher per operator, boundaries, lists, attribute, text vs number, non-numeric and missing values, unavailable with `not_equals`; action schema accepts and rejects (counts, non-numeric); stored banner with `not_equals` shows and hides; rule flow with operator, error codes, defaults, reconfigure of an old rule.

## 19. Condition `for` and template conditions (Phase 10)

Status: implemented 2026-10-26 (`tests/test_for_template.py`). Decisions D-066, D-067. Not built: `at_least` and `at_most` operators (dropped by the maintainer, D-066).

### 19.1 Problem
A condition reacts the moment an entity matches. "Door open for 5 minutes" needs an automation with a timer. A condition on several entities, or on time of day, needs an automation as well.

### 19.2 Design
- **`for`:** optional on a condition. Action input is any time period (dict, `HH:MM:SS`, seconds), stored as whole seconds; 0 is dropped; the maximum is 24 hours (`MAX_FOR_SECONDS`). A watch rule stores `for` in its subentry data as seconds; its form uses a duration selector.
- **Wait:** `_effective` turns a true result into "not yet" and starts an `async_call_later` timer per banner or rule (`_for_timers`). A false result cancels the timer. A true result while the timer runs, or while the banner is already shown, changes nothing, so attribute updates do not restart the wait. When the timer fires, the condition is evaluated again; only a still true, real result shows the banner (`elapsed`). An unavailable entity at that moment shows nothing and the wait restarts at the next matching state.
- **Where the timer is cancelled:** the banner is replaced, cleared, expires or is evicted (`_remove`); the manager unloads; a rule is rebuilt or removed.
- **Restart:** timers are not stored. A banner stored as shown stays shown. A waiting banner, and a rule that is true at setup, start the wait again (D-066). A rule that becomes true after its wait fires `heads_up_banner_created` and sets `updated_at` then. Setup finds the state without events (D-058), the later flip is an event.
- **Rules and unavailable:** a rule treats an unreadable result as false (D-053), so it also cancels the wait.
- **`create_banner` response:** a banner whose condition is true but still waiting has status `waiting`. With `wait_for_condition: false` it is not stored (`condition_false`).
- **Template condition:** `condition.template` (string, not empty, must parse) replaces `entity_id`, `operator`, `state` and `attribute`; mixing them is a validation error. The result is the template's boolean (`result_as_boolean`). `for` can be added. A render error gives no result: unchanged, like an unavailable entity (D-061). The entity-exists check of `create` applies to `entity_id` conditions only.
- **Tracking:** `async_track_template_result` per banner with a template condition (`_template_trackers`), set up in `create` and `async_load`, removed with the banner. It re-evaluates when entities read by the template change and for time functions, which the state listener could not do (D-067). Rule messages keep their own entity tracking (D-063).
- **Card and payloads:** unchanged; `condition` is never sent to the card.

### 19.3 Blast radius
Restart: a code update needs the usual restart. Notification path: not touched. Dashboard: banners with `for` or a template condition appear later or by other rules than before; nothing existing changes (no `for` and no `template` behave as before). Storage: stored banners may contain `template` and `for` in `condition`; older versions of the integration would fail on a banner without `entity_id` (a downgrade after using templates should clear them).

### 19.4 Tests
`tests/test_for_template.py`: schema (seconds, text, zero, limits, template rules), wait and restart of the wait, reload with a shown banner, replace, clear, `once` mode, operators with `for`; template show/hide, recurring, several entities, errors, `for`, reload, tracking stops; rules with `for` (wait, time, cancel, setup, delete, edit); rule flow (`for` as seconds, omitted, zero, too long).

## 20. `empty` and `not_empty` operators (Phase 11)

Status: implemented 2026-10-27 (`tests/test_empty_operators.py`). Decision D-068.

### 20.1 Problem
"The entity has some value" had no direct form. `not_equals` with `state: ""` worked in an action, but the rule form replaced an empty State with `on` (schema default and fallback) and dropped blank entries, so a rule could not express it.

### 20.2 Design
- **Operators:** `empty` and `not_empty` (`NO_STATE_OPERATORS` in `conditions.py`). They look at the value only; `state` is not required and is dropped from the stored condition if given (action schema, rule form).
- **Value:** the state, or the attribute as text. Empty means no text after stripping spaces. A missing (`None`) attribute and an empty list, object or tuple count as empty. `unavailable`, `unknown` and a missing entity give no result, as for every operator (D-061); the missing attribute is the one case with a result, because an absent value is what `empty` asks about.
- **Rule form:** the State field has no prefilled value. For `equals` and `not_equals`, an empty field (or blanks) still means `on` (D-068); for `empty` and `not_empty` nothing is stored under `state`. The virtual banner's condition carries no `state` for them.
- **Compatibility:** stored rules and banners are unchanged. `for` and templates are not affected.

### 20.3 Blast radius
Restart: the usual one after a code update. Notification path: not touched. Dashboard: none by itself. Rule subentries with these operators have no `state` key; an older version of the integration would fail to build them (a downgrade after using them should delete such rules).

### 20.4 Tests
`tests/test_empty_operators.py`: matcher, schema, banners (shows, hides, unavailable, attribute, `for`), rules (state, attribute), rule form (no prefilled State, no stored state, `equals` default kept, reconfigure).

## 21. Banner buttons and snooze (Phase 12)

Status: implemented 2026-10-27 (`tests/test_snooze.py`, `tests/test_actions.py`, vitest, `dev/smoke.py snooze`). Decisions D-069, D-070.

### 21.1 Problem
A viewer could only close a banner for good, and a banner could not lead to anything an automation could react to. "Remind me later" and "I did it" had no form.

### 21.2 Design
- **Snooze fields:** `snoozable` (bool), `snooze_scope` (`user` or `global`), `snooze_options` (1 to 6 durations, 1 minute to 7 days, stored as seconds). Defaults come from the integration options `default_snoozable` (off), `default_snooze_scope` (`user`) and `default_snooze_options` (15 min, 1 h, 4 h). A banner that is not dismissible is never snoozable: an explicit `snoozable: true` with `dismissible: false` is a validation error, and the option default is ignored for it.
- **Snooze state:** `snoozed_until` maps a user ID, or `*` for a global snooze, to an end time. It is stored with the banner. `Banner.snoozed_for(user_id)` gives the end that hides the banner from that user. `visible()` leaves a snoozed banner out (not with `show_all`, which flags it with `snoozed`). One `async_track_point_in_utc_time` timer per entry removes it and updates the cards; setup drops ended entries and re-arms the rest.
- **What ends a snooze:** its end time; an upsert (the new banner has none, like `dismissed_by`, D-010); a recurring condition turning false and true again; removal of the banner. For a rule, the condition turning false. The timeout and the condition keep running while a banner is snoozed.
- **WebSocket `heads_up/snooze`** (`banner_id`, `seconds`): `seconds` must be one of the banner's options (`invalid_snooze`), the banner must be snoozable (`not_snoozable`). Only a person the banner is addressed to can call it (`not_targeted` otherwise, D-156). Fires `heads_up_banner_snoozed` with `id`, `tag`, `scope`, `user_id`, `until`.
- **Ending a snooze early (D-074):** WebSocket `heads_up/unsnooze` (`banner_id`) removes the snooze that hides the banner from the caller, and a global one for everyone (`not_snoozed` when there is none, `not_targeted` for a user the banner is not addressed to, D-156). It cancels the timer and fires `heads_up_banner_unsnoozed` with `id`, `tag`, `user_id`. `heads_up/subscribe` takes `show_snoozed` (default false): the list then also holds the viewer's snoozed banners, flagged `snoozed` with `snoozed_until`. Card key `show_snoozed` (off) adds a "Snoozed (n)" list with the time left and a Show now button; the same for action and rule banners (D-073).
- **Buttons:** field `actions`, up to 3 entries `{key, label, dismiss?, action?}`. `key` follows the ID pattern and is unique in the banner, `label` has 1 to 40 characters, `action` is a mapping with an `action` key (as `tap_action`), `dismiss` defaults to false and is rejected with `dismissible: false`. The card receives the whole list.
- **WebSocket `heads_up/action`** (`banner_id`, `key`): fires `heads_up_banner_action` with `id`, `tag`, `key`, `user_id`; with `dismiss` it then dismisses for that user. Errors: `unknown_action`, `not_found` (also for a banner targeted at other people), `message_ended` (D-125). The backend never runs `action`; the card does, after the call succeeds, with the same `hass-action` event as the tap action, so HA handles confirmation and the viewer's permissions (N-38).
- **Watch rules:** the rule form has Snoozable, Snooze scope and Snooze choices (minutes in the form, seconds in the subentry); unset fields use the option defaults; Snoozable needs Dismissible (`snoozable_needs_dismissible`). Rules got buttons and a tap action in §22. A rule's snoozes are not stored, like its dismissals.
- **Card:** no new config key. A banner with `snoozable` and choices gets a snooze button (48 px, `aria-label`) that opens a row of choices under the banner; Escape closes it. With `swipe_to_dismiss`, a right swipe on a snoozable banner opens the same row and a left swipe dismisses; on other banners both directions dismiss as before (`swipeOutcome`). Buttons are text buttons under the message; the compact layout hides them. The card sends `snoozable`, `snooze_options`, `snoozed`, `snoozed_until` (the viewer's own end, null when not snoozed) and `actions`; `snooze_scope` stays server-side.

- **Ended messages (D-125):** option `disable_ended_buttons` (default on). With it on, `BannerManager.press` refuses with `message_ended` when the pressing user dismissed the message or it was dismissed for all, when anyone acknowledged it, or when its condition is not true. A snooze does not end it. One check in `press`, so card, popup, push and rule banners behave alike (§22). A removed message has no record to check the sender against, so it stays `not_found`.

### 21.3 Blast radius
Restart: the usual one after a code update. Notification path: not touched. Dashboard: nothing changes for existing banners (`snoozable` is off by default, no buttons). Banners that set the new fields show a snooze button or text buttons. Options: three new keys, filled with defaults when missing. Storage: stored banners gain `snoozable`, `snooze_scope`, `snooze_options`, `snoozed_until` and `actions`; an older version of the integration would fail to load them (a downgrade after using these fields should clear the banners). New events: `heads_up_banner_snoozed`, `heads_up_banner_action`.

### 21.4 Tests
`tests/test_snooze.py`: default off, per-user and global scope, expiry timer, choices, not-dismissible rules, limits, upsert, recurring flip, restart, snooze ended during downtime, `show_all` flag, options flow. `tests/test_actions.py`: payload, event, dismiss button, unknown key, targeted banner, upsert, invalid input, restart. `tests/test_rules.py` and `tests/test_rules_flow.py`: rule snooze and form. vitest: `controlsFor`, `snoozeLabel`, `swipeOutcome`. `dev/smoke.py snooze` and `snooze_verify`: per-user snooze, dismiss button and persistence over a container restart on the dev HA.

### 21.5 Speech areas and the missing-speaker entry (D-126)
- Direct areas: `to.speak.recipients` takes any area id or name (`recipients.find_area`, `HubResolver.accepts`). `known("speak")` lists every area id.
- Bell entry: `HubEngine._send` calls `persistent.warn_speech` when a speak row is skipped with `group_empty` or fails with `entity_missing`. Not on a dry run (`plan`, `preview`) and not on a startup resume. Id `heads_up_warning_<slug>`, so a repeat replaces it; text names the area, group or speaker, never the message.

### 21.6 Image (D-127)
- Field `image` on `create_banner`, `notify`, `push`, `popup` and in the rule form; `Banner.image`; shape checked by `services.IMAGE` (http(s) URL or `/path`, up to 2048 characters). Push: `data.image` when the lock screen setting is `full`, otherwise left out with the note `image_hidden`. Card (not compact) and popup: an `<img>` under the message; `/api/` and `/media/` paths go through `auth/sign_path` (N-93), kept 50 minutes. The duplicate signature of `hub/limits.py` includes the image.

### 21.7 Delivery-failed event (D-128)
- `HubEngine._report` fires `heads_up_delivery_failed` after each `_send` (origins `message`, `escalation`, `fallback`, `deliver`) and each reminder round. One event per non-banner channel that had a `failed` outcome or a skip in `NOBODY_REASONS`, with `reached`, and `failed` as `{recipient, reason, person?}`. Not fired on the first delivery after a restart (`resume` with origin `message`), not on `plan` or `preview`. Duplicates, quiet hours, holds, cooldown are choices and fire nothing.

### 21.8 Mail channel (D-129)
- `hub/channels/mail.py` `MailChannel`: capabilities title, per user, no buttons, no clear, no replace. `deliver` renders `mail_subject` and `mail_body` (`{name}` placeholders, `check_template`) and calls `notify.<mail_service>` with `title`, `message`, `target`. Recipients come from `HubResolver`: persons whose profile has `mail` in `channels` and a `mail_address` (`Skipped no_mail_address` otherwise), and `Global address` (key `mail:global`, address from `mail_global_address`). `PROFILE_CHANNELS` gains `mail`; `DEFAULT_PROFILE_CHANNELS` stays banner, push, popup. `NOBODY_REASONS` gains `no_mail_address`.

## 22. Parity of banner sources (rule, D-073)

Status: implemented 2026-10-27 (`tests/test_rule_parity.py`, `tests/test_rules_flow.py`). Decision D-073.

### 22.1 Rule
A banner comes from one of two sources: the action `create_banner` (stored) and a watch rule (virtual, §17). Both must offer the same features to the viewer and the producer. A phase that adds or changes a banner feature ships it for both sources, or lists the missing side as an exception below with a decision number. `docs/dev/PHASE_PROMPT.md` checks this at the end of every phase, and the card never needs to know the source (only `rule: true` hides "Clear for everyone").

How both sources stay equal:
- The rule form validates input with the schemas of the action (`ACTIONS_SCHEMA`, `TAP_ACTION_SCHEMA` in `services.py`), so a button or tap action means the same thing in both.
- Rule banners are built by `_build_rule` into the same `Banner` model; the manager methods for dismissal, snooze, button presses and delivery (`dismiss`, `snooze`, `press`, `visible`) work on `rules` and `banners` alike.
- Each source has a test for every feature in the table.

### 22.2 Feature table
| Banner feature | Action | Rule |
|---|---|---|
| message (`{name}` and templates in rules, D-055, D-063), title, severity, icon, people | yes | yes |
| dismissible | yes | yes |
| dismiss scope | `user` or `global`, option default | `user` or `global`; a rule without the field stays `user`, whatever the option says (D-073) |
| snooze (flag, scope, choices) | yes | yes |
| buttons (`actions`) | yes | yes (Buttons field, YAML) |
| tap action | yes | yes (Tap action field, YAML) |
| condition on an entity (operators, `for`) | yes | yes |
| template condition | yes | yes (Template field; replaces the entity) |
| `id`, `tag`, `timeout`, `mode`, `wait_for_condition` | yes | exception: a rule's lifetime is its condition; its tag is `rule`; its mode is recurring (D-052, D-056) |
| clear by action or by an admin | yes | exception: the rule is disabled or deleted instead (D-056) |
| stored over a restart (banner, dismissals, snoozes) | yes | exception: a rule is rebuilt from its subentry; dismissals and snoozes are not kept (D-056, D-069) |
| hub delivery (channels, a target per channel, a named policy) | yes (`notify`) | exception: a rule is a banner-channel message; other channels come from policies, by severity and tag `rule` or by the rule's Policy field (D-100, D-146) |
| acknowledgement (card button, push button, `heads_up/acknowledge`), escalation and reminder by policy | yes | yes: the policies of the tag `rule` apply, and the acknowledgement starts again each time the condition turns false and true |
| rate limits and ignored identical updates (D-123) | yes, on every delivery | yes, on every delivery that a policy makes for a rule message |
| Deliver, Quiet hours, Away, Fallback and Summarize policies (D-121) | yes | yes, by severity and tag `rule` (D-100); a Summarize policy holds a rule message on every channel |
| panel Test send and trace | yes (message id) | trace yes (`rule_<id>`); Test send previews a call, not a stored rule |
| buttons stop acting once the message has ended (D-125) | yes | yes (one check in `BannerManager.press`; `tests/test_ended_buttons.py`) |
| image under the message (D-127) | yes | yes (Image field of the rule form; `tests/hub/test_image.py`) |
| `heads_up_delivery_failed` (D-128) | yes | yes for the deliveries a policy makes for a rule message, same engine path (no rule-specific test); the banner channel never fires it |
| Policy field: name one policy or `none` (D-146) | yes (`policy`) | yes (Policy field of the rule form; `tests/test_rules_flow.py`) |
| a switched-off recipient gets nothing (D-147) | yes (named persons are dropped from the banner's people; all dropped means nobody) | yes (the rule's `people` are filtered when the rule is built and again when a profile changes, D-161; `tests/hub/test_recipient_disabled.py`) |

Audit for the hub (H10, 2026-11-02), extended 2026-11-05: every banner feature above is in both columns or carries an exception with a decision number.

### 22.3 Details of the rule additions
- **Buttons and tap action:** subentry fields `actions` (list, up to 3, normalized with `dismiss: false` defaults) and `tap_action`. A rule's button presses fire `heads_up_banner_action` with `id = rule_<subentry_id>` and `tag = rule`. A button with `dismiss` needs a dismissible rule (`actions_dismiss_needs_dismissible`).
- **Dismiss scope:** `global` on a rule keeps the banner hidden for everyone until its condition turns false, because a rule banner cannot be removed. The marker is `*` in `dismissed_by`, as `*` is the global key of snoozes; it is cleared with the other dismissals when the condition flips. `heads_up_banner_dismissed` fires with `scope: global`.
- **Template condition:** subentry field `template` replaces `entity_id`, `operator`, `state` and `attribute` (the form accepts exactly one of entity and template). `for` works with it. The manager tracks it with `async_track_template_result` (`_template_trackers`) like a template condition of an action; `_template_changed` re-evaluates a rule through `_apply_rule`. An unreadable result hides the banner (D-053). `{name}` in the message is the rule name when there is no entity. The subentry title reaches the manager as `rule_name` in the rule source.
- **Form errors:** `entity_and_template`, `entity_or_template_required`, `template_invalid`, `actions_invalid`, `tap_action_invalid`, `actions_dismiss_needs_dismissible`. The Template field is plain multiline text, not the template selector, because the selector rejects a bad template before our error message.

### 22.4 Blast radius
Restart: the usual one after a code update. Notification path: not touched. Dashboard: existing rules look the same (new fields are optional; an unset dismiss scope is `user`). Subentries with a template have no `entity_id`; an older version of the integration would fail to build them, and a downgrade after using these fields should delete such rules. Same for rules with buttons: older versions ignore the field.

### 22.5 Tests
`tests/test_rule_parity.py`: rule payload with buttons and tap action, button event and dismissal, unknown key, global dismissal until the condition flips, default scope, template rule (follows, `{name}`, `for`, tracking removed on delete). `tests/test_rules_flow.py`: template stored without entity fields, one of entity and template, invalid template, buttons and tap action stored as the action stores them, invalid input, dismiss button needs a dismissible rule.



## 23. Notification hub (Phase 15)

Status: built on the branch `hub/h9e-wizard`, a chain of feature branches from H1 to H9e (D-107, 2026-10-30) with later maintainer changes. Pre-releases 1.0.0-alpha.2 to 1.0.0-alpha.5 are tagged and pushed (D-133, D-154). `main` is at 0.4.0 and holds nothing of the hub; the maintainer merges and tags 1.0.0 (D-020, `docs/dev/RELEASE.md`). Decisions D-075 to D-159; `docs/dev/hub/DECISION_INDEX.md` lists which decisions are current and which are superseded. This section is the consolidated design. The UI is specified in `docs/dev/hub/UX_SPEC.md` (with the mockup `docs/dev/mockups/hub-panel-mockup.html`), the work breakdown in `docs/dev/hub/ROADMAP.md`. `docs/dev/HUB_DESIGN.md` is the historical planning record and contains superseded text.

### 23.1 Problem
Automations hard-code notify services, speaker entities, quiet-hour templates and clean-up logic. Replacing a phone means editing every automation. A critical alert nobody read, a doorbell with nobody home, a push dismissed on one device and still shown on a wall tablet: each is handled ad hoc, with no shared state.

### 23.2 Principles
- Today's banner delivery is the foundation. The hub adds channels and features; the banner is one channel (D-077).
- Everything that exists works without the hub (D-076): `create_banner`, `clear_banner`, `clear_all`, watch rules, the card. Without a policy a message goes to the channels the call names.
- A message has one id for all channels; state changes on one surface apply to every channel (D-078).
- Parity (rule 9): action messages and rule messages offer the same features.
- Delivery never blocks creation; failures show in the trace.
- The hub is always on (D-139; the option `hub_enabled` of D-107 was removed, a stored value is ignored). A message that names no hub channel and matches no policy is delivered exactly as before. The panel's sidebar entry is chosen by the user during initial setup (option `show_panel`, off by default).
- UI-first households and power users are served equally: the same objects are created in the panel, in the setup wizard, in the standard forms, and used from automations as plain actions.

### 23.3 Concepts
| Concept | Meaning |
|---|---|
| Message | The unit a producer creates; owns the lifecycle (timeout, condition, dismiss, snooze, acknowledgement). |
| Channel | An output surface: banner, push (Companion app), popup, speak, persistent notification. |
| Audience | People-based, channel-neutral, flat (D-079): persons, or a presence kind. Built in: Everyone, Admins, At home, Not home, Last to leave, First home. |
| Recipient group | A named set of explicit targets (speakers, Assist satellites, areas, notify targets), tied to channels (D-088). |
| Recipient profile | Per person: detected devices, manual overrides, primary device, accepted channels (D-088). |
| Policy | One small typed rule (D-097): Escalation, Quiet hours, Fallback, Reminder, Away or Summarize, with a trigger and an effect and an optional "Applies to" (severities, tags). |
| Channel settings | One settings page with defaults by severity: push level and lock-screen text, buttons, popup style, speech language. |
| Delivery | One message, one recipient, one channel, with a state: planned, held, sent, skipped, failed, cleared. |

### 23.4 Actions and fields (D-083, D-087)
- `heads_up.notify`: content `message` (required), `title`, `icon`, `severity`, `actions`, `tap_action`, `tts_message`; lifecycle `id`, `tag`, `timeout`, `condition`, `mode`, `wait_for_condition`, `dismissible`, `dismiss_scope`, `snoozable`, `snooze_scope`, `snooze_options`; delivery `channels` (required list), `to` (a target per channel: `audience` or `recipients`, never both, kinds depend on the channel, D-098), `policy` (omitted: all that apply; `none`: no policy behavior).
- Shortcuts `push`, `popup`, `speak`: fixed channel, optional audience or recipients, no escalation; fire and forget without an `id`, a tracked message with one. `create_banner` is unchanged and keeps `people`.
- One generic clear removes a message from every channel. Response: `id`, `status` (`created`, `updated`, `waiting`, `condition_false`) and per channel counts of `sent`, `held`, `skipped`, `failed`.
- Watch rules are frozen (D-100): they keep working as released, deliver to the banner channel and get no channels or targets. Policies still apply to their messages by severity and tag.

### 23.5 Recipients per channel (D-090, D-091)
| Channel | `audience` | `recipients` |
|---|---|---|
| banner | yes | persons (empty: everyone) |
| push | yes | persons, notify targets or devices |
| popup | yes | persons only in the first version |
| speak | no | recipient groups, media players, Assist satellites, areas |
| persistent | no | none (targets everyone) |

### 23.6 Policies (D-097)
A policy is one rule: type, When, Then. All policies that apply to a message (by severity and tag) are active together.

| Type | When | Then |
|---|---|---|
| Escalation | nobody acknowledged within X minutes | also notify an audience or recipients on channels; setting: dismissing counts as acknowledging |
| Quiet hours | a message is sent between two times (days selectable) | wait until the end, send quietly, or drop; setting: critical passes |
| Fallback | the audience is empty or sending failed | send to an audience or recipients on channels instead |
| Reminder | still not acknowledged | repeat every X minutes, up to N times |
| Away | a recipient is not home | send when they arrive, while the message is active |
| Summarize | messages arrive | hold all channels including the banner (D-105), send one summary every N minutes or at a fixed time (count, titles, resolved marked, cut at 10) |

```yaml
policy:
  name: Water escalation
  type: escalation
  applies_to: {severities: [critical], tags: [water]}
  after: 5
  notify:
    channels: [push, speak, persistent]
    to:
      push: {audience: Admins}
      speak: {recipients: [Ground floor speakers]}
  dismiss_counts: true
```
- Common fields: `name`, `type`, `applies_to` (empty means all), `enabled`. There is no "only if" condition and there are no named conditions in the first version (D-099).
- A second policy of the same type with identical `applies_to` and trigger is refused. Precedence on one delivery (D-106): Summarize, Quiet hours, Away, Fallback; escalations, reminders and the summary itself are deliveries that pass through the same chain.
- A summary (D-106) takes the highest severity of its messages, goes to the channels and targets the held messages would have used (one per recipient and channel), and stays until dismissed or 24 hours. There is no default delivery by severity: calls always name their channels.
- The first delivery (channels and a target per channel) always comes from the call. Escalation and Fallback name their own channels and a target for each (D-098).
- Acknowledgement: any recipient stops escalation and reminders. Snooze clears the user's push, pauses their reminders and notifies again when it ends. A severity change restarts escalation and reminders with the policies of the new severity. An overdue escalation fires once after a restart if the message is active and unacknowledged.
- The lifecycle condition ending the message clears every channel and cancels all policies for it.

### 23.7 Audiences and devices (D-080, D-088)
Presence audiences read the person state (`None`, `unknown` and `unavailable` count as unknown, N-63). Membership is a snapshot when a delivery is made (a call, an escalation, a reminder or a summary); people not yet home get the delivery on arrival through the Away policy. Companion devices are found from the person's trackers with manual override (read from source, N-70 and N-71; not run on a device). The hub stores a device's `device_id`, never its notify service name: the app can rename a device, which renames the service (N-78), and the service is resolved from the registration's `device_name` at send time. All devices of a person are notified under one tag. Unknown presence: critical notifies, lower severities skip with a trace entry. A person without a usable device is skipped on push and flagged in the panel. Built (H2, D-109): Last to leave and First home change after a presence delay (option, 60 seconds, 0 for none), their state is stored in `heads_up.presence`, and the set of people at home is recomputed at start; a profile exists for every person without setup and a profile subentry only holds changes; an area stands for the speakers assigned to it in Home Assistant.

### 23.8 Channels (D-090, D-091, D-092)
- Push: legacy `notify.mobile_app_*` services only (N-61); tag `hu-<install token>-<message id>`; clear with `clear_notification`; severity maps to passive, normal, time-sensitive (iOS critical is a policy opt-in); buttons are the message's own, then Dismiss and Snooze when allowed, and Acknowledge when an escalation or reminder policy applies; button ids `hu:<message>:<recipient>:<action>` (the action event is never relied on for the tag or other data, N-79); Snooze uses the first snooze option; swiping a push away changes nothing.
- Popup: global loader under 1 KB, lazy popup code; corner card up to warning, centered modal for critical; one at a time.
- Speak: announce when the player's state shows the `MEDIA_ANNOUNCE` feature (N-75), else the current volume; no volume changes, no all-clear; text is `tts_message`, else the title or the message, shortened.
- Persistent notification: `persistent_notification.create` and `dismiss` with an id derived from the message.
- Banner: unchanged, plus the line "Acknowledged by <first name>" with a card option to hide it.
- Rate limits: per device and global caps per minute and duplicate suppression, defaults in the options.

### 23.9 State and restarts
A second store holds deliveries and due times; the manager emits a typed transition for every moment a message appears or disappears (today some are silent, such as a snooze ending or a condition turning true). Existing event payloads do not change. On startup the hub clears pushes of messages that no longer exist, never re-sends anything already sent, and fires overdue escalations and reminders once.

### 23.10 Admin panel (D-093)
Admin-only sidebar panel, in two levels (D-103): Overview; Notifications and Rules (Test send, Watch rules, Message Log); Configuration (Audiences, Recipients, Policies, Channels); Settings (one page with every setting, D-122, and a button that opens the introduction); Help (FAQ, Notify examples, Card examples, D-137). Own forms (`ha-form`) and pages that save through the subentry flow APIs, so storage stays in config subentries (D-119). The Overview holds counts of active notifications with their states, shortcut cards, an activity chart of the last 24 hours, needs-attention warnings that can be hidden, and the last actions (D-118, D-135, D-138). Watch rules are listed, added, edited and deleted on their own page (D-134). Test send previews who would be notified now and can send a real test message (D-120). The Message Log shows recent messages with the per-message delivery trace. The introduction is a four-step tour that creates the default policies (D-121, D-131). Panel registration without a build step is verified (N-88).

### 23.11 Blast radius
Restart: the usual one after a code update. Notification path: touched for the first time (calls to notify, tts, media player and persistent notification services of other integrations; nothing of theirs is modified). Dashboard: nothing changes until a policy or channels are used. Storage: new subentry types and a deliveries store; a downgrade must be checked for unknown subentry types. Manifest: optional integrations as `after_dependencies` (N-68).

### 23.12 Tests (later)
Fake notify, tts, media player and persistent notification services; the lifecycle × channel × source matrix; restart and overdue-step tests; presence with the time freezer (a debounce of presence changes is proposed, not decided); each policy type and their precedence; summary collection and resolved marking; button round trip with stale ids; loader size budget; translation parity; `dev/smoke.py` with stub services.

### 23.13 Alternatives not chosen
A separate integration consuming events (events lack recipients and silent transitions); automations only for delivery; one action per channel only; audiences with set operations; policy matching by explicit priority; the panel with its own storage.

### 23.14 Policy fields and channel settings (D-097)
- Escalation: `after` (minutes), `notify` (`channels` and `to`, a target per channel), `dismiss_counts`.
- Quiet hours: `from`, `to`, `days`, `action` (`wait`, `quiet`, `drop`), `critical_passes`.
- Fallback: `when` (`no_audience`, `failed`, `both`), `notify` as above.
- Reminder: `every` (minutes), `max`.
- Away: `max_wait` (default: the message lifetime).
- Summarize: `every` (minutes) or `at` (time of day), `include_critical` (default false; policy decides).
- Channel settings by severity: push `level`, `privacy`, `sticky`, `channel_id`; buttons Snooze and Dismiss, with Acknowledge when an escalation or reminder policy applies; popup `style`; speak `language`, `announce`.
- Quiet hours "quiet": push passive without sound, speech skipped, popup as a corner card.

### 23.15 Open
Whether the panel is registered through `panel_custom` or through the frontend function and which passes hassfest (N-77); the recent-messages list across restarts; the unit name in public docs; volume restore on platforms other than Sonos (N-76), the iOS action event, and a run against the dev instance; blueprints cannot be shipped by an integration (N-80); popup area recipients (not built); build phasing (delayed until the design is final). See `docs/OPEN_QUESTIONS.md`.
