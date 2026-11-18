# Policy redesign, design B: goals, not policies

Round one, Designer B. Inputs: [fact sheet](00-fact-sheet.md), [users and stories](01-users-and-stories.md). Mockup: [policy-redesign-b.html](../mockups/policy-redesign-b.html). Sample names only.

Stance: the user writes down what they want to happen ("Wake the Admins for leaks", "Keep small things quiet at night"), one sentence per wish. Every sentence that fits a message acts. There is no list order and no mode to choose.

## 1. The mental model

"Every goal that fits a message does its part: some goals make it calmer, some make sure it arrives, and a 'gets through' goal beats every calm one for the people it names."

## 2. Vocabulary

Every term the user sees, English then German.

- Goals (page title) / Ziele
- Goal / Ziel
- Add a goal / Ziel hinzufügen
- Section "Always gets through" / "Kommt immer durch"
- Section "Keep it calm" / "Für Ruhe sorgen"
- Section "Make sure it arrives" / "Damit es ankommt"
- Section "Only when named" / "Nur wenn genannt"
- Goal kinds, as shown on each card:
  - Gets through / Kommt durch
  - Quiet times / Ruhezeiten
  - Presence / Anwesenheit
  - Summary / Zusammenfassung
  - Also send / Zusätzlich senden
  - Pass on / Weitergeben
  - Repeat / Wiederholen
  - If unreached / Wenn niemand erreicht
- Which messages / Welche Nachrichten
- Severities / Schweregrade
- Tags / Tags
- Except tags / Außer Tags
- Only if / Nur wenn
- Unless / Außer wenn
- Faster while / Öfter, solange
- Steps aside for / Lässt den Vortritt
- Reached someone / Hat jemanden erreicht
- Reacts (acknowledges) / Reagiert (bestätigt)
- Counts from / Zählt ab
- Own rhythm / Eigener Takt
- What will happen / Was passiert
- Check a message / Nachricht prüfen
- Show details / Details zeigen
- Converted from 1.0 / Aus 1.0 übernommen

Words removed from the page: policy, mode, "only the first", "all that apply", order, Move up, Move down, "Critical messages pass" (its job moves to a "Gets through" goal). The word "policy" stays in YAML keys and in the advanced details, shown as "Goal (policy in YAML)".

## 3. Structure

### What a goal is

A goal is one sentence with blanks. Each of the eight kinds has one sentence template; the blanks are the fields. One goal is one stored policy subentry with one switch entity (D-119, D-198). The seven 1.0 types keep their stored type key; one type is new.

- Gets through (new, `get_through`): "Wake [who] for [which messages]." Optional: "and also push it to them." These deliveries pass every "Keep it calm" goal for the people named. Who may be "whoever it is sent to" or named recipients, audiences or speakers.
- Quiet times (`quiet_hours`): "Keep [which messages] quiet [windows]: [wait until the end / go quietly / drop]." One goal holds any number of windows.
- Presence (`presence`): "Send [channels] for [which messages] only when [the recipient / somebody of an audience] is [in / not in] [zone], [unless ...]." Otherwise hold or drop, with a maximum wait (D-212).
- Summary (`summarize`): "Collect [which messages] into one summary [at a time / every N minutes]."
- Also send (`deliver`): "Also send [which messages] to [who] on [channels]."
- Pass on (`escalation`): "If nobody reacts to [which messages] within [N minutes] after it reached someone, tell [who] on [channels]."
- Repeat (`reminder`): "Repeat [which messages] every [N minutes] until someone reacts, at most [M] times, [faster while ...]."
- If unreached (`fallback`): "If [which messages] reach nobody, send them to [who] on [channels]."

I considered goals that build several hidden policies ("Wake me for leaks" writing a Deliver policy plus a pass flag on every quiet policy) and rejected it: hidden pieces break D-198 entity IDs, confuse Ben's YAML and cannot be explained when something goes wrong. A goal is exactly what it says and nothing more.

### The Goals page

One page, four sections, always in this order and never reordered by the user:

1. Always gets through. Placed first so Chris sees in one look what may wake people. Each card shows its sentence, for example "Wakes Admins for warnings tagged leak".
2. Keep it calm. Quiet times, Presence, Summary.
3. Make sure it arrives. Also send, Pass on, Repeat, If unreached.
4. Only when named. Goals that act only when an automation or watch rule names them (`apply: manual`), with the entity ID shown.

