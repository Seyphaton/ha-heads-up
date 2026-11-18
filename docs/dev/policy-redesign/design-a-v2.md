# Policy redesign, design A v2: two lanes and one band

Designer A, round two, 2026-11-18. Stance: holding back and sending are two separate lanes; exactly one strength rule sits between them, the Always gets through band, keyed on the kind of message. Mockup (updated in place): [policy-redesign-a.html](../mockups/policy-redesign-a.html). Round one: [design-a-v1.md](design-a-v1.md). Reviews read: [review-by-b.md](review-by-b.md), [review-by-c.md](review-by-c.md), [review-by-d.md](review-by-d.md). None was missing.

What keeps A apart from B, C and D: policies stay small and typed, every policy that fits acts, and strength lives in one place only, a list of message kinds on the band. No goal, step or type carries strength of its own.

## Answers to the reviews

Raised by all three: the band decides per message, so it wakes everyone and passes Presence.
- Fixed. Each band entry now has Wakes: "everyone it goes to" or "only these" (audiences, people, speaker groups). Deliveries to anyone else go through the hold lane as usual. So Chris can wake only the Admins while Anna's phone stays quiet.
- Fixed. The band now passes only the holds that are about time: Quiet hours and Summarize. Presence policies still act, so a leak is not spoken into an empty house. In 1.0.0, critical passed Away; a converted Presence policy keeps that as Not for critical (section 6).

B, D: the conversion of "only the first" was a snapshot of switch states.
- Fixed. The conversion now writes a link that is checked on every message: "Not for messages that «Evening summary» takes, while it is on". It follows the switches as 1.0.0 did. Where the fixed chip gives the same result, the check list offers it ("Write as Not for tag digest") with the caveat about switches. It is never applied automatically. "Restore 1.0 links" recomputes all links from the kept `policy_order`.

B: rules 1 to 3 hid holds that skip instead of hold.
- Fixed. Rule 1 now says it: a repeat never waits. Quiet hours skip a repeat that would wait, and Presence does not act on repeats. Both behave as in 1.0.0 (`quiet.py`, `away.py`).

C: scenario 8, a fallback cannot speak at night without making the whole message loud.
- Partly fixed, partly accepted. With Wakes, the band entry can name only Kitchen speaker, so only the speech skips Night quiet. The first push to the household stays quiet. An info message's fallback still follows info at night unless info is on the band. A fallback has the same strength as the message it belongs to. If info is not worth waking for, neither is its fallback, and the checker says so.

C: D-211 is reopened without naming it.
- Accepted and named. The band replaces the "Critical messages pass" field of D-211 on Quiet hours and Summarize. On Presence it becomes a pre-filled Not for critical. This needs a maintainer decision, recorded as superseding D-211 if accepted.

C: in "all" mode, two reminders on one channel lose a stream with no exact way back.
- Fixed. A Reminder has the option "Runs alongside other reminders". The conversion turns it on for every reminder that overlaps another on a channel in an "all" setup, which matches 1.0.0 exactly. New reminders start with it off.

D: reminders share one count, so the slow one can stop at once.
- Fixed. Each reminder counts only its own repeats and stops at its own "at most". The Reminder form says so in a fixed line, and Where it overlaps names the other reminder and which one counts when (Q3 now sits in the form).

My own error, found while reviewing: there is no `error` severity (`const.py`). The starter list puts the order Critical delivery, Warning reminder, Evening summary, Night quiet (`welcome.py`); an Away added later sits last and does nothing in 1.0.0. Scenario 11 is rewritten.

v1 changed escalation and reminder timing for converted setups. Changed back: converted Escalation and Reminder policies get Count from "when it was created", the 1.0.0 timing. The check list offers the new timing, one policy at a time.

## Taken from others

