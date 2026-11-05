# Limitations

## What Heads Up does not do

- Push has no retry: a failed push is not tried again, and a push over the rate limit is skipped ([Push notifications](push.md), [Settings](settings.md#limits)).
- Speech has no volume handling and no all-clear announcement ([Speech](speech.md)).
- Mail delivery is the job of the notify service you choose; Heads Up knows only whether the call returned an error ([Mail](mail.md)).
- A popup needs an open Home Assistant page ([Popups](popup.md)). A persistent notification goes to everyone ([Persistent notifications](persistent.md)).
- It keeps no history of messages. Each change fires an event; see [actions](actions.md#events). The panel's trace, recent messages and log of last actions are kept in memory and start empty after a restart.
- Pushes were tried with stub devices only, not with a real Companion app. The critical level needs the app's permission on iOS and plays a sound in silent mode there. On Android it uses the alarm channel, which also sounds in silent mode; Do Not Disturb is overridden only if you allow it for that channel in the Android settings.
- A watch rule watches one entity (its state or one attribute) or one template. The state is compared as text unless the condition is above, below or between.
- Banner text is shown as you write it. The card's own labels and the integration's screens follow your Home Assistant language in English, German, French and Spanish; other languages show English. The German, French and Spanish texts were written without review by native speakers.

## Access

- `people` decides who receives a banner in the card. It is not access control. Administrators can see every banner with the card option `show_all`, and anyone who can read the Home Assistant files or backups can read `.storage/heads_up.banners` in plain text. Do not put secrets in banners.
- Any logged-in user can create, clear and dismiss banners through the API. Only administrators can use the card's "Clear for everyone" button and `show_all`.
- Anyone who can see a banner can run its `tap_action`, including on a shared screen. Use `confirmation` for actions that change something physical.
- With `dismiss_scope: user`, closing a banner hides it for that Home Assistant user, in every Heads Up card. People who share one login also share the closed state.
- "Clear all" and swipe to dismiss remove banners with `dismiss_scope: global` for everyone, like the X button, and ask for no confirmation.
- Swipe to dismiss was tested with a mouse only, not on a touch screen.

## Behaviour to know

- A banner has a timeout of 24 hours unless you set `timeout` or change the option. A banner with `mode: once` whose condition never matches ends at that timeout; with `timeout: 0` it stays until you clear it.
- `unavailable` and `unknown` states do not change a banner, including while Home Assistant starts.
- When the limit is reached and every stored banner is `critical`, or eviction is off, creating a banner fails.
- A dashboard page that finishes loading in the first second after Home Assistant starts can miss the card and show "Custom element doesn't exist: heads-up-card". Reload the page once. See [troubleshooting](troubleshooting.md).
- Installing needs a Home Assistant restart, which pauses all automations until it has finished.
- Banner defaults changed in the options form or in Settings apply to new banners only.
- Watch rules ([rules](rules.md)) compare one entity's state or attribute as text, like `condition`. A closed rule banner returns after a restart.

## Tested versions

Home Assistant 2026.10.4 (tests and a local instance) and 2026.9.4 (tests). Other versions are not tested.
