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

## D-043 Phase 5 examples and scope
- Date: 2026-10-25.
- Decision: `docs/examples.md` covers four examples: an open window with a condition (automation), a critical alert for one person (script), a tap action with confirmation, and REST and WebSocket calls for external systems. No blueprint ships in this phase. Every YAML example is validated by `make docs-check` and was run on the dev HA.
- Alternatives: one blueprint (entity state to banner); no REST/WebSocket page.
- Reason: actions are the only contract (D-022); plain YAML is enough and a blueprint adds a second surface to keep stable.

## D-044 Damaged storage never stops the integration
- Date: 2026-10-25.
- Decision: an undecodable `.storage/heads_up.banners` is handled by HA's `Store`: it renames the file to `.corrupt.<time>`, logs an error and returns no data, so Heads Up starts empty (N-45, checked on the dev HA). A readable file with a damaged banner entry: that entry is skipped with an error log naming its `id`, the rest loads, and the file is rewritten (`tests/test_storage_corruption.py`).
- Alternatives: fail setup and ask the user to delete the file (DESIGN §10 before Phase 6).
- Reason: banners are transient; a dead integration costs more than lost banners.

## D-045 Card can miss the first second after an HA start
- Date: 2026-10-25.
- Decision: accept and document. HA serves `index.html` from the start of the web server, and `heads_up` adds its module URL a moment later (about 0.6 s in the dev HA); a page loaded in between has no card until it is reloaded (N-42).
- Alternatives: none inside an integration: `add_extra_js_url` cannot run before the integration is set up.
- Consequences: documented in `docs/limitations.md` and `docs/troubleshooting.md`.

## D-046 Phase 6 packaging choices
- Date: 2026-10-25.
- Decision: the brand icon is generated by `scripts/make_icon.py` (no dependencies) into `custom_components/heads_up/brand/icon.png`, the location HA 2026.3+ and the HACS validator read (N-47). README screenshots are not included; the maintainer adds them. CI gets a second Python job on HA 2026.10.4 with `pytest-homeassistant-custom-component==0.13.375`; it ran locally in a throwaway venv, CI itself has not run (no remote).
- Alternatives: icon supplied by the maintainer; SVG mock-up instead of screenshots; documenting the 2026.10 check only.

## D-047 Card follow-up choices (not implemented)
- Date: 2026-10-25.
- Decision: the card's "time since triggered" uses `updated_at`. The option `show_severity` defaults to `false` and hides only the text label; the severity icon and color stay, so severity is still not color only.
- Alternatives: `created_at`; default `true`.
- Consequences: the five card follow-ups in `docs/OPEN_QUESTIONS.md` wait for a phase approval. Implementing `show_severity: false` by default requires changing the wording in DESIGN §3 and `.claude/rules/frontend-card.md`.

## D-048 Card design phase: options and behaviour
- Date: 2026-10-25.
- Decision (maintainer's answers):
  - `layout: compact` is one line per banner: icon, time, title and message on one truncated line, full text as tooltip (`title` attribute). No tap-to-expand, so a tap keeps meaning `tap_action`.
  - Card option `title`: a header inside the card above the banners; shown with the card only.
  - `show_time` (default `false`): relative time from `updated_at` (D-047), refreshed every 30 s.
  - `show_severity` (default `false`, D-047): hides the text label only. A visually hidden label stays for screen readers.
  - `colors`: map from severity to a CSS color or theme variable; defaults stay the theme variables. `colorize` (dropdown): `all` (background, icon, left bar; today's look, default), `background`, `icon`, `bar`.
  - `clear_all` (default `false`): a "Clear all" button that dismisses, for the viewer, every dismissible banner the card matches (filters applied, including banners behind "Show more"). New WebSocket command `heads_up/dismiss_many`. Global-scope banners are removed for everyone, as with the X button. No confirmation.
  - `swipe_to_dismiss` (default `false`): swipe either way dismisses a dismissible banner, no confirmation. Kept only if the browser spike shows no conflict with vertical scrolling and `tap_action`.
  - `collapsed_items` (default off): show N banners and a "Show N more" / "Show less" button. `max_items` stays the hard cap on the whole list.
  - `empty_message` and `empty_icon` (default `mdi:bell-check-outline`): when no banner matches and `empty_message` is set, the card shows the icon and the text centered. Without a message, `show_empty` keeps its meaning (D-040).
- Alternatives: see the answers listed in `docs/OPEN_QUESTIONS.md` before this decision.
- Consequences: the "severity is never color only" rule now means icon shape plus a screen-reader label; the visible label is optional. DESIGN §3, §8 and `.claude/rules/frontend-card.md` change with the code.

## D-049 Card design details not covered by the answers
- Date: 2026-10-25.
- Decision:
  - `show_time` text: under 1 minute "just now"; then "N min ago" up to 59; "N h ago" up to 23; "1 day ago"; "N days ago". Refreshed every 30 s by a timer that runs while the card is on the page. A time in the future or an unreadable time reads "just now".
  - Parts that `colorize` leaves uncolored use theme variables: background `--secondary-background-color`, icon `--primary-text-color`, label `--secondary-text-color`, no left bar color.
  - `colors` values must be non-empty strings without `;`, `{` or `}`, because they go into a CSS custom property. The card also checks them with `CSS.supports("color", value)` and falls back to the theme variable.
  - Swipe: only when `swipe_to_dismiss` is on and the banner is dismissible; starts after 10 px of horizontal movement; a mostly vertical gesture is left to the browser; dismiss at 80 px or 30% of the banner width, whichever is larger; a swipe suppresses the click that follows it, so the tap action does not run.
  - `heads_up/dismiss_many` skips unknown and non-dismissible IDs and reports `{dismissed, skipped}`; it needs no admin rights.
  - The card editor shows defaults for unset dropdowns and writes only non-default values.
- Reason: smallest behaviour that satisfies D-048 and keeps the saved YAML minimal.

## Gate log
- 2026-10-24: Phase 0 design approved, with D-031.
- 2026-10-25: Phase 1 complete; Phase 2 approved.
- 2026-10-25: Phase 2 complete; Phase 3 approved.
- 2026-10-25: Phase 3 complete; Phase 4 approved.
- 2026-10-25: Phase 4 delivered (card, serving, tests, docs); Phase 5 not approved.
- 2026-10-25: Phase 4 reviewed; Phase 5 approved (examples set in D-043).
- 2026-10-25: Phase 5 delivered (`docs/examples.md`, call paths verified); Phase 6 not approved.
- 2026-10-25: Phase 5 reviewed; Phase 6 approved (choices in D-044 to D-046).
- 2026-10-25: Phase 6 delivered and committed; Phase 7 (card design, D-048) approved.
- 2026-10-25: Phase 7 delivered (card design options, `heads_up/dismiss_many`); not committed at the time of writing; no further phase approved.
