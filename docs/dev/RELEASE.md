# Release

Releases `v0.1.0` to `v0.4.0` follow the steps below (D-020: tags and pushes only with the maintainer's explicit approval).

## Before the first release (maintainer, on github.com)
1. CI: open the Actions tab of `Seyphaton/ha-heads-up`. Workflows `CI` (jobs `python`, `python-ha-2026-9`, `card`) and `Validate` (jobs `hacs`, `hassfest`) must be green on `main`. They had never run before the first push.
2. Settings > General > Danger Zone > Change visibility > Public. HACS only works with public repositories (N-18).
3. About (gear icon on the repository page): set the description and topics.
   - Description: `Dismissible dashboard banners for Home Assistant, created by actions`
   - Topics: `home-assistant`, `hacs`, `home-assistant-custom-component`, `lovelace`, `notifications`, `banner`
4. Settings > General > Features: Issues enabled (the HACS Action checks it; the bug report template needs it).
5. Settings > Code security: enable private vulnerability reporting (`SECURITY.md` asks reporters to use it).
6. Try the integration once on your own Home Assistant (copy `custom_components/heads_up`, restart, add the integration, add the card). It has only been run on the dev instance.

## Publish 0.1.0
1. `make check`, `make hassfest` and `make dev-smoke` green; the release commit is pushed and CI is green on it.
2. Tag and push the tag:

   ```bash
   git tag -a v0.1.0 -m "Heads Up 0.1.0"
   git push origin v0.1.0
   ```

3. github.com > Releases > Draft a new release > choose tag `v0.1.0` > title `0.1.0` > paste the `[0.1.0]` section of `CHANGELOG.md` as the notes > Publish. HACS reads versions from releases, not tags (N-18).
4. Add the repository to HACS as a custom repository (README, "With HACS") and download it to check the install path.

## Releasing the hub (prepared in H10, not done)
The hub, the panel and the new channels are on a chain of feature branches ending in `hub/h9e-wizard`. Nothing is merged, tagged or pushed (D-020, D-123).
1. Decide the version. The manifest says 0.4.0 and `CHANGELOG.md` has an Unreleased section with every change; rename it to the version and date.
2. Merge the chain into `main` in the order of `docs/dev/hub/ROADMAP.md`. Every branch continues the one before it, so merging `hub/h9e-wizard` brings all of them.
3. Run `make check`, `make hassfest` and `make dev-smoke`, and let CI run (jobs `python` on 2026.10.4, `python-ha-2026-9` on 2026.9.4, `card`) before tagging.
4. Check on real devices what the stub devices could not (`docs/OPEN_QUESTIONS.md`, hub section): a Companion push with buttons, the iOS critical level, snooze and acknowledge from a phone, speech on a speaker and a satellite, the popup on a wall tablet.
5. Update `version` in `custom_components/heads_up/manifest.json`, commit, tag and push the tag, create the GitHub release as for 0.1.0.

## Default HACS list (optional)
Custom-repository installs work without this. For the default list (N-54): the repository is public, the HACS Action and hassfest pass without ignores, a full GitHub release exists. Then fork `hacs/default`, create a branch from `master`, add `Seyphaton/ha-heads-up` to the file `integration` in alphabetical order, and open a pull request from a personal account with the template filled in.

## Later releases
1. Update `version` in `custom_components/heads_up/manifest.json` (SemVer) and `CHANGELOG.md` (Keep a Changelog, from real commits), and commit and push that before tagging. The tag must point at a commit whose manifest has the same version (0.2.0 was tagged without it, so 0.2.1 exists).
2. `make check`, `make hassfest` and `make dev-smoke` green; CI green.
3. Commit, tag `vX.Y.Z`, push the tag, create the GitHub release.
4. The card URL carries `?v=<manifest version>-<file hash>`, so browsers fetch the new card after the HA restart, even if the version was not bumped (D-050).

Compatibility policy: DESIGN.md §13.
