# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up is a notification hub for Home Assistant. An automation makes one call that says what happened and how serious it is. Heads Up decides where the message goes, who gets it and when, and takes it back from every channel when it is over.

The channel it adds to Home Assistant is the banner. A banner sits in a dashboard card until someone dismisses it, its condition stops matching or its timeout passes. The same call also reaches phones through the Companion app, shows a popup over any dashboard, speaks on speakers and Assist satellites, sends mail and writes a Persistent Notification.

![Your automation makes one call, and Heads Up orchestrates where the message shows up (banner, push, popup, speech, mail, Persistent Notification), who gets it (everyone, admins, whoever is home, the last one to leave, one person) and when (quiet at night, repeat until acknowledged, escalate, evening summary, send on arrival).](https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/where-who-when.svg)

## What it takes out of your automations

### Channels

A message lists its channels: `channels: [banner, push, popup]`. Send it again with the same `id` and it is replaced on each of them, so a phone keeps a single notification for it. `heads_up.clear_notifications` removes the banner, the pushes, the popup and the Persistent Notification in one step. Speech and mail cannot be taken back.

### Audiences

A call names people. Heads Up finds each person's phones through their trackers, so a new phone needs no change in any automation.

The built-in audiences are Everyone, Admins, At home, Not home, Last to leave and First home. They are worked out when the message goes out. Last to leave is the person whose departure emptied the house: the push about the open back door goes to whoever just walked out of it, and nobody else. You can add your own, such as one person while at home, or everyone in a zone.

### Policies

A policy describes behaviour once and applies to every message with a matching severity and tag. Escalate to more people when nobody reacts. Repeat until someone acknowledges. Keep pushes quiet from 22:00 to 07:00. Hold a push until the person arrives home, or collect messages tagged `digest` into one summary at 20:00.

The leak automation then only says "critical, tag `water`". If nobody acknowledges within five minutes, an escalation policy has the speakers say it and pushes it to the administrators. The automation itself has no loop, no wait and no presence check. The [leak example](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/examples.md#a-leak-that-escalates) lists the policies.

### Keeping track

Acknowledging a message on a phone, the card or a popup stops its escalations and reminders for everyone. A Fallback policy sends a message somewhere else when it reached nobody, for example because nobody was home or the push failed.

When something did not arrive, the Message Log tells you why. It lists each channel with the people and phones it reached and a reason for every skipped delivery, such as "push to Anna skipped: quiet hours".

<img src="https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/panel-message-log.png" width="414" alt="The Message Log trace of a warning: the Persistent Notification and the banner were sent, the push to Anna and Ben was skipped because they have no usable device">


## Get started in the UI

1. In HACS, search for "Heads Up", click Download and restart Home Assistant. It needs Home Assistant 2026.9.0 or newer. Make a backup first.
2. Go to Settings > Devices & services > Add integration > Heads Up. Leave "Show Heads Up in the sidebar" on: it adds the panel, visible to administrators.
3. Open Heads Up in the sidebar. A four-step introduction shows what it found in your Home Assistant and offers four default policies: critical messages pushed at once to the administrators, warnings repeated every 30 minutes up to three times, an evening summary and quiet hours at night. Not now creates nothing.
4. Open Notifications and rules > Test send. Pick channels and an audience, and the table shows who would get the message on which channel, or why not. Send test sends one real message, which ends by itself after 10 minutes.

   <img src="https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/panel-test-send.png" width="480" alt="Test send preview: the banner would be sent to everyone, the push to Anna and Ben skipped for lack of a device, and a reminder policy applies until someone acknowledges">

5. Add the card to a dashboard of your own (the built-in Overview cannot be edited): Edit, Add card, then search for Heads Up.
6. In an automation, add the action Heads Up: Notify and fill in the form. For a banner that shows while an entity is in a state, with no automation at all, add a watch rule under Notifications and rules > Watch rules.

<img src="https://raw.githubusercontent.com/Seyphaton/ha-heads-up/main/docs/images/card-default.png" width="420" alt="The card with four banners: critical, warning, info and success">

## The same in YAML

The call from step 6, for a banner and a push to everyone. A push needs the Companion app on a phone that belongs to a person.

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

Take it back from every channel when the door closes:

```yaml
action: heads_up.clear_notifications
data:
  id: front_door
```

To try a call by hand, use Developer tools > Actions (named Tools in Home Assistant 2026.10) in YAML mode. If nothing arrives, open Notifications and rules > Message Log and select the message.

## Documentation

- [Setup guide](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/setup.md): install, first message, card, panel, introduction, upgrading, uninstalling.
- [Actions, watch rules and card](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/actions.md): every action field, watch rules and the card options.
- [Configuration](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/configuration.md): channels, audiences, recipients and policies.
- [Settings](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/settings.md): every setting and global default, with its limits.
- [Examples and FAQ](https://github.com/Seyphaton/ha-heads-up/blob/main/docs/examples.md): working examples, common questions, troubleshooting and limitations.
- [Security](https://github.com/Seyphaton/ha-heads-up/blob/main/SECURITY.md) and [Changelog](https://github.com/Seyphaton/ha-heads-up/blob/main/CHANGELOG.md).

## License

MIT, see [LICENSE](https://github.com/Seyphaton/ha-heads-up/blob/main/LICENSE).
