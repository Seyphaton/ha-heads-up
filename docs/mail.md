# Mail

The mail channel calls a Home Assistant notify service once per recipient, with a subject and a body. Use it with `heads_up.notify` (`channels: [mail]`). There is no shortcut action. It works with any notify service that takes `title`, `message` and `target`, for example the SMTP integration.

```yaml
- action: heads_up.notify
  data:
    id: water_leak
    title: Water leak
    message: The basement sensor is wet.
    severity: critical
    channels:
      - push
      - mail
    to:
      push:
        audience: Admins
      mail:
        recipients:
          - person.anna
          - Global address
```

## Set it up

Heads Up does not send e-mail itself, so mail does not work until a mail notify service exists.

1. Add the SMTP integration under Settings > Devices & services. It asks for the server, port, connection security, sender, user name and password. It creates a notify service named after the entry.
2. Open the panel, Configuration, Channels, section Mail.
3. Choose the notify service from step 1. Without one, mail fails with `no_mail_service`.
4. Optional: enter a Global address.
5. Open Recipients. For each person who gets mail, switch Mail on and enter the person's mail address.

Mail is off for everyone until step 5. An audience such as Everyone therefore reaches only the persons who opted in.

## Who gets it

`to.mail` takes either an audience or recipients, never both.

| Recipient | What happens |
|---|---|
| A person with Mail on and an address | One call of the notify service with `target: [address]`. |
| A person with Mail on and no address | Fails with `no_mail_address` and a log warning. The Global address is not used instead. |
| A person with Mail off | Skipped with `channel_not_accepted`. |
| `Global address` | One call with the Global address as the target. Fails with `no_mail_address` while the setting is empty. Audiences never include it; name it in `recipients`. |

## Subject and body

The subject and the body are templates. Defaults: subject `{severity}: {title}`, body `{message}`. Change them on the Channels page.

| Placeholder | Value |
|---|---|
| `{severity}` | The severity as a word in your Home Assistant language, for example Critical. |
| `{title}` | The title, or the message when there is no title. |
| `{message}` | The message. |
| `{person}` | The person's name; empty for the Global address. |
| `{id}` | The message id. |
| `{tag}` | The tag; empty when there is none. |

Any other `{name}` is refused when you save. A subject has at most 200 characters, a body at most 2000. The notify service receives the subject as `title` and the body as `message`.

For a shared mailbox that tells recipients apart by subject, give every person the mailbox as their address and set the subject to `{person}`.

## What happens

- A mail cannot be taken back. Clearing, dismissing or ending the message sends nothing and removes nothing.
- An update to a message does not send the mail again (`already_sent`).
- Quiet hours, the speech cooldown and buttons do not apply to mail. The message text is sent; images and buttons are not.
- A failed call or a missing address fires `heads_up_delivery_failed`; see [actions](actions.md#events).

## Limits

- Delivery is the notify service's job. Heads Up knows only whether the service call returned an error, not whether the mail arrived.
- A Quiet hours policy with the action Drop or Wait applies to mail like to other channels.
- After a mail went through the SMTP integration's notify service, the SMTP integration raises a repair that the service is deprecated and due to be removed in Home Assistant 2027.3 (from its source in 2026.10.4).
- Not tested with a real mail server.
