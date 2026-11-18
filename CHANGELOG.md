# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/). Only releases are listed; the 1.0.0 pre-releases are summarized under 1.0.0.

## [Unreleased]

### Before you upgrade

- `heads_up_banner_unsnoozed` also fires when a snooze runs out, not only when someone ends it in the card. The event has a new field `reason`: `ended` or `user`. An automation that should react only to the card, as before, needs a condition on `reason: user`.

### Added

- `snooze_custom` on `heads_up.notify`, `heads_up.create_banner` and watch rules: the card's snooze row offers **Other…**, so the viewer can snooze for any number of minutes or until a time of day, up to 24 hours.
- `heads_up_banner_unsnoozed` has the field `reason` and fires when a snooze ends by itself, including a snooze that ran out while Home Assistant was stopped. A global snooze has no `user_id`.

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
