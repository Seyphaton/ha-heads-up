# Open questions

## Before Phase 2
- Domain `heads_up` collision: web search found none (N-22); HACS default list not checked yet; do before the first release.
- Sections view (N-14): does a card that renders nothing leave a visible grid gap? If yes, document a visibility condition on the count sensor as workaround.
- Person `user_id` resolution when a person entity changes or is removed while banners target it.

## Phase 4 spikes
- `hass-action` event for tap actions.
- WebSocket re-subscribe after reconnect.

## Deferred ideas (out of MVP scope)
- Popup/modal for critical banners (D-018).
- Event-based banner creation; mirroring persistent notifications as banners (D-022).
- Template and full HA condition syntax for `condition` (D-005).
- Absolute `expires_at` input (D-024).
- Per-severity binary sensors (D-013).
- Other channels under the Heads Up name: toasts, popups (D-004).
