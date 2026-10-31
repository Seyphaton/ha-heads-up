# The Heads Up panel

The panel is an administrator page in Home Assistant's sidebar. In this version it has the navigation and the Settings page; the other pages say they are not available yet.

## Show it in the sidebar

When you add the integration, the first screen asks "Show Heads Up in the sidebar". The switch starts on. You can change it later in two places:

- Settings > Devices & services > Heads Up > Configure: Show Heads Up in the sidebar.
- The panel's own Settings page.

The entry appears and disappears when you save, without a restart. Only administrators see it. An installation that existed before the panel keeps the entry off until you switch it on.

## Navigation

Five groups in a top row: Overview, Notifications and rules, Configuration, Settings, FAQ and examples. A group with more than one page has a second row with its pages (Notifications and rules: Test send, Watch rules, Messages; Configuration: Audiences, Recipients, Policies, Channels). The address of a page is `/heads-up/<page>`, for example `/heads-up/general`. On a narrow screen the page has a menu button that opens Home Assistant's sidebar.

## Settings

| Part | What it does |
|---|---|
| Hub | The hub switch (option `hub_enabled`) and the sidebar switch. Off: messages reach only the dashboard banner. |
| Setup wizard | A button for the wizard. It is not available yet. |
| People and devices | Each person with the number of usable Companion devices and whether a Home Assistant user is linked. A person without a device gets only banner and popup; a person without a user gets no popup. |
| Loudness | Three presets. A preset adds the policies it names that do not exist yet and never changes or deletes one. A policy with the same name, or one that does the same as an existing policy, is skipped. |
| Limits | Pushes per device per minute, deliveries per minute for all devices, seconds in which identical updates are ignored. Stored now; not enforced yet. |
| History | Trace entries kept (50 to 5000) and recent messages kept (10 to 1000). |
| Identity | The install token, read only. It is part of every push tag. |

Save is enabled only when something changed and every number is inside its range; the page names a number that is not.

### Presets

| Preset | Adds |
|---|---|
| Quiet | Night quiet: Quiet hours 22:00 to 07:00, send quietly, critical passes. |
| Balanced | Night quiet, Water escalation (critical messages tagged `water` go to the Admins audience by push after 5 minutes) and Evening summary (messages tagged `digest` with severity info or success, one summary at 20:00). |
| Loud | Balanced, plus Warning reminders (every 30 minutes, 3 times, for warnings) and Push failed fallback (a notification in the bell when a push could not be delivered). |

Evening summary only collects messages tagged `digest`, so nothing is held that you did not choose. Edit the policies afterwards in Settings > Devices & services > Heads Up; see [Policies](policies.md).

## Limits

- Only the Settings page exists. Status, Test send, Watch rules, Messages, Audiences, Recipients, Policies, Channels and FAQ come in later versions. Until then use the integration's own forms.
- Not tested on a touch device or with a screen reader.
