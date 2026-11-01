# The Heads Up panel

The panel is an administrator page in Home Assistant's sidebar. In this version it has the navigation, the Overview, the Messages page, the four Configuration pages, Test send, the Settings page, the welcome and the FAQ and examples page; Watch rules says it is not available yet.

## Show it in the sidebar

When you add the integration, the first screen asks "Show Heads Up in the sidebar". The switch starts on. You can change it later in two places:

- Settings > Devices & services > Heads Up > Configure: Show Heads Up in the sidebar.
- The panel's own Settings page.

The entry appears and disappears when you save, without a restart. Only administrators see it. An installation that existed before the panel keeps the entry off until you switch it on.

## Navigation

Five groups in a top row: Overview, Notifications and rules, Configuration, Settings, FAQ and examples. A group with more than one page shows its pages as pills under the top row (Notifications and rules: Test send, Watch rules, Messages; Configuration: Audiences, Recipients, Policies, Channels). The address of a page is `/heads-up/<page>`, for example `/heads-up/general`. On a narrow screen the page has a menu button that opens Home Assistant's sidebar.

## Overview

The Status page (Overview group) refreshes every 10 seconds.

- **Active notifications:** the number of messages that are active now, with a badge for each state that occurs: escalating, reminding, snoozed, in a summary and acknowledged. Show list opens a list with each message's severity, title and a one-line explanation of each state, for example "Escalation Water sends in 3 min unless someone acknowledges". Watch rule messages are listed too.
- **Watch rules:** "N of M active", with badges for disabled rules and for rules that show a message now. Show list opens every rule with its state and what it watches. Rules are edited under Settings > Devices & services > Heads Up.
- **Needs attention:** each problem with a button to the page that fixes it. Errors: a watch rule on an unavailable or missing entity, a device without a notify service in Home Assistant, a recipient group without an existing speaker, an invalid policy (with the reason), a policy that names a deleted audience or group. Warnings: a person without a usable device, no escalation policy covering critical messages (without a tag), the hub switched off. With none of these the list says nothing needs attention.
- **Last actions:** the latest events, newest first: created (with severity and channels), escalation sent, reminder sent, acknowledged (by whom), dismissed, snoozed, snooze ended, summary sent, fallback sent, delivery skipped or failed (with the reason), expired, cleared.
- A line offers the welcome while no policy exists.

## Messages

The Messages page (Notifications and rules group) lists the recent messages, newest first: severity, title, how long ago, whether it is active or how it ended, and a count of its delivery results ("2 sent, 1 skipped"). Choose a message to see its delivery trace: time, channel, recipient and result with the reason; who acknowledged; and the escalations and reminders with their state and due time.

The recent messages and the log of last actions are kept in memory. They start empty after a restart; messages that are still active are listed again with the time they were created, without delivery history. The History settings (trace entries kept, recent messages kept) set the sizes.

## The welcome

The first time an administrator opens the panel, a dialog explains four defaults. Each has a switch, all on. Create makes the policies of the switched-on items and Not now creates nothing; either way the dialog does not return by itself. The Show the welcome button on Settings opens it again.

| Item | What it creates |
|---|---|
| Quiet hours | Night quiet: Quiet hours 22:00 to 07:00, send quietly, critical passes. |
| Evening summary | Evening summary: messages tagged `digest` are held and sent as one summary at 20:00; critical messages are never held. |
| Critical messages | Critical delivery (a Deliver policy: critical messages are also pushed at once to the audience you choose, Admins by default), Critical reminder (a push again every 10 minutes, at most 3 times) and, if you choose speakers, Critical escalation (after 10 minutes the message is said on those speakers; dismissing counts as acknowledging). It also sets the push level of critical messages to the iOS critical level. |
| Warning reminders | Warning reminders: a warning nobody acknowledges is repeated every 30 minutes, at most 3 times. |

Things to know before you switch on Critical messages:
- It covers every critical message, also those of your existing automations. They get an Acknowledge button on the card and in the push, and a push or speech after 10 minutes without an acknowledgement.
- The iOS critical level needs the Companion app's permission for critical alerts and plays a sound even in silent mode. Android receives it as time sensitive. You can change the push levels on the Channels page.
- Speech passes quiet hours, so a critical message that nobody acknowledges is said on the speakers at night too.
- Evening summary only holds messages that carry the tag `digest`; your automations have to set it.

Create adds only what is missing: a policy with the same name, or one that does the same as a policy you have, is skipped, and nothing you have is changed or deleted. The audience and the speakers are chosen in the dialog because a policy cannot mean "the people of the original call". Edit the policies afterwards on the Policies page.

## Test send

The page (Notifications and rules group) previews a call and can send it once. It has no compose form for real messages.

1. Enter the content (title, message, spoken text for speech), the call (severity, tag, channels, policy: all that apply, none, or one by name) and the target of each channel (an audience or recipients; the banner and the bell need none).
2. The result table updates as you type. It has one row per recipient and channel: sent, held (with the time it is released), skipped or failed, with the reason. A note says when a push goes out quietly. A summary line counts the results per channel, the policies that apply are listed, and Later steps lists the escalations, reminders, away rules and summaries that would follow, with their timing. A fallback that would fire shows its rows marked with its name. A Summarize policy shows every channel held.
3. The call is shown as the YAML of a `heads_up.notify` action, with a Copy call button.
4. Send test sends one real message. It is a normal message with a marker: the title starts with `Test: ` (a message without a title gets the title `Test`), the tag is `test`, the id starts with `hu_test_` and it ends by itself after 10 minutes. Policies apply to it like to any other message. Clear the test message removes it at once.

The preview runs the engine's own planning and the same precedence chain as a delivery, with the real clock and the real presence, so it shows what the same call does now. It stores nothing and sends nothing. A call that `notify` would refuse (an unknown audience, recipient or policy, a missing target) is refused in the preview with the same reason.

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
| Welcome | A button that shows the welcome again. |
| People and devices | Each person with the number of usable Companion devices and whether a Home Assistant user is linked. A person without a device gets only banner and popup; a person without a user gets no popup. |
| Limits | Pushes per device per minute, deliveries per minute for all devices, seconds in which identical updates are ignored. Stored now; not enforced yet. |
| History | Trace entries kept (50 to 5000) and recent messages kept (10 to 1000). |
| Identity | The install token, read only. It is part of every push tag. |

Save is enabled only when something changed and every number is inside its range; the page names a number that is not.

## FAQ and examples

Six example calls, from a banner without the hub to a push to one person, each with a Copy button. Eleven questions open and close: banners without the hub, audience versus direct recipients, why speech takes no audience, several channels in one call, nobody reacting, quiet nights, someone not home, summaries, replacing a phone, a missing notification, and restarts. Names such as Anna and Admins are samples. `make docs-check` validates every example against the action schemas.

## Limits

- Watch rules comes in a later version. The Needs attention button for a rule opens a page that says so.
- Test send has no "what if" time: it uses the real clock.
- The pages poll every 10 seconds; they do not update the moment something happens.
- Not tested on a touch device or with a screen reader.
