# Policy redesign, design B v2: goals, not policies

Round two, Designer B. Inputs: [fact sheet](00-fact-sheet.md), [users and stories](01-users-and-stories.md), [v1](design-b-v1.md) and the reviews [by A](review-by-a.md), [by C](review-by-c.md) and [by D](review-by-d.md). Mockup, updated in place: [policy-redesign-b.html](../mockups/policy-redesign-b.html). Sample names only.

What makes B different, and what v2 sharpens: the user writes outcomes, and each outcome is a promise the page checks. Every goal card says whether its promise holds against all other goals ("Kept", or "Bent for doorbell messages by 'Doorbell may wake'"). A conflict is never resolved by a hidden order. It is shown as the promise that gives way and the goal that bends it, on both cards.

## A. Answers to the reviews

All three reviews arrived; none was missing.

Raised by A:
- A1, scenario 11 computed on the wrong order. Fixed. The introduction creates Critical delivery, Warning reminder, Evening summary and Night quiet in that order (`welcome.py`), and an Away policy added later is appended last. In mode "first" that Away policy acts on nothing; Warning reminder and Critical delivery do act. Section 5, scenario 11 now walks this case, and the case where the order was stored with Away earlier. Migration always computes from the stored `policy_order`, so both cases convert exactly.
- A2, "Gets through" names people, so naming Household speakers passes Presence and speaks into an empty house. Fixed. A "Gets through" goal now says which kinds of calm goal it passes: Quiet times and Summary by default, Presence only when ticked. Section 3 explains why Presence is off by default: Presence is about whether a message is useful where people are, not about how loud it is.
- A3, "Steps aside" is an order in disguise and rule 1 has two exceptions. Fixed. "Steps aside for" is no longer offered for new goals. It exists only on converted goals, shown as part of Which messages ("not for messages Evening summary collects, kept from 1.0"), and has a "Restore 1.0 links" way back. Ben's "everything except digest" is "Except tags: digest". The conflict rules are rewritten without exceptions (section 4).
- A, sentence templates in four languages. Fixed by changing the form (section 3): the sentence becomes a vertical form whose lines follow the translated sentence. The mockup shows the German form next to the English one.
- A, quiet windows list changes the stored shape. Accepted with a limit. Stored `windows` is a list; the first window is also written to the 1.0 keys `from_time`, `to_time` and `days`, so a downgrade reads the first window and ignores the others. This is stated in the CHANGELOG line.

Raised by C:
- C1, language and focus jumps. Fixed as for A: no inline buttons, fields in the order of the translated sentence.
- C2, the migrated "Critical messages get through" passes a list of old goals, so a new quiet goal holds critical. Fixed. A "Gets through" goal passes kinds of calm goal, never a list, so a new Quiet times goal is passed from its first save. A converted calm goal that had `critical_passes` off gets the visible line "Holds these even when a goal says they get through". New goals never get it by default. The "Always gets through" section lists every goal that carries this line.
- C3a, two places to change who gets the leak push. Fixed. "Gets through" has one optional send ("and push it to [who]"), and a scope: "everyone it reaches" or "only the people this goal sends to". The leak push and the leak permission now live in one goal. When an Also send goal sends the same messages to the same people, both cards show "Also sent by …".
- C3b and D2b, per-rhythm limits stop repeats unpredictably. Fixed. Inside one Repeat goal, "faster while" shares one count and one limit ("at most 12 repeats in all"). Separate Repeat goals each count only their own repeats. The form states the last possible repeat.

Raised by D:
- D1, who may be woken has to be kept in step with every sending goal. Fixed by the scope default "everyone it reaches": a pass-on to Ben or a fallback to the speakers added later is passed too. Narrowing to "only the people this goal sends to" is a deliberate choice, and the card then says "Others it reaches stay quiet at night".
- D2a, a wide "Repeat every 5 min" silently overrides Ben's hourly rhythm. Accepted, with the promise check as mitigation. The shortest rhythm in force is kept because a faster repeat is the more urgent wish. The overlap now shows on both cards, not only in the editor of the new goal: "Bent for warnings tagged pump: 'Every 5 min' repeats faster".
- D3, sentence is a second rendering of the same form. Fixed: the sentence is the form.

