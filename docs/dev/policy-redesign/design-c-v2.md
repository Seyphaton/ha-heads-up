# Policy redesign, design C (clean slate), version 2

Designer C, round two. v1: [design-c-v1.md](design-c-v1.md). Reviews read: [review-by-a.md](review-by-a.md), [review-by-b.md](review-by-b.md), [review-by-d.md](review-by-d.md); none missing. Mockup, updated in place: [policy-redesign-c.html](../mockups/policy-redesign-c.html). Sample names only.

What stays distinct about C: a plan is the whole journey of one kind of message (what goes out at once, what follows, where it goes if nobody is reached, and which house rules it may pass), and house rules are written once for the whole house. v2 moves strength from single steps to the plan, names the house rules it passes one by one, and removes the second way through ("Critical messages pass").

## Answers to the reviews

- Plans add up: two plans double the first push and two reminder plans give two rhythms (A2, B1, D1). Fixed. Each person gets one delivery per channel at a time across all plans and the call itself. This is already the 1.0.0 rule for Deliver (`_apply_deliver` leaves out a recipient that already has the message on that channel), now applied across all plans. Repeat steps from several plans that act on one channel share one rhythm: the shortest one in force sets the next repeat, and the count is shared. Ben's scenario 5 written as two plans now behaves exactly like the one-step "Faster while". Only converted 1.0.0 "all" setups keep side-by-side reminders, through a visible step option "Own rhythm (1.0.0)".
- Two ways through a hold, and one is not shown (A3, B2, D2). Fixed. "Critical messages pass" leaves the house rule form. The only way through a house rule is a plan's "Lets through" field, and the house rule form shows it read-only as "Let through by: Critical messages, Leaks (its own sends)". The "Can wake people" block lists every plan that lets something through. This departs from D-211, so it needs a new decision (section 8).
- "Passes presence rules" passes every presence rule, including the shopping list and doorbell rules (D2). Fixed. "Lets through" names house rules one by one. Optionally it also covers "all quiet times, also ones added later", per kind.
- The call's own first delivery cannot pass a hold, so the leak's own push stays quiet (A3). Fixed. A plan chooses the reach of "Lets through": "every delivery of these messages", which includes the call's own deliveries, or "only what this plan sends". Because a person gets one delivery per channel, an Admin whom both the call and the Leaks plan push to gets one push, and it rings.
- The safety-net fallback speaks info at 03:00 into an empty house (A1, B3). Fixed in the scenario and made visible. The Safety net plan no longer lets anything through, so Night quiet makes its speech quiet for info at night, and the plan's In words says so. Chris adds a fallback step to the Leaks and Critical plans, which let Night quiet through for their messages. Presence rules are never let through by a fallback in the starter plans.
- Digest messages and plan steps at 20:00 (B3). Fixed and moved into the rules. A message collected into a summary starts no plan steps at all, as in 1.0.0. The summary is one delivery that house rules see like any other. This is now part of conflict rule 2, not a side remark.
- Timer rows keyed by step index break when a step is deleted (D3). Fixed. Each step has a stable step ID, stored with the step. Timer rows use the policy key plus the step ID, so deleting one step cancels only its own row.
- One switch per plan: Ben cannot switch off only the repeat step from YAML (A, other remark). Accepted. Converted plans keep one step each, so every 1.0.0 switch still controls exactly what it did. Steps are never merged automatically. A user who builds a multi-step plan gets one switch for the journey, and the form says so.
- Downgrade is lost after the first multi-step plan (A, D3). Accepted. D-213 asks that every 1.0.0 setup converts without a breaking change, and that every behaviour change has a way back inside 1.1. It does not ask for a downgrade path. The way back for converted behaviour lives inside 1.1 ("Restore 1.0.0 links"). A plan with one step keeps the old type key, so a downgrade still reads it.
- Pain point 4 only avoided for users who find "Faster while" (A2). Fixed by the shared rhythm (first answer above). Two plans and one plan with "Faster while" now give the same repeats.

