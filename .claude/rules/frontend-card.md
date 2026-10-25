---
paths:
  - "custom_components/heads_up/frontend/**"
---

# Card (`custom:heads-up-card`)

- One plain-JS ES module, no build step, no npm runtime dependencies (D-021).
- Colors only from HA theme variables (`--info-color`, `--success-color`, `--warning-color`, `--error-color`, `--primary-text-color`, `--card-background-color`). No hard-coded colors.
- Severity is never color-only: icon + text label. Dismiss button ≥ 48×48 px with translated `aria-label`.
- UI strings in English, kept in one `STRINGS` table so other languages can be added later (D-037); banner text is never translated.
- Data only via WebSocket `heads_up/subscribe`; unsubscribe in `disconnectedCallback`.
- Pure logic (sort, filter, control visibility) in exported functions so vitest can test them without a DOM.
- Card API facts: HA_API_NOTES N-12, N-13, N-14, N-38 to N-40. Subscribe with `resubscribe: false` and handle `ready` and retries yourself (D-041).
- Banner text only via `textContent`, never `innerHTML`.
- A new config key goes into `CONFIG_KEYS`, the editor schema, `normalizeConfig`, `docs/card.md` and a test; `make docs-check` compares `CONFIG_KEYS` with the docs.
