# Policy redesign: interaction matrix for 2.0.0

Written 2026-11-20 on `release/2.0`. Every pair of policy kinds, and every kind against every sort of delivery, with what the 1.1 engine does today (read from `release/1.1`: `hub/engine.py`, `hub/policies/`), what 2.0 does under `docs/DESIGN.md` §25, and whether that is settled. Open cells were numbered O1 to O12; the maintainer decided each on 2026-11-20 (D-235, answers below). Where a row says "decided On", the 2.0 column above it shows 1.x behaviour and the answer below wins. Each row becomes one test in the build phase.

Kinds: Summarize (SUM), Quiet hours (QH), Presence (PR), Get through (GT, the band), Deliver (DL), Escalation (ES), Reminder (RM), Fallback (FB).
Sorts of delivery (`Step.origin`): the call's own (first), Deliver, escalation, reminder, fallback, summary, and a held delivery that is released.

## Engine facts the rows rely on
- The ledger has one row per message, channel and recipient. Deliver, Escalation and Fallback send with `resume=True`: a recipient who already has the message on that channel, or has it held, is skipped (`_send`).
- The chain stops at the first stage that holds or skips (`chain.run`): Summarize, Quiet hours, Presence, Fallback. A released delivery runs the whole chain again.
- Quiet hours never touch the banner. Several windows: drop beats wait beats quiet; wait holds until the latest end (`quiet.py`). A reminder in a wait or drop window is skipped.
- Presence never touches the banner or a reminder; it checks every recipient of push, popup and mail (D-232), and the household for speech.
- Summarize decides once, when the message appears, and holds every channel. A held message gets no Deliver, no Fallback and no timers (`_apply_deliver`, `_arm`, `_handle`). A message released from a summary (its policy switched off) is delivered and its timers start then, without Deliver or Fallback (`_release_held`).
- Escalation and Reminder timers are planned once, when the message appears or is updated (`_arm`); a policy that starts to apply later does not plan one.
- A reminder repeats every delivery in state sent that is not the banner, Deliver and Fallback deliveries included (`_remind`).
- Fallback looks only at the results of the call's own delivery; a held delivery counts as reached (`_unreached`). An escalation, reminder or Deliver never triggers a Fallback.

## A. Hold kinds against sorts of delivery

| Hold | Delivery | Today (1.1) | 2.0 (§25) | Status |
|---|---|---|---|---|
| SUM | first | whole message held, banner too | same, unless a fitting GT entry keeps it out (D-235) | settled |
| SUM | Deliver | none for a held message, none for the summary | same | decided O1 |
| SUM | escalation, reminder | no timers for a held message or a summary | same | settled (1.x) |
| SUM | fallback | none for a held message | same | decided O1 |
| SUM | summary | not held again | same | settled |
| SUM | released by GT | not possible today | delivered at once (D-235) | decided O2 |
| QH | first, Deliver | per delivery: drop, wait or quiet | same; GT passes it per covered recipient unless `holds_anyway` | settled |
| QH | escalation | held or quieted like any delivery | same; held is a setup mistake with a warning (D-235) | decided O3 |
| QH | reminder | skipped in wait and drop, quiet in quiet | same; GT passes it for covered recipients (scenario 4) | settled |
| QH | fallback | held or quieted | same, never louder than its message; GT covering a speaker passes it (D-235) | settled |
| QH | summary | acts on the summary delivery | same; a GT entry fits a summary by its severity (the highest) | settled |
| QH | released | runs the chain again | same | settled |
| PR | first, Deliver | holds or drops per recipient (D-232) | same; never passed by GT | settled |
| PR | escalation | held while the target is away; a held delivery is not a failure, so no Fallback | same | decided O4 |
| PR | reminder | not checked | same | settled (1.x) |
| PR | fallback | checked; an empty house drops speech | same | settled |
| PR | summary | checked | same | settled |
| GT | every sort | not a type today | passes QH for covered recipients on every sort; passes SUM only at appearance | settled (rule 3) |

## B. Two hold kinds on one message

| Pair | Today (1.1) | 2.0 (§25) | Status |
|---|---|---|---|
| SUM + SUM | the policy whose name sorts first holds it (`_summary_policy`): a hidden order | undefined | decided O5 |
| SUM + QH | the summary holds; Quiet hours act on the summary delivery | same | settled |
| SUM + PR | the summary holds; Presence acts on the summary delivery | same | settled |
| QH + QH | drop, then wait (latest end), then quiet | same | settled |
| QH + PR | Quiet hours first; a wait hold is checked by Presence only at release; quiet then Presence hold: held, then sent quietly if still quiet | same; result equals "calmest counts", only the time of a drop moves to the release | settled |
| PR + PR | both act; two policies can contradict (hold while home and hold while away): never sent until the maximum wait | same | decided O6 |
| GT + GT | not a type today | undefined: what two entries with different Covers add up to | decided O7 |
| GT + `holds_anyway` | not a type today | the hold wins | settled |
| GT + PR | not a type today | Presence wins | settled (D-224) |

## C. Two sending kinds on one message

