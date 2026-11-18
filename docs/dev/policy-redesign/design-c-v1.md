# Policy redesign, design C (clean slate), version 1

Designer C. Started from the stories and the twelve scenarios, not from the seven types. Mockup: [policy-redesign-c.html](../mockups/policy-redesign-c.html). Sample names only.

## 1. Mental model

Plans say what is sent and when; house rules say when the house holds back; a step that must get through says so itself.

The seven types collapse into two kinds of policy that never compete with each other:

- A **plan** is the journey of a message: what goes out at once, what happens if nobody reacts, how it repeats, and where it goes if nobody could be reached. Plans only ever add.
- A **house rule** is a limit the house sets: quiet times, presence, summaries. House rules only ever hold back.

Strength is not a place in a list. It is a visible mark on a single step: "Passes quiet times", "Passes presence rules". There is no list order and no mode.

## 2. Vocabulary (English / German)

- Policies / Richtlinien (page title; the umbrella word, also used in calls)
- Plans / Pläne; Plan / Plan
- House rules / Hausregeln; House rule / Hausregel
- Step / Schritt
- At once / Sofort
- If nobody reacts within … / Wenn niemand reagiert innerhalb …
- Repeat every … / Wiederholen alle …
- Faster while … / Schneller solange …
- At most … times / Höchstens … Mal
- If nobody could be reached / Wenn niemand erreicht wurde
- Send to / Senden an
- Passes quiet times / Übergeht Ruhezeiten
- Passes presence rules / Übergeht Anwesenheitsregeln
- Count from: when it went out / when it appeared / Zählen ab: Versand / Erscheinen
- Quiet times / Ruhezeiten
- Presence / Anwesenheit
- Summary / Zusammenfassung
- Wait until the end / Bis zum Ende warten
- Send quietly / Leise senden
- Drop / Verwerfen
- Hold until … / Zurückhalten bis …
- Which messages / Welche Nachrichten
- Severity / Dringlichkeit
- With tags / Mit Tags
- Not with tags / Nicht mit Tags
- Critical messages pass / Kritische Nachrichten kommen durch
- Only if / Nur wenn
- Runs: automatically / only when named / Läuft: automatisch / nur wenn genannt
- In words / In Worten
- Also acting on these messages / Wirkt auch auf diese Nachrichten
- Try a message / Nachricht ausprobieren
- Can wake people / Kann Leute wecken
- Steps back for … (1.0.0) / Tritt zurück hinter … (1.0.0)
- Converted from 1.0.0 / Aus 1.0.0 übernommen

French and Spanish follow the same short forms ("Plans / Planes", "Règles de la maison / Reglas de la casa", "Passe les heures calmes / Pasa las horas de silencio"). No label relies on a word like filter, precedence or priority.

## 3. Structure

### The Policies page
Four blocks, top to bottom, all single column at 380 px:

1. **Try a message.** Severity, tags, a time and "somebody home: yes, no". The answer is the journey in plain lines: "At once: push to Admins (passes Night quiet). 07:00: banner and push to everyone else (Night quiet waits until the end)." This answers Q1 without docs. It is a dry run of the same matching and chain the engine uses.
2. **Can wake people.** One line per step that passes quiet times, with the plan name and the messages it acts on, for example "Leaks: at once, push to Admins". Chris sees at a glance what may ring at 03:00 and notices a change made by someone else (S1).
3. **Plans: what is sent, and when.** One card per plan: name, switch, a "Which messages" line, then its steps as a short timeline ("At once", "After 10 min", "Every 15 min", "If nobody reached"). Each step that passes a house rule carries a text badge with an icon ("Passes quiet times"), never colour alone.
4. **House rules: when the house holds back.** One card per rule: name, switch, kind (Quiet times, Presence, Summary), "Which messages", and the effect in words ("weekdays 22:00 to 07:00, weekends 23:00 to 09:00: send quietly").

There are no drag handles and no Move up or Move down, because nothing depends on order. Cards sort by kind, then by name.

