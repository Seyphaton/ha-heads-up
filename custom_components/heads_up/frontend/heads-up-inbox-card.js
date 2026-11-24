// Heads Up inbox card: the viewing user's own inbox (Phase 22, D-264, D-266, D-274).
// Plain ES module, no build step (D-021). Item text is caller-supplied and is only ever written
// with textContent. The card shows the inbox of the logged-in user; there is no person option.

export const SIZES = ["compact", "small", "medium", "large"];
export const DESIGNS = { small: ["number", "ring", "mosaic"], medium: ["tile", "ring", "split"], large: [], compact: [] };
// Read by scripts/docs_check.py to keep docs/configuration.md in step with the card.
export const CONFIG_KEYS = ["size", "design", "titles_only", "hide_send_button"];
const SEVERITIES = ["critical", "warning", "info", "passive"];
const SEVERITY_COLOR = {
  critical: "var(--error-color)",
  warning: "var(--warning-color)",
  info: "var(--info-color)",
  passive: "var(--success-color)",
};
const SEVERITY_ICON = {
  critical: "mdi:alert-circle",
  warning: "mdi:alert",
  info: "mdi:information",
  passive: "mdi:check-circle",
};
const RING_GAP = 5;
const MOSAIC_CELLS = 4;
const PAGE = 50;
const MAX_MESSAGE = 1000; // the server's limit (D-265)
const MESSAGE_CHANNELS = ["inbox", "push", "popup", "mail"];

// ---- Strings (D-037, D-071) ----------------------------------------------------------------

const ENGLISH = {
  inbox: "Inbox",
  all_notifications: "All notifications",
  unread_n: "{n} unread",
  needs_n: "{n} needs action",
  all_caught_up: "All caught up",
  nothing_waiting: "Nothing is waiting for you",
  unread_word: "unread",
  clear_word: "clear",
  open: "Open",
  mark_all_read: "Mark all read",
  filter_all: "All",
  filter_unread: "Unread",
  today: "Today",
  yesterday: "Yesterday",
  close: "Close",
  delete: "Delete",
  show_more: "Show more",
  no_person: "Your Home Assistant user is not linked to a person, so there is no inbox for it.",
  load_error: "The inbox could not be loaded. Trying again.",
  nothing_yet: "Nothing here yet",
  new_messages_show: "New messages show up here.",
  nothing_unread: "Nothing unread",
  caught_up_message: "You are all caught up.",
  chip_needs_action: "Needs action",
  chip_resolved: "Ended",
  unread_label: "Unread",
  sent_tab: "Sent",
  new_message: "New message",
  to_label: "To",
  you: "you",
  send_via: "Send via",
  via: { inbox: "Inbox", push: "Push notification", popup: "Popup on screens", mail: "Mail" },
  message_label: "Message",
  characters: "{n} of {max}",
  send: "Send",
  back: "Back",
  done: "Done",
  loading_people: "Loading people…",
  pick_one: "Choose at least one person.",
  no_inbox_for_you: "Nobody to write to yet.",
  from_name: "From {name}",
  to_names: "To {names}",
  skip_note: "{name}: no {channels}",
  sent_ok: "Message sent",
  not_delivered: "{name}: not delivered by {channels}",
  nothing_sent: "Nothing sent yet",
  sent_here: "Messages you send show up here.",
  error_send: "The message could not be sent.",
  error_rate_limited: "Too many messages. Wait a moment and try again.",
  error_messages_off: "Messages between people are switched off.",
  error_mail_off: "No mail service is set on the Channels page.",
  inbox_always: "Direct messages are always sent to the inbox.",
  error_no_person: "Your Home Assistant user is not linked to one person.",
  with_channel: "{what}: {channel}",
  ended_because: "Ended: {reason}",
  timeline: {
    sent: "Sent",
    updated: "Updated",
    reminder: "Reminder",
    escalation: "Escalated",
    acknowledged: "Acknowledged",
    acknowledged_by_other: "Acknowledged by someone else",
    resolved: "Ended",
  },
  channels: {
    banner: "Banner",
    push: "Push",
    popup: "Popup",
    speak: "Speak",
    persistent: "Persistent Notification",
    mail: "Mail",
    inbox: "Inbox",
  },
  reasons: {
    cleared: "Cleared",
    expired: "Expired",
    condition: "The condition is no longer true",
    dismissed: "Dismissed",
  },
  severity: { critical: "Critical", warning: "Warning", info: "Info", passive: "Passive" },
  editor: {
    size: "Size",
    design: "Design",
    titles_only: "Show titles only, never the text",
    hide_send_button: "Hide the button that writes a message",
    size_compact: "Compact tile",
    size_small: "Small tile",
    size_medium: "Medium card",
    size_large: "Large list",
    design_number: "Number",
    design_ring: "Ring",
    design_mosaic: "Mosaic",
    design_tile: "Tile",
    design_split: "Split",
  },
};

export const STRINGS = structuredClone(ENGLISH);

