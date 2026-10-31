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

## D-050 Card URL carries a content hash
- Date: 2026-10-25.
- Decision: the module URL is `/heads_up/heads-up-card.js?v=<manifest version>-<first 8 hex of the file's SHA-256>`. The URL added with `add_extra_js_url` is remembered and the same one is removed on unload.
- Alternatives: version only (D-042); `Cache-Control: no-cache` on the file.
- Reason: with the version alone, a build with the same version had the same URL, and a maintainer's Safari kept showing the old card after Phase 7 (screenshot, 2026-10-25). The file was first served without `Cache-Control`, only `ETag` and `Last-Modified` (N-52); D-064 changes that.

## D-051 First release prepared as 0.1.0
- Date: 2026-10-25.
- Decision: version `0.1.0` (not `1.0.0`: the integration ran only on a dev instance); HACS and hassfest checks move to `.github/workflows/validate.yml` (official layout, daily run, hassfest with checkout, N-53, N-54); README offers HACS custom repository and manual install. Tag, release, visibility and repository settings stay with the maintainer (D-020).
- Alternatives: `1.0.0`; keeping the checks in `ci.yml`.

## D-052 Phase 8 proposal: watch rules as config subentries
- Date: 2026-10-25.
- Decision: rules ("show a banner while entity X is in state Y") are config subentries of the single entry, shown as virtual banners built in memory, never stored in `.storage/heads_up.banners`, never evicted, not counted against `max_banners`. Design in `docs/DESIGN.md` §17. Phase 8 is not yet approved.
- Alternatives: card-level rules (repeated per card); YAML in `configuration.yaml` (reload, breaks D-026); label-based watching (D-057).
- Reason: one definition, shown on every card for every targeted user, without an automation.

## D-053 Rule banner with unavailable or unknown entity is hidden
- Date: 2026-10-25.
- Decision: while the entity state is `unavailable`, `unknown` or missing, the rule banner is not shown.
- Alternatives: keep the last in-memory result (as D-006 does for stored banners).
- Reason: nothing is stored for rule banners, so there is no result to keep after a restart; showing only real matches is predictable.

## D-054 Rule banners count in the active-banner sensor
- Date: 2026-10-25.
- Decision: `sensor.heads_up_active_banners` counts active rule banners as well. They still do not count against `max_banners`.
- Alternatives: count stored banners only.
- Reason: the sensor then matches what the cards show.

## D-055 Rule message supports a `{name}` placeholder
- Date: 2026-10-25.
- Decision: a rule has fixed message text plus an optional `{name}`, replaced with the entity's friendly name (entity ID if it has none). No other placeholders or templates (D-005).
- Alternatives: fixed text only.
- Reason: one wording can serve several rules.

## D-056 Rule banners: per-rule `dismissible` switch, dismissal until the condition flips
- Date: 2026-10-25.
- Decision: each rule has `dismissible` (default `false`). A dismissible rule banner is dismissed per user only (no global scope). The dismissal is held in memory and cleared when the condition turns false, so the banner returns the next time the entity enters the state. A restart also clears dismissals. `heads_up/admin_clear` on any rule banner is rejected with `rule_banner`; disable or delete the rule instead.
- Alternatives: never dismissible (the original request); dismissals persisted in storage.
- Reason: maintainer chose the switch; the default keeps the requested non-dismissible behaviour. In-memory dismissals avoid a second store.

## D-057 Label-based watching is not part of Phase 8
- Date: 2026-10-25.
- Decision: no label-based watching in Phase 8; the idea stays in `docs/OPEN_QUESTIONS.md`.
- Alternatives: include it.
- Reason: a second path with no custom message or severity widens the phase.

## D-058 Rule banners fire created and cleared events
- Date: 2026-10-25.
- Decision: rule banners fire `heads_up_banner_created` when the condition turns true and `heads_up_banner_cleared` with `reason: rule` when it turns false or the rule is disabled or deleted. They also fire `heads_up_banner_dismissed` with `scope: user` for a dismissal. Events carry `id` = `rule_<subentry_id>` and `tag` = `rule`. No events are fired for the state found at setup (open detail: Q-W7).
- Alternatives: no events.
- Reason: lets automations react to rule banners.

## D-059 Phase 8 implementation details
- Date: 2026-10-25.
- Decision: rule banner ID `rule_<subentry_id>` (uppercase ULID, so no action can use it, N-59); `tag` is `rule`; mode is `recurring` internally; editing a rule rebuilds its banner (dismissals reset, no event if it stays active); a rule that is enabled but false is listed with `show_all` as `active: false`; setup fires no events (resolves Q-W7); `{name}` is replaced literally and no escape exists; the flow validates entity existence, non-blank message (max 1000) and title (max 100).
- Alternatives: events at setup; storing rule banners.
- Reason: smallest behaviour that satisfies D-052 to D-058 and keeps rule banners out of the store.

## D-060 Phase 9: condition operators shared by rules and actions
- Date: 2026-10-25.
- Decision: `condition` (action) and watch rules get an optional `operator`: `equals` (default), `not_equals`, `above`, `below`, `between`, `contains`, `not_contains`. One matcher (`custom_components/heads_up/conditions.py`) serves both. `state` stays a string or list: `equals`/`contains` match any value, `not_equals`/`not_contains` match when none matches, `above`/`below` take one number, `between` takes two (inclusive). Without `operator` nothing changes for existing banners and rules.
- Alternatives: `not_equals` only; full set with regex and "changed in the last N minutes".
- Reason: maintainer chose equals, not equals and numeric; text `contains` is cheap with the same matcher. Regex and time-based operators widen the phase.

## D-061 Operators and missing values
- Date: 2026-10-25.
- Decision: `unavailable`, `unknown` and a missing entity hide the banner for every operator, `not_equals` included (D-053, D-006 stay). For the new operators a missing attribute, and for numeric operators a value that is not a number, count as no real value: the condition is not evaluated. `equals` keeps its current result for a missing attribute (no match).
- Alternatives: `not_equals` matches unavailable devices.
- Reason: "is not on" must not fire because a device dropped off the network.

## D-062 Release 0.2.1 instead of moving the v0.2.0 tag
- Date: 2026-10-25.
- Decision: `v0.2.0` was published from `c3ed219` with `manifest.json` still at `0.1.0` and no `[0.2.0]` changelog section. The tag stays; `0.2.1` carries the manifest and changelog fix. RELEASE.md now says to commit and push the version bump before tagging.
- Alternatives: move the published tag and republish.
- Reason: a published tag is not rewritten.


