# Troubleshooting

Turn on debug logging for the integration in `configuration.yaml`, restart, and read the Home Assistant log:

```yaml
logger:
  logs:
    custom_components.heads_up: debug
```

## The card shows "Custom element doesn't exist: heads-up-card"

- Reload the page. If the page loaded in the first second after Home Assistant started, it can miss the card. A reload fixes it.
- If it persists, check that the integration is added (Settings > Devices & services). The card is registered only while the integration is loaded.
- Open `/heads_up/heads-up-card.js` in the browser. It should return JavaScript. Then reload the page without cache.

## The card looks old after an update

Reload the page without cache once. The card address changes with every new version of the card file, so a normal reload loads the new one; a page that was loaded before the update keeps the old card until it is reloaded.

## The card shows "Heads Up is not available"

The card cannot reach `heads_up/subscribe`. During a Home Assistant start it retries after 1, 2, 5 and 10 seconds and then every 30 seconds, and the banners return by themselves. If the message stays after the start has finished, the integration is not loaded: look for errors from `custom_components.heads_up` in the log.

## An action fails with "Heads Up is not set up"

The integration is not added or is disabled. Add it in Settings > Devices & services.

## A banner does not show

Check, in this order:

1. The response of `create_banner`. `status: waiting` means the condition is not true yet. `condition_false` means nothing was stored because you set `wait_for_condition: false`.
2. `sensor.heads_up_active_banners`. Its state counts banners that are stored and not waiting.
3. People. With `people`, only users linked to those person entities see the banner. A user sees only banners without `people` when no person is linked to them. The link is the person's `user_id` attribute in Developer tools > States.
4. Dismissal. With `dismiss_scope: user` you do not see a banner you closed. Calling `create_banner` again with the same `id` shows it again.
5. Card filters `severity`, `tag` and `max_items` in the card configuration. With `collapsed_items`, the rest sits behind "Show N more".
6. Timeout. The banner may have expired; the event `heads_up_banner_expired` shows it.

For a banner from a watch rule, see [A watch rule shows no banner](#a-watch-rule-shows-no-banner).

## The "Clear all" button is missing

The button appears only when the card shows at least one banner that can be dismissed, and only with `clear_all: true`. Banners with `dismissible: false` are not counted.

## A banner cannot be closed

It was created with `dismissible: false`. An administrator sees a "Clear for everyone" button. `heads_up.clear_banner` with its `id` or `tag` also removes it.

A banner from a watch rule has no button for anyone unless the rule is dismissible. `clear_banner` does not remove it. Disable or delete the rule in Settings > Devices & services > Heads Up.

## A watch rule shows no banner

Check, in this order:

1. The rule is enabled.
2. The entity state or attribute equals one of the rule's states. The comparison is text, so `on` and `On` differ.
3. The entity is not `unavailable` or `unknown`, and it exists. Rule banners are hidden in those cases.
4. People. With `people` set, only users linked to those person entities see it.
5. Dismissal. A dismissible rule hides the banner for the user who closed it until the entity leaves the state and enters it again. A restart also brings it back.
6. The card filters `severity`, `tag` and `max_items`. Rule banners have the tag `rule`.

## The log says "Skipping unreadable banner"

`.storage/heads_up.banners` is valid JSON, but one stored banner is damaged. Heads Up skips it, keeps the others, and rewrites the file without the damaged banner.

## The storage file is damaged

If `.storage/heads_up.banners` cannot be read as JSON, Home Assistant renames it to `heads_up.banners.corrupt.<time>`, logs an error, and Heads Up starts with no banners. Delete or keep the renamed file as you like.

## Access denied for `show_all` or "Clear for everyone"

Both are for administrators only. The card ignores `show_all` for other users.
