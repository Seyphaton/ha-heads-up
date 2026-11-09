# Decisions

ADR-style log. Each entry: decision, alternatives, consequences. All entries dated 2026-10-24 unless stated; status accepted unless stated.

## D-001 Phase 0 repo contains documentation only
- Decision: until the design was approved, the repo held only Markdown docs and `.gitignore`.
- Alternatives: scaffold the integration immediately.
- Consequences: no source code before the Phase 0 gate.

## D-002 Structure of the human docs
- Decision:
  - Install and quickstart are numbered imperative steps; upgrading has its own section; FAQ headings are phrased as the user's question, including "How do I uninstall …?".
  - Configuration and action fields are tables (key, type, required/default, description); events are a table of `event_type` and data fields, followed by one automation example.
  - HACS install comes first; troubleshooting starts with "check the version, clear the cache, check the browser console".
- Not used: emoji headings, badge rows, promotional tone; limitations scattered across sections (we use one `docs/limitations.md`).
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
- Alternatives: TypeScript + Lit + bundler; `getConfigForm`; YAML-only; manual `/local` resource; separate HACS plugin repo; swipe.

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

## D-033 Not used
- The number was skipped and is not reused. No decision of this number exists.

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

## D-063 Rule messages render Home Assistant templates
- Date: 2026-10-26.
- Decision: a rule message is rendered as a Home Assistant template (`{{ states('...') }}`), after `{name}` is replaced. Entities the template reads are tracked, so the text updates when they change; time-based functions such as `now()` are not refreshed. An invalid template is refused by the rule form (`message_template_invalid`); a template that fails at render time shows the unrendered text and logs a warning. This changes D-055 ("no other placeholders or templates"); `create_banner` is unchanged (HA renders its data before the call, D-017).
- Alternatives: reject templates in the form; a state placeholder without Jinja.
- Reason: a maintainer rule used `{{ states(...) }}` and showed the raw text. Maintainer chose rendering.

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
  - There is no default delivery by severity: calls always name their channels (D-087 stands). Reversed in part by D-121: the policy type Deliver adds channels and targets to the first delivery.
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

