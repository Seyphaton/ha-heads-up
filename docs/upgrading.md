# Upgrading

1. Make a backup.
2. Read [CHANGELOG.md](../CHANGELOG.md) for the new version.
3. Replace the folder `custom_components/heads_up`, or update it in HACS.
4. Restart Home Assistant. A restart pauses all automations until it has finished.
5. Reload open dashboards. The card address contains the integration version and a hash of the card file, so a browser that reloads the page loads the new card file. If a dashboard still looks old, reload the page without cache once.

Banners, closed states and timeouts are kept across the restart. Options keep their values. Watch rules are part of the integration entry and stay too; a closed rule banner returns after the restart.

## Versions

Heads Up uses [semantic versioning](https://semver.org/). Action names, field names, defaults, response keys, event types, event data keys, the card type and the card options are the public interface.

- A minor version adds to it.
- A removal or a change of meaning needs a major version. The previous minor version logs a warning when you use the old form.

The storage file has version 1. No release has changed it yet.
