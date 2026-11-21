# Design: Heads Up

Living design document: requirements and architecture. Decisions are referenced as D-nnn (`docs/DECISIONS.md`), API facts as N-nn (row in `docs/dev/HA_API_NOTES.md`), risks as R-n (§14). Where code and this document disagree, fix one of them in the same commit.

## 0. Implementation status (2026-11-19)

| Part | Status |
|---|---|
| §4 data model, §5 lifecycle, §6 backend, §7 actions, §9 targeting | implemented and tested (Phases 2–3) |
| §17 watch rules (config subentries, virtual banners) | implemented and tested (Phase 8); card unchanged |
| §18 condition operators (shared matcher for actions and rules) | implemented and tested (Phase 9); card unchanged |
| §19 condition `for` and template conditions | implemented and tested (Phase 10); card unchanged |
| §20 `empty` and `not_empty` operators, rule form without a prefilled State | implemented and tested (Phase 11); card unchanged |
| §21 banner buttons and snooze | implemented and tested (Phase 12); card checked on the dev HA with a mouse |
| §22 parity of banner sources, rule buttons, tap action, dismiss scope and template conditions | implemented and tested (Phase 12 follow-up) |
| §23 notification hub | built (Phase 15, H0 to H10 and the later maintainer changes) on the branch `hub/h9e-wizard`; pre-releases 1.0.0-alpha.2 to 1.0.0-alpha.8 are tagged and pushed (D-133, D-154, D-175, D-190, D-196); not merged to `main`, no 1.0.0 |
| §24 1.1.0: speech volume, Presence, quiet hours and home from an entity, snooze, severities | built and tested on `release/1.1` (Phase 16, D-225); checked on the dev HA; not on real devices; "only if" moved to 2.0.0 |
| §25 2.0.0 policies in two lanes | built on `release/2.0` (Phase 17, D-234 to D-237): conversion, matching, band, matrix interactions, Only if, reminder rhythm, checker, panel and help page; user docs written; promise lines on the long list (D-241) |
| §8 frontend (card, editor, serving the JS file) | implemented; pure functions tested with vitest, behaviour checked on the dev HA (Phases 4 and 7) |
| Human docs | README and five pages in `docs/`: `setup.md` (install, first message, card, panel, upgrading, uninstalling), `actions.md` (actions, watch rules, card), `configuration.md`, `settings.md`, `examples.md` (examples, FAQ, troubleshooting, limitations) (D-164) |
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
| `severity` | `info` \| `passive` \| `warning` \| `critical` | `warning` | enum; `success` accepted as `passive` (D-231) |
| `icon` | mdi string | per severity: `mdi:information`, `mdi:check-circle`, `mdi:alert`, `mdi:alert-octagon` | `cv.icon` (N-2) |
| `timeout` | seconds or duration; `0` = no timeout | option `default_timeout` (shipped: 24 h, D-031) | `cv.time_period`, 0 or 1 s – 365 days |
| `condition` | object `{entity_id, state, attribute}` | none | `entity_id` must exist at creation (`entity_not_found`); `state` string or list of strings, default `"on"`; `attribute` optional string |
| `mode` | `once` \| `recurring` | `once` | `recurring` needs a `condition` (refused otherwise, D-188); `once` without a condition stays until timeout, dismissal or clear |
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
- New ID when full and `evict` on: remove the banner with the lowest severity (`passive` < `info` < `warning`), oldest `updated_at` first; `critical` is never evicted. Fires `heads_up_banner_cleared` with `reason: evicted`.
- No candidate or `evict` off: fails with `too_many_banners`. Upserts of existing IDs never evict.

## 5. Lifecycle