Each card: kind label in text (never colour alone), the sentence, an on/off switch with an aria label naming the goal, and short notes in text such as "Converted from 1.0" or "Steps aside for Evening summary". No drag handles, no Move up or Move down. Ordering needs no keyboard or touch design because there is none.

Above the sections, "Check a message": pick a severity, tags, a time, who is home and where the message comes from (automation or watch rule). The page lists, in time order, what happens and which goal causes each step. This answers Q1 and S12 without opening a form. The same timeline, filled from the ledger, sits in each message's history entry and answers Q2 ("Held until 07:00 by Night quiet; 'Leak' would have let it through, but it is off").

"Show details" (one switch for the page) adds to every card the type key, the switch entity ID, every stored field and a copy button for the YAML that names it. That is Ben's exact view; it is the same goals, not a second model.

### The form of one goal

- Top: the sentence, with each blank as a button showing its current value ("warnings", "every 1 h"). Tapping a blank moves focus to its field below. Screen readers read the sentence as text and the buttons as "Change which messages: warnings".
- Fields below in a fixed order, so the form still works when a language orders the sentence differently: Which messages (severities, tags, except tags), then the kind's own fields, then "More options" (only if, unless, faster while, counts from, own rhythm, steps aside for, only when named).
- "What will happen", live before Save: the sentence of this goal; every other goal that fits the same messages, with one sentence on how they combine where they meet; and a sample timeline for one message the user can change (severity, tag, time, condition values).
- A wide "Gets through" goal (no tag, or info and success included) shows a note: "This can wake people for everyday messages."

### Strength and order

There is no order. Strength is said in words in three places only: the section a goal sits in, the "Gets through" kind, and an explicit "Steps aside for [goal]" line, which is rare and mostly comes from migration.

## 4. Conflict rules

