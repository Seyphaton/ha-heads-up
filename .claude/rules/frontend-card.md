---
paths:
  - "custom_components/heads_up/frontend/**"
---

# Card (`custom:heads-up-card`)

- One plain-JS ES module, no build step, no npm runtime dependencies (D-021).
- Colors only from HA theme variables (`--info-color`, `--success-color`, `--warning-color`, `--error-color`, `--primary-text-color`, `--card-background-color`). No hard-coded colors.
- Severity is never color-only: icon + text label. Dismiss button ≥ 48×48 px with translated `aria-label`.
- UI strings in an `en`/`de` table keyed by `hass.locale.language`; banner text is never translated.
- Data only via WebSocket `heads_up/subscribe`; unsubscribe in `disconnectedCallback`.
- Pure logic (sort, filter, control visibility) in exported functions so vitest can test them without a DOM.
- Card API facts: HA_API_NOTES N-12, N-13. Unverified items (N-14, `hass-action`, re-subscribe) must be checked in the dev HA before code depends on them.
