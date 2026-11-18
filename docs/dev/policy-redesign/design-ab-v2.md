# Policy redesign, design AB v2: two lanes, one band, promises on every card

Merged design of A v2 and B v2, written by Designer A on 2026-11-18 after the distinctness check found that both had reached the same model. Sources: [design-a-v2.md](design-a-v2.md), [design-b-v2.md](design-b-v2.md), the reviews [by A](review-by-a.md), [by B](review-by-b.md), [by C](review-by-c.md) and [by D](review-by-d.md). Mockup, updated in place: [policy-redesign-a.html](../mockups/policy-redesign-a.html). Sample names only.

## Answers to the reviews

Raised against A (by B, C, D) and against B (by A, C, D), merged where they say the same thing.

- The way through worked per message, so it woke everyone and passed Presence (A, all three). Fixed: each Gets through entry covers "everyone it reaches" or "only these" people, audiences or speakers. It passes Quiet hours and Summarize only, never Presence.
- The way through bundled a permission with a send (B, by A, C, D). Fixed: an entry never sends. The push lives in a Deliver policy; both cards name each other ("Sent by Alarms to Admins", "Lets through: tag alarm"). Switching off waking does not stop the push.
- Who may be woken had to be kept in step with every sending policy (B, by D). Fixed by the default "everyone it reaches": a fallback or escalation added later is covered. "Only these" is a deliberate narrowing.
- A new hold after migration did not let critical through (B, by C). Fixed: an entry passes kinds of hold, never a list of policies, so a new Quiet hours policy is passed from its first save. A converted hold that held critical in 1.0 carries the visible line "Holds these anyway". The band lists every such hold.
- Conversion was a snapshot of switch states (A, by B and D). Fixed: converted policies get links checked on every message ("not for messages that Evening summary takes, while it is on"). Restore 1.0 links recomputes them from the kept `policy_order`.
- Scenario 11 used the wrong order (B, by A). Fixed: the introduction's order (`welcome.py`) plus a later Away at the end; Away acts on nothing in 1.0.
- The rules hid repeats that skip (A, by B). Fixed: rule 1 says it.
- "Steps aside" was an order in disguise and rule 1 had exceptions (B, by A). Fixed: links exist only on converted policies; Not for severities and tags cover new wishes.
- Per-rhythm limits stopped repeats without notice (A by D, B by C and D). Fixed: each reminder counts its own repeats. Inside one reminder with Faster while, one count and one limit cover both rhythms. The form names the last possible repeat.
- A wide reminder silently overrode a narrow one (B, by D). Fixed: the promise line on the narrow reminder's card says "Bent for warnings: Every 5 min repeats faster".
- Two reminders lost a stream in "all" setups (A, by C). Fixed: Runs alongside other reminders, switched on by the conversion where reminders overlap.
- D-211 was reopened without naming it (A, by C). Accepted and named: Gets through replaces the per-hold "Critical messages pass" on Quiet hours and Summarize; this needs a maintainer decision.
- Sentence forms broke in four languages at 380 px (B, by A, C, D). Fixed by dropping sentence forms: ha-form fields with plain labels, and the sentence shown read-only (section 3).
- A list of quiet windows changed the stored shape (B, by A). Fixed by not doing it: one window per Quiet hours policy; two policies work side by side.
- An info message's fallback cannot speak at night without making the message loud (A, by C). Accepted: a fallback is never louder than its message. An entry with "only these: Kitchen speaker" makes only the speech loud.

## What came from A, what came from B

From A:
- Two lanes plus the band between them as the page layout, and the model that strength sits only in the band.
- An entry passes only holds about time (Quiet hours, Summarize); Presence is never passed.
- Not for severities and tags; per-reminder counts; Runs alongside; repeat rhythm resolved per channel.
- The check list after the update ("Keep as before", "Let it act"), and keeping the 1.0 type names.

