# Watch rules

A watch rule shows a banner while an entity is in a state. You set it up once in the integration. No automation, script or dashboard setting is needed, and every Heads Up card shows the banner.

## Add a rule

1. Go to Settings > Devices & services > Heads Up.
2. Choose "Add watch rule".
3. Fill in the form and submit.

| Field | Default | Meaning |
|---|---|---|
| Rule name | – | Shown in the list of rules only. |
| Entity | – | The entity to watch. It must exist when you save. |
| Condition | Equals | How to compare: equals, does not equal, above, below, between, contains text, does not contain text. |
| State | `on` for equals and does not equal | The values to compare with. Above and below take one number, between takes two (low, high). |
| Attribute | none | Compare this attribute instead of the state. The value is compared as text; numeric conditions need a number. |
| Condition must hold for | none | Optional, up to 24 hours. The banner appears only after the condition has held this long without a break. After a restart the wait starts again. |
| Message | – | Banner text, up to 1000 characters. `{name}` becomes the entity's name. Home Assistant templates such as `{{ states('input_text.reason') }}` are rendered; the text updates when the entities the template reads change (not for `now()`). |
| Title | none | Up to 100 characters. |
| Severity | `warning` | Color, icon and sort order, as for [actions](actions.md). |
| Icon | severity icon | Replaces the default icon. |
| People | everyone | Show only to users linked to these person entities. |
| Dismissible | off | Off: no close button. On: each user can hide the banner. |
| Enabled | on | Off hides the banner without deleting the rule. |

To change or delete a rule, open it from the same page. Changes apply at once; no restart is needed.

<img src="images/watch-rule.png" width="500" alt="The Add watch rule form: rule name, entity, condition, state">

## Examples

Each row is one rule. `{name}` in the message becomes the entity's name. The condition columns are what you enter in "Condition" and "State".

| Goal | Entity | Attribute | Condition | State | Message | Severity |
|---|---|---|---|---|---|---|
| Window open | `binary_sensor.bedroom_window` | none | Equals | `on` | `{name} is open.` | warning |
| Door not locked | `lock.front_door` | none | Does not equal | `locked` | `{name} is not locked.` | critical |
| Dishwasher not idle or off | `sensor.dishwasher_status` | none | Does not equal | `idle`, `off` | `{name} is running.` | info |
| Room too warm | `sensor.living_room_temperature` | none | Above | `25` | `The living room is warmer than 25 °C.` | info |
| Room too cold | `sensor.living_room_temperature` | none | Below | `16` | `The living room is colder than 16 °C.` | warning |
| Battery low | `sensor.phone_battery` | none | Between | `5`, `15` | `The phone battery is low.` | warning |
| Printer reports a problem | `sensor.printer_status` | none | Contains text | `error`, `jam` | `The printer reports a problem.` | warning |
| Garage door not closed | `cover.garage_door` | `current_position` | Above | `0` | `{name} is open.` | warning |
| Door open too long | `binary_sensor.front_door` | none | Equals | `on` | `{name} has been open for 5 minutes.` | warning |

Notes:

- "Does not equal" with several values matches when the value equals none of them.
- "Above" and "below" take one number and exclude it. "Between" takes two numbers, low then high, and includes both.
- "Contains text" matches when any of the values is part of the state. "Does not contain text" matches when none is.
- The value is compared as text for equals, does not equal and contains. The numeric conditions need a number in the state or attribute.

## What you see

- The banner shows while the condition is true and goes away when it is false. It has no timeout.
- With "Condition must hold for" set, a true condition first waits. The banner shows after that time, and the "time ago" text counts from then. If the condition turns false first, the wait starts again. Disabling, changing or deleting the rule also starts it again or ends it. For the example "Door open too long" set 5 minutes.
- While the entity is `unavailable` or `unknown`, or does not exist, the banner is hidden. This includes "does not equal": a rule "is not `on`" does not show for an unavailable entity.
- A numeric condition hides the banner while the value is not a number. A missing attribute hides it for every condition except equals, where it does not match.
- Rules saved before conditions existed keep working as "equals".
- A dismissible rule hides the banner for the user who closed it, until the entity leaves the state and enters it again. A restart also brings it back.
- Rule banners do not count against the banner limit and are never evicted. `sensor.heads_up_active_banners` counts them.
- `heads_up.clear_banner` and `heads_up.clear_all` do not remove them, and administrators cannot clear them in the card. Disable or delete the rule instead.
- Events: see [actions](actions.md#events).
