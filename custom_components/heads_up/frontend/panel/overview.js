// Heads Up panel: Overview page (D-118, D-244). Loaded by the shell when the page is opened.

export const STRINGS = {
  en: {
    title: "Overview",
    status: "Status",
    status_title_clear: "All clear",
    status_sub_clear: "No warning or critical notification is active.",
    status_sub_active: "Acknowledge, snooze or clear them here.",
    live_dismiss: "Dismiss",
    live_meta: "Live activity · {n}%",
    status_clear: "All clear. No warning or critical notification is active.",
    status_one: "1 notification needs you",
    status_many: "{n} notifications need you",
    acknowledge_message: "Acknowledge",
    snooze_message: "Snooze 1 h",
    clear_message: "Clear",
    clear_confirm: "Clear “{title}” on every channel?",
    action_failed: "Could not do that: {error}",
    path_show: "Show path",
    path_hide: "Hide path",
    path_loading: "Loading…",
    path_failed: "The path could not be loaded.",
    source_rule: "watch rule",
    coming_title: "Coming up",
    coming_none: "Nothing is scheduled.",
    coming_escalation: "Escalation {policy}: {when}",
    coming_reminder: "Reminder {policy}: {when}",
    coming_summary: "Summary {policy}: {when}",
    coming_quiet: "Held by quiet hours, sent {when}",
    count_one: "1 message",
    count_many: "{n} messages",
    attention: "Needs attention",
    attention_none: "Nothing needs attention.",
    error: "Error",
    warning: "Warning",
    hide: "Hide",
    hidden_line: "{n} hidden.",
    show_hidden: "Show again",
    hide_label: "Hide this warning",
    fix_recipients: "Open Recipients",
    fix_rules: "Open Watch rules",
    fix_messages: "Open Message Log",
    fix_policies: "Open Policies",
    fix_general: "Open Settings",
    last_actions: "Last actions",
    last_none: "Nothing has happened since Home Assistant started.",
    open_messages: "Open Message Log",
    refresh: "Refresh",
    reach_help: "What does this table show?",
    reach_title: "What would a message do right now?",
    reach_intro: "The call chooses channels and people. This shows a message to Everyone.",
    reach_now: "It is {time}.",
    reach_quiet: "Quiet hours until {time}.",
    reach_quiet_open: "Quiet hours are on.",
    reach_away: "Away: {names}.",
    reach_digest: "Messages tagged {tags} wait for the summary {policy}, {when}.",
    reach_digest_all: "Messages wait for the summary {policy}, {when}.",
    reach_failed: "The table could not be loaded.",
    cell_sound: "Sound",
    cell_shown: "Shown",
    cell_quiet: "Quiet",
    cell_held: "Waits",
    cell_skipped: "Skipped",
    cell_not_set_up: "Not set up",
    cell_count: "{n} of {total}",
    sentence_sound: "Makes a sound or speaks.",
    sentence_shown: "Appears with no special sound.",
    sentence_quiet: "Arrives quietly, with no sound.",
    sentence_held: "Waits and is sent later.",
    sentence_skipped: "Is not sent.",
    sentence_not_set_up: "Is not set up yet.",
    reach_nobody: "Nobody to reach.",
    reach_detail: "{channel}, {severity}: {state}",
    activity: "Activity",
    chart_title: "Last 24 hours",
    chart_one: "message",
    chart_many: "messages",
    chart_empty: "Nothing was sent in the last 24 hours.",
    chart_start: "24 h ago",
    chart_now: "now",
    chart_tip_ago: "{n} {unit} · {h} h ago",
    chart_tip_now: "{n} {unit} · last hour",
    chart_label: "Messages per hour over the last 24 hours, {total} in all",
    period_24h: "24 hours",
    period_week: "Week",
    period_month: "Month",
    period_year: "Year",
    period_2y: "2 years",
    period_label: "Period",
    kpi_notifications: "Notifications",
    kpi_failed: "Failed deliveries",
    kpi_critical: "Critical notifications",
    kpi_escalations: "Escalations",
    kpi_quiet: "Quiet hours share",
    kpi_summary: "Summary share",
    kpi_change_pp: "{sign}{n} pp against the period before",
    kpi_quiet_help: "Deliveries that quiet hours held, dropped or sent quietly, of all that could go out. Banners are not counted.",
    kpi_summary_help: "Messages held for a summary, of all messages.",
    kpi_before: "Before: {n}",
    legend_pill: "Change vs. previous period",
    kpi_no_change: "No comparison: the period before has none of it, or its history does not exist yet.",
    sum_attention_none: "All good",
    sum_attention_sub: "Errors {errors} · Warnings {warnings}",
    sum_coming_next: "Next {when}",
    sum_coming_none: "Nothing scheduled",
    sum_last_new: "Newest {when}",
    sum_last_none: "Nothing yet",
    sum_show: "Show details",
    sum_hide: "Hide details",
    kpi_change: "{sign}{n}% against the period before",
    kpi_none: "no data",
    kpi_scope_24h: "Apart from Notifications, the numbers cover today and yesterday.",
    dur_s: "{n} s",
    dur_min: "{n} min",
    dur_h: "{h} h {m} min",
    chart_tip_day: "{label} · {n} {unit}",
    matrix_title: "When your house talks",
    matrix_sub: "Messages by weekday and hour.",
    matrix_short: "Pick a longer period to see this.",
    matrix_label: "Messages by weekday and hour, {total} in all",
    sources_title: "Top sources",
    sources_none: "No messages in this period.",
    source_gone: "deleted watch rule",
    stats_failed: "The activity could not be loaded.",
    legend_label: "Severities",
    all_messages: "All messages",
    act_acked: "acknowledged by {who} after {time}",
    act_acked_time: "acknowledged after {time}",
    act_acked_who: "acknowledged by {who}",
    act_acked_plain: "acknowledged",
    chip_escalated: "Escalated",
    chip_reminder_one: "1 reminder",
    chip_reminder_many: "{n} reminders",
    chip_held_by: "Held by {policy}",
    chip_failed_on: "Failed on {channel}",
    act_source_action: "Action",
    act_text_none: "(no text)",
    source_kind_rule: "Watch rule",
    source_kind_call: "Call",
    source_kind_tag: "Tag",
    source_other: "Other calls (no ID or tag)",
    source_test: "Test send",
    sc_label: "Quick shortcuts",
    sc_channels: "Channels",
    sc_audiences: "Audiences",
    sc_policies: "Policies",
    sc_rules: "Watch rules",
    sc_open: "Open {page}",
    ev_line: "{what} at {time}",
    ev_sent: "Sent",
    ev_reminder: "Reminder sent",
    ev_escalation: "Escalation sent",
    ev_deliver: "Sent by a policy",
    ev_fallback: "Fallback sent",
    ev_released: "Sent after the hold",
    ev_summary: "Summary sent",
    ev_held_summary: "Held for summary",
    ev_held: "Held",
    ev_not_sent: "Not sent",
    ev_failed: "Failed",
    ev_ack: "Acknowledged by {who}",
    ev_ack_plain: "Acknowledged",
    ev_dismissed: "Dismissed by {who}",
    ev_dismissed_plain: "Dismissed",
    ev_snoozed: "Snoozed by {who}",
    ev_snoozed_plain: "Snoozed",
    ev_unsnoozed: "Snooze ended",
    ev_silent: "silently due to {policy}",
    ev_silent_plain: "silently",
    ev_channels_silent: "{channels} silently",
    first_run: "No policies yet. The introduction explains a few defaults you can switch on.",
    first_run_button: "Restart introduction",
    ph_attention: "Problems with your setup show up here.",
    ph_coming: "Escalations, reminders and summaries show up here.",
    ph_activity: "Your last 24 hours show up here once messages arrive.",
    ph_last: "What Heads Up did shows up here.",
    loading: "Loading…",
    load_failed: "The overview could not be loaded.",
    path_none: "No delivery details are kept for this message.",
    dur_hours: "{n} h",
    dur_days: "{n} d",
    status_active: "Active",
    status_acknowledged: "Acknowledged",
    status_snoozed: "Snoozed",
    status_resolved: "Resolved",
    status_expired: "Expired",
    status_expired_after: "Expired after {time}",
    status_dismissed: "Dismissed",
    status_dismissed_all: "Dismissed for everyone",
    status_cleared: "Cleared",
    status_ended: "Ended",
    reach_to: "To {audience}",
    reach_reached: "{names} reached",
    people_failed: "{names} failed",
    reach_not_reached: "{names} not reached",
    reach_held: "{names} held back",
    reach_counts: "{n}/{total} reached",
    reach_all: "all {total} reached",
    reach_failed_n: "{n} failed",
    reach_not_reached_n: "{n} not reached",
    reach_held_n: "{n} held back",
    ev_not_reached: "Not reached on {channels}: {names}",
    ev_ended: "{status}",
  },
  de: {
    title: "Übersicht",
    status: "Status",
    status_title_clear: "Alles ruhig",
    status_sub_clear: "Keine Warnung und keine kritische Meldung ist aktiv.",
    status_sub_active: "Bestätige, stelle zurück oder entferne sie hier.",
    live_dismiss: "Beenden",
    live_meta: "Live-Aktivität · {n} %",
    status_clear: "Alles ruhig. Keine Warnung und keine kritische Meldung ist aktiv.",
    status_one: "1 Meldung braucht dich",
    status_many: "{n} Meldungen brauchen dich",
    acknowledge_message: "Bestätigen",
    snooze_message: "1 Std. zurückstellen",
    clear_message: "Entfernen",
    clear_confirm: "„{title}“ auf allen Kanälen entfernen?",
    action_failed: "Das ging nicht: {error}",
    path_show: "Weg zeigen",
    path_hide: "Weg verbergen",
    path_loading: "Lädt…",
    path_failed: "Der Weg konnte nicht geladen werden.",
    source_rule: "Überwachungsregel",
    coming_title: "Als Nächstes",
    coming_none: "Nichts ist geplant.",
    coming_escalation: "Eskalation {policy}: {when}",
    coming_reminder: "Erinnerung {policy}: {when}",
    coming_summary: "Zusammenfassung {policy}: {when}",
    coming_quiet: "Von der Ruhezeit zurückgehalten, gesendet {when}",
    count_one: "1 Meldung",
    count_many: "{n} Meldungen",
    attention: "Braucht Aufmerksamkeit",
    attention_none: "Nichts braucht Aufmerksamkeit.",
    error: "Fehler",
    warning: "Warnung",
    hide: "Ausblenden",
    hidden_line: "{n} ausgeblendet.",
    show_hidden: "Wieder anzeigen",
    hide_label: "Diese Warnung ausblenden",
    fix_recipients: "Empfänger öffnen",
    fix_rules: "Überwachungsregeln öffnen",
    fix_messages: "Meldungsprotokoll öffnen",
    fix_policies: "Richtlinien öffnen",
    fix_general: "Einstellungen öffnen",
    last_actions: "Letzte Aktionen",
    last_none: "Seit dem Start von Home Assistant ist nichts passiert.",
    open_messages: "Meldungsprotokoll öffnen",
    refresh: "Aktualisieren",
    reach_help: "Was zeigt diese Tabelle?",
    reach_title: "Was würde eine Meldung jetzt tun?",
    reach_intro: "Der Aufruf wählt Kanäle und Personen. Hier siehst du eine Meldung an Alle.",
    reach_now: "Es ist {time}.",
    reach_quiet: "Ruhezeit bis {time}.",
    reach_quiet_open: "Ruhezeit ist an.",
    reach_away: "Unterwegs: {names}.",
    reach_digest: "Meldungen mit dem Tag {tags} warten auf die Zusammenfassung {policy}, {when}.",
    reach_digest_all: "Meldungen warten auf die Zusammenfassung {policy}, {when}.",
    reach_failed: "Die Tabelle konnte nicht geladen werden.",
    cell_sound: "Ton",
    cell_shown: "Angezeigt",
    cell_quiet: "Leise",
    cell_held: "Wartet",
    cell_skipped: "Übersprungen",
    cell_not_set_up: "Nicht eingerichtet",
    cell_count: "{n} von {total}",
    sentence_sound: "Macht einen Ton oder spricht.",
    sentence_shown: "Erscheint ohne besonderen Ton.",
    sentence_quiet: "Kommt leise an, ohne Ton.",
    sentence_held: "Wartet und wird später gesendet.",
    sentence_skipped: "Wird nicht gesendet.",
    sentence_not_set_up: "Ist noch nicht eingerichtet.",
    reach_nobody: "Niemand zu erreichen.",
    reach_detail: "{channel}, {severity}: {state}",
    activity: "Aktivität",
    chart_title: "Letzte 24 Stunden",
    chart_one: "Meldung",
    chart_many: "Meldungen",
    chart_empty: "In den letzten 24 Stunden wurde nichts gesendet.",
    chart_start: "vor 24 Std.",
    chart_now: "jetzt",
    chart_tip_ago: "{n} {unit} · vor {h} Std.",
    chart_tip_now: "{n} {unit} · letzte Stunde",
    chart_label: "Meldungen pro Stunde in den letzten 24 Stunden, insgesamt {total}",
    period_24h: "24 Stunden",
    period_week: "Woche",
    period_month: "Monat",
    period_year: "Jahr",
    period_2y: "2 Jahre",
    period_label: "Zeitraum",
    kpi_notifications: "Meldungen",
    kpi_failed: "Fehlgeschlagene Zustellungen",
    kpi_critical: "Kritische Meldungen",
    kpi_escalations: "Eskalationen",
    kpi_quiet: "Anteil Ruhezeit",
    kpi_summary: "Anteil Zusammenfassungen",
    kpi_change_pp: "{sign}{n} Prozentpunkte gegenüber dem Zeitraum davor",
    kpi_quiet_help: "Zustellungen, die die Ruhezeit zurückgehalten, verworfen oder leise gesendet hat, von allen, die hätten rausgehen können. Banner zählen nicht.",
    kpi_summary_help: "Meldungen, die für eine Zusammenfassung zurückgehalten wurden, von allen Meldungen.",
    kpi_before: "Davor: {n}",
    legend_pill: "Änderung zum Zeitraum davor",
    kpi_no_change: "Kein Vergleich: Im Zeitraum davor gab es nichts davon, oder es gibt dafür noch keinen Verlauf.",
    sum_attention_none: "Alles in Ordnung",
    sum_attention_sub: "Fehler {errors} · Warnungen {warnings}",
    sum_coming_next: "Als Nächstes {when}",
    sum_coming_none: "Nichts geplant",
    sum_last_new: "Neueste {when}",
    sum_last_none: "Noch nichts",
    sum_show: "Details zeigen",
    sum_hide: "Details verbergen",
    kpi_change: "{sign}{n} % gegenüber dem Zeitraum davor",
    kpi_none: "keine Daten",
    kpi_scope_24h: "Außer den Meldungen gelten die Zahlen für heute und gestern.",
    dur_s: "{n} Sek.",
    dur_min: "{n} Min.",
    dur_h: "{h} Std. {m} Min.",
    chart_tip_day: "{label} · {n} {unit}",
    matrix_title: "Wann dein Haus spricht",
    matrix_sub: "Meldungen nach Wochentag und Stunde.",
    matrix_short: "Wähle einen längeren Zeitraum, um das zu sehen.",
    matrix_label: "Meldungen nach Wochentag und Stunde, insgesamt {total}",
    sources_title: "Häufigste Quellen",
    sources_none: "In diesem Zeitraum gab es keine Meldungen.",
    source_gone: "gelöschte Überwachungsregel",
    stats_failed: "Die Aktivität konnte nicht geladen werden.",
    legend_label: "Schweregrade",
    all_messages: "Alle Meldungen",
    act_acked: "bestätigt von {who} nach {time}",
    act_acked_time: "bestätigt nach {time}",
    act_acked_who: "bestätigt von {who}",
    act_acked_plain: "bestätigt",
    chip_escalated: "Eskaliert",
    chip_reminder_one: "1 Erinnerung",
    chip_reminder_many: "{n} Erinnerungen",
    chip_held_by: "Zurückgehalten von {policy}",
    chip_failed_on: "Fehlgeschlagen auf {channel}",
    act_source_action: "Aktion",
    act_text_none: "(kein Text)",
    source_kind_rule: "Überwachungsregel",
    source_kind_call: "Aufruf",
    source_kind_tag: "Tag",
    source_other: "Andere Aufrufe (ohne ID und Tag)",
    source_test: "Test senden",
    sc_label: "Schnellzugriff",
    sc_channels: "Kanäle",
    sc_audiences: "Zielgruppen",
    sc_policies: "Richtlinien",
    sc_rules: "Überwachungsregeln",
    sc_open: "{page} öffnen",
    ev_line: "{what} um {time}",
    ev_sent: "Gesendet",
    ev_reminder: "Erinnerung gesendet",
    ev_escalation: "Eskalation gesendet",
    ev_deliver: "Von einer Richtlinie gesendet",
    ev_fallback: "Ersatz gesendet",
    ev_released: "Nach dem Zurückhalten gesendet",
    ev_summary: "Zusammenfassung gesendet",
    ev_held_summary: "Für die Zusammenfassung zurückgehalten",
    ev_held: "Zurückgehalten",
    ev_not_sent: "Nicht gesendet",
    ev_failed: "Fehlgeschlagen",
    ev_ack: "Bestätigt von {who}",
    ev_ack_plain: "Bestätigt",
    ev_dismissed: "Ausgeblendet von {who}",
    ev_dismissed_plain: "Ausgeblendet",
    ev_snoozed: "Zurückgestellt von {who}",
    ev_snoozed_plain: "Zurückgestellt",
    ev_unsnoozed: "Zurückstellung beendet",
    ev_silent: "leise wegen {policy}",
    ev_silent_plain: "leise",
    ev_channels_silent: "{channels} leise",
    first_run: "Noch keine Richtlinien. Die Einführung erklärt ein paar Standards, die du einschalten kannst.",
    first_run_button: "Einführung neu starten",
    ph_attention: "Probleme mit deiner Einrichtung erscheinen hier.",
    ph_coming: "Eskalationen, Erinnerungen und Zusammenfassungen erscheinen hier.",
    ph_activity: "Deine letzten 24 Stunden erscheinen hier, sobald Meldungen eintreffen.",
    ph_last: "Was Heads Up getan hat, erscheint hier.",
    loading: "Lädt…",
    load_failed: "Die Übersicht konnte nicht geladen werden.",
    path_none: "Zu dieser Meldung sind keine Zustelldetails gespeichert.",
    dur_hours: "{n} Std.",
    dur_days: "{n} T.",
    status_active: "Aktiv",
    status_acknowledged: "Bestätigt",
    status_snoozed: "Zurückgestellt",
    status_resolved: "Erledigt",
    status_expired: "Abgelaufen",
    status_expired_after: "Abgelaufen nach {time}",
    status_dismissed: "Ausgeblendet",
    status_dismissed_all: "Für alle ausgeblendet",
    status_cleared: "Entfernt",
    status_ended: "Beendet",
    reach_to: "An {audience}",
    reach_reached: "{names} erreicht",
    people_failed: "{names} fehlgeschlagen",
    reach_not_reached: "{names} nicht erreicht",
    reach_held: "{names} zurückgehalten",
    reach_counts: "{n}/{total} erreicht",
    reach_all: "alle {total} erreicht",
    reach_failed_n: "{n} fehlgeschlagen",
    reach_not_reached_n: "{n} nicht erreicht",
    reach_held_n: "{n} zurückgehalten",
    ev_not_reached: "Nicht erreicht über {channels}: {names}",
    ev_ended: "{status}",
  },
  fr: {
    title: "Vue d'ensemble",
    status: "État",
    status_title_clear: "Tout est calme",
    status_sub_clear: "Aucun avertissement ni message critique n'est actif.",
    status_sub_active: "Acquittez, reportez ou retirez-les ici.",
    live_dismiss: "Terminer",
    live_meta: "Activité en direct · {n} %",
    status_clear: "Tout est calme. Aucun avertissement ni message critique n'est actif.",
    status_one: "1 notification a besoin de vous",
    status_many: "{n} notifications ont besoin de vous",
    acknowledge_message: "Acquitter",
    snooze_message: "Reporter 1 h",
    clear_message: "Retirer",
    clear_confirm: "Retirer « {title} » de tous les canaux ?",
    action_failed: "Impossible : {error}",
    path_show: "Voir le parcours",
    path_hide: "Masquer le parcours",
    path_loading: "Chargement…",
    path_failed: "Le parcours n'a pas pu être chargé.",
    source_rule: "règle de surveillance",
    coming_title: "À venir",
    coming_none: "Rien n'est prévu.",
    coming_escalation: "Escalade {policy} : {when}",
    coming_reminder: "Rappel {policy} : {when}",
    coming_summary: "Résumé {policy} : {when}",
    coming_quiet: "Retenu par les heures calmes, envoyé {when}",
    count_one: "1 message",
    count_many: "{n} messages",
    attention: "À surveiller",
    attention_none: "Rien à surveiller.",
    error: "Erreur",
    warning: "Avertissement",
    hide: "Masquer",
    hidden_line: "{n} masqué(s).",
    show_hidden: "Afficher à nouveau",
    hide_label: "Masquer cet avertissement",
    fix_recipients: "Ouvrir Destinataires",
    fix_rules: "Ouvrir Règles de surveillance",
    fix_messages: "Ouvrir le journal des messages",
    fix_policies: "Ouvrir Politiques",
    fix_general: "Ouvrir Réglages",
    last_actions: "Dernières actions",
    last_none: "Rien ne s'est passé depuis le démarrage de Home Assistant.",
    open_messages: "Ouvrir le journal des messages",
    refresh: "Actualiser",
    reach_help: "Que montre ce tableau ?",
    reach_title: "Que ferait un message maintenant ?",
    reach_intro: "L'appel choisit les canaux et les personnes. Ici : un message pour Tout le monde.",
    reach_now: "Il est {time}.",
    reach_quiet: "Heures calmes jusqu'à {time}.",
    reach_quiet_open: "Les heures calmes sont actives.",
    reach_away: "Absents : {names}.",
    reach_digest: "Les messages avec l'étiquette {tags} attendent le résumé {policy}, {when}.",
    reach_digest_all: "Les messages attendent le résumé {policy}, {when}.",
    reach_failed: "Le tableau n'a pas pu être chargé.",
    cell_sound: "Son",
    cell_shown: "Affiché",
    cell_quiet: "Discret",
    cell_held: "Attend",
    cell_skipped: "Ignoré",
    cell_not_set_up: "Non configuré",
    cell_count: "{n} sur {total}",
    sentence_sound: "Fait du bruit ou parle.",
    sentence_shown: "Apparaît sans son particulier.",
    sentence_quiet: "Arrive discrètement, sans son.",
    sentence_held: "Attend et part plus tard.",
    sentence_skipped: "N'est pas envoyé.",
    sentence_not_set_up: "N'est pas encore configuré.",
    reach_nobody: "Personne à joindre.",
    reach_detail: "{channel}, {severity} : {state}",
    activity: "Activité",
    chart_title: "Dernières 24 heures",
    chart_one: "message",
    chart_many: "messages",
    chart_empty: "Rien n'a été envoyé ces dernières 24 heures.",
    chart_start: "il y a 24 h",
    chart_now: "maintenant",
    chart_tip_ago: "{n} {unit} · il y a {h} h",
    chart_tip_now: "{n} {unit} · dernière heure",
    chart_label: "Messages par heure sur les dernières 24 heures, {total} au total",
    period_24h: "24 heures",
    period_week: "Semaine",
    period_month: "Mois",
    period_year: "Année",
    period_2y: "2 ans",
    period_label: "Période",
    kpi_notifications: "Notifications",
    kpi_failed: "Envois en échec",
    kpi_critical: "Notifications critiques",
    kpi_escalations: "Escalades",
    kpi_quiet: "Part des heures calmes",
    kpi_summary: "Part des résumés",
    kpi_change_pp: "{sign}{n} pt par rapport à la période précédente",
    kpi_quiet_help: "Envois que les heures calmes ont retenus, abandonnés ou envoyés discrètement, sur tous ceux qui pouvaient partir. Les bannières ne comptent pas.",
    kpi_summary_help: "Messages retenus pour un résumé, sur tous les messages.",
    kpi_before: "Avant : {n}",
    legend_pill: "Variation par rapport à la période précédente",
    kpi_no_change: "Pas de comparaison : la période précédente n'en a pas, ou son historique n'existe pas encore.",
    sum_attention_none: "Tout va bien",
    sum_attention_sub: "Erreurs {errors} · Avertissements {warnings}",
    sum_coming_next: "Prochain {when}",
    sum_coming_none: "Rien de prévu",
    sum_last_new: "Dernier {when}",
    sum_last_none: "Rien pour l'instant",
    sum_show: "Afficher les détails",
    sum_hide: "Masquer les détails",
    kpi_change: "{sign}{n} % par rapport à la période précédente",
    kpi_none: "pas de données",
    kpi_scope_24h: "Hors Notifications, les chiffres couvrent aujourd'hui et hier.",
    dur_s: "{n} s",
    dur_min: "{n} min",
    dur_h: "{h} h {m} min",
    chart_tip_day: "{label} · {n} {unit}",
    matrix_title: "Quand votre maison parle",
    matrix_sub: "Messages par jour de la semaine et par heure.",
    matrix_short: "Choisissez une période plus longue pour le voir.",
    matrix_label: "Messages par jour de la semaine et par heure, {total} au total",
    sources_title: "Principales sources",
    sources_none: "Aucun message sur cette période.",
    source_gone: "règle de surveillance supprimée",
    stats_failed: "L'activité n'a pas pu être chargée.",
    legend_label: "Gravités",
    all_messages: "Tous les messages",
    act_acked: "confirmé par {who} après {time}",
    act_acked_time: "confirmé après {time}",
    act_acked_who: "confirmé par {who}",
    act_acked_plain: "confirmé",
    chip_escalated: "Escaladé",
    chip_reminder_one: "1 rappel",
    chip_reminder_many: "{n} rappels",
    chip_held_by: "Retenu par {policy}",
    chip_failed_on: "Échec sur {channel}",
    act_source_action: "Action",
    act_text_none: "(sans texte)",
    source_kind_rule: "Règle de surveillance",
    source_kind_call: "Appel",
    source_kind_tag: "Étiquette",
    source_other: "Autres appels (sans ID ni étiquette)",
    source_test: "Envoi test",
    sc_label: "Raccourcis",
    sc_channels: "Canaux",
    sc_audiences: "Audiences",
    sc_policies: "Politiques",
    sc_rules: "Règles de surveillance",
    sc_open: "Ouvrir {page}",
    ev_line: "{what} à {time}",
    ev_sent: "Envoyé",
    ev_reminder: "Rappel envoyé",
    ev_escalation: "Escalade envoyée",
    ev_deliver: "Envoyé par une politique",
    ev_fallback: "Repli envoyé",
    ev_released: "Envoyé après la retenue",
    ev_summary: "Résumé envoyé",
    ev_held_summary: "Retenu pour le résumé",
    ev_held: "Retenu",
    ev_not_sent: "Non envoyé",
    ev_failed: "Échec",
    ev_ack: "Confirmé par {who}",
    ev_ack_plain: "Confirmé",
    ev_dismissed: "Masqué par {who}",
    ev_dismissed_plain: "Masqué",
    ev_snoozed: "Reporté par {who}",
    ev_snoozed_plain: "Reporté",
    ev_unsnoozed: "Report terminé",
    ev_silent: "discrètement à cause de {policy}",
    ev_silent_plain: "discrètement",
    ev_channels_silent: "{channels} discrètement",
    first_run: "Aucune politique pour l'instant. L'introduction explique quelques réglages par défaut que vous pouvez activer.",
    first_run_button: "Relancer l'introduction",
    ph_attention: "Les problèmes de votre configuration apparaissent ici.",
    ph_coming: "Les escalades, rappels et résumés apparaissent ici.",
    ph_activity: "Vos dernières 24 heures apparaissent ici dès que des messages arrivent.",
    ph_last: "Ce que Heads Up a fait apparaît ici.",
    loading: "Chargement…",
    load_failed: "La vue d'ensemble n'a pas pu être chargée.",
    path_none: "Aucun détail de remise n'est conservé pour ce message.",
    dur_hours: "{n} h",
    dur_days: "{n} j",
    status_active: "Actif",
    status_acknowledged: "Confirmé",
    status_snoozed: "Reporté",
    status_resolved: "Résolu",
    status_expired: "Expiré",
    status_expired_after: "Expiré après {time}",
    status_dismissed: "Masqué",
    status_dismissed_all: "Masqué pour tous",
    status_cleared: "Retiré",
    status_ended: "Terminé",
    reach_to: "À {audience}",
    reach_reached: "{names} atteint(s)",
    people_failed: "{names} en échec",
    reach_not_reached: "{names} non atteint(s)",
    reach_held: "{names} retenu(s)",
    reach_counts: "{n}/{total} atteints",
    reach_all: "les {total} atteints",
    reach_failed_n: "{n} en échec",
    reach_not_reached_n: "{n} non atteints",
    reach_held_n: "{n} retenus",
    ev_not_reached: "Non atteint par {channels} : {names}",
    ev_ended: "{status}",
  },
  es: {
    title: "Resumen",
    status: "Estado",
    status_title_clear: "Todo en calma",
    status_sub_clear: "Ningún aviso ni mensaje crítico está activo.",
    status_sub_active: "Confírmalos, pospónlos o retíralos aquí.",
    live_dismiss: "Terminar",
    live_meta: "Actividad en directo · {n} %",
    status_clear: "Todo en calma. Ningún aviso ni mensaje crítico está activo.",
    status_one: "1 notificación te necesita",
    status_many: "{n} notificaciones te necesitan",
    acknowledge_message: "Confirmar",
    snooze_message: "Posponer 1 h",
    clear_message: "Retirar",
    clear_confirm: "¿Retirar «{title}» de todos los canales?",
    action_failed: "No se pudo: {error}",
    path_show: "Ver recorrido",
    path_hide: "Ocultar recorrido",
    path_loading: "Cargando…",
    path_failed: "No se pudo cargar el recorrido.",
    source_rule: "regla de vigilancia",
    coming_title: "Próximamente",
    coming_none: "No hay nada programado.",
    coming_escalation: "Escalada {policy}: {when}",
    coming_reminder: "Recordatorio {policy}: {when}",
    coming_summary: "Resumen {policy}: {when}",
    coming_quiet: "Retenido por las horas de silencio, se envía {when}",
    count_one: "1 mensaje",
    count_many: "{n} mensajes",
    attention: "Requiere atención",
    attention_none: "Nada requiere atención.",
    error: "Error",
    warning: "Aviso",
    hide: "Ocultar",
    hidden_line: "{n} oculta(s).",
    show_hidden: "Mostrar de nuevo",
    hide_label: "Ocultar este aviso",
    fix_recipients: "Abrir Destinatarios",
    fix_rules: "Abrir Reglas de vigilancia",
    fix_messages: "Abrir el registro de mensajes",
    fix_policies: "Abrir Políticas",
    fix_general: "Abrir Ajustes",
    last_actions: "Últimas acciones",
    last_none: "No ha pasado nada desde que arrancó Home Assistant.",
    open_messages: "Abrir el registro de mensajes",
    refresh: "Actualizar",
    reach_help: "¿Qué muestra esta tabla?",
    reach_title: "¿Qué haría un mensaje ahora mismo?",
    reach_intro: "La llamada elige canales y personas. Aquí se ve un mensaje para Todos.",
    reach_now: "Son las {time}.",
    reach_quiet: "Horas de silencio hasta las {time}.",
    reach_quiet_open: "Las horas de silencio están activas.",
    reach_away: "Fuera: {names}.",
    reach_digest: "Los mensajes con la etiqueta {tags} esperan al resumen {policy}, {when}.",
    reach_digest_all: "Los mensajes esperan al resumen {policy}, {when}.",
    reach_failed: "No se pudo cargar la tabla.",
    cell_sound: "Sonido",
    cell_shown: "Mostrado",
    cell_quiet: "Discreto",
    cell_held: "Espera",
    cell_skipped: "Omitido",
    cell_not_set_up: "Sin configurar",
    cell_count: "{n} de {total}",
    sentence_sound: "Suena o habla.",
    sentence_shown: "Aparece sin un sonido especial.",
    sentence_quiet: "Llega sin hacer ruido.",
    sentence_held: "Espera y se envía más tarde.",
    sentence_skipped: "No se envía.",
    sentence_not_set_up: "Aún no está configurado.",
    reach_nobody: "Nadie a quien llegar.",
    reach_detail: "{channel}, {severity}: {state}",
    activity: "Actividad",
    chart_title: "Últimas 24 horas",
    chart_one: "mensaje",
    chart_many: "mensajes",
    chart_empty: "No se envió nada en las últimas 24 horas.",
    chart_start: "hace 24 h",
    chart_now: "ahora",
    chart_tip_ago: "{n} {unit} · hace {h} h",
    chart_tip_now: "{n} {unit} · última hora",
    chart_label: "Mensajes por hora en las últimas 24 horas, {total} en total",
    period_24h: "24 horas",
    period_week: "Semana",
    period_month: "Mes",
    period_year: "Año",
    period_2y: "2 años",
    period_label: "Periodo",
    kpi_notifications: "Notificaciones",
    kpi_failed: "Entregas fallidas",
    kpi_critical: "Notificaciones críticas",
    kpi_escalations: "Escaladas",
    kpi_quiet: "Parte de horas de silencio",
    kpi_summary: "Parte de resúmenes",
    kpi_change_pp: "{sign}{n} pp frente al periodo anterior",
    kpi_quiet_help: "Entregas que las horas de silencio retuvieron, descartaron o enviaron en silencio, de todas las que podían salir. Los banners no cuentan.",
    kpi_summary_help: "Mensajes retenidos para un resumen, de todos los mensajes.",
    kpi_before: "Antes: {n}",
    legend_pill: "Cambio frente al periodo anterior",
    kpi_no_change: "Sin comparación: el periodo anterior no tiene nada de esto, o aún no existe su historial.",
    sum_attention_none: "Todo bien",
    sum_attention_sub: "Errores {errors} · Avisos {warnings}",
    sum_coming_next: "Próximo {when}",
    sum_coming_none: "Nada programado",
    sum_last_new: "Último {when}",
    sum_last_none: "Aún nada",
    sum_show: "Mostrar detalles",
    sum_hide: "Ocultar detalles",
    kpi_change: "{sign}{n} % frente al periodo anterior",
    kpi_none: "sin datos",
    kpi_scope_24h: "Salvo Notificaciones, las cifras cubren hoy y ayer.",
    dur_s: "{n} s",
    dur_min: "{n} min",
    dur_h: "{h} h {m} min",
    chart_tip_day: "{label} · {n} {unit}",
    matrix_title: "Cuándo habla tu casa",
    matrix_sub: "Mensajes por día de la semana y hora.",
    matrix_short: "Elige un periodo más largo para verlo.",
    matrix_label: "Mensajes por día de la semana y hora, {total} en total",
    sources_title: "Principales fuentes",
    sources_none: "No hubo mensajes en este periodo.",
    source_gone: "regla de vigilancia eliminada",
    stats_failed: "No se pudo cargar la actividad.",
    legend_label: "Gravedades",
    all_messages: "Todos los mensajes",
    act_acked: "confirmado por {who} tras {time}",
    act_acked_time: "confirmado tras {time}",
    act_acked_who: "confirmado por {who}",
    act_acked_plain: "confirmado",
    chip_escalated: "Escalado",
    chip_reminder_one: "1 recordatorio",
    chip_reminder_many: "{n} recordatorios",
    chip_held_by: "Retenido por {policy}",
    chip_failed_on: "Fallo en {channel}",
    act_source_action: "Acción",
    act_text_none: "(sin texto)",
    source_kind_rule: "Regla de vigilancia",
    source_kind_call: "Llamada",
    source_kind_tag: "Etiqueta",
    source_other: "Otras llamadas (sin ID ni etiqueta)",
    source_test: "Envío de prueba",
    sc_label: "Accesos rápidos",
    sc_channels: "Canales",
    sc_audiences: "Audiencias",
    sc_policies: "Políticas",
    sc_rules: "Reglas de vigilancia",
    sc_open: "Abrir {page}",
    ev_line: "{what} a las {time}",
    ev_sent: "Enviado",
    ev_reminder: "Recordatorio enviado",
    ev_escalation: "Escalada enviada",
    ev_deliver: "Enviado por una política",
    ev_fallback: "Respaldo enviado",
    ev_released: "Enviado tras la retención",
    ev_summary: "Resumen enviado",
    ev_held_summary: "Retenido para el resumen",
    ev_held: "Retenido",
    ev_not_sent: "No enviado",
    ev_failed: "Fallido",
    ev_ack: "Confirmado por {who}",
    ev_ack_plain: "Confirmado",
    ev_dismissed: "Descartado por {who}",
    ev_dismissed_plain: "Descartado",
    ev_snoozed: "Pospuesto por {who}",
    ev_snoozed_plain: "Pospuesto",
    ev_unsnoozed: "Pospuesta terminada",
    ev_silent: "en silencio por {policy}",
    ev_silent_plain: "en silencio",
    ev_channels_silent: "{channels} en silencio",
    first_run: "Aún no hay políticas. La introducción explica algunos valores por defecto que puedes activar.",
    first_run_button: "Reiniciar la introducción",
    ph_attention: "Los problemas de tu configuración aparecen aquí.",
    ph_coming: "Las escaladas, recordatorios y resúmenes aparecen aquí.",
    ph_activity: "Tus últimas 24 horas aparecen aquí cuando lleguen mensajes.",
    ph_last: "Lo que hizo Heads Up aparece aquí.",
    loading: "Cargando…",
    load_failed: "No se pudo cargar el resumen.",
    path_none: "No se guardan detalles de entrega de este mensaje.",
    dur_hours: "{n} h",
    dur_days: "{n} d",
    status_active: "Activo",
    status_acknowledged: "Confirmado",
    status_snoozed: "Pospuesto",
    status_resolved: "Resuelto",
    status_expired: "Caducado",
    status_expired_after: "Caducado tras {time}",
    status_dismissed: "Ocultado",
    status_dismissed_all: "Ocultado para todos",
    status_cleared: "Retirado",
    status_ended: "Terminado",
    reach_to: "A {audience}",
    reach_reached: "{names} alcanzado(s)",
    people_failed: "{names} con error",
    reach_not_reached: "{names} sin alcanzar",
    reach_held: "{names} retenido(s)",
    reach_counts: "{n}/{total} alcanzados",
    reach_all: "los {total} alcanzados",
    reach_failed_n: "{n} con error",
    reach_not_reached_n: "{n} sin alcanzar",
    reach_held_n: "{n} retenidos",
    ev_not_reached: "No alcanzado por {channels}: {names}",
    ev_ended: "{status}",
  },
};

