# Policy redesign: independent reviewer scores

Reviewer outside the design rounds, 2026-11-18. Read: the designer brief, [00-fact-sheet.md](00-fact-sheet.md), [01-users-and-stories.md](01-users-and-stories.md), the final designs [design-ab-v2.md](design-ab-v2.md), [design-c-v2.md](design-c-v2.md), [design-d-v2.md](design-d-v2.md), [design-e-v2.md](design-e-v2.md), and the mockups [policy-redesign-a.html](../mockups/policy-redesign-a.html) (AB), [policy-redesign-c.html](../mockups/policy-redesign-c.html), [policy-redesign-d.html](../mockups/policy-redesign-d.html), [policy-redesign-e.html](../mockups/policy-redesign-e.html). Claims were checked against `hub/engine.py`, `hub/policies/quiet.py`, `hub/policies/away.py`, `hub/policies/__init__.py`, `hub/welcome.py` and `__init__.py` of 1.0.0. Sample names only.

Scores run from 1 (poor) to 5 (good). For migration risk and build cost, 5 means lowest risk and cheapest.

## Facts used for the checks

- Order in a 1.0.0 setup: `policy_order` is written once at the first load from `initial_order()`. The introduction creates its policies after that load, in the order Critical delivery, Warning reminders, Evening summary, Night quiet (`ITEMS_BY_MODE["first"]` in `welcome.py`), and `ordered()` appends them in creation order. So in a typical 1.0.0 setup the starter policies come first and a later Away sits at the end. Away sits above them when it was created before the introduction or when the user moved it.
- In the starter list, Night quiet and Evening summary only cover info and success. Night quiet has `critical_passes` on and Evening summary has `include_critical` off, but neither flag matters for those severities.
- A Deliver policy's push goes through `_send(..., resume=True)`, and that call skips a channel and recipient that already has a sent or held row. In 1.0.0 the earlier delivery wins, so the first delivery from the call wins over a Deliver push to the same person.
- Quiet hours: one window per policy (`from_time`, `to_time`, `days`), and `days` names the day a window starts on. A repeat is skipped only by the action "wait". With the action "quiet", a repeat goes out quietly.
- Away does not check repeats (`step.origin == "reminder"` passes).

## Design AB: two lanes, one band, promises on every card

- Learnability: 3. Anna can repeat the two lanes ("calm" and "make sure it arrives"). But the band, the per-person "Covers", the promise lines and the converted links make up a five-part model, and the design's own one-sentence model needs four clauses.
- Predictability: 4. The checker answers per recipient and channel, the form shows the sentence, the promise line and "Where it overlaps" before Save, and scenario 12 comes out right ("the calmer counts: info waits until 10:00"). The promise lines come from a dry run over a grid, and the design calls them its biggest risk. A wrong line would mislead exactly where users look.
- Scenario coverage: 4. Scenarios 1 to 12 are all answered. In scenario 1 only the Admins ring, because the entry acts per person on the call's own delivery too, so the 1.0.0 deduplication does no harm. Scenario 5 gives repeats at 15, 30 and 45 with one count, or with two counts when written as two policies. In scenario 8 the household fallback speaks a night leak only if the entry covers the speaker, and the design says so. Scenario 9 escalates at 07:30. In scenario 11, the "Away above" position has a gap (see Errors).
- Conflict clarity: 5. Strength sits only in the "Always gets through" band, and each entry is a policy with its own switch. "Holds these anyway" is listed in the same band, and Presence is never passed, which is one plain rule.
- Migration risk: 3. Nothing changes at upgrade, `policy_order` and `policy_mode` are kept, and "Restore 1.0 links" is the way back. But the live links, the new "Critical" entry, the "Not for critical" rewrite and "Holds these anyway" all have to reproduce "only the first" exactly, in both positions of Away, and the worked text gets one of them wrong.
- Build cost: 2. The engine parts are fine (the chain already lets the calmest hold count, and it rechecks released deliveries). Three parts are each L: the promise line grid over severity × tag × 168 hours, the new `get_through` subentry with a check per recipient in two stages, and the panel. Per-channel rhythm plus per-reminder counts is M.
- Parity, accessibility, translation, phone width: 3. The mockup works at 380 px (max 420), has dark mode by system and by toggle, and gives aria labels on switches and selects. Lane meaning is carried by text headings and glyphs, not colour alone. Two concerns. The strings "Bent for … by …" and "Not for messages that … takes, while it is on" are built from fragments, which is hard to order in German and French. And the watch-rule parity gap is not handled: a warning leak from a watch rule carries only the tag `rule`, so "Alarms wake Admins" (tag `alarm`) cannot reach it.

