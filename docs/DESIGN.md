# Design: Heads Up

Phase 0 design document. Decisions are referenced as D-nnn (`docs/DECISIONS.md`), API facts as N-nn (row in `docs/dev/HA_API_NOTES.md`), risks as R-n (§14).

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
| Load | At most 50 banners by default (option), one state listener per distinct condition entity, one timer per banner with a timeout. |
| Concurrency | Actions run in the event loop and mutate state synchronously (no `await` between read and write), so parallel callers cannot interleave a single upsert. |
| Accessibility | Severity shown by icon and text label, not color only; `aria-live` region; dismiss button 48×48 px with translated `aria-label`; keyboard reachable. |
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
| `dismissible: false` | Card shows no X; WebSocket dismiss rejected with `not_dismissible`. Admin clear still works (D-011). |
| Condition entity `unavailable` / `unknown` | `condition_met` unchanged (D-006). |
| Condition entity removed after creation | Treated like `unavailable`; banner kept; timeout still applies. Logged at warning level once. |
| HA was down past `expires_at` | Removed during setup, `expired` event fired. |
| Restart with condition | Re-evaluated when the entity reports a state other than `unavailable`/`unknown`; until then `condition_met` keeps its stored value. |
| `once` banner, condition never becomes true | Removed by the 24 h default timeout unless the caller passed `timeout: 0` or the option was cleared (R-4, D-031). |

History: no stored history; events only (D-012).

## 6. Backend architecture

```
custom_components/heads_up/
  __init__.py      async_setup: register actions + WebSocket commands; async_setup_entry: load store, start manager, register frontend
  manager.py       BannerManager: in-memory dict, mutations, visibility rules, listeners, timers, events, subscriber fan-out
  store.py         Store subclass (version/migration), serialisation
  services.py      action schemas + handlers
  websocket.py     heads_up/subscribe, heads_up/dismiss, heads_up/admin_clear
  sensor.py        count sensor
  frontend.py      static path + add_extra_js_url
  config_flow.py   single-instance config flow + options flow
  const.py, strings.json, translations/en.json, services.yaml, icons.json, manifest.json
  frontend/heads-up-card.js
```

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
| `heads_up/admin_clear` | admin (`require_admin`) | `banner_id` | `{}` or `not_found` / `unauthorized` |

Banner IDs travel as `banner_id` because `id` is the WebSocket message ID.

Visibility is computed per connection from `connection.user.id`; the person whose `user_id` equals it decides targeting. Sending the full list (≤ 200 items) per change is chosen over diffs: fewer states to get wrong.

Config flow: one entry, no input (D-026). Options: `max_banners`, `evict`, `default_dismiss_scope`, `default_timeout`. Option change applies to new banners only. Removing the entry deletes `.storage/heads_up.banners` (`Store.async_remove`, N-6) in `async_remove_entry`.

## 7. Action reference

| Action | Fields | Response (`SupportsResponse.OPTIONAL`, N-3) | Errors |
|---|---|---|---|
| `heads_up.create_banner` | §4.1 | `{id, status}` with `status` `created` \| `updated` \| `waiting` \| `condition_false`; `evicted` ID if any | schema errors (`vol.Invalid`), `entity_not_found` (Phase 3), `too_many_banners`, `not_loaded` |
| `heads_up.clear_banner` | `id` or `tag` (at least one) | `{cleared: n}` | none (unknown id → `cleared: 0`) |
| `heads_up.clear_all` | none | `{cleared: n}` | none |

Errors are `ServiceValidationError` with translation keys in `strings.json`. Actions are registered in `async_setup`; called without a loaded config entry they fail with `not_loaded`.

Examples (validated by `docs-check` from Phase 1 on)
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
External call paths (D-022): REST `POST /api/services/heads_up/create_banner` (with `?return_response` for response data) and WebSocket `call_service` work through HA core; no own endpoints.

## 8. Frontend architecture

