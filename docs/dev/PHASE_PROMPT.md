# Phase session prompt

Paste the block below into a new Claude Code session started in this repo, replacing `<N>` with the phase number. It works for every phase (4, 5, 6 and later work).

---

You are continuing the Heads Up (`heads_up`) Home Assistant integration in this repository. Work on **Phase <N>** only.

## 1. Load context before doing anything
1. Read `docs/dev/STATE.md` (current phase, gate status, setup steps, plan for the next phase).
2. Read `docs/DESIGN.md` §0 (implementation status) and the sections the phase touches.
3. Skim `docs/DECISIONS.md` (decisions D-nnn; gate log at the end) and `docs/OPEN_QUESTIONS.md`.
4. Check `docs/dev/HA_API_NOTES.md` for every HA API the phase will use.
5. Run `make setup` and `make check`; report anything red before changing code.

## 2. Gate
- Do not write code for Phase <N> until the maintainer has approved it explicitly. Ask with the AskUserQuestion tool.
- Ask every open decision, design choice or risk with AskUserQuestion: 2–4 options, recommended option first and marked. Record each answer in `docs/DECISIONS.md` immediately.
- Use only core Claude Code tools, plus read-only web access to HA docs and source (D-028). No connectors or MCP servers.
- Never connect to any Home Assistant instance other than the local dev instance (D-003). Nothing is pushed or published without explicit approval (D-020).
- Tracked files stay installation-independent (D-036): no personal setup, hosts, addresses or tool configuration.

## 3. Work
- Spikes and unverified API facts first; record results in `docs/dev/HA_API_NOTES.md` (source URL, HA version, date, status).
- Tests before implementation for behaviour changes.
- Small, reversible steps; one logical change per commit; documentation in the same commit as the behaviour it describes.
- Verify on the dev HA (`make dev-up`, `make dev-smoke`, plus phase-specific checks), not only in unit tests.

## 4. Documentation definition of done
The phase is not finished until every item below is true. Check each one and report it in the phase summary.

Claude-facing docs
- [ ] `docs/DESIGN.md` matches the code: §0 status table, module list, schemas, lifecycle, WebSocket API, edge cases. No section describes behaviour the code does not have.
- [ ] `docs/DECISIONS.md` has an entry for every decision made in this phase, and a gate-log line for the phase.
- [ ] `docs/dev/HA_API_NOTES.md` has a row for every HA API the phase uses, with status `verified` or a stated reason why not.
- [ ] `docs/OPEN_QUESTIONS.md` lists what is still open; resolved items moved to "Resolved" with a pointer to the test or decision.
- [ ] `docs/dev/TESTING.md` lists new test files and how to run them; `docs/dev/DEV_ENVIRONMENT.md` covers any new setup step or Make target.
- [ ] `CLAUDE.md` updated if commands, repo layout or rules changed; still under 200 lines.
- [ ] `docs/dev/STATE.md` rewritten for the next session: where we are, what is verified, what is not, setup steps, concrete plan for the next phase.

Human-facing docs
- [ ] Every user-visible behaviour added in this phase is documented in `README.md` or a page under `docs/` (`actions.md`, `card.md`, `examples.md`, `troubleshooting.md`, `limitations.md`, `uninstall.md`, `upgrading.md`), in the style of `.claude/rules/docs-style.md`.
- [ ] Every claim is backed by a test, the source or a check on the dev instance. Claims that cannot be backed are removed or listed as unverified in the phase summary.
- [ ] `CHANGELOG.md` "Unreleased" describes the user-visible changes of this phase.
- [ ] `SECURITY.md` still matches what the code does.

Checks
- [ ] `make check` green (lint, types, tests, docs-check: banned words, placeholders, YAML examples validated against the real schemas, field parity).
- [ ] `make hassfest` green.
- [ ] Staged files scanned for installation-specific content before each commit.

## 5. End of phase
Give a short summary: what was done, what was decided, what was verified and how, what is not verified, what is open, the documentation checklist above with each item ticked, and the proposed next phase. Then ask with AskUserQuestion whether to approve the next phase, and stop.
