// Heads Up panel: Policies page (D-119, DESIGN §25.9): the lanes, the band, the check list and the
// checker. One form for the eight types, saved through the policy flow.

const TYPE_NAMES = {
  en: { escalation: "Escalation", reminder: "Reminder", quiet_hours: "Quiet hours", presence: "Presence", fallback: "Fallback", summarize: "Summarize", deliver: "Deliver", get_through: "Get through" },
  de: { escalation: "Eskalation", reminder: "Erinnerung", quiet_hours: "Ruhezeit", presence: "Anwesenheit", fallback: "Ersatz", summarize: "Zusammenfassen", deliver: "Zustellen", get_through: "Kommt durch" },
  fr: { escalation: "Escalade", reminder: "Rappel", quiet_hours: "Heures calmes", presence: "Présence", fallback: "Repli", summarize: "Résumer", deliver: "Livrer", get_through: "Laisser passer" },
  es: { escalation: "Escalado", reminder: "Recordatorio", quiet_hours: "Horas de silencio", presence: "Presencia", fallback: "Alternativa", summarize: "Resumir", deliver: "Entregar", get_through: "Dejar pasar" },
};
const DAY_NAMES = {
  en: { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" },
  de: { mon: "Montag", tue: "Dienstag", wed: "Mittwoch", thu: "Donnerstag", fri: "Freitag", sat: "Samstag", sun: "Sonntag" },
  fr: { mon: "Lundi", tue: "Mardi", wed: "Mercredi", thu: "Jeudi", fri: "Vendredi", sat: "Samedi", sun: "Dimanche" },
  es: { mon: "Lunes", tue: "Martes", wed: "Miércoles", thu: "Jueves", fri: "Viernes", sat: "Sábado", sun: "Domingo" },
};
const ACTIONS = {
  en: { quiet: "Send quietly", wait: "Hold until the end", drop: "Drop" },
  de: { quiet: "Leise senden", wait: "Bis zum Ende zurückhalten", drop: "Verwerfen" },
  fr: { quiet: "Envoyer discrètement", wait: "Retenir jusqu'à la fin", drop: "Abandonner" },
  es: { quiet: "Enviar en silencio", wait: "Retener hasta el final", drop: "Descartar" },
};
const WHENS = {
  en: { no_audience: "Nobody to notify", failed: "Delivery failed", both: "Either" },
  de: { no_audience: "Niemand zu benachrichtigen", failed: "Zustellung fehlgeschlagen", both: "Eines von beiden" },
  fr: { no_audience: "Personne à notifier", failed: "Échec de l'envoi", both: "L'un ou l'autre" },
  es: { no_audience: "Nadie a quien avisar", failed: "Falló el envío", both: "Cualquiera de los dos" },
};

export const STRINGS = {
  en: {
    title: "Policies",
    intro: "Policies decide when a message may reach people, who else gets it and how often. Every policy that fits a message acts; there is no order.",
    none: "You have no policies yet. The introduction (Settings, Restart introduction) offers a starting set.",
    new: "New policy",
    editing: "Edit policy",
    type: "Type",
    types: TYPE_NAMES.en,
    disabled: "disabled",
    applies: "Applies to",
    severities: "Severities (none selected: any)",
    tags: "Tags, comma separated (empty: any)",
    severity_names: { passive: "Passive", info: "Info", warning: "Warning", critical: "Critical" },
    channel_names: { push: "Push", popup: "Popup", speak: "Speak", persistent: "Persistent Notification", mail: "Mail" },
    after: "Escalate after (minutes)",
    channels: "Channels",
    channels_reminder: "Limit to these channels (none selected: all)",
    dismiss_acks: "Dismissing counts as acknowledging",
    every: "Repeat every (minutes)",
    max_count: "At most this many reminders",
    from: "Quiet from",
    to: "Quiet until",
    days: "Days (none selected: every day)",
    days_names: DAY_NAMES.en,
    action: "During quiet hours",
    actions: ACTIONS.en,
    entity_id: "Entity ID of the switch",
    entity_id_new: "Home Assistant gives the policy this switch when you save. Name it in the policy field of a call by this ID: it keeps working when you rename the policy.",
    entity_id_own: "A rename does not change this ID. A call that names the policy by its text name stops working after a rename; a call that uses this ID does not.",
    max_wait: "Wait for arrival (minutes, 0: as long as the message lives)",
    when: "Use when",
    whens: WHENS.en,
    channels_from: "Channels come from",
    targets_from: "Recipients come from",
    cf: { policy: "This policy (the channels below)", call: "The call (the same channels)", failed: "The call, only the channels that reached nobody" },
    tf: { policy: "This policy (the recipients below)", call: "The call (the same recipients)" },
    people_target: "People: push, popup and mail",
    speakers_target: "Speakers: speech",
    tf_call_hint: "The people and speakers the call named receive it on the channels above.",
    same_empty: "The call reached nobody because the audience was empty, so the same recipients are empty too. Use Delivery failed, or give other recipients.",
    s_channels_call: "the channels of the call",
    s_channels_failed: "the channels of the call that reached nobody",
    s_recipients_call: " The recipients are the ones the call named.",
    s_recipients_policy: " It goes to {who}.",
    summary_mode: "Send the summary",
    summary_every_mode: "Every N minutes",
    summary_at_mode: "At a time of day",
    summary_every: "Minutes after the first held message",
    summary_at: "Time of day",
    summarize_note: "Nothing is sent individually while a message waits. The summary shows the count and the titles, marks resolved ones and cuts at 10 (“and N more”).",
    ack_note: "Pushes of messages this policy covers get an Acknowledge button.",
    target_channel: "Channel {channel}",
    target_audience: "Audience",
    target_recipients: "Recipients",
    target_persistent: "No target: it goes to everyone.",
    sentence: "In words",
    s_applies_any: "Every message",
    enabled_hint: "A disabled policy is never used, not even when a call names it.",
    sec_when: "Which messages",
    sec_does: "What it does",
    type_desc: {"get_through": "Lets the messages it fits past quiet hours and summaries for the people it covers. It sends nothing itself; pair it with a Deliver policy.", "escalation": "If nobody acknowledges within the time, the message is also delivered on the channels and to the targets you choose.", "reminder": "While nobody acknowledges, the message is repeated at an interval, up to a maximum.", "quiet_hours": "Between two times of day, deliveries outside the dashboard are sent quietly, held until the end or dropped.", "presence": "Holds or drops a delivery by where people are: for each recipient on push, popup and mail, for the household on speakers.", "fallback": "If the first delivery reached nobody, the message is delivered somewhere else: on other channels, or to other people on the same channels.", "summarize": "Matching messages are held on every channel, the banner included, and one summary is sent instead.", "deliver": "Matching messages are also delivered at once to the audience and channels you choose."},
    apply_label: "Attaches to messages",
    apply_auto: "Automatically",
    apply_auto_hint: "Every message whose severity and tag match gets this policy. An empty list matches any.",
    apply_manual: "Manually",
    apply_manual_hint: "Only a call that names this policy gets it. The severity and the tag of the message do not matter.",
    manual_how: "Name it in a call:",
    manual_note: "A call that names a policy uses only that policy, not the automatic ones. policy: none switches every policy off for a call.",
    badge_manual: "manual",
    lane_calm: "Keep it calm",
    lane_calm_hint: "These act on every delivery, also on what the other lane adds. Where two disagree, the calmer counts. Repeats never wait: they are skipped.",
    band: "Always gets through",
    band_hint: "These messages are never summarized, and quiet hours do not apply to the people covered. Presence still decides by where people are.",
    lane_arrive: "Make sure it arrives",
    lane_arrive_hint: "Every sending policy that fits runs. Escalations and reminders count from when the message was created.",
    lane_named: "Only when named",
    lane_named_hint: "These act only when a call or a watch rule names them by their entity ID.",
    not_severities: "Not for severities",
    not_tags: "Not for tags, comma separated",
    rules: "From watch rule (none selected: any source)",
    only_if: "Only if",
    only_if_hint: "The policy acts only while this holds. Unknown counts as whatever delivers more.",
    oi_entity: "Entity",
    oi_state: "State",
    oi_none: "Always (no condition)",
    faster: "Faster while",
    faster_every: "Then repeat every (minutes)",
    alongside: "Runs alongside other reminders",
    alongside_hint: "Off: reminders on the same channel share the shortest rhythm, each with its own count.",
    holds_anyway: "Holds these anyway",
    holds_anyway_hint: "No Always gets through entry lets messages past this policy.",
    covers: "Covers",
    covers_everyone: "Everyone it reaches",
    covers_only: "Only these",
    covers_audiences: "Audiences",
    covers_recipients: "People and speakers",
    s_through: "{applies}: may wake {who} despite quiet hours and summaries.",
    s_through_everyone: "everyone it reaches",
    s_not_for: " Not for {list}.",
    s_only_if: " Only while {entity} is {state}.",
    s_faster: " While {entity} is {state}: every {n} min.",
    s_alongside: " Runs alongside other reminders.",
    s_holds_anyway: " No Always gets through entry passes it.",
    s_rules: " Only messages of the watch rules {names}.",
    links_note: "Acts only on messages that {names} do not take, as in 1.x.",
    overlap_calm: "Where it and {names} both fit, the calmer counts.",
    overlap_send: "Also acts on the same messages: {names}.",
    cl_title: "Check after the update",
    cl_intro: "The update kept what your policies did. These policies now work differently or never act; choose for each.",
    cl_links: "{name} acts only on messages that {names} do not take, as before.",
    cl_never: "{name} never acts: {names} take all its messages first.",
    cl_holds: "{name} holds critical messages too, as before.",
    cl_keep: "Keep as before",
    cl_act: "Let it act",
    cl_through: "Let Critical through",
    cl_dismiss: "Hide the list",
    cl_kept: "kept",
    cl_changed: "changed",
    ck_title: "What happens to a message?",
    ck_intro: "Nothing is sent. The answer uses the policies as they are now.",
    ck_severity: "Severity",
    ck_tag: "Tag",
    ck_channels: "Channels",
    ck_banner: "Dashboard banner",
    ck_audience: "Sent to",
    ck_source: "Comes from",
    ck_source_call: "An automation or script",
    ck_time: "At",
    ck_home: "At home",
    ck_ack: "Acknowledged after (minutes, empty: never)",
    ck_run: "Check",
    ck_first: "At once",
    ck_later: "Later",
    ck_nothing: "Nothing is delivered.",
    r_sent: "sent",
    r_quiet: "sent quietly",
    r_held: "held",
    r_held_until: "held until {time}",
    r_skipped: "skipped",
    r_failed: "fails",
    r_by: "by {policy}",
    r_through: "let through by {names}",
    r_via: "added by {policy}",
    ck_band_off: "{names} would let it through, but is switched off.",
    ck_summary: "Collected for the summary of {policy}.",
    ck_waits: "waits for its Only if",
    help_button: "How policies work together",
    s_applies_manual: "Calls that name this policy",
    s_applies: "Messages with {parts}",
    s_severity: "severity {severities}",
    s_tag: "tag {tags}",
    s_and: " and ",
    s_escalation: "{applies}: if nobody acknowledges within {n} min, it is also sent on {channels}.",
    s_reminder: "{applies}: while nobody acknowledges, the notification is repeated every {n} min, at most {m} times{channels}.",
    s_quiet_hours: "{applies}: between {from} and {to}{days}, deliveries outside the dashboard are {action}.",
    s_away: "{applies}: a person who is not home gets it when they arrive{wait}.",
    s_presence_people: "{who} who {where} {zone}: push, popup and mail are {then}",
    s_presence_speak: "speech while {who} of {audience} is in {zone} is {then}",
    w_recipient: "a recipient",
    w_in: "is in",
    w_not_in: "is not in",
    t_hold: "held until that changes",
    t_drop: "dropped",
    aw_send: ", then sent anyway",
    aw_drop: ", then dropped",
    everyone: "everyone",
    nobody: "nobody",
    somebody: "somebody",
    presence_channels: "Channels it covers (none selected: push, popup, mail)",
    zone: "Zone",
    presence_when: "Push, popup, mail: when the recipient",
    household_who: "Speech: when",
    household_audience: "of this audience is in the zone",
    presence_then: "Then",
    after_wait: "When the wait ends",
    max_wait_presence: "Wait at most (minutes, 0: as long as the message lives)",
    hint_odd: "Speech is then said only once nobody of this audience is in the zone.",
    when_opts: {"not_in": "is not in the zone", "in": "is in the zone"},
    who_opts: {"nobody": "nobody", "somebody": "somebody"},
    then_opts: {"hold": "Hold until that changes", "drop": "Drop"},
    after_opts: {"send": "Send anyway", "drop": "Drop"},
    s_deliver: "{applies}: it is also sent at once on {channels}.",
    s_fallback: "{applies}: if {when}, it is sent on {channels} instead.",
    s_summarize_every: "{applies}: held, and one summary is sent {n} min after the first held message.",
    s_summarize_at: "{applies}: held, and one summary is sent every day at {time}.",
    s_in_channels: ", only on {channels}",
    s_days: " on {days}",
    quiet_entity: "Or quiet while this is on",
    quiet_entity_none: "No entity: use the times",
    quiet_entity_hint: "A schedule, input boolean or binary sensor. While it is on, the times are not used. Held messages go out when it turns off; a missing or unavailable entity is not quiet.",
    s_quiet_entity: "{applies}: while {entity} is on, deliveries outside the dashboard are {action}.",
    s_wait: ", for at most {n} min",
    a_quiet: "sent quietly",
    a_wait: "held until the end",
    a_drop: "dropped",
    w_no_audience: "the audience is empty",
    w_failed: "delivery fails",
    w_both: "the audience is empty or delivery fails",
  },
  de: {
    title: "Richtlinien",
    intro: "Richtlinien entscheiden, wann eine Meldung Leute erreichen darf, wer sie noch bekommt und wie oft. Jede Richtlinie, die auf eine Meldung passt, wirkt; es gibt keine Reihenfolge.",
    none: "Du hast noch keine Richtlinien. Die Einführung (Einstellungen, Einführung neu starten) bietet einen Grundstock an.",
    new: "Neue Richtlinie",
    editing: "Richtlinie bearbeiten",
    type: "Art",
    types: TYPE_NAMES.de,
    disabled: "deaktiviert",
    applies: "Gilt für",
    severities: "Schweregrade (keiner gewählt: alle)",
    tags: "Tags, durch Komma getrennt (leer: alle)",
    severity_names: { passive: "Passiv", info: "Info", warning: "Warnung", critical: "Kritisch" },
    channel_names: { push: "Push", popup: "Popup", speak: "Sprache", persistent: "Persistente Benachrichtigung", mail: "E-Mail" },
    after: "Eskalieren nach (Minuten)",
    channels: "Kanäle",
    channels_reminder: "Auf diese Kanäle beschränken (keiner gewählt: alle)",
    dismiss_acks: "Ausblenden zählt als Bestätigung",
    every: "Wiederholen alle (Minuten)",
    max_count: "Höchstens so viele Erinnerungen",
    from: "Ruhe ab",
    to: "Ruhe bis",
    days: "Tage (keiner gewählt: jeden Tag)",
    days_names: DAY_NAMES.de,
    action: "Während der Ruhezeit",
    actions: ACTIONS.de,
    entity_id: "Entitäts-ID des Schalters",
    entity_id_new: "Home Assistant legt beim Speichern diesen Schalter für die Richtlinie an. Nenne die Richtlinie im Feld policy eines Aufrufs mit dieser ID: Sie gilt weiter, wenn du die Richtlinie umbenennst.",
    entity_id_own: "Eine Umbenennung ändert diese ID nicht. Ein Aufruf, der die Richtlinie mit ihrem Namen nennt, funktioniert nach einer Umbenennung nicht mehr; ein Aufruf mit dieser ID schon.",
    max_wait: "Auf Ankunft warten (Minuten, 0: solange die Meldung besteht)",
    when: "Verwenden, wenn",
    whens: WHENS.de,
    channels_from: "Kanäle stammen aus",
    targets_from: "Empfänger stammen aus",
    cf: { policy: "Diese Richtlinie (die Kanäle unten)", call: "Der Aufruf (dieselben Kanäle)", failed: "Der Aufruf, nur die Kanäle, die niemanden erreicht haben" },
    tf: { policy: "Diese Richtlinie (die Empfänger unten)", call: "Der Aufruf (dieselben Empfänger)" },
    people_target: "Personen: Push, Popup und E-Mail",
    speakers_target: "Lautsprecher: Sprache",
    tf_call_hint: "Die Personen und Lautsprecher, die der Aufruf nannte, erhalten es auf den Kanälen oben.",
    same_empty: "Der Aufruf hat niemanden erreicht, weil die Zielgruppe leer war; dieselben Empfänger sind also auch leer. Nimm Zustellung fehlgeschlagen oder gib andere Empfänger an.",
    s_channels_call: "den Kanälen des Aufrufs",
    s_channels_failed: "den Kanälen des Aufrufs, die niemanden erreicht haben",
    s_recipients_call: " Die Empfänger sind die, die der Aufruf nannte.",
    s_recipients_policy: " Es geht an {who}.",
    summary_mode: "Zusammenfassung senden",
    summary_every_mode: "Alle N Minuten",
    summary_at_mode: "Zu einer Uhrzeit",
    summary_every: "Minuten nach der ersten zurückgehaltenen Meldung",
    summary_at: "Uhrzeit",
    summarize_note: "Solange eine Meldung wartet, wird nichts einzeln gesendet. Die Zusammenfassung zeigt die Anzahl und die Titel, markiert erledigte und kürzt bei 10 („und N weitere“).",
    ack_note: "Pushes von Meldungen, die diese Richtlinie abdeckt, bekommen eine Schaltfläche Bestätigen.",
    target_channel: "Kanal {channel}",
    target_audience: "Zielgruppe",
    target_recipients: "Empfänger",
    target_persistent: "Kein Ziel: geht an alle.",
    sentence: "In Worten",
    s_applies_any: "Jede Meldung",
    enabled_hint: "Eine deaktivierte Richtlinie wird nie genutzt, auch nicht, wenn ein Aufruf sie nennt.",
    sec_when: "Welche Meldungen",
    sec_does: "Was sie tut",
    type_desc: {"get_through": "Lässt die passenden Meldungen für die erfassten Leute an Ruhezeit und Zusammenfassung vorbei. Sendet selbst nichts; kombiniere sie mit Zustellen.", "escalation": "Bestätigt niemand innerhalb der Zeit, wird die Meldung zusätzlich auf den gewählten Kanälen und an die gewählten Ziele zugestellt.", "reminder": "Solange niemand bestätigt, wird die Meldung in einem Abstand wiederholt, höchstens so oft wie eingestellt.", "quiet_hours": "Zwischen zwei Uhrzeiten werden Zustellungen außerhalb des Dashboards leise gesendet, bis zum Ende zurückgehalten oder verworfen.", "presence": "Hält eine Zustellung zurück oder verwirft sie, je nachdem wo Personen sind: für jeden Empfänger bei Push, Popup und Mail, für den Haushalt bei Lautsprechern.", "fallback": "Hat die erste Zustellung niemanden erreicht, wird die Meldung anderswo zugestellt: auf anderen Kanälen oder an andere Personen auf denselben Kanälen.", "summarize": "Passende Meldungen werden auf jedem Kanal zurückgehalten, auch im Banner, und stattdessen wird eine Zusammenfassung gesendet.", "deliver": "Passende Meldungen werden zusätzlich sofort an die gewählte Zielgruppe auf den gewählten Kanälen zugestellt."},
    apply_label: "Gilt für Meldungen",
    apply_auto: "Automatisch",
    apply_auto_hint: "Jede Meldung, deren Schweregrad und Tag passen, bekommt diese Richtlinie. Eine leere Liste passt auf alles.",
    apply_manual: "Manuell",
    apply_manual_hint: "Nur ein Aufruf, der diese Richtlinie nennt, bekommt sie. Schweregrad und Tag der Meldung spielen keine Rolle.",
    manual_how: "In einem Aufruf nennen:",
    manual_note: "Ein Aufruf, der eine Richtlinie nennt, nutzt nur diese, nicht die automatischen. policy: none schaltet alle Richtlinien für einen Aufruf ab.",
    badge_manual: "manuell",
    lane_calm: "Für Ruhe sorgen",
    lane_calm_hint: "Diese wirken auf jede Zustellung, auch auf das, was die andere Spur ergänzt. Sind sich zwei uneinig, zählt die ruhigere. Wiederholungen warten nie: sie fallen aus.",
    band: "Kommt immer durch",
    band_hint: "Diese Meldungen werden nie gesammelt, und die Ruhezeit gilt nicht für die erfassten Leute. Die Anwesenheit entscheidet weiter danach, wo Leute sind.",
    lane_arrive: "Damit es ankommt",
    lane_arrive_hint: "Jede passende sendende Richtlinie läuft. Eskalationen und Erinnerungen zählen ab dem Erstellen der Meldung.",
    lane_named: "Nur wenn genannt",
    lane_named_hint: "Diese wirken nur, wenn ein Aufruf oder eine Überwachungsregel sie mit ihrer Entitäts-ID nennt.",
    not_severities: "Nicht für Stufen",
    not_tags: "Nicht für Tags, durch Komma getrennt",
    rules: "Von Überwachungsregel (keine gewählt: jede Quelle)",
    only_if: "Nur wenn",
    only_if_hint: "Die Richtlinie wirkt nur, solange das gilt. Unbekannt zählt als das, was mehr zustellt.",
    oi_entity: "Entität",
    oi_state: "Zustand",
    oi_none: "Immer (keine Bedingung)",
    faster: "Öfter, solange",
    faster_every: "Dann alle (Minuten) wiederholen",
    alongside: "Läuft neben anderen Erinnerungen",
    alongside_hint: "Aus: Erinnerungen auf demselben Kanal teilen sich den kürzesten Rhythmus, jede mit eigener Zählung.",
    holds_anyway: "Hält sie trotzdem",
    holds_anyway_hint: "Kein Eintrag von Kommt immer durch lässt Meldungen an dieser Richtlinie vorbei.",
    covers: "Gilt für",
    covers_everyone: "Alle, die sie erreicht",
    covers_only: "Nur diese",
    covers_audiences: "Zielgruppen",
    covers_recipients: "Personen und Lautsprecher",
    s_through: "{applies}: darf {who} trotz Ruhezeit und Zusammenfassung wecken.",
    s_through_everyone: "alle, die sie erreicht",
    s_not_for: " Nicht für {list}.",
    s_only_if: " Nur solange {entity} {state} ist.",
    s_faster: " Solange {entity} {state} ist: alle {n} Min.",
    s_alongside: " Läuft neben anderen Erinnerungen.",
    s_holds_anyway: " Kein Eintrag von Kommt immer durch kommt vorbei.",
    s_rules: " Nur Meldungen der Überwachungsregeln {names}.",
    links_note: "Wirkt nur auf Meldungen, die {names} nicht übernehmen, wie in 1.x.",
    overlap_calm: "Wo sie und {names} beide passen, zählt die ruhigere.",
    overlap_send: "Wirkt auch auf dieselben Meldungen: {names}.",
    cl_title: "Nach dem Update prüfen",
    cl_intro: "Das Update hat beibehalten, was deine Richtlinien taten. Diese Richtlinien arbeiten jetzt anders oder wirken nie; entscheide für jede.",
    cl_links: "{name} wirkt nur auf Meldungen, die {names} nicht übernehmen, wie bisher.",
    cl_never: "{name} wirkt nie: {names} übernehmen alle ihre Meldungen zuerst.",
    cl_holds: "{name} hält auch kritische Meldungen zurück, wie bisher.",
    cl_keep: "Wie bisher lassen",
    cl_act: "Wirken lassen",
    cl_through: "Kritisch durchlassen",
    cl_dismiss: "Liste ausblenden",
    cl_kept: "beibehalten",
    cl_changed: "geändert",
    ck_title: "Was passiert mit einer Meldung?",
    ck_intro: "Es wird nichts gesendet. Die Antwort nutzt die Richtlinien, wie sie jetzt sind.",
    ck_severity: "Stufe",
    ck_tag: "Tag",
    ck_channels: "Kanäle",
    ck_banner: "Dashboard-Banner",
    ck_audience: "Gesendet an",
    ck_source: "Kommt von",
    ck_source_call: "Einer Automation oder einem Skript",
    ck_time: "Um",
    ck_home: "Zu Hause",
    ck_ack: "Bestätigt nach (Minuten, leer: nie)",
    ck_run: "Prüfen",
    ck_first: "Sofort",
    ck_later: "Später",
    ck_nothing: "Nichts wird zugestellt.",
    r_sent: "gesendet",
    r_quiet: "leise gesendet",
    r_held: "zurückgehalten",
    r_held_until: "zurückgehalten bis {time}",
    r_skipped: "übersprungen",
    r_failed: "schlägt fehl",
    r_by: "durch {policy}",
    r_through: "durchgelassen von {names}",
    r_via: "ergänzt von {policy}",
    ck_band_off: "{names} würde sie durchlassen, ist aber ausgeschaltet.",
    ck_summary: "Gesammelt für die Zusammenfassung von {policy}.",
    ck_waits: "wartet auf ihr Nur wenn",
    help_button: "Wie Richtlinien zusammenwirken",
    s_applies_manual: "Aufrufe, die diese Richtlinie nennen",
    s_applies: "Meldungen mit {parts}",
    s_severity: "Schweregrad {severities}",
    s_tag: "Tag {tags}",
    s_and: " und ",
    s_escalation: "{applies}: bestätigt niemand innerhalb von {n} Min., wird zusätzlich auf {channels} gesendet.",
    s_reminder: "{applies}: solange niemand bestätigt, wird die Benachrichtigung alle {n} Min. wiederholt, höchstens {m} Mal{channels}.",
    s_quiet_hours: "{applies}: zwischen {from} und {to}{days} werden Zustellungen außerhalb des Dashboards {action}.",
    s_away: "{applies}: wer nicht zu Hause ist, bekommt sie bei der Ankunft{wait}.",
    s_presence_people: "{who}, der {where} {zone} ist: Push, Popup und Mail werden {then}",
    s_presence_speak: "Sprache, solange {who} von {audience} in {zone} ist, wird {then}",
    w_recipient: "Ein Empfänger",
    w_in: "in",
    w_not_in: "nicht in",
    t_hold: "zurückgehalten, bis sich das ändert",
    t_drop: "verworfen",
    aw_send: ", dann trotzdem gesendet",
    aw_drop: ", dann verworfen",
    everyone: "allen",
    nobody: "niemand",
    somebody: "jemand",
    presence_channels: "Abgedeckte Kanäle (keiner gewählt: Push, Popup, Mail)",
    zone: "Zone",
    presence_when: "Push, Popup, Mail: wenn der Empfänger",
    household_who: "Sprache: wenn",
    household_audience: "dieser Zielgruppe in der Zone ist",
    presence_then: "Dann",
    after_wait: "Wenn die Wartezeit endet",
    max_wait_presence: "Höchstens warten (Minuten, 0: solange die Meldung besteht)",
    hint_odd: "Sprache wird dann erst gesagt, wenn niemand dieser Zielgruppe in der Zone ist.",
    when_opts: {"not_in": "nicht in der Zone ist", "in": "in der Zone ist"},
    who_opts: {"nobody": "niemand", "somebody": "jemand"},
    then_opts: {"hold": "Zurückhalten, bis sich das ändert", "drop": "Verwerfen"},
    after_opts: {"send": "Trotzdem senden", "drop": "Verwerfen"},
    s_deliver: "{applies}: wird zusätzlich sofort auf {channels} gesendet.",
    s_fallback: "{applies}: wenn {when}, wird stattdessen auf {channels} gesendet.",
    s_summarize_every: "{applies}: zurückgehalten, und eine Zusammenfassung wird {n} Min. nach der ersten zurückgehaltenen Meldung gesendet.",
    s_summarize_at: "{applies}: zurückgehalten, und eine Zusammenfassung wird jeden Tag um {time} gesendet.",
    s_in_channels: ", nur auf {channels}",
    s_days: " an {days}",
    quiet_entity: "Oder ruhig, solange dies an ist",
    quiet_entity_none: "Keine Entität: Uhrzeiten verwenden",
    quiet_entity_hint: "Ein Zeitplan, ein Eingabe-Schalter oder ein binärer Sensor. Solange er an ist, gelten die Uhrzeiten nicht. Zurückgehaltene Meldungen gehen raus, wenn er aus geht; eine fehlende oder nicht verfügbare Entität ist nicht ruhig.",
    s_quiet_entity: "{applies}: solange {entity} an ist, werden Zustellungen außerhalb des Dashboards {action}.",
    s_wait: ", höchstens {n} Min.",
    a_quiet: "leise gesendet",
    a_wait: "bis zum Ende zurückgehalten",
    a_drop: "verworfen",
    w_no_audience: "die Zielgruppe leer ist",
    w_failed: "die Zustellung fehlschlägt",
    w_both: "die Zielgruppe leer ist oder die Zustellung fehlschlägt",
  },
  fr: {
    title: "Politiques",
    intro: "Les règles décident quand un message peut joindre les gens, qui d'autre le reçoit et à quelle fréquence. Chaque règle qui correspond à un message agit ; il n'y a pas d'ordre.",
    none: "Vous n'avez pas encore de politique. L'introduction (Réglages, Relancer l'introduction) propose un jeu de départ.",
    new: "Nouvelle politique",
    editing: "Modifier la politique",
    type: "Type",
    types: TYPE_NAMES.fr,
    disabled: "désactivée",
    applies: "S'applique à",
    severities: "Gravités (aucune choisie : toutes)",
    tags: "Étiquettes, séparées par des virgules (vide : toutes)",
    severity_names: { passive: "Passif", info: "Info", warning: "Avertissement", critical: "Critique" },
    channel_names: { push: "Push", popup: "Fenêtre", speak: "Voix", persistent: "Notification persistante", mail: "Courriel" },
    after: "Escalader après (minutes)",
    channels: "Canaux",
    channels_reminder: "Limiter à ces canaux (aucun choisi : tous)",
    dismiss_acks: "Masquer vaut acquittement",
    every: "Répéter toutes les (minutes)",
    max_count: "Au plus ce nombre de rappels",
    from: "Calme de",
    to: "Calme jusqu'à",
    days: "Jours (aucun choisi : tous les jours)",
    days_names: DAY_NAMES.fr,
    action: "Pendant les heures calmes",
    actions: ACTIONS.fr,
    entity_id: "ID d'entité du commutateur",
    entity_id_new: "Home Assistant crée ce commutateur pour la politique à l'enregistrement. Nommez la politique dans le champ policy d'un appel par cet ID : il reste valable si vous renommez la politique.",
    entity_id_own: "Renommer ne change pas cet ID. Un appel qui désigne la politique par son nom cesse de fonctionner après un renommage ; un appel qui utilise cet ID continue de fonctionner.",
    max_wait: "Attendre l'arrivée (minutes, 0 : tant que le message existe)",
    when: "Utiliser quand",
    whens: WHENS.fr,
    channels_from: "Les canaux viennent de",
    targets_from: "Les destinataires viennent de",
    cf: { policy: "Cette politique (les canaux ci-dessous)", call: "L'appel (les mêmes canaux)", failed: "L'appel, seulement les canaux qui n'ont atteint personne" },
    tf: { policy: "Cette politique (les destinataires ci-dessous)", call: "L'appel (les mêmes destinataires)" },
    people_target: "Personnes : push, fenêtre et courriel",
    speakers_target: "Haut-parleurs : voix",
    tf_call_hint: "Les personnes et haut-parleurs que l'appel a nommés le reçoivent sur les canaux ci-dessus.",
    same_empty: "L'appel n'a atteint personne parce que l'audience était vide ; les mêmes destinataires sont donc vides aussi. Utilisez Échec de l'envoi, ou donnez d'autres destinataires.",
    s_channels_call: "les canaux de l'appel",
    s_channels_failed: "les canaux de l'appel qui n'ont atteint personne",
    s_recipients_call: " Les destinataires sont ceux que l'appel a nommés.",
    s_recipients_policy: " Il est envoyé à {who}.",
    summary_mode: "Envoyer le résumé",
    summary_every_mode: "Toutes les N minutes",
    summary_at_mode: "À une heure du jour",
    summary_every: "Minutes après le premier message retenu",
    summary_at: "Heure",
    summarize_note: "Rien n'est envoyé individuellement tant qu'un message attend. Le résumé montre le nombre et les titres, marque les messages résolus et s'arrête à 10 (« et N autres »).",
    ack_note: "Les push des messages que cette politique couvre ont un bouton Confirmer.",
    target_channel: "Canal {channel}",
    target_audience: "Audience",
    target_recipients: "Destinataires",
    target_persistent: "Pas de cible : va à tout le monde.",
    sentence: "En clair",
    s_applies_any: "Tout message",
    enabled_hint: "Une politique désactivée n'est jamais utilisée, même si un appel la nomme.",
    sec_when: "Quels messages",
    sec_does: "Ce qu'elle fait",
    type_desc: {"get_through": "Fait passer les messages qu'elle concerne au-delà des heures calmes et des résumés pour les personnes concernées. N'envoie rien elle-même ; combinez-la avec Livrer.", "escalation": "Si personne ne confirme dans le délai, le message est aussi remis sur les canaux et aux cibles que vous choisissez.", "reminder": "Tant que personne ne confirme, le message est répété à intervalle régulier, jusqu'à un maximum.", "quiet_hours": "Entre deux heures de la journée, les remises hors tableau de bord sont envoyées discrètement, retenues jusqu'à la fin ou abandonnées.", "presence": "Retient ou abandonne une livraison selon où se trouvent les personnes : pour chaque destinataire sur push, popup et courriel, pour le foyer sur les haut-parleurs.", "fallback": "Si la première remise n'a joint personne, le message est remis ailleurs : sur d'autres canaux, ou à d'autres personnes sur les mêmes canaux.", "summarize": "Les messages correspondants sont retenus sur chaque canal, bannière comprise, et un seul résumé est envoyé à la place.", "deliver": "Les messages correspondants sont aussi remis tout de suite à l'audience et sur les canaux que vous choisissez."},
    apply_label: "S'applique aux messages",
    apply_auto: "Automatiquement",
    apply_auto_hint: "Chaque message dont la gravité et l'étiquette correspondent reçoit cette politique. Une liste vide correspond à tout.",
    apply_manual: "Manuellement",
    apply_manual_hint: "Seul un appel qui nomme cette politique la reçoit. La gravité et l'étiquette du message n'ont pas d'importance.",
    manual_how: "La nommer dans un appel :",
    manual_note: "Un appel qui nomme une politique n'utilise que celle-là, pas les automatiques. policy: none désactive toutes les politiques pour un appel.",
    badge_manual: "manuelle",
    lane_calm: "Garder le calme",
    lane_calm_hint: "Elles agissent sur chaque envoi, aussi sur ce que l'autre voie ajoute. Quand deux divergent, la plus calme compte. Les répétitions n'attendent jamais : elles sont ignorées.",
    band: "Passe toujours",
    band_hint: "Ces messages ne sont jamais résumés, et les heures calmes ne s'appliquent pas aux personnes concernées. La présence décide toujours selon où sont les gens.",
    lane_arrive: "S'assurer qu'il arrive",
    lane_arrive_hint: "Chaque règle d'envoi qui correspond s'exécute. Les escalades et les rappels comptent depuis la création du message.",
    lane_named: "Seulement si nommée",
    lane_named_hint: "Elles n'agissent que si un appel ou une règle de surveillance les nomme par leur ID d'entité.",
    not_severities: "Sauf pour les niveaux",
    not_tags: "Sauf pour les étiquettes, séparées par des virgules",
    rules: "Depuis la règle de surveillance (aucune : toute source)",
    only_if: "Seulement si",
    only_if_hint: "La règle n'agit que tant que c'est vrai. Inconnu compte comme ce qui livre davantage.",
    oi_entity: "Entité",
    oi_state: "État",
    oi_none: "Toujours (sans condition)",
    faster: "Plus souvent tant que",
    faster_every: "Puis répéter toutes les (minutes)",
    alongside: "Fonctionne à côté des autres rappels",
    alongside_hint: "Désactivé : les rappels d'un même canal partagent le rythme le plus court, chacun avec son propre compte.",
    holds_anyway: "Les retient quand même",
    holds_anyway_hint: "Aucune entrée Passe toujours ne fait passer les messages au-delà de cette règle.",
    covers: "Concerne",
    covers_everyone: "Tous ceux qu'il atteint",
    covers_only: "Seulement ceux-ci",
    covers_audiences: "Audiences",
    covers_recipients: "Personnes et haut-parleurs",
    s_through: "{applies} : peut réveiller {who} malgré les heures calmes et les résumés.",
    s_through_everyone: "tous ceux qu'il atteint",
    s_not_for: " Sauf pour {list}.",
    s_only_if: " Seulement tant que {entity} est {state}.",
    s_faster: " Tant que {entity} est {state} : toutes les {n} min.",
    s_alongside: " Fonctionne à côté des autres rappels.",
    s_holds_anyway: " Aucune entrée Passe toujours ne passe.",
    s_rules: " Seulement les messages des règles de surveillance {names}.",
    links_note: "N'agit que sur les messages que {names} ne prennent pas, comme en 1.x.",
    overlap_calm: "Là où elle et {names} correspondent toutes deux, la plus calme compte.",
    overlap_send: "Agit aussi sur les mêmes messages : {names}.",
    cl_title: "À vérifier après la mise à jour",
    cl_intro: "La mise à jour a gardé ce que faisaient vos règles. Ces règles fonctionnent désormais autrement ou n'agissent jamais ; choisissez pour chacune.",
    cl_links: "{name} n'agit que sur les messages que {names} ne prennent pas, comme avant.",
    cl_never: "{name} n'agit jamais : {names} prennent tous ses messages d'abord.",
    cl_holds: "{name} retient aussi les messages critiques, comme avant.",
    cl_keep: "Garder comme avant",
    cl_act: "La laisser agir",
    cl_through: "Laisser passer Critique",
    cl_dismiss: "Masquer la liste",
    cl_kept: "gardé",
    cl_changed: "modifié",
    ck_title: "Que devient un message ?",
    ck_intro: "Rien n'est envoyé. La réponse utilise les règles telles qu'elles sont maintenant.",
    ck_severity: "Niveau",
    ck_tag: "Étiquette",
    ck_channels: "Canaux",
    ck_banner: "Bannière du tableau de bord",
    ck_audience: "Envoyé à",
    ck_source: "Vient de",
    ck_source_call: "Une automatisation ou un script",
    ck_time: "À",
    ck_home: "À la maison",
    ck_ack: "Confirmé après (minutes, vide : jamais)",
    ck_run: "Vérifier",
    ck_first: "Tout de suite",
    ck_later: "Plus tard",
    ck_nothing: "Rien n'est livré.",
    r_sent: "envoyé",
    r_quiet: "envoyé discrètement",
    r_held: "retenu",
    r_held_until: "retenu jusqu'à {time}",
    r_skipped: "ignoré",
    r_failed: "échoue",
    r_by: "par {policy}",
    r_through: "laissé passer par {names}",
    r_via: "ajouté par {policy}",
    ck_band_off: "{names} le laisserait passer, mais est désactivée.",
    ck_summary: "Collecté pour le résumé de {policy}.",
    ck_waits: "attend son Seulement si",
    help_button: "Comment les règles agissent ensemble",
    s_applies_manual: "Appels qui nomment cette politique",
    s_applies: "Messages avec {parts}",
    s_severity: "la gravité {severities}",
    s_tag: "l'étiquette {tags}",
    s_and: " et ",
    s_escalation: "{applies} : si personne ne confirme en {n} min, il est aussi envoyé sur {channels}.",
    s_reminder: "{applies} : tant que personne ne confirme, la notification est répétée toutes les {n} min, au plus {m} fois{channels}.",
    s_quiet_hours: "{applies} : entre {from} et {to}{days}, les livraisons hors tableau de bord sont {action}.",
    s_away: "{applies} : une personne qui n'est pas à la maison le reçoit à son arrivée{wait}.",
    s_presence_people: "{who} qui {where} {zone} : push, popup et courriel sont {then}",
    s_presence_speak: "la voix, tant que {who} de {audience} est dans {zone}, est {then}",
    w_recipient: "Un destinataire",
    w_in: "est dans",
    w_not_in: "n'est pas dans",
    t_hold: "retenus jusqu'à ce que cela change",
    t_drop: "abandonnés",
    aw_send: ", puis envoyés quand même",
    aw_drop: ", puis abandonnés",
    everyone: "tout le monde",
    nobody: "personne",
    somebody: "quelqu'un",
    presence_channels: "Canaux couverts (aucun choisi : push, popup, courriel)",
    zone: "Zone",
    presence_when: "Push, popup, courriel : quand le destinataire",
    household_who: "Voix : quand",
    household_audience: "de cette audience est dans la zone",
    presence_then: "Ensuite",
    after_wait: "À la fin de l'attente",
    max_wait_presence: "Attendre au plus (minutes, 0 : tant que le message existe)",
    hint_odd: "La voix n'est alors dite que lorsque personne de cette audience n'est dans la zone.",
    when_opts: {"not_in": "n'est pas dans la zone", "in": "est dans la zone"},
    who_opts: {"nobody": "personne", "somebody": "quelqu'un"},
    then_opts: {"hold": "Retenir jusqu'à ce que cela change", "drop": "Abandonner"},
    after_opts: {"send": "Envoyer quand même", "drop": "Abandonner"},
    s_deliver: "{applies} : il est aussi envoyé tout de suite sur {channels}.",
    s_fallback: "{applies} : si {when}, il est envoyé sur {channels} à la place.",
    s_summarize_every: "{applies} : retenu, et un résumé est envoyé {n} min après le premier message retenu.",
    s_summarize_at: "{applies} : retenu, et un résumé est envoyé chaque jour à {time}.",
    s_in_channels: ", seulement sur {channels}",
    s_days: " le {days}",
    quiet_entity: "Ou calme tant que ceci est allumé",
    quiet_entity_none: "Aucune entité : utiliser les heures",
    quiet_entity_hint: "Un planning, un interrupteur d'entrée ou un capteur binaire. Tant qu'il est allumé, les heures ne servent pas. Les messages retenus partent quand il s'éteint ; une entité absente ou indisponible n'est pas calme.",
    s_quiet_entity: "{applies} : tant que {entity} est allumé, les livraisons hors tableau de bord sont {action}.",
    s_wait: ", au plus {n} min",
    a_quiet: "envoyées discrètement",
    a_wait: "retenues jusqu'à la fin",
    a_drop: "abandonnées",
    w_no_audience: "l'audience est vide",
    w_failed: "la livraison échoue",
    w_both: "l'audience est vide ou la livraison échoue",
  },
  es: {
    title: "Políticas",
    intro: "Las reglas deciden cuándo un mensaje puede llegar a la gente, quién más lo recibe y con qué frecuencia. Cada regla que encaja con un mensaje actúa; no hay orden.",
    none: "Aún no tienes políticas. La introducción (Ajustes, Reiniciar la introducción) ofrece un conjunto inicial.",
    new: "Nueva política",
    editing: "Editar política",
    type: "Tipo",
    types: TYPE_NAMES.es,
    disabled: "desactivada",
    applies: "Se aplica a",
    severities: "Gravedades (ninguna elegida: todas)",
    tags: "Etiquetas, separadas por comas (vacío: todas)",
    severity_names: { passive: "Pasivo", info: "Info", warning: "Aviso", critical: "Crítico" },
    channel_names: { push: "Push", popup: "Ventana", speak: "Voz", persistent: "Notificación persistente", mail: "Correo" },
    after: "Escalar tras (minutos)",
    channels: "Canales",
    channels_reminder: "Limitar a estos canales (ninguno elegido: todos)",
    dismiss_acks: "Descartar cuenta como confirmar",
    every: "Repetir cada (minutos)",
    max_count: "Como máximo este número de recordatorios",
    from: "Silencio desde",
    to: "Silencio hasta",
    days: "Días (ninguno elegido: todos los días)",
    days_names: DAY_NAMES.es,
    action: "Durante las horas de silencio",
    actions: ACTIONS.es,
    entity_id: "ID de entidad del interruptor",
    entity_id_new: "Home Assistant crea este interruptor para la política al guardar. Nombra la política en el campo policy de una llamada con este ID: sigue valiendo si renombras la política.",
    entity_id_own: "Renombrar no cambia este ID. Una llamada que nombra la política por su texto deja de funcionar tras renombrarla; una que usa este ID sigue funcionando.",
    max_wait: "Esperar la llegada (minutos, 0: mientras exista el mensaje)",
    when: "Usar cuando",
    whens: WHENS.es,
    channels_from: "Los canales vienen de",
    targets_from: "Los destinatarios vienen de",
    cf: { policy: "Esta política (los canales de abajo)", call: "La llamada (los mismos canales)", failed: "La llamada, solo los canales que no llegaron a nadie" },
    tf: { policy: "Esta política (los destinatarios de abajo)", call: "La llamada (los mismos destinatarios)" },
    people_target: "Personas: push, ventana y correo",
    speakers_target: "Altavoces: voz",
    tf_call_hint: "Las personas y altavoces que nombró la llamada lo reciben por los canales de arriba.",
    same_empty: "La llamada no llegó a nadie porque la audiencia estaba vacía, así que los mismos destinatarios también están vacíos. Usa Falló el envío o indica otros destinatarios.",
    s_channels_call: "los canales de la llamada",
    s_channels_failed: "los canales de la llamada que no llegaron a nadie",
    s_recipients_call: " Los destinatarios son los que nombró la llamada.",
    s_recipients_policy: " Se envía a {who}.",
    summary_mode: "Enviar el resumen",
    summary_every_mode: "Cada N minutos",
    summary_at_mode: "A una hora del día",
    summary_every: "Minutos tras el primer mensaje retenido",
    summary_at: "Hora",
    summarize_note: "No se envía nada por separado mientras un mensaje espera. El resumen muestra el número y los títulos, marca los resueltos y corta en 10 («y N más»).",
    ack_note: "Los push de los mensajes que cubre esta política tienen un botón Confirmar.",
    target_channel: "Canal {channel}",
    target_audience: "Audiencia",
    target_recipients: "Destinatarios",
    target_persistent: "Sin destino: va a todos.",
    sentence: "En palabras",
    s_applies_any: "Todos los mensajes",
    enabled_hint: "Una política desactivada nunca se usa, ni siquiera si una llamada la nombra.",
    sec_when: "Qué mensajes",
    sec_does: "Qué hace",
    type_desc: {"get_through": "Deja pasar los mensajes que encaja más allá de las horas de silencio y los resúmenes para las personas afectadas. No envía nada; combínala con Entregar.", "escalation": "Si nadie confirma en el tiempo, el mensaje se entrega también por los canales y a los destinos que elijas.", "reminder": "Mientras nadie confirma, el mensaje se repite a intervalos, hasta un máximo.", "quiet_hours": "Entre dos horas del día, las entregas fuera del panel se envían en silencio, se retienen hasta el final o se descartan.", "presence": "Retiene o descarta una entrega según dónde está la gente: para cada destinatario en push, ventana y correo, para el hogar en los altavoces.", "fallback": "Si la primera entrega no llegó a nadie, el mensaje se entrega en otro sitio: por otros canales o a otras personas por los mismos canales.", "summarize": "Los mensajes que coinciden se retienen en todos los canales, el aviso incluido, y se envía un solo resumen.", "deliver": "Los mensajes que coinciden también se entregan al instante a la audiencia y por los canales que elijas."},
    apply_label: "Se aplica a los mensajes",
    apply_auto: "Automáticamente",
    apply_auto_hint: "Cada mensaje cuya gravedad y etiqueta coinciden recibe esta política. Una lista vacía coincide con todo.",
    apply_manual: "Manualmente",
    apply_manual_hint: "Solo una llamada que nombra esta política la recibe. La gravedad y la etiqueta del mensaje no importan.",
    manual_how: "Nómbrala en una llamada:",
    manual_note: "Una llamada que nombra una política usa solo esa, no las automáticas. policy: none desactiva todas las políticas para una llamada.",
    badge_manual: "manual",
    lane_calm: "Mantener la calma",
    lane_calm_hint: "Actúan en cada envío, también en lo que añade la otra vía. Cuando dos discrepan, cuenta la más tranquila. Las repeticiones nunca esperan: se omiten.",
    band: "Siempre pasa",
    band_hint: "Estos mensajes nunca se resumen y las horas de silencio no se aplican a las personas afectadas. La presencia sigue decidiendo según dónde está la gente.",
    lane_arrive: "Asegurar que llegue",
    lane_arrive_hint: "Se ejecuta cada regla de envío que encaja. Los escalados y recordatorios cuentan desde la creación del mensaje.",
    lane_named: "Solo si se nombra",
    lane_named_hint: "Solo actúan cuando una llamada o una regla de vigilancia las nombra por su ID de entidad.",
    not_severities: "Excepto niveles",
    not_tags: "Excepto etiquetas, separadas por comas",
    rules: "Desde la regla de vigilancia (ninguna: cualquier origen)",
    only_if: "Solo si",
    only_if_hint: "La regla solo actúa mientras se cumple. Desconocido cuenta como lo que entrega más.",
    oi_entity: "Entidad",
    oi_state: "Estado",
    oi_none: "Siempre (sin condición)",
    faster: "Más a menudo mientras",
    faster_every: "Entonces repetir cada (minutos)",
    alongside: "Funciona junto a otros recordatorios",
    alongside_hint: "Desactivado: los recordatorios de un mismo canal comparten el ritmo más corto, cada uno con su propio recuento.",
    holds_anyway: "Los retiene igualmente",
    holds_anyway_hint: "Ninguna entrada Siempre pasa deja pasar mensajes más allá de esta regla.",
    covers: "Afecta a",
    covers_everyone: "Todos a quienes llega",
    covers_only: "Solo estos",
    covers_audiences: "Audiencias",
    covers_recipients: "Personas y altavoces",
    s_through: "{applies}: puede despertar a {who} pese a las horas de silencio y los resúmenes.",
    s_through_everyone: "todos a quienes llega",
    s_not_for: " Excepto {list}.",
    s_only_if: " Solo mientras {entity} esté en {state}.",
    s_faster: " Mientras {entity} esté en {state}: cada {n} min.",
    s_alongside: " Funciona junto a otros recordatorios.",
    s_holds_anyway: " Ninguna entrada Siempre pasa la atraviesa.",
    s_rules: " Solo mensajes de las reglas de vigilancia {names}.",
    links_note: "Solo actúa en mensajes que {names} no toman, como en 1.x.",
    overlap_calm: "Donde ella y {names} encajan, cuenta la más tranquila.",
    overlap_send: "También actúa en los mismos mensajes: {names}.",
    cl_title: "Revisar tras la actualización",
    cl_intro: "La actualización mantuvo lo que hacían tus reglas. Estas reglas ahora funcionan de otro modo o nunca actúan; elige para cada una.",
    cl_links: "{name} solo actúa en mensajes que {names} no toman, como antes.",
    cl_never: "{name} nunca actúa: {names} toman primero todos sus mensajes.",
    cl_holds: "{name} también retiene los mensajes críticos, como antes.",
    cl_keep: "Dejar como antes",
    cl_act: "Dejar que actúe",
    cl_through: "Dejar pasar Crítico",
    cl_dismiss: "Ocultar la lista",
    cl_kept: "mantenido",
    cl_changed: "cambiado",
    ck_title: "¿Qué pasa con un mensaje?",
    ck_intro: "No se envía nada. La respuesta usa las reglas tal como están ahora.",
    ck_severity: "Nivel",
    ck_tag: "Etiqueta",
    ck_channels: "Canales",
    ck_banner: "Aviso del panel",
    ck_audience: "Enviado a",
    ck_source: "Viene de",
    ck_source_call: "Una automatización o un script",
    ck_time: "A las",
    ck_home: "En casa",
    ck_ack: "Confirmado tras (minutos, vacío: nunca)",
    ck_run: "Comprobar",
    ck_first: "Enseguida",
    ck_later: "Más tarde",
    ck_nothing: "No se entrega nada.",
    r_sent: "enviado",
    r_quiet: "enviado en silencio",
    r_held: "retenido",
    r_held_until: "retenido hasta {time}",
    r_skipped: "omitido",
    r_failed: "falla",
    r_by: "por {policy}",
    r_through: "dejado pasar por {names}",
    r_via: "añadido por {policy}",
    ck_band_off: "{names} lo dejaría pasar, pero está desactivada.",
    ck_summary: "Recogido para el resumen de {policy}.",
    ck_waits: "espera su Solo si",
    help_button: "Cómo actúan juntas las reglas",
    s_applies_manual: "Llamadas que nombran esta política",
    s_applies: "Mensajes con {parts}",
    s_severity: "gravedad {severities}",
    s_tag: "etiqueta {tags}",
    s_and: " y ",
    s_escalation: "{applies}: si nadie confirma en {n} min, se envía también por {channels}.",
    s_reminder: "{applies}: mientras nadie confirme, la notificación se repite cada {n} min, como máximo {m} veces{channels}.",
    s_quiet_hours: "{applies}: entre {from} y {to}{days}, las entregas fuera del panel se {action}.",
    s_away: "{applies}: quien no está en casa lo recibe al llegar{wait}.",
    s_presence_people: "{who} que {where} {zone}: push, ventana y correo se {then}",
    s_presence_speak: "la voz, mientras {who} de {audience} esté en {zone}, se {then}",
    w_recipient: "Un destinatario",
    w_in: "está en",
    w_not_in: "no está en",
    t_hold: "retienen hasta que eso cambie",
    t_drop: "descartan",
    aw_send: ", luego se envían igualmente",
    aw_drop: ", luego se descartan",
    everyone: "todos",
    nobody: "nadie",
    somebody: "alguien",
    presence_channels: "Canales que cubre (ninguno elegido: push, ventana, correo)",
    zone: "Zona",
    presence_when: "Push, ventana, correo: cuando el destinatario",
    household_who: "Voz: cuando",
    household_audience: "de esta audiencia está en la zona",
    presence_then: "Entonces",
    after_wait: "Cuando termina la espera",
    max_wait_presence: "Esperar como máximo (minutos, 0: mientras exista el mensaje)",
    hint_odd: "La voz solo se dice cuando nadie de esta audiencia está en la zona.",
    when_opts: {"not_in": "no está en la zona", "in": "está en la zona"},
    who_opts: {"nobody": "nadie", "somebody": "alguien"},
    then_opts: {"hold": "Retener hasta que eso cambie", "drop": "Descartar"},
    after_opts: {"send": "Enviar igualmente", "drop": "Descartar"},
    s_deliver: "{applies}: se envía además de inmediato por {channels}.",
    s_fallback: "{applies}: si {when}, se envía por {channels} en su lugar.",
    s_summarize_every: "{applies}: retenido, y se envía un resumen {n} min después del primer mensaje retenido.",
    s_summarize_at: "{applies}: retenido, y se envía un resumen cada día a las {time}.",
    s_in_channels: ", solo por {channels}",
    s_days: " en {days}",
    quiet_entity: "O silencio mientras esto esté encendido",
    quiet_entity_none: "Sin entidad: usar las horas",
    quiet_entity_hint: "Un horario, un interruptor de entrada o un sensor binario. Mientras esté encendido, las horas no se usan. Los mensajes retenidos salen cuando se apaga; una entidad ausente o no disponible no cuenta como silencio.",
    s_quiet_entity: "{applies}: mientras {entity} esté encendido, las entregas fuera del panel se {action}.",
    s_wait: ", como máximo {n} min",
    a_quiet: "envían en silencio",
    a_wait: "retienen hasta el final",
    a_drop: "descartan",
    w_no_audience: "la audiencia está vacía",
    w_failed: "la entrega falla",
    w_both: "la audiencia está vacía o la entrega falla",
  },
};

const CSS = `
.hu-page h3.sec { font-size: 15px; margin: 20px 0 6px; padding-top: 12px; border-top: 1px solid var(--divider-color); }
.hu-page .summary { background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; margin: 16px 0 12px; }
.hu-page .summary .sentence { margin: 4px 0; }
.hu-page label.radio { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; cursor: pointer; }
.hu-page label.radio input { margin-top: 4px; width: 20px; height: 20px; }
.hu-page .type-desc { margin-top: 0; }
.hu-page section.lane { border-left: 4px solid var(--divider-color); padding-left: 12px; }
.hu-page section.lane.calm { border-left-color: var(--success-color); }
.hu-page section.lane.band { border-left-color: var(--warning-color); background: var(--secondary-background-color); border-radius: 0 8px 8px 0; padding: 8px 12px; }
.hu-page section.lane.arrive { border-left-color: var(--primary-color); }
.hu-page li.policy { display: flex; align-items: center; gap: 4px; }
.hu-page li.policy .grow { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.hu-page li.policy button { flex: none; }
.hu-page ul.checklist { list-style: none; margin: 8px 0; padding: 0; }
.hu-page ul.checklist li { padding: 10px 0; border-bottom: 1px solid var(--divider-color); overflow-wrap: anywhere; }
.hu-page ul.checklist .row { margin-top: 8px; flex-wrap: wrap; }
.hu-page .answer ul { margin: 4px 0; padding-left: 18px; }
.hu-page .answer li { padding: 2px 0; overflow-wrap: anywhere; }
.hu-page .answer .when { font-weight: 600; margin-top: 8px; }
.hu-page input[type="datetime-local"] { font: inherit; padding: 6px; max-width: 100%; }
`;

// The page order: the lanes and the band (DESIGN §25.2). Which policies act does not depend on it.
const LANES = [
  { id: "calm", types: ["summarize", "quiet_hours", "presence"] },
  { id: "band", types: ["get_through"] },
  { id: "arrive", types: ["deliver", "escalation", "reminder", "fallback"] },
];
const TYPES = LANES.flatMap((lane) => lane.types);
const CALM = LANES[0].types;
const PRESENCE_CHANNELS = ["push", "popup", "mail", "speak"];
const PEOPLE_CHANNELS = ["push", "popup", "mail"];
const SEVERITIES = ["passive", "info", "warning", "critical"];
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const POLICY_CHANNELS = ["push", "popup", "speak", "persistent", "mail"];
const TARGET_CHANNELS = ["push", "popup", "speak", "mail"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues(type = "escalation") {
  return {
    name: "",
    type,
    severities: [],
    tags: "",
    not_severities: [],
    not_tags: "",
    rules: [],
    links: [],
    enabled: true,
    apply: "auto",
    // Only if: an entity and a state are edited here; any other stored shape is kept as it is.
    oi_entity: "",
    oi_state: "",
    only_if_raw: null,
    after_minutes: 5,
    channels: [],
    channels_from: "policy",
    targets_from: "policy",
    dismiss_acks: false,
    every_minutes: 30,
    max_count: 3,
    fw_entity: "",
    fw_state: "",
    fw_every: 15,
    faster_raw: null,
    alongside: false,
    from_time: "22:00:00",
    to_time: "07:00:00",
    days: [],
    quiet_entity: "",
    action: "quiet",
    holds_anyway: false,
    max_wait: 0,
    zone: "zone.home",
    presence_when: "not_in",
    household_who: "nobody",
    household_audience: "",
    presence_then: "hold",
    after_wait: "send",
    when: "no_audience",
    summary_mode: "every",
    summary_every: 60,
    summary_at: "20:00:00",
    covers: "everyone",
    covers_audiences: [],
    covers_recipients: [],
    push_audience: "",
    push_recipients: [],
    popup_audience: "",
    popup_recipients: [],
    speak_recipients: [],
    people_audience: "",
    people_recipients: [],
  };
}

// The domains Quiet hours can follow, and the entities of them that exist (plus the stored one).
const QUIET_DOMAINS = ["schedule", "input_boolean", "binary_sensor"];
export function quietEntities(hass, current) {
  const ids = Object.keys(hass?.states || {}).filter((id) => QUIET_DOMAINS.includes(id.split(".")[0])).sort();
  if (current && !ids.includes(current)) ids.push(current);
  return ids;
}

// The sentence of a Presence policy: one part for the people channels, one for speech (D-212).
function presenceSentence(values, t, applies) {
  const covered = values.channels.length ? values.channels : PEOPLE_CHANNELS;
  const zone = values.zone === "zone.home" ? "Home" : values.zone.replace(/^zone\./, "");
  const then = values.presence_then === "drop" ? t.t_drop : t.t_hold;
  const parts = [];
  if (covered.some((c) => PEOPLE_CHANNELS.includes(c))) {
    parts.push(fill(t.s_presence_people, { who: t.w_recipient, where: values.presence_when === "in" ? t.w_in : t.w_not_in, zone, then }));
  }
  if (covered.includes("speak")) {
    const audience = values.household_audience || t.everyone;
    parts.push(fill(t.s_presence_speak, { who: values.household_who === "somebody" ? t.somebody : t.nobody, audience, zone, then }));
  }
  let tail = "";
  if (values.presence_then === "hold" && values.max_wait > 0) tail = fill(t.s_wait, { n: values.max_wait }) + (values.after_wait === "drop" ? t.aw_drop : t.aw_send);
  return `${applies}: ${parts.join("; ")}${tail}.`;
}

// A simple condition (entity and state) splits into the two fields; anything else is kept raw.
function simpleCondition(condition) {
  if (!condition || typeof condition !== "object") return null;
  const keys = Object.keys(condition);
  const simple = keys.every((k) => ["entity_id", "state", "operator"].includes(k)) && (!condition.operator || condition.operator === "equals");
  return simple && condition.entity_id && typeof condition.state === "string" ? condition : null;
}

export function fromPolicy(policy) {
  const data = policy.data || {};
  const oldAway = data.type === "away"; // a 1.0 Away policy reads as Presence (D-214)
  const values = { ...blankValues(oldAway ? "presence" : data.type), name: policy.name };
  if (oldAway) values.after_wait = "drop";
  for (const key of ["severities", "not_severities", "channels", "days", "rules", "links", "covers_audiences", "covers_recipients"]) values[key] = [...(data[key] || [])];
  values.tags = (data.tags || []).join(", ");
  values.not_tags = (data.not_tags || []).join(", ");
  values.apply = data.apply === "manual" ? "manual" : "auto";
  for (const key of ["enabled", "dismiss_acks", "holds_anyway", "alongside"]) {
    if (key in data) values[key] = Boolean(data[key]);
  }
  for (const key of ["after_minutes", "every_minutes", "max_count", "max_wait", "summary_every"]) {
    if (data[key] !== undefined) values[key] = data[key];
  }
  for (const key of ["from_time", "to_time", "quiet_entity", "action", "when", "summary_at", "zone", "presence_when", "household_who", "household_audience", "presence_then", "after_wait"]) {
    if (data[key]) values[key] = data[key];
  }
  if (data.covers === "only") values.covers = "only";
  if (data.channels_from) values.channels_from = data.channels_from;
  if (data.targets_from) values.targets_from = data.targets_from;
  if (data.type === "summarize") values.summary_mode = data.summary_at ? "at" : "every";
  if (data.only_if) {
    const simple = simpleCondition(data.only_if);
    if (simple) Object.assign(values, { oi_entity: simple.entity_id, oi_state: simple.state });
    else values.only_if_raw = data.only_if;
  }
  if (data.faster_while && data.faster_while.condition) {
    const simple = simpleCondition(data.faster_while.condition);
    values.fw_every = data.faster_while.every_minutes || 15;
    if (simple) Object.assign(values, { fw_entity: simple.entity_id, fw_state: simple.state });
    else values.faster_raw = data.faster_while;
  }
  for (const [channel, target] of Object.entries(data.targets || {})) {
    if (target.audience) values[`${channel}_audience`] = target.audience;
    if (target.recipients) values[`${channel}_recipients`] = [...target.recipients];
  }
  return values;
}

export function splitTags(text) {
  return [...new Set(String(text || "").split(",").map((tag) => tag.trim()).filter(Boolean))];
}

// What goes to the policy flow: only the fields of the type, targets for the chosen channels only.
export function toFlowData(values) {
  const manual = values.apply === "manual";
  const data = {
    name: String(values.name).trim(),
    type: values.type,
    apply: manual ? "manual" : "auto",
    // A manual policy has no conditions.
    severities: manual ? [] : [...values.severities],
    tags: manual ? [] : splitTags(values.tags),
    enabled: Boolean(values.enabled),
  };
  if (!manual) {
    if (values.not_severities.length) data.not_severities = [...values.not_severities];
    if (splitTags(values.not_tags).length) data.not_tags = splitTags(values.not_tags);
    if (values.rules.length) data.rules = [...values.rules];
  }
  if (values.oi_entity && values.oi_state) data.only_if = { entity_id: values.oi_entity, state: values.oi_state };
  else if (values.only_if_raw) data.only_if = values.only_if_raw;
  // Which target fields go to the flow: none when the recipients come from the call, the people and
  // speakers targets when the channels do, else one per chosen channel (D-181).
  const targetKeys = () => {
    if (values.targets_from === "call") return [];
    if (values.channels_from !== "policy") return ["people", "speak"];
    return values.channels.filter((c) => TARGET_CHANNELS.includes(c));
  };
  const targets = () => {
    for (const channel of targetKeys()) {
      if (values[`${channel}_audience`]) data[`${channel}_audience`] = values[`${channel}_audience`];
      if ((values[`${channel}_recipients`] || []).length) data[`${channel}_recipients`] = [...values[`${channel}_recipients`]];
    }
  };
  const sources = () => {
    // Sent only when they differ from the default, as the server stores them (D-181).
    if (values.channels_from !== "policy") data.channels_from = values.channels_from;
    if (values.targets_from !== "policy") data.targets_from = values.targets_from;
    data.channels = values.channels_from === "policy" ? [...values.channels] : [];
  };
  switch (values.type) {
    case "escalation":
      Object.assign(data, { after_minutes: values.after_minutes, dismiss_acks: Boolean(values.dismiss_acks) });
      sources();
      targets();
      break;
    case "reminder":
      Object.assign(data, { every_minutes: values.every_minutes, max_count: values.max_count, channels: [...values.channels] });
      if (values.fw_entity && values.fw_state) data.faster_while = { condition: { entity_id: values.fw_entity, state: values.fw_state }, every_minutes: values.fw_every };
      else if (values.faster_raw) data.faster_while = values.faster_raw;
      if (values.alongside) data.alongside = true;
      break;
    case "quiet_hours":
      Object.assign(data, { from_time: values.from_time, to_time: values.to_time, days: [...values.days], action: values.action });
      if (values.quiet_entity) data.quiet_entity = values.quiet_entity;
      if (values.holds_anyway) data.holds_anyway = true;
      break;
    case "presence": {
      Object.assign(data, { max_wait: values.max_wait || 0, after_wait: values.after_wait || "send" });
      const covered = PRESENCE_CHANNELS.filter((c) => values.channels.includes(c));
      if (covered.length && !(covered.length === 3 && PEOPLE_CHANNELS.every((c) => covered.includes(c)))) data.channels = covered;
      else delete data.channels;
      const defaults = { zone: "zone.home", presence_when: "not_in", household_who: "nobody", household_audience: "", presence_then: "hold" };
      for (const [key, value] of Object.entries(defaults)) if ((values[key] || value) !== value) data[key] = values[key];
      break;
    }
    case "fallback":
      data.when = values.when;
      sources();
      targets();
      break;
    case "deliver":
      sources();
      targets();
      break;
    case "get_through":
      data.covers = values.covers === "only" ? "only" : "everyone";
      if (data.covers === "only") {
        if (values.covers_audiences.length) data.covers_audiences = [...values.covers_audiences];
        if (values.covers_recipients.length) data.covers_recipients = [...values.covers_recipients];
      }
      break;
    default:
      if (values.summary_mode === "at") data.summary_at = values.summary_at;
      else data.summary_every = values.summary_every;
      if (values.holds_anyway) data.holds_anyway = true;
  }
  return data;
}

const positive = (n) => Number.isInteger(n) && n >= 1;

// Problems as { field: code }; the codes are the policy flow's own error keys.
export function validate(values, existingNames, ownName) {
  const problems = {};
  const name = String(values.name || "").trim();
  const taken = existingNames.filter((n) => n.toLowerCase() !== String(ownName || "").toLowerCase());
  if (!name) problems.name = "name_required";
  else if (name.toLowerCase() === "none" || taken.some((n) => n.toLowerCase() === name.toLowerCase())) problems.name = "name_exists";
  const needsTargets = ["escalation", "fallback", "deliver"].includes(values.type);
  if (values.type === "escalation" && !positive(values.after_minutes)) problems.after_minutes = "after_required";
  if (values.type === "reminder") {
    if (!positive(values.every_minutes)) problems.every_minutes = "every_required";
    if (!positive(values.max_count)) problems.max_count = "max_required";
    if (values.fw_entity && !positive(values.fw_every)) problems.fw_every = "every_required";
  }
  if (values.type === "quiet_hours" && values.quiet_entity) {
    if (!QUIET_DOMAINS.includes(values.quiet_entity.split(".")[0])) problems.quiet_entity = "quiet_entity_invalid";
  } else if (values.type === "quiet_hours" && (!values.from_time || !values.to_time)) problems.from_time = "time_invalid";
  else if (values.type === "quiet_hours" && values.from_time === values.to_time) problems.to_time = "window_empty";
  if (values.type === "presence" && !(values.max_wait >= 0)) problems.max_wait = "wait_invalid";
  if (values.type === "summarize") {
    if (values.summary_mode === "at" && !values.summary_at) problems.summary_at = "time_invalid";
    if (values.summary_mode !== "at" && !positive(values.summary_every)) problems.summary_every = "every_required";
  }
  if (values.type === "get_through" && values.covers === "only" && !values.covers_audiences.length && !values.covers_recipients.length) {
    problems.covers_recipients = "target_required";
  }
  if (needsTargets) {
    const channelsFromPolicy = values.channels_from === "policy";
    if (!channelsFromPolicy && values.targets_from !== "policy") problems.targets_from = "nothing_new";
    if (channelsFromPolicy && values.channels.length === 0) problems.channels = "channels_required";
    if (values.targets_from !== "call") {
      // Channels from the call: the people and speakers targets are optional one by one, but one is set.
      const keys = channelsFromPolicy ? values.channels.filter((c) => TARGET_CHANNELS.includes(c)) : ["people", "speak"];
      let anySet = false;
      for (const channel of keys) {
        const audience = values[`${channel}_audience`];
        const recipients = values[`${channel}_recipients`] || [];
        if (!channelsFromPolicy && !audience && recipients.length === 0) continue;
        anySet = true;
        if (Boolean(audience) === (recipients.length > 0)) problems[`${channel}_target`] = "target_exclusive";
      }
      if (!channelsFromPolicy && !anySet) problems.people_target = "target_required";
    }
  }
  return problems;
}

// Two policies overlap when some message can match both: an empty list matches any.
export function overlaps(a, b) {
  const meet = (x, y) => x.length === 0 || y.length === 0 || x.some((item) => y.includes(item));
  return meet(a.severities, b.severities) && meet(a.tags, b.tags);
}

// The lane of a policy on the page; manual policies have their own section.
export function laneOf(policy) {
  const data = policy.data || {};
  if (data.apply === "manual") return "named";
  const type = data.type === "away" ? "presence" : data.type;
  return (LANES.find((l) => l.types.includes(type)) || { id: "arrive" }).id;
}

// The other enabled automatic policies of the same lane (for sending policies: the same type)
// that fit some of the same messages. Every one of them acts too (DESIGN §25.3).
export function overlapNames({ values, own, policies }) {
  if (values.apply === "manual") return [];
  const mine = { severities: values.severities, tags: splitTags(values.tags) };
  const lane = laneOf({ data: { type: values.type } });
  return policies
    .filter((p) => p.subentry_id !== own?.subentry_id)
    .filter((p) => p.data.apply !== "manual" && p.data.enabled !== false)
    .filter((p) => laneOf(p) === lane && (lane !== "arrive" || p.data.type === values.type))
    .filter((p) => overlaps(mine, { severities: p.data.severities || [], tags: p.data.tags || [] }))
    .map((p) => p.name);
}

export function appliesText(values, t) {
  if (values.apply === "manual") return t.s_applies_manual;
  const tags = splitTags(values.tags);
  if (values.severities.length === 0 && tags.length === 0) return t.s_applies_any;
  const parts = [];
  if (values.severities.length) {
    parts.push(fill(t.s_severity, { severities: values.severities.map((x) => t.severity_names[x]).join(", ") }));
  }
  if (tags.length) parts.push(fill(t.s_tag, { tags: tags.join(", ") }));
  return fill(t.s_applies, { parts: parts.join(t.s_and) });
}

export function sentence(values, t, labels = {}) {
  const audienceName = labels.audience || ((v) => v);
  const recipientName = labels.recipient || ((v) => v);
  const ruleName = labels.rule || ((v) => v);
  let text = sentenceBase(values, t, audienceName, recipientName);
  // Recipients taken from the call are said once, after the sentence (D-181).
  if (["escalation", "fallback", "deliver"].includes(values.type)) {
    if (values.targets_from === "call") text = `${text}${t.s_recipients_call}`;
    else if (values.channels_from !== "policy") {
      const audience = values.people_audience ? audienceName(values.people_audience) : "";
      const people = [...(values.people_recipients || []), ...(values.speak_recipients || [])].map(recipientName);
      const who = [audience, ...people].filter(Boolean).join(", ");
      if (who) text = `${text}${fill(t.s_recipients_policy, { who })}`;
    }
  }
  return text + tails(values, t, ruleName);
}

// What 2.0 adds to every sentence: Not for, From watch rule, Only if, and the type's extras.
function tails(values, t, ruleName) {
  let out = "";
  if (values.apply !== "manual") {
    const not = [...values.not_severities.map((x) => t.severity_names[x]), ...splitTags(values.not_tags).map((x) => `#${x}`)];
    if (not.length) out += fill(t.s_not_for, { list: not.join(", ") });
    if (values.rules.length) out += fill(t.s_rules, { names: values.rules.map(ruleName).join(", ") });
  }
  if (values.oi_entity && values.oi_state) out += fill(t.s_only_if, { entity: values.oi_entity, state: values.oi_state });
  if (values.type === "reminder" && values.fw_entity && values.fw_state) out += fill(t.s_faster, { entity: values.fw_entity, state: values.fw_state, n: values.fw_every });
  if (values.type === "reminder" && values.alongside) out += t.s_alongside;
  if (["quiet_hours", "summarize"].includes(values.type) && values.holds_anyway) out += t.s_holds_anyway;
  return out;
}

function sentenceBase(values, t, audienceName, recipientName) {
  const applies = appliesText(values, t);
  const named = values.channels.map((c) => t.channel_names[c]).join(", ") || "—";
  const channels = values.channels_from === "call" ? t.s_channels_call : values.channels_from === "failed" ? t.s_channels_failed : named;
  switch (values.type) {
    case "escalation":
      return fill(t.s_escalation, { applies, n: values.after_minutes, channels });
    case "reminder":
      return fill(t.s_reminder, { applies, n: values.every_minutes, m: values.max_count, channels: values.channels.length ? fill(t.s_in_channels, { channels }) : "" });
    case "quiet_hours": {
      if (values.quiet_entity) return fill(t.s_quiet_entity, { applies, entity: values.quiet_entity, action: t[`a_${values.action}`] });
      const days = values.days.length ? fill(t.s_days, { days: values.days.map((d) => t.days_names[d]).join(", ") }) : "";
      return fill(t.s_quiet_hours, { applies, from: String(values.from_time).slice(0, 5), to: String(values.to_time).slice(0, 5), days, action: t[`a_${values.action}`] });
    }
    case "presence":
      return presenceSentence(values, t, applies);
    case "fallback":
      return fill(t.s_fallback, { applies, when: t[`w_${values.when}`], channels });
    case "deliver":
      return fill(t.s_deliver, { applies, channels });
    case "get_through": {
      const who = values.covers === "only" ? [...values.covers_audiences.map(audienceName), ...values.covers_recipients.map(recipientName)].join(", ") || "—" : t.s_through_everyone;
      return fill(t.s_through, { applies, who });
    }
    default:
      return values.summary_mode === "at"
        ? fill(t.s_summarize_at, { applies, time: String(values.summary_at).slice(0, 5) })
        : fill(t.s_summarize_every, { applies, n: values.summary_every });
  }
}

// One line of the checker's answer: who, which channel, what happens and why (DESIGN §25.8).
export function checkLine(row, t, who, reasonText = (code) => code) {
  let what;
  if (row.result === "sent") what = row.note === "quiet" ? t.r_quiet : t.r_sent;
  else if (row.result === "held") what = row.until ? fill(t.r_held_until, { time: row.untilText || row.until }) : t.r_held;
  else what = t[`r_${row.result}`] || row.result;
  const why = [];
  // A skip or a failure without a policy behind it says why (no device, nobody home, ...).
  if (!row.by && row.reason && row.result !== "sent") why.push(reasonText(row.reason));
  if (row.by) why.push(fill(t.r_by, { policy: row.by }));
  if (row.through && row.through.length && row.result === "sent" && row.note !== "quiet") why.push(fill(t.r_through, { names: row.through.join(", ") }));
  if (row.via) why.push(fill(t.r_via, { policy: row.via }));
  const channel = t.channel_names[row.channel] || row.channel;
  return `${who} · ${channel}: ${what}${why.length ? ` (${why.join("; ")})` : ""}`;
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own, values }
  let message = "";
  let checked = null; // the last answer of the checker
  const ask = { severity: "warning", tag: "", rule: "", at: "", home: {}, ack: "", channels: ["banner", "push"], audience: "" };
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const policyName = (id) => (data.policies.find((p) => p.subentry_id === id) || {}).name || id;
  const ruleName = (id) => (data.rules.find((r) => r.subentry_id === id) || {}).name || id;
  const labels = () => ({ audience: (v) => ui.audienceLabel(v, data.choices), recipient: (v) => ui.recipientLabel(v, data.choices), rule: ruleName });

  function card(policy) {
    const values = fromPolicy(policy);
    const edit = el("button", { type: "button", textContent: s.common.edit });
    edit.addEventListener("click", () => { message = ""; editing = { own: policy, values }; render(); });
    const body = el("div", { className: "grow" }, [
      el("strong", { textContent: policy.name }),
      el("span", { className: "badge", textContent: t.types[values.type] || values.type }),
      ...(values.enabled ? [] : [el("span", { className: "badge", textContent: t.disabled })]),
      el("div", { className: "sub", textContent: sentence(values, t, labels()) }),
      ...(values.links.length ? [el("div", { className: "sub", textContent: fill(t.links_note, { names: values.links.map(policyName).join(", ") }) })] : []),
      ...(values.apply === "manual" ? [el("div", { className: "sub" }, [el("code", { textContent: policy.entity_id || "" })])] : []),
    ]);
    return el("li", { className: `policy${values.enabled ? "" : " dim"}` }, [body, edit]);
  }

  function lanes() {
    const out = [];
    for (const id of ["calm", "band", "arrive", "named"]) {
      const titles = { calm: [t.lane_calm, t.lane_calm_hint], band: [t.band, t.band_hint], arrive: [t.lane_arrive, t.lane_arrive_hint], named: [t.lane_named, t.lane_named_hint] };
      const mine = data.policies.filter((p) => laneOf(p) === id);
      if (id === "named" && !mine.length) continue;
      const [title, hint] = titles[id];
      out.push(
        el("section", { className: `lane ${id}` }, [
          el("h2", { textContent: title }),
          el("div", { className: "hint", textContent: hint }),
          el("ul", { className: "list" }, mine.length ? mine.map(card) : [el("li", { className: "sub", textContent: "—" })]),
        ]),
      );
    }
    return out;
  }

  // The check list after the 2.0 conversion (DESIGN §25.7): open items first.
  function checklist() {
    const items = data.conversion_items || [];
    if (!items.length) return [];
    const list = el("ul", { className: "checklist" });
    for (const item of items) {
      const policy = data.policies.find((p) => p.subentry_id === item.policy);
      if (!policy) continue;
      const linked = (policy.data.links || []).map(policyName).join(", ");
      const text = { links: t.cl_links, never_acts: t.cl_never, holds_anyway: t.cl_holds }[item.kind];
      const li = el("li", {}, [el("div", { textContent: fill(fill(text, { name: `“${policy.name}”` }), { names: linked }) })]);
      if (item.state === "open") {
        const answer = async (choice) => {
          await hass.callWS({ type: "heads_up/conversion_item", policy: item.policy, kind: item.kind, choice });
          await load();
        };
        const keep = el("button", { type: "button", textContent: t.cl_keep });
        keep.addEventListener("click", () => answer("keep"));
        const change = el("button", { type: "button", textContent: item.kind === "holds_anyway" ? t.cl_through : t.cl_act });
        change.addEventListener("click", () => answer("change"));
        li.append(el("div", { className: "row" }, [keep, change]));
      } else {
        li.append(el("div", { className: "sub", textContent: item.state === "kept" ? t.cl_kept : t.cl_changed }));
      }
      list.append(li);
    }
    const hide = el("button", { type: "button", textContent: t.cl_dismiss });
    hide.addEventListener("click", async () => { await hass.callWS({ type: "heads_up/conversion_items_dismiss" }); await load(); });
    return [el("section", {}, [el("h2", { textContent: t.cl_title }), el("div", { className: "hint", textContent: t.cl_intro }), list, hide])];
  }

  // The checker "What happens to a message?" (DESIGN §25.8): nothing is sent.
  function checker() {
    const box = el("section", {}, [el("h2", { textContent: t.ck_title }), el("div", { className: "hint", textContent: t.ck_intro })]);
    box.append(ui.field(t.ck_severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), ask.severity, (v) => { ask.severity = v; })));
    box.append(ui.field(t.ck_tag, ui.textInput(ask.tag, (v) => { ask.tag = v; })));
    box.append(ui.chips(t.ck_channels, ["banner", ...POLICY_CHANNELS].map((c) => ({ value: c, label: c === "banner" ? t.ck_banner : t.channel_names[c] })), ask.channels, (list) => { ask.channels = list; }));
    const audiences = data.choices.audience_choices || [];
    if (!ask.audience && audiences.length) ask.audience = (audiences.find((a) => a.id === "everyone") || audiences[0]).id;
    box.append(ui.field(t.ck_audience, ui.selectInput(audiences.map((a) => ({ value: a.id, label: a.name })), ask.audience, (v) => { ask.audience = v; })));
    const sources = [{ value: "", label: t.ck_source_call }, ...data.rules.map((r) => ({ value: r.subentry_id, label: r.name }))];
    box.append(ui.field(t.ck_source, ui.selectInput(sources, ask.rule, (v) => { ask.rule = v; })));
    const at = el("input", { type: "datetime-local", value: ask.at });
    at.addEventListener("input", () => { ask.at = at.value; });
    box.append(ui.field(t.ck_time, at));
    const persons = data.choices.persons || [];
    if (persons.length) {
      box.append(ui.chips(t.ck_home, persons.map((p) => ({ value: p.id, label: p.name })), persons.filter((p) => ask.home[p.id] !== false).map((p) => p.id), (list) => {
        ask.home = Object.fromEntries(persons.map((p) => [p.id, list.includes(p.id)]));
      }));
    }
    box.append(ui.field(t.ck_ack, ui.textInput(ask.ack, (v) => { ask.ack = v; })));
    const run = el("button", { type: "button", className: "primary", textContent: t.ck_run });
    run.addEventListener("click", async () => {
      const request = { type: "heads_up/policy_check", severity: ask.severity, home: ask.home, channels: ask.channels.length ? ask.channels : ["banner"] };
      if (ask.audience && ask.channels.some((c) => c !== "banner")) request.audience = ask.audience;
      if (ask.tag.trim()) request.tag = ask.tag.trim();
      if (ask.rule) request.rule = ask.rule;
      if (ask.at) request.at = new Date(ask.at).toISOString();
      if (/^\d+$/.test(ask.ack.trim())) request.ack_after = Number(ask.ack.trim());
      try {
        checked = await hass.callWS(request);
      } catch (err) {
        checked = { error: err.message || String(err) };
      }
      render();
    });
    box.append(run);
    if (checked) box.append(answer(checked));
    return box;
  }

  function answer(result) {
    const out = el("div", { className: "summary answer" });
    out.setAttribute("role", "status");
    if (result.error) return out.append(el("div", { className: "hint problems", textContent: result.error })), out;
    const time = (iso) => new Date(iso).toLocaleTimeString(ctx.language, { hour: "2-digit", minute: "2-digit" });
    const who = (row) => ui.recipientLabel(row.person || row.recipient || "", data.choices) || "—";
    const lines = (rows) => el("ul", {}, rows.map((row) => el("li", { textContent: checkLine({ ...row, untilText: row.until ? time(row.until) : "" }, t, who(row), (code) => ctx.fmt.reasonText(code, s)) })));
    if (result.held_for_summary) out.append(el("div", { textContent: fill(t.ck_summary, { policy: result.held_for_summary }) }));
    const first = (result.rows || []).filter((r) => r.channel !== "banner");
    out.append(el("div", { className: "when", textContent: t.ck_first }), first.length ? lines(first) : el("div", { textContent: t.ck_nothing }));
    if ((result.steps || []).length) {
      out.append(el("div", { className: "when", textContent: t.ck_later }));
      for (const step of result.steps) {
        const head = `${time(step.time)} · ${t.types[step.type] || step.type} ${step.policy}${step.skipped ? ` (${t.ck_waits})` : ""}`;
        out.append(el("div", { textContent: head }), lines(step.rows));
      }
    }
    if ((result.band_off || []).length) out.append(el("div", { className: "hint", textContent: fill(t.ck_band_off, { names: result.band_off.join(", ") }) }));
    return out;
  }

  function conditionFields(target, entityKey, stateKey, label, hint, again) {
    const entities = Object.keys(hass?.states || {}).sort();
    target.append(ui.field(label, ui.selectInput([{ value: "", label: t.oi_none }, ...entities.map((id) => ({ value: id, label: id }))], editing.values[entityKey], (v) => { editing.values[entityKey] = v; again(); }), hint));
    if (editing.values[entityKey]) target.append(ui.field(t.oi_state, ui.textInput(editing.values[stateKey], (v) => { editing.values[stateKey] = v; again(); })));
  }

  function editor() {
    const { own, values } = editing;
    const existing = data.policies.map((p) => p.name);
    const box = el("section", {}, [el("h2", { textContent: own ? t.editing : t.new })]);
    const again = () => render();

    box.append(ui.checkbox(s.common.enabled, values.enabled, (on) => { values.enabled = on; paint(); }));
    box.append(el("div", { className: "hint", textContent: t.enabled_hint }));
    // The switch of the policy: the registered ID, or the one a new policy will get (D-197).
    const entityLine = el("code", { textContent: own?.entity_id || "…" });
    let entityTimer = null;
    const showEntity = (name) => {
      if (own) return; // a rename does not change the ID of an existing policy
      clearTimeout(entityTimer);
      if (!String(name).trim()) {
        entityLine.textContent = "…";
        return;
      }
      entityTimer = setTimeout(async () => {
        try {
          const reply = await hass.callWS({ type: "heads_up/policy_entity_id", name: String(name).trim() });
          entityLine.textContent = reply.entity_id;
        } catch (err) {
          entityLine.textContent = "…";
        }
      }, 250);
    };
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; showEntity(v); paint(); })));
    box.append(ui.field(t.entity_id, entityLine, own ? t.entity_id_own : t.entity_id_new));
    showEntity(values.name);
    box.append(ui.field(t.type, ui.selectInput(TYPES.map((k) => ({ value: k, label: t.types[k] })), values.type, (v) => { values.type = v; again(); })));
    box.append(el("div", { className: "hint type-desc", textContent: t.type_desc[values.type] }));

    const words = el("div", { className: "sentence" });
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    const noteUpdaters = [];
    const does = el("div");
    const when = el("div");
    const number = (key, label, min = 1) => does.append(ui.field(label, ui.numberInput(values[key], (v) => { values[key] = v; paint(); }, { min })));
    const channelChips = (label) =>
      does.append(ui.chips(label, POLICY_CHANNELS.map((c) => ({ value: c, label: t.channel_names[c] })), values.channels, (list) => { values.channels = list; again(); }));
    const targetBlocks = () => {
      const labelsOf = { audience: t.target_audience, recipients: t.target_recipients, persistent: t.target_persistent };
      for (const channel of values.channels) {
        does.append(ui.targetBlock(channel, values, data.choices, { ...labelsOf, channel: fill(t.target_channel, { channel: t.channel_names[channel] }) }, (mode) => (mode ? again() : paint())));
      }
    };
    // Escalation, Deliver and Fallback: the channels and the recipients come from this policy or from
    // the call, in the four combinations of D-181. Taking both from the call adds nothing.
    const peopleBlocks = () => {
      const labelsOf = { audience: t.target_audience, recipients: t.target_recipients, persistent: t.target_persistent };
      does.append(ui.targetBlock("people", values, data.choices, { ...labelsOf, channel: t.people_target }, (mode) => (mode ? again() : paint())));
      does.append(ui.targetBlock("speak", values, data.choices, { ...labelsOf, channel: t.speakers_target }, () => paint()));
    };
    const sourceControls = (kind) => {
      const from = ["policy", "call", ...(kind === "fallback" ? ["failed"] : [])];
      does.append(ui.field(t.channels_from, ui.selectInput(from.map((k) => ({ value: k, label: t.cf[k] })), values.channels_from, (v) => { values.channels_from = v; again(); })));
      does.append(ui.field(t.targets_from, ui.selectInput(["policy", "call"].map((k) => ({ value: k, label: t.tf[k] })), values.targets_from, (v) => { values.targets_from = v; again(); })));
      if (values.channels_from === "policy") channelChips(t.channels);
      if (values.targets_from === "call") {
        does.append(el("div", { className: "hint", textContent: t.tf_call_hint }));
        if (kind === "fallback" && values.when === "no_audience") does.append(el("div", { className: "hint problems", textContent: t.same_empty }));
      } else if (values.channels_from === "policy") targetBlocks();
      else peopleBlocks();
    };
    const holdsAnyway = () => {
      does.append(ui.checkbox(t.holds_anyway, values.holds_anyway, (on) => { values.holds_anyway = on; paint(); }));
      does.append(el("div", { className: "hint", textContent: t.holds_anyway_hint }));
    };
    switch (values.type) {
      case "escalation":
        number("after_minutes", t.after);
        sourceControls("escalation");
        does.append(ui.checkbox(t.dismiss_acks, values.dismiss_acks, (on) => { values.dismiss_acks = on; paint(); }));
        does.append(el("div", { className: "hint", textContent: t.ack_note }));
        break;
      case "reminder":
        number("every_minutes", t.every);
        number("max_count", t.max_count);
        channelChips(t.channels_reminder);
        conditionFields(does, "fw_entity", "fw_state", t.faster, "", again);
        if (values.fw_entity) number("fw_every", t.faster_every);
        does.append(ui.checkbox(t.alongside, values.alongside, (on) => { values.alongside = on; paint(); }));
        does.append(el("div", { className: "hint", textContent: t.alongside_hint }));
        does.append(el("div", { className: "hint", textContent: t.ack_note }));
        break;
      case "quiet_hours":
        does.append(ui.field(t.quiet_entity, ui.selectInput([{ value: "", label: t.quiet_entity_none }, ...quietEntities(hass, values.quiet_entity).map((id) => ({ value: id, label: id }))], values.quiet_entity, (v) => { values.quiet_entity = v; again(); }), t.quiet_entity_hint));
        if (!values.quiet_entity) {
          does.append(ui.field(t.from, ui.timeInput(values.from_time, (v) => { values.from_time = v; paint(); })));
          does.append(ui.field(t.to, ui.timeInput(values.to_time, (v) => { values.to_time = v; paint(); })));
          does.append(ui.chips(t.days, DAYS.map((d) => ({ value: d, label: t.days_names[d] })), values.days, (list) => { values.days = list; paint(); }));
        }
        does.append(ui.field(t.action, ui.selectInput(["quiet", "wait", "drop"].map((k) => ({ value: k, label: t.actions[k] })), values.action, (v) => { values.action = v; paint(); })));
        holdsAnyway();
        break;
      case "presence": {
        does.append(ui.chips(t.presence_channels, PRESENCE_CHANNELS.map((c) => ({ value: c, label: t.channel_names[c] })), values.channels, (list) => { values.channels = list; again(); }));
        const zones = (data.choices.zones || []).map((z) => ({ value: z.id, label: z.name }));
        if (!zones.some((z) => z.value === values.zone)) zones.unshift({ value: values.zone, label: values.zone });
        does.append(ui.field(t.zone, ui.selectInput(zones, values.zone, (v) => { values.zone = v; paint(); })));
        const covered = values.channels.length ? values.channels : PEOPLE_CHANNELS;
        if (covered.some((c) => PEOPLE_CHANNELS.includes(c))) {
          does.append(ui.field(t.presence_when, ui.selectInput(["not_in", "in"].map((k) => ({ value: k, label: t.when_opts[k] })), values.presence_when, (v) => { values.presence_when = v; paint(); })));
        }
        if (covered.includes("speak")) {
          does.append(ui.field(t.household_who, ui.selectInput(["nobody", "somebody"].map((k) => ({ value: k, label: t.who_opts[k] })), values.household_who, (v) => { values.household_who = v; again(); })));
          const lists = (data.audiences || []).filter((a) => (a.data || {}).kind === "persons").map((a) => ({ value: a.subentry_id, label: a.name }));
          does.append(ui.field(t.household_audience, ui.selectInput([{ value: "", label: t.everyone }, ...lists], values.household_audience, (v) => { values.household_audience = v; paint(); })));
          if (values.household_who === "somebody" && values.presence_then === "hold") does.append(el("div", { className: "hint problems", textContent: t.hint_odd }));
        }
        does.append(ui.field(t.presence_then, ui.selectInput(["hold", "drop"].map((k) => ({ value: k, label: t.then_opts[k] })), values.presence_then, (v) => { values.presence_then = v; again(); })));
        if (values.presence_then === "hold") {
          number("max_wait", t.max_wait_presence, 0);
          does.append(ui.field(t.after_wait, ui.selectInput(["send", "drop"].map((k) => ({ value: k, label: t.after_opts[k] })), values.after_wait, (v) => { values.after_wait = v; paint(); })));
        }
        break;
      }
      case "deliver":
        sourceControls("deliver");
        break;
      case "fallback":
        does.append(ui.field(t.when, ui.selectInput(["no_audience", "failed", "both"].map((k) => ({ value: k, label: t.whens[k] })), values.when, (v) => { values.when = v; again(); })));
        sourceControls("fallback");
        break;
      case "get_through": {
        does.append(ui.field(t.covers, ui.selectInput([{ value: "everyone", label: t.covers_everyone }, { value: "only", label: t.covers_only }], values.covers, (v) => { values.covers = v; again(); })));
        if (values.covers === "only") {
          const audiences = (data.choices.audience_choices || []).map((a) => ({ value: a.id, label: a.name }));
          does.append(ui.chips(t.covers_audiences, audiences, values.covers_audiences, (list) => { values.covers_audiences = list; paint(); }));
          const people = [...(data.choices.persons || []).map((p) => ({ value: p.id, label: p.name })), ...((data.choices.recipients || {}).speak || []).map((id) => ({ value: id, label: ui.recipientLabel(id, data.choices) }))];
          does.append(ui.chips(t.covers_recipients, people, values.covers_recipients, (list) => { values.covers_recipients = list; paint(); }, true));
        }
        break;
      }
      default:
        does.append(ui.field(t.summary_mode, ui.selectInput([{ value: "every", label: t.summary_every_mode }, { value: "at", label: t.summary_at_mode }], values.summary_mode, (v) => { values.summary_mode = v; again(); })));
        if (values.summary_mode === "at") does.append(ui.field(t.summary_at, ui.timeInput(values.summary_at, (v) => { values.summary_at = v; paint(); })));
        else number("summary_every", t.summary_every);
        holdsAnyway();
        does.append(el("div", { className: "hint", textContent: t.summarize_note }));
    }

    // Which messages: automatic (For, Not for, From watch rule) or manual (named in a call).
    const radio = (value, label, hint) => {
      const input = el("input", { type: "radio", name: "apply", checked: values.apply === value });
      input.addEventListener("change", () => { values.apply = value; again(); });
      return el("label", { className: "radio" }, [input, el("span", {}, [el("strong", { textContent: label }), el("div", { className: "hint", textContent: hint })])]);
    };
    when.append(el("fieldset", {}, [el("legend", { textContent: t.apply_label }), radio("auto", t.apply_auto, t.apply_auto_hint), radio("manual", t.apply_manual, t.apply_manual_hint)]));
    if (values.apply === "manual") {
      when.append(el("div", { className: "hint", textContent: t.manual_how }), ui.yamlBlock(`policy: ${own?.entity_id || String(values.name).trim() || "…"}`, s.common), el("div", { className: "hint", textContent: t.manual_note }));
    } else {
      when.append(ui.chips(t.severities, SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), values.severities, (list) => { values.severities = list; paint(); }));
      when.append(ui.field(t.tags, ui.textInput(values.tags, (v) => { values.tags = v; paint(); })));
      when.append(ui.chips(t.not_severities, SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), values.not_severities, (list) => { values.not_severities = list; paint(); }));
      when.append(ui.field(t.not_tags, ui.textInput(values.not_tags, (v) => { values.not_tags = v; paint(); })));
      if (data.rules.length) when.append(ui.chips(t.rules, data.rules.map((r) => ({ value: r.subentry_id, label: r.name })), values.rules, (list) => { values.rules = list; paint(); }));
      if (values.links.length) when.append(el("div", { className: "hint", textContent: fill(t.links_note, { names: values.links.map(policyName).join(", ") }) }));
      const note = el("div", { className: "hint" });
      const paintNote = () => {
        const names = overlapNames({ values, own, policies: data.policies });
        note.textContent = names.length ? fill(CALM.includes(values.type) ? t.overlap_calm : t.overlap_send, { names: names.join(", ") }) : "";
      };
      paintNote();
      noteUpdaters.push(paintNote);
      when.append(note);
    }
    if (values.only_if_raw) when.append(ui.field(t.only_if, el("code", { textContent: JSON.stringify(values.only_if_raw) }), t.only_if_hint));
    else conditionFields(when, "oi_entity", "oi_state", t.only_if, t.only_if_hint, again);

    box.append(el("h3", { className: "sec", textContent: t.sec_when }), when, el("h3", { className: "sec", textContent: t.sec_does }), does);

    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", saveIt);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", () => { editing = null; render(); });
    const buttons = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete });
      del.addEventListener("click", remove);
      buttons.append(del);
    }
    box.append(buttons, el("div", { className: "summary" }, [el("strong", { textContent: t.sentence }), words, status]));
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), ui.yamlBlock(ui.toYaml({ name: own.name, ...own.data }), s.common));
    function paint() {
      const found = validate(values, existing, own?.name);
      const codes = Object.values(found);
      words.textContent = sentence(values, t, labels());
      save.disabled = codes.length > 0;
      status.className = codes.length ? "hint problems" : "hint ok";
      status.textContent = codes.length ? codes.map((c) => ui.errorText(c, ctx.language)).join(" ") : message || s.common.valid;
      noteUpdaters.forEach((update) => update());
    }
    paint();
    return box;
  }

  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    if (editing) return void root.append(editor());
    const help = el("button", { type: "button", textContent: t.help_button });
    help.addEventListener("click", () => ctx.navigate("policy-help"));
    root.append(el("div", { className: "row" }, [help]));
    root.append(...checklist(), checker());
    if (message) root.append(el("div", { className: "hint problems", textContent: message }));
    if (!data.policies.length) root.append(el("div", { className: "sub", textContent: t.none }));
    root.append(...lanes());
    const add = el("button", { type: "button", className: "primary", textContent: s.common.add });
    add.addEventListener("click", () => { message = ""; editing = { own: null, values: blankValues() }; render(); });
    root.append(el("div", { className: "row" }, [add]));
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "policy", own?.subentry_id, toFlowData(values));
    if (!result.ok) {
      message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      render();
      return;
    }
    editing = null;
    message = "";
    await load();
  }

  async function remove() {
    const { own } = editing;
    if (!window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
    await ui.removeSubentry(hass, data.entry_id, own.subentry_id);
    editing = null;
    await load();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    render();
  }

  root.append(el("div", { textContent: "…" }));
  load().catch(() => root.replaceChildren(el("div", { textContent: "…" })));
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      root.remove();
    },
  };
}
