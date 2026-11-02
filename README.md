# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up is a central hub for notifications in Home Assistant. Automations, scripts and external programs say what happened. Heads Up decides who is told, on which channel and how loudly, and keeps every channel in step.

## What it solves

- **Notifications are scattered.** Every automation and script hard-codes phones, speakers and quiet-hour templates. Replace a phone and you edit thirty automations.
- **Banners are inconsistent.** Each setup builds its own dashboard banner, with its own lifecycle. Heads Up has one banner with a timeout, a condition, a closed state per person and a snooze.
- **There are no critical popups.** A critical alert looks like any other message. Heads Up shows it as a window over any dashboard.
- **There is no escalation.** A critical alert that nobody read stays unread. Heads Up notifies more people or channels after a delay, until someone acknowledges it.
- **There are no reminders.** A message is sent once and forgotten. Heads Up repeats it while nobody acknowledges it.
- **Channels disagree.** Closed on the phone, still on the wall tablet, spoken again. Heads Up takes a message back on every channel when it is cleared or expires, and for a person when that person closes it.

## What it does

**Banner.** Dismissible banners in a dashboard card. They stay until someone closes them, a condition on an entity stops matching, a timeout passes, or an action clears them, and they survive a restart. Watch rules show a banner while an entity is in a state, without an automation.

**Push, popup, speech and the notification bell.** The same message reaches Companion app notifications, windows over any dashboard, speakers and Assist satellites, and Home Assistant's notification bell. One action, `heads_up.notify`, names the channels. Each channel can also be called alone.

**Audiences and recipients.** Send to Everyone, Admins, At home, Not home, Last to leave, First home, to persons, to a zone, or to a speaker group. Phones are found from the person. Replace a phone once, in one place.

**Policies.** Rules for how messages behave, kept apart from the automations: Escalation, Reminder, Quiet hours, Away, Fallback, Summarize and Deliver. A welcome in the panel offers four defaults: quiet hours, an evening summary, critical messages and warning reminders.

**Acknowledgement.** Someone saw the message. It stops escalations and reminders, and the card shows who.

**Explanation.** The panel previews who a call would reach right now and why anyone is skipped, held or dropped. It keeps a trace for each message. Rate limits stop a flood: 5 pushes per device per minute and 60 in total, never for critical.

**Panel.** An administrator page in the sidebar with the overview, the messages, the editors for audiences, recipients, policies and channels, test send, settings, FAQ and examples. See [Panel](docs/panel.md).

Everything the banner did before still works without any hub object. The hub is on by default and can be switched off in the settings.

**Every option with examples: [How to use Heads Up](docs/how-to.md). The concepts: [Notification hub](docs/hub.md).**

Status: version 0.4.0 is the last release. The hub and the panel are not released yet. Everything was tested on local development instances of Home Assistant with stub devices only, not on real phones or speakers. Make a backup before you install it.

## Requirements

- Home Assistant 2026.9.0 or newer.
- Tested on Home Assistant 2026.10.4 (tests and a local instance) and 2026.9.4 (tests).

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

Go to Settings > Devices & services and add the integration Heads Up. It asks whether to show Heads Up in the sidebar. The card is registered by the integration, so you do not add a dashboard resource. Open the panel to see the welcome.

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

Send one message to the banner, the phones of the people at home and the notification bell:

```yaml
action: heads_up.notify
data:
  message: Water leak
  severity: critical
  channels: [banner, push, persistent]
  to:
    push: {audience: Everyone}
```

## How it works

The card receives banners over the Home Assistant WebSocket connection and updates when a banner changes. It does not poll. The integration creates one entity, `sensor.heads_up_active_banners`, with the number of active banners, including active watch-rule banners.

## Documentation

- [How to use Heads Up](docs/how-to.md): every option with examples and screenshots.
- [Notification hub](docs/hub.md): the words used, and examples from a household.
- [Panel](docs/panel.md), [Policies](docs/policies.md), [Audiences and recipients](docs/audiences.md)
- Channels: [Push](docs/push.md), [Popup](docs/popup.md), [Speech](docs/speech.md), [Notification bell](docs/persistent.md)
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