From B:
- Each band entry is its own policy (`get_through`) with a switch entity, so an automation can turn it off (D-198).
- Promise lines on every card: "Kept", "Bent for … by …", "Never acts".
- Faster while inside one reminder; the "Only when named" section; Show details for Ben; ready-made starting points under Add.
- The history timeline filled from the ledger (Q2) and "says why" in the checker.
- "Holds these anyway" for converted holds; scope default "everyone it reaches".

Settled where they differed:
- Band on the page or a goal in a list. Both: each entry is a policy with a switch (B), shown together as the band between the lanes (A). The switch makes "no waking while we are on holiday" an automation. The band keeps "what can wake me" in one place for Chris.
- Whether Presence can be passed. Never (A). Presence answers "is anyone there to receive it", not "how loud". A leak spoken into an empty house helps nobody. A Presence policy that must not hold critical says Not for critical, on the policy where Anna looks. B's tick would give each entry a second dimension and make the band harder to read.
- One shared rhythm or per-reminder counts. Both, split cleanly. The time comes from the shortest rhythm in force on a channel (both designs agreed). The count belongs to each reminder (A), so a slow reminder never stops at once. Inside one reminder, Faster while shares one count and limit (B), which is the simplest way to write scenario 5.
- Promise lines. Taken from B. They answer Q3 on the card itself, where Ben edits. B's risk is length and correctness, so lines have a short form and a test per scenario.
- Sentence display. The sentence is shown, not edited. ha-form fields have one label each, which translates and reads aloud cleanly. B's fragment labels such as "innerhalb von" do not stand alone for a screen reader, and they need a split per language. The sentence appears on the card, at the top of the form and in the checker.

## 1. The mental model

"Calming policies decide when a message may reach people, sending policies decide who else gets it and how often, the Always gets through list says which messages may wake whom anyway, and every card tells you whether it gets its way."

## 2. Vocabulary

English then German. The 1.0 type names stay.

- Policies (page) / Richtlinien; Policy / Richtlinie
- Keep it calm (lane) / Für Ruhe sorgen
- Make sure it arrives (lane) / Damit es ankommt
- Always gets through (band) / Kommt immer durch; entry type Gets through / Kommt durch
- Only when named (section) / Nur wenn genannt
- Covers: everyone it reaches / alle, die sie erreicht; only these / nur diese
- Holds these anyway / Hält sie trotzdem
- Quiet hours / Ruhezeit; Presence / Anwesenheit; Summarize / Zusammenfassen
- Deliver / Zustellen; Escalation / Eskalation; Reminder / Erinnerung; Fallback / Ersatz
- Which messages / Welche Meldungen; For / Für; Not for / Nicht für; Only if / Nur wenn
- Not for messages that … takes, while it is on / Nicht für Meldungen, die … übernimmt, solange sie an ist
- Faster while / Öfter, solange; Runs alongside other reminders / Läuft neben anderen Erinnerungen
- Count from: when it has reached someone, when it was created / Zählen ab: sobald sie jemanden erreicht hat, ab dem Erstellen
- Kept / Eingehalten; Bent for … by … / Eingeschränkt für … durch …; Never acts / Wirkt nie
- What happens to a message? / Was passiert mit einer Meldung?; Show details / Details zeigen
- Check after the update / Nach dem Update prüfen; Keep as before / Wie bisher lassen; Let it act / Wirken lassen; Restore 1.0 links / 1.0-Verknüpfungen wiederherstellen
- Held, Released, Sent quietly, Dropped, Skipped / Zurückgehalten, Freigegeben, Leise gesendet, Verworfen, Ausgelassen

## 3. Structure

### The Policies page, top to bottom

