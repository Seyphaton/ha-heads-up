# H3: Push channel (Companion app)

Size: large. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Deliver messages as Companion app notifications through the legacy `notify.mobile_app_*` services, keep them in sync with the message lifecycle, and handle Dismiss, Snooze and Acknowledge presses without any automation.

## Dependencies and parallel work
- Needs: H1, H2
- Can run at the same time as: H4a, H5, H6, H7 (all after H2 where they need the resolver)
- Files this package owns (create): `hub/channels/push.py`, `tests/hub/test_push_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `hub/engine.py` (registration only), `strings.json`, `translations/*.json`, `manifest.json` (`after_dependencies` for `mobile_app` and `notify`, N-68), `docs/limitations.md`, `docs/actions.md`

## Scope
- Use the legacy services only: the notify entity forwards no `data` (N-61, N-74). Service name per N-70.
- Payload: `title`, `message`, `data.tag` = `hu-<install token>-<message id>` (one tag per message so devices replace instead of stacking), `data.group`, Android `channel` and `importance`, iOS `push.interruption-level`, `sticky`, `actions`, `clickAction` from the message's `tap_action` (N-62).
- Levels by severity from the Channels settings (defaults: success and info passive, warning normal, critical time-sensitive); iOS critical only as an opt-in; for iOS critical an update is clear then send because critical cannot be replaced. Lock-screen text by setting: full, title only, generic.
- Buttons: the message's own `actions` first, then Dismiss and Snooze when the message allows them, and Acknowledge when an escalation or reminder policy applies (the policy hook from H4a; until then a flag in the delivery context). Limit 3 on Android, about 10 on iOS; clip with a trace note. Ids `hu:<message>:<recipient>:<action>`. Snooze uses the first snooze option of the message.
- Action events: listen to `mobile_app_notification_action`; ignore unknown or stale ids with a trace entry; attribute the press to the recipient in the id (the event's `context.user_id` may be used as a cross-check, N-72); map to the existing manager methods `dismiss`, `snooze`, `press` and acknowledge.
- Lifecycle: update replaces in place by tag; hide (cleared, expired, condition false, dismissed or snoozed by that user) sends `message: clear_notification` with the tag (iOS app 2021.5 or later); a snooze clears the user's push and a new push is sent when it ends. Swiping a push away changes nothing.
- Devices: all devices of a person under one tag; accepted channels respected; a person with no usable device is skipped with a trace entry (the failure counts as 'failed' for the Fallback policy).
- Failures: an unavailable service gives a `failed` delivery with a reason, one log warning per device per hour, no retry in the first version; never blocks the message.
- Quiet-hours downgrade hook: when the engine marks a delivery as quiet, send passive without sound. Rate limit hook points are added here and enforced in H10.

## Out of scope
Policies (H4); the panel (H9); rate limit enforcement (H10); iOS critical entitlement handling beyond the opt-in.

## Tests
Payload exactness per severity and setting; tag and group; buttons and the platform limits; press round trip with the fake event helper (valid, stale, unknown, wrong recipient); clear on every hide reason; snooze and remind; all devices of a person; no device; failing service; hub off; restart (no re-send, stale push cleared). Real device checks are listed as unverified in OPEN_QUESTIONS.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md` (push fields and behavior), `docs/limitations.md` (the 'does not send push' line is no longer true; change it to what is built), `docs/troubleshooting.md` (a push that did not arrive), CHANGELOG, HA_API_NOTES, STATE.

## Parity (CLAUDE.md rule 9)
Rule messages reach push only through policies (escalation, fallback) by severity and tag; `notify` messages can name push directly.

## Blast radius (rule 5)
Restart: the usual one. Notification path: touched for the first time (calls to `notify.mobile_app_*` of another integration, nothing of theirs is modified). Dashboard: unchanged. Manifest: optional `after_dependencies`.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Whether the app's action presses carry the user (N-72, from H0b); push defaults that are still proposed. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-61, N-62, N-70, N-72 (with a fake device); a real device check by the maintainer is separate. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Push delivery, clear, buttons and press handling built and tested with fakes; docs fixed; `make check`, `make hassfest`, `make dev-smoke` (with stubs) green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
