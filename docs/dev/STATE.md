# State

- Phase: 1 (Scaffold and dev environment)
- Gate: Phase 0 approved 2026-10-24; Phase 1 done, waiting for review
- Done: integration skeleton (config flow, manifest, de/en translations, hacs.json), uv/Python 3.14 venv, tests green, ruff + mypy strict clean, Makefile, docker-compose, CI workflow, pre-commit, docs-check (words/placeholders active), `.claude/rules/*`, dev docs, CONTRIBUTING/SECURITY/CHANGELOG/LICENSE/issue template; repo scrubbed of installation-specific content (D-036)
- Not verified: `make dev-up`, `make hassfest` (Docker not installed); CI workflow (repo not published)
- Next: install Docker → `make dev-up`, onboarding, `make hassfest`. Then Phase 2 (backend core) on approval.
- Publishing: not approved; nothing pushed (D-020)
