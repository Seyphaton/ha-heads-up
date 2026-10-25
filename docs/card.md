# Card

The card `custom:heads-up-card` shows the banners created by `heads_up.create_banner`. It is registered when the integration loads. You do not add a dashboard resource.

Add it in the dashboard YAML editor:

```yaml
type: custom:heads-up-card
```

The card shows a banner while it is active, not dismissed by you, and not removed by timeout, condition or `clear_banner`. Changes appear in an open dashboard without a reload.

## Options

| Option | Type | Default | Meaning |
|---|---|---|---|
| `severity` | list of `critical`, `warning`, `info`, `success` | all | Show only these severities. A single string is accepted. |
| `tag` | list of strings | all | Show only banners with one of these tags. A single string is accepted. |
| `max_items` | integer, 1 or more | no limit | Show at most this many banners, after sorting. |
| `sort` | `severity` or `time` | `severity` | `severity`: critical first, then warning, info, success; newest first within a severity. `time`: newest first. |
| `layout` | `comfortable` or `compact` | `comfortable` | `compact` uses less padding. |
| `show_all` | boolean | `false` | Administrators only: also show banners that are targeted at other people. Ignored for other users. |
| `show_empty` | boolean | `false` | Show an empty card when there are no banners. |

An invalid value makes Home Assistant show a configuration error for the card with the reason.

Example with filters:

```yaml
type: custom:heads-up-card
severity: [critical, warning]
sort: time
max_items: 3
layout: compact
```

## What a banner shows

- An icon and a text label for the severity. Color alone never carries the severity.
- The title (if set) and the message.
- A dismiss button (48×48 px) when the banner is dismissible. What it does depends on `dismiss_scope` (see [actions](actions.md)).
- For administrators, a "Clear for everyone" button on banners that are not dismissible.

Critical banners sit in an `aria-live="assertive"` region, the others in a `polite` one.

## Empty card

With `show_empty: false` the card hides itself when there is nothing to show. On Home Assistant 2026.9.4 in a sections view, the cards above and below then sit at the usual distance and no gap remains. Set `show_empty: true` to keep a visible empty card.

## Tap action

A banner with a `tap_action` is a button. Tapping it passes the action to Home Assistant, which runs it. Tested: `navigate`, with and without `confirmation`. Add a `confirmation` to the tap action to show a dialog first. Any user who can see the banner can run its tap action; see [SECURITY.md](../SECURITY.md).

## Connection loss and restarts

When Home Assistant restarts, the card reconnects by itself. It shows "Heads Up is not available" until the integration has loaded, retries after 1, 2, 5 and 10 seconds and then every 30 seconds, and shows the banners again without a page reload.

## Not supported

- Banner text is shown as written; it is not translated.
- The card has no theme options. Colors come from the theme variables `--info-color`, `--success-color`, `--warning-color`, `--error-color`, `--primary-text-color` and `--card-background-color`.
