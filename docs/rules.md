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
| State | `on` | One or more values. The banner shows while the entity equals any of them. |
| Attribute | none | Compare this attribute instead of the state. |
| Message | – | Banner text, up to 1000 characters. `{name}` becomes the entity's name. |
| Title | none | Up to 100 characters. |
| Severity | `warning` | Color, icon and sort order, as for [actions](actions.md). |
| Icon | severity icon | Replaces the default icon. |
| People | everyone | Show only to users linked to these person entities. |
| Dismissible | off | Off: no close button. On: each user can hide the banner. |
| Enabled | on | Off hides the banner without deleting the rule. |

To change or delete a rule, open it from the same page. Changes apply at once; no restart is needed.

## What you see

- The banner shows while the condition is true and goes away when it is false. It has no timeout.
- While the entity is `unavailable` or `unknown`, or does not exist, the banner is hidden.
- A dismissible rule hides the banner for the user who closed it, until the entity leaves the state and enters it again. A restart also brings it back.
- Rule banners do not count against the banner limit and are never evicted. `sensor.heads_up_active_banners` counts them.
- `heads_up.clear_banner` and `heads_up.clear_all` do not remove them, and administrators cannot clear them in the card. Disable or delete the rule instead.
- Events: see [actions](actions.md#events).
