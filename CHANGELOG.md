# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Images: the field `image` (an http(s) URL or a path such as `/media/local/door.jpg`) on `create_banner`, `notify`, `push` and `popup`, and an Image field in the watch rule form. The picture shows under the message on the card (not in the compact layout) and in the popup, and goes to the phone as `data.image`. A push leaves it out when the lock screen setting is not `full`.
- Notification hub: the actions `heads_up.notify`, `heads_up.push`, `heads_up.popup`, `heads_up.speak` and `heads_up.clear`. `notify` takes a list of channels and a target per channel. The option `hub_enabled` (on by default) switches the hub off; with it off, `notify` accepts only `channels: [banner]` and no hub listener, task or store exists. The option `install_token` is generated once. See [Notification hub](docs/hub.md).
- Delivery ledger in `.storage/heads_up.deliveries`, a trace of delivery decisions (admin WebSocket command `heads_up/hub_trace`) and optional banner fields `channels`, `targets`, `policy`, `tts_message`, `acknowledged_by` and `source`. Banners saved by an older version load unchanged. After using `notify`, a downgrade needs the banners cleared.
- Push channel: Companion app notifications through `notify.mobile_app_<device>`, one tag per message so devices replace instead of stacking, a level per severity, buttons (the message's own, Snooze, Dismiss, Acknowledge) and clearing when the message ends. Options `push_levels`, `push_lockscreen`, `push_channel_id`, `push_sticky`. Manifest: `after_dependencies` `mobile_app` and `notify`. See [Push notifications](docs/push.md).
- Popup channel: a corner card for success, info and warning and a centered window for critical, over any dashboard, one at a time, with the message's buttons, Acknowledge, Snooze and Dismiss. A script under 1 KB is added to every page and loads the popup code only when a popup is due. Option `popup_styles`; WebSocket commands `heads_up/popup_config` and `heads_up/popup_subscribe`. See [Popups](docs/popup.md).
- Speak channel: a message said on media players and Assist satellites through `assist_satellite.announce`, `tts.speak` or plain playback. Groups and areas expand to their speakers. Options for the longest text (200 characters), the repeat pause (60 seconds) and the text-to-speech engine. Manifest: `after_dependencies` `assist_satellite`, `media_player` and `tts`. See [Speech](docs/speech.md).
- Notification bell channel: `channels: [persistent]` mirrors a message to Home Assistant's notification bell with the id `hu_<message id>`, replaces it on update and dismisses it when the message ends. After a restart, the entries of active messages come back. See [Persistent notifications](docs/persistent.md).
- Audiences, recipient groups and recipient profiles: built-in audiences `Everyone`, `Admins`, `At home`, `Not home`, `Last to leave`, `First home`; custom audiences of persons or presence (including in a zone); recipient groups of speakers, satellites and areas; profiles derived from each person's Companion devices. Option Presence delay (60 seconds). Admin command `heads_up/hub_preview_audience`. See [Audiences and recipients](docs/audiences.md).
- Policies: Escalation, Reminder, Quiet hours, Away, Fallback, Summarize and Deliver, each a new entry type with a form, matched by severity and tag (watch rule messages have the tag `rule`) or named in the `policy` field of `notify`. Due times and held deliveries survive a restart. Admin command `heads_up/hub_usage`. See [Policies](docs/policies.md).
- Acknowledgement: the command `heads_up/acknowledge`, an Acknowledge button on banners, popups and pushes that an escalation or reminder policy covers, and the line "Acknowledged by Anna" (or "and 2 others") on the card. New card option `show_acknowledged` (on by default) and the banner fields `acknowledged`, `acknowledged_by`, `acknowledged_count` and `can_acknowledge`. See [Card](docs/card.md).
- Rate limits for pushes: 5 per device per minute and 60 in total are skipped (`rate_limited` in the trace), and an update with the same content within 30 seconds is ignored (`duplicate`). Critical messages are never held back. The three numbers are settings.
- Panel: a Heads Up entry in the sidebar for administrators (option `show_panel`; the setup flow asks, existing installations keep it off). It has the Overview, Messages with the delivery trace of each message, editors for audiences, recipients, policies and channels, Test send with a live preview and one real send, Settings, a welcome that creates four default policies, and a FAQ and examples page in English, German, French and Spanish. Admin WebSocket commands `heads_up/settings_get`, `settings_set`, `settings_apply_preset`, `welcome_get`, `welcome_apply`, `hub_plan`, `hub_test_send`, `panel_config`, `channels_set`, `panel_overview`, `panel_messages` and `panel_trace`. See [Panel](docs/panel.md).

### Changed
- Speech accepts any Home Assistant area by ID or name in `recipients`; before, an area needed a recipient group. An area or group with no speaker, and a missing speaker, leave an entry in the notification bell that names the area, group or speaker.
- A press on a message's own button is refused with `message_ended` once the message was dismissed, acknowledged or its condition turned false. Before, it was accepted until the message was removed. The option "Disable message buttons once the message has ended" (Banners, on by default) turns the check off.
- The options screen (Configure) and the panel's Settings page hold the same entries in the same order and wording: Hub, Banners, Presence, Speech, Limits and History. The options screen is grouped in sections, shows the install token and gained the limits and the history sizes; the panel gained the banner defaults, the presence delay and the speech settings.

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
