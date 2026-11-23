# Setup guide

This page takes you from nothing to a first message on a phone, a banner on a dashboard and a policy. It also covers upgrading and uninstalling. Every action field is in [Actions](actions.md), every setting in [Settings](settings.md).

## Requirements

- Home Assistant 2026.9.0 or newer, tested on 2026.10.4 and 2026.9.4.
- HACS.
- For push: the Home Assistant Companion app on a phone that belongs to a person.
- For popups: a Home Assistant user linked to a person.

Make a backup before you install.

## Install

1. In HACS, search for "Heads Up" and click "Download".
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
  severity: warning
  channels: [persistent]
```

Open the bell in the sidebar: the entry is there. Take the message back from every channel with its `id`:

```yaml
action: heads_up.clear_notifications
data:
  id: hello
```

### When nothing arrived

1. Open Heads Up > Test & Logs > Message Log, select the message. A window lists every channel with its result (sent, held, skipped or failed), the people or phones it covers and a reason, for example `no_usable_device` (the person has no Companion app device) or `rate_limited`. The sidebar entry must be on; see Install.
2. Use Test send, in the same group as the Message Log, to see the same reasons before you send anything. `dry_run: true` on the `notify` action does the same from an automation. The response of a `notify` call lists the reasons known at the call in `reasons`.
3. [Examples and FAQ](examples.md#troubleshooting) lists every reason.
4. To report a bug, download diagnostics from Settings > Devices & services > Heads Up. They hold the options, policies, rules, audiences and recipients, the last 200 trace entries and the list of recent messages, without mail addresses and message texts.

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
  audience: binary_sensor.heads_up_audience_everyone
```

