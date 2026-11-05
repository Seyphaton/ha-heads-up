// Heads Up panel: FAQ and examples page (H9f). Loaded by the shell when the page is opened.
// The examples are plain calls: `make docs-check` validates every `yaml:` block below against the
// real action schemas, so an example cannot drift from the actions.

export const EXAMPLES = [
  {
    id: "e1",
    yaml: `action: heads_up.create_banner
data:
  message: Window open`,
  },
  {
    id: "e2",
    yaml: `action: heads_up.notify
data:
  message: Water leak
  severity: critical
  tag: water
  channels: [banner, push]
  audience: Everyone`,
  },
  {
    id: "e3",
    yaml: `action: heads_up.notify
data:
  message: Water leak
  tts_message: Water in the utility room
  severity: critical
  channels: [push, speak, persistent]
  audience: Admins
  speakers: [Ground floor (group)]`,
  },
  {
    id: "e4",
    yaml: `action: heads_up.notify
data:
  message: Doorbell
  tts_message: Someone is at the door
  channels: [speak]
  speakers: [media_player.kitchen]
  policy: none`,
  },
  {
    id: "e5",
    yaml: `action: heads_up.push
data:
  message: Window left open
  audience: Last to leave`,
  },
  {
    id: "e6",
    yaml: `action: heads_up.notify
data:
  message: Washer is done
  severity: info
  channels: [push]
  recipients: [person.anna]`,
  },
];

export const CARD_EXAMPLES = [
  {
    id: "c1",
    yaml: `type: custom:heads-up-card`,
  },
  {
    id: "c2",
    yaml: `type: custom:heads-up-card
title: Notices
layout: compact
collapsed_items: 3
show_time: true`,
  },
  {
    id: "c3",
    yaml: `type: custom:heads-up-card
severity: [critical, warning]
clear_all: true
swipe_to_dismiss: true`,
  },
  {
    id: "c4",
    yaml: `type: custom:heads-up-card
tag: kitchen
sort: time
empty_message: All clear in the kitchen`,
  },
  {
    id: "c5",
    yaml: `type: custom:heads-up-card
show_all: true
show_snoozed: true
show_empty: true`,
  },
  {
    id: "c6",
    yaml: `type: custom:heads-up-card
colorize: icon
show_severity: true
colors:
  critical: "#c62828"`,
  },
];

export const ISSUES_URL = "https://github.com/Seyphaton/ha-heads-up/issues";

export const QUESTION_IDS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22", "q23", "q24", "q25", "q26", "q27"];