Found by me while reviewing A: the 1.0 engine skips a reminder in a "wait" window instead of holding it, and Away never holds a reminder. v1 left both out of the rules. Fixed: rule 2 now says a repeat is skipped where another delivery would wait. Converted Presence goals keep "repeats not checked" (section 6).

## B. Taken from others

- From A: "Except severities" next to "Except tags". The post-upgrade check list with the buttons "Keep as before" and "Let it act". Also A's finding on the stored order, used in scenario 11.
- From C: "Restore 1.0 links", which recomputes the converted "not for messages … collects" lines from the kept `policy_order`. Also one count and one limit inside one rhythm with "faster while".
- From D: the before-Save warning when a change takes protection away. In B it covers switching off, narrowing or deleting a "Gets through" goal, and adding "Holds these even when a goal says they get through". Also D's "says why" in the checker ("because it is tagged leak").
- Not taken: A's band by message class, C's plans bundling sends, D's one type per message. These are their models, not mechanics.

## 1. The mental model

"You write down what you want in plain sentences; each one is a promise, and the page tells you whether every promise holds, and if not, which other goal bends it."

## 2. Vocabulary

English then German.

- Goals / Ziele (page title); Goal / Ziel; Add a goal / Ziel hinzufügen
- Sections: Always gets through / Kommt immer durch; Keep it calm / Für Ruhe sorgen; Make sure it arrives / Damit es ankommt; Only when named / Nur wenn genannt
- Goal kinds: Gets through / Kommt durch; Quiet times / Ruhezeiten; Presence / Anwesenheit; Summary / Zusammenfassung; Also send / Zusätzlich senden; Pass on / Weitergeben; Repeat / Wiederholen; If unreached / Wenn niemand erreicht
- Promise status: Kept / Eingehalten; Bent for … by … / Gebrochen für … durch …; Never acts / Wirkt nie
- Which messages / Welche Nachrichten; Severities / Schweregrade; Tags / Tags; Except severities / Außer Schweregrade; Except tags / Außer Tags
- Only if / Nur wenn; Unless / Außer wenn; Faster while / Öfter, solange
- Passes / Übergeht (with Quiet times, Summary, Presence)
- For: everyone it reaches / Für alle, die sie erreicht; only the people this goal sends to / nur für die, an die dieses Ziel sendet
- Holds these even when a goal says they get through / Hält sie auch, wenn ein Ziel sie durchlässt
- Reached someone / Hat jemanden erreicht; Counts from / Zählt ab
- Check a message / Nachricht prüfen; Show details / Details zeigen
- Converted from 1.0 / Aus 1.0 übernommen; Keep as before / Wie bisher lassen; Let it act / Wirken lassen; Restore 1.0 links / 1.0-Verknüpfungen wiederherstellen

Removed from the page: policy, mode, order, Move up, Move down, "only the first", "Critical messages pass", and "Steps aside" for new goals. "Policy" stays in YAML keys and in Show details as "Goal (policy in YAML)".

## 3. Structure

### What a goal is

A goal is one outcome sentence, stored as one policy subentry with one switch entity (D-119, D-198). The seven 1.0 type keys stay; `get_through` is new.

- Gets through: "Let [which messages] through [Quiet times, Summary; Presence only if ticked] for [everyone it reaches / only the people this goal sends to], and push it to [who] (optional)."
- Quiet times: "Keep [which messages] quiet [windows]: [wait until the end / go quietly / drop]."
- Presence: "Send [channels] for [which messages] only when [the recipient / somebody of an audience] is [in / not in] [zone]; otherwise [hold / drop], at most [wait], [unless …]."
- Summary: "Collect [which messages] into one summary [at a time / every N minutes]."
- Also send: "Also send [which messages] to [who] on [channels]."
- Pass on: "If nobody reacts to [which messages] within [N minutes] after it reached someone, tell [who] on [channels]."
- Repeat: "Repeat [which messages] every [N minutes] until someone reacts, at most [M] times in all, [every K minutes while …]."
- If unreached: "If [which messages] reach nobody, send them to [who] on [channels]."

