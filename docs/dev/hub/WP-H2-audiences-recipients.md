# H2: Audiences, recipient groups and recipient profiles

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the objects that answer 'who': config subentry types for audiences, recipient groups and recipient profiles, the built-in audiences, the presence tracking, the person to device resolution, and the resolver the engine calls.

## Dependencies and parallel work
- Needs: H1
- Can run at the same time as: H4a, H5 (after the resolver interface), H6, H7
- Files this package owns (create): `hub/audiences.py`, `hub/recipients.py`, `hub/presence.py`, `tests/hub/test_audiences_*.py`, `tests/hub/test_recipients_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `config_flow.py` (three subentry flow classes and the registration dict), `__init__.py` and `manager.py` or `hub/engine.py` (sync like `sync_rules`), `strings.json`, `translations/*.json`, `websocket.py` (preview commands)

## Scope
- Subentry types `audience`, `recipient_group`, `recipient_profile`, each with a `ConfigSubentryFlow` class and a `reconfigure` step (pattern of `RuleSubentryFlow`); sync from `_async_entry_updated` beside `sync_rules`; strings for forms, errors and abort reasons in all four languages (key parity test).
- Audience (D-080, D-088): flat. Built in, not stored: Everyone (every person with a recipient profile), Admins (persons whose user is an admin), At home, Not home, Last to leave (the person whose departure emptied the house; empty while anyone is home), First home (the first person home after the house was empty; empty if nobody is home). Custom, stored: kind persons (list of person entities) or kind presence (at_home, not_home, last_to_leave, first_home, in_zone, not_in_zone with a zone). Names unique; a custom audience used by a policy cannot be deleted (H4 provides the usage lookup; until then no check).
- Presence: read the `person` state; `None`, `unknown`, `unavailable` count as unknown (N-63). Membership is a snapshot when a delivery is made. Track person and zone state changes only for entities that audiences reference. Last to leave and First home need a small state (who left last, who came first) kept across restarts or recomputed; decide and document. A debounce of presence changes is proposed (DEFAULTS_AND_PROPOSALS), ask first.
- Recipient profile (D-088): per person: detected devices, manual add and remove, primary device, accepted channels (banner, push, popup). Detection: `person.device_trackers` to the entity registry to a `mobile_app` registration (`device_name`, `device_id`) to the notify service `notify.mobile_app_<slugify(device_name)>` (N-70, N-71). Trackers from other integrations are skipped. A device whose notify service does not exist is flagged 'service not found'. A device is stored by its `device_id`, never by its notify service name: the app can rename a device, which renames the service, and two devices with the same name share one service (N-78); the service name is resolved from the registration's `device_name` at send time. A person with no usable device is skipped on push with a trace entry.
- Profiles exist without manual work (D-107): a recipient profile is created for every person automatically, with the detected devices; to confirm in this package (ask).
- Recipient group: a named set of speakers, satellites and areas; used in calls as `<name> (group)`; members are validated against existing entities; an area expands to the speakers assigned to it (assignment mechanism decided in the session: HA area of the entity).
- Resolver implementing the interface from H1: `resolve(target, channel, context)` returns recipients with reasons; used by the engine, the dry run and the panel preview. WebSocket commands `heads_up/hub_preview_audience` (admin) returning the members now with reasons.
- Targets by channel are validated as in DESIGN 23.5 (shared with `notify` validation from H1).

## Out of scope
Sending anything (H3, H5); policies (H4); the panel forms (H9c); popup area recipients (not built).

## Tests
Audience resolution for every built-in and custom kind with the time freezer and person states (home, not_home, zone, None, unavailable); admins; Last to leave and First home sequences; profile detection with the fake registration from H0a (detected, manual, missing service, no device, tracker from another integration); groups and areas; subentry flows create, reconfigure and refuse duplicates; translation parity; restart.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md` or a new page for audiences and recipients as user documentation when the forms exist (README and how-to at H10), `docs/dev/HA_API_NOTES.md`, `docs/DESIGN.md` 23.7 if details change, CHANGELOG, STATE.

## Parity (CLAUDE.md rule 9)
Applies to every message regardless of source: the resolver is shared. Rule messages use banner targets only.

## Blast radius (rule 5)
Restart: the usual one. Notification path: not touched (no sending). Dashboard: nothing changes. Storage: three new subentry types; an older version with unknown subentry types must be checked (document the result in HA_API_NOTES).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Presence debounce; how Last to leave and First home state is kept; area to speaker assignment. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-63, N-70, N-71 (run with the fake registration); behavior of an older version with an unknown subentry type. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Three subentry types with flows, strings in four languages, built-in audiences, resolver, preview command; tests green; `make check`, `make hassfest`, `make dev-smoke` green; docs per the list; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
