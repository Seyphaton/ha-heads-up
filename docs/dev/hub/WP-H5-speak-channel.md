# H5: Speak channel (speakers and satellites)

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Deliver spoken messages to media players, Assist satellites and groups of them.

## Dependencies and parallel work
- Needs: H1, H2 (recipient groups)
- Can run at the same time as: H3, H4a, H6, H7
- Files this package owns (create): `hub/channels/speak.py`, `tests/hub/test_speak_*.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `manifest.json` (`after_dependencies`: `tts`, `media_player`, `assist_satellite`, N-68), `strings.json`, `translations/*.json`, `docs/actions.md`

## Scope
- Targets: recipient groups (expanded to members), media players, Assist satellites, areas (their assigned speakers). No audience (D-090).
- Text: `tts_message`, else the title if set, else the message, shortened to a length limit (limit decided here).
- Services (N-65, N-66): `assist_satellite.announce` for satellites; for media players `tts.speak` with the player, or `media_player.play_media` with `announce: true` only when the player's state shows the `MEDIA_ANNOUNCE` feature (the base class does not check it, N-75); otherwise plain playback at the current volume. The hub never changes or restores volume. Language from the Channels settings.
- Per-speaker queue so two messages do not overlap, and a short cooldown against identical repeats; speech cannot be cleared and nothing is said when a message is resolved (D-091); quiet hours `quiet` skips speech.
- Failures give a `failed` delivery with a reason; a missing entity is flagged in the panel's needs attention list.

## Out of scope
Volume handling; all-clear announcements; room occupancy.

## Tests
Each service path with fakes from H0a (satellite, player with and without announce, tts); text fallback and shortening; groups and areas; queue and cooldown with the freezer; quiet skip; failure; hub off.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/actions.md` (`speak` shortcut, `tts_message`), `docs/limitations.md` (speech behavior and no volume handling), CHANGELOG, HA_API_NOTES, STATE.

## Parity (CLAUDE.md rule 9)
Rule messages reach speech only through escalation or fallback policies.

## Blast radius (rule 5)
Restart: the usual one. Notification path: touched (tts, media player, assist satellite services of other integrations).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Speech length limit; cooldown length. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-65, N-66 (platform behavior from H0b). (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Speak channel built and tested with fakes; `make check`, `make hassfest`, `make dev-smoke` (stubs) green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
