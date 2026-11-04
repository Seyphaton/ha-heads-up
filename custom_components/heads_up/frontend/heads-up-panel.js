// Heads Up admin panel: the shell (D-117). One plain ES module, no build step (D-021).
// Pages are separate files under panel/, loaded when opened. Text only via textContent.

export const NAV = [
  { id: "overview", pages: ["status"] },
  { id: "notifications", pages: ["test", "rules", "messages"] },
  { id: "configuration", pages: ["audiences", "recipients", "policies", "channels"] },
  { id: "settings", pages: ["general"] },
  { id: "faq", pages: ["faq"] },
];
// Page id to the module that renders it. A page without a module shows a note.
export const MODULES = {
  status: "overview.js",
  test: "test_send.js",
  messages: "messages.js",
  rules: "rules.js",
  general: "settings.js",
  audiences: "audiences.js",
  recipients: "recipients.js",
  policies: "policies.js",
  channels: "channels.js",
  faq: "help.js",
};
export const DEFAULT_PAGE = "status";
export const BASE_PATH = "/heads-up";

export const STRINGS = {
  en: {
    shared: {"common": {"save": "Save", "cancel": "Cancel", "delete": "Delete", "edit": "Edit", "add": "Add", "name": "Name", "saved": "Saved.", "deleted": "Deleted.", "delete_confirm": "Delete {name}?", "in_use": "In use by {names}. Remove it from those policies first.", "valid": "No problems.", "problems": "Problems", "yaml": "Stored as YAML", "hub_off": "The hub is switched off. Switch it on in Settings to edit this.", "none": "none", "yes": "yes", "enabled": "Enabled", "back": "Back to the list"}, "log_cleared_plain": "Cleared", "severity": {"critical": "Critical", "warning": "Warning", "info": "Info", "success": "Success"}, "channel": {"banner": "Banner", "push": "Push", "popup": "Popup", "speak": "Speak", "persistent": "Persistent HASS Notification", "mail": "Mail"}, "ago_now": "just now", "ago_min": "{n} min ago", "ago_hour": "{n} h ago", "ago_day": "{n} d ago", "in_now": "any moment", "in_min": "in {n} min", "in_hour": "in {n} h", "in_day": "in {n} d", "state_held": "In the summary of {policy}", "state_escalating_pending": "Escalation {policy} sends {when} unless someone acknowledges", "state_escalating_sent": "Escalation {policy} was sent, nobody acknowledged yet", "state_reminding": "Reminding ({policy}), next {when}", "state_snoozed": "Snoozed, back {when}", "state_acknowledged": "Acknowledged", "log_created": "Created ({severity}, {channels})", "log_escalation_sent": "Escalation sent: {detail}", "log_reminder_sent": "Reminder sent: {detail}", "log_acknowledged": "Acknowledged by {detail}", "log_acknowledged_anon": "Acknowledged", "log_dismissed": "Dismissed by {detail}", "log_dismissed_anon": "Dismissed", "log_snoozed": "Snoozed by {detail}", "log_snoozed_anon": "Snoozed", "log_unsnoozed": "Snooze ended for {detail}", "log_unsnoozed_anon": "Snooze ended", "log_summary_sent": "Summary sent on {channel} ({n} messages)", "log_fallback_sent": "Fallback sent: {detail}", "log_skipped": "Skipped on {channel}: {reason}", "log_failed": "Failed on {channel}: {reason}", "log_expired": "Expired", "log_cleared": "Cleared ({reason})", "att_rule_entity": "Rule {subject} watches {detail}, which is unavailable.", "att_device_service": "{subject}: the device {detail} has no notify service in Home Assistant.", "att_person_no_device": "{subject} has no usable device: push is skipped.", "att_group_empty": "Recipient group {subject} has no speaker that exists.", "att_policy_invalid": "Policy {subject} is invalid: {reason}.", "att_policy_target": "Policy {subject} names an audience or group that no longer exists.", "att_no_critical_escalation": "No escalation policy covers critical messages.", "att_hub_off": "The hub is switched off.", "reason": {"waiting_for_condition": "waiting for its condition", "no_recipients": "nobody to send to", "channel_unavailable": "channel not available", "no_usable_device": "no usable device", "service_not_found": "service not found", "channel_not_accepted": "channel not accepted by the profile", "presence_unknown": "presence unknown", "quiet_hours": "quiet hours", "cooldown": "said a moment ago", "already_spoken": "already said", "popup_off": "popups off for this severity", "no_user": "no Home Assistant user", "entity_missing": "speaker missing", "send_failed": "sending failed", "no_tts_engine": "no text-to-speech engine", "max_wait_exceeded": "waited long enough", "no_longer_needed": "no longer needed", "audience_missing": "audience deleted", "group_missing": "group deleted", "dismissed": "dismissed", "snoozed": "snoozed", "nothing_to_say": "nothing to say", "not_clearable": "cannot be taken back", "device_missing": "device missing", "cleared": "cleared", "expired": "expired", "condition": "condition ended", "dismissed_global": "dismissed for everyone", "evicted": "evicted", "rule": "rule ended", "admin": "cleared by an admin", "clear_all": "cleared with all", "unknown_type": "unknown policy type", "after_required": "no time set", "channels_required": "no channels", "channel_unknown": "channel not allowed", "every_required": "no interval", "max_required": "no maximum", "window_empty": "empty time window", "when_required": "no trigger", "time_invalid": "invalid time", "wait_invalid": "invalid wait", "user_mismatch": "wrong user", "rate_limited": "over the rate limit", "duplicate": "same as the last update"}, "result": {"sent": "sent", "held": "held", "skipped": "skipped", "failed": "failed", "cleared": "cleared", "planned": "planned", "acknowledged": "acknowledged", "escalated": "escalated", "summary": "summary", "fallback": "fallback"}},
    title: "Heads Up",
    menu: "Open the sidebar",
    tour_paused: "Welcome tour paused after step {n} of {total}.",
    tour_continue: "Continue the tour",
    tour_end: "End the tour",
    groups: { overview: "Overview", notifications: "Notifications and rules", configuration: "Configuration", settings: "Settings", faq: "FAQ and examples" },
    pages: { status: "Status", test: "Test send", rules: "Watch rules", messages: "Messages", audiences: "Audiences", recipients: "Recipients", policies: "Policies", channels: "Channels", general: "General", faq: "FAQ and examples" },
    not_built: "This page is not available.",
    loading: "Loading…",
    load_failed: "The page could not be loaded. Reload the browser page.",
    nav_label: "Heads Up pages",
  },
  de: {
    shared: {"common": {"save": "Speichern", "cancel": "Abbrechen", "delete": "Löschen", "edit": "Bearbeiten", "add": "Hinzufügen", "name": "Name", "saved": "Gespeichert.", "deleted": "Gelöscht.", "delete_confirm": "{name} löschen?", "in_use": "Wird von {names} verwendet. Entferne es zuerst aus diesen Richtlinien.", "valid": "Keine Probleme.", "problems": "Probleme", "yaml": "Gespeichert als YAML", "hub_off": "Der Hub ist ausgeschaltet. Schalte ihn in den Einstellungen ein, um dies zu bearbeiten.", "none": "keine", "yes": "ja", "enabled": "Aktiv", "back": "Zurück zur Liste"}, "log_cleared_plain": "Entfernt", "severity": {"critical": "Kritisch", "warning": "Warnung", "info": "Info", "success": "Erfolg"}, "channel": {"banner": "Banner", "push": "Push", "popup": "Popup", "speak": "Sprache", "persistent": "Persistente HASS-Benachrichtigung", "mail": "E-Mail"}, "ago_now": "gerade eben", "ago_min": "vor {n} Min.", "ago_hour": "vor {n} Std.", "ago_day": "vor {n} T.", "in_now": "gleich", "in_min": "in {n} Min.", "in_hour": "in {n} Std.", "in_day": "in {n} T.", "state_held": "In der Zusammenfassung von {policy}", "state_escalating_pending": "Eskalation {policy} sendet {when}, wenn niemand bestätigt", "state_escalating_sent": "Eskalation {policy} wurde gesendet, noch niemand hat bestätigt", "state_reminding": "Erinnerung ({policy}), nächste {when}", "state_snoozed": "Zurückgestellt, zurück {when}", "state_acknowledged": "Bestätigt", "log_created": "Erstellt ({severity}, {channels})", "log_escalation_sent": "Eskalation gesendet: {detail}", "log_reminder_sent": "Erinnerung gesendet: {detail}", "log_acknowledged": "Bestätigt von {detail}", "log_acknowledged_anon": "Bestätigt", "log_dismissed": "Ausgeblendet von {detail}", "log_dismissed_anon": "Ausgeblendet", "log_snoozed": "Zurückgestellt von {detail}", "log_snoozed_anon": "Zurückgestellt", "log_unsnoozed": "Zurückstellung beendet für {detail}", "log_unsnoozed_anon": "Zurückstellung beendet", "log_summary_sent": "Zusammenfassung gesendet auf {channel} ({n} Meldungen)", "log_fallback_sent": "Ersatz gesendet: {detail}", "log_skipped": "Übersprungen auf {channel}: {reason}", "log_failed": "Fehlgeschlagen auf {channel}: {reason}", "log_expired": "Abgelaufen", "log_cleared": "Entfernt ({reason})", "att_rule_entity": "Regel {subject} überwacht {detail}, das nicht verfügbar ist.", "att_device_service": "{subject}: Das Gerät {detail} hat keinen Benachrichtigungsdienst in Home Assistant.", "att_person_no_device": "{subject} hat kein nutzbares Gerät: Push wird übersprungen.", "att_group_empty": "Die Empfängergruppe {subject} hat keinen vorhandenen Lautsprecher.", "att_policy_invalid": "Richtlinie {subject} ist ungültig: {reason}.", "att_policy_target": "Richtlinie {subject} nennt eine Zielgruppe oder Gruppe, die es nicht mehr gibt.", "att_no_critical_escalation": "Keine Eskalationsrichtlinie deckt kritische Meldungen ab.", "att_hub_off": "Der Hub ist ausgeschaltet.", "reason": {"waiting_for_condition": "wartet auf ihre Bedingung", "no_recipients": "niemand zum Senden", "channel_unavailable": "Kanal nicht verfügbar", "no_usable_device": "kein nutzbares Gerät", "service_not_found": "Dienst nicht gefunden", "channel_not_accepted": "Kanal vom Profil nicht akzeptiert", "presence_unknown": "Anwesenheit unbekannt", "quiet_hours": "Ruhezeit", "cooldown": "gerade eben gesagt", "already_spoken": "schon gesagt", "popup_off": "Popups für diesen Schweregrad aus", "no_user": "kein Home-Assistant-Benutzer", "entity_missing": "Lautsprecher fehlt", "send_failed": "Senden fehlgeschlagen", "no_tts_engine": "keine Text-zu-Sprache-Engine", "max_wait_exceeded": "lange genug gewartet", "no_longer_needed": "nicht mehr nötig", "audience_missing": "Zielgruppe gelöscht", "group_missing": "Gruppe gelöscht", "dismissed": "ausgeblendet", "snoozed": "zurückgestellt", "nothing_to_say": "nichts zu sagen", "not_clearable": "kann nicht zurückgenommen werden", "device_missing": "Gerät fehlt", "cleared": "entfernt", "expired": "abgelaufen", "condition": "Bedingung beendet", "dismissed_global": "für alle ausgeblendet", "evicted": "verdrängt", "rule": "Regel beendet", "admin": "von einem Admin entfernt", "clear_all": "mit allen entfernt", "unknown_type": "unbekannte Richtlinienart", "after_required": "keine Zeit gesetzt", "channels_required": "keine Kanäle", "channel_unknown": "Kanal nicht erlaubt", "every_required": "kein Intervall", "max_required": "kein Maximum", "window_empty": "leeres Zeitfenster", "when_required": "kein Auslöser", "time_invalid": "ungültige Uhrzeit", "wait_invalid": "ungültige Wartezeit", "user_mismatch": "falscher Benutzer", "rate_limited": "über dem Limit", "duplicate": "gleich wie die letzte Aktualisierung"}, "result": {"sent": "gesendet", "held": "zurückgehalten", "skipped": "übersprungen", "failed": "fehlgeschlagen", "cleared": "entfernt", "planned": "geplant", "acknowledged": "bestätigt", "escalated": "eskaliert", "summary": "Zusammenfassung", "fallback": "Ersatz"}},
    title: "Heads Up",
    menu: "Seitenleiste öffnen",
    tour_paused: "Willkommens-Tour nach Schritt {n} von {total} pausiert.",
    tour_continue: "Tour fortsetzen",
    tour_end: "Tour beenden",
    groups: { overview: "Übersicht", notifications: "Benachrichtigungen und Regeln", configuration: "Konfiguration", settings: "Einstellungen", faq: "FAQ und Beispiele" },
    pages: { status: "Status", test: "Testsenden", rules: "Überwachungsregeln", messages: "Meldungen", audiences: "Zielgruppen", recipients: "Empfänger", policies: "Richtlinien", channels: "Kanäle", general: "Allgemein", faq: "FAQ und Beispiele" },
    not_built: "Diese Seite ist nicht verfügbar.",
    loading: "Lädt…",
    load_failed: "Die Seite konnte nicht geladen werden. Lade die Browserseite neu.",
    nav_label: "Heads-Up-Seiten",
  },
  fr: {
    shared: {"common": {"save": "Enregistrer", "cancel": "Annuler", "delete": "Supprimer", "edit": "Modifier", "add": "Ajouter", "name": "Nom", "saved": "Enregistré.", "deleted": "Supprimé.", "delete_confirm": "Supprimer {name} ?", "in_use": "Utilisé par {names}. Retirez-le d'abord de ces politiques.", "valid": "Aucun problème.", "problems": "Problèmes", "yaml": "Stocké en YAML", "hub_off": "Le hub est désactivé. Activez-le dans Réglages pour modifier ceci.", "none": "aucun", "yes": "oui", "enabled": "Activée", "back": "Retour à la liste"}, "log_cleared_plain": "Supprimé", "severity": {"critical": "Critique", "warning": "Avertissement", "info": "Info", "success": "Succès"}, "channel": {"banner": "Bannière", "push": "Push", "popup": "Fenêtre", "speak": "Voix", "persistent": "Notification persistante HASS", "mail": "Courriel"}, "ago_now": "à l'instant", "ago_min": "il y a {n} min", "ago_hour": "il y a {n} h", "ago_day": "il y a {n} j", "in_now": "dans un instant", "in_min": "dans {n} min", "in_hour": "dans {n} h", "in_day": "dans {n} j", "state_held": "Dans le résumé de {policy}", "state_escalating_pending": "L'escalade {policy} envoie {when} si personne ne confirme", "state_escalating_sent": "L'escalade {policy} a été envoyée, personne n'a encore confirmé", "state_reminding": "Rappel ({policy}), prochain {when}", "state_snoozed": "Reporté, retour {when}", "state_acknowledged": "Confirmé", "log_created": "Créé ({severity}, {channels})", "log_escalation_sent": "Escalade envoyée : {detail}", "log_reminder_sent": "Rappel envoyé : {detail}", "log_acknowledged": "Confirmé par {detail}", "log_acknowledged_anon": "Confirmé", "log_dismissed": "Masqué par {detail}", "log_dismissed_anon": "Masqué", "log_snoozed": "Reporté par {detail}", "log_snoozed_anon": "Reporté", "log_unsnoozed": "Report terminé pour {detail}", "log_unsnoozed_anon": "Report terminé", "log_summary_sent": "Résumé envoyé sur {channel} ({n} messages)", "log_fallback_sent": "Repli envoyé : {detail}", "log_skipped": "Ignoré sur {channel} : {reason}", "log_failed": "Échec sur {channel} : {reason}", "log_expired": "Expiré", "log_cleared": "Supprimé ({reason})", "att_rule_entity": "La règle {subject} surveille {detail}, qui est indisponible.", "att_device_service": "{subject} : l'appareil {detail} n'a pas de service de notification dans Home Assistant.", "att_person_no_device": "{subject} n'a pas d'appareil utilisable : le push est ignoré.", "att_group_empty": "Le groupe de destinataires {subject} n'a aucun haut-parleur existant.", "att_policy_invalid": "La politique {subject} est invalide : {reason}.", "att_policy_target": "La politique {subject} nomme une audience ou un groupe qui n'existe plus.", "att_no_critical_escalation": "Aucune politique d'escalade ne couvre les messages critiques.", "att_hub_off": "Le hub est désactivé.", "reason": {"waiting_for_condition": "attend sa condition", "no_recipients": "personne à qui envoyer", "channel_unavailable": "canal indisponible", "no_usable_device": "aucun appareil utilisable", "service_not_found": "service introuvable", "channel_not_accepted": "canal refusé par le profil", "presence_unknown": "présence inconnue", "quiet_hours": "heures calmes", "cooldown": "dit à l'instant", "already_spoken": "déjà dit", "popup_off": "fenêtres désactivées pour cette gravité", "no_user": "aucun utilisateur Home Assistant", "entity_missing": "haut-parleur absent", "send_failed": "échec de l'envoi", "no_tts_engine": "aucun moteur de synthèse vocale", "max_wait_exceeded": "attente suffisante", "no_longer_needed": "plus nécessaire", "audience_missing": "audience supprimée", "group_missing": "groupe supprimé", "dismissed": "masqué", "snoozed": "reporté", "nothing_to_say": "rien à dire", "not_clearable": "ne peut pas être repris", "device_missing": "appareil absent", "cleared": "supprimé", "expired": "expiré", "condition": "condition terminée", "dismissed_global": "masqué pour tous", "evicted": "évincé", "rule": "règle terminée", "admin": "supprimé par un administrateur", "clear_all": "supprimé avec tous", "unknown_type": "type de politique inconnu", "after_required": "aucun délai", "channels_required": "aucun canal", "channel_unknown": "canal non autorisé", "every_required": "aucun intervalle", "max_required": "aucun maximum", "window_empty": "plage vide", "when_required": "aucun déclencheur", "time_invalid": "heure invalide", "wait_invalid": "attente invalide", "user_mismatch": "mauvais utilisateur", "rate_limited": "au-delà de la limite", "duplicate": "identique à la dernière mise à jour"}, "result": {"sent": "envoyé", "held": "retenu", "skipped": "ignoré", "failed": "échec", "cleared": "supprimé", "planned": "prévu", "acknowledged": "confirmé", "escalated": "escaladé", "summary": "résumé", "fallback": "repli"}},
    title: "Heads Up",
    menu: "Ouvrir la barre latérale",
    tour_paused: "Visite de bienvenue en pause après l'étape {n} sur {total}.",
    tour_continue: "Continuer la visite",
    tour_end: "Terminer la visite",
    groups: { overview: "Vue d'ensemble", notifications: "Notifications et règles", configuration: "Configuration", settings: "Réglages", faq: "FAQ et exemples" },
    pages: { status: "État", test: "Envoi de test", rules: "Règles de surveillance", messages: "Messages", audiences: "Audiences", recipients: "Destinataires", policies: "Politiques", channels: "Canaux", general: "Général", faq: "FAQ et exemples" },
    not_built: "Cette page n'est pas disponible.",
    loading: "Chargement…",
    load_failed: "La page n'a pas pu être chargée. Rechargez la page du navigateur.",
    nav_label: "Pages Heads Up",
  },
  es: {
    shared: {"common": {"save": "Guardar", "cancel": "Cancelar", "delete": "Eliminar", "edit": "Editar", "add": "Añadir", "name": "Nombre", "saved": "Guardado.", "deleted": "Eliminado.", "delete_confirm": "¿Eliminar {name}?", "in_use": "Lo usan {names}. Quítalo primero de esas políticas.", "valid": "Sin problemas.", "problems": "Problemas", "yaml": "Guardado como YAML", "hub_off": "El hub está desactivado. Actívalo en Ajustes para editar esto.", "none": "ninguno", "yes": "sí", "enabled": "Activa", "back": "Volver a la lista"}, "log_cleared_plain": "Borrado", "severity": {"critical": "Crítico", "warning": "Aviso", "info": "Info", "success": "Éxito"}, "channel": {"banner": "Aviso", "push": "Push", "popup": "Ventana", "speak": "Voz", "persistent": "Notificación persistente de HASS", "mail": "Correo"}, "ago_now": "ahora mismo", "ago_min": "hace {n} min", "ago_hour": "hace {n} h", "ago_day": "hace {n} d", "in_now": "en un momento", "in_min": "en {n} min", "in_hour": "en {n} h", "in_day": "en {n} d", "state_held": "En el resumen de {policy}", "state_escalating_pending": "El escalado {policy} envía {when} si nadie confirma", "state_escalating_sent": "El escalado {policy} se envió, nadie ha confirmado aún", "state_reminding": "Recordando ({policy}), próximo {when}", "state_snoozed": "Pospuesto, vuelve {when}", "state_acknowledged": "Confirmado", "log_created": "Creado ({severity}, {channels})", "log_escalation_sent": "Escalado enviado: {detail}", "log_reminder_sent": "Recordatorio enviado: {detail}", "log_acknowledged": "Confirmado por {detail}", "log_acknowledged_anon": "Confirmado", "log_dismissed": "Descartado por {detail}", "log_dismissed_anon": "Descartado", "log_snoozed": "Pospuesto por {detail}", "log_snoozed_anon": "Pospuesto", "log_unsnoozed": "Pospuesto terminado para {detail}", "log_unsnoozed_anon": "Pospuesto terminado", "log_summary_sent": "Resumen enviado en {channel} ({n} mensajes)", "log_fallback_sent": "Alternativa enviada: {detail}", "log_skipped": "Omitido en {channel}: {reason}", "log_failed": "Falló en {channel}: {reason}", "log_expired": "Caducado", "log_cleared": "Borrado ({reason})", "att_rule_entity": "La regla {subject} vigila {detail}, que no está disponible.", "att_device_service": "{subject}: el dispositivo {detail} no tiene servicio de notificación en Home Assistant.", "att_person_no_device": "{subject} no tiene dispositivo utilizable: el push se omite.", "att_group_empty": "El grupo de destinatarios {subject} no tiene ningún altavoz que exista.", "att_policy_invalid": "La política {subject} no es válida: {reason}.", "att_policy_target": "La política {subject} nombra una audiencia o grupo que ya no existe.", "att_no_critical_escalation": "Ninguna política de escalado cubre los mensajes críticos.", "att_hub_off": "El hub está desactivado.", "reason": {"waiting_for_condition": "espera su condición", "no_recipients": "nadie a quien enviar", "channel_unavailable": "canal no disponible", "no_usable_device": "ningún dispositivo utilizable", "service_not_found": "servicio no encontrado", "channel_not_accepted": "canal no aceptado por el perfil", "presence_unknown": "presencia desconocida", "quiet_hours": "horas de silencio", "cooldown": "dicho hace un momento", "already_spoken": "ya dicho", "popup_off": "ventanas desactivadas para esta gravedad", "no_user": "sin usuario de Home Assistant", "entity_missing": "falta el altavoz", "send_failed": "falló el envío", "no_tts_engine": "sin motor de texto a voz", "max_wait_exceeded": "esperó lo suficiente", "no_longer_needed": "ya no hace falta", "audience_missing": "audiencia borrada", "group_missing": "grupo borrado", "dismissed": "descartado", "snoozed": "pospuesto", "nothing_to_say": "nada que decir", "not_clearable": "no se puede retirar", "device_missing": "falta el dispositivo", "cleared": "borrado", "expired": "caducado", "condition": "condición terminada", "dismissed_global": "descartado para todos", "evicted": "desalojado", "rule": "regla terminada", "admin": "borrado por un administrador", "clear_all": "borrado con todos", "unknown_type": "tipo de política desconocido", "after_required": "sin tiempo", "channels_required": "sin canales", "channel_unknown": "canal no permitido", "every_required": "sin intervalo", "max_required": "sin máximo", "window_empty": "franja vacía", "when_required": "sin disparador", "time_invalid": "hora no válida", "wait_invalid": "espera no válida", "user_mismatch": "usuario incorrecto", "rate_limited": "por encima del límite", "duplicate": "igual que la última actualización"}, "result": {"sent": "enviado", "held": "retenido", "skipped": "omitido", "failed": "falló", "cleared": "borrado", "planned": "previsto", "acknowledged": "confirmado", "escalated": "escalado", "summary": "resumen", "fallback": "alternativa"}},
    title: "Heads Up",
    menu: "Abrir la barra lateral",
    tour_paused: "Recorrido de bienvenida en pausa tras el paso {n} de {total}.",
    tour_continue: "Continuar el recorrido",
    tour_end: "Terminar el recorrido",
    groups: { overview: "Resumen", notifications: "Notificaciones y reglas", configuration: "Configuración", settings: "Ajustes", faq: "Preguntas y ejemplos" },
    pages: { status: "Estado", test: "Envío de prueba", rules: "Reglas de vigilancia", messages: "Mensajes", audiences: "Audiencias", recipients: "Destinatarios", policies: "Políticas", channels: "Canales", general: "General", faq: "Preguntas y ejemplos" },
    not_built: "Esta página no está disponible.",
    loading: "Cargando…",
    load_failed: "No se pudo cargar la página. Recarga la página del navegador.",
    nav_label: "Páginas de Heads Up",
  },
};

