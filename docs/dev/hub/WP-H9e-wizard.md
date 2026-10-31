# H9e: Setup wizard (window and config flow entry)

Size: medium. Status: built differently, on branch `hub/h9e-wizard` (see `ROADMAP.md`): the maintainer replaced the wizard and the presets by a welcome with four default policies and added the policy type Deliver (D-121). The scope below is historical. Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Build the four-step wizard as a window in the panel and as a config flow entry on the integration page, creating the same objects.

## Dependencies and parallel work
- Needs: H9a, H2, H4a
- Can run at the same time as: H9b, H9c, H9d, H9f
- Files this package owns (create): `frontend/panel/wizard.js`, `hub/wizard.py`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `config_flow.py` (wizard entry), `strings.json`, `translations/*.json`

## Scope
- Steps per UX_SPEC: people, devices, loudness (Quiet, Balanced, Loud), test; Create writes recipient profiles and the preset's policies and never deletes or changes existing objects; Apply preset on the Settings page adds only missing policies.
- Presets contents are fixed here (proposed in DEFAULTS_AND_PROPOSALS) and recorded as a decision.
- A first-run prompt on the Overview and a button on Settings; the config flow entry works without the panel.

## Out of scope
Editing policies.

## Tests
Creation matrix per preset; idempotence; existing policies untouched; config flow and panel produce identical objects; translation parity.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, UX_SPEC, how-to at H10, STATE.

## Parity (CLAUDE.md rule 9)
Not a banner feature.

## Blast radius (rule 5)
Creates objects only on the admin's confirmation.

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Preset contents. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Wizard built and tested in both entry points; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
