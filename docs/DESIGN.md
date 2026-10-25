# Design: Heads Up

Living design document: requirements and architecture. Decisions are referenced as D-nnn (`docs/DECISIONS.md`), API facts as N-nn (row in `docs/dev/HA_API_NOTES.md`), risks as R-n (§14). Where code and this document disagree, fix one of them in the same commit.

## 0. Implementation status (2026-10-25)

| Part | Status |
|---|---|
| §4 data model, §5 lifecycle, §6 backend, §7 actions, §9 targeting | implemented and tested (Phases 2–3) |
| §17 watch rules (config subentries, virtual banners) | implemented and tested (Phase 8); card unchanged |
| §8 frontend (card, editor, serving the JS file) | implemented; pure functions tested with vitest, behaviour checked on the dev HA (Phases 4 and 7) |
| Human docs | README, `actions.md`, `card.md`, `examples.md`, `troubleshooting.md`, `limitations.md`, `uninstall.md`, `upgrading.md` done (Phase 6) |
| Packaging, release, CI run | icon, CI job for HA 2026.10.4 and `docs/dev/RELEASE.md` runbook updated; CI itself has not run, the repository is not published (D-020). README has no screenshots (D-046) |

## 1. Goals, non-goals, scope cut

Goals
- One backend that holds every in-dashboard banner; producers call actions, one card displays.
- Banner lifecycle (timeout, condition, dismiss, clear) survives HA restarts.
- No caller-specific code; the action schema is the only contract.

Non-goals
- Delivering push, TTS or mobile notifications.
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
| i18n | All UI strings in English (D-037), kept in HA translation files (`strings.json`, `translations/en.json`) and one card string table, so languages can be added without code changes. Banner text is caller-supplied and not translated. |
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
| `heads_up/dismiss` | user | `banner_id` | `{}` or error `not_found` / `not_dismissible` |
| `heads_up/dismiss_many` | user | `banner_ids` (list) | `{dismissed, skipped}`; unknown and non-dismissible IDs count as skipped; one subscriber update for the batch (D-048) |
| `heads_up/admin_clear` | admin (`require_admin`) | `banner_id` | `{}` or `not_found` / `unauthorized` / `rule_banner` (D-056) |

Banner IDs travel as `banner_id` because `id` is the WebSocket message ID.

Visibility is computed per connection from `connection.user.id`; the person whose `user_id` equals it decides targeting. Sending the full list (≤ 200 items) per change is chosen over diffs: fewer states to get wrong.

Config flow: one entry, no input (D-026). Options: `max_banners`, `evict`, `default_dismiss_scope`, `default_timeout`. Option change applies to new banners only. Removing the entry deletes `.storage/heads_up.banners` (`Store.async_remove`, N-6) in `async_remove_entry`.

## 7. Action reference

| Action | Fields | Response (`SupportsResponse.OPTIONAL`, N-3) | Errors |
|---|---|---|---|
| `heads_up.create_banner` | §4.1 | `{id, status}` with `status` `created` \| `updated` \| `waiting` \| `condition_false`; `evicted` ID if any | schema errors (`vol.Invalid`), `entity_not_found`, `too_many_banners`, `not_loaded` |
| `heads_up.clear_banner` | `id` or `tag` (at least one) | `{cleared: n}` | none (unknown id → `cleared: 0`) |
| `heads_up.clear_all` | none | `{cleared: n}` | none |

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

Status: Python tests implemented (121, files listed in `docs/dev/TESTING.md`); card pure functions tested (65 vitest tests); CI matrix job for 2026.10.4 written, CI itself not run; the 2026.10.4 run of the Phase 8 tests has not been done.

- Python: `pytest-homeassistant-custom-component` 0.13.367 = HA 2026.9.4 (N-25); CI runs the same tests on 2026.10.4 (N-46).
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
- CI (D-027): `ci.yml` runs ruff, mypy, pytest (HA 2026.9.4 and 2026.10.4), vitest and docs-check; `validate.yml` runs hassfest and the HACS action, also daily and on demand (D-051).
- Dev environment: Docker `homeassistant/home-assistant:2026.9.4` (verified, N-28), config from `dev/ha-config/`, no notify services; see `docs/dev/DEV_ENVIRONMENT.md`.
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
- **Storage:** one config subentry per rule (type `rule`) of the single config entry. HA keeps `entry.subentries` in `.core.config_entries`; `.storage/heads_up.banners` is unchanged. Subentry fields: `entity_id`, `state` (string or list, default `on`), `attribute?`, `message`, `title?`, `severity` (default `warning`), `icon?`, `people?` (person entities), `dismissible` (default false, D-056), `enabled` (default true). `message` may contain `{name}` (D-055). The subentry `title` is the rule name shown in the UI. `unique_id` is not set, so two rules may watch the same entity.
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
