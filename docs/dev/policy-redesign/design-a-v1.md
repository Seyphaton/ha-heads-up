# Policy redesign, design A: two lanes

Designer A, round one, 2026-11-18. Stance: holding back and sending are two separate lanes on the page, with exactly one strength rule between them. Mockup: [policy-redesign-a.html](../mockups/policy-redesign-a.html). Facts: [00-fact-sheet.md](00-fact-sheet.md), stories: [01-users-and-stories.md](01-users-and-stories.md).

## 1. The mental model

"Hold-back policies decide when a message may reach people, sending policies decide who else gets it and how often, and only the messages on the Always gets through list skip every hold."

## 2. Vocabulary

Every term a user sees, English then German. Existing type names stay, so the 1.0.0 docs, translations and entity names keep working.

- Policies (page): Richtlinien
- Policy: Richtlinie
- Hold back (lane): Zurückhalten
- Send (lane): Senden
- Always gets through (the strength rule): Kommt immer durch
- Quiet hours: Ruhezeit
- Presence: Anwesenheit
- Summarize: Zusammenfassen
- Deliver: Zustellen
- Escalation: Eskalation
- Reminder: Erinnerung
- Fallback: Ersatz
- Which messages: Welche Meldungen
- For (severities, tags): Für
- Not for (severities, tags): Nicht für
- Only if: Nur wenn
- What it does: Was sie tut
- Count from: Zählen ab
- when it has reached someone: sobald sie jemanden erreicht hat
- when it was created: ab dem Erstellen
- Held: Zurückgehalten
- Released: Freigegeben
- Sent quietly: Leise gesendet
- Dropped: Verworfen
- Stricter: strenger
- More often: häufiger
- What happens to a message?: Was passiert mit einer Meldung?
- Where it overlaps: Wo sie sich überschneidet
- Check after the update: Nach dem Update prüfen
- Did nothing in 1.0: Hat in 1.0 nichts getan
- Let it act: Wirken lassen
- Keep as before: Wie bisher lassen

French and Spanish follow the same lengths ("Passe toujours", "Siempre pasa"; "Retenir", "Retener"; "Envoyer", "Enviar"). No term needs the words filter, precedence or priority.

## 3. Structure

### The Policies page, top to bottom

1. What happens to a message? A small checker: severity, tag, time of day, and who is home (home, away, unknown). It lists, in plain sentences, which hold-back policies act, which sending policies add what, and the result for each channel. This answers Q1 and Q2 without the message log.
2. Lane "Hold back" with the line: "These act on every delivery of a message, also on what the Send lane adds. Escalations and reminders start counting once a message has reached someone." One card per Quiet hours, Presence and Summarize policy, sorted by type, then name. Each card: name, switch, one "In words" sentence, the For and Not for chips.
3. The band "Always gets through", visually between the lanes and full width: "Messages with these severities or tags skip every hold-back policy and go out at once, with everything the Send lane adds." Two chip rows: severities (starts with critical) and tags (empty). An Edit button. When the list holds more than critical, the band names it in words: "Messages tagged alarm may wake people at night."
4. Lane "Send" with the line: "Every sending policy that fits a message runs. Where two reminders repeat on the same channel, the one that repeats more often counts." Cards for Deliver, Escalation, Reminder and Fallback.
5. Check after the update (only after a conversion, until dismissed): policies the conversion narrowed or that did nothing in 1.0, each with its reason and buttons.

There is no list order, no drag and drop, no Move up or Move down, and no mode setting. Strength never depends on position.

### The form of one policy

Same sections for all seven types, same ha-form style as 1.0:

- Name, enabled, type (fixed after creation, the lane is shown next to it: "Hold back" or "Send").
- Which messages: Automatically or Manually; For severities and tags (none: all); Not for severities and tags (new); Only if (D-216). Hold-back forms show a read-only line instead of 1.0's "Critical messages pass": "Messages on Always gets through (critical, tag alarm) are never held by this policy."
- What it does: the type's own fields, unchanged from 1.0 and from the Presence design (D-212, D-214). Escalation and Reminder gain Count from (default: when it has reached someone).
- In words: one sentence built from the fields.
- Where it overlaps: computed before Save, one sentence per overlapping policy of the same lane, saying where both act and which result counts (S12). Never blocks (D-151).

### How strength is expressed

- Inside the hold lane, strength is the action itself: summary, then drop, then wait, then quiet. A user sees it in the card sentence ("drops", "waits until 07:00", "sends quietly").
- Inside the send lane, sending policies add up; for reminders on the same channel, "more often" counts. Visible in the card sentence ("every 15 min").
- Between the lanes, the one band. It is the only place on the page where something is stronger than a hold.

