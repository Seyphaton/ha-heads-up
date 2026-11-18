# Policy redesign: fact sheet

Design session 2026-11-18 on `release/1.1`. Read from `docs/DESIGN.md` §22 and §23, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md` ("1.1.0 design") and the code of 1.0.0 (`hub/policies/`, `hub/engine.py`, `frontend/panel/policies.js`). Sample names only.

## What a policy is today
- One small typed rule (D-097): name, type, enabled, "Which messages" (severities and tags, empty means all; no exclusion), "What it does". Stored as a config subentry (D-119); each policy has a switch entity, and a call names a policy by that entity ID (D-198).
- Attachment (D-146, D-187): `apply: auto` matches by severity and tag; `apply: manual` runs only when named. A `notify` call adds named policies to the automatic ones (`match_policies_automatically`, D-189); a watch rule's named policy replaces them (D-145). `none` means no policy.
- Watch rules are frozen (D-100): banner only, tag `rule`; policies reach them by severity and tag (parity, rule 9, §22).

## The seven types
Hold back or change a delivery:
- Summarize: holds a message on every channel, the banner too (D-105), and sends one summary per recipient and channel every N minutes or at a time of day. Critical only with `include_critical`. The summary takes the highest severity and passes the chain again (D-106).
- Quiet hours: in a window (from, to, days) a delivery waits until the end, goes quietly (passive push, no speech, popup as card) or is dropped. `critical_passes` (default on). A reminder in a "wait" window is skipped, not held. Several windows: strictest action wins (drop, wait, quiet).
- Away (becomes Presence in 1.1.0, D-212, D-214): a person known not home is sent the delivery on arrival; optional maximum wait. Audience targets on push, popup, mail; unknown presence sends at once; `critical_passes`. Never the banner.

Send more:
- Deliver: at once, also deliver on its channels to its recipients (D-121); gives a watch-rule message a push or speech.
- Escalation: nobody acknowledged within N minutes, deliver on its channels to its recipients; dismissal may count as acknowledgement; fires at most once per policy.
- Reminder: while unacknowledged, repeat every N minutes, at most M times, optionally on some channels; repeats only the deliveries already sent.
- Fallback: the audience was empty, sending failed, or both; deliver elsewhere; fires once; never triggered by an escalation, reminder or other fallback.
- Escalation, Deliver and Fallback may take channels or recipients from the call (D-181).

## The delivery chain
Every delivery (first, Deliver, escalation, reminder, fallback, summary) passes a fixed chain: Summarize, Quiet hours, Away, Fallback (D-106, `chain.py`). Each stage passes, changes, holds (`Hold` with release time or deadline) or skips. A stage only looks at the policies returned by `PolicyBook.for_message`.

## The two modes (D-148, D-152)
- "Only the first" (`policy_mode: first`, default for new and existing setups, D-149): `for_message` returns only the first enabled automatic policy in list order that matches. One place per message, shared by all seven types. A named policy still runs.
- "All that apply" (`all`): every matching policy runs; order does not matter; overlaps are not designed (D-149).
- The order is a drag-and-drop list with Move up and Move down; stored as `policy_order` (subentry IDs). Starting order: Summarize, Quiet hours, Away, Escalation, Reminder, Fallback, Deliver.
- The introduction offers, under "only the first": Critical delivery (critical), Warning reminder (warning, 30 min, 3 times), Evening summary (info and success, tag `digest`, 20:00), Night quiet (info and success, 22:00 to 07:00, quietly) (D-150). Only the order keeps Night quiet away from digest messages.

## Engine facts cheap to reuse
- Timer rows per message and policy in the ledger (channel `timer`); planned once when the message appears (`_arm`); `_drop_inapplicable_timers` cancels rows whose policy no longer applies; an overdue step fires once after a restart; a severity change restarts timers.
- Held deliveries are ledger rows (state `held`, kind `quiet_hours` or `away`, `due`), released at the window end, on arrival (person state listener) or at the deadline; restored after a restart.
- Summarize decides the hold once, when the message appears; a held message starts no timers and no Deliver.
- The editor's "In words" line builds one sentence per policy from its fields; the page lists overlaps as a note and never blocks (D-151).

## Decided for 1.1.0 (design, staged, D-207 to D-216)
- D-207 scope: speech that fits the house, "only if", snooze polish, custom severities step 1.
- D-208, D-215: speech volume by time band and severity, restore on by default.
- D-209: guests through "only if" on the policy, not a presence field.
- D-210: modes get their own design session (this one).
- D-211: "Critical messages pass" sits in Which messages on every hold-back policy.
- D-212, D-214: Presence replaces Away (channels covered; zone; recipient in or not in for push, popup, mail; nobody or somebody of an audience for speech; hold until it changes or drop; maximum wait then send or drop). Stored key `presence`, `away` still read.
- D-213: every 1.0.0 setup converts without a breaking change; every behaviour change needs a way back and a CHANGELOG line.
- D-216: "only if" uses the `notify` condition shape; checked whenever the policy would act; a held delivery is released when its policy's condition turns false; unknown means "whatever delivers more".

## Known pain points
1. Hold-back and sending policies look alike in one list.
2. Under "only the first" one place is shared by all types (Critical delivery blocks a critical reminder; a speech Presence policy switches off Night quiet, D-210).
3. The order means "more specific" and "stronger" at once.
4. "Only if" checked at every step can change the chosen policy mid-life (15 min only if X versus 1 h).
5. Holds against sends: escalation held until morning; household fallback held by Presence; escalations fire for a message nobody has seen because it is held.
6. Severity `critical` is the only way through a hold.
7. Tags cannot be excluded; the order is the workaround.

## Constraints
- Panel without a build step, own `ha-form`-style forms, admin only, storage in config subentries (D-119) unless argued.
- English, German, French, Spanish at similar length; no jargon (filter, generator, precedence).
- Keyboard and touch for ordering, screen-reader labels, no meaning by colour only; every page at about 380 px.
- Policy switch entity IDs keep working in calls (D-198). Watch rules frozen, policies by severity and tag.
