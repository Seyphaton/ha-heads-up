# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up is a notification hub for Home Assistant. Your automations make one call. Heads Up decides where the message shows up, who gets it and when, and removes it from every channel when it ends.

It shows messages as banners in a dashboard card and delivers them as phone pushes, popups, speech, mail and Persistent Notification entries. A message escalates to more people until someone acknowledges it, repeats as a reminder, and waits for the right moment: until someone is home, for the last person to leave or for the first one back.

![Your automation makes one call, and Heads Up orchestrates where the message shows up (banner, push, popup, speech, mail, Persistent Notification), who gets it (everyone, admins, whoever is home, the last one to leave, one person) and when (quiet at night, repeat until acknowledged, escalate, evening summary, send on arrival).](https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/where-who-when.svg)

## One call instead of a pile of steps

A leak sensor should warn the dashboard and every phone at home, repeat if nobody reacts, call in the speakers and an administrator after five minutes, and stop everywhere once someone acknowledges it or the sensor is dry. In plain Home Assistant that is a notify call for each phone, a presence check, a speech call, a repeat loop with waits, and a second automation that cleans up.

With Heads Up the automation states what happened and how serious it is:

```yaml
action: heads_up.notify
data:
  id: water_leak
  title: Water leak
  message: Water on the kitchen floor.
  severity: critical
  tag: water
  channels: [banner, push, popup]
  audience: binary_sensor.heads_up_audience_at_home
  timeout: 0
```

You set the repeat and the escalation once, on the panel's Policies page, and they apply to every critical message tagged `water`. The [leak example](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/examples.md#a-leak-that-escalates) lists the three policies.

## What you get

With no setup beyond the integration and the card:
- Banners in the card until the message is dismissed, its condition ends or its timeout passes.
- Pushes to the Companion app of everyone, of the administrators, of whoever is home, or of one person.
- A popup on dashboards, speech on speakers, mail and Persistent Notification entries.
- One call, `heads_up.clear_notifications`, takes the message back from every channel.
- The Message Log shows why a delivery was skipped.

With policies, which a four-step introduction in the panel creates for you:
- Critical messages push at once, with the iOS critical alert and the Android alarm channel.
- A warning nobody acknowledges repeats every 30 minutes, at most three times.
- Info messages tagged `digest` are held and sent as one summary at 20:00.
- Other info and success messages are sent quietly from 22:00 to 07:00.

## How to start

Install: in HACS, search for "Heads Up" and click "Download", then restart Home Assistant. It needs Home Assistant 2026.9.0 or newer; make a backup first.

1. Add the integration under Settings > Devices & services > Add integration > Heads Up. Leave "Show Heads Up in the sidebar" on to get the panel.
2. Add the card to a dashboard of your own (Settings > Dashboards > Add dashboard; the built-in Overview cannot be edited): Edit, Add card, Manual, then paste:

   ```yaml
   type: custom:heads-up-card
   title: House Information
   ```

3. Send a message to the banner and to the phones of everyone (a phone needs the Home Assistant Companion app and a person it belongs to), from an automation, a script or Developer tools > Actions (named Tools in Home Assistant 2026.10), in YAML mode:

   ```yaml
   action: heads_up.notify
   data:
     id: front_door
     title: Front door
     message: The front door has been open for 10 minutes.
     severity: warning
     channels: [banner, push]
     audience: binary_sensor.heads_up_audience_everyone
   ```

4. Nothing arrived? Open Heads Up > Notifications and rules > Message Log, select the message. A window lists each channel with the people and phones it reached and the reason for every skipped delivery.

<img src="https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/card-default.png" width="420" alt="The card with four banners: critical, warning, info and success">

Take the message back from every channel with `heads_up.clear_notifications` and its `id`:

```yaml
action: heads_up.clear_notifications
data:
  id: front_door
```

## Documentation

Start with the setup guide.

- [Setup guide](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/setup.md): install, first message, card, panel, introduction, upgrading, uninstalling.
- [Actions, watch rules and card](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/actions.md): the actions with every field, banners from an entity state without an automation, and the card options.
- [Configuration](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/configuration.md): channels, audiences, recipients and policies.
- [Settings](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/settings.md): every setting and global default, with its limits.
- [Examples and FAQ](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/examples.md): working examples, answers to common questions, troubleshooting and limitations.
- [Security](https://github.com/Seyphaton/ha-heads-up/blob/main/SECURITY.md) and [Changelog](https://github.com/Seyphaton/ha-heads-up/blob/main/CHANGELOG.md).

## License

MIT, see [LICENSE](https://github.com/Seyphaton/ha-heads-up/blob/main/LICENSE).
