# Policy redesign, design E: keep the list

Written in round two by Designer B, as the alternative every other design rejected: the smallest step from the 1.0.0 model. Inputs: [fact sheet](00-fact-sheet.md), [users and stories](01-users-and-stories.md), the v2 designs [A](design-a-v2.md), [C](design-c-v2.md), [D](design-d-v2.md) and the four reviews. Mockup: [policy-redesign-e.html](../mockups/policy-redesign-e.html). Sample names only.

The goal of E is low build cost and the smallest visible change, held to D-213 strictly. Where E is weaker than AB, C or D, this file says so.

## A. Why the others rejected this, and the answer

- "The order means two things" (pain point 3; A v1, B v1). Answer: under "One of each type" order only decides between policies of the same type, and the page shows the list per type, so it has one meaning.
- "One place per message is shared by all types" (pain point 2; all designs). Answer: one place per type. A speech Presence no longer switches off Night quiet; Critical delivery and a critical reminder both act.
- "Only if changes the chosen policy mid-life" (pain point 4; the reason modes were merged into this session). Answer: the change is intended and defined. Re-choose at every step, plan from the last delivery, keep each reminder's count. Scenario 5 is predictable and the form states the maximum.
- "Holds against sends" (pain point 5). Answer: one fixed rule (holds win) plus clocks from first reach. This is weaker than AB and C for a fallback that should pass, and honest about it.
- "Critical is the only way through" (pain point 6). Answer: Not for tags. It works, but per hold rather than in one place.
- "Tags cannot be excluded" (pain point 7). Answer: Not for tags.
- "Ordering needs keyboard and touch design." Answer: it already exists in 1.0 (Move up and Move down); E only limits it to one type.
- Where E wins: cost (M), no forced change for any 1.0 setup, the same page and words users already know, and an exact way back by one setting.

## 1. The mental model

"Each kind of policy has its own place: the highest one of that kind in the list that fits at that moment acts, different kinds never block each other, and a hold always beats a send."

## 2. Vocabulary

English then German. The type names, "Which messages", "Only if" and the switch entities stay as in 1.0.0.

- Policies / Richtlinien (page, unchanged)
- Hold back / Zurückhalten (group heading)
- Send / Senden (group heading)
- Quiet hours / Ruhezeit; Presence / Anwesenheit; Summarize / Zusammenfassen (unchanged)
- Deliver / Zustellen; Escalation / Eskalation; Reminder / Erinnerung; Fallback / Ersatz (unchanged)
- Higher in the list counts / Weiter oben zählt (one line under each type with two or more policies)
- Move up / Nach oben; Move down / Nach unten (unchanged; now only within one type)
- Place / Platz (in the form: above or below another policy of this type)
- Not for tags / Nicht für Tags (new)
- Critical messages pass / Kritische Nachrichten kommen durch (unchanged, D-211)
- Let through at night / Nachts durchgelassen (computed line in the Hold back group)
- Count from / Zählen ab: when it reached someone / sobald sie jemanden erreicht hat; when it was created / ab dem Erstellen
- How the list works / So wirkt die Liste: One of each type / Eine pro Art; Only the first (1.0) / Nur die erste (1.0); All that apply (1.0) / Alle passenden (1.0)
- What changes / Was sich ändert; Keep as before / Wie bisher lassen; Let it act / Wirken lassen
- What happens to a message? / Was passiert mit einer Nachricht?

## 3. Structure

### The Policies page

- One stored list, as today (`policy_order`, unchanged format).
- Under "One of each type", the page shows the list grouped by type, in two groups:
  - Hold back: Summarize, Quiet hours, Presence.
  - Send: Deliver, Escalation, Reminder, Fallback.
- Inside a type the policies keep their list order. Drag, Move up and Move down work only inside a type. Moving a policy swaps it with the neighbour of the same type in the stored list, so the order across types is kept and a switch back to "Only the first" reads the same list.
- A type with one policy shows no handles. A type with two or more shows "Higher in the list counts".
- Top of the Hold back group, one computed line from the hold policies' fields: "Let through at night: critical messages (all quiet hours), tag `leak` (Night quiet)". This is E's answer to "what may wake me".
- Above everything, "What happens to a message?": severity, tag, time, who is home. It names, per type, the policy that acts and what it does.
- Under "Only the first (1.0)" and "All that apply (1.0)", the page keeps today's single list. On top it shows "Your list uses the 1.0 rule. Switch to One of each type", with the What changes dialog (section 6).

