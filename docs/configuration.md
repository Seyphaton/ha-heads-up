# Configuration: channels, audiences, recipients and policies

These are the hub objects and the channel settings. A call says what to send (see [Actions](actions.md)); this page says who is reached, how each channel behaves and which policies shape the delivery.

Create and edit them in the panel (Configuration group: Audiences, Recipients, Policies, Channels) or under Settings > Devices & services > Heads Up (Add entry, pencil to edit). Both save to the same entries, so a change in one shows in the other. Each panel editor shows the stored data as YAML and a list of problems; Save is disabled while there are problems. An audience or speaker group that a policy uses cannot be deleted in the panel: the Delete button is disabled and the page names the policies. Home Assistant's own screen does not enforce this. If it is deleted there, the policy cannot run, the Message Log shows `audience_missing` or `group_missing`, and Needs attention on the Overview reports the policy.

## Channels

A call names its channels in `channels`. Push, popup and mail take `recipients` or `audience`, speech takes `speakers`. The banner takes `recipients` or `audience` too, or shows to everyone without them. The Persistent Notification takes no target.

| Channel | Target in `notify` | Shortcut action |
|---|---|---|
| `banner` | none, or `recipients`/`audience` to limit who sees it | `create_banner` |
| `push` | `audience` or `recipients` (persons, phones) | `push` |
| `popup` | `audience` or `recipients` (persons) | `popup` |
| `speak` | `speakers` (speakers, Assist satellites, groups, areas) | `speak` |
| `mail` | `audience` or `recipients` (persons, `Global address`) | none |
| `persistent` | none | none |

The panel's Channels page sets the options below. They are stored in the integration options; [Settings](settings.md) lists every option with its default.

| Option | Default | Meaning |
|---|---|---|
| `push_levels` | success and info `passive`, warning `normal`, critical `time-sensitive` | Push level per severity. |
| `push_lockscreen` | `full` | `full` shows title and text. `title_only` shows the title and a fixed line. `generic` shows "Heads Up" and a fixed line. |
| `push_channel_id` | `heads_up` | Prefix of the Android notification channel. |
| `push_sticky` | off | Keeps the notification after a tap (Android). |
| `popup_styles` | corner card (bottom right) for success, info and warning, centered window for critical | Per severity: `card` (bottom right), `card_bottom_left`, `card_top_right`, `card_top_left`, `modal` (centered window) or `off`. The Channels page words them as the corner or the centered window. |
| `speak_language` | the Home Assistant language | Language of the spoken text. |
| `mail_service`, `mail_global_address`, `mail_subject`, `mail_body` | none, none, `{severity}: {title}`, `{message}` | The mail channel, see Mail below. |

### Push

The push channel sends a message to the Home Assistant Companion app on the phones and tablets of the people you target. It calls the services `notify.mobile_app_<device name>`, not the notify entities, because only the services pass `tag`, `actions` and `clear_notification` on to the app.

```yaml
action: heads_up.notify
data:
  id: garage_open
  title: Garage
  message: The garage door has been open for 10 minutes.
  severity: warning
  channels: [push]
  audience: binary_sensor.heads_up_audience_at_home
```

Every device of a person gets the notification. A person with no usable device, a device whose notify service does not exist and a profile that does not accept push are skipped, and the Message Log says why (`no_usable_device`, `service_not_found`, `channel_not_accepted`). The response counts of `notify` come from the plan made before sending: `sent` means the notification was handed to the app's service. A service that then fails shows as a failed delivery in the Message Log.

