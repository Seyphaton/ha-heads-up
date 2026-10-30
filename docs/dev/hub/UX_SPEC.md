# Hub panel: UI specification

Source: the mockup `docs/dev/mockups/hub-panel-mockup.html` (open it in a browser; it simulates the behavior below with sample data) and decisions D-093, D-097 to D-106. The mockup is the visual reference; this file is the written specification a build session works from. Where the mockup simulates something (time, presence, data), the real panel reads real state.

## General rules
- Admin-only sidebar panel, registered with `panel_custom` (N-69). `require_admin` only hides the sidebar entry; every WebSocket command of the panel checks admin itself.
- One plain JavaScript module, no build step (D-021). Forms use Home Assistant's `ha-form` selectors where possible. Colors only from theme variables. Touch targets at least 40 px. Light and dark themes.
- Storage stays in config subentries (audiences, recipient groups, recipient profiles, policies) and the integration options; the panel keeps no store of its own. Saving goes through Home Assistant's subentry flow APIs, so the native dialogs keep working.
- Every panel string exists in English, German, French and Spanish with the same keys and placeholders (existing parity test).
- Every list row and every error message names the object and the field; every error offers a link to the page that fixes it.
- A form shows "valid" or the list of problems before Save is enabled; Save is disabled while there are problems.
- Navigation has two levels (D-103). A group with one page shows no second row.

## Navigation
- Overview: Status
- Notifications and Rules: Test send, Watch rules, Messages
- Configuration: Audiences, Recipients, Policies, Channels
- Settings: General (one page)
- FAQ and Examples
- The setup wizard is a window opened by a button, not a page.

## Overview (Status)
A dashboard page, nothing editable.
- Tile "Active notifications": the number of messages that are active now, with a badge per state: escalating (an escalation policy is waiting or has fired and nobody acknowledged), reminding, snoozed, in a summary (held for a Summarize policy). Click or double-click opens a list: message title, severity, state with a one-line explanation (for example "Escalation ongoing: Water escalation sends push and speech in 3 min unless acknowledged"). A single click opens the list too, because double-click is awkward on touch screens.
- Tile "Watch rules": "N of M active" (enabled out of all), a badge for disabled rules and a badge for rules showing a message now. Click or double-click opens the rule list with state and condition.
- "Needs attention": configuration errors and warnings, each with a link to the page that fixes it. Items:
  - a watch rule whose entity is unavailable (error)
  - a device whose notify service was not found in Home Assistant (error)
  - a person with no usable device: push is skipped (warning)
  - a recipient group without members (error)
  - an invalid policy, with the reason (error)
  - a policy that names an audience that no longer exists (error)
  - no escalation policy covers critical messages (warning)
  - the hub is switched off (warning)
  - "Nothing needs attention" when the list is empty
- "Last actions": a log of the latest events, newest first, time and one line. Kinds: created (with severity and channels), escalation sent, reminder sent, acknowledged (by whom), dismissed, snoozed, unsnoozed, summary sent, delivery skipped (reason), delivery failed (reason), expired, cleared. A button opens all messages (Messages page). How many entries and how long they are kept is set in Settings (History).
- A short line offers the setup wizard on first run.

## Notifications and Rules
### Test send
One page that previews and tests a notification (D-101). There is no compose form for real notifications.
- Content: title (optional), message, spoken text (optional, speech only).
- The call: severity, tag (none or a tag), channels (chips: banner, push, popup, speak, persistent), policy ("all that apply", "none", or one policy by name).
- "Who, per channel": one block per selected channel, each with Audience and Direct recipients buttons, a select, a one-line explanation of the selected option including who it is right now for audiences, and a note about what the channel accepts. Speak has no audience button. Persistent notification shows only "No target: it goes to everyone". Choices follow the matrix of DESIGN 23.5 (push also lists phones; speak lists groups and speakers).
- Simulate the house (mockup only): time of day (day or night with quiet hours) and a presence toggle per person. The real page reads the clock and real presence and may offer a "what if" time later.
- Result: a table with one row per recipient and channel: recipient, channel, result (sent, shown, held, skipped, dropped), reason. A response summary line ("push: 2 sent, 1 skipped") and the policies that applied. A "Later steps" list shows escalations, reminders, summaries and away rules that apply with their timing.
- "The call": the generated `heads_up.notify` YAML to copy into an automation, a Copy call button, and a Send test button. Send test is the only real send of the panel; it sends the message with a test marker (exact marker to be decided in the build).
- Rules the result follows: precedence Summarize, Quiet hours, Away, Fallback (D-106); critical passes quiet hours when the policy says so; a summarized message is held on every channel including the banner (D-105); fallback rows are prefixed with the fallback policy name.

### Watch rules
A read-only list (D-100): name, state (disabled, enabled, showing), condition, message, severity, and the policies that apply to the rule's message. A note explains that rules are edited in Home Assistant under Devices and services, Heads Up. Rule messages have the tag `rule`, so only policies without a tag restriction or with the tag `rule` apply by tag.

### Messages
The recent messages (title, severity, outcome) and the delivery trace of the selected message: time, recipient, channel, result with reason, acknowledgements, escalation due times. Backed by the delivery store and the trace buffer. Whether the list survives a restart is open.