"Add a goal" opens a list of outcomes in plain words, grouped as "Wake people for …", "Keep … quiet", "Only when someone is home", "Collect into a summary", "Make sure someone reacts". Ready-made outcomes fill the fields: "Wake the Admins for leaks", "Quiet nights for small things", "Speak only when someone is home", "Summarize digest at 20:00". One outcome is always one goal.

Why "Gets through" passes Presence only when ticked: Quiet times and Summary are about volume and timing, and an alarm should beat both. Presence is about whether a delivery is useful where people are. A leak spoken into an empty house helps nobody, while a push to an away Admin is never held unless a Presence goal says so.

### The form is the sentence

The translation of each kind is a sentence with named blanks. The form renders it as a column: each line is a fragment of the sentence as the label, with the field below it, in the order of the sentence in the current language.

English Pass on: "If nobody reacts to" [warnings] / "within" [30 minutes] / "after it reached someone, tell" [Admins] / "on" [push].

German Pass on: "Wenn niemand reagiert auf" [Warnungen] / "innerhalb von" [30 Minuten] / "nachdem sie jemanden erreicht hat, informiere" [Admins] / "über" [Push].

Reading down the column reads the sentence. The field order changes per language, focus order follows it, and nothing wraps inline at 380 px. Optional parts (only if, unless, except, faster while, counts from) sit under "More options" as further lines of the same sentence. Screen readers read each label with its field.

### The Goals page

1. Check a message: severity, tag, time, who is home, source (automation or watch rule). It lists in time order what happens, which goal does it and why ("because it is tagged leak"). The same timeline, filled from the ledger, is in each message's history and answers Q2 ("Held until 07:00 by Night quiet; 'Leak' would have let it through, but it is off").
2. Converted from 1.0 (only after an upgrade, until dismissed): goals whose behaviour is kept by a 1.0 link, with "Keep as before" and "Let it act".
3. Always gets through, then Keep it calm, then Make sure it arrives, then Only when named. These sections are fixed, and there is no user order.

Each card shows the kind in text, the sentence, the on/off switch (aria label names the goal) and the promise line:
- "Kept."
- "Bent for doorbell messages at night: 'Doorbell may wake' lets them through."
- "Never acts: Night quiet and Critical delivery take all its messages first (kept from 1.0)."

The line is computed by the same dry run as Check a message, over every severity, every tag any goal names and a week of times. "Show details" adds the type key, entity ID, stored fields and YAML.

The "Always gets through" section header lists, in words, every goal that holds messages anyway ("Night wait holds critical messages anyway, from 1.0"). Chris finds everything that can wake him, or that stops him being woken, in one section.

## 4. Conflict rules

