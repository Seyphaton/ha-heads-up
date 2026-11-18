# Policy redesign: users and stories

Sample names only. Every design answers these stories and the twelve scenarios below.

## Scenario set
1. A water leak sent as a warning at 03:00: someone must act; nights stay quiet for everything else.
2. Info and success quiet from 22:00 to 07:00 on weekdays and 23:00 to 09:00 at weekends.
3. The doorbell is spoken only when someone is home; with guests (guest mode on) it is always spoken.
4. A critical message is pushed at once to the Admins and repeated every 10 minutes until acknowledged.
5. Two reminders: every 15 min only if X, otherwise every 1 h; X is false at creation and turns true after 15 minutes.
6. A shopping-list push is held until the person leaves home.
7. Messages tagged `digest` are summarized once at 20:00.
8. If nobody could be reached, the household speakers say it.
9. An escalation for a message that is still held (quiet hours) when its delay is over.
10. A watch-rule message (banner only) that is critical must reach phones.
11. A 1.0.0 setup with the starter list (Critical delivery, Warning reminder, Evening summary, Night quiet) and one Away policy converts with no change in behaviour.
12. A user adds a second policy of the same type that overlaps the first and must see, before saving, what will happen.

## Personas
- Anna, household member, UI first. Opens the Heads Up panel a few times a year, never writes YAML, reads German. Wants quiet evenings and to hear the doorbell. Judges the page by whether one look tells her what will happen.
- Ben, power user. Thirty automations call `heads_up.notify` with tags; he copies policy switch entity IDs into YAML. Wants exact, predictable behaviour and a way to say "everything except digest".
- Chris, the person who set it up and gets the 3 a.m. alarms. Admin, owns the phones in the Admins audience. Wants water and smoke to wake them every time, and nothing else at night. Fears that a change made by someone else silences an alarm.

## Questions the Policies page must answer without docs
- Q1 "What happens to this message?" For a severity, a tag and a time, which policies act and in what order.
- Q2 "Why did my phone not ring?" Which policy held, quieted or dropped the delivery, and which policy would have let it through.
- Q3 "Which of these two policies wins?" Where strength is set, visible on the page, not in the order of a list that also means something else.
- Q4 "What do I change to get X?" One place to edit per wish.

## Stories

S1 (scenario 1). As Chris, I want a water leak sent as a warning at 03:00 to reach someone who acts, so that the house is not flooded while nights stay quiet for everything else.
- The leak reaches the Admins' phones with sound within one minute, without being marked critical.
- An info message at 03:00 makes no sound.
- The page shows, without opening a form, that leak messages may wake people at night.

S2 (scenario 2). As Anna, I want info and success messages quiet from 22:00 to 07:00 on weekdays and from 23:00 to 09:00 at weekends, so that I can sleep in.
- Two time windows can exist side by side and both work.
- A warning is not affected.
- The editor says in a sentence what the second window adds and that it does not overlap the first.

S3 (scenario 3). As Anna, I want the doorbell spoken only when someone is home, and always when guests are here (guest mode on), so that nobody hears a doorbell in an empty house and guests are not missed.
- With nobody home and guest mode off, nothing is spoken; push still works.
- With guest mode on, it is spoken whoever is home.
- Setting this up does not switch off night quiet for other messages.

S4 (scenario 4). As Chris, I want a critical message pushed at once to the Admins and repeated every 10 minutes until acknowledged, so that I cannot sleep through it.
- The first push and the repeats both happen; neither blocks the other.
- An acknowledgement on any device stops the repeats.

S5 (scenario 5). As Ben, I want a reminder every 15 minutes while X is on and every hour otherwise, so that urgent states nag more.
- When X turns on 15 minutes after the message appeared, the next reminder follows the 15-minute rhythm; the page says when.
- The reminder count does not reset when the rhythm changes, or the page says that it does.

S6 (scenario 6). As Anna, I want the shopping list pushed when I leave home, so that I see it on the way.
- The push is held while I am home and sent when I leave (after the presence delay).
- Other people's messages are not held by this.

S7 (scenario 7). As Ben, I want messages tagged `digest` summarized once at 20:00, so that they do not interrupt the day.
- Digest messages are not also quieted or held by another policy in a way that changes the summary.
- Other info messages are not summarized.

S8 (scenario 8). As Chris, I want the household speakers to say a message if nobody could be reached, so that it is not lost.
- The fallback is not held by a presence or quiet rule meant for ordinary messages, or the page shows that it is.

S9 (scenario 9). As Chris, I want to know what an escalation does when the message is still held by quiet hours when its delay is over, so that I am not woken for something nobody was meant to see yet, or I am, by my choice.
- The behaviour is one plain rule visible on the page.

S10 (scenario 10). As Chris, I want a critical watch-rule message (banner only) to reach phones, so that rules are as safe as automations.
- The same policy that serves `notify` serves the rule; no YAML.

S11 (scenario 11). As Ben, I want my 1.0.0 setup (Critical delivery, Warning reminder, Evening summary, Night quiet, one Away policy) to behave the same after the upgrade, so that nothing changes without my knowing.
- Every message gets the same deliveries as before; anything that changes is listed in the CHANGELOG with the way back.

S12 (scenario 12). As Anna, I want to see, before saving a second policy of a type that overlaps the first, what will happen, so that I do not break something.
- The form shows which messages each policy will act on and which one wins where they overlap, in a sentence, before Save.