### Why this strength rule and not the ones on the table

- "Hold-back always wins" makes `critical` the only way through, which is pain point 6: users mark leaks critical to be woken.
- "Sending always wins" gives a quiet first push followed by a loud reminder 15 minutes later for the same info message; a Deliver policy for speech would talk into an empty house. Quiet hours then only shape the first delivery, which no household member expects.
- "One sorted list, first one runs" is pain points 2 and 3.
- The previous proposal's "May wake people" on each sending policy sits on the wrong side. The leak's own push comes from the automation, not from a sending policy, so it stays held unless a Deliver policy repeats it. One escalation marked this way wakes people for every message it covers, including the ones a hold was written for. A fallback marked this way speaks into an empty house, because the mark passes Presence and Quiet hours alike. And the permission is spread over many forms: Chris cannot see in one look what may wake him, and a sending policy added later by someone else can break the nights.
- A per-hold "lets through" (1.0's "Critical messages pass", D-211) is spread the same way, and a hold added later does not know that leaks must pass.
- The band decides by the message, not by the policy. A message either is held by the hold lane or it is not, and then all its deliveries behave alike: the first push, Deliver, escalation, reminders and fallback. It sits in one place, it is visible without opening a form (S1), and a hold added later respects it without anyone remembering to tick a box. It takes tags, so `critical` stops being the only way through.

## 4. Conflict rules

1. Every hold-back policy that fits a message acts on each of its deliveries, also on those the Send lane adds; where they disagree the stricter result counts (summary, then drop, then wait, then quiet), and a released delivery passes all holds again.
2. Every sending policy that fits a message runs; where two reminders repeat on the same channel the one that repeats more often counts, and escalation and reminder clocks start once the message has reached someone.
3. A message whose severity or tag is on Always gets through skips every hold-back policy, so it goes out at once with everything the Send lane adds.

"Fits" means For and Not for match and Only if is true (unknown counts as whatever delivers more, D-216). Two reminders with the same rhythm on one channel: the one with more repeats counts, then the one created first; Where it overlaps names it. A named policy (manual, or named by a call or a watch rule) joins its lane and follows the same three rules. A held delivery is not a failure, so it never triggers a Fallback.

## 5. The twelve scenarios

### 1. Water leak as a warning at 03:00

Configure: Always gets through gets the tag `alarm`. The leak automation sends severity warning, tag `alarm`. A Deliver policy "Alarms to Admins" (For tag `alarm`) pushes the Admins audience with sound. Night quiet stays as it is (info and success, 22:00 to 07:00, quietly), or may even cover all severities.

What happens: at 03:00 the message is on the band, no hold looks at it, the Admins get the push with sound at once, and a reminder or escalation for `alarm` runs on its normal clock. An info message at 03:00 is sent quietly by Night quiet. The band on the page reads "Messages tagged alarm may wake people at night."

### 2. Two quiet windows

Configure: Quiet hours "Weeknights" (info, success; Sun to Thu, 22:00 to 07:00; quietly) and Quiet hours "Weekends" (info, success; Fri and Sat, 23:00 to 09:00; quietly).

What happens: both act; each covers its own nights. A warning is not in For, so neither touches it. Before saving "Weekends", Where it overlaps says: "«Weekends» adds Friday and Saturday nights, 23:00 to 09:00. It does not overlap «Weeknights»."

### 3. Doorbell spoken only when someone is home, always with guests

Configure: Presence "Doorbell in an empty house" (For tag `doorbell`; covers speech; when nobody of the household is in Home: drop; Only if guest mode is off).

What happens: nobody home, guest mode off: speech is dropped, the push goes out. Guest mode on: the policy does not fit, the doorbell is spoken. Night quiet still acts on the doorbell at 23:00 (speech becomes quiet), because holds no longer share one place.

### 4. Critical pushed to the Admins and repeated every 10 minutes

Configure: Deliver "Critical to Admins" (For critical; push to Admins) and Reminder "Critical repeat" (For critical; every 10 min, at most 12 times). Critical is on the band from the start.

What happens: the push goes at once; the message has reached someone, so the reminder clock starts; repeats every 10 min. Both are sending policies and both run. An acknowledgement on any device stops the repeats (unchanged).

### 5. Every 15 min only if X, otherwise every hour

Configure: Reminder "Urgent" (every 15 min, at most 8, Only if X is on) and Reminder "Hourly" (every 60 min, at most 8). Both cover all channels already sent.

What happens, with the message created at 00:00 and X off:
- 00:00 first delivery; only "Hourly" fits; next repeat due 01:00.
- 00:15 X turns on. "Urgent" now fits and repeats more often, so it counts. Next repeat = last delivery + 15 min = 00:15, so it goes now (repeat 1).
- 00:30, 00:45 repeats 2 and 3.
- 00:50 X turns off. "Hourly" counts again; next repeat = 00:45 + 60 = 01:45.
- The repeat count belongs to the message and channel and does not reset; each reminder's "at most" is compared with it. The message log and the checker say "Now every 15 min (Urgent, while X is on); repeat 3 of at most 8; next 01:00."

The form's Where it overlaps: "Where both fit, «Urgent» counts while X is on (it repeats more often); otherwise «Hourly». The repeat count carries over."

### 6. Shopping-list push held until the person leaves

Configure: Presence "Shopping list on leaving" (For tag `shopping`; covers push; when the recipient is in Home: hold until it changes).

What happens: Anna's push waits while she is home and goes when she leaves, after the presence delay. Presence acts per recipient, and only on `shopping` messages, so nothing else is held. If she leaves at 06:30, the released push passes the holds again and Night quiet sends it quietly.

### 7. Digest summarized at 20:00

Configure: Summarize "Evening summary" (For tag `digest`; at 20:00).

What happens: a digest message goes into the summary. Night quiet also fits it (info), but a summary is the strictest result, so the message is held only by the summary; Night quiet acts on the summary delivery at 20:00, where it does nothing. A digest at 23:00 waits for tomorrow's summary, it is not quieted or dropped. Info messages without the tag are not summarized. The send lane does nothing for a message that goes into a summary (as in 1.0).

### 8. Household speakers when nobody could be reached

Configure: Fallback "Say it in the house" (trigger: nobody to notify or sending failed; speech on Kitchen speaker).

What happens: the fallback is a delivery and passes the hold lane like any other. For a warning (no hold fits), Kitchen speaker says it at once. For an info message at night, Night quiet makes the speech quiet; the hold lane line on the page and the checker say so ("Fallback speech: sent quietly by Night quiet"). If Chris wants it spoken, he puts the tag on the band or narrows Night quiet with Not for. A push held by Presence is not "nobody reached", so it never triggers the fallback.

### 9. Escalation for a message still held by quiet hours

Configure: Quiet hours "Night wait" (info; 22:00 to 07:00; wait until the end) and Escalation "Nobody looked" (info; 30 min; Admins).

What happens: an info message at 23:00 is held until 07:00; it has reached nobody, so the escalation clock does not run. At 07:00 it is delivered, at 07:30 the escalation goes if nobody acknowledged. If the hold was "quietly" instead, the message reached people at 23:00 (quietly), the escalation fires at 23:30 and is itself sent quietly. To be woken by choice: put the tag on the band. The rule is one line at the top of the hold lane.

### 10. A critical watch-rule message must reach phones

Configure: Deliver "Critical to Admins" from scenario 4 (For critical, any tag). Watch-rule messages carry tag `rule` and are matched like any message (rule 9).

What happens: the rule's banner appears, the same Deliver policy pushes the Admins. Critical is on the band, no hold delays it. No YAML.

### 11. A 1.0.0 setup with the starter list and one Away policy

Stored: Evening summary, Night quiet, Warning reminder, Critical delivery, Away (all severities, `critical_passes` on), mode "only the first". The conversion (section 6) computes what each policy acted on in 1.0 and writes it as Not for:
- Evening summary: unchanged.
- Night quiet: Not for tag `digest` (the summary came first).
- Away becomes Presence. If Away sat at the end of the list: Not for info, success, warning, critical (in 1.0 it only ever acted on errors). Warning reminder and Critical delivery unchanged.
- If Away sat in the starting position, before the reminder: Away gets Not for info, success; Warning reminder and Critical delivery did nothing in 1.0 and are marked so (they act on nothing). Check after the update lists them: "Did nothing in 1.0 because «Away» came first." Buttons: Keep as before, Let it act.
- Every hold let critical through, so the band starts with critical.

Every message gets the same deliveries as before. The visible changes are the Not for chips, the band and the check list.

### 12. A second, overlapping policy of the same type

Example: Anna adds Quiet hours "Late weekend" (all severities except critical; Sat 23:00 to 09:00; wait) next to "Weekends" (info, success; Fri and Sat 23:00 to 09:00; quietly). Before Save, Where it overlaps says: "Saturday 23:00 to 09:00, info and success: both act; «Late weekend» waits, which is stricter than «Weekends» sending quietly, so these messages wait until 09:00. Warnings and errors on Saturday night: only «Late weekend» acts." For two reminders it uses the scenario 5 sentence; for sending policies of other types: "Both run."

## 6. Migration from 1.0.0 (D-213)

The conversion only adds keys; it never rewrites For, the order or the mode. A downgrade to 1.0.0 therefore reads the same policies, order and mode it wrote.

Types:
- `summarize`, `quiet_hours`: hold lane, fields unchanged.
- `away`: becomes `presence` as already designed (D-212, D-214), hold lane; `away` is still read.
- `deliver`, `escalation`, `reminder`, `fallback`: send lane, fields unchanged. Escalation and reminder get `count_from: reached`.

Critical passes:
- If every hold-back policy lets critical through (`critical_passes` on, Summarize without `include_critical`), the band starts with critical (`pass_through` in the entry options).
- Otherwise the band starts empty and each hold that let critical through gets Not for critical. Same result, no change.

Mode "only the first" (`first`):
- For each automatic policy, the conversion computes what it acted on in 1.0: its For minus the For of every enabled automatic policy above it. Where that difference fits Not for severities or tags (the starter list and nearly every real setup), it is written as `exclude_severities` and `exclude_tags`.
- Where it does not fit (a policy above with both severities and tags that only partly overlap), the conversion writes `not_with` (subentry IDs). The form shows it as "Not for messages that «Evening summary» is for (kept from 1.0)", with Remove.
- A policy that acted on nothing gets `did_nothing_in_1_0: true`: it acts on nothing until the user picks Let it act on the check list.
- Manual policies were never shadowed and stay unchanged.

Mode "all that apply" (`all`): scopes unchanged. Two behaviour changes, each a CHANGELOG line:
- Two reminders on the same channel: only the one that repeats more often now runs. Way back: give each reminder its own channels.
- Escalation and reminder clocks start once the message reached someone, not when it was created. Way back: Count from "when it was created" on that policy. With the starting mode `first`, this change affects only named policies.

Stored options:
- `policy_mode` and `policy_order` stay stored and are no longer read; the drag list goes away. New option `policy_model: lanes` marks a converted entry.
- Policies named in calls by switch entity ID (D-198), `match_policies_automatically` (D-189) and watch-rule named policies (D-145): unchanged; a named policy joins its lane.

Full way back: a 1.0.0 backup, or a downgrade, which ignores the new keys.

## 7. Engine impact

Reused:
- The chain order Summarize, Quiet hours, Presence, Fallback already behaves like "stricter counts": each stage holds or changes, and a released delivery passes the chain again.
- Held rows with release on arrival or at a time, timer rows per policy, `_drop_inapplicable_timers`, the overdue-once rule.
- Matching by severity and tag; the "In words" builder; the overlap note (D-151).

New, with rough cost:
- `for_message` returns every fitting policy (the `all` path) plus Not for and `not_with`; the `first` path survives only in the conversion. S.
- Band check before the hold stages; replaces `critical_passes` and `include_critical` at run time (still read for conversion). S.
- Count from reached: arm escalation and reminder rows on the first delivery that reached someone (not held, not dropped) or on a release, not at creation. M.
- Reminder resolution per channel, shared repeat count, recomputed when an Only if changes (needs the condition listeners of D-216). A send whose time came while its Only if was false goes when it turns true, if the message is still unacknowledged. M, L if the D-216 listeners are not built yet.
- Conversion with effective scopes, `not_with`, `did_nothing_in_1_0`. M.
- Panel: two lanes, the band, Not for, Count from, Where it overlaps, the checker, the check list; remove the drag list. L.
- Translations in four languages and docs. M.

## 8. Risks and what the design gives up

Risks:
- The band is strong. One tag added by another admin wakes everyone for every message with that tag. It is at least visible in one place and named in words; the panel cannot say who changed it.
- "Stricter counts" can surprise: a dropping window added next to a waiting one silently drops. Where it overlaps says so before Save, but only for policies of the same type.
- Clocks from reach change timing: an escalation for a message held overnight goes at 07:30, not at night. Intended, but anyone relying on night escalations must use the band.
- The conversion is exact but can leave narrowed or dead policies that look odd. The check list explains them; some users will press Let it act without reading.
- Per-channel reminder resolution is the subtlest rule; the message log and checker must show the current rhythm.

Given up:
- A user-set order. Ben cannot say "this hold beats that hold"; strength comes from the action only.
- Sends that pass some holds but not others, such as a fallback that passes Presence but not Quiet hours. A message passes all holds or none.
- A band with time or condition ("let warnings through while the alarm is armed"). Severity and tag only.
- The choice between modes. One model for everyone.
- Two simultaneous reminders on one channel.