## D-064 Card file is cached by the browser
- Date: 2026-10-26.
- Decision: `/heads_up/heads-up-card.js` is registered with `cache_headers=True`, so it is served with `Cache-Control` (long `max-age`). Partly supersedes D-050, which kept it uncached.
- Alternatives: keep revalidating on every load (D-050).
- Reason: intermittent "Custom element doesn't exist: heads-up-card" on plain page reloads with no restart. HA loads the module with an unordered `import()` and a dashboard that renders the card before it arrives waits about 2 s before giving up; a fetch on every reload makes that miss possible. The URL contains the file hash (D-050), so a changed file is a new URL and a cached copy is never stale. The cause is inferred from HA's frontend behaviour, not reproduced.


## D-065 A rule banner's time restarts when its condition turns true
- Date: 2026-10-26.
- Decision: when a watch rule's condition flips to true, the banner's `updated_at` is set to that moment. Before, it stayed at the time the rule was loaded (HA start or rule edit), so `show_time` read "15 h ago" for a banner that had just appeared. Part of D-047: `updated_at` is the time of the trigger.
- Alternatives: leave `updated_at` and let the card use a new field.
- Reason: the card's time text means "since it appeared"; for a rule that is the flip. A message change while the condition stays true does not restart the time.


## D-066 Condition `for`, no `at_least` and `at_most`
- Date: 2026-10-26. Phase 10 requested and approved by the maintainer.
- Decision: a condition (action and watch rule) takes an optional `for`, 1 second to 24 hours, stored as seconds. The condition must be true for the whole time before the banner shows. After a restart or reload a banner that was shown stays; waits start again (timers are not stored). An unavailable entity when the wait ends shows nothing. `at_least` and `at_most` are not built.
- Alternatives: count from the entity's `last_changed` (wrong for numeric operators and attributes); store the start of the wait (needs storage for rules, D-058); `at_least` and `at_most` as inclusive single bounds (the maintainer saw them as redundant next to `for`; `between` covers the inclusive case).
- Reason: the smallest rule that never shows a banner early and works for every operator. The maintainer chose "timer restarts" and "skip at_least/at_most" (2026-10-26).

## D-067 Template conditions in `create_banner`
- Date: 2026-10-26.
- Decision: `condition.template` replaces `entity_id`, `operator`, `state` and `attribute` (mixing them is a validation error); `for` may be added. Tracked with `async_track_template_result`, so time functions such as `now()` also re-evaluate. A render error leaves the banner as it was. Templates are not available in watch rules (maintainer scope). Partly resolves D-005.
- Alternatives: a template next to `entity_id` as an extra condition; tracking only the entities found at render time (as D-063 does for rule messages, which cannot follow `now()`).
- Reason: one clear shape per condition; the tracker helper is the supported way to follow a template (N-60).

## D-063 Rule messages render Home Assistant templates
- Date: 2026-10-26.
- Decision: a rule message is rendered as a Home Assistant template (`{{ states('...') }}`), after `{name}` is replaced. Entities the template reads are tracked, so the text updates when they change; time-based functions such as `now()` are not refreshed. An invalid template is refused by the rule form (`message_template_invalid`); a template that fails at render time shows the unrendered text and logs a warning. This changes D-055 ("no other placeholders or templates"); `create_banner` is unchanged (HA renders its data before the call, D-017).
- Alternatives: reject templates in the form; a state placeholder without Jinja.
- Reason: a maintainer rule used `{{ states(...) }}` and showed the raw text. Maintainer chose rendering.

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
- 2026-10-25: `main` pushed to the private repository `Seyphaton/ha-heads-up` (maintainer approval); all commits re-authored to the GitHub noreply identity; no tag or release.
- 2026-10-25: Phase 8 (watch rules) proposed in DESIGN §17; design choices answered (D-052 to D-058).
- 2026-10-25: Phase 8 approved; delivered (watch rules, D-059); not committed at the time of writing.
- 2026-10-25: Phase 9 (condition operators, D-060, D-061) requested and approved by the maintainer.
- 2026-10-25: Phase 9 delivered (condition operators); `make check` and `make hassfest` green; not committed at the time of writing.
- 2026-10-25: `v0.2.0` published by the maintainer; `0.2.1` prepared (D-062).
- 2026-10-26: Phase 10 (condition `for`, template conditions, D-066, D-067) requested and approved by the maintainer; delivered; not committed at the time of writing.
- 2026-10-27: Phase 12 (banner buttons and snooze, D-069, D-070) requested and approved by the maintainer; delivered and committed; not pushed.

## D-068 `empty` and `not_empty` operators; State is not prefilled
- Date: 2026-10-27. Phase 11 requested and approved by the maintainer.
- Decision: two operators, `empty` and `not_empty`, ignore `state`. A value is empty when it has no text after stripping spaces; a missing attribute and an empty list or object count as empty. `unavailable` and `unknown` still change nothing. The rule form's State field has no default value; an empty field still means `on` for equals and does not equal, and is stored as nothing for the new operators.
- Alternatives: allow an empty string in the State list (a blank entry is easy to leave by accident); `not_equals` with `""` only (undiscoverable in the form); treating a missing attribute as no result (D-061).
- Reason: "has a value" is a common condition. Treating a missing attribute as empty matches what a user means by "no value". Keeping `on` as the fallback for equals and does not equal keeps old rules and the documented default.
- 2026-10-27: Phase 11 delivered; not committed at the time of writing.

## D-069 Snooze: opt-in, per user or global, fixed choices
- Date: 2026-10-27. Phase 12 requested and approved by the maintainer; scope and swipe behaviour answered by the maintainer.
- Decision: a banner is snoozable only if it says so (`snoozable`, default off through the option `default_snoozable`). Scope (`user` or `global`) and the offered durations are banner fields with integration-wide defaults, like `dismiss_scope`. The viewer picks one of the offered durations; the backend rejects any other. Banners with `dismissible: false` cannot be snoozable. A snooze ends on its time, on upsert, when a recurring condition turns false and true again, or when the banner goes. Snoozes are stored; a rule's snoozes are not. The condition `for` wait is not stored in this phase.
- Alternatives: snoozable by default (every dashboard would change after an update); one fixed duration per banner (no choice for the viewer); any duration from the client (no limit on what a viewer can hide); critical banners never snoozable (not chosen by the maintainer).
- Reason: the default keeps existing dashboards unchanged. A fixed list keeps the stored data and the check simple.
- Swipe: with `swipe_to_dismiss`, a right swipe on a snoozable banner opens the choices, a left swipe dismisses. The choices appear in a row under the banner instead of behind it, so the same row serves the snooze button and keyboard users.