const REFRESH_MS = 10000;
const SNOOZE_SECONDS = 3600;
export const CELL_STATES = ["sound", "shown", "quiet", "held", "skipped", "not_set_up"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// The page that fixes an item of "Needs attention", as the key of the button text.
export function fixKey(page) {
  return `fix_${page}`;
}

// "2 messages" for a count, one word per number.
export function countText(n, t) {
  return n === 1 ? t.count_one : fill(t.count_many, { n });
}

export function statusHeadline(count, t) {
  if (count === 0) return t.status_clear;
  return count === 1 ? t.status_one : fill(t.status_many, { n: count });
}

// "Live activity · 60%": the line under a running job.
export function liveMeta(item, t) {
  return fill(t.live_meta, { n: item.progress });
}

// The pills under the status title: "1 Critical · 2 Warning" from the listed messages.
export function statusPills(items, s) {
  const counts = {};
  for (const item of items) counts[item.severity] = (counts[item.severity] || 0) + 1;
  return ["critical", "warning"].filter((k) => counts[k]).map((k) => ({ severity: k, text: `${counts[k]} ${s.severity[k] || k}` }));
}

// One line of "Coming up": what happens, when, and how many messages it concerns.
export function comingText(entry, now, t, s, fmt) {
  const key = { escalation: "coming_escalation", reminder: "coming_reminder", summary: "coming_summary", quiet_release: "coming_quiet" }[entry.kind];
  const what = fill(t[key] || entry.kind, { policy: entry.policy, when: fmt.inTime(entry.time, now, s) });
  return `${what} · ${countText(entry.count, t)}`;
}

// A cell of the table: its word, and "2 of 3" when the people differ.
export function cellLabel(cell, t) {
  const differ = cell.total > 1 && cell.count < cell.total;
  return { word: t[`cell_${cell.state}`] || cell.state, count: differ ? fill(t.cell_count, { n: cell.count, total: cell.total }) : null };
}

// What a click on a cell shows: a title, one sentence, and a line per person with the reason.
export function cellDetail(cell, channel, severity, t, s, fmt) {
  const label = cellLabel(cell, t);
  const people = (cell.who || []).map((person) => {
    const reason = person.reason ? fmt.reasonText(person.reason, s) : "";
    return `${person.name}: ${t[`cell_${person.state}`] || person.state}${reason ? ` (${reason})` : ""}`;
  });
  const reason = cell.reason && !people.length ? fmt.reasonText(cell.reason, s) : "";
  return {
    title: fill(t.reach_detail, { channel: s.channel[channel] || channel, severity: s.severity[severity] || severity, state: label.count ? `${label.word}, ${label.count}` : label.word }),
    sentence: t[`sentence_${cell.state}`] || "",
    reason,
    people,
    empty: cell.total === 0 && channel !== "banner" && channel !== "persistent" ? t.reach_nobody : "",
  };
}

// The facts the table is read against: time, quiet hours, who is away, summaries that hold messages.
export function contextLines(context, now, t, s, fmt, locale) {
  if (!context) return [];
  const clock = (iso) => new Date(iso).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
  const lines = [fill(t.reach_now, { time: clock(context.now) })];
  if (context.quiet) lines.push(context.quiet.until ? fill(t.reach_quiet, { time: clock(context.quiet.until) }) : t.reach_quiet_open);
  if (context.away?.length) lines.push(fill(t.reach_away, { names: context.away.join(", ") }));
  for (const summary of context.summaries || []) {
    const when = fmt.inTime(summary.due, now, s);
    lines.push(
      summary.tags.length
        ? fill(t.reach_digest, { tags: summary.tags.join(", "), policy: summary.policy, when })
        : fill(t.reach_digest_all, { policy: summary.policy, when }),
    );
  }
  return lines;
}

const DELIVERY_RESULTS = ["sent", "held", "skipped", "failed", "cleared", "summarized"];
const CLUSTER_MS = 90000;
// Skips the user chose (D-250): the Overview does not show them; the Message Log does. The same list is in
// hub/panel_data.py (CHOICE_REASONS).
export const CHOICE_REASONS = ["recipient_disabled", "channel_not_accepted", "popup_off"];
const ORIGIN_TEXT = { message: "ev_sent", reminder: "ev_reminder", escalation: "ev_escalation", deliver: "ev_deliver", fallback: "ev_fallback", released: "ev_released", summary: "ev_summary" };

// The clock time of an event: "13:57", or with the date when it is not today.
export function clockText(iso, now, locale) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const time = date.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
  return date.toDateString() === new Date(now).toDateString() ? time : `${date.toLocaleDateString(locale, { day: "numeric", month: "short" })} ${time}`;
}

