# Policies

A policy adds behaviour to messages without changing the automation that sends them. Types: Escalation, Reminder, Quiet hours, Away, Fallback, Deliver and Summarize. Add one in Settings > Devices & services > Heads Up > Add policy.

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
- On the card, an Acknowledge button and the line "Acknowledged by Anna" show this; see [Card](card.md#acknowledge).
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

## Quiet hours

Between two times of day, deliveries outside the dashboard are held, sent quietly or dropped. The banner on the dashboard is never affected.

| Field | Default | Meaning |
|---|---|---|
| Quiet from, Quiet until | 22:00 to 07:00 | The window, on the clock of the Home Assistant time zone. A window may cross midnight. The two times must differ. |
| Days | every day | The days a window starts on. A window that starts on Friday ends on Saturday morning. |
| During quiet hours | Send quietly | `quiet`: a push is sent passive and without sound, speech is skipped, a popup is shown as a corner card. `wait`: hold the delivery until the window ends, then send it once. `drop`: do not deliver. |
| Critical messages pass | on | Critical messages ignore the policy. |

- The window follows the wall clock. On the day the clocks change it is one hour shorter or longer. A time that does not exist or occurs twice uses its first occurrence.
- Reminders during the window are skipped, not held, whatever the action.
- A held delivery is stored. After a restart it is still released at the end of the window, once. If the message was cleared, expired or acknowledged meanwhile, or the person dismissed it, nothing is sent and the trace says why.
- If several quiet hours policies are in their window, the strictest action applies: `drop`, then `wait`, then `quiet`.

## Away

A person who is not home when a message is sent gets it when they arrive, if the message is still there.

| Field | Default | Meaning |
|---|---|---|
| Wait for arrival (minutes) | 0 | How long to wait. 0 means as long as the message lives. After that time the delivery is skipped (`max_wait_exceeded`). |

- Away holds only deliveries to an audience, and only for people whose state is known and not `home`. Recipients you list yourself, and people whose presence is unknown, are sent at once.
- Arrival is the person's state changing to `home`. The delivery is sent once. It is not sent if the message was cleared, expired or acknowledged meanwhile, or if that person dismissed or snoozed it.
- Away has no exception for critical messages. Limit its severities if you want critical messages to go out at once.
- Held deliveries are stored and survive a restart.

## Fallback

If the first delivery of a message reached nobody on a channel, the policy delivers on its own channels to its own targets.

| Field | Default | Meaning |
|---|---|---|
| Use when | Nobody to notify | `no_audience`: the audience resolved to nobody (for example nobody is home). `failed`: the person has no usable device or sending failed. `both`: either. |
| Channels, targets | none | As for an escalation: an audience or recipients per channel. |

- A fallback is judged once, after the first delivery of the message. It is not judged again on updates, and escalations, reminders and fallbacks never start a fallback.
- A channel with a delivery that was sent or held counts as reached. The banner does not count.
- Messages from watch rules only have the banner channel, so they have no first delivery to fall back from. Their escalations still pass quiet hours and away.

## Deliver

A call names the channels of its first delivery. A Deliver policy adds channels and targets to it, at once, for the messages it applies to. It is how a critical message reaches phones the moment it appears even when the automation or the watch rule only creates a banner.

| Field | Meaning |
|---|---|
| Channels, targets | As for an escalation: an audience or recipients per channel; speech takes recipients only; a bell notification takes none. |

- It fires once per message, at its first delivery. An update to the message replaces what it sent, like it replaces the call's own deliveries.
- Someone who already has the message on that channel from the call is not notified a second time.
- It passes quiet hours, away and fallback like any delivery. It does not fire for a message held for a summary, and not for a message that became visible while Home Assistant was starting.
- A watch rule message gets it when the policy applies to the tag `rule`. With `policy: none` in the call it is switched off for that call.
- Dismissing, snoozing and acknowledging work as for the call's own deliveries.

## Summarize

A Summarize policy holds the messages it applies to on every channel, including the dashboard banner, and sends one summary instead.

| Field | Default | Meaning |
|---|---|---|
| Summary every (minutes) | 60 | The summary is sent this many minutes after the first message was held. |
| Summary at (time of day) | none | Sends one summary each day at this local time instead of by the interval. |
| Include critical messages | off | Off: critical messages are not held and are delivered at once. |

- A held message is not shown on the dashboard, not counted by the active banners sensor and not sent. Administrators with `show_all` still see it.
- The summary is one message for each recipient and channel: a person's phone gets a push that lists the messages meant for that person; the dashboard gets one banner. It has a count in the title and one line per message, at most ten, then "and N more". The severity is the highest of the messages.
- A message that was cleared before the summary is listed once, marked resolved. Nothing is sent when nothing was held.
- The summary stays for 24 hours or until it is dismissed. It passes through quiet hours, away and fallback like any delivery. It is never held, escalated, reminded or summarized itself.
- The messages stay hidden after their summary; the summary stands for them. A held message that changes its text or severity is listed again in the next summary. A held message that becomes critical is released at once, unless the policy includes critical.
- The hold is decided when the message appears. A policy added later does not hold messages that are already there. Deleting or disabling the policy releases its held messages.
- Held messages and the timer are stored and survive a restart. A summary that came due while Home Assistant was stopped is sent once.
- Watch rule messages are held like any other message when the policy applies to the tag `rule`.

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

- A policy added after the message was sent only starts when the message is next updated.
- Speech and popup channels are not built yet; the `quiet` marker is passed to them when they exist.
- The panel is not built; use the entry's Add policy form.