## Configuration
### Audiences
- List: name, kind (built in, persons, presence), who is in it right now, Edit for custom ones.
- Built in and read-only: Everyone, Admins (persons whose user is an admin), At home, Not home, Last to leave, First home.
- Editor for a custom audience: name; kind Persons (chips of persons) or Presence (at home, not home, last to leave, first home, in a zone, not in a zone; a zone select for the zone kinds); the members right now; the policies that use it; Save; Delete (disabled while a policy uses it). Problems: name required, name unique, at least one person.
- Membership is checked once when a delivery is made (snapshot). Unknown presence (`None`, `unknown`, `unavailable`) counts as unknown: critical notifies anyway, lower severities skip with a trace entry.

### Recipients
- Recipient profiles, one per person: devices with a badge detected or manual and a badge "service not found" when the notify service is missing; a primary device (radio); remove a device; add a device by name; accepted channels (banner, push, popup). A person with no device shows a warning "skipped on push".
- Recipient groups: name, members chosen from speakers, satellites and areas, a note with the member count and how the group is named in calls ("<name> (group)"). New and delete.
- Devices of a person are found automatically (person trackers to the `mobile_app` registration, N-70, N-71) with manual add and remove.

### Policies
- List: name, type badge, applies to, Edit; disabled policies appear dimmed.
- Editor: name; type (Escalation, Quiet hours, Fallback, Reminder, Away, Summarize); type-specific When and Then fields; Applies to (severities as chips, none selected means any; tags comma separated, empty means any tag); Enabled.
- Escalation: nobody acknowledged within N minutes (more than 0); then also send on channels with a target per channel (same blocks as Test send); dismissing counts as acknowledging. Note: pushes of messages this policy covers get an Acknowledge button.
- Quiet hours: sent from, to, days (default all); action wait (hold until the end), quiet (passive push without sound, speech skipped, popup as corner card), drop; critical messages pass anyway (default on).
- Fallback: trigger no_audience, failed or both; then send instead on channels with a target per channel.
- Reminder: while not acknowledged, repeat every N minutes, at most M times.
- Away: when a recipient is not home, send when they arrive while the message is active.
- Summarize: every N minutes or at a time of day; include critical (default off, warning shown when on); a note that nothing is sent individually while a message waits and that the summary shows the count and titles, marks resolved ones and cuts at 10 ("and N more").
- Below the editor: a one-sentence description of the policy, the validation result, the stored YAML, Save and Delete. Refused: a second policy of the same type with identical applies to and identical trigger.

### Channels
Settings by severity (D-097):
- Push level per severity (passive, normal, time-sensitive, critical); popup style per severity (card or modal). Defaults: success and info passive and card, warning normal and card, critical time-sensitive and modal. A note on iOS critical (needs app permission, bypasses silent mode, cannot be replaced or grouped).
- Push: lock-screen text (full, title only, generic; default full), buttons Snooze and Dismiss (Acknowledge is added when an escalation or reminder policy applies), sticky, Android channel id (note: Android keeps the first importance of a channel).
- Speech: language, use announce when the player supports it (never changes or restores volume).

## Settings (General)
One page that holds everything the setup wizard sets up, plus the rest.
- Setup wizard: a button that opens the wizard window.
- Hub: enabled switch, on by default (D-107). Off means messages reach only the dashboard banner, as before the hub existed.
- Sidebar: show the Heads Up panel in the sidebar (off until the user enables it during initial setup; changeable here).
- People and devices: a summary table with a link to Configuration, Recipients.
- Loudness: Quiet, Balanced, Loud with a description and the policies each creates; an Apply preset button that adds missing policies and never deletes or changes existing ones. Presets: Quiet creates Night quiet; Balanced creates Night quiet, Water escalation, Evening summary; Loud adds Warning reminders and Push failed fallback. Preset contents are sample content to be fixed in the build.
- Limits: pushes per device per minute, deliveries per minute for all devices, seconds during which identical updates are ignored (proposed defaults 10, 60, 30; suppressed deliveries are counted in the trace).
- History: trace entries kept and recent messages kept (proposed defaults 500 and 100).
- Identity: the install token (read-only), used in push tags.
- Save.

## Setup wizard (window)
Four steps with Back and Next; the last button reads Create.
1. People: chips of persons; each chosen person gets a recipient profile.
2. Devices: the detected devices per person as checkboxes; a person without a device is told that only banner and popup work until one is added.
3. Loudness: Quiet, Balanced, Loud (radio) with description and the policies created.
4. Test: a simulated test per person ("push sent, 2 devices" or "skipped, no usable device") and the list of objects the wizard will create. Create writes the profiles and policies and tells the user where to edit them.
The wizard also exists as a config flow entry on the integration page (D-093).

## FAQ and Examples
Examples: six calls, from the simplest to the most detailed (banner only; banner and push with matching policies; push, speech and persistent together; a one-off speech call with `policy: none`; the push shortcut with a presence audience; push to one person). Eleven collapsible answers: banners without the hub; audience versus direct recipients; why speech takes no audience; push, speech and persistent in one call; what happens if nobody reacts; quiet nights; someone not home; summaries; replacing a phone; why a notification did not arrive; what happens after a restart. This text becomes user documentation (README and `docs/how-to.md`) when the features exist.

## Interaction details
- Changing a type in the policy editor keeps name, severities, tags and enabled, and resets the type-specific fields.
- Changing the channel chips in a block re-filters the target choices; a target that is no longer valid is replaced by the first valid one.
- A person, device, group or audience that is deleted disappears from every choice; policies that referenced it show up under "needs attention".
- Everything in the mockup that simulates (time, presence, the sample messages, the log, rate limits) is replaced by real data in the build.
