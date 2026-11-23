# Personal inbox: plan for Phase 22

Status: plan only, written 2026-11-23 on `release/2.1` (`e88ab51`). Nothing is built. Build starts only on the maintainer's explicit go (CLAUDE.md rule 1). Decisions: D-264. Line numbers and names below were read on that date; re-check before relying on them.

## 1. What it is

A per-person list of messages that survives a restart. One item per message and person, with title, text, severity, time, read state and a short timeline (sent, acknowledged, resolved). It answers "what was that message again?" and "what did I miss while I was away?".

It is a channel, so policies, audiences, presence and fallback apply to it like to push. A setting can also keep a copy of every message a person receives on another channel.

Requests it answers: history per person that survives a restart; a personal count of what is waiting (only what the person still has to look at, critical visible at once); one row per message, not one per reminder; person shown, not phone; opening is not acknowledging; messages kept for someone who was away.
Left out on purpose: a received time from the phone (needs the app's confirmation event), a history of messages nobody was addressed with, a `sensitive` flag (D-264, open question).

## 2. Model

Store `heads_up.inbox` (own store, own version, like `heads_up.stats`). Open: one file or one per person; measure first (see step 1).

Item, keyed by (person entity ID, message ID):
- `title`, `text`, `severity`, `icon`, `color`, `image` (the reference only, never fetched), `source` (`engine.source_key`, a key, never a name), `tag`.
- `created`, `updated`, `read_at`, `acknowledged_at`, `resolved_at`, `resolved_reason` (cleared, expired, condition, dismissed).
- `via`: channels that reached the person ("push, popup"), from the mirror or the delivery.
- `timeline`: at most 10 entries (kind, time, channel); reminders and escalations add an entry, never a row.
- `reminders`: count.

Rules:
- A content update or a higher severity writes the same item and marks it unread. A reminder or escalation only adds a timeline entry (the person already saw it; open: confirm).
- `Kind.HIDDEN` for the message (condition, timeout, clear, global dismissal) sets `resolved_at`; the item stays and stays unread (D-264). A dismissal by this person marks it read and resolved.
- `Kind.ACKNOWLEDGED` by this person marks it read. Acknowledged by another person only adds a timeline entry.
- Retention: setting `inbox_retention_months`, 1 to 36, default 12. Pruned at load and once a day. A person removed from Home Assistant: the inbox is purged.
- Writes are debounced (`SAVE_DELAY`).

## 3. Channel `inbox`

- New file `hub/channels/inbox.py` (model: `mail.py` for a person-addressed channel, `popup.py` for per-user state). `deliver` and `update` upsert, `clear` marks resolved. Targets: persons (audience or recipients), like popup (DESIGN §23.5).
- Added to `CHANNELS`, `TARGET_CHANNELS`, `PROFILE_CHANNELS` and `POLICY_CHANNELS` in `const.py`, to the strings and the Channels page (panel `channels.js`), Test send and the checker (`hub/checker.py`, `hub/reach.py`).
- It is silent, so no hold applies: Quiet hours and Away must not hold it. To verify in `hub/policies/` before building; if a policy holds every channel, the inbox gets an explicit exemption and a test.
- Not subject to push or popup rate limits (`hub/limits.py`). Not repeated on update by speech rules (`NOT_REPEATED_ON_UPDATE` does not list it: an update changes the item).
- Mirror: option `inbox_mirror` (list of severities, default empty). After the engine plans the deliveries of a message, each person reached on any channel gets an implicit inbox delivery with origin `mirror`, through the same channel code and the same trace line. Speech to a speaker group with no person is not mirrored. Hook point: next to the stats recording hooks in `hub/engine.py` (D-246).
- Watch rules: no channels (D-100). Their messages reach the inbox through the mirror or a policy; DESIGN §22 gets a line, no exception.
- Summaries (Summarize policy) hold the banner and channels; the mirror records the single messages when they are created, not the summary (open: confirm).

## 4. Surfaces

### 4.1 Card `custom:heads-up-inbox-card`
- Files: new `frontend/heads-up-inbox-card.js` (or a lazy module of `heads-up-loader.js`; decide after reading `frontend.py`), registered like the card and popup.
- Sizes and designs (D-266, reference `docs/dev/mockups/inbox-card.html`, all checked there): small square tiles (number, ring, mosaic of the unread icons without text), medium boxes (Tile, Ring, Split with the buttons Open and Mark all read and, with messages on, a pen button), and the large list (switch Inbox, Everything, Sent; day groups; expandable rows with a timeline; compose dialog from the pen button). A badge card opens the same dialog as the list.
- Proposed options, to settle in the build: `size` (`small`, `medium`, `large`), `design` (small: `number`, `ring`, `mosaic`; medium: `tile`, `ring`, `split`), `show_text` (medium Split and Tile show the latest unread title; open: default off for shared screens).
- Look rules: severity colors from the severity settings; one check mark when everything is read; the mosaic shows at most four tiles and then "+N"; a critical unacknowledged item is ringed or flagged red with a symbol, never by color alone.
- It always shows the viewing user's own inbox. No `person` option (D-264). A user without a person entity sees an empty card with a hint.
- "Opened" means the row is expanded, never that the card rendered.
- WebSocket (user-scoped, the person comes from `connection.user`): `heads_up/inbox_list` (paged), `heads_up/inbox_subscribe` (live, model: `popup_subscribe`), `inbox_read`, `inbox_read_all`, `inbox_delete`, `inbox_clear`. No command returns another person's items, not even for an admin.
- Card options are mirrored in `docs/` (`make docs-check` enforces the parity).

### 4.2 Sensor
- `sensor.heads_up_inbox_<person>` per person entity, unique ID `<entry>_inbox_<person entity id>`, created and removed with the person (model: `GroupSensor` and its sync in `sensor.py`).
- State: unread count. Attributes: `needs_action`, `unread_critical`. Never title or text: every user can read entity states.
- Open: a person without a Heads Up setup gets a sensor too (a profile exists for every person, §23.7).

### 4.3 Push badge (iOS)
- Setting `push_badge` (default off). Sets the badge number on pushes to the person's iOS devices to the unread count.
- Unverified: the exact Companion key, whether a badge can change without a visible push, and the Android equivalent. Step 0 reads the Companion docs and records the result in `docs/dev/HA_API_NOTES.md`. If the badge cannot change without a push, the plan states it as a limit; it is not built around.
- Blast radius: the push path is touched (rule 5).

## 5. Settings and panel
- Settings page: `inbox_retention_months`, `inbox_mirror`, `push_badge`, a Clear inbox button (all people, with confirmation, like Clear history).
- Channels page: an Inbox row (on or off, mirror severities).
- Diagnostics: counts per person and the oldest date, never text. Stats store: unchanged (counts only).
- Four languages for every string (`strings.json`, `translations/`, panel text).

## 6. Steps (one commit each, `make check` before and after)

0. Done 2026-11-23 (N-115 to N-118, D-268): verify the user to person mapping the popup uses; whether policies hold a new channel; the iOS badge; store size for 12 months (measured 846 bytes per item, N-118: 6.2 MB per person at 20 items a day over 12 months; the estimate of 0.5 KB was too low). Record in `HA_API_NOTES.md`; decide one store or one per person.
1. `hub/inbox.py` and the store: model, upsert, read, resolve, retention, load and damaged rows dropped. Unit tests.
2. The `inbox` channel, engine wiring, constants, trace and ledger rows, checker, reach, Test send. Tests with the fake notify setup.
3. Read, acknowledge and dismiss hooks from transitions; WebSocket commands with a test per command that no other person's item is returned.
4. The sensor per person.
5. The card, its editor, loader registration, vitest for the pure functions, docs parity.
6. Mirror and retention settings, Settings page, Clear inbox, diagnostics.
7. Push badge, only if step 0 allows it.
8. Docs: README, `docs/*.md`, CHANGELOG, DESIGN §29, SECURITY (plain-text storage, retention), TESTING, FAQ in four languages, STATE, DECISIONS, OPEN_QUESTIONS.
9. Dev instance: send messages on each channel, restart the container, check the card at desktop and phone width, light and dark, the sensor, retention with a sample file; `make dev-smoke` gets an `inbox` phase; `make check` and `make hassfest`.

## 7. Blast radius
- Restart needed (new platform entities, store, WebSocket commands).
- Notification path: a new channel and, with `push_badge`, the push payload. Off by default, so existing setups send what they sent before.
- Dashboard: nothing changes until the card is added.
- Storage: a new store with message text in plain text (also in backups). Downgrade: an older release ignores the store.
- Parity (rule 9): action and rule messages both reach the inbox through the mirror and policies; no exception planned.

## 8. Open
- Version: a new phase on its own branch, or part of 2.1.0? Everything is additive and off by default.
- Does a reminder mark an item unread again (planned: no)?
- One store or one per person (decided by the step 0 measurement).
- `sensitive` flag and private messages (D-264, `docs/OPEN_QUESTIONS.md`).
- A wall tablet logged in as one person shows that person's text to the room; a card option that shows titles only is a candidate.
- Received time from the app (Android confirmation event): not planned.

## 9. Phase 23: messages to other people (D-265)

Own phase after the inbox. Nothing is built. Needs the inbox store, the `inbox` channel and the user-scoped WebSocket commands (steps 1 to 3).

Scope (tier 1 plus a Sent view):
- WebSocket command `heads_up/send_message` (any logged-in user, not admin-only): `to` (person entity IDs), `text`. The sender is the person of `connection.user`; the call has no sender field. A user without a person entity cannot send.
- The call takes `channels`: `inbox` always, plus `push` and `popup` as the sender chooses (default `inbox` and `push`). `speak` and `mail` are refused. For each recipient the engine checks the accepted channels of their profile (`PROFILE_CHANNELS`, D-088) and skips a channel they do not accept; the result lists the skipped channel per person and the dialog shows it. The message goes through the same engine path as `notify`, so quiet hours and the other policies apply. Severity is always `info`; the sender cannot set it (D-265).
- Inbox item gets `sender` (person entity ID). The card shows "From Anna" with the person's picture.
- Sent view: the sender gets an item of kind `sent` in their own store (recipients, text, time). It has no read state, no unread dot and no badge count. Delete removes it for the sender only.
- Admin switch `inbox_messages` (default off, no behaviour change on upgrade). Limits: text up to `MAX_MESSAGE` (1000), a rate limit per sender (open: number and window).
- No read receipts: the recipient's read state is never sent to the sender, not in the card, the sensor or the WebSocket result.
- Card: a compose button, a dialog with recipient chips, a "Send via" row and a text field, and a third switch segment "Sent" next to Inbox and Everything. Only people with a Heads Up profile are offered; a person without a phone is offered and reached by inbox and screens (D-265).

Rules and exceptions:
- Parity (rule 9): action messages may carry a sender only through this command; the `notify` action gets no `sender` field. Watch rules have no caller and no sender; DESIGN §22 lists that.
- Privacy: text is stored in plain text for sender and recipient; `SECURITY.md` says so. Retention is the inbox setting.
- Message Log and diagnostics show no text, as for every message.

Steps (one commit each):
0. Verify: how `panel_test.send` builds a message, how a user maps to a person, what a non-admin may call.
1. Model and store: `sender`, kind `sent`, retention. Tests.
2. `heads_up/send_message` with the sender from the connection, the channel list checked against the recipient profiles (skipped channels reported), the severity cap, the limits and the rate limit; tests that a forged sender is impossible and that a user without a person is refused.
3. The Sent items and the "From" display in the list and badges.
4. Compose dialog and the Sent segment in the card; vitest for the pure functions.
5. Setting `inbox_messages` on the Settings page; strings in four languages; docs; DESIGN §22 line; CHANGELOG, STATE, OPEN_QUESTIONS (permissions, opt-out, replies, pictures).
6. Dev instance checks (two users, browser pane), `make dev-smoke` phase, `make check`, `make hassfest`.

Open:
- Rate limit numbers.
- Later tiers: permissions, per-person opt-out, replies, lock-screen reply, pictures (`docs/OPEN_QUESTIONS.md`).