// The table of a language, English where a key is missing.
export function table(strings, language) {
  const code = String(language || "en").split("-")[0];
  const own = strings[code] || {};
  const base = strings.en;
  return new Proxy(own, {
    get: (target, key) => (key in target ? target[key] : base[key]),
    has: (target, key) => key in target || key in base,
  });
}

export function groupOf(page) {
  return NAV.find((group) => group.pages.includes(page)) || null;
}

// The page for a route path such as "/settings" or "/general"; unknown paths show the first page.
export function pageFromPath(path) {
  const id = String(path || "").split("/").filter(Boolean)[0];
  return groupOf(id) ? id : DEFAULT_PAGE;
}

// The second row: the pages of the group, or nothing for a group with one page (D-103).
export function secondRow(page) {
  const group = groupOf(page);
  return group && group.pages.length > 1 ? group.pages : [];
}

export function pageUrl(page) {
  return `${BASE_PATH}/${page}`;
}

export function moduleUrl(base, version, file) {
  return `${base}/${file}?v=${version}`;
}


// Shared wording of the pages (the tables are in STRINGS.<language>.shared). The server sends
// structured fields and no text (D-118).
const MIN = 60000;
const HOUR = 60 * MIN;
const DAY = 24 * HOUR;

function fillIn(text, params) {
  return Object.entries(params).reduce((out, [key, value]) => out.replace(`{${key}}`, value ?? ""), text);
}

