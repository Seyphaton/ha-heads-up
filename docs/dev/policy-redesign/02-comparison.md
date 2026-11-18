# Policy redesign: comparison and recommendation

Design session 2026-11-18 on `release/1.1`. Design only; nothing is decided until the maintainer chooses. Sample names only.

## How the designs were made
- Inputs: [00-fact-sheet.md](00-fact-sheet.md), [01-users-and-stories.md](01-users-and-stories.md).
- Round 1: four independent designers. A "Two lanes", B "Goals, not policies", C "Clean slate" (no earlier positions given), D "Message types". Files `design-<letter>-v1.md`.
- Round 2: each designer red-teamed the other three (`review-by-<letter>.md`) and wrote a v2 (`design-<letter>-v2.md`).
- Distinctness check: A v2 and B v2 had the same model (goals had become one typed policy each, shown as a sentence; B's "Gets through" goal had become A's band entry; both used "every policy that fits acts, the calmest wins"). They were merged into [design-ab-v2.md](design-ab-v2.md). B's designer then worked out the strongest alternative every design had rejected, the smallest step from today's model: [design-e-v2.md](design-e-v2.md) "Keep the list".
- Four distinct designs remain: AB, [C](design-c-v2.md), [D](design-d-v2.md), E. A reviewer who saw none of the rounds scored them: [03-reviewer-scores.md](03-reviewer-scores.md).
- Mockups: [AB](../mockups/policy-redesign-a.html), [C](../mockups/policy-redesign-c.html), [D](../mockups/policy-redesign-d.html), [E](../mockups/policy-redesign-e.html). The B v1/v2 mockup ([policy-redesign-b.html](../mockups/policy-redesign-b.html)) is kept for its sentence layout in German.

Decided in a parallel session on the same day, after the designs were written: Quiet hours can take their window from a schedule helper or any on/off entity (D-218, D-220), so scenario 2 can be one Quiet hours policy with one schedule in every design, without a new stored shape; the four severities stay (D-222). None of the designs conflicts with these; C's "two windows in one house rule" becomes unnecessary.

Scores run 1 to 5; for migration risk and cost, 5 is lowest risk and cheapest.

## Design AB: two lanes, one band
- Model: calming policies decide when a message may reach people; sending policies decide who else gets it and how often; the "Always gets through" list says which messages may wake whom anyway; every card says whether it gets its way.
- Page: lane "Keep it calm" (Summarize, Quiet hours, Presence), the band, lane "Make sure it arrives" (Deliver, Escalation, Reminder, Fallback), "Only when named", a checker "What happens to a message?". No order, no mode.
- Conflict rules: every policy that fits acts; the calmest hold counts (summary, drop, wait, quiet); a band entry passes Quiet hours and Summarize for the people it covers; Presence is never passed; clocks start once the message reached someone; one repeat rhythm per channel, each reminder keeps its own count.
- Strengths:
  - The only design where scenario 1 comes out as Chris wants under today's engine: the Admins ring and Anna's push stays quiet, because a band entry acts per person on the call's own delivery too.
  - One place for strength, each entry a switch an automation can turn off; "Not for" ends the order workaround for tags.
  - Keeps the seven 1.0 type names, so entity names, docs and translations stay.
- Weaknesses:
  - A five-part model (lanes, band, covers, promise lines, converted links); Anna needs more than one look.
  - Promise lines ("Kept", "Bent for … by …") need a dry run over severity × tag × week; wrong or long lines break trust and phone width, and fragment strings are hard in German and French.
  - Its own migration text has an error: computing links after the "Not for critical" rewrite lets Critical delivery act where 1.0.0 kept it silent (Away stored above the starter list).
  - Replaces D-211 ("Critical messages pass" on each hold) by the band.
- Scores: learnability 3, predictability 4, scenario coverage 4, conflict clarity 5, migration risk 3, cost 2, parity/accessibility/translation/phone 3.

## Design C: plans and house rules
- Model: each plan is the journey of one kind of message (at once, if nobody reacts, repeat, if nobody could be reached); house rules (quiet times, presence, summary) are the house's limits; a plan says which house rules it may pass.
- Conflict rules: plans add their steps, one delivery per person and channel, repeats share the shortest rhythm and one count; house rules hold with the strictest winning; a delivery passes a house rule only when a fitting plan lets it through; clocks count from first reach.
- Strengths:
  - A plan reads like the story of a message; Anna can say it in two sentences.
  - Holds are written once for the house; a fallback or quiet window is not repeated per message kind.
  - "Can wake people" lists every pass in one block; each house rule shows "Let through by".
- Weaknesses:
  - Scenario 1 is answered wrongly: today a Deliver push to a person who already has the call's push is skipped (`_apply_deliver`, `resume=True`), so the quiet push wins. Making the plan's push ring needs new merge logic that is not costed; the reach "every delivery" wakes Anna too.
  - Strength is set on each plan form, so there are as many places as plans.
  - Two windows in one house rule change the stored shape; a repeatable step list in the ha-form style is not verified; no downgrade once a plan has several steps.
  - Reverses D-211.
