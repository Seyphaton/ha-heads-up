# Persistent notifications

The persistent channel shows a message in Home Assistant's notification bell. Use it with `heads_up.notify` (`channels: [persistent]`). There is no shortcut action.

```yaml
- action: heads_up.notify
  data:
    id: backup_failed
    title: Backup
    message: The nightly backup failed.
    severity: warning
    channels:
      - banner
      - persistent
```

## Who sees it

Everyone who uses Home Assistant: the bell has one list for all users. The channel takes no target, and `to.persistent` is refused. Use push or popups to reach single people.

## What happens

- One entry per message, with the id `hu_<message id>`, the message's title and text.
- An update to the message replaces the entry.
- When the message ends (cleared, expired, condition false, dismissed for everyone, evicted), the entry is dismissed. A dismissal or snooze by one user changes nothing, because the bell is shared.
- A restart does not create the entry again. An entry whose message ended while Home Assistant was stopped is dismissed at startup.
- Dismissing the entry in the bell is not reported back to Heads Up. The message stays; a later update creates the entry again.

## Failures

A missing `persistent_notification` service or a failing call gives a `failed` delivery in the trace (`heads_up/hub_trace`) with the reason `service_not_found` or `send_failed`.

## Limits

- No per-user entries, no buttons, no Acknowledge or Snooze.
- A rule message reaches the bell only through an escalation or fallback policy.