// Who an entry of the trace was for: "Anna (iPhone)", a person, a phone, a speaker.
export function entryWho(entry, choices, label) {
  const person = entry.person ? label(entry.person, choices) : "";
  const recipient = String(entry.recipient || "");
  if (recipient.startsWith("device:")) {
    const device = label(recipient.slice("device:".length), choices);
    return person ? `${person} (${device})` : device;
  }
  return person || (recipient ? label(recipient, choices) : "") || "—";
}

// What happened to a message, newest first, one event per moment: a send (with its channels, and
// "silently due to <policy>"), a reminder, an escalation, a hold, a summary, an acknowledgement.
// A failed delivery is an event of its own. Only the steps since the message appeared (`since`): an
// ID that is used again keeps its old entries, which belong to earlier messages. `title` is the
// hover text: who each line was for. `who(entry)` names the person and phone of an entry.
export function pathEvents(entries, { t, s, fmt, since, who, now, locale, ended = null }) {
  const from = since ? Date.parse(since) : NaN;
  const list = [...(entries || [])].reverse().filter((e) => (Number.isNaN(from) || Date.parse(e.time) >= from) && e.channel !== "timer" && e.reason !== "duplicate");
  const channel = (c) => fmt.channelName(c, s);
  const order = ["banner", "push", "popup", "speak", "persistent", "mail"];
  const rank = (c) => (order.includes(c) ? order.indexOf(c) : order.length);
  const channels = (names) => [...new Set(names)].sort((a, b) => rank(a) - rank(b)).map(channel).join(", ");
  const reasonOf = (e) => (e.reason ? fmt.reasonText(e.reason, s) : "");
  const events = [];
  const line = (what, time, rest = "") => `${fill(t.ev_line, { what, time: clockText(time, now, locale) })}${rest}`;
  const hover = (rows) => rows.map((e) => `${who(e)}: ${s.result[e.result] || e.result}${reasonOf(e) ? ` (${reasonOf(e)})` : ""}`).join("\n");
  let cluster = null;
  const flush = () => {
    if (!cluster) return;
    const rows = cluster.rows;
    const time = cluster.time;
    const add = (type, kind, text, group) => events.push({ time, type, kind, text, title: hover(group) });
    const sent = rows.filter((e) => e.result === "sent");
    // A skipped delivery without a policy behind it: a choice of the user (a disabled recipient, a
    // channel the profile does not accept) is not shown here, the Message Log lists it (D-250). Any
    // other skip is a line that names the people who were not reached.
    const skipped = rows.filter((e) => e.result === "skipped");
    const plain = skipped.filter((e) => !e.by && !CHOICE_REASONS.includes(e.reason));
    const byPolicy = skipped.filter((e) => e.by);
    if (sent.length) {
      const quiet = sent.filter((e) => e.by);
      const policies = [...new Set(quiet.map((e) => e.by))].join(", ");
      let rest = "";
      if (quiet.length === sent.length) rest = ` · ${fill(t.ev_silent, { policy: policies })}`;
      else if (quiet.length) rest = ` · ${fill(t.ev_channels_silent, { channels: channels(quiet.map((e) => e.channel)) })} (${policies})`;
      add("sent", "ok", line(t[ORIGIN_TEXT[cluster.origin] || "ev_sent"], time, ` (${channels(sent.map((e) => e.channel))})${rest}`), sent);
    }
    const summarized = rows.filter((e) => e.result === "summarized");
    if (summarized.length) add("summary", "ok", line(t.ev_summary, time, ` (${channels(summarized.map((e) => e.channel))})${summarized[0].by ? ` · ${summarized[0].by}` : ""}`), summarized);
    const held = rows.filter((e) => e.result === "held");
    if (held.length) add("held", "hold", line(t.ev_held, time, ` (${channels(held.map((e) => e.channel))})${held[0].by ? ` · ${held[0].by}` : ""}`), held);
    for (const reason of [...new Set(byPolicy.map(reasonOf))]) {
      const same = byPolicy.filter((e) => reasonOf(e) === reason);
      const by = same.find((e) => e.by)?.by;
      add("skipped", "note", line(t.ev_not_sent, time, ` (${channels(same.map((e) => e.channel))})${reason ? `: ${reason}` : ""}${by ? ` · ${by}` : ""}`), same);
    }
    // People who were not reached belong to the send of the same moment: a line under it. Without a send
    // (nothing arrived) they are a line of their own.
    const sentEvent = events.find((e) => e.type === "sent" && e.time === time);
    for (const reason of [...new Set(plain.map(reasonOf))]) {
      const same = plain.filter((e) => reasonOf(e) === reason);
      const names = [...new Set(same.map(who).filter((n) => n && n !== "—"))].join(", ");
      const text = `${fill(t.ev_not_reached, { channels: channels(same.map((e) => e.channel)), names: names || "—" })}${reason ? ` (${reason})` : ""}`;
      if (sentEvent) sentEvent.details = [...(sentEvent.details || []), text];
      else add("skipped", "note", line(text, time), same);
    }
    const failed = rows.filter((e) => e.result === "failed");
    for (const reason of [...new Set(failed.map(reasonOf))]) {
      const same = failed.filter((e) => reasonOf(e) === reason);
      add("failed", "fail", line(t.ev_failed, time, ` (${channels(same.map((e) => e.channel))})${reason ? `: ${reason}` : ""}`), same);
    }
    cluster = null;
  };
  for (const entry of list) {
    if (entry.channel === "") {
      flush();
      const named = (key, plain) => (entry.who ? fill(t[key], { who: entry.who }) : t[plain]);
      const text = {
        acknowledged: () => named("ev_ack", "ev_ack_plain"),
        dismissed: () => named("ev_dismissed", "ev_dismissed_plain"),
        snoozed: () => named("ev_snoozed", "ev_snoozed_plain"),
        unsnoozed: () => t.ev_unsnoozed,
        held: () => `${t.ev_held_summary}${entry.by ? ` (${entry.by})` : ""}`,
      }[entry.result];
      if (text) events.push({ time: entry.time, type: entry.result, kind: entry.result === "held" ? "hold" : "note", text: line(text(), entry.time), title: "" });
      continue;
    }
    if (!DELIVERY_RESULTS.includes(entry.result) || entry.result === "cleared") continue;
    const origin = entry.result === "summarized" ? "summary" : entry.origin || "message";
    if (cluster && cluster.origin === origin && Date.parse(entry.time) - Date.parse(cluster.time) <= CLUSTER_MS) cluster.rows.push(entry);
    else {
      flush();
      cluster = { origin, time: entry.time, rows: [entry] };
    }
  }
  flush();
  // Taking the message off the channels is not an event of its own: the end says why it ended, unless
  // a dismissal a moment before already says it (D-250).
  if (ended?.time) {
    const covered = events.some((e) => e.type === "dismissed" && Math.abs(Date.parse(e.time) - Date.parse(ended.time)) <= CLUSTER_MS);
    if (!covered) events.push({ time: ended.time, type: "ended", kind: "note", text: line(fill(t.ev_ended, { status: ended.label }), ended.time), title: "" });
  }
  // Oldest first, like a story; at the same moment the end comes last.
  const lastRank = (e) => (e.type === "ended" ? 1 : 0);
  return events.map((e, i) => ({ e, i })).sort((a, b) => Date.parse(a.e.time) - Date.parse(b.e.time) || lastRank(a.e) - lastRank(b.e) || a.i - b.i).map(({ e }) => e);
}