export const STRINGS = {
  en: {
    titles: {"faq": "FAQ", "examples": "Notify examples", "card": "Card examples"},
    intros: {"faq": "Answers to common questions.", "examples": "Calls of the action heads_up.notify, from the simplest to the most detailed. Admins is a built-in audience. Ground floor (group), person.anna and media_player.kitchen are samples: replace them with your own speaker groups, persons and speakers.", "card": "Settings for the dashboard card custom:heads-up-card. Paste one into the card's YAML editor, or set the same options in its visual editor."},
    copy: "Copy",
    copied: "Copied.",
    issues_lead: "Found a problem or missing something?",
    issues_link: "Open an issue on GitHub",
    copy_failed: "Copying is not possible here. Select the text.",
    ex: {
      e1: { title: "1. Banner only", note: "No hub object is needed. Nothing else is sent." },
      e2: { title: "2. Banner and push, policies add the rest", note: "Policies that match the severity and the tag apply as well, for example an escalation to Admins after 5 minutes." },
      e3: { title: "3. Push, speech and persistent notification together", note: "Each channel has its own target. The persistent notification needs none." },
      e4: { title: "4. One call, no policy", note: "Speech on one speaker, ignoring every policy." },
      e5: { title: "5. Shortcut for one channel", note: "The push shortcut with a presence audience: the person whose departure emptied the house." },
      e6: { title: "6. To one person", note: "A direct recipient instead of an audience." },
    },
    card_ex: {
      c1: { title: "1. The default card", note: "Shows every banner meant for the viewer, critical first." },
      c2: { title: "2. A compact list", note: "One line per banner: the first three are visible, a button shows the rest, and each banner says how long ago it was created." },
      c3: { title: "3. Only what needs action", note: "Critical and warning banners only, with a button that clears them all and swipe to dismiss on a touch screen." },
      c4: { title: "4. One room", note: "Only banners with the tag kitchen, newest first, and a short text when there are none. Send the tag with tag: kitchen in the call." },
      c5: { title: "5. A wall tablet for the administrator", note: "Also shows banners meant for other people (administrators only), lists snoozed banners and stays visible when empty." },
      c6: { title: "6. Your own colours", note: "Only the icon and the label take the severity colour, the label is shown as text, and critical uses a fixed red." },
    },
    q: {
      q1: { q: "What does Heads Up do?", a: "Your automation makes one call, heads_up.notify. Heads Up decides where the message shows up (channels), who gets it (audiences and recipients) and when it is delivered or escalated (policies). You set this up once in this panel, not in every automation." },
      q2: { q: "How is this different from what Home Assistant already has?", a: "Each Home Assistant notify service sends to one place, and each automation names its own devices. Heads Up adds:\n- One call that reaches several channels.\n- Audiences such as At home or Last to leave, worked out when the message is sent.\n- Policies (escalate, remind, keep quiet at night, summarize), set once for all automations.\n- The banner, a new channel: a card on your dashboards that stays until it is dismissed, its condition ends or it times out.\n- One lifecycle: a message ends everywhere at once, pushes included, and every delivery is traced." },
      q3: { q: "What are the key things to set up?", a: "Start with these:\n- Banners: add the card to a dashboard.\n- Push: make sure each person has the Companion app. Heads Up finds the devices through the person's trackers.\n- Speech: name your speakers, alone or in a speaker group.\n- Mail: choose a notify service on the Channels page (see the mail question).\n- Policies: switch on the ones you want in the introduction.\n\nThe Overview lists problems it can detect, such as a person without a usable device, under Needs attention." },
      q4: { q: "Can I show a banner without writing an automation?", a: "Yes, with a watch rule. A rule watches an entity or a template and shows a banner while the condition is true.\n- When the condition stops being true, Heads Up removes the banner.\n- Rules live in Heads Up, not in a dashboard, so several cards with different filters share them.\n- Add one on the Watch rules page.\n\nAn automation with heads_up.create_banner, or heads_up.notify with the banner channel, and a condition does the same. Policies apply too: with the tag rule, a Deliver policy can also push a critical rule message at once." },
      q5: { q: "Can I test notifications?", a: "Yes, on Test send. Fill in the message, the channels and who gets it. The table shows who would be reached and why anyone would be skipped, held or dropped. Copy call gives the YAML for your automation. Send test sends one real message that ends by itself after 10 minutes." },
      q6: { q: "What is a channel?", a: "A channel is where a message shows up. There are six:\n- Banner: a card on your dashboards.\n- Push: the Companion app on phones and tablets.\n- Popup: a message on top of any open dashboard page.\n- Speech: spoken on speakers and Assist satellites.\n- Mail: through a notify service you choose.\n- Persistent Notification: the bell of Home Assistant.\n\nA call lists the channels it wants, and a policy can add more later, for example on escalation." },
      q7: { q: "How do I set up mail (SMTP)?", a: "Mail does not work out of the box because Heads Up does not send e-mail itself. It hands each mail to a Home Assistant notify service, and that service needs a mail server.\n\nTo set it up:\n- Add the SMTP integration under Settings > Devices & services. It asks for the server, port, connection security, sender, user name and password, and creates a notify service named after the entry.\n- Open Configuration > Channels > Mail and choose that notify service. Without one, mail fails with no_mail_service.\n- Optional: enter a Global address.\n- Open Recipients. For each person who should get mail, switch Mail on and enter the address.\n\nMail stays off for everyone until the last step, so an audience such as Everyone reaches only the people who opted in. Try it with Test send and the Mail channel.\n\nHeads Up only knows whether the notify service returned an error, not whether the mail arrived. If a send fails, check the log lines of the SMTP integration. After a mail went through it, the SMTP integration raises a repair that this notify service is deprecated and due to be removed in Home Assistant 2027.3." },
      q8: { q: "What is an audience, and how does it differ from a recipient?", a: "An audience is a named group of people that can change over time: Everyone, Admins, At home, Last to leave, or your own. A recipient is one fixed target: a person, a phone or a speaker. A channel takes an audience or recipients, never both." },
      q9: { q: "What is a policy?", a: "A policy changes how messages behave without changing the automation that sends them. There are seven types:\n- Escalation: tell more people or channels if nobody acknowledges.\n- Reminder: repeat the message.\n- Quiet hours: send quietly, hold or drop messages at night.\n- Away: send when the person arrives.\n- Fallback: send to someone else when nobody was reached.\n- Deliver: add channels at once, for example a push for critical messages.\n- Summarize: hold messages and send one summary.\n\nThe introduction offers four defaults, and the Policies page lists every policy you have." },
      q10: { q: "What does severity do?", a: "A message has one of four severities: success, info, warning (the default) and critical.\n- Banner: sets the colour, the icon and the order, critical first.\n- Push: sets the level. Success and info are passive, warning is normal, critical is time sensitive.\n- Popup: the style is set per severity too.\n- Policies: can match on it, for example an escalation for critical only." },
      q11: { q: "What are tags for?", a: "A tag is a label you give a message, for example laundry or water. Policies can apply to chosen tags only, a card can show only banners with one tag, and heads_up.clear_notifications can remove every message with a tag. Messages from watch rules carry the tag rule." },
      q12: { q: "Does it work with Android and iPhone?", a: "Push goes through the Home Assistant Companion app, which exists for both.\n- The severity sets the level.\n- Critical is an alarm on both. On an iPhone it is the critical alert: it needs the app's permission and plays a sound in silent mode. On Android it uses the alarm channel, which also sounds in vibrate and silent mode. Do Not Disturb is overridden on Android only if you allow it for that channel in the system settings.\n- Android shows up to 3 buttons on a push and iOS up to 10. Android keeps Acknowledge and Dismiss first.\n\nThis has not been tried on real phones yet; the tests use a stand-in for the app." },
      q13: { q: "What are escalations and reminders?", a: "Both start when nobody acknowledges a message.\n- An escalation waits a set time (5 minutes by default) and then delivers the message on other channels or to other people.\n- A reminder repeats the message every N minutes (30 by default), at most 3 times.\n\nAn acknowledgement stops both. Under the setting that every policy that applies runs, the introduction's Critical messages item creates a push at once, a reminder every 10 minutes and, if you choose speakers, speech after 10 minutes. By default only the first policy that applies runs, so critical messages get the push at once only." },
      q14: { q: "How do I apply policies?", a: "There are two ways.\n- Automatic: every policy lists the severities and tags it applies to, and an empty list matches everything. Each message that matches uses the policy, with no change to the automation.\n- Manual: a policy set to Manually never attaches by itself. Only a call or a watch rule that names it in its policy field gets it. A named policy is the only one used for that call, and none uses no policy.\n\nWhen several automatic policies match, the setting How policies interact on the Policies page decides: by default only the first one in the list runs, and the order is set by dragging. The other setting runs every matching policy.\n\nA message without a tag matches only policies with no tags. A disabled policy is never used." },
      q15: { q: "What does acknowledging do, and how is it different from dismissing?", a: "Acknowledging says that someone has seen the message. It stops every escalation and reminder of that message for everyone, and the banner stays. Dismissing closes the message for the person who dismissed it. An escalation policy can count a dismissal as an acknowledgement." },
      q16: { q: "How do I dismiss a message for everyone, on all channels?", a: "There are three ways.\n- By hand: call heads_up.clear_notifications with an id, a tag, a severity or a channel. It removes the matching messages from every channel; all: true removes every message.\n- By condition: give the message a condition. In mode once it ends when the condition turns false.\n- By viewer: set the dismiss scope (dismiss_scope) to global, on the message, on a watch rule or as the default under Settings > Messages. When anyone closes it, it ends for everyone and the pushes are taken back. With the scope user, closing hides it only for that person and removes only their push.\n\nA timeout also ends a message everywhere." },
      q17: { q: "Why did I not get a notification?", a: "- Test send shows who would be notified for a call and why someone is skipped, held or dropped.\n- The Message Log shows what happened to a real message: each delivery with its result and reason, for example quiet hours, no usable device or rate limited.\n- A failed send in the last 24 hours also appears under Needs attention." },
      q18: { q: "How do I keep messages quiet at night?", a: "Add a quiet hours policy. During the window it can send quietly, hold the messages until the end or drop them. Critical messages pass by default. The Quiet hours item of the introduction creates one from 22:00 to 07:00 that sends quietly." },
      q19: { q: "What if someone is not home?", a: "An away policy sends the message when the person arrives, as long as it is still there. A fallback policy sends it to someone else when the first delivery reached nobody." },
      q20: { q: "Can I get a summary instead of many messages?", a: "Yes. A summarize policy holds the matching messages and sends one summary every N minutes or at a fixed time, with a count and the titles. While a message is held nothing is sent for it on any channel, the dashboard banner included. Critical messages are held only if you include them." },
      q21: { q: "Can one call use several channels?", a: "Yes. Name the channels and give each its own target under to, as in example 3 of the Notify examples. The persistent notification needs no target." },
      q22: { q: "Why does speech take no audience?", a: "An audience is a set of people, and speech goes to a speaker in a place. The hub does not know which speaker a person is near, so you name speakers, speaker groups or areas." },
      q23: { q: "Do critical messages get special treatment?", a: "Yes, in four places.\n- Quiet hours let them pass unless you switch that off.\n- Summarize does not hold them unless you include them.\n- Rate limits never hold them back.\n- Presence audiences include a person whose presence is unknown.\n\nAway has no exception, so limit its severities if critical messages must go out at once." },
      q24: { q: "What stops a flood of pushes?", a: "Three limits:\n- 5 pushes per device per minute.\n- 60 pushes in total per minute.\n- No repeat of an identical update within 30 seconds.\n\nA skipped push shows in the trace as rate_limited or duplicate. All three are settings, and critical messages are never held back." },
      q25: { q: "What happens when I replace a phone?", a: "Edit the person's recipient profile once. Audiences and policies stay the same, and no automation needs a change." },
      q26: { q: "Why does a new policy not change a message that is already showing?", a: "A policy is looked up when a message appears. A policy you add later starts when the message is next updated. A summarize policy does not hold messages that are already there." },
      q27: { q: "What happens after a restart?", a: "- Pending escalations keep their due time. A step that came due during the restart runs once if the message is still active and not acknowledged.\n- Messages held for quiet hours, away or a summary stay held.\n- Pushes of messages that no longer exist are removed.\n- The record of recent messages and last actions starts empty." },
    },
  },
  de: {
    titles: {"faq": "FAQ", "examples": "Notify-Beispiele", "card": "Karten-Beispiele"},
    intros: {"faq": "Antworten auf häufige Fragen.", "examples": "Aufrufe der Aktion heads_up.notify, vom einfachsten bis zum ausführlichsten. Admins ist eine eingebaute Zielgruppe. Ground floor (group), person.anna und media_player.kitchen sind Beispiele: Ersetze sie durch deine eigenen Lautsprechergruppen, Personen und Lautsprecher.", "card": "Einstellungen für die Dashboard-Karte custom:heads-up-card. Füge eine in den YAML-Editor der Karte ein oder setze dieselben Optionen im visuellen Editor."},
    copy: "Kopieren",
    copied: "Kopiert.",
    issues_lead: "Ein Problem gefunden oder etwas vermisst?",
    issues_link: "Ticket auf GitHub öffnen",
    copy_failed: "Kopieren ist hier nicht möglich. Markiere den Text.",
    ex: {
      e1: { title: "1. Nur Banner", note: "Es braucht kein Hub-Objekt. Es wird nichts anderes gesendet." },
      e2: { title: "2. Banner und Push, Richtlinien ergänzen den Rest", note: "Richtlinien, die zu Schweregrad und Tag passen, gelten ebenfalls, zum Beispiel eine Eskalation an Admins nach 5 Minuten." },
      e3: { title: "3. Push, Sprache und dauerhafte Benachrichtigung zusammen", note: "Jeder Kanal hat sein eigenes Ziel. Die dauerhafte Benachrichtigung braucht keines." },
      e4: { title: "4. Ein Aufruf ohne Richtlinie", note: "Sprache auf einem Lautsprecher, alle Richtlinien werden ignoriert." },
      e5: { title: "5. Kurzform für einen Kanal", note: "Die Push-Kurzform mit einer Anwesenheits-Zielgruppe: die Person, deren Weggang das Haus geleert hat." },
      e6: { title: "6. An eine Person", note: "Ein direkter Empfänger statt einer Zielgruppe." },
    },
    card_ex: {
      c1: { title: "1. Die Standardkarte", note: "Zeigt jedes Banner, das für den Betrachter bestimmt ist, kritische zuerst." },
      c2: { title: "2. Eine kompakte Liste", note: "Eine Zeile pro Banner: Die ersten drei sind sichtbar, eine Schaltfläche zeigt den Rest, und jedes Banner sagt, wie lange es her ist." },
      c3: { title: "3. Nur was Handeln braucht", note: "Nur kritische und Warn-Banner, mit einer Schaltfläche, die alle entfernt, und Wischen zum Ausblenden auf dem Touchscreen." },
      c4: { title: "4. Ein Raum", note: "Nur Banner mit dem Tag kitchen, neueste zuerst, und ein kurzer Text, wenn es keine gibt. Den Tag sendest du im Aufruf mit tag: kitchen." },
      c5: { title: "5. Ein Wandtablet für den Administrator", note: "Zeigt auch Banner für andere Personen (nur Administratoren), listet zurückgestellte Banner und bleibt sichtbar, wenn sie leer ist." },
      c6: { title: "6. Eigene Farben", note: "Nur Symbol und Beschriftung nehmen die Farbe des Schweregrads an, die Beschriftung wird als Text gezeigt, und kritisch nutzt ein festes Rot." },
    },
    q: {
      q1: { q: "Was macht Heads Up?", a: "Deine Automatisierung macht einen Aufruf, heads_up.notify. Heads Up entscheidet, wo die Meldung erscheint (Kanäle), wer sie bekommt (Zielgruppen und Empfänger) und wann sie zugestellt oder eskaliert wird (Richtlinien). Das richtest du einmal in diesem Panel ein, nicht in jeder Automatisierung." },
      q2: { q: "Was ist anders als bei dem, was Home Assistant schon hat?", a: "Jeder Notify-Dienst von Home Assistant sendet an einen Ort, und jede Automatisierung nennt ihre eigenen Geräte. Heads Up fügt hinzu:\n- Ein Aufruf erreicht mehrere Kanäle.\n- Zielgruppen wie Zu Hause oder Zuletzt gegangen, die beim Senden ermittelt werden.\n- Richtlinien (eskalieren, erinnern, nachts leise, zusammenfassen), einmal für alle Automatisierungen festgelegt.\n- Das Banner, ein neuer Kanal: eine Karte auf deinen Dashboards, die bleibt, bis sie ausgeblendet wird, ihre Bedingung endet oder sie abläuft.\n- Einen gemeinsamen Ablauf: Eine Meldung endet überall gleichzeitig, Pushes eingeschlossen, und jede Zustellung wird protokolliert." },
      q3: { q: "Was muss ich zuerst einrichten?", a: "Das sind die Hauptsachen:\n- Banner: Füge die Karte einem Dashboard hinzu.\n- Push: Sorge dafür, dass jede Person die Companion-App hat. Heads Up findet die Geräte über die Tracker der Person.\n- Sprache: Nenne deine Lautsprecher, allein oder in einer Lautsprechergruppe.\n- Mail: Wähle auf der Seite Kanäle einen Notify-Dienst (siehe die Frage zu Mail).\n- Richtlinien: Schalte in der Einführung die gewünschten ein.\n\nDie Übersicht listet unter Braucht Aufmerksamkeit Probleme, die sie erkennt, etwa eine Person ohne nutzbares Gerät." },
      q4: { q: "Kann ich einen Banner ohne Automatisierung zeigen?", a: "Ja, mit einer Überwachungsregel. Eine Regel beobachtet eine Entität oder ein Template und zeigt ein Banner, solange die Bedingung wahr ist.\n- Gilt die Bedingung nicht mehr, entfernt Heads Up das Banner.\n- Regeln liegen in Heads Up, nicht in einem Dashboard, daher teilen sich mehrere Karten mit unterschiedlichen Filtern dieselben Regeln.\n- Lege eine auf der Seite Überwachungsregeln an.\n\nEine Automatisierung mit heads_up.create_banner oder heads_up.notify mit dem Kanal Banner und einer Bedingung tut dasselbe. Richtlinien gelten auch: Mit dem Tag rule kann eine Zustellen-Richtlinie eine kritische Regelmeldung sofort auch pushen." },
      q5: { q: "Kann ich Benachrichtigungen testen?", a: "Ja, unter Testsenden. Gib Meldung, Kanäle und Empfänger an. Die Tabelle zeigt, wer erreicht würde und warum jemand übersprungen, zurückgehalten oder verworfen würde. Aufruf kopieren liefert das YAML für deine Automatisierung. Test senden schickt eine echte Meldung, die nach 10 Minuten von selbst endet." },
      q6: { q: "Was ist ein Kanal?", a: "Ein Kanal ist der Ort, an dem eine Meldung erscheint. Es gibt sechs:\n- Banner: eine Karte auf deinen Dashboards.\n- Push: die Companion-App auf Telefonen und Tablets.\n- Popup: eine Meldung über jeder geöffneten Dashboard-Seite.\n- Sprache: gesprochen auf Lautsprechern und Assist-Satelliten.\n- E-Mail: über einen Notify-Dienst deiner Wahl.\n- Persistent Notification: die Glocke von Home Assistant.\n\nEin Aufruf nennt die gewünschten Kanäle, und eine Richtlinie kann später weitere hinzufügen, etwa bei einer Eskalation." },
      q7: { q: "Wie richte ich E-Mail (SMTP) ein?", a: "E-Mail funktioniert nicht von selbst, weil Heads Up keine E-Mails selbst sendet. Es gibt jede Mail an einen Notify-Dienst von Home Assistant weiter, und dieser Dienst braucht einen Mailserver.\n\nSo richtest du es ein:\n- Füge die SMTP-Integration unter Einstellungen > Geräte & Dienste hinzu. Sie fragt nach Server, Port, Verbindungssicherheit, Absender, Benutzername und Passwort und legt einen Notify-Dienst an, der nach dem Eintrag benannt ist.\n- Öffne Konfiguration > Kanäle > E-Mail und wähle diesen Notify-Dienst. Ohne ihn schlägt E-Mail mit no_mail_service fehl.\n- Optional: Trage eine globale Adresse ein.\n- Öffne Empfänger. Schalte für jede Person, die E-Mails bekommen soll, E-Mail ein und trage die Adresse ein.\n\nBis zum letzten Schritt ist E-Mail für alle aus, daher erreicht eine Zielgruppe wie Alle nur die Personen, die zugestimmt haben. Probiere es mit Testsenden und dem Kanal E-Mail.\n\nHeads Up weiß nur, ob der Notify-Dienst einen Fehler zurückgab, nicht ob die Mail ankam. Schlägt ein Versand fehl, sieh in die Protokollzeilen der SMTP-Integration. Nach einer versendeten Mail meldet die SMTP-Integration eine Reparatur: Dieser Notify-Dienst ist veraltet und soll in Home Assistant 2027.3 entfernt werden." },
      q8: { q: "Was ist eine Zielgruppe, und wie unterscheidet sie sich von einem Empfänger?", a: "Eine Zielgruppe ist eine benannte Gruppe von Personen, die sich mit der Zeit ändern kann: Alle, Admins, Zu Hause, Zuletzt gegangen oder deine eigenen. Ein Empfänger ist ein festes Ziel: eine Person, ein Telefon oder ein Lautsprecher. Ein Kanal nimmt eine Zielgruppe oder Empfänger, nie beides." },
      q9: { q: "Was ist eine Richtlinie?", a: "Eine Richtlinie ändert, wie sich Meldungen verhalten, ohne die Automatisierung zu ändern, die sie sendet. Es gibt sieben Typen:\n- Eskalation: weitere Personen oder Kanäle benachrichtigen, wenn niemand bestätigt.\n- Erinnerung: die Meldung wiederholen.\n- Ruhezeit: nachts leise senden, zurückhalten oder verwerfen.\n- Abwesenheit: senden, wenn die Person ankommt.\n- Ersatz: an jemand anderen senden, wenn niemand erreicht wurde.\n- Zustellen: sofort Kanäle hinzufügen, etwa einen Push für kritische Meldungen.\n- Zusammenfassen: Meldungen zurückhalten und eine Zusammenfassung senden.\n\nDie Einführung bietet vier Standardrichtlinien an, die Seite Richtlinien listet alle, die du hast." },
      q10: { q: "Was bewirkt der Schweregrad?", a: "Eine Meldung hat einen von vier Schweregraden: success, info, warning (Standard) und critical.\n- Banner: bestimmt Farbe, Symbol und Reihenfolge, kritisch zuerst.\n- Push: bestimmt die Stufe. success und info sind passiv, warning normal, critical zeitkritisch.\n- Popup: Auch der Stil wird pro Schweregrad gewählt.\n- Richtlinien: können darauf passen, etwa eine Eskalation nur für kritische Meldungen." },
      q11: { q: "Wofür sind Tags da?", a: "Ein Tag ist ein Etikett, das du einer Meldung gibst, zum Beispiel laundry oder water. Richtlinien können nur für bestimmte Tags gelten, eine Karte kann nur Banner mit einem Tag zeigen, und heads_up.clear_notifications kann alle Meldungen mit einem Tag entfernen. Meldungen von Überwachungsregeln tragen den Tag rule." },
      q12: { q: "Funktioniert es mit Android und iPhone?", a: "Push läuft über die Home-Assistant-Companion-App, die es für beide gibt.\n- Der Schweregrad bestimmt die Stufe.\n- Kritisch ist auf beiden ein Alarm. Auf dem iPhone ist es die kritische Mitteilung: Sie braucht die Erlaubnis der App und spielt auch im Lautlosmodus einen Ton. Auf Android nutzt es den Alarmkanal, der auch im Vibrations- und Lautlosmodus ertönt. Nicht stören wird auf Android nur übergangen, wenn du es in den Systemeinstellungen für diesen Kanal erlaubst.\n- Android zeigt bis zu 3 Schaltflächen an einem Push, iOS bis zu 10. Android behält Bestätigen und Schließen zuerst.\n\nDas wurde noch nicht auf echten Telefonen ausprobiert; die Tests nutzen einen Ersatz für die App." },
      q13: { q: "Was sind Eskalationen und Erinnerungen?", a: "Beide beginnen, wenn niemand eine Meldung bestätigt.\n- Eine Eskalation wartet eine bestimmte Zeit (standardmäßig 5 Minuten) und stellt die Meldung dann auf anderen Kanälen oder an andere Personen zu.\n- Eine Erinnerung wiederholt die Meldung alle N Minuten (standardmäßig 30), höchstens 3 Mal.\n\nEine Bestätigung stoppt beides. Mit der Einstellung, dass jede passende Richtlinie läuft, legt der Punkt Kritische Meldungen in der Einführung einen sofortigen Push, eine Erinnerung alle 10 Minuten und, wenn du Lautsprecher wählst, Sprache nach 10 Minuten an. Standardmäßig läuft nur die erste passende Richtlinie, kritische Meldungen bekommen dann nur den sofortigen Push." },
      q14: { q: "Wie wende ich Richtlinien an?", a: "Es gibt zwei Wege.\n- Automatisch: Jede Richtlinie nennt die Schweregrade und Tags, für die sie gilt, eine leere Liste passt auf alles. Jede passende Meldung nutzt die Richtlinie, ohne dass die Automatisierung geändert wird.\n- Manuell: Eine Richtlinie auf Manuell gilt nie von selbst. Nur ein Aufruf oder eine Überwachungsregel, die sie im Feld policy nennt, bekommt sie. Eine genannte Richtlinie ist die einzige für diesen Aufruf, none nutzt keine.\n\nPassen mehrere automatische Richtlinien, entscheidet die Einstellung Wie Richtlinien zusammenwirken auf der Seite Richtlinien: Standardmäßig läuft nur die erste in der Liste, die Reihenfolge stellst du durch Ziehen ein. Die andere Einstellung lässt jede passende Richtlinie laufen.\n\nEine Meldung ohne Tag passt nur auf Richtlinien ohne Tags. Eine deaktivierte Richtlinie wird nie genutzt." },
      q15: { q: "Was bewirkt Bestätigen, und wie unterscheidet es sich vom Ausblenden?", a: "Bestätigen sagt, dass jemand die Meldung gesehen hat. Es stoppt alle Eskalationen und Erinnerungen dieser Meldung für alle, der Banner bleibt. Ausblenden schließt die Meldung für die Person, die sie ausblendet. Eine Eskalationsrichtlinie kann Ausblenden als Bestätigen zählen." },
      q16: { q: "Wie blende ich eine Meldung für alle auf allen Kanälen aus?", a: "Es gibt drei Wege.\n- Von Hand: Rufe heads_up.clear_notifications mit einer ID, einem Tag, einem Schweregrad oder einem Kanal auf. Das entfernt die passenden Meldungen von jedem Kanal; all: true entfernt jede Meldung.\n- Per Bedingung: Gib der Meldung eine Bedingung. Im Modus once endet sie, wenn die Bedingung falsch wird.\n- Per Betrachter: Setze den Bereich beim Schließen (dismiss_scope) auf global, an der Meldung, an einer Überwachungsregel oder als Standard unter Einstellungen > Meldungen. Blendet jemand sie aus, endet sie für alle und die Pushes werden zurückgenommen. Beim Bereich user verbirgt Schließen sie nur für diese Person und entfernt nur deren Push.\n\nAuch ein Timeout beendet eine Meldung überall." },
      q17: { q: "Warum habe ich keine Benachrichtigung bekommen?", a: "- Testsenden zeigt, wer für einen Aufruf benachrichtigt würde und warum jemand übersprungen, zurückgehalten oder verworfen wird.\n- Das Meldungsprotokoll zeigt, was mit einer echten Meldung geschah: jede Zustellung mit Ergebnis und Grund, zum Beispiel Ruhezeit, kein nutzbares Gerät oder Rate-Limit.\n- Ein fehlgeschlagener Versand der letzten 24 Stunden erscheint auch unter Braucht Aufmerksamkeit." },
      q18: { q: "Wie halte ich Meldungen nachts leise?", a: "Füge eine Ruhezeit-Richtlinie hinzu. Im Zeitfenster kann sie leise senden, Meldungen bis zum Ende zurückhalten oder verwerfen. Kritische Meldungen kommen standardmäßig durch. Der Punkt Ruhezeit in der Einführung legt eine von 22:00 bis 07:00 an, die leise sendet." },
      q19: { q: "Was, wenn jemand nicht zu Hause ist?", a: "Eine Abwesenheitsrichtlinie sendet die Meldung bei der Ankunft der Person, solange sie noch aktiv ist. Eine Ersatzrichtlinie sendet sie an jemand anderen, wenn die erste Zustellung niemanden erreicht hat." },
      q20: { q: "Kann ich eine Zusammenfassung statt vieler Meldungen bekommen?", a: "Ja. Eine Zusammenfassungsrichtlinie hält passende Meldungen zurück und sendet alle N Minuten oder zu einer festen Uhrzeit eine Zusammenfassung mit Anzahl und Titeln. Solange eine Meldung gehalten wird, wird für sie auf keinem Kanal etwas gesendet, auch nicht als Banner im Dashboard. Kritische Meldungen werden nur gehalten, wenn du sie einschließt." },
      q21: { q: "Kann ein Aufruf mehrere Kanäle nutzen?", a: "Ja. Nenne die Kanäle und gib jedem sein eigenes Ziel unter to, wie in Beispiel 3 der Notify-Beispiele. Die persistente Benachrichtigung braucht kein Ziel." },
      q22: { q: "Warum nimmt Sprache keine Zielgruppe?", a: "Eine Zielgruppe ist eine Menge von Personen, Sprache geht aber an einen Lautsprecher an einem Ort. Der Hub weiß nicht, bei welchem Lautsprecher eine Person ist, daher nennst du Lautsprecher, Lautsprechergruppen oder Bereiche." },
      q23: { q: "Werden kritische Meldungen besonders behandelt?", a: "Ja, an vier Stellen.\n- Ruhezeiten lassen sie durch, solange du das nicht abschaltest.\n- Zusammenfassen hält sie nicht zurück, außer du schließt sie ein.\n- Rate-Limits halten sie nie zurück.\n- Anwesenheits-Zielgruppen schließen eine Person mit unbekannter Anwesenheit ein.\n\nAbwesenheit hat keine Ausnahme: Begrenze ihre Schweregrade, wenn kritische Meldungen sofort raus sollen." },
      q24: { q: "Was verhindert eine Flut von Pushes?", a: "Drei Grenzen:\n- 5 Pushes pro Gerät und Minute.\n- 60 Pushes insgesamt pro Minute.\n- Keine Wiederholung einer identischen Aktualisierung innerhalb von 30 Sekunden.\n\nEin übersprungener Push steht im Verlauf als rate_limited oder duplicate. Alle drei sind Einstellungen, und kritische Meldungen werden nie zurückgehalten." },
      q25: { q: "Was passiert, wenn ich ein Telefon ersetze?", a: "Bearbeite einmal das Empfängerprofil der Person. Zielgruppen und Richtlinien bleiben gleich, und keine Automatisierung muss angepasst werden." },
      q26: { q: "Warum ändert eine neue Richtlinie nichts an einer Meldung, die schon angezeigt wird?", a: "Eine Richtlinie wird nachgeschlagen, wenn eine Meldung erscheint. Eine später hinzugefügte Richtlinie beginnt, wenn die Meldung das nächste Mal aktualisiert wird. Eine Zusammenfassungsrichtlinie hält Meldungen, die schon da sind, nicht zurück." },
      q27: { q: "Was passiert nach einem Neustart?", a: "- Ausstehende Eskalationen behalten ihre Fälligkeit. Ein Schritt, der während des Neustarts fällig war, läuft einmal, wenn die Meldung noch aktiv und unbestätigt ist.\n- Meldungen, die für Ruhezeit, Abwesenheit oder eine Zusammenfassung gehalten werden, bleiben gehalten.\n- Pushes zu Meldungen, die es nicht mehr gibt, werden entfernt.\n- Die Liste der letzten Meldungen und Aktionen beginnt leer." },
    },
  },
  fr: {
    titles: {"faq": "FAQ", "examples": "Exemples notify", "card": "Exemples de carte"},
    intros: {"faq": "Réponses aux questions courantes.", "examples": "Appels de l'action heads_up.notify, du plus simple au plus détaillé. Admins est une audience intégrée. Ground floor (group), person.anna et media_player.kitchen sont des exemples : remplacez-les par vos propres groupes d'enceintes, personnes et haut-parleurs.", "card": "Réglages de la carte de tableau de bord custom:heads-up-card. Collez-en un dans l'éditeur YAML de la carte, ou réglez les mêmes options dans son éditeur visuel."},
    copy: "Copier",
    copied: "Copié.",
    issues_lead: "Un problème ou un manque ?",
    issues_link: "Ouvrir un ticket sur GitHub",
    copy_failed: "La copie n'est pas possible ici. Sélectionnez le texte.",
    ex: {
      e1: { title: "1. Bannière seule", note: "Aucun objet du hub n'est nécessaire. Rien d'autre n'est envoyé." },
      e2: { title: "2. Bannière et push, les politiques ajoutent le reste", note: "Les politiques qui correspondent à la gravité et à l'étiquette s'appliquent aussi, par exemple une escalade vers Admins après 5 minutes." },
      e3: { title: "3. Push, voix et notification persistante ensemble", note: "Chaque canal a sa propre cible. La notification persistante n'en a pas besoin." },
      e4: { title: "4. Un appel, sans politique", note: "Voix sur un haut-parleur, en ignorant toutes les politiques." },
      e5: { title: "5. Raccourci pour un canal", note: "Le raccourci push avec une audience de présence : la personne dont le départ a vidé la maison." },
      e6: { title: "6. À une personne", note: "Un destinataire direct au lieu d'une audience." },
    },
    card_ex: {
      c1: { title: "1. La carte par défaut", note: "Affiche toutes les bannières destinées au spectateur, les critiques d'abord." },
      c2: { title: "2. Une liste compacte", note: "Une ligne par bannière : les trois premières sont visibles, un bouton montre le reste, et chaque bannière indique depuis combien de temps elle existe." },
      c3: { title: "3. Seulement ce qui demande une action", note: "Bannières critiques et d'avertissement seulement, avec un bouton qui les efface toutes et le balayage pour masquer sur écran tactile." },
      c4: { title: "4. Une pièce", note: "Seulement les bannières avec l'étiquette kitchen, les plus récentes d'abord, et un court texte quand il n'y en a pas. Envoyez l'étiquette avec tag: kitchen dans l'appel." },
      c5: { title: "5. Une tablette murale pour l'administrateur", note: "Affiche aussi les bannières destinées à d'autres personnes (administrateurs seulement), liste les bannières reportées et reste visible quand elle est vide." },
      c6: { title: "6. Vos propres couleurs", note: "Seuls l'icône et le libellé prennent la couleur de la gravité, le libellé est affiché en texte, et critique utilise un rouge fixe." },
    },
    q: {
      q1: { q: "Que fait Heads Up ?", a: "Votre automatisation fait un seul appel, heads_up.notify. Heads Up décide où le message s'affiche (canaux), qui le reçoit (audiences et destinataires) et quand il est remis ou escaladé (politiques). Vous réglez cela une fois dans ce panneau, pas dans chaque automatisation." },
      q2: { q: "En quoi est-ce différent de ce que Home Assistant a déjà ?", a: "Chaque service notify de Home Assistant envoie vers un seul endroit, et chaque automatisation nomme ses propres appareils. Heads Up ajoute :\n- Un appel qui atteint plusieurs canaux.\n- Des audiences comme À la maison ou Dernier parti, calculées à l'envoi.\n- Des politiques (escalader, rappeler, silence la nuit, résumer), réglées une fois pour toutes les automatisations.\n- La bannière, un nouveau canal : une carte sur vos tableaux de bord qui reste jusqu'à ce qu'elle soit masquée, que sa condition prenne fin ou qu'elle expire.\n- Un seul cycle de vie : un message se termine partout à la fois, push compris, et chaque remise est tracée." },
      q3: { q: "Que dois-je régler d'abord ?", a: "Voici l'essentiel :\n- Bannières : ajoutez la carte à un tableau de bord.\n- Push : vérifiez que chaque personne a l'application Companion. Heads Up trouve ses appareils par les suivis de la personne.\n- Voix : nommez vos haut-parleurs, seuls ou en groupe.\n- Mail : choisissez un service notify sur la page Canaux (voir la question sur le mail).\n- Politiques : activez celles que vous voulez dans l'introduction.\n\nLa vue d'ensemble liste sous À surveiller les problèmes qu'elle détecte, par exemple une personne sans appareil utilisable." },
      q4: { q: "Puis-je afficher une bannière sans écrire d'automatisation ?", a: "Oui, avec une règle de surveillance. Une règle observe une entité ou un template et affiche une bannière tant que la condition est vraie.\n- Quand la condition n'est plus vraie, Heads Up retire la bannière.\n- Les règles vivent dans Heads Up, pas dans un tableau de bord : plusieurs cartes avec des filtres différents les partagent.\n- Ajoutez-en une sur la page Règles de surveillance.\n\nUne automatisation avec heads_up.create_banner, ou heads_up.notify avec le canal bannière, et une condition fait la même chose. Les politiques s'appliquent aussi : avec l'étiquette rule, une politique de remise peut aussi envoyer tout de suite un push pour un message critique de règle." },
      q5: { q: "Puis-je tester les notifications ?", a: "Oui, sur Envoi de test. Indiquez le message, les canaux et les destinataires. Le tableau montre qui serait joint et pourquoi quelqu'un serait ignoré, retenu ou abandonné. Copier l'appel donne le YAML pour votre automatisation. Envoyer le test envoie un vrai message qui se termine de lui-même après 10 minutes." },
      q6: { q: "Qu'est-ce qu'un canal ?", a: "Un canal est l'endroit où un message s'affiche. Il y en a six :\n- Bannière : une carte sur vos tableaux de bord.\n- Push : l'application Companion sur téléphones et tablettes.\n- Popup : un message au-dessus de toute page de tableau de bord ouverte.\n- Voix : dite sur des haut-parleurs et satellites Assist.\n- Courriel : par un service notify de votre choix.\n- Persistent Notification : la cloche de Home Assistant.\n\nUn appel liste les canaux voulus, et une politique peut en ajouter plus tard, par exemple lors d'une escalade." },
      q7: { q: "Comment configurer le courriel (SMTP) ?", a: "Le courriel ne fonctionne pas tout seul, car Heads Up n'envoie pas de courriel lui-même. Il confie chaque courriel à un service notify de Home Assistant, et ce service a besoin d'un serveur de messagerie.\n\nPour le configurer :\n- Ajoutez l'intégration SMTP sous Réglages > Appareils et services. Elle demande le serveur, le port, la sécurité de connexion, l'expéditeur, le nom d'utilisateur et le mot de passe, et crée un service notify nommé d'après l'entrée.\n- Ouvrez Configuration > Canaux > Courriel et choisissez ce service notify. Sans lui, le courriel échoue avec no_mail_service.\n- Facultatif : saisissez une adresse globale.\n- Ouvrez Destinataires. Pour chaque personne qui doit recevoir des courriels, activez Courriel et saisissez l'adresse.\n\nLe courriel reste désactivé pour tous jusqu'à la dernière étape : une audience comme Tout le monde ne joint donc que les personnes qui ont accepté. Essayez avec Envoi de test et le canal Courriel.\n\nHeads Up sait seulement si le service notify a renvoyé une erreur, pas si le courriel est arrivé. Si un envoi échoue, consultez les lignes de journal de l'intégration SMTP. Après un envoi réussi, l'intégration SMTP crée une réparation indiquant que ce service notify est obsolète et sera supprimé dans Home Assistant 2027.3." },
      q8: { q: "Qu'est-ce qu'une audience, et en quoi diffère-t-elle d'un destinataire ?", a: "Une audience est un groupe nommé de personnes qui peut changer avec le temps : Tout le monde, Admins, À la maison, Dernier parti, ou les vôtres. Un destinataire est une cible fixe : une personne, un téléphone ou un haut-parleur. Un canal prend une audience ou des destinataires, jamais les deux." },
      q9: { q: "Qu'est-ce qu'une politique ?", a: "Une politique change le comportement des messages sans modifier l'automatisation qui les envoie. Il y en a sept types :\n- Escalade : prévenir d'autres personnes ou canaux si personne ne confirme.\n- Rappel : répéter le message.\n- Heures calmes : envoyer discrètement, retenir ou abandonner les messages la nuit.\n- Absence : envoyer quand la personne arrive.\n- Repli : envoyer à quelqu'un d'autre quand personne n'a été joint.\n- Remise : ajouter des canaux tout de suite, par exemple un push pour les messages critiques.\n- Résumé : retenir les messages et envoyer un seul résumé.\n\nL'introduction propose quatre politiques par défaut, et la page Politiques liste toutes les vôtres." },
      q10: { q: "À quoi sert la gravité ?", a: "Un message a l'une de quatre gravités : success, info, warning (par défaut) et critical.\n- Bannière : règle la couleur, l'icône et l'ordre, critique d'abord.\n- Push : règle le niveau. success et info sont passifs, warning normal, critical urgent.\n- Popup : le style se règle aussi par gravité.\n- Politiques : peuvent s'y appuyer, par exemple une escalade pour les seuls messages critiques." },
      q11: { q: "À quoi servent les étiquettes ?", a: "Une étiquette est un libellé que vous donnez à un message, par exemple laundry ou water. Des politiques peuvent s'appliquer à certaines étiquettes seulement, une carte peut n'afficher que les bannières d'une étiquette, et heads_up.clear_notifications peut supprimer tous les messages d'une étiquette. Les messages des règles de surveillance portent l'étiquette rule." },
      q12: { q: "Cela fonctionne-t-il avec Android et iPhone ?", a: "Le push passe par l'application Companion de Home Assistant, qui existe pour les deux.\n- La gravité règle le niveau.\n- Critique est une alarme sur les deux. Sur iPhone, c'est l'alerte critique : elle demande l'autorisation de l'application et joue un son en mode silencieux. Sur Android, elle utilise le canal d'alarme, qui sonne aussi en mode vibreur et silencieux. Ne pas déranger n'est contourné sur Android que si vous l'autorisez pour ce canal dans les réglages du système.\n- Android affiche jusqu'à 3 boutons sur un push et iOS jusqu'à 10. Android garde Confirmer et Fermer en premier.\n\nCela n'a pas encore été essayé sur de vrais téléphones ; les tests utilisent un substitut de l'application." },
      q13: { q: "Que sont les escalades et les rappels ?", a: "Les deux démarrent quand personne ne confirme un message.\n- Une escalade attend un temps donné (5 minutes par défaut) puis remet le message sur d'autres canaux ou à d'autres personnes.\n- Un rappel répète le message toutes les N minutes (30 par défaut), 3 fois au plus.\n\nUne confirmation arrête les deux. Avec le réglage selon lequel chaque politique qui s'applique agit, l'élément Messages critiques de l'introduction crée un push immédiat, un rappel toutes les 10 minutes et, si vous choisissez des haut-parleurs, la voix après 10 minutes. Par défaut, seule la première politique qui s'applique agit : les messages critiques ne reçoivent alors que le push immédiat." },
      q14: { q: "Comment appliquer des politiques ?", a: "Il y a deux façons.\n- Automatique : chaque politique liste les gravités et étiquettes auxquelles elle s'applique, une liste vide correspond à tout. Chaque message correspondant utilise la politique, sans rien changer à l'automatisation.\n- Manuelle : une politique réglée sur Manuellement ne s'applique jamais d'elle-même. Seul un appel ou une règle de surveillance qui la nomme dans son champ policy la reçoit. Une politique nommée est la seule utilisée pour cet appel, none n'en utilise aucune.\n\nQuand plusieurs politiques automatiques correspondent, le réglage Comment les politiques interagissent sur la page Politiques décide : par défaut, seule la première de la liste agit, et l'ordre se règle en faisant glisser. L'autre réglage fait agir chaque politique correspondante.\n\nUn message sans étiquette ne correspond qu'aux politiques sans étiquette. Une politique désactivée n'est jamais utilisée." },
      q15: { q: "Que fait une confirmation, et en quoi diffère-t-elle d'un masquage ?", a: "Confirmer dit que quelqu'un a vu le message. Cela arrête toutes les escalades et tous les rappels de ce message pour tout le monde, et la bannière reste. Masquer ferme le message pour la personne qui le masque. Une politique d'escalade peut compter un masquage comme une confirmation." },
      q16: { q: "Comment masquer un message pour tous, sur tous les canaux ?", a: "Il y a trois façons.\n- À la main : appelez heads_up.clear_notifications avec un id, une étiquette, une gravité ou un canal. Cela retire les messages correspondants de chaque canal ; all: true retire tous les messages.\n- Par condition : donnez une condition au message. En mode once il se termine quand la condition devient fausse.\n- Par le spectateur : réglez la portée de fermeture (dismiss_scope) sur global, sur le message, sur une règle de surveillance ou par défaut sous Réglages > Messages. Quand quelqu'un le ferme, il se termine pour tous et les push sont retirés. Avec la portée user, fermer ne le masque que pour cette personne et ne retire que son push.\n\nUn délai d'expiration termine aussi un message partout." },
      q17: { q: "Pourquoi n'ai-je pas reçu de notification ?", a: "- Envoi de test montre qui serait prévenu pour un appel et pourquoi quelqu'un est ignoré, retenu ou abandonné.\n- Le journal des messages montre ce qui s'est passé pour un vrai message : chaque remise avec son résultat et sa raison, par exemple heures calmes, aucun appareil utilisable ou limite de débit.\n- Un envoi échoué dans les dernières 24 heures apparaît aussi sous À surveiller." },
      q18: { q: "Comment garder les messages silencieux la nuit ?", a: "Ajoutez une politique d'heures calmes. Pendant la plage, elle peut envoyer discrètement, retenir les messages jusqu'à la fin ou les abandonner. Les messages critiques passent par défaut. L'élément Heures calmes de l'introduction en crée une de 22:00 à 07:00 qui envoie discrètement." },
      q19: { q: "Et si quelqu'un n'est pas à la maison ?", a: "Une politique d'absence envoie le message à l'arrivée de la personne, tant qu'il est encore actif. Une politique de repli l'envoie à quelqu'un d'autre quand la première remise n'a joint personne." },
      q20: { q: "Puis-je recevoir un résumé au lieu de nombreux messages ?", a: "Oui. Une politique de résumé retient les messages correspondants et envoie un résumé toutes les N minutes ou à une heure fixe, avec le nombre et les titres. Tant qu'un message est retenu, rien n'est envoyé pour lui sur aucun canal, la bannière du tableau de bord comprise. Les messages critiques ne sont retenus que si vous les incluez." },
      q21: { q: "Un appel peut-il utiliser plusieurs canaux ?", a: "Oui. Nommez les canaux et donnez à chacun sa propre cible sous to, comme dans l'exemple 3 des exemples notify. La notification persistante n'a pas besoin de cible." },
      q22: { q: "Pourquoi la voix n'accepte-t-elle pas d'audience ?", a: "Une audience est un ensemble de personnes, alors que la voix va vers un haut-parleur dans un lieu. Le hub ne sait pas près de quel haut-parleur se trouve une personne : vous nommez donc des haut-parleurs, des groupes ou des zones." },
      q23: { q: "Les messages critiques sont-ils traités à part ?", a: "Oui, à quatre endroits.\n- Les heures calmes les laissent passer, sauf si vous le désactivez.\n- Le résumé ne les retient pas, sauf si vous les incluez.\n- Les limites de débit ne les retiennent jamais.\n- Les audiences de présence incluent une personne dont la présence est inconnue.\n\nL'absence n'a pas d'exception : limitez ses gravités si les messages critiques doivent partir tout de suite." },
      q24: { q: "Qu'est-ce qui empêche un déluge de push ?", a: "Trois limites :\n- 5 push par appareil et par minute.\n- 60 push au total par minute.\n- Aucune répétition d'une mise à jour identique pendant 30 secondes.\n\nUn push ignoré apparaît dans la trace comme rate_limited ou duplicate. Les trois sont des réglages, et les messages critiques ne sont jamais retenus." },
      q25: { q: "Que se passe-t-il quand je remplace un téléphone ?", a: "Modifiez une fois le profil de destinataire de la personne. Les audiences et les politiques ne changent pas, et aucune automatisation n'est à modifier." },
      q26: { q: "Pourquoi une nouvelle politique ne change-t-elle pas un message déjà affiché ?", a: "Une politique est consultée quand un message apparaît. Une politique ajoutée plus tard commence à la prochaine mise à jour du message. Une politique de résumé ne retient pas les messages déjà présents." },
      q27: { q: "Que se passe-t-il après un redémarrage ?", a: "- Les escalades en attente gardent leur échéance. Une étape échue pendant le redémarrage s'exécute une fois si le message est encore actif et non confirmé.\n- Les messages retenus pour les heures calmes, l'absence ou un résumé restent retenus.\n- Les push de messages qui n'existent plus sont supprimés.\n- La liste des messages récents et des dernières actions repart vide." },
    },
  },
  es: {
    titles: {"faq": "Preguntas", "examples": "Ejemplos de notify", "card": "Ejemplos de tarjeta"},
    intros: {"faq": "Respuestas a preguntas frecuentes.", "examples": "Llamadas de la acción heads_up.notify, de la más simple a la más detallada. Admins es una audiencia integrada. Ground floor (group), person.anna y media_player.kitchen son ejemplos: sustitúyelos por tus propios grupos de altavoces, personas y altavoces.", "card": "Ajustes de la tarjeta de panel custom:heads-up-card. Pega uno en el editor YAML de la tarjeta, o pon las mismas opciones en su editor visual."},
    copy: "Copiar",
    copied: "Copiado.",
    issues_lead: "¿Encontraste un problema o echas algo en falta?",
    issues_link: "Abrir una incidencia en GitHub",
    copy_failed: "No se puede copiar aquí. Selecciona el texto.",
    ex: {
      e1: { title: "1. Solo aviso", note: "No hace falta ningún objeto del hub. No se envía nada más." },
      e2: { title: "2. Aviso y push, las políticas añaden el resto", note: "Las políticas que coinciden con la gravedad y la etiqueta también se aplican, por ejemplo un escalado a Admins tras 5 minutos." },
      e3: { title: "3. Push, voz y notificación persistente juntos", note: "Cada canal tiene su propio destino. La notificación persistente no necesita ninguno." },
      e4: { title: "4. Una llamada sin política", note: "Voz en un altavoz, ignorando todas las políticas." },
      e5: { title: "5. Atajo para un canal", note: "El atajo push con una audiencia de presencia: la persona cuya salida vació la casa." },
      e6: { title: "6. A una persona", note: "Un destinatario directo en lugar de una audiencia." },
    },
    card_ex: {
      c1: { title: "1. La tarjeta por defecto", note: "Muestra todos los avisos pensados para quien mira, los críticos primero." },
      c2: { title: "2. Una lista compacta", note: "Una línea por aviso: los tres primeros son visibles, un botón muestra el resto, y cada aviso dice hace cuánto se creó." },
      c3: { title: "3. Solo lo que requiere acción", note: "Solo avisos críticos y de aviso, con un botón que los borra todos y deslizar para descartar en pantalla táctil." },
      c4: { title: "4. Una habitación", note: "Solo avisos con la etiqueta kitchen, los más nuevos primero, y un texto breve cuando no hay ninguno. Envía la etiqueta con tag: kitchen en la llamada." },
      c5: { title: "5. Una tableta de pared para el administrador", note: "Muestra también avisos pensados para otras personas (solo administradores), lista los avisos pospuestos y sigue visible cuando está vacía." },
      c6: { title: "6. Tus propios colores", note: "Solo el icono y la etiqueta toman el color de la gravedad, la etiqueta se muestra como texto, y crítico usa un rojo fijo." },
    },
    q: {
      q1: { q: "¿Qué hace Heads Up?", a: "Tu automatización hace una sola llamada, heads_up.notify. Heads Up decide dónde aparece el mensaje (canales), quién lo recibe (audiencias y destinatarios) y cuándo se entrega o se escala (políticas). Lo configuras una vez en este panel, no en cada automatización." },
      q2: { q: "¿En qué se diferencia de lo que Home Assistant ya tiene?", a: "Cada servicio notify de Home Assistant envía a un solo lugar, y cada automatización nombra sus propios dispositivos. Heads Up añade:\n- Una llamada que llega a varios canales.\n- Audiencias como En casa o Último en salir, calculadas al enviar.\n- Políticas (escalar, recordar, silencio nocturno, resumir), fijadas una vez para todas las automatizaciones.\n- El aviso, un canal nuevo: una tarjeta en tus paneles que se queda hasta que se descarta, termina su condición o caduca.\n- Un solo ciclo de vida: un mensaje termina en todas partes a la vez, push incluido, y cada entrega queda registrada." },
      q3: { q: "¿Qué tengo que configurar primero?", a: "Esto es lo esencial:\n- Avisos: añade la tarjeta a un panel.\n- Push: comprueba que cada persona tiene la app Companion. Heads Up encuentra sus dispositivos por los rastreadores de la persona.\n- Voz: nombra tus altavoces, solos o en un grupo.\n- Correo: elige un servicio notify en la página Canales (mira la pregunta sobre el correo).\n- Políticas: activa en la introducción las que quieras.\n\nEl resumen lista en Requiere atención los problemas que detecta, por ejemplo una persona sin dispositivo utilizable." },
      q4: { q: "¿Puedo mostrar un aviso sin escribir una automatización?", a: "Sí, con una regla de vigilancia. Una regla observa una entidad o una plantilla y muestra un aviso mientras la condición sea verdadera.\n- Cuando deja de serlo, Heads Up quita el aviso.\n- Las reglas viven en Heads Up, no en un panel, así que varias tarjetas con filtros distintos las comparten.\n- Añade una en la página Reglas de vigilancia.\n\nUna automatización con heads_up.create_banner, o heads_up.notify con el canal aviso, y una condición hace lo mismo. Las políticas también se aplican: con la etiqueta rule, una política de entrega puede enviar además un push inmediato de un mensaje crítico de regla." },
      q5: { q: "¿Puedo probar las notificaciones?", a: "Sí, en Envío de prueba. Indica el mensaje, los canales y quién lo recibe. La tabla muestra a quién se llegaría y por qué alguien se omitiría, retendría o descartaría. Copiar llamada da el YAML para tu automatización. Enviar prueba envía un mensaje real que termina solo tras 10 minutos." },
      q6: { q: "¿Qué es un canal?", a: "Un canal es el lugar donde aparece un mensaje. Hay seis:\n- Aviso: una tarjeta en tus paneles.\n- Push: la app Companion en teléfonos y tabletas.\n- Ventana emergente: un mensaje sobre cualquier página de panel abierta.\n- Voz: dicho en altavoces y satélites Assist.\n- Correo: con un servicio notify que elijas.\n- Persistent Notification: la campana de Home Assistant.\n\nUna llamada lista los canales que quiere, y una política puede añadir más después, por ejemplo al escalar." },
      q7: { q: "¿Cómo configuro el correo (SMTP)?", a: "El correo no funciona de fábrica porque Heads Up no envía correos por sí mismo. Entrega cada correo a un servicio notify de Home Assistant, y ese servicio necesita un servidor de correo.\n\nPara configurarlo:\n- Añade la integración SMTP en Ajustes > Dispositivos y servicios. Pide servidor, puerto, seguridad de la conexión, remitente, usuario y contraseña, y crea un servicio notify con el nombre de la entrada.\n- Abre Configuración > Canales > Correo y elige ese servicio notify. Sin él, el correo falla con no_mail_service.\n- Opcional: escribe una dirección global.\n- Abre Destinatarios. Para cada persona que deba recibir correo, activa Correo y escribe la dirección.\n\nEl correo sigue desactivado para todos hasta el último paso, así que una audiencia como Todos solo llega a las personas que lo aceptaron. Pruébalo con Envío de prueba y el canal Correo.\n\nHeads Up solo sabe si el servicio notify devolvió un error, no si el correo llegó. Si un envío falla, mira las líneas de registro de la integración SMTP. Tras enviar un correo, la integración SMTP crea una reparación que indica que este servicio notify está obsoleto y se eliminará en Home Assistant 2027.3." },
      q8: { q: "¿Qué es una audiencia y en qué se diferencia de un destinatario?", a: "Una audiencia es un grupo con nombre de personas que puede cambiar con el tiempo: Todos, Admins, En casa, Último en salir o las tuyas. Un destinatario es un destino fijo: una persona, un teléfono o un altavoz. Un canal admite una audiencia o destinatarios, nunca ambos." },
      q9: { q: "¿Qué es una política?", a: "Una política cambia cómo se comportan los mensajes sin cambiar la automatización que los envía. Hay siete tipos:\n- Escalado: avisar a más personas o canales si nadie confirma.\n- Recordatorio: repetir el mensaje.\n- Horas de silencio: enviar en silencio, retener o descartar mensajes por la noche.\n- Ausencia: enviar cuando la persona llega.\n- Alternativa: enviar a otra persona cuando no se llegó a nadie.\n- Entrega: añadir canales al instante, por ejemplo un push para mensajes críticos.\n- Resumen: retener mensajes y enviar un solo resumen.\n\nLa introducción ofrece cuatro por defecto, y la página Políticas lista todas las tuyas." },
      q10: { q: "¿Para qué sirve la gravedad?", a: "Un mensaje tiene una de cuatro gravedades: success, info, warning (por defecto) y critical.\n- Aviso: fija el color, el icono y el orden, crítico primero.\n- Push: fija el nivel. success e info son pasivos, warning normal, critical urgente.\n- Ventana emergente: el estilo también se fija por gravedad.\n- Políticas: pueden basarse en ella, por ejemplo un escalado solo para críticos." },
      q11: { q: "¿Para qué sirven las etiquetas?", a: "Una etiqueta es un rótulo que das a un mensaje, por ejemplo laundry o water. Las políticas pueden aplicarse solo a ciertas etiquetas, una tarjeta puede mostrar solo avisos con una etiqueta, y heads_up.clear_notifications puede eliminar todos los mensajes con una etiqueta. Los mensajes de las reglas de vigilancia llevan la etiqueta rule." },
      q12: { q: "¿Funciona con Android y iPhone?", a: "El push pasa por la app Companion de Home Assistant, que existe para ambos.\n- La gravedad fija el nivel.\n- Crítico es una alarma en ambos. En iPhone es la alerta crítica: necesita el permiso de la app y suena aunque esté en silencio. En Android usa el canal de alarma, que también suena en modo vibración y silencio. No molestar solo se anula en Android si lo permites para ese canal en los ajustes del sistema.\n- Android muestra hasta 3 botones en un push e iOS hasta 10. Android conserva Confirmar y Descartar primero.\n\nAún no se ha probado en teléfonos reales; las pruebas usan un sustituto de la app." },
      q13: { q: "¿Qué son los escalados y los recordatorios?", a: "Ambos empiezan cuando nadie confirma un mensaje.\n- Un escalado espera un tiempo (5 minutos por defecto) y entrega el mensaje en otros canales o a otras personas.\n- Un recordatorio repite el mensaje cada N minutos (30 por defecto), como máximo 3 veces.\n\nUna confirmación detiene ambos. Con el ajuste de que actúa cada política que se aplica, el elemento Mensajes críticos de la introducción crea un push inmediato, un recordatorio cada 10 minutos y, si eliges altavoces, voz a los 10 minutos. Por defecto solo actúa la primera política que se aplica, así que los mensajes críticos reciben solo el push inmediato." },
      q14: { q: "¿Cómo aplico las políticas?", a: "Hay dos formas.\n- Automática: cada política lista las gravedades y etiquetas a las que se aplica, una lista vacía coincide con todo. Cada mensaje que coincide usa la política, sin cambiar la automatización.\n- Manual: una política en Manualmente nunca se aplica sola. Solo una llamada o una regla de vigilancia que la nombra en su campo policy la recibe. Una política nombrada es la única que se usa para esa llamada, none no usa ninguna.\n\nCuando varias políticas automáticas coinciden, decide el ajuste Cómo interactúan las políticas de la página Políticas: por defecto solo actúa la primera de la lista, y el orden se fija arrastrando. El otro ajuste hace actuar cada política que coincide.\n\nUn mensaje sin etiqueta solo coincide con políticas sin etiquetas. Una política desactivada nunca se usa." },
      q15: { q: "¿Qué hace confirmar y en qué se diferencia de descartar?", a: "Confirmar dice que alguien vio el mensaje. Detiene todos los escalados y recordatorios de ese mensaje para todos, y el aviso se queda. Descartar cierra el mensaje para quien lo descarta. Una política de escalado puede contar un descarte como confirmación." },
      q16: { q: "¿Cómo descarto un mensaje para todos, en todos los canales?", a: "Hay tres formas.\n- A mano: llama a heads_up.clear_notifications con un id, una etiqueta, una gravedad o un canal. Quita los mensajes que coinciden de todos los canales; all: true quita todos los mensajes.\n- Por condición: da una condición al mensaje. En modo once termina cuando la condición pasa a falsa.\n- Por quien lo ve: pon el ámbito de cierre (dismiss_scope) en global, en el mensaje, en una regla de vigilancia o por defecto en Ajustes > Mensajes. Cuando alguien lo cierra, termina para todos y se retiran los push. Con el ámbito user, cerrar lo oculta solo a esa persona y retira solo su push.\n\nUn tiempo límite también termina un mensaje en todas partes." },
      q17: { q: "¿Por qué no recibí una notificación?", a: "- Envío de prueba muestra a quién se avisaría con una llamada y por qué alguien se omite, retiene o descarta.\n- El registro de mensajes muestra qué pasó con un mensaje real: cada entrega con su resultado y motivo, por ejemplo horas de silencio, ningún dispositivo utilizable o límite de frecuencia.\n- Un envío fallido en las últimas 24 horas también aparece en Requiere atención." },
      q18: { q: "¿Cómo mantengo los mensajes en silencio por la noche?", a: "Añade una política de horas de silencio. Durante la franja puede enviar en silencio, retener los mensajes hasta el final o descartarlos. Los mensajes críticos pasan por defecto. El elemento Horas de silencio de la introducción crea una de 22:00 a 07:00 que envía en silencio." },
      q19: { q: "¿Y si alguien no está en casa?", a: "Una política de ausencia envía el mensaje cuando la persona llega, mientras siga activo. Una política de alternativa lo envía a otra persona cuando la primera entrega no llegó a nadie." },
      q20: { q: "¿Puedo recibir un resumen en lugar de muchos mensajes?", a: "Sí. Una política de resumen retiene los mensajes que coinciden y envía un resumen cada N minutos o a una hora fija, con el número y los títulos. Mientras un mensaje está retenido no se envía nada por ningún canal, tampoco el aviso del panel. Los mensajes críticos solo se retienen si los incluyes." },
      q21: { q: "¿Puede una llamada usar varios canales?", a: "Sí. Nombra los canales y da a cada uno su propio destino bajo to, como en el ejemplo 3 de los ejemplos de notify. La notificación persistente no necesita destino." },
      q22: { q: "¿Por qué la voz no admite audiencia?", a: "Una audiencia es un conjunto de personas, y la voz va a un altavoz en un lugar. El hub no sabe junto a qué altavoz está una persona, así que nombras altavoces, grupos o áreas." },
      q23: { q: "¿Los mensajes críticos reciben un trato especial?", a: "Sí, en cuatro sitios.\n- Las horas de silencio los dejan pasar, salvo que lo desactives.\n- El resumen no los retiene, salvo que los incluyas.\n- Los límites de frecuencia nunca los retienen.\n- Las audiencias de presencia incluyen a una persona con presencia desconocida.\n\nLa ausencia no tiene excepción: limita sus gravedades si los críticos deben salir al instante." },
      q24: { q: "¿Qué evita una avalancha de push?", a: "Tres límites:\n- 5 push por dispositivo y minuto.\n- 60 push en total por minuto.\n- Ninguna repetición de una actualización idéntica en 30 segundos.\n\nUn push omitido aparece en el rastro como rate_limited o duplicate. Los tres son ajustes, y los mensajes críticos nunca se retienen." },
      q25: { q: "¿Qué pasa cuando cambio un teléfono?", a: "Edita una vez el perfil de destinatario de la persona. Las audiencias y las políticas no cambian, y ninguna automatización necesita edición." },
      q26: { q: "¿Por qué una política nueva no cambia un mensaje que ya se muestra?", a: "Una política se consulta cuando aparece un mensaje. Una política añadida después empieza cuando el mensaje se actualiza. Una política de resumen no retiene los mensajes que ya están." },
      q27: { q: "¿Qué pasa tras un reinicio?", a: "- Los escalados pendientes conservan su vencimiento. Un paso que venció durante el reinicio se ejecuta una vez si el mensaje sigue activo y sin confirmar.\n- Los mensajes retenidos por horas de silencio, ausencia o resumen siguen retenidos.\n- Se eliminan los push de mensajes que ya no existen.\n- La lista de mensajes recientes y últimas acciones empieza vacía." },
    },
  },
};

