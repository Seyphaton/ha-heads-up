# Policies: escalation and reminders

A policy adds behaviour to messages without changing the automation that sends them. This version has two types: Escalation and Reminder. Add one in Settings > Devices & services > Heads Up > Add policy.

## Which messages a policy applies to

Every policy has two lists. A message matches when its severity is in the first list and its tag in the second. An empty list matches everything.

- Messages from watch rules have the tag `rule`.
- A message without a tag matches only a policy whose tag list is empty.
- The `policy` field of `heads_up.notify` changes this. A name uses that one policy, whatever its lists say. Leave the field out to use every policy that matches. `none` uses no policy.
- A disabled policy is never used.
- Names must be unique, and `none` is reserved.
- The form refuses a second policy of the same type with the same severities, tags and time, because it would do the same thing twice.

## Acknowledging

Acknowledging says that someone has seen a message. It stops every escalation and reminder of that message for everyone. The banner stays on the dashboard.

- On a phone, pushes of a message that has an escalation or reminder policy carry an Acknowledge button.
- A dashboard or panel can call the WebSocket command `heads_up/acknowledge` with `banner_id`.
- The acknowledgement stays when the message is updated with the same severity. A new severity starts again. A watch rule message starts again each time its condition turns false and true.
- Home Assistant stores who acknowledged in `acknowledged_by`. No event is fired.

## Escalation

If nobody acknowledges within the time, the policy delivers the message on the channels you choose, to the targets you choose for each channel.

| Field | Default | Meaning |
|---|---|---|
| Escalate after (minutes) | 5 | Time from the moment the message is visible. |
| Channels | none | `push`, `popup`, `speak`, `persistent`. |
| Push, popup: audience or recipients | none | Either an audience or recipients per channel, never both. Speak takes recipients only. A persistent notification takes no target. |
| Dismissing counts as acknowledging | off | A dismissal by anyone stops this escalation. |

- Someone who already has the message on that channel is not notified a second time.
- Several escalations form a chain by their times. Each runs on its own timer.
- The time is stored. After a restart, an escalation that came due while Home Assistant was stopped runs once.
- A message that waits for its condition does not start its timer until the condition is true. A message that ends (cleared, expired, condition false) cancels its timers.
- A new severity restarts the timers with the policies of the new severity.

## Reminder

While nobody acknowledges, the policy repeats the notification.

| Field | Default | Meaning |
|---|---|---|
| Repeat every (minutes) | 30 | Time between repeats. |
| At most this many reminders | 3 | The reminder stops after this many. |
| Channels | all | Limit the repeats to these channels. |

- Only people who still have the notification are reminded. Someone who dismissed or snoozed it is left out; when a snooze ends they are notified again. When nobody is left the reminder stops.
- Reminders repeat the push with the same tag, so the phone replaces it.

## If an audience or group is deleted

Home Assistant lets you delete an audience or recipient group even if a policy uses it. The policy then cannot run: when its time comes the trace shows `skipped` with the reason `audience_missing` or `group_missing`, and nothing is sent. Admins can list the policies that use a name with the WebSocket command `heads_up/hub_usage` (`name`).

## Example

```yaml
- action: heads_up.notify
  data:
    id: water_leak
    message: Water on the kitchen floor.
    severity: critical
    tag: water
    channels:
      - banner
      - push
    to:
      push:
        audience: At home
    policy: Water escalation
```

## Limits

- Quiet hours, Away, Fallback and Summarize are not built yet.
- A policy that applies after the message was sent only starts when the message is next updated.
- Policy forms and the panel are not built; use the entry's Add policy form.
