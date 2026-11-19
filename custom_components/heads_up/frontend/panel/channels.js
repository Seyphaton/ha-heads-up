// Heads Up panel: Channels page (D-119): settings of push, popup and speech by severity.

export const STRINGS = {
  en: {
    title: "Channels",
    banner: "Banner",
    banner_snooze: "Snooze choices on the banner",
    banner_snooze_hint: "Used when a call or watch rule sets no snooze choices of its own. Whether a message can be snoozed, and the dismiss settings, are under Settings, Messages: they apply to banner, push and popup. The look of the card is set in the card's options.",
    snooze_time: "Snooze time on push and popup (minutes)",
    snooze_time_hint: "1–1440. The Snooze button of the push and of the popup snoozes for this time. It is the same setting on the Push and Popup rows.",
    bad_snooze_time: "The snooze time is a whole number of minutes from 1 to 1440.",
    snooze_summary: "Snooze {time}",
    styles_label: "Popup by severity",
    styles_hint: "Set on the Severities page.",
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 hour", "120": "2 hours", "240": "4 hours", "480": "8 hours", "1440": "24 hours"},
    minutes_n: "{n} minutes",
    no_choices: "no snooze choices",
    col_channel: "Channel",
    col_settings: "Settings",
    sticky_on: "kept after a tap",
    android: "Android channel {id}",
    ha_language: "Home Assistant language",
    mail_off: "Off",
    global_to: "global address {a}",
    edit: "Edit {name}",
    changed: "changed",
    severities_note: "The push level and the popup style of each severity are set on the Severities page.",
    severities_link: "Severities",
    intro: "How each channel works for every message. Select a channel to change it.",
    push: "Push",
    popup: "Popup",
    speech: "Speech",
    severities: { success: "Success", info: "Info", warning: "Warning", critical: "Critical" },
    levels: { passive: "Passive (no sound)", normal: "Normal", "time-sensitive": "Time sensitive", critical: "Critical (alarm)" },
    styles: { card: "Corner, bottom right", card_bottom_left: "Corner, bottom left", card_top_right: "Corner, top right", card_top_left: "Corner, top left", modal: "Centered window", off: "Off" },
    push_level: "Push level when the severity is {severity}",
    popup_style: "Popup when the severity is {severity}",
    critical_note: "The level critical is an alarm on both platforms. iOS: the critical alert; it needs the app's permission, plays a sound even in silent mode and cannot be replaced or grouped. Android: the alarm channel; it sounds even in vibrate and silent mode and is delivered at once. Do Not Disturb is only overridden if you allow it for that channel in the Android settings. Time sensitive is delivered at once on Android too.",
    ha_language_named: "Home Assistant language ({name})",
    no_engine_languages: "Choose a text-to-speech engine under Settings, Speech to pick from its languages. Until then, type a language code such as en-US, or leave it empty for the Home Assistant language.",
    lockscreen: "Lock-screen text",
    lockscreens: { full: "Title and text", title_only: "Title only", generic: "Generic text" },
    buttons_note: "Buttons: Snooze and Dismiss. Acknowledge is added when an escalation or reminder policy applies.",
    sticky: "Keep the notification after a tap (Android)",
    channel_id: "Android channel name",
    channel_id_note: "Android keeps the first importance of a channel, so each level has its own channel named <name>_<level>.",
    language: "Spoken language",
    speech_note: "Speech uses announce when the player supports it. The volume is set under Settings, Speech volume. Assist satellites speak in the language of their own voice assistant.",
    save: "Save",
    saved: "Saved.",
    failed: "Could not save. Try again.",
    valid: "No problems.",
    bad_channel_id: "The channel name uses lower-case letters, digits and underscores, up to 40 characters.",
    mail: "Mail",
    mail_intro: "Mail calls a notify service once per recipient with a subject and a body. A person's address is set under Recipients, where Mail must be switched on for them.",
    mail_service: "Notify service",
    mail_service_none: "None (mail is off)",
    mail_global_address: "Global address",
    mail_global_note: "Optional. Not tied to a person: name Global address as a recipient to send to it. It is never used for a person without an address.",
    mail_subject: "Subject",
    mail_body: "Body",
    mail_placeholders: "Placeholders: {severity} (for example Critical), {title} (the title, or the message when there is none), {message}, {person} (the person's name, empty for the Global address), {person_id} (the part of the person's entity ID after person., for example philip; lower case), {id}, {tag}.",
    bad_mail_subject: "The subject needs text, up to 200 characters, and may use only the placeholders listed.",
    bad_mail_body: "The body needs text, up to 2000 characters, and may use only the placeholders listed.",
    bad_mail_address: "The address can have at most 254 characters.",
  },
  de: {
    title: "Kanäle",
    banner: "Banner",
    banner_snooze: "Auswahl beim Zurückstellen im Banner",
    banner_snooze_hint: "Gilt, wenn ein Aufruf oder eine Überwachungsregel keine eigene Auswahl angibt. Ob eine Meldung zurückgestellt werden kann und die Einstellungen zum Schließen stehen unter Einstellungen, Meldungen: Sie gelten für Banner, Push und Popup. Das Aussehen der Karte legst du in den Optionen der Karte fest.",
    snooze_time: "Zurückstellzeit bei Push und Popup (Minuten)",
    snooze_time_hint: "1–1440. Die Schaltfläche Zurückstellen von Push und Popup stellt für diese Zeit zurück. Es ist dieselbe Einstellung in den Zeilen Push und Popup.",
    bad_snooze_time: "Die Zurückstellzeit ist eine ganze Zahl von 1 bis 1440 Minuten.",
    snooze_summary: "Zurückstellen {time}",
    styles_label: "Popup nach Schweregrad",
    styles_hint: "Wird auf der Seite Schweregrade festgelegt.",
    minutes: {"5": "5 Minuten", "15": "15 Minuten", "30": "30 Minuten", "60": "1 Stunde", "120": "2 Stunden", "240": "4 Stunden", "480": "8 Stunden", "1440": "24 Stunden"},
    minutes_n: "{n} Minuten",
    no_choices: "keine Auswahl beim Zurückstellen",
    col_channel: "Kanal",
    col_settings: "Einstellungen",
    sticky_on: "bleibt nach Tippen",
    android: "Android-Kanal {id}",
    ha_language: "Sprache von Home Assistant",
    mail_off: "Aus",
    global_to: "globale Adresse {a}",
    edit: "{name} bearbeiten",
    changed: "geändert",
    severities_note: "Push-Stufe und Popup-Stil jedes Schweregrads stehen auf der Seite Schweregrade.",
    severities_link: "Schweregrade",
    intro: "Wie jeder Kanal für alle Meldungen arbeitet. Wähle einen Kanal, um ihn zu ändern.",
    push: "Push",
    popup: "Popup",
    speech: "Sprache",
    severities: { success: "Erfolg", info: "Info", warning: "Warnung", critical: "Kritisch" },
    levels: { passive: "Passiv (kein Ton)", normal: "Normal", "time-sensitive": "Zeitkritisch", critical: "Kritisch (Alarm)" },
    styles: { card: "Ecke unten rechts", card_bottom_left: "Ecke unten links", card_top_right: "Ecke oben rechts", card_top_left: "Ecke oben links", modal: "Zentriertes Fenster", off: "Aus" },
    push_level: "Push-Stufe bei Schweregrad {severity}",
    popup_style: "Popup bei Schweregrad {severity}",
    critical_note: "Die Stufe kritisch ist auf beiden Plattformen ein Alarm. iOS: die kritische Mitteilung; sie braucht die Erlaubnis der App, spielt auch im Lautlosmodus einen Ton und kann nicht ersetzt oder gruppiert werden. Android: der Alarmkanal; er ertönt auch im Vibrations- und Lautlosmodus und wird sofort zugestellt. Nicht stören wird nur übergangen, wenn du es in den Android-Einstellungen für diesen Kanal erlaubst. Zeitkritisch wird auch auf Android sofort zugestellt.",
    ha_language_named: "Sprache von Home Assistant ({name})",
    no_engine_languages: "Wähle unter Einstellungen, Sprache eine Text-zu-Sprache-Engine, um aus ihren Sprachen zu wählen. Bis dahin gib einen Sprachcode wie de-DE ein oder lass das Feld leer für die Sprache von Home Assistant.",
    lockscreen: "Text auf dem Sperrbildschirm",
    lockscreens: { full: "Titel und Text", title_only: "Nur Titel", generic: "Allgemeiner Text" },
    buttons_note: "Schaltflächen: Später und Schließen. Bestätigen kommt hinzu, wenn eine Eskalations- oder Erinnerungsrichtlinie gilt.",
    sticky: "Benachrichtigung nach einem Tippen behalten (Android)",
    channel_id: "Android-Kanalname",
    channel_id_note: "Android behält die erste Wichtigkeit eines Kanals, darum hat jede Stufe einen eigenen Kanal namens <Name>_<Stufe>.",
    language: "Gesprochene Sprache",
    speech_note: "Sprache nutzt announce, wenn der Player es unterstützt. Die Lautstärke steht unter Einstellungen, Lautstärke der Sprache. Assist-Satelliten sprechen in der Sprache ihres eigenen Sprachassistenten.",
    save: "Speichern",
    saved: "Gespeichert.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    valid: "Keine Probleme.",
    bad_channel_id: "Der Kanalname besteht aus Kleinbuchstaben, Ziffern und Unterstrichen, höchstens 40 Zeichen.",
    mail: "E-Mail",
    mail_intro: "E-Mail ruft einen Benachrichtigungsdienst einmal pro Empfänger mit Betreff und Text auf. Die Adresse einer Person stellst du unter Empfänger ein; dort muss E-Mail für sie aktiviert sein.",
    mail_service: "Benachrichtigungsdienst",
    mail_service_none: "Keiner (E-Mail ist aus)",
    mail_global_address: "Globale Adresse",
    mail_global_note: "Optional. Nicht an eine Person gebunden: Nenne Global address als Empfänger, um dorthin zu senden. Sie ersetzt nie die Adresse einer Person.",
    mail_subject: "Betreff",
    mail_body: "Text",
    mail_placeholders: "Platzhalter: {severity} (zum Beispiel Kritisch), {title} (der Titel, sonst die Nachricht), {message}, {person} (der Name der Person, leer bei der globalen Adresse), {person_id} (der Teil der Entitäts-ID nach person., zum Beispiel philip; kleingeschrieben), {id}, {tag}.",
    bad_mail_subject: "Der Betreff braucht Text, höchstens 200 Zeichen, und darf nur die genannten Platzhalter nutzen.",
    bad_mail_body: "Der Text braucht Inhalt, höchstens 2000 Zeichen, und darf nur die genannten Platzhalter nutzen.",
    bad_mail_address: "Die Adresse darf höchstens 254 Zeichen lang sein.",
  },
  fr: {
    title: "Canaux",
    banner: "Bannière",
    banner_snooze: "Durées de report sur la bannière",
    banner_snooze_hint: "Utilisé quand un appel ou une règle de surveillance ne définit pas ses propres durées. La possibilité de reporter un message et les réglages de fermeture sont dans Réglages, Messages : ils valent pour la bannière, le push et le popup. L'apparence de la carte se règle dans les options de la carte.",
    snooze_time: "Durée de report sur le push et le popup (minutes)",
    snooze_time_hint: "1–1440. Le bouton Reporter du push et du popup reporte pour cette durée. C'est le même réglage sur les lignes Push et Popup.",
    bad_snooze_time: "La durée de report est un nombre entier de minutes de 1 à 1440.",
    snooze_summary: "Report {time}",
    styles_label: "Popup par gravité",
    styles_hint: "Réglé sur la page Gravités.",
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 heure", "120": "2 heures", "240": "4 heures", "480": "8 heures", "1440": "24 heures"},
    minutes_n: "{n} minutes",
    no_choices: "aucune durée de report",
    col_channel: "Canal",
    col_settings: "Réglages",
    sticky_on: "conservée après un appui",
    android: "Canal Android {id}",
    ha_language: "Langue de Home Assistant",
    mail_off: "Désactivé",
    global_to: "adresse globale {a}",
    edit: "Modifier {name}",
    changed: "modifié",
    severities_note: "Le niveau du push et le style du popup de chaque gravité se règlent sur la page Gravités.",
    severities_link: "Gravités",
    intro: "Le fonctionnement de chaque canal pour tous les messages. Choisissez un canal pour le modifier.",
    push: "Push",
    popup: "Fenêtre",
    speech: "Voix",
    severities: { success: "Succès", info: "Info", warning: "Avertissement", critical: "Critique" },
    levels: { passive: "Passif (sans son)", normal: "Normal", "time-sensitive": "Urgent", critical: "Critique (alarme)" },
    styles: { card: "Coin en bas à droite", card_bottom_left: "Coin en bas à gauche", card_top_right: "Coin en haut à droite", card_top_left: "Coin en haut à gauche", modal: "Fenêtre centrée", off: "Désactivé" },
    push_level: "Niveau du push quand la gravité est {severity}",
    popup_style: "Fenêtre quand la gravité est {severity}",
    critical_note: "Le niveau critique est une alarme sur les deux plateformes. iOS : l'alerte critique ; elle demande l'autorisation de l'app, joue un son même en mode silencieux et ne peut être ni remplacée ni groupée. Android : le canal d'alarme ; il sonne même en mode vibreur et silencieux et est livré tout de suite. Ne pas déranger n'est contourné que si vous l'autorisez pour ce canal dans les réglages d'Android. Urgent est aussi livré tout de suite sur Android.",
    ha_language_named: "Langue de Home Assistant ({name})",
    no_engine_languages: "Choisissez un moteur de synthèse vocale dans Réglages, Voix pour choisir parmi ses langues. En attendant, saisissez un code de langue comme fr-FR, ou laissez vide pour la langue de Home Assistant.",
    lockscreen: "Texte sur l'écran verrouillé",
    lockscreens: { full: "Titre et texte", title_only: "Titre seulement", generic: "Texte générique" },
    buttons_note: "Boutons : Reporter et Fermer. Confirmer s'ajoute quand une politique d'escalade ou de rappel s'applique.",
    sticky: "Garder la notification après un appui (Android)",
    channel_id: "Nom du canal Android",
    channel_id_note: "Android garde la première importance d'un canal, donc chaque niveau a son propre canal nommé <nom>_<niveau>.",
    language: "Langue parlée",
    speech_note: "La voix utilise announce quand le lecteur le permet. Le volume se règle dans Réglages, Volume de la voix. Les satellites Assist parlent dans la langue de leur propre assistant vocal.",
    save: "Enregistrer",
    saved: "Enregistré.",
    failed: "Enregistrement impossible. Réessayez.",
    valid: "Aucun problème.",
    bad_channel_id: "Le nom du canal utilise des minuscules, des chiffres et des tirets bas, 40 caractères au plus.",
    mail: "Courriel",
    mail_intro: "Le courriel appelle un service de notification une fois par destinataire avec un objet et un corps. L'adresse d'une personne se règle sous Destinataires, où Courriel doit être activé pour elle.",
    mail_service: "Service de notification",
    mail_service_none: "Aucun (courriel désactivé)",
    mail_global_address: "Adresse globale",
    mail_global_note: "Facultatif. Non liée à une personne : nommez Global address comme destinataire pour y envoyer. Elle ne remplace jamais l'adresse d'une personne.",
    mail_subject: "Objet",
    mail_body: "Corps",
    mail_placeholders: "Variables : {severity} (par exemple Critique), {title} (le titre, sinon le message), {message}, {person} (le nom de la personne, vide pour l'adresse globale), {person_id} (la partie de l'ID d'entité après person., par exemple philip ; en minuscules), {id}, {tag}.",
    bad_mail_subject: "L'objet a besoin de texte, 200 caractères au plus, et n'utilise que les variables listées.",
    bad_mail_body: "Le corps a besoin de texte, 2000 caractères au plus, et n'utilise que les variables listées.",
    bad_mail_address: "L'adresse peut avoir 254 caractères au plus.",
  },
  es: {
    title: "Canales",
    banner: "Aviso",
    banner_snooze: "Opciones de posposición en el aviso",
    banner_snooze_hint: "Se usa cuando una llamada o una regla de vigilancia no define sus propias opciones. Si un mensaje se puede posponer y los ajustes de cierre están en Ajustes, Mensajes: valen para aviso, push y ventana emergente. El aspecto de la tarjeta se ajusta en las opciones de la tarjeta.",
    snooze_time: "Tiempo de posposición en push y ventana emergente (minutos)",
    snooze_time_hint: "1–1440. El botón Posponer del push y de la ventana emergente pospone durante este tiempo. Es el mismo ajuste en las filas Push y Ventana.",
    bad_snooze_time: "El tiempo de posposición es un número entero de minutos de 1 a 1440.",
    snooze_summary: "Posponer {time}",
    styles_label: "Ventana por gravedad",
    styles_hint: "Se ajusta en la página Gravedades.",
    minutes: {"5": "5 minutos", "15": "15 minutos", "30": "30 minutos", "60": "1 hora", "120": "2 horas", "240": "4 horas", "480": "8 horas", "1440": "24 horas"},
    minutes_n: "{n} minutos",
    no_choices: "sin opciones de posposición",
    col_channel: "Canal",
    col_settings: "Ajustes",
    sticky_on: "se mantiene tras tocar",
    android: "Canal Android {id}",
    ha_language: "Idioma de Home Assistant",
    mail_off: "Desactivado",
    global_to: "dirección global {a}",
    edit: "Editar {name}",
    changed: "cambiado",
    severities_note: "El nivel del push y el estilo de la ventana de cada gravedad se ajustan en la página Gravedades.",
    severities_link: "Gravedades",
    intro: "Cómo funciona cada canal para todos los mensajes. Elige un canal para cambiarlo.",
    push: "Push",
    popup: "Ventana",
    speech: "Voz",
    severities: { success: "Éxito", info: "Info", warning: "Aviso", critical: "Crítico" },
    levels: { passive: "Pasivo (sin sonido)", normal: "Normal", "time-sensitive": "Urgente", critical: "Crítico (alarma)" },
    styles: { card: "Esquina inferior derecha", card_bottom_left: "Esquina inferior izquierda", card_top_right: "Esquina superior derecha", card_top_left: "Esquina superior izquierda", modal: "Ventana centrada", off: "Desactivado" },
    push_level: "Nivel del push cuando la gravedad es {severity}",
    popup_style: "Ventana cuando la gravedad es {severity}",
    critical_note: "El nivel crítico es una alarma en ambas plataformas. iOS: la alerta crítica; necesita el permiso de la app, suena incluso en modo silencio y no se puede reemplazar ni agrupar. Android: el canal de alarma; suena incluso en modo vibración y silencio y se entrega de inmediato. No molestar solo se anula si lo permites para ese canal en los ajustes de Android. Urgente también se entrega de inmediato en Android.",
    ha_language_named: "Idioma de Home Assistant ({name})",
    no_engine_languages: "Elige un motor de texto a voz en Ajustes, Voz para elegir entre sus idiomas. Mientras tanto, escribe un código de idioma como es-ES, o déjalo vacío para el idioma de Home Assistant.",
    lockscreen: "Texto en la pantalla de bloqueo",
    lockscreens: { full: "Título y texto", title_only: "Solo el título", generic: "Texto genérico" },
    buttons_note: "Botones: Posponer y Descartar. Confirmar se añade cuando se aplica una política de escalado o recordatorio.",
    sticky: "Mantener la notificación tras tocarla (Android)",
    channel_id: "Nombre del canal de Android",
    channel_id_note: "Android conserva la primera importancia de un canal, así que cada nivel tiene su propio canal llamado <nombre>_<nivel>.",
    language: "Idioma hablado",
    speech_note: "La voz usa announce cuando el reproductor lo admite. El volumen se ajusta en Ajustes, Volumen de la voz. Los satélites Assist hablan en el idioma de su propio asistente de voz.",
    save: "Guardar",
    saved: "Guardado.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    valid: "Sin problemas.",
    bad_channel_id: "El nombre del canal usa minúsculas, dígitos y guiones bajos, hasta 40 caracteres.",
    mail: "Correo",
    mail_intro: "El correo llama a un servicio de notificación una vez por destinatario con asunto y cuerpo. La dirección de una persona se define en Destinatarios, donde Correo debe estar activado para ella.",
    mail_service: "Servicio de notificación",
    mail_service_none: "Ninguno (correo desactivado)",
    mail_global_address: "Dirección global",
    mail_global_note: "Opcional. No ligada a una persona: nombra Global address como destinatario para enviar allí. Nunca sustituye la dirección de una persona.",
    mail_subject: "Asunto",
    mail_body: "Cuerpo",
    mail_placeholders: "Variables: {severity} (por ejemplo Crítico), {title} (el título, si no el mensaje), {message}, {person} (el nombre de la persona, vacío para la dirección global), {person_id} (la parte del ID de entidad después de person., por ejemplo philip; en minúsculas), {id}, {tag}.",
    bad_mail_subject: "El asunto necesita texto, hasta 200 caracteres, y solo puede usar las variables indicadas.",
    bad_mail_body: "El cuerpo necesita texto, hasta 2000 caracteres, y solo puede usar las variables indicadas.",
    bad_mail_address: "La dirección puede tener 254 caracteres como máximo.",
  },
};

