# Actions

Heads Up has eight actions. `create_banner`, `clear_banner` and `clear_all` are the banner actions. `notify`, `push`, `popup`, `speak` and `clear` belong to the notification hub, which delivers one message on several channels. Call them from automations, scripts, blueprints or Developer tools > Actions.

## `heads_up.create_banner`

Shows a banner in every Heads Up card. Calling it again with the same `id` replaces the banner.

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `message` | text | required | Banner text, 1–1000 characters. |
| `id` | text | generated, for example `hu_3f9a1c02b7` | Lowercase letters, digits, `-` and `_`, up to 64 characters. Use your own ID to replace or clear the banner later. |
| `title` | text | none | Up to 100 characters. |
| `severity` | `success`, `info`, `warning`, `critical` | `warning` | Sets color, default icon and sort order. |
| `icon` | icon, for example `mdi:water-alert` | icon of the severity | Replaces the default icon. |
| `timeout` | seconds or duration | integration option, shipped as 24 hours | The banner disappears after this time, also across restarts. `0` means no timeout. Maximum 365 days. |
| `dismissible` | boolean | `true` | Shows a close button. |
| `dismiss_scope` | `user`, `global` | integration option, shipped as `user` | `user`: closing hides the banner only for that user. `global`: closing removes it for everyone. |
| `snoozable` | `true`, `false` | integration option, shipped as `false` | `true`: the card offers a snooze button and, with `swipe_to_dismiss`, a right swipe with quick choices. The banner hides for the chosen time and then returns. Rejected together with `dismissible: false`. |
| `snooze_scope` | `user`, `global` | integration option, shipped as `user` | `user`: a snooze hides the banner only for that user. `global`: for everyone. |
| `snooze_options` | list of durations, 1 minute to 7 days, at most 6 | integration option, shipped as 15 minutes, 1 hour, 4 hours | The choices the viewer gets. The timeout and the condition keep running while a banner is snoozed. Creating the banner again with the same `id`, or a recurring condition turning false and true again, ends all snoozes. |
| `actions` | list of up to 3 buttons | none | Each button has `key` (lowercase letters, digits, `_`, `-`), `label` (1 to 40 characters), optional `dismiss` (`true`: pressing it also closes the banner for that user; rejected with `dismissible: false`) and optional `action` (a Home Assistant action the card runs, like `tap_action`). Pressing a button fires the event `heads_up_banner_action` with `id`, `tag`, `key` and `user_id`. After the message was dismissed, acknowledged or its condition turned false, a press is refused with `message_ended` and fires no event; the option "Disable message buttons once the message has ended" turns this off. A press on a message that was removed is always refused (`not_found`). |
| `tag` | text | none | Group name, same character rules as `id`. Used by card filters and by `clear_banner`. |
| `condition` | object | none | Show the banner only while an entity matches or a template is true, optionally for a set time. See [Conditions](#conditions). |
| `mode` | `once`, `recurring` | `once` | What happens when the condition turns false. Ignored without `condition`. |
| `wait_for_condition` | boolean | `true` | What happens when the condition is false at the time of the call. Ignored without `condition`. |
| `people` | list of person entities | everyone | Show the banner only to the users linked to these people. See [People](#people). |
| `tap_action` | object with `action` | none | Home Assistant action config run when the banner is tapped. Passed to the card unchanged. Anyone who sees the banner can trigger it; see [SECURITY.md](../SECURITY.md). |
| `image` | text | none | A picture shown under the message on the card, in the popup and on the push: an `http://` or `https://` URL, or a path on this Home Assistant starting with `/` (`/local/door.jpg`, `/media/local/door.jpg`). Up to 2048 characters. Heads Up does not fetch or check it; a wrong path shows no picture. Paths under `/api/` and `/media/` are signed for the card and the popup. The phone loads the picture itself, so it must reach the URL; camera proxy paths (`/api/camera_proxy/...`) work on Android only. The compact card layout shows no picture. With a lock screen setting other than `full`, the push has no picture (`image_hidden` in the trace). |

Response data:

| Key | Value |
|---|---|
| `id` | ID of the banner. |
| `status` | `created`, `updated`, `waiting` (stored, condition not true yet) or `condition_false` (nothing stored). |
| `evicted` | Only present when a banner was removed to make room. ID of that banner. |

Replacing a banner with the same `id`:

- Every field takes the value of the new call. Fields you leave out get their defaults; they do not keep the old value.
- The timeout starts again.
- Users who closed the banner see it again.

When Heads Up is full (option, default 50 banners), it removes the oldest banner with the lowest severity: `success` first, then `info`, then `warning`. It never removes a `critical` banner. If no banner can be removed, the call fails with "Heads Up already holds 50 banners and none can be evicted."

```yaml
- action: heads_up.create_banner
  data:
    id: front_door
    title: Front door open
    message: The front door has been open for 10 minutes.
    severity: warning
    timeout:
      minutes: 30
```

```yaml
- action: heads_up.create_banner
  data:
    message: Water detected under the dishwasher.
    severity: critical
    timeout: 0
    dismissible: false
    tap_action:
      action: navigate
      navigation_path: /lovelace/kitchen
  response_variable: banner
```

### Buttons and snooze

A banner that can be snoozed for 30 minutes or 2 hours, with one button that closes it for the user who pressed it and fires an event:

```yaml
action: heads_up.create_banner
data:
  id: laundry_done
  message: The washing machine has finished.
  severity: info
  snoozable: true
  snooze_options:
    - minutes: 30
    - hours: 2
  actions:
    - key: ack
      label: Got it
      dismiss: true
```

An automation can react to the button:

```yaml
triggers:
  - trigger: event
    event_type: heads_up_banner_action
    event_data:
      id: laundry_done
      key: ack
```

Snooze needs `dismissible: true`. A new call with the same `id`, or a recurring condition turning false and true again, ends all snoozes. The card runs a button's `action` itself, so a button that opens a dashboard works only where a card is open.

### Conditions

`condition` takes these keys. Use either `entity_id` (with `operator`, `state` and `attribute`) or `template`, not both. `for` works with both.

| Key | Required / default | Meaning |
|---|---|---|
| `entity_id` | required unless `template` is set | Entity to watch. It must exist when you call the action. |
| `template` | none | A Home Assistant template. The condition holds while it renders true (`true`, `on`, `yes`, `1`). It cannot be combined with `entity_id`, `operator`, `state` or `attribute`. |
| `for` | none | How long the condition must hold without a break before the banner shows, for example `{minutes: 5}` or `"00:05:00"`. From 1 second to 24 hours. See below. |
| `operator` | `equals` | How to compare. See the table below. |
| `state` | `"on"` for `equals` and `not_equals`; required for the others except `empty` and `not_empty`, which ignore it | Value or values to compare with. |
| `attribute` | none | Compare this attribute instead of the state. The attribute value is compared as text. |

| `operator` | `state` | Matches when |
|---|---|---|
| `equals` | text or list | The value equals any of them. |
| `not_equals` | text or list | The value equals none of them. |
| `above` | one number | The value is greater than the number. |
| `below` | one number | The value is less than the number. |
| `between` | two numbers, low then high | The value is from low to high, both included. |
| `contains` | text or list | The value contains any of the texts. |
| `not_contains` | text or list | The value contains none of the texts. |
| `empty` | not used | The value is empty or only spaces. A missing attribute counts as empty. |
| `not_empty` | not used | The value has text other than spaces. A missing attribute does not match. |

What you see:

- While the entity matches, the banner shows.
- `mode: once`: the first time the entity stops matching, the banner is removed for good. The event `heads_up_banner_cleared` has `reason: condition`.
- `mode: recurring`: the banner hides while the entity does not match and shows again when it matches. Users who closed it see it again.
- `unavailable` and `unknown` do not change anything, for every operator. `not_equals: "on"` does not match an unavailable entity. A banner stays as it was until the entity has a real state again. This also applies while Home Assistant starts and entities are not loaded yet.
- `empty` and `not_empty` work on the state or the attribute. An empty list or object counts as empty. `unavailable` and `unknown` still change nothing.
- `above`, `below` and `between` do not change anything while the value is not a number. The other operators do not change anything while the attribute is missing.
- If the entity does not match when you call the action, the banner waits and shows when the entity matches. With `wait_for_condition: false`, nothing is stored and the response status is `condition_false`. A banner that already had this `id` is removed.
- The `timeout` keeps running while a banner waits.

#### `for`: hold for a while

- The banner shows only after the condition has been true for the whole `for` time. If it turns false first, the wait starts again the next time it is true. While it waits the response status is `waiting`.
- Once shown, the banner follows the condition as usual: `mode: once` removes it, `mode: recurring` hides it and waits `for` again the next time.
- After a Home Assistant restart or an integration reload, a banner that was already shown stays. A banner that was still waiting starts its wait again from the restart.
- If the entity is `unavailable` or `unknown` when the wait ends, nothing is shown; the wait starts again when it has a matching state.
- `for` is not combined with `wait_for_condition: false`: with a true condition the banner would have to wait, so nothing is stored.
- Keep `for` shorter than `timeout`, which keeps running during the wait.

#### `template`: any condition you can write

- The template is checked when you call the action. A template that does not render yet (for example a missing entity) leaves the banner waiting.
- Home Assistant re-evaluates it when an entity it reads changes, and for time functions such as `now()` on their own schedule.
- A template that fails to render later leaves the banner as it was and logs a message at debug level.

```yaml
- action: heads_up.create_banner
  data:
    id: window_bedroom
    message: The bedroom window is open.
    condition:
      entity_id: binary_sensor.bedroom_window
      state: "on"
```

```yaml
- action: heads_up.create_banner
  data:
    id: vacuum_stuck
    message: The vacuum needs help.
    mode: recurring
    timeout: 0
    condition:
      entity_id: vacuum.downstairs
      state: [error, idle]
```

```yaml
- action: heads_up.create_banner
  data:
    id: living_room_hot
    message: The living room is warm.
    mode: recurring
    timeout: 0
    condition:
      entity_id: sensor.living_room_temperature
      operator: above
      state: 25
```

```yaml
- action: heads_up.create_banner
  data:
    id: note_set
    message: A note was left.
    mode: recurring
    timeout: 0
    condition:
      entity_id: input_text.door_note
      operator: not_empty
```

```yaml
- action: heads_up.create_banner
  data:
    id: garage_open
    message: The garage door has been open for 10 minutes.
    mode: recurring
    timeout: 0
    condition:
      entity_id: cover.garage_door
      state: "open"
      for:
        minutes: 10
```

```yaml
- action: heads_up.create_banner
  data:
    id: evening_window
    message: A window is open in the evening.
    mode: recurring
    timeout: 0
    condition:
      template: "{{ is_state('binary_sensor.bedroom_window', 'on') and now().hour >= 20 }}"
```

### People

`people` lists person entities, for example `person.alex`. A user sees the banner if one of the listed people is linked to that user. The link is the person's `user_id` attribute, visible in Developer tools > States. Users without a linked person only see banners without `people`.

Targeting decides who receives the banner in the card. It is not access control: administrators can see all banners with the card option `show_all`, and anyone with access to the Home Assistant files can read them. Do not put secrets in banners.

```yaml
- action: heads_up.create_banner
  data:
    message: Your parcel was delivered.
    severity: info
    people:
      - person.alex
```

## `heads_up.clear_banner`

Removes banners by `id`, by `tag`, or both. With both, a banner must match both.

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `id` | text | one of `id` or `tag` | ID of the banner to remove. |
| `tag` | text | one of `id` or `tag` | Removes every banner with this tag. |

Response data: `cleared`, the number of removed banners. An unknown ID returns `cleared: 0`; it is not an error.

```yaml
- action: heads_up.clear_banner
  data:
    tag: laundry
```

## `heads_up.clear_all`

Removes every banner, including banners that cannot be closed. No fields. Response data: `cleared`, the number of removed banners.

```yaml
- action: heads_up.clear_all
```

## `heads_up.clear`

Removes messages by `id`, by `tag`, or both, from every channel. `clear_banner` removes only messages that have the banner channel; `clear` also removes messages without it, such as a `notify` call with `channels: [push]` and an `id`.

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `id` | text | one of `id` or `tag` | ID of the message to remove. |
| `tag` | text | one of `id` or `tag` | Removes every message with this tag. |

Response data: `cleared`, the number of removed messages.

```yaml
- action: heads_up.clear
  data:
    id: garage_open
```

## `heads_up.notify`

Delivers one message on the channels you name. It takes the content and lifecycle fields of [`create_banner`](#headsupcreate_banner) and adds the channel fields below. It has no `people` field: use `to.banner.recipients`. Calling it again with the same `id` replaces the message.

The hub is on by default. With the hub switched off in the integration options, only `channels: [banner]` works and `notify` behaves like `create_banner`; other channels fail with the error "The hub is switched off".

Channels: `banner`, `push`, `popup`, `speak`, `persistent`, `mail`. See [Push notifications](push.md), [Popups](popup.md), [Speech](speech.md), [Persistent notifications](persistent.md) and [Mail](mail.md).

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `message` | text | required | Message text, 1–1000 characters. |
| `id` | text | generated | As in `create_banner`. |
| `title` | text | none | Up to 100 characters. |
| `severity` | `success`, `info`, `warning`, `critical` | `warning` | As in `create_banner`. |
| `icon` | icon | icon of the severity | As in `create_banner`. |
| `timeout` | seconds or duration | integration option | As in `create_banner`. |
| `dismissible` | boolean | `true` | As in `create_banner`. |
| `dismiss_scope` | `user`, `global` | integration option | As in `create_banner`. |
| `snoozable` | `true`, `false` | integration option | As in `create_banner`. |
| `snooze_scope` | `user`, `global` | integration option | As in `create_banner`. |
| `snooze_options` | list of durations | integration option | As in `create_banner`. |
| `actions` | list of up to 3 buttons | none | As in `create_banner`. |
| `tag` | text | none | As in `create_banner`. |
| `condition` | object | none | As in `create_banner`. See [Conditions](#conditions). |
| `mode` | `once`, `recurring` | `once` | As in `create_banner`. |
| `wait_for_condition` | boolean | `true` | As in `create_banner`. |
| `tap_action` | object with `action` | none | As in `create_banner`. |
| `image` | text | none | As in `create_banner`. |
| `tts_message` | text | the title if set, otherwise the message | Text for the speak channel instead of the title and message. |
| `channels` | list of channels | required | One or more of the five channels, each at most once. |
| `to` | object | none | A target per channel: `audience` (a name) or `recipients` (a list), never both. `push`, `popup`, `speak` and `mail` need a target. Audience and recipient names are described in [Audiences and recipients](audiences.md). `speak` takes recipients only. `persistent` takes no target and goes to everyone (see [Persistent notifications](persistent.md)). `banner` is optional: recipients limit the banner to the users linked to those persons. An audience does the same with the persons it has when the call is made; a person who joins the audience later does not see a banner that already exists, and an audience that is empty then gives a banner nobody sees. |
| `policy` | text | every policy that applies | A policy name, or `none` for no policy behavior. See [Policies](policies.md). |

Response data: `id`, `status` (`created`, `updated`, `waiting` or `condition_false`, as in `create_banner`), and `channels`: for each channel the counts `sent`, `held`, `skipped` and `failed`. A banner that waits for its condition counts as `held`.

A message without the `banner` channel is stored so it can be updated and cleared, but the card does not show it. The names in `to` and `policy` are checked when you call the action; a name that does not exist fails with an error that lists the valid names.

```yaml
- action: heads_up.notify
  data:
    id: garage_open
    title: Garage
    message: The garage door has been open for 10 minutes.
    severity: warning
    channels:
      - banner
      - push
    to:
      push:
        recipients:
          - person.alex
```

## `heads_up.push`

Shortcut for `notify` with `channels: [push]` and no policies. It needs `audience` or `recipients`. With an `id` the message is tracked like a `notify` message and is removed by `heads_up.clear`. Without an `id` it is delivered once and no record is kept, so a later `clear` cannot take it back. The response holds `id`, `status` (`sent_once` without an `id`) and `channels`, as in `notify`. See [Push notifications](push.md).

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `message` | text | required | Message text, 1–1000 characters. |
| `id` | text | none | Tracks the message when set. |
| `title` | text | none | Up to 100 characters. |
| `severity` | `success`, `info`, `warning`, `critical` | `warning` | As in `create_banner`. |
| `icon` | icon | icon of the severity | As in `create_banner`. |
| `timeout` | seconds or duration | integration option | Only used when `id` is set. |
| `actions` | list of up to 3 buttons | none | As in `create_banner`. |
| `tag` | text | none | As in `create_banner`. |
| `tap_action` | object with `action` | none | As in `create_banner`. |
| `image` | text | none | As in `create_banner`. |
| `tts_message` | text | the title if set, otherwise the message | Text for the speak channel. |
| `recipients` | list | one of `audience` or `recipients` | Persons, phones, speakers or groups, depending on the channel. |
| `audience` | text | one of `audience` or `recipients` | Name of an audience. Not available for `speak`. |

```yaml
- action: heads_up.push
  data:
    message: The washing machine is done.
    recipients:
      - person.alex
```

## `heads_up.popup`

Shortcut for `notify` with `channels: [popup]` and no policies. It needs `audience` or `recipients`; the fields are those of `heads_up.push`. With an `id` the message is tracked like a `notify` message and is removed by `heads_up.clear`. Without an `id` it is delivered once and no record is kept, so a later `clear` cannot take it back. The response holds `id`, `status` (`sent_once` without an `id`) and `channels`, as in `notify`. See [Popups](popup.md).

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `message` | text | required | Message text, 1–1000 characters. |
| `id` | text | none | Tracks the message when set. |
| `title` | text | none | Up to 100 characters. |
| `severity` | `success`, `info`, `warning`, `critical` | `warning` | As in `create_banner`. |
| `icon` | icon | icon of the severity | As in `create_banner`. |
| `timeout` | seconds or duration | integration option | Only used when `id` is set. |
| `actions` | list of up to 3 buttons | none | As in `create_banner`. |
| `tag` | text | none | As in `create_banner`. |
| `tap_action` | object with `action` | none | As in `create_banner`. |
| `image` | text | none | As in `create_banner`. |
| `tts_message` | text | the title if set, otherwise the message | Text for the speak channel. |
| `recipients` | list | one of `audience` or `recipients` | Persons, phones, speakers or groups, depending on the channel. |
| `audience` | text | one of `audience` or `recipients` | Name of an audience. Not available for `speak`. |

```yaml
- action: heads_up.popup
  data:
    message: Someone is at the door.
    audience: At home
```

## `heads_up.speak`

Shortcut for `notify` with `channels: [speak]` and no policies. It needs `recipients` (speakers or groups) and has no `audience` field, because speech goes to speakers, not to people. With an `id` the message is tracked like a `notify` message and is removed by `heads_up.clear`. Without an `id` it is delivered once and no record is kept, so a later `clear` cannot take it back. The response holds `id`, `status` (`sent_once` without an `id`) and `channels`, as in `notify`. See [Speech](speech.md).

| Field | Type | Required / default | Meaning |
|---|---|---|---|
| `message` | text | required | Message text, 1–1000 characters. |
| `id` | text | none | Tracks the message when set. |
| `title` | text | none | Up to 100 characters. |
| `severity` | `success`, `info`, `warning`, `critical` | `warning` | As in `create_banner`. |
| `icon` | icon | icon of the severity | As in `create_banner`. |
| `timeout` | seconds or duration | integration option | Only used when `id` is set. |
| `actions` | list of up to 3 buttons | none | As in `create_banner`. |
| `tag` | text | none | As in `create_banner`. |
| `tap_action` | object with `action` | none | As in `create_banner`. |
| `tts_message` | text | the title if set, otherwise the message | Text for the speak channel. |
| `recipients` | list | one of `audience` or `recipients` | Persons, phones, speakers or groups, depending on the channel. |

```yaml
- action: heads_up.speak
  data:
    message: Dinner is ready.
    recipients:
      - media_player.kitchen
```

## Errors

| Message | Cause |
|---|---|
| Heads Up is not set up. Add the integration first. | The integration is not added or is disabled. |
| Heads Up already holds N banners and none can be evicted. | The limit is reached and every banner is `critical`, or eviction is turned off. |
| Condition entity X does not exist. | `condition.entity_id` names an entity Home Assistant does not know. |
| Validation error on `template`, `for` or an entity field | The template does not parse, `for` is over 24 hours, or `template` is combined with `entity_id`, `operator`, `state` or `attribute`. |
| The hub is switched off. | `notify` names a channel other than `banner`, or a shortcut is called, while the hub is off. |
| Audience, recipient or policy "X" does not exist. | A name in `to`, `audience`, `recipients` or `policy` is unknown. The message lists the valid names. |
| Validation error naming the field | A field breaks the rules in the tables above. Nothing is stored. |

## Events

Each change fires an event. Use them as automation triggers.

| `event_type` | Data |
|---|---|
| `heads_up_banner_created` | `id`, `severity`, `tag` |
| `heads_up_banner_updated` | `id`, `severity`, `tag` |
| `heads_up_banner_dismissed` | `id`, `tag`, `scope` (`user` or `global`), `user_id` |
| `heads_up_banner_snoozed` | `id`, `tag`, `scope` (`user` or `global`), `user_id`, `until` |
| `heads_up_banner_unsnoozed` | `id`, `tag`, `user_id` |
| `heads_up_banner_action` | `id`, `tag`, `key`, `user_id` |
| `heads_up_banner_expired` | `id`, `tag` |
| `heads_up_banner_cleared` | `id`, `tag`, `reason` (`action`, `clear_all`, `condition`, `evicted`, `admin`, `rule`) |
| `heads_up_delivery_failed` | `id`, `tag`, `channel`, `origin`, `reached`, `failed` |

Banners from [watch rules](rules.md) fire `created` when the entity enters the state and `cleared` with `reason: rule` when it leaves, or when the rule is disabled or deleted. Their `id` starts with `rule_` and their `tag` is `rule`.

`heads_up_delivery_failed` fires once per channel and delivery step when a send failed or the message reached nobody on that channel. `origin` is `message` (the call itself), `escalation`, `reminder`, `fallback` or `deliver`. `reached` counts the recipients that got it. `failed` lists `{recipient, reason}` and, when the recipient is a person's device, `person`. The reasons are `send_failed`, `service_not_found`, `device_missing`, `entity_missing`, `no_tts_engine`, `no_recipients`, `no_usable_device`, `channel_not_accepted`, `group_empty`, `unknown_audience`, `unknown_recipient`, `person_not_found`, `no_user`, `presence_unknown` and `rate_limited`. Quiet hours, holds, duplicates and the speech cooldown are choices, not failures, and fire nothing. A dry run in the panel fires nothing, and neither does the first delivery after a restart. The banner channel never fires it.

```yaml
triggers:
  - trigger: event
    event_type: heads_up_delivery_failed
    event_data:
      channel: push
conditions:
  - condition: template
    value_template: "{{ trigger.event.data.reached == 0 }}"
```

A banner whose timeout passed while Home Assistant was stopped is removed at the next start and fires `heads_up_banner_expired` then.

```yaml
triggers:
  - trigger: event
    event_type: heads_up_banner_dismissed
    event_data:
      id: front_door
```
