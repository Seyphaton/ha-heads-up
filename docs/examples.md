# Examples and FAQ

Working examples from simple to complex, then answers to common questions, troubleshooting by symptom and the known limits. Each example uses the actions from [Actions](actions.md). Replace the entity IDs, persons and audience names with your own. Every YAML block on this page is checked against the real action schemas before each release.

On this page: the examples (Basics, Messages that follow your home, People and reactions, Several channels and policies, From outside Home Assistant), [Frequently asked questions](#frequently-asked-questions), [Troubleshooting](#troubleshooting), [Limitations](#limitations) and [Developer notes](#developer-notes).

## Basics

### A message on the dashboard

The banner appears in every Heads Up card ([Card](actions.md#the-card)). Without `timeout` it ends after 24 hours.

```yaml
action: heads_up.notify
data:
  id: pv_status
  title: PV Information
  message: Autarky today at almost 100%.
  severity: success
  channels: [banner]
```

- The `id` makes a second call replace the banner instead of adding another one.
- `severity` is one of `success`, `info` (the default), `warning` and `critical`. It sets the color, the icon and the sort order. `critical` sorts first and is never removed to make room for new messages.
- `timeout` takes seconds or a duration. `timeout: {minutes: 30}` ends the message after 30 minutes, `timeout: 0` keeps it until someone closes or clears it.

### A push to everyone at home

```yaml
action: heads_up.notify
data:
  message: The washing machine has finished.
  severity: info
  channels: [push]
  audience: At home
```

The shortcut `heads_up.push` does the same with `audience` and no `channels`. See [Push notifications](configuration.md#push).

### A spoken message

```yaml
action: heads_up.speak
data:
  message: Dinner is ready.
  recipients:
    - media_player.kitchen
```

Speech goes to speakers, not to people. See [Speech](configuration.md#speech).

### Take a message back

Give the message an `id`, then clear it. The banner, the push on every phone, the popup and the bell entry are taken back.

```yaml
action: heads_up.clear_notifications
data:
  id: pv_status
```

## Messages that follow your home

### Open window

A banner and a push appear when a window has been open for 5 minutes, and both are taken back when it closes.

```yaml
alias: Bedroom window open
triggers:
  - trigger: state
    entity_id: binary_sensor.bedroom_window
    to: "on"
    for:
      minutes: 5
actions:
  - action: heads_up.notify
    data:
      id: window_bedroom
      title: Window open
      message: The bedroom window has been open for 5 minutes.
      channels: [banner, push]
      audience: At home
      timeout: 0
      condition:
        entity_id: binary_sensor.bedroom_window
        state: "on"
```

- `condition` ties the message to the window sensor. With the default `mode: once`, the message ends the first time the sensor stops being `on`. The automation needs no second trigger.
- `timeout: 0` keeps the message until the window closes. Without it, the default of 24 hours applies.
- For a window that opens and closes often, add `mode: recurring`. The message then hides while the window is closed and shows again, also for people who closed it, when the window opens.

### A message that follows an entity

Put the wait in the call instead of in an automation trigger. The message shows after the garage door has been open for 10 minutes, hides when it closes and shows again the next time.

```yaml
action: heads_up.notify
data:
  id: garage_open
  message: The garage door has been open for 10 minutes.
  severity: warning
  channels: [banner]
  mode: recurring
  timeout: 0
  condition:
    entity_id: cover.garage_door
    state: "open"
    for:
      minutes: 10
```

Call it once, for example when Home Assistant starts. A [watch rule](actions.md#watch-rules) does the same from a form and needs no call at all.

## People and reactions

### Critical alert for one person

A banner and a push for one person only. Nobody can close the banner, and it removes itself after 10 minutes.

```yaml
alias: Water leak alert
sequence:
  - action: heads_up.notify
    data:
      id: water_leak
      title: Water leak
      message: Water detected in the basement.
      severity: critical
      icon: mdi:water-alert
      tag: leak
      timeout:
        minutes: 10
      dismiss: "off"
      channels: [banner, push]
      recipients: [person.alex]
```

- Users who are not linked to `person.alex` do not receive the banner. This is targeting, not access control; see [SECURITY.md](../SECURITY.md).
- An administrator sees a "Clear for everyone" button on the banner, and the action `heads_up.clear_notifications` with `id: water_leak` or `tag: leak` removes the message from every channel.

### Snooze and your own buttons

A banner and a push that can be snoozed for 15 minutes or 1 hour, with a button that fires an event. An automation can react to `heads_up_banner_action` with `key: light`; see [Buttons and snooze](actions.md#buttons-and-snooze).

```yaml
action: heads_up.notify
data:
  id: garage_open
  message: Garage door open after 10pm.
  severity: warning
  channels: [banner, push]
  audience: At home
  snooze: user
  snooze_options:
    - minutes: 15
    - hours: 1
  actions:
    - key: light
      label: Outdoor light
```

On the banner, Snooze offers 15 minutes and 1 hour. On the push, Snooze uses the one time of the setting Snooze time on push and popup.

### Tap action with confirmation

A banner that runs an action after the user confirms a dialog.

```yaml
action: heads_up.notify
data:
  id: garage_open
  title: Garage door open
  message: Tap to close it.
  channels: [banner]
  tap_action:
    action: perform-action
    perform_action: cover.close_cover
    target:
      entity_id: cover.garage_door
    confirmation:
      text: Close the garage door?
```

- Tapping the banner shows the dialog. The action runs when the user confirms.
- Without `confirmation`, one tap runs the action. Every user who sees the banner can tap it, so use `confirmation` for actions that change something physical.
- `action: navigate` with `navigation_path` opens a dashboard view instead.

## Several channels and policies

### A leak that escalates

The automation states what happened and how serious it is. The panel's Policies page holds the rest.

```yaml
action: heads_up.notify
data:
  id: water_leak
  title: Water leak
  message: Water on the kitchen floor.
  tts_message: Water in the kitchen.
  severity: critical
  tag: water
  channels: [banner, push, popup]
  audience: At home
  timeout: 0
```

| Policy | Type | Settings | Effect |
|---|---|---|---|
| Water escalation | Escalation | severity `critical`, tag `water`; after 5 minutes; speak to the group `Ground floor (group)`; push to `Admins` | If nobody acknowledges within 5 minutes, the message is also said on the speakers and pushed to the administrators. |
| Water reminder | Reminder | severity `critical`, tag `water`; every 10 minutes, at most 3 | Repeats the push while nobody acknowledges. |
| Night quiet | Quiet hours | 22:00 to 07:00, critical messages pass | Lower severities become passive pushes at night; this message still alerts. |

The default setting runs only the first policy that matches a message. For both policies to run, choose "Every policy that applies runs" on the Policies page. If you used the introduction's defaults, put both above "Critical delivery" (see [Policies](configuration.md#how-policies-interact)). Acknowledging the message on a phone stops both the escalation and the reminder. The banner stays until `heads_up.clear_notifications` or the sensor's own automation takes it back. See [Policies](configuration.md#policies).

### An evening summary

Messages with the tag `digest` are held and sent as one summary at 20:00 instead of one push each.

```yaml
action: heads_up.notify
data:
  message: Backup finished.
  severity: info
  tag: digest
  channels: [banner, push]
  audience: Admins
```

Create a Summarize policy for the tag `digest` with the time 20:00. The banner and the push are held on every channel and appear in the summary. Critical messages are not held unless the policy includes them.

### Mail to one person

Mail needs a notify service, and the person needs Mail switched on and an address in the recipient profile; see [Mail](configuration.md#mail).

```yaml
action: heads_up.notify
data:
  id: backup_failed
  title: Backup
  message: The nightly backup failed.
  severity: warning
  channels: [banner, mail]
  recipients: [person.anna]
```

## From outside Home Assistant

Any program that can call the Home Assistant API can use the actions. Create a long-lived access token in your Home Assistant user profile; see the [REST API documentation](https://developers.home-assistant.io/docs/api/rest/).

### REST

```bash
curl -X POST "http://homeassistant.local:8123/api/services/heads_up/create_banner?return_response" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "backup_done", "message": "Backup finished", "severity": "success", "timeout": 3600}'
```

Response:

```json
{"changed_states": [], "service_response": {"id": "backup_done", "status": "created"}}
```

- Without `?return_response` the call returns `[]` and no data.
- `notify`, `clear_notifications`, `clear_banner` and `clear_all` are called the same way, with `/api/services/heads_up/<action>`. The clear actions return `{"cleared": <number>}` in `service_response`.
- An invalid field, for example a `severity` that does not exist, returns status `400` with the body `400: Bad Request`. Nothing is stored.

### WebSocket

Send this message on an authenticated connection to `/api/websocket`:

```json
{
  "id": 1,
  "type": "call_service",
  "domain": "heads_up",
  "service": "create_banner",
  "service_data": {"id": "backup_done", "message": "Backup finished"},
  "return_response": true
}
```

The result has the action's response under `result.response`:

```json
{"id": 1, "type": "result", "success": true, "result": {"context": {"id": "…", "parent_id": null, "user_id": "…"}, "response": {"id": "backup_done", "status": "created"}}}
```

An invalid field returns `"success": false` with `error.code` `invalid_format` and a message that names the field.

Any user with a valid token can call the actions; Heads Up does not check for administrators.

## In a household

- A leak at 03:00: a critical message reaches every phone and the dashboard, quiet hours let it pass, and speakers say it. Ben acknowledges on his phone, so the escalation stops. The banner stays until the sensor is dry.
- A window left open in an empty house: the audience Last to leave gets a push. Nobody else is disturbed. The push is taken back when the window closes.
- The doorbell: a short message on the wall tablet and a spoken line. With a timeout of 60 seconds everything clears itself.
- The washing machine: a push to the person who started it. Quiet hours turn it into a banner at night. An Away policy sends it when they arrive.
- Nobody reacts to a critical message: after five minutes an escalation notifies a backup person and the speakers. A reminder repeats it. An acknowledgement stops both.
- A phone is replaced: edit the person's recipient profile once. No automation changes.
- Why you did not get a message: Test send previews a call, who is reached now and why anyone is skipped, held or dropped. The Message Log shows what happened, for example "push to Anna skipped: quiet hours".

## Frequently asked questions

The panel's Help > FAQ has the same questions and more, from first steps to detailed use.

### What does Heads Up do?

Your automation makes one call, `heads_up.notify`. Heads Up decides where the message shows up (channels), who gets it (audiences and recipients) and when it is delivered or escalated (policies). You set this up once in the panel, not in every automation.

### How is this different from what Home Assistant already has?

Each Home Assistant notify service sends to one place, and each automation names its own devices. Heads Up adds:

- One call that reaches several channels.
- Audiences such as At home or Last to leave, worked out when the message is sent.
- Policies (escalate, remind, keep quiet at night, summarize), set once for all automations.
- The banner, a card on your dashboards that stays until it is dismissed, its condition ends or it times out.
- One lifecycle: a message ends everywhere at once, pushes included, and every delivery is traced.

### What is an audience, and how does it differ from a recipient?

An audience is a named group of people that can change over time: Everyone, Admins, At home, Last to leave, or your own. A recipient is one fixed target: a person, a phone or a speaker. A channel takes an audience or recipients, never both.

### Why does speech take no audience?

An audience is a set of people, and speech goes to a speaker in a place. Heads Up does not know which speaker a person is near, so you name speakers, speaker groups or areas.

### What does severity do?

A message has one of four severities: success, info (the default), warning and critical. On the banner it sets the color, the icon and the order, critical first. On a push it sets the level: success and info are passive, warning is normal, critical is time-sensitive until you set the level critical. The popup style is set per severity, and policies can match on it.

### What are tags for?

A tag is a label you give a message, for example `laundry` or `water`. A policy can apply to chosen tags only, a card can show only banners with one tag, and `heads_up.clear_notifications` can remove every message with a tag. Messages from watch rules carry the tag `rule`.

### What is the difference between acknowledging and dismissing?

Acknowledging says that someone has seen the message. It stops every escalation and reminder of that message for everyone, and the banner stays. Dismissing closes the message for the person who dismissed it. An escalation policy can count a dismissal as an acknowledgement.

### How do I end a message for everyone, on all channels?

- By hand: call `heads_up.clear_notifications` with an `id`, a `tag`, a `severity` or `channels`; `all: true` removes every message.
- By condition: give the message a `condition`. In mode `once` it ends when the condition turns false.
- By viewer: set `dismiss: everyone`, on the message, on a watch rule or as the default in Settings. When anyone closes it, it ends for everyone and the pushes are taken back. With the scope `user`, closing hides it only for that person.
- A timeout also ends a message everywhere.

### How do I keep messages quiet at night?

Add a Quiet hours policy. During the window it can send quietly, hold the messages until the end or drop them. Critical messages pass by default. The introduction creates one from 22:00 to 07:00 that sends quietly.

### What if someone is not home?

An Away policy sends the message when the person arrives, as long as it is still there. A Fallback policy sends it to someone else when the first delivery reached nobody.

### Do critical messages get special treatment?

Yes, in four places. Quiet hours let them pass unless you switch that off. Summarize does not hold them unless you include them. The rate limits never hold them back. Presence audiences include a person whose presence is unknown. Away has no exception, so limit its severities if critical messages must go out at once.

### What stops a flood of pushes?

Three limits: 5 pushes per device per minute, 60 in total per minute, and no repeat of an identical update within 30 seconds. A skipped push shows in the Message Log as `rate_limited` or `duplicate`. All three are settings, and critical messages are never held back.

### What happens when I replace a phone?

Edit the person's recipient profile once. Audiences and policies stay the same, and no automation needs a change.

### Why does a new policy not change a message that is already showing?

A policy is looked up when a message appears. A policy you add later starts when the message is next updated. A Summarize policy does not hold messages that are already there.

### What happens after a restart?

Pending escalations keep their due time, and a step that came due during the restart runs once if the message is still active and not acknowledged. Messages held for quiet hours, away or a summary stay held. Pushes of messages that no longer exist are removed. The record of recent messages and last actions starts empty.

## Troubleshooting

Start with the Message Log (Heads Up > Notifications and rules > Message Log): choose the message and read the result and the reason of each row. Test send shows the same reasons before you send anything.

### The card shows "Custom element doesn't exist: heads-up-card"

- Reload the page. If the page loaded in the first second after Home Assistant started, it can miss the card. A reload fixes it.
- If it persists, check that the integration is added (Settings > Devices & services). The card is registered only while the integration is loaded.
- Open `/heads_up/heads-up-card.js` in the browser. It should return JavaScript. Then reload the page without cache.

### The card looks old after an update

Reload the page without cache once. The card address changes with every new version of the card file, so a normal reload loads the new one; a page that was loaded before the update keeps the old card until it is reloaded.

### The card shows "Heads Up is not available"

The card cannot reach `heads_up/subscribe`. During a Home Assistant start it retries after 1, 2, 5 and 10 seconds and then every 30 seconds, and the banners return by themselves. If the message stays after the start has finished, the integration is not loaded: look for errors from `custom_components.heads_up` in the log.

### An action fails with "Heads Up is not set up"

The integration is not added or is disabled. Add it in Settings > Devices & services.

### A banner does not show

Check, in this order:

1. The response of `create_banner`. `status: waiting` means the condition is not true yet.
2. `sensor.heads_up_active_banners`. Its state counts banners that are stored and not waiting.
3. People. With `people`, only users linked to those person entities see the banner. A user sees only banners without `people` when no person is linked to them. The link is the person's `user_id` attribute in Developer tools > States.
4. Dismissal. With `dismiss_scope: user` you do not see a banner you closed. Calling `create_banner` again with the same `id` shows it again.
5. Card filters `severity`, `tag` and `max_items` in the card configuration. With `collapsed_items`, the rest sits behind "Show N more".
6. Timeout. The banner may have expired; the event `heads_up_banner_expired` shows it.

For a banner from a watch rule, see [A watch rule shows no banner](#a-watch-rule-shows-no-banner).

### A push stays on the phone after I dismissed the banner

Open the message in the Message Log. A dismissal shows a `dismissed` row, then one `cleared` row for each of your devices that got a push. With `cleared` rows and no problem reason, Heads Up asked every device to remove the notification, and the app on the phone did not. Open the Companion app once and try again; the app documents that a clear can need recent use. A reason such as `send_failed` or `service_not_found` means Home Assistant could not reach that device. Without `cleared` rows, the user who dismissed is not linked to the person that owns the phone (Settings > People).

### A push did not arrive

Open Heads Up > Notifications and rules > Message Log and choose the message. Each recipient has a result and a reason.

- `no_usable_device`: the person has no Companion device. Check that a `device_tracker` of the app is in the person's trackers, or add the device in a recipient profile.
- `service_not_found`: `notify.mobile_app_<device name>` does not exist. The app was removed or renamed and has not registered again. Look for the service in Developer tools > Actions.
- `channel_not_accepted`: the person's recipient profile does not accept push.
- `recipient_disabled`: Receives notifications is switched off in the person's recipient profile. It stops every channel, also critical messages. Switch it on again on the Recipients page.
- `send_failed`: the service raised an error; the log has one warning per device and hour.
- `rate_limited`: the device had 5 pushes in the last minute, or all devices 60. Raise the limits in Settings. Critical messages are never held back.
- `duplicate`: an update with the same content as the last one arrived within 30 seconds. Change the text, or set the seconds to 0 in Settings.
- `presence_unknown`: an audience such as `Not home` skipped a person whose presence is unknown. Only `critical` messages include them.
- A button press that does nothing: the trace says `user_mismatch`, `stale_message` or `unknown_recipient`.

### An escalation or reminder did not run

Open the message in the Message Log and look for entries with the channel `timer`.

- `cleared` with `acknowledged`: someone acknowledged the message.
- `cleared` with `dismissed_counts_as_acknowledged`: the policy counts a dismissal as an acknowledgement.
- `skipped` with `audience_missing` or `group_missing`: an audience or group the policy names was deleted. Edit the policy.
- `cleared` with `nobody_left`: every recipient had dismissed or snoozed, so there was nobody to remind.
- No entry: the policy did not match the message (severity, tag, or the `policy` field), is disabled, or was added after the message became visible. A policy added later starts at the message's next update. See [Policies](configuration.md#policies).

### A push did not arrive during the night, or arrived late

Open the message in the Message Log.

- `held` with `quiet_hours`: a Quiet hours policy with the action `wait` holds it until the window ends.
- `skipped` with `quiet_hours`: the action is `drop`, or the delivery was a reminder.
- `held` with `away`: the person was not home. It is sent when their person state becomes `home`. `skipped` with `max_wait_exceeded`: they did not arrive in time.
- Critical messages ignore Quiet hours unless the policy has Critical messages pass turned off.
- The window uses the Home Assistant time zone (Settings > System > General).

See [Policies](configuration.md#policies).

### A message does not show on the dashboard

If a Summarize policy applies to the message (its severities and tags, and `policy` in the call), it is held until the summary. The message has no delivery entries in the Message Log, and the summary appears there once it is sent. Critical messages are held only if the policy includes them. Deleting or disabling the policy releases its held messages. See [Policies](configuration.md#policies).

### A message was not spoken

Open the message in the Message Log and look at the speak entries.

- `no_tts_engine`: set the option Text-to-speech engine, or keep exactly one `tts` entity.
- `cooldown`: the same text was said on that speaker in the last 60 seconds.
- `quiet_hours`: a Quiet hours policy skips speech.
- `already_spoken`: updates are not said again.
- `service_not_found` or `send_failed`: the speaker's integration does not offer the service or it failed; the log has one warning per speaker per hour.
- `entity_missing`: the speaker no longer exists. Edit the recipient group.

See [Speech](configuration.md#speech).

### A popup did not appear

- Popups need an open Home Assistant page for a user who is linked to a person in the audience or recipients. The Message Log says `no_user` for a person without a user and `popup_off` for a severity set to `off`.
- You closed it with the close button or Escape: it only hides on that page. Reload the page to see it again.
- For about a second after Home Assistant starts, pages are served without extra scripts. A page loaded in that time has no popups until you reload it.
- If you dismissed or snoozed it, it is gone for you until the snooze ends.

See [Popups](configuration.md#popup).

### An entry is missing in the notification bell

Open the message in the Message Log. `service_not_found` or `send_failed` means Home Assistant's `persistent_notification` service failed. If you dismissed the entry in the bell, Heads Up does not know: the next update of the message creates it again, and so does a restart of Home Assistant, which empties the bell. A rule message reaches the bell only through an escalation or fallback policy. See [Persistent notifications](configuration.md#persistent-notification).

### Mail is not sent

Open the message in the Message Log and read the reason.

- `channel_not_accepted`: Mail is not switched on in the person's profile (Recipients page).
- `no_mail_address`: the person has Mail on but no address, or the Global address is empty. Heads Up never sends a person's mail to the Global address instead. The log has a warning once an hour per person.
- `no_mail_service`: no notify service is chosen on the Channels page.
- `service_not_found`: the chosen notify service no longer exists. Choose it again.
- `send_failed`: the notify service raised an error. Check its own log lines, for example the SMTP server and login.

The event `heads_up_delivery_failed` carries the same reasons. See [Mail](configuration.md#mail).

### The Heads Up entry is not in the sidebar

The entry exists only while the option is on: Settings > Devices & services > Heads Up > Configure > Show Heads Up in the sidebar. Only administrators see it. If it is on and the entry is still missing, reload the browser page. See [The panel](setup.md#the-panel).

### The "Clear all" button is missing

The button appears only when the card shows at least one banner that can be dismissed, and only with `clear_all: true`. Banners with `dismissible: false` are not counted.

### A banner cannot be closed

It was created with `dismissible: false`. An administrator sees a "Clear for everyone" button. `heads_up.clear_banner` with its `id` or `tag` also removes it.

A banner from a watch rule has no button for anyone unless the rule is dismissible. `clear_banner` does not remove it. Disable or delete the rule in Settings > Devices & services > Heads Up.

### A watch rule shows no banner

Check, in this order:

1. The rule is enabled.
2. The entity state or attribute equals one of the rule's states. The comparison is text, so `on` and `On` differ.
3. The entity is not `unavailable` or `unknown`, and it exists. Rule banners are hidden in those cases.
4. People. With `people` set, only users linked to those person entities see it.
5. Dismissal. A dismissible rule hides the banner for the user who closed it until the entity leaves the state and enters it again. A restart also brings it back.
6. The card filters `severity`, `tag` and `max_items`. Rule banners have the tag `rule`.

### The log says "Skipping unreadable banner"

`.storage/heads_up.banners` is valid JSON, but one stored banner is damaged. Heads Up skips it, keeps the others, and rewrites the file without the damaged banner.

### The storage file is damaged

If `.storage/heads_up.banners` cannot be read as JSON, Home Assistant renames it to `heads_up.banners.corrupt.<time>`, logs an error, and Heads Up starts with no banners. Delete or keep the renamed file as you like.

### Access denied for `show_all` or "Clear for everyone"

Both are for administrators only. The card ignores `show_all` for other users.

### What to attach to a bug report

- The Home Assistant version and the Heads Up version (Settings > Devices & services > Heads Up).
- The action call, rule or card configuration that shows the problem.
- The log lines of `custom_components.heads_up` with debug logging on (see Developer notes).
- For a message that did not reach someone: its entry from the Message Log (choose the message and copy its rows).

See also [CONTRIBUTING](../CONTRIBUTING.md#report-a-bug).

## Limitations

### What Heads Up does not do

- Push has no retry: a failed push is not tried again, and a push over the rate limit is skipped ([Push notifications](configuration.md#push), [Settings](settings.md#limits)).
- Speech has no volume handling and no all-clear announcement ([Speech](configuration.md#speech)).
- Mail delivery is the job of the notify service you choose; Heads Up knows only whether the call returned an error ([Mail](configuration.md#mail)).
- A popup needs an open Home Assistant page ([Popups](configuration.md#popup)). A persistent notification goes to everyone ([Persistent notifications](configuration.md#persistent-notification)).
- It keeps no history of messages. Each change fires an event; see [actions](actions.md#events). The panel's trace, recent messages and log of last actions are kept in memory and start empty after a restart.
- Pushes were tried with stub devices only, not with a real Companion app. The critical level needs the app's permission on iOS and plays a sound in silent mode there. On Android it uses the alarm channel, which also sounds in silent mode; Do Not Disturb is overridden only if you allow it for that channel in the Android settings.
- A watch rule watches one entity (its state or one attribute) or one template. The state is compared as text unless the condition is above, below or between.
- Banner text is shown as you write it. The card's own labels and the integration's screens follow your Home Assistant language in English, German, French and Spanish; other languages show English. The German, French and Spanish texts were written without review by native speakers.

### Access

- `people` decides who receives a banner in the card. It is not access control. Administrators can see every banner with the card option `show_all`, and anyone who can read the Home Assistant files or backups can read `.storage/heads_up.banners` in plain text. Do not put secrets in banners.
- Any logged-in user can create, clear and dismiss banners through the API. Only administrators can use the card's "Clear for everyone" button and `show_all`.
- Anyone who can see a banner can run its `tap_action`, including on a shared screen. Use `confirmation` for actions that change something physical.
- With `dismiss_scope: user`, closing a banner hides it for that Home Assistant user, in every Heads Up card. People who share one login also share the closed state.
- "Clear all" and swipe to dismiss remove banners with `dismiss_scope: global` for everyone, like the X button, and ask for no confirmation.
- Swipe to dismiss was tested with a mouse only, not on a touch screen.

### Behaviour to know

- A banner has a timeout of 24 hours unless you set `timeout` or change the option. A banner with `mode: once` whose condition never matches ends at that timeout; with `timeout: 0` it stays until you clear it.
- `unavailable` and `unknown` states do not change a banner, including while Home Assistant starts.
- When the limit is reached and every stored banner is `critical`, or eviction is off, creating a banner fails.
- A dashboard page that finishes loading in the first second after Home Assistant starts can miss the card and show "Custom element doesn't exist: heads-up-card". Reload the page once. See Troubleshooting above.
- Installing needs a Home Assistant restart, which pauses all automations until it has finished.
- Banner defaults changed in the options form or in Settings apply to new banners only.
- Watch rules ([rules](actions.md#watch-rules)) compare one entity's state or attribute as text, like `condition`. A closed rule banner returns after a restart.

### Tested versions

Home Assistant 2026.10.4 (tests and a local instance) and 2026.9.4 (tests). Other versions are not tested.

## Developer notes

Turn on debug logging for the integration in `configuration.yaml`, restart, and read the Home Assistant log:

```yaml
logger:
  logs:
    custom_components.heads_up: debug
```

The panel reads its data through administrator WebSocket commands that you can also call from a script or a tool:

| Command | Data | Returns |
|---|---|---|
| `heads_up/hub_trace` | `message_id` | The delivery trace of one message: per recipient and channel a result and a reason. |
| `heads_up/hub_usage` | `name` | The policies that use an audience or speaker group. |
| `heads_up/hub_preview_audience` | `audience`, optional `severity` | The members of an audience now, and the skipped persons with a reason. |
| `heads_up/acknowledge` | `banner_id` | Acknowledges the message for the calling user. |


