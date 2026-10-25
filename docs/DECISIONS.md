# Decisions

ADR-style log. Each entry: decision, alternatives, consequences. All entries dated 2026-10-24 unless stated; status accepted unless stated.

## D-001 Phase 0 repo contains documentation only
- Decision: until the design was approved, the repo held only Markdown docs and `.gitignore`.
- Alternatives: scaffold the integration immediately.
- Consequences: no source code before the Phase 0 gate.

## D-002 Reference READMEs for human docs
- Decision:
  - Browser Mod: numbered imperative Installation/Quickstart steps; separate "Upgrading" section; FAQ headings phrased as the user's question, including "How do I uninstall …?".
  - Alert2: configuration and action fields as tables (key, type, required/default, description); events as a table of `event_type` and data fields, followed by one automation example.
  - Mushroom: HACS install first, manual install second; troubleshooting starts with "check the version, clear the cache, check the browser console".
- Not adopted: emoji headings, badge rows, promotional tone; limitations scattered across sections (we use one `docs/limitations.md`).
- Consequences: reference tables live in `docs/actions.md` and `docs/card.md`.

## D-003 Development only against a local throwaway instance
- Decision: development and tests run against unit tests and the local Docker instance (`make dev-up`). No connection to any other Home Assistant instance. Data from a real instance is never fetched by tooling.
- Consequences: any enforcement beyond this rule is local developer configuration and not part of the repo.

## D-004 Name and domain: Heads Up (`heads_up`)
- Context: scope may grow beyond dashboard banners (toasts, popups, other channels).
- Decision: integration name "Heads Up", domain `heads_up`, actions `heads_up.create_banner|clear_banner|clear_all`, card `custom:heads-up-card`.
- Alternatives: `dashboard_banner`, `herald`, `beacon`, `noticeboard`.
- Consequences: collision with existing HACS/core domains not fully checked (N-22).

## D-005 Condition: entity + state match
- Decision: `condition: {entity_id, state (default "on"), attribute (optional)}`. Object form so template / full HA conditions can be added later without breaking callers.
- Alternatives: template, full HA condition syntax, boolean entity only.
- Consequences: one state listener per conditioned banner.

## D-006 Condition lifecycle: `mode` and `wait_for_condition`
- Decision:
  - `mode: once | recurring`, default `once`. Only valid with a `condition`.
  - `once`: the banner is removed for good the first time the condition goes from true to false.
  - `recurring`: stored; visible while the condition is true, hidden while false. Each false→true flip resets user dismissals. Removed only by timeout, `clear_banner`, `clear_all`.
  - `wait_for_condition: bool`, default `true`: a banner whose condition is false at creation is stored and appears on the first true. `false`: create returns status `condition_false` and stores nothing.
  - Condition entity `unavailable`/`unknown`: visibility unchanged. Entity missing at creation: fails with `entity_not_found`.
- Alternatives: dismissals kept across recurring flips; always reject when false at creation; unavailable treated as false or true.

## D-007 Dismiss scope per banner, default `user`
- Decision: `dismiss_scope: user | global` on `create_banner`; default from the options flow, shipped default `user`. Per-user dismissals stored by HA user ID.
- Alternatives: integration-wide option only, per card, per browser.
- Consequences: a dismissal on a shared login hides the banner for everyone using that login.

## D-008 Targeting: person entities, server-side filtering
- Decision: `people: [person.x, ...]`, empty = everyone. The backend resolves each person's `user_id`; the WebSocket API returns only banners targeted at the connected user. Admins see all banners only with card option `show_all: true` (enforced server-side). Users without a person entity see only untargeted banners.
- Alternatives: browser-side filter (data readable by all), HA user IDs, both.
- Consequences: no assumptions about any particular installation. Not a security boundary against admins or file access; SECURITY.md states this.

## D-009 Severity levels
- Decision: `info | success | warning | critical`, default `warning`. Colors from theme variables; distinct default icon and text label per level.
- Alternatives: info/warning/critical; warning/critical.

## D-010 IDs and upsert
- Decision: `id` optional; generated if missing and returned in response data. Allowed `[a-z0-9_-]`, max 64 chars. `create_banner` with an existing ID replaces all fields, restarts the timeout, keeps `created_at`, sets `updated_at`, clears dismissals.
- Alternatives: required ID; replace keeping dismissals; field merge.

## D-011 Banners without end and the admin valve
- Decision: no timeout + no condition + `dismissible: false` is allowed. Admins get a clear button on every banner in the card; `clear_all` always works.
- Alternatives: max lifetime cap; no valve.