## Taken from others

- From A: render each 1.0.0 conversion link as a plain sentence in Which messages, and list converted policies that never acted with "Keep as before" and "Let it act". I did not take A's static Not for, because a switch toggled from YAML would then behave differently from 1.0.0 (see my review of D). The stored link stays live, and the form offers a one-click rewrite to "Not with tags digest" wherever that is exact.
- From A and B: one shared repeat rhythm per message and channel, the shortest in force, and B's "Own rhythm" as the visible way back for converted "all" setups.
- From B: the message history shows the same timeline as Try a message, filled from the ledger, with the reason for each hold and the plan that would have let it through (Q2). Also B's "Show details" switch, which adds each card's switch entity ID and a copy button for Ben.
- From D: "A window belongs to the day it starts" settles scenario 2's Friday night in one sentence, and the card note "Never acts" for converted policies.

## 1. The mental model

Each plan is the journey of one kind of message and says which house rules it may pass; house rules are the house's limits and apply to everything else.

## 2. Vocabulary (English / German)

- Policies / Richtlinien (page; the word stays because calls name policies)
- Plans / Pläne; Plan / Plan
- House rules / Hausregeln; House rule / Hausregel
- Step / Schritt
- At once / Sofort
- If nobody reacts within … / Wenn niemand reagiert innerhalb …
- Repeat every … / Wiederholen alle …
- Faster while … / Schneller solange …
- At most … times / Höchstens … Mal
- Own rhythm (1.0.0) / Eigener Takt (1.0.0)
- If nobody could be reached / Wenn niemand erreicht wurde
- Send to / Senden an; as the call says / wie im Aufruf
- Lets through / Lässt durch
- for every delivery of these messages / für jede Zustellung dieser Nachrichten
- only for what this plan sends / nur für das, was dieser Plan sendet
- All quiet times, also later ones / Alle Ruhezeiten, auch spätere
- Let through by / Durchgelassen von
- Count from: when it reached someone / when it appeared / Zählen ab: Erreichen / Erscheinen
- Quiet times / Ruhezeiten; Presence / Anwesenheit; Summary / Zusammenfassung
- Wait until the end / Bis zum Ende warten; Send quietly / Leise senden; Drop / Verwerfen
- Which messages / Welche Nachrichten; Severity / Dringlichkeit
- With tags / Mit Tags; Not with tags / Nicht mit Tags
- Only if / Nur wenn
- Runs: automatically / only when named / Läuft: automatisch / nur wenn genannt
- In words / In Worten
- Also acting on these messages / Wirkt auch auf diese Nachrichten
- Try a message / Nachricht ausprobieren
- Can wake people / Kann Leute wecken
- Not for messages that … takes (1.0.0) / Nicht für Nachrichten, die … nimmt (1.0.0)
- Never acts (1.0.0) / Wirkt nie (1.0.0); Keep as before / Wie bisher; Let it act / Wirken lassen
- Show details / Details zeigen

## 3. Structure

### The Policies page (single column, 380 px)
1. Converted from 1.0.0 (only after a conversion, until dismissed): policies that never acted, and each conversion link, with "Keep as before", "Let it act" and "Restore 1.0.0 links".
2. Try a message: severity, tag, time, somebody home. The answer is the journey in time order, each line naming its plan or house rule. The same timeline sits in each message's history, built from the ledger (Q1, Q2).
3. Can wake people: one line per plan with "Lets through", for example "Leaks: lets Night quiet through for its own sends (push to Admins, Kitchen speaker)". This is the single place where strength lives (Q3).
4. Plans. One card per plan: name, switch, Which messages, "Lets through" as a text badge with an icon, then the steps as a short timeline.
5. House rules. One card per rule: name, kind, switch, Which messages, the effect in words, and "Let through by" (read-only).

No order and no mode. Cards sort by kind, then name. "Show details" adds entity IDs.

