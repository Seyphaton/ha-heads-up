# The Heads Up panel

The panel is an administrator page in Home Assistant's sidebar. It has the navigation, the Overview, the Message Log, the Watch rules page, the four Configuration pages, Test send, the Settings page, the introduction and the Help pages.

## Show it in the sidebar

When you add the integration, the first screen asks "Show Heads Up in the sidebar". The switch starts on. You can change it later in two places:

- Settings > Devices & services > Heads Up > Configure: Show Heads Up in the sidebar.
- The panel's own Settings page.

The entry appears and disappears when you save, without a restart. Only administrators see it. On an existing installation the entry is off until you switch it on.

Without the panel you cannot use Test send, the Message Log with the delivery trace, the Overview with Needs attention, the introduction that creates the default policies, the Channels settings (push levels, popup styles, mail) or the Help pages. Audiences, recipients, policies, watch rules and the other settings stay editable under Settings > Devices & services > Heads Up. Calls, the card and the messages themselves work the same with or without the panel.

## Navigation

Five groups in a top row: Overview, Notifications and rules, Configuration, Settings, Help. A group with more than one page shows its pages as pills under the top row (Notifications and rules: Test send, Watch rules, Message Log; Configuration: Audiences, Recipients, Policies, Channels; Help: FAQ, Notify examples, Card examples). The address of a page is `/heads-up/<page>`, for example `/heads-up/general`. On a narrow screen the page has a menu button that opens Home Assistant's sidebar.

## Overview

The Status page (Overview group) refreshes every 10 seconds.

- **Active notifications:** the number of messages that have not ended yet, with a line saying that some wait for an acknowledgement and others come back or escalate. Under it, a badge for each state that occurs: escalating, reminding, snoozed, in a summary and acknowledged. Show list opens a list with each message's severity, title and a one-line explanation of each state, for example "Escalation Water sends in 3 min unless someone acknowledges". Watch rule messages are listed too.
- **Shortcut cards:** Watch rules (the number of enabled rules and how many show a message now), Channels (six, and whether mail is set up), Audiences (built in and your own) and Policies (enabled of all). Choosing a card opens its page.
- **Needs attention:** each problem with a button to the page that fixes it. Errors: a watch rule on an unavailable or missing entity, a device without a notify service in Home Assistant, a recipient group without an existing speaker, an invalid policy (with the reason), a policy that names a deleted audience or group. Warnings: a person without a usable device, no escalation policy covering critical messages (without a tag). A person whose profile does not accept push is not checked for a device. Each warning has a Hide button; hidden warnings are counted under the list and Show again brings them back, while errors cannot be hidden. A warning also appears for sends that failed in the last 24 hours, one per channel and reason, with the count; it links to the Message Log, where the trace of each message gives the details. The record of failed sends is kept in memory, so it starts empty after a restart. With none of these the list says nothing needs attention.
- **Last actions:** the latest events, newest first: created (with severity and channels), escalation sent, reminder sent, acknowledged (by whom), dismissed, snoozed, snooze ended, summary sent, fallback sent, delivery skipped or failed (with the reason), expired, cleared.
- A line offers the introduction while no policy exists.

## Message Log

The Message Log page (Notifications and rules group) lists the recent messages, newest first: severity, title, how long ago, whether it is active or how it ended, and a count of its delivery results ("2 sent, 1 skipped"). Choose a message to see its delivery trace: time, channel, recipient and result with the reason; who acknowledged; and the escalations and reminders with their state and due time.

The recent messages and the log of last actions are kept in memory. They start empty after a restart; messages that are still active are listed again with the time they were created, without delivery history. The History settings (trace entries kept, recent messages kept) set the sizes.

## The introduction

The first time an administrator opens the panel, a tour of four steps opens. Next and Back move between the steps; Skip the tour and Escape close it.

1. What Heads Up does: where a message shows up, who gets it, and when it is loud or quiet.
2. Channels: the six channels in one line each, with the number of app devices and speakers found and whether a notify service is set for mail. Open Channels leaves the tour for that page.
3. Recipients: audiences and profiles, with the number of people, app devices, audiences of your own and speaker groups. Open Audiences and Open Recipients leave the tour for those pages.
4. Policies: four defaults, each with a switch, all on. Create makes the policies of the switched-on items and Not now creates nothing.

Only the last step creates anything. After a visit to a page, a bar above the page offers Continue the tour and End the tour. Closing the tour in any way marks it as seen, so it does not return by itself. The Restart introduction button on Settings opens it again.

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
4. Send test sends one real message and then shows what happened: the delivery results of that message, read from its trace a moment after the send, with the reason for each skipped or failed delivery. The line above the table counts what was planned. It is a normal message with a marker: the title starts with `Test: ` (a message without a title gets the title `Test`), the tag is `test`, the id starts with `hu_test_` and it ends by itself after 10 minutes. Policies apply to it like to any other message. Clear the test message removes it at once.

The preview runs the engine's own planning and the same precedence chain as a delivery, with the real clock and the real presence, so it shows what the same call does now. It stores nothing and sends nothing. A call that `notify` would refuse (an unknown audience, recipient or policy, a missing target) is refused in the preview with the same reason.

## Watch rules

The page opens with a short text: a rule shows a banner while its condition holds and removes it when the condition ends, rules are stored in Heads Up and not in a dashboard so several cards with different filters share them, and an automation that calls `heads_up.create_banner` or `heads_up.notify` with the banner channel and a condition does the same. The page lists every rule with a badge for its state (showing now, not showing, off) and its severity, what it watches and its message. Add opens an empty form and Edit opens the stored rule. Save, Delete and the error texts are those of the rule form under Settings > Devices & services > Heads Up, because the page saves through that form.

