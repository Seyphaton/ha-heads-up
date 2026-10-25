# Actions

Heads Up has three actions. Call them from automations, scripts, blueprints or Developer tools > Actions.

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
| `tag` | text | none | Group name, same character rules as `id`. Used by card filters and by `clear_banner`. |
| `condition` | object | none | Show the banner only while an entity matches. See [Conditions](#conditions). |
| `mode` | `once`, `recurring` | `once` | What happens when the condition turns false. Ignored without `condition`. |
| `wait_for_condition` | boolean | `true` | What happens when the condition is false at the time of the call. Ignored without `condition`. |
| `people` | list of person entities | everyone | Show the banner only to the users linked to these people. See [People](#people). |
| `tap_action` | object with `action` | none | Home Assistant action config run when the banner is tapped. Passed to the card unchanged. Anyone who sees the banner can trigger it; see [SECURITY.md](../SECURITY.md). |

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

### Conditions

`condition` takes three keys:

| Key | Required / default | Meaning |
|---|---|---|
| `entity_id` | required | Entity to watch. It must exist when you call the action. |
| `state` | `"on"` | Value to match, or a list of values. Matches if the value equals any of them. |
| `attribute` | none | Compare this attribute instead of the state. The attribute value is compared as text. |

What you see:

- While the entity matches, the banner shows.
- `mode: once`: the first time the entity stops matching, the banner is removed for good. The event `heads_up_banner_cleared` has `reason: condition`.
- `mode: recurring`: the banner hides while the entity does not match and shows again when it matches. Users who closed it see it again.
- `unavailable` and `unknown` do not change anything. A banner stays as it was until the entity has a real state again. This also applies while Home Assistant starts and entities are not loaded yet.
- If the entity does not match when you call the action, the banner waits and shows when the entity matches. With `wait_for_condition: false`, nothing is stored and the response status is `condition_false`. A banner that already had this `id` is removed.
- The `timeout` keeps running while a banner waits.

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

## Errors

| Message | Cause |
|---|---|
| Heads Up is not set up. Add the integration first. | The integration is not added or is disabled. |
| Heads Up already holds N banners and none can be evicted. | The limit is reached and every banner is `critical`, or eviction is turned off. |
| Condition entity X does not exist. | `condition.entity_id` names an entity Home Assistant does not know. |
| Validation error naming the field | A field breaks the rules in the tables above. Nothing is stored. |

## Events

Each change fires an event. Use them as automation triggers.

| `event_type` | Data |
|---|---|
| `heads_up_banner_created` | `id`, `severity`, `tag` |
| `heads_up_banner_updated` | `id`, `severity`, `tag` |
| `heads_up_banner_dismissed` | `id`, `tag`, `scope` (`user` or `global`), `user_id` |
| `heads_up_banner_expired` | `id`, `tag` |
| `heads_up_banner_cleared` | `id`, `tag`, `reason` (`action`, `clear_all`, `condition`, `evicted`, `admin`, `rule`) |

Banners from [watch rules](rules.md) fire `created` when the entity enters the state and `cleared` with `reason: rule` when it leaves, or when the rule is disabled or deleted. Their `id` starts with `rule_` and their `tag` is `rule`.

A banner whose timeout passed while Home Assistant was stopped is removed at the next start and fires `heads_up_banner_expired` then.

```yaml
triggers:
  - trigger: event
    event_type: heads_up_banner_dismissed
    event_data:
      id: front_door
```