- One plain-JS ES module `heads-up-card.js`, no build (D-021). Served at `/heads_up/heads-up-card.js` via `async_register_static_paths` (N-9) and registered with `add_extra_js_url(hass, "/heads_up/heads-up-card.js?v=<manifest version>")` (N-8); the version query busts the browser cache on upgrade. No manual resource step. Not loaded in safe mode (N-8).
- Elements: `heads-up-card` and `heads-up-card-editor` (`getConfigElement`, `config-changed`, N-13); `window.customCards` entry.
- Data: on `connectedCallback` the card calls `hass.connection.subscribeMessage(cb, {type: "heads_up/subscribe", show_all})`; unsubscribes in `disconnectedCallback`. Reconnect handling relies on home-assistant-js-websocket re-subscribing (unverified, test in Phase 4).

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

Rendering: banner = icon, title, message, optional tap target, X button if dismissible, admin clear button for admins on non-dismissible banners. Colors: `--info-color`, `--success-color`, `--warning-color`, `--error-color` for accent and icon; background tinted from the same variable with `color-mix`; text `--primary-text-color`. Critical banners in an `aria-live="assertive"` region, others `polite`. Tap action: dispatch `hass-action` event with `{config: {tap_action}, action: "tap"}` (pattern used by community cards; unverified against frontend source, Phase 4 spike). Sizing: `getCardSize` = number of rendered banners; `getGridOptions` → `{columns: 12, rows: "auto"}` (N-12). Empty slot in sections view: N-14 unverified; fallback is a visibility condition on `sensor.heads_up_active_banners > 0`, which works on 2026.9 (numeric state) but is global, not per user.

Touch and kiosk use: 48 px touch targets; no hover-only controls; `compact` layout for narrow viewports; Phase 4 test matrix includes a 768×1024 and a 1280×800 kiosk viewport.

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
| Condition entity unavailable/unknown | visibility unchanged |
| Person ID in `people` does not exist | accepted; matches nobody until created |
| Full and no evictable banner | `too_many_banners` |
| Two parallel `create_banner` with same `id` | serialized in event loop; last call wins; two events |
| Clock change / DST | all times UTC; DST has no effect. A manual system-clock jump forward expires banners early (HA timer semantics). |
| Corrupt storage file | `Store` load raises; integration setup fails with a log error, other integrations unaffected; user can remove the file (troubleshooting doc). Stricter probatio validation of stored data on load (N-1) is covered by a test. |
| Card on HA without the integration loaded | card shows a one-line error "Heads Up integration not loaded". |
| Huge `tap_action` | limited by WebSocket message size; not validated beyond being a mapping (R-1). |

## 11. Test strategy

- Python: `pytest-homeassistant-custom-component` pinned to the release matching HA 2026.9.4 (N-20); CI matrix adds latest 2026.10.x.
- Lifecycle tests first (Phase 2): upsert, each removal reason, eviction order, limits, response data, events, permission checks for `show_all`/`admin_clear`.
- Restart tests: create → unload/reload entry with persisted store → assert banners, dismissals, `expires_at`; freeze time past expiry across restart → `expired` event.
- Condition tests (Phase 3): flips, `once` vs `recurring`, `wait_for_condition`, unavailable, entity removed, person `user_id` changes.
- WebSocket tests with the HA test client: per-user filtering, subscription cleanup on close (N-5).
- Card: vitest on pure functions extracted into the same module (sorting, filtering, visibility of controls) — exported for tests; DOM checked manually.
- Manual matrix (Phase 4): sections/masonry/panel, light/dark theme, narrow viewport, non-admin user, reconnect after HA restart.
- Docs: `docs-check` validates every YAML example against the real action schemas and compares documented fields with schema fields.

## 12. Packaging, CI, versioning, runbook