- From B: a definition of "reached someone". A person on any channel other than the banner counts. The banner counts only when it is the message's only channel.
- From B: delivery-level strength for named people, as the Wakes field of a band entry. A's band stays a permission and never sends; B's Gets through goal also sends.
- From C: "Restore 1.0 links" from the kept `policy_order`, a way back without a backup.
- From C: the "Can wake people" summary, merged into the band's own sentence at the top of the page.
- From D: a warning before Save when a band change stops critical messages, or any entry, from waking people.
- From B and D: converted timed policies keep the 1.0.0 timing; the new timing is offered, not imposed.

## 1. The mental model

"Hold-back policies decide when a message may reach people, sending policies decide who else gets it and how often, and the Always gets through list says which kinds of message may wake whom despite quiet hours and summaries."

## 2. Vocabulary

English then German. Existing type names stay, so 1.0.0 docs, translations and entity IDs keep working.

- Policies (page): Richtlinien
- Policy: Richtlinie
- Hold back (lane): Zurückhalten
- Send (lane): Senden
- Always gets through (the band): Kommt immer durch
- Wakes (band entry field): Weckt
- everyone it goes to: alle Empfänger
- only these: nur diese
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
- Not for messages that … takes, while it is on: Nicht für Meldungen, die … übernimmt, solange sie an ist
- Only if: Nur wenn
- What it does: Was sie tut
- Count from: Zählen ab
- when it has reached someone: sobald sie jemanden erreicht hat
- when it was created: ab dem Erstellen
- Runs alongside other reminders: Läuft neben anderen Erinnerungen
- Counts its own repeats: Zählt ihre eigenen Wiederholungen
- Held, Released, Sent quietly, Dropped, Skipped: Zurückgehalten, Freigegeben, Leise gesendet, Verworfen, Ausgelassen
- Stricter: strenger
- More often: häufiger
- What happens to a message?: Was passiert mit einer Meldung?
- Where it overlaps: Wo sie sich überschneidet
- Check after the update: Nach dem Update prüfen
- Did nothing in 1.0: Hat in 1.0 nichts getan
- Let it act, Keep as before: Wirken lassen, Wie bisher lassen
- Restore 1.0 links: 1.0-Verknüpfungen wiederherstellen

French and Spanish keep similar lengths ("Passe toujours", "Siempre pasa"; "Réveille", "Despierta"). No term needs filter, precedence or priority.

## 3. Structure

### The Policies page, top to bottom

1. What happens to a message? A checker with severity, tag, time of day and who is home. It lists the result per recipient and channel ("Admins: push with sound. Anna: quiet push. Kitchen speaker: not spoken, nobody home"), and for each line the policy that caused it. It is a dry run of matching and the chain; the same lines fill the message log (Q1, Q2).
2. Lane "Hold back". Line at the top: "These act on every delivery of a message, also on what the Send lane adds. Where two disagree, the stricter counts. Repeats never wait: quiet hours skip them." Cards for Quiet hours, Presence and Summarize, sorted by type, then name.
3. The band "Always gets through", full width between the lanes. Line: "For these messages, quiet hours and summaries do not apply to the people named. Presence still decides by where people are." Each entry is one row: which messages, then whom it wakes. The band ends with one sentence per entry in words: "Messages tagged alarm may wake the Admins at night." Edit opens a short form; removing or narrowing an entry shows, before Save, what will no longer wake whom.
4. Lane "Send". Line: "Every sending policy that fits a message runs. Escalations and reminders start counting once the message has reached someone." Cards for Deliver, Escalation, Reminder and Fallback.
5. Check after the update (after a conversion, until dismissed).

There is no list order, no drag and drop, no mode setting.

### The form of one policy

- Name, enabled, type (fixed after creation, with its lane shown as text).
- Which messages: Automatically or Manually; For severities and tags; Not for severities and tags; on converted policies, the "Not for messages that … takes" links; Only if (D-216). Hold-back forms show a read-only line naming the band entries that pass them, for example "Critical, and tag alarm for the Admins, are never held by this policy". Presence forms do not show it, because the band does not pass Presence.
- What it does: the type's fields as in 1.0.0 and the Presence design (D-212, D-214). Escalation and Reminder have Count from. Reminder has Runs alongside other reminders, plus the fixed line "This reminder counts its own repeats".
- In words, and Where it overlaps: one sentence per overlapping policy of the same lane, before Save, never blocking (D-151, S12).

