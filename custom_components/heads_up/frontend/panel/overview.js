// Heads Up panel: Overview page (D-118, D-244). Loaded by the shell when the page is opened.

export const STRINGS = {
  en: {
    title: "Overview",
    status: "Status",
    status_title_clear: "All clear",
    status_sub_clear: "No warning or critical notification is active.",
    status_sub_active: "Acknowledge, snooze or clear them here.",
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
    path_none: "Nothing was recorded for this message.",
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
    kpi_delivered: "Delivered",
    kpi_median: "Median time to acknowledge",
    kpi_held: "Held by quiet hours",
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
    source_action: "Actions (all calls)",
    source_gone: "deleted watch rule",
    source_rule: "Watch rule {name}",
    stats_failed: "The activity could not be loaded.",
    legend_label: "Severities",
    first_run: "No policies yet. The introduction explains a few defaults you can switch on.",
    first_run_button: "Restart introduction",
    ph_attention: "Problems with your setup show up here.",
    ph_coming: "Escalations, reminders and summaries show up here.",
    ph_activity: "Your last 24 hours show up here once messages arrive.",
    ph_last: "What Heads Up did shows up here.",
    loading: "Loading…",
    load_failed: "The overview could not be loaded.",
  },
  de: {
    title: "Übersicht",
    status: "Status",
    status_title_clear: "Alles ruhig",
    status_sub_clear: "Keine Warnung und keine kritische Meldung ist aktiv.",
    status_sub_active: "Bestätige, stelle zurück oder entferne sie hier.",
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
    path_none: "Zu dieser Meldung wurde nichts aufgezeichnet.",
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
    kpi_delivered: "Zugestellt",
    kpi_median: "Mittlere Zeit bis zur Bestätigung",
    kpi_held: "Von der Ruhezeit zurückgehalten",
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
    source_action: "Aktionen (alle Aufrufe)",
    source_gone: "gelöschte Überwachungsregel",
    source_rule: "Überwachungsregel {name}",
    stats_failed: "Die Aktivität konnte nicht geladen werden.",
    legend_label: "Schweregrade",
    first_run: "Noch keine Richtlinien. Die Einführung erklärt ein paar Standards, die du einschalten kannst.",
    first_run_button: "Einführung neu starten",
    ph_attention: "Probleme mit deiner Einrichtung erscheinen hier.",
    ph_coming: "Eskalationen, Erinnerungen und Zusammenfassungen erscheinen hier.",
    ph_activity: "Deine letzten 24 Stunden erscheinen hier, sobald Meldungen eintreffen.",
    ph_last: "Was Heads Up getan hat, erscheint hier.",
    loading: "Lädt…",
    load_failed: "Die Übersicht konnte nicht geladen werden.",
  },
  fr: {
    title: "Vue d'ensemble",
    status: "État",
    status_title_clear: "Tout est calme",
    status_sub_clear: "Aucun avertissement ni message critique n'est actif.",
    status_sub_active: "Acquittez, reportez ou retirez-les ici.",
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
    path_none: "Rien n'a été enregistré pour ce message.",
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
    kpi_delivered: "Remis",
    kpi_median: "Délai médian de confirmation",
    kpi_held: "Retenus par les heures calmes",
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
    source_action: "Actions (tous les appels)",
    source_gone: "règle de surveillance supprimée",
    source_rule: "Règle de surveillance {name}",
    stats_failed: "L'activité n'a pas pu être chargée.",
    legend_label: "Gravités",
    first_run: "Aucune politique pour l'instant. L'introduction explique quelques réglages par défaut que vous pouvez activer.",
    first_run_button: "Relancer l'introduction",
    ph_attention: "Les problèmes de votre configuration apparaissent ici.",
    ph_coming: "Les escalades, rappels et résumés apparaissent ici.",
    ph_activity: "Vos dernières 24 heures apparaissent ici dès que des messages arrivent.",
    ph_last: "Ce que Heads Up a fait apparaît ici.",
    loading: "Chargement…",
    load_failed: "La vue d'ensemble n'a pas pu être chargée.",
  },
  es: {
    title: "Resumen",
    status: "Estado",
    status_title_clear: "Todo en calma",
    status_sub_clear: "Ningún aviso ni mensaje crítico está activo.",
    status_sub_active: "Confírmalos, pospónlos o retíralos aquí.",
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
    path_none: "No se registró nada de este mensaje.",
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
    kpi_delivered: "Entregadas",
    kpi_median: "Tiempo mediano hasta confirmar",
    kpi_held: "Retenidas por las horas de silencio",
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
    source_action: "Acciones (todas las llamadas)",
    source_gone: "regla de vigilancia eliminada",
    source_rule: "Regla de vigilancia {name}",
    stats_failed: "No se pudo cargar la actividad.",
    legend_label: "Gravedades",
    first_run: "Aún no hay políticas. La introducción explica algunos valores por defecto que puedes activar.",
    first_run_button: "Reiniciar la introducción",
    ph_attention: "Los problemas de tu configuración aparecen aquí.",
    ph_coming: "Las escaladas, recordatorios y resúmenes aparecen aquí.",
    ph_activity: "Tus últimas 24 horas aparecen aquí cuando lleguen mensajes.",
    ph_last: "Lo que hizo Heads Up aparece aquí.",
    loading: "Cargando…",
    load_failed: "No se pudo cargar el resumen.",
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

// The path of one message, oldest step first. Identical steps are written once with a count.
export function pathLines(entries, s, fmt) {
  const lines = [];
  for (const entry of [...(entries || [])].reverse()) {
    let text;
    if (entry.channel === "timer") text = [entry.timer?.policy, s.result[entry.result] || entry.result].filter(Boolean).join(" · ");
    else if (!entry.channel) text = [s.result[entry.result] || entry.result, entry.who].filter(Boolean).join(" · ");
    else {
      const reason = entry.reason ? `: ${fmt.reasonText(entry.reason, s)}` : "";
      text = `${fmt.channelName(entry.channel, s)} · ${s.result[entry.result] || entry.result}${reason}`;
    }
    const found = lines.find((line) => line.text === text);
    if (found) found.n += 1;
    else lines.push({ text, time: entry.time, n: 1 });
  }
  return lines;
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

// The four numbers of the Activity card, as text and a pill for the change.
export function kpiModel(numbers, t) {
  const change = numbers.change;
  return {
    notifications: String(numbers.notifications ?? 0),
    change: change === null || change === undefined ? null : { up: change > 0, text: fill(t.kpi_change, { sign: change > 0 ? "+" : "", n: change }) },
    delivered: numbers.delivered === null || numbers.delivered === undefined ? t.kpi_none : `${numbers.delivered} %`,
    median: durationText(numbers.median_ack_seconds, t),
    held: String(numbers.held_quiet ?? 0),
  };
}

// The weekday-by-hour grid: each cell's share of the busiest cell (0 to 1), Monday first.
export function matrixModel(matrix) {
  if (!matrix) return null;
  const peak = Math.max(1, ...matrix.flat());
  return { peak, total: matrix.flat().reduce((a, b) => a + b, 0), rows: matrix.map((row) => row.map((n) => ({ n, share: n / peak }))) };
}

// A source of the top list: its name and its share of the busiest one.
export function sourceRows(sources, t) {
  const peak = Math.max(1, ...sources.map((x) => x.count));
  return sources.map((x) => ({
    text: x.kind === "action" ? t.source_action : x.name ? fill(t.source_rule, { name: x.name }) : t.source_gone,
    count: x.count,
    share: x.count / peak,
  }));
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
.hu-overview section { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: var(--hu-radius); padding: 18px 20px; margin-bottom: 16px; box-shadow: var(--hu-shadow); animation: hu-rise .45s both; }
.hu-overview section:nth-of-type(2) { animation-delay: .05s; } .hu-overview section:nth-of-type(3) { animation-delay: .1s; }
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
.hu-overview .context { margin: 0 0 8px; display: grid; gap: 2px; }
.hu-overview .context .sub:first-child { color: var(--primary-text-color); }

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
.hu-overview .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 12px; margin: 12px 0 8px; }
.hu-overview .kpi { padding: 12px 14px; border-radius: 14px; background: var(--hu-chip); }
.hu-overview .kpi .big { font-size: 28px; font-weight: 700; line-height: 1.1; letter-spacing: -.02em; }
.hu-overview .kpi .name { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }
.hu-overview .kpi .pill { margin-top: 6px; font-size: 11px; }
.hu-overview .legend { display: flex; gap: 12px; font-size: 12px; color: var(--secondary-text-color); flex-wrap: wrap; margin-top: 8px; }
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
@keyframes hu-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes hu-pulse { 0% { box-shadow: 0 0 0 8px color-mix(in srgb, var(--hero-tint) 30%, transparent), 0 0 0 18px color-mix(in srgb, var(--hero-tint) 7%, transparent); } 100% { box-shadow: 0 0 0 8px color-mix(in srgb, var(--hero-tint) 14%, transparent), 0 0 0 26px transparent; } }
@keyframes hu-grow { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }
@keyframes hu-glow { 0%, 100% { opacity: .35; } 50% { opacity: .75; } }
@media (prefers-reduced-motion: reduce) { .hu-overview section, .hu-overview .orb, .hu-overview svg.chart .bar, .hu-overview svg.chart .bar .shine { animation: none !important; } .hu-overview .reach button.cell { transition: none; } }
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
  let tour = null;
  let tourStarted = false;
  let period = "week";
  let stats = null; // the Activity data of `period`, or false when it could not be loaded
  // The tour lives in its own node, so the page's redraws never wipe it.
  const tourHost = el("div");
  const root = el("div", { className: "hu-overview" });
  container.append(root);

  const now = () => Date.now();
  const section = (title, children, label) => {
    const box = el("section", {}, [el("h2", { textContent: title }), ...children]);
    if (label) box.setAttribute("aria-label", label);
    return box;
  };

  // The path of a message: its trace, oldest step first.
  async function togglePath(id) {
    if (openPaths[id]) {
      delete openPaths[id];
      render();
      return;
    }
    openPaths[id] = "loading";
    render();
    try {
      const result = await hass.callWS({ type: "heads_up/panel_trace", message_id: id });
      openPaths[id] = result?.entries || [];
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
      const lines = pathLines(value, s, fmt);
      if (!lines.length) box.append(el("div", { className: "sub", textContent: t.path_none }));
      for (const line of lines) {
        const times = line.n > 1 ? ` ×${line.n}` : "";
        box.append(el("div", {}, [el("span", { className: "sub", textContent: `${fmt.timeAgo(line.time, now(), s)} · ` }), el("span", { textContent: line.text + times })]));
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
    if (!active) return box;
    const items = el("div", { className: "items" });
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

  function lastActionsCard() {
    const log = el("ul");
    if (data.log.length === 0) log.append(el("li", { className: "placeholder", textContent: t.last_none }));
    for (const entry of data.log) {
      const text = [fmt.logText(entry, s), entry.title || s.severity[entry.severity]].filter(Boolean).join(" · ");
      const acts = el("div", { className: "acts" });
      // A message that still has a trace can unfold its path.
      if (entry.message_id) acts.append(pathButton(entry.message_id));
      const row = el("li", {}, [el("div", { className: "row log" }, [el("span", { className: "time", textContent: fmt.timeAgo(entry.time, now(), s) }), el("span", { className: "text", textContent: text }), acts])]);
      if (entry.message_id && openPaths[entry.message_id]) row.append(pathNode(entry.message_id));
      log.append(row);
    }
    const more = el("button", { type: "button", className: "mini", textContent: t.open_messages });
    more.addEventListener("click", () => ctx.navigate("messages"));
    const refresh = el("button", { type: "button", className: "mini", textContent: t.refresh, style: "margin-left:8px" });
    refresh.addEventListener("click", load);
    return section(t.last_actions, [log, el("div", { style: "margin-top:10px" }, [more, refresh])]);
  }

  function reachCard() {
    if (reach === false) return section(t.reach_title, [el("div", { className: "sub", textContent: t.reach_failed })]);
    if (!reach) return section(t.reach_title, [el("div", { className: "sub", textContent: t.loading })]);
    const lines = contextLines(reach.context, now(), t, s, fmt, ctx.language);
    const context = el("div", { className: "context" }, [el("div", { className: "sub", textContent: t.reach_intro }), ...lines.map((line) => el("div", { className: "sub", textContent: line }))]);
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
    const parts = [context, table];
    if (selected) {
      const detail = cellDetail(reach.cells[selected.channel][selected.severity], selected.channel, selected.severity, t, s, fmt);
      const box = el("div", { className: "detail" }, [el("div", { className: "t", textContent: detail.title }), el("div", { textContent: detail.sentence })]);
      if (detail.reason) box.append(el("div", { className: "sub", textContent: detail.reason }));
      if (detail.empty) box.append(el("div", { className: "sub", textContent: detail.empty }));
      for (const line of detail.people) box.append(el("div", { className: "sub", textContent: line }));
      parts.push(box);
    }
    return section(t.reach_title, parts);
  }

  // The bars of the last 24 hours, stacked by severity. The bars grow in once, when the page opens;
  // the page refreshes every 10 seconds and must not replay that.
  function chartNode(intro) {
    const model = chartModel({ buckets: stats.buckets, total: stats.numbers.notifications });
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
    const kpi = kpiModel(stats.numbers, t);
    const tile = (value, name, pill) => el("div", { className: "kpi" }, [el("div", { className: "big", textContent: value }), el("div", { className: "name", textContent: name }), pill || ""]);
    const change = kpi.change ? el("span", { className: `pill ${kpi.change.up ? "warning" : "ok"}`, textContent: kpi.change.text }) : null;
    first.append(
      el("div", { className: "kpis" }, [tile(kpi.notifications, t.kpi_notifications, change), tile(kpi.delivered, t.kpi_delivered), tile(kpi.median, t.kpi_median), tile(kpi.held, t.kpi_held)]),
    );
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
    const sourcesCard = section(t.sources_title, rows.length ? [] : [el("div", { className: "sub", textContent: t.sources_none })]);
    if (rows.length) {
      const bars = el("div", { className: "bars" });
      for (const row of rows) {
        const fill_ = el("i");
        const track = el("span", { className: "t" }, [fill_]);
        track.style.setProperty("--share", String(row.share));
        bars.append(el("div", { className: "srcbar" }, [el("span", { textContent: row.text }), track, el("span", { className: "n", textContent: String(row.count) })]));
      }
      sourcesCard.append(bars);
    }
    return [first, matrixCard, sourcesCard];
  }

  // The first launch: the same cards as placeholders, each with one line on what it will show.
  function placeholder(title, text) {
    return section(title, [el("div", { className: "placeholder", textContent: text })]);
  }

  function render() {
    const intro = !played;
    played = true;
    ctx.ui?.lockHeight(root);
    root.replaceChildren(el("style", { textContent: CSS }), el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }), tourHost);
    if (data.first_run) {
      if (!tour) {
        const go = el("button", { type: "button", className: "mini primary", textContent: t.first_run_button });
        go.addEventListener("click", () => startTour(true));
        root.append(el("div", { className: "hint" }, [el("span", { textContent: t.first_run }), go]));
      }
      if (data.status.count > 0) root.append(statusCard());
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
    root.append(statusCard(), el("div", { className: "pair" }, [attentionCard(), comingCard()]), lastActionsCard(), reachCard(), ...activityCards(intro));
  }

  async function loadStats() {
    try {
      stats = await hass.callWS({ type: "heads_up/panel_stats", period });
    } catch (err) {
      stats = false;
    }
    if (data && !data.first_run) render();
  }

  async function load() {
    try {
      data = await hass.callWS({ type: "heads_up/panel_overview" });
      render();
      if (!tourStarted) {
        tourStarted = true;
        startTour(new URLSearchParams(globalThis.location?.search || "").get("tour") === "1");
      }
    } catch (err) {
      root.replaceChildren(el("div", { textContent: t.load_failed }));
      return;
    }
    // The table is a dry run per severity: it loads on its own so a slow answer never holds the page.
    if (!data.first_run) {
      try {
        reach = await hass.callWS({ type: "heads_up/panel_reach" });
      } catch (err) {
        reach = false;
      }
      render();
      await loadStats();
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
      tour?.destroy();
      root.remove();
    },
  };
}
