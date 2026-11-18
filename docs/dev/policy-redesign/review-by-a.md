# Review by Designer A (round two)

Reviews of designs B, C and D, v1. Facts checked against the fact sheet and the 1.0.0 code in `custom_components/heads_up/hub/`. Two code facts several designs get wrong:

- There is no `error` severity. `SEVERITIES` is success, info, warning, critical (`const.py`). My own v1 used `error`; v2 corrects it.
- The order is stored at the first load (`__init__.py`, `initial_order()`), and the introduction creates its policies in the order Critical delivery, Warning reminder, Evening summary, Night quiet (`welcome.py`, `ITEMS_BY_MODE["first"]`). A policy added later is appended at the end (`PolicyBook.ordered`). So in scenario 11 the Away policy sits last, and with the four built-in severities covered by the starter list it acts on nothing in 1.0.0. Warning reminder and Critical delivery do act.

## Design B: goals

### Three most serious failures

1. Scenario 11 is computed on the wrong order. B assumes "stored order Summarize, Quiet hours, Away, Reminder, Deliver" and concludes that Warning reminder and Critical delivery never act and get "steps aside for Presence". With the order a real 1.0.0 setup stores (above), the opposite is true: Away never acts. Ben upgrades, sees "Critical delivery: never acts" on the page, believes his critical pushes were broken, and presses the offer that changes behaviour. The migration rule itself ("steps aside for every earlier overlapping policy") is sound; the worked example and the notes it promises are not.
2. "Gets through" bundles a permission with a send and ties both to people, so scenario 8 cannot be configured cleanly. To have the household fallback spoken at night for warnings, Chris must write a Gets through goal that names Household speakers. That goal passes every calm goal for those speakers, Presence included, so the next warning tagged `doorbell` or any other warning sent to the speakers is spoken into an empty house. The step where it goes wrong: choosing "who" on the Gets through goal, where the form says nothing about Presence.
3. Strength is back in three places, one of which is an order in disguise. "Steps aside for [goal]" sits in More options for any goal, not only for converted ones. Ben, who wanted "everything except digest", will reach for it because it is the only cross-goal tool, and Q3 ("which of these two wins") again needs reading links between cards. Rule 1 also carries two exceptions ("except one that steps aside", "unless a repeat goal has its own rhythm"), which the brief asked to avoid.

Also weak: sentence templates with tappable blanks in four languages at 380 px (B names it as the biggest risk; nothing in the mockup shows a German or French sentence fitting). And "one goal holds any number of windows" changes the stored shape of `quiet_hours` without saying what a downgrade reads.

### Worth stealing

"Reached someone" is defined: the banner counts only when it is the message's only channel. Without that, every message "reaches someone" at once through its banner and the clock rule means nothing. I take this into A v2.

## Design C: clean slate (plans and house rules)

### Three most serious failures

1. Scenario 8 as configured breaks scenario 1. C's "Safety net" plan applies to all messages and its fallback step passes quiet times and presence rules. When the Admins' phones fail to deliver an info message at 03:00 (sending failed counts as unreached), Kitchen speaker speaks it at 03:00, and into an empty house if nobody is home. S1's "an info message at 03:00 makes no sound" fails, and the "Can wake people" block lists the step without saying it fires for info. The step where Chris goes wrong: ticking both Passes chips on a step whose Which messages is "all".
2. Plans add up, so scenario 5 as written in the brief ("two reminders") gives two rhythms. C answers scenario 5 by changing the question to one step with "Faster while". Ben, who already has a Reminder "Hourly" and adds a plan "Urgent" for X, gets both: every 15 minutes and every hour, with two counters. C's own scenario 12 sentence admits it ("they get both repeat rhythms"). Pain point 4 is avoided only for users who find the Faster while field.
3. Pain point 6 stays. "Critical messages pass" remains on every house rule, on by default, while C states "severity has no hidden power". A new house rule starts letting critical through, the Passes marks are per step and per kind of rule, and Chris must look in two places (Which messages on each house rule, Passes on each step) to answer "what can wake me". Also, the call's own first delivery is not a step, so for anything but critical it can never pass a hold: the leak's banner and the push the automation asked for stay quiet unless a plan repeats them.

Also: a plan has one switch (D-198), so Ben cannot turn off only the repeat step of a converted plan from YAML once steps are merged, and downgrade is lost after the first multi-step plan.

### Worth stealing

The "Converted from 1.0.0" card with "Restore 1.0.0 links", recomputed from the kept `policy_order`. A way back that needs no backup. A v2 offers the same for its converted Not for lines.

## Design D: message types

### Three most serious failures

1. Parity fails for watch rules (rule 9, scenario 1 by rule). Every watch-rule message has tag `rule`, and watch rules are frozen and cannot name a type. A leak watch rule at warning severity gets the warning default type, not Alarm. Chris's leak rule at 03:00 does whatever "Warning" does at night. D names this as a risk and asks for a maintainer decision; until then, rules are not as safe as automations, which is exactly S10's point.
2. Claims move silently between types, which is Chris's fear in a new place. "Saving a claim that another type holds moves it". Anna adds type "Loud doorbell" and claims tag `leak` by mistake (or any tag the Alarm type holds); after Save, leak messages lose Alarm's "Send as usual" at night. The form says it in a sentence, but the Alarm card does not warn, and nothing stops it. The step: Save on another type's form.
3. Shared behaviour must be copied, and "all that apply" setups explode. A household fallback or a night rule used by four types is set four times (scenario 8 in D needs the fallback in each type that should have it; an info type gets none). Migration of an `all` setup creates one type per distinct set of policies ("Night quiet + Away"), so six overlapping 1.0.0 policies can produce many joined names. Ben's "everything except digest" also needs the claim mechanism: he cannot say it on the night rule, only by building a Digest type.

Also: when a call updates an existing message's severity, D fixes the type at creation and does not say whether it changes, while 1.0.0 restarts timers on a severity change. The new `type` field in `heads_up.notify` is new API surface that Ben's thirty automations do not use.

### Worth stealing

The warning before Save when a change stops critical messages from waking people. A v2 adds it to the band: removing a severity or tag from Always gets through shows "This stops critical messages from waking people at night" before Save.
