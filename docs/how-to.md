# How to use Heads Up

This page takes you from your first message to policies and watch rules. Read it in order, or jump to what you need. Install and set up first, see the [README](../README.md).

| You want to | Go to |
|---|---|
| Send your first message | [1. Send a message](#1-send-a-message) |
| Choose who gets it | [3. Choose who gets it](#3-choose-who-gets-it) |
| Know what a field does and its default | [Actions](actions.md) |
| Know what a setting does and its default | [Settings](settings.md) |
| Copy a working example | [Examples](examples.md) |
| Style the dashboard card | [Card](card.md) |

## The idea

An automation sends one message. A message has text, a severity and a lifecycle. Three questions decide what happens to it:

- Where does it show up? These are the channels: banner, push, popup, speech, mail and the Persistent Notification bell.
- Who gets it? This is an audience such as `At home` or `Admins`, or named persons and speakers.
- When? Policies handle quiet nights, repeats, escalation and summaries, without changing the automation.

When the message ends, every channel takes it back. The terms are in [Notification hub](hub.md).

## 1. Send a message

The action `heads_up.notify` sends a message. The bell needs no card and no target, so it is the simplest first test. Run this in Developer tools > Actions (YAML mode):

```yaml
action: heads_up.notify
data:
  id: hello
  message: Hello from Heads Up.
  channels: [persistent]
```

Open the bell in the sidebar. The entry is there. Take it back from every channel with its `id`:

```yaml
action: heads_up.clear
data:
  id: hello
```

Only `message` and `channels` are required. Without an `id`, Heads Up generates one and returns it in the response. Every field is explained in [Actions](actions.md#heads_upnotify).

## 2. Show it on a dashboard

The channel `banner` shows the message in the Heads Up card. Add the card to a dashboard in the YAML editor:

```yaml
type: custom:heads-up-card
title: House Information
```

Then send a message to the banner:

```yaml
action: heads_up.notify
data:
  id: garage_open
  title: Garage
  message: The garage door is open after 10pm.
  severity: warning
  channels: [banner]
```

The banner appears without a reload. Close it with the X button, or clear it with `heads_up.clear`. Without a `timeout` it ends after 24 hours (setting Default timeout). A banner is the dashboard view of a message, so `heads_up.create_banner` is only the shortcut for this call. See [Card](card.md) for the card's options and looks.

## 3. Choose who gets it

Push and popup need a target. Name an audience for a group that changes over time, or recipients for fixed persons:

```yaml
action: heads_up.notify
data:
  id: garage_open
  title: Garage
  message: The garage door is open after 10pm.
  severity: warning
  channels: [banner, push]
  to:
    push: {audience: At home}
```

The banner is in the card. Everyone who is home gets a push on every Companion app device of their person. Phones are found from the person, so replacing a phone is one change in the recipient profile.

| Audience | Who |
|---|---|
| `Everyone` | Every person. |
| `Admins` | Persons whose user is an administrator. |
| `At home`, `Not home` | Persons by their state. |
| `Last to leave`, `First home` | The person whose departure emptied the house, and the first one back. |

You can add audiences of your own. See [Audiences and recipients](audiences.md). Speech goes to speakers instead (`recipients: [media_player.kitchen]`); see [Speech](speech.md).

## 4. Choose how long it lives

By default a message ends after 24 hours, or earlier when someone closes it. Three fields change that:

- `timeout` sets the time. `0` keeps the message until someone closes or clears it.
- `condition` ties the message to an entity or a template. It shows while the entity matches and ends when it stops.
- `mode: recurring` hides the message while the condition is false and shows it again when it is true.

A banner and a push while a window is open, taken back when it closes:

```yaml
action: heads_up.notify
data:
  id: window_bedroom
  message: The bedroom window is open.
  channels: [banner, push]
  to:
    push: {audience: At home}
  timeout: 0
  condition:
    entity_id: binary_sensor.bedroom_window
    state: "on"
    for:
      minutes: 5
```

The message appears after the window has been open for 5 minutes. All operators, `for` and templates are in [Conditions](actions.md#conditions).

## 5. Let people react

- `dismissible` (default `true`) lets people close the message. `dismiss_scope: global` ends it for everyone instead of only for the person who closed it.
- `snoozable: true` adds Snooze, which hides the message for a while and brings it back.
- `actions` adds up to 3 buttons of your own. A press fires the event `heads_up_banner_action`, which an automation can use.

```yaml
action: heads_up.notify
data:
  id: garage_open
  message: The garage door is open after 10pm.
  channels: [banner, push]
  to:
    push: {audience: At home}
  snoozable: true
  actions:
    - key: light
      label: Outdoor light
```

See [Buttons and snooze](actions.md#buttons-and-snooze) for the event and its automation.

## 6. Use a shortcut

| Action | Same as |
|---|---|
| `heads_up.create_banner` | `notify` with `channels: [banner]`, and `people` for a banner limited to some users |
| `heads_up.push` | `notify` with `channels: [push]` and an `audience` or `recipients` |
| `heads_up.popup` | `notify` with `channels: [popup]` and an `audience` or `recipients` |
| `heads_up.speak` | `notify` with `channels: [speak]` and `recipients` |

A shortcut has no policies. `heads_up.clear` takes back a message from every channel. `heads_up.clear_banner` and `heads_up.clear_all` remove banners only.

## 7. Add behaviour with policies

A policy changes how messages behave without changing the automation. Types: Escalation, Reminder, Quiet hours, Away, Fallback, Deliver and Summarize.

The panel's introduction offers four defaults: quiet hours, an evening summary, critical messages and warning reminders. To escalate a water leak, create an Escalation policy in the panel for severity `critical` and tag `water`, with a push to `Admins` after 5 minutes. If you used the introduction's defaults, drag the new policy above "Critical delivery" in the Policies list: with the default setting only the first matching policy runs, and "Critical delivery" matches every critical message. The Policies page marks a policy that a policy above it hides this way. The automation only sets the severity and the tag:

```yaml
action: heads_up.notify
data:
  id: water_leak
  message: Water on the kitchen floor.
  severity: critical
  tag: water
  channels: [banner, push]
  to:
    push: {audience: At home}
```

If nobody acknowledges the message within 5 minutes, the policy pushes it to the administrators. See [Policies](policies.md).

## 8. Show a banner without an automation

A watch rule shows a banner while an entity is in a state and removes it when the state ends. Add one in the panel's Watch rules page, or under Settings > Devices & services > Heads Up. See [Watch rules](rules.md).

## 9. See what happened

- Test send in the panel previews a call: who it reaches now, and why anyone is skipped, held or dropped.
- The Message Log lists recent messages with the delivery trace of each.
- [Troubleshooting](troubleshooting.md) explains each reason by symptom.

## Reference

| Page | Covers |
|---|---|
| [Actions](actions.md) | Every field of every action, with defaults, conditions, errors and events. |
| [Settings](settings.md) | Every setting with its default, including limits. |
| [Card](card.md) | Every card option, looks and screenshots. |
| [Examples](examples.md) | Working examples from simple to complex, including REST and WebSocket. |
| [Policies](policies.md), [Audiences and recipients](audiences.md), [Watch rules](rules.md) | The hub objects. |
| [Push](push.md), [Popup](popup.md), [Speech](speech.md), [Mail](mail.md), [Persistent notifications](persistent.md) | One page per channel. |
