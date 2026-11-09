# Open questions

## Card follow-ups (found in Phase 4)
- Checked 2026-10-27 in the browser pane (admin, dev HA 2026.9.4, 375×812 emulation): both layouts at phone width, Enter on a tappable banner, keyboard use of the snooze button and its choices (Enter, Escape, focus), right swipe with a mouse and with synthetic touch pointer events. Banner buttons wrap to a second line at 375 px; text buttons are 40 px high, the icon buttons 48 px.
- Not checked: `show_all` with a banner targeted at another person, Space on a tappable banner, screen readers (only the DOM was read: live regions, hidden severity labels, `aria-label`s), swipe on a real touch screen (R-10; `touch-action: pan-y` is untested), and the card editor inside HA's own card dialog (only as a floating element).
- Contrast of custom `colors` is not checked by the card (D-048); a contrast hint in the editor is an idea, not planned.
- `clear_all` always dismisses without a confirmation (D-048). A `confirm_clear_all` option is an idea for shared wall displays.
- N-14 was checked on one layout (one grid section, 1280×800). Other column counts are not compared.

## Before the first release
- Maintainer reported on 2026-10-26: CI is green, the repository is public, the integration runs on their own Home Assistant, and no other HACS integration uses the name "Heads Up" (checked by the maintainer; this supersedes the partial check in N-48).
- Read from the public GitHub API on 2026-10-27: description and topics are set, issues are on, the license is MIT, releases `v0.1.0` to `v0.3.0` exist. Private vulnerability reporting cannot be read without a login (the security page shows a "Report a vulnerability" button). The pull request to `hacs/default` (number 12746) is open in the review queue with one bot comment, no requested changes and a clean merge state; the bot asks submitters not to comment on it.
- Not checked: the HACS install steps in the README after "Add" (download step) against the now public repository; private vulnerability reporting (`docs/dev/RELEASE.md` step 5).
- The README has eight screenshots. A GIF of a banner disappearing is not planned (maintainer, 2026-10-27); a produced video is on the deferred list.
- Resolved in H10 (2026-11-02): mypy, the tests and the dev HA run on 2026.10.4; 2026.9.4 stays in CI (D-123, N-91, N-92).

## Resolved
- Card design follow-ups (compact one-liner, time, title, `show_severity`, severity colors and `colorize`, clear all, swipe, collapsed items, empty message): built in Phase 7 (D-048, D-049, N-49 to N-51).
- N-42 (card missing after a restart): cause found, not fixable in the integration; documented (D-045).
- Corrupt storage behaviour: D-044, `tests/test_storage_corruption.py`, N-45.
- Sections-view gap for an empty card (N-14): none with `display: none` (D-040).
- `hass-action` for tap actions and `confirmation` (N-38, live check) and WebSocket re-subscribe (N-39, N-40, D-041; live restart check).
- Person `user_id` changes while banners target it: re-filtered on every change of a referenced person's `user_id`; a removed person matches nobody (Phase 3, `tests/test_people.py`).

## Deferred ideas (out of MVP scope)
- Popup/modal for critical banners (D-018).
- Event-based banner creation; mirroring persistent notifications as banners (D-022).
- Template and full HA condition syntax for `condition` (D-005).
- Absolute `expires_at` input (D-024).
- Per-severity binary sensors (D-013).
- Other channels under the Heads Up name: toasts, popups (D-004).
- A produced demo video of the card and the banner lifecycle (long list, maintainer 2026-10-27).

## Phase 8: watch rules
- Label-based watching (a label on an entity adds a banner with its name): not built (D-057).
- Not verified: the rule form in Home Assistant's own UI (wording of "Add watch rule", the multi-value State field, entity pickers; the flow ran through the REST API only), `show_all` rendering of an inactive rule banner, the rule banner layout in the compact layout and at phone width.
- A rule whose watched entity is also one of its `people` entities is not tested.