## Design C: plans and house rules

- Learnability: 4. "A plan is the journey of one kind of message; house rules are the house's limits" is two sentences Anna can repeat. "Lets through" with two reaches ("only what this plan sends" or "every delivery") is the part she will need explained.
- Predictability: 4. "In words", "Also acting on these messages" and "Let through by" all show before Save, and scenario 12 is stated with the stricter action. The shared repeat count ("ends at the highest At most among the steps that fit at that moment") is exact but hard to foresee when Only if conditions flip.
- Scenario coverage: 3. Scenario 1 is answered wrongly as written (see Errors): under today's deduplication the Admins get the call's quiet push, not a ringing one. Scenario 2 puts two windows into one house rule, which is a new stored shape. Scenario 8 needs the fallback step copied into each plan that should speak at night, which is a workaround. Scenarios 5 and 9 are correct, and 3, 4, 6, 7, 10 and 12 are fine.
- Conflict clarity: 4. "Can wake people" lists every "Lets through" in one block, and each house rule shows "Let through by". The strength is still set on each plan form, so there are as many places to set it as there are plans.
- Migration risk: 3. One subentry stays one subentry, a one-step plan keeps its type key, the links are live, and "Own rhythm (1.0.0)" protects 1.0.0 "all" setups. The new plan "Critical messages pass (1.0.0)" reproduces the per-hold flags. Only the `initial_order` position of Away is walked. The general rule ("links to earlier overlapping policies") covers the welcome order, but the stated outcome ("Warning reminder and Critical delivery never act") is true only for the position that was walked.
- Build cost: 2. New parts: the plan type with steps and stable step IDs, a timer key change, cross-plan deduplication that must now prefer the delivery that passes, Lets through in three stages, the converter, and an L panel with a repeatable step list. The design names the step list in ha-form style without a build step as unverified.
- Parity, accessibility, translation, phone width: 3. The mockup is fine at 380 px and in dark mode. Switches use `role="switch"` with an On or Off text, and badges are text. Fragment labels such as "If nobody reacts within …" with an inline field are the translation risk C itself raised against B. Watch-rule parity has the same tag `rule` gap as AB.

## Design D: message types

- Learnability: 5. "Every message is of one type, and that type alone decides" is the clearest model of the four, and the type cards read like a household's own categories. The split of quiet behaviour into "What the call sends" and "What this type adds" is the one place where Anna needs help.
- Predictability: 4. Try a message names the type and the reason ("tagged leak", "from watch rule Leak sensor"), and nothing combines. Two things can surprise: the hidden handoff "When switched off", and the deduplication gap in scenario 1. Scenario 12 is reframed as moving a claim, not as an overlap of two policies of one type. The Move box makes that move visible before Save.
- Scenario coverage: 3. Scenario 1 has the same deduplication gap as C: the Admins' "Also send" push is skipped when the call already pushed them quietly, and the design does not mention it. Scenario 6 needs `type: shopping` in the call, which is a YAML change for an existing automation. A tag claim would avoid that. Scenario 8 sets the fallback once per type. Scenarios 5, 9, 10 and 11 are correct, and scenario 10 is the best answer of the four.
- Conflict clarity: 4. "Can wake people" and the Quiet times card (every type with its choice, editable in place) put strength in one visible place. Claims are owned once, so two types never compete. The Move box guards the moment a claim changes owner.
- Migration risk: 2. The cell method recomputes 1.0.0 into a different model: severity × each named tag or watch rule, with `critical_passes` folded in, merged by equal sets. It walks both positions of Away correctly. But one "When switched off" target per type cannot always express a chain that differs by cell (see Errors). "All" setups turn into joined types, and one 1.0.0 switch can then control sections in several types.
- Build cost: 2. Many items are S, but there are new `message_type` subentries, house-wide quiet times, claims and the Move box, type choice stored on the message, handoff, the cell migration with fixtures for both orders, and an L panel. The design rates the total L.
- Parity, accessibility, translation, phone width: 4. The watch-rule claim through the `rule_` ID prefix (checked in `const.py` and `panel_data.py`) is the only answer that gives a warning watch rule its own behaviour without touching frozen rules (D-100). Badges pair a glyph with text. The mockup is fine at 380 px and in dark mode. The mockup label "Skip this while a condition is true" contradicts the design's "Only while" and the decided name "Only if" (D-216). That is a wording risk across four languages.