### The form of one band entry

- Which messages: severities and tags (one entry may have both: "warning tagged alarm").
- Wakes: everyone it goes to, or only these (audiences, people, speaker groups).
- In words: "Warnings tagged alarm skip quiet hours and summaries for the Admins."

### How strength is expressed

- Inside the hold lane: by the action (summary, drop, wait, quiet), shown in each card sentence.
- Inside the send lane: sending policies add up. Among reminders on one channel, the one that repeats more often counts, unless one runs alongside.
- Between the lanes: the band, the only place where something is stronger than a hold.

### Why the band and not the positions on the table

- "Hold-back always wins": `critical` stays the only way through (pain point 6).
- "Sending always wins": a quiet first push and then a loud reminder for the same info message.
- "One sorted list, first one runs": pain points 2 and 3.
- "May wake people" on each sending policy (the previous proposal) and C's "Passes" on each step: the permission sits on the sender. A step that applies to all messages passes for all of them; C's own scenario 8 then speaks an info message at 03:00. The automation's own first push has no step to mark. And "what can wake me" is spread over many forms.
- B's Gets through goal bundles a permission with a send, so switching off the permission also removes the push.
- D's type setting "Send as usual" ties waking to one type per message, and watch-rule messages (tag `rule`) cannot choose their type.
- The band answers "what may wake whom" by the kind of message, in one place, without sending anything. A hold added later respects it without anyone ticking a box. It takes tags, so `critical` stops being the only way through.

## 4. Conflict rules

1. Every hold-back policy that fits a message acts on each of its deliveries, also on those the Send lane adds; where they disagree the stricter result counts (summary, then drop, then wait, then quiet), a released delivery passes all holds again, and a repeat never waits (Quiet hours skip it, Presence does not act on it).
2. Every sending policy that fits a message runs, where two reminders repeat on one channel the one that repeats more often counts unless one runs alongside, each reminder counts its own repeats, and escalation and reminder clocks start once the message has reached someone.
3. For a message that matches an Always gets through entry, quiet hours and summaries do not apply to its deliveries to the people that entry wakes; Presence still acts.

Definitions, not exceptions:
- A policy fits when For and Not for match, every "Not for messages that … takes" link is false, and Only if is true (unknown counts as whatever delivers more, D-216).
- A message has reached someone when a delivery other than the banner was sent to a person or speaker, or when the banner is its only channel.
- A named policy (manual, or named by a call or a watch rule) joins its lane and follows the same rules. A held delivery is not a failure and never triggers a Fallback.
- When two reminders with the same rhythm overlap, the one created first counts, and Where it overlaps names it.

## 5. The twelve scenarios

### 1. Water leak as a warning at 03:00

Configure:
- Band entry: tag `alarm`, Wakes only Admins.
- Deliver "Alarms to Admins": For tag `alarm`, push to Admins with sound.
- The leak automation sends warning, tag `alarm`, to the household.
- Night quiet covers all severities from 22:00 to 07:00, quietly (it may also stay at info and success).

What happens:
- At 03:00 the push to the Admins skips Night quiet and rings.
- Anna's and Ben's pushes are not covered by the band entry, so Night quiet sends them quietly.
- An info message at 03:00 is quiet for everyone.
- The band reads "Messages tagged alarm may wake the Admins at night." Nothing is marked critical.

### 2. Two quiet windows

Configure: Quiet hours "Weeknights" (info, success; Sun to Thu, 22:00 to 07:00; quietly) and "Weekends" (info, success; Fri and Sat, 23:00 to 09:00; quietly).

