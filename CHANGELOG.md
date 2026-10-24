# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Actions `heads_up.create_banner`, `heads_up.clear_banner` and `heads_up.clear_all` with response data.
- Banners with a `timeout` disappear after that time, also when Home Assistant restarts in between.
- When the banner limit (default 50) is reached, the oldest lowest-severity banner is removed; `critical` banners are never removed.
- Events `heads_up_banner_created`, `_updated`, `_dismissed`, `_expired`, `_cleared`.
- Sensor `sensor.heads_up_active_banners` with the number of stored banners.
- Options: maximum banners, eviction on/off, default dismiss scope, default timeout (24 hours).