export const TRANSLATIONS = {
  de: {
    inbox: "Posteingang",
    sent_tab: "Gesendet",
    new_message: "Neue Nachricht",
    to_label: "An",
    you: "du",
    send_via: "Senden über",
    message_label: "Nachricht",
    characters: "{n} von {max}",
    send: "Senden",
    back: "Zurück",
    done: "Fertig",
    loading_people: "Personen werden geladen…",
    pick_one: "Wähle mindestens eine Person.",
    no_inbox_for_you: "Noch niemand, dem du schreiben kannst.",
    from_name: "Von {name}",
    to_names: "An {names}",
    skip_note: "{name}: kein {channels}",
    sent_ok: "Nachricht gesendet",
    not_delivered: "{name}: nicht zugestellt über {channels}",
    nothing_sent: "Noch nichts gesendet",
    sent_here: "Nachrichten, die du sendest, erscheinen hier.",
    error_send: "Die Nachricht konnte nicht gesendet werden.",
    error_rate_limited: "Zu viele Nachrichten. Warte einen Moment und versuche es erneut.",
    error_messages_off: "Nachrichten zwischen Personen sind ausgeschaltet.",
    error_mail_off: "Auf der Kanäle-Seite ist kein Mail-Dienst eingestellt.",
    inbox_always: "Direkte Nachrichten gehen immer in den Posteingang.",
    error_no_person: "Dein Home-Assistant-Benutzer ist nicht mit genau einer Person verknüpft.",
    via: { inbox: "Posteingang", push: "Push-Benachrichtigung", popup: "Popup auf Bildschirmen", mail: "E-Mail" },
    all_notifications: "Alle Benachrichtigungen",
    unread_n: "{n} ungelesen",
    needs_n: "{n} braucht Aktion",
    all_caught_up: "Alles gelesen",
    nothing_waiting: "Nichts wartet auf dich",
    unread_word: "ungelesen",
    clear_word: "leer",
    open: "Öffnen",
    mark_all_read: "Alle als gelesen markieren",
    filter_all: "Alle",
    filter_unread: "Ungelesen",
    today: "Heute",
    yesterday: "Gestern",
    close: "Schließen",
    delete: "Löschen",
    show_more: "Mehr anzeigen",
    no_person: "Dein Home-Assistant-Benutzer ist keiner Person zugeordnet, daher gibt es keinen Posteingang.",
    load_error: "Der Posteingang konnte nicht geladen werden. Neuer Versuch folgt.",
    nothing_yet: "Noch nichts hier",
    new_messages_show: "Neue Nachrichten erscheinen hier.",
    nothing_unread: "Nichts ungelesen",
    caught_up_message: "Du bist auf dem neuesten Stand.",
    chip_needs_action: "Braucht Aktion",
    chip_resolved: "Beendet",
    unread_label: "Ungelesen",
    with_channel: "{what}: {channel}",
    ended_because: "Beendet: {reason}",
    timeline: {
      sent: "Gesendet",
      updated: "Aktualisiert",
      reminder: "Erinnerung",
      escalation: "Eskaliert",
      acknowledged: "Bestätigt",
      acknowledged_by_other: "Von jemand anderem bestätigt",
      resolved: "Beendet",
    },
    channels: {
      banner: "Banner",
      push: "Push",
      popup: "Popup",
      speak: "Sprache",
      persistent: "Persistente Benachrichtigung",
      mail: "E-Mail",
      inbox: "Posteingang",
    },
    reasons: {
      cleared: "Gelöscht",
      expired: "Abgelaufen",
      condition: "Die Bedingung gilt nicht mehr",
      dismissed: "Verworfen",
    },
    severity: { critical: "Kritisch", warning: "Warnung", info: "Info", passive: "Passiv" },
    editor: {
      size: "Größe",
      design: "Darstellung",
      titles_only: "Nur Titel zeigen, nie den Text",
      hide_send_button: "Die Schaltfläche zum Schreiben einer Nachricht ausblenden",
      size_compact: "Kompakte Kachel",
      size_small: "Kleine Kachel",
      size_medium: "Mittlere Karte",
      size_large: "Große Liste",
      design_number: "Zahl",
      design_ring: "Ring",
      design_mosaic: "Mosaik",
      design_tile: "Kachel",
      design_split: "Geteilt",
    },
  },
  fr: {
    inbox: "Boîte de réception",
    sent_tab: "Envoyés",
    new_message: "Nouveau message",
    to_label: "À",
    you: "toi",
    send_via: "Envoyer par",
    message_label: "Message",
    characters: "{n} sur {max}",
    send: "Envoyer",
    back: "Retour",
    done: "Terminé",
    loading_people: "Chargement des personnes…",
    pick_one: "Choisis au moins une personne.",
    no_inbox_for_you: "Personne à qui écrire pour l'instant.",
    from_name: "De {name}",
    to_names: "À {names}",
    skip_note: "{name} : pas de {channels}",
    sent_ok: "Message envoyé",
    not_delivered: "{name} : non remis par {channels}",
    nothing_sent: "Rien d'envoyé pour l'instant",
    sent_here: "Les messages que tu envoies apparaissent ici.",
    error_send: "Le message n'a pas pu être envoyé.",
    error_rate_limited: "Trop de messages. Attends un instant et réessaie.",
    error_messages_off: "Les messages entre personnes sont désactivés.",
    error_mail_off: "Aucun service de courriel n'est défini sur la page Canaux.",
    inbox_always: "Les messages directs vont toujours dans la boîte de réception.",
    error_no_person: "Ton utilisateur Home Assistant n'est pas lié à une seule personne.",
    via: { inbox: "Boîte de réception", push: "Notification push", popup: "Popup sur les écrans", mail: "Courriel" },
    all_notifications: "Toutes les notifications",
    unread_n: "{n} non lu(s)",
    needs_n: "{n} à traiter",
    all_caught_up: "Tout est lu",
    nothing_waiting: "Rien ne vous attend",
    unread_word: "non lus",
    clear_word: "vide",
    open: "Ouvrir",
    mark_all_read: "Tout marquer comme lu",
    filter_all: "Tout",
    filter_unread: "Non lus",
    today: "Aujourd'hui",
    yesterday: "Hier",
    close: "Fermer",
    delete: "Supprimer",
    show_more: "Afficher plus",
    no_person: "Votre utilisateur Home Assistant n'est lié à aucune personne : il n'a donc pas de boîte de réception.",
    load_error: "La boîte de réception n'a pas pu être chargée. Nouvel essai en cours.",
    nothing_yet: "Rien ici pour l'instant",
    new_messages_show: "Les nouveaux messages apparaissent ici.",
    nothing_unread: "Rien de non lu",
    caught_up_message: "Vous êtes à jour.",
    chip_needs_action: "À traiter",
    chip_resolved: "Terminé",
    unread_label: "Non lu",
    with_channel: "{what} : {channel}",
    ended_because: "Terminé : {reason}",
    timeline: {
      sent: "Envoyé",
      updated: "Mis à jour",
      reminder: "Rappel",
      escalation: "Escaladé",
      acknowledged: "Acquitté",
      acknowledged_by_other: "Acquitté par quelqu'un d'autre",
      resolved: "Terminé",
    },
    channels: {
      banner: "Bannière",
      push: "Push",
      popup: "Fenêtre",
      speak: "Voix",
      persistent: "Notification persistante",
      mail: "Courriel",
      inbox: "Boîte de réception",
    },
    reasons: {
      cleared: "Effacé",
      expired: "Expiré",
      condition: "La condition n'est plus remplie",
      dismissed: "Ignoré",
    },
    severity: { critical: "Critique", warning: "Avertissement", info: "Info", passive: "Passif" },
    editor: {
      size: "Taille",
      design: "Présentation",
      titles_only: "Afficher seulement les titres, jamais le texte",
      hide_send_button: "Masquer le bouton pour écrire un message",
      size_compact: "Tuile compacte",
      size_small: "Petite tuile",
      size_medium: "Carte moyenne",
      size_large: "Grande liste",
      design_number: "Nombre",
      design_ring: "Anneau",
      design_mosaic: "Mosaïque",
      design_tile: "Tuile",
      design_split: "Divisé",
    },
  },
  es: {
    inbox: "Bandeja de entrada",
    sent_tab: "Enviados",
    new_message: "Mensaje nuevo",
    to_label: "Para",
    you: "tú",
    send_via: "Enviar por",
    message_label: "Mensaje",
    characters: "{n} de {max}",
    send: "Enviar",
    back: "Atrás",
    done: "Listo",
    loading_people: "Cargando personas…",
    pick_one: "Elige al menos una persona.",
    no_inbox_for_you: "Todavía no hay nadie a quien escribir.",
    from_name: "De {name}",
    to_names: "Para {names}",
    skip_note: "{name}: sin {channels}",
    sent_ok: "Mensaje enviado",
    not_delivered: "{name}: no entregado por {channels}",
    nothing_sent: "Todavía no has enviado nada",
    sent_here: "Los mensajes que envíes aparecerán aquí.",
    error_send: "No se pudo enviar el mensaje.",
    error_rate_limited: "Demasiados mensajes. Espera un momento e inténtalo de nuevo.",
    error_messages_off: "Los mensajes entre personas están desactivados.",
    error_mail_off: "No hay ningún servicio de correo en la página Canales.",
    inbox_always: "Los mensajes directos siempre van a la bandeja de entrada.",
    error_no_person: "Tu usuario de Home Assistant no está vinculado a una sola persona.",
    via: { inbox: "Bandeja de entrada", push: "Notificación push", popup: "Ventana emergente en pantallas", mail: "Correo" },
    all_notifications: "Todas las notificaciones",
    unread_n: "{n} sin leer",
    needs_n: "{n} requiere acción",
    all_caught_up: "Todo leído",
    nothing_waiting: "Nada te espera",
    unread_word: "sin leer",
    clear_word: "vacía",
    open: "Abrir",
    mark_all_read: "Marcar todo como leído",
    filter_all: "Todo",
    filter_unread: "Sin leer",
    today: "Hoy",
    yesterday: "Ayer",
    close: "Cerrar",
    delete: "Eliminar",
    show_more: "Mostrar más",
    no_person: "Tu usuario de Home Assistant no está vinculado a ninguna persona, así que no tiene bandeja de entrada.",
    load_error: "No se pudo cargar la bandeja de entrada. Se reintenta.",
    nothing_yet: "Todavía no hay nada",
    new_messages_show: "Los mensajes nuevos aparecen aquí.",
    nothing_unread: "Nada sin leer",
    caught_up_message: "Estás al día.",
    chip_needs_action: "Requiere acción",
    chip_resolved: "Terminado",
    unread_label: "Sin leer",
    with_channel: "{what}: {channel}",
    ended_because: "Terminado: {reason}",
    timeline: {
      sent: "Enviado",
      updated: "Actualizado",
      reminder: "Recordatorio",
      escalation: "Escalado",
      acknowledged: "Confirmado",
      acknowledged_by_other: "Confirmado por otra persona",
      resolved: "Terminado",
    },
    channels: {
      banner: "Aviso",
      push: "Push",
      popup: "Ventana",
      speak: "Voz",
      persistent: "Notificación persistente",
      mail: "Correo",
      inbox: "Bandeja de entrada",
    },
    reasons: {
      cleared: "Borrado",
      expired: "Caducado",
      condition: "La condición ya no se cumple",
      dismissed: "Descartado",
    },
    severity: { critical: "Crítico", warning: "Advertencia", info: "Info", passive: "Pasivo" },
    editor: {
      size: "Tamaño",
      design: "Diseño",
      titles_only: "Mostrar solo los títulos, nunca el texto",
      hide_send_button: "Ocultar el botón para escribir un mensaje",
      size_compact: "Ficha compacta",
      size_small: "Ficha pequeña",
      size_medium: "Tarjeta mediana",
      size_large: "Lista grande",
      design_number: "Número",
      design_ring: "Anillo",
      design_mosaic: "Mosaico",
      design_tile: "Ficha",
      design_split: "Dividido",
    },
  },
};

function assign(target, source) {
  for (const [key, value] of Object.entries(source)) {
    if (value !== null && typeof value === "object") assign(target[key], value);
    else target[key] = value;
  }
}

// Switches STRINGS to the user's language; unknown languages stay English. Item text is never
// translated.
export function setLanguage(language) {
  const code = String(language ?? "en").toLowerCase().split(/[-_]/)[0];
  assign(STRINGS, ENGLISH);
  if (TRANSLATIONS[code]) assign(STRINGS, TRANSLATIONS[code]);
  return TRANSLATIONS[code] ? code : "en";
}

const fill = (text, values) => text.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ""));

// ---- Pure logic (tested with vitest) --------------------------------------------------------

export function normalizeConfig(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("Invalid configuration");
  }
  const size = config.size ?? "large";
  if (!SIZES.includes(size)) throw new Error(`size must be one of ${SIZES.join(", ")}`);
  const allowed = DESIGNS[size];
  if (config.design !== undefined && config.design !== null && config.design !== "") {
    if (!allowed.includes(config.design)) {
      throw new Error(
        allowed.length
          ? `design for size ${size} must be one of ${allowed.join(", ")}`
          : "design is only for the small and medium sizes",
      );
    }
  }
  return {
    size,
    design: config.design || allowed[0] || "",
    titles_only: config.titles_only === true,
    hide_send_button: config.hide_send_button === true,
  };
}