export function timeAgo(iso, now, s) {
  const diff = now - Date.parse(iso);
  if (diff < MIN) return s.ago_now;
  if (diff < HOUR) return fillIn(s.ago_min, { n: Math.floor(diff / MIN) });
  if (diff < DAY) return fillIn(s.ago_hour, { n: Math.floor(diff / HOUR) });
  return fillIn(s.ago_day, { n: Math.floor(diff / DAY) });
}

export function inTime(iso, now, s) {
  const diff = Date.parse(iso) - now;
  if (!iso || diff < MIN) return s.in_now;
  if (diff < HOUR) return fillIn(s.in_min, { n: Math.ceil(diff / MIN) });
  if (diff < DAY) return fillIn(s.in_hour, { n: Math.round(diff / HOUR) });
  return fillIn(s.in_day, { n: Math.round(diff / DAY) });
}

export function reasonText(code, s) {
  return (code && s.reason[code]) || code || "";
}

export function channelName(channel, s) {
  return s.channel[channel] || channel;
}

export function stateText(state, now, s) {
  const when = state.due || state.until ? inTime(state.due || state.until, now, s) : "";
  const policy = state.policy || "";
  switch (state.state) {
    case "held":
      return fillIn(s.state_held, { policy });
    case "escalating":
      return state.phase === "sent"
        ? fillIn(s.state_escalating_sent, { policy })
        : fillIn(s.state_escalating_pending, { policy, when });
    case "reminding":
      return fillIn(s.state_reminding, { policy, when });
    case "snoozed":
      return fillIn(s.state_snoozed, { when });
    default:
      return s.state_acknowledged;
  }
}

