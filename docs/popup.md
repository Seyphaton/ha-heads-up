# Popups

The popup channel shows a message on top of any dashboard, for the people you target. It needs no card on the dashboard: Heads Up adds one small script (under 1 KB) to every page, which loads the popup code only when a popup is due.

```yaml
- action: heads_up.notify
  data:
    id: garage_open
    title: Garage
    message: The garage door has been open for 10 minutes.
    severity: warning
    channels:
      - popup
    to:
      popup:
        audience: At home
```

## Who sees it

A popup goes to persons, by audience or by `recipients` (person entities). A person needs a linked Home Assistant user to see it; a person without one is skipped (`no_user` in the trace). The popup appears on every dashboard and every device where that user has Home Assistant open. Areas are not supported.

## What it looks like

| Severity | Default |
|---|---|
| success, info, warning | A card in the bottom right corner (full width at phone size). |
| critical | A centered window over a dimmed page. |

- A quiet message (a Quiet hours policy with the action Send quietly) is always a card.
- The option `popup_styles` sets `card`, `modal` or `off` per severity. It has no form yet.
- The severity is written out ("Critical"), not only colored, and uses the theme colors.
- Buttons are at least 48 px high: the message's own buttons, Acknowledge when an escalation or reminder policy applies, Snooze (the first snooze choice) when the message is snoozable, and Dismiss when it can be dismissed. A button's `action` (navigation, confirmation) is not run by the popup; only the event `heads_up_banner_action` is fired.
- One popup is shown at a time, highest severity first, then the oldest. The next one appears when the first is dismissed, closed or resolved.
- The close button (×) and Escape hide the popup on that page only. They do not dismiss the message, and the popup comes back after a reload.
- Dismiss hides it for you on every device and keeps the message for others. Snooze hides it until the snooze ends. Acknowledge hides it on that page and stops escalation and reminders for the message.
- A critical window takes keyboard focus and keeps Tab inside. A card never takes focus. Another window takes focus only while you are not typing in a field.
- With reduced motion set in the system, nothing is animated.
- When the message ends (cleared, expired, condition false) the popup closes.

## Limits

- Popups need an open Home Assistant page. A closed app shows nothing; use push for that.
- The popup is not shown on the login page.
- Not tested with a screen reader.
