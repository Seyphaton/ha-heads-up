# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up is a notification hub for Home Assistant. Your automations make one call. Heads Up orchestrates where the message shows up, who gets it, and when it is delivered or escalated. It removes the message from every channel when it ends.

It shows messages as banners in a dashboard card and delivers them as phone pushes, popups, speech, mail and Persistent Notification entries. A message escalates to more people until someone acknowledges it, repeats as a reminder, and waits for the right moment: until someone is home, for the last person to leave or for the first one back.

![Your automation makes one call, and Heads Up orchestrates where the message shows up (banner, push, popup, speech, mail, Persistent Notification), who gets it (everyone, admins, whoever is home, the last one to leave, one person) and when (quiet at night, repeat until acknowledged, escalate, evening summary, send on arrival).](docs/images/where-who-when.svg)

## How to start

Install: in HACS, search for "Heads Up" and click "Download" (for a pre-release, switch on "Show beta versions" in the download dialog), then restart Home Assistant. It needs Home Assistant 2026.9.0 or newer; make a backup first.

1. Add the integration under Settings > Devices & services > Add integration > Heads Up. Leave "Show Heads Up in the sidebar" on to get the panel.
2. Add the card to a dashboard of your own (Settings > Dashboards > Add dashboard; the built-in Overview cannot be edited): Edit, Add card, Manual, then paste:

   ```yaml
   type: custom:heads-up-card
   title: House Information
   ```

3. Send a message to the banner and to the phones of everyone, from an automation, a script or Developer tools > Actions (named Tools in Home Assistant 2026.10), in YAML mode:

   ```yaml
   action: heads_up.notify
   data:
     id: front_door
     title: Front door
     message: The front door has been open for 10 minutes.
     severity: warning
     channels: [banner, push]
     to:
       push: {audience: Everyone}
   ```

4. Nothing arrived? Open Heads Up > Notifications and rules > Message Log, choose the message and read the Result column. It names the reason for every skipped delivery.

<img src="docs/images/card-default.png" width="420" alt="The card with four banners: critical, warning, info and success">

Take the message back from every channel with `heads_up.clear_notifications` and its `id`:

```yaml
action: heads_up.clear_notifications
data:
  id: front_door
```

Everything was tested on local Home Assistant instances with stub devices, not on real phones or speakers.

### Go deeper

- [Setup guide and initial configuration](docs/setup.md): install, your first message, the panel, the introduction, upgrading and uninstalling.
- [Actions](docs/actions.md): every callable action with all its parameters and their defaults.

## Documentation

- [Setup guide](docs/setup.md): install, first message, card, panel, introduction, upgrading, uninstalling.
- [Actions, watch rules and card](docs/actions.md): the actions with every field, banners from an entity state without an automation, and the card options.
- [Configuration](docs/configuration.md): channels, audiences, recipients and policies.
- [Settings](docs/settings.md): every setting and global default, with its limits.
- [Examples and FAQ](docs/examples.md): working examples, answers to common questions, troubleshooting and limitations.
- [Security](SECURITY.md) and [Changelog](CHANGELOG.md).

## License

MIT, see [LICENSE](LICENSE).
