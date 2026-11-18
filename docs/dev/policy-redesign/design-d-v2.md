# Policy redesign, design D (v2): message types

Stance: behaviour belongs to the kind of message, not to rules that match severity and tag. A message has exactly one type, and the type carries everything that happens to it. Nothing combines and nothing competes. v1: [design-d-v1.md](design-d-v1.md). Mockup: [policy-redesign-d.html](../mockups/policy-redesign-d.html). Sample names only.

## A. Answers to the reviews

Reviews read: [review-by-a.md](review-by-a.md), [review-by-b.md](review-by-b.md), [review-by-c.md](review-by-c.md). None was missing.

1. Scenario 11 told for the wrong order (C1, B1). Fixed. `policy_order` is stored once at setup and later policies are appended (`initial_order`, `ordered()`), so Away can sit before the reminder and Critical delivery or at the end. Section 6 now walks through both positions. The cell method was right; the worked example was wrong. A `critical_passes` on the policy that took a cell is now part of the cell's result, so critical messages that Away let through do not end up in a type that holds them.
2. Switch toggles no longer reproduce 1.0.0 "only the first" (C2). Fixed. A type now has a "When switched off" line: if every section of a type is off, its messages go to the type named there. The migration fills it from `policy_order` per cell. So switching Night quiet off from an automation hands info messages to Away again, as 1.0.0 did. New types hand their messages to nobody ("delivered as the call says").
3. One switch controls sections in several joined types after an "all" migration (C2). Accepted, with the reason shown. That is exactly what the 1.0.0 switch did: the policy stopped acting on every message it matched. The section header says "Switch Away also turns this off in 2 other types".
4. Fallback and the night choice must be set per type; what a new type starts with is unclear (C3, A3, B3). Fixed in part. A new type must start from an existing type ("Start from: Everyday"), so it copies every section, its fallback and its night choice; there is no hidden default. The Quiet times card is now the one place for the wish "quiet nights": it lists every type with its choice and lets Anna change them there (Q4). The per-type fallback stays per type (accepted, section 8). Try a message and the type card say "If nobody is reached, nothing more happens" when a type has none.
5. Watch-rule messages all carry tag `rule`, so a warning leak rule cannot reach Alarm (C3, A1, B3). Fixed. "Used for" can name watch rules: "Messages from watch rule Leak sensor". A rule message already carries its rule in its ID (`rule_` plus the rule's subentry ID, `manager.py`), so the type can claim it without any change to the frozen rule (D-100 kept). This removes the parity exception v1 asked for (rule 9).
6. A claim moves silently on Save and can take a leak away from Alarm (A2, B2). Fixed. A tag or rule that another type holds is shown on the form as "leak belongs to Alarm", with an unchecked box "Move it to Kitchen". Saving without the box keeps the claim on Alarm and saves the rest (D-151: nothing blocks Save). When the losing type may wake people, the box reads "Move it to Kitchen. Leak messages will no longer wake people at night." The Alarm card shows "Gave tag leak to Kitchen" until it is dismissed.
7. An "all" migration makes many joined types; Ben's tags multiply them (A3, B1). Accepted, reduced. Cells merge whenever their set of acting policies is the same, so the count is the number of distinct sets, not tags times severities. The "Check after the update" list (taken from A) offers "Merge with ..." for types that differ in one section. Ben's ten tags that all meet the same two policies give one type.
8. "Everything except digest" only through a Digest type (A3). Accepted. In this model that is the honest answer: a message that should be treated differently is a different type. The digest tag is claimed by Digest and every other message keeps its type.
9. A severity change after creation is not covered (A). Fixed. A call that updates a message's severity runs the type choice again. Its timers restart, as they do in 1.0.0 on a severity change.
10. The `type` field is new API Ben's automations do not use (A). Accepted. It is optional; tags and rules cover existing calls.
11. Repeats in a "wait" window are skipped in 1.0.0, not held. Presence never held a reminder (B, raised against A, true for D v1 too). Fixed in the rules. Rule 2 now says a repeat that falls in a hold is skipped, not saved up, which is the 1.0.0 stage behaviour.

## B. Taken from others

- From A: the "Check after the update" list with "Keep as before" and "Let it act", and the who-is-home input in Try a message.
- From B: the timeline in each message's history, filled from the ledger, for Q2 ("Held until 07:00 by type Everyday, quiet times; type Alarm would have sent it as usual").
- From C: the "Can wake people" block near the top of the page. In D it lists types, their claims and the watch rules they claim, because a type is the only thing that can wake anyone.
- From A and C, as a lesson: their reviews showed that a message-wide pass wakes everyone. D v2 splits the night choice of a type into "What the call sends" and "What this type adds", so the Admins can be woken while the household push stays quiet (scenario 1), still inside one type.
- From A and B, mechanics only: the before-Save warning extends from the critical default to every claim that leaves a type that may wake people (item 6).

## 1. Mental model

"Every message is of one type, such as Alarm, Doorbell or Digest, and that type alone decides who gets it, how, at night, and what happens if nobody reacts."

How D differs: in A, B and C every policy, goal or rule that fits a message acts, and a strength rule settles the meeting points. In D nothing meets: one type per message, so there is no strength rule between types at all.

## 2. Vocabulary

English then German. The word "policy" leaves the page; it stays in old YAML.

- Message types / Nachrichtenarten (page)
- Type / Art; type key / Schlüssel der Art (the stable name in calls, for example `doorbell`)
- Used for / Gilt für: Tagged / Mit Tag; From watch rule / Von Überwachungsregel; Everything else with severity / Alles andere mit Schweregrad
- Belongs to / Gehört zu; Move it to ... / Zu ... verschieben
- Start from / Beginnen mit (when adding a type)
- When switched off / Wenn ausgeschaltet
- Can wake people / Kann wecken (block and badge)
- Quiet times / Ruhezeiten; During quiet times / Während der Ruhezeiten: Wait until they end / Bis zum Ende warten; Send quietly / Leise senden; Drop / Verwerfen; Send as usual / Normal senden
- Also send / Zusätzlich senden; Collect into a summary / In einer Zusammenfassung sammeln; Presence / Anwesenheit; Repeat / Wiederholen (every, at most, faster while / alle, höchstens, schneller solange); Escalate / Eskalation; If nobody was reached / Wenn niemand erreicht wurde
- Only while / Nur solange
- Clocks start / Zeit läuft ab: when first delivered / ab der ersten Zustellung; when the message appears / ab dem Erscheinen
- Try a message / Nachricht ausprobieren
- Check after the update / Nach dem Update prüfen; Keep as before / Wie bisher lassen; Let it act / Wirken lassen; Did nothing in 1.0.0 / Hat in 1.0.0 nichts getan
- Added by the call / Vom Aufruf hinzugefügt

## 3. Structure

### The page "Message types"
Single column, five blocks:

1. Try a message: severity, tag, from watch rule (optional), time, who is home. Answer: the type, why ("tagged leak", "from watch rule Leak sensor", "critical, no other claim"), and what each channel does.
2. Can wake people: one line per type set to "Send as usual" for some quiet time, with what it is used for. "Alarm: critical; tagged leak, smoke; watch rule Leak sensor." A change made by someone else shows here.
3. Quiet times: the windows, and below them every type with its choice, editable in place. This is the one place for "quiet nights".
4. Types: one card per type, alphabetical. Name, key, Used for, text badges (Can wake people, Repeats, Escalates, Holds by presence, Summarized, No fallback), In words.
5. Check after the update (only after a conversion, until dismissed).

No order, no drag list, no mode.

### How a message gets its type
Decided when the message appears, again if a call changes its severity, and stored on the message.

1. The call names it: `type: doorbell`.
2. Else the type that claims its watch rule (rule messages only).
3. Else the type that claims its tag, optionally only for some severities.
4. Else the type set for its severity.
5. If the chosen type is switched off (all sections off), the type named under "When switched off", else no type: the message goes out as the call says.

Each claim belongs to one type and each severity to one default, so no order is needed. A step a call names by a 1.0.0 switch entity (D-198) joins the message's type for that message ("Added by the call").

### The form of one type
Fixed sections, each at most once, in the order of a message's life: Name and key; Used for (tags with optional severities, watch rules, severity defaults, each showing "belongs to ..." and the Move box when held elsewhere); Also send; Collect into a summary; During quiet times (two rows: "What the call sends" and "What this type adds": Also send, escalation, fallback; a repeat follows the row of the delivery it repeats; each row one choice, or per window); Presence (D-212, D-214, with Only while); Repeat (with Faster while); Escalate (stages by minutes); If nobody was reached; Clocks start; When switched off; In words.

Every section keeps or gets a switch entity; 1.0.0 policy switches keep their entity IDs as section switches.

## 4. Conflict rules

1. A message has exactly one type, chosen by the call, else by its watch rule, its tag or its severity, and only that type acts on it, plus a step the call names by switch.
2. The type's quiet-time and presence choices apply to every delivery of the message: a first delivery, escalation, fallback or summary waits, goes quietly or is dropped as the type says, and a repeat that falls in a hold is skipped, not saved up.
3. Repeat and escalation clocks start at the first delivery unless the type says "when the message appears", and only a delivery its type sets to "Send as usual" goes out normally during a quiet time; severity never passes by itself.

## 5. Scenarios

1. Leak, warning, 03:00. Chris adds tag `leak` and watch rule "Leak sensor" to Alarm. Alarm: also send push with sound to Admins; during quiet times, "What the call sends: Send quietly" and "What this type adds: Send as usual". The leak, from an automation or from the rule, gets Alarm: at 03:00 the Admins' push rings, while the push the automation sent to the household arrives quietly, so Anna sleeps. An info message at 03:00 is type Everyday, "Send quietly". "Can wake people" lists Alarm with `leak` and "Leak sensor".
2. Two windows. Quiet times "Weekday nights" 22:00 to 07:00 Mon to Fri and "Weekend nights" 23:00 to 09:00 Sat and Sun; a window belongs to the day it starts. In the Quiet times card Everyday is "Send quietly", Warning "Send as usual". The form says: "Weekend nights adds Saturday and Sunday 23:00 to 09:00. It does not overlap Weekday nights."
3. Doorbell. Type Doorbell (start from Everyday), tag `doorbell`. Also send speech on Kitchen speaker. Presence, speech: only when somebody of Household is home; Only while guest mode is off. Nobody home, guest mode off: push only. Guest mode on: spoken. Other types are untouched.
4. Critical. Alarm (critical default): also send push to Admins, Repeat every 10 minutes. The repeat of the Admins' push follows "What this type adds" and rings at night; a repeat of the household push follows "What the call sends" and stays quiet. Two sections of one type; nothing blocks. Acknowledging anywhere stops repeats.
5. Two rhythms. Warning: Repeat every 60 minutes, at most 6; faster while X is on: every 15 minutes. At 15 X turns on; next = last delivery plus 15 = now, so it fires at 15, 30, 45. One count, one limit of 6 for both rhythms (the form says it), so it never stops early because the rhythm changed. If Ben has two 1.0.0 reminders, the migration puts them in one type as "kept from 1.0.0, runs side by side" with a "Merge into one Repeat" button.
6. Shopping. Type Shopping, called with `type: shopping`. Presence, push: hold while the recipient is home, send when they leave, at most 12 hours then drop. Only messages of this type are held.
7. Digest. Type Digest, tag `digest` with info or success; summary at 20:00; quietly during quiet times. Digest messages have no other type, so nothing else touches them. A held digest starts no timers, as in 1.0.0.
8. Fallback. Alarm and Warning: If nobody was reached, speech on Household speakers. It follows the type's night choice: spoken at night for Alarm, quiet for types that send quietly. A type without one shows "No fallback". A held delivery is not "not reached" (`fallback.py`, D-123).
9. Escalation while held. Warning "Wait until they end", Escalate after 30 minutes. A 02:00 warning is delivered at 07:00 and escalates at 07:30. "When the message appears": due at 02:30, held with the message, sent at 07:00 with it, never before it. To be woken: "Send as usual".
10. Critical watch-rule message. It gets Alarm by severity, or by "From watch rule" for a warning rule. Same type as an automation; no YAML.
11. Starter list plus Away. See section 6 for both positions. Every message gets the 1.0.0 deliveries; Check after the update lists the types that did nothing in 1.0.0.
12. Overlap. Anna creates "Loud doorbell", tag `doorbell`, severity warning. The form: "Warning messages tagged doorbell belong to Doorbell. [ ] Move them to Loud doorbell." Checked: Doorbell keeps the other severities, and the sentence says so before Save. Overlapping quiet windows: "Where they overlap, each type uses its stricter choice (drop, then wait, then quietly)."

## 6. Migration from 1.0.0 (D-213)

For each severity and each tag or watch rule a policy names (plus "other"), the migration computes the effective 1.0.0 result: which policies acted, including `critical_passes` and `include_critical`. Cells with the same result become one type.

Scenario 11, position 1: Away created with the starter list, starting order Evening summary, Night quiet, Away, Warning reminder, Critical delivery.
- info and success tagged digest: Evening summary. Type "Evening summary".
- other info and success: Night quiet. Type "Night quiet", quietly during quiet time "Night quiet"; When switched off: Away.
- warning: Away held them. Type "Away" with the Presence section; When switched off: Warning reminder.
- critical: Away took them but let them pass (`critical_passes`), so nothing acted. Type "Critical messages" with no sections; When switched off is not needed. When Away is switched off, critical goes to Critical delivery, as in 1.0.0; the migration writes this as "When Away is off: Critical delivery".
- Warning reminder and Critical delivery: types with no claims, listed under Check after the update as "Did nothing in 1.0.0 because Away came first", with Keep as before or Let it act.

Position 2: Away added later, at the end. Critical goes to "Critical delivery", warning to "Warning reminder", info and success as above. Away has no cells and is listed as "Did nothing in 1.0.0".

The handoff on switch-off is stored per type as the 1.0.0 order restricted to its cells. It is shown on the type form as "When switched off: Away (from 1.0.0)", with Remove.

Other keys:
- Mode "all": each distinct set becomes a type with joined name. Two of a kind in one set stay side by side (merge button).
- Quiet hours windows become house quiet times with the policy's name; each type gets the action for the window if its set held it, otherwise "Send as usual".
- Away (`away`, read as `presence`, D-214): Presence section.
- `apply: manual`: type with no claims.
- Named policies in calls and in watch rules: unchanged meaning; `match_policies_automatically` (D-189) and D-145 kept.
- `policy_mode` and `policy_order` stay stored, used for the handoff and for "Restore 1.0.0", no longer shown.
- Migrated types: Clocks start "when the message appears" (1.0.0 timing).

Visible: new page; types named after policies; "Can wake people" lists types that were never quieted. No delivery changes. CHANGELOG: "Policies become message types; every 1.0.0 setup converts with the same deliveries"; "New `type` field in `notify`"; "New types start repeat and escalation clocks at first delivery; choose 'when the message appears' for the old timing." Way back: that setting; "Restore 1.0.0" on the Check card recomputes from the stored order; downgrade reads the untouched policy subentries.

## 7. Engine impact

- Reused: chain stages, held rows, timer rows, `_drop_inapplicable_timers`, overdue-once, the In words builder, policy subentries and switches as sections.
- Type choice at creation and on severity change, stored on the message; `for_message` returns its sections plus named steps. S.
- Rule claims from the message ID prefix. S.
- `message_type` subentries, house quiet times, claim ownership and the Move box. S to M.
- Handoff on switch-off. S.
- Quiet stage reads windows plus the type's choice. S.
- Clocks at first delivery. M.
- Faster while: condition listener re-plans the repeat row. M.
- Migration by cells with both orders, fixtures from a clean 1.0.0 instance. M.
- Message history timeline from the ledger. M.
- Panel: page, five blocks, type form, Check card. L.
- Overall L, most in the panel.

## 8. Risks and what the design gives up

- Biggest risk: severity loses its special power, and a type setting can silence alarms. Mitigation: Can wake people block, the Move box, and the warning before Save on any change that stops a type from sending as usual.
- Sections cannot be shared: a fallback used by four types is set four times. "Start from" copies it; it does not keep it in step.
- Sorting only by call field, watch rule, tag and severity. "Doorbell only from this sensor" needs the call to name the type.
- Migrated setups in "all" mode can show many joined names until merged.
- Named steps from YAML are a seam in "one type decides", kept for D-198.
- Gives up: list order, the two modes, per-policy matching, "critical passes" as a field, combining several behaviours on one message. Gains: no choice that changes mid-life (pain point 4), no shared single place (2), holds and sends with one owner (5), tags kept out by claiming them elsewhere (7), one place per type for strength (3).

## 9. Mockup

[policy-redesign-d.html](../mockups/policy-redesign-d.html), updated: the Types page with Try a message, Can wake people, Quiet times with the per-type choice list, type cards and the Check after the update card; and the Doorbell form with "Start from", the contested claim and Move box, the watch-rule claim, and When switched off.
