# Limitations

## What Heads Up does not do

- It does not send push, voice or mobile notifications. It only shows banners in dashboards.
- It keeps no history. Each change fires an event; see [actions](actions.md#events).
- A condition watches one entity: its state or one attribute, compared as text. There are no templates.
- Banner text is shown as you write it. The card's own labels are English only.

## Access

- `people` decides who receives a banner in the card. It is not access control. Administrators can see every banner with the card option `show_all`, and anyone who can read the Home Assistant files or backups can read `.storage/heads_up.banners` in plain text. Do not put secrets in banners.
- Any logged-in user can create, clear and dismiss banners through the API. Only administrators can use the card's "Clear for everyone" button and `show_all`.
- Anyone who can see a banner can run its `tap_action`, including on a shared screen. Use `confirmation` for actions that change something physical.
- With `dismiss_scope: user`, closing a banner hides it for that Home Assistant user. People who share one login also share the closed state.

## Behaviour to know

- A banner has a timeout of 24 hours unless you set `timeout` or change the option. A banner with `mode: once` whose condition never matches ends at that timeout; with `timeout: 0` it stays until you clear it.
- `unavailable` and `unknown` states do not change a banner, including while Home Assistant starts.
- When the limit is reached and every stored banner is `critical`, or eviction is off, creating a banner fails.
- A dashboard page that finishes loading in the first second after Home Assistant starts can miss the card and show "Custom element doesn't exist: heads-up-card". Reload the page once. See [troubleshooting](troubleshooting.md).
- Installing needs a Home Assistant restart, which pauses all automations until it has finished.
- Settings changes in the options form apply to new banners only.

## Tested versions

Home Assistant 2026.9.4 (tests and a local instance) and 2026.10.4 (tests). Other versions are not tested.