const SEVERITIES = ["success", "info", "warning", "critical"];
const LEVELS = ["passive", "normal", "time-sensitive", "critical"];
const STYLES = ["card", "card_bottom_left", "card_top_right", "card_top_left", "modal", "off"];
const LOCKSCREENS = ["full", "title_only", "generic"];

// The channels the page lists, the settings each one owns and its icon.
const CHANNELS = [
  { key: "banner", icon: "mdi:card-text-outline", keys: [], settings: ["default_snooze_options"] },
  { key: "push", icon: "mdi:cellphone-message", keys: ["push_lockscreen", "push_channel_id", "push_sticky"], settings: ["quick_snooze_minutes"] },
  { key: "popup", icon: "mdi:dock-window", keys: [], settings: ["quick_snooze_minutes"] },
  { key: "speech", icon: "mdi:account-voice", keys: ["speak_language"], settings: [] },
  { key: "mail", icon: "mdi:email-outline", keys: ["mail_service", "mail_global_address", "mail_subject", "mail_body"], settings: [] },
];

// The two snooze settings these rows show are stored with the other settings (heads_up/settings_set).
export const SETTING_KEYS = ["default_snooze_options", "quick_snooze_minutes"];
const SNOOZE_MINUTES = [5, 15, 30, 60, 120, 240, 480, 1440];
const SEVERITY_ORDER = ["critical", "warning", "info", "success"];