- Public GitHub repo (D-020); layout `custom_components/heads_up/`, `brand/icon.png`, `hacs.json` `{name: "Heads Up", homeassistant: "2026.9.0"}` (N-18, N-19).
- manifest: `domain`, `name`, `version`, `documentation`, `issue_tracker`, `codeowners`, `config_flow: true`, `integration_type: service`, `iot_class: local_push`, `dependencies: [frontend, http, person]`, `single_config_entry: true` (key existence to verify in Phase 1).
- SemVer; CHANGELOG (Keep a Changelog); GitHub releases, not only tags (N-18).
- CI (D-027): ruff, mypy, pytest, hassfest, HACS action, vitest, docs-check.
- Dev environment: Docker `ghcr.io/home-assistant/home-assistant:2026.9.4` (tag to verify in Phase 1), config from `dev/ha-config/`, no notify services.
- Install runbook (Phase 6, for users): backup, HACS custom repo install, restart (all automations pause for the restart duration), add integration, open dashboard, smoke test with one `create_banner`, rollback = remove integration + HACS uninstall + restart.

## 13. External callability and API stability

- Contract = action names, field names, defaults, response keys, event types and data keys, card `type` and config keys.
- Additions are minor versions; removals or meaning changes are major versions with one minor release of deprecation warning in the log.
- `condition` is an object so new forms (`template`, `conditions`) can be added without breaking existing calls (D-005).
- `Store` minor version for additive storage changes, major + `_async_migrate_func` for breaking ones (N-6).

## 14. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-1 | `tap_action` with `perform-action` runs any action when tapped, including on a shared display (D-015). | Caller responsibility; stated in SECURITY.md and `docs/actions.md`; HA's own `confirmation` option documented in the example. |
| R-2 | Installing requires an HA restart, which pauses all automations, including security-related ones. | Install docs state this before the restart step. |
| R-3 | Empty card leaves a grid gap in sections view (N-14). | Test in Phase 4; fallback visibility condition (global count). |
| R-4 | `once` banner with an entity that never turns true and no timeout stays waiting forever. | `default_timeout` ships as 24 h (D-031); clearing it shows a warning in the options form; documented in limitations. |
| R-5 | HA API drift (probatio switch in 2026.9 shows how fast). | Dev image pinned to the minimum supported minor; monthly release-note check; `stale-check-on-upgrade` rows in HA_API_NOTES. |
| R-6 | `hass-action` event and websocket re-subscribe behaviour unverified. | Phase 4 spikes before card code depends on them. |
| R-7 | Domain `heads_up` collision (N-22). | Re-check before Phase 1 scaffold. |
| R-8 | Per-user dismiss on a shared login hides the banner for everyone on it (D-007). | Documented; callers choose `dismiss_scope`. |

## 15. Verified facts

All in `docs/dev/HA_API_NOTES.md` with source, version, date, status. Unverified items that affect design: N-14 (empty card in sections), N-21 (not needed), N-22 (domain collision), `single_config_entry` manifest key, `hass-action` event, websocket re-subscribe on reconnect, Docker image tag. Rows checked on `dev` must be re-checked at tag 2026.9.4 in Phase 1 (N-6–N-10).

## 16. Documentation plan

Claude-facing: `CLAUDE.md`, `.claude/rules/{backend-python,frontend-card,docs-style,tests}.md` (`paths:` frontmatter, verified syntax: YAML list of globs, only field read), `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`, `docs/dev/{HA_API_NOTES,STATE,DEV_ENVIRONMENT,TESTING,RELEASE}.md`.

Human-facing: `README.md`, `docs/{actions,card,examples,troubleshooting,limitations,uninstall,upgrading}.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`.

README screenshots (from dev HA): one image with a warning and a critical banner in light theme, one in dark theme, one GIF of a banner disappearing when its condition entity turns off.

HA documentation rules covered: `docs-high-level-description` (README intro), `docs-installation-instructions` (README), `docs-removal-instructions` (`uninstall.md`), `docs-actions` (`actions.md`), `docs-configuration-parameters` (`card.md`, options in README), `docs-installation-parameters` (none: config flow has no input; stated), `docs-examples` (`examples.md`), `docs-known-limitations` (`limitations.md`), `docs-troubleshooting` (`troubleshooting.md`), `docs-use-cases` (`examples.md`), `docs-data-update` (README: push via WebSocket, no polling).

`docs-check` (Phase 1): banned-word grep over human docs; YAML examples validated against action schemas; field parity between `services.yaml`/schemas and `docs/actions.md`; card config keys vs. `docs/card.md`.

Adopted style elements: D-002.