export function logText(entry, s) {
  const [first, second] = String(entry.detail ?? "").split("|");
  const named = (key) => (entry.detail ? fillIn(s[key], { detail: entry.detail }) : s[`${key}_anon`]);
  switch (entry.kind) {
    case "created":
      return fillIn(s.log_created, {
        severity: s.severity[entry.severity] || entry.severity,
        channels: String(entry.detail ?? "").split(",").map((c) => channelName(c, s)).join(", "),
      });
    case "acknowledged":
    case "dismissed":
    case "snoozed":
    case "unsnoozed":
      return named(`log_${entry.kind}`);
    case "escalation_sent":
    case "reminder_sent":
    case "fallback_sent":
      return fillIn(s[`log_${entry.kind}`], { detail: entry.detail });
    case "summary_sent":
      return fillIn(s.log_summary_sent, { channel: channelName(first, s), n: second });
    case "skipped":
    case "failed":
      return fillIn(s[`log_${entry.kind}`], { channel: channelName(first, s), reason: reasonText(second, s) });
    case "cleared":
      // A plain clear needs no reason in brackets.
      return entry.detail && entry.detail !== "cleared"
        ? fillIn(s.log_cleared, { reason: reasonText(entry.detail, s) })
        : s.log_cleared_plain;
    default:
      return s.log_expired;
  }
}