## D-070 Banner buttons: an event, an optional dismissal, an action run by the card
- Date: 2026-10-27. Phase 12.
- Decision: up to 3 buttons per banner (`actions`). Pressing one calls `heads_up/action`, which fires `heads_up_banner_action` and, with `dismiss`, dismisses for that user. A button's `action` runs in the card through `hass-action`, as `tap_action` does, after the call succeeded. The backend runs no action itself. Rule banners had no buttons in this phase; D-073 added them.
- Alternatives: run the action in the backend (it would run with no user context and needs its own permission rules); event only (every button needs an automation); no limit on buttons (the row would not fit a phone).
- Reason: the event lets automations react without new code; running the action in the card reuses HA's confirmation and permission handling. The limit of 3 keeps the row short; phone width was not checked.
- Open: the permission model is as for dismissals: any user who can see a banner can press its buttons (D-029).
- 2026-10-27: Phase 12 delivered; commits `45baa6d`, `0905d7e`, `d9f36d4`, `bb76969` and the documentation commit.

## D-071 German, French and Spanish translations
- Date: 2026-10-27. Requested by the maintainer as part of the adoption work.
- Decision: English stays the source language of code, comments, docs and `strings.json` (D-037). Added: `translations/de.json`, `fr.json`, `es.json` (the same keys as `strings.json`, placeholders unchanged) and a `TRANSLATIONS` table in the card, applied by `setLanguage(hass.language)`. A language code with a region (`fr-CA`) uses its base language; other languages and missing keys show English. Banner text is never translated. Code samples inside descriptions stay unchanged.
- Alternatives: separate translation files for the card (the card is one file without a build, D-021); more languages now.
- Reason: the card and the forms are what a household sees. A table in the card file keeps the no-build rule.
- Open: the texts were written without review by native speakers. A string added to `strings.json` or the card needs a line in each language, or it shows English there.

## D-072 The card defines its elements only after Home Assistant's frontend
- Date: 2026-10-27. Reported by the maintainer: the error "Custom element doesn't exist: heads-up-card" appeared on every second or third reopen of the dashboard in the iOS Companion app (0.3.0, local network), until the page was reloaded.
- Decision: the card module waits until `customElements.get("home-assistant")` is defined (polling the current `window.customElements`, every 25 ms, at most 10 s), then defines `heads-up-card` and `heads-up-card-editor` and adds the `window.customCards` entry once. Defining is skipped for a tag that is already defined.
- Cause (from the frontend source as described in public issue reports of other cards, not read in the frontend source by us): the app bundle replaces `window.customElements` with a scoped-registry polyfill. Extra modules are imported in parallel with the app bundle. A module that defines its element first defines it on the native registry, which the polyfill does not see; Lovelace's wait for the element never ends. Since 0.3.0 the module is cached (D-064), which makes the module faster than the app bundle more often. This replaces the explanation of D-045 for reloads without a restart; D-045 (page loaded in the first second after a start) stays.
- Alternatives: a Lovelace resource (the integration must not change dashboards, rule 3); retry loading the module under a new URL (needs a loader outside the card); removing the cache header (restores the race only partly).
- Not reproduced: the failure itself did not occur in the browser pane (Chromium with the polyfill, 8 reloads); it was seen before the change as a missing element after container restarts, once. Checked after the change: the elements and one `customCards` entry exist on every reload; vitest covers the wait. Not checked on an iPhone or iPad.

