# Round 2 review by Designer B

Reviews of designs A, C and D (v1). Checked against the [fact sheet](00-fact-sheet.md) and the 1.0.0 code in `custom_components/heads_up/hub/`. Code facts used below:
- A message has exactly one tag (`applies()` in `policies/matching.py` checks `tag in policy.tags`).
- The order is stored once at first load (`initial_order()`, ranked by `TYPE_RANK`); policies created later, including those from the introduction, are appended in creation order (`PolicyBook.ordered`).
- In a "wait" window Quiet hours skips a reminder instead of holding it (`policies/quiet.py`). Away never holds a reminder or a banner, and only holds audience deliveries (`policies/away.py`).
- Summarize decides once when the message appears, and `_arm` starts no timers for a held message (`engine.py`).

## Design A: two lanes

### Failure 1: the band decides per message, not per person (scenario 1, S1)
- Chris puts tag `leak` on "Always gets through" so the Admins are woken.
- The leak automation's own audience is "everyone". At 03:00 the band makes the message skip every hold for every delivery, so Anna's phone rings too.
- If the call also asks for speech, the Kitchen speaker talks. Presence is skipped as well, so it talks into an empty house. A's section 3 names exactly this as the flaw of "May wake people".
- S1 asks that the alarm reaches "someone who acts" while nights stay quiet for everything else. A cannot say "wake the Admins, but not Anna" without editing the automation. A gives this up in section 8 ("passes all holds or none").

### Failure 2: conversion writes fixed "Not for" chips where 1.0 depended on switches (scenario 11, D-213)
- A computes "For minus the For of every enabled automatic policy above it" once, and writes it as `exclude_tags`.
- Ben has an automation that switches Evening summary off on holidays. That is what policy switch entities are for (D-186, D-198).
- In 1.0, Night quiet then quiets digest messages. After A's conversion, Night quiet keeps "Not for tag `digest`", so digest messages ring at night on holidays.
- The reverse case is a policy above that was disabled at conversion and is switched on later. 1.0 would let it shadow the one below; A does not.
- So "every message gets the same deliveries as before" is true only for the switch states at upgrade time. A needs the `not_with` link (which it already defines) everywhere, not only where the subtraction is inexact.

### Failure 3: the conflict rules leave out holds that skip instead (constraint "no exceptions hidden elsewhere", scenario 5, scenario 9)
- Rule 1 says every hold acts on every delivery, "also on those the Send lane adds", and a released delivery passes all holds again.
- In 1.0 a reminder in a "wait" window is dropped, not held, and Presence never holds a reminder at all. A keeps both stages "reused" (section 7) and never mentions either.
- Step where Ben gets it wrong: in scenario 5 he expects the 15-minute repeat at 22:15 to arrive at 07:00 under "Night wait". It is skipped.
- He also expects Presence to hold reminders for an away person. It does not.
- Either the rules change these stages (engine cost and a CHANGELOG line), or the three sentences are not the whole truth.

### Worth stealing
"Not for severities" next to "Not for tags", and the post-upgrade check list with the two buttons "Keep as before" and "Let it act". These are plain words, and they turn a migration oddity into a decision.

## Design C: clean slate (plans and house rules)

### Failure 1: plans add up, so two plans double the noise (scenario 5, scenario 11, Q1)
- Conversion turns each 1.0 Reminder into its own one-step plan. In mode "all", two overlapping reminders become two plans with two rhythms.
- C answers scenario 5 with "one step, not two policies". But Ben, writing the reference case as the scenario states it (two reminders), gets both rhythms.
- When X turns on, he gets repeats every 15 minutes and every hour, not one 15-minute rhythm. C's own scenario 12 sentence confirms it: "they get both repeat rhythms".
- A leak warning that fits both "Leaks" and the converted "Warning reminder" gets two first pushes and two repeat series. C names this as its biggest risk and leaves the user to find it with "Try a message".

