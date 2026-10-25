# Open questions

## Card design follow-ups (requested 2026-10-25, not approved, no code yet)
Each item needs the maintainer's decision before work starts. Docs, `CONFIG_KEYS`, the editor schema, `normalizeConfig` and tests change together (`.claude/rules/frontend-card.md`).
1. `layout: compact` is too close to `comfortable`. Wanted: compact shows each banner on one line (icon, optional time, title and message on a single truncated line, dismiss button). Open: what happens to a long message (ellipsis, tooltip, tap to expand); whether the 48 px touch target stays.
2. Option to show when a banner was triggered, as relative text ("just now", "50 min ago", "1 day ago"). Decided (D-047): use `updated_at`. Open: the text needs a timer so it stays current without a new event; format thresholds; English only (D-037), kept in `STRINGS`. Both timestamps are already in the `heads_up/subscribe` payload.
3. Option for a card title (a header above the banners). Open: key name (`title` is also a banner field, so the card option may need a different name such as `header`); whether the header shows when the card is empty and `show_empty: false`.
4. Option to hide the severity label ("Info", "Success", ...), named "Show severity". Wanted default: off. Conflict: `.claude/rules/frontend-card.md` and DESIGN §3 require that severity is never color only. Today the card shows icon plus label. Decided (D-047): option `show_severity`, default `false`; "off" hides only the text label, icon and color stay. This changes today's default (label shown), so it needs a changelog entry and an update of the rule and DESIGN §3.
5. Option to change the severity colors. Conflict: the card rule allows only HA theme variables. Open: per-severity color keys (CSS color or theme variable name), whether `critical`/`warning` keep a contrast check against the card background in light and dark, and how the editor offers it.
6. Optional "Clear all" button on the card. Open: what it does. Dismissing every visible banner for the viewer needs one `heads_up/dismiss` per banner or a new WebSocket command; it cannot touch banners with `dismissible: false`. `heads_up.clear_all` removes banners for everyone and stays an action or the admin button. A confirmation step; the option name and default (off).
7. Swipe to dismiss (as on phones). Looks possible with pointer events in plain JavaScript, not tried. Open: it must not fight vertical scrolling of the dashboard (`touch-action`); non-dismissible banners do not swipe; the dismiss button and keyboard path stay; direction (left, right or both) and whether `dismiss_scope: global` banners need a confirmation because the swipe removes them for everyone.
8. Show only X banners and a "Show more" button for the rest. `max_items` already caps the list and has no way to expand. Open: a new option or a change of `max_items`; label with the hidden count ("Show 3 more"); expanded state lives in the open page only and resets on reload; "Show less" after expanding.
9. Customizable "All clear" message when no banner is left, like the reference screenshot (bell-check icon plus "All clear — no notifications" in the middle of the card, dark theme). Today an empty card is hidden (`show_empty: false`, D-040) or shows nothing (`show_empty: true`). Open: option names for the text (and icon), whether setting a message implies showing the card, default text and default off or on, and that the text is caller-written so it is not translated (D-037). Check the sections-view gap (N-14) again when the card stays visible.

## Card follow-ups (found in Phase 4)
- Not checked in the browser: `show_all` with a banner targeted at another person, the editor's visual appearance, keyboard activation (Enter, Space) of a tappable banner, screen readers.
- N-14 was checked on one layout (one grid section, 1280×800). Other column counts are not compared.

## Before the first release
- Domain `heads_up` collision: no hit in the HACS default list or in core (N-48); an unlisted custom repository with the same domain cannot be excluded.
- README screenshots (light, dark, GIF of a banner disappearing) are missing; they must come from the dev HA (D-046).
- HACS install steps for the README, once the repository is public.
- Publishing the repo, the first tag and the GitHub release need the maintainer's approval (D-020).
- The CI jobs, including `python-ha-2026-10`, have never run.
- mypy and the dev HA were not run on 2026.10.

## Resolved
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