// The four small links under the status card: the page each opens.
export function shortcutCards(t) {
  return [
    { page: "channels", title: t.sc_channels },
    { page: "audiences", title: t.sc_audiences },
    { page: "policies", title: t.sc_policies },
    { page: "rules", title: t.sc_rules },
  ];
}

// The bars of the activity chart: one per hour, oldest first, stacked by severity (the least
// severe at the bottom). An empty hour is a small capsule so the chart never looks broken.
export const CHART_SEVERITIES = ["critical", "warning", "info", "passive"];

export function chartModel(activity, { width = 600, height = 150, gap = 6, minimum = 5 } = {}) {
  const buckets = activity?.buckets ?? [];
  const count = buckets.length;
  const barWidth = count ? (width - gap * (count - 1)) / count : 0;
  const peak = Math.max(1, ...buckets.map((b) => b.total));
  const bars = buckets.map((bucket, index) => {
    const full = bucket.total ? Math.max(minimum * 2, (bucket.total / peak) * height) : minimum;
    let y = height;
    const segments = [];
    for (const severity of [...CHART_SEVERITIES].reverse()) {
      const n = bucket.by?.[severity] ?? 0;
      if (!n) continue;
      const h = (full * n) / bucket.total;
      y -= h;
      segments.push({ severity, y, h });
    }
    return {
      index,
      x: index * (barWidth + gap),
      width: barWidth,
      top: height - full,
      height: full,
      empty: bucket.total === 0,
      total: bucket.total,
      hoursAgo: count - 1 - index,
      start: bucket.start,
      segments,
    };
  });
  return { width, height, barWidth, bars, peak, total: activity?.total ?? 0 };
}

// The label of a bar: a day or a month for the longer periods.
export function bucketLabel(start, period, locale) {
  const date = new Date(start);
  if (Number.isNaN(date.getTime())) return "";
  const options = period === "year" || period === "2y" ? { month: "short", year: "numeric" } : { day: "numeric", month: "short" };
  return date.toLocaleDateString(locale, options);
}

export function barTip(bar, t, period = "24h", locale) {
  const unit = bar.total === 1 ? t.chart_one : t.chart_many;
  if (period !== "24h") return fill(t.chart_tip_day, { label: bucketLabel(bar.start, period, locale), n: bar.total, unit });
  return fill(bar.hoursAgo === 0 ? t.chart_tip_now : t.chart_tip_ago, { n: bar.total, unit, h: bar.hoursAgo });
}

export const PERIODS = ["24h", "week", "month", "year", "2y"];

// "45 s", "4 min", "1 h 5 min".
export function durationText(seconds, t) {
  if (seconds === null || seconds === undefined) return t.kpi_none;
  if (seconds < 60) return fill(t.dur_s, { n: Math.round(seconds) });
  if (seconds < 3600) return fill(t.dur_min, { n: Math.round(seconds / 60) });
  return fill(t.dur_h, { h: Math.floor(seconds / 3600), m: Math.round((seconds % 3600) / 60) });
}

// The key to the pills of the numbers: one pill, what it is.
export function pillLegend(t) {
  return [{ tone: "", text: t.legend_pill }];
}

// The three cards that open the details below them: a number, one line and a tone each.
export function summaryModel(data, now, t, s, fmt) {
  const attention = data.attention || [];
  const errors = attention.filter((a) => a.level === "error").length;
  const warnings = attention.length - errors;
  const coming = data.coming_up || [];
  const last = data.last_actions || [];
  return [
    {
      key: "attention",
      title: t.attention,
      big: attention.length,
      sub: attention.length ? fill(t.sum_attention_sub, { errors, warnings }) : t.sum_attention_none,
      tone: errors ? "crit" : attention.length ? "warn" : "ok",
    },
    {
      key: "coming",
      title: t.coming_title,
      big: coming.length,
      sub: coming.length ? fill(t.sum_coming_next, { when: fmt.inTime(coming[0].time, now, s) }) : t.sum_coming_none,
      tone: "info",
    },
    {
      key: "last",
      title: t.last_actions,
      big: last.length,
      sub: last.length ? fill(t.sum_last_new, { when: fmt.timeAgo(last[0].time, now, s) }) : t.sum_last_none,
      tone: "",
    },
  ];
}

// How many notifications the period had, for the chart's heading.
export function notificationTotal(numbers) {
  return numbers?.notifications?.value ?? 0;
}

// The six numbers of the Activity card: a value and a pill with the change against the period
// before. Counts change in percent, shares in percentage points. `worse` says that more is worse
// (failures, critical, escalations), so a rise is a warning and a fall is good; the rest is neutral.
export function kpiModel(numbers, t) {
  const sign = (n) => (n > 0 ? "+" : "");
  // The hover of a pill names the number of the period before, so "0 %" can be told from "no data".
  const pill = (number, unit, key, worse) => {
    const change = number?.change;
    // No comparison (nothing in the period before, or no history yet): a neutral dash that says so.
    if (change === null || change === undefined) return { tone: "", text: "–", title: t.kpi_no_change };
    const tone = change === 0 || !worse ? "" : change > 0 ? "warning" : "ok";
    const before = number.previous === null || number.previous === undefined ? "" : ` · ${fill(t.kpi_before, { n: unit === "pp" ? `${number.previous} %` : number.previous })}`;
    return { tone, text: `${sign(change)}${change} ${unit}`, title: `${fill(t[key], { sign: sign(change), n: change })}${before}` };
  };
  const count = (key, name, worse) => ({ key, name, value: String(numbers[key]?.value ?? 0), pill: pill(numbers[key], "%", "kpi_change", worse) });
  const share = (key, name, help) => ({ key, name, help, value: numbers[key]?.value === null || numbers[key]?.value === undefined ? t.kpi_none : `${numbers[key].value} %`, pill: pill(numbers[key], "pp", "kpi_change_pp", false) });
  return [
    count("notifications", t.kpi_notifications, false),
    count("failed", t.kpi_failed, true),
    count("critical", t.kpi_critical, true),
    count("escalations", t.kpi_escalations, true),
    share("quiet_share", t.kpi_quiet, t.kpi_quiet_help),
    share("summary_share", t.kpi_summary, t.kpi_summary_help),
  ];
}

