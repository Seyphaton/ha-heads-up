# Release

1. Update `version` in `custom_components/heads_up/manifest.json` (SemVer) and `CHANGELOG.md` (Keep a Changelog, from real commits).
2. `make check` and `make hassfest` green.
3. Commit, tag `vX.Y.Z`, push tag.
4. Create a GitHub **release** for the tag. HACS reads versions from releases, not tags (HA_API_NOTES N-18).
5. The card URL carries `?v=<manifest version>`, so browsers fetch the new card after the HA restart.

Compatibility policy: DESIGN.md §13.
