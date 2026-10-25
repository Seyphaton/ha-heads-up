# Open questions

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
