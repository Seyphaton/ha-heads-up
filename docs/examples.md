# Examples

Each example uses the actions from [actions.md](actions.md) and the card from [card.md](card.md). Replace the entity IDs with your own.

## Open window

A banner appears when a window has been open for 5 minutes and disappears when it closes.

```yaml
alias: Bedroom window open banner
triggers:
  - trigger: state
    entity_id: binary_sensor.bedroom_window
    to: "on"
    for:
      minutes: 5
actions:
  - action: heads_up.create_banner
    data:
      id: window_bedroom
      title: Window open
      message: The bedroom window has been open for 5 minutes.
      timeout: 0
      condition:
        entity_id: binary_sensor.bedroom_window
        state: "on"
```

- `condition` ties the banner to the window sensor. With the default `mode: once`, the banner is removed the first time the sensor stops being `on`. The automation needs no second trigger.
- `timeout: 0` keeps the banner until the window closes. Without it, the default of 24 hours applies.
- The `id` makes a second run replace the banner instead of adding another one.
- For a window that opens and closes often, add `mode: recurring`. The banner then hides while the window is closed and shows again, also for users who closed it, when the window opens.

## Critical alert for one person

A script that shows a banner only to the user linked to one person. The banner cannot be closed and removes itself after 10 minutes.

```yaml
alias: Water leak alert
sequence:
  - action: heads_up.create_banner
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
      people:
        - person.alex
```

- Users who are not linked to `person.alex` do not receive the banner. This is targeting, not access control; see [SECURITY.md](../SECURITY.md).
- Nobody can close the banner. An administrator sees a "Clear for everyone" button on it, and the action `heads_up.clear_banner` with `id: water_leak` or `tag: leak` removes it.
- `critical` banners sort first and are never removed to make room for new ones.

## Tap action with confirmation

A banner that runs an action after the user confirms a dialog.

```yaml
- action: heads_up.create_banner
  data:
    id: garage_open
    title: Garage door open
    message: Tap to close it.
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
- `clear_banner` and `clear_all` work the same way and return `{"cleared": <number>}` in `service_response`.
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
