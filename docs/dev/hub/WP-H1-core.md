# H1: Core engine, notify action and message store

Size: large, first and alone. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the foundation every other package uses: a typed transition seam in the manager, the `hub` package with the delivery engine, channel protocol, delivery store, trace buffer and install token, and the `heads_up.notify` action with the shortcuts `push`, `popup`, `speak`. With the hub switched off, or for a call that names no hub channel and matches no policy, nothing changes for anyone. The hub is on by default (D-107). Only the banner channel delivers in this package; the other channels are registered as 'not available' until their packages exist.

## Dependencies and parallel work
- Needs: H0a (fixtures)
- Can run at the same time as: H0b
- Files this package owns (create): `custom_components/heads_up/hub/` (new package: `__init__.py`, `engine.py`, `transitions.py`, `ledger.py`, `trace.py`, `channels/__init__.py`, `channels/banner.py`), `tests/hub/test_core_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `manager.py` (the seam, only here), `models.py` (optional message fields), `services.py`, `services.yaml`, `strings.json`, `translations/*.json`, `icons.json`, `const.py`, `__init__.py`, `config_flow.py` (options), `websocket.py` (trace command), `docs/actions.md`, `docs/limitations.md` (later, with push), `CHANGELOG.md`

## Scope
- Message record: extend the stored `Banner` with optional fields `channels` (default: banner only, which is what `create_banner` produces), `targets` (channel to target), `policy` (name or none), `tts_message`, `acknowledged_by`, `source` (action or rule). All optional, so existing banners load unchanged; a downgrade after use needs banners cleared (as in earlier phases, DESIGN 21.3). A message whose channels do not include `banner` exists as a record but is not shown by `visible()`.
- Transition seam in `manager.py`: a typed `BannerTransition(kind, banner, reason, user_id, silent)` emitted from every mutation point: appeared, updated, became_visible (condition turned true, a waiting banner became active, a snooze ended), hidden (reasons: cleared, expired, condition, dismissed, evicted, rule, admin, clear_all), snoozed, unsnoozed, severity_changed, acknowledged (emitted by H4a and H8). Silent paths that fire no bus event today (`_snooze_elapsed`, `_apply_condition` false to true, `sync_rules(silent=True)`) must emit transitions too, with `silent=True` for startup. A `created` bus event fires for a `waiting` banner before it is visible: the engine must key on transitions, not on bus events. Existing bus events and their exact payloads do not change (pinned by `tests/test_create.py`, `tests/test_clear.py`, `tests/test_actions.py`).
- The transition listener list is separate from the existing no-argument `_listeners`; the engine subscribes once and never reads private manager state.
- Engine: per-message serialization of deliveries, background tasks through `entry.async_create_background_task`, cancellation on unload, bounded concurrency. A `plan()` method returns the deliveries that a call would produce without sending anything (dry run); the Test send and Preview of the panel (H9d) use it.
- Channel protocol: `capabilities` (title, buttons, clear, replace, per-user), `deliver`, `update`, `clear`, plus a registry. The banner channel wraps the existing card path. Interfaces for the audience and recipient resolvers (consumed by H2, H3, H5) and for policy hooks (consumed by H4) are defined here with fake implementations for tests.
- Delivery model and store: second `Store` with its own key (`heads_up.deliveries`), version 1 and a `minor_version` migration hook (the banner store has no migration pattern); rows hold message id, recipient key, channel, state (planned, held, sent, skipped, failed, cleared), due times, last tag or notification id; saves debounced as the banner store does; a startup reconciliation skeleton (clear what no longer exists, never re-send what was sent).
- Trace: a ring buffer of delivery decisions with reasons (size from the options) and the WebSocket command `heads_up/hub_trace` (admin only).
- Options: `hub_enabled` (default true, D-107; the off switch), install token (6 hexadecimal characters, generated once, read-only), the limit and history keys with their proposed defaults (stored here, enforced in H10). New option keys are added to `DEFAULT_OPTIONS` and the options flow dict (the flow rewrites all keys on save).
- Action `heads_up.notify` (D-087, D-098): content `message` (1 to 1000 characters), `title`, `icon`, `severity`, `actions`, `tap_action`, `tts_message`; lifecycle fields shared with `create_banner` (reuse its validators and constants); `channels` (required, non-empty, values from the five channels); `to` (a mapping channel to `{audience: name}` or `{recipients: [...]}`, never both); `policy` (a name, or `none`). Validation by channel as in DESIGN 23.5: push, popup and speak need a target; banner and persistent do not; speak accepts recipients only; persistent accepts no target. Unknown audience or recipient names are validation errors that list the valid names. Errors are `ServiceValidationError` with translation keys.
- Response: `id`, `status` (`created`, `updated`, `waiting`, `condition_false`) and per channel counts of `sent`, `held`, `skipped`, `failed`.
- Shortcuts `heads_up.push`, `heads_up.popup`, `heads_up.speak`: one fixed channel, optional `audience` or `recipients`, no escalation; fire and forget without an `id`, a tracked message with one.
- Clearing: one generic clear removes a message from every channel. `clear_banner` already clears by `id` and/or `tag`; decide in the session (AskUserQuestion) whether `clear_banner` gains the all-channel behavior or a new `clear` action is added; keep `clear_banner` working either way.
- Hub switched off: `notify` accepts only `channels: [banner]` and behaves exactly like `create_banner`; other channels return a validation error that says the hub is switched off. No listeners, timers or stores are created while the hub is off.

## Out of scope
Audiences, recipient profiles and groups (H2); any real push, popup, speak or persistent delivery (H3, H5, H6, H7); policies (H4); the panel (H9); rate limit enforcement and restart reconciliation details (H10).

## Tests
`tests/hub/test_core_transitions.py` (every mutation path emits the right transition incl. the silent ones; startup silent; existing event payloads unchanged), `test_core_notify.py` (schema matrix per channel, unknown names, XOR rule, shortcuts, response, hub off), `test_core_engine.py` (serialization, cancellation on unload, dry run), `test_core_ledger.py` (store, migration hook, corrupt data skipped like `tests/test_storage_corruption.py`), `test_core_options.py`. Existing suite stays green unchanged. `dev/smoke.py`: a `hub_core` phase (notify banner only, restart, message still there).

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md` (new `notify` section and shortcuts, field tables; `scripts/docs_check.py` checks field parity with `SCHEMAS` and `services.yaml`), `CHANGELOG.md` Unreleased, `docs/DESIGN.md` section 23 status line, `docs/dev/TESTING.md`, `docs/dev/HA_API_NOTES.md` (any new API), STATE.

## Parity (CLAUDE.md rule 9)
`notify` messages and watch rule messages go through the same manager, transition seam and engine; rules do not get hub fields (D-100, DESIGN 22.2 exception row). Add tests for both sources in the transition tests.

## Blast radius (rule 5)
Restart: the usual one after a code update. Notification path: not touched yet (banner only). Dashboard: nothing changes for messages that name no hub channel and match no policy. Storage: optional fields on stored banners (downgrade needs banners cleared) and a new deliveries store created only when the hub is on. New action `notify`, three shortcuts.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Name of the generic clear. Panel and popup are not asked here. Speech length limit is asked in H5. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None new; rely on N-1 to N-60 and N-61 to N-68. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Seam, engine, ledger, trace, options, `notify` and shortcuts built and tested for both message sources; hub off and unaffected calls change nothing; `make check`, `make hassfest`, `make dev-smoke` green; docs per the list; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