// The weekday-by-hour grid: each cell's share of the busiest cell (0 to 1), Monday first.
export function matrixModel(matrix) {
  if (!matrix) return null;
  const peak = Math.max(1, ...matrix.flat());
  return { peak, total: matrix.flat().reduce((a, b) => a + b, 0), rows: matrix.map((row) => row.map((n) => ({ n, share: n / peak }))) };
}

// A source of the top list: what it is called, what kind it is, and its share of the busiest one.
export function sourceRows(sources, t) {
  const peak = Math.max(1, ...sources.map((x) => x.count));
  return sources.map((x) => {
    const label = { rule: x.name || t.source_gone, id: x.name, tag: x.name, test: t.source_test }[x.kind] ?? t.source_other;
    const kind = { rule: t.source_kind_rule, id: t.source_kind_call, tag: t.source_kind_tag }[x.kind] ?? "";
    return { text: label, kind, count: x.count, share: x.count / peak };
  });
}

const AUTO_ID = /^hu_[0-9a-f]{10}$/;

// "45 s", "4 min", "5 h", "3 d": how long something took, rounded for a status.
export function spanText(seconds, t) {
  if (seconds < 3600) return durationText(seconds, t);
  if (seconds < 48 * 3600) return fill(t.dur_hours, { n: Math.round(seconds / 3600) });
  return fill(t.dur_days, { n: Math.round(seconds / 86400) });
}

// The status of a message in one word (and the time it took when it expired). `kind` is the CSS class.
export function statusOf(item, t) {
  if (item.state === "acknowledged") return { label: t.status_acknowledged, kind: "acknowledged" };
  if (item.state !== "ended") return item.snoozed ? { label: t.status_snoozed, kind: "snoozed" } : { label: t.status_active, kind: "active" };
  const label = {
    condition: t.status_resolved,
    rule: t.status_resolved,
    dismissed: t.status_dismissed,
    dismissed_global: t.status_dismissed_all,
    admin: t.status_cleared,
    clear_all: t.status_cleared,
    cleared: t.status_cleared,
    evicted: t.status_cleared,
  }[item.end_reason];
  if (item.end_reason === "expired") {
    const seconds = item.created_at && item.ended_at ? (Date.parse(item.ended_at) - Date.parse(item.created_at)) / 1000 : 0;
    return { label: seconds > 0 ? fill(t.status_expired_after, { time: spanText(seconds, t) }) : t.status_expired, kind: "ended" };
  }
  return { label: label || t.status_ended, kind: "ended" };
}

// Who was reached, as one phrase: "Everyone (3/4 reached, 1 failed)", "Last to leave (Ben reached)".
// Up to three people by name, more as counts. A person who was left out on purpose is not counted.
export function reachText(reach, t) {
  if (!reach) return "";
  const groups = [["reached", "reach_reached"], ["failed", "people_failed", "reach_failed_n"], ["not_reached", "reach_not_reached", "reach_not_reached_n"], ["held", "reach_held", "reach_held_n"]];
  const total = groups.reduce((n, [key]) => n + (reach[key] || []).length, 0);
  if (!total) return "";
  let detail;
  if (total <= 3) detail = groups.filter(([key]) => reach[key]?.length).map(([key, text]) => fill(t[text], { names: reach[key].join(", ") })).join(", ");
  else {
    const n = reach.reached.length;
    detail = [n === total ? fill(t.reach_all, { total }) : fill(t.reach_counts, { n, total }), ...groups.slice(1).filter(([key]) => reach[key]?.length).map(([key, , count]) => fill(t[count], { n: reach[key].length }))].join(", ");
  }
  const audience = (reach.audiences || []).join(" + ");
  return audience ? `${fill(t.reach_to, { audience })} (${detail})` : detail;
}

// One row of Last actions: severity, title and status on the first line; time, channels and who was
// reached on the second, then chips for what a policy did and what went wrong (D-250).
export function actionRow(item, now, t, s, fmt, locale) {
  const text = item.title || item.message || t.act_text_none;
  let source;
  if (item.source.kind === "rule") source = `${t.source_kind_rule} ${item.source.name || t.source_gone}`;
  else if (item.id.startsWith("hu_test_")) source = t.source_test;
  else source = AUTO_ID.test(item.id) ? t.act_source_action : item.id;
  const parts = [];
  if (item.channels?.length) parts.push(item.channels.map((c) => fmt.channelName(c, s)).join(", "));
  const reach = reachText(item.reach, t);
  if (reach) parts.push(reach);
  if (item.acknowledged) {
    const who = item.acknowledged.by;
    const time = item.acknowledged.seconds === null || item.acknowledged.seconds === undefined ? null : durationText(item.acknowledged.seconds, t);
    const key = who && time ? "act_acked" : time ? "act_acked_time" : who ? "act_acked_who" : "act_acked_plain";
    parts.push(fill(t[key], { who, time }));
  }
  const chips = [];
  if (item.escalated) chips.push(t.chip_escalated);
  if (item.reminded) chips.push(item.reminded === 1 ? t.chip_reminder_one : fill(t.chip_reminder_many, { n: item.reminded }));
  for (const policy of item.held_by || []) chips.push(fill(t.chip_held_by, { policy }));
  for (const channel of item.failed_on || []) chips.push(fill(t.chip_failed_on, { channel: fmt.channelName(channel, s) }));
  // A reason is shown when someone was not reached, or when no person is involved (a speaker, mail). When
  // everyone got the message on another channel, Needs attention already names the cause.
  const r = item.reach;
  if (!r || r.not_reached?.length || r.failed?.length || !(r.reached?.length || r.held?.length)) for (const problem of item.problems || []) chips.push(fmt.reasonText(problem.reason, s));
  const diff = now - Date.parse(item.time);
  const when = diff >= 24 * 3600000 && locale ? clockText(item.time, now, locale) : fmt.timeAgo(item.time, now, s);
  const status = statusOf(item, t);
  return { text, source, when, outcome: parts.join(" · "), chips, state: status.label, stateKind: status.kind, severity: item.severity };
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-overview { --hu-radius: 16px; --hu-shadow: 0 1px 2px rgba(0,0,0,.10), 0 8px 24px rgba(0,0,0,.10); --hu-ok: var(--success-color, #43a047); --hu-crit: var(--error-color, #db4437); --hu-warn: var(--warning-color, #ffa600); --hu-info: var(--info-color, #039be5); --hu-chip: color-mix(in srgb, var(--primary-text-color) 8%, transparent); }
.hu-overview > h1 { font-size: 26px; letter-spacing: -.02em; margin: 4px 0 18px; }
.hu-overview section { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: var(--hu-radius); padding: 18px 20px; margin-bottom: 16px; box-shadow: var(--hu-shadow); }
.hu-overview.enter section { animation: hu-rise .45s both; }
.hu-overview.enter section:nth-of-type(2) { animation-delay: .05s; } .hu-overview.enter section:nth-of-type(3) { animation-delay: .1s; }
.hu-overview h2 { font-size: 15px; font-weight: 600; letter-spacing: .01em; margin: 0 0 6px; }
.hu-overview .pair { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.hu-overview .pair section { margin-bottom: 16px; }
.hu-overview button { font: inherit; cursor: pointer; color: var(--primary-text-color); }
.hu-overview button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-overview button.mini { min-height: 36px; padding: 0 12px; font-size: 13px; border-radius: 10px; border: 1px solid var(--divider-color); background: transparent; }
.hu-overview button.mini:hover { border-color: var(--primary-color); }
.hu-overview button.mini.primary { background: var(--primary-color); border-color: transparent; color: var(--text-primary-color, #fff); font-weight: 600; }
.hu-overview button.link { min-height: 36px; padding: 0 6px; border: none; background: none; color: var(--primary-color); font-size: 13px; white-space: nowrap; }
.hu-overview button.link:hover { text-decoration: underline; }
.hu-overview button.link.quiet { color: var(--secondary-text-color); }
.hu-overview .sub { color: var(--secondary-text-color); font-size: 13px; }
.hu-overview .pill { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; background: var(--hu-chip); color: var(--secondary-text-color); white-space: nowrap; }
.hu-overview .pill.critical, .hu-overview .pill.error { background: color-mix(in srgb, var(--hu-crit) 18%, transparent); color: var(--hu-crit); }
.hu-overview .pill.warning { background: color-mix(in srgb, var(--hu-warn) 22%, transparent); color: color-mix(in srgb, var(--hu-warn) 85%, var(--primary-text-color)); }
.hu-overview .pill.info { background: color-mix(in srgb, var(--hu-info) 18%, transparent); color: var(--hu-info); }
.hu-overview .pill.ok { background: color-mix(in srgb, var(--hu-ok) 18%, transparent); color: var(--hu-ok); }
.hu-overview ul { list-style: none; margin: 10px 0 0; padding: 0; }
.hu-overview ul > li { padding: 10px 0; border-top: 1px solid var(--divider-color); }
.hu-overview ul > li:first-child { border-top: none; }

/* status hero */
.hu-overview section.hero { position: relative; overflow: hidden; border-radius: 20px; padding: 24px; display: grid; grid-template-columns: auto 1fr; gap: 8px 24px; align-items: center; background: radial-gradient(120% 140% at 0% 0%, color-mix(in srgb, var(--hero-tint) 16%, var(--card-background-color)), var(--card-background-color) 60%); }
.hu-overview .hero.clear { --hero-tint: var(--hu-ok); } .hu-overview .hero.active { --hero-tint: var(--hu-crit); }
.hu-overview .orb { width: 76px; height: 76px; border-radius: 50%; display: grid; place-items: center; font-size: 34px; font-weight: 700; color: var(--text-primary-color, #fff); background: linear-gradient(135deg, color-mix(in srgb, var(--hero-tint) 70%, #fff), var(--hero-tint)); box-shadow: 0 0 0 8px color-mix(in srgb, var(--hero-tint) 14%, transparent), 0 0 0 18px color-mix(in srgb, var(--hero-tint) 7%, transparent); margin: 10px; }
.hu-overview .hero.active .orb { animation: hu-pulse 1.8s infinite; }
.hu-overview .hero .title { font-size: 24px; font-weight: 700; letter-spacing: -.02em; margin: 2px 0; }
.hu-overview .hero .pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.hu-overview .hero .items { grid-column: 1 / -1; display: grid; gap: 10px; margin-top: 12px; }
.hu-overview .alert { display: grid; grid-template-columns: auto 1fr auto; gap: 4px 12px; align-items: center; padding: 12px 14px; border-radius: 14px; border: 1px solid var(--divider-color); background: var(--card-background-color); }
.hu-overview .alert .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--hu-warn); }
.hu-overview .alert.critical .dot { background: var(--hu-crit); }
.hu-overview .alert.live .dot { background: var(--hu-info); }
.hu-overview .alert .name { font-weight: 600; overflow-wrap: anywhere; }
.hu-overview .alert .acts { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.hu-overview .alert .path { grid-column: 1 / -1; }
@media (max-width: 640px) { .hu-overview section.hero { grid-template-columns: 1fr; } .hu-overview .alert { grid-template-columns: auto 1fr; } .hu-overview .alert .acts { grid-column: 1 / -1; justify-content: flex-start; } }

/* rows */
.hu-overview .row { display: grid; grid-template-columns: auto 1fr auto; gap: 4px 12px; align-items: center; }
.hu-overview .row .text { overflow-wrap: anywhere; }
.hu-overview .row .acts { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.hu-overview .row.simple { grid-template-columns: 1fr auto; }
.hu-overview .row.stack { grid-template-columns: auto 1fr; align-items: start; }
.hu-overview .row.stack .acts { grid-column: 2; justify-content: flex-start; margin-left: -6px; }
.hu-overview .time { font-variant-numeric: tabular-nums; color: var(--secondary-text-color); font-size: 12px; background: var(--hu-chip); border-radius: 999px; padding: 2px 9px; white-space: nowrap; }
.hu-overview .path { margin: 6px 0 0; padding-left: 14px; border-left: 3px solid var(--primary-color); display: grid; gap: 4px; }
.hu-overview .path div { font-size: 13px; }
.hu-overview .placeholder { color: var(--secondary-text-color); font-size: 14px; padding: 10px 0 4px; }
.hu-overview .row.log { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; }
.hu-overview .row.log .time { flex: none; align-self: center; }
.hu-overview .row.log .text { flex: 1 1 160px; min-width: 0; }
.hu-overview .row.log .acts { margin-left: auto; }
@media (max-width: 560px) { .hu-overview .row:not(.log):not(.stack):not(.simple) { grid-template-columns: 1fr; } }

/* reach table */
.hu-overview .reach { width: 100%; border-collapse: separate; border-spacing: 6px; table-layout: fixed; margin: 6px -6px 0; width: calc(100% + 12px); }
.hu-overview .reach th { font-size: 12px; font-weight: 600; text-align: left; padding: 4px 6px; color: var(--secondary-text-color); letter-spacing: .02em; }
.hu-overview .reach th.col { text-align: center; }
.hu-overview .reach td { padding: 0; }
.hu-overview .reach button.cell { width: 100%; min-height: 46px; padding: 4px 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1.2; border-radius: 12px; border: 1px solid transparent; font-size: 13px; font-weight: 600; transition: transform .12s, box-shadow .12s; }
.hu-overview .reach button.cell:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.18); }
.hu-overview .reach button.cell .count { font-size: 11px; font-weight: 400; opacity: .85; }
.hu-overview .reach button.cell[aria-pressed="true"] { border-color: var(--primary-color); box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color) 35%, transparent); }
.hu-overview .reach .st-sound { background: color-mix(in srgb, var(--hu-crit) 22%, transparent); color: var(--hu-crit); }
.hu-overview .reach .st-shown { background: color-mix(in srgb, var(--hu-ok) 20%, transparent); color: var(--hu-ok); }
.hu-overview .reach .st-quiet { background: color-mix(in srgb, var(--hu-info) 20%, transparent); color: var(--hu-info); }
.hu-overview .reach .st-held { background: color-mix(in srgb, var(--hu-warn) 24%, transparent); color: color-mix(in srgb, var(--hu-warn) 85%, var(--primary-text-color)); }
.hu-overview .reach .st-skipped { background: var(--hu-chip); color: var(--secondary-text-color); }
.hu-overview .reach .st-not_set_up { background: transparent; border: 1px dashed var(--divider-color); color: var(--secondary-text-color); font-weight: 400; }
.hu-overview .detail { margin-top: 12px; padding: 12px 14px; border-radius: 12px; background: var(--hu-chip); display: grid; gap: 2px; }
.hu-overview .detail .t { font-weight: 600; }
.hu-overview button.help { min-width: 24px; min-height: 24px; width: 24px; height: 24px; padding: 0; margin-left: 8px; border-radius: 50%; border: 1px solid var(--divider-color); background: transparent; font-size: 13px; line-height: 1; cursor: help; vertical-align: middle; color: var(--secondary-text-color); }
.hu-overview button.help[aria-expanded="true"], .hu-overview button.help:hover { color: var(--primary-text-color); border-color: var(--primary-text-color); }
.hu-overview .tip { margin: 4px 0 10px; padding: 10px 12px; border-radius: 10px; background: var(--hu-chip); font-size: 13px; display: grid; gap: 2px; }

/* chart */
.hu-overview .chartbox .head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
.hu-overview .chartbox .head .total { font-size: 22px; font-weight: 700; letter-spacing: -.02em; }
.hu-overview .chartbox .axis { display: flex; justify-content: space-between; margin-top: 6px; }
.hu-overview svg.chart { display: block; width: 100%; height: auto; overflow: visible; }
.hu-overview svg.chart .bar { transform-box: fill-box; transform-origin: 50% 100%; transition: filter .2s; }
.hu-overview svg.chart .bar:hover { filter: brightness(1.18); }
.hu-overview svg.chart .empty { fill: var(--divider-color); opacity: .7; }
.hu-overview svg.chart .sev-critical { fill: var(--hu-crit); }
.hu-overview svg.chart .sev-warning { fill: var(--hu-warn); }
.hu-overview svg.chart .sev-info { fill: var(--hu-info); }
.hu-overview svg.chart .sev-passive { fill: var(--hu-ok); }
.hu-overview svg.chart.intro .bar { animation: hu-grow .8s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(var(--i) * 30ms); }
.hu-overview svg.chart .bar.now .shine { animation: hu-glow 2.6s ease-in-out infinite; }
.hu-overview .hint { background: var(--hu-chip); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }

/* activity */
.hu-overview .seg { display: inline-flex; flex-wrap: wrap; gap: 2px; padding: 3px; border-radius: 12px; background: var(--hu-chip); }
.hu-overview .seg button { min-height: 34px; padding: 0 12px; border: none; border-radius: 9px; background: none; color: var(--secondary-text-color); font-size: 14px; }
.hu-overview .seg button[aria-pressed="true"] { background: var(--card-background-color); color: var(--primary-text-color); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.2); }
.hu-overview .activity-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 6px; }
.hu-overview .kpis { display: flex; gap: 12px; margin: 12px 0 8px; overflow-x: auto; scroll-snap-type: x proximity; padding-bottom: 6px; }
.hu-overview .kpis:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-overview .kpi { flex: 1 0 140px; scroll-snap-align: start; padding: 12px 14px; border-radius: 14px; background: var(--hu-chip); }
.hu-overview .kpi .big { font-size: 28px; font-weight: 700; line-height: 1.1; letter-spacing: -.02em; }
.hu-overview .kpi .name { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }
.hu-overview .kpi .pill { margin-top: 6px; font-size: 11px; max-width: 100%; }
.hu-overview .kpi .name { min-height: 2.4em; }
.hu-overview .legend { display: flex; gap: 12px; font-size: 12px; color: var(--secondary-text-color); flex-wrap: wrap; margin-top: 8px; }
.hu-overview .legend .pilllegend.first { margin-left: auto; }
.hu-overview .legend .pilllegend .pill { font-size: 10px; padding: 0 7px; margin-right: 5px; }
.hu-overview .legend i { display: inline-block; width: 9px; height: 9px; border-radius: 3px; margin-right: 5px; }
.hu-overview .heat { display: grid; grid-template-columns: 34px repeat(24, minmax(0, 1fr)); gap: 3px; margin-top: 10px; font-size: 11px; color: var(--secondary-text-color); }
.hu-overview .heat .c { aspect-ratio: 1; border-radius: 4px; min-height: 10px; background: color-mix(in srgb, var(--primary-color) calc(var(--share) * 100%), var(--hu-chip)); }
.hu-overview .heat .lab { display: flex; align-items: center; }
.hu-overview .heat .hr { text-align: left; overflow: visible; white-space: nowrap; }
.hu-overview .bars { display: grid; gap: 9px; margin-top: 12px; }
.hu-overview .srcbar { display: grid; grid-template-columns: minmax(90px, 220px) 1fr 44px; gap: 10px; align-items: center; font-size: 13px; }
.hu-overview .srcbar .t { height: 10px; border-radius: 6px; background: var(--hu-chip); overflow: hidden; }
.hu-overview .srcbar .t i { display: block; height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--primary-color), color-mix(in srgb, var(--primary-color) 55%, var(--hu-info))); width: calc(var(--share) * 100%); }
.hu-overview .srcbar .n { text-align: right; font-variant-numeric: tabular-nums; }
@media (max-width: 480px) { .hu-overview .srcbar { grid-template-columns: 1fr 44px; } .hu-overview .srcbar .t { grid-column: 1 / -1; order: 3; } .hu-overview .heat { grid-template-columns: 28px repeat(24, minmax(0, 1fr)); gap: 2px; } .hu-overview .seg button { padding: 0 9px; font-size: 13px; } .hu-overview .kpi .big { font-size: 22px; } }

