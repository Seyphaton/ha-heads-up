# Setup guide

This page takes you from nothing to a first message on a phone, a banner on a dashboard and a policy. It also covers upgrading and uninstalling. Every action field is in [Actions](actions.md), every setting in [Settings](settings.md).

## Requirements

- Home Assistant 2026.9.0 or newer, tested on 2026.10.4 and 2026.9.4.
- HACS.
- For push: the Home Assistant Companion app on a phone that belongs to a person.
- For popups: a Home Assistant user linked to a person.

Everything was tested on local Home Assistant instances with stub devices, not on real phones or speakers. Make a backup before you install.

## Install

1. In HACS, search for "Heads Up" and click "Download". To install a pre-release, switch on "Show beta versions" in the download dialog first.
2. Restart Home Assistant. A restart pauses all automations until it has finished.
3. Go to Settings > Devices & services > Add integration and choose Heads Up. The first screen asks "Show Heads Up in the sidebar". Leave it on to get the panel.

The integration registers the card, so you add no dashboard resource. You can change the sidebar switch later in the integration's options (Configure) and on the panel's Settings page. Only administrators see the entry.

## The words

- Message: what an automation sends. It has text, a severity and a lifecycle: it ends when someone closes it, a condition stops matching, a timeout passes or an action clears it. The dashboard banner is one view of a message.
- Channel: where a message appears. The six channels are banner, push, popup, speech, mail and Persistent Notification (Home Assistant's bell).
- Audience: a named group of people that changes over time: Everyone, Admins, At home, Not home, Last to leave, First home, or one you define.
- Recipient: one target inside an audience: a person, a phone or a speaker.
- Policy: a rule for how messages behave, kept apart from the automation: escalate, remind, keep quiet at night, wait until someone is home, fall back to someone else, summarize, deliver at once.
- Hub object: an audience, a speaker group, a recipient profile or a policy. You edit them in the panel or under Settings > Devices & services > Heads Up.
- Acknowledgement: someone saw the message. It stops escalations and reminders; the banner stays for the others.
- Delivery: one message, one recipient, one channel, with a result: sent, held, skipped or failed. The Message Log lists them.

Without any hub object, a message goes to the channels the call names and nothing more.

## Send your first message

The Persistent Notification channel needs no phone, no card and no target, so it is the simplest first test. Open Developer tools > Actions (named Tools in Home Assistant 2026.10), switch to YAML mode and run:

```yaml
action: heads_up.notify
data:
  id: hello
  message: Hello from Heads Up
  channels: [persistent]
```

Open the bell in the sidebar: the entry is there. Take the message back from every channel with its `id`:

```yaml
action: heads_up.clear_notifications
data:
  id: hello
```

### When nothing arrived

Open Heads Up > Notifications and rules > Message Log, choose the message and read the Result column. Every recipient and channel has a result (sent, held, skipped or failed) and a reason, for example `no_usable_device` (the person has no Companion app device) or `rate_limited`. The response of the `notify` call lists the reasons known at the call in `reasons`. The sidebar entry must be on; see Install. Test send, on the same group, shows the same reasons before you send anything. [Examples and FAQ](examples.md#troubleshooting) lists the reasons.

## Add the card

A banner shows in a dashboard card until someone closes it, its condition stops matching, its timeout passes or an action clears it. The built-in Overview dashboard cannot be edited, so use one of your own:

1. Settings > Dashboards > Add dashboard, or open a dashboard you made earlier.
2. Choose the pencil (Edit), then Add card, scroll to the end and choose Manual.
3. Paste this and save:

```yaml
type: custom:heads-up-card
title: House Information
show_time: true
show_severity: true
```

Send a message with the banner channel and a push:

```yaml
action: heads_up.notify
data:
  id: front_door
  title: Front door
  message: The front door has been open for 10 minutes.
  severity: warning
  channels: [banner, push]
  audience: Everyone
```

The banner appears in the card without a reload, and everyone with a Companion app gets a push. When the message ends, both are taken back. All card options are in [Actions, watch rules and card](actions.md#the-card).

## The panel

The panel is an administrator page in the sidebar. Without it you cannot use Test send, the Message Log with the delivery trace, the Overview, the introduction, the Channels settings or the Help pages. Audiences, recipients, policies, watch rules and the other settings stay editable under Settings > Devices & services > Heads Up. Calls, the card and the messages work the same with or without the panel.

Five groups in a top row: Overview, Notifications and rules, Configuration, Settings, Help. A group with several pages shows them as pills. The address of a page is `/heads-up/<page>`, for example `/heads-up/general`.

### Overview

The Status page refreshes every 10 seconds.

- Active notifications: the number of messages that have not ended, with a badge for each state that occurs (escalating, reminding, snoozed, in a summary, acknowledged). Show list explains each message in one line.
- Shortcut cards for Watch rules, Channels, Audiences and Policies. A card opens its page.
- Needs attention: each problem with a button to the page that fixes it. Errors are a watch rule on a missing entity, a device without a notify service, a speaker group without an existing speaker, an invalid policy and a policy that names a deleted audience. Warnings are a person without a usable device, sends that failed in the last 24 hours and no escalation policy for critical messages. Each warning has a Hide button; errors cannot be hidden.
- Last actions: the latest events, newest first, with the reason for a skipped or failed delivery.

### Message Log

Lists the recent messages, newest first: severity, title, how long ago, whether it is active or how it ended, and a count of its results ("2 sent, 1 skipped"). Choose a message to see its trace: time, channel, recipient and result with the reason, who acknowledged, and the escalations and reminders with their state and due time. The log, the recent messages and the failure record are kept in memory and start empty after a restart. The History settings set their sizes.

### Test send

Previews a call and can send it once. Enter the content, the call (severity, tag, channels, policy) and the target of each channel. The result table updates as you type, with one row per recipient and channel: sent, held, skipped or failed, with the reason. A mail row names the address the mail would go to, and a person without an address, or a call with no mail service chosen, shows that reason. The Behaviour choices (dismissible, scope, snoozable) apply to the banner, push and popup; the page says so when a call has only mail and speech, which cannot be taken back. Later steps lists the escalations, reminders and summaries that would follow. The call is shown as YAML with a Copy button.

Send test sends one real message with the title prefix `Test: `, the tag `test` and an id that starts with `hu_test_`. It ends by itself after 10 minutes. Policies apply to it like to any message. Clear the test message removes it at once. Test send uses the real clock and the real presence.

### Watch rules, configuration, settings and help

- Watch rules (Notifications and rules group): lists every rule with its state, what it watches and its message. Add opens an empty form and Edit opens the stored rule. The page saves through the rule form under Settings > Devices & services > Heads Up, so Save, Delete and the error texts are the same. It does not edit a rule's buttons and tap action; it keeps them as they are. See [Watch rules](actions.md#watch-rules).
- Audiences, Recipients, Policies and Channels (Configuration group): see [Configuration](configuration.md).
- Settings: see [Settings](settings.md).
- Help: three pages. FAQ has the questions of [Examples and FAQ](examples.md#frequently-asked-questions) and more. Notify examples has six calls from a banner to a push to one person, each with a Copy button; the names in them are samples, so replace them with your own audiences, persons and speakers. Card examples has six configurations of the card, each with a Copy button. Every Help page links to the project's GitHub issues page.

The panel polls every 10 seconds, so pages do not update the moment something happens. It was not tested on a touch device or with a screen reader.

### The introduction

The first time an administrator opens the panel, a tour of four steps opens: what Heads Up does, the channels, the recipients, and the default policies. Only the last step creates anything, and Not now creates nothing. The Restart introduction button on Settings opens it again.

The last step first asks how policies interact: Only the first policy that applies runs (the default), or Every policy that applies runs. [Configuration](configuration.md#how-policies-interact) explains both. Under the default, the tour offers four policies that do not overlap, in this order:

| Item | What it creates |
|---|---|
| Critical messages | Critical delivery: critical messages are pushed at once to the audience you choose (Admins by default). It also sets the push level of critical messages to critical: the alert on iOS and the alarm channel on Android. A critical message gets this and no reminder. |
| Warning reminders | Warning reminders: a warning nobody acknowledges is repeated every 30 minutes, at most 3 times. |
| Evening summary | Evening summary: info and success messages tagged `digest` are held and sent as one summary at 20:00. |
| Quiet hours | Night quiet: info and success messages without that tag are sent quietly from 22:00 to 07:00. |

Create adds only what is missing. A policy with the same name, or one that does the same as a policy you have, is skipped, and nothing you have is changed or deleted. Edit the policies afterwards on the Policies page.

"Critical delivery" matches every critical message, so it comes first in the list and hides later policies for critical messages. Put a narrower policy, such as an escalation for severity `critical` and tag `water`, above it. The Policies page marks a policy that a policy above it hides.

## Upgrading

1. Make a backup.
2. Read [CHANGELOG.md](../CHANGELOG.md) for the new version.
3. Update Heads Up in HACS.
4. Restart Home Assistant.
5. Reload open dashboards. The card address contains the integration version and a hash of the card file, so a reloaded page loads the new card. If a dashboard still looks old, reload once without cache.

Banners, closed states and timeouts are kept across the restart. So are the timers of escalations and reminders, held messages and the delivery records. Options and watch rules stay. The notification bell is emptied by every restart; Heads Up puts back the entries of active messages. A step that was due during the restart runs once if the message is still active and not acknowledged. A closed rule banner returns after the restart.

From 0.4.0 or earlier to 1.0.0: the field `wait_for_condition` and the response status `condition_false` of `create_banner` are removed, and `mode: recurring` without a `condition` is refused. Delete `wait_for_condition` from your automations. A banner whose condition is false now waits; to send only when the condition is true now, add a condition to the automation before the action.

Heads Up uses [semantic versioning](https://semver.org/). Action names, field names, defaults, response keys, event types, event data keys, the card type and the card options are the public interface. A minor version adds to it. A removal or a change of meaning needs a major version, and the minor version before it logs a warning when you use the old form. The storage file has version 1.

## Uninstalling

1. Remove the card from your dashboards. A card of a removed integration shows "Custom element doesn't exist" after the next reload.
2. Go to Settings > Devices & services > Heads Up, open the menu and choose Delete. This removes your watch rules, the sensor `sensor.heads_up_active_banners`, the audiences, recipient profiles, speaker groups and policies, and deletes `.storage/heads_up.banners`.
3. Remove Heads Up in HACS.
4. Restart Home Assistant.

Deleting the integration does not take back what it already sent. Notifications on phones stay until someone swipes them away, and entries in the bell stay until the next restart or until you dismiss them. Remove the `heads_up.*` calls from your automations and scripts; a call without the integration fails. Heads Up does not change other integrations, automations or scripts, so nothing else needs to be restored.
