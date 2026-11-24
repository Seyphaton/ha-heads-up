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
    intro: "Policies change how messages are delivered: when they may arrive, who else gets them and how often. Every policy that fits a message is applied.",
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
    channel_names: { push: "Push", popup: "Popup", speak: "Speak", persistent: "Persistent Notification", mail: "Mail", inbox: "Inbox" },
    after: "Escalate after (minutes)",
    channels: "Channels",
    channels_reminder: "Limit to these channels (none selected: all)",
    channels_quiet: "Limit to these channels (none selected: every channel except the banner)",
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
    entity_switch_hint: "Switch it off to pause the policy and on to use it again, also from an automation, for example to turn on holiday policies. Only if inside the policy does the same with a condition.",
    max_wait: "Wait for arrival (minutes, 0: as long as the message lives)",
    when: "Use when",
    whens: WHENS.en,
    channels_from: "Channels come from",
    targets_from: "Recipients come from",
    cf: { policy: "This policy (the channels below)", call: "The call (the same channels)", failed: "The call, only the channels that reached nobody" },
    tf: { policy: "This policy (the recipients below)", call: "The call (the same recipients)" },
    people_target: "People: push, popup, mail and inbox",
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
    type_desc: {"get_through": "Lets the messages it fits past quiet hours and summaries for the people it covers. It sends nothing itself: it only changes how a message arrives for people who get it anyway. To reach other people too, add a Deliver policy.", "escalation": "If nobody acknowledges within the time, the message is also delivered on the channels and to the targets you choose.", "reminder": "While nobody acknowledges, the message is repeated at an interval, up to a maximum.", "quiet_hours": "Between two times of day, deliveries outside the dashboard are sent quietly, held until the end or dropped.", "presence": "Holds or drops a delivery by where people are: for each recipient on push, popup, mail and inbox, for the household on speakers.", "fallback": "If the first delivery reached nobody, the message is delivered somewhere else: on other channels, or to other people on the same channels.", "summarize": "Matching messages are held on every channel, the banner included, and one summary is sent instead.", "deliver": "Matching messages are also delivered at once to the audience and channels you choose."},
    apply_label: "Attaches to messages",
    apply_auto: "Automatically",
    apply_auto_hint: "Every message whose severity and tag match gets this policy. An empty list matches any.",
    apply_manual: "Manually",
    apply_manual_hint: "Only a call that names this policy gets it. The severity and the tag of the message do not matter.",
    manual_how: "Name it in a call:",
    manual_note: "A call that names a policy uses only that policy, not the automatic ones. policy: none switches every policy off for a call.",
    badge_manual: "manual",
    lane_calm: "Keep it calm",
    lane_calm_hint: "Policies that hold messages back, send them quietly or bundle them into a summary. If two disagree, the quieter one wins.",
    band: "Always gets through",
    band_hint: "These messages are never summarized, and quiet hours do not apply to the people covered. Who gets them depends on the original message (for example named people, the Admins, everyone at home).",
    lane_arrive: "Make sure it arrives",
    lane_arrive_hint: "Policies that send additional messages, for example when the original recipients could not be reached or nobody reacted. All policies that fit are applied.",
    lane_named: "Only when named",
    lane_named_hint: "Used only when an automation or a watch rule names them.",
    x_summary_every: "Summary every {n} min",
    x_summary_at: "Summary at {time}",
    x_quiet: "{from}–{to}: {action}{channels}",
    x_quiet_entity: "While {entity} is on: {action}{channels}",
    x_act_quiet: "send quietly",
    x_act_wait: "hold until the end",
    x_act_drop: "drop",
    x_away_hold: "Hold until the person is at {zone}",
    x_home_hold: "Hold until the person leaves {zone}",
    x_away_drop: "Drop when the person is not at {zone}",
    x_home_drop: "Drop when the person is at {zone}",
    x_speak_nobody: "Speech only when someone is at {zone}",
    x_speak_somebody: "Speech only when nobody is at {zone}",
    x_through: "Ignores quiet hours and summaries",
    x_through_for: "Ignores quiet hours and summaries for {who}",
    x_deliver: "Also sends: {channels}",
    x_escalation: "After {n} min: {channels}",
    x_reminder: "Every {n} min, at most {m} times",
    x_fallback: "If nobody was reached: {channels}",
    x_only_if: "only while {entity} is {state}",
    d_messages: "Which messages",
    d_does: "What it does",
    ck_close: "Close",
    help_close: "Close",
    w_all: "All messages",
    w_severity: "Severity: {list}",
    w_tag: "Tag: {list}",
    w_not: "not {list}",
    w_named: "Only when named",
    col_policy: "Policy",
    col_messages: "Which messages",
    col_does: "What it does",
    lane_empty: "None yet.",
    turn_off: "Switch off",
    turn_on: "Switch on",
    not_tags: "Not for tags, comma separated",
    only_if: "Only if",
    only_if_hint: "The policy acts only while this is true. If the state cannot be read, for example because the device is offline, policies that hold or quiet messages do nothing, and policies that send still send.",
    oi_entity: "Entity",
    oi_state: "State",
    oi_none: "Always (no condition)",
    faster: "Faster while",
    faster_every: "Then repeat every (minutes)",
    alongside: "Runs alongside other reminders",
    alongside_hint: "Off: reminders on the same channel share the shortest rhythm, each with its own count.",
    holds_heading: "Interaction with 'Get through' policies",
    holds_anyway: "Ignore 'get through' policies",
    holds_anyway_hint: "No Always gets through entry can get messages past this policy.",
    holds_anyway_warning: "Caution: Critical messages will also be {what}. Only enable this if you are aware of the impact.",
    holds_what: { quiet: "sent quietly", wait: "held", drop: "dropped", summarize: "summarized" },
    covers: "Covers",
    covers_everyone: "Everyone it reaches",
    covers_only: "Only these",
    covers_audiences: "Audiences",
    covers_recipients: "People and speakers",
    s_through: "{applies}: ignores quiet hours and summaries{who}.",
    s_through_everyone: "",
    s_through_for: " for {who}",
    not_overlap: "Not for repeats something from For ({list}): those messages never get this policy.",
    unsaved_confirm: "You have changes that are not saved. Close anyway?",
    s_not_for: " Not for {list}.",
    s_only_if: " Only while {entity} is {state}.",
    s_faster: " While {entity} is {state}: every {n} min.",
    s_alongside: " Runs alongside other reminders.",
    s_holds_anyway: " Nothing gets past it, not even Always gets through.",
    links_note: "Leaves out {what} while {other} is switched on.",
    overlap_calm: "Where it and {names} both fit, the calmer counts.",
    overlap_send: "Also acts on the same messages: {names}.",
    cl_title: "The policy feature has been updated – please review the new behaviour",
    cl_intro: "Below you find the policies that we have automatically updated to match the previous behaviour. Decide for each one if you want to keep the migration edits. This is a one-time task after the introduction of the policy redesign.",
    cl_links: "{name} leaves out {what} while {other} is switched on, as before the update.",
    cl_never: "{name} does nothing at the moment, so it works as before the update: it leaves out all its messages.",
    cl_holds: "{name} also holds back critical messages, as before the update.",
    cl_not_for: "{name} now leaves out {what}, so it works as before the update.",
    cl_sev: "messages with severity {list}",
    cl_tag: "messages with the tag {list}",
    cl_sev_tag: "messages with severity {sev} and the tag {tags}",
    cl_and: " and ",
    cl_or: " or ",
    cl_keep: "Keep it like this",
    cl_act: "Apply to them too",
    cl_through: "Let critical messages through",
    cl_dismiss: "Hide this list",
    cl_kept: "Kept",
    cl_changed: "Changed",
    ck_title: "Test policies",
    ck_intro: "Try out a message: you see who would get it, when and why. Nothing is sent.",
    ck_severity: "Severity",
    ck_tag: "Tag",
    ck_channels: "Channels",
    ck_banner: "Dashboard banner",
    ck_audience: "Sent to",
    ck_source: "Comes from",
    ck_source_call: "An automation or script",
    ck_time: "At",
    ck_home: "At home",
    ck_ack: "Acknowledged after (min)",
    ck_ack_hint: "Empty: nobody acknowledges.",
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
    s_quiet_hours: "{applies}: between {from} and {to}{days}, deliveries outside the dashboard are {action}{channels}.",
    s_away: "{applies}: a person who is not home gets it when they arrive{wait}.",
    s_presence_people: "{who} who {where} {zone}: push, popup, mail and inbox are {then}",
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
    presence_channels: "Channels it covers (none selected: push, popup, mail, inbox)",
    zone: "Zone",
    presence_when: "Push, popup, mail, inbox: when the recipient",
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
    s_quiet_entity: "{applies}: while {entity} is on, deliveries outside the dashboard are {action}{channels}.",
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
    intro: "Richtlinien ändern, wie Meldungen zugestellt werden: wann sie ankommen dürfen, wer sie noch bekommt und wie oft. Jede Richtlinie, die auf eine Meldung passt, wird angewendet.",
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
    channel_names: { push: "Push", popup: "Popup", speak: "Sprache", persistent: "Persistente Benachrichtigung", mail: "E-Mail", inbox: "Posteingang" },
    after: "Eskalieren nach (Minuten)",
    channels: "Kanäle",
    channels_reminder: "Auf diese Kanäle beschränken (keiner gewählt: alle)",
    channels_quiet: "Auf diese Kanäle beschränken (keiner gewählt: alle außer dem Banner)",
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
    entity_switch_hint: "Schalte ihn aus, um die Richtlinie zu pausieren, und wieder an, um sie zu nutzen, auch per Automation, zum Beispiel um Urlaubs-Richtlinien einzuschalten. Nur wenn in der Richtlinie erreicht dasselbe mit einer Bedingung.",
    max_wait: "Auf Ankunft warten (Minuten, 0: solange die Meldung besteht)",
    when: "Verwenden, wenn",
    whens: WHENS.de,
    channels_from: "Kanäle stammen aus",
    targets_from: "Empfänger stammen aus",
    cf: { policy: "Diese Richtlinie (die Kanäle unten)", call: "Der Aufruf (dieselben Kanäle)", failed: "Der Aufruf, nur die Kanäle, die niemanden erreicht haben" },
    tf: { policy: "Diese Richtlinie (die Empfänger unten)", call: "Der Aufruf (dieselben Empfänger)" },
    people_target: "Personen: Push, Popup, E-Mail und Posteingang",
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
    type_desc: {"get_through": "Lässt die passenden Meldungen für die erfassten Leute an Ruhezeit und Zusammenfassung vorbei. Sendet selbst nichts: Der Eintrag ändert nur, wie eine Meldung bei den Leuten ankommt, die sie ohnehin bekommen. Sollen weitere Leute sie bekommen, ergänze eine Richtlinie Zustellen.", "escalation": "Bestätigt niemand innerhalb der Zeit, wird die Meldung zusätzlich auf den gewählten Kanälen und an die gewählten Ziele zugestellt.", "reminder": "Solange niemand bestätigt, wird die Meldung in einem Abstand wiederholt, höchstens so oft wie eingestellt.", "quiet_hours": "Zwischen zwei Uhrzeiten werden Zustellungen außerhalb des Dashboards leise gesendet, bis zum Ende zurückgehalten oder verworfen.", "presence": "Hält eine Zustellung zurück oder verwirft sie, je nachdem wo Personen sind: für jeden Empfänger bei Push, Popup, Mail und Posteingang, für den Haushalt bei Lautsprechern.", "fallback": "Hat die erste Zustellung niemanden erreicht, wird die Meldung anderswo zugestellt: auf anderen Kanälen oder an andere Personen auf denselben Kanälen.", "summarize": "Passende Meldungen werden auf jedem Kanal zurückgehalten, auch im Banner, und stattdessen wird eine Zusammenfassung gesendet.", "deliver": "Passende Meldungen werden zusätzlich sofort an die gewählte Zielgruppe auf den gewählten Kanälen zugestellt."},
    apply_label: "Gilt für Meldungen",
    apply_auto: "Automatisch",
    apply_auto_hint: "Jede Meldung, deren Schweregrad und Tag passen, bekommt diese Richtlinie. Eine leere Liste passt auf alles.",
    apply_manual: "Manuell",
    apply_manual_hint: "Nur ein Aufruf, der diese Richtlinie nennt, bekommt sie. Schweregrad und Tag der Meldung spielen keine Rolle.",
    manual_how: "In einem Aufruf nennen:",
    manual_note: "Ein Aufruf, der eine Richtlinie nennt, nutzt nur diese, nicht die automatischen. policy: none schaltet alle Richtlinien für einen Aufruf ab.",
    badge_manual: "manuell",
    lane_calm: "Für Ruhe sorgen",
    lane_calm_hint: "Richtlinien, die Meldungen zurückhalten, leise senden oder in einer Zusammenfassung bündeln. Sind sich zwei uneinig, gewinnt die ruhigere.",
    band: "Kommt immer durch",
    band_hint: "Diese Meldungen werden nie zusammengefasst, und die Ruhezeit gilt nicht für die erfassten Leute. Wer sie bekommt, hängt von der ursprünglichen Meldung ab (zum Beispiel genannte Personen, die Admins, alle zu Hause).",
    lane_arrive: "Damit es ankommt",
    lane_arrive_hint: "Richtlinien, die zusätzliche Meldungen senden, zum Beispiel wenn die ursprünglichen Empfänger nicht erreicht wurden oder niemand reagiert hat. Alle passenden Richtlinien werden angewendet.",
    lane_named: "Nur wenn genannt",
    lane_named_hint: "Werden nur benutzt, wenn eine Automation oder eine Überwachungsregel sie nennt.",
    x_summary_every: "Zusammenfassung alle {n} Min.",
    x_summary_at: "Zusammenfassung um {time}",
    x_quiet: "{from}–{to}: {action}{channels}",
    x_quiet_entity: "Solange {entity} an ist: {action}{channels}",
    x_act_quiet: "leise senden",
    x_act_wait: "bis zum Ende zurückhalten",
    x_act_drop: "verwerfen",
    x_away_hold: "Zurückhalten, bis die Person in {zone} ist",
    x_home_hold: "Zurückhalten, bis die Person {zone} verlässt",
    x_away_drop: "Verwerfen, wenn die Person nicht in {zone} ist",
    x_home_drop: "Verwerfen, wenn die Person in {zone} ist",
    x_speak_nobody: "Sprache nur, wenn jemand in {zone} ist",
    x_speak_somebody: "Sprache nur, wenn niemand in {zone} ist",
    x_through: "Ignoriert Ruhezeit und Zusammenfassung",
    x_through_for: "Ignoriert Ruhezeit und Zusammenfassung für {who}",
    x_deliver: "Sendet zusätzlich: {channels}",
    x_escalation: "Nach {n} Min.: {channels}",
    x_reminder: "Alle {n} Min., höchstens {m}-mal",
    x_fallback: "Wenn niemand erreicht wurde: {channels}",
    x_only_if: "nur solange {entity} {state} ist",
    d_messages: "Welche Meldungen",
    d_does: "Was sie tut",
    ck_close: "Schließen",
    help_close: "Schließen",
    w_all: "Alle Meldungen",
    w_severity: "Stufe: {list}",
    w_tag: "Tag: {list}",
    w_not: "nicht {list}",
    w_named: "Nur wenn genannt",
    col_policy: "Richtlinie",
    col_messages: "Welche Meldungen",
    col_does: "Was sie tut",
    lane_empty: "Noch keine.",
    turn_off: "Ausschalten",
    turn_on: "Einschalten",
    not_tags: "Nicht für Tags, durch Komma getrennt",
    only_if: "Nur wenn",
    only_if_hint: "Die Richtlinie wirkt nur, solange das zutrifft. Lässt sich der Zustand nicht lesen, zum Beispiel weil das Gerät offline ist, tun Richtlinien, die zurückhalten oder leise schalten, nichts, und sendende Richtlinien senden trotzdem.",
    oi_entity: "Entität",
    oi_state: "Zustand",
    oi_none: "Immer (keine Bedingung)",
    faster: "Öfter, solange",
    faster_every: "Dann alle (Minuten) wiederholen",
    alongside: "Läuft neben anderen Erinnerungen",
    alongside_hint: "Aus: Erinnerungen auf demselben Kanal teilen sich den kürzesten Rhythmus, jede mit eigener Zählung.",
    holds_heading: "Zusammenspiel mit „Kommt durch“-Richtlinien",
    holds_anyway: "Richtlinien „Kommt durch“ ignorieren",
    holds_anyway_hint: "Kein Eintrag von Kommt immer durch bringt Meldungen an dieser Richtlinie vorbei.",
    holds_anyway_warning: "Achtung: Auch kritische Meldungen werden {what}. Aktiviere das nur, wenn du die Folgen kennst.",
    holds_what: { quiet: "leise gesendet", wait: "zurückgehalten", drop: "verworfen", summarize: "zusammengefasst" },
    covers: "Gilt für",
    covers_everyone: "Alle, die sie erreicht",
    covers_only: "Nur diese",
    covers_audiences: "Zielgruppen",
    covers_recipients: "Personen und Lautsprecher",
    s_through: "{applies}: ignoriert Ruhezeit und Zusammenfassung{who}.",
    s_through_everyone: "",
    s_through_for: " für {who}",
    not_overlap: "Nicht für wiederholt etwas aus Für ({list}): diese Meldungen bekommen die Richtlinie nie.",
    unsaved_confirm: "Du hast Änderungen, die nicht gespeichert sind. Trotzdem schließen?",
    s_not_for: " Nicht für {list}.",
    s_only_if: " Nur solange {entity} {state} ist.",
    s_faster: " Solange {entity} {state} ist: alle {n} Min.",
    s_alongside: " Läuft neben anderen Erinnerungen.",
    s_holds_anyway: " Nichts kommt vorbei, auch nicht Kommt immer durch.",
    links_note: "Lässt {what} aus, solange {other} eingeschaltet ist.",
    overlap_calm: "Wo sie und {names} beide passen, zählt die ruhigere.",
    overlap_send: "Wirkt auch auf dieselben Meldungen: {names}.",
    cl_title: "Die Richtlinien wurden überarbeitet – bitte prüfe das neue Verhalten",
    cl_intro: "Unten findest du die Richtlinien, die wir automatisch angepasst haben, damit sie sich wie vorher verhalten. Entscheide für jede, ob du die Anpassung behalten willst. Das ist eine einmalige Aufgabe nach der Neugestaltung der Richtlinien.",
    cl_links: "{name} lässt {what} aus, solange {other} eingeschaltet ist, wie vor dem Update.",
    cl_never: "{name} tut gerade nichts und arbeitet damit wie vor dem Update: Sie lässt alle ihre Meldungen aus.",
    cl_holds: "{name} hält auch kritische Meldungen zurück, wie vor dem Update.",
    cl_not_for: "{name} lässt jetzt {what} aus und arbeitet damit wie vor dem Update.",
    cl_sev: "Meldungen mit Stufe {list}",
    cl_tag: "Meldungen mit dem Tag {list}",
    cl_sev_tag: "Meldungen mit Stufe {sev} und dem Tag {tags}",
    cl_and: " und ",
    cl_or: " oder ",
    cl_keep: "So lassen",
    cl_act: "Auch auf diese anwenden",
    cl_through: "Kritische Meldungen durchlassen",
    cl_dismiss: "Liste ausblenden",
    cl_kept: "Beibehalten",
    cl_changed: "Geändert",
    ck_title: "Richtlinien testen",
    ck_intro: "Probiere eine Meldung aus: du siehst, wer sie wann bekommen würde und warum. Es wird nichts gesendet.",
    ck_severity: "Stufe",
    ck_tag: "Tag",
    ck_channels: "Kanäle",
    ck_banner: "Dashboard-Banner",
    ck_audience: "Gesendet an",
    ck_source: "Kommt von",
    ck_source_call: "Einer Automation oder einem Skript",
    ck_time: "Um",
    ck_home: "Zu Hause",
    ck_ack: "Bestätigt nach (Min.)",
    ck_ack_hint: "Leer: niemand bestätigt.",
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
    s_quiet_hours: "{applies}: zwischen {from} und {to}{days} werden Zustellungen außerhalb des Dashboards {action}{channels}.",
    s_away: "{applies}: wer nicht zu Hause ist, bekommt sie bei der Ankunft{wait}.",
    s_presence_people: "{who}, der {where} {zone} ist: Push, Popup, Mail und Posteingang werden {then}",
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
    presence_channels: "Abgedeckte Kanäle (keiner gewählt: Push, Popup, Mail, Posteingang)",
    zone: "Zone",
    presence_when: "Push, Popup, Mail, Posteingang: wenn der Empfänger",
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
    s_quiet_entity: "{applies}: solange {entity} an ist, werden Zustellungen außerhalb des Dashboards {action}{channels}.",
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
    intro: "Les règles changent la façon dont les messages sont livrés : quand ils peuvent arriver, qui d'autre les reçoit et à quelle fréquence. Chaque règle qui correspond à un message est appliquée.",
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
    channel_names: { push: "Push", popup: "Fenêtre", speak: "Voix", persistent: "Notification persistante", mail: "Courriel", inbox: "Boîte de réception" },
    after: "Escalader après (minutes)",
    channels: "Canaux",
    channels_reminder: "Limiter à ces canaux (aucun choisi : tous)",
    channels_quiet: "Limiter à ces canaux (aucun choisi : tous sauf la bannière)",
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
    entity_switch_hint: "Désactivez-le pour mettre la règle en pause et activez-le pour l'utiliser à nouveau, aussi depuis une automatisation, par exemple pour activer des règles de vacances. Seulement si dans la règle fait la même chose avec une condition.",
    max_wait: "Attendre l'arrivée (minutes, 0 : tant que le message existe)",
    when: "Utiliser quand",
    whens: WHENS.fr,
    channels_from: "Les canaux viennent de",
    targets_from: "Les destinataires viennent de",
    cf: { policy: "Cette politique (les canaux ci-dessous)", call: "L'appel (les mêmes canaux)", failed: "L'appel, seulement les canaux qui n'ont atteint personne" },
    tf: { policy: "Cette politique (les destinataires ci-dessous)", call: "L'appel (les mêmes destinataires)" },
    people_target: "Personnes : push, fenêtre, courriel et boîte de réception",
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
    type_desc: {"get_through": "Fait passer les messages qu'elle concerne au-delà des heures calmes et des résumés pour les personnes concernées. N'envoie rien elle-même : elle change seulement la façon dont un message arrive chez ceux qui le reçoivent de toute façon. Pour joindre d'autres personnes, ajoutez une règle Livrer.", "escalation": "Si personne ne confirme dans le délai, le message est aussi remis sur les canaux et aux cibles que vous choisissez.", "reminder": "Tant que personne ne confirme, le message est répété à intervalle régulier, jusqu'à un maximum.", "quiet_hours": "Entre deux heures de la journée, les remises hors tableau de bord sont envoyées discrètement, retenues jusqu'à la fin ou abandonnées.", "presence": "Retient ou abandonne une livraison selon où se trouvent les personnes : pour chaque destinataire sur push, popup, courriel et boîte de réception, pour le foyer sur les haut-parleurs.", "fallback": "Si la première remise n'a joint personne, le message est remis ailleurs : sur d'autres canaux, ou à d'autres personnes sur les mêmes canaux.", "summarize": "Les messages correspondants sont retenus sur chaque canal, bannière comprise, et un seul résumé est envoyé à la place.", "deliver": "Les messages correspondants sont aussi remis tout de suite à l'audience et sur les canaux que vous choisissez."},
    apply_label: "S'applique aux messages",
    apply_auto: "Automatiquement",
    apply_auto_hint: "Chaque message dont la gravité et l'étiquette correspondent reçoit cette politique. Une liste vide correspond à tout.",
    apply_manual: "Manuellement",
    apply_manual_hint: "Seul un appel qui nomme cette politique la reçoit. La gravité et l'étiquette du message n'ont pas d'importance.",
    manual_how: "La nommer dans un appel :",
    manual_note: "Un appel qui nomme une politique n'utilise que celle-là, pas les automatiques. policy: none désactive toutes les politiques pour un appel.",
    badge_manual: "manuelle",
    lane_calm: "Garder le calme",
    lane_calm_hint: "Des règles qui retiennent les messages, les envoient discrètement ou les regroupent dans un résumé. Si deux divergent, la plus calme l'emporte.",
    band: "Passe toujours",
    band_hint: "Ces messages ne sont jamais résumés, et les heures calmes ne s'appliquent pas aux personnes concernées. Qui les reçoit dépend du message d'origine (par exemple des personnes nommées, les admins, tout le monde à la maison).",
    lane_arrive: "S'assurer qu'il arrive",
    lane_arrive_hint: "Des règles qui envoient des messages supplémentaires, par exemple quand les destinataires d'origine n'ont pas été joints ou que personne n'a réagi. Toutes les règles qui correspondent sont appliquées.",
    lane_named: "Seulement si nommée",
    lane_named_hint: "Utilisées seulement quand une automatisation ou une règle de surveillance les nomme.",
    x_summary_every: "Résumé toutes les {n} min",
    x_summary_at: "Résumé à {time}",
    x_quiet: "{from}–{to} : {action}{channels}",
    x_quiet_entity: "Tant que {entity} est activé : {action}{channels}",
    x_act_quiet: "envoyer discrètement",
    x_act_wait: "retenir jusqu'à la fin",
    x_act_drop: "abandonner",
    x_away_hold: "Retenir jusqu'à ce que la personne soit à {zone}",
    x_home_hold: "Retenir jusqu'à ce que la personne quitte {zone}",
    x_away_drop: "Abandonner si la personne n'est pas à {zone}",
    x_home_drop: "Abandonner si la personne est à {zone}",
    x_speak_nobody: "Voix seulement si quelqu'un est à {zone}",
    x_speak_somebody: "Voix seulement si personne n'est à {zone}",
    x_through: "Ignore les heures calmes et les résumés",
    x_through_for: "Ignore les heures calmes et les résumés pour {who}",
    x_deliver: "Envoie aussi : {channels}",
    x_escalation: "Après {n} min : {channels}",
    x_reminder: "Toutes les {n} min, au plus {m} fois",
    x_fallback: "Si personne n'a été joint : {channels}",
    x_only_if: "seulement tant que {entity} est {state}",
    d_messages: "Quels messages",
    d_does: "Ce qu'elle fait",
    ck_close: "Fermer",
    help_close: "Fermer",
    w_all: "Tous les messages",
    w_severity: "Niveau : {list}",
    w_tag: "Étiquette : {list}",
    w_not: "sauf {list}",
    w_named: "Seulement si nommée",
    col_policy: "Règle",
    col_messages: "Quels messages",
    col_does: "Ce qu'elle fait",
    lane_empty: "Aucune pour l'instant.",
    turn_off: "Désactiver",
    turn_on: "Activer",
    not_tags: "Sauf pour les étiquettes, séparées par des virgules",
    only_if: "Seulement si",
    only_if_hint: "La règle n'agit que tant que c'est vrai. Si l'état ne peut pas être lu, par exemple parce que l'appareil est hors ligne, les règles qui retiennent ou mettent en sourdine ne font rien, et les règles qui envoient envoient quand même.",
    oi_entity: "Entité",
    oi_state: "État",
    oi_none: "Toujours (sans condition)",
    faster: "Plus souvent tant que",
    faster_every: "Puis répéter toutes les (minutes)",
    alongside: "Fonctionne à côté des autres rappels",
    alongside_hint: "Désactivé : les rappels d'un même canal partagent le rythme le plus court, chacun avec son propre compte.",
    holds_heading: "Interaction avec les politiques « Laisser passer »",
    holds_anyway: "Ignorer les politiques « Laisser passer »",
    holds_anyway_hint: "Aucune entrée Passe toujours ne fait passer les messages au-delà de cette règle.",
    holds_anyway_warning: "Attention : les messages critiques seront aussi {what}. N'activez ceci que si vous en connaissez l'effet.",
    holds_what: { quiet: "envoyés discrètement", wait: "retenus", drop: "abandonnés", summarize: "résumés" },
    covers: "Concerne",
    covers_everyone: "Tous ceux qu'il atteint",
    covers_only: "Seulement ceux-ci",
    covers_audiences: "Audiences",
    covers_recipients: "Personnes et haut-parleurs",
    s_through: "{applies} : ignore les heures calmes et les résumés{who}.",
    s_through_everyone: "",
    s_through_for: " pour {who}",
    not_overlap: "Sauf pour reprend un élément de Pour ({list}) : ces messages ne reçoivent jamais cette règle.",
    unsaved_confirm: "Vous avez des modifications non enregistrées. Fermer quand même ?",
    s_not_for: " Sauf pour {list}.",
    s_only_if: " Seulement tant que {entity} est {state}.",
    s_faster: " Tant que {entity} est {state} : toutes les {n} min.",
    s_alongside: " Fonctionne à côté des autres rappels.",
    s_holds_anyway: " Rien ne passe, pas même Passe toujours.",
    links_note: "Laisse de côté {what} tant que {other} est activée.",
    overlap_calm: "Là où elle et {names} correspondent toutes deux, la plus calme compte.",
    overlap_send: "Agit aussi sur les mêmes messages : {names}.",
    cl_title: "Les règles ont été repensées – vérifiez le nouveau comportement",
    cl_intro: "Voici les règles que nous avons adaptées automatiquement pour garder le comportement d'avant. Décidez pour chacune si vous gardez l'adaptation. C'est une tâche unique après la refonte des règles.",
    cl_links: "{name} laisse de côté {what} tant que {other} est activée, comme avant la mise à jour.",
    cl_never: "{name} ne fait rien pour l'instant et fonctionne ainsi comme avant la mise à jour : elle laisse de côté tous ses messages.",
    cl_holds: "{name} retient aussi les messages critiques, comme avant la mise à jour.",
    cl_not_for: "{name} laisse maintenant de côté {what} et fonctionne ainsi comme avant la mise à jour.",
    cl_sev: "les messages de niveau {list}",
    cl_tag: "les messages avec l'étiquette {list}",
    cl_sev_tag: "les messages de niveau {sev} avec l'étiquette {tags}",
    cl_and: " et ",
    cl_or: " ou ",
    cl_keep: "Laisser ainsi",
    cl_act: "L'appliquer aussi à eux",
    cl_through: "Laisser passer les messages critiques",
    cl_dismiss: "Masquer la liste",
    cl_kept: "Gardé",
    cl_changed: "Modifié",
    ck_title: "Tester les règles",
    ck_intro: "Essayez un message : vous voyez qui le recevrait, quand et pourquoi. Rien n'est envoyé.",
    ck_severity: "Niveau",
    ck_tag: "Étiquette",
    ck_channels: "Canaux",
    ck_banner: "Bannière du tableau de bord",
    ck_audience: "Envoyé à",
    ck_source: "Vient de",
    ck_source_call: "Une automatisation ou un script",
    ck_time: "À",
    ck_home: "À la maison",
    ck_ack: "Confirmé après (min)",
    ck_ack_hint: "Vide : personne ne confirme.",
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
    s_quiet_hours: "{applies} : entre {from} et {to}{days}, les livraisons hors tableau de bord sont {action}{channels}.",
    s_away: "{applies} : une personne qui n'est pas à la maison le reçoit à son arrivée{wait}.",
    s_presence_people: "{who} qui {where} {zone} : push, popup, courriel et boîte de réception sont {then}",
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
    presence_channels: "Canaux couverts (aucun choisi : push, popup, courriel, boîte de réception)",
    zone: "Zone",
    presence_when: "Push, popup, courriel, boîte de réception : quand le destinataire",
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
    s_quiet_entity: "{applies} : tant que {entity} est allumé, les livraisons hors tableau de bord sont {action}{channels}.",
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
    intro: "Las reglas cambian cómo se entregan los mensajes: cuándo pueden llegar, quién más los recibe y con qué frecuencia. Se aplica cada regla que encaja con un mensaje.",
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
    channel_names: { push: "Push", popup: "Ventana", speak: "Voz", persistent: "Notificación persistente", mail: "Correo", inbox: "Bandeja de entrada" },
    after: "Escalar tras (minutos)",
    channels: "Canales",
    channels_reminder: "Limitar a estos canales (ninguno elegido: todos)",
    channels_quiet: "Limitar a estos canales (ninguno elegido: todos menos el aviso)",
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
    entity_switch_hint: "Desactívalo para pausar la regla y actívalo para usarla de nuevo, también desde una automatización, por ejemplo para activar reglas de vacaciones. Solo si dentro de la regla hace lo mismo con una condición.",
    max_wait: "Esperar la llegada (minutos, 0: mientras exista el mensaje)",
    when: "Usar cuando",
    whens: WHENS.es,
    channels_from: "Los canales vienen de",
    targets_from: "Los destinatarios vienen de",
    cf: { policy: "Esta política (los canales de abajo)", call: "La llamada (los mismos canales)", failed: "La llamada, solo los canales que no llegaron a nadie" },
    tf: { policy: "Esta política (los destinatarios de abajo)", call: "La llamada (los mismos destinatarios)" },
    people_target: "Personas: push, ventana, correo y bandeja de entrada",
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
    type_desc: {"get_through": "Deja pasar los mensajes que encaja más allá de las horas de silencio y los resúmenes para las personas afectadas. No envía nada: solo cambia cómo llega un mensaje a quienes lo reciben igualmente. Para llegar a otras personas, añade una regla Entregar.", "escalation": "Si nadie confirma en el tiempo, el mensaje se entrega también por los canales y a los destinos que elijas.", "reminder": "Mientras nadie confirma, el mensaje se repite a intervalos, hasta un máximo.", "quiet_hours": "Entre dos horas del día, las entregas fuera del panel se envían en silencio, se retienen hasta el final o se descartan.", "presence": "Retiene o descarta una entrega según dónde está la gente: para cada destinatario en push, ventana, correo y bandeja de entrada, para el hogar en los altavoces.", "fallback": "Si la primera entrega no llegó a nadie, el mensaje se entrega en otro sitio: por otros canales o a otras personas por los mismos canales.", "summarize": "Los mensajes que coinciden se retienen en todos los canales, el aviso incluido, y se envía un solo resumen.", "deliver": "Los mensajes que coinciden también se entregan al instante a la audiencia y por los canales que elijas."},
    apply_label: "Se aplica a los mensajes",
    apply_auto: "Automáticamente",
    apply_auto_hint: "Cada mensaje cuya gravedad y etiqueta coinciden recibe esta política. Una lista vacía coincide con todo.",
    apply_manual: "Manualmente",
    apply_manual_hint: "Solo una llamada que nombra esta política la recibe. La gravedad y la etiqueta del mensaje no importan.",
    manual_how: "Nómbrala en una llamada:",
    manual_note: "Una llamada que nombra una política usa solo esa, no las automáticas. policy: none desactiva todas las políticas para una llamada.",
    badge_manual: "manual",
    lane_calm: "Mantener la calma",
    lane_calm_hint: "Reglas que retienen mensajes, los envían en silencio o los agrupan en un resumen. Si dos discrepan, gana la más tranquila.",
    band: "Siempre pasa",
    band_hint: "Estos mensajes nunca se resumen y las horas de silencio no se aplican a las personas afectadas. Quién los recibe depende del mensaje original (por ejemplo personas nombradas, los admins, todos en casa).",
    lane_arrive: "Asegurar que llegue",
    lane_arrive_hint: "Reglas que envían mensajes adicionales, por ejemplo cuando no se localizó a los destinatarios originales o nadie reaccionó. Se aplican todas las reglas que encajan.",
    lane_named: "Solo si se nombra",
    lane_named_hint: "Solo se usan cuando una automatización o una regla de vigilancia las nombra.",
    x_summary_every: "Resumen cada {n} min",
    x_summary_at: "Resumen a las {time}",
    x_quiet: "{from}–{to}: {action}{channels}",
    x_quiet_entity: "Mientras {entity} está activado: {action}{channels}",
    x_act_quiet: "enviar en silencio",
    x_act_wait: "retener hasta el final",
    x_act_drop: "descartar",
    x_away_hold: "Retener hasta que la persona esté en {zone}",
    x_home_hold: "Retener hasta que la persona salga de {zone}",
    x_away_drop: "Descartar si la persona no está en {zone}",
    x_home_drop: "Descartar si la persona está en {zone}",
    x_speak_nobody: "Voz solo si hay alguien en {zone}",
    x_speak_somebody: "Voz solo si no hay nadie en {zone}",
    x_through: "Ignora las horas de silencio y los resúmenes",
    x_through_for: "Ignora las horas de silencio y los resúmenes para {who}",
    x_deliver: "Envía también: {channels}",
    x_escalation: "Tras {n} min: {channels}",
    x_reminder: "Cada {n} min, como mucho {m} veces",
    x_fallback: "Si no se localizó a nadie: {channels}",
    x_only_if: "solo mientras {entity} esté en {state}",
    d_messages: "Qué mensajes",
    d_does: "Qué hace",
    ck_close: "Cerrar",
    help_close: "Cerrar",
    w_all: "Todos los mensajes",
    w_severity: "Nivel: {list}",
    w_tag: "Etiqueta: {list}",
    w_not: "excepto {list}",
    w_named: "Solo si se nombra",
    col_policy: "Regla",
    col_messages: "Qué mensajes",
    col_does: "Qué hace",
    lane_empty: "Ninguna todavía.",
    turn_off: "Desactivar",
    turn_on: "Activar",
    not_tags: "Excepto etiquetas, separadas por comas",
    only_if: "Solo si",
    only_if_hint: "La regla solo actúa mientras esto se cumple. Si no se puede leer el estado, por ejemplo porque el dispositivo está desconectado, las reglas que retienen o silencian no hacen nada y las que envían siguen enviando.",
    oi_entity: "Entidad",
    oi_state: "Estado",
    oi_none: "Siempre (sin condición)",
    faster: "Más a menudo mientras",
    faster_every: "Entonces repetir cada (minutos)",
    alongside: "Funciona junto a otros recordatorios",
    alongside_hint: "Desactivado: los recordatorios de un mismo canal comparten el ritmo más corto, cada uno con su propio recuento.",
    holds_heading: "Interacción con las políticas «Dejar pasar»",
    holds_anyway: "Ignorar las políticas «Dejar pasar»",
    holds_anyway_hint: "Ninguna entrada Siempre pasa deja pasar mensajes más allá de esta regla.",
    holds_anyway_warning: "Atención: los mensajes críticos también se {what}. Actívalo solo si conoces el efecto.",
    holds_what: { quiet: "enviarán en silencio", wait: "retendrán", drop: "descartarán", summarize: "resumirán" },
    covers: "Afecta a",
    covers_everyone: "Todos a quienes llega",
    covers_only: "Solo estos",
    covers_audiences: "Audiencias",
    covers_recipients: "Personas y altavoces",
    s_through: "{applies}: ignora las horas de silencio y los resúmenes{who}.",
    s_through_everyone: "",
    s_through_for: " para {who}",
    not_overlap: "Excepto repite algo de Para ({list}): esos mensajes nunca reciben esta regla.",
    unsaved_confirm: "Tienes cambios sin guardar. ¿Cerrar de todos modos?",
    s_not_for: " Excepto {list}.",
    s_only_if: " Solo mientras {entity} esté en {state}.",
    s_faster: " Mientras {entity} esté en {state}: cada {n} min.",
    s_alongside: " Funciona junto a otros recordatorios.",
    s_holds_anyway: " No pasa nada, ni siquiera Siempre pasa.",
    links_note: "Deja fuera {what} mientras {other} está activada.",
    overlap_calm: "Donde ella y {names} encajan, cuenta la más tranquila.",
    overlap_send: "También actúa en los mismos mensajes: {names}.",
    cl_title: "Las reglas se han rediseñado – revisa el nuevo comportamiento",
    cl_intro: "Abajo están las reglas que hemos ajustado automáticamente para mantener el comportamiento anterior. Decide para cada una si conservas el ajuste. Es una tarea única tras el rediseño de las reglas.",
    cl_links: "{name} deja fuera {what} mientras {other} está activada, como antes de la actualización.",
    cl_never: "{name} no hace nada por ahora y así funciona como antes de la actualización: deja fuera todos sus mensajes.",
    cl_holds: "{name} también retiene los mensajes críticos, como antes de la actualización.",
    cl_not_for: "{name} deja ahora fuera {what} y así funciona como antes de la actualización.",
    cl_sev: "los mensajes de nivel {list}",
    cl_tag: "los mensajes con la etiqueta {list}",
    cl_sev_tag: "los mensajes de nivel {sev} con la etiqueta {tags}",
    cl_and: " y ",
    cl_or: " o ",
    cl_keep: "Dejarlo así",
    cl_act: "Aplicarla también a ellos",
    cl_through: "Dejar pasar los mensajes críticos",
    cl_dismiss: "Ocultar la lista",
    cl_kept: "Mantenido",
    cl_changed: "Cambiado",
    ck_title: "Probar las reglas",
    ck_intro: "Prueba un mensaje: ves quién lo recibiría, cuándo y por qué. No se envía nada.",
    ck_severity: "Nivel",
    ck_tag: "Etiqueta",
    ck_channels: "Canales",
    ck_banner: "Aviso del panel",
    ck_audience: "Enviado a",
    ck_source: "Viene de",
    ck_source_call: "Una automatización o un script",
    ck_time: "A las",
    ck_home: "En casa",
    ck_ack: "Confirmado tras (min",
    ck_ack_hint: "Vacío: nadie confirma.",
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
    s_quiet_hours: "{applies}: entre {from} y {to}{days}, las entregas fuera del panel se {action}{channels}.",
    s_away: "{applies}: quien no está en casa lo recibe al llegar{wait}.",
    s_presence_people: "{who} que {where} {zone}: push, ventana, correo y bandeja de entrada se {then}",
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
    presence_channels: "Canales que cubre (ninguno elegido: push, ventana, correo, bandeja de entrada)",
    zone: "Zona",
    presence_when: "Push, ventana, correo, bandeja de entrada: cuando el destinatario",
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
    s_quiet_entity: "{applies}: mientras {entity} esté encendido, las entregas fuera del panel se {action}{channels}.",
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
.hu-page .pol-intro { max-width: 72ch; margin-bottom: 12px; }
.hu-page .pol-bar { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 16px; }
.hu-page .pol-bar button, .hu-page .tl-actions button { display: inline-flex; align-items: center; gap: 8px; }
.hu-page .pol-bar ha-icon, .hu-page .tl-actions ha-icon { --mdc-icon-size: 20px; }
.hu-page .pol-bar button[aria-expanded="true"] { border-color: var(--primary-color); color: var(--primary-color); }
.hu-page section.tl-list, .hu-page section.cl-card, .hu-page section.ck-card { padding: 0; overflow: hidden; --tl-cols: minmax(0, 1.5fr) minmax(0, 1fr) minmax(0, 1.3fr); }
.hu-page .tl-lead .badge { white-space: nowrap; flex: none; }
.hu-page section.tl-list .tl-cell { white-space: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.35; }
.hu-page .lane-head { display: flex; align-items: center; gap: 12px; padding: 14px 16px 10px; }
.hu-page .lane-head .tl-title { margin: 0; }
.hu-page .lane-hint { color: var(--secondary-text-color); font-size: 13px; line-height: 1.4; max-width: 70ch; }
.hu-page .lane-icon { display: inline-flex; align-items: center; justify-content: center; flex: none; width: 36px; height: 36px; border-radius: 10px; background: color-mix(in srgb, var(--lane-color) 16%, transparent); color: var(--lane-color); --mdc-icon-size: 20px; }
.hu-page .lane-count { margin-left: auto; flex: none; min-width: 28px; height: 28px; padding: 0 8px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; background: var(--hu-fill); color: var(--secondary-text-color); }
.hu-page section { --lane-color: var(--primary-color); }
.hu-page section.lane.calm { --lane-color: var(--success-color, #43a047); }
.hu-page section.lane.band { --lane-color: var(--warning-color, #ffa600); }
.hu-page section.lane.arrive { --lane-color: var(--info-color, #039be5); }
.hu-page section.lane.named { --lane-color: var(--secondary-text-color); }
.hu-page section.cl-card { --lane-color: var(--warning-color, #ffa600); }
.hu-page .tl-list .tl-lead ha-icon { color: var(--lane-color); }
.hu-page .lane-head + .tl-head + .tl-item, .hu-page .lane-head + .tl-item { border-top: 1px solid var(--divider-color); }
.hu-page .pol-sentence { margin: 0 0 12px; font-size: 15px; line-height: 1.5; max-width: 72ch; }
.hu-page .pol-note { display: flex; align-items: flex-start; gap: 8px; margin: 0 0 12px; padding: 8px 12px; border-radius: 8px; background: var(--card-background-color); border: 1px solid var(--divider-color); font-size: 14px; --mdc-icon-size: 18px; }
.hu-page .pol-note ha-icon { color: var(--secondary-text-color); margin-top: 1px; }
.hu-page .pol-pill { display: inline-flex; align-items: center; gap: 8px; max-width: 100%; padding: 2px 2px 2px 10px; border-radius: 8px; background: var(--card-background-color); border: 1px solid var(--divider-color); }
.hu-page .pol-pill code { font-size: 12px; overflow-wrap: anywhere; }
.hu-page .pol-switch-hint { margin-top: 6px; }
.hu-page .pol-sub { margin: 18px 0 6px; padding-top: 12px; border-top: 1px solid var(--divider-color); font-size: 14px; font-weight: 600; color: var(--primary-text-color); }
.hu-page .pol-caution { display: flex; align-items: flex-start; gap: 8px; margin: 6px 0 12px; color: var(--error-color, #db4437); }
.hu-page .pol-warn { display: flex; align-items: flex-start; gap: 8px; margin: 6px 0 12px; padding: 8px 12px; border-radius: 8px; color: var(--warning-color, #ffa600); background: color-mix(in srgb, var(--warning-color, #ffa600) 12%, transparent); border: 1px solid color-mix(in srgb, var(--warning-color, #ffa600) 40%, transparent); font-size: 14px; --mdc-icon-size: 18px; }
.hu-page .pol-pill .pol-copy { min-height: 32px; padding: 0 10px; font-size: 13px; }
.hu-page .cl-row { display: grid; grid-template-columns: 24px minmax(0, 1fr) auto; gap: 12px; align-items: center; padding: 12px 16px; border-top: 1px solid var(--divider-color); --mdc-icon-size: 20px; }
.hu-page .cl-row ha-icon { color: var(--lane-color); }
.hu-page .cl-row.done { opacity: .7; }
.hu-page .cl-row.done ha-icon { color: var(--success-color, #43a047); }
.hu-page .cl-text { font-size: 14px; line-height: 1.45; overflow-wrap: anywhere; }
.hu-page .cl-buttons { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.hu-page section.cl-card > .tl-actions, .hu-page section.ck-card > .tl-actions { padding: 0 16px 14px; margin-top: 4px; }
.hu-page button.link { background: none; border-color: transparent; color: var(--primary-color); padding: 0 4px; }
.hu-page .ck-grid, .hu-page section.ck-card > fieldset { margin: 0 16px 12px; }
.hu-page .ck-grid { padding-top: 4px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); align-items: start; }
.hu-page .ck-grid .field { min-width: 0; }
.hu-page .ck-grid input, .hu-page .ck-grid select { min-width: 0; width: 100%; box-sizing: border-box; }
.hu-page input[type="datetime-local"] { box-sizing: border-box; height: 44px; padding: 0 12px; border-radius: 8px; border: 1px solid var(--hu-line); background: var(--hu-fill); color: var(--primary-text-color); font: inherit; width: 100%; }
.hu-page fieldset.pills { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 12px 12px; }
.hu-page fieldset.pills.scroll { max-height: 220px; overflow: auto; }
.hu-page fieldset.pills label.inline { min-height: 36px; gap: 8px; padding: 0 14px 0 10px; border-radius: 18px; border: 1px solid var(--hu-line); background: var(--hu-fill); cursor: pointer; }
.hu-page fieldset.pills label.inline:has(input:checked) { border-color: var(--primary-color); background: color-mix(in srgb, var(--primary-color) 16%, var(--card-background-color)); }
.hu-page fieldset.pills label.inline input { width: 16px; height: 16px; margin: 0; }
.hu-page dialog.hu-modal { width: min(920px, calc(100vw - 32px)); max-height: calc(100dvh - 48px); padding: 0; border: 1px solid var(--divider-color); border-radius: 16px; background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 12px 40px rgba(0, 0, 0, .35); overflow: hidden; }
.hu-page dialog.hu-modal[open] { display: flex; flex-direction: column; }
.hu-page dialog.hu-modal::backdrop { background: rgba(0, 0, 0, .55); }
.hu-page .hu-modal-head { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--divider-color); }
.hu-page .hu-modal-head .tl-title { margin: 0; }
.hu-page .hu-close { margin-left: auto; flex: none; width: 44px; height: 44px; padding: 0; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; }
.hu-page .hu-modal-body { overflow: auto; padding: 8px 0 16px; }
.hu-page .hu-modal-body .ck-card .tl-grid, .hu-page .hu-modal-body .ck-card > fieldset { margin: 0 16px 12px; }
.hu-page .hu-modal-body .ck-card > .tl-actions { padding: 0 16px; }
.hu-page .hu-modal-body > .hu-page { padding: 0 16px; }
.hu-page .hu-modal-body > .pol-editor { padding: 8px 20px 4px; }
.hu-page .pol-editor .row { position: sticky; bottom: -16px; background: var(--card-background-color); padding: 10px 0; z-index: 1; }
@media (max-width: 600px) {
  .hu-page dialog.hu-modal { width: 100vw; max-width: 100vw; height: 100dvh; max-height: 100dvh; border-radius: 0; border: 0; }
}
.hu-page .ck-answer { margin: 4px 16px 16px; padding: 4px 0 0; border-top: 1px solid var(--divider-color); }
.hu-page .ck-step { display: grid; grid-template-columns: 76px minmax(0, 1fr); gap: 12px; position: relative; padding: 12px 0 4px; }
.hu-page .ck-step::before { content: ""; position: absolute; left: 37px; top: 34px; bottom: -8px; width: 2px; background: var(--divider-color); }
.hu-page .ck-step:last-of-type::before { display: none; }
.hu-page .ck-when { white-space: nowrap; font-variant-numeric: tabular-nums; font-weight: 600; font-size: 13px; text-align: center; padding: 3px 0; border-radius: 12px; background: var(--hu-fill); height: fit-content; position: relative; z-index: 1; }
.hu-page .ck-title { font-weight: 600; margin-bottom: 4px; }
.hu-page ul.ck-lines { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; }
.hu-page .ck-line { display: flex; align-items: flex-start; gap: 8px; font-size: 14px; line-height: 1.4; overflow-wrap: anywhere; --mdc-icon-size: 18px; }
.hu-page .ck-line ha-icon { flex: none; margin-top: 1px; }
.hu-page .ck-line.sent ha-icon { color: var(--success-color, #43a047); }
.hu-page .ck-line.quiet ha-icon, .hu-page .ck-line.held ha-icon { color: var(--warning-color, #ffa600); }
.hu-page .ck-line.skipped ha-icon { color: var(--secondary-text-color); }
.hu-page .ck-line.failed ha-icon { color: var(--error-color, #db4437); }
.hu-page h3.sec { font-size: 15px; margin: 20px 0 6px; padding-top: 12px; border-top: 1px solid var(--divider-color); }
.hu-page .summary { background: var(--hu-fill); border-radius: 10px; padding: 10px 12px; margin: 16px 0 12px; }
.hu-page .summary .sentence { margin: 4px 0; }
.hu-page label.radio { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; cursor: pointer; }
.hu-page label.radio input { margin-top: 4px; width: 20px; height: 20px; }
.hu-page .type-desc { margin-top: 0; }
@container (max-width: 520px) {
  .hu-page .cl-row { grid-template-columns: 24px minmax(0, 1fr); }
  .hu-page .cl-buttons, .hu-page .cl-row > .badge { grid-column: 2; justify-content: flex-start; }
}
@media (max-width: 520px) {
  .hu-page .cl-row { grid-template-columns: 24px minmax(0, 1fr); }
  .hu-page .cl-buttons, .hu-page .cl-row > .badge { grid-column: 2; justify-content: flex-start; }
  .hu-page .lane-head { padding: 12px 12px 8px; }
}
`;

// The page order: the lanes and the band (DESIGN §25.2). Which policies act does not depend on it.
const LANES = [
  { id: "calm", types: ["summarize", "quiet_hours", "presence"] },
  { id: "band", types: ["get_through"] },
  { id: "arrive", types: ["deliver", "escalation", "reminder", "fallback"] },
];
const TYPES = LANES.flatMap((lane) => lane.types);
const CALM = LANES[0].types;
const PRESENCE_CHANNELS = ["push", "popup", "mail", "inbox", "speak"];
const PEOPLE_CHANNELS = ["push", "popup", "mail", "inbox"];
const SEVERITIES = ["passive", "info", "warning", "critical"];
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const POLICY_CHANNELS = ["push", "popup", "speak", "persistent", "mail", "inbox"];
const TARGET_CHANNELS = ["push", "popup", "speak", "mail", "inbox"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues(type = "escalation") {
  return {
    name: "",
    type,
    severities: [],
    tags: "",
    not_tags: "",
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
    inbox_audience: "",
    inbox_recipients: [],
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
  for (const key of ["severities", "channels", "days", "links", "covers_audiences", "covers_recipients"]) values[key] = [...(data[key] || [])];
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
    if (splitTags(values.not_tags).length) data.not_tags = splitTags(values.not_tags);
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
      if (values.channels.length) data.channels = [...values.channels];
      break;
    case "presence": {
      Object.assign(data, { max_wait: values.max_wait || 0, after_wait: values.after_wait || "send" });
      const covered = PRESENCE_CHANNELS.filter((c) => values.channels.includes(c));
      if (covered.length && !(covered.length === PEOPLE_CHANNELS.length && PEOPLE_CHANNELS.every((c) => covered.includes(c)))) data.channels = covered;
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
  return text + tails(values, t);
}

// The red caution under "Ignore 'get through' policies": what happens to critical messages then.
export function holdsWarning(values, t) {
  const what = t.holds_what[values.type === "summarize" ? "summarize" : values.action] || t.holds_what.quiet;
  return fill(t.holds_anyway_warning, { what });
}

// What 2.0 adds to every sentence: Not for tags, Only if, and the type's extras.
function tails(values, t) {
  let out = "";
  if (values.apply !== "manual") {
    const not = splitTags(values.not_tags).map((x) => `#${x}`);
    if (not.length) out += fill(t.s_not_for, { list: not.join(", ") });
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
      const only = values.channels.length ? fill(t.s_in_channels, { channels }) : "";
      if (values.quiet_entity) return fill(t.s_quiet_entity, { applies, entity: values.quiet_entity, action: t[`a_${values.action}`], channels: only });
      const days = values.days.length ? fill(t.s_days, { days: values.days.map((d) => t.days_names[d]).join(", ") }) : "";
      return fill(t.s_quiet_hours, { applies, from: String(values.from_time).slice(0, 5), to: String(values.to_time).slice(0, 5), days, action: t[`a_${values.action}`], channels: only });
    }
    case "presence":
      return presenceSentence(values, t, applies);
    case "fallback":
      return fill(t.s_fallback, { applies, when: t[`w_${values.when}`], channels });
    case "deliver":
      return fill(t.s_deliver, { applies, channels });
    case "get_through": {
      // Objective: what the entry does, and for whom only when it is limited (D-238).
      const names = [...values.covers_audiences.map(audienceName), ...values.covers_recipients.map(recipientName)].join(", ");
      const who = values.covers === "only" ? fill(t.s_through_for, { who: names || "—" }) : "";
      return fill(t.s_through, { applies, who });
    }
    default:
      return values.summary_mode === "at"
        ? fill(t.s_summarize_at, { applies, time: String(values.summary_at).slice(0, 5) })
        : fill(t.s_summarize_every, { applies, n: values.summary_every });
  }
}

// Who a row of the checker is about. A push row names the phone as well as the person, so two
// phones of one person do not look like duplicates: "Anna (iPhone)".
export function rowWho(row, choices, label) {
  const person = row.person ? label(row.person, choices) : "";
  const recipient = String(row.recipient || "");
  if (recipient.startsWith("device:")) {
    const device = label(recipient.slice("device:".length), choices);
    return person ? `${person} (${device})` : device;
  }
  return person || (recipient ? label(recipient, choices) : "") || "—";
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

const TYPE_ICONS = {
  summarize: "mdi:text-box-multiple-outline",
  quiet_hours: "mdi:weather-night",
  presence: "mdi:home-account",
  get_through: "mdi:bell-ring-outline",
  deliver: "mdi:send-outline",
  escalation: "mdi:arrow-up-bold-circle-outline",
  reminder: "mdi:repeat",
  fallback: "mdi:speaker-wireless",
};
const LANE_ICONS = { calm: "mdi:weather-night", band: "mdi:bell-ring-outline", arrive: "mdi:send-outline", named: "mdi:at" };
const RESULT_ICONS = { sent: "mdi:check-circle-outline", quiet: "mdi:bell-sleep-outline", held: "mdi:pause-circle-outline", skipped: "mdi:minus-circle-outline", failed: "mdi:alert-circle-outline" };

// The "Which messages" column: For and Not for tags in a few words.
export function whichText(values, t) {
  if (values.apply === "manual") return t.w_named;
  const parts = [];
  if (values.severities.length) parts.push(fill(t.w_severity, { list: values.severities.map((x) => t.severity_names[x]).join(", ") }));
  const tags = splitTags(values.tags);
  if (tags.length) parts.push(fill(t.w_tag, { list: tags.join(", ") }));
  if (!parts.length) parts.push(t.w_all);
  const not = splitTags(values.not_tags).map((x) => `#${x}`);
  if (not.length) parts.push(fill(t.w_not, { list: not.join(", ") }));
  return parts.join(" · ");
}

// What Not for repeats from For: those messages never get the policy, so the editor warns.
export function notOverlap(values, t) {
  const tags = splitTags(values.not_tags).filter((x) => splitTags(values.tags).includes(x)).map((x) => `#${x}`);
  return tags;
}

// "messages with severity Warning, Critical or messages with the tag digest": what a policy leaves out.
export function leftOut(severities, tags, t, joiner = "cl_or") {
  const parts = [];
  if (severities.length) parts.push(fill(t.cl_sev, { list: severities.map((x) => t.severity_names[x]).join(", ") }));
  if (tags.length) parts.push(fill(t.cl_tag, { list: tags.join(", ") }));
  return parts.join(t[joiner]);
}

// What a linked policy takes: its severities AND its tags.
export function takenBy(linked, t) {
  const data = linked.data || {};
  const severities = data.severities || [];
  const tags = data.tags || [];
  if (severities.length && tags.length) return fill(t.cl_sev_tag, { sev: severities.map((x) => t.severity_names[x]).join(", "), tags: tags.join(", ") });
  return leftOut(severities, tags, t);
}

// The "What it does" column: the sentence without who it applies to.
// The "What it does" column: a few words with the policy's own values, short enough for one row.
// The full sentence is in the opened row.
export function doesText(values, t, labels = {}) {
  const audienceName = labels.audience || ((v) => v);
  const recipientName = labels.recipient || ((v) => v);
  const channels = () => (values.channels_from === "call" ? t.s_channels_call : values.channels_from === "failed" ? t.s_channels_failed : values.channels.map((c) => t.channel_names[c]).join(", ") || "—");
  const zone = values.zone === "zone.home" ? "Home" : String(values.zone).replace(/^zone\./, "");
  let text;
  switch (values.type) {
    case "summarize":
      text = values.summary_mode === "at" ? fill(t.x_summary_at, { time: String(values.summary_at).slice(0, 5) }) : fill(t.x_summary_every, { n: values.summary_every });
      break;
    case "quiet_hours": {
      const action = t[`x_act_${values.action}`];
      const only = values.channels.length ? fill(t.s_in_channels, { channels: channels() }) : "";
      text = values.quiet_entity ? fill(t.x_quiet_entity, { entity: values.quiet_entity, action, channels: only }) : fill(t.x_quiet, { from: String(values.from_time).slice(0, 5), to: String(values.to_time).slice(0, 5), action, channels: only });
      break;
    }
    case "presence": {
      const covered = values.channels.length ? values.channels : PEOPLE_CHANNELS;
      if (covered.some((c) => PEOPLE_CHANNELS.includes(c))) {
        const key = `x_${values.presence_when === "in" ? "home" : "away"}_${values.presence_then === "drop" ? "drop" : "hold"}`;
        text = fill(t[key], { zone });
      } else {
        text = fill(values.household_who === "somebody" ? t.x_speak_somebody : t.x_speak_nobody, { zone });
      }
      break;
    }
    case "get_through": {
      const who = [...values.covers_audiences.map(audienceName), ...values.covers_recipients.map(recipientName)].join(", ");
      text = values.covers === "only" ? fill(t.x_through_for, { who: who || "—" }) : t.x_through;
      break;
    }
    case "deliver":
      text = fill(t.x_deliver, { channels: channels() });
      break;
    case "escalation":
      text = fill(t.x_escalation, { n: values.after_minutes, channels: channels() });
      break;
    case "reminder":
      text = fill(t.x_reminder, { n: values.every_minutes, m: values.max_count });
      break;
    default:
      text = fill(t.x_fallback, { channels: channels() });
  }
  if (values.oi_entity && values.oi_state) text += ` · ${fill(t.x_only_if, { entity: values.oi_entity, state: values.oi_state })}`;
  return text;
}

// Whether the check list has items of existing policies and every one of them is answered.
export function checklistAnswered(items, policies) {
  const shown = (items || []).filter((i) => (policies || []).some((p) => p.subentry_id === i.policy));
  return shown.length > 0 && shown.every((i) => i.state !== "open");
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  // Multiple choices as pill toggles; the checkbox stays, so the state is not shown by color only.
  const pills = (...args) => {
    const box = ui.chips(...args);
    box.classList.add("pills");
    return box;
  };
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own, values }
  let message = "";
  let checked = null; // the last answer of the checker
  let openKey = null; // the policy whose row is open
  let checkDialog = null; // the open "Test policies" dialog
  const ask = { severity: "warning", tag: "", rule: "", at: "", home: {}, ack: "", channels: ["banner", "push"], audience: "" };
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const linkText = (ids) =>
    ids
      .map((id) => data.policies.find((p) => p.subentry_id === id))
      .filter(Boolean)
      .map((l) => fill(t.links_note, { what: takenBy(l, t), other: `“${l.name}”` }))
      .join(" ");
  const policyName = (id) => (data.policies.find((p) => p.subentry_id === id) || {}).name || id;
  const labels = () => ({ audience: (v) => ui.audienceLabel(v, data.choices), recipient: (v) => ui.recipientLabel(v, data.choices) });

  // The lanes as tables like the other configuration pages: an icon and the name, which messages,
  // what it does. A row opens its details: the sentence, the switch ID, the policies it skips for, and
  // the actions (DESIGN §25.9).
  function lanes() {
    const out = [];
    const titles = { calm: [t.lane_calm, t.lane_calm_hint], band: [t.band, t.band_hint], arrive: [t.lane_arrive, t.lane_arrive_hint], named: [t.lane_named, t.lane_named_hint] };
    for (const id of ["calm", "band", "arrive", "named"]) {
      const mine = data.policies.filter((p) => laneOf(p) === id);
      if (id === "named" && !mine.length) continue;
      const [title, hint] = titles[id];
      const box = el("section", { className: `tl-list lane ${id}` });
      box.append(
        el("div", { className: "lane-head" }, [
          el("span", { className: "lane-icon" }, [el("ha-icon", { icon: LANE_ICONS[id] })]),
          el("div", {}, [el("h2", { className: "tl-title", textContent: title }), el("div", { className: "lane-hint", textContent: hint })]),
          el("span", { className: "lane-count", textContent: String(mine.length) }),
        ]),
      );
      if (mine.length) box.append(ui.tableHead([t.col_policy, t.col_messages, t.col_does]));
      for (const policy of mine) box.append(policyRow(policy));
      if (!mine.length) box.append(el("div", { className: "tl-empty", textContent: t.lane_empty }));
      out.push(box);
    }
    return out;
  }

  function policyRow(policy) {
    const values = fromPolicy(policy);
    const id = `hu-pol-${policy.subentry_id}`;
    const isOpen = openKey === policy.subentry_id;
    const lead = [el("ha-icon", { icon: TYPE_ICONS[values.type] || "mdi:tune" }), el("span", { className: "tl-name", textContent: policy.name })];
    if (!values.enabled) lead.push(el("span", { className: "badge", textContent: t.disabled }));
    const messages = whichText(values, t);
    const does = doesText(values, t, labels());
    const { item } = ui.tableRow({
      id,
      lead,
      cells: [
        { label: t.col_messages, node: el("span", { textContent: messages, title: messages }) },
        { label: t.col_does, node: el("span", { textContent: does, title: does }), muted: true },
      ],
      open: isOpen,
      dim: !values.enabled,
      label: `${policy.name}, ${t.types[values.type]}: ${messages}. ${does}`,
      onToggle: () => {
        openKey = isOpen ? null : policy.subentry_id;
        render();
        root.querySelector(`[aria-controls="${id}"]`)?.focus();
      },
      body: isOpen ? policyDetails(policy, values) : null,
    });
    return item;
  }

  function policyDetails(policy, values) {
    const body = el("div", {});
    // The opened row shows the full details once; the column has the short form, the editor the
    // description of the type.
    const full = sentence(values, t, labels());
    const lead = `${appliesText(values, t)}: `;
    const does = full.startsWith(lead) ? full.slice(lead.length) : full;
    if (values.links.length) body.append(el("div", { className: "pol-note" }, [el("ha-icon", { icon: "mdi:link-variant" }), el("span", { textContent: linkText(values.links) })]));
    const pairs = [
      [t.d_messages, whichText(values, t)],
      [t.d_does, does.charAt(0).toUpperCase() + does.slice(1)],
      [t.type, t.types[values.type]],
    ];
    if (policy.entity_id) {
      const copy = el("button", { type: "button", className: "pol-copy", textContent: s.common.copy });
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(policy.entity_id);
          copy.textContent = s.common.copied;
        } catch (err) {
          copy.textContent = s.common.copy_failed;
        }
      });
      pairs.push([t.entity_id, el("span", {}, [el("span", { className: "pol-pill" }, [el("code", { textContent: policy.entity_id }), copy]), el("div", { className: "lane-hint pol-switch-hint", textContent: t.entity_switch_hint })])]);
    }
    body.append(ui.facts(pairs));
    const edit = el("button", { type: "button", className: "primary", textContent: s.common.edit });
    edit.addEventListener("click", () => openEditor(policy, fromPolicy(policy)));
    const flip = el("button", { type: "button", textContent: values.enabled ? t.turn_off : t.turn_on });
    flip.addEventListener("click", async () => {
      const result = await ui.runFlow(hass, data.entry_id, "policy", policy.subentry_id, toFlowData({ ...values, enabled: !values.enabled }));
      message = result.ok ? "" : Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      await load();
    });
    body.append(el("div", { className: "tl-actions" }, [edit, flip]));
    return body;
  }

  // The check list after the 2.0 conversion (DESIGN §25.7): one row per item, its answer at the end.
  function checklist() {
    const items = (data.conversion_items || []).filter((i) => data.policies.some((p) => p.subentry_id === i.policy));
    if (!items.length) return [];
    const open = items.filter((i) => i.state === "open").length;
    const box = el("section", { className: "cl-card" });
    box.append(
      el("div", { className: "lane-head" }, [
        el("span", { className: "lane-icon warn" }, [el("ha-icon", { icon: "mdi:clipboard-check-outline" })]),
        el("div", {}, [el("h2", { className: "tl-title", textContent: t.cl_title }), el("div", { className: "lane-hint", textContent: t.cl_intro })]),
        el("span", { className: "lane-count", textContent: String(open) }),
      ]),
    );
    for (const item of items) {
      const policy = data.policies.find((p) => p.subentry_id === item.policy);
      const added = item.added || {};
      const linked = (policy.data.links || []).map((id) => data.policies.find((p) => p.subentry_id === id)).filter(Boolean);
      const what = item.kind === "links" ? linked.map((l) => takenBy(l, t)).join(t.cl_or) : leftOut(added.not_severities || [], added.not_tags || [], t);
      const other = linked.map((l) => `“${l.name}”`).join(", ");
      const text = { not_for: t.cl_not_for, links: t.cl_links, never_acts: t.cl_never, holds_anyway: t.cl_holds }[item.kind] || "";
      const row = el("div", { className: `cl-row${item.state === "open" ? "" : " done"}` }, [
        el("ha-icon", { icon: item.state === "open" ? (item.kind === "never_acts" ? "mdi:sleep" : item.kind === "holds_anyway" ? "mdi:shield-outline" : "mdi:filter-outline") : "mdi:check" }),
        el("div", { className: "cl-text", textContent: fill(text, { name: `“${policy.name}”`, what, other }) }),
      ]);
      if (item.state === "open") {
        const answer = async (choice) => {
          await hass.callWS({ type: "heads_up/conversion_item", policy: item.policy, kind: item.kind, choice });
          await load();
        };
        const keep = el("button", { type: "button", textContent: t.cl_keep });
        keep.addEventListener("click", () => answer("keep"));
        const change = el("button", { type: "button", className: "primary", textContent: item.kind === "holds_anyway" ? t.cl_through : t.cl_act });
        change.addEventListener("click", () => answer("change"));
        row.append(el("div", { className: "cl-buttons" }, [keep, change]));
      } else {
        row.append(el("span", { className: "badge", textContent: item.state === "kept" ? t.cl_kept : t.cl_changed }));
      }
      box.append(row);
    }
    const hide = el("button", { type: "button", className: "link", textContent: t.cl_dismiss });
    hide.addEventListener("click", async () => { await hass.callWS({ type: "heads_up/conversion_items_dismiss" }); await load(); });
    box.append(el("div", { className: "tl-actions" }, [hide]));
    return [box];
  }

  // The checker "What happens to a message?" (DESIGN §25.8): nothing is sent.
  // A dialog over the page, closed by its button, Escape or a click beside it.
  function modal(title, intro, icon, requestClose = null) {
    const dialog = el("dialog", { className: "hu-modal" });
    const ask = () => (requestClose ? requestClose() : dialog.close());
    const close = el("button", { type: "button", className: "hu-close" }, [el("ha-icon", { icon: "mdi:close" })]);
    close.setAttribute("aria-label", t.ck_close);
    close.addEventListener("click", ask);
    // Escape asks too, so unsaved changes are not lost by accident.
    dialog.addEventListener("cancel", (event) => { event.preventDefault(); ask(); });
    const head = el("div", { className: "hu-modal-head" }, [
      el("span", { className: "lane-icon" }, [el("ha-icon", { icon })]),
      el("div", {}, [el("h2", { className: "tl-title", textContent: title }), ...(intro ? [el("div", { className: "lane-hint", textContent: intro })] : [])]),
      close,
    ]);
    const body = el("div", { className: "hu-modal-body" });
    dialog.append(head, body);
    dialog.addEventListener("click", (event) => { if (event.target === dialog) ask(); });
    dialog.addEventListener("close", () => dialog.remove());
    root.append(dialog);
    dialog.showModal();
    return { dialog, body };
  }

  let editorDialog = null;

  function openEditor(own, values) {
    message = "";
    editing = { own, values, start: JSON.stringify(toFlowData(values)) };
    const { dialog, body } = modal(own ? `${t.editing}: ${own.name}` : t.new, "", own ? TYPE_ICONS[values.type] || "mdi:tune" : "mdi:plus", requestCloseEditor);
    editorDialog = { dialog, body };
    dialog.addEventListener("close", () => { editing = null; editorDialog = null; });
    body.append(editor());
  }

  function refreshEditor() {
    if (!editorDialog) return;
    const scroll = editorDialog.body.scrollTop;
    editorDialog.body.replaceChildren(editor());
    editorDialog.body.scrollTop = scroll;
  }

  // Closing by X, Cancel, Escape or a click beside it: ask first when something changed.
  function requestCloseEditor() {
    if (!editorDialog) return;
    const changed = editing && JSON.stringify(toFlowData(editing.values)) !== editing.start;
    if (changed && !window.confirm(t.unsaved_confirm)) return;
    editorDialog.dialog.close();
  }

  function openChecker() {
    const { dialog, body } = modal(t.ck_title, t.ck_intro, "mdi:flask-outline");
    checkDialog = { dialog, body };
    dialog.addEventListener("close", () => { checkDialog = null; });
    body.append(checker());
  }

  async function openHelp() {
    const { body } = modal(t.help_button, "", "mdi:help-circle-outline");
    try {
      const self = new URL(import.meta.url);
      const url = new URL("policy_help.js", self);
      url.search = self.search;
      const help = await import(url.href);
      const code = String(ctx.language || "en").split("-")[0];
      help.mount(body, { t: help.STRINGS[code] || help.STRINGS.en, ui, embedded: true });
    } catch (err) {
      body.append(el("div", { className: "hint problems", textContent: String(err.message || err) }));
    }
  }

  function checker() {
    const box = el("div", { className: "ck-card" });
    const grid = el("div", { className: "tl-grid ck-grid" });
    grid.append(ui.field(t.ck_severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), ask.severity, (v) => { ask.severity = v; })));
    grid.append(ui.field(t.ck_tag, ui.textInput(ask.tag, (v) => { ask.tag = v; })));
    const sources = [{ value: "", label: t.ck_source_call }, ...data.rules.map((r) => ({ value: r.subentry_id, label: r.name }))];
    grid.append(ui.field(t.ck_source, ui.selectInput(sources, ask.rule, (v) => { ask.rule = v; })));
    const audiences = data.choices.audience_choices || [];
    if (!ask.audience && audiences.length) ask.audience = (audiences.find((a) => a.id === "everyone") || audiences[0]).id;
    grid.append(ui.field(t.ck_audience, ui.selectInput(audiences.map((a) => ({ value: a.id, label: a.name })), ask.audience, (v) => { ask.audience = v; })));
    const at = el("input", { type: "datetime-local", value: ask.at });
    at.addEventListener("input", () => { ask.at = at.value; });
    grid.append(ui.field(t.ck_time, at));
    grid.append(ui.field(t.ck_ack, ui.textInput(ask.ack, (v) => { ask.ack = v; }), t.ck_ack_hint));
    box.append(grid);
    box.append(pills(t.ck_channels, ["banner", ...POLICY_CHANNELS].map((c) => ({ value: c, label: c === "banner" ? t.ck_banner : t.channel_names[c] })), ask.channels, (list) => { ask.channels = list; }));
    const persons = data.choices.persons || [];
    if (persons.length) {
      box.append(pills(t.ck_home, persons.map((p) => ({ value: p.id, label: p.name })), persons.filter((p) => ask.home[p.id] !== false).map((p) => p.id), (list) => {
        ask.home = Object.fromEntries(persons.map((p) => [p.id, list.includes(p.id)]));
      }));
    }
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
      if (checkDialog) {
        checkDialog.body.replaceChildren(checker());
        checkDialog.body.querySelector(".ck-answer")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
    box.append(el("div", { className: "tl-actions" }, [run]));
    if (checked) box.append(answer(checked));
    return box;
  }

  function answer(result) {
    const out = el("div", { className: "ck-answer" });
    out.setAttribute("role", "status");
    if (result.error) return out.append(el("div", { className: "hint problems", textContent: result.error })), out;
    const time = (iso) => new Date(iso).toLocaleTimeString(ctx.language, { hour: "2-digit", minute: "2-digit" });
    const who = (row) => rowWho(row, data.choices, ui.recipientLabel);
    const reason = (code) => ctx.fmt.reasonText(code, s);
    const lines = (rows) =>
      el("ul", { className: "ck-lines" }, rows.map((row) => {
        const kind = row.result === "sent" && row.note === "quiet" ? "quiet" : row.result;
        return el("li", { className: `ck-line ${kind}` }, [el("ha-icon", { icon: RESULT_ICONS[kind] || "mdi:circle-outline" }), el("span", { textContent: checkLine({ ...row, untilText: row.until ? time(row.until) : "" }, t, who(row), reason) })]);
      }));
    const step = (when, title, rows, note) =>
      el("div", { className: "ck-step" }, [el("div", { className: "ck-when", textContent: when }), el("div", { className: "ck-what" }, [el("div", { className: "ck-title", textContent: title }), ...(note ? [el("div", { className: "lane-hint", textContent: note })] : []), rows])]);
    if (result.held_for_summary) out.append(el("div", { className: "pol-note" }, [el("ha-icon", { icon: "mdi:text-box-multiple-outline" }), el("span", { textContent: fill(t.ck_summary, { policy: result.held_for_summary }) })]));
    const first = (result.rows || []).filter((r) => r.channel !== "banner");
    out.append(step(result.at ? time(result.at) : t.ck_first, t.ck_first, first.length ? lines(first) : el("div", { className: "lane-hint", textContent: t.ck_nothing })));
    for (const s2 of result.steps || []) {
      out.append(step(time(s2.time), `${t.types[s2.type] || s2.type} · ${s2.policy}`, lines(s2.rows), s2.skipped ? t.ck_waits : ""));
    }
    if ((result.band_off || []).length) out.append(el("div", { className: "pol-note" }, [el("ha-icon", { icon: "mdi:information-outline" }), el("span", { textContent: fill(t.ck_band_off, { names: result.band_off.join(", ") }) })]));
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
    const box = el("div", { className: "pol-editor" });
    const again = () => refreshEditor();

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
    box.append(ui.field(t.entity_id, entityLine, `${own ? t.entity_id_own : t.entity_id_new} ${t.entity_switch_hint}`));
    showEntity(values.name);
    // The types in the groups of the page, so it is clear where a type belongs.
    const typeSelect = el("select", {});
    for (const lane of LANES) {
      const group = el("optgroup", { label: { calm: t.lane_calm, band: t.band, arrive: t.lane_arrive }[lane.id] });
      for (const k of lane.types) group.append(el("option", { value: k, textContent: t.types[k], selected: values.type === k }));
      typeSelect.append(group);
    }
    typeSelect.addEventListener("change", () => { values.type = typeSelect.value; again(); });
    box.append(ui.field(t.type, typeSelect));
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
      does.append(pills(label, POLICY_CHANNELS.map((c) => ({ value: c, label: t.channel_names[c] })), values.channels, (list) => { values.channels = list; again(); }));
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
      does.append(el("h4", { className: "pol-sub", textContent: t.holds_heading }));
      does.append(ui.checkbox(t.holds_anyway, values.holds_anyway, (on) => { values.holds_anyway = on; again(); }));
      does.append(el("div", { className: "hint", textContent: t.holds_anyway_hint }));
      if (values.holds_anyway) {
        const warn = el("div", { className: "pol-caution" }, [el("ha-icon", { icon: "mdi:alert-outline" }), el("span", { textContent: holdsWarning(values, t) })]);
        warn.setAttribute("role", "alert");
        does.append(warn);
      }
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
        if (!values.quiet_entity) {
          does.append(ui.field(t.from, ui.timeInput(values.from_time, (v) => { values.from_time = v; paint(); })));
          does.append(ui.field(t.to, ui.timeInput(values.to_time, (v) => { values.to_time = v; paint(); })));
          does.append(pills(t.days, DAYS.map((d) => ({ value: d, label: t.days_names[d] })), values.days, (list) => { values.days = list; paint(); }));
        }
        does.append(ui.field(t.quiet_entity, ui.selectInput([{ value: "", label: t.quiet_entity_none }, ...quietEntities(hass, values.quiet_entity).map((id) => ({ value: id, label: id }))], values.quiet_entity, (v) => { values.quiet_entity = v; again(); }), t.quiet_entity_hint));
        does.append(ui.field(t.action, ui.selectInput(["quiet", "wait", "drop"].map((k) => ({ value: k, label: t.actions[k] })), values.action, (v) => { values.action = v; paint(); })));
        channelChips(t.channels_quiet);
        holdsAnyway();
        break;
      case "presence": {
        does.append(pills(t.presence_channels, PRESENCE_CHANNELS.map((c) => ({ value: c, label: t.channel_names[c] })), values.channels, (list) => { values.channels = list; again(); }));
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
          does.append(pills(t.covers_audiences, audiences, values.covers_audiences, (list) => { values.covers_audiences = list; paint(); }));
          const people = [...(data.choices.persons || []).map((p) => ({ value: p.id, label: p.name })), ...((data.choices.recipients || {}).speak || []).map((id) => ({ value: id, label: ui.recipientLabel(id, data.choices) }))];
          does.append(pills(t.covers_recipients, people, values.covers_recipients, (list) => { values.covers_recipients = list; paint(); }, true));
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

    // Which messages: automatic (For, Not for tags) or manual (named in a call).
    const radio = (value, label, hint) => {
      const input = el("input", { type: "radio", name: "apply", checked: values.apply === value });
      input.addEventListener("change", () => { values.apply = value; again(); });
      return el("label", { className: "radio" }, [input, el("span", {}, [el("strong", { textContent: label }), el("div", { className: "hint", textContent: hint })])]);
    };
    when.append(el("fieldset", {}, [el("legend", { textContent: t.apply_label }), radio("auto", t.apply_auto, t.apply_auto_hint), radio("manual", t.apply_manual, t.apply_manual_hint)]));
    if (values.apply === "manual") {
      when.append(el("div", { className: "hint", textContent: t.manual_how }), ui.yamlBlock(`policy: ${own?.entity_id || String(values.name).trim() || "…"}`, s.common), el("div", { className: "hint", textContent: t.manual_note }));
    } else {
      when.append(pills(t.severities, SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), values.severities, (list) => { values.severities = list; paint(); }));
      when.append(ui.field(t.tags, ui.textInput(values.tags, (v) => { values.tags = v; paint(); })));
      when.append(ui.field(t.not_tags, ui.textInput(values.not_tags, (v) => { values.not_tags = v; paint(); })));
      const clash = el("div", { className: "hint problems" });
      clash.setAttribute("role", "status");
      const paintClash = () => {
        const list = notOverlap(values, t);
        clash.textContent = list.length ? fill(t.not_overlap, { list: list.join(", ") }) : "";
        clash.hidden = !list.length;
      };
      paintClash();
      noteUpdaters.push(paintClash);
      when.append(clash);
      if (values.links.length) when.append(el("div", { className: "hint", textContent: linkText(values.links) }));
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
    cancel.addEventListener("click", requestCloseEditor);
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
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + ui.TABLE_CSS + CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint pol-intro", textContent: t.intro }));
    // The action bar: add, check a message, and the help page (DESIGN §25.9).
    const add = el("button", { type: "button", className: "primary" }, [el("ha-icon", { icon: "mdi:plus" }), el("span", { textContent: t.new })]);
    add.addEventListener("click", () => openEditor(null, blankValues("quiet_hours")));
    const check = el("button", { type: "button" }, [el("ha-icon", { icon: "mdi:flask-outline" }), el("span", { textContent: t.ck_title })]);
    check.setAttribute("aria-haspopup", "dialog");
    check.addEventListener("click", openChecker);
    const help = el("button", { type: "button" }, [el("ha-icon", { icon: "mdi:help-circle-outline" }), el("span", { textContent: t.help_button })]);
    help.setAttribute("aria-haspopup", "dialog");
    help.addEventListener("click", openHelp);
    root.append(el("div", { className: "pol-bar" }, [add, check, help]));
    if (message) root.append(el("div", { className: "hint problems", textContent: message, role: "alert" }));
    root.append(...checklist());
    if (!data.policies.length) root.append(el("div", { className: "tl-empty", textContent: t.none }));
    root.append(...lanes());
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "policy", own?.subentry_id, toFlowData(values));
    if (!result.ok) {
      message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      refreshEditor();
      return;
    }
    message = "";
    editorDialog?.dialog.close();
    await load();
  }

  async function remove() {
    const { own } = editing;
    if (!window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
    await ui.removeSubentry(hass, data.entry_id, own.subentry_id);
    editorDialog?.dialog.close();
    await load();
  }

  let firstLoad = true;
  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    // A check list whose items are all answered goes away the next time the page is opened, not
    // while the user is answering, so the last answer stays visible until then (D-242).
    if (firstLoad && checklistAnswered(data.conversion_items, data.policies)) {
      await hass.callWS({ type: "heads_up/conversion_items_dismiss" });
      data = { ...data, conversion_items: [] };
    }
    firstLoad = false;
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
