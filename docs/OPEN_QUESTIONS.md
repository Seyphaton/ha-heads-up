# Open questions

## Card follow-ups (found in Phase 4)
- Not checked: `show_all` with a banner targeted at another person, keyboard activation (Enter, Space) of a tappable banner, screen readers, swipe to dismiss on a real touch screen (R-10), the compact layout on a phone-width viewport, and the card editor inside HA's own card dialog (only as a floating element).
- Contrast of custom `colors` is not checked by the card (D-048); a contrast hint in the editor is an idea, not planned.
- `clear_all` always dismisses without a confirmation (D-048). A `confirm_clear_all` option is an idea for shared wall displays.
- N-14 was checked on one layout (one grid section, 1280×800). Other column counts are not compared.

## Before the first release
- Domain `heads_up` collision: no hit in the HACS default list or in core (N-48); an unlisted custom repository with the same domain cannot be excluded.
- The README has seven screenshots; a GIF of a banner disappearing is not made. The HACS install steps in the README follow the HACS custom repository page; the download step after "Add" is unchecked until the repository is public.
- `main` is pushed to a private repository. Making it public, the first tag and the GitHub release need the maintainer's approval (D-020).
- The CI jobs, including `python-ha-2026-10`, start with the first push; their results are not read yet.
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
