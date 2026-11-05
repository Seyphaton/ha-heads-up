# Settings

Settings are the defaults and limits of the integration. A field you leave out of an action call takes its value from here. This page lists every setting with its default and what it changes.

## Where to change them

- Settings > Devices & services > Heads Up > Configure.
- The Settings page of the [panel](panel.md#settings). It shows the same entries in the same order and wording, and a change in one shows in the other.
- The channel settings (push levels, popup styles, lock screen text, spoken language and mail) are on the panel's Channels page and under Configure.

A change applies at once. Message defaults apply to messages created afterwards; they do not change messages that already exist.

## Panel

| Setting | Default | Meaning |
|---|---|---|
| Show Heads Up in the sidebar (`show_panel`) | off; the setup flow switches it on | Shows the panel in the sidebar of administrators. Without the panel you cannot use Test send, the Message Log, the Overview, the introduction that creates the default policies, the Channels settings or the Help pages. Audiences, recipients, policies, watch rules and the other settings stay editable under Devices & services. |

## Message defaults

These settings belong to the message, not to one channel. They apply to the banner, the push and the popup of a message, and to a message that has no banner. An action field overrides the setting for that message.

| Setting | Default | Used when the call sets no | Meaning |
|---|---|---|---|
| Default dismiss scope (`default_dismiss_scope`) | `user` | `dismiss_scope` | `user`: closing hides the message only for that person and takes back only their push. `global`: closing ends the message for everyone. |
| Default timeout (`default_timeout`) | 24 hours | `timeout` | The message ends on every channel after this time. Empty or 0 keeps messages until they are closed or cleared. |
| Disable message buttons once the message has ended (`disable_ended_buttons`) | on | none | A press on the message's own buttons, on the banner, the push or the popup, is refused with `message_ended` after the message was dismissed (by that person or for everyone), acknowledged by anyone, or its condition turned false. A snooze does not end it. Dismiss, Snooze and Acknowledge are not affected. Off: presses are accepted until the message is removed. |
| Messages can be snoozed by default (`default_snoozable`) | off | `snoozable` | Adds Snooze to the banner, the push and the popup. Messages that are not dismissible are never snoozable. |
| Default snooze scope (`default_snooze_scope`) | `user` | `snooze_scope` | `user`: a snooze hides the message only for that person. `global`: for everyone. |
| Snooze choices on the banner (`default_snooze_options`) | 15 minutes, 1 hour, 4 hours | `snooze_options` | The choices the banner offers, from 5 minutes to 24 hours. |
| Snooze time on push and popup (`quick_snooze_minutes`) | 15 (1–1440) | none | The Snooze button of the push and of the popup snoozes for this many minutes, whatever `snooze_options` says. |

## Limits

| Setting | Default | Meaning |
|---|---|---|
| Maximum number of stored messages (`max_banners`) | 50 (1–200) | How many messages from action calls can exist at once, on any channel. Watch rules do not count. It protects storage and timers, not the phones or the card (the card has `max_items`). It is not a rate limit. |
| Evict the oldest lowest-severity message when full (`evict`) | on | When off, creating a message beyond the limit fails. `critical` messages are never evicted, so a full house of critical messages fails new calls. An evicted message ends on every channel. |
| Pushes per device per minute (`rate_per_device_per_minute`) | 5 (1–600) | A push over the cap is skipped and the trace says `rate_limited`. Critical messages are never held back. |
| Deliveries per minute, all devices (`rate_total_per_minute`) | 60 (1–6000) | The same, counted over all devices. |
| Seconds in which identical updates are ignored (`dedupe_seconds`) | 30 (0–3600) | An update with the same content is not sent again to the same recipient within this time (`duplicate`). 0 switches it off. Critical messages are never held back. |

## Presence

| Setting | Default | Meaning |
|---|---|---|
| Presence delay (`presence_debounce_seconds`) | 60 seconds (0–600) | How long a person must stay home or away before the audiences Last to leave and First home change. 0 reacts at once. |

## Push

| Setting | Default | Meaning |
|---|---|---|
| Push level per severity (`push_levels`) | success and info `passive`, warning `normal`, critical `time-sensitive` | The level of the notification. `critical` is an alarm on both platforms: the critical alert on iOS (needs the app's permission, plays in silent mode) and the alarm channel on Android (sounds in vibrate and silent mode; Do Not Disturb is overridden only if you allow it for that channel in the Android settings). |
| Lock screen text (`push_lockscreen`) | `full` | `full` shows title and text. `title_only` shows the title and a fixed line. `generic` shows "Heads Up" and a fixed line. |
| Android channel name (`push_channel_id`) | `heads_up` | Prefix of the Android notification channel. |
| Keep after tap (`push_sticky`) | off | Keeps the notification after a tap (Android). |

See [Push notifications](configuration.md#push).

## Popup

| Setting | Default | Meaning |
|---|---|---|
| Popup style per severity (`popup_styles`) | success, info and warning `card`; critical `modal` | `card` is a card in the bottom right corner, `modal` a centered window over a dimmed page, `off` shows nothing. |

See [Popups](configuration.md#popup).

## Speech

| Setting | Default | Meaning |
|---|---|---|
| Spoken text: longest (`speak_max_length`) | 200 characters (20–1000) | Longer texts are cut after the last word that fits. |
| Spoken text: repeat pause (`speak_cooldown_seconds`) | 60 seconds (0–3600) | The same text is not spoken again on the same speaker within this time. 0: always speak. |
| Text-to-speech engine (`speak_tts_entity`) | automatic | The engine for media players. Automatic: the only text-to-speech entity, if there is exactly one. |
| Spoken language (`speak_language`) | the Home Assistant language | The language of the speech. |

See [Speech](configuration.md#speech).

## Mail

| Setting | Default | Meaning |
|---|---|---|
| Notify service (`mail_service`) | none | The Home Assistant notify service that sends the mail. Without one, mail fails with `no_mail_service`. |
| Global address (`mail_global_address`) | none | A shared address that a call names as `Global address`. |
| Subject (`mail_subject`) | `{severity}: {title}` | A template, up to 200 characters. |
| Body (`mail_body`) | `{message}` | A template, up to 2000 characters. |

See [Mail](configuration.md#mail).

## History

| Setting | Default | Meaning |
|---|---|---|
| Trace entries kept (`trace_entries`) | 500 (50–5000) | The size of the delivery trace. |
| Recent messages kept (`recent_messages`) | 100 (10–1000) | The size of the list of recent messages in the Message Log. |

The trace, the recent messages and the log of last actions are kept in memory and start empty after a restart.

## Install token

The install token is shown on the options screen and in the panel, read only. It is part of every push tag and group name (`hu-<install token>-<message id>`).
