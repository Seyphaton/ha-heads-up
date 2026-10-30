# Notification hub: consolidated plan

Status: proposal on branch `design/notification-hub`, 2026-10-29. No code. Not approved for build; whether the hub is built is open (D-075). This is the readable summary. The design is `docs/DESIGN.md` §23, the decisions are D-075 to D-095 in `docs/DECISIONS.md`, the full planning record is `docs/dev/HUB_DESIGN.md`.

## 1. What it is
Today's implementation sets the foundation for how notifications (right now: banners) are delivered. The hub expands this idea to more channels and additional features.

- A producer (an automation or a watch rule) creates a message.
- A policy decides who is told, on which channels, and what happens if nobody reacts.
- The banner on the dashboard is one channel among five.
- Everything that exists today keeps working without the hub: `create_banner`, `clear_banner`, `clear_all`, watch rules, the card.

## 2. The problem it solves (README material)
- Automations hard-code notify services, speaker entities, quiet-hour templates and clean-up logic.
- Replacing a phone means editing every automation.
- A leak alert at night, a doorbell with nobody home, a critical alert nobody read.
- A push dismissed on one device is still shown on the wall tablet and spoken again.

## 3. Building blocks
- Message: the unit a producer creates. It has one id for all channels and owns the lifecycle (timeout, condition, dismiss, snooze, acknowledgement).
- Channel: banner, push (Companion app), popup, speak, persistent notification.
- Audience: people-based and channel-neutral. Persons, or a presence kind. Built in: Everyone, Admins, At home, Not home, Last to leave, First home.
- Recipient group: a named set of explicit targets (speakers, Assist satellites, areas, notify targets).
- Recipient profile: per person, the detected devices, manual overrides, primary device and accepted channels.
- Policy: one small typed rule with a trigger and an effect (D-097). Types: Escalation, Quiet hours, Fallback, Reminder, Away, Summarize. Each can apply to severities and tags. There are no named conditions in the first version (D-099).
- Channel settings: one page with defaults by severity (push level, lock-screen text, buttons, popup style, speech language).

## 4. How a producer calls it
- `heads_up.notify`: content (message, title, icon, severity, buttons, tap action, tts_message), lifecycle (id, tag, timeout, condition, mode, dismiss and snooze fields), delivery (channels, `to` with a target per channel, policy). One call can send push, speech and persistent notification together (D-098).
- Shortcuts `push`, `popup`, `speak`: one channel, optional audience or recipients, fire and forget unless an id is given.
- `create_banner`: unchanged.
- One generic clear removes a message from every channel.
- Watch rules are frozen (D-100): they keep working as released and show on the banner channel; policies still apply to their messages by severity and tag.

## 5. Who gets what, per channel
- banner: audience, or persons; empty means everyone.
- push: audience, or persons and notify targets.
- popup: audience, or persons (persons only in the first version).
- speak: recipients only (groups, media players, satellites, areas).
- persistent notification: no recipients, it targets everyone.

## 6. What happens over time
- The call's channels and audience go out at once. All policies that apply are active together: escalations and reminders run from the message start, quiet hours, away and fallback act on every delivery, summarize collects messages into one summary.
- Any recipient acknowledging stops escalation. Whether a dismissal counts is a policy setting.
- Snooze clears the user's push, pauses their repeats and notifies again when it ends.
- A fallback policy applies when the audience is empty or sending failed.
- If the lifecycle condition ends the message, every channel is cleared and its policies stop.
- A severity change restarts the timeline with the policy of the new severity.
- After a restart an overdue step fires once if the message is still active and unacknowledged.

## 7. Channel behavior
- push: legacy notify services only. Passive for success and info, normal for warning, time-sensitive for critical. Buttons: the message's own, then Dismiss and Snooze, and Acknowledge when an escalation or reminder policy applies. Swiping a push away changes nothing.
- popup: tiny global loader, lazy popup code. Corner card up to warning, centered modal for critical.
- speak: announce when the player supports it, else the current volume. No volume changes, no all-clear.
- persistent notification: create and dismiss by message id.
- banner: unchanged, plus "Acknowledged by <first name>" with a card option to hide it.
- Rate limits: caps per device and global, and duplicate suppression, defaults in the options.

## 8. Admin experience
- Admin-only sidebar panel with own forms; storage stays in config subentries.
- First version: overview and editors, live preview (who would be notified now), per-message delivery trace, recent messages, test send (the preview and the test send are one tab, D-101).
- First-run wizard as a panel stepper and as a config flow entry. Presets: Quiet, Balanced, Loud.
- A standalone mockup of the panel is in `docs/dev/mockups/hub-panel-mockup.html` (not part of the integration). Navigation in two levels (D-102): Overview (Status); Activity (Test send, Messages); Configuration (Audiences, Recipients, Policies, Channels, Watch rules as a read-only list); Settings (General, Setup wizard); FAQ and Examples. All data in it is sample data and nothing is saved.

## 9. Build phasing (draft, delayed until the design is final)
- 15a: core push, audiences and one-step policies, delivery store, trace, test send.
- 15b: presence audiences, quiet hours, deliver on arrival, snooze with remind.
- 15c: acknowledgement, escalation and reminder policies, push buttons.
- 15d: popup.
- 15e: speak.
- 15f: persistent notification and the admin panel.
- Each phase ships for action messages and rule messages alike, with tests, docs, translations, `make check`, `make hassfest` and `make dev-smoke`.

## 10. Blast radius
- Restart: the usual one after a code update.
- Notification path: touched for the first time (calls to notify, tts, media player and persistent notification services; nothing of theirs is modified).
- Dashboard: nothing changes until a policy or channels are used.
- Storage: new subentry types and a deliveries store; a downgrade needs a check for unknown subentry types.

## 11. Still open
- Hub status (build or not) and the amendment of the "no push delivery" non-goal in DESIGN §1.
- Build phasing.
- Home Assistant facts not verified: the person to Companion device path, the user in the push action event, announce and volume behavior per platform, the custom panel component contract and manifest listing, everything on 2026.10.
- Whether the recent-messages list survives a restart.
- The unit name in public docs (the action stays `notify`).
- Popup area recipients (not built).
