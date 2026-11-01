# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Panel page FAQ and examples: six example calls with a Copy button and eleven questions with answers, in English, German, French and Spanish. The examples are validated against the action schemas by the documentation check.
- Panel navigation: the pages of a group are pills under the top row instead of a second grey tab bar.
- Welcome: the first time an administrator opens the panel, a dialog explains four default policies and lets you switch each on or off: Quiet hours (22:00 to 07:00, send quietly, critical passes), Evening summary (messages tagged `digest`, 20:00), Critical messages (pushed at once at the iOS critical level, a reminder every 10 minutes, speech after 10 minutes, dismissing counts as acknowledging) and Warning reminders. It adds only what is missing and changes nothing you have. A button on Settings shows it again. New admin-only WebSocket commands `heads_up/welcome_get` and `heads_up/welcome_apply`. See [The panel](docs/panel.md).
- Policy type Deliver: sends the messages it applies to to a chosen audience on chosen channels at once, in addition to the call. See [Policies](docs/policies.md).
- Panel page Test send: a live preview of a call (one row per recipient and channel with the result and reason, a summary, the policies that apply, the later steps, fallback rows), the call as `heads_up.notify` YAML with a Copy button, and one real Send test with a marker (title starting with `Test: `, tag `test`, id `hu_test_…`, 10 minutes). New admin-only WebSocket commands `heads_up/hub_plan` and `heads_up/hub_test_send`. See [The panel](docs/panel.md).
- Panel editors: Audiences, Recipients (profiles and speaker groups), Policies (all six types) and Channels (push level, popup style, lock-screen text and the other channel settings). They save through the integration's own forms, show the stored YAML and a sentence in words, and refuse to delete an audience or group a policy uses. New admin-only WebSocket commands `heads_up/panel_config` and `heads_up/channels_set`. See [The panel](docs/panel.md).
- Panel pages Overview and Messages: active notifications with their states (escalating, reminding, snoozed, in a summary, acknowledged), watch rules, a Needs attention list with fix buttons, a log of last actions, and the recent messages with their delivery trace. New admin-only WebSocket commands `heads_up/panel_overview`, `heads_up/panel_messages` and `heads_up/panel_trace`. The log and the recent messages are kept in memory and start empty after a restart. See [The panel](docs/panel.md).
- Admin panel (hub work in progress): a Heads Up entry in the sidebar for administrators, off until you switch it on. The setup flow asks "Show Heads Up in the sidebar" (on by default there); installations that exist keep it off. The option `show_panel` is also in the integration's options and on the panel's Settings page, and the entry appears and disappears without a restart. The panel has the navigation (five groups, a second row for groups with several pages) and the Settings page: hub and sidebar switches, people and devices, limits, history and the read-only install token. New admin-only WebSocket commands `heads_up/settings_get`, `heads_up/settings_set` and `heads_up/settings_apply_preset`. See [The panel](docs/panel.md).
- Card: an Acknowledge button on banners that an escalation or reminder policy covers, and the line "Acknowledged by Anna" (or "and 2 others") under an acknowledged banner. New card option `show_acknowledged` (on by default). The banner payload has the new fields `acknowledged`, `acknowledged_by`, `acknowledged_count` and `can_acknowledge`. See [Card](docs/card.md).
- Persistent notification channel (hub work in progress): `heads_up.notify` with `channels: [persistent]` mirrors a message to Home Assistant's notification bell with the id `hu_<message id>`, replaces it on update and dismisses it when the message ends. It takes no target and is visible to every user. All five channels now deliver. See [Persistent notifications](docs/persistent.md).
- Popup channel (hub work in progress): `heads_up.notify` and `heads_up.popup` show a message over any dashboard for the people you target: a corner card for success, info and warning and a centered window for critical, one at a time, with the message's buttons, Acknowledge, Snooze and Dismiss. A script under 1 KB is added to every page and loads the popup code only when a popup is due. New WebSocket commands `heads_up/popup_config` and `heads_up/popup_subscribe`, option `popup_styles` (no form yet). See [Popups](docs/popup.md).
- Speak channel (hub work in progress): `heads_up.notify` and `heads_up.speak` say a message on media players and Assist satellites, through `assist_satellite.announce`, `tts.speak` or plain playback. Groups and areas expand to their speakers. The text is `tts_message`, the title or the message, cut at 200 characters (option). A speaker says one message at a time and does not repeat the same text within 60 seconds (option). Quiet hours skip speech; nothing is said when a message ends. New options Spoken text: longest, Spoken text: repeat pause and Text-to-speech engine. Manifest: `after_dependencies` `assist_satellite`, `media_player` and `tts`. See [Speech](docs/speech.md).
- Policy type Summarize: holds the messages it applies to on every channel, including the banner, and sends one summary per recipient and channel every N minutes (default 60) or at a time of day. Critical messages are held only if the policy includes them. A summary lists at most ten messages, marks cleared ones as resolved and stays 24 hours. See [Policies](docs/policies.md).
- Policy types Quiet hours (hold, send quietly or drop deliveries in a time window on the local clock, critical passes by default), Away (send to people who are not home when they arrive) and Fallback (other channels and targets when the first delivery reached nobody). Held deliveries are stored and survive a restart. See [Policies](docs/policies.md).
- Policies: Escalation (deliver on more channels after N minutes without acknowledgement) and Reminder (repeat while nobody acknowledges), a new Policy entry type with a form, matching by severity and tag (watch rule messages have the tag `rule`), the `policy` field of `notify`, acknowledgement (`acknowledged_by`, WebSocket command `heads_up/acknowledge`, an Acknowledge button on pushes when a policy applies), due times kept over restarts, and the admin command `heads_up/hub_usage` that lists the policies naming an audience or group. See [Policies](docs/policies.md).
- Push channel (hub work in progress): `heads_up.notify` and `heads_up.push` send Companion app notifications through `notify.mobile_app_<device>`, one tag per message so devices replace instead of stacking, a level per severity, buttons (the message's own, Snooze, Dismiss) and clearing when the message ends. Pressing a button acts for the person it was sent to. See [Push notifications](docs/push.md). Options `push_levels`, `push_lockscreen`, `push_channel_id`, `push_sticky` (no form yet). Manifest: `after_dependencies` `mobile_app` and `notify`.
- Audiences, recipient groups and recipient profiles (hub work in progress). Built-in audiences `Everyone`, `Admins`, `At home`, `Not home`, `Last to leave`, `First home`; custom audiences of persons or presence (including in a zone); recipient groups of speakers, satellites and areas; recipient profiles that are derived for every person from their Companion devices. Three new entry types with forms, option Presence delay (60 seconds), admin WebSocket command `heads_up/hub_preview_audience`. See [Audiences and recipients](docs/audiences.md). `notify` now checks audience and recipient names against these objects.
- Hub core (work in progress on a feature branch): the actions `heads_up.notify`, `heads_up.push`, `heads_up.popup`, `heads_up.speak` and `heads_up.clear`. `notify` takes a list of channels and a target per channel. Only the banner channel delivers in this version; the other channels report `skipped` with the reason `channel_unavailable`.
- Option `hub_enabled` (on by default). Off: `notify` accepts only `channels: [banner]`, and no hub listener, task or store exists.
- Option `install_token`, generated once. Hub limits and history sizes are stored as options and not enforced yet.
- A delivery ledger in `.storage/heads_up.deliveries`, a trace of delivery decisions and the admin WebSocket command `heads_up/hub_trace`.
- Stored banners carry the optional fields `channels`, `targets`, `policy`, `tts_message`, `acknowledged_by` and `source`. Banners saved by an older version load unchanged. After using `notify`, a downgrade needs the banners cleared.

## [0.4.0] - 2026-10-27

### Added
- Watch rules got the features that actions have: Buttons and Tap action (YAML fields in the rule form, same format as `actions` and `tap_action`), Dismiss scope (per user or everyone) and a Template in place of an entity. A rule without a dismiss scope stays per user.
- German, French and Spanish: the integration's screens and the card follow your Home Assistant language. Other languages show English. The texts are not reviewed by native speakers.
- Snooze: `snoozable`, `snooze_scope` and `snooze_options` in `heads_up.create_banner`, and a Snoozable option in the watch rule form. The card shows a snooze button; with `swipe_to_dismiss`, a right swipe opens the choices. New options `default_snoozable`, `default_snooze_scope`, `default_snooze_options`. New event `heads_up_banner_snoozed`.
- End a snooze early: card option `show_snoozed` lists your snoozed banners with a Show now button. New WebSocket command `heads_up/unsnooze`, option `show_snoozed` for `heads_up/subscribe`, new event `heads_up_banner_unsnoozed`.
- Banner buttons: `actions` in `heads_up.create_banner` (up to 3 buttons with `key`, `label`, `dismiss` and an optional `action`). New event `heads_up_banner_action`.
- Conditions `empty` and `not_empty` ("Is empty", "Is not empty" in the rule form) for `heads_up.create_banner` and watch rules. They need no `state`.

### Fixed
- The card no longer shows "Custom element doesn't exist: heads-up-card" on some reloads. It registered itself before Home Assistant's scripts had finished loading, which Home Assistant then ignored until the page was reloaded. It now waits for Home Assistant.
- The watch rule form no longer fills the State field with `on`. A rule with equals or does not equal and no value still uses `on`.

## [0.3.0] - 2026-10-26

### Added
- Conditions can hold for a while first: `condition.for` in `heads_up.create_banner` and the "Condition must hold for" field of watch rules. The banner shows only after the condition has been true for that long (1 second to 24 hours). After a restart the wait starts again.
- `heads_up.create_banner` accepts `condition.template`: a Home Assistant template that must be true. It cannot be combined with `entity_id`, `operator`, `state` or `attribute`.

### Fixed
- A watch rule banner's "time ago" counts from the moment its condition turned true. Before, it counted from when Home Assistant started or the rule was edited.
- The card file is now cached by the browser (its address already changes with the file). This avoids the occasional "Custom element doesn't exist: heads-up-card" on page reloads when the file loads too slowly.

## [0.2.2] - 2026-10-26

### Fixed
- Watch rule messages now render Home Assistant templates. Before, `{{ states('...') }}` appeared as literal text. The text updates when the entities the template reads change, not for time functions such as `now()`. The rule form refuses an invalid template; a template that fails at render time shows its raw text and logs a warning.

## [0.2.1] - 2026-10-25

### Fixed
- Home Assistant showed version 0.1.0 for the 0.2.0 release because `manifest.json` was not updated. It now matches the release. No other change from 0.2.0.

## [0.2.0] - 2026-10-25

### Added
- `condition.operator` for `create_banner` and watch rules: `equals` (default), `not_equals`, `above`, `below`, `between`, `contains`, `not_contains`. Banners and rules without an operator behave as before. See [actions](docs/actions.md#conditions) and [rules](docs/rules.md).
- README section with watch rule examples and a screenshot of the rule form.

### Fixed
- The "Add watch rule" form no longer shows a translation error in its description.

## [0.1.0] - 2026-10-25

First release. Tested on a local Home Assistant 2026.9.4 instance and, with the test suite only, on 2026.10.4.

### Added
- Actions `heads_up.create_banner`, `heads_up.clear_banner` and `heads_up.clear_all` with response data.
- Banners with a `timeout` disappear after that time, also when Home Assistant restarts in between.
- When the banner limit (default 50) is reached, the oldest lowest-severity banner is removed; `critical` banners are never removed.
- Events `heads_up_banner_created`, `_updated`, `_dismissed`, `_expired`, `_cleared`.
- Sensor `sensor.heads_up_active_banners` with the number of active banners (not waiting for a condition).
- `condition`: a banner shows only while an entity matches a state, a list of states or an attribute value. `mode: once` removes it when the entity stops matching; `mode: recurring` hides it and shows it again.
- `wait_for_condition`: a banner whose condition is false at the time of the call waits for it, or is not stored (`condition_false`).
- `people`: a banner reaches only the users linked to the listed person entities.
- Options: maximum banners, eviction on/off, default dismiss scope, default timeout (24 hours).
- Card `custom:heads-up-card` with options `severity`, `tag`, `max_items`, `sort`, `layout`, `show_all`, `show_empty` and a visual editor. It loads with the integration; no dashboard resource is needed. See [docs/card.md](docs/card.md).
- Banners with a `tap_action` are tappable in the card, including `confirmation`.
- Examples for an open window, a critical alert for one person, a tap action with confirmation, and REST and WebSocket calls: [docs/examples.md](docs/examples.md).
- Card options `title`, `show_time`, `collapsed_items` ("Show N more"), `clear_all`, `swipe_to_dismiss`, `colors`, `colorize`, `empty_message` and `empty_icon`. The `compact` layout now shows each banner on one line.
- WebSocket command `heads_up/dismiss_many`, used by the "Clear all" button.
- Brand icon for the integration.
- Pages: [troubleshooting](docs/troubleshooting.md), [limitations](docs/limitations.md), [upgrading](docs/upgrading.md), [uninstalling](docs/uninstall.md).
- The card reconnects after a Home Assistant restart and retries until the integration is loaded.
- Watch rules: add a rule in Settings > Devices & services > Heads Up, and a banner shows on every Heads Up card while an entity is in a state, without an automation. Rules can be dismissible per user, target people and use `{name}` for the entity name. See [docs/rules.md](docs/rules.md).
- `heads_up_banner_cleared` has the new `reason` value `rule`.
- WebSocket error `rule_banner` for `heads_up/admin_clear` on a rule banner. The card shows no "Clear for everyone" button on rule banners.

### Changed
- The card no longer shows the severity text label by default. The icon and color still show the severity, and screen readers still get the label. Set `show_severity: true` to show it.

### Fixed
- A banner that cannot be read from storage is skipped with an error in the log; the other banners and the integration still load.
- After an update, browsers could keep showing the previous card because its address did not change. The address now includes a hash of the card file.