## Design E: keep the list

- Learnability: 4. "Each kind has its own place, the highest of that kind that fits counts, kinds never block each other, and a hold beats a send" is short. Anna still has to understand "higher counts" inside a type.
- Predictability: 4. The overlap sentence names the winner and how to change it ("Move it below Night quiet"), and it changes live. Across types the one fixed rule (holds win) is easy to foresee. Order-dependent starving (a wide policy above a narrow one) is caught only by that sentence.
- Scenario coverage: 3. In scenario 1 the leak wakes Anna too, because a hold acts on the whole message. Scenario 8 for a night leak needs "Not for tags leak" on each hold. Scenario 5 works only if Urgent is placed above Hourly. One Escalation and one Deliver per message drops escalation tiers. Scenarios 2, 3, 4, 6, 7, 9, 10 and 12 are fine, and scenario 11 is trivially exact. Users who never press Switch keep pain points 2 and 3.
- Conflict clarity: 2. Strength is spread over the order inside each type, "Not for tags" on each hold and "Critical messages pass" on each hold. The computed "Let through at night" line shows it, but it is not one place to set it. A new hold does not inherit an exemption. The Copy hint only suggests it.
- Migration risk: 5. There is no data change at upgrade, existing modes are kept, the switch comes with a "What changes" preview and "Keep as before" per line, and setting the mode back is an exact way back because the list is never reordered across types. Both positions of Away are handled, because nothing moves until the user switches.
- Build cost: 4. Changes to `select()` per type, `exclude_tags`, `not_with`, Count from, the What changes function and grouping in the existing drag list are each S or M. The D-216 listeners that re-choose a reminder are needed by every design.
- Parity, accessibility, translation, phone width: 4. Move up and Move down are buttons with labels such as "Move Weekend lie-in up within Quiet hours" and a live status line. Switches use `role="switch"`. Labels are short and keep the 1.0.0 words, so the existing translations stay valid. Watch-rule parity has the same tag `rule` gap as AB and C.

## The three cases where the designs disagree most

1. A leak sent as a warning at 03:00 by an automation whose push goes to the whole household, the Admins included, with Night quiet on all severities.
   - AB: the Admins ring and Anna gets a quiet push, because "Alarms wake Admins" covers the Admins on any delivery, the call's own included.
   - C: the design says each Admin gets one push and it rings. Under today's deduplication, the call's quiet push is sent first and the plan's ringing push is skipped. The Admins ring only if the plan's reach is "every delivery", and then Anna rings too.
   - D: the same as C. The Alarm type's "What this type adds: Send as usual" never gets to act for a person the call already pushed to quietly.
   - E: everyone rings. A hold acts per message, and the leak is taken out of Night quiet by "Not for tags leak". The design states this openly.
2. A critical message when nobody is home, with a Presence policy that speaks only when somebody is home and covers all messages.
   - AB: not spoken. Presence is never passed, unless that Presence policy says "Not for critical".
   - C: spoken. The plan "Critical messages" lets through all presence rules, also later ones, for every delivery.
   - D: whatever the Alarm type's own Presence section says. A house-wide presence rule does not exist, so with no section the critical message is spoken.
   - E: spoken. "Critical messages pass" is on by default on the Presence policy (D-211 kept).
