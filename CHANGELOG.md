# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/). Only releases are listed; the 1.0.0 pre-releases are summarized under 1.0.0, and the 2.1.0 and 3.0.0 pre-releases under 3.0.0.

## [3.0.0] - 2026-11-25

### Before you upgrade

- Nothing you need to act on. New features are optional or off by default.
- The policy form no longer has "Not for severities" and "From watch rule". The first start converts your policies so they behave as before and keeps a backup. See [Upgrading](docs/setup.md#upgrading).

### Added

- Personal inbox and messaging:
  - Each person gets their own list of messages that survives restarts, with an unread count.
  - A new inbox card shows it on a dashboard in four sizes.
  - With one switch (off by default), people write short messages to each other from the card. They choose where it goes: inbox, push, popup on screens or mail.
  - On a phone a message reads like a chat message, with the sender's name and picture.
  - The sender gets a Sent list and never learns whether a message was read.
- Richer push notifications:
  - Icon, color, subtitle and sender picture work the same on Android and iOS.
  - Banners and popups show them too, so a message looks alike on the phone and the dashboard.
  - An optional setting (off by default) gives each push the icon and color of its severity.
- Progress bars and Live Activities: a bar follows any entity on banners, popups and phones. On phones it is a Live Update (Android 16 and later) or a Live Activity (iOS 17.2 and later), updated in place, and the Overview lists running ones with a Dismiss button.
- Easier editing in the panel: Test send shows every field with a color picker and a Visual or YAML switch, the watch rule form edits buttons and the tap action, and built-in audiences can be edited, for example to leave one person out of "At home".
- Quiet hours for chosen channels: limit a quiet-hours policy to the channels you pick.

### Changed

- The speech settings and the push limits moved to the Speech and Push rows of the Channels page. Their values are kept.

### Fixed

- A Live Update or Live Activity sent only to phones could not be ended from the phone. The Overview now lists it with a Dismiss button.
- The help text of the mail subject showed an error in the action form.

## [2.0.0] - 2026-11-22

### Before you upgrade

- Make a backup before you update. The first start converts your policies, and Heads Up 1.x cannot read the converted setup. To go back, restore the backup. [Upgrading](docs/setup.md#upgrading) has the steps.
- Policies no longer run in a list order or a mode: every policy that fits a message acts. The conversion keeps what your policies did. A policy that came below another one leaves out the messages that one handled, written as Not for (for example Night quiet: Not for the tag `digest`). The Policies page lists every such policy under "The policy feature has been updated – please review the new behaviour", with Keep it like this and Apply to them too. A policy that was switched off at the update is not taken into account.
- "Critical messages pass" and "Include critical messages" are gone. Where they let critical messages through, the conversion adds the Get through entry Critical; where they held them, the policy gets Holds these anyway; a Presence policy that let them through gets Not for Critical. The policy switch attributes `critical_passes`, `include_critical` and `order` are gone; `not_severities`, `not_tags` and `rules` are new.
- Setups on "Every policy that applies runs": two reminders on the same channel now share the shorter rhythm instead of both repeating. Turn on Runs alongside on a reminder to keep its own rhythm.
- An escalation also sends to people who already have the message: they get a second push.
- A Fallback steps in only when neither the call nor a Deliver policy reached anyone.
- A summary also goes to the people a Deliver policy would have added, and a summary that reaches nobody gets a Fallback.
- A message released from a summary, because its policy was switched off or a Get through entry now fits it, runs as a new message: Deliver and Fallback act and its escalations and reminders start then.
- The severity `success` is now called `passive`. Calls and card YAML with `success` keep working: it is read as `passive`. Events, entity attributes, the message log and the panel say `passive`, so an automation or template that checks for `success` must check for `passive`. Stored messages, policies, watch rules and severity settings are converted on the first start.
- The card editor no longer shows Severity colors. A card that has `colors` in its YAML keeps them; set colors for every card on the panel's new Severities page instead.
- The Away policy is now called Presence. Your Away policies are converted on the first start and keep what they did: push, popup and mail, held until the person comes home, and dropped when the maximum wait ends. One difference: a person the call lists by name (`recipients`) is held too, where Away sent to them at once. A backup of the policies is written to `.storage/heads_up.migration_v2_2`. The policy switch attribute `type` reads `presence`.
- A held message is released 60 seconds after the person arrives (the presence delay in Settings), not at once, so a short GPS flip releases nothing. Set the presence delay to 0 for the old timing; it also changes Last to leave and First home.
- Going back to 1.0.0 after the update ignores the converted policies. Restore the backup first, as described in [Upgrading](docs/setup.md#upgrading).
- After speaking, Heads Up puts a speaker's volume back to where it was, if the message set a volume. Sonos speakers keep their volume and say the message at the chosen level. For the 1.0 behaviour, switch off "Put the volume back after speaking" under Settings, Speech volume.
- `heads_up_banner_unsnoozed` also fires when a snooze runs out, not only when someone ends it in the card. The event has a new field `reason`: `ended` or `user`. An automation that should react only to the card, as before, needs a condition on `reason: user`.

### Added

- Watch rules can name an audience: the banner shows to the members of the audience at the moment it appears.
- Banner watch rules has its own tab, with a table and the form in a window like the Policies page. Test send and the Message Log are under Test & Logs.
- Policies page in three tables: Keep it calm (Summarize, Quiet hours, Presence), Always gets through and Make sure it arrives (Deliver, Escalation, Reminder, Fallback), plus Only when named. Each row says in words what the policy does and opens its switch ID, Edit and Switch off.
- Get through entries: say which messages may wake whom despite quiet hours and summaries, for everyone a message reaches or only some people and speakers. Presence is never passed.
- Not for severities and Not for tags, and From watch rule, on every policy.
- Only if on every policy: it acts only while a condition holds, in the shape of the `notify` condition. Guests: a Presence policy with Only if "guest mode is off".
- Reminders: Faster while repeats at a shorter time while a condition holds; Runs alongside keeps a reminder's own rhythm.
- Test policies on the Policies page: plays a message through your policies at a chosen time and with chosen people at home, and lists per person what happens and why, with the escalations and reminders of the next 24 hours. Nothing is sent.
- How policies work together, in a window from the Policies page and under Help: each type of policy against every other one, with an example.
- The Message Log names the policy that held, dropped or quieted a delivery. Needs attention warns when an escalation can be caught by quiet hours or Presence, when it was, and when two Presence policies contradict each other.
- The introduction offers one list without a choice of mode; Critical messages adds the Get through entry Critical.
- New setups get other default push levels: critical `critical` (an alarm that sounds in silent mode), warning `time-sensitive`, info `normal`, passive `passive`. An existing setup keeps the levels it had; change them on the Severities page.
- Audiences page: a table with who is in each audience now and how many messages were sent to it and when last, kept across restarts. An audience's details list its policies and link to the Message Log filtered to the messages sent to it.
- The Channels, Audiences, Recipients and Severities pages show one row per item with the current settings, and open an item's fields under its row. The Configuration group starts with Channels.
- Severities page in the panel: a label, an icon and a color for each severity, used by the card, the popup, mail and the panel, and the push level and popup style of each severity. YAML and events keep the names passive, info, warning and critical.
- Presence policy: hold or drop by where people are, for any zone. "Hold until the recipient leaves" and "drop while they are in the zone" for push, popup and mail; "nobody or somebody of an audience is in the zone" for speech; send or drop when the maximum wait ends.
- A recipient profile can say where the person is from an input boolean or binary sensor, per zone, instead of Home Assistant's location. Zones without one keep the person's state. The presence audiences and the Presence policy follow it.
- Quiet hours can follow a schedule, input boolean or binary sensor instead of fixed times: quiet while it is on. Held messages go out when it turns off.
- Speech volume by time of day (up to 4 bands) and by severity, under Settings, Speech volume. Without bands or a severity volume the volume is not changed.
- `snooze_custom` on `heads_up.notify`, `heads_up.create_banner` and watch rules: the card's snooze row offers **Other…**, so the viewer can snooze for any number of minutes or until a time of day, up to 24 hours.
- `heads_up_banner_unsnoozed` has the field `reason` and fires when a snooze ends by itself, including a snooze that ran out while Home Assistant was stopped. A global snooze has no `user_id`.
- New Overview. A status card lists the critical and warning messages nobody has acknowledged, with Acknowledge, Snooze 1 h, Clear and Show path. Coming up lists escalations, reminders, the next summary and the deliveries quiet hours hold, with a time and a count. The table "What would a message do right now?" shows for each channel and severity whether a message would make a sound, show, arrive quietly, wait, be skipped or not be set up, worked out by the same engine that delivers. Last actions rows can show the path of a message.
- The introduction is part of the Overview instead of a window. Step 2 sets the mail notify service, the global address and the speech engine, and saves them when you leave it. Step 3 shows the six built-in audiences with the people in them. Step 4 names the groups of policies and says how many policies Create makes. Settings > Restart introduction opens it on the Overview.
- Last to leave and First home remember when they happened; the introduction shows the time.
- Quick shortcuts under the Overview's status card: narrow links to Channels, Audiences, Policies and Watch rules. Needs attention, Coming up and Last actions are three cards with a number and one line; select one and its details slide out below, one at a time.
- Show path on the Overview lists what happened to a message as events: sent, reminder, escalation, held, summary, acknowledged, ended. Quiet sends name the policy, people who were not reached are named with the reason, and failed deliveries are explicit.
- Last actions on the Overview lists the five newest messages, one row each: severity, title and status (Active, Acknowledged, Snoozed, Resolved, Expired, Dismissed, Cleared), then the time, the channels that delivered and who was reached ("To Everyone (3/4 reached, 1 failed)"). Recipients you disabled are left out of the row and listed in the Message Log under "Not sent on purpose". Show path and the Message Log trace read oldest first, say how the message ended and no longer say "taken back" or "nothing was delivered". Top sources lists calls by their ID or tag instead of lumping them together.
- Activity on the Overview reads a history of the last 24 months, one record of counts per day, stored on disk and kept across restarts. Choose 24 hours, Week, Month, Year or 2 years: notifications with the change against the period before, failed deliveries, critical notifications, escalations, the share held by quiet hours and the share held for a summary, each with its change against the period before, a chart by severity, a weekday-by-hour grid and the top sources. Settings > Activity history shows its size and clears it. Diagnostics list its size and range, not its counts.

### Fixed

- After a restart or reload, Last actions no longer lists a watch rule as Active while it is not showing. A rule whose condition was false at the start came back without an end.

## [1.0.0] - 2026-11-16

Heads Up turns from a dashboard banner into a notification hub. One `heads_up.notify` call delivers a message on up to six channels, to audiences that follow who is home, with policies for escalation, reminders, quiet hours and summaries. Banners, the card and watch rules from 0.4.0 keep working.

### Before you upgrade

Read these if you have automations that use 0.4.0. Make a backup first; [Upgrading](docs/setup.md#upgrading) has the steps.

- `wait_for_condition` and the response status `condition_false` are removed from `heads_up.create_banner`. A call that still sends the field works, Heads Up ignores it and shows a notice under Settings > System > Repairs. A banner whose condition is false now always waits. To send only when the condition is true at the time of the call, add a condition to the automation before the action.
- `mode: recurring` without a `condition` is refused. Before, `mode` was ignored without a condition.
- `heads_up.clear_banner` and `heads_up.clear_all` are deprecated. They keep working and write one warning to the log per start. Use `heads_up.clear_notifications`; `clear_all` already removes every message on every channel, not only banners.
- The card shows "Snoozed (n)" with a Show now button to anyone who snoozed a banner. Set `show_snoozed: false` for the 0.4.0 look.
- A press on a banner's own button is refused once the banner was dismissed or its condition turned false. The setting "Disable message buttons once the message has ended" turns this off.
- The sidebar panel stays off on an existing installation. Switch on "Show Heads Up in the sidebar" under Settings > Devices & services > Heads Up > Configure.
- The stored data is converted on the first start and a backup is written to `.storage/heads_up.migration_v2`. 0.4.0 refuses the converted data; to go back, follow [Upgrading](docs/setup.md#upgrading).

### Added

- `heads_up.notify`: one message on several channels, with `recipients`, `audience` and `speakers` for all of them. `severity` is required. Calling it again with the same `id` replaces the message on every channel. `dry_run: true` returns who would get it and why, and sends nothing.
- Channels next to the banner: push to the Companion app, a popup over any dashboard, speech on media players and Assist satellites, mail through a notify service you choose, and Home Assistant's Persistent Notification. The shortcuts `heads_up.push`, `heads_up.popup` and `heads_up.speak` send on one channel.
- Push: one notification per message that is replaced on update and removed when the message ends, a level per severity (critical is the iOS critical alert and the Android alarm channel), and Acknowledge, Snooze, Dismiss and the message's own buttons. Pushes are rate limited per phone and in total; critical messages are never held back.
- `heads_up.clear_notifications` takes messages back from every channel by `id`, `tag`, `severity` or `channels`, or all of them with `all: true`. Speech and mail cannot be taken back.
- Audiences: Everyone, Admins, At home, Not home, Last to leave and First home, plus your own lists of persons or presence, including in a zone. Each audience is a sensor, and a call names it by its entity ID.
- Recipient profiles: every person's Companion devices are found through their trackers. A profile adds or removes a device, limits the channels, holds the mail address or switches the person off.
- Speaker groups of speakers, satellites and areas, each with a sensor that a call names.
- Policies, set once and matched by severity and tag or named in a call: Escalation, Reminder, Quiet hours, Away, Fallback, Deliver and Summarize. Each is a switch. Due times and held deliveries survive a restart. By default only the first matching policy in the ordered list runs.
- Acknowledgement: an Acknowledge button on the card, the popup and the push stops every escalation and reminder of the message, and the card shows "Acknowledged by Anna".
- The sidebar panel, for administrators: Overview with Needs attention, the Message Log with each message's delivery trace and the reason for every skipped delivery, Test send with a live preview and one real send, Watch rules, editors for audiences, recipients, policies and channels, Settings, and Help pages with examples. A four-step introduction offers four default policies.
- `image` on messages and watch rules: a picture under the message on the card, in the popup and on the push.
- Buttons can be `destructive` (red) and `require_auth` (a push button that works only on an unlocked phone).
- Conditions take `treat_unavailable_as` (`met` or `not_met`) for an entity that is unavailable or unknown.
- `heads_up.create_banner` takes `audience` and `recipients` like `notify`; `people` keeps working.
- `heads_up.get_trace` returns the delivery trace to an automation. The event `heads_up_delivery_failed` fires when a send failed or a channel reached nobody.
- Download diagnostics from the integration page, without mail addresses and message texts.
- Renaming a policy, audience or speaker group changes nothing that runs. When you change the entity ID of a person, speaker, zone or watched entity, Heads Up updates its own copies.

### Changed

- The Overview no longer has the Active notifications tile with its badges and the Watch rules tile, and the shortcut cards of 1.0 are narrow links. The introduction window, the bar that continued a paused tour and the Open page buttons are gone.
- The integration options (Configure) are grouped in sections and hold the same entries as the panel's Settings page.
- The event `heads_up_banner_action` carries `person` and `channel`.
- An invalid call is explained in a sentence, for example "The field message is required.", and a close misspelling of a name gets "Did you mean ...?".

### Fixed

- A signed-in user can no longer dismiss, snooze or unsnooze a banner addressed to other people (`not_targeted`).

## [0.4.0] - 2026-10-27

Summary of the 0.x releases (0.1.0 to 0.4.0): dashboard banners, the card and watch rules. Tested on Home Assistant 2026.9.4 and 2026.10.4.

### Added

- `heads_up.create_banner`, `heads_up.clear_banner` and `heads_up.clear_all`, with response data. Calling `create_banner` again with the same `id` replaces the banner.
- Banners end when someone dismisses them (per user or for everyone), when their `timeout` passes, also across a restart, or when an action clears them. At most 50 are kept by default; the oldest low-severity banner goes first and critical banners are never removed.
- Conditions: a banner shows only while an entity matches, with the operators `equals`, `not_equals`, `above`, `below`, `between`, `contains`, `not_contains`, `empty` and `not_empty`, or while a template is true. `for` makes the condition hold for a while first. `mode: once` ends the banner when the condition turns false; `mode: recurring` hides it and shows it again.
- `people` limits a banner to the users of the listed persons.
- Buttons: up to three per banner, each with an optional action, and `tap_action` with confirmation. The event `heads_up_banner_action` fires on a press.
- Snooze, with the choices you give and per user or for everyone. The card option `show_snoozed` lists snoozed banners with Show now.
- The card `custom:heads-up-card`, loaded by the integration with no dashboard resource. It filters by severity and tag, has the layouts comfortable and compact, and options for title, time, colors, "Show N more", Clear all, swipe to dismiss and an empty state. It has a visual editor.
- Watch rules: a banner while an entity is in a state or a template is true, set up under Settings > Devices & services > Heads Up, without an automation. Rules have the same buttons, tap action, snooze, dismiss scope and templated messages as actions.
- Events for created, updated, dismissed, expired, cleared, snoozed and unsnoozed banners, and the sensor `sensor.heads_up_active_banners`.
- English, German, French and Spanish, following your Home Assistant language. The translations are not reviewed by native speakers.

### Fixed

- The card no longer shows "Custom element doesn't exist: heads-up-card" on a reload: it waits for Home Assistant before it registers, and the browser caches the card file.
- After an update, the card address includes a hash of the card file, so a reloaded dashboard loads the new card.
