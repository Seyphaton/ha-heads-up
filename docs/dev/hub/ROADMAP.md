# Hub roadmap: work packages, order and parallel lanes

Status: the hub is approved for build (D-107, 2026-10-30), on feature branches only; nothing reaches `main` until the maintainer confirms. Each package below is one phase approval (CLAUDE.md rule 1); a session builds exactly one package, then stops. The status column is updated by the maintainer or the session that finishes a package, on the branch it merges to.

## Packages
- H0a Test fixtures and dev stubs. Small. Needs nothing. `WP-H0a-test-scaffolding.md`
- H0b Verify the remaining Home Assistant facts. Small. Needs nothing. `WP-H0b-verify-ha-facts.md`
- H1 Core engine, notify action, message store. Large. Needs H0a. `WP-H1-core.md`
- H2 Audiences, recipient groups, recipient profiles. Medium. Needs H1. `WP-H2-audiences-recipients.md`
- H3 Push channel. Large. Needs H1, H2. `WP-H3-push-channel.md`
- H4a Policy framework, Escalation, Reminder, acknowledgement. Large. Needs H1 (H2 for real audiences). `WP-H4a-policy-framework.md`
- H4b Quiet hours, Away, Fallback. Medium. Needs H4a. `WP-H4b-quiet-away-fallback.md`
- H4c Summarize. Medium. Needs H4a. `WP-H4c-summarize.md`
- H5 Speak channel. Medium. Needs H1, H2. `WP-H5-speak-channel.md`
- H6 Popup channel (loader and popup). Medium. Needs H1. `WP-H6-popup-channel.md`
- H7 Persistent notification channel. Small. Needs H1. `WP-H7-persistent-channel.md`
- H8 Card acknowledgement line and button. Small. Needs H1, H4a. `WP-H8-card-acknowledgement.md`
- H9a Panel shell, navigation, Settings. Medium. Needs H1. `WP-H9a-panel-shell.md`
- H9b Panel Overview and Messages. Medium. Needs H9a, H1, H4a. `WP-H9b-overview-messages.md`
- H9c Panel editors (audiences, recipients, policies, channels). Large. Needs H9a, H2, H4a, H3. `WP-H9c-editors.md`
- H9d Panel Test send. Medium. Needs H9a, H1, H2, H4a. `WP-H9d-test-send.md`
- H9e Setup wizard. Medium. Needs H9a, H2, H4a. `WP-H9e-wizard.md`
- H9f Panel FAQ and Examples. Small. Needs H9a, H1. `WP-H9f-faq-examples.md`
- H10 Hardening, documentation, Home Assistant 2026.10, release preparation. Large, last. Needs everything. `WP-H10-hardening-release.md`

## Status
Nothing is merged until the full feature is implemented (maintainer, 2026-10-30). Work continues on one chain of feature branches: `hub/h1-core` was created from `hub/h0a-test-scaffolding` with `hub/h0b-verify-ha-facts` merged in, and later packages branch from it.
H0a: built 2026-10-30, branch `hub/h0a-test-scaffolding`. H0b: done 2026-10-30, branch `hub/h0b-verify-ha-facts`. H1: built 2026-10-30, branch `hub/h1-core`; `make check` (393 pytest, 81 vitest), `make hassfest` and `make dev-smoke` (with the new `hub_core` phases) green. H2: built 2026-10-31, branch `hub/h2-audiences` (from `hub/h1-core`); gates below. All others not started. One line per finished package: date, branch, commit, what was verified.

## Dependency graph
```
H0a ──► H1 ──┬──► H2 ──┬──► H3
             │         ├──► H5
             │         └──► (real audiences for H4a, H9c, H9d, H9e)
             ├──► H4a ──┬──► H4b
             │          ├──► H4c
             │          └──► H8
             ├──► H6
             ├──► H7
             └──► H9a ──┬──► H9b (needs H4a for states)
                        ├──► H9c (needs H2, H4a, H3)
                        ├──► H9d (needs H2, H4a)
                        ├──► H9e (needs H2, H4a)
                        └──► H9f
H0b (any time, before the packages that name it)
all ──► H10
```

## Lanes: what can run at the same time
One session per package, each in its own git worktree, each on its own branch.
- Start: H0a and H0b in parallel (tiny, no overlap: tests versus docs).
- Then H1 alone. It changes `manager.py`, the services and the options; nothing else may touch those files meanwhile.
- After H1 merges, these start in parallel (disjoint files):
  - Lane A: H2, then H3, then H5 (H5 can start when H2's resolver interface exists).
  - Lane B: H4a, then H4b and H4c in parallel, then H8.
  - Lane C: H6.
  - Lane D: H7.
  - Lane E: H9a, then H9b, H9d, H9f in parallel; H9c and H9e once H2 and H4a have merged.
- H10 starts when every other package has merged.

A package may start against a fake of a dependency it does not need to merge (the engine interfaces from H1 come with fakes). Its final integration tests run after the dependency merges.

## Shared files and how to avoid conflicts
Hot spots: `strings.json`, `translations/en.json`, `de.json`, `fr.json`, `es.json` (every package adds keys), `config_flow.py` (H2 and H4a add subentry types), `__init__.py`, `const.py`, `services.yaml`, `manifest.json`, `CHANGELOG.md`, `docs/dev/STATE.md`.
- Add keys in a block named after the package; never reorder existing keys.
- Merge in the order of the dependency graph; the session that merges second rebases and resolves.
- `docs/dev/STATE.md` and `ROADMAP.md` status are updated only by the session that finishes a package, in one line.
- Only H1 changes `manager.py`. If another package needs a new transition, it adds the kind in `hub/transitions.py` and asks the maintainer before touching `manager.py`.

## Branches
- This design lives on `design/notification-hub` (not merged to `main`, nothing pushed).
- Each package works on `hub/<id>` (for example `hub/h1-core`), created from the branch of the package it depends on (from `design/notification-hub` for H0a, H0b, H1). Packages that start in parallel after H1 branch from H1's tip.
- Merges go into `design/notification-hub` in graph order, only when the maintainer says so. Nothing goes to `main`, and nothing is pushed or tagged, without explicit approval (rule 7, D-020).

## Gates for every package
- `make check`, `make hassfest`, `make dev-smoke` green (the dev instance uses stub services, never a real device, rule 2).
- The documentation checklist of `docs/dev/PHASE_PROMPT.md`, including four-language strings and the parity audit of DESIGN 22.2.
- Every banner feature works for action messages and for rule messages, or the exception has a decision number (rule 9; D-100 lists the rule exception for hub delivery).
- Tracked files stay installation-independent and in English; no product names or comparisons (rule 6, D-036).

## Estimated order for one maintainer working sequentially
H0a, H0b, H1, H2, H4a, H3, H4b, H4c, H5, H6, H7, H8, H9a, H9b, H9c, H9d, H9e, H9f, H10. The parallel plan above shortens the calendar time without changing the order of dependencies.

## Decisions needed from the maintainer before building
1. Done: hub status (D-107).
2. Done: approval of the roadmap and of H0a and H0b (2026-10-30). Each later package needs its own approval.
3. The open and proposed values in `DEFAULTS_AND_PROPOSALS.md`, asked by the package that needs each one.