1. Every goal that fits a message acts, except one that steps aside for a goal that is on and also fits; for repeats the message keeps one rhythm, the shortest that fits at that moment, unless a repeat goal has its own rhythm.
2. A delivery, including a summary, repeat, pass-on or fallback, goes out only when every calm goal that fits it lets it go, is dropped if any of them drops it, goes quietly if any says quietly, and passes all of them for the people a "Gets through" goal names.
3. Waiting times for "Pass on" and "Repeat" count from the moment the message first reached someone (the banner counts only when it is the message's only channel), so nobody is passed on or reminded about a message that is still held.

## 5. The twelve scenarios

Scenario 1, leak at 03:00.
- Configure: Gets through "Wake Admins for warnings tagged leak, and also push it to them." Quiet times "Keep info and success quiet every night 22:00 to 07:00: go quietly."
- Happens: the leak warning matches the first goal. The push to the Admins passes every calm goal and rings at once. An info message at 03:00 is only matched by the quiet goal and arrives quietly. The leak goal sits at the top of the page, so S1's "visible without opening a form" holds. Nothing is marked critical.

Scenario 2, two quiet windows.
- Configure: one Quiet times goal for info and success with two windows: "nights starting Sunday to Thursday 22:00 to 07:00" and "nights starting Friday and Saturday 23:00 to 09:00", go quietly.
- Happens: both windows work side by side. The editor writes "The second window covers Friday and Saturday nights; it does not overlap the first." A warning is not in Which messages and is not affected. Two separate goals would behave the same (rule 2), and the preview would say so.

Scenario 3, doorbell spoken only when someone is home.
- Configure: Presence "Send speech for messages tagged doorbell only when somebody of Household is in Home, unless Guest mode is on. Otherwise drop."
- Happens: nobody home and guest mode off: speech is dropped; push is not a channel of this goal and goes out. Guest mode on: the goal does not act and speech plays. Night quiet keeps acting on other messages, because every goal that fits acts. At night an info doorbell is also matched by Night quiet and is not spoken; the preview shows that.

Scenario 4, critical pushed and repeated.
- Configure: Gets through "Wake Admins for critical messages, and also push it to them." Repeat "Repeat critical messages every 10 minutes until someone reacts, at most 12 times."
- Happens: the push goes out at once; the clock for repeats starts with that push. Repeats every 10 minutes also pass every calm goal for the Admins. Neither blocks the other. An acknowledgement on any device ends the repeats.

Scenario 5, "faster while X".
- Configure: one Repeat goal "Repeat warnings every 1 h until someone reacts, at most 6 times, every 15 minutes while X is on (at most 12 times)." Two separate repeat goals (1 h; 15 minutes only if X) give exactly the same result by rule 1.
- Happens, minute by minute: 0, message reaches Anna, rhythm 1 h, next repeat planned at 60. 15, X turns on, the rhythm becomes 15 minutes, the next repeat is recalculated as last delivery plus 15 = 15, which is due, so repeat 1 goes out now. Then 30, 45. At 50 X turns off: the rhythm is 1 h again, next is 45 plus 60 = 105.
- The count belongs to the message and never resets. Each rhythm has its own limit; when the count reaches the limit of the rhythm in force, repeats stop. The form says so in "What will happen", and the message history shows "Repeat 3 of 12, every 15 minutes because X is on".
- Why this closes pain point 4: "only if" no longer chooses which goal holds the single place; it only changes the rhythm, which is planned again at every step from the goals that fit at that moment.

Scenario 6, shopping list when leaving.
- Configure: Presence "Send push for messages tagged shopping only when the recipient is not in Home. Otherwise hold until that changes."
- Happens: held for Anna while she is home, sent when she leaves (after the presence delay). The check is per recipient, so Ben, who is away, gets it at once. Messages without the tag are untouched.

Scenario 7, digest at 20:00.
- Configure: Summary "Collect messages tagged digest into one summary at 20:00."
- Happens: digest messages are collected when they appear; no other calm goal touches them, because they are not delivered. At 20:00 the summary is one delivery and passes rule 2; Night quiet starts at 22:00 and does not touch it. Info messages without the tag are not collected.

Scenario 8, nobody could be reached.
- Configure: If unreached "If any message reaches nobody, send it to Household speakers on speech."
- Happens: the fallback is a delivery and passes the calm goals (rule 2). For an info message at night Night quiet keeps the speakers silent, and the form says so: "At night, Night quiet keeps this silent for info and success. Messages a 'Gets through' goal names are spoken." For a leak covered by a "Gets through" goal whose who includes Household speakers, it is spoken.

Scenario 9, escalation for a held message.
- Configure: Pass on "If nobody reacts to warnings within 30 minutes after it reached someone, tell Admins on push." Night quiet covers warnings with "wait until the end".
- Happens: a warning at 23:00 is held until 07:00 for everyone. It has reached nobody, so the 30 minutes start at 07:00; Admins are told at 07:30 if nobody reacted. The rule is in the goal's sentence. Chris can choose otherwise in More options, "Counts from: when the message was created"; the pass-on then fires at 23:30 and is itself held by Night quiet unless a "Gets through" goal names it.

Scenario 10, critical watch-rule message to phones.
- Configure: the same goal as scenario 4, "Wake Admins for critical messages, and also push it to them."
- Happens: the watch-rule message (banner only, tag `rule`) matches by severity and gets the push. Same goal, same switch, no YAML (rule 9 parity).

Scenario 11, 1.0.0 starter list plus one Away policy (Which messages empty, stored order Summarize, Quiet hours, Away, Reminder, Deliver, mode first).
- What 1.0 does: digest info goes to Evening summary; other info and success to Night quiet; warning and critical to Away, because Away matches everything and is earlier. Warning reminder and Critical delivery therefore never act.
- After conversion: Evening summary unchanged. Night quiet "steps aside for Evening summary". Presence (from Away) steps aside for Evening summary and Night quiet. Warning reminder and Critical delivery step aside for Presence. A new goal "Critical messages get through" lists the goals that had critical messages pass. Every message gets the same deliveries as before.
- Visible: a note on top, "3 goals keep 1.0 behaviour with 'steps aside'. Review", and on Critical delivery "Never acts: Presence fits every critical message first (kept from 1.0)". One button per note offers the new behaviour with a preview.

Scenario 12, a second overlapping goal.
- Configure: Anna adds Quiet times "Keep info quiet 21:00 to 23:00: wait until the end" next to Night quiet (info and success, 22:00 to 07:00, quietly).
- Happens before Save: "What will happen" says "Where both fit (info, 22:00 to 23:00), the calmer one decides: info waits until 23:00, then goes quietly because Night quiet still applies." The sample timeline shows an info message at 22:30 arriving quietly at 23:00. Nothing is blocked (D-151).

## 6. Migration from 1.0.0 (D-213)

Storage stays in config subentries. The config entry minor version is raised once.

- Summarize, Quiet hours, Deliver, Escalation, Reminder, Fallback: same type key and fields; shown as Summary, Quiet times, Also send, Pass on, Repeat, If unreached.
- Away: becomes `presence` with the D-212 defaults (D-214); shown as Presence.
- `critical_passes` and `include_critical`: one new "Gets through" goal "Critical messages get through", who "whoever it is sent to", listing exactly the calm goals that let critical pass. Goals with the field off are not listed. The stored fields stay, so a downgrade reads them.
- Mode "first": for each automatic policy in `policy_order`, migration writes "steps aside for" with every earlier automatic policy whose Which messages can overlap it (severities intersect and tags compatible). A goal steps aside only while the other is on and fits, which matches 1.0, where a switched-off policy was skipped. Goals with no overlap get no line. Where the subtraction is exact as an "except tags" line (as for Night quiet against Evening summary), the page offers that as a one-click rewrite, never automatically.
- Mode "all": no "steps aside". Overlapping reminders get "own rhythm" so each keeps repeating as before.
- All converted Pass on and Repeat goals get "counts from: when the message was created", the 1.0 timing. New goals default to "after it reached someone".
- `policy_order` and `policy_mode`: kept in storage, no longer read after conversion, not shown.
- `apply: manual`: the goal moves to "Only when named"; behaviour unchanged.
- Named policies in `notify` calls and watch rules: entity IDs unchanged; a named goal still adds to automatic ones in calls (D-189) and replaces them in watch rules (D-145).

Visible changes: page title, section layout, wording, the new top goal, "steps aside" lines. Behaviour changes: none at conversion. Changes happen only when the user accepts an offer; each offer is listed in the CHANGELOG with its way back: put the "steps aside" line back, set "counts from" back to "created", switch "own rhythm" on, or remove the "Gets through" goal and switch the legacy pass field on.

## 7. Engine impact

- Every matching goal acts (`PolicyBook.for_message` returns all, minus steps-aside): reuses the "all" path. S.
- "Steps aside for" and "except tags" in matching: S.
- "Unless" as a negated "only if" (D-216 shape): S.
- Quiet times with several windows in one goal: reuses "several windows, strictest wins". S.
- "Gets through" type: chain stages ask "is this delivery to this person passed?" instead of reading `critical_passes`; also send reuses Deliver. M.
- One shared repeat rhythm per message: one timer row per message, planned again at every step from the goals that fit; reuses `_drop_inapplicable_timers` and "overdue fires once"; count kept on the message. M.
- Counting from first reach: arm pass-on and repeat timers on the first delivery to a person instead of on appearance; restart rules unchanged. M.
- Migration (steps-aside computation, the new goal, timing flags): M.
- "Check a message" and the form preview: a dry run of matching and chain for a sample message, time and state, via one websocket command; the same code fills the message history timeline. L.
- Panel: Goals page, sentence forms, details view, removal of ordering. L.

## 8. Risks and what the design gives up

- Biggest risk: sentence templates in four languages. German and French reorder blanks; a sentence with buttons inside can read badly or overflow at 380 px. Mitigation: whole-sentence translations with named blanks, fields always present below in a fixed order, and a plain-text fallback if a translation lacks the template.
- "Every goal acts" surprises users who relied on one policy shadowing another. The preview and "Check a message" carry this; there is no order to fall back on.
- "Gets through" is strong: a wide one wakes people for everyday messages. The page puts these goals first and warns about wide ones; it cannot stop a determined admin.
- Converted setups carry "steps aside" lines that read oddly ("Critical delivery never acts") until the user accepts the offer. That is honest about 1.0 behaviour, but the first look after the upgrade is busier.
- "Counts from first reach" is a new idea for escalation timing; defining "reached" (banner only counts alone) needs care in docs.
- Given up: drag-and-drop order, the "only the first" mode, per-policy "Critical messages pass" as the way through (still stored, no longer edited), and goals that generate several policies.