export function attentionText(item, s) {
  return fillIn(s[`att_${item.kind}`] || item.kind, {
    subject: item.subject,
    detail: item.detail,
    reason: reasonText(item.detail, s),
  });
}

export function messageTitle(message) {
  return message.title || message.message || message.id;
}

const CSS = `
:host { display: block; min-height: 100vh; background: var(--primary-background-color); color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
header { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 12px; background: var(--app-header-background-color, var(--primary-color));
  color: var(--app-header-text-color, var(--text-primary-color, #fff)); }
header h1 { font-size: 20px; font-weight: 500; margin: 0; }
button { font: inherit; cursor: pointer; }
.menu { min-width: 48px; min-height: 48px; border: none; background: transparent; color: inherit; font-size: 22px; }
nav .row { display: flex; gap: 4px; overflow-x: auto; padding: 0 8px; background: var(--card-background-color); border-bottom: 1px solid var(--divider-color); }
nav button { min-height: 48px; padding: 0 14px; border: none; border-bottom: 3px solid transparent; background: transparent; color: var(--secondary-text-color); white-space: nowrap; }
nav button[aria-current="page"] { color: var(--primary-color); border-bottom-color: var(--primary-color); font-weight: 600; }
nav .second { gap: 8px; max-width: 900px; margin: 0 auto; padding: 12px 16px 0; background: transparent; border-bottom: none; }
nav .second button { min-height: 36px; padding: 0 16px; border: 1px solid var(--divider-color); border-radius: 18px; background: transparent; color: var(--primary-text-color); font-weight: 400; }
nav .second button[aria-current="page"] { background: var(--primary-color); border-color: var(--primary-color); color: var(--text-primary-color, #fff); font-weight: 500; }
nav button:focus-visible, .menu:focus-visible { outline: 3px solid var(--primary-color); outline-offset: -3px; }
main { max-width: 900px; margin: 0 auto; padding: 16px; }
.note { color: var(--secondary-text-color); padding: 24px 0; }
.tour { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; max-width: 900px; margin: 12px auto 0; padding: 8px 16px; box-sizing: border-box; background: var(--card-background-color); border: 1px solid var(--divider-color); border-left: 4px solid var(--primary-color); border-radius: 8px; }
.tour[hidden] { display: none; }
.tour span { flex: 1; min-width: 200px; }
.tour button { min-height: 40px; padding: 0 14px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); }
.tour button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.tour button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
`;

