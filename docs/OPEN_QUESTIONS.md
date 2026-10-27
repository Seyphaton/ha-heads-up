# Open questions

## Card follow-ups (found in Phase 4)
- Not checked: `show_all` with a banner targeted at another person, keyboard activation (Enter, Space) of a tappable banner, screen readers, swipe to dismiss on a real touch screen (R-10), the compact layout on a phone-width viewport, and the card editor inside HA's own card dialog (only as a floating element).
- Contrast of custom `colors` is not checked by the card (D-048); a contrast hint in the editor is an idea, not planned.
- `clear_all` always dismisses without a confirmation (D-048). A `confirm_clear_all` option is an idea for shared wall displays.
- N-14 was checked on one layout (one grid section, 1280×800). Other column counts are not compared.

## Before the first release
- Maintainer reported on 2026-10-26: CI is green, the repository is public, the integration runs on their own Home Assistant, and no other HACS integration uses the name "Heads Up" (checked by the maintainer; this supersedes the partial check in N-48).
- Not checked: the HACS install steps in the README after "Add" (download step) against the now public repository; the repository description, topics, issues and private vulnerability reporting settings (`docs/dev/RELEASE.md` steps 3 to 5).
- The README has seven screenshots; a GIF of a banner disappearing is not made.
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
