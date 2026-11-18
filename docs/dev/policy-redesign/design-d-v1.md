# Policy redesign, design D (v1): message types

Stance: behaviour belongs to the kind of message, not to rules that match severity and tag. A message has exactly one type; the type carries everything that happens to it. Round one, independent of the other designs. Sample names only.

## 1. Mental model

"Every message is of one type, such as Alarm, Doorbell or Digest, and its type alone decides who gets it, how, at night, and what happens if nobody reacts."

The only thing outside types is the house's quiet times: they are clock windows that do nothing by themselves; each type says what they mean for it.

## 2. Vocabulary

Every term the user sees, English then German. The word "policy" leaves the page; it stays only in old YAML.

- Message types / Nachrichtenarten (the page, replaces "Policies" / "Richtlinien")
- Type / Art (one entry; in a call the field `type`)
- Type key / Schlüssel der Art (the stable name used in calls, set once, for example `doorbell`)
- Used for / Gilt für (which messages get this type without naming it)
- Tagged / Mit Tag
- Severity / Schweregrad (kept from 1.0.0)
- Everything else with severity ... / Alles andere mit Schweregrad ... (the severity default)
- Also send / Zusätzlich senden (1.0.0 Deliver)
- Quiet times / Ruhezeiten (house-wide windows)
- During quiet times / Während der Ruhezeiten, with the choices: Wait until they end / Bis zum Ende warten; Send quietly / Leise senden; Drop / Verwerfen; Send as usual (may wake people) / Normal senden (darf wecken)
- May wake people / Darf wecken (badge on the type card)
- Presence / Anwesenheit (D-212 wording kept)
- Repeat / Wiederholen (1.0.0 Reminder), with "every", "at most", "faster while" / "alle", "höchstens", "schneller solange"
- Escalate / Eskalation (1.0.0 Escalation), "after ... minutes without acknowledgement" / "nach ... Minuten ohne Bestätigung"
- If nobody was reached / Wenn niemand erreicht wurde (1.0.0 Fallback)
- Collect into a summary / In einer Zusammenfassung sammeln (1.0.0 Summarize)
- Only while / Nur solange (D-216 "only if", attached to one setting)
- Clocks start / Zeit läuft ab: when first delivered / ab der ersten Zustellung; when the message appears / ab dem Erscheinen
- Try a message / Nachricht ausprobieren (the preview at the top of the page)
- Added by the call / Vom Aufruf hinzugefügt (steps named in YAML)

## 3. Structure

### The page "Message types"
Three blocks, top to bottom, all single column at 380 px:

1. Try a message. Severity, tag (optional), time of day. Answers in one sentence: "Type Alarm. Push with sound to the Admins at once; repeats every 10 minutes; sent as usual during quiet times (may wake people)." It also says why: "because it is tagged `leak`" or "because it is critical and no type claims its tag". This answers Q1 and most of Q2.
2. Quiet times. A short list of named windows (from, to, days). Each row says how many types send as usual during it: "Weekday nights, 22:00 to 07:00, Mon to Fri. 2 types may wake people."
3. Types. One card per type, alphabetical (no order to manage). A card shows: name, key, "Used for" line, a badge row with text and icon (never colour alone): "May wake people", "Holds by presence", "Summarized", "Repeats", and the "In words" line. A type that no message can reach shows "No message gets this type unless a call names it".

There is no drag list, no mode switch, no order anywhere. Strength is not ranked: it is written inside each type ("Send as usual during quiet times").

### How a message gets its type
Decided once, when the message appears, and stored on the message; it never changes during the message's life.

1. The call names it: `type: doorbell` (new optional field of `heads_up.notify`).
2. Else the type whose "Used for" names the message's tag (optionally only for some severities).
3. Else the type set for the message's severity under "Everything else with severity ...".

The form guarantees uniqueness instead of an order: one tag-and-severity pair belongs to at most one type, and each severity has exactly one default type. Saving a claim that another type holds moves it, and the form says so before Save (section 5, scenario 12). Watch-rule messages have tag `rule` and their severity, so they follow steps 2 and 3 like any message without a tag.

### The form of one type
Fixed sections, each at most once per type, each optional and collapsed when off. The order on screen is the order of a message's life:

- Name, key (read-only after creation, with a copy button), Used for (tags, optional severities), Everything else with severity (checkboxes, each severity shows which type has it now).
- Also send: channels and recipients at once (D-121, D-181 "from the call" kept).
- Collect into a summary: every N minutes or at a time.
- During quiet times: one choice for all windows, or "set per quiet time" to choose per window.
- Presence: per channel, as specified in D-212 and D-214, with "Only while" (guest mode).
- Repeat: every N minutes, at most M times, channels; "faster while" a condition: every K minutes.
- Escalate: one or more stages, each "after N minutes without acknowledgement, send to ...", sorted by minutes.
- If nobody was reached: channels and recipients.
- Clocks start: when first delivered (default) or when the message appears.
- In words: the whole type in two to four sentences, live.