function node(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

// vitest runs without a DOM: the class only needs a base there.
const Base = typeof HTMLElement !== "undefined" ? HTMLElement : class {};

class HeadsUpPanel extends Base {
  constructor() {
    super();
    this._hass = null;
    this._page = null;
    this._mounted = null;
    this._token = 0;
    this.attachShadow({ mode: "open" });
  }

  set hass(value) {
    this._hass = value;
    if (!this._built) this._build();
    this._mounted?.setHass?.(value);
  }

  get hass() {
    return this._hass;
  }

  set narrow(value) {
    this._narrow = value;
    if (this._built) this._renderHeader();
  }

  set route(value) {
    this._route = value;
    if (this._built) this._open(pageFromPath(value?.path));
  }

  set panel(value) {
    this._config = value?.config || {};
  }

  get _t() {
    return table(STRINGS, this._hass?.language);
  }

  _build() {
    this._built = true;
    const root = this.shadowRoot;
    root.append(node("style", { textContent: CSS }));
    this._header = node("header");
    this._nav = node("nav");
    this._main = node("main");
    this._tourBar = node("div", { className: "tour", hidden: true });
    this._tourBar.setAttribute("role", "region");
    root.append(this._header, this._nav, this._tourBar, this._main);
    this._renderHeader();
    this._open(pageFromPath(this._route?.path));
    this.openWelcome(false);
  }

  _renderHeader() {
    const t = this._t;
    this._header.replaceChildren();
    if (this._narrow) {
      const menu = node("button", { type: "button", className: "menu", textContent: "☰" });
      menu.setAttribute("aria-label", t.menu);
      menu.addEventListener("click", () =>
        this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })),
      );
      this._header.append(menu);
    }
    this._header.append(node("h1", { textContent: t.title }));
  }

  _renderNav() {
    const t = this._t;
    this._nav.replaceChildren();
    this._nav.setAttribute("aria-label", t.nav_label);
    const first = node("div", { className: "row" });
    const group = groupOf(this._page);
    for (const g of NAV) {
      const button = node("button", { type: "button", textContent: t.groups[g.id] });
      if (g === group) button.setAttribute("aria-current", "page");
      button.addEventListener("click", () => this.navigate(g.pages[0]));
      first.append(button);
    }
    this._nav.append(first);
    const pages = secondRow(this._page);
    if (pages.length > 0) {
      const second = node("div", { className: "row second" });
      for (const page of pages) {
        const button = node("button", { type: "button", textContent: t.pages[page] });
        if (page === this._page) button.setAttribute("aria-current", "page");
        button.addEventListener("click", () => this.navigate(page));
        second.append(button);
      }
      this._nav.append(second);
    }
  }

  // The welcome tour (D-121, D-131): on the first opening, again on request, and resumable after a
  // visit to a page it points to.
  async openWelcome(force = false, step = 0) {
    try {
      const base = this._config?.base ?? "/heads_up/panel";
      const version = this._config?.v ?? "";
      this._ui ||= await import(moduleUrl(base, version, "ui.js"));
      const mod = await import(moduleUrl(base, version, "welcome.js"));
      this._welcome?.close();
      this._setTour(null);
      this._welcome = await mod.open(this.shadowRoot, {
        hass: this._hass,
        t: table(mod.STRINGS, this._hass?.language),
        s: this._t.shared,
        ui: this._ui,
        language: this._hass?.language,
        force,
        step,
        navigate: (target) => this.navigate(target),
        leave: (page, next) => {
          this._welcome?.close();
          this.navigate(page);
          this._setTour({ next, total: mod.STEPS.length });
        },
      });
    } catch (err) {
      // The welcome is a convenience: a failure must not block the panel.
    }
  }

  // The bar that offers to continue a tour left for a page; null hides it.
  _setTour(tour) {
    const bar = this._tourBar;
    if (!bar) return;
    bar.replaceChildren();
    bar.hidden = !tour;
    if (!tour) return;
    const t = this._t;
    bar.setAttribute("aria-label", t.tour_paused.replace("{n}", tour.next).replace("{total}", tour.total));
    const resume = node("button", { type: "button", className: "primary", textContent: t.tour_continue });
    resume.addEventListener("click", () => this.openWelcome(true, tour.next));
    const end = node("button", { type: "button", textContent: t.tour_end });
    end.addEventListener("click", () => this._setTour(null));
    bar.append(node("span", { textContent: t.tour_paused.replace("{n}", tour.next).replace("{total}", tour.total) }), resume, end);
  }

  navigate(page) {
    history.pushState(null, "", pageUrl(page));
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
    this._open(page);
  }

  async _open(page) {
    if (page === this._page && this._mounted) return;
    this._page = page;
    this._renderNav();
    const t = this._t;
    const token = ++this._token;
    this._mounted?.destroy?.();
    this._mounted = null;
    this._main.replaceChildren(node("div", { className: "note", textContent: t.loading }));
    const file = MODULES[page];
    if (!file) {
      this._main.replaceChildren(node("div", { className: "note", textContent: t.not_built }));
      return;
    }
    try {
      const base = this._config?.base ?? "/heads_up/panel";
      const version = this._config?.v ?? "";
      const mod = await import(moduleUrl(base, version, file));
      // The helpers the editor pages share are loaded once, under the same versioned URL scheme.
      this._ui ||= await import(moduleUrl(base, version, "ui.js"));
      if (token !== this._token) return; // another page was opened meanwhile
      const container = node("div");
      this._main.replaceChildren(container);
      this._mounted = mod.mount(container, {
        hass: this._hass,
        t: table(mod.STRINGS, this._hass?.language),
        s: this._t.shared,
        ui: this._ui,
        language: this._hass?.language,
        fmt: { timeAgo, inTime, stateText, logText, attentionText, reasonText, channelName, messageTitle },
        navigate: (target) => this.navigate(target),
        openWelcome: () => this.openWelcome(true),
      });
    } catch (err) {
      if (token === this._token) this._main.replaceChildren(node("div", { className: "note", textContent: t.load_failed }));
    }
  }
}

if (typeof customElements !== "undefined" && !customElements.get("heads-up-panel")) {
  customElements.define("heads-up-panel", HeadsUpPanel);
}