## D-012 History: events only
- Decision: fire `heads_up_banner_created|updated|dismissed|expired|cleared`. No stored history.
- Alternatives: short stored history; none.

## D-013 Entities: one count sensor
- Decision: one sensor with the number of active banners (all users). No banner text in attributes.
- Alternatives: per-severity binary sensors; no entities.

## D-014 Text rendered at call time
- Decision: HA renders templates in action data once; callers update text by calling `create_banner` again.
- Alternatives: live re-rendered templates.

## D-015 Tap action: full HA `tap_action`, caller decides confirmation
- Decision: banners accept a standard HA `tap_action` including `perform-action`, with HA's optional `confirmation`. No forced confirmation.
- Alternatives: forced confirm for `perform-action`; navigate/url only.
- Consequences: risk R-1.

## D-016 Limits and overflow
- Decision: options flow sets max banners (default 50) and eviction on/off (default on). On overflow the oldest banner with the lowest severity is evicted, never a `critical` one; if every stored banner is critical, create fails with `too_many_banners`. Title max 100, message max 1000 chars. Each eviction fires `heads_up_banner_cleared` with reason `evicted`.
- Alternatives: always reject; fixed limits.

## D-017 Card sorting is a card option
- Decision: `sort: severity | time`, default `severity` (critical > warning > info > success, then `updated_at` newest first).

## D-018 Popup: later
- Decision: MVP shows inline banners only.

## D-019 Minimum HA 2026.9.0
- Decision: `hacs.json` minimum 2026.9.0; dev image and tests pinned to 2026.9.4; CI also tests 2026.10.

## D-020 Public GitHub repo when published
- Decision: the repo is designed to be installable as a public HACS custom repository. Publishing is a separate, explicit maintainer decision; nothing is pushed until then.

## D-021 Card delivery and tech
- Decision: own card (existing notification cards checked, e.g. HKI Notification Card, lack severity/timeout/condition/per-person fields), plain JS single ES module, no build step, served by the integration (static path + `add_extra_js_url`, version query for cache-busting). Editor: custom element (`getConfigElement`). Dismiss via an X button (48 px target), no swipe.
- Alternatives: reuse an existing card; TypeScript + Lit + bundler; `getConfigForm`; YAML-only; manual `/local` resource; separate HACS plugin repo; swipe.

## D-022 External call paths: actions only
- Decision: HA actions are the only contract. REST `/api/services/heads_up/...` and WebSocket `call_service` work through HA core.
- Alternatives: custom event listener; persistent-notification mirror (both in OPEN_QUESTIONS).

## D-023 Persistence
- Decision: `Store` with `async_delay_save` (1 s). Timeout stored as absolute `expires_at`; banners expired while HA was down are dropped on start with an `expired` event.
- Alternatives: save on every change.
- Consequences: a hard crash can lose the last second of changes.

## D-024 Timeout input
- Decision: `timeout` accepts seconds or an HA duration (`{minutes: 5}`). Absolute datetimes not accepted in MVP.

## D-025 Metadata: `tag` only
- Decision: optional `tag`; card can filter by tag; `clear_banner` accepts `tag`. No `priority`, no `source`.

## D-026 Options flow
- Decision: single config entry; options: max banners + eviction, default dismiss scope, default timeout (see D-031).

## D-027 CI and tests
- Decision: GitHub Actions with ruff, mypy, pytest-homeassistant-custom-component, hassfest, HACS action, vitest for card logic, docs-check. Playwright manual only.

## D-028 Research sources
- Decision: API facts are verified against HA docs and source (developers/contributors.home-assistant.io, home-assistant.io, github.com/home-assistant, hacs.xyz) and recorded in `docs/dev/HA_API_NOTES.md`.

## D-029 Action permissions: any user
- Decision: any authenticated user may call the actions and dismiss from the card. `show_all` and admin clear require admin.
- Alternatives: admin-only actions.

## D-030 Defaults set during design
- Generated IDs: `hu_` + 10 hex chars.
- `condition.state` accepts a string or a list of strings (match any).
- `timeout` range 0 or 1 s – 365 days; `max_banners` range 1–200.
- Eviction order: `success` < `info` < `warning`, oldest `updated_at` first; upserts never evict.
- `heads_up/subscribe` sends the full visible list on every change; `heads_up/admin_clear` is a separate admin-only command.
- `clear_banner` with an unknown `id` returns `cleared: 0`.
- Option changes apply to new banners only.
- Removing the config entry deletes the storage file.
- `integration_type: service`, `iot_class: local_push`.