const CSS = `
.hu-help details { border-top: 1px solid var(--divider-color); padding: 4px 0; }
.hu-help summary { cursor: pointer; min-height: 44px; display: flex; align-items: center; font-weight: 500; }
.hu-help summary:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-help .answer { margin: 4px 0 12px; color: var(--secondary-text-color); }
.hu-help a { color: var(--primary-color); }
.hu-help h3 { font-size: 15px; margin: 16px 0 2px; }
`;

export const PAGES = ["faq", "examples", "card"];

// One example with its title, note and a Copy button.
function exampleNode(example, text, t, el) {
  const status = el("span", { className: "hint" });
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const copy = el("button", { type: "button", textContent: t.copy });
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(example.yaml);
      status.textContent = t.copied;
    } catch (err) {
      status.textContent = t.copy_failed;
    }
  });
  return [
    el("h3", { textContent: text.title }),
    el("div", { className: "hint", textContent: text.note }),
    el("pre", { textContent: example.yaml }),
    el("div", { className: "row" }, [copy, status]),
  ];
}

export function mount(container, ctx) {
  const t = ctx.t;
  const page = PAGES.includes(ctx.page) ? ctx.page : "faq";
  const { el, BASE_CSS } = ctx.ui;
  const root = el("div", { className: "hu-page hu-help" });
  root.append(el("style", { textContent: BASE_CSS + CSS }), el("h1", { textContent: t.titles[page] }));
  const link = el("a", { href: ISSUES_URL, target: "_blank", rel: "noopener noreferrer", textContent: t.issues_link });
  root.append(el("div", { className: "hint" }, [`${t.intros[page]} ${t.issues_lead} `, link]));

  if (page === "faq") {
    const questions = el("section", {});
    for (const id of QUESTION_IDS) {
      const item = t.q[id];
      questions.append(el("details", {}, [el("summary", { textContent: item.q }), ctx.ui.richNode(item.a, { className: "answer" })]));
    }
    root.append(questions);
  } else {
    const list = page === "examples" ? EXAMPLES : CARD_EXAMPLES;
    const texts = page === "examples" ? t.ex : t.card_ex;
    const section = el("section", {});
    for (const example of list) section.append(...exampleNode(example, texts[example.id], t, el));
    root.append(section);
  }
  container.append(root);
  return { setHass() {} };
}
