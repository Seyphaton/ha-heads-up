# Rename-proof identities (D-199 to D-202)

Part 1 of the phase: research and design. The maintainer approved it on 2026-11-10; part 2 is built (D-203). Steps 1 to 3 landed in one commit and 8 and 9 were split differently from the list in section 5; the order of the checks is the same.

Scope statement from the maintainer: all of it is part of release 1.0.0, so breaking changes against the alphas are acceptable. Only the maintainer's own production data must migrate. The four open choices below were put as questions and not answered one by one; the recommended option is used and listed in "Choices to confirm".

## 1. Findings

Severity: A = a running or stored alarm is lost or changed without any error; B = a call or form is refused, or a delivery goes to other people; C = display only.

### 1.1 Policies

| # | Where | What breaks on a rename (or type change, delete and re-create) | Sev | Disk |
|---|-------|------------------------------------------------------------------|-----|------|
| P1 | `hub/policies/models.py` `Policy.key` = `type:name`; `engine.py` `_arm`, `_schedule`, `_stop_timers`, `_dismissed`, `_drop_inapplicable_timers`, `_run_timer` | Timer rows (`heads_up.deliveries`, channel `timer`, recipient = key) keep the old key. `PolicyBook.by_key` finds nothing, `_run_timer` ends the row with `policy_gone`: the running escalation or reminder stops. Changing a policy's type in its form (the `type` field is also shown on reconfigure) does the same. | A | yes |
| P2 | `engine.py` `_arm_summary`, `_run_summary`, `on_policies_changed`; ledger `HeldMessage.policy`; message id `summary:<key>` | A rename makes `by_key(held.policy)` fail, so `on_policies_changed` releases every held message at once (a Summarize policy stops summarising and dumps its messages). The summary timer row is orphaned. | A | yes |
| P3 | `matching.select` (`p.name in names`), `Banner.policy` (stored in `heads_up.banners`), `services._check_policy_names` | A stored message keeps the old name, so after a rename it matches no policy: with `names` set and no match the result is empty, so its escalation, reminder and quiet hours are gone from then on. | A | yes |
| P4 | Rule subentry `policy` (text), `manager._build_rule`, rule form `policy_unknown` check, `frontend/panel/rules.js` | A rule keeps the old name; the rule then has no policy (see P3). The form only validates at save time, so nothing reports it later. | A | yes (entry) |
| P5 | Policy subentry `targets[channel].audience` (name), `recipients` containing `Name (group)` | A renamed audience or group leaves the policy's target pointing at nothing. `engine.policy_problem` reports `audience_missing` or `group_missing` when the policy fires and skips the step. | A | yes (entry) |
| P6 | Delete and re-create under the same name | Today the new policy silently inherits the old name's rules, messages and orphaned timers. With IDs the old references would dangle instead, so a dangling reference needs a visible, fixable state. | B | yes |
| P7 | Rename to a name that exists | The flow refuses (`name_exists`, `_names_taken`, case-insensitive; `none` and `automatic` are reserved). Safe. | – | – |
| P8 | Rename that differs only in case | Allowed (own subentry is excluded from `_names_taken`); identical to a rename for P1 to P5. | A | yes |
| P9 | `policy_order` option | Holds subentry IDs. Safe. | – | – |
| P10 | Policy switch entity (`switch.py`) | Unique ID holds the subentry ID; a rename changes the entity name, not the registered entity ID (`policy_entity_ids` reads the registry). Safe. If the user changes the entity ID in Home Assistant, a call by the old ID is refused (`unknown_policy`, with the valid IDs). Nothing stored is affected. | B | no |
| P11 | `diagnostics.py` `policy_order` and attention keys (`Attention.key` = `kind|subject|detail`, subject = policy name) | Hidden-warning keys in `attention_dismissed` name the policy; a rename brings a hidden warning back. | C | yes (options) |

### 1.2 Audiences