### The form of one policy

Unchanged from 1.0.0 and the Presence design (D-212, D-214), plus four fields:
- Not for tags, in Which messages.
- Place: "above / below [policy of this type]". The default is the bottom of the type. Shown only when the type has another policy.
- Count from, on Escalation and Reminder.
- The overlap sentence (D-151, never blocks) for same-type policies only: "Where both fit (info, Saturday 06:00 to 09:00), Weekend lie-in counts because it is higher. Move it below Night quiet to change that."

### How order and strength are expressed

- Order has one meaning: which policy of the same type counts where two fit. It no longer means "stronger than another kind".
- Strength between kinds is one fixed rule: holding back beats sending (section 4). The way through a hold is to take the message out of it: Not for tags, or Critical messages pass.

### Which strength rule, and why

The two candidates were a "May wake people" mark on sending policies, or "holds win, and clocks pause while held". E takes the second, with Not for tags as the way through:
- A mark on a sending policy cannot help the automation's own first push. The leak push to Anna and the banner come from the call, not from a Deliver policy, so they stay quiet.
- A marked escalation or fallback wakes people for every message it covers, including the info messages a quiet hour was written for. It also passes Presence and speaks into an empty house.
- The permission is spread over every sending form, so Chris cannot see in one place what may wake him. A sending policy added later by someone else can break the nights.
- "Holds win" needs no new concept, and it is what the 1.0 chain already does for every delivery.
- Pausing the clocks (counting from the first reach) fixes scenario 9 without any mark.
- Not for tags fixes pain point 6 without making things critical. The cost is that the exemption sits on each hold (section 8).

## 4. Conflict rules

1. Policies of different types never block each other; of one type, only the highest in the list that is in effect at that moment acts: switched on, severity and tag fit, not excluded by Not for tags, Only if true, for Quiet hours its window is now, for Presence it covers that channel.
2. A hold beats a send: every delivery, including those added by Deliver, Escalation, Reminder or Fallback, passes the summary, quiet hour and presence policy in effect, and a repeat that would have to wait is skipped; a message is let through only by Not for tags or Critical messages pass on that hold.
3. Escalation and Reminder count from the first delivery that reached a person (the banner counts only when it is the only channel), unless the policy says "when it was created"; when the reminder in effect changes, the next repeat is the last delivery plus the new interval, and each reminder keeps its own count.

"At that moment" means at every step: when the message appears, at each delivery, at each timer, and when an Only if condition changes (the D-216 listeners).

## 5. The twelve scenarios

Scenario 1, leak warning at 03:00.
- Configure: Deliver "Leak to Admins" (tag `leak`, push to Admins). Night quiet (info, success, 22:00 to 07:00, quietly). If Night quiet covers all severities, add Not for tags `leak`.
- Happens: the leak gets its Deliver. No quiet hour fits it, so the Admins' push rings at 03:00; so does Anna's push from the call. An info message is quiet. The Hold back group says "Let through at night: tag leak (Night quiet)".
- Weaker than AB: E cannot wake only the Admins and keep Anna quiet for the same message. A hold acts per message, not per person.

Scenario 2, two windows.
- Configure: Quiet hours "Weeknights" (info, success; Sunday to Thursday, 22:00 to 07:00) and "Weekends" (Friday and Saturday, 23:00 to 09:00).
- Happens: at any time at most one window is now, so each acts in its own nights. The form says "Weekends does not overlap Weeknights". Warnings are not in Which messages.

Scenario 3, doorbell.
- Configure: Presence "Doorbell at home" (tag `doorbell`, covers speech, somebody of Household in Home, otherwise drop, Only if guest mode is off).
- Happens: nobody home and guest mode off: no speech; push is not covered and goes out. Guest mode on: the policy is not in effect, speech plays. Night quiet is a different type and keeps acting (pain point 2 fixed).

Scenario 4, critical pushed and repeated.
- Configure: Deliver "Critical delivery" (critical, push to Admins) and Reminder "Critical repeat" (critical, every 10 minutes, at most 12).
- Happens: different types, both act. The push starts the clock; repeats every 10 minutes; any acknowledgement stops them. Under 1.0 "only the first" one of them was lost.