| Part | Value |
|---|---|
| Title and text | The message's `title` and `message`. |
| `tag` | `hu-<install token>-<message id>`. A new notification with the same tag replaces the old one on the device. |
| `group` | `hu-<install token>`. |
| Level | By severity: `success` and `info` passive, `warning` normal, `critical` time-sensitive until you set the level critical. Passive is `importance: low`, normal `default`, time-sensitive `high`, critical `max`. |
| Android delivery | For time-sensitive and critical: `priority: high` and `ttl: 0`, so an idle phone shows the notification at once. |
| Android channel | `heads_up_<level>`; the level critical uses the channel `alarm_stream`, which plays from the alarm stream. Android keeps the importance a channel had when it was first used. |
| Tap | A `navigate` tap action opens its `navigation_path`, a `url` tap action its `url_path`. |
| Image | The message's `image` as `data.image`. Left out when the lock screen setting is not `full` (`image_hidden`). Camera proxy paths work on Android only. |
| Buttons | The message's own `actions`, then Snooze when the message is snoozable, then Dismiss when it is dismissible. Android shows at most 3 buttons and iOS 10. Extra buttons are left out (`buttons_clipped:<n>`): Acknowledge and Dismiss are kept first, then the message's own buttons in order, and Snooze goes first. |

The level critical is an alarm on both platforms. On iOS it is the critical alert: it needs the app's permission, plays a sound regardless of silent mode and cannot be replaced, so the hub clears it and sends a new one on an update. On Android it uses the alarm channel, so it sounds in vibrate and silent mode. Do Not Disturb is overridden only if you allow it for that channel in the Android settings.

A message that ends (cleared, expired, condition false, dismissed for everyone, evicted) is removed from every device. Heads Up asks the app to remove it (`clear_notification` with the tag), and the Message Log shows a `cleared` row per device when it did. Whether the phone then removes it is up to the app: the Companion app documents that iOS, and Android for notifications that are not critical, may need the app to have been used recently for a clear to work, and that on iOS only the most recent critical notification per tag is cleared. The documentation says nothing about macOS. A user who dismisses or snoozes the banner loses only their own notification, and when a snooze ends that user is notified again. Swiping a notification away changes nothing. An update to a message replaces the notification in place.

Pressing Acknowledge, Dismiss, Snooze or one of the message's own buttons does the same as pressing it on the banner, for the person the notification was sent to. Snooze uses one time, the option Snooze time on push and popup (15 minutes by default). The button ID is `hu:<message>:<person>:<action>`. If the event carries a Home Assistant user that is not the person's user, the press is ignored (`user_mismatch`); a press for a message that no longer exists is ignored (`stale_message`). Buttons of other automations are not touched.

Limits: a failed push is not tried again; a push over 5 per device per minute or 60 in total is skipped (`rate_limited`); an update with the same content within 30 seconds is ignored (`duplicate`); critical messages are never held back. The Acknowledge button appears only when an escalation or reminder policy applies. Pushes were tested with a stand-in for the app, not with a real phone.

### Popup

The popup channel shows a message on top of any dashboard, for the people you target. It needs no card: Heads Up adds one small script (under 1 KB) to every page, which loads the popup code only when a popup is due.

```yaml
action: heads_up.notify
data:
  id: garage_open
  title: Garage
  message: The garage door has been open for 10 minutes.
  severity: warning
  channels: [popup]
  audience: binary_sensor.heads_up_audience_at_home
```

A popup goes to persons, by audience or by `recipients`. A person needs a linked Home Assistant user; a person without one is skipped (`no_user`). The popup appears on every dashboard and device where that user has Home Assistant open. Areas are not supported.

- Each severity is shown as a card in one of the four corners (bottom right by default for success, info and warning), as a centered window over a dimmed page (the default for critical) or not at all. At phone width a card spans the screen and sits at the top or the bottom, as chosen; left and right make no difference there. A quiet message (Quiet hours with the action Send quietly) is always a card.
- An `image` shows under the text, up to 200 px high; a picture that does not load is left out.
- Buttons are at least 48 px high: the message's own, Acknowledge when an escalation or reminder policy applies, Snooze when the message is snoozable, Dismiss when it can be dismissed. A button's `action` is not run by the popup; only `heads_up_banner_action` is fired.
- One popup is shown at a time, highest severity first, then the oldest. The close button and Escape hide the popup on that page only and the popup returns after a reload. Dismiss hides it for you on every device and keeps the message for others. Acknowledge stops escalation and reminders.
- A critical window takes keyboard focus and keeps Tab inside. With reduced motion set in the system, nothing is animated. When the message ends, the popup closes.

Popups need an open Home Assistant page; use push for a closed app. The popup is not shown on the login page, and it was not tested with a screen reader.

