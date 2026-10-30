# Hub test plan

How the hub is tested across packages. Each package brief lists its own tests; this file is the matrix that keeps them consistent. Tests come first for behavior changes (`.claude/rules/tests.md`): time with the freezer, never sleep; assert error codes and translation keys, not message text.

## Fakes (H0a)
- Fake `notify.mobile_app_<slug>` services with recorded calls (N-70).
- Fake `mobile_app` registration with its tracker entity and a person (N-71), including the user id.
- Fake `tts`, `media_player` (with and without the announce feature), `assist_satellite` and persistent notification services.
- A helper that fires `mobile_app_notification_action` with a given action, tag and `context.user_id`.
- Helpers for person states (`home`, `not_home`, a zone, `None`, `unavailable`) and time.
- The dev instance gets stub services (decided in H0a); no real device is ever needed.

## Matrix: message events by channel and source
Rows: created, updated, waiting then visible, severity changed, condition false, condition true again, expired, evicted, cleared (action, admin, clear all), dismissed (user, global), snoozed (user, global), snooze ended, unsnoozed, acknowledged, button pressed, startup, reload, restart while held, restart while an escalation is due.
Columns: banner, push, popup, speak, persistent, ledger row, escalation and reminder timers, trace entry.
Every cell is tested for two sources: a message from `notify` and a message from a watch rule (rule messages reach other channels only through policies).

## Matrix: targets
- Each channel with an audience, with direct recipients, and with an invalid kind (validation error with the list of valid names).
- Empty audiences, unknown presence, a person without a device, a device whose service is missing, a group with no members.
- Audience or recipients both given (error); neither given for push, popup, speak (error).

## Matrix: policies
- Each type alone, then in combination in the precedence order Summarize, Quiet hours, Away, Fallback.
- Matching by severity and tag; empty lists; `policy` named, omitted and `none`; duplicates refused; rule messages (tag `rule`).
- Escalation chain of two; Reminder limits; acknowledgement stopping both; dismiss counting or not; severity change restart; snooze pause and resume.
- Quiet hours across midnight and a daylight saving change; Away leave and return; Fallback triggers without loops; Summarize collection, cut at 10, resolved marking, highest severity, lifetime of 24 hours.

## Restart and storage
- Banner store and deliveries store: normal, corrupt entries skipped, migration hook, downgrade note.
- Stale pushes and persistent entries cleared; nothing sent twice; overdue steps fire once; held deliveries released once.

## Frontend
- vitest for pure functions (card, popup, panel formatters, target normalization, sentences, needs-attention checks, YAML generator).
- Loader byte budget under 1 KB; registration and removal like `tests/test_frontend.py`.
- Panel in the browser pane against the dev instance: admin and non-admin, phone width, keyboard, dark theme, German, French and Spanish.

## Gates
`make check`, `make hassfest`, `make dev-smoke`; the suite on Home Assistant 2026.9.4 and 2026.10 at H10; docs-check validates every YAML example against the real schemas.

## Real devices
Not available to the build sessions. A list of checks for the maintainer goes to `docs/OPEN_QUESTIONS.md` as unverified: push on iOS and Android (tag replace and clear, interruption levels, buttons), speech on real players and satellites, popups on a wall tablet.