Scenario 5, 15 minutes only if X, otherwise 1 hour.
- Configure: Reminder "Urgent" (every 15 minutes, at most 8, Only if X) above Reminder "Hourly" (every 60 minutes, at most 6).
- Happens:
  - Minute 0: X is off, so Hourly is in effect; next at 60.
  - Minute 15: X turns on, and the listener re-chooses. Urgent is higher and in effect. Next = last delivery (0) + 15 = now, so Urgent's repeat 1 goes now, then 30 and 45.
  - Minute 50: X turns off. Hourly is in effect again; next = 45 + 60 = 105, and Hourly's count is still 0 of 6.
- Each reminder keeps its own count, so the most repeats is 8 + 6. The form says so: "Urgent and Hourly count separately; at most 14 repeats in all".
- If Hourly were placed above Urgent, Urgent would never act. The overlap sentence says that before Save.

Scenario 6, shopping list.
- Configure: Presence "Shopping on leaving" (tag `shopping`, covers push, recipient in Home: hold until it changes), placed above any wider Presence policy that covers push.
- Happens: held for Anna while home, sent when she leaves; checked per recipient; other messages untouched.

Scenario 7, digest.
- Configure: Summarize "Evening summary" (tag `digest`, 20:00).
- Happens: the summary holds the message when it appears, so Night quiet (a different type that also fits) never sees the single messages. The summary at 20:00 passes the holds; Night quiet starts at 22:00. Under 1.0 only the order kept Night quiet away (D-150); here the type rule does.

Scenario 8, nobody reached.
- Configure: Fallback "Say it in the house" (speech on Household speakers).
- Happens: the fallback passes the holds in effect (rule 2). At night an info message stays quiet. A doorbell fallback with nobody home is dropped by "Doorbell at home". The page says so in the "What happens" checker.
- For a leak, Not for tags `leak` on Night quiet lets the speech through. There is no way to let the fallback through but keep the first push quiet (weaker than C).

Scenario 9, escalation for a held message.
- Configure: Escalation "Nobody looked" (warning, 30 minutes, Admins); Quiet hours "Night wait" (warning, 22:00 to 07:00, wait).
- Happens: a warning at 23:00 waits until 07:00 and has reached nobody, so the clock starts at 07:00 and Admins are told at 07:30. With "when it was created", it is due at 23:30 and waits until 07:00 with the message. To be woken, take warnings out of Night wait or narrow it with Not for tags.

Scenario 10, critical watch-rule message.
- Configure: Critical delivery from scenario 4.
- Happens: rule messages (tag `rule`) fit by severity. In 1.0 this broke whenever another type above matched critical (an Away policy in the starting order); here different types never block it.

Scenario 11, starter list plus one Away policy, mode "first".
- Nothing changes at the upgrade. The setup stays on "Only the first (1.0)": same list, same order, same deliveries, whether Away was appended last or placed by the starting order.
- The page shows the switch offer. Its What changes dialog depends on where Away sits:
  - Away appended last (the introduction creates the starter list first): under "One of each type", Presence starts holding push for people not home for info, success and warning messages; critical passes. Evening summary and Night quiet both fit digest messages, but the summary holds them first: no change.
  - Away placed by the starting order, above Reminder and Deliver: Warning reminder starts reminding about warnings, and Critical delivery starts pushing critical messages to the Admins. In 1.0 neither acted. Presence keeps holding.
  - A hold listed above an escalation on purpose (Quiet hours for warnings above Escalation for warnings): in 1.0 the escalation never ran for warnings at any hour, because matching ignores the window. Under the new rule it runs, counting from the first reach.
- Each line has "Keep as before" (writes a link "not for messages that [policy] takes, while it is on") or "Let it act".

Scenario 12, a second overlapping quiet hour.
- Configure: Anna adds Quiet hours "Weekend lie-in" (info, Saturday and Sunday 06:00 to 10:00, wait). Place defaults to below Night quiet.
- Happens before Save: "Where both fit (info, Saturday and Sunday 06:00 to 09:00) Night quiet counts because it is higher: info goes quietly. From 09:00 to 10:00 only Weekend lie-in fits: info waits until 10:00." She sets Place to "above Night quiet" and the sentence changes live. Critical passes stays on by default, and the form says "Let through: critical" as Night quiet does.
- Weaker than AB and C: a new hold does not inherit Night quiet's Not for tags `leak`. The form shows "Night quiet lets through tag leak; this policy does not. Copy?" It does not copy by itself.