### Speech

The speak channel says a message on speakers: media players and Assist satellites. Use `heads_up.notify` with `channels: [speak]` or the `heads_up.speak` shortcut.

```yaml
action: heads_up.speak
data:
  id: garage_open
  message: The garage door has been open for 10 minutes.
  recipients:
    - media_player.kitchen
    - sensor.heads_up_group_ground_floor
```

`recipients` are media players, Assist satellites, speaker groups and areas. A group is written as the entity ID of its sensor. An area is written by its area ID (`living_room`) and needs no group; it stands for the speakers assigned to it. A group or area written as its name fails with the ID to use. Speech has no audience: it goes to speakers, not to people.

The text is `tts_message` if you set it, otherwise the title, otherwise the message. A text longer than 200 characters is cut after the last word that fits and ends with `…` (option Spoken text: longest).

| Speaker | What Heads Up calls |
|---|---|
| Assist satellite | `assist_satellite.announce` |
| Media player that supports announcements | `tts.speak`, which announces; the player lowers or pauses what it plays and continues afterwards, if the player does that |
| Other media player | `media_player.play_media` with the text-to-speech media source, as plain playback |

- The text-to-speech engine is the option Text-to-speech engine. If it is empty and exactly one `tts` entity exists, that one is used. With several or none, speech to media players fails with `no_tts_engine`.
- Heads Up never changes or restores a volume. What happens to music after an announcement depends on the player.
- A speaker says one message at a time. The same text is not said again on the same speaker within 60 seconds (option Spoken text: repeat pause, 0 for no pause; the Message Log shows `cooldown`). An update does not say a message again (`already_spoken`).
- Speech cannot be taken back. A Quiet hours policy with the action Send quietly skips speech (`quiet_hours`).
- An area or group with no speaker, and a speaker that no longer exists, also leave one entry in the notification bell ("Heads Up: no speaker" or "Heads Up: speaker not found"). It names the area, group or speaker and never the message, because every user sees the bell.
- A missing speaker, a missing service and a missing engine are failed deliveries (`entity_missing`, `service_not_found`, `send_failed`, `no_tts_engine`) and write a log warning, at most one per speaker per hour. Skips are written at debug level. Test send shows each result with its reason.

There is no all-clear announcement and no volume handling. Rooms are Home Assistant areas and their assigned speakers; occupancy is not used. Speech was not tested on a real speaker.

### Persistent Notification

The persistent channel shows a message in Home Assistant's notification list, the bell in the sidebar. Use `heads_up.notify` with `channels: [persistent]`.

```yaml
action: heads_up.notify
data:
  id: backup_failed
  title: Backup
  message: The nightly backup failed.
  severity: warning
  channels: [banner, persistent]
```

Everyone who uses Home Assistant sees the entry: the bell has one list for all users. Use push or popups to reach single people.

- One entry per message, with the id `hu_<message id>`. An update replaces the entry.
- When the message ends, the entry is dismissed. A dismissal or snooze by one user changes nothing, because the bell is shared.
- Home Assistant empties the bell on a restart. At startup Heads Up creates the entry again for every message that is still active, with the same id, and dismisses entries whose message ended meanwhile.
- Dismissing the entry in the bell is not reported back to Heads Up. The message stays; a later update creates the entry again.
- A missing `persistent_notification` service or a failing call is a failed delivery (`service_not_found`, `send_failed`).
- No per-user entries, no buttons, no Acknowledge or Snooze. A rule message reaches the bell only through an escalation or fallback policy.

### Mail

The mail channel calls a Home Assistant notify service once per recipient, with a subject and a body. Use `heads_up.notify` with `channels: [mail]`. It works with any notify service that takes `title`, `message` and `target`, for example the SMTP integration. Heads Up does not send e-mail itself, so mail does not work until a mail notify service exists.

```yaml
action: heads_up.notify
data:
  id: water_leak
  title: Water leak
  message: The basement sensor is wet.
  severity: critical
  channels: [push, mail]
  audience: binary_sensor.heads_up_audience_admins
        - Global address
```

Set it up:

