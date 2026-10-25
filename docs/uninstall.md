# Uninstall

1. Remove the card from your dashboards. A card of a removed integration shows "Custom element doesn't exist" after the next reload.
2. Go to Settings > Devices & services > Heads Up, open the menu and choose Delete. This removes your [watch rules](rules.md), the sensor `sensor.heads_up_active_banners`, stops dashboards from loading the card, and deletes `.storage/heads_up.banners`.
3. Delete the folder `custom_components/heads_up` from your Home Assistant configuration folder, or remove the repository in HACS.
4. Restart Home Assistant. A restart pauses all automations until it has finished.

Remove the calls of `heads_up.*` actions from your automations and scripts. A call without the integration fails because the action no longer exists.

Heads Up does not change other integrations, automations or scripts, so nothing else needs to be restored.