## D-116 H8 choices: the acknowledgement line and button on the card (2026-10-31)
- Context: H8 shows who acknowledged a banner and lets a viewer acknowledge it, on the card.
- Decisions (maintainer): the card option is `show_acknowledged`, on by default, `false` hides the line. With several people the line names the first and counts the others: "Acknowledged by Anna", "Acknowledged by Anna and 1 other", "Acknowledged by Anna and 2 others".
- Build details decided in H8 without a question: the payload of each banner carries `acknowledged`, `acknowledged_by` (first names, in the order they acknowledged; the first word of the person's name), `acknowledged_count` (all users, also those without a person) and `can_acknowledge`; `can_acknowledge` is true when an escalation or reminder policy applies, nobody acknowledged yet and the viewer is a target; the Acknowledge button is shown whatever `show_acknowledged` says; the first is "first" by time of acknowledgement; the same fields are sent for action and rule messages; the popup's `ack` flag follows `can_acknowledge` (no button once someone acknowledged).

## D-117 H9a choices: panel layout, sidebar entry, setup step (2026-10-31)
- Context: H9a registers the admin panel and builds its shell and the Settings page.
- Decisions (maintainer): the panel is a shell plus one module per page: `heads-up-panel.js` holds the shell and the navigation, each page is a file under `frontend/panel/` loaded when it is opened. The sidebar entry has the title "Heads Up" and the icon `mdi:bell-ring-outline`. The setup flow asks "Show Heads Up in the sidebar" and the toggle starts on (this refines D-107, which has no entry for installations that already exist: they keep the option off until enabled).
- Build details decided in H9a without a question: the entry is added and removed without a restart when the option `show_panel` changes (registration is a function of the option, run at setup, on every options update and removed on unload); the panel is registered with `frontend.async_register_built_in_panel` (component `custom`) when `panel_custom` would need a manifest entry, see N-88; Settings changes are written with admin-only WebSocket commands that update the integration options, so the integration's own options form keeps working; presets create only the policies that do not exist yet and never change or delete one.

## D-118 H9b choices: recent messages and the log are memory only (2026-10-31)
- Context: the Overview shows a log of last actions and the Messages page the recent messages and the delivery trace of each.
- Decisions (maintainer): the recent messages and the delivery log are kept in memory (sizes from the History setting: 100 messages and 500 entries by default) and start empty after a restart; messages that are still active come back from their stored records. Nothing new is written to storage. The log has the kinds of the UX spec: created, escalation sent, reminder sent, acknowledged (by whom), dismissed, snoozed, unsnoozed, summary sent, delivery skipped, delivery failed, expired, cleared (and fallback sent).
- Build details decided in H9b without a question: the log and the recent messages are filled from the transitions of the manager and from the engine's own steps; the number of log entries follows the setting Trace entries kept and the number of recent messages follows Recent messages kept, and a change applies at once; an active message that was loaded from storage after a restart is listed as recent with the time it was created; states of an active message (escalating, reminding, snoozed, in a summary, acknowledged) are worked out when the page asks, from the ledger timers, the held store and the snooze times; the panel words every explanation in four languages from structured fields, the server sends no text.

## D-119 H9c choices: the panel drives the integration's own forms (2026-10-31)
- Context: H9c builds editors for audiences, recipients, policies and channel settings in the panel.
- Decision (taken by the build session, technical): the editors save through the integration's own subentry flows, driven over Home Assistant's REST API for subentry flows (`POST /api/config/config_entries/subentries/flow` with the handler `[entry id, type]`, a `subentry_id` to reconfigure, then the data), so the validation exists once and the native dialogs keep working; deleting uses `config_entries/subentries/delete`. Home Assistant cannot veto a delete (D-111), so the panel refuses a delete itself while a policy uses the object and shows who uses it; the native screen can still delete it, and the Overview reports the result. The Channels page writes the options with the admin command `heads_up/channels_set`. A new command `heads_up/panel_config` returns what the editors show. Each flow save starts a new flow with the whole data and cancels it when the flow returns errors.
- Build details: a recipient profile subentry holds only changes, so the panel saves manual devices, removed devices, the primary and the channels, and deletes the subentry when nothing differs from the detected devices; the stored data of every object is shown as YAML under its editor.

## D-120 H9d choices: the test marker, no "what if" time (2026-10-31)
- Context: Send test is the only real send of the panel (D-101); its message must be recognizable. The mockup also simulated the time of day.
- Decisions (maintainer): a test message is a normal message with the marker: the title starts with `Test: ` (a message without a title gets the title `Test`), the id starts with `hu_test_`, the tag is `test`, and it ends by itself after 10 minutes. It is otherwise a normal message, so every policy that applies to it applies. The page offers no "what if" time in this version: the preview uses the real clock and the real presence. A what-if time stays an open idea (`docs/OPEN_QUESTIONS.md`).
- Build details decided in H9d without a question: the preview runs the engine's own planning and the precedence chain on a message that is never stored or delivered, and shows what the first delivery and the fallback policies would do now; the later steps (escalation, reminder, away, summary) are listed from the policies that apply; Send test calls the `notify` action itself, so the real send is the real code path; a test message can be cleared from the page.

## D-121 Welcome with default policies replaces presets and the wizard; immediate delivery by policy (2026-11-01)
- Context: the maintainer did not accept the loudness presets (H9a) and the four-step wizard (D-093). They asked for one welcome message that explains a few defaults and lets the admin switch each on or off on the first opening.
- Decisions (maintainer):
  - The loudness presets, their Settings section and the wizard (people, devices, loudness, test; also the config flow entry) are dropped. Recipient profiles are automatic anyway (D-109). This supersedes the preset parts of D-093 and D-117.
  - A welcome dialog in the panel, on the first opening and again from a button on Settings, offers four defaults, each with a switch, all switched on: Quiet hours (22:00 to 07:00, send quietly, critical passes); Evening summary (messages tagged `digest`, one summary at 20:00, critical excluded); Critical (a critical message is also pushed at once to a chosen audience at the iOS critical level, a reminder every 10 minutes at most 3 times on push, an escalation after 10 minutes with speech on chosen speakers, dismissing counts as acknowledging); Warning reminders (every 30 minutes, at most 3 times). Create adds only the policies of the switched-on items that do not exist yet and never changes or deletes one.
  - D-106 is reversed in part: a new policy type Deliver sends matching messages to a chosen audience on chosen channels at once, in addition to what the call names. Without it a critical watch-rule message could reach phones only through an escalation.
  - The welcome appears only in the panel (the setup flow is not extended).
- Build details decided without a question: the audience of Critical defaults to the built-in Admins; with no speakers chosen the speech escalation is not created; the Critical item also sets the push level for critical to `critical` (iOS critical: needs the app's permission, plays a sound in silent mode, Android receives it as time sensitive); a Deliver policy fires once per message at its first delivery (not on updates, not for held messages, not for silent startup transitions), skips recipients that already have the message on that channel, and passes the precedence chain; the welcome is remembered in the option `welcome_seen`.

## D-122 One list of settings on the options screen and the Settings page (2026-11-01)
- Context: the integration's options screen and the panel's Settings page held different entries (banner defaults, presence delay and speech only on the options screen; limits, history and the install token only in the panel).
- Decision (maintainer): all entries on both, 100% identical.
- Build: one definition, `hub/settings.py` `SECTIONS`: Hub, Banners, Presence, Speech, Limits, History in this order, each with its entries. The options flow builds Home Assistant form sections from it and the panel builds its page from the layout that `heads_up/settings_get` returns. Labels, hints, section names and choice names are the same words on both and in four languages; `tests/card/panel.test.js` compares the panel's tables with `strings.json` and the translations, and `tests/hub/test_panel_settings.py` compares the order. The install token is shown read only: in the description at the top of the options screen and in an Identity section at the end of the panel page. Welcome and People and devices exist only in the panel because a form cannot show them.
- Details: `heads_up/settings_set` accepts every entry (snooze choices in minutes, the default timeout in seconds, 0 for none, at most 365 days, the text-to-speech engine as a `tts.` entity or empty). The options form refuses a timeout over 365 days with `timeout_too_long`. The form sends its fields nested by section; fields left out keep their stored value. Fields carry the stored value as default and as suggested value because the frontend fills the form from the suggested value and a section must not carry a default (it then stays empty).

## D-123 H10: release preparation, README framing, rate limits, Home Assistant 2026.10 (2026-11-02)
- Decisions (maintainer):
  - Version number: no tag and no merge to `main` yet. The manifest stays at 0.4.0 and the changelog keeps its Unreleased section; a version is chosen when the maintainer releases.
  - README and DESIGN section 1: the "no push delivery" non-goal is replaced by a holistic framing. Heads Up is a central hub for notifications with a short description; the banner is a core feature and the other channels sit on the same level; the text starts from the problems it solves (scattered notifications in automations and scripts, inconsistent banners, no critical popups, no escalation, no reminders), then features with the banner first, then configuration. The opt-in nature is not the focus.
  - Rate limits: 5 pushes per device per minute (the proposal said 10), 60 per minute for all devices, identical updates ignored for 30 seconds; all configurable in Settings.
- Build details decided without a question: the limits apply to pushes (per device and in total) and to reminders and released deliveries; the dedupe applies to updates on every channel except the banner; critical messages are counted but never suppressed (the proposed behaviour, accepted with "else as proposed"); a suppressed delivery leaves an earlier push in place and clearable, shows as `rate_limited` or `duplicate` in the trace and the log, and does not start a fallback.
- Restart: Home Assistant keeps the notification bell in memory only (N-90), so the engine puts back the entry of every active message that was shown there. A ledger of the wrong shape no longer stops setup.
- Home Assistant 2026.10.4 is the development version (tests, mypy, dev instance, `uv.lock`); 2026.9.4 stays the minimum tested version in CI and `hacs.json`. The code imports `probatio as vol` because only that type-checks on 2026.10 and it runs on both (N-91). This supersedes the pin of D-019 and the pytest pin of the test setup.

## D-124 Capabilities for fanning one message out to several channels (2026-11-03)
- Context: the maintainer asked which generic capabilities a message that fans out to push, speech and mail needs. Heads Up stays standalone and knows no caller (CLAUDE.md); each item below is generic.
- Decisions (maintainer), accepted as features, none approved for a phase yet:
  - Push `image` field: the Companion field names for iOS and Android are checked against current docs first (rule 4).
  - Speech accepts any Home Assistant area directly, without a speaker group.
  - A delivery-failure event: fired when a message reaches nobody or a delivery fails. Not needed for parity; for automations that react to failures.
  - A mail channel: generic (a notify service called once per recipient with a subject and a body), not specific to one mail forwarder.
  - A bell entry when a speech area has no speaker.
  - A setting "Disable buttons when the message has ended" (dismissed, acknowledged, condition no longer true). Global only, default on, which is today's behaviour. Off, a late press still fires `heads_up_banner_action`. It does not keep the button on the phone: the push is cleared when the message ends, so alarm-style buttons also need a message that does not end.
- Decisions (maintainer), declined: a per-call fallback target on `notify` (fallback policies stay the mechanism); a generic "call a service" channel; an `is_critical` flag separate from severity; a normal push volume; title presets and a default title.
- Parity (CLAUDE.md rule 9): the image, the bell entry and the button setting touch banners from actions and from watch rules; each ships for both or lists an exception in `docs/DESIGN.md` §22.

## D-125 Buttons stop acting once the message has ended (2026-11-03)
- Context: D-124. A press was accepted until the message record was removed, even after the message was dismissed, acknowledged or its condition turned false. D-124 called default on "today's behaviour"; that was wrong, on is stricter.
- Decisions (maintainer): the option `disable_ended_buttons` (Banners section of the options screen and the panel Settings page), global, default on. A message has ended for a press when the pressing user dismissed it or it was dismissed for all, when anyone acknowledged it (the first acknowledgement counts), or when its condition is not true. A snooze does not end it. One check in `BannerManager.press` for card, popup and push buttons and for both banner sources; the built-in Acknowledge, Snooze and Dismiss buttons are not affected.
- Build details decided without a question: error code `message_ended`; a press on a removed message stays `not_found` (nothing is left to check the sender against), so off does not revive a removed message. Alarm-style buttons also need a message that does not end (`timeout: 0`, not dismissible), because the push is cleared when the message ends.
- Blast radius: usual restart; existing automations that reacted to late presses stop receiving them unless the option is turned off; a stored option is added with its default.

## D-126 Speech to any area, and a bell entry when nobody can speak (2026-11-03)
- Context: D-124. A speech call could name an area only if a recipient group listed it, and a speech target with no speaker showed only in the response and trace.
- Decisions (maintainer): `to.speak.recipients` accepts any area by id or by name (case-insensitive); an unknown name fails the call with the list of valid names. A bell entry is left when an area has no speaker, when a speaker group resolves to nothing and when a named speaker entity is missing at delivery. One entry per area, group or speaker with no message text (the bell is visible to every user); a repeat replaces it; it stays until someone dismisses it.
- Build details decided without a question: no new setting; no entry on a dry run, in Test send's preview or when deliveries resume after a restart; the welcome dialog and policy forms list areas among the speakers; the entry text exists in English, German, French and Spanish; an area and a group cannot clash because a group is written `Name (group)`.
- Parity: speech from rule messages goes through the same delivery path (escalation, Deliver), so both banner sources behave alike.
- Blast radius: usual restart; the list of valid speech recipients grows to all areas; a call that named an area before only through a group now also works without one.

## D-127 Image under the message (2026-11-03)
- Context: D-124. Camera alerts need a picture; no schema, push payload, card or popup had an image.
- Decisions (maintainer): the field `image` on `create_banner`, `notify`, `push` and `popup`, shown on the push, the card, the popup and the watch rule form. It takes an `http://` or `https://` URL or a path starting with `/` (not `//`), at most 2048 characters, no whitespace; nothing is fetched or checked. The push sends it as `data.image` (both platforms read it, N-93); camera proxy paths work on Android only. A push leaves the image out when the lock screen setting is `title_only` or `generic` (trace reason `image_hidden`).
- Build details decided without a question: no card option (the card always shows it, except in the compact layout); `/api/` and `/media/` paths are signed with `auth/sign_path` for the card and popup, `/local/` and external URLs are used as written; a picture that fails to load is removed; the duplicate check of D-123 includes the image, so an update that changes only the picture is sent; speech takes no image; the Test send page has no image field.
- Parity (rule 9): actions and rules both carry the image (rule form field `image`, `rule_banner` payload), so no exception in DESIGN section 22.
- Blast radius: usual restart; a stored banner without the field loads unchanged; the card and popup request a picture from the given URL (a third-party URL sees the viewer's address).

## D-128 Delivery-failed event (2026-11-03)
- Context: D-124. A script could not react to a message that reached nobody; only the ledger, the trace and the action response showed it.
- Decisions (maintainer): the event `heads_up_delivery_failed`, one per message, channel and delivery step (not per recipient), after every delivery step with `origin` (`message`, `escalation`, `reminder`, `fallback`, `deliver`), so a failing escalation or fallback is visible too. It fires for send failures, for nobody to deliver to (no recipients, no usable device, unknown audience, empty group...) and for `rate_limited`. Duplicates, quiet hours, holds and the speech cooldown are choices and do not fire it.
- Build details decided without a question: payload `id`, `tag`, `channel`, `origin`, `reached`, `failed` (a list of `{recipient, reason, person?}`); the banner channel never fires it; not on a dry run and not on the first delivery after a restart (the same rule as the speech bell entry); a partial failure (one of two devices) fires with `reached: 1`. Escalation, fallback and deliver deliveries use `resume` to skip rows already sent, so D-126's "no bell entry on resume" was narrowed to `resume` with origin `message`; before, an escalation to an empty speaker group left no bell entry.
- Parity: rule messages use the same delivery path, so both banner sources fire it.
- Blast radius: usual restart; a new event, no change to existing events; automations triggering on it see a failure per channel and step.

## D-129 Mail channel (2026-11-03)
- Context: D-124. Heads Up had no way to reach a person through a notify service such as SMTP.
- Decisions (maintainer): a sixth channel `mail`. It calls one notify service, chosen on the Channels page, once per recipient with `title` (subject), `message` (body) and `target: [address]`. A person's address is a field of their recipient profile; the channel is off for everyone until the person's profile has Mail on. A separate Global address (a setting) can be named as the recipient `Global address`; it is never a stand-in for a person without an address: a person with Mail on and no address fails with `no_mail_address`, which is logged (once an hour per person) and fires the delivery-failed event. Subject and body are templates, defaults `{severity}: {title}` and `{message}`; the hint texts list the placeholders.
- Build details decided without a question: placeholders `severity` (a word in the Home Assistant language), `title` (the message when there is no title), `message`, `person` (empty for the Global address), `id`, `tag`, anything else refused on save; limits 200 characters for the subject, 2000 for the body and 254 for an address; the settings are options `mail_service`, `mail_global_address`, `mail_subject`, `mail_body` on the Channels page and in the profile form, not in the unified Settings list (like the other channel settings); no shortcut action; an update does not send again and nothing is taken back; quiet hours do not change mail and images and buttons are not sent; `mail` can be added by escalation, fallback, deliver and reminder policies; the channel name in calls is `mail` and the shared recipient is written `Global address`; the notify service must exist when it is saved.
- Parity: rule messages reach mail through policies, the same delivery path as action messages.
- Blast radius: usual restart; no existing audience or policy sends mail because Mail is opt-in per person; a new option set with defaults; a call with `mail` needs `to.mail`.

## D-130 First pre-release: 1.0.0-alpha.1 (2026-11-03)
- Context: the notification hub (H0 to H10) and the D-124 features are finished on `hub/h9e-wizard` and need a test on a production machine without a stable release.
- Decision (maintainer): the manifest version and the changelog heading are `1.0.0-alpha.1`. The tag, the GitHub pre-release and any merge to `main` stay the maintainer's steps (D-020). The `[Unreleased]` section of `CHANGELOG.md` is empty again above it.

## D-131 Panel polish: channel name, banner audience, welcome tour (2026-11-03)
- Context: maintainer feedback after trying the alpha in the panel. The channel label "Bell" was unclear; Test send's Recipients option could not be chosen; a banner with the audience Admins went to everyone and listed a guest; the welcome showed only the default policies; the built-in audiences needed explaining.
- Decisions (maintainer): the persistent channel is shown as "Persistent HASS Notification" in all panel texts (channel id `persistent` unchanged). `to.banner.audience` is resolved to persons when the banner is created and stored as `people` (Everyone limits nothing; an audience that is empty then gives a banner nobody sees). The welcome is a four-step tour (introduction, channels, recipients, policies); only the last step creates policies. The Audiences page gets a "?" explanation per built-in audience.
- Build details decided without a question: `Admins` no longer reports a person without a Home Assistant user as skipped (`no_user`), because that person is not an administrator; popup and push still report `no_user` for a named person. The audience is a snapshot for the banner because `people` is the card's own targeting (D-008). An empty audience is stored as the nonexistent person `person.heads_up_nobody`. The tour is resumable: leaving for a page shows a bar with Continue and End. Test send keeps the chosen Audience or Recipients mode per channel while no recipient is ticked, and its rows show the banner's people and the device of each push.
- Parity (rule 9): watch rules stay banner-only without targets (D-100), so the banner audience adds no exception.
- Blast radius: usual restart; a banner call that named an audience before now limits the banner; a stored banner is unchanged. The panel's channel label changes in four languages.

## D-132 Integration page: order of the Add buttons (2026-11-03)
- Context: maintainer asked to organise the entries on the integration page (Settings > Devices & services > Heads Up) with subtitles. Home Assistant lists the entries of an integration as one flat list in creation order (`config_entries/subentries/list` returns them unsorted) and the page has no group headers; an integration cannot add them. Each row already shows its type under the name (`entry_type`, four languages).
- Decision (maintainer): the recommended small change. Title prefixes were not used: the title is the object's name, which calls and policies refer to, so a prefix would break references. The Add buttons follow the panel's order: audience, recipient group, recipient profile, policy, watch rule (before: watch rule first).
- Not done (maintainer's option): re-sorting stored entries by type at startup. It rewrites stored entries and relies on Home Assistant internals. The grouped place for entries is the panel's Configuration pages.
- Blast radius: usual restart; only the order of the buttons changes.

## D-133 Pre-release 1.0.0-alpha.2 (2026-11-03)
- Context: D-131 and D-132 are finished on `hub/h9e-wizard`; the maintainer wants them in a second pre-release.
- Decision (maintainer, explicit): commit and push the branch, tag `v1.0.0-alpha.2`, publish a GitHub pre-release that is not marked as the latest release. No merge to `main`.
- Blast radius: the manifest version is `1.0.0-alpha.2`; the pre-release is not offered as the default download.

## D-134 Watch rules page in the panel (2026-11-04)
- Context: the Watch rules tab showed "This page is not available"; rules could only be edited on the integration page. The maintainer chose to build the page.
- Decisions (maintainer): a list with the state of each rule (showing now, not showing, off), severity, what it watches and its message, plus add, edit and delete. It saves through the integration's own rule flow over the REST API, like the other editors (D-119), so validation and error texts are the flow's and a change shows on both screens.
- Build details decided without a question: the form covers condition (entity or template, operator, value, attribute, hold time), message, title, severity, icon, image, people, dismissible, dismiss scope, snooze, snooze scope and choices, enabled. Buttons and the tap action are not editable in the panel (they need YAML); an edit passes the stored values through unchanged and a link opens the full form. `heads_up/panel_config` gains `rules` (name, subentry_id, stored data, showing). The error texts in the page are copied from the rule form's four translations. The page works with the hub off.
- Parity (rule 9): not a new banner feature; rule and action banners keep the features of D-073 and D-100.
- Blast radius: usual restart; admin panel only; no change to how rules evaluate.

## D-135 Overview: shortcut cards, hideable warnings, push-off persons (2026-11-04)
- Context: maintainer feedback on the Overview. "Show list" on Watch rules duplicated the Watch rules page; Active notifications was unexplained; a person with push switched off was reported as having no usable device; the critical-escalation warning could not be silenced; the maintainer asked whether Needs attention shows failed deliveries.
- Decisions (maintainer): the Watch rules tile becomes a small shortcut card that opens the page; Channels, Audiences and Policies get the same cards; Active notifications gets a line saying that some messages wait for an acknowledgement and others return or escalate; warnings of Needs attention can be hidden and shown again.
- Build details decided without a question: only warnings (`level` warning) are hideable, because an error means something is broken. A hidden warning is remembered as `kind|subject|detail` in the option `attention_dismissed` (at most 200 keys, kept across restarts, not an option form field), through the admin commands `heads_up/attention_dismiss` and `heads_up/attention_restore`. Persons whose profile channels lack `push` are skipped by the device and no-device checks. The Channels card shows the number of channels (6) and whether mail is set up; Audiences counts built-in plus own; Policies and Watch rules count enabled ones.
- Not done: Needs attention does not list delivery failures; they are in Last actions and in the event `heads_up_delivery_failed` (D-128). Whether to add a "recent failures" item is left open.
- Blast radius: usual restart; admin panel only; one new key in the entry options.

## D-136 Audiences: switch off built-ins, limit presence audiences; failed sends; speech log (2026-11-04)
- Context: maintainer feedback. The built-in audiences showed their name twice; they could not be switched off; a presence audience could not be limited to some persons; a speech test failed with nothing in the Home Assistant log; Needs attention did not show failed deliveries (D-135 left it open).
- Decisions (maintainer): built-in audiences get a checkbox. A custom presence audience can be limited to chosen persons. Needs attention gets a warning for failed sends.
- Build details decided without a question: a switched-off built-in audience (option `audiences_disabled`, names) is not offered by `names()`, resolves to nothing and fails a call with `unknown_audience`; it cannot be switched off while a policy uses it (`heads_up/audience_enable`, error `in_use`). The limit is the field `limit` (persons) of a presence audience, empty meaning everyone; for Last to leave and First home it intersects the house-wide result instead of finding the last of the chosen persons (a per-group tracker is not built). The failed-send warning counts `failed` entries of the in-memory log of the last 24 hours per channel and reason, is hideable like other warnings and links to Messages. Speech now logs a warning for a missing engine (naming the engines found), a missing engine from the media source and a missing speaker; skips stay at debug. Test send reads the real results from the trace after the send and shows them with the reason, because the call's response only counts what was planned.
- Not known: why the maintainer's speech test failed. On the dev instance Test send to a stub player with and without announce gives `sent`; the likely causes on a real setup are several `tts` entities with no engine chosen, quiet hours (the test ran at night) or a speaker that cannot fetch the media URL, which Home Assistant does not report. The new logging and the result table show the first two.
- Blast radius: usual restart; one new key in the entry options; a call naming a switched-off built-in audience fails.

## D-137 Help group with three pages (2026-11-04)
- Context: the maintainer asked for three pills on the FAQ page: FAQ, example calls and card examples, or names that are easy to grasp.
- Decisions (maintainer): the group splits into FAQ, "Notify examples" (the calls of `heads_up.notify` and its shortcuts) and "Card examples" (configurations of `custom:heads-up-card`). The group is called Help; the addresses are `/heads-up/faq`, `/heads-up/examples` and `/heads-up/card`.
- Build details decided without a question: one module renders the three pages by the page id the shell passes (`ctx.page`). Six card examples: default, compact list, only critical and warning, one room by tag, a wall tablet for the administrator, own colours. `make docs-check` checks each card example's options against `CONFIG_KEYS`; values are not checked.
- Blast radius: usual restart; the old address `/heads-up/faq` still opens the FAQ.

## D-138 Panel wording, FAQ order, activity chart, Test send behaviour (2026-11-04)
- Context: maintainer feedback after D-137. New users do not ask what an existing user would; the channel name was long; Test send could not set dismissal or show acknowledgement; the Overview had no sense of recent activity.
- Decisions (maintainer): the FAQ opens with a new user's questions (what Heads Up does, how it differs from Home Assistant's own functions, setup, test, channels, audiences, policies, severity, tags, Android and iPhone, escalations and reminders, how policies are applied, dismissing for everyone) and ends with detailed ones. The page "Messages" is called "Message Log". The channel is called "Persistent Notification" everywhere (this replaces the name in D-131; the channel id `persistent` is unchanged). The Watch rules page and its FAQ answer explain that rules live in Heads Up, remove the banner when the condition ends, and that an automation with a condition does the same. The Overview's active card gets a chart of the last 24 hours.
- Build details decided without a question: the chart counts messages created per rolling hour (24 bars), stacked by severity, from the in-memory log (the newest 5000 creations), so it starts empty after a restart. The bars grow in once when the page opens. Test send gets a Behaviour section (dismissible, dismiss scope, snoozable). Acknowledging is not a field of `notify`: the preview lists the escalation and reminder policies that apply, or says that none does and how to add one.
- Blast radius: usual restart; the panel's WebSocket commands `hub_plan` and `hub_test_send` accept four more optional fields; `panel_overview` returns `activity`.

## D-139 The hub is always on (2026-11-04)
- Context: the hub switch (`hub_enabled`, D-107) was an off switch for a feature that is on by default. The maintainer asked to remove it and to say, next to the sidebar switch, what is not possible without the panel.
- Decisions (maintainer): the option, its form entry, its panel entry, its welcome and page hints and its Needs attention warning are removed. Only the sidebar switch (`show_panel`) stays, in a section called Sidebar panel, with a text that lists what needs the panel: Test send, the Message Log, the Overview, the welcome with the default policies, the Channels settings and the Help pages. Audiences, recipients, policies, watch rules and the other settings stay under Devices & services.
- Build details decided without a question: the engine starts with the entry and is never stopped by an option; a stored `hub_enabled` is ignored and not removed. `notify` no longer has a banner-only fallback. The guards for a missing engine stay (for the moment before the engine exists) and answer `hub_off`, now worded "The notification hub is not running". The settings section `hub` is renamed `sidebar` in the options form, the panel and the translations. This supersedes the off switch in D-107.
- Blast radius: usual restart; an installation that had the hub switched off now runs the hub.

## D-140 Introduction, readable long texts, mail FAQ (2026-11-04)
- Context: maintainer feedback after D-139. "Show the welcome" was an odd button label; long explanations were one block of text; nothing explained why mail does not work out of the box.
- Decisions (maintainer): the button is "Restart introduction" and the screen is called the introduction in the panel and the docs (the screens keep their code names). Long explanations get paragraphs and bullet lists. The FAQ gets a question on mail (SMTP): it needs the SMTP integration with its notify service chosen on the Channels page, and each person switched on under Recipients.
- Build details decided without a question: long texts are plain strings with a blank line between paragraphs and "- " for bullets, rendered by `richNode` in `panel/ui.js` without HTML; Home Assistant's own forms show the same strings as Markdown, so the settings wording test still compares equal strings. Applied to the FAQ answers, the Watch rules text, hints that contain a line break (the sidebar text) and the first setup screen. The mail answer is backed by the SMTP source in 2026.10.4 (HA_API_NOTES 95): a config flow, a legacy `notify.<entry title>` service, and a repair that announces its removal in 2027.3.
- Blast radius: usual restart; wording only.

## D-141 The banner settings are message settings (2026-11-04)
- Context: the Settings page listed Maximum number, Evict, Default dismiss scope, Default timeout, snooze settings and Disable message buttons under "Banners". The maintainer asked whether they apply only to banners.
- Decision: they do not. The manager applies them to the message that every `notify` call creates, whatever its channels (`manager.create`, `press`), and the push buttons and the popup buttons call the same code. The section is called Messages and the labels and hints name the channels. The option keys (`max_banners`, `evict` and so on) are unchanged.
- Verified by tests (`tests/hub/test_message_defaults.py`, `test_push_actions.py`): the defaults apply to a message without the banner channel; messages without the banner channel count toward the maximum (this closes the open question about `max_banners`); an own button of an ended message is refused on the phone as on the banner. Watch rule messages do not count toward the maximum (D-052). Push and popup use the first snooze choice; the banner card offers all.
- Blast radius: wording only; usual restart.

## D-142 Snooze time of push and popup is its own setting (2026-11-04)
- Context: the snooze choices were one list, but only the banner card offers a menu. The push and the popup have one Snooze button and used the first choice. The maintainer asked for dedicated settings for the banner and for the push.
- Decision (maintainer): the list stays the banner's choices (`default_snooze_options`, and `snooze_options` per call) and a new option `quick_snooze_minutes` (15, range 1 to 1440, in the Messages section) is the one snooze time of the push and popup buttons. This replaces "the first snooze option of the message" (D-092).
- Build details decided without a question: the popup shares the push's time, because it has one button too. `manager.snooze` accepts a time that is one of the message's choices or the quick snooze time. A call's `snooze_options` no longer changes what the push or popup button does. The popup message payload carries `snooze_seconds`.
- Blast radius: usual restart; a push or popup snooze that used a call's first choice now uses the setting.

## D-143 The message cap sits with the limits (2026-11-04)
- Context: the maximum number and Evict were listed with the banner defaults, but they count every stored message and bound state, not the dashboard. The push rate limits bound deliveries. The maintainer asked for them to be one group.
- Decision (maintainer): Maximum number of stored messages and Evict move to the Limits section, in front of the rate limits. The hints say what each guard protects. The option keys `max_banners` and `evict` are unchanged. The dashboard needs no new option: the card has `max_items` and `collapsed_items`.
- Verified by `tests/hub/test_limits_interplay.py`: the cap is applied when a message is created and evicts the oldest lowest-severity message on any channel; the rate limits apply to each push; evicting takes pushes back without a rate check; an update never counts toward the cap but counts toward the push rate; the two do not know each other. Critical messages are never evicted and never rate limited, but a cap full of critical messages fails new calls.
- Blast radius: wording and place only; usual restart.

## D-144 Message settings in clusters (2026-11-04)
- Context: eight settings under one Messages heading did not show which belong together or which channel they act on. The default snooze scope looked like a banner setting.
- Decision (maintainer): clusters Dismiss settings; Snooze settings; and under snooze, Banners and Push & Popup. The cards carry a one-line description naming the channels, and the hint of the snooze scope names them too.
- Build details decided without a question: the section keys are `dismiss`, `snooze`, `snooze_banner` and `snooze_push` (the key `banners` is gone; the option keys are unchanged). The default timeout and the ended-buttons switch are in Dismiss settings because they decide when a message ends or stops reacting. A section name is a path with " › "; the panel shows its first part as a heading over the cards that share it, the options screen of Home Assistant has no nesting and shows the whole path as the section name. Sections have a `description` in `strings.json` and the panel keeps the same text (tested).
- Blast radius: usual restart; the options form has four sections where it had one.
- Follow-up (maintainer): the cards below Messages looked like part of it. Every block now has its own heading (a card without a path has no second title); only the Messages cards, which share a heading, have smaller titles.

## D-145 Policies page: decisions taken before the design (2026-11-04)
- Context: the maintainer asked for a clearer Policies page: Enabled at the top, a text per type, a choice between manual and automatic attachment, and a choice between chosen and message-taken channels and targets. Analysis in `.private/policies-page-adjustments.md` (not tracked).
- Decisions (maintainer): the Watch rules form and page get a Policy field, the same choices as Test send, so rules and calls keep parity. The integration's own policy form stays one step; the text under Type is one fixed text, the panel shows the text of the chosen type. How conflicting policies and the Away policy interact needs a dedicated design session; it is not decided here.
- Not decided: how a manual policy combines with the automatic ones on one message (add to them, or replace them as a named policy does today). Settled in D-151: it replaces them.

## D-146 Policy form in two tabs, manual and automatic policies (2026-11-04)
- Context: the maintainer asked to start the policy form changes at once: a clear split between what a policy does and when it applies, with manual versus automatic chosen by the user, and a design session on conflicting policies in parallel.
- Decisions (maintainer): the editor has Enabled at the top, then the name, the type with a short text for the chosen type, and two tabs: What it does and When it applies. Manual versus automatic is a choice under When it applies. The Watch rules form gets a Policy field (D-145).
- Build details decided without a question: the field `apply` is `auto` (default, as before) or `manual`. A manual policy has no severities or tags, never attaches by itself, is not compared by the duplicate check and does not count as the escalation that covers critical messages in Needs attention. A call or a rule that names a policy uses only that policy, as before; a named manual policy replaces the automatic ones (settled in D-151). The sentence and the status stay above the tabs; a tab with a problem gets a dot. The integration's form stays one step: Enabled first, an Applies choice, a fixed text under the step. A rule's `policy` is a name or `none` and the flow refuses an unknown name (`policy_unknown`).
- Challenge to the form (accepted): two tabs hide half of the form, so the sentence and the problems are pinned above them and a tab with a problem is marked. Stacked cards would show both halves at once; tabs were kept as asked.
- Not built: channels or targets taken from the message, and the Away interplay (design session).
- Blast radius: usual restart; existing policies stay automatic; a stored policy gets `apply` when it is next saved.


## D-147 Disable a recipient fully (2026-11-04)
- Context: a profile could only limit the channels a person accepts, and the form refused an empty list, so there was no way to switch a person off completely.
- Decision (maintainer): a recipient profile has `enabled` (default on). Off, the person gets nothing on any channel. Maintainer answers: banners without a target stay visible on the person's dashboard (the card is not filtered by it); the switch applies to audiences, to a call that names the person and to critical messages alike.
- Build details decided without a question: the profile subentry stores `enabled: false` only when off. A disabled person is removed from every audience in `Resolver.members` (a skip with the reason `recipient_disabled`, so the audience previews, `banner_people` and the "Right now" line leave them out) and skipped in `_expand_person` for named recipients. A banner whose `to.banner.recipients` are all disabled gets `people == [BANNER_NOBODY]`, not an empty list, which would mean everyone. `recipient_disabled` is a choice like quiet hours: it is not in `NOBODY_REASONS`, so it fires no `heads_up_delivery_failed` and no failed-send warning. Needs attention does not flag a disabled person for a missing device. Presence audiences (Last to leave, First home) are still computed over all persons; a disabled last person leaves the audience empty. Devices, channels and address stay stored. Mail to the Global address is not a person and is not affected.
- Alternatives: hide all banners from the person too (needs a card filter and a decision for administrators); let critical messages through (not fully off).
- Blast radius: usual restart; existing profiles stay enabled; the profile form gets one more field.

## D-148 Policy interaction is a choice of the user, with an ordered list (2026-11-04)
- Context: round 2 of the policy design session. The maintainer wants the simplest possible rules, chosen by the user.
- Decisions (maintainer): how policies interact is a setting with two values, picked at the top of the Policies page and in the introduction. (1) Every policy that applies runs; where two disagree, the order of the policy list decides. (2) Only the first policy that applies runs; the order of the list decides, and a policy chosen by hand on a message overrides the rule-based ones. The order is set by drag and drop. Whether more simple behaviours should be offered is a separate task, not part of this session.
- Challenge recorded: with today's single-purpose policies, value (2) lets a critical message get only one of quiet hours, an escalation or a reminder, and the four default policies of the introduction no longer work together. The maintainer keeps (2) as a deliberate choice for users who want it simple.
- Build details not yet decided: the default value, the starting order of existing policies, what the introduction offers under (2), and the exact meaning of "disagree" under (1). Drag and drop needs a keyboard and touch fallback (Move up and Move down).
- Nothing is built for this decision.

## D-149 Policy design session, round 3 (2026-11-04)
- Context: answers to the defaults, the starting order and the introduction (D-148).
- Decisions (maintainer): the default setting, for existing and new installations, is "only the first policy that applies runs". "All that apply run" is not designed yet: how it works with overlapping policies needs separate design decisions, and the order-overrides rule of round 2 is not adopted for it. For the later design, the maintainer proposes a switch on each policy that creates new notifications (escalation, fallback, deliver): whether the policies that hold messages back (quiet hours, away, summaries) apply to its notifications. The introduction asks the setting first and, for "only the first runs", proposes an ordered list of simple, non-overlapping policies: 1) Critical delivery, 2) Critical reminder, 3) Warning reminder, 4) Quiet hours.
- Challenge recorded, not yet answered: under "only the first runs" the list as proposed does overlap. Critical delivery and Critical reminder both match critical messages, so the reminder never runs; a critical message gets one behaviour only. A set without overlap is Critical delivery (critical), Warning reminder (warning) and Quiet hours (the rest, which are info and success). Waiting for the maintainer to choose the exact list.
- Not built, not started: the setting, the ordered list with drag and drop, the introduction step. It needs the maintainer's approval as a phase of its own.

