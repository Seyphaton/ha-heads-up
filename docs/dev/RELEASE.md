# Release

1. Update `version` in `custom_components/heads_up/manifest.json` (SemVer) and `CHANGELOG.md` (Keep a Changelog, from real commits).
2. `make check`, `make hassfest` and `make dev-smoke` green; the CI jobs (`python`, `python-ha-2026-10`, `card`, `hassfest`, `hacs`) green on the release commit.
3. Commit, tag `vX.Y.Z`, push tag.
4. Create a GitHub **release** for the tag. HACS reads versions from releases, not tags (HA_API_NOTES N-18).
5. The card URL carries `?v=<manifest version>-<file hash>`, so browsers fetch the new card after the HA restart, even if the version was not bumped.

Compatibility policy: DESIGN.md §13.

Before the first release (maintainer's decisions, D-020):
- Create the public GitHub repository, set the remote, push. Make sure the repository has a description and topics (N-18).
- Replace the placeholders in `manifest.json` (`documentation`, `issue_tracker`, `codeowners`) and `hacs.json` if the repository address differs.
- Add the README screenshots and the HACS install steps.
- Check the HACS action output; the brands check reads `custom_components/heads_up/brand/icon.png` (N-47).
- Set the first version (the manifest says `0.0.0`) and move the CHANGELOG "Unreleased" entries under it.