1. Add the SMTP integration under Settings > Devices & services. It asks for the server, port, connection security, sender, user name and password, and creates a notify service named after the entry.
2. Open the panel, Configuration, Channels, section Mail, and choose that notify service. Without one, mail fails with `no_mail_service`.
3. Optional: enter a Global address.
4. Open Recipients. For each person who gets mail, switch Mail on and enter the person's mail address.

Mail is off for everyone until step 4, so an audience such as Everyone reaches only the persons who opted in.

| Recipient | What happens |
|---|---|
| A person with Mail on and an address | One call of the notify service with `target: [address]`. |
| A person with Mail on and no address | Fails with `no_mail_address` and a log warning. The Global address is not used instead. |
| A person with Mail off | Skipped with `channel_not_accepted`. |
| `Global address` | One call with the Global address as the target. Fails with `no_mail_address` while the setting is empty. Audiences never include it; name it in `recipients`. |

Subject and body are placeholder texts, not Home Assistant templates. The defaults are subject `{severity}: {title}` and body `{message}`.

| Placeholder | Value |
|---|---|
| `{severity}` | The severity as a word in your Home Assistant language, for example Critical. |
| `{title}` | The title, or the message when there is no title. |
| `{message}` | The message. |
| `{person}` | The person's name (the friendly name of the person entity); empty for the Global address. |
| `{person_id}` | The part of the person's entity ID after `person.`, for example `philip` for `person.philip`. It is lower case and has no spaces, whatever the friendly name says; empty for the Global address. |
| `{id}` | The message id. |
| `{tag}` | The tag; empty when there is none. |

Any other `{name}` is refused when you save. A subject has at most 200 characters, a body at most 2000. The notify service receives the subject as `title` and the body as `message`. For a shared mailbox that tells recipients apart by subject, give every person the mailbox as their address and set the subject to `{person}`.