1. What happens to a message? Severity, tag, time, who is home, source (automation or watch rule). The answer is one line per recipient and channel, each with the policy that caused it and why ("because it is tagged alarm"). The same lines fill each message's history from the ledger ("Held until 07:00 by Night quiet; Alarms wake Admins would have let it through, but it is off").
2. Check after the update (after a conversion, until dismissed).
3. Lane "Keep it calm": Quiet hours, Presence, Summarize. Top line: "These act on every delivery, also on what the other lane adds. Where two disagree, the calmer counts. Repeats never wait: they are skipped."
4. Band "Always gets through": one row per entry, each with its switch, which messages, whom it covers, and the Deliver policies that send those messages. Top line: "For these messages, quiet hours and summaries do not apply to the people covered. Presence still decides by where people are." Below the rows, every hold marked "Holds these anyway".
5. Lane "Make sure it arrives": Deliver, Escalation, Reminder, Fallback. Top line: "Every sending policy that fits runs. Escalations and reminders start counting once the message has reached someone."
6. Only when named: manual policies with their switch entity IDs.

Each card has its type in text, the sentence, a switch whose aria label names the policy, and the promise line. Show details adds the type key, entity ID, stored fields and YAML. There is no order, no drag and drop, no mode.

### Promise lines

Computed by the checker's dry run over every severity, every tag a policy names and the hours of one week:
- "Kept."
- "Bent for doorbell messages at night by Night quiet: sent quietly."
- "Bent for tag alarm by Alarms wake Admins: let through for the Admins."
- "Never acts: Critical delivery, Warning reminder, Evening summary and Night quiet take all its messages first (kept from 1.0)."

When more than two cases apply, the short form is "Bent for 3 kinds of message: see What happens".

### The form of one policy

ha-form fields with one plain label each:
- Name, enabled, type with its lane in text.
- Which messages: Automatically or Manually, For, Not for, converted links, Only if (D-216).
- What it does: the type's fields (1.0, and D-212, D-214 for Presence). Reminder adds Faster while, Runs alongside and Count from. Escalation adds Count from. Gets through has Which messages and Covers.
- At the top, read-only, updated live: the sentence and the promise line. Below Save: Where it overlaps, one sentence per policy it meets, and a warning before Save when the change takes waking away ("Messages tagged alarm will no longer wake the Admins at night").

Add a policy starts from plain outcomes ("Wake the Admins for leaks", "Quiet nights for small things", "Speak only when someone is home", "Summarize digest at 20:00"). One outcome fills one policy. "Wake the Admins for leaks" offers a second step that adds the Deliver policy, shown as its own card.

## 4. Conflict rules

1. Every policy that fits a message acts; on one delivery the calmest hold counts (summary, then drop, then wait, then quiet), a released delivery passes all holds again, and a repeat is skipped where it would wait (Presence does not check repeats).
2. On each channel a message keeps one repeat rhythm, the shortest among the reminders that fit at that moment, unless a reminder runs alongside; each reminder counts its own repeats, and escalation and reminder clocks start once the message has reached someone.
3. A Gets through entry lets its messages pass Quiet hours and Summarize for the people it covers, except a converted hold marked "Holds these anyway"; Presence is never passed.

Definitions: a policy fits when For, Not for, its links and Only if all match (unknown counts as whatever delivers more, D-216). A message has reached someone when a delivery other than the banner was sent to a person or speaker, or when the banner is its only channel. A named policy joins its lane and follows these rules. A held delivery is not a failure and never triggers a Fallback. Two reminders with the same rhythm: the one created first counts.

## 5. The twelve scenarios

1. Leak, warning, 03:00.
   - Configure: from "Wake the Admins for leaks", Gets through "Alarms wake Admins" (tag `alarm`, covers only Admins) and Deliver "Alarms to Admins" (tag `alarm`, push with sound). Night quiet: all severities, 22:00 to 07:00, quietly.
   - Happens: the Admins' push rings at 03:00; Anna's push from the automation is quiet. An info message is quiet for everyone. Night quiet's card says "Bent for tag alarm by Alarms wake Admins". Nothing is critical.