### The form of a plan
- Name; Which messages (severity chips, With tags, Not with tags, Only if, Runs).
- Lets through: chips, one per house rule by name, plus "All quiet times, also later ones", "All presence rules, also later ones" and "All summaries, also later ones". Reach: "for every delivery of these messages" or "only for what this plan sends".
- Steps, each a card with a stable ID: At once (send to …, or as the call says); If nobody reacts within N; Repeat every N, Faster while, At most M (Own rhythm only on converted steps); If nobody could be reached. Timed steps have "Count from".
- In words, and Also acting on these messages, live before Save (D-151, never blocks).

### The form of a house rule
- Name, kind (Quiet times, Presence, Summary); Which messages (no "Critical messages pass"); channels; the kind's own fields (windows; D-212 presence fields; summary time). A window belongs to the day it starts.
- Let through by: read-only list of plans that let this rule through, with their reach. A new rule shows the plans whose "also later ones" chip already covers it, before Save. This answers Chris's fear: Anna sees that Critical messages still get through her new "Weekend lie-in".

## 4. Conflict rules

1. Every plan that fits a message adds its steps; each person gets one delivery per channel at a time, and repeats on one channel follow the shortest rhythm in force with one shared count, unless a step keeps "Own rhythm (1.0.0)".
2. Every house rule that fits holds back: a summary collects the whole message, which then starts no steps, quiet times and presence act on each delivery with the strictest winning (drop, then wait, then send quietly), and a delivery passes a house rule only when a plan that fits the message lets that rule through for it.
3. Waiting times count from when the message first reached someone, unless the step says "when it appeared", so a held message neither escalates nor repeats.

A shared count ends when it reaches the highest "At most" among the repeat steps that fit at that moment. A 1.0.0 conversion link narrows Which messages; it is not a fourth rule.

## 5. The twelve scenarios

