# H9a: Panel shell, navigation, Settings page

Size: medium. Status: not started (the roadmap table in `ROADMAP.md` is the status source). Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Register the admin panel, build the two-level navigation and the Settings page, so later pages plug in.

## Dependencies and parallel work
- Needs: H1
- Can run at the same time as: H2, H3, H4a, H5, H6, H7
- Files this package owns (create): `hub/panel.py`, `frontend/heads-up-panel.js` (shell), `tests/hub/test_panel_*.py`, `tests/card/panel.test.js`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `__init__.py` (register and remove the panel), `manifest.json` (`panel_custom` if required, N-69), `websocket.py` (settings commands), `strings.json`, `translations/*.json`, `.claude/rules/frontend-card.md`

## Scope
- Register through `panel_custom.async_register_panel` (`module_url`, `require_admin: true`, sidebar title and icon, N-69) or through `frontend.async_register_built_in_panel` with component `custom` (N-77); check with `make hassfest` which one passes the manifest rules and record it; the element is a standard class that takes `hass`, `narrow`, `route`, `panel` and owns its page including a way to open the sidebar, remove it on unload with `async_remove_panel`; static path and cache busting like the card. Every panel WebSocket command checks admin itself (N-69).
- Navigation per UX_SPEC: five groups, second row for groups with more than one page, wizard as a window opened by a button.
- Option `show_panel` (default false) set in a new step of the integration's setup flow (initial setup) and changeable in Settings; the panel is registered only when it is true. Installations that already exist have the option false until the user enables it.
- Settings page: hub switch, limits, history, install token (read-only), people and devices summary, loudness presets, the 'Run the setup wizard' button; saving writes the integration options through the options flow API or a command that updates options.
- Decision to ask: the panel is one ES module or a shell that loads one module per page (conflicts when parallel sessions build pages); recommended: a shell plus one module per page file under `frontend/panel/`.
- Strings in four languages; accessible names for tabs; dark and light themes.

## Out of scope
Page content other than Settings (H9b to H9f).

## Tests
Registration and removal; admin-only commands (non-admin refused); settings read and write; options persisted; vitest for navigation.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
CHANGELOG, DESIGN 23.10, UX_SPEC if details change, STATE.

## Parity (CLAUDE.md rule 9)
Not a banner feature.

## Blast radius (rule 5)
Sidebar: an admin-only entry that is not registered by default; the user enables it during initial setup (D-107).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Module layout; sidebar title and icon; whether the entry can be added and removed without a restart when the option changes; the wording of the setup step. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
N-69 (component contract, manifest, from H0b). (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Shell, navigation and Settings built and tested; checks green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
