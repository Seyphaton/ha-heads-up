# Release

Releases `v0.1.0` to `v0.4.0` follow the steps below (D-020: tags and pushes only with the maintainer's explicit approval). The pre-releases `v1.0.0-alpha.1` to `v1.0.0-alpha.8` were tagged and pushed on the hub branch (D-196); `v1.0.0-alpha.9`, `v1.0.0-alpha.10` and `v1.0.0-beta.1` were tagged and pushed; 1.0.0 is released from `main`. 1.1.0 is built on `release/1.1`; `v1.1.0-beta.1` (D-226), `v1.1.0-beta.2` (D-228) and `v1.1.0-beta.3` (D-233) are tagged and pushed there; "Releasing 1.1.0" is the open runbook. 2.0.0 is built on `release/2.0`, which holds `release/1.1`; `v2.0.0-beta.1` is tagged and pushed there (D-243); `2.0.0-beta.2` is prepared (D-247, not tagged); the GitHub pre-release is the maintainer's step.

## Before the first release (maintainer, on github.com)
1. CI: open the Actions tab of `Seyphaton/ha-heads-up`. Workflows `CI` (jobs `python`, `python-ha-2026-9`, `card`) and `Validate` (jobs `hacs`, `hassfest`) must be green on `main`. They had never run before the first push.
2. Settings > General > Danger Zone > Change visibility > Public. HACS only works with public repositories (N-18).
3. About (gear icon on the repository page): set the description and topics.
   - Description: `Notification hub for Home Assistant: banners, push, popups, speech and mail with policies for who gets what and when` (the 0.x text, "Dismissible dashboard banners ...", is outdated)
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
State: `main` is at 0.4.0 and has no commit that `hub/h9e-wizard` lacks, so the merge is a fast-forward. The branch holds the hub, the panel and every change since 0.4.0. Its manifest says `1.0.0-beta.1`; the tags `v1.0.0-alpha.2` to `v1.0.0-alpha.8` are pushed on the branch (D-133, D-154, D-196). Nothing is merged to `main`, and there is no 1.0.0 (D-020: the maintainer decides).
1. Real-device checks first (`docs/OPEN_QUESTIONS.md`, hub section): a Companion push with buttons, the iOS critical level and the Android alarm, snooze and acknowledge from a phone, speech on a speaker and a satellite, mail through a real server, the popup on a wall tablet. While they are open, release another pre-release instead (step "Later releases", version `1.0.0-alpha.N`).
2. Decide the version (1.0.0). Rename `[Unreleased]` in `CHANGELOG.md` to it, with the date, and fold the alpha blocks into the notes of 1.0.0 or keep them below it. Set `version` in `custom_components/heads_up/manifest.json` and commit that on the branch.
3. `make check`, `make hassfest` and `make dev-smoke` green on a clean instance (`make dev-reset`, `make dev-up`, `make dev-onboard`); push the branch and read the CI result (jobs `python` on 2026.10.4, `python-ha-2026-9` on 2026.9.4, `card`; workflow `Validate`).
4. Merge `hub/h9e-wizard` into `main` (fast-forward) and push `main`, only on the maintainer's explicit approval.
5. Tag `v1.0.0` on the merge commit, push the tag, create the GitHub release (not a pre-release) with the 1.0.0 section as notes.
6. Update the README status and the HACS notes if they changed. The README's absolute image and document URLs already point at `main` (done 2026-11-12; they show nothing on GitHub until `main` has the merge, D-176).

## Releasing 1.1.0
State: `release/1.1` was cut from `main` at `c5af204` (D-207); 1.0.x fixes go to `main` and are merged into `release/1.1`. Manifest `1.1.0-beta.3` (D-233). Nothing is merged to `main`.
1. Real-device checks (`docs/OPEN_QUESTIONS.md`, section 1.1.0): speech volume and restore on a plain player and on Sonos, quiet hours and Presence on a real phone, home from an entity, the Severities colors on a phone. While they are open, release another pre-release (`1.1.0-beta.N`: manifest version, commit, tag, push).
2. Merge `main` into `release/1.1` if `main` moved. Rename `[Unreleased]` in `CHANGELOG.md` to `[1.1.0]` with the date and set `version` in the manifest to `1.1.0`.
3. `make check`, `make hassfest` and `make dev-smoke` green; an upgrade from a 1.0.0 setup on the dev instance converts Away policies; push the branch and read CI.
4. Merge `release/1.1` into `main` and push `main`, only on the maintainer's explicit approval.
5. Tag `v1.1.0` on `main`, push the tag, create the GitHub release (not a pre-release) with the 1.1.0 section as notes.

## Releasing 2.0.0
State: `release/2.0` was cut from `main` at `c5af204` and holds `release/1.1` (merged 2026-11-20, D-231), so 1.1.0 is not released on its own. Manifest `2.0.0-beta.2` (D-247); `release/2.0` and the tag `v2.0.0-beta.1` are pushed (2026-11-21); the tag `v2.0.0-beta.2` is not created. The first start converts policies to entry version 3.1; 1.x cannot read that (N-109), so the CHANGELOG and `docs/setup.md#upgrading` tell users to back up first.
1. Real-device checks (`docs/OPEN_QUESTIONS.md`, sections 2.0.0 design, 1.1.0 and hub). While they are open, release pre-releases (`2.0.0-beta.N`: manifest version, commit, tag, push on the maintainer's approval).
   - `v2.0.0-beta.1`, on the maintainer's approval: push `release/2.0` (`git push -u origin release/2.0`), read CI, tag the prepared commit (`git tag -a v2.0.0-beta.1 -m "2.0.0-beta.1"`), push the tag, create the GitHub pre-release with the `[Unreleased]` section of `CHANGELOG.md` as notes, its "Before you upgrade" list first. Mark it a pre-release, so HACS offers it only to users who show beta versions.
   - `v2.0.0-beta.2`, on the maintainer's approval: push `release/2.0` if it is ahead, read CI, tag the prepared commit (`git tag -a v2.0.0-beta.2 -m "2.0.0-beta.2"`), push the tag, create the GitHub pre-release (mark it a pre-release) with the `[Unreleased]` section of `CHANGELOG.md` as notes, its "Before you upgrade" list first.
2. Merge `main` into `release/2.0` if `main` moved. Rename `[Unreleased]` in `CHANGELOG.md` to `[2.0.0]` with the date and set `version` in the manifest to `2.0.0`.
3. `make check`, `make hassfest` and `make dev-smoke` green on a clean instance; an upgrade from a 1.1 setup on the dev instance converts the policies and shows the check list; push the branch and read CI.
4. Merge `release/2.0` into `main` and push `main`, only on the maintainer's explicit approval. `release/1.1` needs no own merge.
5. Tag `v2.0.0` on `main`, push the tag, create the GitHub release (not a pre-release) with the 2.0.0 section as notes. The tags `v1.1.0-beta.*` stay as they are.

## Default HACS list (optional)
Custom-repository installs work without this. For the default list (N-54): the repository is public, the HACS Action and hassfest pass without ignores, a full GitHub release exists. Then fork `hacs/default`, create a branch from `master`, add `Seyphaton/ha-heads-up` to the file `integration` in alphabetical order, and open a pull request from a personal account with the template filled in.

## Later releases
1. Update `version` in `custom_components/heads_up/manifest.json` (SemVer) and `CHANGELOG.md` (Keep a Changelog, from real commits), and commit and push that before tagging. The tag must point at a commit whose manifest has the same version (0.2.0 was tagged without it, so 0.2.1 exists).
2. `make check`, `make hassfest` and `make dev-smoke` green; CI green.
3. Commit, tag `vX.Y.Z`, push the tag, create the GitHub release.
4. The card URL carries `?v=<manifest version>-<file hash>`, so browsers fetch the new card after the HA restart, even if the version was not bumped (D-050).

Compatibility policy: DESIGN.md §13.