## 6. Migration from 1.0.0 (D-213)

- No data migration beyond what 1.1.0 already decided (Away to Presence, D-214). Every type, field, switch entity ID (D-198), `apply: manual`, named policies in calls (D-189) and watch rules (D-145) stay as they are.
- `policy_mode`: a new value `per_type` ("One of each type") is the default for new setups. Existing `first` and `all` stay what they are, and 1.0 setups behave exactly as before.
- Switching from `first` to `per_type` opens What changes. A pure function compares, for each severity × each tag any policy names (plus "other tag") × channel, which policy of each type acts under the old and the new rule, using today's switch states. Each difference is one line with "Keep as before" or "Let it act". "Keep as before" writes `not_with: [subentry id]`, which follows the other policy's switch, as 1.0 did.
- Switching from `all` to `per_type`: the lines are same-type overlaps that now pick one ("Two quiet hours fit on Saturday; Night quiet counts").
- Way back: set How the list works back to the 1.0 rule. `policy_order` was never rewritten across types, so the old rule reads the same list.
- Count from: existing Escalation and Reminder policies get `count_from: created`; new ones get `reached`. The What changes dialog offers to switch them.
- CHANGELOG lines: "New rule One of each type for new setups; existing setups keep their rule and can switch with a preview"; "Not for tags"; "Escalation and Reminder can count from when the message reached someone".

## 7. Engine impact

Reused: the chain and its holds, timer rows, `_drop_inapplicable_timers`, overdue fires once, `policy_order`, the drag list with Move up and Move down, the overlap note.

- `select()` with `per_type`: for each type, the policies that match, in list order. S.
- Quiet stage: the first policy whose window is now, instead of the strictest of all; Presence stage: the first that covers the channel. S each.
- Summarize: the first in order instead of the first by name. S.
- Reminder and Escalation: the first in effect; on change, cancel the other row but keep its count, and plan from the last delivery. Needs the D-216 condition listeners, which 1.1.0 builds anyway. M.
- Not for tags (`exclude_tags`) and `not_with` in `applies()`. S.
- Count from reached: arm on the first delivery to a person or on release. M.
- What changes dialog (pure function plus panel dialog). M.
- Panel: grouping by type, moves within a type, Place, Not for tags, Count from, "Let through at night" line. M.
- "What happens to a message?": a websocket dry run of matching plus the stage choice; no full timeline. M.

Overall M, against L for AB, C and D. Nothing new is stored except one mode value, `exclude_tags`, `not_with` and `count_from`.

## 8. Risks and what the design gives up

Risks:
- Biggest risk: converted setups keep the 1.0 pain points until someone presses Switch. Pain points 2 and 3 stay for every user who ignores the offer.
- The order survives. Anna still has to understand "higher counts" within a type, and putting a wide policy above a narrow one silently starves the narrow one. The overlap sentence is the only defence.
- The way through a hold sits on each hold. Chris's fear stays partly open: a new quiet hour without Not for tags `leak` holds leaks. The "Let through at night" line and the Copy hint make this visible but do not prevent it.
- "Chosen again at every step" moves timers when conditions change. Tests must cover flapping conditions; each reminder's own count bounds the total.

Given up, compared with AB, C and D:
- Waking some people but not others for one message (AB's "Wakes", B's "for the people this goal sends to").
- Escalation tiers and two Deliver policies for one message: one place per type means one escalation and one Deliver per message. Combine targets in one policy, or split by tag.
- A send stronger than its hold (C's "Lets through").
- One place per wish (D's per-type quiet choice, AB's band). Here a wish like "leaks wake us" can touch several holds.
- An order-free page.

## 9. Mockup

[policy-redesign-e.html](../mockups/policy-redesign-e.html): the Policies page under "One of each type" (grouped by type, moves within a type, the "Let through at night" line, the switch offer for a 1.0 setup with its What changes dialog) and the Quiet hours form for scenario 12 with Place, Not for tags and the live overlap sentence. Light and dark, phone width, sample data.
