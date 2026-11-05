# Push notifications

The push channel sends a message to the Home Assistant Companion app on the phones and tablets of the people you target. It calls the services `notify.mobile_app_<device name>`; it does not use the notify entities, because only the services pass `tag`, `actions` and `clear_notification` on to the app.

```yaml
- action: heads_up.notify
  data:
    id: garage_open
    title: Garage
    message: The garage door has been open for 10 minutes.
    severity: warning
    channels:
      - push
    to:
      push:
        audience: At home
```

## Who receives it

A target is an audience, persons, or a Companion registration ID. A person's devices are found automatically; see [Audiences and recipients](audiences.md). Every device of a person gets the notification. A person with no usable device, a device whose notify service does not exist and a profile that does not accept push are skipped, and the trace says why (`no_usable_device`, `service_not_found`, `channel_not_accepted`).

The response counts of `notify` come from the plan made before sending: `sent` means the notification was handed to the app's service. A service that then fails is a `failed` delivery in the trace (`heads_up/hub_trace`), not in the response.

## What the notification looks like

| Part | Value |
|---|---|
| Title and text | The message's `title` and `message`. |
| `tag` | `hu-<install token>-<message id>`. A new notification with the same tag replaces the old one on the device. |
| `group` | `hu-<install token>`. |
| Level | By severity: `success` and `info` passive, `warning` normal, `critical` time-sensitive. Passive is `importance: low`, normal `default`, time-sensitive `high`, critical `max`. |
| Android delivery | For the levels time-sensitive and critical on Android: `priority: high` and `ttl: 0`, so an idle phone shows the notification at once. |
| Android channel | `heads_up_<level>`. Android keeps the importance a channel had when it was first used, so the channel is named after the level. The level critical uses the channel `alarm_stream` instead, which plays from the alarm stream. |
| Tap | A `navigate` tap action opens its `navigation_path`, a `url` tap action its `url_path`. |
| Image | The message's `image` as `data.image`, which Android and iOS both read. Left out when the lock screen setting is not `full` (`image_hidden` in the trace). Camera proxy paths work on Android only. |
| Buttons | The message's own `actions`, then Snooze when the message is snoozable, then Dismiss when it is dismissible. Android shows at most 3 buttons and iOS 10. Extra buttons are left out and the trace entry says `buttons_clipped:<n>`. Acknowledge and Dismiss are kept first, then the message's own buttons in order, and Snooze goes first. |

A message that ends (cleared, expired, its condition false, dismissed for everyone, evicted) is removed from every device with `clear_notification` and its tag. A user who dismisses or snoozes the banner loses only their own notification. When a snooze ends, that user is notified again. Swiping a notification away changes nothing.

An update to a message replaces the notification in place. An iOS critical notification cannot be replaced, so the hub clears it and sends a new one.

## Buttons

Pressing Acknowledge, Dismiss, Snooze or one of the message's own buttons does the same as pressing it on the banner, for the person the notification was sent to. Snooze uses one time, the option Snooze time on push and popup (15 minutes by default). The choices of `snooze_options` are for the banner. The button's ID is `hu:<message>:<person>:<action>`; the hub trusts nothing else in the event. If the event carries a Home Assistant user and it is not the person's user, the press is ignored and the trace says `user_mismatch`. A press for a message that no longer exists is ignored (`stale_message`). Buttons of other automations are not touched.

## Settings

Set these options on the panel's Channels page. They are stored in the integration options.

| Option | Default | Meaning |
|---|---|---|
| `push_levels` | success and info `passive`, warning `normal`, critical `time-sensitive` | Level per severity. `critical` is an alarm on both platforms. iOS: the critical alert; it needs the app's permission, plays a sound regardless of silent mode and cannot be replaced. Android: the channel `alarm_stream`, which plays from the alarm stream so it sounds in vibrate and silent mode, with `priority: high` and `ttl: 0`. Do Not Disturb is overridden only if you allow it for that channel in the Android settings. |
| `push_lockscreen` | `full` | `full` shows title and text. `title_only` shows the title and a fixed line. `generic` shows "Heads Up" and a fixed line. |
| `push_channel_id` | `heads_up` | Prefix of the Android channel. |
| `push_sticky` | off | Keeps the notification after a tap (Android). |

## Limits

- No retry. A failed push is not tried again.
- A push over 5 per device per minute or 60 in total is skipped (`rate_limited`), and an update with the same content within 30 seconds is ignored (`duplicate`). Critical messages are never held back. See [Notification hub](hub.md#limits-that-protect-the-phones).
- The Acknowledge button appears only when an escalation or reminder policy applies to the message; see [Policies](policies.md). Pressing it acknowledges the message for the person the notification was sent to.
- The behavior on real phones was not checked; the tests use a stand-in for the app.
