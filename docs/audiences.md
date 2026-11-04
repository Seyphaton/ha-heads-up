# Audiences, recipient groups and recipient profiles

These objects say who a [`heads_up.notify`](actions.md#headsupnotify) call is for. An audience applies to the push and popup channels. The speak channel takes recipients instead (see [Speech](speech.md)). Persistent Notification takes no target.

Add custom objects under Settings > Devices & services > Heads Up > Add entry. Edit them with the pencil next to the entry.

## Audiences

An audience is a named group of people. A call uses its name: `to: {push: {audience: At home}}`. Membership is worked out when the message is delivered. For the banner channel it is worked out once, when the banner is created.

| Name | Who |
|---|---|
| `Everyone` | Every person. |
| `Admins` | Persons whose Home Assistant user is an administrator. |
| `At home` | Persons whose state is `home`. |
| `Not home` | Persons whose state is anything else, including a zone. |
| `Last to leave` | The person whose departure emptied the house. Nobody while anyone is home. |
| `First home` | The first person home after the house was empty. Nobody while the house is empty. |

You can add your own:

- **Persons**: a fixed list of persons.
- **Presence**: one of at home, not home, last to leave, first home, in a zone, not in a zone (with a zone).

A presence audience can be limited to chosen persons, for example `At home` for one person only, or `Last to leave` for two persons. A limited `Last to leave` or `First home` names the person only when that person is also the last to leave or the first home of the whole house; it does not look for the last of the chosen persons.

In the panel each built-in audience has a checkbox. One that is switched off is not offered, and a call that names it fails with the list of valid names. A built-in audience that a policy uses cannot be switched off.

A custom name must differ, ignoring case, from the built-in names and from other audiences.

A person whose state is `unknown`, `unavailable` or has no usable tracker has unknown presence. Presence audiences include that person for `critical` messages and skip them for lower severities. The trace says why (`presence_unknown`).

`Last to leave` and `First home` change only after a person has been home or away for the presence delay (option Presence delay, 60 seconds by default, 0 for no delay). This keeps a flapping location fix from moving them. Both are kept across restarts.

## Recipient profiles

Every person has a recipient profile without any setup. Their Companion app devices are found through the person's trackers. Trackers from other integrations are ignored.

Add a profile entry only to change that:

- **Added devices**: a Companion device that was not found.
- **Removed devices**: a detected device to leave out.
- **Primary device**: listed first. A push still goes to every device of the person.
- **Accepted channels**: banner, push and popup by default. A channel you remove is skipped for that person. Mail is off until you add it.
- **Mail address**: where mail to this person goes; see [Mail](mail.md).

A person with no usable device is skipped on push (`no_usable_device`). A device whose notify service does not exist is skipped (`service_not_found`). A renamed device keeps working: the service is worked out from the device's current name each time.

## Recipient groups

A recipient group is a named set of speakers, Assist satellites and areas for speech. A call names it `<name> (group)`, for example `Ground floor (group)`. An area stands for the speakers and satellites assigned to that area in Home Assistant. A call may also name an area by its area ID or its name.

## Preview

Administrators can ask who an audience is right now with the WebSocket command `heads_up/hub_preview_audience` (`audience`, optional `severity`). The reply lists `members` and `skipped`, each with a `person` and a `reason`.