A single message can use its own subject and body with the `mail_subject` and `mail_body` fields of [`heads_up.notify`](actions.md#mail-text-of-this-message). They replace these two texts for that message only.

A mail cannot be taken back: clearing, dismissing or ending the message sends nothing and removes nothing. An update does not send the mail again (`already_sent`). Speech cooldown and buttons do not apply; images and buttons are not sent. A failed call or a missing address fires `heads_up_delivery_failed` (see [Actions](actions.md#events)). A Quiet hours policy with the action Drop or Wait applies to mail.

Delivery is the notify service's job: Heads Up knows only whether the call returned an error. After a mail went through the SMTP integration's notify service, the SMTP integration raises a repair that the service is deprecated and due to be removed in Home Assistant 2027.3. Mail was not tested with a real mail server.

## Audiences

These objects say who a call is for. An audience applies to push, popup, mail and, for who sees it, the banner. Speech takes recipients instead; the Persistent Notification takes no target.

An audience is a named group of people. Every audience is a sensor, and a call names the audience by the entity ID of its sensor: `to: {push: {audience: binary_sensor.heads_up_audience_at_home}}`. The audience editor shows the ID, and a rename does not change it. Membership is worked out when the message is delivered. For the banner channel it is worked out once, when the banner is created.

| Name | Who |
|---|---|
| `Everyone` | Every person. |
| `Admins` | Persons whose Home Assistant user is an administrator. |
| `At home` | Persons whose state is `home`. |
| `Not home` | Persons whose state is anything else, including a zone. |
| `Last to leave` | The person whose departure emptied the house. Nobody while anyone is home. |
| `First home` | The first person home after the house was empty. Nobody while the house is empty. |

The panel lists the six built-in audiences with who is in them right now. Each has a checkbox: one that is switched off is not offered and a call that names it fails with the list of valid names; one that a policy uses cannot be switched off.

You can add your own audience, either as a fixed list of persons or as a presence: at home, not home, last to leave, first home, in a zone, not in a zone (with a zone). A presence audience can be limited to chosen persons, for example At home for one person only. A limited Last to leave or First home names the person only when that person is also the last to leave or the first home of the whole house; it does not look for the last of the chosen persons. A custom name must differ, ignoring case, from the built-in names and from other audiences. The panel lists which policies use each audience.

A person whose state is `unknown`, `unavailable` or who has no usable tracker has unknown presence. Presence audiences include that person for `critical` messages and skip them for lower severities (`presence_unknown`). Last to leave and First home change only after a person has been home or away for the presence delay (option Presence delay, 60 seconds by default, 0 for no delay), so a flapping location fix does not move them. Both are kept across restarts.

## Recipients

Every person has a recipient profile without any setup. Their Companion app devices are found through the person's trackers; trackers from other integrations are ignored. Add a profile entry only to change that:

- Receives notifications: on by default. Off, the person gets nothing on any channel: not in an audience, not when a call names them, not for critical messages (`recipient_disabled`). Devices, channels and address stay saved. A banner without a target stays visible on their dashboard; a banner or watch rule that names only switched-off persons is shown to nobody.
- Added devices: a Companion device that was not found, added by name.
- Removed devices: a detected device to leave out; you can bring it back.
- Primary device: listed first. A push still goes to every device of the person.
- Accepted channels: banner, push and popup by default. A channel you remove is skipped for that person. Mail is off until you add it.
- Mail address: where mail to this person goes.

The panel lists each person with a column per channel (Banner, Push, Popup, Mail): a tick when the person accepts the channel and it can work, a dash when the profile does not accept it, and a warning mark when it is accepted but cannot work (push without a usable device, popup without a Home Assistant user, mail without an address). Point at the mark for the reason. On a narrow screen the channels are written under the name, for example "Banner, Push (no device), Popup". A person who receives nothing is greyed out with a "disabled" badge. Devices, added and removed devices, the primary device, a missing notify service and the missing Home Assistant user are shown when you open a person. A profile that equals the detected devices is not stored. A person with no usable device is skipped on push (`no_usable_device`). A renamed device keeps working: the service is worked out from the device's current name each time.

Speaker groups are named sets of speakers, Assist satellites and areas for speech. Every group is a sensor, and a call names the group by the entity ID of that sensor, for example `sensor.heads_up_group_ground_floor`. The sensor shows how many speakers reach the group now. The panel shows the ID. An area stands for the speakers and satellites assigned to it in Home Assistant, and a call names an area by its area ID.

## Renaming

You can rename a policy, an audience, a speaker group, a watch rule or a person without breaking anything that is running. Heads Up keeps each of them under an ID that a rename does not change, and the name is only what the panel shows.

- A call that names an audience, a policy or a group by its entity ID keeps working. The editor of each shows the ID.
- Watch rules, policy targets, messages that are showing and the timers of running escalations, reminders and summaries keep their policy, audience and group.
- If you change the entity ID of a person, a speaker, a zone or a watched entity in Home Assistant, Heads Up changes its own copies of that ID (audiences, groups, profiles, rules, policy targets, stored messages, templates) and writes one line to the Message Log. A call in your own YAML that names the old ID fails with the valid IDs; change it there.
- Heads Up cannot follow a name that another integration owns. If the notify service that sends mail is renamed, Needs attention names the missing service; choose the new one on the Channels page.

## Policies

A policy adds behaviour to messages without changing the automation that sends them. The types are Escalation, Reminder, Quiet hours, Away, Fallback, Deliver and Summarize. Add one in the panel's Policies page or under Settings > Devices & services > Heads Up > Add policy. Every policy is also a switch entity. Its attributes show what it does: `type`, `apply`, `severities`, `tags`, the fields of its type (for example `from_time`, `to_time`, `action` and `critical_passes` for Quiet hours) and `order`, its place in the list. The policy editor shows the entity ID of the switch. A new policy shows the ID it gets when you save.

Renaming a policy changes only its name. Its entity ID, the watch rules that use it, the messages that are running and their escalations, reminders and held summaries stay as they were. Deleting a policy ends its timers; a new policy with the same name is a different policy, and a rule or message that used the deleted one is listed under Needs attention until you choose another.

### How policies interact

A setting on the Policies page, and the first question of the policies step of the introduction, decides what happens when several automatic policies match one message.

- Only the first policy that applies runs (the default). The Policies page is one ordered list, and a message gets the first enabled automatic policy of the list that matches its severity and tag. Drag a policy or use the arrows to change the order. A policy you add later goes to the bottom. When a policy above it matches every message it matches, the list marks it "Never runs by itself"; a call that names it still uses it.
- Every policy that applies runs. A message can get several policies at once, for example quiet hours and a reminder. The order does not matter. Policies can interfere with each other: check a call with Test send.

A call or a watch rule that names a policy uses only that policy under both settings. `none` uses no policy. Policies that have no stored order start in this order: Summarize, Quiet hours, Away, Escalation, Reminder, Fallback, Deliver, each type by name.

"Critical delivery" from the introduction matches every critical message, so under the first setting it comes first and hides later policies for critical messages. Put a policy for a narrower critical case, such as severity `critical` with tag `water`, above it.

### The defaults of the introduction

Under "only the first policy that applies runs" the introduction offers four policies that do not overlap, in this order: Critical delivery (critical messages are pushed at once to the audience you choose, Admins by default, and the push level of critical becomes critical; no reminder follows), Warning reminders (every 30 minutes, at most 3 times), Evening summary (info and success messages tagged `digest` are held and sent at 20:00) and Night quiet (info and success messages without that tag are sent quietly from 22:00 to 07:00).

Under "every policy that applies runs" it offers: Night quiet (22:00 to 07:00, send quietly, critical passes), Evening summary (messages tagged `digest`, critical never held), Critical messages (Critical delivery as a Deliver policy, Critical reminder every 10 minutes at most 3 times and, if you choose speakers, Critical escalation after 10 minutes on those speakers; dismissing counts as acknowledging) and Warning reminders. Before you switch on Critical messages in this mode:

- It covers every critical message, also those of your existing automations. They get an Acknowledge button on the card and in the push, and a push or speech after 10 minutes without an acknowledgement.
- Speech passes quiet hours, so a critical message that nobody acknowledges is said on the speakers at night too.
- Evening summary only holds messages that carry the tag `digest`; your automations have to set it.

Create adds only what is missing: a policy with the same name, or one that does the same as a policy you have, is skipped, and nothing you have is changed or deleted. The audience and the speakers are chosen in the dialog because a policy cannot mean "the people of the original call".

### Which messages a policy applies to

A policy attaches to messages automatically or manually, chosen in the editor under Which messages.

- Automatically: the policy has two lists. A message gets it when its severity is in the first list and its tag in the second. An empty list matches everything. A message without a tag matches only a policy whose tag list is empty. Messages from watch rules have the tag `rule`.
- Manually: the policy has no lists and never attaches by itself. Only a call or a watch rule that names it in the `policy` field gets it.

The `policy` field of `heads_up.notify` names manual policies by the entity ID of their switch: they apply next to every automatic policy that matches, whatever their own lists say. Set `match_policies_automatically: false` to switch the automatic policies off for the call; `policy: none` uses no policy at all. A disabled policy is never used. Names must be unique, and `none` is reserved. The form refuses a second automatic policy of the same type with the same severities, tags and time, because it would do the same thing twice.

### Acknowledging

Acknowledging says that someone has seen a message. It stops every escalation and reminder of that message for everyone. The banner stays on the dashboard.

- On a phone, pushes of a message that has an escalation or reminder policy carry an Acknowledge button.
- On the card and in the popup, an Acknowledge button and the line "Acknowledged by Anna" show it; see [the card](actions.md#acknowledge).
- The acknowledgement stays when the message is updated with the same severity. A new severity starts again. A watch rule message starts again each time its condition turns false and true.
- Home Assistant stores who acknowledged in `acknowledged_by`. No event is fired.

### Channels and recipients from the call

Escalation, Deliver and Fallback add a delivery to a call. Each has two settings, Channels come from and Recipients come from. By default both come from the policy: you list the channels and give the audience or recipients for each. You can take either from the call instead.

| Channels come from | Recipients come from | What the policy sends |
|---|---|---|
| This policy | This policy | The channels you list, to the recipients you give for each. This is the default. |
| The call | This policy | The channels of the call, to other people: the same channels, new recipients. |
| The call, only the channels that reached nobody (Fallback only) | This policy | The channels of the call that reached nobody, to other people. |
| This policy | The call | The channels you list, to the people and speakers the call named: new channels, the same recipients. |

Taking both from the call is refused, because the policy would add nothing. Escalation and Deliver offer three of the four rows: they have no failure to react to, so they do not offer "only the channels that reached nobody".

- When the channels come from the call, the policy has a People target (an audience or persons, used for push, popup and mail) and a Speakers target (used for speech). Give at least one; a kind of channel without a target is skipped.
- When the recipients come from the call, the people are the audience or persons the call gave on push, popup or mail, reused on every new channel that takes people. Speech uses the speakers the call named, or is skipped when it named none. The Persistent Notification needs no target. The banner is never part of these deliveries.
- Someone who already has the message on a channel is not notified there a second time.

Example: send to At home, and fall back to Everyone when nobody is home. Add a Fallback policy that applies to the tag `home-only`, with Use when "Nobody to notify", Channels come from "The call", and the People target set to the audience Everyone. A call with `channels: [push]`, `to: {push: {audience: binary_sensor.heads_up_audience_at_home}}` and `tag: home-only` then pushes to Everyone when At home is empty.

### Escalation

If nobody acknowledges within the time, the policy delivers the message on the channels you choose, to the targets you choose for each channel, or on the channels of the call to other people, or on other channels to the people of the call.

| Field | Default | Meaning |
|---|---|---|
| Escalate after (minutes) | 5 | Time from the moment the message is visible. |
| Channels come from | This policy | This policy, or the call. See above. |
| Channels | none | `push`, `popup`, `speak`, `persistent`, `mail`; used when the channels come from the policy. |
| Recipients come from | This policy | This policy, or the call. |
| Targets | none | Per channel an audience or recipients, never both. Speak takes recipients only; a persistent notification takes none. With channels from the call: a People target and a Speakers target. |
| Dismissing counts as acknowledging | off | A dismissal by anyone stops this escalation. |

- Someone who already has the message on that channel is not notified a second time.
- Several escalations form a chain by their times. Each runs on its own timer.
- The time is stored. After a restart, an escalation that came due while Home Assistant was stopped runs once.
- A message that waits for its condition does not start its timer until the condition is true. A message that ends cancels its timers.
- A new severity restarts the timers with the policies of the new severity.

### Reminder

While nobody acknowledges, the policy repeats the notification.

| Field | Default | Meaning |
|---|---|---|
| Repeat every (minutes) | 30 | Time between repeats. |
| At most this many reminders | 3 | The reminder stops after this many. |
| Channels | all | Limit the repeats to these channels. |

Only people who still have the notification are reminded. Someone who dismissed or snoozed it is left out, and when a snooze ends they are notified again. When nobody is left the reminder stops. Reminders repeat the push with the same tag, so the phone replaces it.

### Quiet hours

Between two times of day, deliveries outside the dashboard are held, sent quietly or dropped. The banner on the dashboard is never affected.

| Field | Default | Meaning |
|---|---|---|
| Quiet from, Quiet until | 22:00 to 07:00 | The window, on the clock of the Home Assistant time zone. A window may cross midnight. The two times must differ. |
| Days | every day | The days a window starts on. A window that starts on Friday ends on Saturday morning. |
| During quiet hours | Send quietly | Send quietly: a push is passive and without sound, speech is skipped, a popup is a corner card. Wait: hold the delivery until the window ends, then send it once. Drop: do not deliver. |
| Critical messages pass | on | Critical messages ignore the policy. |

- The window follows the wall clock. On the day the clocks change it is one hour shorter or longer. A time that does not exist or occurs twice uses its first occurrence.
- Reminders during the window are skipped, not held, whatever the action.
- A held delivery is stored and released once at the end of the window, also after a restart. If the message was cleared, expired or acknowledged meanwhile, or the person dismissed it, nothing is sent and the Message Log says why.
- If several quiet hours policies are in their window, the strictest action applies: Drop, then Wait, then Send quietly.

### Away

A person who is not home when a message is sent gets it when they arrive, if the message is still there.

| Field | Default | Meaning |
|---|---|---|
| Wait for arrival (minutes) | 0 | How long to wait. 0 means as long as the message lives. After that time the delivery is skipped (`max_wait_exceeded`). |
| Critical messages pass | on | On: critical messages are sent at once to people who are away. Off: they wait for the arrival like other messages. |

- Away holds only deliveries to an audience, and only for people whose state is known and not `home`. Recipients you list yourself, and people whose presence is unknown, are sent at once.
- Arrival is the person's state changing to `home`. The delivery is sent once, and not if the message was cleared, expired or acknowledged meanwhile, or that person dismissed or snoozed it.
- With Critical messages pass off, Away holds critical messages too.
- Held deliveries are stored and survive a restart.

### Fallback

If the first delivery of a message reached nobody on a channel, the policy delivers somewhere else: on its own channels to its own targets, on the channels of the call to other people, or on other channels to the same people. It is not limited to other channels: a Fallback on push can send the same message to another audience.

| Field | Default | Meaning |
|---|---|---|
| Use when | Nobody to notify | Nobody to notify: the audience resolved to nobody (for example nobody is home). Delivery failed: the person has no usable device or sending failed. Both: either. |
| Channels come from, Channels, Recipients come from, Targets | This policy | As for an escalation, with a fourth choice for the channels: the channels of the call that reached nobody for the reason you chose. "Same recipients" helps only with Delivery failed: when the audience was empty, the same recipients are empty too. |

- A fallback is judged once, after the first delivery of the message. It is not judged again on updates, and escalations, reminders and fallbacks never start a fallback.
- A channel with a delivery that was sent or held counts as reached. The banner does not count.
- Messages from watch rules only have the banner channel, so they have no first delivery to fall back from. Their escalations still pass quiet hours and away.

### Deliver

A call names the channels of its first delivery. A Deliver policy adds channels and targets to it, at once, for the messages it applies to: its own channels and targets, the channels of the call for other people, or other channels for the people of the call. It is how a critical message reaches phones the moment it appears even when the automation or the watch rule only creates a banner.

- It fires once per message, at its first delivery. An update replaces what it sent, like the call's own deliveries.
- Someone who already has the message on that channel from the call is not notified a second time.
- It passes quiet hours, away and fallback like any delivery. It does not fire for a message held for a summary, and not for a message that became visible while Home Assistant was starting.
- A watch rule message gets it when the policy applies to the tag `rule`. With `match_policies_automatically: false` in the call it is switched off for that call.

### Summarize

A Summarize policy holds the messages it applies to on every channel, including the dashboard banner, and sends one summary instead.

| Field | Default | Meaning |
|---|---|---|
| Summary every (minutes) | 60 | The summary is sent this many minutes after the first message was held. |
| Summary at (time of day) | none | Sends one summary each day at this local time instead of by the interval. |
| Include critical messages | off | Off: critical messages are not held and are delivered at once. |

- A held message is not shown on the dashboard, not counted by the active banners sensor and not sent. Administrators with `show_all` still see it.
- The summary is one message for each recipient and channel: a person's phone gets a push that lists the messages meant for that person; the dashboard gets one banner. It has a count in the title and one line per message, at most ten, then "and N more". Its severity is the highest of the messages.
- A message that was cleared before the summary is listed once, marked resolved. Nothing is sent when nothing was held.
- The summary stays for 24 hours or until it is dismissed. It passes through quiet hours, away and fallback like any delivery, and is never held, escalated, reminded or summarized itself.
- The messages stay hidden after their summary. A held message that changes its text or severity is listed again in the next summary. A held message that becomes critical is released at once, unless the policy includes critical.
- The hold is decided when the message appears. A policy added later does not hold messages that are already there, and a policy added after a message was sent only starts when that message is next updated. Deleting or disabling the policy releases its held messages.
- Held messages and the timer are stored and survive a restart. A summary that came due while Home Assistant was stopped is sent once.

### Example

```yaml
action: heads_up.notify
data:
  id: water_leak
  message: Water on the kitchen floor.
  severity: critical
  tag: water
  channels: [banner, push]
  audience: binary_sensor.heads_up_audience_at_home
  policy: switch.heads_up_policy_water_escalation
```