1. Every goal whose Which messages fits acts; where several act on one delivery, the calmest wins (drop, then wait, then quietly), and a message keeps one repeat rhythm, the shortest that fits at that moment.
2. A "Gets through" goal lets its messages pass the kinds of calm goal it names, for the people it covers, except a calm goal that says "Holds these even when a goal says they get through"; for a repeat, waiting means skipping it.
3. Pass on and Repeat count from the first delivery that reached a person (the banner counts only when it is the message's only channel), unless the goal says "counts from when the message was created".

"Which messages" covers severities, tags, except severities, except tags, only if, unless, and, on converted goals only, "not for messages that [goal] takes". None of these is an exception to the rules; they decide whether a goal fits.

## 5. The twelve scenarios

Scenario 1, leak warning at 03:00.
- Configure: from "Wake the Admins for leaks": Gets through "Let warnings tagged leak through Quiet times and Summary for only the people this goal sends to, and push it to Admins." Quiet times "Keep info and success quiet every night 22:00 to 07:00: go quietly."
- Happens: at 03:00 the push to the Admins passes and rings. Anna, in the automation's audience, gets it quietly if a quiet goal covers warnings, because the goal covers only the Admins. An info message is quiet. The leak card is first on the page, and Night quiet's promise line says "Kept".

Scenario 2, two windows.
- Configure: one Quiet times goal, info and success: "nights starting Sunday to Thursday 22:00 to 07:00", "nights starting Friday and Saturday 23:00 to 09:00", go quietly.
- Happens: both windows work. The form says the second window adds Friday and Saturday nights and does not overlap. Warnings are outside Which messages.

Scenario 3, doorbell.
- Configure: from "Speak only when someone is home": Presence "Send speech for messages tagged doorbell only when somebody of Household is in Home; otherwise drop; unless Guest mode is on."
- Happens: nobody home, guest mode off: no speech, push goes out. Guest mode on: the goal does not fit, speech plays. Night quiet keeps acting; its card says "Kept".

Scenario 4, critical pushed and repeated.
- Configure: Gets through "Let critical messages through Quiet times and Summary for everyone it reaches, and push it to Admins." Repeat "Repeat critical messages every 10 minutes until someone reacts, at most 12 times in all."
- Happens: the push goes at once and starts the clock. Repeats every 10 minutes pass Quiet times too, because the scope is everyone it reaches. An acknowledgement on any device stops them.

Scenario 5, faster while X.
- Configure: Repeat "Repeat warnings every 1 h until someone reacts, at most 12 times in all, every 15 minutes while X is on."
- Happens: minute 0, delivery, next at 60. Minute 15, X on: the next repeat is last delivery plus 15, which is due, so repeat 1 goes now. Then 30 and 45. Minute 50, X off: next at 45 plus 60 = 105. One count, one limit of 12 for both rhythms. The form says "The last repeat comes after 12 repeats at the latest, whatever the rhythm."
- Two separate goals (1 h at most 6; 15 minutes only if X, at most 12): the shorter rhythm in force sets the time, and each goal counts only its own repeats. The form says "At most 6 hourly and 12 fast repeats". Both cards show "Bent while X is on: 'Fast' repeats faster".

Scenario 6, shopping list.
- Configure: Presence "Send push for messages tagged shopping only when the recipient is not in Home; otherwise hold."
- Happens: held for Anna while home, sent when she leaves. Checked per recipient. Untagged messages are untouched.

Scenario 7, digest.
- Configure: Summary "Collect messages tagged digest into one summary at 20:00."
- Happens: collected messages are not delivered, so no other calm goal touches them. They start no Also send, Pass on or Repeat (as in 1.0). The summary at 20:00 is one delivery under rule 1. Night quiet's card says "Kept"; Evening summary's says "Kept".

Scenario 8, nobody reached.
- Configure: If unreached "If any message reaches nobody, send it to Household speakers on speech."
- Happens: for an info message at night, Night quiet keeps the speakers silent, and the card says so ("Bent for info and success at night: Night quiet keeps it quiet"). For a leak, the scenario 1 goal passes only the Admins, so the speakers stay quiet unless Chris widens it to "everyone it reaches". With that scope Quiet times is passed, but Presence is not ticked, so in an empty house nothing is spoken. The form shows both outcomes before Save.

Scenario 9, pass on while held.
- Configure: Pass on "If nobody reacts to warnings within 30 minutes after it reached someone, tell Admins on push." Night quiet covers warnings with "wait until the end".
- Happens: a warning at 23:00 waits until 07:00 and has reached nobody; Admins are told at 07:30 if nobody reacted. "Counts from when the message was created" instead gives 23:30, and that delivery waits too unless a "Gets through" goal covers it.

Scenario 10, critical watch-rule message.
- Configure: the scenario 4 goal.
- Happens: the rule message (tag `rule`) fits by severity and is pushed to the Admins. Same goal and switch, no YAML.

Scenario 11, 1.0 starter list plus Away, mode "first".
- Stored order from the introduction, Away added later: Critical delivery, Warning reminder, Evening summary, Night quiet, Away (Which messages empty, `critical_passes` on everywhere).
- 1.0 behaviour: critical goes to Critical delivery, warning to Warning reminder, digest info and success to Evening summary, other info and success to Night quiet. Away acts on nothing.
- Converted:
  - Night quiet: "not for messages Evening summary takes".
  - Presence (from Away): "not for messages that Critical delivery, Warning reminder, Evening summary or Night quiet take", promise line "Never acts (kept from 1.0)".
  - The other goals are unchanged.
  - Every hold let critical through, so a goal "Let critical messages through Quiet times, Summary and Presence for everyone it reaches" is added, with no send.
- Every message gets the same deliveries. The "Converted from 1.0" list shows Presence with "Keep as before" and "Let it act" (with preview), and Night quiet with "Use 'except tag digest'".
- If the order had been stored with Away before Reminder and Deliver, the same algorithm gives Warning reminder and Critical delivery "Never acts", and Presence acts on warning and critical.

Scenario 12, second overlapping goal.
- Configure: Anna adds Quiet times "Weekend lie-in" (info, Saturday and Sunday 06:00 to 10:00, wait).
- Happens before Save: the new goal's promise line and Night quiet's are computed live: "Where both fit (info, Saturday and Sunday 06:00 to 09:00) the calmer one wins: info waits until 10:00. Night quiet: bent there by Weekend lie-in." The critical goal's line stays "Kept", because Gets through passes the kind Quiet times. Nothing blocks Save (D-151).

## 6. Migration from 1.0.0 (D-213)

- The seven types keep their keys; `away` becomes `presence` (D-214). `apply: manual` goes to "Only when named". Entity IDs, named policies in calls (D-189) and watch rules (D-145) are unchanged.
- `critical_passes` and `include_critical`: one Gets through goal for critical messages, passing the kinds where every hold of that kind let critical through. A hold whose field was off gets "Holds these even when a goal says they get through". The stored fields stay for a downgrade.
- Mode "first": each automatic policy gets "not for messages that [earlier overlapping automatic policies] take", computed from `policy_order`. The link follows the other goal's switch, as 1.0 did. "Restore 1.0 links" recomputes the links from the kept `policy_order`.
- Mode "all": no links. Overlapping reminders get "own rhythm" so each repeats as before.
- Converted Pass on and Repeat: "counts from when the message was created". Converted Presence: "repeats not checked". Both match 1.0 timing.
- Quiet windows: stored as a list, with the first window mirrored to the 1.0 keys.
- `policy_order` and `policy_mode` are kept, no longer read except by "Restore 1.0 links".

Nothing changes at upgrade. Each "Let it act" or rewrite is a user step, listed in the CHANGELOG with its way back: restore the link, set "counts from" back, tick "own rhythm" or "repeats not checked".

## 7. Engine impact

- Every fitting goal acts (`for_message` "all" path), with except severities, except tags, unless and converted links: S.
- Gets through: stages ask whether a delivery to this person is passed for their kind; reads the legacy fields for converted entries: M.
- Shared repeat rhythm with per-goal counts, one count inside a faster-while goal; reuses timer rows, `_drop_inapplicable_timers`, overdue fires once: M.
- Counting from first reach (arm on first delivery to a person or on release): M.
- Quiet windows list with legacy mirror: S.
- Migration with links, the critical goal and timing flags: M.
- Dry run for Check a message, history timeline and promise lines over the severity × tag × week grid: L. The grid is small (four severities, the tags goals name, about 336 hour slots per week), computed in the panel's websocket call on page load and after each edit.
- Panel with sentence-column forms in four languages: L.

## 8. Risks and what the design gives up

- Biggest risk: promise lines that are wrong or too long. They are computed, not written, and a slow or misleading line breaks trust in the whole page. They need tests per scenario and a short form ("Bent for 2 kinds of message: see Check a message").
- Sentence columns need careful translation: each language's template must split into fragments that make sense as labels.
- "Gets through" is strong; the before-Save warning and the first section do not stop a determined admin.
- Given up: user order, the two modes, "Steps aside" for new goals, per-goal "Critical messages pass", goals that build several policies, and a downgrade that keeps more than the first quiet window.
