# Overview redesign: plan for Phases 18 and 19

Status: plan only, written 2026-11-21 on `release/2.0` (`e8ab8ae`). Nothing is built. Build starts only on the maintainer's explicit go, one phase per approval (CLAUDE.md rule 1).

Approved mockup: `.claude/local/overview-mockups.html` in this worktree, a local file that is not committed (decision 15). Its step 2 and step 4 predate decisions 5 and 9; this plan is the later word. Every statement below was checked against the code of `release/2.0` on that date; file and line are given. Where the code does not back a mockup element, section 3 says so and what the plan does about it.

## 0. For the next session

- Work on `release/2.0` (worktree `.claude/local/wt-2.0` of the main checkout, or check the branch out anywhere). The state at writing is `e8ab8ae` plus the commit that added this plan; the line numbers below are from `e8ab8ae` and may have moved, so re-check each one before relying on it.
- Read in this order: `docs/dev/STATE.md`, this plan, `docs/DESIGN.md` §25, `CLAUDE.md`. The maintainer's decisions are rows 1 to 15 below and D-244 in `docs/DECISIONS.md`; do not reopen them, and ask (AskUserQuestion) for anything that needs a new design choice.
- Nothing is approved yet. Phase 18 starts when the maintainer says go; Phase 19 needs its own go. Put D-244 first in your work log, then follow section 4 step by step, one commit per step, `make check` before and after.
- The visual reference is a local file: `.claude/local/overview-mockups.html` in the worktree where this plan was written (git ignores it, decision 15). Open it in a browser and use the three switches at the top. If it is gone, section 3a has the content.
- Verified facts and the places where the mockup was wrong are sections 2 and 3. Section 3 lists what must be computed from the engine and not written as text.
- The dev instance is `make dev-up` (http://127.0.0.1:8124); check the page in the browser pane at desktop and phone width, light and dark, in all three states.

## 1. Decisions taken (maintainer, 2026-11-21)

| # | Question | Answer |
|---|----------|--------|
| 1 | History for periods, matrix, sources | New persistent store. It always covers the last 24 months. |
| 2 | Introduction tour | In-page on the Overview. The modal dialog is dropped. |
| 3 | Cells of "What would a message do right now?" | Run for the people of the Everyone audience; a cell shows a count when people differ. |
| 4 | Phasing | Two phases: 18 (layout on data that exists) and 19 (history). |
| 5 | Optional setup in the tour | Step 2 (Channels) holds only what a channel needs to work: the mail notify service (global address optional) and the speech engine where one is needed. Speakers are chosen in step 4 inside the Critical item, next to the audience select. Mail is configured only; no default policy sends it. The warning "no escalation covers critical" stays as it is. |
| 6 | Tips | None in the first version. Needs attention keeps only problems. |
| 7 | Status card | Counts only unacknowledged critical and warning messages. |
| 8 | Audience cards | The store keeps the time of the last leave and the first arrival. |
| 9 | When step 2 saves | The mail service, the global address and the engine are saved when the user leaves step 2. Policies, the audience and the speakers are written by Create in step 4. |
| 10 | Last period button | Labeled "2 years", because the store covers a rolling 24 months. The periods are 24 hours, week, month, year, 2 years. |
| 11 | Daily record | Full: hourly totals, severity, channel outcomes, acknowledge times and sources, plus the additions in 19.1 where they help later analysis and a recording hook exists. |
| 12 | Clear and diagnostics | A Clear history button in Settings with a confirmation, and the store size and date range in diagnostics. |
| 13 | Delivered | Sent divided by sent plus failed. Deliveries held or skipped by choice are not counted. |
| 14 | Version | Decided at release time. Neither phase changes the manifest or tags. |
| 15 | Mockup file | Stays local, not committed. |

These go to `docs/DECISIONS.md` when Phase 18 starts.

## 2. What exists today (verified)

Overview
- `panel_data.overview()` (`hub/panel_data.py:502`) returns active items, rule counts, attention, shortcuts, the last 50 log entries, a 24-hour histogram and `first_run` (no policies yet).
- `overview.js` (`frontend/panel/overview.js`) renders tiles, shortcut cards, the chart, Needs attention and Last actions, and polls every 10 s (`REFRESH_MS`).
- An item's states come from `message_states()` (`panel_data.py:427`): held in a summary, escalation due (`due`), reminder due (`due`, `count`), snoozed (`until`), acknowledged.
- `Attention` has the levels `error` and `warning` only; only warnings can be hidden (`panel_data.py:64-90`).

History
- `ActivityLog` is memory only and bounded by Trace entries kept (default 500, `const.py:273`). It starts empty after a restart (`hub/activity.py` docstring).
- The hourly chart counts at most the newest 5000 created messages over 24 hours (`activity.py`, `CREATED_KEEP`).
- The delivery trace is stored (`TRACE_KEY`, `const.py:127`), bounded by the same setting.
- The ledger drops a message's rows when it ends (`ledger.drop_message`, `hub/ledger.py:246`). Nothing keeps long-term counts.
- `Banner` has `created_at` and `acknowledged_by` (a list of user IDs), no acknowledge time (`models.py:32,67`). `manager.acknowledge` (`manager.py:465`) is the one place that knows when.
- The activity log has one write point: `HubEngine._log` (`hub/engine.py`, near line 562), called from `_remember`.

Dry run
- `HubEngine.preview()` (`hub/engine.py:335`) runs the real plan and the real precedence chain for a message that does not exist, and sends nothing. The checker `hub/checker.py` wraps it with an assumed clock and assumed presence (`clock.assumed`).
- A row carries `result`, `reason`, `note` (`quiet`), `by`, `until`, `push_level` and `through` (band entries that let it pass).

Welcome
- A modal dialog, `welcome.js` `open()` (line 363), opened by the shell on any first page (`heads-up-panel.js:344`, `openWelcome` at 389). Four steps (`STEPS`, line 258). Pausing for a page shows a resume bar (`_setTour`).
- Backend: `welcome_get` (`websocket.py:197`) and `welcome_apply` (`websocket.py:222`); `hub/welcome.py` builds the policies and sets `welcome_seen`.
- Restart introduction is a button in Settings (`docs/settings.md:19`).

## 3. Where the mockup is not backed by code, and what the plan does

1. Critical creates more policies than the mockup says. `welcome.policies_for` (`hub/welcome.py`) creates Critical (Get through), Critical delivery, Critical reminder, and Critical escalation only when speakers are chosen. So Critical makes 3 or 4 policies, and the whole tour 5 to 7, not "2" and "4". `apply` also sets the critical push level to `critical`. The Create button and the Critical text change to state this.
2. "Left at 17:40" and "Arrived at 07:12" have no source: the presence store keeps only two entity IDs (`hub/presence.py:74-82,192`). Decision 8 adds two optional timestamps to that store (step 18.3).
3. Median time to acknowledge has no source. Phase 19 records the difference between `created_at` and the moment of `acknowledge`.
4. "The last critical message was acknowledged 2 hours ago" would come from the memory log and disappear at a restart. Phase 18 drops that line; Phase 19 can restore it from the store.
5. Cells that depend on settings are never hard-coded. The engine says: banner unaffected by quiet hours (`policies/quiet.py`, `apply`); the Quiet action sends push at level `passive` (`channels/push.py:112`), shows a popup as a corner card (`channels/popup.py:55,101`) and skips speech (`channels/speak.py:167`); the Wait and Drop actions hold or skip instead. Which severity gets which push level is the option `push_levels` (`const.py:174,180`). So "Sound" appears only when the real push level is `critical` and "Quiet" only when the engine says `quiet`.
6. `preview()` does not predict three channel states, because they arise at send time: popup style `off` for a severity (`popup.py:49-51`), speech without a speaker group or engine, and mail without a notify service or address (`mail.py:126-130`). The table gets these from configuration: `severity_display` styles, `check_speech_engine` and `check_mail_service` (`panel_data.py:304-326`). This is new code, not a reuse of `preview()`.
7. A message with no named target resolves to nobody on push (`hub/resolver.py:383-423`). The table therefore names the target explicitly: the people of the Everyone audience, as decision 3 says. Speech has no audience; it uses the speaker groups (`resolver.py:389`).
8. The digest line ("tagged digest wait for the 20:00 summary") is only true while a Summarize policy for that tag is on. The line is built from the active policies, not written as a constant.
9. The mockup uses its own colors. The panel uses Home Assistant theme variables, as `overview.js` does today.
10. The mail sub-block is new to the tour. Mail is two options: `mail_service`, the name of a notify service (empty means mail is off), and `mail_global_address` (`const.py:232-233`). The service is checked against the notify services that exist (`hub/panel_config.py:138-140`, error `mail_service_unknown`) and the address against 254 characters (`panel_config.py:141-143`). `welcome_apply` takes neither today (`websocket.py:222-229`), but `heads_up/channels_set` already saves and validates both (`websocket.py:402-433`, `check_channels`), and `heads_up/settings_set` saves the engine (`speak_tts_entity`, `hub/settings.py:207`; it checks the form of the ID, not that the entity exists). None of the four default policies sends mail, so the block configures the channel only; mail leaves only when a call or a policy names it.
11. Speakers are not a channel setting. Speech works when a call names a speaker. A speaker choice matters only as the target of the Critical escalation that Create makes (`hub/welcome.py`, `targets.speak.recipients`), so it is chosen in step 4 in the Critical item. No speaker group is needed.

## 3a. Design summary (what the approved mockup shows)

The local mockup is the visual reference; this is the content, so the build does not depend on that file. Sample names in it (Anna, Marc, Lea, Tom, Admins) are invented.

Three states of the page: first launch (no policy yet and welcome not seen), all clear, active alerts.

Page order, all clear or active:
1. Status card. All clear: a green mark, "No warnings or critical notifications active". Active: a red count and one row per unacknowledged critical or warning message with Acknowledge and a path link (a warning row also Snooze). No escalation text in these rows; that is Coming up.
2. Needs attention (problems only, errors first) beside Coming up.
3. Last actions: newest first; a row unfolds its path (created, sent, skipped, acknowledged) from the trace.
4. "What would a message do right now?": rows Banner, Push, Popup, Speech, Persistent, Mail; columns Critical, Warning, Info, Passive. A cell is one word: Sound, Quiet, Shown, Skipped, Not set up (colors red, blue, green, amber, grey; never color only). A count such as "2 of 3" when people differ (decision 3). A click shows one sentence and the reason. Above it one context line (time, quiet hours until, who is away) and the statement that the call chooses channels and recipients. Under it one line that digest messages wait for the summary, only while a Summarize policy for that tag is on.
5. Activity (Phase 19): period switch 24 hours, week, month, year, 2 years; four numbers (notifications with change, delivered, median time to acknowledge, held by quiet hours); a stacked chart by severity.
6. "When your house talks": hours by weekday, hidden for 24 hours with a note to pick a longer period (Phase 19).
7. Top sources (Phase 19).

First launch: the tour on top, then the same cards as empty placeholders with one explanatory line each (Needs attention, Coming up, Activity, Last actions).

Tour, four steps, a progress row with check marks, Back, Next, Skip the tour:
1. Introduction. Title "The right message, to the right people, at the right time", the lead sentence, then three boxes Where, Who, When. Their texts start with the key words: "Channels decide where...", "Audiences decide who gets it...", "Policies decide when...". Foot line says what is saved when.
2. Channels. Six rows with what was found; the two settings of decision 5 in the Mail and Speech rows; nothing else to set.
3. Audiences (not Recipients). Six cards (Everyone, Admins, At home, Not home, Last to leave, First home), each showing who is in it now with a home or away mark; a click flips the card to what the audience means and an example. Then one paragraph about profiles and where to change them. Notes with times ("Left at 17:40") come from the new presence times (decision 8).
4. Policies. One line on what a policy is; three small boxes for the groups Keep it calm, Always gets through, Make sure it arrives with one sentence each; one line that every fitting policy acts and the calmer hold counts; the title "Recommended default policies for you:"; four switches (Critical messages, Warning reminders, Evening summary, Quiet hours), each with its group badge(s) and one or two lines; Critical holds the audience and speaker selects. Create states how many policies it made (Critical makes 3 or 4).

Removed from the earlier mockups on purpose: the test-banner preview in the tour, the mode choice "first or every policy", Tips and "Worth a look", "Active policies" as a list of policies (replaced by Coming up), the three loose selects at the bottom of the Policies step.

UI texts stay short: one sentence per explanation, no long blocks. Claims in cells come from the engine, never from fixed text (section 3, item 5).

## 4. Phase 18: new Overview on data that exists

Blast radius: changes what administrators see on the Overview and in the first-run flow. The notification path is not touched. Backend commands need a Home Assistant restart on the dev instance; the panel needs its version parameter bumped.

Steps, one commit each:

18.1 Status and Coming up (backend)
- Add `status` to `panel_overview`: the unacknowledged active messages of severity critical or warning (decision 7), each with its states.
- Add `coming_up`: escalation and reminder `due` from `message_states`; the next summary time from the planned summary timer row (`engine._arm_summary`, `ledger.timers`); the number of held messages (`ledger.held`, not resolved, not summarized); the number of quiet-held deliveries and their release time (`Delivery.hold == "quiet_hours"`, `due`). Each entry has a kind, a time and a count.
- Tests: extend `tests/hub/test_panel_overview.py`; every new field is covered, including an empty setup.

18.2 Reach table (backend)
- New admin-only command `heads_up/panel_reach`: for each of 6 channels and 4 severities, run the real chain for the Everyone audience (or the speaker groups for speech) and return a state, a count of people, and the reasons per person. The configuration cases of item 6 above come from the existing checks.
- Reuse `preview()`/`plan()`; no second implementation of the rules.
- Tests: quiet hours with each of the three actions, a Get through entry that covers only some people, passive and critical push levels, popup off, no mail service, no speech engine, a person without a device.

18.3 Audience members and presence times (backend)
- Optional `last_to_leave_at` and `first_home_at` in the presence store (`hub/presence.py`); no migration needed because the fields are optional.
- New command that returns the six built-in audiences with their members and reasons in one call (the existing `hub_preview_audience` answers one audience per call), plus the two times.
- Tests: times survive a restart, are empty before the first event, follow the debounce.

18.4 Overview page (frontend)
- Rewrite `overview.js` to the mockup: status card, Needs attention beside Coming up, Last actions with the expandable path (from `panel_trace`), the reach table. The 24-hour chart and its numbers stay as today until Phase 19.
- Strings in en, de, fr, es. The same-keys tests for the Overview and welcome strings (`tests/card/panel.test.js`, `tests/card/welcome.test.js`) cover the new keys; the welcome test that asserts "no mode texts" stays true.
- Pure functions exported and covered by vitest (`tests/card/panel.test.js`).

18.5 Tour in the page (frontend and shell)
- Move the four steps from `welcome.js` into a module the Overview mounts when `welcome_get` says `show`, or on request.
- Shell: remove the modal call in `_build`, `openWelcome`, the resume bar and the `leave` hook; a first opening on another page goes to Overview. Settings > Restart introduction opens the Overview in tour mode.
- Step 2 (Channels) lists the six channels with what was found and what each one needs. Only two settings appear: the mail notify service with an optional global address, in the Mail row; and the speech engine, in the Speech row, as a select when two or more `tts` entities exist and none is chosen, or as the `tts_none` text when none exists (media players need an engine, Assist satellites do not, `hub/channels/speak.py:219-236`). Banner, push, popup and persistent notification show what was found and what to fix outside the integration; they have no select.
- Step 3 is "Audiences" with six flip cards. Step 4 follows the 2.0 wording: the three lanes in one line each, the title "Recommended default policies for you:", four switches with a lane badge each. While Critical is on, its item holds the audience select (default Admins) and, when speakers exist, the speakers for "speak after 10 minutes" (none means no speech). Step 1 keeps Where, Who, When, each text starting with Channels, Audiences, Policies.
- Saving (decision 9): the mail service, the global address and the engine are saved when the user leaves step 2 (Next or Back), and only if they changed. Policies, the audience and the speakers are written by Create in step 4. The intro text "Nothing is created until the last step" becomes: policies are created only in the last step, and the channel settings of step 2 are saved when you leave it. Skip the tour and Not now therefore keep those settings and create no policy.
- Backend for step 2: `welcome_get` also returns the notify services (`panel_config.notify_services`) and the current mail options, so a restarted tour shows what is set. No new command: leaving step 2 calls `heads_up/channels_set` for the mail service and global address and `heads_up/settings_set` for the engine. Both are the commands the Channels and Settings pages use, with their checks; an error stays on step 2. `welcome_apply` and `hub/welcome.py` stay as they are (speakers and audience still go in at Create).
- Tests: a vitest case for what step 2 sends (only changed fields, nothing when untouched); a pytest case that `channels_set` accepts exactly the mail fields the tour sends and refuses an unknown service and an address over 254 characters.
- Tests: `tests/card/welcome.test.js` updated; `tests/hub/test_welcome.py` and `test_welcome_modes.py` stay green.

18.6 Documentation
- `docs/setup.md` (Overview, The introduction), `docs/settings.md` (Introduction row), `README.md` (step 3 and the Overview screenshot), `docs/configuration.md` (the defaults of the introduction), `CHANGELOG.md` `[Unreleased]`, `docs/DESIGN.md` (panel section), `docs/DECISIONS.md`, `docs/dev/STATE.md`.
- A new screenshot of the Overview from the dev instance replaces `docs/images/overview-active.png`, with sample names only.

18.7 Checks
- `make check`, `make hassfest`, `make dev-smoke`; the page opened in the browser pane at desktop and phone width in light and dark theme, all three states (first launch, all clear, active alerts). No real-device claims.

## 5. Phase 19: history

Blast radius: a new store file on disk, and a recording call inside the notification path (`_remember` and `acknowledge`). The recording must never raise into delivery; it is wrapped and logged. No restart is needed for users beyond the update.

19.1 Store
- New store `heads_up.stats`, its own version, loaded at start, saved with the existing delayed-save pattern (`SAVE_DELAY`).
- Always the last 24 months (decision 1): older days are removed once a day and at start.
- Record shape (decision 11): one record per local day with
  - 24 hourly totals of created messages;
  - totals by severity and by tag;
  - outcomes per channel (sent, held, skipped, failed) and the counts of each skip and failure reason code;
  - how messages ended (acknowledged, dismissed, expired, cleared, evicted) and a coarse histogram of the time to end;
  - a coarse histogram of the time to acknowledge, per severity;
  - counts per source, per policy (how often it held, quieted, escalated, reminded, summarized or fell back) and per person (outcomes on push, popup and mail);
  - push levels used, snoozes, and escalations that fired against those acknowledged before they were due.
  Each field is kept only if 19.2 finds a reliable recording hook for it; the trace entry carries the policy as a name (`hub/trace.py`, field `by`), so per-policy counts need the ID looked up at record time. A field without a hook is dropped and listed in the phase summary.
- Size: not measured yet. 19.1 measures a busy synthetic household over 730 days and reports the size before 19.2 starts; a test keeps a record under a stated limit.
- Days follow the Home Assistant time zone, including clock changes.
- A damaged file is ignored and rebuilt empty, as the other stores do (`tests/test_storage_corruption.py`).

19.2 Recording
- One call from `HubEngine._remember` (created, acknowledged, dismissed, skipped, failed, held, expired) and the acknowledge time at `manager.acknowledge`.
- Sources are keyed by rule subentry ID or by the call's source, never by a name, so a rename does not split the history (lesson of `docs/dev/hub/IDENTITY.md`).
- Parity (rule 9): messages from actions and from watch rules are recorded the same way.

19.3 Reading
- New command `heads_up/panel_stats` with a period (24 hours, week, month, year, 24 months) that returns the buckets, the four numbers (notifications, delivered, median acknowledge, held by quiet hours), the weekday-by-hour matrix and the top sources.
- Admin-only; the existing test that every panel command is admin-only must list it.

19.4 Page
- Activity card with the period switch, the matrix and Top sources as in the mockup. No Tips. The last period is labeled "2 years" (decision 10).
- A Clear history button in Settings with a confirmation, and the store size and date range in diagnostics (decision 12). "Delivered" is sent divided by sent plus failed (decision 13).

19.5 Documentation and checks: as 18.6 and 18.7, plus a restart test that counts survive.

## 6. Open points

None. Decisions 1 to 15 settle every point raised while writing this plan. The build of Phase 18 starts only on your explicit go, and Phase 19 on a second one.

## 7. Rules check

- Rule 3 additive: no other integration, automation or script is touched.
- Rule 4: no new Home Assistant API is used; store, websocket and timers follow the patterns already in the code. Unverified: nothing outside this repository.
- Rule 5: stated above per phase.
- Rule 6: sample names only; no household data.
- Rule 7: nothing is pushed.
- Rule 9: parity stated in 19.2.