1. Leak, warning, 03:00. Plan "Leaks": tags `leak`, `smoke`; At once push to Admins; after 10 min if nobody reacts Kitchen speaker; Lets through Night quiet, only for what this plan sends. Night quiet: all severities, 22:00 to 07:00, send quietly. At 03:00 the call pushes to the household and the plan pushes to the Admins. Each Admin gets one push, and it rings. Anna and Ben get theirs quietly. An info message at 03:00 is quiet. "Can wake people" shows the Leaks line.
2. Two windows. House rule "Night quiet", info and success, windows Monday to Friday 22:00 to 07:00 and Saturday and Sunday 23:00 to 09:00, send quietly. A window belongs to the day it starts, so Friday 22:00 to Saturday 07:00 is the weekday window. In words: "The weekend window adds Saturday and Sunday nights; the windows do not overlap." A warning is not touched.
3. Doorbell. House rule "Doorbell speech", Presence: tag `doorbell`, speech, speak when somebody of Household is home, otherwise drop; Only if guest mode is off. Nobody home: speech dropped, push sent. Guest mode on: the rule does not apply, speech plays. Night quiet is a separate rule and keeps working. No plan lets Doorbell speech through.
4. Critical. Plan "Critical messages": critical; At once push to Admins; Repeat every 10 min, no limit; Lets through all quiet times, presence rules and summaries, also later ones, for every delivery of these messages. The push and the repeats belong to one plan, so neither can block the other. An acknowledgement stops the repeats.
5. 15 min while X, else 1 h. Either one step (every 60 min, Faster while X: 15 min, at most 6) or two plans (Hourly: every 60 min, at most 6; Urgent: every 15 min, at most 6, Only if X). Both give the same result. Minute 0: the message reaches Anna and the shared count starts. Minute 15: X turns on, the shortest rhythm in force is 15 min, the next repeat is last send plus 15, which is due now, so repeat 1 goes now. Then minutes 30 and 45. When X turns off, the next repeat is 60 minutes after the last one. The count is never reset. Try a message and the history say "Repeat 3 of 6, every 15 min while X is on".
6. Shopping list. House rule "Shopping list", Presence: tag `shopping`, push, recipient not in Home, hold until it changes, maximum wait 12 h then drop. Anna's push waits while she is home and goes out when she leaves. The check is per recipient; untagged messages are untouched.
7. Digest. House rule "Evening summary", Summary: tag `digest`, at 20:00. Each digest message is collected on every channel, banner included, and starts no plan steps. At 20:00 one summary per recipient and channel goes out and meets Night quiet and presence like any delivery. Other info messages are not summarized.
8. Nobody reached. Plan "Safety net": all messages; If nobody could be reached, speech on Household speakers; lets nothing through. For a warning in the day it speaks. For info at night Night quiet makes it quiet, and In words says so. A Presence rule for speech can drop it, and In words says that too. For leaks and critical messages Chris adds the same fallback step to those plans, which let Night quiet through. The page shows this under "Can wake people".
9. Escalation, message held. Plan "Warnings": If nobody reacts within 30 min, push to Admins. Night quiet for warnings: wait until the end. A warning at 23:00 reaches nobody until 07:00, so the escalation goes at 07:30 at the earliest. If Chris wants a night escalation, he sets Count from "when it appeared" and adds Night quiet to Lets through for this plan's sends: it then fires at 23:30 and rings. In words shows the result before Save.
10. Critical watch-rule message. Plan "Critical messages" fits by severity, and watch-rule messages are matched like any other (rule 9). Its push to Admins applies. No YAML.
11. 1.0.0 starter list plus Away (all severities, `critical_passes` on), order Summarize, Quiet hours, Away, Reminder, Deliver, mode first. In 1.0.0, digest info goes to Evening summary, other info and success to Night quiet, and warning and critical to Away, so Warning reminder and Critical delivery never act. After conversion every subentry and switch stays. Night quiet: "Not for messages that Evening summary takes (1.0.0)". Presence: not for messages that Evening summary or Night quiet takes. Warning reminder and Critical delivery: not for messages that Presence takes, listed as "Never acts (1.0.0)". `critical_passes` becomes one new plan "Critical messages pass (1.0.0)": critical, no steps, lets through every delivery past the rules that had the flag (here Night quiet and Presence, and Evening summary when `include_critical` was off). Every message gets the same deliveries.
12. Overlap before Save. Anna adds "Weekend lie-in" (Quiet times, info and success, Saturday and Sunday 06:00 to 10:00, wait). Also acting: "Night quiet also acts here. Saturday and Sunday 06:00 to 09:00 both apply; waiting is stricter than sending quietly, so these messages wait until 10:00." Let through by: "Critical messages (all quiet times, also later ones)". For a second plan: "Warnings also fits these messages; repeats follow the shorter rhythm, one count."

## 6. Migration from 1.0.0 (D-213)

One subentry stays one subentry with the same ID, title and switch entity ID (D-198). Old keys are still read.

- Deliver, Escalation, Reminder, Fallback: a plan with one step and the same fields, keeping its type key. Escalation and Reminder get "Count from: when it appeared" (1.0.0 timing).
- Summarize, Quiet hours, Away and `presence`: house rules of kind Summary, Quiet times and Presence (Presence by D-214).
- `critical_passes` and `include_critical`: one new plan "Critical messages pass (1.0.0)", severity critical, no steps, Lets through, for every delivery of these messages, exactly the rules that let critical pass. Where every rule of a kind had the flag, the chip is "all of that kind, also later ones", so a rule added later behaves the way new 1.0.0 rules did by default. This plan adds one switch entity and removes none.
- Mode `first`: each automatic policy stores live links to the earlier overlapping automatic policies in `policy_order`. It does not fit a message while a linked policy is on and fits it. This matches 1.0.0 even when a switch is toggled from YAML. The form shows each link as a sentence and offers a rewrite to plain Not for where exact. Policies that can never act are listed as "Never acts (1.0.0)".
- Mode `all`: no links. Overlapping converted Reminder steps get "Own rhythm (1.0.0)", so both keep repeating side by side as before.
- `policy_order` and `policy_mode`: kept in storage, read by the converter and by "Restore 1.0.0 links", not shown.
- `apply: manual`: Runs only when named. Named policies in calls add to the automatic ones (D-189), `match_policies_automatically: false` runs only named ones, a watch rule's named policy replaces them (D-145): unchanged. A named policy ignores its conversion links, as it ignored the order in 1.0.0.