.hu-overview .cardhead { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin-bottom: 6px; }
.hu-overview .cardhead h2 { margin: 0; }
.hu-overview .act { display: grid; gap: 2px; padding: 7px 0; }
.hu-overview .act .top { display: flex; align-items: center; gap: 8px; min-width: 0; }
.hu-overview .act .headline { flex: 1 1 auto; min-width: 0; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hu-overview .act .top .pill { font-size: 11px; padding: 1px 8px; flex: none; }
@media (max-width: 480px) {
  .hu-overview .act .top { flex-wrap: wrap; row-gap: 2px; }
  .hu-overview .act .headline { order: 3; flex: 1 1 100%; white-space: normal; }
  .hu-overview .act .top > :last-child { margin-left: auto; }
}
.hu-overview .act button.link { min-height: 28px; font-size: 12px; padding: 0 2px; flex: none; }
.hu-overview .act .meta { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 8px; font-size: 12px; color: var(--secondary-text-color); }
.hu-overview .act .meta .pill { font-size: 11px; font-weight: 500; padding: 0 8px; }
.hu-overview .act .pill.state-ended { background: var(--hu-chip); }
.hu-overview .act .pill.state-acknowledged { background: color-mix(in srgb, var(--hu-ok) 18%, transparent); color: var(--hu-ok); }
.hu-overview .act .pill.state-snoozed { background: color-mix(in srgb, var(--hu-warn) 22%, transparent); }
.hu-overview .act .pill.state-active { background: color-mix(in srgb, var(--hu-info) 18%, transparent); color: var(--hu-info); }
.hu-overview .srcbar .nm { display: flex; align-items: baseline; gap: 6px; min-width: 0; overflow-wrap: anywhere; }
.hu-overview .srcbar .kind { font-size: 11px; color: var(--secondary-text-color); white-space: nowrap; }

.hu-overview .shortcuts { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 16px; }
.hu-overview button.shortcut { display: inline-flex; align-items: center; gap: 8px; min-height: 40px; padding: 0 14px; border-radius: 999px; border: 1px solid var(--divider-color); background: var(--card-background-color); box-shadow: var(--hu-shadow); transition: border-color .12s; }
.hu-overview button.shortcut:hover { border-color: var(--primary-color); }
.hu-overview button.shortcut .name { font-size: 14px; font-weight: 600; }
.hu-overview button.shortcut .arrow { color: var(--primary-color); font-size: 15px; transition: transform .12s; }
.hu-overview button.shortcut:hover .arrow { transform: translateX(2px); }
.hu-overview .path .ev { position: relative; padding: 2px 0 2px 18px; font-size: 13px; cursor: default; overflow-wrap: anywhere; }
.hu-overview .path .ev::before { content: ""; position: absolute; left: 2px; top: 9px; width: 8px; height: 8px; border-radius: 50%; background: var(--hu-ok); }
.hu-overview .path .ev-note::before { background: var(--secondary-text-color); }
.hu-overview .path .ev-hold::before { background: var(--hu-warn); }
.hu-overview .path .ev-detail { font-size: 12px; color: var(--secondary-text-color); padding-top: 1px; }
.hu-overview .path .ev-fail { color: var(--hu-crit); font-weight: 600; }
.hu-overview .path .ev-fail::before { background: var(--hu-crit); }

/* the three summary cards and the panel under them */
.hu-overview .summary { margin-bottom: 16px; }
.hu-overview .sumcards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.hu-overview button.sumcard { position: relative; display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; align-items: end; text-align: left; padding: 14px 16px; min-height: 104px; border-radius: 16px; border: 1px solid var(--divider-color); background: var(--card-background-color); box-shadow: var(--hu-shadow); transition: transform .18s, border-color .18s, box-shadow .18s; --tone: var(--secondary-text-color); }
.hu-overview button.sumcard.tone-crit { --tone: var(--hu-crit); } .hu-overview button.sumcard.tone-warn { --tone: var(--hu-warn); }
.hu-overview button.sumcard.tone-ok { --tone: var(--hu-ok); } .hu-overview button.sumcard.tone-info { --tone: var(--hu-info); }
.hu-overview button.sumcard:hover { transform: translateY(-2px); border-color: var(--primary-color); }
.hu-overview button.sumcard[aria-expanded="true"] { border-color: var(--primary-color); box-shadow: 0 0 0 1px var(--primary-color), var(--hu-shadow); }
.hu-overview .sumcard .sumtitle { grid-column: 1 / -1; font-size: 13px; font-weight: 600; color: var(--secondary-text-color); }
.hu-overview .sumcard .sumbig { font-size: 34px; font-weight: 700; line-height: 1.05; letter-spacing: -.02em; color: var(--tone); }
.hu-overview .sumcard .sumsub { grid-column: 1; font-size: 12px; color: var(--secondary-text-color); }
.hu-overview .sumcard .sumchev { grid-row: 2 / span 2; grid-column: 2; width: 10px; height: 10px; border-right: 2px solid var(--secondary-text-color); border-bottom: 2px solid var(--secondary-text-color); transform: rotate(45deg); margin: 0 4px 6px; transition: transform .35s cubic-bezier(.2, .8, .2, 1); }
.hu-overview .sumcard[aria-expanded="true"] .sumchev { transform: rotate(-135deg); margin-bottom: 2px; }
.hu-overview .reveal { overflow: hidden; opacity: 0; transition: height .45s cubic-bezier(.2, .8, .2, 1), opacity .3s ease; }
.hu-overview .reveal.open { opacity: 1; }
.hu-overview .reveal-inner { padding-top: 14px; }
.hu-overview .reveal .panel > section { margin-bottom: 0; }
.hu-overview .reveal.open:not(.static) .panel:not([hidden]) > section { animation: hu-slide .45s cubic-bezier(.2, .8, .2, 1) both; }
@keyframes hu-slide { from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: none; } }
@media (max-width: 560px) { .hu-overview .sumcards { gap: 8px; } .hu-overview button.sumcard { padding: 12px 10px; min-height: 96px; } .hu-overview .sumcard .sumbig { font-size: 28px; } .hu-overview .sumcard .sumchev { display: none; } }
@media (prefers-reduced-motion: reduce) { .hu-overview .reveal, .hu-overview button.sumcard, .hu-overview .sumchev { transition: none; } .hu-overview .reveal .panel > section { animation: none !important; } }
@keyframes hu-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes hu-pulse { 0% { box-shadow: 0 0 0 8px color-mix(in srgb, var(--hero-tint) 30%, transparent), 0 0 0 18px color-mix(in srgb, var(--hero-tint) 7%, transparent); } 100% { box-shadow: 0 0 0 8px color-mix(in srgb, var(--hero-tint) 14%, transparent), 0 0 0 26px transparent; } }
@keyframes hu-grow { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }
@keyframes hu-glow { 0%, 100% { opacity: .35; } 50% { opacity: .75; } }
@media (prefers-reduced-motion: reduce) { .hu-overview.enter section, .hu-overview .orb, .hu-overview svg.chart .bar, .hu-overview svg.chart .bar .shine { animation: none !important; } .hu-overview .reach button.cell { transition: none; } }
@media (max-width: 480px) {
  .hu-overview .reach { border-spacing: 4px; margin: 6px -4px 0; width: calc(100% + 8px); }
  .hu-overview .reach th { font-size: 11px; padding: 2px; }
  .hu-overview .reach button.cell { font-size: 11px; padding: 2px; min-height: 48px; }
}
`;

export function mount(container, ctx) {
  const { t, s, fmt } = ctx;
  let hass = ctx.hass;
  let data = null;
  let reach = null; // the table, or false when it could not be loaded
  let selected = null; // { channel, severity }
  let openPaths = {}; // message id -> trace entries, "loading" or "error"
  let timer = null;
  let played = false;
  let openSummary = null; // which of the three cards is open: attention, coming or last
  let reachHelp = false; // the explanation of the table is open
  let tour = null;
  let tourStarted = false;
  let period = "week";
  let stats = null; // the Activity data of `period`, or false when it could not be loaded
  // The tour lives in its own node, so the page's redraws never wipe it.
  const tourHost = el("div");
  // The style node is made once: a new one on every redraw made the page flash.
  const styleNode = el("style", { textContent: CSS });
  const root = el("div", { className: "hu-overview" });
  container.append(root);

  const now = () => Date.now();
  const section = (title, children, label) => {
    const box = el("section", {}, [el("h2", { textContent: title }), ...children]);
    if (label) box.setAttribute("aria-label", label);
    return box;
  };

  // The path of a message: its trace, oldest step first.
  // The names of people and phones for the hover text; asked once, when the first path opens.
  let choices = null;
  async function ensureChoices() {
    if (choices) return;
    try {
      choices = (await hass.callWS({ type: "heads_up/panel_config" })).choices || {};
    } catch (err) {
      choices = {};
    }
  }

  async function togglePath(id) {
    if (openPaths[id]) {
      delete openPaths[id];
      render();
      return;
    }
    openPaths[id] = "loading";
    render();
    try {
      await ensureChoices();
      const result = await hass.callWS({ type: "heads_up/panel_trace", message_id: id });
      openPaths[id] = { entries: result?.entries || [], since: result?.message?.created_at || null };
    } catch (err) {
      openPaths[id] = "error";
    }
    render();
  }

  function pathNode(id) {
    const value = openPaths[id];
    const box = el("div", { className: "path" });
    if (value === "loading") box.append(el("div", { className: "sub", textContent: t.path_loading }));
    else if (value === "error") box.append(el("div", { textContent: t.path_failed }));
    else {
      const label = (v, c) => (ctx.ui ? ctx.ui.recipientLabel(v, c) : v);
      const item = (data?.last_actions || []).find((a) => a.id === id);
      const status = item && item.state === "ended" ? statusOf(item, t) : null;
      const ended = status && item.ended_at ? { time: item.ended_at, label: status.label } : null;
      const events = pathEvents(value.entries, { t, s, fmt, since: value.since, now: now(), locale: ctx.language, ended, who: (entry) => entryWho(entry, choices || {}, label) });
      if (item) box.append(el("div", { className: "sub", textContent: actionRow(item, now(), t, s, fmt, ctx.language).source }));
      if (!events.length || (item && item.trace_complete === false)) box.append(el("div", { className: "sub", textContent: t.path_none }));
      for (const event of events) {
        const row = el("div", { className: `ev ev-${event.kind}` }, [document.createTextNode(event.text), ...(event.details || []).map((text) => el("div", { className: "ev-detail", textContent: text }))]);
        if (event.title) row.title = event.title;
        box.append(row);
      }
    }
    return box;
  }

  // The introduction tour, inside the page (D-244): shown on the first opening, or when asked for.
  async function startTour(force) {
    if (tour) return;
    try {
      const mod = await ctx.loadModule("welcome.js");
      tour = await mod.mount(tourHost, {
        hass,
        t: ctx.tableFor(mod),
        s,
        ui: ctx.ui,
        language: ctx.language,
        force,
        onClose: () => {
          tour = null;
          if (globalThis.location?.search) globalThis.history?.replaceState(null, "", globalThis.location.pathname);
          load();
        },
      });
    } catch (err) {
      tour = null; // the tour is a convenience: a failure must not block the page
    }
    if (tour) render();
  }

  async function act(type, extra, confirmText) {
    if (confirmText && !window.confirm(confirmText)) return;
    try {
      await hass.callWS({ type, ...extra });
    } catch (err) {
      window.alert(fill(t.action_failed, { error: (err && err.message) || String(err) }));
    }
    await load();
  }

  function pathButton(id) {
    const open = Boolean(openPaths[id]);
    const button = el("button", { type: "button", className: "link", textContent: open ? t.path_hide : t.path_show });
    button.setAttribute("aria-expanded", String(open));
    button.addEventListener("click", () => togglePath(id));
    return button;
  }

  function shortcutRow() {
    const row = el("div", { className: "shortcuts" });
    row.setAttribute("aria-label", t.sc_label);
    for (const card of shortcutCards(t)) {
      const button = el("button", { type: "button", className: "shortcut" }, [el("span", { className: "name", textContent: card.title }), el("span", { className: "arrow", textContent: "→", "aria-hidden": "true" })]);
      button.setAttribute("aria-label", fill(t.sc_open, { page: card.title }));
      button.addEventListener("click", () => ctx.navigate(card.page));
      row.append(button);
    }
    return row;
  }

  // A job with a progress bar. A push-only one has no button on the phone, so it ends here.
  function liveRow(item) {
    const end = el("button", { type: "button", className: "mini", textContent: t.live_dismiss });
    end.addEventListener("click", () => act("heads_up/panel_clear", { message_id: item.id }));
    return el("div", { className: "alert live" }, [
      el("span", { className: "dot", "aria-hidden": "true" }),
      el("div", {}, [el("div", { className: "name", textContent: fmt.messageTitle(item) }), el("div", { className: "sub", textContent: liveMeta(item, t) })]),
      el("div", { className: "acts" }, [end]),
    ]);
  }

  function statusCard() {
    const status = data.status;
    const active = status.count > 0;
    const box = el("section", { className: `hero ${active ? "active" : "clear"}` });
    box.setAttribute("aria-label", t.status);
    const pills = el("div", { className: "pills" }, statusPills(status.items, s).map((p) => el("span", { className: `pill ${p.severity}`, textContent: p.text })));
    box.append(
      el("div", { className: "orb", textContent: active ? String(status.count) : "✓", "aria-hidden": "true" }),
      el("div", {}, [
        active ? pills : "",
        el("div", { className: "title", textContent: active ? statusHeadline(status.count, t) : t.status_title_clear }),
        el("div", { className: "sub", textContent: active ? t.status_sub_active : t.status_sub_clear }),
      ]),
    );
    const live = data.live_activities || [];
    if (!active && !live.length) return box;
    const items = el("div", { className: "items" });
    // Running jobs first: not in the count above, so a green page stays green (D-282).
    for (const item of live) items.append(liveRow(item));
    for (const item of status.items) {
      const buttons = el("div", { className: "acts" });
      const mini = (text, onClick, extra = "") => {
        const button = el("button", { type: "button", className: `mini ${extra}`.trim(), textContent: text });
        button.addEventListener("click", onClick);
        return button;
      };
      if (item.can_acknowledge) buttons.append(mini(t.acknowledge_message, () => act("heads_up/panel_acknowledge", { message_id: item.id })));
      if (item.severity === "warning" && item.snoozable) buttons.append(mini(t.snooze_message, () => act("heads_up/snooze", { banner_id: item.id, seconds: SNOOZE_SECONDS })));
      if (item.can_clear) buttons.append(mini(t.clear_message, () => act("heads_up/panel_clear", { message_id: item.id }, fill(t.clear_confirm, { title: fmt.messageTitle(item) }))));
      buttons.append(pathButton(item.id));
      const states = item.states.map((state) => fmt.stateText(state, now(), s));
      const origin = item.source === "rule" ? [t.source_rule] : [];
      const meta = [s.severity[item.severity] || item.severity, ...origin, ...states].join(" · ");
      const row = el("div", { className: `alert ${item.severity}` }, [
        el("span", { className: "dot", "aria-hidden": "true" }),
        el("div", {}, [el("div", { className: "name", textContent: fmt.messageTitle(item) }), el("div", { className: "sub", textContent: meta })]),
        buttons,
      ]);
      if (openPaths[item.id]) row.append(pathNode(item.id));
      items.append(row);
    }
    box.append(items);
    return box;
  }

  function attentionCard() {
    const attention = data.attention;
    const list = el("ul");
    if (attention.length === 0) list.append(el("li", { className: "placeholder", textContent: t.attention_none }));
    for (const item of attention) {
      const acts = el("div", { className: "acts" });
      const key = fixKey(item.page);
      if (t[key]) {
        const fix = el("button", { type: "button", className: "link", textContent: t[key] });
        fix.addEventListener("click", () => ctx.navigate(item.page));
        acts.append(fix);
      }
      if (item.dismissible) {
        const hide = el("button", { type: "button", className: "link quiet", textContent: t.hide });
        hide.setAttribute("aria-label", `${t.hide_label}: ${fmt.attentionText(item, s)}`);
        hide.addEventListener("click", () => act("heads_up/attention_dismiss", { key: item.key }));
        acts.append(hide);
      }
      list.append(el("li", { className: "row stack" }, [el("span", { className: `pill ${item.level}`, textContent: t[item.level] }), el("span", { className: "text", textContent: fmt.attentionText(item, s) }), acts]));
    }
    const parts = [list];
    if (data.attention_hidden > 0) {
      const again = el("button", { type: "button", className: "link", textContent: t.show_hidden });
      again.addEventListener("click", () => act("heads_up/attention_restore", {}));
      parts.push(el("div", { className: "sub", style: "margin-top:8px" }, [el("span", { textContent: `${fill(t.hidden_line, { n: data.attention_hidden })} ` }), again]));
    }
    return section(t.attention, parts);
  }

  function comingCard() {
    const list = el("ul");
    if (data.coming_up.length === 0) list.append(el("li", { className: "placeholder", textContent: t.coming_none }));
    for (const entry of data.coming_up) {
      const [what, count] = comingText(entry, now(), t, s, fmt).split(" · ");
      list.append(el("li", { className: "row simple" }, [el("span", { className: "text", textContent: what }), el("span", { className: "time", textContent: count })]));
    }
    return section(t.coming_title, [list]);
  }

  // A card title with a link to the Message Log on the right, as in the mockup.
  function headed(title, children) {
    const link = el("button", { type: "button", className: "link", textContent: t.all_messages });
    link.addEventListener("click", () => ctx.navigate("messages"));
    return el("section", {}, [el("div", { className: "cardhead" }, [el("h2", { textContent: title }), link]), ...children]);
  }

  function lastActionsCard() {
    const list = el("ul");
    if (data.last_actions.length === 0) list.append(el("li", { className: "placeholder", textContent: t.last_none }));
    for (const item of data.last_actions) {
      const row = actionRow(item, now(), t, s, fmt, ctx.language);
      const top = el("div", { className: "top" }, [
        el("span", { className: `pill ${row.severity}`, textContent: s.severity[row.severity] || row.severity }),
        el("span", { className: "headline", textContent: row.text }),
        el("span", { className: `pill state-${row.stateKind}`, textContent: row.state }),
        pathButton(item.id),
      ]);
      const meta = el("div", { className: "meta" }, [el("span", { textContent: [row.when, row.outcome].filter(Boolean).join(" · ") }), ...row.chips.map((chip) => el("span", { className: "pill", textContent: chip }))]);
      const li = el("li", { className: "act" }, [top, meta]);
      if (openPaths[item.id]) li.append(pathNode(item.id));
      list.append(li);
    }
    return headed(t.last_actions, [list]);
  }

  function reachCard() {
    if (reach === false) return section(t.reach_title, [el("div", { className: "sub", textContent: t.reach_failed })]);
    if (!reach) return section(t.reach_title, [el("div", { className: "sub", textContent: t.loading })]);
    const lines = [t.reach_intro, ...contextLines(reach.context, now(), t, s, fmt, ctx.language)];
    const help = el("button", { type: "button", className: "help", textContent: "?", title: t.reach_help });
    help.setAttribute("aria-label", t.reach_help);
    help.setAttribute("aria-expanded", String(reachHelp));
    help.addEventListener("click", () => {
      reachHelp = !reachHelp;
      render();
    });
    const context = reachHelp ? el("div", { className: "tip", role: "note" }, lines.map((line) => el("div", { textContent: line }))) : "";
    const table = el("table", { className: "reach" });
    const head = el("tr", {}, [el("th", { className: "rowhead", scope: "col" })]);
    for (const severity of reach.severities) head.append(el("th", { className: "col", scope: "col", textContent: s.severity[severity] || severity }));
    table.append(el("thead", {}, [head]));
    const body = el("tbody");
    for (const channel of reach.channels) {
      const row = el("tr", {}, [el("th", { scope: "row", textContent: s.channel[channel] || channel })]);
      for (const severity of reach.severities) {
        const cell = reach.cells[channel][severity];
        const label = cellLabel(cell, t);
        const button = el("button", { type: "button", className: `cell st-${cell.state}` }, [
          el("span", { textContent: label.word }),
          label.count ? el("span", { className: "count", textContent: label.count }) : "",
        ]);
        const pressed = selected && selected.channel === channel && selected.severity === severity;
        button.setAttribute("aria-pressed", String(Boolean(pressed)));
        button.setAttribute("aria-label", `${s.channel[channel] || channel}, ${s.severity[severity] || severity}: ${label.word}${label.count ? `, ${label.count}` : ""}`);
        button.addEventListener("click", () => {
          selected = pressed ? null : { channel, severity };
          render();
        });
        row.append(el("td", {}, [button]));
      }
      body.append(row);
    }
    table.append(body);
    const parts = [context, table].filter(Boolean);
    if (selected) {
      const detail = cellDetail(reach.cells[selected.channel][selected.severity], selected.channel, selected.severity, t, s, fmt);
      const box = el("div", { className: "detail" }, [el("div", { className: "t", textContent: detail.title }), el("div", { textContent: detail.sentence })]);
      if (detail.reason) box.append(el("div", { className: "sub", textContent: detail.reason }));
      if (detail.empty) box.append(el("div", { className: "sub", textContent: detail.empty }));
      for (const line of detail.people) box.append(el("div", { className: "sub", textContent: line }));
      parts.push(box);
    }
    const card = section(t.reach_title, parts);
    card.querySelector("h2").append(help);
    return card;
  }

  // The bars of the last 24 hours, stacked by severity. The bars grow in once, when the page opens;
  // the page refreshes every 10 seconds and must not replay that.
  function chartNode(intro) {
    const model = chartModel({ buckets: stats.buckets, total: notificationTotal(stats.numbers) });
    const NS = "http://www.w3.org/2000/svg";
    const make = (name, attrs = {}, children = []) => {
      const node = document.createElementNS(NS, name);
      for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
      node.append(...children);
      return node;
    };
    const defs = make("defs", {}, [
      make("linearGradient", { id: "hu-shine", x1: 0, y1: 0, x2: 0, y2: 1 }, [
        make("stop", { offset: "0%", "stop-color": "#fff", "stop-opacity": 0.55 }),
        make("stop", { offset: "100%", "stop-color": "#fff", "stop-opacity": 0 }),
      ]),
      ...model.bars.map((bar) =>
        make("clipPath", { id: `hu-clip-${bar.index}` }, [
          make("rect", { x: bar.x, y: bar.top, width: bar.width, height: bar.height, rx: Math.min(6, bar.width / 2) }),
        ]),
      ),
    ]);
    const bars = model.bars.map((bar) => {
      const inner = bar.empty
        ? [make("rect", { class: "empty", x: bar.x, y: bar.top, width: bar.width, height: bar.height })]
        : [
            ...bar.segments.map((seg) => make("rect", { class: `sev-${seg.severity}`, x: bar.x, y: seg.y, width: bar.width, height: seg.h })),
            make("rect", { class: "shine", x: bar.x, y: bar.top, width: bar.width, height: bar.height, fill: "url(#hu-shine)" }),
          ];
      const title = make("title");
      title.textContent = barTip(bar, t, period, ctx.language);
      return make("g", { class: `bar${bar.hoursAgo === 0 ? " now" : ""}`, style: `--i:${bar.index}` }, [title, make("g", { "clip-path": `url(#hu-clip-${bar.index})` }, inner)]);
    });
    const unit = model.total === 1 ? t.chart_one : t.chart_many;
    const label = period === "24h" ? fill(t.chart_label, { total: model.total }) : `${t[`period_${period}`]}: ${model.total} ${unit}`;
    const svg = make("svg", { class: `chart${intro ? " intro" : ""}`, viewBox: `0 0 ${model.width} ${model.height}`, role: "img", "aria-label": label }, [defs, ...bars]);
    const first = stats.buckets[0];
    const legend = el("div", { className: "legend" }, CHART_SEVERITIES.map((severity) => {
      const dot = el("i");
      dot.style.background = `var(--hu-${{ critical: "crit", warning: "warn", info: "info", passive: "ok" }[severity]})`;
      return el("span", {}, [dot, el("span", { textContent: s.severity[severity] || severity })]);
    }));
    legend.setAttribute("aria-label", t.legend_label);
    // The key to the pills sits next to the severities, so the colours of both can be read together.
    pillLegend(t).forEach((item, index) => {
      const mark = el("span", { className: `pill ${item.tone}`.trim(), textContent: "±", "aria-hidden": "true" });
      legend.append(el("span", { className: `pilllegend${index === 0 ? " first" : ""}` }, [mark, el("span", { textContent: item.text })]));
    });
    return el("div", { className: "chartbox" }, [
      el("div", { className: "head" }, [
        el("span", { className: "sub", textContent: period === "24h" ? t.chart_title : t[`period_${period}`] }),
        el("span", model.total ? { className: "total", textContent: `${model.total} ${unit}` } : { className: "sub", textContent: t.chart_empty }),
      ]),
      svg,
      el("div", { className: "axis sub" }, [el("span", { textContent: period === "24h" ? t.chart_start : bucketLabel(first?.start, period, ctx.language) }), el("span", { textContent: t.chart_now })]),
      legend,
    ]);
  }

  // The Activity card: the period switch, the four numbers and the chart; then the weekday grid and
  // the top sources. All of it from the stored history, so it survives a restart.
  function activityCards(intro) {
    const switcher = el("div", { className: "seg" });
    switcher.setAttribute("role", "group");
    switcher.setAttribute("aria-label", t.period_label);
    for (const value of PERIODS) {
      const button = el("button", { type: "button", textContent: t[`period_${value}`] });
      button.setAttribute("aria-pressed", String(value === period));
      button.addEventListener("click", () => {
        period = value;
        stats = null;
        render();
        loadStats();
      });
      switcher.append(button);
    }
    const head = el("div", { className: "activity-head" }, [el("h2", { textContent: t.activity, style: "margin:0" }), switcher]);
    const first = el("section", {}, [head]);
    if (stats === false) {
      first.append(el("div", { className: "sub", textContent: t.stats_failed }));
      return [first];
    }
    if (!stats) {
      first.append(el("div", { className: "sub", textContent: t.loading }));
      return [first];
    }
    const tiles = kpiModel(stats.numbers, t).map((kpi) => {
      const pill = kpi.pill ? el("span", { className: `pill ${kpi.pill.tone}`.trim(), textContent: kpi.pill.text, title: kpi.pill.title }) : "";
      if (kpi.pill) pill.setAttribute("aria-label", kpi.pill.title);
      const tile = el("div", { className: "kpi" }, [el("div", { className: "big", textContent: kpi.value }), el("div", { className: "name", textContent: kpi.name }), pill]);
      if (kpi.help) tile.title = kpi.help;
      return tile;
    });
    // One row; it scrolls sideways on a narrow screen instead of wrapping into several lines.
    const row = el("div", { className: "kpis" }, tiles);
    row.setAttribute("role", "group");
    row.tabIndex = 0;
    first.append(row);
    if (period === "24h") first.append(el("div", { className: "sub", textContent: t.kpi_scope_24h }));
    first.append(chartNode(intro));

    const grid = matrixModel(stats.matrix);
    const matrixCard = section(t.matrix_title, [el("div", { className: "sub", textContent: grid ? t.matrix_sub : t.matrix_short })]);
    if (grid) {
      const heat = el("div", { className: "heat", role: "img" });
      heat.setAttribute("aria-label", fill(t.matrix_label, { total: grid.total }));
      heat.append(el("span"));
      for (let hour = 0; hour < 24; hour += 1) heat.append(el("span", { className: "hr", textContent: hour % 6 === 0 ? String(hour) : "" }));
      // Monday first; the weekday names come from the browser's locale.
      const monday = new Date(Date.UTC(2024, 0, 1));
      grid.rows.forEach((row, index) => {
        const name = new Date(monday.getTime() + index * 86400000).toLocaleDateString(ctx.language, { weekday: "short", timeZone: "UTC" });
        heat.append(el("span", { className: "lab", textContent: name }));
        row.forEach((cell, hour) => {
          const node = el("span", { className: "c", title: `${name} ${hour}:00 · ${cell.n}` });
          node.style.setProperty("--share", String(cell.share));
          heat.append(node);
        });
      });
      matrixCard.append(heat);
    }
    const rows = sourceRows(stats.sources, t);
    const sourcesCard = headed(t.sources_title, rows.length ? [] : [el("div", { className: "sub", textContent: t.sources_none })]);
    if (rows.length) {
      const bars = el("div", { className: "bars" });
      for (const row of rows) {
        const fill_ = el("i");
        const track = el("span", { className: "t" }, [fill_]);
        track.style.setProperty("--share", String(row.share));
        const name = el("span", { className: "nm" }, [el("span", { textContent: row.text }), row.kind ? el("span", { className: "kind", textContent: row.kind }) : ""]);
        bars.append(el("div", { className: "srcbar" }, [name, track, el("span", { className: "n", textContent: String(row.count) })]));
      }
      sourcesCard.append(bars);
    }
    return [first, matrixCard, sourcesCard];
  }

  // The first launch: the same cards as placeholders, each with one line on what it will show.
  // The three cards and the panel that slides out below them (D-251). Opening, closing and switching
  // animate the height of the panel; the page is redrawn every few seconds, so a redraw builds the
  // open panel in its final state and never replays the animation or moves the scroll position.
  function summaryBlock() {
    const model = summaryModel(data, now(), t, s, fmt);
    const build = { attention: attentionCard, coming: comingCard, last: lastActionsCard };
    const cards = el("div", { className: "sumcards" });
    const reveal = el("div", { className: `reveal static${openSummary ? " open" : ""}` });
    const inner = el("div", { className: "reveal-inner" });
    reveal.append(inner);
    reveal.style.height = openSummary ? "auto" : "0px";
    const panels = {};
    const buttons = {};
    for (const card of model) {
      const panel = el("div", { className: "panel", id: `hu-sum-${card.key}` });
      panel.dataset.key = card.key;
      panel.hidden = openSummary !== card.key;
      try {
        panel.append(build[card.key]());
      } catch (err) {
        console.error("Heads Up overview:", card.key, err);
        panel.append(section(card.title, [el("div", { className: "sub", textContent: `${t.load_failed} (${(err && err.message) || err})` })]));
      }
      panels[card.key] = panel;
      inner.append(panel);
      const button = el("button", { type: "button", className: `sumcard tone-${card.tone}` }, [
        el("span", { className: "sumtitle", textContent: card.title }),
        el("span", { className: "sumbig", textContent: String(card.big) }),
        el("span", { className: "sumsub", textContent: card.sub }),
        el("span", { className: "sumchev", "aria-hidden": "true" }),
      ]);
      button.dataset.sum = card.key;
      button.setAttribute("aria-controls", panel.id);
      button.setAttribute("aria-expanded", String(openSummary === card.key));
      button.setAttribute("aria-label", `${card.title}: ${card.big}, ${card.sub}`);
      button.addEventListener("click", () => toggleSummary(card.key));
      buttons[card.key] = button;
      cards.append(button);
    }

    function toggleSummary(key) {
      const next = openSummary === key ? null : key;
      const reduce = globalThis.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
      const from = reveal.getBoundingClientRect().height;
      openSummary = next;
      reveal.classList.remove("static");
      for (const [name, panel] of Object.entries(panels)) panel.hidden = name !== next;
      for (const [name, button] of Object.entries(buttons)) button.setAttribute("aria-expanded", String(name === next));
      reveal.classList.toggle("open", next !== null);
      const to = next === null ? 0 : inner.scrollHeight;
      if (reduce) {
        reveal.style.height = next === null ? "0px" : "auto";
        return;
      }
      reveal.style.height = `${from}px`;
      void reveal.offsetHeight; // the starting height is painted before the end height is set
      reveal.style.height = `${to}px`;
      const finish = () => {
        reveal.removeEventListener("transitionend", onEnd);
        if (openSummary === next && next !== null) reveal.style.height = "auto";
      };
      const onEnd = (event) => {
        if (event.target === reveal && event.propertyName === "height") finish();
      };
      reveal.addEventListener("transitionend", onEnd);
      setTimeout(finish, 700);
    }

    return el("div", { className: "summary" }, [cards, reveal]);
  }

  function placeholder(title, text) {
    return section(title, [el("div", { className: "placeholder", textContent: text })]);
  }

  // One card that fails to draw must not take the page down: it shows what failed instead.
  const guard = (name, build) => {
    try {
      return build();
    } catch (err) {
      console.error("Heads Up overview:", name, err);
      return section(name, [el("div", { className: "sub", textContent: `${t.load_failed} (${(err && err.message) || err})` })]);
    }
  };

  const guardList = (name, build) => {
    try {
      return build();
    } catch (err) {
      console.error("Heads Up overview:", name, err);
      return [guard(name, () => { throw err; })];
    }
  };

  function render() {
    const intro = !played;
    played = true;
    ctx.ui?.lockHeight(root);
    const focused = root.getRootNode().activeElement?.dataset?.sum;
    root.classList.toggle("enter", intro);
    root.replaceChildren(styleNode, el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }), tourHost);
    if (data.first_run) {
      if (!tour) {
        const go = el("button", { type: "button", className: "mini primary", textContent: t.first_run_button });
        go.addEventListener("click", () => startTour(true));
        root.append(el("div", { className: "hint" }, [el("span", { textContent: t.first_run }), go]));
      }
      if (data.status.count > 0) root.append(statusCard());
      root.append(shortcutRow());
      root.append(
        el("div", { className: "pair" }, [
          data.attention.length ? attentionCard() : placeholder(t.attention, t.ph_attention),
          data.coming_up.length ? comingCard() : placeholder(t.coming_title, t.ph_coming),
        ]),
        placeholder(t.activity, t.ph_activity),
        data.log.length ? lastActionsCard() : placeholder(t.last_actions, t.ph_last),
      );
      return;
    }
    root.append(
      guard(t.status, statusCard),
      guard(t.sc_label, shortcutRow),
      guard(t.attention, summaryBlock),
      ...guardList(t.activity, () => activityCards(intro)),
      guard(t.reach_title, reachCard),
    );
    // A redraw must not take the keyboard focus from an open card.
    if (focused) root.querySelector(`[data-sum="${focused}"]`)?.focus({ preventScroll: true });
  }

  async function loadStats() {
    try {
      stats = await hass.callWS({ type: "heads_up/panel_stats", period });
    } catch (err) {
      if (!stats) stats = false; // earlier numbers stay rather than turning into an error
    }
    if (data && !data.first_run) render();
  }

  // One load at a time: the 10-second timer and a button press must not run side by side. A load
  // that fails once (a blip of the connection, Home Assistant still starting) keeps what is on the
  // page and tries again after three seconds; only a page that never loaded shows the failure.
  let loading = false;
  let again = false;
  let retry = null;
  async function load() {
    if (loading) {
      again = true; // a button pressed meanwhile: load once more when this one is done
      return;
    }
    loading = true;
    clearTimeout(retry);
    try {
      try {
        data = await hass.callWS({ type: "heads_up/panel_overview" });
        render();
        if (!tourStarted) {
          tourStarted = true;
          startTour(new URLSearchParams(globalThis.location?.search || "").get("tour") === "1");
        }
      } catch (err) {
        console.error("Heads Up overview:", err);
        if (!data) root.replaceChildren(el("div", { textContent: `${t.load_failed} ${(err && err.message) || ""}`.trim() }));
        retry = setTimeout(load, 3000);
        return;
      }
      // The table is a dry run per severity: it loads on its own so a slow answer never holds the page.
      if (!data.first_run) {
        try {
          reach = await hass.callWS({ type: "heads_up/panel_reach" });
        } catch (err) {
          console.error("Heads Up overview table:", err);
          if (!reach) reach = false; // an earlier table stays rather than turning into an error
        }
        render();
        await loadStats();
      }
    } finally {
      loading = false;
    }
    if (again) {
      again = false;
      await load();
    }
  }

  root.append(el("div", { textContent: t.loading }));
  load();
  timer = setInterval(load, REFRESH_MS);
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      clearInterval(timer);
      clearTimeout(retry);
      tour?.destroy();
      root.remove();
    },
  };
}