| # | Where | What breaks | Sev | Disk |
|---|-------|-------------|-----|------|
| A1 | `resolver.py` `_audiences` keyed by name; `resolver.audience(name)`; `Banner.targets[ch].audience` stored in banners and in `HeldMessage.targets` | A stored message keeps the old name; `resolve` reports `unknown_audience`, the push, popup or mail goes to nobody (the delivery is skipped, with a trace row only). | A | yes |
| A2 | Policy targets (see P5), watch rule `people` (person entity IDs, not names, safe) | As P5. | A | yes |
| A3 | `audiences_disabled` option holds built-in English names | Safe against renames (built-ins cannot be renamed, names are constants, not translated). Would break if a built-in name constant were ever changed. Keying by kind removes the dependency. | C | yes |
| A4 | `heads_up/audience_enable`, `hub_preview_audience`, `hub_usage`, `PolicyBook.usage(name)` | Address an audience by name. They are admin panel calls issued from the current list, so a rename between load and click gives `not_found`. `usage` compares `target.audience == name`; after a rename it reports no users, so the panel allows deleting an audience that a policy still uses. | B | no |
| A5 | Audience sensor (`binary_sensor.py`) | Unique ID = built-in kind or subentry ID. Renaming changes name only; the registered entity ID is kept. Safe. | – | – |
| A6 | Custom audience named like a built-in | `flows.py` refuses a built-in name case-insensitively. A future new built-in would collide with an existing custom one under a name model; under an ID model it would not. | C | – |
| A7 | Language change | Built-in names are constants, panel labels are translated separately; stored data contains the English constants. A language change breaks nothing today. Removing names from storage keeps it that way. | – | – |
| A8 | Delete and re-create under the same name | Same silent re-link as P6 (policy targets and stored messages find the new audience by name). | B | yes |

### 1.3 Recipient groups, profiles, areas, speakers, global address

| # | Where | What breaks | Sev | Disk |
|---|-------|-------------|-----|------|
| G1 | `resolver._groups` keyed by name; recipients `Name (group)` in calls, policy targets, `Banner.targets`, `HeldMessage.targets` | Rename leaves the old text everywhere; `_speakers` reports `unknown_recipient`; speech goes nowhere. A call that names the group in YAML is refused. | A | yes |
| G2 | `recipients.parse_profile` keyed by person entity ID | Renaming the person's friendly name changes nothing. Changing the person entity ID in Home Assistant orphans the profile (settings lost, device list back to detection). | B | yes |
| G3 | Persons in audiences (`persons`, `limit`), groups (`members` are speakers), rules `people`, banner `people`, presence store | Person entity ID is the key everywhere; an entity ID change drops the person from audiences and from banners aimed at them. Friendly-name renames are harmless. | A (entity ID change) | yes |
| G4 | Areas: recipients stored as given; `accepts` accepts an area by name or ID and `_check_names` stores the text as typed | A call or policy that stored an area by name breaks when the area is renamed in Home Assistant. Group `areas` hold area IDs (safe). | B | yes |
| G5 | Speakers `media_player.*`, `assist_satellite.*` | Entity ID based; an entity ID change breaks group members, policy and call targets. | B | yes |
| G6 | Push devices: profile `devices` hold the registration `device_id`; the notify service is worked out from `device_name` each time (N-78) | Device rename in the app keeps working. Safe. | – | – |
| G7 | `mail_service` option (notify service name), `speak_tts_entity` | Names of other integrations' objects. A rename there makes the channel fail (`no_mail_service`, delivery failed warning exists). The integration cannot repair another integration's name, only report it (Repairs issue, attention item). | B | yes |
| G8 | `Global address` / `mail:global` | Fixed keyword, not user-named. Safe. | – | – |

### 1.4 Rules, panel, stored data

| # | Where | What breaks | Sev | Disk |
|---|-------|-------------|-----|------|
| R1 | Rule id `rule_<subentry_id>`; ledger rows and trace key by message id | Stable. Safe. | – | – |
| R2 | `{name}` in a rule message with no entity falls back to the rule name (`_rule_message`) | Renaming the rule changes the message text. Intended; documented limit (see OPEN_QUESTIONS). | C | no |
| R3 | Trace (`heads_up.trace`), activity log, recent messages quote names (`policy.name`) | Old entries keep the old name. History only. | C | yes |
| R4 | Panel `policies.js`, `audiences.js`, `recipients.js`, `welcome.js`, `rules.js`, `test_send.js` | The editors write names into the flows (audience select values and `custom_value`, group chips `Name (group)`, policy text in rules). Test send maps names to entity IDs (D-198). The welcome applies policies by audience name. | A (through P4, P5) | via flows |
| R5 | `HeldMessage.channels/targets/people`, `Banner.targets` | Copies of names at the time of the call. | A | yes |