What happens: both act on their own nights; a warning is not in For. Where it overlaps, before Save: "«Weekends» adds Friday and Saturday nights, 23:00 to 09:00. It does not overlap «Weeknights»."

### 3. Doorbell spoken only when someone is home, always with guests

Configure: Presence "Doorbell in an empty house": For tag `doorbell`; covers speech; when nobody of the household is in Home, drop; Only if guest mode is off.

What happens:
- Nobody home, guest mode off: speech dropped, push sent.
- Guest mode on: the policy does not fit, so the doorbell is spoken.
- Night quiet still acts on an info doorbell at 23:00, because holds do not share one place.

### 4. Critical pushed to the Admins and repeated every 10 minutes

Configure:
- Deliver "Critical to Admins": For critical, push to Admins.
- Reminder "Critical repeat": For critical, every 10 min, at most 12.
- Band entry: critical, Wakes everyone it goes to (the starting entry).

What happens: the push goes at once, the clock starts with it, and repeats follow every 10 min. Neither blocks the other. An acknowledgement on any device stops the repeats.

### 5. Every 15 min only if X, otherwise every hour

Configure:
- Reminder "Urgent": warning, every 15 min, at most 8, Only if X is on.
- Reminder "Hourly": warning, every 60 min, at most 3.
- Both cover all channels already sent; neither runs alongside.

What happens, with the message created at 00:00 and X off:
- 00:00 first delivery. Only "Hourly" fits; next repeat due 01:00.
- 00:15 X turns on. "Urgent" fits and repeats more often, so it counts. Due = last delivery + 15 min = 00:15, so repeat 1 of "Urgent" goes now.
- 00:30, 00:45, 01:00: repeats 2 to 4 of "Urgent".
- 01:05 X turns off. "Hourly" counts again with its own count at 0. Next = 01:00 + 60 = 02:00, then 03:00 and 04:00, then it stops at 3.
- The checker and the log say "Now every 60 min (Hourly, X is off); Hourly repeat 1 of 3; next 02:00."

The Reminder form: "Where both fit, «Urgent» counts while X is on, because it repeats more often; otherwise «Hourly». Each counts its own repeats."

### 6. Shopping-list push held until the person leaves

Configure: Presence "Shopping list on leaving": For tag `shopping`; covers push; when the recipient is in Home, hold until it changes.

What happens: Anna's push waits while she is home and goes when she leaves, after the presence delay. The check is per recipient and only for `shopping`. If she leaves at 06:30, the released push passes the holds again and Night quiet sends it quietly.

### 7. Digest summarized at 20:00

Configure: Summarize "Evening summary": For tag `digest`, at 20:00.

What happens: a digest message goes into the summary. Night quiet also fits it, but a summary is the strictest result, so only the summary holds it; Night quiet acts on the summary delivery at 20:00, where it does nothing. A digest at 23:00 waits for the next summary. Other info messages are not summarized. As in 1.0.0, the Send lane does nothing for a message that goes into a summary.

### 8. Household speakers when nobody could be reached

Configure: Fallback "Say it in the house": trigger nobody to notify or sending failed; speech on Kitchen speaker. The band entry for `alarm` from scenario 1 gets Kitchen speaker added to Wakes.

What happens:
- A warning: no hold fits, Kitchen speaker says it at once.
- An `alarm` at 03:00: the speech to Kitchen speaker skips Night quiet; the household pushes stay quiet.
- If nobody is home and a Presence policy drops speech in an empty house, the speech is dropped. The band does not pass Presence, and nobody is there to hear it.
- An info message at night: Night quiet makes the speech quiet. The checker says "Fallback speech: sent quietly by Night quiet".
- A push held by Presence is not "nobody reached", so it never triggers the fallback.

### 9. Escalation for a message still held by quiet hours

Configure: Quiet hours "Night wait" (info; 22:00 to 07:00; wait) and Escalation "Nobody looked" (info; 30 min; Admins; Count from when it has reached someone).