The banner appears in the card without a reload, and everyone with a Companion app gets a push. When the message ends, both are taken back. All card options are in [Actions, watch rules and card](actions.md#the-card).

## The panel

The panel is an administrator page in the sidebar. Without it you cannot use Test send, the Message Log with the delivery trace, the Overview, the introduction, the Channels settings or the Help pages. Audiences, recipients, policies, watch rules and the other settings stay editable under Settings > Devices & services > Heads Up. Calls, the card and the messages work the same with or without the panel.

Six groups in a top row: Overview, Configuration, Banner watch rules, Settings, Test & Logs, Help. A group with several pages shows them as pills. The address of a page is `/heads-up/<page>`, for example `/heads-up/general`.

### Overview

The page refreshes every 10 seconds. From the top:

- Status: all clear, or the number of critical and warning messages nobody has acknowledged. Each message has Acknowledge (only while an escalation or reminder policy applies), Snooze 1 h (warnings that allow snoozing), Clear (after a confirmation; a watch rule's message has none, so disable or delete the rule) and Show path, which lists what happened to the message, one line per event, newest first.
- Quick shortcuts: four narrow links under the status card for Channels, Audiences, Policies and Watch rules. Each has an arrow and opens its page.
- Three cards under the shortcuts: Needs attention, Coming up and Last actions, each with a number and one line (errors and warnings; the next scheduled event; the newest message). Select a card and its details slide out below it; select another to switch and the same card again to close. The open card stays open when the page refreshes. The three entries below describe those details.
- Needs attention: each problem with a button to the page that fixes it. Errors are a watch rule on a missing entity, a device without a notify service, a speaker group without an existing speaker, a speaker group with a media player and no usable text-to-speech engine, an invalid policy and a policy that names a deleted audience. Warnings are a person without a usable device, sends that failed in the last 24 hours and no escalation policy for critical messages. Each warning has a Hide button; errors cannot be hidden.
- Coming up: what is about to happen, earliest first. Escalations and reminders that are due, the next summary with the number of messages waiting for it, and the messages held by quiet hours with the time they are sent. It says "Nothing is scheduled." when there is nothing.
- Last actions: the five newest messages, one row each, ordered by their latest activity. The first line has the severity, the title (or the text) and the status: Active, Acknowledged, Snoozed, Resolved (the condition or the watch rule ended), Expired (with how long it lasted), Dismissed, Cleared or Ended. The second line has the time, the channels that delivered and who was reached, for example "To Everyone (3/4 reached, 1 failed)" or "To Last to leave (Ben reached)". Up to three people are named; more are counted. A person you left out on purpose, such as a disabled recipient, is not counted and not shown here; the Message Log lists them. Chips show escalations, reminders, the policy that held the message, the channels that failed and the reasons people were not reached. A message whose delivery details are no longer kept shows no delivery claim. Show path names where the message came from, then lists what happened since it appeared, oldest first, one line per event: "Sent at 13:47 (Banner, Push)", "Reminder sent at 13:57 (Banner, Push, Speak)", "Acknowledged by Ben at 13:58", "Held for summary", "Summary sent", and last how it ended, for example "Expired after 24 h at 13:47". A send that went out quietly names the policy. People who were not reached are named under the send they belong to, with the reason. A failed delivery is a line in red with its reason. A date is added to every line that is not from today. All messages opens the Message Log.
- Activity: pick 24 hours, Week, Month, Year or 2 years. Six numbers in one row (it scrolls sideways on a narrow screen), each with a pill for the change against the period before: Notifications, Failed deliveries, Critical notifications and Escalations as counts (change in percent), and the Quiet hours share and the Summary share (change in percentage points). The quiet hours share is the deliveries that quiet hours held, dropped or sent quietly, of all that could go out (banners and skips for other reasons do not count). The summary share is the messages held for a summary, of all messages. A rise in failures, critical messages or escalations is marked as a warning, a fall as good. A key next to the chart legend names the pill: change against the previous period. Under the numbers a chart of the messages split by severity. For 24 hours, only Notifications cover exactly those hours; the other numbers cover today and yesterday. Where there is nothing to compare with, the pill is a dash: for 2 years, when the period before had none of that number, and while the history does not reach back far enough (it starts when you update, so a year can only be compared with the year before after two years).
- When your house talks: the messages by weekday and hour over the period. It needs a period of a week or more.
- Top sources: the eight sources that made the most messages in the period. A watch rule shows its current name. A call is listed by the ID you gave it, else by its tag; calls with neither are grouped as Other calls, and the panel's Test send as Test send. A call that sets a new ID for every message is grouped as Other calls after 60 IDs a day.
- What would a message do right now?: a table with the channels as rows and Critical, Warning, Info and Passive as columns. Each cell is the result of a test message to Everyone (speech: to every speaker), run through your policies at this moment, and nothing is sent. A cell says Sound, Shown, Quiet, Waits, Skipped or Not set up. When the people differ it adds a count such as "1 of 4": one of four people gets it that way, and the hover lists the others. A cell says Skipped only when nobody is reached. Select a cell for one sentence, the reason and each person's result. The ? next to the title explains the table and shows the time, quiet hours if they are on, who is away, and each summary with the tags it holds.

The Activity cards read a history that Heads Up stores for the last 24 months, one record of counts per day. It holds no titles, texts or addresses, only counts per rule, policy and person, and it survives a restart. Settings > Activity history shows how much is stored and clears it after a confirmation. The history starts when you update; messages from before are not counted.

Before the first policy exists, the page shows the introduction on top and, under it, empty cards for Needs attention, Coming up, Activity and Last actions with a line on what each will show.

### Message Log

Lists the recent messages, newest first: severity, title, then the status, the time, the channels that delivered and who was reached, in the same words as Last actions on the Overview. Select a message to open its trace in a window (a sheet on a phone): who was reached, who acknowledged, the people you left out on purpose (for example a disabled recipient) under "Not sent on purpose", then one group per channel and result, oldest first, with the names of the people and phones, how long ago it happened and the reason, and the escalations and reminders with their state and due time. Close it with the × button, Escape or a tap outside. The delivery trace is stored and survives a restart. The log of last actions, the recent messages and the failure record are kept in memory and start empty after a restart. The History settings set their sizes. The action `heads_up.get_trace` returns the trace to an automation or a script; see [Actions](actions.md#heads_upget_trace).

### Test send

Previews a call and can send it once. Enter the content, the call (severity, tag, channels, policy) and the target of each channel. The result table updates as you type, with one row per recipient and channel: sent, held, skipped or failed, with the reason. A mail row names the address the mail would go to, and a person without an address, or a call with no mail service chosen, shows that reason. The Behaviour choices (dismissible, scope, snoozable) apply to the banner, push and popup; the page says so when a call has only mail and speech, which cannot be taken back. Later steps lists the escalations, reminders and summaries that would follow. The call is shown as YAML with a Copy button.

Under the form, Test a pasted call takes an action step or only its `data`. Templates such as `{{ trigger.entity_id }}` are rendered with the sample values you give as YAML, for example `trigger: {entity_id: binary_sensor.door}`, as Home Assistant renders them before it calls the action. Show plan renders the call and shows the same table as the form, with the push level of each push row, and sends nothing. Send test sends the rendered call as a test message, like the button above. Only `heads_up.notify` can be tested, and a `dry_run` in the pasted call is ignored.

Send test sends one real message with the title prefix `Test: `, the tag `test` and an id that starts with `hu_test_`. It ends by itself after 10 minutes. Policies apply to it like to any message. Clear the test message removes it at once. Test send uses the real clock and the real presence.

### Watch rules, configuration, settings and help

- Banner watch rules: a table of the rules with what each watches and what it shows, with a badge for its state. Open a row for the details, Edit and Switch off. New watch rule and Edit open the form in a window; closing it with unsaved changes asks first. The page saves through the rule form under Settings > Devices & services > Heads Up, so Save, Delete and the error texts are the same. It does not edit a rule's buttons and tap action; it keeps them as they are. See [Watch rules](actions.md#watch-rules).
- Audiences, Recipients, Policies and Channels (Configuration group): see [Configuration](configuration.md).
- Settings: see [Settings](settings.md).
- Help: three pages. FAQ has the questions of [Examples and FAQ](examples.md#frequently-asked-questions) and more. Notify examples has six calls from a banner to a push to one person, each with a Copy button; the names in them are samples, so replace them with your own audiences, persons and speakers. Card examples has six configurations of the card, each with a Copy button. Every Help page links to the project's GitHub issues page.

The panel polls every 10 seconds, so pages do not update the moment something happens.

### The introduction

The first time an administrator opens the panel, the Overview shows a tour of four steps above its cards. While the tour has not been seen, a visit to any other page opens the Overview. The Restart introduction button on Settings opens it again.

1. Introduction: Channels decide where a message shows up, Audiences decide who gets it, Policies decide when.
2. Channels: the six channels with what was found. Two settings are here: the notify service for mail with an optional global address, and the text-to-speech engine when Home Assistant has more than one. Mail is only set up here; none of the default policies sends mail. The settings are saved when you leave the step with Next or Back, so they stay if you stop the tour later.
3. Audiences: the six built-in audiences with the people in them now and whether each is home or away. Last to leave and First home show when it happened. Select a card to read what the audience means, with an example.
4. Policies: the three groups, Keep it calm, Always gets through and Make sure it arrives, and four default policies, each marked with its group. Create says how many policies it makes. Critical messages makes three, or four when you choose speakers. Policies are created only in this step; Skip the tour and Not now create none.

The last step offers four items:

| Item | What it creates |
|---|---|
| Critical messages | The Get through entry Critical, so critical messages pass quiet hours and summaries for everyone. Critical delivery: critical messages are pushed at once to the audience you choose (Admins by default). Critical reminder: every 10 minutes, at most 3 times. With speakers: Critical escalation, said after 10 minutes. It also sets the push level of critical messages back to critical, the alert on iOS and the alarm channel on Android, if it was changed. |
| Warning reminders | Warning reminders: a warning nobody acknowledges is repeated every 30 minutes, at most 3 times. |
| Evening summary | Evening summary: messages tagged `digest` are held and sent as one summary at 20:00. |
| Quiet hours | Night quiet: from 22:00 to 07:00 pushes go out without sound and speech is skipped, except for messages tagged `digest`. |

Create adds only what is missing. A policy with the same name, or one that does the same as a policy you have, is skipped, and nothing you have is changed or deleted. Edit the policies afterwards on the Policies page. When you choose speakers and Home Assistant has more than one text-to-speech engine, the Critical item asks which engine to use.

## Upgrading

1. Make a backup.
2. Read [CHANGELOG.md](../CHANGELOG.md) for the new version.
3. Update Heads Up in HACS.
4. Restart Home Assistant.
5. Reload open dashboards. The card address contains the integration version and a hash of the card file, so a reloaded page loads the new card. If a dashboard still looks old, reload once without cache.

Banners, closed states and timeouts are kept across the restart. So are the timers of escalations and reminders, held messages and the delivery records. Options and watch rules stay. The notification bell is emptied by every restart; Heads Up puts back the entries of active messages. A step that was due during the restart runs once if the message is still active and not acknowledged. A closed rule banner returns after the restart.

From 0.4.0 or earlier to 1.0.0: the field `wait_for_condition` and the response status `condition_false` of `create_banner` are removed, and `mode: recurring` without a `condition` is refused. A call that still sends `wait_for_condition` works: Heads Up ignores the field and shows a repair notice under Settings > System > Repairs. Delete the field from your automations. A banner whose condition is false now waits; to send only when the condition is true now, add a condition to the automation before the action. The action `heads_up.notify` needs a `severity`.

From an earlier 1.0.0 pre-release to 1.0.0: Heads Up stores policies, audiences and groups by an ID instead of by name, so a rename changes nothing that runs. The first start after the update converts the watch rules, the policy targets, the stored messages and the timers, keeps every due time, and writes a backup of the old data to `.storage/heads_up.migration_v2` first. The backup is written once and never overwritten. A group or an area written as text in a call fails now: name a group by the entity ID of its sensor (`sensor.heads_up_group_ground_floor`) and an area by its area ID. The speakers field of the action offers the group sensors.

From 1.0.0 to 1.1.0: Away policies become Presence policies. They behave as before, except that a person the call names in `recipients` is held too. The first start after the update writes a backup of the policies to `.storage/heads_up.migration_v2_2` first. The severity `success` is renamed to `passive` in the settings, policies, watch rules and stored messages; calls that send `success` keep working. Your push levels stay as they were.

From 1.x to 2.0.0: policies no longer run in a list order or a mode. Every policy that fits a message acts. The first start converts your policies so that they do what they did:

- A policy that came below another one in the list leaves out the messages that one handled, written as Not for. Example: Night quiet came below Evening summary (messages tagged `digest`), so it gets Not for the tag `digest`. Where Not for cannot say it, because the policy above names a severity and a tag together, the policy leaves out those messages while the one above is switched on.
- Where critical messages passed quiet hours or summaries, a Get through entry Critical is added. A Quiet hours or Summarize policy that held critical messages gets Holds these anyway. A Presence policy that let critical messages pass gets Not for severities Critical.
- Setups on "Every policy that applies runs" get the 2.0 rules: two reminders on one channel share the shorter rhythm instead of both repeating.

The Policies page shows "The policy feature has been updated – please review the new behaviour" with every policy the update changed this way, or that now does nothing. For each, choose Keep it like this or Apply to them too. When every item is answered, the list is gone the next time you open the page; Hide this list removes it earlier. 1.x cannot read the converted setup: make a backup before you update, and restore it to go back.

To go back to an earlier 1.x release, stop Home Assistant, run `python scripts/restore_identity_backup.py <config folder>` from the repository, then install the earlier release. To go back from 1.1.0 to 1.0.0, run `python scripts/restore_presence_backup.py <config folder>` instead. It puts the Away policies back and renames `passive` to `success` again, because 1.0.0 knows neither Presence nor `passive`. Without the restore, Home Assistant refuses to set up the converted data in an older release instead of reading it wrongly.

Heads Up uses [semantic versioning](https://semver.org/). Action names, field names, defaults, response keys, event types, event data keys, the card type and the card options are the public interface. A minor version adds to it. A removal or a change of meaning needs a major version, and the minor version before it logs a warning when you use the old form. The stored data has version 3.

## Uninstalling

1. Remove the card from your dashboards. A card of a removed integration shows "Custom element doesn't exist" after the next reload.
2. Go to Settings > Devices & services > Heads Up, open the menu and choose Delete. This removes your watch rules, the sensor `sensor.heads_up_active_banners`, the audiences, recipient profiles, speaker groups and policies, and deletes `.storage/heads_up.banners` and `.storage/heads_up.stats`.
3. Remove Heads Up in HACS.
4. Restart Home Assistant.

Deleting the integration does not take back what it already sent. Notifications on phones stay until someone swipes them away, and entries in the bell stay until the next restart or until you dismiss them. Remove the `heads_up.*` calls from your automations and scripts; a call without the integration fails. Heads Up does not change other integrations, automations or scripts, so nothing else needs to be restored.