Every section in an existing 1.0.0 policy becomes a "step" internally and keeps its switch entity, so YAML that names or toggles a 1.0.0 policy switch keeps working (D-198). The switch shows in the section header as the section's on/off toggle.

## 4. Conflict rules

1. A message has exactly one type (named in the call, else claimed by its tag, else set by its severity), and only that type acts on it, plus any step the call names by switch.
2. A type's quiet-time and presence choices hold every delivery of the message, its repeats, escalations, fallback and summary included, and repeat and escalation clocks start when the message is first delivered unless the type says "when the message appears".
3. Nothing passes a quiet time or presence hold except a type set to "Send as usual" for it, which the page shows as "May wake people"; severity never passes by itself.

## 5. Scenarios

1. Water leak, warning, 03:00. Chris opens type Alarm, adds tag `leak` to Used for. Alarm: also send push with sound to Admins, during quiet times "Send as usual". The leak arrives tagged `leak`, gets type Alarm (tag beats severity), pushes to the Admins at 03:00. An info at 03:00 has type Everyday, set to "Send quietly": passive push, no sound. The Alarm card shows "May wake people"; the leak tag is visible on it.
2. Two windows. Anna adds quiet times "Weekday nights" 22:00 to 07:00 Mon to Fri and "Weekend nights" 23:00 to 09:00 Sat and Sun. Type Everyday (default for info and success) is "Send quietly" during quiet times. Type Warning is "Send as usual". The form says: "Weekend nights adds Saturday and Sunday 23:00 to 09:00. It does not overlap Weekday nights." (Friday 22:00 to Saturday 07:00 is covered by Weekday nights because a window belongs to the day it starts.)
3. Doorbell. Anna adds type Doorbell, key `doorbell`, Used for tag `doorbell`. Also send: speech on Kitchen speaker. Presence, speech: only when somebody of Household is home; Only while: skip this when guest mode is on. During quiet times: Send quietly (no speech at night). Nobody home, guest mode off: push goes out, nothing spoken. Guest mode on: spoken whoever is home. Night quiet for other messages is untouched: it belongs to other types.
4. Critical repeated. Type Alarm (default for critical): also send push to Admins; Repeat every 10 minutes, no maximum. First push and repeats are sections of one type and cannot block each other. Acknowledging on any device stops the repeat (unchanged engine).
5. Two rhythms. Ben's type Warning: Repeat every 60 minutes, faster while `binary_sensor.x` is on: every 15 minutes. At 0 X is off, next repeat planned at 60. At 15 X turns on; the repeat is re-planned to "last delivery plus 15 minutes", which is now, so it fires at 15, then 30, 45 while X stays on. The count continues (the form says "The count does not restart when the rhythm changes"). If X turns off, the next one is "last plus 60". The type does not change, because "only while" changes a setting, never which type the message has.
6. Shopping list. Type Shopping, key `shopping`, the automation calls with `type: shopping`. Presence, push: hold while the recipient is home, send when they leave (after the presence delay), maximum wait 12 hours then drop. Only Anna's messages of this type are held; other types have no presence step.
7. Digest. Type Digest, Used for tag `digest` with severity info or success. Collect into a summary at 20:00. During quiet times: Send quietly. The summary is one delivery of type Digest; nothing else holds digest messages because they have no other type. Other info messages have type Everyday and are not summarized. A warning tagged `digest` goes to Warning (the claim names only info and success); the card says so.
8. Fallback. In the type that needs it (starter: Alarm and Warning), If nobody was reached: speech on Household speakers. The fallback follows its type's quiet-time and presence choice (rule 2), and the In words line says it: "If nobody was reached, the Household speakers say it, also at night." For Alarm that is "Send as usual", so it speaks at night.
9. Escalation while held. Type Warning: during quiet times "Wait until they end"; Escalate after 30 minutes. A warning at 02:00 is held until 07:00; the escalation clock starts at the first delivery, so it escalates at 07:30 if nobody acknowledged. Chris, wanting the other behaviour, sets Clocks start to "when the message appears": the escalation is then due at 02:30 and is held to 07:00 with the message, never sent before the message itself. To be woken, he sets Warning to "Send as usual". One rule, shown on the card.
10. Critical watch-rule message. A watch rule sends a critical banner with tag `rule`. No type claims `rule`, so it gets the critical default, Alarm, and the Alarm's push to Admins and repeats apply. Same type as a critical `notify`; no YAML.
11. 1.0.0 starter list plus Away. Migration (section 6) produces types "Critical delivery" (default for critical), "Warning reminder" (default for warning), "Night quiet" (default for info and success, quietly during the quiet time "Night quiet"), "Evening summary" (tag `digest`, info and success). Under "only the first", an Away policy below them was never reached by any severity; it becomes type "Away" with no claims, shown as "No message gets this type unless a call names it". Every message gets the deliveries it got in 1.0.0. The three types that do not quiet at night show "May wake people", which was true before and is now visible.
12. Overlapping second definition. Anna creates type "Loud doorbell", Used for tag `doorbell` with severity warning. Before Save, the form says: "Warning messages tagged doorbell now get the type Doorbell. After saving they get Loud doorbell; Doorbell keeps the other severities." Inside one type a second Repeat or Presence cannot be added, so the 1.0.0 case "two reminders that overlap" does not arise; two quiet windows that overlap get the sentence "Where they overlap, each type uses its stricter choice (drop, then wait, then quietly)". Nothing blocks Save (D-151 kept).