export function minutesText(n, t) {
  return t.minutes[String(n)] || fill(t.minutes_n, { n });
}

// Popup styles grouped: "Centered window (Critical) · Corner, bottom right (Warning, Info, Success)".
export function stylesText(styles, t) {
  const groups = new Map();
  for (const severity of SEVERITY_ORDER) {
    const style = (styles || {})[severity];
    if (!style) continue;
    groups.set(style, [...(groups.get(style) || []), t.severities[severity] || severity]);
  }
  return [...groups].map(([style, names]) => `${t.styles[style] || style} (${names.join(", ")})`).join(" · ");
}

export function settingProblems(settings) {
  const time = settings.quick_snooze_minutes;
  return Number.isInteger(time) && time >= 1 && time <= 1440 ? [] : ["bad_snooze_time"];
}

export function settingChanges(settings, saved) {
  const out = {};
  for (const key of SETTING_KEYS) if (JSON.stringify(settings[key]) !== JSON.stringify(saved[key])) out[key] = settings[key];
  return out;
}

// "German (Germany) · de-DE" in the panel's language; the code alone where the browser cannot name it.
export function languageName(code, language) {
  try {
    const name = new Intl.DisplayNames([language || "en"], { type: "language" }).of(code);
    return name && name !== code ? `${name} · ${code}` : code;
  } catch (err) {
    return code;
  }
}

