# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up shows banners inside a Home Assistant dashboard. Automations, scripts and external programs create and clear banners with actions. Watch rules show a banner while an entity is in a state, without an automation. The dashboard holds no message text.

**Every option with examples: [How to use Heads Up](docs/how-to.md).**

Banners stay until someone closes them, a condition on an entity stops matching, a timeout passes, or an action clears them. They survive a Home Assistant restart.

Status: version 0.3.0. It was tested on a local development instance of Home Assistant only. Make a backup before you install it.

## Requirements

- Home Assistant 2026.9.0 or newer.
- Tested on Home Assistant 2026.9.4 (tests and a local instance) and 2026.10.4 (tests only).

## Install

Make a backup first. Installing needs a Home Assistant restart, which pauses all automations until it has finished.

### With HACS

The first button at the top opens the repository in HACS on your Home Assistant. It works once the repository is public. The second button opens the setup dialog of the integration after it is installed.

Heads Up is not in the default HACS list. Add it as a custom repository:

1. In HACS, click the three dots in the top right corner and choose "Custom repositories".
2. Enter `https://github.com/Seyphaton/ha-heads-up` and select the type "Integration".
3. Click "Add", then find Heads Up in HACS and download it.
4. Restart Home Assistant.

### By hand

1. Copy the folder `custom_components/heads_up` of this repository to `custom_components/heads_up` in your Home Assistant configuration folder.
2. Restart Home Assistant.

## Set up

Go to Settings > Devices & services and add the integration Heads Up. It asks for nothing. The card is registered by the integration, so you do not add a dashboard resource.

Banners also come from watch rules: a rule shows a banner while an entity matches a condition. See [docs/rules.md](docs/rules.md).

## Quick start

Add the card to a dashboard in the YAML editor:

```yaml
type: custom:heads-up-card
title: House Information
show_time: true
show_severity: true
```

Create a banner in Developer tools > Actions (YAML mode), or from an automation or script:

```yaml
action: heads_up.create_banner
data:
  id: garage_open
  title: Warning
  message: Garage door open after 10pm.
  severity: warning
```

The banner appears in the card without a reload. Close it with the X button, or remove it with `heads_up.clear_all`. Without `timeout` it disappears after 24 hours.

![Card with four banners: critical, warning, info and success, each with a severity label and the time since it was created](docs/images/card-default.png)

> **All options and more examples: [How to use Heads Up](docs/how-to.md).** Card options with screenshots, every action field, buttons and snooze, watch rules and integration options.

## How it works

The card receives banners over the Home Assistant WebSocket connection and updates when a banner changes. It does not poll. The integration creates one entity, `sensor.heads_up_active_banners`, with the number of active banners, including active watch-rule banners.

## Documentation

- [How to use Heads Up](docs/how-to.md): every option with examples and screenshots.
- [Actions](docs/actions.md): fields, responses, conditions, people, events.
- [Card](docs/card.md): options and behaviour.
- [Watch rules](docs/rules.md): banners from an entity state or value, without an automation.
- [Examples](docs/examples.md): window with a condition, alert for one person, tap action, REST and WebSocket.
- [Troubleshooting](docs/troubleshooting.md)
- [Limitations](docs/limitations.md)
- [Upgrading](docs/upgrading.md) and [uninstalling](docs/uninstall.md)
- [Security](SECURITY.md)

## License

MIT, see [LICENSE](LICENSE).
