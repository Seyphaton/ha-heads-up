# Open questions

## Phase 4 spikes (see `docs/dev/STATE.md`)
- Sections view (N-14): does a card that renders nothing leave a visible grid gap? If yes, document a visibility condition on the count sensor as workaround.
- `hass-action` event for tap actions, including `confirmation`.
- WebSocket re-subscribe after reconnect.

## Before the first release
- Domain `heads_up` collision: web search found none (N-22); HACS default list not checked yet.
- Corrupt storage file behaviour (DESIGN §10): untested.
- Publishing the repo needs the maintainer's approval (D-020).

## Resolved
- Person `user_id` changes while banners target it: re-filtered on every change of a referenced person's `user_id`; a removed person matches nobody (Phase 3, `tests/test_people.py`).

## Deferred ideas (out of MVP scope)
- Popup/modal for critical banners (D-018).
- Event-based banner creation; mirroring persistent notifications as banners (D-022).
- Template and full HA condition syntax for `condition` (D-005).
- Absolute `expires_at` input (D-024).
- Per-severity binary sensors (D-013).
- Other channels under the Heads Up name: toasts, popups (D-004).