## D-031 Shipped default timeout 24 h (R-4)
- Decision: option `default_timeout` ships as 24 h and applies to every banner created without `timeout`. It can be cleared in the options flow; the form warns that without it banners stay until cleared. A caller passes `timeout: 0` for a banner with no timeout.
- Alternatives: no default; 24 h only for waiting banners.

## D-032 Toolchain
- Decision: `uv` manages Python 3.14 and a project `.venv`; `uv.lock` committed. Docker for the dev HA. MIT license.
- Alternatives: system Python; pytest in Docker only; Apache-2.0.
- Consequences: HA 2026.9.4 needs Python ≥ 3.14.2 (N-23).

## D-034 Test environment
- Decision: `pytest-homeassistant-custom-component==0.13.367` (pins `homeassistant==2026.9.4`) and `home-assistant-frontend==20260826.7` as dev dependencies.
- Consequences: the `frontend` dependency sets up in tests.

## D-035 Human user pages created with content
- Decision: `docs/actions.md`, `card.md`, `examples.md`, `troubleshooting.md`, `limitations.md`, `uninstall.md`, `upgrading.md` are created in the phase that ships their content, not as heading-only files.
- Reason: a heading-only page documents something that does not exist yet.

## D-036 Repo contains only neutral, installation-independent content
- Date: 2026-10-25.
- Decision: no references to any specific installation, household, device, host, address or tool configuration in tracked files or history. Private notes and local tooling live in gitignored `.private/` and `.claude/local/`.
- Consequences: git history rebuilt before any publication.

## D-037 English only
- Date: 2026-10-25.
- Decision: all UI strings (actions, options flow, exceptions, entity names, card) are English. No German translation ships. Strings stay in HA translation files and one card string table, so another language is a new file, not a code change.
- Alternatives: English + German (earlier requirement, withdrawn).

## D-038 `wait_for_condition: false` on an existing ID removes the old banner
- Date: 2026-10-25.
- Decision: when `create_banner` with `wait_for_condition: false` finds the condition false and a banner with that `id` exists, the existing banner is removed (`heads_up_banner_cleared`, reason `condition`) and the response status is `condition_false`.
- Alternatives: keep the old banner unchanged.
- Reason: the caller replaced the ID; keeping the old text would show content the caller no longer wants.

## D-039 Targeting and condition data never leave the backend
- Date: 2026-10-25.
- Decision: `heads_up/subscribe` payloads omit `people`, `condition`, `mode`, `dismissed_by` and internal condition state. Each item carries `active` and `dismissed` for the viewer.

## D-040 Empty card hides its host element
- Date: 2026-10-25.
- Decision: with `show_empty: false` the card sets `display: none` on its host element. It does not add a visibility condition or ask users to add one to their dashboard.
- Alternatives: render an empty `ha-card`; recommend a visibility condition on `sensor.heads_up_active_banners` (global count, not per user).
- Reason: N-14 spike shows no extra gap in a sections view, and the card knows the per-user list.

## D-041 The card manages its own re-subscribe
- Date: 2026-10-25.
- Decision: the card calls `subscribeMessage` with `resubscribe: false`, listens for the connection event `ready` and subscribes again, and retries a failed subscribe after 1, 2, 5, 10 and then every 30 seconds. While it fails it shows a one-line error.
- Alternatives: rely on the library's re-subscribe (fails when HA accepts clients before `heads_up/subscribe` exists, N-40); register the WebSocket commands earlier (cannot be earlier than integration setup).
- Reason: observed failure on the dev HA after a container restart.

## D-042 Card serving and tooling
- Date: 2026-10-25.
- Decision: `async_register_static_paths` runs once in `async_setup`; `add_extra_js_url` with `?v=<manifest version>` runs per entry and is removed on unload (N-41). Card tests use vitest 3.2.4 from a dev-only root `package.json`; `make test-card` and a CI job run them. `make check` includes `make test-card`. The card passes `{tap_action}` to Home Assistant's `hass-action` event and dispatches only for banners that have one (N-38).
- Alternatives: register the path per entry (duplicate registration on reload); a vendored test runner.
- Consequences: Node 22 is needed for card tests, not for running the card.

## Gate log
- 2026-10-24: Phase 0 design approved, with D-031.
- 2026-10-25: Phase 1 complete; Phase 2 approved.
- 2026-10-25: Phase 2 complete; Phase 3 approved.
- 2026-10-25: Phase 3 complete; Phase 4 approved.
- 2026-10-25: Phase 4 delivered (card, serving, tests, docs); Phase 5 not approved.