### Failure 2: two ways through the house rules, one of them not shown (Q3, S1, Chris's fear)
- C keeps "Critical messages pass" on every house rule (D-211, on by default) and adds a per-step "Passes" mark.
- "Can wake people" lists only steps with a "Passes quiet times" mark. Anna creates a second quiet-times rule and unticks "Critical messages pass" because she wants quiet weekends.
- From then on every critical message is quieted at weekends. No line in "Can wake people" changes, because no step changed.
- Q3 ("where is strength set, visible on the page") has two answers in C, and the page shows one of them.

### Failure 3: the safety-net fallback wakes the house for everyday messages (scenario 8 against S1)
- C's scenario 8 has Chris tick both "Passes presence rules" and "Passes quiet times" on the plan "Safety net" for all messages.
- At 03:00 an info message "Washing done" whose audience was empty, for example a presence-based audience with nobody home, triggers the fallback. It is then spoken loudly on the Household speakers, into an empty house.
- The mark sits on the step, not on the message, so it cannot be "for leaks only" without a second plan.
- Related: rule 3 says timed steps count from when the message "first went out". For a digest message the first going out is the summary at 20:00. C says "Plans that fit a digest message do nothing until the summary went out", which suggests an "At once" step fires per digest message at 20:00, after the summary. That contradicts 1.0, where a summarized message starts no Deliver and no timers. The exception lives outside the three rules.

### Worth stealing
"Restore 1.0.0 links", which recomputes the conversion links from the kept `policy_order`. A user who removes a conversion link by mistake has a way back that does not need a backup.

## Design D: message types

### Failure 1: migration by cells makes the first page after the upgrade unreadable (scenario 11, D-213, Q1)
- Correction to my first draft: D's scenario 11 is right for the common case. The introduction creates its policies in its own order (`welcome.py`, `ITEMS_BY_MODE`), and an Away policy added later is appended last. In mode "first" it then acts on nothing. Only setups that already had policies when the order was first stored (`initial_order()`, `__init__.py`) put Away before Reminder and Deliver.
- The failure is the cell algorithm itself. It makes one type per distinct set of policies over every severity × every tag any policy mentions.
- In mode "all", cells become joined names ("Night quiet + Away"). Ben has 30 tagged automations and several tag-specific policies, so the type list grows with every tag × severity combination.
- Each of these types repeats the quiet, fallback and repeat settings it inherited, so a later change to "the fallback" has to be made once per type.
- The "one look" promise breaks on the first page Ben sees after the upgrade.

### Failure 2: one claim moved by one Save silences an alarm (Chris's fear, scenario 12, Q4)
- "Saving a claim that another type holds moves it."
- Anna creates a type "Kitchen" and, picking from the tag list, claims `leak` because the kitchen sink sensor sends it. The form warns in one sentence and she saves.
- Leaks now follow "Kitchen": no push to the Admins, "Send quietly" at night. Chris's alarm is silent and nothing on Alarm's card says that it lost a tag.
- D's mitigation only covers the critical severity default, not tag claims.

### Failure 3: "quiet nights" has to be set once per type (Q4, S1, S2)
- D's only shared object is the quiet-time window; the meaning is per type. Anna's wish "quiet nights for small things" is spread over Everyday, Doorbell, Digest, Shopping and every type she adds later.
- When she adds "Shopping", its "During quiet times" has a default. If that default is "Send as usual", the new type rings at night and S1's "nights stay quiet for everything else" fails. If the default is quiet, Chris's new "Water" type stays silent at night until he notices.
- Q4 asks for one place per wish; D gives one place per type.
- Watch rules make it worse: every rule message has tag `rule` and cannot name a type (D-100). All warning rules therefore share one type, and D needs a change to a frozen form (parity, rule 9).

### Worth stealing
The before-Save warning when a change takes protection away (D: a critical default type stops sending as usual). In design B this applies to any edit, switch-off or deletion that narrows a "Gets through" goal.