export function summaryKind({ unread, needs_action: needs }) {
  if (needs > 0) return "needs";
  return unread > 0 ? "unread" : "clear";
}

export function summaryText(state, strings) {
  const kind = summaryKind(state);
  if (kind === "needs") return fill(strings.needs_n, { n: state.needs_action });
  if (kind === "unread") return fill(strings.unread_n, { n: state.unread });
  return strings.all_caught_up;
}

export function severityCounts(items) {
  const unread = items.filter((i) => i.unread);
  return SEVERITIES.map((s) => [s, unread.filter((i) => i.severity === s).length]).filter(([, n]) => n > 0);
}

const needsFirst = (items) => [...items].sort((a, b) => Number(b.needs_action) - Number(a.needs_action));

export function topItem(items) {
  return needsFirst(items.filter((i) => i.needs_action || i.unread))[0] ?? null;
}

// The compact tile (D-277): title of the message that matters most, else "Inbox".
export function compactTile(state, items, strings = STRINGS) {
  const kind = summaryKind(state);
  const top = kind === "clear" ? null : topItem(items);
  return {
    kind,
    severity: top ? top.severity : null,
    title: top?.title || strings.inbox,
    sub: summaryText(state, strings),
  };
}

export function ringSegments(counts, radius, gap = RING_GAP) {
  const total = counts.reduce((sum, [, n]) => sum + n, 0);
  if (!total) return [];
  const circle = 2 * Math.PI * radius;
  const space = counts.length > 1 ? gap : 0;
  let offset = 0;
  return counts.map(([severity, n]) => {
    const length = (n / total) * circle - space;
    const segment = { severity, length, offset };
    offset += length + space;
    return segment;
  });
}

// Up to four unread icons; from five items on, three and a "+N" tile.
export function mosaicTiles(items) {
  const unread = needsFirst(items.filter((i) => i.unread));
  if (unread.length <= MOSAIC_CELLS) return unread.map((item) => ({ item }));
  return [...unread.slice(0, MOSAIC_CELLS - 1).map((item) => ({ item })), { more: unread.length - (MOSAIC_CELLS - 1) }];
}

// The tab row: Inbox, then All notifications while that switch is on, then Sent while messages
// are on (D-279). With one tab the card shows the inbox alone and no row.
export function visibleTabs(state) {
  const tabs = ["inbox"];
  if (state.all_notifications) tabs.push("all");
  if (state.messages && state.has_person !== false) tabs.push("sent");
  return tabs;
}

export function visibleScope(state, scope) {
  return visibleTabs(state).includes(scope) ? scope : "inbox";
}

// The view Inbox shows the real items, All notifications also the copies (D-275); Sent shows only
// the sender's own copies and no other view shows them.
export function scopeItems(items, scope) {
  if (scope === "sent") return items.filter((i) => i.sent);
  const own = items.filter((i) => !i.sent);
  return scope === "all" ? own : own.filter((i) => !i.copy);
}

// ---- messages between people ----

export function showCompose(state, config) {
  return Boolean(state.messages) && state.has_person !== false && !config.hide_send_button;
}

export function personName(states, id) {
  return states?.[id]?.attributes?.friendly_name || String(id).split(".").slice(1).join(".") || String(id);
}

// "From Anna" on a received item, "To Anna, Ben" on a sent one (D-265).
export function rowLine(item, states, strings) {
  if (item.sent) return fill(strings.to_names, { names: (item.recipients ?? []).map((id) => personName(states, id)).join(", ") });
  return item.sender ? fill(strings.from_name, { name: personName(states, item.sender) }) : "";
}

// The avatar of a message between people: the picture of the person who wrote it (a received
// message) or of its one recipient (a sent one), else the first letter of their name. Any other
// message has none and keeps the icon of its severity (D-285).
export function rowAvatar(item, states) {
  const who = item.sent ? (item.recipients?.length === 1 ? item.recipients[0] : null) : item.sender;
  if (!who) return null;
  const picture = states?.[who]?.attributes?.entity_picture;
  const first = Array.from(personName(states, who).trim())[0];
  return {
    picture: typeof picture === "string" && /^(\/|https?:\/\/)/.test(picture) ? picture : null,
    initial: first ? first.toUpperCase() : "?",
  };
}

export function canSend(draft) {
  const text = (draft.text ?? "").trim();
  return draft.to.length > 0 && text.length > 0 && text.length <= MAX_MESSAGE;
}

// The channels each chosen person does not accept, so the dialog can say so before sending.
export function composeHints(people, chosen, channels) {
  return people
    .filter((p) => chosen.includes(p.person))
    .map((p) => ({ person: p.person, name: p.name, channels: channels.filter((c) => !p.channels.includes(c)) }))
    .filter((hint) => hint.channels.length);
}

const SEND_ERRORS = ["rate_limited", "messages_off", "no_person", "mail_off"];
export function sendError(error) {
  return SEND_ERRORS.includes(error?.code) ? `error_${error.code}` : "error_send";
}

export function filterItems(items, filter) {
  return needsFirst(filter === "unread" ? items.filter((i) => i.unread) : items);
}

const dayStart = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate());

// Groups in the order the items arrive, one group per local day.
export function dayGroups(items, now = new Date()) {
  const today = dayStart(now).getTime();
  const groups = new Map();
  for (const item of items) {
    const date = dayStart(new Date(item.updated));
    const key = date.getTime();
    if (!groups.has(key)) {
      const days = Math.round((today - key) / 86400000);
      const kind = days === 0 ? "today" : days === 1 ? "yesterday" : days > 1 && days < 7 ? "weekday" : "date";
      groups.set(key, { key, kind, date, items: [] });
    }
    groups.get(key).items.push(item);
  }
  return [...groups.values()];
}

export function mergePages(first, more) {
  const seen = new Set(first.map((i) => i.message_id));
  return [...first, ...more.filter((i) => !seen.has(i.message_id))];
}

export function visibleText(item, config) {
  return config.titles_only ? "" : item.text;
}

export function timelineText(entry, strings) {
  const what = strings.timeline[entry.kind] ?? entry.kind;
  if (!entry.channel) return what;
  return fill(strings.with_channel, { what, channel: strings.channels[entry.channel] ?? entry.channel });
}

export function severityColor(severity) {
  return SEVERITY_COLOR[severity] ?? SEVERITY_COLOR.info;
}

export function severityIcon(severity, own = null) {
  return own || SEVERITY_ICON[severity] || SEVERITY_ICON.info;
}

export function formatClock(iso, language) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(language, { hour: "numeric", minute: "2-digit" }).format(date);
}

export function retryDelay(attempt) {
  return Math.min(30000, 1000 * 2 ** Math.min(attempt, 5));
}

// Protected addresses need a signed path before a browser may load them.
export function needsSignature(path) {
  return path.startsWith("/api/") || path.startsWith("/media/");
}

// ---- The element -----------------------------------------------------------------------------

const Base = typeof HTMLElement !== "undefined" ? HTMLElement : class {};
const SVG = "http://www.w3.org/2000/svg";

function h(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "text") node.textContent = value;
    else if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "style") node.setAttribute("style", value);
    else node.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of [].concat(children)) if (child) node.append(child);
  return node;
}

