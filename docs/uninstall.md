# Uninstall

1. Remove the card from your dashboards. A card of a removed integration shows "Custom element doesn't exist" after the next reload.
2. Go to Settings > Devices & services > Heads Up, open the menu and choose Delete. This removes your [watch rules](rules.md), the sensor `sensor.heads_up_active_banners`, stops dashboards from loading the card, and deletes `.storage/heads_up.banners`.
3. Remove Heads Up in HACS.
4. Restart Home Assistant. A restart pauses all automations until it has finished.

Deleting the integration does not take back what it already sent. Notifications on phones stay until someone swipes them away, and entries in the notification bell stay until the next restart of Home Assistant or until you dismiss them. Audiences, recipient profiles, speaker groups and policies are entries of the integration and are deleted with it.

Remove the calls of `heads_up.*` actions from your automations and scripts. A call without the integration fails because the action no longer exists.

Heads Up does not change other integrations, automations or scripts, so nothing else needs to be restored.