// The choices of the spoken language: the Home Assistant language first, then the engine's
// languages by name. A saved value the engine does not list stays selectable.
export function languageOptions(supported, current, haLanguage, language, t) {
  const codes = [...new Set([...(supported || []), ...(current ? [current] : [])])];
  const named = codes.map((code) => ({ value: code, label: languageName(code, language) })).sort((a, b) => a.label.localeCompare(b.label, language));
  return [{ value: "", label: fill(t.ha_language_named, { name: languageName(haLanguage, language) }) }, ...named];
}

// The overview line of a channel: what a reader needs to know without opening it.
export function summaryText(key, values, t, language, settings = {}) {
  if (key === "banner") {
    const choices = settings.default_snooze_options || [];
    return choices.length ? fill(t.snooze_summary, { time: choices.map((m) => minutesText(m, t)).join(", ") }) : t.no_choices;
  }
  if (key === "popup") {
    return [settings.quick_snooze_minutes ? fill(t.snooze_summary, { time: minutesText(settings.quick_snooze_minutes, t) }) : "", stylesText(values.popup_styles, t)].filter(Boolean).join(" · ");
  }
  if (key === "push") {
    return [t.lockscreens[values.push_lockscreen] || values.push_lockscreen, fill(t.android, { id: values.push_channel_id || "" }), values.push_sticky ? t.sticky_on : ""].filter(Boolean).join(" · ");
  }
  if (key === "speech") {
    const code = String(values.speak_language || "").trim();
    return code ? languageName(code, language) : t.ha_language;
  }
  if (!values.mail_service) return t.mail_off;
  const address = String(values.mail_global_address || "").trim();
  return [`notify.${values.mail_service}`, address ? fill(t.global_to, { a: address }) : ""].filter(Boolean).join(" · ");
}