const icon = (name) => h("ha-icon", { icon: name });
const CSS_ESCAPE = (value) => String(value).replace(/["\\]/g, "\\$&");

const CSS = `
:host { display: block; height: 100%; }
* { box-sizing: border-box; }
button { font: inherit; color: inherit; }
ha-card { overflow: hidden; }
.tap { cursor: pointer; border: 0; background: none; width: 100%; text-align: start; padding: 0; display: block; color: inherit; }
.tap:focus-visible, .btn:focus-visible, .link:focus-visible, .pill:focus-visible, .x:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
.num { font-variant-numeric: tabular-nums; font-weight: 700; letter-spacing: -.02em; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.tile { width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center; --mdc-icon-size: 22px; color: var(--c, var(--info-color)); background: color-mix(in srgb, var(--c, var(--info-color)) 15%, transparent); flex: none; position: relative; }
.tile.ok { --c: var(--success-color); }
.tile.more { background: var(--secondary-background-color); color: var(--primary-text-color); font-size: 13px; font-weight: 700; }
.tile .pip { position: absolute; top: -3px; inset-inline-end: -3px; width: 12px; height: 12px; border-radius: 50%; background: var(--error-color); border: 2px solid var(--card-background-color); }
.crit-bg { background: linear-gradient(100deg, color-mix(in srgb, var(--error-color) 14%, var(--card-background-color)), var(--card-background-color) 70%); }
.t1 { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--secondary-text-color); font-weight: 600; }
.sub { color: var(--secondary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.crit .sub, .sub.crit { color: var(--error-color); font-weight: 600; }

ha-card.compact { height: 100%; }
ha-card.compact .tap, ha-card.small .tap { height: 100%; }
.cmp { display: flex; align-items: center; gap: 12px; padding: 0 14px; height: 100%; box-sizing: border-box; overflow: hidden; }
.cmp .tile { width: 40px; height: 40px; border-radius: 12px; }
.cmp .tx { flex: 1; min-width: 0; }
.cmp .t1 { font-weight: 600; font-size: 16px; text-transform: none; letter-spacing: 0; color: var(--primary-text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cmp .sub { font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tileA { display: flex; align-items: center; gap: 14px; padding: 16px 18px; }
.tileA .tx { flex: 1; min-width: 0; }
.tileA .big { font-size: 34px; line-height: 1; }
.tileA .zero { color: var(--success-color); font-size: 26px; }

.ringB { display: flex; align-items: center; gap: 16px; padding: 16px 18px; }
.ringw { position: relative; width: 72px; height: 72px; flex: none; }
.ringw svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.ringw .c { position: absolute; inset: 0; display: grid; place-items: center; font-size: 24px; --mdc-icon-size: 24px; }
.ringw .c ha-icon { color: var(--success-color); }
.ringB .tx { flex: 1; min-width: 0; }
.ringB .t2 { font-size: 16px; font-weight: 600; margin: 2px 0; }
.legend { display: flex; gap: 10px; flex-wrap: wrap; font-size: 12px; color: var(--secondary-text-color); }
.legend i { font-style: normal; display: inline-flex; align-items: center; gap: 4px; }
.legend i::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--c); }

.sq { container-type: size; width: 100%; aspect-ratio: 1; max-height: 100%; overflow: hidden; }
ha-card.small { height: 100%; }
.Q { height: 100%; padding: 11cqmin; display: flex; flex-direction: column; justify-content: space-between; }
.Q .tile { width: 24cqmin; height: 24cqmin; border-radius: 8cqmin; --mdc-icon-size: 13cqmin; }
.Q .n { font-size: 30cqmin; line-height: .9; }
.Q .lb { font-size: max(10px, 8cqmin); font-weight: 600; line-height: 1.2; }
.Q .sub { font-size: max(9px, 7cqmin); line-height: 1.2; }
.Q.crit { background: linear-gradient(160deg, color-mix(in srgb, var(--error-color) 24%, var(--card-background-color)), var(--card-background-color) 78%); }
.Q .top { display: flex; align-items: flex-start; justify-content: space-between; }
.QA .n { font-size: 38cqmin; line-height: .85; }
.QA.clear { background: color-mix(in srgb, var(--success-color) 14%, var(--card-background-color)); }
.QA.clear .top ha-icon { --mdc-icon-size: 30cqmin; color: var(--success-color); }
.Qr { align-items: center; justify-content: center; text-align: center; gap: 2cqmin; }
.Qr .rg { position: relative; width: 50cqmin; height: 50cqmin; flex: none; }
.Qr .rg svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.Qr .rg .c { position: absolute; inset: 0; display: grid; place-items: center; font-size: 18cqmin; --mdc-icon-size: 18cqmin; }
.Qr .rg .c ha-icon { color: var(--success-color); }
.Qm .g { display: grid; grid-template-columns: repeat(2, 24cqmin); grid-auto-rows: 24cqmin; gap: 4cqmin; }
.Qm .g .tile { width: 24cqmin; height: 24cqmin; border-radius: 7cqmin; --mdc-icon-size: 12cqmin; }
.Qm .g .tile.crit { box-shadow: 0 0 0 2px var(--card-background-color), 0 0 0 4px var(--error-color); }
.Qm .g .tile.more { font-size: 9cqmin; }
.Qm .g.one { grid-template-columns: 38cqmin; grid-auto-rows: 38cqmin; }
.Qm .g.one .tile { width: 38cqmin; height: 38cqmin; --mdc-icon-size: 20cqmin; border-radius: 11cqmin; }

.S { display: flex; align-items: stretch; }
.S .lp { width: 96px; flex: none; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; color: #fff; background: var(--primary-color); border: 0; cursor: pointer; padding: 0; }
.S.crit .lp { background: var(--error-color); }
.S.zero .lp { background: var(--success-color); }
.S .lp .n { font-size: 38px; line-height: 1; --mdc-icon-size: 38px; }
.S .lp small { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; }
.S .rp { flex: 1; min-width: 0; padding: 14px 16px; }
.S .hl { font-size: 17px; font-weight: 700; margin: 2px 0; }
.S.crit .hl { color: var(--error-color); }
.S .btns { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.btn { border: 0; border-radius: 999px; padding: 6px 14px; font-weight: 600; font-size: 13px; cursor: pointer; min-height: 32px; background: var(--primary-text-color); color: var(--card-background-color); }
.btn.ghost { background: var(--secondary-background-color); color: var(--primary-text-color); }
.btn[disabled] { opacity: .4; cursor: default; }

.head { display: flex; align-items: center; gap: 8px; padding: 16px 16px 8px; }
.head .ttl { font-size: 18px; font-weight: 700; flex: 1; letter-spacing: -.01em; }
.badge { font-size: 11px; background: var(--primary-color); color: #fff; border-radius: 999px; padding: 0 7px; min-width: 18px; text-align: center; }
.badge.crit { background: var(--error-color); }
.tools { display: flex; align-items: center; gap: 6px; padding: 0 16px 6px; }
.pill { border: 1px solid var(--divider-color); background: none; border-radius: 999px; padding: 2px 12px; font-size: 12px; cursor: pointer; min-height: 28px; }
.pill[aria-pressed="true"] { background: color-mix(in srgb, var(--primary-color) 14%, transparent); border-color: var(--primary-color); color: var(--primary-color); font-weight: 600; }
.link { background: none; border: 0; color: var(--primary-color); font-weight: 600; cursor: pointer; padding: 4px 6px; border-radius: 8px; min-height: 32px; }
.link.danger { color: var(--error-color); }
.link[disabled] { opacity: .4; cursor: default; }
.day { padding: 10px 20px 4px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--secondary-text-color); font-weight: 600; }
.list { padding: 0 8px 10px; }
.item { border-radius: 16px; position: relative; }
.item + .item::before { content: ""; position: absolute; top: 0; inset-inline: 12px; height: 1px; background: var(--divider-color); }
.item.open::before, .item.open + .item::before { display: none; }
.item.open { background: var(--secondary-background-color); }
.row { display: flex; gap: 12px; padding: 10px; align-items: center; }
.row .tile { width: 40px; height: 40px; border-radius: 12px; --mdc-icon-size: 20px; }
.row .bd { flex: 1; min-width: 0; }
.row .ttl2 { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item.read .ttl2 { font-weight: 500; }
.row .pv { font-size: 13px; color: var(--secondary-text-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row .rt { text-align: end; font-size: 12px; color: var(--secondary-text-color); display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--primary-color); }
.item.read .dot { background: transparent; }
.item.needs .dot { background: var(--error-color); }
.chips { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px; }
.chip { display: inline-flex; align-items: center; gap: 4px; border-radius: 999px; padding: 1px 8px; font-size: 11px; font-weight: 600; background: var(--secondary-background-color); color: var(--secondary-text-color); --mdc-icon-size: 12px; }
.chip.crit { background: color-mix(in srgb, var(--error-color) 14%, transparent); color: var(--error-color); }
.detail { padding: 0 12px 12px 62px; }
.detail p { margin: 0 0 10px; white-space: pre-wrap; overflow-wrap: anywhere; }
.detail img { max-width: 100%; max-height: 220px; border-radius: 12px; margin-bottom: 10px; display: block; }
.tl { list-style: none; margin: 0 0 6px; padding: 0 0 0 14px; font-size: 12px; color: var(--secondary-text-color); position: relative; }
.tl::before { content: ""; position: absolute; left: 3px; top: 6px; bottom: 6px; width: 2px; background: var(--divider-color); border-radius: 1px; }
.tl li { padding: 2px 0; position: relative; }
.tl li::before { content: ""; position: absolute; left: -14px; top: 7px; width: 8px; height: 8px; border-radius: 50%; background: var(--card-background-color); border: 2px solid var(--divider-color); }
.empty { text-align: center; padding: 34px 16px 40px; color: var(--secondary-text-color); }
.empty .tile { margin: 0 auto 10px; width: 56px; height: 56px; --mdc-icon-size: 28px; }
.note { padding: 16px; color: var(--secondary-text-color); }
.more { display: block; margin: 0 auto 12px; }
.tile.ini { overflow: hidden; --c: var(--primary-color); font-size: 18px; font-weight: 700; }
.tile.ini img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.row .from { font-size: 12px; color: var(--secondary-text-color); font-weight: 600; }
.cf { padding-bottom: 16px; }
.cf .lbl { padding: 10px 16px 4px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--secondary-text-color); font-weight: 600; }
.chips2 { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 16px; }
.pill[disabled], .pill[aria-disabled="true"] { opacity: .6; cursor: default; }
.cf .hint.soft { color: var(--secondary-text-color); }
.cf .hint { padding: 4px 16px 0; font-size: 12px; color: var(--warning-color); }
.cf textarea { display: block; width: calc(100% - 32px); margin: 0 16px; font: inherit; color: inherit; background: var(--secondary-background-color); border: 1px solid var(--divider-color); border-radius: 12px; padding: 10px; resize: vertical; min-height: 96px; }
.cf textarea:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 1px; }
.cf .count { padding: 2px 16px 0; text-align: end; font-size: 11px; color: var(--secondary-text-color); }
.cf .acts { display: flex; justify-content: flex-end; padding: 12px 16px 0; }
.note.err { color: var(--error-color); }

.scrim { position: fixed; inset: 0; background: rgba(8,10,14,.55); z-index: 9; display: grid; place-items: center; padding: 16px; }
.dialog { width: min(480px, 100%); max-height: 88vh; overflow: auto; background: var(--card-background-color); color: var(--primary-text-color); border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,.45); }
.x { background: var(--secondary-background-color); border: 0; border-radius: 50%; width: 36px; height: 36px; cursor: pointer; display: grid; place-items: center; color: inherit; }
@media (prefers-reduced-motion: no-preference) { .scrim { animation: fade .15s ease-out; } @keyframes fade { from { opacity: 0; } } }
`;

class HeadsUpInboxCard extends Base {
  static getConfigElement() {
    return document.createElement("heads-up-inbox-card-editor");
  }

  static getStubConfig() {
    return { size: "large" };
  }

  constructor() {
    super();
    this._config = null;
    this._state = { items: [], unread: 0, needs_action: 0, unread_critical: 0, has_person: true, more: false, all_notifications: false };
    this._scope = "inbox";
    this._extra = [];
    this._sentItems = [];
    this._sentMore = false;
    this._composing = null; // the draft while the compose view is open (D-279)
    this._recipients = null;
    this._recipientsError = null;
    this._filter = "all";
    this._open = new Set();
    this._dialog = false;
    this._error = false;
    this._loaded = false;
    this._unsub = null;
    this._generation = 0;
    this._retryTimer = null;
    this._attempt = 0;
    this._connection = null;
    this._connected = false;
    this._onReady = () => this._resubscribe();
    this._onKey = (event) => this._key(event);
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    this._config = normalizeConfig(config);
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (hass?.language !== this._language) {
      this._language = hass?.language;
      setLanguage(this._language);
      if (this._config && !first) this._render();
    }
    if (first && this._connected) this._subscribe();
  }

  connectedCallback() {
    this._connected = true;
    if (this._hass) this._subscribe();
  }

  disconnectedCallback() {
    this._connected = false;
    this._connection?.removeEventListener("ready", this._onReady);
    this._connection = null;
    this._unsubscribe();
    this._closeDialog(false);
  }

  getCardSize() {
    return this._config?.size === "large" ? Math.max(3, Math.min(8, this._items().length + 2)) : 2;
  }

  getGridOptions() {
    const size = this._config?.size ?? "large";
    if (size === "compact") return { columns: 6, rows: 1, min_columns: 3, min_rows: 1 };
    if (size === "small") return { columns: 3, rows: 2, min_columns: 3, min_rows: 2 };
    if (size === "medium") return { columns: 12, rows: "auto", min_columns: 6 };
    return { columns: 12, rows: "auto", min_columns: 6 };
  }

  _items() {
    return mergePages(this._state.items, this._extra);
  }

  // ---- data ----

  _unsubscribe() {
    const unsub = this._unsub;
    this._unsub = null;
    this._generation += 1;
    clearTimeout(this._retryTimer);
    this._retryTimer = null;
    if (unsub) unsub.then((fn) => fn()).catch(() => {});
  }

  // After a reconnect the old subscription is gone; the library's own re-subscribe is off because
  // it cannot retry when the command is not registered yet (N-39, N-40, D-041).
  _resubscribe() {
    this._unsub = null;
    this._generation += 1;
    this._attempt = 0;
    clearTimeout(this._retryTimer);
    this._subscribe();
  }

  _subscribe() {
    if (!this._hass || !this._config || this._unsub) return;
    const connection = this._hass.connection;
    if (this._connection !== connection) {
      this._connection?.removeEventListener("ready", this._onReady);
      connection.addEventListener("ready", this._onReady);
      this._connection = connection;
    }
    const generation = this._generation;
    const promise = connection.subscribeMessage(
      (event) => {
        if (generation !== this._generation) return;
        this._error = false;
        this._loaded = true;
        this._state = event;
        this._extra = [];
        this._render();
        if (visibleScope(event, this._scope) === "sent") this._loadSent();
      },
      { type: "heads_up/inbox_subscribe" },
      { resubscribe: false },
    );
    this._unsub = promise;
    promise.then(
      () => {
        if (generation === this._generation) this._attempt = 0;
      },
      () => {
        if (generation !== this._generation) return;
        this._unsub = null;
        this._error = true;
        this._render();
        this._retryTimer = setTimeout(() => this._subscribe(), retryDelay(this._attempt++));
      },
    );
  }

  _call(message) {
    return this._hass.callWS(message).catch(() => null);
  }

  _toggle(item) {
    if (this._open.has(item.message_id)) this._open.delete(item.message_id);
    else {
      this._open.add(item.message_id);
      if (item.unread) this._call({ type: "heads_up/inbox_read", message_id: item.message_id });
    }
    this._render();
  }

  _markAll() {
    this._call({ type: "heads_up/inbox_read_all" });
  }

  _delete(item) {
    this._open.delete(item.message_id);
    this._extra = this._extra.filter((i) => i.message_id !== item.message_id);
    this._sentItems = this._sentItems.filter((i) => i.message_id !== item.message_id);
    this._call({ type: "heads_up/inbox_delete", message_id: item.message_id }).then(() => {
      if (item.sent) this._loadSent();
    });
  }

  async _showMore() {
    const scope = visibleScope(this._state, this._scope);
    const sent = scope === "sent";
    const result = await this._call({
      type: "heads_up/inbox_list",
      view: scope,
      limit: PAGE,
      offset: scopeItems(sent ? this._sentItems : this._items(), scope).length,
    });
    if (!result) return;
    if (sent) {
      this._sentItems = mergePages(this._sentItems, result.items);
      this._sentMore = result.more;
    } else {
      this._extra = mergePages(this._extra, result.items);
      this._state = { ...this._state, more: result.more };
    }
    this._render();
  }

  async _loadSent() {
    const result = await this._call({ type: "heads_up/inbox_list", view: "sent", limit: PAGE });
    if (!result) return;
    this._sentItems = result.items;
    this._sentMore = result.more;
    this._render();
  }

  // ---- compose (D-265, D-279) ----

  _openCompose() {
    this._composing = { to: [], channels: ["inbox", "push"], text: "", busy: false, error: null, result: null };
    this._recipients = null;
    this._recipientsError = null;
    this._mailOn = false;
    this._call({ type: "heads_up/inbox_recipients" }).then((result) => {
      if (!this._composing) return;
      if (result) {
        this._recipients = result.recipients;
        this._mailOn = result.mail === true;
      }
      else this._recipientsError = "error_send";
      this._renderCompose();
    });
    if (!this._dialog) this._openDialog();
    this._renderCompose();
  }

  _closeCompose(toSent = false) {
    this._composing = null;
    if (toSent) {
      this._scope = "sent";
      this._loadSent();
    }
    this._render();
    this._restoreFocus(this._overlayRoot ?? this.shadowRoot, "compose");
  }

  async _send() {
    const draft = this._composing;
    if (!draft || draft.busy || !canSend(draft)) return;
    draft.busy = true;
    draft.error = null;
    this._renderCompose();
    try {
      draft.result = await this._hass.callWS({
        type: "heads_up/send_message",
        to: draft.to,
        text: draft.text.trim(),
        channels: draft.channels,
      });
      this._loadSent();
    } catch (error) {
      draft.error = sendError(error);
    }
    draft.busy = false;
    if (this._composing === draft) this._renderCompose();
  }

  _renderCompose() {
    if (!this._dialogBox || !this._composing) return;
    const focus = this._focusKey(this._overlayRoot);
    this._dialogBox.setAttribute("aria-label", STRINGS.new_message);
    this._dialogBox.replaceChildren(this._composeView());
    this._restoreFocus(this._overlayRoot, focus);
  }

  _composeView() {
    const s = STRINGS;
    const draft = this._composing;
    const states = this._hass?.states;
    const head = h("div", { class: "head" }, [
      h("button", { class: "x", "data-key": "back", "aria-label": s.back, onclick: () => this._closeCompose() }, [icon("mdi:arrow-left")]),
      h("div", { class: "ttl", text: s.new_message }),
      h("button", { class: "x", "data-key": "close", "aria-label": s.close, onclick: () => this._closeDialog() }, [icon("mdi:close")]),
    ]);
    if (draft.result) return h("div", {}, [head, this._composeDone(draft.result)]);
    const people = this._recipients;
    let who;
    if (this._recipientsError) who = h("div", { class: "note", role: "alert", text: s[this._recipientsError] });
    else if (people === null) who = h("div", { class: "note", text: s.loading_people });
    else if (!people.length) who = h("div", { class: "note", text: s.no_inbox_for_you });
    else {
      who = h("div", { class: "chips2", role: "group", "aria-label": s.to_label }, people.map((p) =>
        h("button", {
          class: "pill", "data-key": `to:${p.person}`, "aria-pressed": String(draft.to.includes(p.person)),
          onclick: () => {
            draft.to = draft.to.includes(p.person) ? draft.to.filter((x) => x !== p.person) : [...draft.to, p.person];
            this._renderCompose();
          },
          text: p.me ? `${p.name} (${s.you})` : p.name,
        }),
      ));
    }
    const hints = composeHints(people ?? [], draft.to, draft.channels).map((hint) =>
      h("div", { class: "hint", text: fill(s.skip_note, { name: hint.name, channels: hint.channels.map((c) => s.via[c]).join(", ") }) }),
    );
    const via = h("div", { class: "chips2", role: "group", "aria-label": s.send_via }, MESSAGE_CHANNELS.filter((c) => c !== "mail" || this._mailOn).map((c) =>
      h("button", {
        class: "pill", "data-key": `via:${c}`, "aria-pressed": String(draft.channels.includes(c)),
        "aria-disabled": c === "inbox" ? "true" : null, title: c === "inbox" ? s.inbox_always : null,
        onclick: () => {
          if (c === "inbox") {
            // Always on: a click says why instead of doing nothing.
            draft.inboxNote = true;
            this._renderCompose();
            return;
          }
          draft.channels = draft.channels.includes(c) ? draft.channels.filter((x) => x !== c) : [...draft.channels, c];
          this._renderCompose();
        },
        text: s.via[c],
      }),
    ));
    const counter = h("div", { class: "count", text: fill(s.characters, { n: draft.text.length, max: MAX_MESSAGE }) });
    const send = h("button", { class: "btn", "data-key": "send", disabled: canSend(draft) && !draft.busy ? null : true, onclick: () => this._send(), text: s.send });
    const area = h("textarea", {
      "data-key": "text", rows: "4", maxlength: String(MAX_MESSAGE), "aria-label": s.message_label,
      oninput: (event) => {
        draft.text = event.target.value;
        counter.textContent = fill(s.characters, { n: draft.text.length, max: MAX_MESSAGE });
        send.toggleAttribute("disabled", !canSend(draft) || draft.busy);
      },
    });
    area.value = draft.text;
    return h("div", { class: "cf" }, [
      head,
      h("div", { class: "lbl", text: s.to_label }), who, ...hints,
      h("div", { class: "lbl", text: s.send_via }), via,
      draft.inboxNote ? h("div", { class: "hint soft", role: "status", text: s.inbox_always }) : null,
      h("div", { class: "lbl", text: s.message_label }), area, counter,
      draft.error ? h("div", { class: "note err", role: "alert", text: s[draft.error] }) : null,
      h("div", { class: "acts" }, [send]),
    ]);
  }

  _composeDone(result) {
    const s = STRINGS;
    const names = Object.fromEntries((this._recipients ?? []).map((p) => [p.person, p.name]));
    const skipped = new Map();
    for (const row of result.skipped ?? []) {
      skipped.set(row.person, [...(skipped.get(row.person) ?? []), s.via[row.channel] ?? row.channel]);
    }
    const lines = [...skipped].map(([person, channels]) =>
      h("div", { class: "hint", text: fill(s.not_delivered, { name: names[person] ?? personName(this._hass?.states, person), channels: channels.join(", ") }) }),
    );
    return h("div", { class: "cf" }, [
      h("div", { class: "note", role: "status", text: s.sent_ok }),
      ...lines,
      h("div", { class: "acts" }, [h("button", { class: "btn", "data-key": "done", onclick: () => this._closeCompose(true), text: s.done })]),
    ]);
  }

  // ---- dialog ----

  _openDialog() {
    if (this._dialog) return;
    this._dialog = true;
    this._openerKey = this._focusKey(this.shadowRoot);
    this._overlay = h("div");
    this._overlayRoot = this._overlay.attachShadow({ mode: "open" });
    // The scrim and the dialog stay for as long as it is open, so a change of the list does not
    // play the fade again; only their content is replaced.
    this._dialogBox = h("div", { class: "dialog", role: "dialog", "aria-modal": "true", "aria-label": STRINGS.inbox });
    const scrim = h("div", { class: "scrim", onclick: (e) => e.target === scrim && this._closeDialog() }, [this._dialogBox]);
    this._overlayRoot.append(h("style", { text: CSS }), scrim);
    document.body.append(this._overlay);
    document.addEventListener("keydown", this._onKey, true);
    this._render();
    queueMicrotask(() => this._overlayRoot.querySelector(".x")?.focus());
  }

  _closeDialog(restore = true) {
    if (!this._dialog) return;
    this._dialog = false;
    this._composing = null;
    document.removeEventListener("keydown", this._onKey, true);
    this._overlay?.remove();
    this._overlay = null;
    this._overlayRoot = null;
    this._dialogBox = null;
    this._render();
    this._onClosed?.();
    if (restore) this._restoreFocus(this.shadowRoot, this._openerKey);
  }

  _key(event) {
    if (!this._dialog) return;
    if (event.key === "Escape") {
      event.stopPropagation();
      if (this._composing) this._closeCompose();
      else this._closeDialog();
    } else if (event.key === "Tab") {
      const nodes = [...this._overlayRoot.querySelectorAll("button:not([disabled]), textarea")];
      if (!nodes.length) return;
      const active = this._overlayRoot.activeElement;
      const last = nodes[nodes.length - 1];
      if (event.shiftKey && (active === nodes[0] || !active)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        nodes[0].focus();
      }
    }
  }

  // ---- rendering ----

  _render() {
    if (!this._config) return;
    const root = this.shadowRoot;
    const s = STRINGS;
    const body = [];
    if (!this._loaded && !this._error) body.push(h("div", { class: "note", text: "…" }));
    else if (this._error && !this._loaded) body.push(h("div", { class: "note", role: "alert", text: s.load_error }));
    else if (!this._state.has_person) body.push(h("div", { class: "note", text: s.no_person }));
    else if (this._config.size === "large") body.push(this._listView(false));
    else body.push(this._badge());
    const focus = this._focusKey(root);
    root.replaceChildren(h("style", { text: CSS }), h("ha-card", { class: this._config.size }, body));
    this._restoreFocus(root, focus);
    if (this._dialog && this._dialogBox && !this._composing) {
      const dialogFocus = this._focusKey(this._overlayRoot);
      this._dialogBox.setAttribute("aria-label", s.inbox);
      this._dialogBox.replaceChildren(this._dialogContent());
      this._restoreFocus(this._overlayRoot, dialogFocus);
    }
  }

  // The list, or the reason there is none yet: loading, a failed load, or a user without a person.
  _dialogContent() {
    const s = STRINGS;
    if (this._loaded && this._state.has_person) return this._listView(true);
    const text = !this._loaded ? (this._error ? s.load_error : "…") : s.no_person;
    return h("div", {}, [
      h("div", { class: "head" }, [
        h("div", { class: "ttl", text: s.inbox }),
        h("button", { class: "x", "data-key": "close", "aria-label": s.close, onclick: () => this._closeDialog() }, [icon("mdi:close")]),
      ]),
      h("div", { class: "note", role: this._error ? "alert" : null, text }),
    ]);
  }

  // A change of the list rebuilds it; the control the user was on gets the focus back.
  _focusKey(root) {
    return root.activeElement?.dataset?.key ?? null;
  }

  // `ha-card` lays out its content one frame after it is created, and an element that is not laid
  // out cannot take the focus, so a second try follows on the next frame.
  _restoreFocus(root, key) {
    if (!key) return;
    const find = () => root.querySelector(`[data-key="${CSS_ESCAPE(key)}"]`);
    find()?.focus();
    if (root.activeElement !== find() && typeof requestAnimationFrame !== "undefined") {
      requestAnimationFrame(() => {
        if (!root.activeElement) find()?.focus();
      });
    }
  }

  _stateNumbers() {
    const { unread, needs_action: needs } = this._state;
    return { unread, needs_action: needs };
  }

  _badge() {
    const { design, size } = this._config;
    if (size === "compact") return this._compact();
    if (size === "small") return { number: this._number(), ring: this._smallRing(), mosaic: this._mosaic() }[design];
    return { tile: this._tileA(), ring: this._ringB(), split: this._split() }[design];
  }

  _opens(node, label) {
    return h("button", { class: "tap", "data-key": "open", "aria-label": label, onclick: () => this._openDialog() }, [node]);
  }

  _tileIcon(kind, extra = "") {
    const needs = kind === "needs";
    return h("div", { class: `tile ${kind === "clear" ? "ok" : ""} ${extra}`, style: needs ? `--c:${SEVERITY_COLOR.critical}` : null }, [
      icon(kind === "clear" ? "mdi:check" : "mdi:bell"),
      needs ? h("span", { class: "pip" }) : null,
    ]);
  }

  _label() {
    return `${STRINGS.inbox}: ${summaryText(this._stateNumbers(), STRINGS)}`;
  }

  _compact() {
    const n = this._stateNumbers();
    const tile = compactTile(n, this._items());
    const color = tile.kind === "needs" ? SEVERITY_COLOR.critical : tile.severity ? severityColor(tile.severity) : null;
    return this._opens(
      h("div", { class: `cmp ${tile.kind === "needs" ? "crit-bg" : ""}` }, [
        h("div", { class: `tile ${tile.kind === "clear" ? "ok" : ""}`, style: color ? `--c:${color}` : null }, [
          icon(tile.kind === "clear" ? "mdi:check" : "mdi:bell"),
          tile.kind === "needs" ? h("span", { class: "pip" }) : null,
        ]),
        h("div", { class: "tx" }, [h("div", { class: "t1", text: tile.title }), h("div", { class: "sub", text: tile.sub })]),
      ]),
      this._label(),
    );
  }

  _tileA() {
    const n = this._stateNumbers();
    const kind = summaryKind(n);
    const top = topItem(this._items());
    const sub = kind === "unread" && top ? `${summaryText(n, STRINGS)} · ${top.title}` : summaryText(n, STRINGS);
    return this._opens(
      h("div", { class: `tileA ${kind === "needs" ? "crit crit-bg" : ""}` }, [
        this._tileIcon(kind),
        h("div", { class: "tx" }, [h("div", { style: "font-weight:600;font-size:15px", text: STRINGS.inbox }), h("div", { class: "sub", text: sub })]),
        n.unread ? h("div", { class: "big num", text: String(n.unread) }) : h("ha-icon", { class: "zero", icon: "mdi:check" }),
      ]),
      this._label(),
    );
  }

  _ringSvg(radius, width, box) {
    const c = box / 2;
    const svg = document.createElementNS(SVG, "svg");
    svg.setAttribute("viewBox", `0 0 ${box} ${box}`);
    const circle = (extra) => {
      const node = document.createElementNS(SVG, "circle");
      for (const [k, v] of Object.entries({ cx: c, cy: c, r: radius, fill: "none", "stroke-width": width, ...extra })) node.setAttribute(k, v);
      return node;
    };
    svg.append(circle({ stroke: "var(--secondary-background-color)" }));
    for (const seg of ringSegments(severityCounts(this._items()), radius)) {
      svg.append(
        circle({
          stroke: severityColor(seg.severity),
          "stroke-linecap": "round",
          "stroke-dasharray": `${Math.max(seg.length, 1)} ${2 * Math.PI * radius}`,
          "stroke-dashoffset": -seg.offset,
        }),
      );
    }
    return svg;
  }

  _ringB() {
    const n = this._stateNumbers();
    const kind = summaryKind(n);
    const counts = severityCounts(this._items());
    return this._opens(
      h("div", { class: "ringB" }, [
        h("div", { class: "ringw" }, [
          this._ringSvg(29, 7, 72),
          h("div", { class: "c num" }, [n.unread ? document.createTextNode(String(n.unread)) : icon("mdi:check")]),
        ]),
        h("div", { class: "tx" }, [
          h("div", { class: "t1", text: STRINGS.inbox }),
          h("div", { class: `t2 ${kind === "needs" ? "sub crit" : ""}`, text: summaryText(n, STRINGS) }),
          h(
            "div",
            { class: "legend" },
            counts.length
              ? counts.map(([s, c]) => h("i", { style: `--c:${severityColor(s)}`, text: `${c} ${STRINGS.severity[s]}` }))
              : [document.createTextNode(STRINGS.nothing_waiting)],
          ),
        ]),
        icon("mdi:chevron-right"),
      ]),
      this._label(),
    );
  }

  _split() {
    const n = this._stateNumbers();
    const kind = summaryKind(n);
    const top = topItem(this._items());
    return h("div", { class: `S ${kind === "needs" ? "crit" : kind === "clear" ? "zero" : ""}` }, [
      h("button", { class: "lp", "data-key": "open-count", "aria-label": this._label(), onclick: () => this._openDialog() }, [
        h("div", { class: "n num" }, [n.unread ? document.createTextNode(String(n.unread)) : icon("mdi:check")]),
        h("small", { text: n.unread ? STRINGS.unread_word : STRINGS.clear_word }),
      ]),
      h("div", { class: "rp" }, [
        h("div", { class: "t1", text: STRINGS.inbox }),
        h("div", { class: "hl", text: summaryText(n, STRINGS) }),
        h("div", { class: "sub", text: top ? top.title : STRINGS.nothing_waiting }),
        h("div", { class: "btns" }, [
          h("button", { class: "btn", "data-key": "open", onclick: () => this._openDialog(), text: STRINGS.open }),
          h("button", { class: "btn ghost", "data-key": "read-all", disabled: n.unread ? null : true, onclick: () => this._markAll(), text: STRINGS.mark_all_read }),
        ]),
      ]),
    ]);
  }

  _square(kind, children) {
    const n = this._stateNumbers();
    const needs = summaryKind(n) === "needs";
    return this._opens(h("div", { class: "sq" }, [h("div", { class: `Q ${kind} ${needs ? "crit" : ""}` }, children)]), this._label());
  }

  _number() {
    const n = this._stateNumbers();
    const kind = summaryKind(n);
    // With nothing unread there is no number: a tinted tile with a bare check, so it differs from
    // the mosaic's boxed check on a plain card.
    const top = n.unread
      ? h("div", { class: "top" }, [this._tileIcon(kind), h("div", { class: "n num", text: String(n.unread) })])
      : h("div", { class: "top" }, [icon("mdi:check-circle-outline")]);
    return this._square(n.unread ? "QA" : "QA clear", [
      top,
      h("div", {}, [h("div", { class: "lb", text: STRINGS.inbox }), h("div", { class: "sub", text: summaryText(n, STRINGS) })]),
    ]);
  }

  _smallRing() {
    const n = this._stateNumbers();
    return this._square("Qr", [
      h("div", { class: "rg" }, [this._ringSvg(29, 7, 72), h("div", { class: "c num" }, [n.unread ? document.createTextNode(String(n.unread)) : icon("mdi:check")])]),
      h("div", {}, [h("div", { class: "lb", text: STRINGS.inbox }), h("div", { class: "sub", text: summaryText(n, STRINGS) })]),
    ]);
  }

  _mosaic() {
    const n = this._stateNumbers();
    const tiles = mosaicTiles(this._items());
    const cells = tiles.map((t) =>
      t.more
        ? h("div", { class: "tile more", text: `+${t.more}` })
        : h("div", { class: `tile ${t.item.needs_action ? "crit" : ""}`, style: `--c:${severityColor(t.item.severity)}` }, [icon(severityIcon(t.item.severity, t.item.icon))]),
    );
    return this._square("Qm", [
      n.unread ? h("div", { class: "g" }, cells) : h("div", { class: "g one" }, [h("div", { class: "tile ok" }, [icon("mdi:check")])]),
      h("div", {}, [h("div", { class: "lb", text: n.unread ? `${STRINGS.inbox} · ${n.unread}` : STRINGS.inbox }), h("div", { class: "sub", text: summaryText(n, STRINGS) })]),
    ]);
  }

  // The list is the large card and the content of the dialog.
  _listView(dialog) {
    const s = STRINGS;
    const n = this._stateNumbers();
    const scope = visibleScope(this._state, this._scope);
    const sent = scope === "sent";
    const items = filterItems(scopeItems(sent ? this._sentItems : this._items(), scope), sent ? "all" : this._filter);
    const head = h("div", { class: "head" }, [
      h("div", { class: "ttl", text: s.inbox }),
      showCompose(this._state, this._config)
        ? h("button", { class: "x", "data-key": "compose", "aria-label": s.new_message, onclick: () => this._openCompose() }, [icon("mdi:pencil-plus")])
        : null,
      n.unread ? h("span", { class: `badge ${n.needs_action ? "crit" : ""}`, text: String(n.unread), "aria-label": fill(s.unread_n, { n: n.unread }) }) : null,
      dialog ? h("button", { class: "x", "data-key": "close", "aria-label": s.close, onclick: () => this._closeDialog() }, [icon("mdi:close")]) : null,
    ]);
    const tabs = visibleTabs(this._state);
    const labels = { inbox: s.inbox, all: s.all_notifications, sent: s.sent_tab };
    const seg =
      tabs.length > 1
        ? h("div", { class: "tools" }, [
            h("div", { class: "seg", role: "group", "aria-label": s.inbox }, tabs.map((key) =>
              h("button", {
                class: "pill", "data-key": `scope:${key}`, "aria-pressed": String(scope === key),
                onclick: () => {
                  this._scope = key;
                  if (key === "sent") this._loadSent();
                  this._render();
                },
                text: labels[key],
              }),
            )),
          ])
        : null;
    const tools = sent ? null : h("div", { class: "tools" }, [
      ...["all", "unread"].map((f) =>
        h("button", { class: "pill", "data-key": `filter:${f}`, "aria-pressed": String(this._filter === f), onclick: () => { this._filter = f; this._render(); }, text: s[`filter_${f}`] }),
      ),
      h("span", { style: "flex:1" }),
      h("button", { class: "link", "data-key": "read-all", disabled: n.unread ? null : true, onclick: () => this._markAll(), text: s.mark_all_read }),
    ]);
    let body;
    if (items.length) {
      const groups = dayGroups(items);
      body = h("div", { class: "list" }, groups.flatMap((g) => [h("div", { class: "day", text: this._dayLabel(g) }), ...g.items.map((i) => this._row(i))]));
    } else {
      const unread = this._filter === "unread";
      body = h("div", { class: "empty" }, [
        h("div", { class: "tile ok" }, [icon("mdi:check")]),
        h("div", {}, [h("b", { text: sent ? s.nothing_sent : unread ? s.nothing_unread : s.nothing_yet })]),
        h("div", { text: sent ? s.sent_here : unread ? s.caught_up_message : s.new_messages_show }),
      ]);
    }
    const more = (sent ? this._sentMore : this._state.more) ? h("button", { class: "link more", "data-key": "more", onclick: () => this._showMore(), text: s.show_more }) : null;
    return h("div", {}, [head, seg, tools, body, more]);
  }

  _dayLabel(group) {
    if (group.kind === "today") return STRINGS.today;
    if (group.kind === "yesterday") return STRINGS.yesterday;
    const options = group.kind === "weekday" ? { weekday: "long" } : { day: "numeric", month: "long", year: "numeric" };
    return new Intl.DateTimeFormat(this._language, options).format(group.date);
  }

  _row(item) {
    const s = STRINGS;
    const open = this._open.has(item.message_id);
    const text = visibleText(item, this._config);
    const line = rowLine(item, this._hass?.states, s);
    const via = item.copy ? item.via.map((c) => h("span", { class: "chip", text: s.channels[c] ?? c })) : [];
    const chips = [
      ...via,
      item.needs_action ? h("span", { class: "chip crit" }, [icon("mdi:alert"), document.createTextNode(s.chip_needs_action)]) : null,
      item.resolved ? h("span", { class: "chip", text: s.chip_resolved }) : null,
    ].filter(Boolean);
    const row = h("button", { class: "tap row", "data-key": `row:${item.message_id}`, "aria-expanded": String(open), onclick: () => this._toggle(item) }, [
      this._rowTile(item),
      h("div", { class: "bd" }, [
        h("div", { class: "ttl2", text: item.title || text }),
        line ? h("div", { class: "from", text: line }) : null,
        !open && text ? h("div", { class: "pv", text }) : null,
        chips.length ? h("div", { class: "chips" }, chips) : null,
      ]),
      h("div", { class: "rt" }, [
        h("span", { text: formatClock(item.updated, this._language) }),
        item.unread && !item.copy ? h("span", { class: "dot", role: "img", "aria-label": s.unread_label }) : null,
      ]),
    ]);
    const detail = open ? this._detail(item, text) : null;
    return h("div", { class: `item ${item.unread ? "" : "read"} ${open ? "open" : ""} ${item.needs_action ? "needs" : ""}` }, [row, detail]);
  }

  // A message between people shows the person's picture, else their initial; any other item the
  // icon of its severity.
  _rowTile(item) {
    const avatar = rowAvatar(item, this._hass?.states);
    const style = `--c:${severityColor(item.severity)}`;
    if (!avatar) return h("div", { class: "tile", style }, [icon(severityIcon(item.severity, item.icon))]);
    const tile = h("div", { class: "tile ini", style }, [h("span", { text: avatar.initial })]);
    if (avatar.picture) {
      const image = h("img", { alt: "", loading: "lazy", hidden: true });
      image.addEventListener("load", () => image.removeAttribute("hidden"));
      image.addEventListener("error", () => image.remove());
      image.src = avatar.picture;
      tile.append(image);
    }
    return tile;
  }

  _detail(item, text) {
    const s = STRINGS;
    const lines = item.timeline.map((e) => h("li", { text: `${formatClock(e.at, this._language)} ${timelineText(e, s)}` }));
    if (item.resolved && item.resolved_reason) {
      lines.push(h("li", { text: fill(s.ended_because, { reason: s.reasons[item.resolved_reason] ?? item.resolved_reason }) }));
    }
    const picture = item.image ? this._picture(item.image) : null;
    return h("div", { class: "detail" }, [
      picture,
      text ? h("p", { text }) : null,
      h("ul", { class: "tl" }, lines),
      h("button", { class: "link danger", "data-key": `delete:${item.message_id}`, onclick: () => this._delete(item), text: s.delete }),
    ]);
  }

  // A protected address needs a signed path first; a picture that fails to load is left out.
  _picture(path) {
    const image = h("img", { alt: "", loading: "lazy", hidden: true });
    image.addEventListener("load", () => image.removeAttribute("hidden"));
    image.addEventListener("error", () => image.remove());
    const sign = needsSignature(path) ? this._hass.callWS({ type: "auth/sign_path", path, expires: 3600 }).then((r) => r.path) : Promise.resolve(path);
    sign.then((url) => (image.src = url)).catch(() => image.remove());
    return image;
  }
}

class HeadsUpInboxCardEditor extends Base {
  setConfig(config) {
    this._config = config;
    this._update();
  }

  set hass(hass) {
    this._hass = hass;
    if (hass?.language !== this._language) {
      this._language = hass?.language;
      setLanguage(this._language);
    }
    this._update();
  }

  _schema(size) {
    const t = STRINGS.editor;
    const schema = [
      { name: "size", selector: { select: { mode: "dropdown", options: SIZES.map((v) => ({ value: v, label: t[`size_${v}`] })) } } },
    ];
    if (DESIGNS[size].length) {
      schema.push({ name: "design", selector: { select: { mode: "dropdown", options: DESIGNS[size].map((v) => ({ value: v, label: t[`design_${v}`] })) } } });
    }
    schema.push({ name: "titles_only", selector: { boolean: {} } });
    schema.push({ name: "hide_send_button", selector: { boolean: {} } });
    return schema;
  }

  _update() {
    if (!this._config) return;
    const size = SIZES.includes(this._config.size) ? this._config.size : "large";
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) => STRINGS.editor[schema.name] ?? schema.name;
      this._form.addEventListener("value-changed", (ev) => {
        ev.stopPropagation();
        const config = { ...ev.detail.value };
        // A design belongs to one size: changing the size drops a design it does not have.
        const sized = SIZES.includes(config.size) ? config.size : "large";
        if (config.design && !DESIGNS[sized].includes(config.design)) delete config.design;
        // Keep the saved YAML minimal: no default size, no cleared values, no switches that are off.
        for (const key of Object.keys(config)) {
          const v = config[key];
          if (v === undefined || v === null || v === "" || v === false || (key === "size" && v === "large")) delete config[key];
        }
        this.dispatchEvent(new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } }));
      });
      this.append(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema(size);
    this._form.data = { size: "large", ...this._config };
  }
}