The form has four sections. When: an entity in a state (entity, condition, value, optional attribute) or a template, and an optional time the condition must hold. What to show: message, title, severity, icon and image. Who sees it: the people, none meaning everyone. Behaviour: dismissible, dismiss scope, snooze, snooze scope and choices, enabled. A sentence under the form says in words what the rule does.

## Configuration pages

The editors save through the integration's own forms, so the rules are the same as in Settings > Devices & services > Heads Up, and a change made there shows here. Every editor shows the stored data as YAML and a list of problems; Save is disabled while there are problems.

- **Audiences:** the six built-in audiences are listed with who is in them right now. Each has a checkbox: an audience that is switched off is not offered and calls that name it fail with the list of valid names; one that a policy uses cannot be switched off. Your own audiences are edited in a form: a name and either a fixed list of persons or a presence (at home, not home, last to leave, first home, in a zone, not in a zone, with a zone choice). A presence audience can be limited to chosen persons. The list says which policies use each audience.
- **Recipients:** one profile per person with the devices found automatically, a badge for added devices and for a notify service that is missing, a primary device, devices you removed (which you can bring back), a device you add by name, and the channels the person accepts. A profile that equals the detected devices is not stored. Speaker groups have a name, speakers and areas, and show how the group is written in calls ("Name (group)") and how many speakers reach it now.
- **Policies:** all seven types in one form: name, type, severities, tags, enabled and the fields of the type, with a target block per channel for Escalation and Fallback (an audience or recipients, never both; speech takes recipients only; a bell notification takes none). A sentence in words describes the policy as you edit it. A second policy of the same type with the same severities, tags and trigger is refused.
- **Channels:** the push level per severity, the popup style per severity (card, window or off), the lock-screen text, whether the push stays after a tap, the Android channel name, the spoken language and the mail settings (notify service, Global address, subject and body). These are the options `push_levels`, `popup_styles`, `push_lockscreen`, `push_sticky`, `push_channel_id`, `speak_language`, `mail_service`, `mail_global_address`, `mail_subject` and `mail_body`.

An audience or a speaker group that a policy uses cannot be deleted in the panel: the Delete button is disabled and the page names the policies. Home Assistant's own screen does not enforce this; if it is deleted there, Needs attention on the Overview reports the policy.

## Settings

Every block has a heading of its own. The cards of Messages share one heading and have smaller titles.

| Part | What it does |
|---|---|
| Introduction | A button, Restart introduction, that opens the introduction again. |
| Sidebar panel | The sidebar switch (option `show_panel`). |
| Messages | Three clusters under one heading. Dismiss settings: default dismiss scope, default timeout (days, hours, minutes, seconds; empty is none) and the ended-buttons switch. Snooze settings: snoozable by default and the default snooze scope, then the snooze choices of the banner and the snooze time of the push and the popup in their own cards. Each card says which channels it applies to. |
| Presence | The presence delay for Last to leave and First home. |
| Speech | Longest spoken text, repeat pause and the text-to-speech engine. |
| Limits | Maximum number of stored messages and evicting when full, pushes per device per minute, deliveries per minute for all devices, seconds in which identical updates are ignored. The limits are enforced; see [Notification hub](hub.md#limits-that-protect-the-phones). |
| History | Trace entries kept (50 to 5000) and recent messages kept (10 to 1000). |
| Identity | The install token, read only. It is part of every push tag. |
| People and devices | Each person with the number of usable Companion devices and whether a Home Assistant user is linked. A person without a device gets only banner and popup; a person without a user gets no popup. |

Sidebar panel to History are the same entries, in the same order and wording, as Settings > Devices & services > Heads Up > Configure, and a change in one shows in the other. Introduction, Identity and People and devices are only in the panel; the options screen shows the install token at the top.

Save is enabled only when something changed and every number is inside its range; the page names a number that is not.

## Help

The Help group has three pages, shown as pills: FAQ, Notify examples and Card examples.

FAQ has 27 questions that open and close, from a new user's first questions to detailed ones. Longer answers have paragraphs and bullet lists. The first questions cover what Heads Up does, how it differs from Home Assistant's own notify services, what to set up, watch rules, Test send, channels, how to set up mail (SMTP), audiences versus recipients, policies, severity, tags, Android and iPhone, escalations and reminders, how policies are applied, acknowledging versus dismissing, and how to dismiss a message for everyone on all channels. Then come a missing notification, quiet nights, someone not home and summaries. The last ones are for detailed use: several channels in one call, why speech takes no audience, critical messages, rate limits, replacing a phone, a policy added later, and restarts.

Notify examples has six example calls, from a banner without the hub to a push to one person, each with a Copy button. Names such as Anna and Admins are samples.

Card examples has six configurations of `custom:heads-up-card`: the default card, a compact list, only critical and warning banners, one room by tag, a wall tablet for the administrator and your own colours. Each has a Copy button.

The intro line of every Help page ends with a link to the GitHub issues page of the project, for problems and missing features.

`make docs-check` validates every call against the action schemas and every card configuration against the card's options.

## Limits

- The Watch rules page does not edit the buttons and the tap action of a rule; it keeps them as they are. Change them in the rule form under Settings > Devices & services > Heads Up.
- Test send has no "what if" time: it uses the real clock.
- The pages poll every 10 seconds; they do not update the moment something happens.
- Not tested on a touch device or with a screen reader.
