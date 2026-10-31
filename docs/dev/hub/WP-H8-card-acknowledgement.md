# H8: Card: acknowledgement line and button

Size: small. Status: built on branch `hub/h8-card-ack` (see `ROADMAP.md`). Decisions in D-116. Build only after the maintainer approves this package (CLAUDE.md rule 1). Nothing is pushed or merged without approval (rule 7).

## Goal
Show acknowledgement on the banner and let a viewer acknowledge when a policy asks for it.

## Dependencies and parallel work
- Needs: H1, H4a
- Can run at the same time as: H3, H5, H6, H7
- Files this package owns (create): `frontend/heads-up-card.js` additions, `tests/card/*`
- Shared files it touches (keep changes to a clearly delimited block, expect merge conflicts in `strings.json`, `translations/*.json`, `config_flow.py`, `__init__.py`): `websocket.py` (payload fields, `heads_up/acknowledge` if not in H4a), `models.py` (`to_client`), `docs/card.md`, `strings`/`STRINGS` table in four languages

## Scope
- Payload fields `acknowledged` and `acknowledged_by` (first name of the person); the card line 'Acknowledged by <first name>' with a card option to hide it (option name decided here; it goes in `CONFIG_KEYS`, the editor schema, `normalizeConfig`, `docs/card.md` and a test, per the frontend rule). When several people acknowledged show the first only unless decided otherwise.
- An Acknowledge button on a banner when an escalation or reminder policy applies to the message; calls the acknowledge command.
- Parity: the same payload for action and rule messages; rule messages can be acknowledged if a policy applies by severity and tag.

## Out of scope
Panel pages.

## Tests
vitest for the new pure functions and option; payload tests for both sources; docs-check card option parity.

## Documentation to update (definition of done in `docs/dev/PHASE_PROMPT.md`)
`docs/card.md` (new option and the line), CHANGELOG, STATE.

## Parity (CLAUDE.md rule 9)
Both sources, tested.

## Blast radius (rule 5)
Dashboard: a new line and button only when a policy applies; option off by default? (decide).

## Ask the maintainer first (AskUserQuestion, recommended first; record answers in `docs/DECISIONS.md`)
Option name and default; line text with several people. Open items listed in `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md` that this package needs: ask each with AskUserQuestion and record the answer in `docs/DECISIONS.md` before relying on it.

## Home Assistant facts to verify or rely on
None. (rows in `docs/dev/HA_API_NOTES.md`). Verify any API not listed there before using it (rule 4).

## Done when
Card changes built and tested; `make check` (incl. vitest, docs-check) green; STATE updated.

## Read first
`CLAUDE.md`, `docs/dev/STATE.md`, `docs/dev/hub/README.md`, `docs/dev/hub/ROADMAP.md`, this file, `docs/DESIGN.md` section 23, `docs/dev/hub/DECISION_INDEX.md`, `docs/dev/hub/UX_SPEC.md` (for panel and card work), `docs/dev/hub/DEFAULTS_AND_PROPOSALS.md`, `docs/dev/PHASE_PROMPT.md`. Session prompt: `docs/dev/hub/SESSION_PROMPTS.md`.