const PAGE_CSS = `
.hu-page .tl-list { --tl-cols: minmax(0, 1fr) minmax(0, 2.4fr); }
.hu-page .tl-lead ha-icon { color: var(--secondary-text-color); }
.hu-page .tl-body .tl-wide label.field { margin: 0; }
.hu-page .tl-body .tl-wide label.inline { min-height: 44px; }
.hu-page .ch-lang { max-width: 460px; }
.hu-page .ch-chips fieldset { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); column-gap: 12px; margin: 0; }
.hu-page .ch-chips label.inline { min-height: 40px; }
.hu-page .ch-sub { font-size: 14px; margin: 4px 0 8px; }
.hu-page .ch-go { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.hu-page .ch-go .hint { margin: 0; }
.hu-page .ch-note { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; margin: 0 0 8px; }
.hu-page .ch-note .hint { margin: 0; flex: 1; min-width: 200px; }
`;

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function validChannelId(value) {
  return /^[a-z0-9_]{1,40}$/.test(String(value || ""));
}

// What changed against the saved settings: only those keys are sent.
export function changes(values, saved) {
  const out = {};
  for (const key of Object.keys(saved)) {
    if (JSON.stringify(values[key]) !== JSON.stringify(saved[key])) out[key] = values[key];
  }
  return out;
}