Visible changes and CHANGELOG lines:
- "Policies are shown as Plans and House rules; the order list and the mode setting are gone; converted setups behave as before."
- "Critical messages pass moves from each quiet, presence and summary policy to one plan, Critical messages pass (1.0.0)." Way back: none needed, behaviour is the same; switching that plan off holds critical messages.
- Ways to the new behaviour, each undoable: "Let it act" (undo: Restore 1.0.0 links), "Count from: when it reached someone" (undo: set it back), remove "Own rhythm" (undo: set it again).

## 7. Engine impact

Reused:
- Chain stages Summarize, Quiet hours, Presence, Fallback, with holds, release on arrival, at a time or deadline, and restore after restart.
- The "all" path of `for_message`, plus the live links. S.
- One delivery per person and channel: the `_apply_deliver` rule, applied to every plan's At once step. S.
- Timer rows, `_drop_inapplicable_timers`, overdue-fires-once; key becomes policy key plus stable step ID. S.
- The In-words builder, per step; the D-151 overlap note grows into Also acting. M.

New:
- Plan type with steps and step IDs; four old types read as one-step plans. M.
- Lets through: each delivery carries the plans that fit the message and its origin plan; the Quiet and Presence stages check the named rules and the reach; Summarize checks it once at appearance. Replaces `critical_passes` at run time (still read). S to M.
- Shared repeat rhythm per message and channel, with a shared count and Own rhythm; re-planned when an Only if or Faster while condition changes (needs the D-216 listeners). M.
- Count from first reach: arm timers on the first delivery that reached someone, or on release. M.
- Try a message and the history timeline: a dry run of matching and the chain, and a ledger reader for the history. The 1.0.0 preview (`engine.py`, "sends nothing") is the base. M.
- Converter with live links, the Critical plan and Own rhythm; Restore 1.0.0 links. M.
- Panel: page, plan form with steps and Lets through, house rule form with Let through by, converted card, details switch. L.

## 8. Risks and what this design gives up

- Biggest risk: a plan's "Lets through" with the reach "every delivery" is as strong as A's band for its messages. One chip added by another admin can wake everyone. Mitigations: it is listed in "Can wake people", the house rule form shows it, and the default reach for a new plan is "only for what this plan sends".
- D-211 is reversed: "Critical messages pass" leaves the house rule form. This needs a maintainer decision and a new decision number. Without it, C falls back to two ways through (the v1 problem).
- A shared rhythm hides a slower plan while a faster one fits, so a user may wonder where the hourly reminder went. The history line names the rhythm in force.
- Converted setups show link sentences, "Never acts" and a new Critical plan on the first look after the upgrade. This is honest, but the page is busier.
- Given up: list order; "only the first" for new setups; per-step strength (now per plan; split a plan to give one step different strength); separate switches for steps inside one plan; downgrade once a plan has several steps.
- Not verified: one condition listener per entity shared by Only if, Faster while and presence; a repeatable step list in the ha-form style without a build step (the wizard's repeatable rows suggest yes).

## 9. Mockup

[policy-redesign-c.html](../mockups/policy-redesign-c.html): the Policies page (converted card, Try a message, Can wake people, Plans with Lets through, House rules with Let through by, Show details) and the plan form (Which messages, Lets through with reach, steps, In words, Also acting). Light and dark with a toggle, 380 px, keyboard and screen-reader labels, text badges with icons.