2. Two quiet windows.
   - Configure: Quiet hours "Weeknights" (info, success; Sun to Thu, 22:00 to 07:00) and "Weekends" (Fri and Sat, 23:00 to 09:00), both quietly.
   - Happens: both act; warnings are outside For. Where it overlaps: "Weekends adds Friday and Saturday nights; it does not overlap Weeknights." Both cards: "Kept".
3. Doorbell.
   - Configure: Presence "Doorbell in an empty house": tag `doorbell`, speech, drop when nobody of the household is home, Only if guest mode is off.
   - Happens: nobody home, no guests: no speech, push sent. Guest mode on: spoken. Night quiet still acts on other messages; at 23:00 a doorbell is sent quietly, and the Presence card says so.
4. Critical, push and repeat.
   - Configure: Deliver "Critical to Admins"; Reminder "Critical repeat" (every 10 min, at most 12); Gets through "Critical" (covers everyone it reaches, the starting entry).
   - Happens: push at once, repeats every 10 min, also at night. An acknowledgement on any device stops them.
5. 15 min only if X, otherwise 1 h.
   - One policy: Reminder "Warnings", every 60 min, Faster while X is on: every 15 min, at most 12 in all.
     - 00:00 delivery, next at 01:00.
     - 00:15 X turns on: last delivery + 15 = now, so repeat 1 goes.
     - 00:30 and 00:45: repeats 2 and 3.
     - 00:50 X turns off: next is 00:45 + 60 = 01:45.
     - The form says "At most 12 repeats in all, whatever the rhythm."
   - Two policies ("Urgent" 15 min only if X, at most 8; "Hourly" 60 min, at most 3): same times. Each counts its own repeats, so Hourly still has its 3 after X turns off. Both cards: "Bent while X is on: Urgent repeats faster".
6. Shopping list.
   - Configure: Presence "Shopping list on leaving": tag `shopping`, push, hold while the recipient is in Home.
   - Happens: Anna's push waits and goes when she leaves, checked per recipient. Released at 06:30, it passes the holds again and goes quietly.
7. Digest.
   - Configure: Summarize "Evening summary": tag `digest`, 20:00.
   - Happens: a summary is the calmest result, so only the summary holds a digest message; Night quiet acts on the summary delivery at 20:00 and does nothing. Collected messages start no sending policy (1.0). Both cards: "Kept".
8. Nobody reached.
   - Configure: Fallback "Say it in the house": Kitchen speaker.
   - Happens:
     - A warning: spoken at once.
     - An `alarm` at 03:00: spoken only if "Alarms wake Admins" covers everyone it reaches, or names Kitchen speaker.
     - Nobody home with a Presence policy on speech: dropped.
     - Info at night: quiet. The card says "Bent for info and success at night by Night quiet".
   - A held push is not "nobody reached".
9. Escalation while held.
   - Configure: Quiet hours "Night wait" (info, wait) and Escalation "Nobody looked" (info, 30 min, Admins).
   - Happens: an info message at 23:00 reaches nobody until 07:00, and the escalation goes at 07:30. Count from "when it was created" gives 23:30, and that delivery waits too unless an entry covers it.
10. Critical watch-rule message.
    - Configure: the scenario 4 policies. A rule message (tag `rule`) fits by severity.
    - Happens: pushed to the Admins, with the same switch and no YAML.
11. 1.0 starter list plus Away, mode first (worked in section 6).
    - Every message gets the same deliveries.
    - Presence shows "Never acts (kept from 1.0)" with Keep as before and Let it act.
    - Night quiet's link offers "Write as Not for tag digest".
12. Second overlapping policy.
    - Configure: Anna adds Quiet hours "Weekend lie-in" (info, Sat and Sun 06:00 to 10:00, wait).
    - Happens, before Save: "Where both fit (info, Sat and Sun 06:00 to 09:00) the calmer counts: info waits until 10:00." Weekends' line becomes "Bent for info on weekend mornings by Weekend lie-in". The Critical entry still passes the new hold, because it passes the kind Quiet hours. Nothing blocks Save (D-151).