### 1.5 Storage state today

- Config entry: `VERSION = 1`, no `MINOR_VERSION`, no `async_migrate_entry`.
- `heads_up.banners`: version 1, no migration hook.
- `heads_up.deliveries`: version 1.1 with an empty migration hook (`LedgerStore._async_migrate_func`).
- `heads_up.trace`, `heads_up.presence`: version 1.

## 2. Home Assistant facts used (verified in source, 2026.10.4 and 2026.9.4)

Recorded as N-98 to N-100 in `docs/dev/HA_API_NOTES.md`.

- `ConfigEntry.async_migrate` runs `async_migrate_entry` of the component when `entry.version`/`minor_version` differ from the flow handler's `VERSION`/`MINOR_VERSION`. A stored `version` greater than the handler's makes setup fail with "has version N which is higher than the current version" (`config_entries.py`). A higher `minor_version` with the same major does not fail.
- The migrated entry is saved by Home Assistant after a True result. Config entries are written as one file, so an entry-level migration is atomic.
- `async_update_subentry(entry, subentry, data=, title=)` rewrites a subentry and fires update listeners; no listener is registered yet during `async_migrate_entry`.
- `Store.async_load` calls the migration function when the stored version differs, then saves the result. A stored major above the store's raises `UnsupportedStorageVersionError`.
- Entity registry rename: the event `entity_registry_updated` has `action: update`, `entity_id` (new), `old_entity_id`, `changes`.
- Issues: `ir.async_create_issue` (already used for `wait_for_condition_removed`).

## 3. Design

### 3.1 Identity model (D-199)

Each thing the user can name has one internal key that never changes; its name is display only.

| Thing | Internal key | Display name | Call-side handle |
|-------|--------------|--------------|------------------|
| Policy | subentry ID | subentry title | switch entity ID (D-198) |
| Custom audience | subentry ID | subentry title | sensor entity ID (D-198) |
| Built-in audience | kind (`at_home`, ...) | English constant, labels translated by the panel | sensor entity ID |
| Recipient group | subentry ID | subentry title | new: sensor entity ID (see 3.4) |
| Recipient profile | person entity ID | person's friendly name | person entity ID |
| Rule | `rule_<subentry_id>` (already) | subentry title | – |
| Area | area ID | area name | area ID (name accepted only by hand-written calls, stored as ID) |
| Speaker, person, zone | entity ID | friendly name | entity ID |

Consequences in code:

- `Policy.key` becomes `policy.subentry_id`. Timer rows have recipient = subentry ID, summary message id `summary:<subentry ID>`, held rows `HeldMessage.policy` = subentry ID. The type is no longer part of the key, so a type change keeps its timers (only a timer whose policy no longer applies is dropped, as now).
- `Banner.policy`, `matching.select`, rule `policy`: lists of subentry IDs plus the keywords `none` and `automatic`.
- Targets: `{"audience": <subentry ID or built-in kind>}` and recipients `group:<subentry ID>`, `area:<area ID>` stored as a prefixed token; person, speaker and device keys unchanged. A resolver function `resolve_audience(ref)` and `resolve_group(ref)` returns the live object; a reference to a deleted object resolves to `None` and is reported (policy_problem and the new attention item), never rebound to a same-named object.
- `audiences_disabled` holds kinds.
- Attention keys use the ID as subject.
- Entities already use these keys; nothing changes in `binary_sensor.py`, `switch.py` except a group sensor.
- Display text (trace, activity log, Message Log, summaries) is built from the current name at the time of writing, so history keeps the name that was valid then.

Delete and re-create: the new object has a new ID, so old references stay dangling and visible. A new attention item `reference_missing` (error, page of the owner) names each rule, policy or stored message that points at a missing object, and the editor offers "Choose another" (policy and audience pickers). This replaces today's silent re-link by name. Running messages with a dangling policy keep running without it; they do not end, and the trace records `policy_missing` once.

Rename to an existing name, or case only: names stay unique case-insensitively among objects of one kind, because names are shown in lists. The check stays; a case-only rename is accepted and changes nothing but the label.

### 3.2 Resolving a reference: dual read, single write

One module `hub/identity.py` holds the lookups:

- `PolicyBook.get(ref)` accepts a subentry ID, and (legacy) `name:<text>` or an unmigrated plain name or `type:name` key; the legacy forms are matched case-insensitively against current titles.
- The resolver does the same for audiences and groups.
- Nothing writes the legacy forms. A legacy value that resolves is rewritten to the ID the next time its owner is written; the migration rewrites all of them at once.

Because reads accept both forms, a missed or interrupted migration step never makes a policy, audience or group disappear. It also covers a stored message written by a caller in the window between versions.

An unresolved legacy name (the object never existed or was deleted before the upgrade) is migrated to `name:<text>`, not dropped. It is shown as a dangling reference, and it resolves by itself if an object with that title is created later (this keeps today's behaviour for exactly these cases).

### 3.3 Stored-data migration (D-200)

Versions (maintainer's choice of the recommended option: a major bump, so older code cannot load the new data):

- Config entry: `VERSION` 1 to 2, `MINOR_VERSION` 0.
- `heads_up.banners`: version 1 to 2, `heads_up.deliveries`: version 1.1 to 2.0, `heads_up.trace`: version 1 to 2.
- `heads_up.presence`: unchanged (person keys).

Order at startup (stores are loaded in `async_setup_entry`, after `async_migrate_entry`):

1. Backup. Before any change, if `.storage/heads_up.migration_v2` does not exist, write it: the entry's subentries and options, plus the raw contents of the three stores (read through `Store(..).async_load()` with the old version, or from the file). Written with `async_save`; never overwritten; not removed by uninstall of the integration; removed only by an explicit admin command or by hand. A second start finds it and skips.
2. `async_migrate_entry` (entry, atomic): builds the maps from current titles (policy, audience, group; built-in name to kind) and
   - rewrites rule `policy` to the policy ID or `name:`/`none`;
   - rewrites policy `targets` (audience to ID or kind; `Name (group)` to `group:<ID>`; area names to `area:<ID>` when the area exists);
   - rewrites `audiences_disabled` and `attention_dismissed`;
   - leaves titles and every other field untouched;
   - sets `version` to 2 through `async_update_entry`.
   Home Assistant saves the entry once, so a crash leaves it either fully 1 or fully 2.
3. Store migration functions (`_async_migrate_func`, version 1 to 2; each runs inside the store's own load, which then saves the result atomically). They need the maps, so the setup code attaches them to the store before the load (`store.identity = maps`):
   - banners: `policy` (string or list), `targets[*].audience`, `targets[*].recipients`;
   - deliveries: timer rows `recipient` `type:name` to the ID, `message_id` `summary:type:name` to `summary:<ID>`, `held` list `policy`, held `targets`; rows for devices, persons and speakers untouched;
   - trace: untouched except the version number (history keeps the old names).
   Idempotent: a value already in the new form is unchanged; running it on migrated data changes nothing; the dual-read rule covers an entry that migrated while a store did not (crash between the two writes).
4. `_restore_timers` runs after the ledger load, so timers restore from the new keys with unchanged `due` values. An overdue timer fires once, exactly as after any restart today. No timer row is deleted, created or duplicated by the migration; a test compares the ledger before and after.
5. After step 3 completes, the integration logs one line with the counts (rules, targets, timers, held messages rewritten, references left unresolved) and writes the same counts to the trace.

What happens to what:

- Running escalation and reminder timers: key rewritten, same due time and count.
- Held (Summarize) messages: `policy` rewritten; the summary timer row and its id rewritten together.
- A stored banner whose policy name matches no policy: `name:<text>` (dangling, reported).
- A rule whose policy name has different case than the title: matched case-insensitively.
- A message mid-flight during startup: engine starts after migration, so no step runs on half-migrated data.

Rollback note: restore `.storage/heads_up.migration_v2` into the entry and the three stores while Home Assistant is stopped (a script `scripts/restore_identity_backup.py` ships in step 9), and install the earlier release. Without the restore, Home Assistant refuses to set up the entry in older code (entry version 2) and older stores raise `UnsupportedStorageVersionError`; nothing is read as wrong data. The restore script is a documented manual step, not an integration feature.

### 3.4 Calls, groups and entity IDs (D-201)

- Groups get a sensor each (`sensor.heads_up_group_<name>`, state = number of resolved speakers, attributes `group` and `members`; unique ID `<entry>_group_<subentry_id>`; attached to its subentry), exactly like audiences. The `speak` and `speakers` recipient pickers list media players, satellites and these sensors. The text form `Name (group)` and a call by area name are refused like D-198, with the entity ID or area ID to use. Areas are named by area ID only in calls and storage (an area is renamed in Home Assistant, not here).
- Home Assistant entity ID changes (a person, speaker, zone or device tracker renamed in Home Assistant): the integration listens to `entity_registry_updated` for `action == update` with `old_entity_id`, and rewrites its own copies in one entry update: audience `persons` and `limit`, group `members`, profile `person`, rule `people` and `entity_id`, policy targets, `condition` entity of rules, `Banner.people`/targets and held targets, presence store keys, `speak_tts_entity`. It records one trace row per rewrite. A reference that cannot be rewritten (a template that names the entity, the mail service of another integration) gets an attention item `entity_renamed` with the old and new IDs. The integration never changes another integration's data, automations or scripts (rule 3); a call in YAML that names the old ID fails with `unknown_*` and the valid IDs.
- `mail_service`: stays a free notify service name; unchanged. The existing `delivery_failed` warning covers a rename on the other side; a new attention check `mail_service_missing` (service not registered) is added.

### 3.5 Forms, panel and parity (D-202)

- Watch rule form: the policy field is a select built when the form opens: Automatic (empty), None, then every policy (label = name, value = subentry ID). The panel rule editor renders the same flow, so it needs no new control type (it already renders selects).
- Policy form `*_audience` fields: select options with value = ID or kind, label = name, `custom_value` stays so that a dangling ID still opens. Group chips store `group:<ID>`.
- `heads_up/audience_enable`, `hub_usage`, `hub_preview_audience`: take the key (kind or subentry ID), names are display. `PolicyBook.usage` and `AudienceBook.usage` look up IDs, so a delete is refused after a rename as it should be.
- Panel: lists show names; every action sends the key. A rename in the panel changes only the title.
- Welcome and Test send map names to keys on the server.
- Parity (rule 9): banners from `notify` and from watch rules both store IDs and both name an object by ID or entity ID. No feature gap is introduced. D-198's exception (the rule form names a policy by text) closes with this phase; the section 22 table gets no new exception.

### 3.6 Blast radius

- Restart: yes. The config entry and three stores migrate once at the first start of the new version.
- Notification path touched: yes. Policy selection, timers, target resolution and the speech recipient resolution change their lookup keys.
- Stored data changed: config entry (version 2, rules, policy targets, options), `heads_up.banners`, `heads_up.deliveries`, `heads_up.trace` (version only). New file `heads_up.migration_v2`.
- Changes what a dashboard shows: no. A new attention item may appear for references that were already dangling.
- Breaking for callers: a group name or an area name in a call (D-201); `Name (group)` in YAML.
- Downgrade: blocked by Home Assistant on purpose (3.3).
- Another integration's data: never written.

## 4. Test plan

New file `tests/hub/test_identity_rename.py` and friends. All use the existing hub fixtures (`tests/hub/helpers.py`, `policy_support.py`, `FakeClock`/fakes from H0a).

1. Property-style rename test (the key test). Build one household: two policies of every timed type (escalation, reminder, summarize, quiet hours, away, fallback, deliver), two custom audiences, one group, a profile, a rule with a policy, a rule with `people`. Create live state: a message with an escalation timer, one with a reminder (count 1), a held summarize message, a held quiet-hours push, a rule banner. Snapshot the delivery plan, the ledger (timer rows with due and count, held list), the trace-relevant outputs of `engine.plan` for each message, and the banner payloads. Then, for every renamable thing in turn (and for all at once), rename it through the real flow (`async_update_subentry(title=...)`): cases `Name -> Other`, case-only, with spaces and unicode, to a free name. After each rename assert: ledger rows unchanged except nothing; the same timers scheduled (`engine._timers` keys); `plan()` for every live message identical; advance the clock and assert the same deliveries fire once; no `policy_gone`, no `unknown_audience`, no `unknown_recipient`; a call by entity ID still succeeds; the attention list is unchanged. The rename order is randomised with a seed printed in the failure.
2. Rename to an existing name and case-only to an existing name: refused by the flow, nothing changed.
3. Delete and re-create with the same name: the old references become `reference_missing` and are not re-linked; the engine does not end a timer on a missing policy (timers of a deleted policy end with `policy_deleted`, a disabled one with `policy_disabled`, which splits today's `policy_gone`); re-link through the picker restores delivery.
4. Migration tests from the current formats: fixtures with the stored shapes of today (entry v1 with rule `policy` names, policy targets with names and `Name (group)`, area by name, `audiences_disabled`, `attention_dismissed`; banners with `policy` string, list and `none`; ledger with `escalation:Name`, `reminder:Name`, `summary:summarize:Name`, held rows with `policy`; trace). Assert: every reference resolves to the same object; timer `due` and `count` equal; no row dropped or duplicated; unresolved names become `name:<text>`; counts logged.
5. Idempotence: run the migration twice; the second run changes nothing (byte-equal stores and entry data). Run only the entry step, restart, run the stores; run only the stores, restart, run the entry step: the dual read keeps every policy working in between.
6. Restart in the middle: stop the engine with a pending escalation, held message and summary timer, migrate, start; assert the same deliveries as an uninterrupted run (clock-driven comparison against a control instance that never migrated).
7. Backup: written once before the first change; not overwritten on a second start; content equals the pre-migration stores; downgrade guard test (a handler with a lower VERSION refuses the entry; the store raises on an unsupported major).
8. Entity ID renames: rename a person, a speaker and a zone in the entity registry; assert the rewrite of every owner, a trace row each, `entity_renamed` for the unresolvable one, other integrations' data untouched.
9. Call refusals: group name and area name in a call fail with the stable codes and the ID to use; group sensor and area ID work.
10. Forms: rule form select lists Automatic, None, every policy; the saved value is the ID; policy form audience select value is ID or kind; panel editors (vitest) send keys, and a rename does not change a key in the payload.
11. Language: change the Home Assistant language; stored data and keys unchanged (guards against translated keys).
12. Docs check: examples and the field list stay valid (`make docs-check`); `tests/test_translations.py` covers the new strings in four languages.

Gates for part 2: `make check`, `make hassfest`, `make dev-smoke`, then the panel on the dev instance (policy rename with a running escalation; audience rename with a held message; group rename and a speech call).

## 5. Steps of part 2 (one commit each, each with tests)

1. `hub/identity.py`: lookup helpers and dual-read for policies, audiences, groups; `PolicyBook`/resolver keyed by ID; `Policy.key` is the subentry ID. Tests 1 (policy part), 3.
2. Engine: timers, held rows, summary ids, `policy_problem`, disabled versus deleted reasons. Tests 1 (timers), 6.
3. Targets: audience and group references stored as keys (`resolve`, `banner_people`, `usage`, `policy_problem`); services `_check_names` stores keys. Tests 1 (audience and group part).
4. Entry migration (`VERSION` 2, `async_migrate_entry`), backup file, `audiences_disabled`, attention keys. Tests 4, 5, 7.
5. Store migrations for banners, deliveries and trace, with the counts. Tests 4, 5, 6.
6. Forms and panel: rule form select, policy form selects, panel editors and websocket commands by key, welcome by key. Tests 10.
7. Group sensor, speech recipient picker, refusal of group and area names in calls. Tests 9.
8. Entity ID rename listener and the attention items `reference_missing`, `entity_renamed`, `mail_service_missing`. Tests 3, 8.
9. Restore script, docs (`docs/audiences.md`, `docs/policies.md`, `docs/actions.md`, `docs/setup.md#upgrading`, troubleshooting), `CHANGELOG.md` `[Unreleased]`, `docs/DESIGN.md` §23 and §22, STATE, panel texts in four languages, the property test in its final form. Then `make check`, `make hassfest`, `make dev-smoke` and the dev instance walk-through.

Steps 1 to 3 can land with the dual read alone (no data change). The migration (4, 5) is the only step that writes the new format.

## 6. Choices to confirm

The maintainer sent "its all part of release 1.0.0" instead of answering the four questions. Read as: breaking is acceptable, so the stricter options are used. Say if any should change:

1. Major version bump (entry 2, stores 2) so older code cannot load migrated data; rollback by restoring the backup. Alternative: minor bump, older code loads and loses policies silently.
2. A sensor entity per recipient group; the text name in calls is refused. Alternative: keep the name in calls.
3. The integration rewrites its own references when an entity ID changes in Home Assistant. Alternative: detect and warn only.
4. The rule form Policy field is a dropdown with ID values. Alternative: entity picker (cannot offer `none`).