## Phase 9: condition operators
- Not built: `matches regex`, `at_least`/`at_most` (inclusive single bounds; `between` covers the inclusive case; dropped in D-066), comparing two entities. "For at least N minutes" is built (D-066).
- Verified in the browser pane (admin, dev HA 2026.9.4, 2026-10-25): the rule form shows the Condition dropdown and the description without a translation error. Not verified: submitting a rule with an operator in the UI, 2026.10, `make dev-smoke` with an operator rule.
- A numeric `state` such as `25` is stored as text `"25"` in an action condition; compared as a float, so `"25.0"` and `"2.5e1"` also work. Not tested with locale decimal commas (a value `"25,5"` is not a number).

## Phase 10: `for` and template conditions
- Not verified on the dev HA or in the rule form UI: the "Condition must hold for" field (duration selector wording, validation message), a real wait over several minutes, a template condition through the REST action. `make dev-smoke` was not extended.
- Templates in watch rules are not built (maintainer scope: `create_banner` only).
- A waiting banner (or a rule true at setup) restarts its wait after a restart; storing the start of the wait would avoid the delay (D-066).
- A downgrade to a version without `condition.template` fails to load stored banners with a template condition (DESIGN §19.3).

## Phase 11: empty operators
- Not verified in the rule form on the dev HA: the blank State field, the new operator labels, saving a rule with `not_empty`.
- Not built: a trigger for the moment a value changes (conditions describe a state, not a change).

## Roadmap candidates (maintainer-chosen order, none approved yet)
- Still open from the Phase 12 idea: store the start of a condition `for` wait so a restart does not restart it (D-066). Buttons and snooze are built (Phase 12, below).
- Phase 13 candidate: bounded, restart-safe history of created, cleared, dismissed, expired and snoozed banners, readable over WebSocket and optionally shown in the card.
- Phase 14 candidate: watch rules by label, area or entity filter (reopens D-057); open: one banner per match or one aggregated banner.
- Phase 15 (design only, branch `design/notification-hub`, not merged): notification hub. Decisions D-075 to D-082, full record in `docs/dev/HUB_DESIGN.md`. Open items are listed under "Phase 15: notification hub" below.
- Adoption candidates: translations, HACS default review feedback, repository settings and topics (`docs/dev/RELEASE.md` steps 3 to 5), the unchecked items listed above.
- Parked: mirroring persistent notifications as banners (D-022), low value for the maintainer.

## Translations (D-071)
- The German, French and Spanish texts need review by native speakers. Checked: HA loads all three files (`frontend/get_translations`), the card shows German on the dev HA. Not checked: the options flow and the rule form in each language in HA's UI, long texts in the narrow card editor.
- `tests/test_translations.py` and a vitest case check that every key and placeholder exists in each language.

## Phase 12: buttons and snooze
- Not verified: swipe on a real touch screen, screen readers, the options flow and the rule form in Home Assistant's UI (only through the flow APIs in tests), Home Assistant 2026.10. Phone width, the compact layout with the snooze row and keyboard use are checked (see the card follow-ups above). Checked in the browser pane (admin, dev HA 2026.9.4) with a mouse: snooze button and row, a choice hides the banner in every card, a button with `dismiss`, right swipe opens the row, left swipe dismisses.
- Not tested on the dev HA: pressing a button with an `action` (navigation, confirmation), a global snooze with a second user in the card, a snooze ending in a real wait.
- Not built: a snooze choice entered by the viewer, an event when a snooze ends, a way to end a snooze early from the card, snooze state of rules over a restart (D-069).
- A button's `action` runs with the viewer's permissions in the card, so it does nothing for a client that is not a card (D-070).

## Card registration (D-072)
- The fix is not confirmed on the maintainer's iPhone: it needs a release, an update of the integration and several reopens of the dashboard in the Companion app. If the error still appears, the next steps are a loader that retries under a new URL and a look at the frontend source for the registry swap.