## 6. Migration from 1.0.0 (D-213)

The migration computes, for every severity and every tag mentioned by any policy (plus "no or another tag"), which 1.0.0 policies acted on such a message. Cells with the same set of policies become one type.

- Mode "first": each cell's set is the first matching policy, so each reachable automatic policy becomes one type named after it. Cells with no policy go to type "Everything else" with no sections.
- Mode "all": each distinct set becomes a type named by joining its policy names ("Night quiet + Away"); the user can rename. If a set contains two policies of one kind (two reminders), both are kept as sections marked "kept from 1.0.0, runs side by side", with a button to merge.
- `policy_order` is used only for the computation above, then no longer read; it stays in storage for a downgrade.
- Summarize, Deliver, Escalation, Reminder, Fallback: become the matching section of each type whose set contains them. `include_critical` off means the critical cells never contained it.
- Quiet hours: each window becomes a house quiet time with the policy's name; each type whose set contained the policy gets that policy's action for that window, others get "Send as usual". `critical_passes` on means the critical cells did not contain it.
- Away (stored `away`, read as `presence`, D-214): the Presence section of each type whose set contains it.
- `apply: manual`: becomes a type with no claims, key from its name; the policy subentry stays as its step with its switch.
- Named policies in calls and watch rules: a name or switch entity in `policy` keeps today's meaning. Without `automatic` the message gets a hidden type made of the named steps only (as today). With `automatic` or in addition (D-189), the named steps are added to the message's type, shown in the trace as "Added by the call". Watch rules (frozen) keep their stored policy name; it resolves the same way.
- Timing: migrated types get "Clocks start: when the message appears", which is the 1.0.0 behaviour; new types default to "when first delivered".

Visible changes: the page is new; policy names become type names; badges show "May wake people" on types that never were quieted. No delivery changes. CHANGELOG lines: "Policies become message types; each 1.0.0 setup converts with the same deliveries"; "New `type` field in `notify`"; "New types start escalation and repeat clocks at first delivery; set Clocks start to 'when the message appears' for the old timing." Way back: the timing setting above; downgrade to 1.0.0 reads the untouched policy subentries and `policy_order` from the backup.

## 7. Engine impact

- Reused: chain stages Summarize, Quiet, Presence, Fallback; timer rows, `_drop_inapplicable_timers`, overdue-once, holds with release on arrival or at a time; policy subentries and switches as steps; the "In words" builder per section.
- Type assignment at message creation, stored `type_id` on the message; `PolicyBook.for_message` returns the steps of that type plus named steps. S.
- New subentry kind `message_type` (name, key, claims, severity defaults, clocks start); steps get `type_id`; house quiet times as subentries. Claim uniqueness check in the form. S to M.
- Quiet stage reads house windows and the type's per-window choice. S.
- Clocks at first delivery: arm timers on the first non-held delivery or on release instead of on appear. M.
- Repeat "faster while": condition listener per running message re-plans the timer row, count kept. M.
- Migration by cells, with fixtures from a clean 1.0.0 instance (OPEN_QUESTIONS, 1.1.0 design). M.
- `type` field in `notify` schema, `services.yaml`, four translations, Test send. S.
- Panel: types page, Try a message, quiet times list, type form with sections, overlap sentences. L.
- Overall: L, most of it in the panel.

## 8. Risks and what the design gives up

- Biggest risk: severity loses its special power. A user can make the critical default type quiet at night, and Chris's fear (someone else silences alarms) moves from "the order" to "a type setting". Mitigation: the form warns before Save when a type that is a severity default for critical stops sending as usual during quiet times, and Try a message shows it.
- Messages are sorted only by tag, severity and an explicit `type`. "Doorbell, but only when the front door sensor is the source" needs the call to name the type. Watch rules cannot name a type (frozen, D-100); a rule that needs another type than its severity gives must use the stored policy name. Parity (rule 9): proposed exception, or a small change to the frozen rule form that lists types in its policy picker; maintainer decision needed.
- Sections cannot be shared: a household fallback used by four types is set four times. A "Copy to other types" action reduces the work but not the duplication.
- "All that apply" composition is gone; migrated "all" setups can produce many joined type names that look odd until renamed.
- Named steps from YAML are a seam in "one type decides": kept for D-198, shown in the trace, not offered for new setups.
- Gives up: ordering, the two modes, per-policy severity matching, "critical passes" as a field. Gains: no list order, no changing choice mid-life (pain point 4), no shared single place (pain point 2), holds and sends inside one owner (pain point 5), tags kept out of a type by claiming them elsewhere (pain point 7).
- Overlaps with the open question "Editable notify presets": a type is that preset for behaviour. Content-level fields of that idea (dismiss and snooze behaviour, default channels) could join the type later; not part of this design.