## D-150 Introduction list for "only the first policy runs" (2026-11-04)
- Context: the open question of D-149.
- Decision (maintainer): one critical policy only, and a fourth policy, a summary for info and success. The introduction offers, in this order: 1) Critical delivery (critical messages: push at once to the chosen audience), 2) Warning reminder (a warning nobody acknowledges is repeated every 30 minutes, at most 3 times), 3) Evening summary (a Summarize policy for the severities info and success with the tag digest: held and sent as one summary at 20:00), 4) Quiet hours (the rest, which is info and success without the tag digest: sent quietly from 22:00 to 07:00). Critical reminder and the critical escalation are not part of this list.
- No overlap in effect: critical goes to 1, warning to 2, info and success with the tag digest to 3, info and success without it to 4. By their lists, policy 4 still matches digest messages; only the order (first wins) keeps it from running for them. A tag cannot be excluded in a policy, so the order is what separates 3 and 4.
- Consequence: under this setting a critical message gets its delivery and no reminder; a digest message gets the summary and no quiet hours (it is held anyway).
- Not built. The build (setting, ordered list with drag and drop, engine, introduction step) waits for the maintainer's approval as a phase.

## D-151 Policy framework design session, first answers (2026-11-04)
- Context: the design session on conflicting policies started with four questions (`.private/policy-framework-design-session.md`, not tracked).
- Decisions (maintainer): a call or watch rule that names a policy replaces the automatic policies, as today. Which of several matching policies applies cannot be settled when a policy is saved, because audiences, presence and time change; conflicts are therefore resolved by rules at delivery time and made visible, not refused when saving. The framework must stay simple for users: no vocabulary of filters and generators in the editor or the docs, and no per-policy switches for conflicts.
- Open: the simple rules themselves (what wins when two policies disagree about timing, how a policy's own targets meet Away, how conflicts are shown). Proposals in the next round of the session.
- Nothing is built for this decision.

## D-152 Build of the interaction setting, the ordered list and the introduction (2026-11-04)
- Context: the maintainer approved the build of D-148 to D-150.
- Built: the options `policy_mode` (`first`, the default, or `all`) and `policy_order` (subentry ids). In `first` the policy book returns only the first enabled automatic policy that applies, in list order; a named policy still runs alone. In `all` it returns every one, as before, and the order does not matter. The order is stored once at setup for an installation that has none: Summarize, Quiet hours, Away, Escalation, Reminder, Fallback, Deliver, each type by name (D-149's migration order); new policies go to the bottom. The admin commands `heads_up/policy_mode_set` and `heads_up/policy_order_set` (every policy exactly once) store them; `panel_config` returns the mode and the policies in order.
- The Policies page has the setting at the top and the ordered list (position, drag handle, Move up and Move down, a drop zone at the end). The editor lists overlapping policies as a note and never blocks. The introduction asks the setting first. Under `first` it offers, in order, Critical delivery (critical), Warning reminders (warning), Evening summary (info and success with the tag digest) and Night quiet (info and success); the other mode keeps the four items as before. The choice is stored with the items.
- Not built: how "every policy that applies runs" resolves overlaps (the switch on policies that create notifications is recorded in D-149), and other simple interaction behaviours (OPEN_QUESTIONS).
- Existing tests that stack policies run with `policy_mode` `all` (the hub test fixture); `tests/hub/test_policy_mode.py` and `test_welcome_modes.py` cover the default.
- Blast radius: usual restart; with the default, an installation that stacks policies on one message now runs only the first. The household fallback under Away still needs the order or recipients; it is part of the design for `all`.

## D-153 Policy form with headed blocks instead of tabs (2026-11-04)
- Context: the maintainer asked to drop the two tabs of D-146 and to structure the form with subheadings, "Applicability" and "Impact", names open for review.
- Decision (maintainer): the editor shows both blocks one under the other, applicability first. The headings are "Which messages" and "What it does": plain questions a user asks, instead of the abstract Applicability and Impact; "What it does" also matches the text under Type. The tab markers and the code for them are removed; the sentence and the problems stay at the top.
- The integration's own form is unchanged (one step, fixed text).
- Blast radius: panel only; usual restart.
- Follow-up (maintainer): the line "In words" with the problems moved from the top to under the Save button, above the stored YAML.

## D-154 Pre-release 1.0.0-alpha.5 (2026-11-04)
- Context: the policy work (D-145 to D-153) and the settings, FAQ and panel changes since 1.0.0-alpha.2 are finished on `hub/h9e-wizard`. The tags `v1.0.0-alpha.3` and `v1.0.0-alpha.4` were set on earlier commits without a version commit, so the manifest still said `1.0.0-alpha.2`.
- Decision (maintainer, explicit): commit and push the branch and tag `v1.0.0-alpha.5`. The manifest version and the changelog heading are set to `1.0.0-alpha.5` in a commit of their own, so the release reports its version inside Home Assistant. The GitHub pre-release, not marked as the latest release, is created by the maintainer. No merge to `main`.
- Blast radius: the manifest version is `1.0.0-alpha.5`; the pre-release is not offered as the default download.

## D-155 Push level critical is an alarm on iOS and Android (2026-11-04)
- Context: the level critical was the iOS critical alert only; Android got time sensitive. The maintainer asked to review the non-parity and to fix it (`.private/push-parity-review.md`, not tracked).
- Decision (maintainer): fix all of it. The level critical is an alarm on both platforms. On Android it sends `channel: alarm_stream` (the documented channel that plays from the alarm stream, so it sounds in vibrate and silent mode), `priority: high`, `ttl: 0` and `importance: max`. The levels time-sensitive and critical on Android also send `priority: high` and `ttl: 0`, so an idle phone shows them at once. When there are more buttons than the platform shows, Acknowledge and Dismiss are kept first, then the message's own buttons in order, and Snooze goes first; the order of display stays. The panel, the introduction, the FAQ and the docs say "alarm" for both platforms and name the iOS permission and the Android Do Not Disturb setting.
- Choice made without an answer: the maintainer did not choose between `alarm_stream` and a channel of our own (`heads_up_critical`). `alarm_stream` is the documented one and is a single constant in `push.py` (`ANDROID_ALARM_CHANNEL`). Whether the user can switch on Do Not Disturb override for it in the Android settings is not verified.
- Default unchanged: the push level of critical is still `time-sensitive` until it is switched to critical (the introduction's Critical delivery does that); the iOS alert and the Android alarm both need that switch.
- Not verified: everything on a real phone; the tests check the payload (`tests/hub/test_push_payload.py`).
- Blast radius: usual restart; an Android phone that receives a critical push with the level critical now sounds in silent mode. Existing iOS payloads are unchanged.

## D-156 Dismiss, snooze and unsnooze check the target (2026-11-05)
- Context: the pre-release review (E-001) showed that `dismiss`, `snooze`, `unsnooze` and `dismiss_many` did not check `people`, while `press` and `acknowledge` did. A user not addressed by a banner could remove it (dismiss scope global) or hide it for everyone (snooze scope global) by id. This replaces the "any user can snooze" line of D-029.
- Decision (maintainer): one check, `BannerManager._require_target`, first in `_dismiss_one`, `snooze` and `unsnooze`. A non-target gets the distinct error `not_targeted` (not `not_found`, unlike `press` and `acknowledge`: the maintainer chose the clearer code over hiding that the id exists). `dismiss_many` skips such banners and counts them in `skipped`. Admins have no override; they clear stored banners with `admin_clear`.
- Applies to stored and rule banners, user and global scope. A banner without `people` stays open to everyone.
- Tests: `tests/test_authorization.py`. No new strings.
- Blast radius: usual restart; an admin who views another person's banner with `show_all` can no longer dismiss or snooze it from the card.

## D-157 Policies page marks a policy that never runs by itself (2026-11-05)
- Context: review finding E-003. In the mode `first` only the first enabled automatic policy that matches runs. The introduction's "Critical delivery" (severity `critical`, any tag) is first, and a policy added later goes to the bottom, so a Water escalation for `critical` and `water` never runs. The editor note of D-149 shows overlaps only while editing.
- Decision (maintainer): option (a). The Policies list marks a row "Never runs by itself: {name} is above it and matches all the same messages" when an earlier enabled automatic policy covers every message of the row (empty list = any; `shadowedBy` in `panel/policies.js`). Only full coverage is marked; partial overlaps stay in the editor note. Shown in the mode `first` only. The how-to, the examples and `docs/policies.md` say to drag a narrower policy above "Critical delivery"; the examples also say that Water escalation and Water reminder need the mode "Every policy that applies runs", because both match the same messages.
- Not chosen: a "Place at top" field in the create form, an Overview warning, a different default mode or introduction order.
- No backend change, no API change; the text is in the panel's four languages.
- Blast radius: panel only; usual restart (the panel URL carries a hash). Not checked in the browser pane.

## D-158 One clear action, `clear_notifications`; the released ones are deprecated (2026-11-05)
- Context: review finding E-005. `clear_all` removed every stored message, including those without the banner channel, while its text and the docs said banners only. The maintainer asked for one function that clears all channels or selected ones, by id, tag, severity or audience/recipient, instead of choosing between the two readings.
- Decision (maintainer): a single action `heads_up.clear_notifications` with `id`, `tag`, `severity` (list), `channels` (list) and `all`. Filters combine with AND; a message matches `channels` when its call named one of them. At least one filter or `all: true` alone is required, so an empty template cannot clear everything. A match is removed completely, on every channel, and rule banners are never removed. The reason in `heads_up_banner_cleared` is `action`.
- Deprecation rule (maintainer): every action in the released 0.4.0 (`create_banner`, `clear_banner`, `clear_all`) is deprecated, not removed, with one log warning per Home Assistant start, and marked in the docs and in the UI texts; an action that exists only on the development branch is deleted. `clear_banner` and `clear_all` are deprecated now and keep their behaviour; `clear_all` keeps clearing every stored message. `heads_up.clear` (H1, D-108) existed only in the 1.0.0 pre-releases and is deleted. `create_banner` is not deprecated by this decision.
- Scope kept for later (`docs/OPEN_QUESTIONS.md`): taking a message back from chosen channels only, and clearing for chosen audiences or recipients. Both change what a stored message means and need engine work.
- Tests: `tests/test_clear.py`. Strings: four languages, hassfest green.
- Blast radius: usual restart; an automation that called `heads_up.clear` (pre-release only) fails with an unknown action until it is renamed.

## D-159 Action texts say "message" (2026-11-05)
- Context: review findings E-006, D-011, R-021. The setup dialog named `create_banner`; the fields of `notify`, `push`, `popup` and `speak` said "Banner text" and "The banner disappears"; `image` said "An https:// URL" while `http://` is accepted; the `notify` channel list missed `mail`; snoozable said "Ignored (error)".
- Decision (maintainer): "message" for the thing an action sends, "banner" only for the card and for `create_banner`, the banner-only shortcut, and for card effects such as the close button. Done in `strings.json`, the four translations (key sets compared by `tests/test_translations.py`) and `docs/actions.md`, which gets a one-line definition. The setup dialog names `heads_up.notify`. The watch rule form's image text is corrected too.
- Not changed: the sensor name "Active banners", the event names `heads_up_banner_*`, error texts such as "holds N banners", the `clear_banner` name (R-016 terminology rename stays on the post-1.0 list).
- Blast radius: texts only; no restart needed beyond reloading the translations.

## D-160 Release and status documents brought up to date (2026-11-05)
- Context: review findings D-001 to D-005. DESIGN section 0, parts of section 23, `RELEASE.md`, `CLAUDE.md`, `STATE.md`, `ROADMAP.md` and the changelog described a state from before the pre-releases.
- Decision (maintainer): the documents state the real position: hub built on `hub/h9e-wizard`, pre-releases alpha.2 to alpha.5 tagged and pushed, `main` at 0.4.0 with nothing the branch lacks, 1.0.0 not released. `RELEASE.md` has a "Releasing 1.0.0" checklist. The D-155 entry moves from the tagged alpha.5 block to `[Unreleased]` (the tag does not contain it). The changelog says in one sentence that alpha.3 and alpha.4 were tagged on the way and have no notes of their own. D-033 is recorded as not used, D-063 is moved to its place, and `DECISION_INDEX.md` lists D-107 to D-159.
- Parity rows added to section 22.2: D-125, D-127, D-146 and D-128 as yes/yes (checked against the code and tests, D-128 by reading the shared engine path); D-147 as a gap: the `people` of a rule are not filtered for a switched-off recipient. Not decided: filter them or list an exception (`docs/OPEN_QUESTIONS.md`).
- Documentation only; no restart.

## D-161 Watch rules respect a switched-off recipient (2026-11-05)
- Context: the parity check of D-160 found that D-147 filtered the `people` of an action banner but not those of a watch rule, so a switched-off person named in a rule still saw its banner.
- Decision (maintainer: "fix it now"): `BannerManager.sync_rules` passes the rule's `people` through `HubResolver.enabled_people`, the same function the `notify` path uses. All named persons off gives `BANNER_NOBODY`, not everyone. The filtered list is part of the rule's source, so a changed recipient profile rebuilds the rule banner through the entry update listener. A rule without `people` stays visible to everyone.
- Side effect: toggling a profile that a rule names rebuilds that rule, as an edit of the rule does (dismissals of that rule banner are reset).
- Tests: `tests/hub/test_recipient_disabled.py` (profile switched off after the rule exists, all off, no people).
- Blast radius: usual restart; rule banners naming a switched-off person disappear for that person.

## D-162 Tracked files describe the project's own choices only (2026-11-05)
- Context: the pre-release review (E-004) found product names in D-002, and a text pass found wording in decisions, state notes and the decision index that pointed at material outside this project.
- Decision (maintainer): rewrite the text only. D-002 is now "Structure of the human docs" and lists the rules without a source; D-124, D-125, D-129, the open-question heading, the state notes and the decision index no longer describe where an idea came from. Git history is not rewritten and no tag is touched.
- Blast radius: documentation only.

## D-163 Smoke test on a populated instance; the screenshot dashboard is tracked (2026-11-05)
- Context: review findings E-002 and E-007. `dev/smoke.py` asserted exact lists of banner ids, so any other banner or rule on the dev instance failed `make dev-smoke`. The untracked file `docs/images/Head-Up Cards.yaml` is the dashboard the screenshots in `docs/images` were taken from.
- Decision (maintainer): the checks compare only the banners of the run: `for_template` keeps the ids that start with `smoke_`, `empty_operators` ignores the ids present before the phase. The Makefile target says it works next to other banners. The dashboard file is committed where it is, as the source of the screenshots, with its name unchanged.
- Checked: `make dev-smoke` green on an instance that held an extra rule banner (rule `Populated` on a sensor that stays on).
- Note: the file lists two badge entities (`script.test_banner`, `script.test_banner_duplicate`) that exist only on the maintainer's dev instance, and titles with emoji. Tracked as the maintainer asked; D-036 allows it because it is test material, not an installation detail.
- Blast radius: development tooling and a docs image source; no runtime change.

## D-164 Documentation in five documents (2026-11-05)
- Context: review findings R-001 to R-003, D-006 to D-010. The user pages had grown to 20 files, a newcomer met the defaults table and six channels before a first success, copy examples used names the engine rejects, and troubleshooting sent users to websocket commands.
- Decision (maintainer): the README is an intro (with the key features and the diagram), a "How to start" with one install line, four steps and three small YAML snippets, links to the in-depth documents and a documentation list; no defaults table. All other user documentation is in five documents: `docs/setup.md` (install, first message, card, panel, introduction, upgrading, uninstalling), `docs/actions.md` (actions, watch rules, card), `docs/configuration.md` (channels, audiences, recipients, policies), `docs/settings.md` (settings, defaults at a glance) and `docs/examples.md` (examples, household scenarios, FAQ, troubleshooting, limitations, developer notes). The pages they replace are deleted.
- Details: troubleshooting leads with the Message Log, and the websocket commands moved to the developer notes; the panel's copy examples and the docs use `Ground floor (group)`, `person.anna` and `media_player.kitchen`; Developer tools is named Tools in Home Assistant 2026.10; the editable dashboard route is in the README and the setup guide; "hub object" is defined once in the setup guide; `make docs-check` no longer appears on user pages.
- HACS wording (maintainer): Heads Up is in the default HACS list; a pre-release needs "Show beta versions" in the download dialog. Not checked by me against the live HACS dialog.
- Code follows: `scripts/docs_check.py` reads the card options from `docs/actions.md`; the card, popup and loader comments point at the new pages.
- Blast radius: documentation and the panel's Help examples; old page URLs on GitHub no longer exist (the changelog links are updated).

## D-165 The notify response lists the reasons (2026-11-05)
- Context: review findings R-001 and E-009. A push without a Companion device returned `skipped: 1` and no reason; the reason was only in the Message Log. The counts come from the plan made before sending.
- Decision (maintainer): the response of `notify` and the shortcuts gets a key `reasons`: a flat list of `{channel, recipient, result, reason}` for every planned delivery that is held or skipped, empty when nothing is. The counts in `channels` do not change. A recipient is the person when the plan knows one, otherwise the key (speaker, address). Only reasons known at the plan are listed; delivery-time outcomes (`rate_limited`, `duplicate`, quiet hours, `already_spoken`, `cooldown`) stay in the Message Log.
- `create_banner` keeps its own response (`id`, `status`, `evicted`); a banner has no recipient to explain except through its channels.
- Parity: an action response only; watch rules have no response.
- Tests: `tests/hub/test_core_notify.py`. Strings: the `notify` description in four languages.
- Blast radius: a new key in a response; callers that ignore unknown keys are unaffected. Usual restart.

## D-166 The response counts a repeated speech or mail as skipped (2026-11-05)
- Context: review finding E-009. An update of a message does not say it again or send the mail again (`already_spoken`, `already_sent`), but the response counted the delivery as sent because the plan did not know.
- Decision (maintainer): `HubEngine.delivered(id)` takes the channel and recipient pairs the message was already sent to before the call, and `plan(delivered=...)` marks speech and mail rows for those recipients skipped with that reason. The snapshot is taken before `manager.create`, because the engine changes the ledger rows while the call is still planning. First calls and every other channel are unchanged; the speech pause (`cooldown`) and the rate limits stay delivery-time outcomes.
- Tests: `tests/hub/test_speak_channel.py`, `tests/hub/test_mail_channel.py`.
- Blast radius: the counts and `reasons` of an updating call; no restart beyond the usual one.

## D-167 Names ignore case; a close name gets a suggestion (2026-11-05)
- Context: review findings R-017 and E-009 follow-up. `at home` failed although `At home` exists, and the error only listed the valid names.
- Decision (maintainer): in `notify` and the shortcuts, audience, recipient (speaker group, entity id) and policy names are matched ignoring case. An exact match wins; a name that differs only in case and matches one stored name is rewritten to it, so the stored message and the trace use one spelling; two names that differ only in case stay an error. A name that matches nothing fails as before, and when a close name exists (`difflib`, cutoff 0.7, compared in lower case) the error uses the `_hint` variant of its message: `Did you mean "X"?`. Strings in four languages.
- Not changed: names in forms, the panel and watch rules (their own checks), and the `policy` field of a rule.
- Tests: `tests/hub/test_core_notify.py`.
- Blast radius: a call that failed now succeeds; stored names are unchanged. A new translation key per name kind.

## D-168 Invalid calls are explained in sentences; channel settings are panel-only (2026-11-05)
- Context: review findings R-018 and R-019. Schema errors read `required key not provided at 'message'`. For the forms, the review said errors sit far from the field and the mail placeholder check is missing.
- Decision (maintainer): the schemas of `notify`, the shortcuts, `create_banner` and `clear_notifications` are wrapped when the actions are registered (`_Readable`); missing fields, unknown fields, a value outside a list and too long or too short values become sentences such as "The field message is required." and "channels[0] must be one of: banner, mail, ...". Other messages pass through. The raw schemas stay in `SCHEMAS` for docs-check. English only, like the schema; tests assert the error type and the text.
- Correction found while building: the options screen (Configure) has no push, popup or mail settings; they exist only on the panel's Channels page, which already checks them (mail placeholders included) and shows the error under the field. The forms of the integration already key every error to its field. So no code was added for R-019; `docs/settings.md` no longer says the channel settings are under Configure. The generic "Not all required fields are filled in" is Home Assistant's own frontend text.
- Tests: `tests/hub/test_core_notify.py`.
- Blast radius: the text of validation errors changes; callers that match the old text break (the error type is the same).

## D-169 Test send shows the banner row after Send test (2026-11-05)
- Context: review finding E-008. After a banner-only Send test the table said "No delivery was recorded yet", because the outcome rows left the banner out and the call had no other channel.
- Decision (maintainer): What happened lists the banner like any channel, with the people it is for (or "everyone"). The wait for the delivery covers every channel the call named, so a banner-only send waits for its row. Panel only.
- Tests: `tests/card/test-send.test.js`. Not checked in the browser pane.
- Blast radius: panel only; usual restart (the panel URL carries a hash).

## D-170 Message Log words timer rows by policy type (2026-11-05)
- Context: review finding E-011. Any timer row that was not an escalation was worded "Reminder", so a Deliver policy showed as "Reminder Critical delivery".
- Decision (maintainer): `timerName` in `panel/messages.js` words escalation, reminder and a new "Delivery {policy}" (Deliver); any other type shows only the policy name. Four languages.
- Tests: `tests/card/panel.test.js`. Panel only; not checked in the browser pane.

## D-171 Snoozed banners can be brought back by default (2026-11-05)
- Context: review finding F-003. `show_snoozed` defaulted to off, so a viewer who snoozed a banner saw nothing on the dashboard that said where it went or how to bring it back.
- Decision (maintainer): the card option `show_snoozed` defaults to `true`. The footer "Snoozed (n)" with Show now per banner appears only while the viewer has snoozed banners; a card with nothing else to show appears as that footer while something is snoozed. `false` restores the old look. The WebSocket `subscribe` field keeps its own default `false`; the card sends its value. Applies to action and rule banners alike (D-073).
- Tests: `tests/card/heads-up-card.test.js`. Not checked in the browser pane.
- Blast radius: changes what existing dashboards show (only for viewers with snoozed banners); usual restart.

## D-172 Banner buttons name their banner for screen readers (2026-11-05)
- Context: review finding R-014. Every Dismiss, Snooze and Clear button had the same accessible name.
- Decision (maintainer: action plus banner name): `bannerLabel` in the card gives the accessible name "Dismiss: <title>", with the message cut to 60 characters when there is no title. It applies to Dismiss, Snooze, Clear for everyone and Show now in the snoozed list. The tooltip keeps the short word. The long-text clamp of the review is not part of this step.
- Tests: `tests/card/heads-up-card.test.js`. Not tested with a screen reader.
- Blast radius: card only; no visual change.

## D-173 External image URLs are documented as a privacy limit (2026-11-05)
- Context: review finding R-015. The `image` field accepts any http(s) URL, so the card, popup and push fetch from a third-party host and reveal the viewer's address to it. Not a vulnerability of the integration.
- Decision (maintainer): document it, no behaviour change. One sentence in the `image` row of `docs/actions.md` and a section in `SECURITY.md`; a path on this Home Assistant avoids the request. A same-origin default was not chosen because it would break remote pictures that work today.
- Documentation only.

## D-174 Narrow screens: wrapped group row, stacked trace rows (2026-11-05)
- Context: review finding E-010. At 375 px the panel's group row scrolled sideways with a group half visible, and a trace row with a long recipient or reason made the Message Log table wider than its card, cutting the Result column.
- Decision (maintainer): below 480 px the group row wraps so every group stays visible and tappable, and each trace row of the Message Log becomes a small block: channel and recipient first, the result and reason under them, the time last. Wider screens keep the table. CSS only, in `heads-up-panel.js` and `panel/messages.js`.
- Checked in the browser pane at 375 px against the dev instance (a trace with a long push row added to the page): no horizontal overflow, Result visible, all five groups visible. Not checked: other panel tables (Test send results, Overview lists), real phones, light theme.
- Blast radius: panel only; usual restart.

## D-175 Pre-release 1.0.0-alpha.6 (2026-11-05)
- Context: the review fixes (D-156 to D-174) and the documentation restructure are finished on `hub/h9e-wizard`, and the maintainer asked to commit, push and tag a new pre-release.
- Decision (maintainer, explicit): set the manifest version and the changelog heading to `1.0.0-alpha.6` (date 2026-11-05) in one commit, push the branch and push the annotated tag `v1.0.0-alpha.6`. The changelog lists the P9 and P10 features that were still missing from `[Unreleased]`. The GitHub pre-release (not marked latest) is created by the maintainer; HACS shows it only with "Show beta versions". No merge to `main`, no 1.0.0.
- Blast radius: the manifest version is `1.0.0-alpha.6`; the card address carries the new version, so browsers load the new card after the restart.

## D-176 README links and images are absolute (2026-11-05)
- Context: HACS shows the README inside Home Assistant, which resolves relative paths against the user's own address. The diagram showed as an empty box and the doc links would have been dead.
- Decision (maintainer): the README uses `raw.githubusercontent.com` URLs for images and `github.com/.../blob` URLs for the documents and the licence, both on the branch `hub/h9e-wizard`. Committed and pushed on the maintainer's explicit answer; no new tag, so the installed alpha shows it only if HACS reads the branch README.
- Follow-up: when the branch is merged to `main`, the URLs must point at `main` (or at the release tag), or they break when the branch is deleted. Added to `docs/dev/RELEASE.md`.
- Blast radius: README only.

## D-177 Dismissals and snoozes are written to the Message Log (2026-11-05)
- Context: maintainer report, with a trace: a banner and push message was dismissed on the dashboard, the Message Log showed the three `cleared` rows of the push devices but no row for the dismissal, and the push stayed on the device.
- Finding: the clear was sent to all three devices (rows `cleared`, no reason), with the payload of the Companion documentation (`clear_notification` with `data.tag`); the app then did not remove the notification. The documentation says a clear can need recent use of the app (iOS, and Android for non-critical notifications) and says nothing about macOS. Not reproducible in tests: dismissal through the X button, Clear all and a button, with a named recipient or an audience, clears the push.
- Decision: the engine writes a trace row for a dismissal, a snooze and the end of a snooze (`dismissed`, `snoozed`, `unsnoozed`, with the first name of the person), as it already does for an acknowledgement. Four languages for the result words. The troubleshooting page and the push section say what the rows mean and the platform limits.
- Not done: nothing on the server can make the app remove a notification; which of the three devices kept it is unknown (open question to the maintainer).
- Tests: `tests/hub/test_push_lifecycle.py`.
- Blast radius: new trace rows; panel words in four languages; usual restart.

## D-178 Test send: behaviour hint, mail address, tag text (2026-11-05)
- Context: maintainer notes after trying the panel. Dismissible, scope and snoozable do nothing for mail or speech, which cannot be taken back (an acknowledgement matters only through a policy). The mail preview named only the person, not the address, and showed the Global address as `mail:global`. The tag field said only "No tag".
- Decision (maintainer, recommended options): `behaviourUnused` adds a hint under Behaviour for a call with mail or speech: "Nothing here applies" when the call has nothing else, "Mail and speech ignore these choices" when other channels use them; the controls stay. A mail row in the preview carries the address (`address` in the row of `hub_plan`, from `MailChannel.check`) and the table shows it after the name; the Global address is labelled "Global address". A call with no mail service chosen shows the row as failed with `no_mail_service`; a person without an address was already skipped with `no_mail_address`. The tag field explains the three uses of a tag, the empty case and that the test message always gets the tag test while the preview uses the tag entered.
- Strings: panel texts in four languages, plus the reasons `no_mail_address` and `no_mail_service`.
- Tests: `tests/hub/test_mail_channel.py`, `tests/card/test-send.test.js`. Checked in the browser pane (tag text, both hints); the address rows are covered by pytest only, because the dev instance has no mail service.
- Blast radius: panel and one extra key in the rows of `hub_plan`; usual restart.

## D-179 Recipients page: a person per row with the channels (2026-11-05)
- Context: maintainer note on the first list (a row per person with its devices, a "changed" badge and the missing-user text). The list was hard to scan and showed devices nobody needed to see there.
- Decision (maintainer, recommended options): on a wide screen a table with one row per person and a column per channel (banner, push, popup, mail); a cell is a tick (accepted and can work), a dash (not accepted) or a warning mark with a tooltip (accepted but cannot work: push without a usable device, popup without a Home Assistant user, mail without an address; `channelState`). Below 560 px the channels are written under the name and a problem after its channel ("Push (no device)"). The "changed" badge and the device list are gone from the list. A disabled person is greyed out with a small "disabled" badge. The text "No Home Assistant user: no popup." appears only when a person is opened. The Edit button stays.
- Strings: new words in four languages, `customized` removed. Tests: `tests/card/editors.test.js` (channel states, words in four languages).
- Checked in the browser pane at desktop and at 375 px with the dev persons, including a disabled person. Not checked: a person with a Companion device, a person with mail set up, the German, French and Spanish texts on screen.
- Blast radius: panel only; usual restart.

## D-180 Popup style per severity: four corners or the middle (2026-11-05)
- Context: maintainer note 4. The style per severity was a card in the bottom right corner, a centered window or off.
- Decision (maintainer): the same per-severity setting offers a card in any of the four corners, the centered window or off, instead of a separate position setting. The values are `card` (bottom right, so a stored `card` keeps its meaning), `card_bottom_left`, `card_top_right`, `card_top_left`, `modal` and `off`. A quiet message is a card in the corner of its severity, or at the bottom right when the severity is centered. At phone width the card is full width and keeps top or bottom; left and right make no difference. Top cards slide in from above.
- Strings: the style words of the Channels page in four languages. Tests: `tests/hub/test_popup_channel.py`, `tests/hub/test_panel_editors.py`, `tests/card/popup.test.js`.
- Checked in the browser pane: the Channels page lists the six styles and saves them, and a warning popup appeared at the top left; settings restored afterwards. Not checked: the other corners on screen, phone width, the animation.
- Blast radius: panel and popup module; usual restart.

## D-181 Escalation, Deliver and Fallback can take channels or recipients from the call (2026-11-05)
- Context: maintainer question: a fallback for "At home is empty, tell Everyone" works, but the policy always lists its own channels; it cannot keep the call's channels, and it cannot reuse the call's recipients on other channels. The maintainer asked for four combinations and, after a review per policy type, for them everywhere they make sense.
- Review: Fallback gets all four. Escalation and Deliver get three: the "only the channels that reached nobody" option needs a failure to react to, which neither has. Reminder, Quiet hours, Away and Summarize do not add deliveries and are unchanged.
- Decision (maintainer): two settings per policy of those three types: where the channels come from (`channels_from`: `policy`, the default; `call`; `failed`, Fallback only) and where the recipients come from (`targets_from`: `policy`, the default; `call`). Taking both from the call is refused (`nothing_new`).
  - Same channels, new recipients: the policy gives a people target (an audience or persons, used for push, popup and mail) and a speakers target (used for speech), stored in `targets` under `people` and `speak`; one of them is required.
  - Only the failed channels: the same, for the channels of the call that reached nobody for the reason the Fallback waits for.
  - New channels, same recipients: the call's people (the first audience or persons it gave on push, popup or mail) are reused on the new people channels; speech reuses the speakers the call named, else the channel is skipped; the Persistent Notification needs no target.
  - New channels and recipients: as before.
- Existing policies read the same: the two settings are stored only when they are not the default.
- Built in `hub/policies/sources.py` (`message_for`, `check`, `target_keys`); `escalation.message_for` delegates to it, so the preview, escalation, Deliver and Fallback all use it. The integration's policy form has the two selectors and the people fields; strings in four languages.
- Tests: `tests/hub/test_policy_sources.py`, `tests/hub/test_policy_flow.py`. The panel editor follows in the next commit.
- Blast radius: usual restart; new optional keys in policy subentries (an older version ignores them and would read a policy with `channels_from: call` as one without channels).

## D-182 Policy sources in the panel; the Fallback wording (2026-11-05)
- Context: D-181 built the engine and the integration form. The panel editor, the plain-language sentence and the misleading text "Fallback: use other channels" were left.
- Decision (maintainer, as D-181): the panel's Escalation, Deliver and Fallback editors have the two selectors (Fallback also offers "only the channels that reached nobody"), the People and Speakers targets, and a hint that "same recipients" is empty when a Fallback waits for an empty audience. The sentence says where the channels come from, who gets it and, when the recipients come from the call, says so. The flow data carries the two settings only when they are not the default. The type texts of Fallback in the panel, the integration form and four languages now say "deliver somewhere else: other channels, or other people on the same channels". `docs/configuration.md` has a section with the four combinations and the At home to Everyone example.
- Tests: `tests/card/editors.test.js` (flow data, checks, stored policy read back, sentences, words in four languages).
- Checked in the browser pane: both selectors in the Fallback editor, the People and Speakers blocks after choosing "The call", a saved policy read back (`channels_from: call`, `targets.people`), the sentence; the dev policy was deleted again. Not checked: the Escalation and Deliver editors on screen, the escalation or fallback sending to a real device, the three other languages on screen.
- Blast radius: panel and texts; usual restart.

## D-183 Action form: field order by purpose, clearer Dismissible text (2026-11-05)
- Context: the fields of `notify` appeared in the order they were added, so `condition` and `wait_for_condition` were apart, and Dismissible said only "shows a close button".
- Decision (maintainer): the action form lists fields in four groups: Content (message, title, severity, icon, image, tts_message), Delivery (channels, to, policy, recipients, audience, people; D-184 puts channels and policy right after message and title), Lifetime (id, tag, timeout, condition, wait_for_condition, mode), Interaction (tap_action, actions, dismissible, dismiss_scope, snoozable, snooze_scope, snooze_options). `push`, `popup`, `speak` and `create_banner` keep the same relative order. Dismissible says that a dismissal removes the message from all channels except speak and mail and what Off implies. Dismissible, Snoozable and Wait for condition say that an unchecked field uses the default (the checkbox of an optional field in the Home Assistant action form means "send this field").
- Blast radius: `services.yaml` order and texts in four languages; no schema change. Collapsible sections were not added (not verified against the current Home Assistant docs).

## D-184 notify: shared recipients, a policy list, dismiss and snooze as one choice each (2026-11-05)
- Context: `to` was nested YAML per channel, `policy` took one typed name, and dismiss and snooze took five fields (two booleans, two scopes, the choices). Home Assistant cannot list policies or audiences in an action form (the select selector has fixed options, checked in the selector docs).
- Decision (maintainer): `notify` gets `recipients` (persons) and `audience` for banner, push, popup and mail at once, and `speakers` for speech; a `to` entry of a channel wins. `channels` stays required (no default channels). `policy` is a list: `automatic` (the policies that match, the default), `none` (alone) and policy names; names alone use only those, with `automatic` they are added to the matching ones; one name is still stored as a string. `dismiss` and `snooze` (`off`, `user`, `everyone`) replace `dismissible`, `dismiss_scope`, `snoozable` and `snooze_scope` in `notify`; an unquoted YAML `off` (false) is accepted. `automatic` and `none` are reserved policy names. `create_banner`, watch rules, the stored banner and the card keep the old fields. The full policy dropdown is in the panel (Test send writes the call as YAML), the action form has a multi-select with typed names.
- Not done: the watch rule form and the integration options form still use the old booleans and scopes; no sections in the action form (syntax not verified). Editable presets stay an open question.
- Blast radius: `notify` schema (breaking for alpha callers using the four old fields), `services.yaml`, texts in four languages, panel Test send, `docs/actions.md`; no stored-data change (a policy list is stored for new calls).

## D-185 notify: `to` hidden from the form and the docs (2026-11-05)
- Context: with `recipients`, `audience` and `speakers`, `to` is needed only for different people per channel, and its nested YAML example cluttered the form.
- Decision (maintainer): remove `to` from `services.yaml`, the texts and `docs/actions.md`; examples use the shared fields. The schema keeps accepting it (`HIDDEN_FIELDS` in `services.py`; `docs_check` skips it), so Test send, the tests and stored messages keep working. Open: see `docs/OPEN_QUESTIONS.md`, "Per-channel targets in notify".
- Consequence: "banner for everyone, push for some people" is not expressible in a documented call; the shared fields limit the banner too.
- Blast radius: form and docs only; no change of behaviour.

## D-186 Audiences as sensors and policies as switches, for dropdowns in the action form (2026-11-05)
- Context: an action form can only offer a dropdown of entities; it has no list that an integration fills at runtime (the select selector is fixed, checked in the selector docs). The entity selector filters by integration and domain (docs). In the installed Home Assistant (2026.10 venv) entities can be attached to a subentry (`config_subentry_id`), and deleting a subentry clears its entities (`async_clear_config_subentry`).
- Decision (maintainer): one `binary_sensor` per audience (built-in ones attached to the entry, custom ones to their subentry; none for a built-in the admin switched off): on while at least one person is in it, severity `warning` for the display, attributes `audience` and `members`. One `switch` per policy: on is `enabled` in the policy subentry, turning it writes the subentry. The unique ID holds the built-in kind or the subentry ID, so a call that names the entity resolves the current audience or policy name and a rename breaks nothing. The `audience` field of `notify`, `push` and `popup` and the `policy` field of `notify` use the entity selector; names stay valid in YAML. `automatic` and `none` cannot be entities (variant a): an empty `policy` is automatic, and `no_policy` is `policy: none`.
- Found on the dev instance (2026.10.4): entities of several subentries that share one device make Home Assistant move the device to the last subentry and drop the entities of the others, the banner-count sensor included, with a warning that stops working in 2027.8. The audience sensors and policy switches therefore have no device; their names carry the prefix (`Heads Up audience At home`, `Heads Up policy Smoke night`), so the entity IDs are `binary_sensor.heads_up_audience_at_home` and `switch.heads_up_policy_smoke_night`. Checked on the dev instance: the Notify form lists the six audiences and the policies in its pickers; the field order is the one in `services.yaml`.
- Not done or not verified: whether Home Assistant's entity picker shows entities of the category diagnostic (not used); the sensor state of Last to leave and First home follows the settled presence; the display severity ignores unknown presence; nothing was run against a real Home Assistant (`make dev-smoke` not run; `make hassfest` passes); the new entities are not in the dev smoke; a device-registry link left by the first run on the dev instance showed the warning once.
- Blast radius: two platforms, a restart, one extra device-linked entity per audience and policy (6 built-in plus own), the entity list of every user; no stored-data change.

## D-187 notify: manual policies add to the automatic ones; field order and defaults (2026-11-06)
- Context: the first form had `policy` (a named policy replaced the automatic ones) and `no_policy` (no policy at all). A user could not say "keep the automatic policies and add this one" or "switch the automatic ones off but keep this one".
- Decision (maintainer): `policy` is the manual policy field and its names apply next to the automatic policies that match; `disable_automatic_policies` (replaces `no_policy`; renamed `match_policies_automatically` with the opposite polarity by D-189) switches the automatic ones off, so manual policies alone apply, and without a manual policy none. It is stored in the same list `matching.select` reads (`automatic` plus the names, the names alone, or `none`), so the engine and the rules are unchanged; `policy: none` and `automatic` still work in YAML. This supersedes "a named policy is the only one used" of D-146 for `notify`; a watch rule's Policy field keeps that meaning. Form order: channels, disable automatic policies, manual policy, audience, recipients, speakers, spoken text, then severity and the rest. Audience has the default `binary_sensor.heads_up_audience_everyone` (checked in the form), recipients none. The channels text has no YAML example. Test send has the same two controls.
- Consequences: a form call with Audience checked and Recipients also given fails with "give either audience or recipients", so the user unchecks Audience; a banner with the default audience Everyone is shown only to users linked to a person, where a banner without a target is shown to everyone; the default entity ID is wrong when the Everyone audience is switched off or its entity ID was changed.
- Blast radius: `notify` field names (`no_policy` removed), policy behaviour of `notify` with named policies, texts in four languages, Test send, docs.

## D-188 Condition logic: `wait_for_condition` removed, recurring needs a condition (2026-11-06)
- Context: `condition`, `mode` and `wait_for_condition` were three fields for two questions. `wait_for_condition: false` ("send only if the condition is true now") duplicates a condition in the automation, and `mode: recurring` without a condition did nothing.
- Decision (maintainer): for the final 1.0.0 release, as a breaking change of `create_banner` (the fields exist since 0.1.0) and of `notify`: `wait_for_condition` and the status `condition_false` are removed from the schema, the manager and the docs, so a condition that is false at the call always waits; `mode: recurring` without `condition` is refused (`_check_create`). `mode` is shown as "Show once" and "Recurring" with the descriptions in the form. This supersedes D-006 (the `wait_for_condition` part) and D-038. A watch rule is always recurring (`manager.py`), so it already has this model; Test send has no condition or mode field. Stored banners are unaffected (neither field was stored).
- Not done: the reverse is not offered; a caller that needs "only if true now" checks it in the automation. The release note and `docs/setup.md#upgrading` carry the breaking change.
- Blast radius: `create_banner` and `notify` schemas, `manager.create`, texts in four languages, docs, tests; the card and the rules are unchanged.

## D-189 notify: positive policy switch, default severity info, clearer scope names (2026-11-06)
- Decision (maintainer): `disable_automatic_policies` becomes `match_policies_automatically` (default on; off means only the manual policies apply, none without one), because a positive switch needs no double negative and "match" is the word the docs use for policies that fit a severity or tag. `notify`, `push`, `popup` and `speak` default to severity `info` (schema default, form default); `create_banner` and the watch rules keep `warning` (released since 0.1.0, not part of this change). Severity text names the push level, popup style and quiet hours effects; Icon says it is shown on the banner and in the popup only; ID says that a fixed ID replaces and clears and that no ID creates a new message each call (shortcuts: sent once, cannot be cleared). `mode` is listed before `condition`. `dismiss` and `snooze` are "Dismiss for" and "Snooze for" with the options Nobody, Only that person, Everyone: the field decides to whom the action applies, not who may do it; Nobody turns it off. Test send follows (same names, default info, same switch).
- Found: the `icon` field of `push` and `speak` has no effect (push and speech show no icon); the text says so. Removing the field is a possible later cleanup.
- Blast radius: `notify` and shortcut defaults (an `info` push is passive, where a `warning` push was normal), texts in four languages, Test send, docs.

## D-190 Pre-release 1.0.0-alpha.7 (2026-11-06)
- Decision (maintainer): prepare a seventh pre-release on the branch `hub/h9e-wizard`. It carries the `notify` simplification (shared recipients, audience and policy dropdowns from sensors and switches, `dismiss` and `snooze`, manual policies, default severity info, D-183 to D-189) and the breaking condition change for 1.0.0 (D-188). Manifest `1.0.0-alpha.7`, changelog section dated 2026-11-06. The tag, the push of the tag and the GitHub pre-release wait for the maintainer's explicit request (D-020).
- Blast radius: manifest version only; the card URL carries the version, so browsers fetch the card again after the restart (D-050).

## D-191 Mail subject and body per message (2026-11-09)
- Decision (maintainer, variant A of five): `heads_up.notify` takes `mail_subject` and `mail_body`. Each replaces the template from the Channels page for that one message; an empty field keeps the page template. The placeholders and limits are those of the page templates (`check_subject`, `check_body`); an unknown placeholder, an empty text or more than 200 or 2000 characters is refused, and so is either field without `mail` in `channels`. `{person}` is the recipient, because the channel already sends one mail per recipient.
- Order: both fields come last in the form and in `services.yaml`, after `snooze_options`; no existing field moved.
- Parity (rule 9): only `notify` has channels, so `create_banner` and watch rules, which only show a banner, have no mail text and need no exception. Test send offers both fields while `mail` is chosen.
- Rejected: named mail templates on the Channels page (B, larger rework, stays an option), a template per policy (C), per person (D), fixed formats in a dropdown (E).
- Blast radius: new optional action fields only; stored messages without them load unchanged; no restart beyond the usual update.

## D-192 notify needs a severity; Away has critical_passes; wait_for_condition is ignored with a repair issue (2026-11-09)
- Context: a maintainer review of a production migration (about 36 callers) found three gaps: a `notify` call without severity became `info` and, with the shipped push levels, a silent passive push; an Away policy held critical messages for people who are away; and an automation that still sends `wait_for_condition` failed at run time (D-188).
- Decision (maintainer): `severity` is required in `heads_up.notify` (`push`, `popup`, `speak`, `create_banner` and the rules keep their defaults). Policies keep `severities` optional, empty meaning any; the form is unchanged. The Away policy gets `critical_passes` (default true, as Quiet hours), so critical messages go to people who are away at once unless the policy says otherwise. `wait_for_condition` is accepted by `create_banner` and `notify`, ignored, and raises one Repairs issue `wait_for_condition_removed` (not fixable, persistent) that names the migration; a message whose condition is false waits (D-188 stays the behaviour, only the hard failure goes).
- Not done: a warning for a policy that hides later ones in the mode "first" (rejected: empty severities are valid); critical always delivered regardless of policy choice (rejected for now); an automatic migration of automations (the integration never edits automations, rule 3).
- Blast radius: callers of `notify` without severity now fail validation; an existing Away policy now lets critical messages pass (stored policies have no `critical_passes`, so they read as true); texts in four languages; Test send already sends a severity; docs and tests.

## D-193 Mail placeholder person_id (2026-11-09)
- Context: `{person}` is the friendly name of the person entity, so a mail rule that routes by a bare name breaks when the friendly name is "Philip Smith" or is renamed. The review asked for the ID or a slug, with an explanation.
- Decision (maintainer): a seventh placeholder `{person_id}`, the part of the entity ID after `person.` (`philip`), empty for the Global address. It applies to the Channels page templates and to `mail_subject` and `mail_body`. The docs say what both person placeholders hold.
- Not done: a capitalised first-name placeholder (`{person_first}`): not chosen; the ID is lower case, so a rule that needs `Philip` must match case-insensitively or the friendly name must be exactly that.
- Docs: Quiet hours with the action Drop or Wait apply to mail was already stated in `docs/configuration.md`; the code matches it and D-129 (which said quiet hours do not change mail) is superseded for those two actions.
- Blast radius: new placeholder only; a template with `{person_id}` was refused before and is valid now.

## D-194 Inspecting a production setup: dry run, pasted calls, diagnostics, trace (2026-11-09)
- Context: the migration review asked for a way to test every caller of `notify` without sending, to read the configuration without the server, and to read the trace from an automation.
- Decision (maintainer): `notify` takes `dry_run` and returns `HubEngine.preview` (the plan the panel already used), with the push level on each push row. Test send gets a second input: a pasted action step or its data, with Jinja rendered on the server from sample values (`yaml.safe_load`, so no tags and no file access; admin only), planned and sent through the same code as the form (`heads_up/hub_plan_yaml`, `heads_up/hub_test_send_yaml`). A diagnostics download redacts mail addresses, the install token, titles and texts. The policy switches show the policy as attributes with its place in the list. `heads_up.get_trace` returns the trace (response only). The trace is stored in `.storage/heads_up.trace`, saved with a delay, loaded at start and removed with the entry.
- Found: `panel_test.check` discarded the corrected names (an audience given as its sensor), so a pasted call that names the audience by sensor was planned wrongly; it now uses the stored spelling like the action.
- Not done: persisting the log of last actions and the recent messages (the trace answers "why"); a dry run that takes another time of day (D-120 stays open).
- Blast radius: new optional field and one new action; a new store file; a new diagnostics platform; the trace now outlives a restart, so the panel shows entries from before it; texts in four languages.

## D-195 Buttons, conditions and banner recipients (2026-11-09)
- Context: the migration review needed to know who pressed a button and where, to mark a dangerous button, to show a banner for a device that is gone, and to address a banner like a `notify` call.
- Decision (maintainer): `heads_up_banner_action` carries `person` and `channel`. A button may set `destructive` and `require_auth`; both are stored only when set. A condition may set `treat_unavailable_as` (`met` or `not_met`); without it an unavailable entity changes nothing, as before. `create_banner` takes `audience` and `recipients` (one of them, or `people`, which stays as an alias); an audience is resolved when the call is made, as in `notify` (D-131). The `recipients` field of `push` and `popup` is a person picker and that of `speak` a speaker picker in the action form; the schema still accepts what it accepted.
- Parity (rule 9, `docs/DESIGN.md` §22): the button fields and the event are in both sources (one schema, one `press`). Exceptions: `treat_unavailable_as` is not in the rule form, because a rule treats an unavailable entity as not true (D-053) and a template rule covers the case; `audience` and `recipients` are not in a rule, because an audience resolved at build time goes stale while a rule lives as long as its condition, and a rule keeps `people`.
- Not done: asking for confirmation before a destructive press (the Companion app has no such key; `require_auth` is the available guard); several entities in one condition (open, see OPEN_QUESTIONS).
- Blast radius: new optional fields and two new event keys; the event data of a press has two more keys, so a trigger with an exact `event_data` match on all keys is unaffected (a trigger matches a subset); card and popup CSS; texts in four languages.

## D-196 Pre-release 1.0.0-alpha.8 (2026-11-09)
- Decision (maintainer): prepare an eighth pre-release on the branch `hub/h9e-wizard`. It carries the review of a production migration (D-192 to D-195) and the mail text per message (D-191): `notify` needs a severity, the Away policy has `critical_passes`, `wait_for_condition` is ignored with a repair issue, `dry_run`, Test send from a pasted call, diagnostics, policy switch attributes, `heads_up.get_trace` with a stored trace, button fields, the event keys `person` and `channel`, `treat_unavailable_as`, `audience` and `recipients` of `create_banner`, and the mail placeholder `{person_id}`. Manifest `1.0.0-alpha.8`, changelog section dated 2026-11-09. The tag, the push of the tag and the GitHub pre-release wait for the maintainer's explicit request (D-020).
- Breaking against alpha.7: a `notify` call without `severity` is refused; a trigger on `heads_up_banner_action` with `event_data` still fires, because it matches a subset of the keys, which now include `person` and `channel`.
- Blast radius: manifest version only; the card URL carries the version, so browsers fetch the card again after the restart (D-050).

## D-197 The policy editor shows the entity ID of the switch (2026-11-09)
- Context: a policy can be named in a call by its text name or by its switch. A rename changes the name, not the entity ID, so a call by name breaks and a call by ID does not; a rule and a stored message keep the old name (no rename handling exists).
- Decision (maintainer): the policy editor shows the entity ID of the switch: the registered ID for an existing policy, and for a new policy the ID Home Assistant will assign (the free one, `_2` when taken), through the admin command `heads_up/policy_entity_id`; `panel_config` lists it for each policy. The help text says that a rename keeps the ID.
- Not done: renaming the name inside rules and stored messages when a policy is renamed (a larger change, open); the same line for audiences.
- Blast radius: panel only, one read-only admin command, texts in four languages.

