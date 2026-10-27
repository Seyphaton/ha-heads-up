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
- mypy and the dev HA were not run on 2026.10.

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
- Phase 15 candidate (design only): notification hub. Named recipient groups (people and their devices) mapped to severity levels by a routing table, so devices change without touching rules. Delivery to the Companion app per group (tag to replace and clear, Android channel, iOS interruption level, action buttons). Popups as a further channel, optional per dashboard or global; any resource loaded on every page must be minimal. Needs a new decision on the non-goal "no push delivery" (§1).
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