export const MAIL_PLACEHOLDERS = ["severity", "title", "message", "person", "id", "tag"];

// A mail template needs text within the limit and may use only the known placeholders.
export function validMailTemplate(text, limit) {
  const value = String(text ?? "");
  if (!value.trim() || value.length > limit) return false;
  return [...value.matchAll(/\{(\w*)\}/g)].every((m) => MAIL_PLACEHOLDERS.includes(m[1]));
}

export function problems(values) {
  const found = [];
  if (!validChannelId(values.push_channel_id)) found.push("bad_channel_id");
  if (values.mail_subject !== undefined && !validMailTemplate(values.mail_subject, 200)) found.push("bad_mail_subject");
  if (values.mail_body !== undefined && !validMailTemplate(values.mail_body, 2000)) found.push("bad_mail_body");
  if (String(values.mail_global_address ?? "").trim().length > 254) found.push("bad_mail_address");
  return found;
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let values = null;
  let message = "";
  let open = null;
  let languages = null;
  let settings = {};
  let savedSettings = {};
  let paint = () => {};
  const root = el("div", { className: "hu-page" });
  container.append(root);

  // One row per channel with a summary of its settings; a row opens its fields underneath.
  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + ui.TABLE_CSS + PAGE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    const list = el("section", { className: "tl-list" }, [ui.tableHead([t.col_channel, t.col_settings])]);
    const rows = [];
    for (const channel of CHANNELS) {
      const id = `hu-ch-${channel.key}`;
      const isOpen = open === channel.key;
      const summary = el("span");
      const mark = el("span", { className: "tl-mark" });
      const body = isOpen ? el("div") : null;
      const { item, row } = ui.tableRow({
        id,
        lead: [el("ha-icon", { icon: channel.icon }), el("span", { className: "tl-name", textContent: t[channel.key] })],
        cells: [{ label: "", node: summary }],
        end: [mark],
        open: isOpen,
        onToggle: () => {
          open = isOpen ? null : channel.key;
          render();
          root.querySelector(`[aria-controls="${id}"]`)?.focus();
        },
        body,
      });
      if (body) body.append(fields(channel.key));
      rows.push(() => {
        summary.textContent = summaryText(channel.key, values, t, ctx.language, settings);
        const changed = channel.keys.some((k) => JSON.stringify(values[k]) !== JSON.stringify(data.channels[k])) || channel.settings.some((k) => JSON.stringify(settings[k]) !== JSON.stringify(savedSettings[k]));
        mark.textContent = changed ? "●" : "";
        row.setAttribute("aria-label", `${fill(t.edit, { name: t[channel.key] })}: ${summary.textContent}${changed ? `, ${t.changed}` : ""}`);
      });
      list.append(item);
    }
    root.append(list);
    // The push level and the popup style of each severity are on the Severities page (D-222).
    const toSeverities = el("button", { type: "button", textContent: t.severities_link });
    toSeverities.addEventListener("click", () => ctx.navigate("severities"));
    root.append(el("div", { className: "ch-note" }, [el("span", { className: "hint", textContent: t.severities_note }), toSeverities]));
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveIt);
    const bar = el("div", { className: "tl-bar" }, [save, status]);
    root.append(bar);
    paint = () => {
      for (const update of rows) update();
      const found = [...problems(values), ...settingProblems(settings)];
      const dirty = Object.keys(changes(values, data.channels)).length > 0 || Object.keys(settingChanges(settings, savedSettings)).length > 0;
      save.disabled = found.length > 0 || !dirty;
      bar.classList.toggle("dirty", dirty);
      status.className = found.length ? "hint problems" : "hint ok";
      status.textContent = found.length ? found.map((c) => t[c]).join(" ") : message || (dirty ? t.valid : "");
    };
    paint();
  }

  function fields(key) {
    const box = el("div", { className: "tl-grid" });
    const hint = (text) => el("div", { className: "hint tl-wide", textContent: text });
    const snoozeTime = () => ui.field(t.snooze_time, ui.numberInput(settings.quick_snooze_minutes, (v) => { settings.quick_snooze_minutes = v; paint(); }, { min: 1, max: 1440 }), t.snooze_time_hint);
    if (key === "banner") {
      box.append(el("div", { className: "tl-wide ch-chips" }, [ui.chips(t.banner_snooze, SNOOZE_MINUTES.map((m) => ({ value: m, label: minutesText(m, t) })), settings.default_snooze_options || [], (list) => { settings.default_snooze_options = SNOOZE_MINUTES.filter((m) => list.includes(m)); paint(); })]));
      box.append(hint(t.banner_snooze_hint));
      return box;
    }
    if (key === "popup") {
      box.append(snoozeTime());
      const styles = ui.facts(SEVERITY_ORDER.map((sev) => [t.severities[sev], t.styles[values.popup_styles?.[sev]] || values.popup_styles?.[sev] || "–"]));
      const go = el("button", { type: "button", textContent: t.severities_link });
      go.addEventListener("click", () => ctx.navigate("severities"));
      box.append(el("div", { className: "tl-wide" }, [el("div", { className: "ch-sub", textContent: t.styles_label }), styles, el("div", { className: "ch-go" }, [el("span", { className: "hint", textContent: t.styles_hint }), go])]));
      return box;
    }
    if (key === "push") {
      box.append(snoozeTime());
      box.append(ui.field(t.lockscreen, ui.selectInput(LOCKSCREENS.map((l) => ({ value: l, label: t.lockscreens[l] })), values.push_lockscreen, (v) => { values.push_lockscreen = v; paint(); })));
      box.append(ui.field(t.channel_id, ui.textInput(values.push_channel_id, (v) => { values.push_channel_id = v; paint(); }, { spellcheck: false, autocapitalize: "off" })));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.sticky, values.push_sticky, (on) => { values.push_sticky = on; paint(); })]));
      box.append(hint(t.channel_id_note), hint(t.buttons_note));
    } else if (key === "speech") {
      if (languages?.length) {
        const options = languageOptions(languages, values.speak_language, hass?.config?.language || "en", ctx.language, t);
        box.append(el("div", { className: "tl-wide ch-lang" }, [ui.field(t.language, ui.selectInput(options, values.speak_language || "", (v) => { values.speak_language = v; paint(); }))]));
      } else {
        box.append(ui.field(t.language, ui.textInput(values.speak_language, (v) => { values.speak_language = v; paint(); }, { placeholder: hass?.config?.language || "", spellcheck: false, autocapitalize: "off" }), t.no_engine_languages));
      }
      box.append(hint(t.speech_note));
    } else {
      const services = [...(data.choices?.notify_services || [])];
      if (values.mail_service && !services.includes(values.mail_service)) services.push(values.mail_service);
      box.append(hint(t.mail_intro));
      box.append(ui.field(t.mail_service, ui.selectInput([{ value: "", label: t.mail_service_none }, ...services.map((n) => ({ value: n, label: `notify.${n}` }))], values.mail_service, (v) => { values.mail_service = v; paint(); })));
      box.append(ui.field(t.mail_global_address, ui.textInput(values.mail_global_address, (v) => { values.mail_global_address = v; paint(); }, { inputMode: "email", autocapitalize: "off", spellcheck: false }), t.mail_global_note));
      box.append(el("div", { className: "tl-wide" }, [ui.field(t.mail_subject, ui.textInput(values.mail_subject, (v) => { values.mail_subject = v; paint(); }))]));
      box.append(el("div", { className: "tl-wide" }, [ui.field(t.mail_body, ui.textInput(values.mail_body, (v) => { values.mail_body = v; paint(); }))]));
      box.append(hint(t.mail_placeholders));
    }
    return box;
  }

  async function saveIt() {
    try {
      const own = changes(values, data.channels);
      if (Object.keys(own).length) {
        const result = await hass.callWS({ type: "heads_up/channels_set", ...own });
        data.channels = result;
        values = JSON.parse(JSON.stringify(result));
      }
      const shared = settingChanges(settings, savedSettings);
      if (Object.keys(shared).length) {
        const stored = (await hass.callWS({ type: "heads_up/settings_set", ...shared })).options || {};
        savedSettings = Object.fromEntries(SETTING_KEYS.map((k) => [k, stored[k]]));
        settings = JSON.parse(JSON.stringify(savedSettings));
      }
      message = t.saved;
    } catch (err) {
      message = t.failed;
    }
    render();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    const stored = (await hass.callWS({ type: "heads_up/settings_get" })).options || {};
    savedSettings = Object.fromEntries(SETTING_KEYS.map((k) => [k, stored[k]]));
    settings = JSON.parse(JSON.stringify(savedSettings));
    // The languages of the engine speech uses (N-108); without one the field stays free text.
    const engine = data.choices?.tts_engine;
    if (engine) {
      try {
        languages = (await hass.callWS({ type: "tts/engine/get", engine_id: engine })).provider?.supported_languages || null;
      } catch (err) {
        languages = null;
      }
    }
    values = JSON.parse(JSON.stringify(data.channels));
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
