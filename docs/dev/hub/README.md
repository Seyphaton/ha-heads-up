# Notification hub: where everything is

Status: design complete, build not approved (D-075). All files here are Claude-facing documents (`docs/dev/**`); user documentation is written when the features exist.

## What the hub is
Today's implementation sets the foundation for how notifications (right now: banners) are delivered; the hub expands this idea to more channels and additional features. A message with one id is delivered on up to five channels (banner, push, popup, speak, persistent notification), to audiences or direct recipients chosen per channel, under typed policies (Escalation, Quiet hours, Fallback, Reminder, Away, Summarize). Everything that exists today works without the hub, and the hub is off by default.

## Reading order for a new session
1. `CLAUDE.md` and `docs/dev/STATE.md` (end of file).
2. This file, then `ROADMAP.md` and the brief of your package (`WP-*.md`).
3. `docs/DESIGN.md` section 23 (the design) and `DECISION_INDEX.md` (which decisions are current).
4. `UX_SPEC.md` and the mockup (panel and card work).
5. `DEFAULTS_AND_PROPOSALS.md` (values: decided, proposed, open).
6. `docs/dev/HA_API_NOTES.md` rows N-61 to N-74 (verified Home Assistant facts and what is still unverified).
7. `docs/dev/PHASE_PROMPT.md` (definition of done).

## Files
- `ROADMAP.md`: work packages, dependency graph, parallel lanes, shared files, branches, gates, decisions needed.
- `WP-*.md`: one brief per work package (goal, dependencies, files, scope, tests, docs, parity, blast radius, questions, done).
- `SESSION_PROMPTS.md`: the prompt to start a session for any package.
- `DECISION_INDEX.md`: every hub decision D-075 to D-106, current or superseded, and the current truth in one page.
- `UX_SPEC.md`: the panel and card UI, page by page, field by field.
- `DEFAULTS_AND_PROPOSALS.md`: every concrete value and its status.
- `TEST_PLAN.md`: the test matrix across packages.
- `docs/dev/mockups/hub-panel-mockup.html`: the interactive mockup (sample data, nothing saved); open it in a browser.

## Other places the hub is written down
- `docs/DESIGN.md` section 23: the consolidated design.
- `docs/DECISIONS.md`: D-075 to D-106 (decision text, alternatives).
- `docs/OPEN_QUESTIONS.md`: open items under "Phase 15: notification hub".
- `docs/dev/HA_API_NOTES.md`: N-61 to N-74.
- `docs/dev/HUB_PLAN.md`: the short readable plan.
- `docs/dev/HUB_DESIGN.md`: the historical planning record. It contains superseded text; where it differs from `DECISION_INDEX.md`, the index wins. Its problem statement, vocabulary and end-to-end journeys are README material for the release.

## Rules that matter most
- One package per approval; nothing pushed, merged or tagged without approval.
- Parity of action messages and rule messages (rule 9); watch rules are frozen (D-100).
- Dev instance only, stub services, never a real device or another instance.
- Installation-independent, English, no product names or comparisons in tracked files.
- Decisions to `docs/DECISIONS.md` immediately; out-of-scope ideas to `docs/OPEN_QUESTIONS.md`.

## README material for the release (approved by the maintainer)
- The problem statement: every automation hard-codes notify services, speaker entities, quiet-hour templates and clean-up logic; replacing a phone means editing every automation; a leak alert at night, a doorbell with nobody home, a critical alert nobody read; a push dismissed on one device is still shown on the wall tablet and spoken again.
- The vocabulary (message, channel, audience, recipient group, recipient profile, policy, acknowledgement, delivery) and the end-to-end journeys are in `docs/dev/HUB_DESIGN.md` (parts B1 and C6) and in the FAQ of `UX_SPEC.md`.
