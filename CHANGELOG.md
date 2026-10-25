# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/).

## [Unreleased]

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
- The card reconnects after a Home Assistant restart and retries until the integration is loaded.
