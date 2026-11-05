# Heads Up

[![Open your Home Assistant instance and open this repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Seyphaton&repository=ha-heads-up&category=integration)
[![Open your Home Assistant instance and start setting up the Heads Up integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=heads_up)

Heads Up is a notification hub for Home Assistant. Your automations make one call. Heads Up orchestrates where the message shows up, who gets it, and when it is delivered or escalated. It removes the message from every channel when it ends.

![Your automation makes one call, and Heads Up orchestrates where the message shows up (banner, push, popup, speech, mail, Persistent Notification), who gets it (everyone, admins, whoever is home, the last one to leave, one person) and when (quiet at night, repeat until acknowledged, escalate, evening summary, send on arrival).](docs/images/where-who-when.svg)

## What it does

- One call, many **channels**: banner in a dashboard card, Companion app push, popup over any dashboard, speech, mail and the Persistent Notification bell.
- **Audiences** instead of device names: Everyone, Admins, At home, Not home, Last to leave, First home, persons, a zone or a speaker group. Phones are found from the person, so replacing a phone is one change.
- **Policies** kept apart from the automations: escalation, reminder, quiet hours, away, fallback and summary. Acknowledging a message stops its escalations and reminders.
- One **lifecycle** for every channel: a message ends when someone closes it, its condition stops matching, its timeout passes or an action clears it. Then every channel takes it back.
- **Explanations**: the panel previews who a call would reach right now and why anyone is skipped, held or dropped. Each message has a trace.

Banners, watch rules and the card work without any hub object.

## Defaults and limits

| Topic | Behaviour |
|---|---|
| Push rate limit | 5 pushes per device per minute and 60 in total. A push over the limit is skipped and the trace says `rate_limited`. |
| Duplicate updates | An update with the same content is not sent again to the same recipient for 30 seconds (`duplicate`). |
| Critical messages | Never held back by the rate limits or the duplicate check. |
| Push retry | None. A failed push is not tried again. |
| Push buttons | Android shows at most 3, iOS 10. Extra buttons are left out, Snooze first, and the trace says `buttons_clipped`. Acknowledge and Dismiss are kept before the message's own buttons. |
| Spoken text | Cut to 200 characters. The same text is not said again on the same speaker within 60 seconds. |
| Banner timeout | 24 hours unless you set `timeout`. `timeout: 0` keeps the banner until it is cleared. |
| Banner count | 50 stored banners. When the limit is reached, the banner with the lowest severity is removed, the oldest first. Critical banners are never removed this way, and creating a banner fails when none can be. |
| Snooze | Choices of 15 minutes, 1 hour and 4 hours when a banner is snoozable. Banners are not snoozable by default. |
| Memory | The trace keeps 500 entries and the panel lists the last 100 messages. Both start empty after a restart. |

Rate limits, the duplicate window, the banner count and the spoken text settings can be changed in the integration options. See [Notification hub](docs/hub.md#limits-that-protect-the-phones) and [Limitations](docs/limitations.md).

Everything was tested on local Home Assistant instances with stub devices, not on real phones or speakers. Make a backup before you install.

## Requirements

- Home Assistant 2026.9.0 or newer.
- Tested on 2026.10.4 (tests and a local instance) and 2026.9.4 (tests).

## Install

Make a backup first. Installing needs a Home Assistant restart, which pauses all automations until it has finished.

1. In HACS, search for "Heads Up" and click "Download".
2. Restart Home Assistant.

The first button at the top opens the repository in HACS on your Home Assistant. The second opens the setup dialog of the integration after it is installed.

## Set up

Go to Settings > Devices & services and add the integration Heads Up. It asks whether to show Heads Up in the sidebar. The integration registers the card, so you add no dashboard resource. Open the panel to see the introduction.

## Quick start

Send one message to the phones of everyone and the Persistent Notification channel. Developer tools > Actions (YAML mode), an automation or a script can make this call:

```yaml
action: heads_up.notify
data:
  id: water_leak
  message: Water leak
  severity: critical
  channels: [push, persistent]
  to:
    push: {audience: Everyone}
```

Remove the message from every channel with its `id`:

```yaml
action: heads_up.clear
data:
  id: water_leak
```

Use `heads_up.push`, `heads_up.popup` and `heads_up.speak` as shortcuts for one channel. See [How to use Heads Up](docs/how-to.md) for audiences, policies and more examples.

### Banner

A banner stays in a dashboard card until someone closes it, its condition stops matching, its timeout passes or an action clears it. It survives a restart. Add the card to a dashboard in the YAML editor:

```yaml
type: custom:heads-up-card
title: House Information
show_time: true
show_severity: true
```

Create a banner. `heads_up.create_banner` is the shortcut for `heads_up.notify` with `channels: [banner]`:

```yaml
action: heads_up.create_banner
data:
  id: garage_open
  title: Warning
  message: Garage door open after 10pm.
  severity: warning
```

The banner appears in the card without a reload. Close it with the X button, or remove it with `heads_up.clear_banner` or `heads_up.clear_all`.

![Card with four banners: critical, warning, info and success, each with a severity label and the time since it was created](docs/images/card-default.png)

The card receives banners over the Home Assistant WebSocket connection and does not poll. The integration creates one entity, `sensor.heads_up_active_banners`, with the number of active banners, including active watch-rule banners. [Watch rules](docs/rules.md) show a banner while an entity is in a state, without an automation.

## Documentation

- [How to use Heads Up](docs/how-to.md): from the first message to policies, step by step.
- [Actions](docs/actions.md): every field of every action with its default, conditions, errors, events.
- [Settings](docs/settings.md): every setting with its default, including limits.
- [Examples](docs/examples.md): working examples from simple to complex, REST and WebSocket.
- [Notification hub](docs/hub.md): the terms, and examples from a household.
- [Panel](docs/panel.md), [Policies](docs/policies.md), [Audiences and recipients](docs/audiences.md)
- Channels: [Push](docs/push.md), [Popup](docs/popup.md), [Speech](docs/speech.md), [Persistent Notification](docs/persistent.md), [Mail](docs/mail.md)
- [Card](docs/card.md): options, looks and behaviour.
- [Watch rules](docs/rules.md): banners from an entity state or value, without an automation.
- [Troubleshooting](docs/troubleshooting.md)
- [Limitations](docs/limitations.md)
- [Upgrading](docs/upgrading.md) and [uninstalling](docs/uninstall.md)
- [Security](SECURITY.md)

## License

MIT, see [LICENSE](LICENSE).
