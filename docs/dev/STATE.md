# State

- Phase: 3 (Conditions + people) — complete, waiting for review and Phase 4 approval
- Gates: Phase 0 approved 2026-10-24; Phases 1–2 complete, Phase 3 approved 2026-10-25
- Done in Phase 3: `condition` (entity, state or list, attribute), `mode` once/recurring, `wait_for_condition`, unavailable/unknown keep visibility, re-evaluation on load, one state listener for all condition and person entities (released when unused), `people` targeting filtered in `heads_up/subscribe`, payload omits targeting/condition data (D-039), D-038
- Verified: 73 pytest tests, ruff, mypy strict, hassfest, docs-check (7 examples), `make dev-smoke` incl. condition + people against real `input_boolean` and person entities on HA 2026.9.4
- Not verified on the real instance: condition re-evaluation across a container restart (covered by unit tests `test_condition_survives_restart_and_is_reevaluated`, `test_restart_with_entity_not_yet_loaded_keeps_state`)
- Next: Phase 4 (card) on approval
- Publishing: not approved; nothing pushed (D-020)
