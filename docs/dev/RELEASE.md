# Release

Releases `v0.1.0` to `v0.4.0` follow the steps below (D-020: tags and pushes only with the maintainer's explicit approval). The pre-releases `v1.0.0-alpha.1` to `v1.0.0-alpha.5` were tagged on the hub branch; "Releasing 1.0.0" is the open runbook.

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

## Releasing 1.0.0 (the hub)
State: `main` is at 0.4.0 and has no commit that `hub/h9e-wizard` lacks, so the merge is a fast-forward. The branch holds the hub, the panel and every change since 0.4.0. Its manifest says `1.0.0-alpha.5`; the tags `v1.0.0-alpha.2` to `v1.0.0-alpha.5` are pushed on the branch (D-133, D-154). Nothing is merged to `main`, and there is no 1.0.0 (D-020: the maintainer decides).
1. Real-device checks first (`docs/OPEN_QUESTIONS.md`, hub section): a Companion push with buttons, the iOS critical level and the Android alarm, snooze and acknowledge from a phone, speech on a speaker and a satellite, mail through a real server, the popup on a wall tablet. While they are open, release another pre-release instead (step "Later releases", version `1.0.0-alpha.N`).
2. Decide the version (1.0.0). Rename `[Unreleased]` in `CHANGELOG.md` to it, with the date, and fold the alpha blocks into the notes of 1.0.0 or keep them below it. Set `version` in `custom_components/heads_up/manifest.json` and commit that on the branch.
3. `make check`, `make hassfest` and `make dev-smoke` green on a clean instance (`make dev-reset`, `make dev-up`, `make dev-onboard`); push the branch and read the CI result (jobs `python` on 2026.10.4, `python-ha-2026-9` on 2026.9.4, `card`; workflow `Validate`).
4. Merge `hub/h9e-wizard` into `main` (fast-forward) and push `main`, only on the maintainer's explicit approval.
5. Tag `v1.0.0` on the merge commit, push the tag, create the GitHub release (not a pre-release) with the 1.0.0 section as notes.
6. Update the README status and the HACS notes if they changed.

## Default HACS list (optional)
Custom-repository installs work without this. For the default list (N-54): the repository is public, the HACS Action and hassfest pass without ignores, a full GitHub release exists. Then fork `hacs/default`, create a branch from `master`, add `Seyphaton/ha-heads-up` to the file `integration` in alphabetical order, and open a pull request from a personal account with the template filled in.

## Later releases
1. Update `version` in `custom_components/heads_up/manifest.json` (SemVer) and `CHANGELOG.md` (Keep a Changelog, from real commits), and commit and push that before tagging. The tag must point at a commit whose manifest has the same version (0.2.0 was tagged without it, so 0.2.1 exists).
2. `make check`, `make hassfest` and `make dev-smoke` green; CI green.
3. Commit, tag `vX.Y.Z`, push the tag, create the GitHub release.
4. The card URL carries `?v=<manifest version>-<file hash>`, so browsers fetch the new card after the HA restart, even if the version was not bumped (D-050).

Compatibility policy: DESIGN.md §13.
