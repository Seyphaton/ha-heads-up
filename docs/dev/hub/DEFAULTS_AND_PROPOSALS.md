# Hub values: decided, proposed, open

Every concrete value the hub design uses, and whether the maintainer decided it. A build session asks about every "proposed" and "open" item with AskUserQuestion before it relies on it, and records the answer in `docs/DECISIONS.md`.

## Decided
- The hub is built (D-107). `hub_enabled` defaults to true with an off switch; the panel sidebar entry is not registered by default and is enabled by the user during initial setup (D-107). All work stays on feature branches until the maintainer confirms.
- Severities: success, info, warning, critical (existing).
- Push levels by severity: success and info passive, warning normal, critical time-sensitive; iOS critical only as an opt-in (D-090).
- Popup style: corner card up to warning, centered modal for critical (D-090).
- Speech text when `tts_message` is missing: the title if set, else the message, shortened to a length limit (D-090). The length limit is open.
- Speech: announce when the player supports it, else current volume; the hub never changes or restores volume; no all-clear (D-091).
- Popup recipients: persons only in the first version (D-091).
- Snooze on push: one button using the first snooze option of the message (D-092).
- Push button id: `hu:<message>:<recipient>:<action>` (D-092).
- Push tag: `hu-<install token>-<message id>`; install token prevents collisions between several Home Assistant servers (D-080, N-62).
- Swiping a push away changes nothing (D-081).
- Acknowledgement: any recipient stops escalation and reminders; dismissing counts as acknowledging only when the escalation policy says so (D-081, D-097).
- Snooze: clears the user's push, pauses their reminders, notifies again when it ends (D-078).
- Severity change on an active message: escalation and reminders restart with the policies of the new severity (D-081).
- After a restart: an overdue escalation or reminder fires once if the message is active and unacknowledged (D-081).
- Presence: unknown presence notifies for critical and skips lower severities with a trace entry; person state `None`, `unknown`, `unavailable` all count as unknown (D-080, N-63).
- Summary: highest severity of its messages; channels and targets of the held messages, one per recipient and channel; stays until dismissed or 24 hours; lists a count and titles, marks resolved ones, cuts at 10 with "and N more"; sends nothing when nothing was collected (D-097, D-106).
- Summarized messages are held on every channel including the banner (D-105); critical may be summarized only if the policy includes it (D-097).
- Precedence: Summarize, Quiet hours, Away, Fallback; the summary and later deliveries pass through the same chain (D-106).
- Policies: identical type, applies to and trigger are refused; the most specific policy wins by tag, then severity (D-079, D-097).
- No default delivery by severity; calls always name channels (D-106).
- Watch rules frozen (D-100). No named conditions, no "only if" (D-099).
- Built-in audiences: Everyone, Admins, At home, Not home, Last to leave, First home (D-080, D-088). Custom audiences: persons, or a presence kind including in and not in a zone (D-080).
- Wizard exists as a panel window and as a config flow entry; presets Quiet, Balanced, Loud (names decided in D-093; contents proposed).

## Proposed (used in the mockup, not decided)
- Install token: 6 hexadecimal characters, generated at first setup, shown read-only.
- Rate limits in the options: 10 pushes per device per minute, 60 deliveries per minute for all devices, identical updates ignored for 30 seconds.
- History: 500 trace entries, 100 recent messages.
- Escalation default 5 minutes; reminder default every 30 minutes, at most 3; summary default every 60 minutes or at 20:00; quiet hours default 22:00 to 07:00, all days, critical passes, action quiet.
- Android channel id default `heads_up`; push default lock-screen text full; push buttons Snooze and Dismiss.
- Preset contents: Quiet creates Night quiet; Balanced creates Night quiet, Water escalation, Evening summary; Loud adds Warning reminders and Push failed fallback.
- Debounce of presence changes (60 seconds) for Last to leave and First home.
- Send test uses a test marker in the message (exact form open).
- Panel sidebar title and icon.
- Banner line "Acknowledged by <first name>": when several people acknowledged, show the first only (open).

## Open (need a maintainer answer or a check before the work package that needs them)
- Build phasing and order (this roadmap is a proposal until approved).
- The speech length limit.
- Whether the recent-messages list survives a restart (relates to the history idea, Phase 13 candidate).
- The unit name in public docs ("message") while the actions keep their names.
- Card option name that hides the "Acknowledged by" line.
- Popup area recipients (not built).
- A "watch an entity" blueprint and whether an integration can ship blueprints (N-73).
- Deprecation of watch rules later (D-100).
- Volume restore per speaker platform (N-66); the custom panel web component contract and manifest listing (N-69); whether the app sends action presses through the fire_event webhook (N-72); everything on a real device and on a dev instance with a fake `mobile_app` registration.