```
                create_banner
                     │
        ┌────────────┴──────────────┐
  condition false                no condition / condition true
        │                               │
        │                               ▼
        │                       ┌──── ACTIVE ◄───────────┐
        │                       │      │                 │ recurring: false→true
        │                       │      │ condition       │ (dismissals reset)
        │                       │      ▼ true→false      │
        └─────────────────► WAITING ─┴─ once: REMOVED (reason condition)
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
| `heads_up.create_banner` | §4.1 | `{id, status}` with `status` `created` \| `updated` \| `waiting`; `evicted` ID if any | schema errors (`vol.Invalid`), `entity_not_found`, `too_many_banners`, `not_loaded` |
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
- Condition tests (Phase 3): flips, `once` vs `recurring`, unavailable, entity removed, person `user_id` changes.
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

Style elements: D-002.

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
- **`create_banner` response:** a banner whose condition is false, or true but still waiting for `for`, has status `waiting`. `wait_for_condition` and the status `condition_false` were removed (D-188); the schema still accepts the field, ignores it and raises the repair issue `wait_for_condition_removed` (D-192).
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
- **Snooze fields:** `snoozable` (bool), `snooze_scope` (`user` or `global`), `snooze_options` (1 to 6 durations, 1 minute to 7 days, stored as seconds). Defaults come from the integration options `default_snoozable` (off), `default_snooze_scope` (`user`) and `default_snooze_options` (15 min, 1 h, 4 h). A banner that is not dismissible is never snoozable: an explicit `snoozable: true` with `dismissible: false` is a validation error, and the option default is ignored for it. `snooze_custom` (bool, default false, D-219) also accepts a duration the viewer types, 1 minute to 24 hours and not past `expires_at`; stored only when true; `snooze_custom: true` with `snoozable: false` is a validation error. The card adds **Other…** (minutes or a time of day, `customSnoozeSeconds`).
- **Snooze state:** `snoozed_until` maps a user ID, or `*` for a global snooze, to an end time. It is stored with the banner. `Banner.snoozed_for(user_id)` gives the end that hides the banner from that user. `visible()` leaves a snoozed banner out (not with `show_all`, which flags it with `snoozed`). One `async_track_point_in_utc_time` timer per entry removes it and updates the cards; setup drops ended entries and re-arms the rest.
- **What ends a snooze:** its end time; an upsert (the new banner has none, like `dismissed_by`, D-010); a recurring condition turning false and true again; removal of the banner. For a rule, the condition turning false. The timeout and the condition keep running while a banner is snoozed.
- **WebSocket `heads_up/snooze`** (`banner_id`, `seconds`): `seconds` must be one of the banner's options (`invalid_snooze`), the banner must be snoozable (`not_snoozable`). Only a person the banner is addressed to can call it (`not_targeted` otherwise, D-156). Fires `heads_up_banner_snoozed` with `id`, `tag`, `scope`, `user_id`, `until`.
- **Ending a snooze early (D-074):** WebSocket `heads_up/unsnooze` (`banner_id`) removes the snooze that hides the banner from the caller, and a global one for everyone (`not_snoozed` when there is none, `not_targeted` for a user the banner is not addressed to, D-156). It cancels the timer and fires `heads_up_banner_unsnoozed` with `id`, `tag`, `user_id` and `reason: user`; a snooze that runs out fires it with `reason: ended` (`user_id` empty for a global one), once at start for one that ran out while stopped (D-221). `heads_up/subscribe` takes `show_snoozed` (default false): the list then also holds the viewer's snoozed banners, flagged `snoozed` with `snoozed_until`. Card key `show_snoozed` (off) adds a "Snoozed (n)" list with the time left and a Show now button; the same for action and rule banners (D-073).
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
| `id`, `tag`, `timeout`, `mode` | yes | exception: a rule's lifetime is its condition; its tag is `rule`; its mode is recurring (D-052, D-056) |
| clear by action or by an admin | yes | exception: the rule is disabled or deleted instead (D-056) |
| stored over a restart (banner, dismissals, snoozes) | yes | exception: a rule is rebuilt from its subentry; dismissals and snoozes are not kept (D-056, D-069) |
| hub delivery (channels, a target per channel, a named policy) | yes (`notify`) | exception: a rule is a banner-channel message; other channels come from policies, by severity and tag `rule` or by the rule's Policy field (D-100, D-146) |
| acknowledgement (card button, push button, `heads_up/acknowledge`), escalation and reminder by policy | yes | yes: the policies of the tag `rule` apply, and the acknowledgement starts again each time the condition turns false and true |
| rate limits and ignored identical updates (D-123) | yes, on every delivery | yes, on every delivery that a policy makes for a rule message |
| Deliver, Quiet hours, Away, Fallback and Summarize policies (D-121) | yes | yes, by severity and tag `rule` (D-100); a Summarize policy holds a rule message on every channel |
| button fields `destructive`, `require_auth` (D-195) | yes | yes (one `ACTIONS_SCHEMA` for the action and the rule form); the red text is in the card and the popup, the push flags are the Companion keys of the action |
| event `heads_up_banner_action` carries `person` and `channel` (D-195) | yes | yes (one `BannerManager.press`) |
| `treat_unavailable_as` in a condition (D-195) | yes | exception: a rule treats an unavailable or removed entity as not true (D-053); a template rule can show a banner for an unavailable entity (`{{ states('x') in ['unavailable', 'unknown'] }}`) |
| `audience` and `recipients` of the banner (D-195) | yes (`create_banner`, `notify`) | `audience` yes: resolved each time the rule banner becomes visible (and when the rule is saved), like a call; nobody sees it until then; `audience` and `people` exclude each other (D-242, `tests/hub/test_rule_audience.py`). `recipients` stays `people` |
| panel Test send and trace | yes (message id) | trace yes (`rule_<id>`); Test send previews a call, not a stored rule |
| buttons stop acting once the message has ended (D-125) | yes | yes (one check in `BannerManager.press`; `tests/test_ended_buttons.py`) |
| image under the message (D-127) | yes | yes (Image field of the rule form; `tests/hub/test_image.py`) |
| `heads_up_delivery_failed` (D-128) | yes | yes for the deliveries a policy makes for a rule message, same engine path (no rule-specific test); the banner channel never fires it |
| Policy field: name one policy or `none` (D-146, D-202) | yes (`policy`, by the entity ID of its switch, D-198) | yes (Policy dropdown of the rule form: Automatic, None or a policy by key; `tests/test_rules_flow.py`) |
| references survive a rename (D-199) | yes (stored as keys) | yes (stored as keys; `tests/hub/test_identity_rename.py`, `tests/hub/test_identity_property.py`) |
| a switched-off recipient gets nothing (D-147) | yes (named persons are dropped from the banner's people; all dropped means nobody) | yes (the rule's `people` are filtered when the rule is built and again when a profile changes, D-161; `tests/hub/test_recipient_disabled.py`) |
| viewer-chosen snooze duration `snooze_custom` (D-219) | yes (`notify`, `create_banner`; `tests/test_snooze.py`) | yes (rule form field; `tests/test_snooze.py`) |
| `heads_up_banner_unsnoozed` with `reason`, also when a snooze runs out (D-221) | yes | yes (one `BannerManager._snooze_elapsed`; a rule's snoozes are not kept over a restart, D-069) |

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

Status: built on the branch `hub/h9e-wizard`, a chain of feature branches from H1 to H9e (D-107, 2026-10-30) with later maintainer changes. Pre-releases 1.0.0-alpha.2 to 1.0.0-alpha.7 are tagged and pushed (D-133, D-154, D-175, D-190); 1.0.0-alpha.8 is prepared and not tagged (D-196). `main` is at 0.4.0 and holds nothing of the hub; the maintainer merges and tags 1.0.0 (D-020, `docs/dev/RELEASE.md`). Decisions D-075 to D-159; `docs/dev/hub/DECISION_INDEX.md` lists which decisions are current and which are superseded. This section is the consolidated design. The UI is specified in `docs/dev/hub/UX_SPEC.md` (with the mockup `docs/dev/mockups/hub-panel-mockup.html`), the work breakdown in `docs/dev/hub/ROADMAP.md`. `docs/dev/HUB_DESIGN.md` is the historical planning record and contains superseded text.

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
- `heads_up.notify`: content `message` (required), `title`, `icon`, `severity`, `actions`, `tap_action`, `tts_message`; lifecycle `id`, `tag`, `timeout`, `condition`, `mode`, `dismissible`, `dismiss_scope`, `snoozable`, `snooze_scope`, `snooze_options`, `mail_subject` and `mail_body` (a mail text for this message, D-191); delivery `channels` (required list), `to` (a target per channel: `audience` or `recipients`, never both, kinds depend on the channel, D-098), `policy` (omitted: all that apply; `none`: no policy behavior).
- Shortcuts `push`, `popup`, `speak`: fixed channel, optional audience or recipients, no escalation; fire and forget without an `id`, a tracked message with one. `create_banner` is unchanged and keeps `people`.
- One generic clear removes a message from every channel. Response: `id`, `status` (`created`, `updated`, `waiting`) and per channel counts of `sent`, `held`, `skipped`, `failed`.
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
      push: {audience: binary_sensor.heads_up_audience_admins}
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
Admin-only sidebar panel, in two levels (D-103, order D-242): Overview; Configuration (Channels, Audiences, Recipients, Policies, Severities); Banner watch rules; Settings; Test & Logs (Test send, Message Log); Help. The old `/heads-up/notifications` address opens Test send. Before D-242: Overview; Notifications and Rules (Test send, Watch rules, Message Log); Configuration; Settings (one page with every setting, D-122, and a button that opens the introduction); Help (FAQ, Notify examples, Card examples, D-137). Own forms (`ha-form`) and pages that save through the subentry flow APIs, so storage stays in config subentries (D-119). The Overview holds counts of active notifications with their states, shortcut cards, an activity chart of the last 24 hours, needs-attention warnings that can be hidden, and the last actions (D-118, D-135, D-138). Watch rules are listed, added, edited and deleted on their own page (D-134). Test send previews who would be notified now and can send a real test message (D-120). The Message Log shows recent messages with the per-message delivery trace. The introduction is a four-step tour that creates the default policies (D-121, D-131). Panel registration without a build step is verified (N-88).

### 23.11 Blast radius
Restart: the usual one after a code update. Notification path: touched for the first time (calls to notify, tts, media player and persistent notification services of other integrations; nothing of theirs is modified). Dashboard: nothing changes until a policy or channels are used. Storage: new subentry types and a deliveries store; a downgrade must be checked for unknown subentry types. Manifest: optional integrations as `after_dependencies` (N-68).

### 23.12 Tests (later)
Fake notify, tts, media player and persistent notification services; the lifecycle × channel × source matrix; restart and overdue-step tests; presence with the time freezer (a debounce of presence changes is proposed, not decided); each policy type and their precedence; summary collection and resolved marking; button round trip with stale ids; loader size budget; translation parity; `dev/smoke.py` with stub services.

### 23.13 Alternatives not chosen
A separate integration consuming events (events lack recipients and silent transitions); automations only for delivery; one action per channel only; audiences with set operations; policy matching by explicit priority; the panel with its own storage.

### 23.14 Policy fields and channel settings (D-097)
- Escalation: `after` (minutes), `notify` (`channels` and `to`, a target per channel), `dismiss_counts`.
- Quiet hours: `from`, `to`, `days`, `action` (`wait`, `quiet`, `drop`), `critical_passes`. Away: `max_wait`, `critical_passes` (D-192).
- Fallback: `when` (`no_audience`, `failed`, `both`), `notify` as above.
- Reminder: `every` (minutes), `max`.
- Away: `max_wait` (default: the message lifetime).
- Summarize: `every` (minutes) or `at` (time of day), `include_critical` (default false; policy decides).
- Channel settings by severity: push `level`, `privacy`, `sticky`, `channel_id`; buttons Snooze and Dismiss, with Acknowledge when an escalation or reminder policy applies; popup `style`; speak `language`, `announce`.
- Quiet hours "quiet": push passive without sound, speech skipped, popup as a corner card.

### 23.15 Open
Whether the panel is registered through `panel_custom` or through the frontend function and which passes hassfest (N-77); the recent-messages list across restarts; the unit name in public docs; volume restore on platforms other than Sonos (N-76), the iOS action event, and a run against the dev instance; blueprints cannot be shipped by an integration (N-80); popup area recipients (not built); build phasing (delayed until the design is final). See `docs/OPEN_QUESTIONS.md`.

### 23.16 Identities and renames (D-199 to D-202)
Inside, a policy, a custom audience and a recipient group are known by their subentry ID, a built-in audience by its kind and an area by its area ID; names are for display. `Policy.key` is the subentry ID: timer rows (channel `timer`, recipient), the message id `summary:<key>`, `HeldMessage.policy`, `Banner.policy`, a rule's `policy`, a policy target's `audience` and the recipients `group:<id>` and `area:<id>` hold keys. `hub/identity.py` (`IdentityMaps`) turns a name of an earlier version into a key; reads accept both, writes use the key. A reference to a deleted object dangles and is listed (`reference_missing`); `name:<text>` marks a name that matched nothing when it was converted.

Conversion: the config entry is version 2 (`async_migrate_entry` in `hub/migration.py`, atomic, writes `.storage/heads_up.migration_v2` once first); the stores of banners, deliveries and trace are version 2 (`storage.py`), their contents converted as they load with the same pure functions and saved at once, so a crash between entry and stores loses nothing. Timer `due` and `count` are kept. `scripts/restore_identity_backup.py` restores the backup for a downgrade; Home Assistant refuses the converted data in an older release.

Calls: an audience and a policy by entity ID (D-198), a group by the entity ID of its sensor (`sensor.heads_up_group_<name>`, unique ID `<entry>_group_<subentry id>`), an area by its area ID; text names fail with `*_needs_entity` or `area_needs_id`. `hub/rename.py` follows an entity ID that changes in Home Assistant (event `entity_registry_updated` with `old_entity_id`) and rewrites only the integration's own copies, with a trace line.

Not covered: another integration's names (the notify service of mail: reported as `mail_service_missing`), history in the trace and log (names of their time), `{name}` in a rule message without an entity (the rule's name, by design), a name of an area in hand-written YAML after the area is renamed (the stored form is the ID).


## 24. 1.1.0 (Phase 16)

Status: built on `release/1.1` (D-207, build choices D-225), checked on the dev instance on 2026-11-19, not released. Binding for every part: a 1.0.0 setup converts without a breaking change, and each intended behaviour change has a CHANGELOG line with the way back (D-213).

### 24.1 Speech volume (D-206, D-208, D-215, D-217)
- Speech settings: up to 4 time bands (from, to, volume in percent), no overlap; an optional volume per severity. Precedence: the call's `volume`, then the severity volume, then the band, else no change.
- Restore, on by default (setting "Restore volume after speech"): a player without announce gets its earlier `volume_level` (N-106) back when playback ends; a `sonos` player (entity registry integration) gets the volume as clip volume through `play_media` with `announce: true` and `extra: {volume}` (N-104, N-105) and its main volume is not touched; other announce players are set and restored after about 15 characters per second plus 2 s (4 to 60 s). No restore when the volume was changed by someone else meanwhile; one restore after the last queued message on a speaker. No per-speaker volume.

### 24.2 Presence replaces Away (D-211, D-212, D-214, D-220)
- Fields: channels it covers (push, popup, mail, speak; default the first three); one zone (default Home); push, popup and mail: "the recipient is in / is not in the zone", per recipient; speech: "nobody of / somebody of <audience> is in the zone"; then hold until that changes, or drop; for hold a maximum wait and its end (send, default, or drop); "Critical messages pass" in the Which messages block (D-211).
- A presence change counts after `presence_debounce_seconds` (60 s; 1.0 Away released at once, listed in the CHANGELOG). A released delivery goes through the chain again, so it is held again if the policy still holds it; the first deadline stays. Unknown presence delivers; for speech, people of unknown presence do not count. The banner and reminders are never held. Push, popup and mail are checked for every recipient, from an audience or named in the call (D-232; 1.0 Away checked audience targets only). The household audience of speech is a persons audience or everyone.
- Where a person is comes, per zone, from Home Assistant (Home: the person state `home`; another zone: `in_zones` or the state's name) or, if set on the Recipients page, an entity for that zone (`on` means in the zone; Home stored as `home_entity`, other zones as `zone_entities`, D-229); used by Presence, the presence audiences and speech.
- Conversion (built): config entry version 2, minor 2 (`hub/migration.py`, `migrate_presence`); `type: away` becomes `type: presence` with `after_wait: drop`, because 1.0 Away dropped a delivery when its wait ended (the design assumed it sent it). A stored `away` is still read as Presence with that default. The policy subentries are backed up to `.storage/heads_up.migration_v2_2` first; `scripts/restore_presence_backup.py` puts them back for a downgrade. Held deliveries keep the hold kind `away` (not converted, unlike the plan of D-214): it is internal, and keeping it leaves the deliveries store unchanged. Tested against a 1.0.0 setup captured by running the 1.0.0 code (`tests/fixtures/setup_1_0_0.json`, script beside it). Visible change: the switch attribute `type`.
- Mockup: `docs/dev/mockups/presence-policy-mockup.html`.

### 24.3 Quiet hours source (D-218, D-220)
- Own times (default, 1.0 behaviour) or any on/off entity (`schedule`, `input_boolean`, `binary_sensor`); `on` means quiet. Release when it turns off, or at a schedule's `next_event` (N-103) if earlier. Missing or unavailable: not quiet, Overview warning.

### 24.4 "Only if" on policies: moved to 2.0.0
- "Only if" (D-216) and guests through it (D-209) ship with the policy redesign in 2.0.0 (D-224). 1.1.0 keeps the policy modes "only the first" and "all" and D-211 unchanged.

### 24.5 Snooze (D-219, D-221)
- `snooze_custom` (default off) on `notify`, `create_banner` and watch rules: the card adds "Other…" (minutes or until a time); the backend accepts up to the remaining lifetime, at most 24 h.
- `heads_up_banner_unsnoozed` also fires when a snooze runs out, with `reason: ended` or `user`; an ended snooze found at start fires once.

### 24.6 Severities (D-222)
- The four keys stay. A Severities page under Configuration holds per level a display label (overrides the translation), an icon, the color, and its channel implications (today's per-severity channel settings). The card editor drops `colors`; an existing card `colors` keeps working.
- The label shows in the card, the popup, the mail placeholder `{severity}` and the panel; YAML, events, attributes and the action form keep the keys. The icon is used when a message has none of its own (D-223).
- Built: option `severity_display` (`{severity: {label, icon, color}}`, only set values stored), saved through `heads_up/channels_set` with `push_levels` and `popup_styles`; read by the panel shell through `heads_up/severity_display`, which replaces the severity words of every page (`withLabels`). `Banner.to_client` adds `severity_label` and `severity_color` and uses the icon; the card prefers its own `colors`, then `severity_color`, then the theme. The panel page is `frontend/panel/severities.js`; the Channels page links to it instead of showing the per-severity rows.

### 24.7 Parity (rule 9)
- `snooze_custom` and the snooze event: actions and watch rules. Presence, Quiet hours sources and severity settings are policy or global settings and apply to both sources by severity and tag. Speech volume: speech exists only for actions and policies (D-206).

### 24.8 Blast radius
- Restart: the usual one after an update; the config entry and the deliveries store are converted once (backup first).
- Notification path: speech volume calls (`volume_set`, `play_media` with `extra`) and restore; holds and releases of Presence and Quiet hours.
- Dashboard: the card editor loses `colors`; labels may change if a label is overridden.

## 25. 2.0.0: policies in two lanes (D-224, D-234)
Built in Phase 17; promise lines are on the long list (§25.11, D-241). The design set behind it is `docs/dev/policy-redesign/` (choice and reasons in `02-comparison.md`, the model in `design-ab-v2.md`, mockup `docs/dev/mockups/policy-redesign-a.html`). §24 is the 1.1 work on `release/1.1`, which is not released on its own and becomes part of 2.0.0 (D-231); this section assumes it merged into `release/2.0` first (Presence holding every recipient, D-232; quiet hours and home from an entity; per-zone location entities, D-229; the severity `passive`, D-231). Pairwise behaviour of every policy kind: `docs/dev/policy-redesign/04-interaction-matrix.md`.

### 25.1 Problem
1.0 and 1.1 decide which policies act by one shared list order and a mode (`first` or `all`, D-148). The order means "more specific" and "stronger" at once, hold-back and sending policies look alike, severity `critical` is the only way through a hold, and tags cannot be excluded (pain points 1 to 7 in `00-fact-sheet.md`). 2.0.0 replaces the order and the modes with rules that need no order.

### 25.2 Model
"Calming policies decide when a message may reach people, sending policies decide who else gets it and how often, and the Always gets through list says which messages may wake whom anyway."
- Lane "Keep it calm": Summarize, Quiet hours, Presence.
- Band "Always gets through": the new type `get_through`.
- Lane "Make sure it arrives": Deliver, Escalation, Reminder, Fallback.
- Only when named: every policy with `apply: manual`.
- The seven type keys of 1.1 stay; there is no list order and no mode.

### 25.3 Rules
1. Every enabled automatic policy that fits a message acts, and so does every named one (D-184, D-189, D-145). On one delivery the calmest hold counts: summary, then drop, then wait, then quiet. A released delivery passes every hold again. A repeat is skipped where it would wait; Presence does not check repeats (1.0).
2. On each channel a message keeps one repeat rhythm, the shortest among the reminders that fit at that moment, except a reminder with Runs alongside, which keeps its own. Each reminder counts its own repeats. Escalation and Reminder clocks start when the message is created, as in 1.x; there is no other choice (D-235).
3. A `get_through` entry that fits a message lets it pass Summarize as a whole (every channel, the banner too) and Quiet hours for the recipients it covers, except on a hold marked "Holds these anyway". Presence is never passed. An entry sends nothing.

Definitions:
- A policy fits a message when For (severities, tags, watch rules), Not for (severities, tags), its links and Only if all match. An unknown Only if counts as whatever delivers more (D-216).
- For and Not for: a list that is empty does not restrict. A message has one severity and at most one tag (`matching.applies`). Not for wins over For.
- "From watch rule": a list of rule subentry IDs; it fits a message whose ID is `rule_<subentry id>` (`RULE_ID_PREFIX`). Messages of every rule still carry the tag `rule` (D-100), so a policy for all rules uses that tag.
- A second policy of the same type with the same For, Not for, From watch rule and trigger is refused by the form, as in 1.x (`matching.duplicate_of`, D-235).
- A held delivery is not a failure and never triggers a Fallback (1.0).
- A Fallback delivery passes the same holds as its message; it is never louder (D-235). A band entry covering a speaker lets it speak at night.
- Two reminders with the same rhythm on one channel: the one created first counts the repeat.

### 25.4 Stored shape (config entry version 3, minor 1)
New fields on every policy subentry:

| Field | Type | Default | Effect |
|---|---|---|---|
| `not_severities` | list | `[]` | Not for these severities |
| `not_tags` | list | `[]` | Not for these tags |
| `rules` | list | `[]` | For messages of these watch rules (subentry IDs); empty: no restriction |
| `links` | list | `[]` | Written only by the conversion: subentry IDs; the policy does not fit a message that a linked policy fits while that policy is enabled |
| `only_if` | object | none | D-216 condition, same shape as `notify` `condition` |
| `faster_while` | object | none | Reminder: `{condition, every_minutes}`; while the condition is true the reminder uses the shorter rhythm, one count and one limit for both |
| `alongside` | bool | false | Reminder: keeps its own rhythm next to other reminders |
| `holds_anyway` | bool | false | Quiet hours and Summarize: no band entry passes this hold |

New subentry type `get_through` (same subentry kind `policy`, own switch entity): `name`, `enabled`, `severities`, `tags`, `rules`, `not_severities`, `not_tags`, `only_if`, `covers` (`everyone` or `only`), `targets` (audiences, recipients and speakers when `covers: only`).

Removed: `critical_passes` (Quiet hours, Presence), `include_critical` (Summarize), the entry options `policy_order` and `policy_mode`. Summarize holds every severity it fits; a band entry passes it.

A 1.x release refuses version 3 (Home Assistant does not load a config entry whose major version is above the handler's, as for version 2 in §23.16). There is no restore script (D-234); the way back is a backup made before the upgrade.

### 25.5 Engine
- `matching.select`: every fitting policy; `first_only` is removed. `fits(policy, message, book)` checks For, Not for, `rules`, `links` (against the linked policies' enabled state at that moment) and `only_if`.
- Chain (`chain.py`): unchanged order Summarize, Quiet hours, Presence, Fallback. Summarize asks `book.passes(message)` once when the message appears (it decides the hold then, 1.x): true when an enabled `get_through` entry fits the message, whatever it covers, and the Summarize policy is not `holds_anyway`; the message is then not collected on any channel. Quiet hours asks `book.passes(message, recipient)` per delivery: true when a fitting enabled entry covers the recipient and the hold is not `holds_anyway`. Covers `everyone`: every recipient and speaker of that delivery. The Quiet hours check is per recipient, so one push can ring for the Admins and stay quiet for Anna (scenario 1).
- Calmest hold: several holds of one stage already resolve strictest first (drop, wait, quiet, `quiet.py`); Summarize runs first and holds every channel (D-105), so "summary first" is the 1.0 order.
- Clocks: `_arm` plans Escalation and Reminder rows when the message is created (1.x, unchanged). An escalation delivery that a hold catches is a setup mistake (D-235): the engine writes an attention item `escalation_held` (policy, hold, message) to the Overview, the message history says "Escalation Nobody looked was held by Night quiet", and the escalation form warns before Save when a hold without a covering band entry fits its messages.
- Reminders: one rhythm per channel, the shortest among fitting reminders without `alongside`; each reminder keeps its own count in its timer row. `faster_while` and `only_if` changes re-plan the next row (state listeners from D-216).
- Only if (D-216): checked whenever the policy would act; a held delivery is released when its policy's condition turns false; guests (D-209) are an Only if on a Presence policy. A band entry that starts to fit (its switch turns on or its Only if turns true) releases at once the Quiet hours deliveries it now covers and takes the messages it fits out of every pending summary; they are delivered as if they had just been sent (D-235). Summarize needs a new release path for this: remove the message from the collection and run its first delivery through the chain.
- Interactions decided from the matrix (D-235, `04-interaction-matrix.md`):
  - A summary goes to everyone the held messages would have reached, Deliver's recipients included; a summary that reaches nobody triggers a fitting Fallback. Two Summarize policies: the one due next collects the message.
  - A message taken out of a summary by a band entry runs as a new message (Deliver, Fallback); its clocks count from the release.
  - An escalation sends again to recipients who already have the message (no `resume` for escalations). An escalation that a hold catches (held, dropped, quiet) or that reaches nobody gets an attention item and no Fallback; the Policies page warns as soon as the setup allows either.
  - A Fallback fires only when the call's own delivery and every Deliver policy reached nobody. Reminders repeat a Fallback's sends (1.x).
  - Several band entries add up. Two Presence policies that contradict both act, with a warning on the page and in the form.
  - A policy switched on, or freed by a link target switched off, acts only on messages that appear afterwards; timers are planned at appearance for every policy that fits by For, Not for, switch and links, and Only if is checked at each step.
  - Automatic matching off for a message (`match_policies_automatically: false`, `policy: none`, a watch rule's own policy): no automatic policy acts, holds and band entries included (1.x). A band entry may be "Only when named".
- Fits is cached per message and recomputed on a severity change, a switch change, a link target's switch change and an Only if change; `_drop_inapplicable_timers` keeps working on the result.

### 25.6 Conversion (version 2 minor 4 to version 3 minor 1)
Runs in `async_migrate_entry` after the steps of `release/1.1` (2.2 Presence, 2.3 push levels, 2.4 `passive`), so a 1.0 setup goes 2.1 to 2.4, then 3.1, in one start. It reads the stored data before any rewrite. Steps, in this order:
1. The order as Not for (only when `policy_mode` is `first` or missing, D-240). For each automatic policy P and each enabled automatic policy Q above P in `policy_order` (policies missing from the order count as appended, in subentry order, as 1.x does) whose For can overlap P's: a condition of Q that all of P's messages meet anyway drops out (P's severities within Q's, or P's tags within Q's). Q with only severities left adds them, within P's, to P's `not_severities`; Q with only tags adds them to `not_tags`; Q with both keeps a link (`links`, checked live against Q's switch and Q's For only). The check-list item stores what was added, so "Apply to them too" takes exactly that back. Disabled policies did nothing in 1.x and are left out; the conversion reproduces "only the first" for the switch states at the update (tested over every severity, tag and switch state, `tests/hub/test_policy_lanes.py`).
2. Never acts: P never acts when, with today's switch states, every (severity, tag) it fits is fitted by an enabled linked policy. Exact test: for each severity of P, each tag of P must be fitted by a linked enabled Q (Q's tags empty or containing it); P with no tags needs a Q with no tags.
3. Mode `all`: no links, and no `alongside`; these setups get the 2.0 rules (D-235). Overlapping reminders on one channel then keep one rhythm, the shortest, instead of running side by side; the CHANGELOG says so.
4. Critical: if any Quiet hours policy had `critical_passes: true` or any Summarize policy had `include_critical: false`, add the entry "Critical" (`get_through`, severities `[critical]`, covers everyone). A Quiet hours policy with `critical_passes: false` that fits critical, and a Summarize policy with `include_critical: true`, get `holds_anyway: true`. A Presence policy with `critical_passes: true` gets `not_severities: [critical]`.
5. Remove `critical_passes`, `include_critical`, `policy_order`, `policy_mode`; set version 3, minor 1.
6. Write one check-list item per change that the user may want to undo (§25.7).

The step is a pure function `convert_v3(entry_data, options, subentries) -> (subentries, options, items)` in `hub/migration.py`, atomic like the earlier steps.

Equivalence test: for each fixture, run the 1.1 selection and chain over a grid (four severities × each named tag and no tag × a source `notify` and `rule` × 168 hours × home and away) and the 2.0 selection and chain over the converted setup; the deliveries must match except the differences listed in the CHANGELOG. For mode `all` fixtures the test lists the differences instead of failing on them, and that list is the CHANGELOG text. Fixtures: `setup_1_0_0.json` (exists on `release/1.1`); the welcome list with a later Away at the end; the same with Away first; mode `all` with two overlapping reminders; Quiet hours with `critical_passes: false`; Summarize with `include_critical: true`; a manual policy named by a watch rule; a disabled policy above another.

### 25.7 Check list after the update
- Stored as the entry option `conversion_items`: `{policy, kind, state, added}`, `kind` one of `not_for`, `links`, `never_acts`, `holds_anyway` (D-235, D-240); `state` `open`, `kept` or `changed`.
- Shown at the top of the Policies page until the list is dismissed (Hide this list), or until the page is opened again after every item was answered; then the panel dismisses it (D-242). Answering the last item does not hide it at once. Each item: one sentence and two buttons.
  - `links`: "Night quiet skips messages that Evening summary already handles." Keep it like this / Let it act on them too (removes the links).
  - `never_acts`: "Never acts: Critical delivery, Warning reminder, Evening summary and Night quiet take all its messages first." Keep as before / Let it act.
  - `holds_anyway`: "Holds critical messages too, as before." Keep as before / Let Critical through.
- The added entry Critical and Not for critical on Presence get no item; the CHANGELOG lists them once, with the mode `all` differences.
- A user who never opens the list keeps 1.x behaviour, except the listed differences.

### 25.8 Checker and message history
Checker "Test policies", a dialog opened from the action bar of the Policies page, admin WebSocket command `heads_up/policy_check`:
- Input: severity, tag, source (`notify`, or a watch rule), channels and recipients as in a call (default: push to everyone), time (default now), who is home (default as now, each person switchable), acknowledged after (never, or N minutes).
- Work: the same `fits` and chain stages as the engine, with a fixed clock and the given presence; no ledger, store or trace writes. It plans escalations and reminders for 24 hours, or until the limits end them.
- Output: one line per recipient and channel and per planned step: time, outcome (sent, sent quietly, held until, dropped, skipped), the policy that caused it and why ("tagged alarm", "22:00 to 07:00", "nobody home"), and "would have let it through" where a fitting band entry is switched off.

History: every delivery, hold, release, skip and drop row in the ledger gets `policy` (subentry ID) and `reason` (code, as in the checker). The Messages page shows them as a timeline with the checker's sentences. Retention follows the existing history limit.

### 25.9 Panel
- Policies page: checker, check list, lane "Keep it calm", band, lane "Make sure it arrives", Only when named. Each lane and the band have one top line (wording in §25.10). The order list, Move up and Move down and the mode setting are removed.
- Card: type in text, the "In words" sentence, switch (aria label names the policy), a links note for converted policies. Show details: type key, entity ID, stored fields, YAML.
- Form (ha-form fields, one plain label each): name, enabled; Which messages (Automatically or Manually, For, Not for, From watch rule, links when present, Only if); What it does (the type's fields; Reminder adds Faster while and Runs alongside; Get through has Covers). At the top, read-only and live: the sentence. Below Save: Where it overlaps (1.0 note, now per pair: "Where both fit, the calmer counts") and a warning when a change takes waking away ("Messages tagged alarm will no longer wake the Admins at night"). Nothing blocks Save (D-151).
- Add a policy offers outcomes as starting points: Wake the Admins for leaks (Get through plus Deliver, two cards), Quiet nights for small things, Speak only when someone is home, Summarize digest at 20:00.
- Welcome (D-121, D-150): Critical delivery, the band entry Critical, Warning reminder, Evening summary, Night quiet. Night quiet gets Not for tag `digest` instead of relying on the order.

### 25.10 Wording
Lane, band and new labels in the four languages; type names and existing labels keep their 1.1 texts.

| Key | English | German | French | Spanish |
|---|---|---|---|---|
| lane calm | Keep it calm | Für Ruhe sorgen | Garder le calme | Mantener la calma |
| lane arrive | Make sure it arrives | Damit es ankommt | S'assurer qu'il arrive | Asegurar que llegue |
| band | Always gets through | Kommt immer durch | Passe toujours | Siempre pasa |
| type `get_through` | Get through | Kommt durch | Laisser passer | Dejar pasar |
| only named | Only when named | Nur wenn genannt | Seulement si nommée | Solo si se nombra |
| covers | Covers | Gilt für | Concerne | Afecta a |
| covers everyone | Everyone it reaches | Alle, die sie erreicht | Tous ceux qu'il atteint | Todos a quienes llega |
| covers only | Only these | Nur diese | Seulement ceux-ci | Solo estos |
| holds anyway | Holds these anyway | Hält sie trotzdem | Les retient quand même | Los retiene igualmente |
| not for | Not for | Nicht für | Sauf pour | Excepto para |
| from rule | From watch rule | Von Überwachungsregel | Depuis la règle de surveillance | Desde la regla de vigilancia |
| faster while | Faster while | Öfter, solange | Plus souvent tant que | Más a menudo mientras |
| alongside | Runs alongside other reminders | Läuft neben anderen Erinnerungen | Fonctionne à côté des autres rappels | Funciona junto a otros recordatorios |
| checker | Test policies | Richtlinien testen | Tester les règles | Probar las reglas |
| check list | The policy feature has been updated – please review the new behaviour | Die Richtlinien wurden überarbeitet – bitte prüfe das neue Verhalten | Les règles ont été repensées – vérifiez le nouveau comportement | Las reglas se han rediseñado – revisa el nuevo comportamiento |
| keep | Keep it like this | So lassen | Laisser ainsi | Dejarlo así |
| let act | Let it act on them too | Auch dafür wirken lassen | La laisser agir aussi sur eux | Que actúe también en ellos |

The German and French terms for "watch rule" follow the existing rule strings of 1.1; the table is checked against them when the strings are written. Top lines (plain language, D-238): calm "Policies that hold messages back, send them quietly or bundle them into a summary. If two disagree, the quieter one wins." Band "These messages are never summarized, and quiet hours do not apply to the people covered. Who gets them depends on the original message (for example named people, the Admins, everyone at home)." Arrive "Policies that send additional messages, for example when the original recipients could not be reached or nobody reacted. All policies that fit are applied." No user-facing text names the earlier version; a converted link reads "Skips messages that … already handle".

### 25.11 Promise lines (moved to the long list, D-241)
A line on every card ("Kept", "Bent for tag alarm by …", "Never acts"), computed by playing four severities × each named tag and no tag × 168 hours through the policies. Not built: the maintainer moved it to the long list with the status "unclear, not needed now" (`docs/OPEN_QUESTIONS.md`, Deferred ideas). Test policies and the Needs attention warnings answer the same questions on request.

### 25.12 Parity (rule 9)
Watch-rule messages fit policies by severity, tag `rule` and From watch rule, reach the band and Deliver, and show in the checker (source watch rule) and the history. Frozen rules (D-100) and a rule's named policy (D-145) are unchanged. No exception is added to §22.

### 25.13 Blast radius
- Restart needed; the config entry moves to version 3 and 1.x cannot load it. A backup before the upgrade is the only way back.
- Notification path touched: matching, the chain, timers and Fallback.
- What the panel shows changes: Policies page rebuilt, Messages page timeline, welcome list.
- Calls: switch entity IDs (D-198), `policy` names and lists (D-184, D-189), `match_policies_automatically` and `policy: none` unchanged. Entity attributes of policy switches gain `not_severities`, `not_tags`, `rules`; `critical_passes` and `include_critical` disappear.

### 25.14 Tests
- Conversion: `convert_v3` per fixture; the equivalence test (§25.6); `never_acts` exact on hand-made cases; idempotent on a second start.
- Rules: one test per rule and per definition in §25.3; the twelve scenarios of `01-users-and-stories.md` as engine tests (scenario 11 is the equivalence test).
- Checker: same result as the engine for each scenario; no writes.
- Panel: vitest for the sentence, the wording keys and the overlap sentence; dev instance: Policies page at 380 px, keyboard, screen-reader labels, the check list after converting `setup_1_0_0.json`.
- `make dev-smoke` gets a `lanes` phase: band entry passes Quiet hours for one recipient only.

### 25.15 Build checklist (one phase, D-234)
Order; each step one or more commits, `make check` green after each.
1. Merge `release/1.1` into `release/2.0` (D-231: 1.1 is not released on its own).
2. Stored shape and `convert_v3` with fixtures and the equivalence test.
3. Matching without order: For, Not for, From watch rule, links, `select` without `first_only`.
4. `get_through` type, switch entity, `passes` in Quiet hours and Summarize, `holds_anyway`.
5. Escalation-held warning; reminder rhythm per channel, own counts, `faster_while`, `alongside`.
6. Only if and guests (D-216, D-209) on every type.
7. Ledger `policy` and `reason`; checker command.
8. Panel: lanes, band, cards, forms, Add outcomes, check list, checker, Messages timeline, welcome list; strings in four languages.
9. Docs: `configuration.md` policies section, `setup.md` upgrading, `examples.md`, CHANGELOG "Before you upgrade" (backup first, then each difference), §0 status, HA_API_NOTES rows.
10. `make hassfest`, `make dev-smoke`, browser-pane checks.
11. Promise lines: moved to the long list (D-241), not part of 2.0.0.

### 25.16 To verify before building
- Verified (N-109): Home Assistant refuses a config entry with a higher major version; the entry shows as a migration error and is not loaded.
- The condition selector for Only if and Faster while in the panel's own forms (D-216 left it open).
- Listeners for Only if on a held delivery across a restart.
- Cost of the checker's 24-hour plan on a setup with 30 policies and 20 tags on a small host.