## Phase 15: notification hub (design only, on branch `design/notification-hub`)
- Dedicated API design session before any implementation: which actions and arguments exist; one generic notify action versus per-channel actions like `create_banner`; how a caller names a policy, audience and channels (create_banner takes no channel argument, D-077).
- Shape of per-channel content overrides (for example text for speech).
- Popup area recipients and how a dashboard session learns its area: not in v1 (D-091); revisit later.
- Technical, proposed in the design for review: push identity with an install token, a delivery ledger store, a transition seam in the manager (the manager has no event for every moment a message becomes visible).
- Whether the unit is called "message" in docs and API, while `create_banner` stays.
- The admin panel under the no-build-step rule (D-021): serving and build approach.
- HA facts checked from source and docs on 2026-10-29 (N-61 to N-68). Still unverified: the person to Companion device mapping (N-64), the exact notify service name pattern on a device, the user in the action event context, announce and volume restore behaviour per platform, the same facts on 2026.10, a second extra JS URL, behaviour of an older version with an unknown subentry type.
- README material for later: problem statement, vocabulary and end-to-end journeys in `docs/dev/HUB_DESIGN.md` (marked).
- Build phasing is delayed until the design is final. Hub status (build or not, §1 non-goal) is undecided.
- Conditions in the hub need their own design session (levels: lifecycle, trigger, policy gate, step gate, channel or recipient gate; shared schema; named conditions; behaviour when a condition flips during escalation). See `docs/dev/HUB_DESIGN.md`.
- Policy steps may add channels and audiences (escalation, fallback); wording of "primary channel" in `notify` to settle in the API session.
- Panel: registration is \`panel_custom.async_register_panel\` with \`module_url\` and \`require_admin\` (N-69); \`require_admin\` only hides the sidebar entry, so the panel's WebSocket commands check admin themselves. Still unverified: the web component contract, whether \`panel_custom\` must be in the manifest, a dev check. Whether the recent-messages list is stored (links to the Phase 13 history candidate).
- Idea, not planned (D-099): named conditions as reusable hub objects and an optional "only if" on a policy (examples: guest mode on, alarm disarmed, freezer temperature above a limit for 10 minutes).
- Watch rules are frozen (D-100). Ideas: a "watch an entity" blueprint as the no-YAML path for new setups; whether a custom integration can ship blueprints (unverified); deprecating rules later with a migration.
- Hub design: the open items about summary details, default delivery and precedence are closed (D-106).
- H0b (2026-10-30) checked more facts (N-75 to N-80): announce and volume per platform, the custom panel contract, device renames, the Android action event, blueprints (an integration cannot ship them). HA facts checked earlier on 2026-10-30 (N-70 to N-74): notify service names, person to device path, action event context, blueprints (not covered by the docs read), 2026.10.4 for the read files. Still open: announce and volume restore per platform, whether an integration can ship blueprints, the custom panel web component contract and manifest listing, and a run on the dev instance with a fake mobile_app registration.
- Follow-up (maintainer, 2026-10-31), decide after trying the integration: move audiences, recipient groups, recipient profiles and policies out of config subentries into one integration-owned store (`heads_up.hub`) written only through an admin-only API, so a delete that would break a reference can be refused with the list of users, ids stay stable on rename, and watch rules remain the only subentries. Cost: the subentry flows of H2 and their tests are replaced, and the panel (H9a, H9c) becomes the only editor, so the panel registration check (N-77) moves to the start of H9a with an options-flow menu as the fallback. Nothing has shipped, so no migration is needed if done before release. Trigger: how often a deleted audience or group breaks a policy in real use (D-111).
- Test send "what if" time (D-120): preview a call as if it were another time of day. It would need the Quiet hours stage to take a time from the dry run. Not planned.
- Hub build plan and all open and proposed values: `docs/dev/hub/ROADMAP.md` and `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`.

## Hub: checks that need real devices (H10, 2026-11-02)
- Every hub check ran against stub devices (rule 2). Not verified on real hardware: Companion app pushes with buttons, tag replacement and `clear_notification`; the iOS critical alert and the Android alarm channel (silent mode, Do Not Disturb, `priority` and `ttl` on an idle phone), the clipped buttons on Android; a press on Acknowledge, Snooze or Dismiss coming back as an event; speech through `assist_satellite.announce`, `tts.speak` and `media_player.play_media` on real speakers; popups on a wall tablet; the panel on a touch screen.
- Not verified: a screen reader on the panel and the popup, and the German, French and Spanish text of the panel on screen.
- Idea: the delivery trace and the recent messages list are kept in memory only; whether they survive a restart is open (D-118).

## Capabilities for fanning one message out (D-124, 2026-11-03)
- Mail channel: how a recipient maps to a mail target (profile field or the call), which notify service it calls, and how a failure shows in the ledger.
- Late button presses: whether the button stays on the phone after the push is cleared; if not, which messages need a different lifetime.
- Delivery-failure event: name, payload and which outcomes fire it (no audience, failed, rate limited).
- Conflicting policies (two escalations, Away against a fallback to an audience, quiet hours against a deliver policy): needs a dedicated design session before channels and targets taken from the message are built, and to settle whether a named manual policy adds to the automatic ones (D-145, D-146, maintainer 2026-11-04). The design session started on 2026-11-04.
- More simple interaction behaviours beyond "all that apply" and "only the first" (D-148, maintainer 2026-11-04): to be checked in a later session, together with how the choice appears in the introduction.
- `heads_up.clear_notifications` removes whole messages (D-158). Ideas: take a message back from chosen channels only while it stays alive on the others, and clear for chosen audiences or recipients (the engine already clears one channel for one person on a dismissal). Deprecating `create_banner` in favour of `notify` is a separate decision.

## Editable notify presets (maintainer, 2026-11-05)
- Idea: a second, simple call next to the expert `notify`, based on presets (a "notification type") that the user edits in the panel: channels, severity, policy, dismiss and snooze behaviour, optionally recipients. The call changes only content (title, message, spoken text, image, tap action). Shipped starters (for example Critical, Info, Reminder) and a type name in the call. Open: fixed or editable types, whether recipients belong to the type, whether `id`, `tag` and `condition` stay in the simple call, one action with a `type` field or one action per type, parity with watch rules (rule 9). Review first the cheaper simplifications of `notify` (single recipients field, optional `channels`, sections in the form); the presets only if those are not enough.

## Per-channel targets in notify (maintainer, 2026-11-05)
- `to` (one target per channel) is hidden from the action form and the docs (D-185); the schema still accepts it for Test send, tests and stored messages. Pick it up later. Scenarios that need it: a banner open to everyone on a hallway tablet while only some people get the push; a popup for the household and a push for the owner; mail for someone without the app while the others get push and banner; speech to speaker groups or areas (`speakers` is a speaker picker). Many of these can also be solved by policies (Away, Fallback, Escalation). Options: show `to` again behind advanced mode (the `advanced` flag of `services.yaml` is not verified), or let the shared fields apply to push, popup and mail only, with the banner open unless named.

## Review of a production migration (maintainer, 2026-11-09)
- `last_to_leave` is empty for `presence_debounce_seconds` after the last person leaves, because the tracker still counts them as home. A "person left" automation that calls the audience at once reaches nobody. Idea: count a person whose state is already `not_home` and whose departure is pending. Not planned yet.
- `condition` takes one entity or one template. Several entities with all or any are open; a template does it today.
- Idea: a notice at the first start after an update from 0.4.0 or earlier that lists the removed `wait_for_condition` and the required `severity` of `notify`. Today the Repairs issue `wait_for_condition_removed` appears on first use of the old field (D-192). The log of last actions and the recent messages are still memory only (D-194).

