# The Heads Up panel

The panel is an administrator page in Home Assistant's sidebar. In this version it has the navigation, the Overview, the Messages page, the four Configuration pages and the Settings page; Test send, Watch rules and FAQ say they are not available yet.

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

## Configuration pages

The editors save through the integration's own forms, so the rules are the same as in Settings > Devices & services > Heads Up, and a change made there shows here. Every editor shows the stored data as YAML and a list of problems; Save is disabled while there are problems. The pages need the hub switched on.

- **Audiences:** the six built-in audiences are listed with who is in them right now. Your own audiences are edited in a form: a name and either a fixed list of persons or a presence (at home, not home, last to leave, first home, in a zone, not in a zone, with a zone choice). The list says which policies use each audience.
- **Recipients:** one profile per person with the devices found automatically, a badge for added devices and for a notify service that is missing, a primary device, devices you removed (which you can bring back), a device you add by name, and the channels the person accepts. A profile that equals the detected devices is not stored. Speaker groups have a name, speakers and areas, and show how the group is written in calls ("Name (group)") and how many speakers reach it now.
- **Policies:** all six types in one form: name, type, severities, tags, enabled and the fields of the type, with a target block per channel for Escalation and Fallback (an audience or recipients, never both; speech takes recipients only; a bell notification takes none). A sentence in words describes the policy as you edit it. A second policy of the same type with the same severities, tags and trigger is refused.
- **Channels:** the push level per severity, the popup style per severity (card, window or off), the lock-screen text, whether the push stays after a tap, the Android channel name and the spoken language. These are the options `push_levels`, `popup_styles`, `push_lockscreen`, `push_sticky`, `push_channel_id` and `speak_language`.

An audience or a speaker group that a policy uses cannot be deleted in the panel: the Delete button is disabled and the page names the policies. Home Assistant's own screen does not enforce this; if it is deleted there, Needs attention on the Overview reports the policy.

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

- Test send, Watch rules and FAQ come in later versions. The Needs attention button for a rule opens a page that says so.
- The pages poll every 10 seconds; they do not update the moment something happens.
- Not tested on a touch device or with a screen reader.