## 6. Migration from 1.0.0 (D-213)

The conversion only adds keys and subentries. It never rewrites For, `policy_order` or `policy_mode`, so a downgrade reads what 1.0.0 wrote and ignores the new subentry type.

- Types: the seven keep their keys and lanes; `away` becomes `presence` (D-214). `apply: manual` moves to Only when named. Converted Escalation and Reminder get Count from "when it was created". Converted Presence keeps "repeats not checked".
- Critical passes (supersedes D-211 if accepted):
  - If any Quiet hours policy had `critical_passes` on, or any Summarize policy had `include_critical` off, the conversion adds the Gets through policy "Critical" (critical, everyone it reaches). Each Quiet hours or Summarize policy that held critical in 1.0 gets "Holds these anyway".
  - Presence with `critical_passes` on gets Not for critical.
- Mode first: each automatic policy gets links to the automatic policies above it in `policy_order` whose For can overlap. The links follow switches. Policies no message can reach show "Never acts". Restore 1.0 links recomputes them.
- Mode all: no links. Reminders that overlap on a channel get Runs alongside.
- Worked scenario 11. Stored order Critical delivery, Warning reminder, Evening summary, Night quiet, Away (added later). Converted:
  - Night quiet is linked to Evening summary.
  - Presence is linked to all four and never acts.
  - "Critical" is added; Presence gets Not for critical.
  - Warning reminder counts from creation.
  - With Away stored higher, Warning reminder and Critical delivery get the links instead, by the same rule.
- Names: switch entity IDs in calls (D-198), `match_policies_automatically` (D-189), watch-rule named policies (D-145) unchanged. A named policy ignores its links, as it ignored the order in 1.0.
- `policy_order`, `policy_mode`: kept, read only by Restore 1.0 links. New option `policy_model: lanes`.

Nothing changes at upgrade. Every offer on the check list is a user step with its way back, and each kind of offer is one CHANGELOG line.

## 7. Engine impact

Reused:
- The chain already behaves like "calmest counts": it re-checks released deliveries, skips repeats in a wait window, and Away ignores repeats.
- Held rows and their releases, timer rows, `_drop_inapplicable_timers`, overdue-once, `is_held` for summaries, matching, the In words builder, the overlap note.

New, with rough cost:
- `for_message` on the "all" path with Not for and links: S.
- `get_through` subentry type with its switch; pass check per delivery and recipient in the Quiet hours and Summarize stages; "Holds these anyway": M.
- Count from reached: M.
- Reminder rhythm per channel, per-reminder counts, Faster while, Runs alongside, re-planned when an Only if changes: M (L if the D-216 listeners are not built yet).
- Conversion, links, check list: M.
- Dry run for the checker, history lines and promise lines over severity × tag × week (four severities, named tags, 168 hours): L.
- Panel: lanes, band, forms, Only when named, Show details: L. Translations in four languages: M.

## 8. Risks and what the design gives up

- Biggest risk: promise lines. They are computed over a grid; a wrong or slow line makes the whole page untrustworthy, and a long one breaks 380 px. They need a test per scenario and the short form.
- An entry covering everyone it reaches wakes the household for every message of that kind. The band, the warning before Save and the history make it visible; nothing shows who changed it.
- Wakes for some and not others is a new idea; Anna may not see why only the Admins were woken. The checker answers per recipient.
- Converted links and "Holds these anyway" make the first look after the upgrade busy, until the user accepts the offers.
- Given up:
  - a user-set order and the modes;
  - passing Presence by permission;
  - entries with time or condition;
  - a fallback louder than its message;
  - sentence-shaped forms;
  - several windows in one Quiet hours policy;
  - B's renamed types (Also send, Pass on, Repeat, If unreached), kept out so that 1.0 entity names, docs and translations stay.
