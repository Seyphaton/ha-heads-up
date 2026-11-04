# Examples

Working examples from simple to complex. Each uses the actions from [Actions](actions.md). Replace the entity IDs, persons and audience names with your own. Every YAML block on this page is checked against the real action schemas by `make docs-check`.

## Basics

### A message on the dashboard

The banner appears in every Heads Up card ([Card](card.md)). Without `timeout` it ends after 24 hours.

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
- `severity` is one of `success`, `info`, `warning` (the default) and `critical`. It sets the color, the icon and the sort order. `critical` sorts first and is never removed to make room for new messages.
- `timeout` takes seconds or a duration. `timeout: {minutes: 30}` ends the message after 30 minutes, `timeout: 0` keeps it until someone closes or clears it.

### A push to everyone at home

```yaml
action: heads_up.notify
data:
  message: The washing machine has finished.
  severity: info
  channels: [push]
  to:
    push: {audience: At home}
```

The shortcut `heads_up.push` does the same with `audience` and no `channels`. See [Push notifications](push.md).

### A spoken message

```yaml
action: heads_up.speak
data:
  message: Dinner is ready.
  recipients:
    - media_player.kitchen
```

Speech goes to speakers, not to people. See [Speech](speech.md).

### Take a message back

Give the message an `id`, then clear it. The banner, the push on every phone, the popup and the bell entry are taken back.

```yaml
action: heads_up.clear
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
      to:
        push: {audience: At home}
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

Call it once, for example when Home Assistant starts. A [watch rule](rules.md) does the same from a form and needs no call at all.

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
      dismissible: false
      channels: [banner, push]
      to:
        banner:
          recipients: [person.alex]
        push:
          recipients: [person.alex]
```

- Users who are not linked to `person.alex` do not receive the banner. This is targeting, not access control; see [SECURITY.md](../SECURITY.md).
- An administrator sees a "Clear for everyone" button on the banner, and the action `heads_up.clear` with `id: water_leak` or `tag: leak` removes the message from every channel.

### Snooze and your own buttons

A banner and a push that can be snoozed for 15 minutes or 1 hour, with a button that fires an event. An automation can react to `heads_up_banner_action` with `key: light`; see [Buttons and snooze](actions.md#buttons-and-snooze).

```yaml
action: heads_up.notify
data:
  id: garage_open
  message: Garage door open after 10pm.
  severity: warning
  channels: [banner, push]
  to:
    push: {audience: At home}
  snoozable: true
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
  to:
    push: {audience: At home}
    popup: {audience: At home}
  timeout: 0
```

| Policy | Type | Settings | Effect |
|---|---|---|---|
| Water escalation | Escalation | severity `critical`, tag `water`; after 5 minutes; speak to the group `Ground floor (group)`; push to `Admins` | If nobody acknowledges within 5 minutes, the message is also said on the speakers and pushed to the administrators. |
| Water reminder | Reminder | severity `critical`, tag `water`; every 10 minutes, at most 3 | Repeats the push while nobody acknowledges. |
| Night quiet | Quiet hours | 22:00 to 07:00, critical messages pass | Lower severities become passive pushes at night; this message still alerts. |

Acknowledging the message on a phone stops both the escalation and the reminder. The banner stays until `heads_up.clear` or the sensor's own automation takes it back. See [Policies](policies.md).

### An evening summary

Messages with the tag `digest` are held and sent as one summary at 20:00 instead of one push each.

```yaml
action: heads_up.notify
data:
  message: Backup finished.
  severity: info
  tag: digest
  channels: [banner, push]
  to:
    push: {audience: Admins}
```

Create a Summarize policy for the tag `digest` with the time 20:00. The banner and the push are held on every channel and appear in the summary. Critical messages are not held unless the policy includes them.

### Mail to one person

Mail needs a notify service, and the person needs Mail switched on and an address in the recipient profile; see [Mail](mail.md).

```yaml
action: heads_up.notify
data:
  id: backup_failed
  title: Backup
  message: The nightly backup failed.
  severity: warning
  channels: [banner, mail]
  to:
    mail:
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
- `notify`, `clear`, `clear_banner` and `clear_all` are called the same way, with `/api/services/heads_up/<action>`. The clear actions return `{"cleared": <number>}` in `service_response`.
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