| Pair | Today (1.1) | 2.0 (§25) | Status |
|---|---|---|---|
| call + DL | recipients add up; each recipient once per channel, the first send wins; loudness is the same for both, since it comes from the severity | same | settled |
| DL + DL | add up, each recipient once per channel | same | settled |
| DL + ES | the escalation skips recipients who already have the message on that channel, Deliver's recipients too: an escalation to people who were already pushed sends nothing new | same | decided O8 |
| DL + RM | reminders repeat Deliver's sends | same | settled |
| DL + FB | Fallback looks only at the call's own delivery: it fires although Deliver reached someone | same | decided O9 |
| ES + ES | each its own timer, each fires once (tiers work) | same | settled |
| ES + RM | after the escalation, reminders repeat its sends too | same | settled |
| ES + FB | an escalation that reaches nobody (away, failed) triggers nothing | same | decided O4 |
| RM + RM | each its own timer ("all") or only the first ("first") | one rhythm per channel, the shortest, own counts; `alongside` keeps its own (D-234, D-235) | settled |
| RM + FB | reminders repeat the fallback's sends, a speaker every N minutes | same | decided O10 |
| FB + FB | each that matches fires once | same | settled |

## D. Over the life of a message

| Event | Today (1.1) | 2.0 (§25) | Status |
|---|---|---|---|
| a policy starts to fit after the message appeared (switched on, a link target switched off, Only if true) | no timers, no Deliver; holds act on the next delivery | undefined for senders | decided O11 |
| a policy stops fitting | its planned timers are dropped at their next run or on an update | same; a held delivery is released when its Only if turns false (D-216) | settled |
| GT entry starts to fit | not a type today | releases QH holds it covers, takes messages out of summaries (D-235) | decided O2 |
| severity change | timers restart with the new policies; a summarized message that becomes critical is released | same, and GT and links are fitted again | settled |
| update of the message | Deliver's sends are updated; the call's own too | same | settled |
| acknowledgement, snooze, dismiss | stop timers; snooze pauses a person's reminders (D-078) | same | settled |
| restart | an overdue step fires once (D-081) | same | settled |

## E. Calls, names and rules

| Case | Today (1.1) | 2.0 (§25) | Status |
|---|---|---|---|
| automatic (no `policy` field) | every fitting automatic policy ("all") or the first ("first") | every fitting policy | settled |
| `policy: X` without `automatic` (call or watch rule, D-145) | only X acts, whatever its filters | same: the band, Night quiet and Presence do not act either | decided O12 |
| `policy: none` | no policy acts | same: no band, no hold | decided O12 |
| named policy and links | a named policy ignored the order | it ignores its links | settled |
| watch-rule message | fits by severity and tag `rule` | also by From watch rule | settled |
| a GT entry set to "Only when named" | not a type today | undefined | decided O12 |

## Decided cells (D-235)

- O1 Summarize and senders: a summarized message never gets Deliver's recipients or a Fallback, and the summary goes only to the people the held messages would have reached. Keep, or add Deliver's recipients to the summary?
  - Decided: Deliver's recipients get the summary too; a summary that reaches nobody triggers a fitting Fallback (O1b).
- O2 A message taken out of a summary by a GT entry: does it then get Deliver and Fallback like a new message, and do its escalation and reminder clocks count from creation (an overdue escalation fires at once) or from the release (as `_release_held` does today)?
  - Decided: runs as a new message (Deliver, Fallback); clocks count from the release.
- O3 Escalation and Quiet hours: is an escalation that Quiet hours drop, or send quietly, the same setup mistake as one they hold, with the same warning?
  - Decided: attention item for held, dropped and quiet; the Policies page warns as soon as the setup allows it.
- O4 Escalation that reaches nobody, because every target is away (Presence) or sending failed: leave it, warn, or let a Fallback act?
  - Decided: attention item, no Fallback; the Policies page warns when Presence can hold an escalation's targets.
- O5 Two Summarize policies fit one message: which one collects it? Today the name decides.
  - Decided: the summary due next collects it.
- O6 Two Presence policies that contradict (one holds while home, one while away): warn in the form, or one wins?
  - Decided: both act; the page and the form warn.
- O7 Two GT entries fit, with different Covers: does each cover its own people (together: everyone either covers)?
  - Decided: together; each entry lets its own people through.
- O8 Escalation to people who already have the message on that channel: send nothing (today), or send them the escalation again as a new push?
  - Decided: send again as a new push.
- O9 Fallback when the call's own delivery reached nobody but Deliver reached someone: fire (today) or not?
  - Decided: Fallback only when the call and every Deliver reached nobody.
- O10 Reminders repeat a fallback's speech: keep (today), or repeat only the call's own and Deliver's sends?
  - Decided: keep repeating (1.x).
- O11 A sending policy that starts to fit after the message appeared (switched on, Only if turns true): does it act on that message (Deliver sends, timers start), or only on new messages (today)?
  - Decided: switched on or freed by a link: only new messages. Only if is checked at each step for policies that fitted at appearance (O11b).
- O12 Named policies: when a call or watch rule names policies without `automatic`, or says `none`, do band entries and holds still act? May a band entry be "Only when named"?
  - Decided: automatic off means no automatic policy, holds and band included (1.x); a band entry may be "Only when named" (O12b).
