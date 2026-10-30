# H0b: Verify the remaining Home Assistant facts

Size: small. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Close the unverified items of the hub design, read-only against Home Assistant source and docs, and on the dev instance where possible. Update `docs/dev/HA_API_NOTES.md` rows N-61 to N-74 with a status of verified, wrong, or still open, and correct the design where a fact is wrong.

## Dependencies and parallel work
- Needs: none
- Can run at the same time as: H0a, H1
- Files this package owns (create): `docs/dev/HA_API_NOTES.md`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `docs/DESIGN.md` section 23 and `docs/OPEN_QUESTIONS.md` only if a fact changes the design

## Scope
- Announce and volume behavior: what `media_player.play_media` with `announce` does on the common platforms (restore of volume and playback), `assist_satellite.announce`, `tts.speak` (N-65, N-66). Say per platform what is verified.
- Custom panel: the web component contract (properties `hass`, `narrow`, `route`, `panel`), whether `panel_custom` must be in `dependencies` or `after_dependencies` of the manifest, how the module URL is cached and invalidated, how `trust_external` and `embed_iframe` behave (N-69).
- Whether the Companion app sends action presses through the `fire_event` webhook and with which `context.user_id` (N-72), from the app documentation or source.
- Whether a custom integration can ship blueprints for users (N-73).
- Device registry behavior for `mobile_app` devices: renamed devices, two devices with the same name (service name collision, N-70), removed devices.
- The same checks on Home Assistant 2026.10 (the dev instance moves to 2026.10 in H10; here read the 2026.10.x source).

## Out of scope
Writing code.

## Tests
None.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/dev/HA_API_NOTES.md`; `docs/OPEN_QUESTIONS.md` (close or reword items).

## Parity (CLAUDE.md rule 9)
Not applicable.

## Blast radius (rule 5)
None.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
None; report findings that change the design and ask before changing a decision.

## Home Assistant facts to verify or rely on
N-65, N-66, N-69, N-72, N-73, N-74. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Every row N-61 to N-74 has a status; design text corrected where a fact was wrong; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