// The frontend's app bundle replaces window.customElements with a scoped-registry polyfill on
// browsers without a native one; an element defined before that swap is never seen (D-072).
const FRONTEND_TAG = "home-assistant";

export function whenFrontendReady(getRegistry, wait = setTimeout, maxMs = 10000, now = Date.now) {
  return new Promise((resolve) => {
    const start = now();
    const check = () => {
      if (getRegistry().get(FRONTEND_TAG) || now() - start >= maxMs) resolve();
      else wait(check, 25);
    };
    check();
  });
}

// Any card or button of the page can ask for the inbox with this event, also when no inbox card is
// on the dashboard: a hidden card opens the dialog and removes itself when it is closed. The
// banner card's Open inbox button uses it.
const OPEN_EVENT = "heads-up-open-inbox";
let opened = null;

function openInbox() {
  if (opened) return;
  const card = document.createElement("heads-up-inbox-card");
  card.style.display = "none";
  card.setConfig({ size: "small" });
  card.hass = document.querySelector("home-assistant")?.hass;
  card._onClosed = () => {
    card.remove();
    if (opened === card) opened = null;
  };
  opened = card;
  document.body.append(card);
  card._openDialog();
}

function registerElements() {
  const registry = window.customElements;
  if (!registry.get("heads-up-inbox-card")) registry.define("heads-up-inbox-card", HeadsUpInboxCard);
  if (!registry.get("heads-up-inbox-card-editor")) registry.define("heads-up-inbox-card-editor", HeadsUpInboxCardEditor);
  if (!window.__headsUpInboxOpener) {
    window.__headsUpInboxOpener = true;
    window.addEventListener(OPEN_EVENT, openInbox);
  }
  window.customCards = window.customCards || [];
  if (!window.customCards.some((card) => card.type === "heads-up-inbox-card")) {
    window.customCards.push({
      type: "heads-up-inbox-card",
      name: "Heads Up Inbox",
      description: "Your own inbox of Heads Up messages.",
      documentationURL: "https://github.com/Seyphaton/ha-heads-up",
    });
  }
}

if (typeof customElements !== "undefined") {
  whenFrontendReady(() => window.customElements).then(registerElements);
}
