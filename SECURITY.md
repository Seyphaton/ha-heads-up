# Security

## Report a vulnerability

Open a private security advisory on the GitHub repository.

## What `people` does and does not protect

`people` decides which users receive a banner in the Heads Up card. It is not access control.

- Administrators can see every banner with the card option `show_all`.
- Banners are stored in plain text in `.storage/heads_up.banners`. Anyone with access to the Home Assistant files or backups can read them.
- Do not put passwords, codes or other secrets in banners.

## Tap actions

`tap_action` runs the Home Assistant action you configure when someone taps the banner. Any user who can see the banner can trigger it, including on a shared or wall-mounted screen. Heads Up does not restrict which actions you configure.