3. Scenario 5 written as two reminders, "Urgent" (15 min, at most 8, Only if X) and "Hourly" (60 min, at most 3), with X switching on and off several times.
   - AB: one rhythm per channel. Each reminder counts its own repeats, so up to 11 in all, and Hourly keeps its 3 after Urgent ends.
   - C: one shared rhythm and one shared count. It ends at the highest "At most" in force, so at most 8 in all.
   - D: written as one Repeat section with "Faster while", one count and one limit. Two converted 1.0.0 reminders run side by side until merged.
   - E: each reminder counts its own repeats (up to 11), but only if Urgent is above Hourly. With Hourly above, Urgent never acts.

## Errors found

- C, scenario 1 and the first answer to the reviews: C says one push per person "is already the 1.0.0 rule for Deliver" and that the Admins' single push rings. The rule exists (`_apply_deliver` sends with `resume=True`, which skips a row already sent), but it keeps the earlier delivery. The call's quiet push wins and the ringing push is dropped. Making "it rings" true needs new merge logic that prefers the delivery that passes a hold, and that logic is not costed.
- C, scenario 2 and the mockup: one house rule with two windows. A 1.0.0 Quiet hours policy stores one window (`quiet.py`), so this is a change to the stored shape. Sections 6 and 7 do not name it.
- C, scenario 11: the outcome is told only for the `initial_order` position (Summarize, Quiet hours, Away, Reminder, Deliver). The usual 1.0.0 order puts the starter policies first and Away last, and then Away is the policy that never acts, not the reminder and Critical delivery.
- AB, section 6: two steps clash. Presence with `critical_passes` gets "Not for critical", and links are written to the policies above "whose For can overlap". With Away stored above the starter policies, Critical delivery's For no longer overlaps Presence after that rewrite, so it gets no link and starts pushing. In 1.0.0, Away took critical messages and Critical delivery stayed silent. The links must be computed from the 1.0.0 For, before the rewrite. The same section also names only Warning reminder and Critical delivery for "Away stored higher". When Away was created before the introduction, Evening summary and Night quiet get links too.
- AB mockup: the Warnings reminder card and the checker say a night repeat is skipped by Night quiet. In the mockup Night quiet sends quietly, and in 1.0.0 only the action "wait" skips a repeat, so the repeat goes out quietly.
- D, scenario 1 and scenario 4: the deduplication gap described under C applies to "Also send" too, and the design does not mention it.
- D, section 6: "When switched off" holds one target per type. A type reached from several cells can then hand a message on to a type whose sections acted only on other severities in 1.0.0. One example: an info message handed from Night quiet to the Away type, and then, with Away off, to the Warning reminder type. The handoff needs to be stored per cell, or the design needs to show that one hop is always enough.
- D: `critical_passes` is dropped as a field without naming D-211 as reversed. AB and C both ask for a maintainer decision.
- E: no factual error found. The claim that Summarize today picks "the first by name" checks out (`_summary_policy` uses `min(..., key=name)`).

## Recommendation

Build AB's model, but convert in E's way, and add D's watch-rule claim.

- The model: two lanes, the per-person "Always gets through" band as the one place for strength, "Presence is never passed", "Not for", per-reminder counts with "Faster while", and clocks from first reach. It is the only design that answers scenario 1 the way Chris asks (Admins ring, Anna sleeps) under today's deduplication, and it scores best on conflict clarity.
- The conversion, taken from E: at upgrade a 1.0.0 setup keeps `policy_mode` as it is and behaves exactly as before. The page offers "Switch to the new layout" with a What changes preview computed from today's switch states. Each line offers "Keep as before" (a live link computed from the 1.0.0 For, before any "Not for critical" rewrite) or "Let it act". Setting the mode back is the way back. This brings AB's migration risk close to E's and makes the check list optional.
- For parity (rule 9), taken from D: let "Which messages" match "From watch rule …" through the `rule_` ID prefix. A warning leak rule can then reach the band and a Deliver policy without touching frozen rules.
- To lower AB's cost and its biggest risk: ship the checker and the message history first. Add promise lines later, in their short form only, once the dry run has a test per scenario.
- Decisions this needs from the maintainer: whether "Gets through" replaces D-211's per-hold "Critical messages pass", and whether new setups start in the new layout.
