# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/).

## [Unreleased]

### Fixed
- Watch rule messages now render Home Assistant templates. Before, `{{ states('...') }}` appeared as literal text.

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