What happens:
- An info message at 23:00 is held and reaches nobody (its banner is not its only channel), so the clock does not run.
- At 07:00 it is delivered; at 07:30 the escalation goes if nobody acknowledged.
- With "quietly" instead of wait, it reached people at 23:00, the escalation fires at 23:30 and is itself sent quietly.
- To be woken by choice, Chris adds the tag to the band with Wakes only Admins.

### 10. A critical watch-rule message must reach phones

Configure: "Critical to Admins" from scenario 4 (For critical, any tag). Watch-rule messages carry tag `rule` and match like any message (rule 9).

What happens: the banner appears and the Admins get the push. Critical is on the band, so no quiet hours delay it. No YAML. A leak watch rule at warning severity is reached by a band entry "warning tagged rule, Wakes only Admins" if Chris wants it, which needs no change to the frozen rule form.

### 11. A 1.0.0 setup with the starter list and one Away policy

Stored: `policy_order` Critical delivery, Warning reminder, Evening summary, Night quiet (the introduction's order under "only the first"), then Away (all severities, added later, appended at the end). Mode first.

What 1.0.0 does: critical goes to Critical delivery, warning to Warning reminder, digest info and success to Evening summary, other info and success to Night quiet. Away matches only when none of these does, which never happens with the four severities. Away does nothing.

After conversion:
- Evening summary, Warning reminder, Critical delivery: no links needed (nothing above them overlaps).
- Night quiet: link "Not for messages that «Evening summary» takes, while it is on". The check list offers "Write as Not for tag digest".
- Away becomes Presence with links to the four policies above and the mark "Did nothing in 1.0". The check list offers Keep as before or Let it act; Let it act shows, before Save, what Presence would then do.
- Band: Quiet hours and Summarize all let critical through, so the band starts with critical, Wakes everyone. Presence gets Not for critical.
- Warning reminder: Count from when it was created.

Every message gets the same deliveries as before, whatever the switches do later. A setup whose Away sat higher in the list (moved up by hand) gets links on the policies below it instead, by the same rule.

### 12. A second, overlapping policy of the same type

Anna adds Quiet hours "Late weekend" (all severities, Not for critical; Sat 23:00 to 09:00; wait) next to "Weekends" (info, success; Fri and Sat 23:00 to 09:00; quietly). Before Save: "Saturday 23:00 to 09:00, info and success: both act; «Late weekend» waits, which is stricter, so these messages wait until 09:00. Warnings on Saturday night: only «Late weekend» acts. Tag alarm for the Admins is on Always gets through and is not held." Two reminders get the scenario 5 sentence; sending policies of other types get "Both run".

## 6. Migration from 1.0.0 (D-213)

The conversion only adds keys. It never rewrites For, `policy_order` or `policy_mode`. A downgrade reads what 1.0.0 wrote.

Types:
- `summarize`, `quiet_hours`: hold lane, fields unchanged.
- `away`: `presence` as designed (D-212, D-214), hold lane; `away` still read.
- `deliver`, `escalation`, `reminder`, `fallback`: send lane, fields unchanged.
- Converted Escalation and Reminder: `count_from: created` (the 1.0.0 timing).

Critical passes (supersedes D-211 if accepted):
- If every Quiet hours policy has `critical_passes` on and every Summarize policy has `include_critical` off, the band starts with one entry: critical, Wakes everyone. Otherwise the band starts empty, and each of those policies that let critical through gets Not for critical.
- Presence (from Away) with `critical_passes` on gets Not for critical. The band does not pass Presence, so this keeps 1.0.0.
- The old fields stay stored for a downgrade.

Mode "only the first" (`first`):
- Each automatic policy gets `not_with`: the subentry IDs of the automatic policies above it in `policy_order` whose For can overlap its own. At run time it does not fit a message when a linked policy is enabled and fits it. This is the 1.0.0 rule, including later switch changes.
- A policy that no message can reach with the switches at upgrade time is marked "Did nothing in 1.0" on the check list. The links stay; the mark only explains.
- Where a link equals a fixed Not for chip while both policies are on, the check list offers to write the chip.
- Restore 1.0 links recomputes all links from the kept `policy_order`.
- Manual policies were never shadowed and get no links.

Mode "all that apply" (`all`):
- Scopes unchanged.
- Reminders that overlap another on a channel get Runs alongside on.
- Timing kept by `count_from: created`.
- No behaviour change.

Stored options and names:
- `policy_mode` and `policy_order` stay stored and are no longer read, except by Restore 1.0 links. The drag list goes away. New option `policy_model: lanes` marks a converted entry. The band is stored in the entry options as `pass_through` (entries of severities, tags, wakes).
- Switch entity IDs in calls (D-198), `match_policies_automatically` (D-189), watch-rule named policies (D-145): unchanged. A named policy joins its lane and ignores its own links, as in 1.0.0, where a named policy ignored the order.

Visible changes: two lanes, the band, links and Not for chips on converted policies, the check list. Behaviour changes at conversion: none. CHANGELOG lines: "Policies are shown in two lanes with an Always gets through list; the order and the mode setting are gone; converted setups behave as before." Each offer on the check list is a change the user chooses, and Restore 1.0 links undoes it.

## 7. Engine impact

Reused:
- The chain Summarize, Quiet hours, Presence, Fallback already behaves like "stricter counts". Each stage holds or changes, a released delivery passes again, Quiet skips repeats in a wait window, and Away ignores repeats.
- Held rows and release on arrival or at a time, timer rows per policy, `_drop_inapplicable_timers`, overdue-once. `_arm` already skips a message held by a summary (`is_held`).
- Matching by severity and tag, the "In words" builder, the overlap note (D-151).

New, with rough cost:
- `for_message` returns every fitting policy (the `all` path) with Not for and `not_with`. S.
- Band check per delivery and recipient in the Quiet hours and Summarize stages, replacing `critical_passes` and `include_critical` at run time. S.
- Count from reached: arm timers on the first non-banner delivery that was sent, or on release; keep "when created" for converted policies. M.
- Reminder resolution per channel, per-reminder counts, Runs alongside, recomputed when an Only if changes (D-216 listeners). A send whose time came while its Only if was false goes when it turns true, if still unacknowledged. M, or L if the D-216 listeners are not built yet.
- Conversion with `not_with`, the "Did nothing" mark, the offers, Restore 1.0 links. M.
- Checker and log lines: one dry-run websocket command over matching and the chain. M.
- Panel: two lanes, band form with the warning before Save, Not for, links, Count from, Runs alongside, Where it overlaps, check list; remove the drag list. L.
- Translations in four languages and docs. M.

## 8. Risks and what the design gives up

Risks:
- The band is still strong. An entry with Wakes "everyone it goes to" wakes the household for every message of that kind. The band names it in words and warns before a change that stops waking, but it cannot say who changed it.
- Wakes adds a second question to each entry. Anna may not see why the Admins are woken and she is not. The checker shows it per recipient, and the page does not explain it otherwise.
- "Stricter counts" can surprise: a dropping window next to a waiting one drops. Where it overlaps shows this only for policies of the same type; the checker covers the rest.
- Converted links read oddly ("Not for messages that Evening summary takes, while it is on") until the user accepts the offered chip. They are exact, so the page is busier for a while after the upgrade.
- The band does not pass Presence. A user who adds a Presence policy for push to all messages will hold alarms for away people until they arrive. The Presence form warns when its For covers a band entry.

Given up:
- A user-set order. Strength comes from the action, the reminder rhythm and the band only.
- Passing Presence by permission. Where people are always counts.
- A band with time or condition ("let warnings through while the alarm is armed"). Severity, tag and whom only.
- A fallback stronger than its message.
- The choice between modes.
