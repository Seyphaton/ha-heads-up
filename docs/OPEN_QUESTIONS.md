# Open questions

## Card follow-ups (found in Phase 4)
- N-42: after a container restart the first dashboard load showed "Custom element doesn't exist: heads-up-card" once, although the module returned 200. Not reproduced. Possible cause: the module executed after the dashboard asked for the element. Needs a repeat test with a slow restart; if it recurs, the troubleshooting page (Phase 6) needs an entry or the card needs another loading path.
- Not checked in the browser: `show_all` with a banner targeted at another person, the editor's visual appearance, keyboard activation (Enter, Space) of a tappable banner, screen readers.
- N-14 was checked on one layout (one grid section, 1280×800). Other column counts are not compared.

## Before the first release
- Domain `heads_up` collision: web search found none (N-22); HACS default list not checked yet.
- Corrupt storage file behaviour (DESIGN §10): untested.
- Publishing the repo needs the maintainer's approval (D-020).

## Resolved
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
