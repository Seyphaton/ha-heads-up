# The Heads Up panel

The panel is an administrator page in Home Assistant's sidebar. In this version it has the navigation, the Overview, the Messages page and the Settings page; the other pages say they are not available yet.

## Show it in the sidebar

When you add the integration, the first screen asks "Show Heads Up in the sidebar". The switch starts on. You can change it later in two places:

- Settings > Devices & services > Heads Up > Configure: Show Heads Up in the sidebar.
- The panel's own Settings page.

The entry appears and disappears when you save, without a restart. Only administrators see it. An installation that existed before the panel keeps the entry off until you switch it on.

## Navigation

Five groups in a top row: Overview, Notifications and rules, Configuration, Settings, FAQ and examples. A group with more than one page has a second row with its pages (Notifications and rules: Test send, Watch rules, Messages; Configuration: Audiences, Recipients, Policies, Channels). The address of a page is `/heads-up/<page>`, for example `/heads-up/general`. On a narrow screen the page has a menu button that opens Home Assistant's sidebar.

## Overview

The Status page (Overview group) refreshes every 10 seconds.

- **Active notifications:** the number of messages that are active now, with a badge for each state that occurs: escalating, reminding, snoozed, in a summary and acknowledged. Show list opens a list with each message's severity, title and a one-line explanation of each state, for example "Escalation Water sends in 3 min unless someone acknowledges". Watch rule messages are listed too.
- **Watch rules:** "N of M active", with badges for disabled rules and for rules that show a message now. Show list opens every rule with its state and what it watches. Rules are edited under Settings > Devices & services > Heads Up.
- **Needs attention:** each problem with a button to the page that fixes it. Errors: a watch rule on an unavailable or missing entity, a device without a notify service in Home Assistant, a recipient group without an existing speaker, an invalid policy (with the reason), a policy that names a deleted audience or group. Warnings: a person without a usable device, no escalation policy covering critical messages (without a tag), the hub switched off. With none of these the list says nothing needs attention.
- **Last actions:** the latest events, newest first: created (with severity and channels), escalation sent, reminder sent, acknowledged (by whom), dismissed, snoozed, snooze ended, summary sent, fallback sent, delivery skipped or failed (with the reason), expired, cleared.
- A line offers the Settings presets while no policy exists.

## Messages

The Messages page (Notifications and rules group) lists the recent messages, newest first: severity, title, how long ago, whether it is active or how it ended, and a count of its delivery results ("2 sent, 1 skipped"). Choose a message to see its delivery trace: time, channel, recipient and result with the reason; who acknowledged; and the escalations and reminders with their state and due time.

The recent messages and the log of last actions are kept in memory. They start empty after a restart; messages that are still active are listed again with the time they were created, without delivery history. The History settings (trace entries kept, recent messages kept) set the sizes.

## Settings

| Part | What it does |
|---|---|
| Hub | The hub switch (option `hub_enabled`) and the sidebar switch. Off: messages reach only the dashboard banner. |
| Setup wizard | A button for the wizard. It is not available yet. |
| People and devices | Each person with the number of usable Companion devices and whether a Home Assistant user is linked. A person without a device gets only banner and popup; a person without a user gets no popup. |
| Loudness | Three presets. A preset adds the policies it names that do not exist yet and never changes or deletes one. A policy with the same name, or one that does the same as an existing policy, is skipped. |
| Limits | Pushes per device per minute, deliveries per minute for all devices, seconds in which identical updates are ignored. Stored now; not enforced yet. |
| History | Trace entries kept (50 to 5000) and recent messages kept (10 to 1000). |
| Identity | The install token, read only. It is part of every push tag. |

Save is enabled only when something changed and every number is inside its range; the page names a number that is not.

### Presets

| Preset | Adds |
|---|---|
| Quiet | Night quiet: Quiet hours 22:00 to 07:00, send quietly, critical passes. |
| Balanced | Night quiet, Water escalation (critical messages tagged `water` go to the Admins audience by push after 5 minutes) and Evening summary (messages tagged `digest` with severity info or success, one summary at 20:00). |
| Loud | Balanced, plus Warning reminders (every 30 minutes, 3 times, for warnings) and Push failed fallback (a notification in the bell when a push could not be delivered). |

Evening summary only collects messages tagged `digest`, so nothing is held that you did not choose. Edit the policies afterwards in Settings > Devices & services > Heads Up; see [Policies](policies.md).

## Limits

- Test send, Watch rules, Audiences, Recipients, Policies, Channels and FAQ come in later versions. Until then use the integration's own forms; the buttons in Needs attention open those pages and say so while they are not available.
- The pages poll every 10 seconds; they do not update the moment something happens.
- Not tested on a touch device or with a screen reader.
