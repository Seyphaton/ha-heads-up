# Heads Up

Heads Up shows dismissible banners inside a Home Assistant dashboard. Automations, scripts and external programs create and clear banners with actions. The dashboard holds no message text.

Banners stay until someone closes them, a condition on an entity stops matching, a timeout passes, or an action clears them. They survive a Home Assistant restart.

Status: in development. There is no release and the repository is not published yet.

## Requirements

- Home Assistant 2026.9.0 or newer.
- Tested on Home Assistant 2026.9.4 (tests and a local instance) and 2026.10.4 (tests only).

## Install

Heads Up is not on HACS yet. Install it by hand:

1. Make a backup.
2. Copy the folder `custom_components/heads_up` of this repository to `custom_components/heads_up` in your Home Assistant configuration folder.
3. Restart Home Assistant. A restart pauses all automations until it has finished.

## Set up

1. Go to Settings > Devices & services and add the integration Heads Up. It asks for nothing.
2. Add the card to a dashboard in the YAML editor:

   ```yaml
   type: custom:heads-up-card
   ```

   The card is registered by the integration. You do not add a dashboard resource.
3. Go to Developer tools > Actions, switch to YAML mode and run:

   ```yaml
   action: heads_up.create_banner
   data:
     message: Hello from Heads Up.
     timeout: 0
   ```

The banner appears in the card without a reload. Close it with the X button, or remove it with `heads_up.clear_all`.

## Options

Open the integration and choose Configure. Changes apply to banners created afterwards.

| Option | Default | Meaning |
|---|---|---|
| Maximum number of banners | 50 (1–200) | Limit for stored banners. |
| Evict the oldest lowest-severity banner when full | on | When off, creating a banner beyond the limit fails. `critical` banners are never evicted. |
| Default dismiss scope | `user` | Used when an action sets no `dismiss_scope`. |
| Default timeout | 24 hours | Used when an action sets no `timeout`. Clearing it keeps banners until they are closed or cleared. |

## How it works

The card receives banners over the Home Assistant WebSocket connection and updates when a banner changes. It does not poll. The integration creates one entity, `sensor.heads_up_active_banners`, with the number of active banners.

## Documentation

- [Actions](docs/actions.md): fields, responses, conditions, people, events.
- [Card](docs/card.md): options and behaviour.
- [Examples](docs/examples.md): window with a condition, alert for one person, tap action, REST and WebSocket.
- [Troubleshooting](docs/troubleshooting.md)
- [Limitations](docs/limitations.md)
- [Upgrading](docs/upgrading.md) and [uninstalling](docs/uninstall.md)
- [Security](SECURITY.md)

## License

MIT, see [LICENSE](LICENSE).