### The form of a plan
- Name.
- **Which messages**: severity chips, With tags, Not with tags, Only if (the `notify` condition shape, D-216), Runs: automatically / only when named.
- **Steps**, each one card, added with "Add a step":
  - At once: send to channels and recipients (or "from the call", D-181).
  - If nobody reacts within N minutes: send to …; dismissal counts as a reaction (yes, no).
  - Repeat every N minutes, Faster while (condition) every M minutes, At most K times; on all channels already used or on chosen ones.
  - If nobody could be reached: send to …; when the audience was empty, sending failed, or both.
  - Every step has "Passes: [Quiet times] [Presence rules]" (two toggle chips, off by default). Timed steps also have "Count from: when it went out / when it appeared".
- **In words**: one sentence per step, built from the fields.
- **Also acting on these messages**: every other plan and house rule that fits the same messages, each with one sentence of what happens together (S12). Shown live, before Save; never blocks (D-151).

### The form of a house rule
- Name, kind (fixed after creation).
- Which messages: severity chips, With tags, Not with tags, "Critical messages pass" (D-211, on by default), Only if, Runs.
- Channels it acts on (Quiet times and Presence; a Summary holds the whole message, D-105).
- What it does: for Quiet times one or more windows (from, to, days) and the action (wait until the end, send quietly, drop); for Presence the D-212 fields (zone, recipient in or not in, nobody or somebody of the audience for speech, hold until it changes or drop, maximum wait then send or drop); for Summary every N minutes or at a time.
- In words, and Also acting on these messages, as for plans.

### Order and strength
- Order: none. Every policy that fits acts.
- Strength between house rules: the strictest action wins on one delivery (drop, then wait, then send quietly). This is the 1.0.0 rule for several quiet windows, extended to all house rules.
- Strength of a send against a hold: only the step's "Passes" mark. Severity has no hidden power; "Critical messages pass" is a visible field in Which messages and can be switched off.

## 4. Conflict rules

1. Every plan that fits a message adds its steps; plans never cancel or replace each other.
2. Every house rule that fits applies, and where several act on one delivery the strictest wins (drop, then wait, then send quietly); only a step marked "Passes" for that kind of rule goes through it.
3. A step's waiting time counts from when the message first went out to someone, unless the step says "Count from: when it appeared", so a held message neither escalates nor repeats by default.

The 1.0.0 "Steps back for" link (section 6) is a visible field in Which messages, not an exception to these rules: it narrows which messages a policy fits.

## 5. The twelve scenarios