## D-073 Parity of banner sources; rule buttons, tap action, dismiss scope, template condition
- Date: 2026-10-27. Requested by the maintainer after noticing that watch rules had no buttons; the maintainer chose to close all three gaps found in the audit.
- Decision: banners from actions and from watch rules offer the same features (CLAUDE.md rule 9, `docs/DESIGN.md` §22). Exceptions are listed with a decision number. Added to rules: buttons (`actions`) and tap action as YAML fields validated by the action's schemas; dismiss scope (`user` or `global`; a global dismissal of a rule hides it for everyone until the condition flips, marker `*` in `dismissed_by`); a template condition in place of an entity. A rule without a dismiss scope stays `user` (compatibility, not the option default). `{name}` in a template rule is the rule name.
- Alternatives: three plain label fields for buttons (no per-button action or dismiss); closing only the buttons gap; removing a rule banner on a global dismissal (a rule banner is virtual and returns when the condition flips); the option default for rules without the field (changes existing rules for users whose default is global).
- Reason: a viewer should not see a different banner depending on how it was made; one schema per input keeps both sources from drifting.
- Supersedes: the part of D-067 that kept templates out of watch rules (maintainer's decision on 2026-10-27).

## D-074 Ending a snooze early from the card
- Date: 2026-10-27. Requested by the maintainer as an optional feature ("show snoozed button").
- Decision: WebSocket `heads_up/unsnooze` ends the snooze that hides a banner from the caller (a global one for everyone) and fires `heads_up_banner_unsnoozed`. `heads_up/subscribe` takes `show_snoozed`; the card option `show_snoozed` (off by default) sets it and shows a "Snoozed (n)" list with the time left and a Show now button. `snoozed_until` is now sent to the viewer, for their own snooze only.
- Alternatives: always sending snoozed banners (older cached cards would show them again); a button only on the banner (it is hidden while snoozed); a service for automations (not requested).
- Reason: without it a mistaken snooze could not be undone before it ended. Off by default keeps existing dashboards unchanged.

## D-075 Notification hub: direction, status undecided
- Date: 2026-10-28. Phase 15 (design only) on branch `design/notification-hub`; full record in `docs/dev/HUB_DESIGN.md`.
- Decision: the maintainer sees the integration as the central notification hub, with the dashboard banner as one channel. Whether the hub is built, and the amendment of the §1 non-goal "no push delivery", are not decided. Nothing of this reaches `main` without the maintainer's explicit go.
- Reason: today's banner delivery is the foundation; the hub extends it to more channels and features.

## D-076 Everything existing works without the hub
- Date: 2026-10-28.
- Decision: `create_banner`, `clear_banner`, `clear_all`, watch rules and the card keep working unchanged without any use of the hub. The hub is additive; without a policy a message is delivered to the dashboard channel only.

## D-077 Banner is one channel; the unit is a message
- Date: 2026-10-28.
- Decision: the unit a producer creates is a message with a lifecycle. Dashboard banner, Companion push, popup, speech and persistent notification are equal channels, each selectable per policy step. `create_banner` is the banner channel's action and takes no `channel` argument. Banner-only special fields are avoided.
- Open: the real action and argument set (one generic `notify` action versus per-channel actions) is decided in a dedicated API design session before any implementation.

## D-078 Banner and its notifications are one linked message
- Date: 2026-10-28.
- Decision: state changes on one surface (clear, expire, condition, dismiss, snooze, acknowledge) apply to all channels of the same message. A snooze clears the user's push, pauses their repeats and re-notifies at its end.

## D-079 Mental model: audiences and policies
- Date: 2026-10-28.
- Decision: an audience says who (flat, no set operations), a policy says how: up to 4 timed steps, each with audience, channels and per-channel profile; quiet hours; an acknowledgement rule. A policy applies by a list of severities and a list of tags (a banner keeps its single tag; `tag` gains routing as a third use next to the card filter and `clear_banner`). Caller may choose a policy and replace step 0's audience and channels; later steps, quiet hours and ack rule stay the policy's. Fallback audiences and channels are configurable per step, or none.

## D-080 Audience semantics
- Date: 2026-10-28.
- Decision: presence audiences: at home, not home, last to leave, first home, in or not in a zone. Membership is a snapshot when a step fires; a step may deliver on arrival to people not yet home. Companion devices are found from the person automatically, with manual override; all devices of a person are notified (same tag). Unknown presence: critical notifies anyway, lower severities skip with a trace.

## D-081 Acknowledgement, escalation, severity change
- Date: 2026-10-28.
- Decision: any recipient acknowledging stops escalation; whether a dismissal counts as acknowledgement is a policy setting. Quiet hours downgrade, critical bypasses unless the policy says otherwise. A severity change while active restarts the timeline with the policy of the new severity. After a restart an overdue step fires once if the message is still active and unacknowledged. Swiping a push away means nothing.

## D-082 Channels and admin UX
- Date: 2026-10-28.
- Decision: channels: banner, Companion push, popup (global on all dashboards, policy decides severities), speech (media players, Assist satellites, targeted speakers; rooms are HA areas with assigned speakers and displays, no occupancy sensors), persistent notification (targets everyone, no special handling). Lock-screen text is a policy setting, default full text. Admin surface: an own admin panel from the start (overview and editors, live preview, delivery trace, test send, first-run wizard).
- Open: build phasing is delayed until the design is final.

## D-083 Hub API: one generic notify action and channel shortcuts
- Date: 2026-10-28. API design session on branch `design/notification-hub`.
- Decision: `heads_up.notify` states content (title, message, optional text for speech), the primary channel, an audience or direct recipients (never both; allowed kinds depend on the channel) and a policy. Shortcuts `push`, `popup` and `speak` fix the channel, take an optional audience and have no escalation. `create_banner` stays as the banner shortcut, unchanged. One id per message for all channels; one generic clear removes the message everywhere. No separate acknowledge, snooze or dismiss actions: push messages get Dismiss and Snooze buttons automatically when allowed, handled by the hub, with the message's own buttons first. Written channels share one text; speech has an optional own text. Watch rules are stored `notify` calls plus a trigger and share its schema.
- Open: exact field names, and how `create_banner` fields and `condition` map onto `notify`.

## D-084 Source of truth
- Date: 2026-10-28.
- Decision: when and what live with the producer (automation, or a rule's trigger and stored `notify` arguments); who and how live in hub subentries (`audience`, `policy`); live state lives in the hub's message store and delivery ledger. The panel edits these subentries and keeps no store of its own.

## D-085 Escalation steps add channels and audiences
- Date: 2026-10-28.
- Decision: the call's channel and audience are step 0; policy steps and fallbacks may add other channels and audiences (for example banner, then push, then push to admins, then speech; or push to the last leavers with a fallback to everyone not at home).

## D-086 Conditions in the hub
- Date: 2026-10-28.
- Decision: the generic condition (entity with operators and `for`, or template) is used for the message lifecycle, as today. Policy, step, channel and recipient gates use predefined types: time window or quiet hours, presence, acknowledgement state, severity or tag. One extra gate type, a named condition, refers to a hub subentry that holds the generic condition schema; named conditions can also serve as lifecycle conditions. If the lifecycle condition turns false the message ends and all channels are cleared; gates are evaluated when a step is due, and a closed gate skips the step with a trace entry.
- Alternatives: predefined gates only (closed list); an inline single-entity gate (not reusable).
- Reason: simple forms for common gates, one escape hatch for the rest, one place for each generic definition.

## D-087 `notify` field list
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - Content: `message` (required), `title`, `icon`, `severity`, `actions`, `tap_action`, `tts_message` (optional text for speech).
  - Lifecycle, same meaning as in `create_banner`: `id`, `tag`, `timeout`, `condition`, `mode`, `wait_for_condition`, `dismissible`, `dismiss_scope`, `snoozable`, `snooze_scope`, `snooze_options`.
  - Delivery: `channels` (required list; step 0 of the delivery), `audience` (name) or `recipients` (list of entities by kind: person, notify target or device, media player, assist satellite, area), never both, allowed kinds depend on the channel; `policy` (name; omitted: matched by severity and tag per D-079; `none` skips all policy behavior).
  - `create_banner` keeps its fields including `people`; in `notify` the same idea is `recipients`.
  - Shortcuts `push`, `popup`, `speak` are fire and forget without an `id`; with an `id` they are full messages (update, clear, expire).
  - `notify` returns `id`, `status` and a per-channel summary; delivery detail stays in the trace.
- Alternatives: single `channel`; one field `to` for audience and recipients; keeping `people` in `notify`; `spoken` or `speech` as the text name; default channel banner when `channels` is omitted.
- Open: validation details per channel (which recipient kinds each channel accepts), `tts_message` fallback when omitted, exact status values.

## D-088 Audience, recipient group and person profile
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision: two object types answer "who". An audience is people-based and channel-neutral: persons, or a presence kind (D-080). A recipient group is a named set of explicit targets (media players, Assist satellites, areas, notify targets) tied to the channels it fits. `audience` takes the first, `recipients` takes entities or the name of a recipient group. Per-person device handling lives in a new hub subentry, the person profile: auto-detected devices, manual add and remove, a primary device, accepted channels; audiences reference persons only. Built-in audiences without setup: Everyone, Admins, At home, Not home, Last to leave, First home. A person with no usable device is skipped on push with a trace entry and shown in the panel with a fix link; banner and popup still work.
- Alternatives: one audience type for everything; speakers only as direct recipients; overrides inside each audience or in a global options table; failing at save; falling back to the banner.
- Open: the shape of the person profile in the Home Assistant UI (name clash with the core person entity), which recipient kinds each channel accepts exactly, area-to-speaker assignment.

## D-089 Policy mechanics: timing, gates, matching, fallback
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - Step timing is an offset from the message start (0, 5, 15 minutes); due times are stored.
  - A closed gate may skip the step, delay it until the gate opens (bounded by the message lifetime), downgrade the step's profile, or stop the delivery completely. Which outcome applies is a setting of the gate.
  - Matching: the most specific policy wins (tag match before severity only). Two policies that match exactly the same severities and tags are refused when the second is created.
  - A fallback (audience or channels) applies when the audience resolves to nobody, when all deliveries of the step failed, and when nobody acknowledged in time (escalation).
- Alternatives: delay after the previous step; explicit priority numbers; all matching policies running; any overlap being an error.
- Open: exact meaning of "stop completely" (ends delivery only, the banner stays; or ends the message), field names of a step and of a gate.

## D-090 Channels: recipient kinds, push levels, speech text, popup
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - Recipient kinds per channel. Banner: audience, or persons (empty means everyone). Push: audience, or persons and notify targets or devices. Popup: audience, or persons and areas (displays). Speak: recipients only (recipient groups, media players, Assist satellites, areas), no audience. Persistent notification: none, it targets everyone.
  - Push level by severity: success and info passive, warning normal, critical time-sensitive (iOS) with matching Android importance. True iOS critical is an opt-in in the policy profile, because it needs app permission and cannot be replaced or grouped. Push must use the legacy `notify.mobile_app_*` services (N-61).
  - Speech text when `tts_message` is missing: the title if set, else the message, shortened to a length limit.
  - Popup by default: a non-blocking card in a corner for warning and lower, a centered modal for critical; one at a time in a queue, buttons as in the card, closes when the message is resolved.
- Alternatives: speak with an audience as a presence gate; critical push defaulting to iOS critical; all default levels; message spoken in full; nothing spoken without `tts_message`; always a modal.

## D-091 Channels: volume, speech cleanup, popup areas, rate limits
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - Speech uses announce when the player supports it, else plays at the current volume. The hub never changes or restores volume.
  - Speech is fire and forget. A resolved message says nothing; there is no all-clear feature.
  - Popups target persons only in the first version; area recipients for popups are not built (this narrows D-090: popup `recipients` are persons only for now).
  - Rate limits: simple defaults in the options (per device and global caps per minute, duplicate suppression of identical updates); suppressed counts appear in the trace.
- Alternatives: volume set and restored by the hub; an all-clear announcement; a display profile or a URL parameter for popup areas; duplicate suppression only; no limits.

## D-092 Acknowledgement and push buttons
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - A push shows an Acknowledge button only if the policy sets it (per step switch, default off).
  - Push buttons carry the message, the recipient and the action in their id (`hu:<message>:<recipient>:<action>`); a press is attributed to that recipient's person. The hub does not rely on the user in the event context (unverified, N-62). Unknown or stale ids are ignored with a trace entry.
  - The push Snooze button uses one duration, the first snooze option of the message, and reads for example "Snooze 15 min"; the other choices stay in the dashboard banner.
  - A banner shows "Acknowledged by <first name>" to everyone who sees it; a card option hides the line.
- Alternatives: Acknowledge button on every push or only with escalation; the event context user; two Snooze buttons; Snooze opening the dashboard; "Acknowledged" without a name; showing nothing.
- Open: the card option name, and what the line shows when several people acknowledged (first only, or all).

## D-093 Admin panel and wizard
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - Editing: audiences, recipient groups, policies, named conditions, person profiles and rules are edited in the panel with own forms (`ha-form` with selectors, as the card editor does) that save through Home Assistant's subentry flow APIs. Storage stays in config subentries, so the native dialogs keep working.
  - Wizard: a guided stepper in the panel (people, devices, loudness preset, test) and a config flow entry on the integration page, both creating the same objects.
  - Access: admins only, as a sidebar item; the panel's WebSocket commands require admin.
  - First panel covers: live preview (who would be notified now), per-message delivery trace, a list of recent messages, and a test send.
- Alternatives: panel only shows and native dialogs edit; panel with its own storage; wizard in one place only; read-only access for all users.
- Open: whether the recent-messages list survives a restart (relates to the history idea in OPEN_QUESTIONS, Phase 13 candidate); the panel registration API and serving under the no-build rule (D-021), to verify; the panel's strings in four languages.

## D-094 Naming, gate types, response values and policy layout
- Date: 2026-10-29. API design session on branch `design/notification-hub`.
- Decision:
  - The per-person hub object (D-088) is called a recipient profile.
  - Gate types: `time_window`, `presence`, `acknowledgement`, `severity_tag`, `named_condition`; gate outcomes: `skip`, `delay`, `downgrade`, `stop`.
  - `notify` response: message status `created`, `updated`, `waiting` or `condition_false` (as today), plus per channel counts of `sent`, `held`, `skipped` and `failed`.
  - Policy layout: `name`, `match` (severities, tags), `acknowledge`, `steps`; a step has `after` (seconds from message start), `audience` or `recipients`, `channels`, `profile`, `gates`, `fallback`; a gate has `type` and `outcome`. Accepted by the maintainer on 2026-10-29 ("Ok") after reading the sketch in `docs/dev/HUB_DESIGN.md`.
- Open: the exact fields of each gate type and of each channel profile.

## D-095 Gate and channel profile fields; `stop` meaning
- Date: 2026-10-29. API design session on branch `design/notification-hub`; accepted by the maintainer after reading the proposal file.
- Decision:
  - Gate fields: `time_window` (`from`, `to`, `days`, `bypass_severity`), `presence` (`who` as an audience, `state` as `any_home`, `none_home` or `all_home`), `acknowledgement` (`state` as `acknowledged` or `not_acknowledged`), `severity_tag` (`severities`, `tags`), `named_condition` (`name`, `state` as `true` or `false`). Every gate also has `type` and `outcome`.
  - Channel profile fields: push (`level`, `privacy`, `sticky`, `buttons`, `channel_id`), popup (`style`), speak (`language`, `announce`); banner and persistent notification have none.
  - `stop` ends delivery only; the message and its banner stay until their normal end.
  - Downgrade: push becomes passive without sound, speak is skipped, popup becomes a corner card, banner and persistent notification are unchanged.

## D-096 A step has one "who"; speech and people channels are separate steps
- Date: 2026-10-29. Found while building the mockup; corrects the example in D-094 and DESIGN §23.6.
- Decision: a step (and a `notify` call) has one audience or recipients value. Banner, push and popup take an audience or persons (push also phones); speech takes speakers, groups or satellites. A step that mixes speech with a people channel is invalid (`notify` returns a validation error; the panel blocks it). Escalation to speech is a separate step, as in the maintainer's example (push to admins, then speech).
- Alternatives: separate "who" per channel inside a step (more fields, harder to explain); speech reading an audience through a room mapping (rejected earlier, D-082).

## D-097 Typed policies replace bundled policies
- Date: 2026-10-29. Requested by the maintainer after trying the mockup ("way too complex"). Supersedes D-079 (a policy as up to 4 steps), D-086 and D-095 (gate list and gate types), the step and gate parts of D-089, and the layout of D-094. Everything else in D-075 to D-096 stands.
- Decision: a policy is one small rule with a type, a trigger ("When") and an effect ("Then"). Every policy has a name, an optional "Applies to" (severities and tags, empty means all), an optional "Only if" (a named condition) and can be disabled. Types in the first version:
  - Escalation: when nobody acknowledged within X minutes, also notify an audience or recipients on channels. Setting: dismissing counts as acknowledging. Several escalation policies form a chain.
  - Quiet hours: when a message is sent between two times (days selectable), wait until the end, send quietly (passive push, no speech, popup as card), or drop it. Setting: critical passes anyway.
  - Fallback: when the audience is empty or sending failed, send to an audience or recipients on channels instead.
  - Reminder: while not acknowledged, repeat every X minutes, up to N times.
  - Away: when a recipient is not home, send when they arrive, while the message is active.
  - Summarize: collect matching messages and send one summary, every N minutes or at a fixed time of day; nothing is sent individually while a message waits (all channels); the summary lists a count and titles, marks resolved ones and cuts at 10 with "and N more"; nothing is sent when nothing was collected; critical may be summarized if the policy says so, with a warning in the form.
- All policies that apply to a message are active at the same time. A second policy of the same type with the same "Applies to" and the same trigger is refused. Precedence when several act on one delivery: Summarize, then Quiet hours, then Away, then Fallback; Escalation and Reminder create later deliveries that pass through the same rules.
- Channel settings move out of policies to one settings page with defaults by severity: push level and lock-screen text, push buttons (Snooze and Dismiss; Acknowledge is added when an escalation or reminder policy applies, replacing the per-step switch of D-092), popup style, speech language and announce.
- The call stays as decided in D-087: `policy` names one policy, omitted means all that apply; `none` skips all.
- Alternatives: keep the bundled policy with steps and gates (too complex to edit and understand); a "Limit" type that drops or bundles (replaced by Summarize).
- Open: whether the dashboard banner is also held while a summary waits (as decided, all channels wait, so the message is not visible on the dashboard until the summary); severity, channels and lifetime of the summary message; whether "Default delivery" by severity is needed because step 0 always comes from the call; the final precedence order.

## D-098 Targets per channel: one call can send push, speech and persistent notification together
- Date: 2026-10-29. Requested by the maintainer ("it must be possible to send both push and tts and persistent"). Supersedes D-096 and the delivery fields of D-087 (top-level `audience` or `recipients`).
- Decision: `notify` takes `channels` (required list) and `to`, a mapping from channel to its target. A target is an `audience` or `recipients`, never both, and the kinds allowed depend on the channel: banner (audience or persons, empty means everyone), push (audience, or persons and phones), popup (audience or persons), speak (speakers, groups, satellites, areas; no audience), persistent notification (no target, it goes to everyone). Push, popup and speak need a target; banner and persistent do not. The shortcuts `push`, `popup` and `speak` keep a plain `audience` or `recipients` field because they have one channel.
- Policies use the same shape: the "Then" of Escalation and Fallback names channels and a target for each channel, so one escalation can push to admins, speak on the ground floor and create a persistent notification.
- Example:
  ```yaml
  action: heads_up.notify
  data:
    message: Water leak
    severity: critical
    channels: [push, speak, persistent]
    to:
      push: {audience: Admins}
      speak: {recipients: [Ground floor speakers]}
  ```
- Alternatives: one audience plus a separate `speakers` field; mixed recipient groups (fixed lists, no dynamic audiences).
- Open: whether `notify` also accepts a top-level default target for all people channels.

## D-099 No "Only if" and no named conditions for now
- Date: 2026-10-29. Requested by the maintainer after asking where "Only if" came from; it had no editor in the mockup.
- Decision: policies have no "Only if" field and the hub has no named conditions in the first version. This removes the escape hatch of D-086 and the "Only if" part of D-097. The generic condition stays where it is today: the message lifecycle condition of `notify` and `create_banner`. Cases such as "only while guest mode is on" are handled by the producer (an automation condition) or by disabling a policy.
- Alternatives: a named conditions screen and subentry type (reusable, one more concept); an inline single-entity condition on a policy.
- Reason: fewer concepts for the first version; the need is unproven. Recorded as an idea in `docs/OPEN_QUESTIONS.md`.

## D-100 Watch rules are frozen
- Date: 2026-10-30. Requested by the maintainer ("we are replicating automation functionality"); decided after a review of keeping, freezing and deprecating rules.
- Decision: watch rules keep working exactly as released in 0.4.0 and get no hub fields (no channels, targets or policy name). They are not edited in the panel; the panel shows a read-only list with the standard settings page as the place to edit. A rule message is a banner-channel message. Policies match by severity and tag, so quiet hours, escalation, reminders, summaries and the other policy types apply to rule messages without any change to the rule form; an escalation policy can push or speak a rule message after its delay. New needs are served by automations calling `notify`.
- Supersedes: the statement in D-083 and D-084 that watch rules are stored `notify` calls sharing its schema.
- Parity (rule 9): an exception row in DESIGN section 22.2 with this decision number: rules do not get channels and targets.
- Alternatives: rules fully in the hub with channels and a Rules tab (most convenient, most duplication, a second editor in the panel); deprecating rules with a migration to automations or a blueprint (cleanest long term, breaks users).
- Open: a "watch an entity" blueprint as the no-YAML path for new setups, and whether a custom integration can ship blueprints (unverified); deprecation later.

## D-101 One tab for preview and test send; no compose form
- Date: 2026-10-30. Requested by the maintainer after asking whether the mockup's "New notification" tab was part of the design (it was not).
- Decision: the panel has no form to compose and send real notifications; that is what automations and Home Assistant's action tool are for. The preview and the test send are one tab: content fields, the call with a target per channel, a simulated result per recipient and channel, the generated call to copy, and a Send test button, which is the only thing the panel sends.
- Alternatives: a separate compose tab (duplicates Developer Tools and the preview); preview without a test send.

## D-102 Panel navigation in two levels
- Date: 2026-10-30. Requested by the maintainer ("I don't like the unstructured list").
- Decision: five top-level groups with sub-pages. Overview (Status). Activity (Test send, Messages). Configuration (Audiences, Recipients, Policies, Channels, Watch rules as a read-only list). Settings (General, Setup wizard). FAQ and Examples. The wizard is a flow, started from Overview on first run and from Settings, not a page to browse. A group with one page shows no second row.
- Alternatives: the maintainer's four groups with Test send and Messages under Overview; three groups with Settings inside Configuration.

## D-103 Panel navigation, second version
- Date: 2026-10-30. Requested by the maintainer; replaces the grouping of D-102.
- Decision: Overview is a dashboard-like page only. Notifications and Rules holds Test send, Watch rules (read-only list, D-100) and Messages (the delivery trace). Configuration holds Audiences, Recipients, Policies and Channels. Settings is one page that covers everything the setup wizard sets up (people and devices, loudness preset) plus the hub switch, limits, history and identity; the wizard is only a button on that page (also offered from Overview on first run) that opens a guided window. FAQ and Examples stays as the last group.
- Alternatives: the five groups of D-102 with Activity and a Setup wizard page.

## D-104 Overview page content
- Date: 2026-10-30. Requested by the maintainer.
- Decision: the Overview is a dashboard page with four parts. A tile with the number of active notifications and their states (escalation ongoing, reminding, snoozed, held for a summary), opening a list of the active messages on click or double-click. A tile with the watch rules: how many are enabled out of all, how many are disabled and how many are showing a message now, opening the list. A log of the last actions (created, escalated, acknowledged, dismissed, snoozed, summary sent, skipped, failed, expired). A "needs attention" list of configuration errors and warnings, each with a link to the place that fixes it: an unavailable rule entity, a missing notify service for a device, a person without a usable device, an empty recipient group, an invalid policy, a policy that names a deleted audience, no escalation for critical, a switched-off hub.
- Open: how many log entries the Overview shows and how long they are kept (the Settings page has the history sizes); whether a double-click is needed at all on touch screens (a single tap opens the details in the mockup).

## D-105 A summarized message is held on every channel, the banner too
- Date: 2026-10-30. Confirmed by the maintainer; closes an open item of D-097.
- Decision: while a Summarize policy holds a message, no channel shows it, including the dashboard banner. It appears on the dashboard only in the summary. The Overview lists such messages as "in a summary", so they stay findable. Critical messages are only held if the policy includes them (a warning appears in the form).
- Alternatives: the banner shows at once and only other channels wait; a policy setting to also hold the banner.

## D-106 Summary message details, no default delivery, precedence
- Date: 2026-10-30. Closes the open items of D-097 and D-105.
- Decision:
  - A summary message gets the highest severity among the messages it contains; policies for that severity then apply to the summary.
  - A summary goes to the channels and targets that the held messages would have used: one summary per recipient and channel, listing the messages meant for that recipient.
  - A summary stays on the dashboard and in the notification bell until dismissed, or for 24 hours.
  - There is no default delivery by severity: calls always name their channels (D-087 stands).
  - Precedence on one delivery: Summarize, then Quiet hours, then Away, then Fallback. The summary itself is a delivery and passes through quiet hours, the away check and fallback like any other. Escalations and reminders create later deliveries that pass through the same chain.
- Alternatives: summary severity always info or set on the policy; summary channels set on the policy; a timeout on the policy; a default delivery per severity; quiet hours before summarize; summaries exempt from the other policies.

## D-107 The hub is built; on by default; sidebar entry chosen at setup; branches only
- Date: 2026-10-30. Decided by the maintainer; resolves the open status of D-075.
- Decision:
  - The hub is built as a core part of Heads Up. The non-goal "Delivering push, TTS or mobile notifications" (DESIGN section 1) and the sentence in `docs/limitations.md` are removed when the first channel ships (H3), and the README says so at release (H10).
  - All hub features are enabled by default. The option `hub_enabled` defaults to true and stays as an off switch in Settings. This replaces the earlier "off by default" statements. Existing calls (`create_banner`, `clear_banner`, `clear_all`) and watch rules behave as before because the hub acts only on messages that name hub channels or that match a policy; with no policies nothing new happens to a message.
  - The sidebar entry of the admin panel is not registered until the user enables it during the initial setup of the integration (a step in the setup flow, also changeable in Settings). Installations that already exist have no entry until the user enables it. The default is no entry.
  - All hub work happens on feature branches: `design/notification-hub` for the design and `hub/<id>` for each work package. Nothing reaches `main`, and nothing is pushed or tagged, until the maintainer confirms (rule 7, D-020).
- Consequences: DESIGN 23.2, the briefs H1, H2, H9a, H9e, H10, UX_SPEC (Settings) and the roadmap are updated. Recipient profiles should exist without manual work, so H2 creates a profile for every person automatically, with detected devices (to confirm in H2).
- Open: whether the sidebar entry can be added and removed without a restart when the option changes (H9a); the wording of the setup step.

## D-108 Generic clear is a new action `clear` (2026-10-30)
- Context: H1 needs one way to remove a message from every channel. Options: extend `clear_banner`, or add an action.
- Decision (maintainer): add `heads_up.clear`. `clear_banner` keeps working and matches only messages that have the banner channel. `clear` matches any message by `id` and/or `tag`. A message has one lifecycle: removing the record clears it on every channel through the hub engine, whichever action removed it.
- Consequence: a `notify` message without the banner channel cannot be removed by `clear_banner`; it ends by timeout, condition, `clear` or `clear_all`.
- Also decided in H1 (build detail, no maintainer question): shortcuts without an `id` keep no record (delivered once, trace only); an ended snooze emits `unsnoozed` with reason `elapsed` rather than `became_visible`; a downgrade after using `notify` needs banners cleared.

## D-109 H2 choices: presence delay, stored state, areas, automatic profiles (2026-10-31)
- Context: H2 (audiences, recipient groups, recipient profiles) needed four answers before relying on them.
- Decisions (maintainer):
  - Presence delay for Last to leave and First home: 60 seconds, configurable (option `presence_debounce_seconds`, 0 reacts at once; in the integration options).
  - The state of Last to leave and First home is stored (`.storage/heads_up.presence`) so it is right after a restart. The set of people at home is recomputed from the person states at start.
  - An area in a recipient group or call stands for the speakers and satellites assigned to it in Home Assistant (the entity's own area, else its device's), resolved when the message is delivered.
  - A recipient profile exists for every person without setup (devices found from the person's trackers). A profile subentry exists only to change that: add a device, remove a detected one, pick a primary device, limit channels.
- Build details decided in H2 without a question: the first state of a new person entity is not an arrival; unknown person states change nothing; a push goes to every device of a person (the primary device is listed first and has no other effect yet); a registration id is a valid push recipient; recipient groups are named `<name> (group)` in calls and an area is addressed by its area id; `plan()` is asynchronous because the Admins audience reads users.

## D-110 H3 choices: press attribution and push defaults (2026-10-31)
- Context: a push button press arrives as an app event whose payload the hub cannot rely on (N-72, N-79). Push defaults were still proposed.
- Decisions (maintainer):
  - A press counts for the recipient named in the button id (their person's linked user, or for a device without a person the user on the event). If the event also carries a user and it differs from the person's user, the press is ignored and traced (`user_mismatch`).
  - The proposed push defaults are confirmed: Android channel prefix `heads_up`, lock-screen text full, buttons Snooze and Dismiss, levels success and info passive, warning normal, critical time-sensitive, iOS critical off.
- Build details decided in H3 without a question: levels are stored in the option `push_levels` and `critical` as a level is the iOS opt-in (sent as time-sensitive to Android); the Android channel is `<prefix>_<level>` so a channel's importance never has to change; own button ids carry the prefix `b-` to stay apart from dismiss, snooze and ack; buttons are clipped from the end (own first, then Acknowledge, Snooze, Dismiss); the response counts of `notify` are the plan, failures show in the trace; a message waiting for its condition holds every channel; `Channel.clear` takes the message id and the stored tag because a message can be gone at startup.

## D-111 Deleted audiences and groups: report, do not block (2026-10-31)
- Context: Home Assistant offers no way to veto the deletion of a subentry (`async_remove_subentry` has no hook), so a policy can end up naming an audience or recipient group that no longer exists.
- Decision (maintainer, provisional): keep audiences, groups, profiles and policies as subentries for now. The hub provides a "used by" lookup; a policy that names a missing audience or group is reported invalid, its step is skipped and the trace says why. Nothing breaks silently.
- Deferred: moving these objects into an integration-owned store with refused deletes is a follow-up (`docs/OPEN_QUESTIONS.md`, Phase 15). The maintainer wants to try the integration first and see how often a broken reference happens.
- Policy defaults confirmed: escalation after 5 minutes; reminder every 30 minutes, at most 3; dismissing counts as acknowledging only when the policy says so.

## D-112 H4b choices: quiet hours on the local clock, defaults (2026-10-31)
- Context: quiet hours need a rule for the days the clock changes, and their defaults were proposed only.
- Decisions (maintainer):
  - A quiet hours window is on the local wall clock of the Home Assistant time zone. 22:00 to 07:00 always means those local times, so on a clock-change day the window is one hour shorter or longer. A time that does not exist or occurs twice uses its first occurrence.
  - Defaults: 22:00 to 07:00, all days, action `quiet`, critical passes.
- Build details decided in H4b without a question: `days` names the day a window starts on; only the non-banner channels are held or quieted; a reminder under `wait` is skipped, not held; several quiet hours policies apply the strictest action (`drop`, then `wait`, then `quiet`); Away holds only audience targets and only recipients whose person state is known and not `home`; Away has no exemption for critical (choose its severities); Fallback is judged after the first delivery of a message (not on updates, not for escalations, reminders or another fallback) and fires once per message; held deliveries are ledger rows in state `held` with the reason in `hold` and the release or deadline time in `due`.

## D-113 H4c choices: what a summary lists, defaults (2026-10-31)
- Context: H4c asked how a summary treats messages a recipient already acknowledged or dismissed.
- Analysis (maintainer): a message held by Summarize is not shown on the banner and not pushed, so no recipient can acknowledge or dismiss it before the summary; both recipients of one call are held together or sent together. An admin acting on a held message through the API is not normal use. A global dismissal removes the record, which is a clear.
- Decision: a summary lists every held message that still exists; a message that was cleared (removed) before the summary is listed once, marked resolved. No separate handling of acknowledged or dismissed messages.
- Defaults (maintainer): a summary every 60 minutes; critical messages are not held unless `include_critical` is set. The form also offers a time of day (default 20:00) in place of the interval.
- Build details decided in H4c without a question: the hold is decided when the message appears (a policy added later, or a message that was already delivered, is not held); a held message stays hidden on every channel after its summary, the summary stands for it; the interval counts from the first message held after the last summary; an update that changes text or severity of a summarized message lists it again in the next summary; a message whose severity becomes critical while the policy excludes critical is released at once; deleting or disabling the policy releases its held messages; a summary is one message per recipient (person, device) and channel, stays 24 hours and is not held, escalated, reminded or summarized itself.

## D-114 H5 choices: speech length, cooldown, engine (2026-10-31)
- Context: the speak channel needs a length limit for spoken text, a cooldown against repeats and a text-to-speech engine for media players.
- Decisions (maintainer): the length limit is 200 characters and configurable (option `speak_max_length`, in the integration options).
- Defaults taken without a separate answer (the maintainer answered only the first question): cooldown 60 seconds, configurable (`speak_cooldown_seconds`, 0 for none); engine from the option `speak_tts_entity`, else the only `tts` entity if exactly one exists, else the delivery fails with `no_tts_engine`; language from the option `speak_language`, else the Home Assistant language. These can be changed on the maintainer's word.
- Build details decided in H5 without a question: a satellite gets `assist_satellite.announce`; a media player with the announce feature gets `tts.speak` (which announces by itself); another player gets `media_player.play_media` with the tts media source and no `announce`; the hub never sets or restores volume; an update does not say the text again; nothing is said when a message ends; quiet hours skip speech; a speaker runs one message at a time and, for a player that does not overlay, waits up to 30 seconds until it stops playing before the next one.

## D-115 H6 choices: one module per surface, popup loader, where popups appear (2026-10-31)
- Context: the rule "one plain-JS ES module" (D-021) covered the card only. The popup must run on every dashboard, so it needs a global script that stays tiny. The brief asked how a popup knows it is on a login page and what the module layout rule is.
- Decisions (taken by the build session, technical; not a maintainer question): the layout rule becomes "one plain-JS ES module per surface, no build step, no npm runtime dependencies": the card, the popup loader, the popup module (and the panel in H9). The loader stays under 1 KB (a test measures the file) and does nothing unless `heads_up/popup_config` says popups are on; it imports the popup module when the first popup is due. The loader needs no login page check: Home Assistant renders extra modules only into the main app page, not into the login (`/auth/authorize`) or onboarding pages (N-87).
- Behaviour: a popup is a ledger row for a person with a linked user (persons only, D-091); the browser gets the messages that have such a row through `heads_up/popup_subscribe`. Dismiss and snooze clear the row (the popup goes for that user and a snooze end brings it back); an ended message clears every row. Default styles: a corner card for success, info and warning, a centered modal for critical (D-090), `popup_styles` per severity (`card`, `modal`, `off`, no form yet). A quiet popup is always a card. Closing a popup with the close button or Escape hides it on that page only and does not dismiss it; Acknowledge also hides it on the page. A button's `action` (navigation, confirmation) is not run by the popup, only its event is fired.