- Scores: learnability 4, predictability 4, scenario coverage 3, conflict clarity 4, migration risk 3, cost 2, parity/accessibility/translation/phone 3.

## Design D: message types
- Model: every message is of one type (Alarm, Doorbell, Digest), and that type alone decides who gets it, how, at night, and what happens if nobody reacts.
- Assignment: the call's new `type` field, else the watch rule (claimed by the `rule_` ID prefix), else the tag, else the severity; stored on the message at creation and on a severity change. House quiet times are clock windows only; each type picks wait, quietly, drop or "Send as usual" per window.
- Strengths:
  - The clearest model of the four; nothing combines, so pain points 2, 3 and 4 disappear by construction.
  - The best answer to watch-rule parity: a type claims a rule by its ID prefix, the frozen rule is untouched.
  - The Move box warns before a tag claim moves away from the Alarm type.
- Weaknesses:
  - Shared behaviour is copied per type: a household fallback set once per type; "everything except digest" needs a Digest type.
  - Migration recomputes 1.0.0 into a different model (severity × tag cells merged into types, a "When switched off" handoff); the handoff with one target per type is not always exact; "all" setups produce joined type names.
  - Scenario 1 has the same deduplication gap as C; scenario 6 needs `type` in the call.
  - Severity loses its power to pass; D-211 is dropped without being named.
- Scores: learnability 5, predictability 4, scenario coverage 3, conflict clarity 4, migration risk 2, cost 2, parity/accessibility/translation/phone 4.

## Design E: keep the list
- Model: each kind of policy has its own place; the highest one of that kind in the list that fits at that moment acts; kinds never block each other; a hold always beats a send.
- Migration: none beyond Away to Presence. Existing setups keep "Only the first" or "All that apply"; new setups start on "One of each type". Switching shows a "What changes" list with "Keep as before" per line; switching back is the way back.
- Strengths:
  - Lowest cost (M) and lowest migration risk; the page and words users know stay.
  - Fixes the shared single place (pain point 2) and gives "only if" a defined meaning within a type (scenario 5).
  - No factual error found by the reviewer.
- Weaknesses:
  - Strength is spread: order within each type, "Not for tags" and "Critical messages pass" on each hold. A new quiet hour without "Not for tags leak" holds leaks.
  - Scenario 1 wakes the whole household; scenario 8 at night needs an exemption on each hold; scenario 5 depends on which reminder is higher.
  - One escalation and one Deliver per message: escalation tiers are lost in the new rule.
  - Setups that never switch keep pain points 2 and 3.
- Scores: learnability 4, predictability 4, scenario coverage 3, conflict clarity 2, migration risk 5, cost 4, parity/accessibility/translation/phone 4.

## Where the designs disagree most
- A night leak whose push goes to the whole household: AB wakes only the Admins; C and D intend that but lose the ringing push to today's deduplication unless new merge logic is built; E wakes everyone.
- A critical message, nobody home, a "speak only when somebody is home" rule: AB stays silent (Presence is never passed); C and E speak it; D depends on the type's own Presence section.
- Scenario 5 as two reminders (15 min at most 8 only if X, 60 min at most 3): AB up to 11 repeats, each reminder its own count; C at most 8, one shared count; D writes it as one Repeat with "Faster while"; E up to 11, but only if the 15-minute reminder is higher in the list.
- Where strength lives: one band (AB), each plan (C), each type (D), each hold plus the order (E).
- Migration shape: AB and C convert in place with live 1.0.0 links; D rebuilds into types; E changes nothing until the user switches.

## Recommendation
Take AB's model forward, convert the way E does, and add D's watch-rule claim.

- Why AB: it is the only design that keeps nights quiet for everyone except the people who must act (scenario 1, Chris's story) with today's engine, and the only one with a single visible place for strength (Q3, Q4). Its two lanes answer pain point 1 directly, and "Presence is never passed" is one plain rule.
- Why E's conversion: AB's in-place links are where its migration error sits. Keeping the 1.0.0 mode at upgrade and offering "Switch to the new layout" with a "What changes" preview (links computed from the 1.0.0 "Which messages", before any rewrite) brings AB's migration risk close to E's and makes D-213 easy to prove. Setting the mode back is the way back.
- Why D's claim: "From watch rule …" in "Which messages", by the `rule_` ID prefix, gives watch-rule messages the band and a Deliver policy without touching frozen rules (rule 9, D-100).
- To lower AB's cost and its biggest risk: ship the checker and the message history first; promise lines later, short form only, with a test per scenario.
- Decisions this needs: whether the band replaces D-211's per-hold "Critical messages pass"; whether new setups start in the new layout; whether the 1.0.0 modes stay offered to new setups.
- Runner-up: E, if the maintainer wants the smallest 1.1.0 and accepts that strength stays spread over the holds.