1. **Water leak at 03:00, warning.** Plan "Leaks": With tags `leak`, `smoke`, any severity. Step At once: push to Admins, Passes quiet times. House rule "Night quiet": all severities, 22:00 to 07:00, send quietly, Critical messages pass. At 03:00 the leak push to Admins goes out with sound; the banner and any other push the call asked for go out quietly. An info message at 03:00 is sent quietly. "Can wake people" lists "Leaks: at once, push to Admins".
2. **Two quiet windows.** One house rule "Night quiet" with two windows: Monday to Friday 22:00 to 07:00, Saturday and Sunday 23:00 to 09:00; Which messages: info, success. (Two separate rules work the same, by rule 2.) In words: "Weekdays 22:00 to 07:00 and weekends 23:00 to 09:00, info and success are sent quietly. The windows do not overlap." A warning is outside Which messages and is not touched.
3. **Doorbell spoken only when someone is home, always with guests.** House rule "Doorbell speech", kind Presence: With tags `doorbell`, channels: speech, "speak when somebody of the audience is home", otherwise drop; Only if: guest mode is off. Nobody home, guest mode off: speech dropped, push untouched. Guest mode on: the rule's condition is false, so it does not apply and speech plays. Night quiet keeps working, because house rules never replace each other.
4. **Critical: push at once, repeat every 10 minutes.** Plan "Critical": severity critical. Step At once: push to Admins, Passes quiet times. Step Repeat every 10 min, no limit, Passes quiet times. Both steps belong to the same plan; nothing blocks either. An acknowledgement on any device ends the message's timers (unchanged engine behaviour).
5. **15 minutes while X, otherwise 1 hour.** One step, not two policies: Repeat every 60 min, Faster while X is on: every 15 min, At most 6 times. Minute 0: first delivery (count starts, nothing sent yet as a repeat). Minute 15: X turns on; the next repeat is due 15 minutes after the last send (minute 0), which is now, so it goes out at once. Then every 15 minutes while X is on. When X turns off, the next repeat is 60 minutes after the last one. The count never resets; "At most 6" covers both rhythms. In words says: "Changing rhythm keeps the count and times from the last repeat."
6. **Shopping list held until Anna leaves.** House rule "Shopping list", kind Presence: With tags `shopping`, channels: push, recipient must be not in zone Home, hold until it changes, maximum wait 12 h then drop. Anna's push waits while she is home and goes out when her person entity leaves (after the presence delay). Ben's messages without the tag are not touched; Ben's own shopping push is held for Ben only (per recipient, D-212).
7. **Digest summarized at 20:00.** House rule "Evening summary", kind Summary: With tags `digest`, at 20:00. Each digest message is held on every channel, banner included (D-105); at 20:00 one summary per recipient and channel goes out and passes quiet times and presence like any delivery. Plans that fit a digest message do nothing until the summary went out (rule 3), so nothing quiets or repeats the single messages. Other info messages lack the tag and are not summarized.
8. **Household speakers if nobody was reached.** Plan "Safety net": all messages. Step If nobody could be reached: speech on Household speakers, Passes presence rules, Passes quiet times (Chris's choice, visible as two badges). A presence rule meant for ordinary speech does not hold this step; the page shows it under "Can wake people".
9. **Escalation for a message still held by quiet times.** One rule, on the page in the step form: the waiting time counts from when the message went out. Default: the info push is held by Night quiet until 07:00; the escalation "after 10 min" fires at 07:10 if nobody reacted. If Chris wants it at night, the step gets "Count from: when it appeared" and "Passes quiet times"; then it fires at 23:10 and rings. Both outcomes are visible in In words before Save.
10. **Critical watch-rule message must reach phones.** Plan "Critical" (scenario 4) fits by severity; watch-rule messages are matched like any other (parity, rule 9). Its At once step pushes to Admins. No YAML, no rule change. The plan card says "Messages from automations and watch rules".
11. **1.0.0 starter list plus one Away policy.** Converted as in section 6. Every policy keeps its switch and entity ID. Because 1.0.0 ran "only the first", each converted policy gets "Steps back for" links to the earlier policies that overlap it, so every message gets exactly the deliveries it got before. A "Converted from 1.0.0" card lists what this keeps, for example "Critical delivery never acted on critical messages, because Away came first. Remove the link to let it act."
12. **Second overlapping policy, seen before saving.** Anna adds a second Quiet times rule "Weekend lie-in" (info, success, Saturday and Sunday 06:00 to 10:00, wait until the end). Also acting on these messages, live: "Night quiet also acts on these messages. Saturday and Sunday 06:00 to 09:00 both apply: Weekend lie-in waits, which is stricter than sending quietly, so messages wait until 10:00." For a second plan: "Warnings also acts on these messages: they get both repeat rhythms, every 30 min and every 60 min."

## 6. Migration from 1.0.0 (D-213)

Each subentry stays one subentry with the same ID, title and switch entity ID (D-198). Conversion runs once on load; stored keys that the old version wrote are still read.

### Types
- Deliver: becomes a plan with one step At once (same channels, recipients, from-the-call flags).
- Escalation: plan with one step If nobody reacts within N (same delay, same dismissal rule, fires once).
- Reminder: plan with one step Repeat every N, At most M, same channels; no Faster while.
- Fallback: plan with one step If nobody could be reached (same triggers; still never triggered by an escalation, reminder or other fallback).
- Summarize: house rule, kind Summary; `include_critical` becomes "Critical messages pass" unchecked when it was on (same meaning).
- Quiet hours: house rule, kind Quiet times, one window; `critical_passes` becomes "Critical messages pass".
- Away (and the 1.1.0 key `presence`): house rule, kind Presence, with the D-214 conversion already decided.
- Converted timed steps (escalation, reminder) get "Count from: when it appeared", which is the 1.0.0 timing. Summarized messages still start no timers, as in 1.0.0.
- Converted steps get no "Passes" marks: in 1.0.0 only severity passed holds, and that stays as "Critical messages pass" on the house rule.

### Modes and order
- `policy_mode: all`: every matching policy already acted. Conversion adds nothing. Same behaviour.
- `policy_mode: first` (the default): for each enabled automatic policy P, the converter stores `steps_back_for`: the IDs of the automatic policies above P in `policy_order` whose Which messages overlap P's. At run time P does not fit a message when any listed policy is enabled and fits it. This is the exact 1.0.0 rule, including the case where an earlier policy is later switched off. It shows in P's form as a removable chip "Steps back for: Away (1.0.0)".
- `policy_order`: read once by the converter, then kept in storage unused (so a reconversion gives the same result). The page shows no order.
- `apply: manual`: becomes Runs: only when named. Unchanged.
- Named policies: a `notify` call naming a policy adds it to the automatic ones (D-189); `match_policies_automatically: false` runs only the named ones; a watch rule's named policy replaces the automatic ones (D-145). All unchanged. A named policy ignores its own "Steps back for", as a named policy ignored the order in 1.0.0.

### What changes visibly
- The page: two groups instead of one list; no order, no mode choice. CHANGELOG line: "Policies are shown as Plans and House rules; the order list and the mode setting are gone. Converted setups behave as before."
- New setups have no "Steps back for" links and get the three conflict rules. This is a new default, not a change to existing setups.

### Getting old behaviour back, or leaving it
- Nothing changes on upgrade, so there is nothing to undo. The "Converted from 1.0.0" card lists every "Steps back for" link that stops a policy from ever acting, and every step counting from when it appeared, each with "Use the new behaviour". Removing a link can be undone by "Restore 1.0.0 links" on the same card, which recomputes from the kept `policy_order`.
- Downgrade to 1.0.0 is not supported once a plan has more than one step or a Faster while; a single-step plan still stores the old type key, so a downgrade reads it.

## 7. Engine impact

Reused:
- The chain (Summarize, Quiet hours, Presence, Fallback) and its Hold, release on arrival, at a time or at a deadline, and restore after restart: unchanged; the house rules are its stages.
- `for_message` in "all" mode is the base for every message; the first mode code goes away. S.
- Timer rows per message and policy: key becomes policy key plus step index; `_drop_inapplicable_timers`, overdue-fires-once and severity restart unchanged. S.
- The In-words builder: per step instead of per policy. S.
- The overlap note (D-151): grows into "Also acting on these messages" with one sentence per pair. M.

New:
- Plan type with a list of steps in one subentry; read the four old sending types as one-step plans. M.
- `steps_back_for` evaluation in matching and the converter that computes it. S.
- "Passes" marks: each planned delivery carries the kinds it passes; the Quiet times and Presence stages skip it. S.
- Count from when it went out: `_arm` runs on the first delivery that is sent rather than on appearance; release of a held delivery calls it. The existing `is_held` guard already covers summaries. M.
- Faster while: a state listener on the condition re-plans the repeat timer from the last send; shared counter in the timer row. M.
- Try a message: a dry run of matching and the chain for a given severity, tags, time and presence, with no side effects; reuses stage functions. M.
- Panel: new page, plan form with steps, house rule form, converted card. L.

Total: about L for the panel, M for the engine, no storage format change beyond new keys in the subentry data.

## 8. Risks and what this design gives up

- **Biggest risk: plans add up.** Two plans that fit the same message both send. Anna can get two rhythms of repeats or two pushes at once. The live "Also acting on these messages" sentence and Try a message are the only defence; there is no automatic "most specific wins". Whether 1.0.0 already merges an identical push from Deliver and from the call at creation must be checked in `deliver.py` before this is promised either way.
- **"Passes quiet times" is easy to tick.** Any admin can make a step loud. Mitigation: the "Can wake people" block at the top of the page, so a change shows on one look. It does not prevent it.
- **Converted setups carry "Steps back for" chips** that most users never asked for and will not understand at first. They keep D-213 exact, but the converted card must explain them in one sentence each.
- **Counting from when it went out** means an escalation for a message held all night fires in the morning. That is the default by design (S9); someone who expected 1.0.0 timing in a new plan must pick "when it appeared".
- **Given up:** the list order as a tool for "this one first"; "only the first" for new setups; a plan step getting through a summary (exclude by tag or "Critical messages pass" instead); downgrade after multi-step plans exist.
- **Not verified here:** whether the person-state listener and condition listeners can share one subscription per entity; whether ha-form style can render a step list without a build step (the hub wizard's repeatable rows suggest yes).
