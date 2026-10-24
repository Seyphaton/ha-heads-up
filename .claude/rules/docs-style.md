---
paths:
  - "*.md"
  - "docs/**"
  - "CHANGELOG.md"
  - ".github/**/*.md"
---

# Docs style

Two audiences, never mixed: human docs (`README.md`, `docs/*.md` user pages, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`) and Claude docs (`CLAUDE.md`, `docs/dev/**`, `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`).

Human docs
- Short imperative sentences for steps; plain statements of fact for behaviour; one idea per sentence. Second person, present tense, active voice.
- Say what the user sees, then what to do. State limitations and non-goals plainly.
- Every claim is backed by a test, the source, or a screenshot from the dev instance. Remove what you cannot back.
- Every YAML example is validated by `make docs-check`; every action/card field appears in the docs and vice versa.

All docs, ADRs, commits, comments
- Banned (unless quoting): seamless, robust, powerful, comprehensive, leverage, utilize, elevate, streamline, unlock, empower, effortless, cutting-edge, state-of-the-art, game-changer, next-level, delve, "in today's", "whether you're … or …", "it's worth noting", "please note that", simply, easily, "just works", best-in-class, ultimate, supercharge, "a testament to", "rich ecosystem". Replace adjectives with the number, behaviour or limit.
- No marketing intro, tagline, emoji in headings/bullets/commits, badge wall (max: release, HACS, license), vague "Features" list.
- No filler sections (Overview/Introduction/Conclusion), no summary that repeats the section above, no "Happy automating!".
- No docs for things that do not exist; no TODO/TBD/Lorem/"coming soon" on main. Future ideas → `docs/OPEN_QUESTIONS.md`.
- Specific over generic: exact entity, field, event, error code, default, limit.
- No invented history, versions, benchmarks, compatibility claims, user quotes. Compatibility only for what was tested.
- Commit messages and CHANGELOG describe the real change and its user effect; no "improve", "enhance", "various fixes".
- Before every doc commit: read as a user with only this page; delete removable sentences; check claims; run `make docs-check`.
- Empty or generic section → omit it.
