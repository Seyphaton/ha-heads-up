# Security

## Report a vulnerability

Open a private security advisory on the GitHub repository.

## What `people` does and does not protect

`people` decides which users receive a banner in the Heads Up card. It is not access control.

- Administrators can see every banner with the card option `show_all`.
- Banners are stored in plain text in `.storage/heads_up.banners`. Anyone with access to the Home Assistant files or backups can read them.
- Inbox items are stored in plain text in `.storage/heads_up.inbox`: title, text and the channels that delivered them, for every person who received a message on the inbox channel. Anyone with access to the Home Assistant files or backups can read them. With the setting Add an optional "Show all notifications" section to the inbox switched on (Channels page, off by default), the title and text of every notification that reached a person on push, popup, mail, the banner or a speaker are stored in their inbox too. Items are removed after the retention (12 months by default, up to 36), at most 2000 per person are kept, and Clear inbox on the Inbox row of the Channels page deletes them all. They are also removed with the integration. The inbox commands of the card return and change only the items of the calling user's own person, for an administrator too, and their results never contain another person's text. The unread sensor of each person holds counts only, because every user can read entity states.
- Messages between people (off by default, Channels page, Inbox row): the text of a message one person sends to others is stored in plain text in `.storage/heads_up.inbox`, once for each recipient and once as the sender's Sent entry, which also holds the recipients' entity IDs. Any logged-in user can call `heads_up/send_message` while the switch is on; the sender is always the person of the connection's user, a user linked to no person or to several cannot send, and a sender can make 10 calls per minute. The sender never receives read state of recipients. The Message Log and the diagnostics hold no text. If the sender picks mail, the text goes to the configured mail service like any mail of Heads Up.
- The activity history in `.storage/heads_up.stats` holds counts per day, rule, policy and person (the person's entity ID). It holds no titles, texts or addresses. Settings > Activity history clears it.
- Do not put passwords, codes or other secrets in banners.

## Images from other hosts

The `image` of a message can be an `http://` or `https://` URL. The card, the popup and the phone load it themselves, so the host behind the URL sees the viewer's network address and when the message is shown. Heads Up does not fetch, proxy or check these pictures. Use a path on your own Home Assistant (`/local/...` or `/media/...`) to keep the request on your network.

## Tap actions

`tap_action` runs the Home Assistant action you configure when someone taps the banner. Any user who can see the banner can trigger it, including on a shared or wall-mounted screen. Heads Up does not restrict which actions you configure. Add a `confirmation` to the tap action to show a dialog before it runs; Home Assistant handles the dialog, and its `exemptions` list can skip it for chosen users.

The card writes banner text into the page as plain text, never as HTML.
