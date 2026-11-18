# Red-team review by Designer D (round 2)

Reviewed: design A (two lanes), B (goals), C (clean slate), all v1. Checked against [00-fact-sheet.md](00-fact-sheet.md), [01-users-and-stories.md](01-users-and-stories.md) and the 1.0.0 code (`hub/policies/__init__.py`, `matching.py`, `fallback.py`). Sample names only.

One code fact matters for all four designs, mine included: `PolicyBook.ordered()` uses the stored `policy_order` and appends every policy created after it at the end; the starting order (Summarize, Quiet hours, Away, Escalation, Reminder, Fallback, Deliver) is written once at setup (`__init__.py`, `initial_order`). So in scenario 11 the Away policy sits either before the reminder and Critical delivery (created with the starter list) or at the end (added later). Every conversion must handle both positions; a design that shows only one has not answered scenario 11.

## Design A: two lanes

### Failures
1. The band is too coarse: it decides by message, for every person and every hold (scenario 1, scenario 3, scenario 6). Chris adds the tag `alarm` to "Always gets through" so the leak wakes the Admins. By rule 3 the whole message skips every hold: the push the automation sends to the household also rings Anna's phone at 03:00, and any Presence rule on an `alarm` message (for example "speak only when someone is home") is skipped too, so the kitchen speaker talks into an empty house. A's own section 8 lists "sends that pass some holds but not others" as given up; S1 asks for the Admins to be woken, not everybody.
2. The "first" conversion is a snapshot of switch states (scenario 11, D-213). The conversion writes "its For minus the For of every enabled automatic policy above it". In 1.0.0 "only the first" skips a disabled policy at the time of each message, and policy switches are entities that automations toggle (D-198). If Ben's automation has Evening summary switched off at the moment of the upgrade, Night quiet gets no "Not for tag digest"; when the summary is switched on again in the evening, digest messages are now summarized and quieted, which 1.0.0 never did. Static exclusions cannot reproduce a dynamic order.
3. Reminder resolution hides a limit trap (scenario 5, Q3). "Urgent" (15 min, at most 8) and "Hourly" (60 min, at most 3) share one count. After four fast repeats X turns off; "Hourly" now counts and its limit of 3 is already passed, so the repeats stop without any notice. Ben sees "at most 3" on Hourly and expects three hourly repeats. The rule "the one that repeats more often counts" also sits in a lane header line, not in either form, so the answer to Q3 for reminders is not where Ben edits.

### Worth stealing
The "Check after the update" list with "Keep as before" and "Let it act" per item: it turns the migration's odd results into a short to-do list instead of leaving them in the forms.

## Design B: goals

### Failures
1. One wish needs edits in two goals (Q4, scenario 8, scenario 9). "Gets through" passes calm goals only "for the people it names". Chris's fallback "Household speakers say it" and his pass-on "tell Ben" are held by Night quiet for a leak unless he also adds Household speakers and Ben to the "who" of the leak's Gets through goal. B's own scenario 8 text says so. The wish "leaks may wake people" lives in one goal, but who may be woken has to be kept in step with every sending goal by hand; a new pass-on target added later is silently held at night.
2. One shared rhythm across all repeat goals (scenario 5, Q3). Rule 1 gives the message "the shortest rhythm that fits at that moment" across every Repeat goal, with "own rhythm" as an opt-out. A wide goal "Repeat warnings every 5 minutes" added by another admin overrides Ben's tag-specific hourly rhythm for every warning, and nothing on Ben's goal card shows it. And with "each rhythm has its own limit", Ben's example (1 h at most 6, 15 min at most 12) stops all repeats when X turns off after the seventh fast repeat, because the count already exceeds 6.
3. Sentence forms do not survive four languages at 380 px (constraint, persona Anna). The Pass on template in German reads roughly "Wenn niemand innerhalb von [30 Minuten] auf [Warnungen] reagiert, nachdem sie jemanden erreicht hat, [Admins] über [Push] benachrichtigen": five inline buttons that wrap into a ragged block on a phone, with the blanks in a different order than the fields below. B's fallback (fields in fixed order below the sentence) means Anna edits in the fields anyway, so the sentence is a second rendering of the same form, not the form.

### Worth stealing
The per-message timeline in the message history, filled from the ledger ("Held until 07:00 by Night quiet; Leak would have let it through, but it is off"). It answers Q2 after the fact, where the page preview only answers Q1.

## Design C: clean slate

### Failures
1. Plans add up, so pain points 2 and 4 come back across plans (scenario 5, scenario 12, S4). C solves scenario 5 inside one step, but a 1.0.0 setup in mode "all" with two Reminder policies converts to two one-step plans, and two plans that fit both run: Ben gets the 15-minute and the 60-minute rhythm together. C's own scenario 12 answer says "they get both repeat rhythms". A "Leaks" plan and a "Critical" plan both fit a critical leak and both push the Admins at once. Nothing on the page prevents or merges this; the only defence is a sentence before Save.
2. Two ways through a hold, in two places (pain point 6, Q3). A step can carry "Passes quiet times", and every house rule also carries "Critical messages pass", on by default. Chris asking "why did the leak ring at 03:00?" must check the plan's step marks and every house rule's critical box. And the mark passes a whole kind: "Passes presence rules" on the safety-net fallback (scenario 8) also passes the shopping-list Presence rule and the doorbell rule, which were never meant for it.
3. Multi-step plans break running timers and the way back (D-213, D-197). Timer rows become "policy key plus step index". Deleting the first step of a running plan shifts the index of the repeat step: its row is either dropped by `_drop_inapplicable_timers` or matched to the wrong step. C also gives up downgrade once any plan has more than one step, so the first use of the new model removes the way back that D-213 asks for.

### Worth stealing
The "Can wake people" block near the top of the page: one line per thing that passes quiet times, so a change made by someone else is visible in one look (Chris's fear).
