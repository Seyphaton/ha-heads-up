// Heads Up panel: Channels page (D-119): settings of push, popup and speech by severity.

export const STRINGS = {
  en: {
    title: "Channels",
    intro: "How each channel looks and sounds, by severity. These settings apply to every message.",
    push: "Push",
    popup: "Popup",
    speech: "Speech",
    severities: { success: "Success", info: "Info", warning: "Warning", critical: "Critical" },
    levels: { passive: "Passive (no sound)", normal: "Normal", "time-sensitive": "Time sensitive", critical: "Critical (iOS)" },
    styles: { card: "Card in the corner", modal: "Centered window", off: "Off" },
    push_level: "Push level when the severity is {severity}",
    popup_style: "Popup when the severity is {severity}",
    ios_note: "The level critical is the iOS critical level: it needs the app's permission, plays a sound even in silent mode and cannot be replaced or grouped. Android receives it as time sensitive.",
    lockscreen: "Lock-screen text",
    lockscreens: { full: "Title and text", title_only: "Title only", generic: "Generic text" },
    buttons_note: "Buttons: Snooze and Dismiss. Acknowledge is added when an escalation or reminder policy applies.",
    sticky: "Keep the notification after a tap (Android)",
    channel_id: "Android channel name",
    channel_id_note: "Android keeps the first importance of a channel, so each level has its own channel named <name>_<level>.",
    language: "Spoken language (empty: the Home Assistant language)",
    speech_note: "Speech uses announce when the player supports it and never changes or restores a volume.",
    save: "Save",
    saved: "Saved.",
    failed: "Could not save. Try again.",
    valid: "No problems.",
    hub_off: "The hub is switched off. Switch it on in Settings to edit this.",
    bad_channel_id: "The channel name uses lower-case letters, digits and underscores, up to 40 characters.",
  },
  de: {
    title: "Kanäle",
    intro: "Wie jeder Kanal aussieht und klingt, nach Schweregrad. Diese Einstellungen gelten für alle Meldungen.",
    push: "Push",
    popup: "Popup",
    speech: "Sprache",
    severities: { success: "Erfolg", info: "Info", warning: "Warnung", critical: "Kritisch" },
    levels: { passive: "Passiv (kein Ton)", normal: "Normal", "time-sensitive": "Zeitkritisch", critical: "Kritisch (iOS)" },
    styles: { card: "Karte in der Ecke", modal: "Zentriertes Fenster", off: "Aus" },
    push_level: "Push-Stufe bei Schweregrad {severity}",
    popup_style: "Popup bei Schweregrad {severity}",
    ios_note: "Die Stufe kritisch ist die kritische Stufe von iOS: Sie braucht die Erlaubnis der App, spielt auch im Lautlosmodus einen Ton und kann nicht ersetzt oder gruppiert werden. Android erhält sie als zeitkritisch.",
    lockscreen: "Text auf dem Sperrbildschirm",
    lockscreens: { full: "Titel und Text", title_only: "Nur Titel", generic: "Allgemeiner Text" },
    buttons_note: "Schaltflächen: Später und Schließen. Bestätigen kommt hinzu, wenn eine Eskalations- oder Erinnerungsrichtlinie gilt.",
    sticky: "Benachrichtigung nach einem Tippen behalten (Android)",
    channel_id: "Android-Kanalname",
    channel_id_note: "Android behält die erste Wichtigkeit eines Kanals, darum hat jede Stufe einen eigenen Kanal namens <Name>_<Stufe>.",
    language: "Sprache der Ansage (leer: die Sprache von Home Assistant)",
    speech_note: "Die Sprachausgabe nutzt Announce, wenn der Player es kann, und ändert oder stellt nie eine Lautstärke wieder her.",
    save: "Speichern",
    saved: "Gespeichert.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    valid: "Keine Probleme.",
    hub_off: "Der Hub ist ausgeschaltet. Schalte ihn in den Einstellungen ein, um dies zu bearbeiten.",
    bad_channel_id: "Der Kanalname besteht aus Kleinbuchstaben, Ziffern und Unterstrichen, höchstens 40 Zeichen.",
  },
  fr: {
    title: "Canaux",
    intro: "L'apparence et le son de chaque canal, par gravité. Ces réglages s'appliquent à tous les messages.",
    push: "Push",
    popup: "Fenêtre",
    speech: "Voix",
    severities: { success: "Succès", info: "Info", warning: "Avertissement", critical: "Critique" },
    levels: { passive: "Passif (sans son)", normal: "Normal", "time-sensitive": "Urgent", critical: "Critique (iOS)" },
    styles: { card: "Carte dans le coin", modal: "Fenêtre centrée", off: "Désactivé" },
    push_level: "Niveau du push quand la gravité est {severity}",
    popup_style: "Fenêtre quand la gravité est {severity}",
    ios_note: "Le niveau critique est le niveau critique d'iOS : il demande l'autorisation de l'app, joue un son même en mode silencieux et ne peut être ni remplacé ni groupé. Android le reçoit comme urgent.",
    lockscreen: "Texte sur l'écran verrouillé",
    lockscreens: { full: "Titre et texte", title_only: "Titre seulement", generic: "Texte générique" },
    buttons_note: "Boutons : Reporter et Fermer. Confirmer s'ajoute quand une politique d'escalade ou de rappel s'applique.",
    sticky: "Garder la notification après un appui (Android)",
    channel_id: "Nom du canal Android",
    channel_id_note: "Android garde la première importance d'un canal, donc chaque niveau a son propre canal nommé <nom>_<niveau>.",
    language: "Langue parlée (vide : la langue de Home Assistant)",
    speech_note: "La voix utilise announce quand le lecteur le permet et ne change ni ne rétablit jamais un volume.",
    save: "Enregistrer",
    saved: "Enregistré.",
    failed: "Enregistrement impossible. Réessayez.",
    valid: "Aucun problème.",
    hub_off: "Le hub est désactivé. Activez-le dans Réglages pour modifier ceci.",
    bad_channel_id: "Le nom du canal utilise des minuscules, des chiffres et des tirets bas, 40 caractères au plus.",
  },
  es: {
    title: "Canales",
    intro: "Cómo se ve y suena cada canal, según la gravedad. Estos ajustes valen para todos los mensajes.",
    push: "Push",
    popup: "Ventana",
    speech: "Voz",
    severities: { success: "Éxito", info: "Info", warning: "Aviso", critical: "Crítico" },
    levels: { passive: "Pasivo (sin sonido)", normal: "Normal", "time-sensitive": "Urgente", critical: "Crítico (iOS)" },
    styles: { card: "Tarjeta en la esquina", modal: "Ventana centrada", off: "Desactivado" },
    push_level: "Nivel del push cuando la gravedad es {severity}",
    popup_style: "Ventana cuando la gravedad es {severity}",
    ios_note: "El nivel crítico es el nivel crítico de iOS: necesita el permiso de la app, suena incluso en modo silencio y no se puede reemplazar ni agrupar. Android lo recibe como urgente.",
    lockscreen: "Texto en la pantalla de bloqueo",
    lockscreens: { full: "Título y texto", title_only: "Solo el título", generic: "Texto genérico" },
    buttons_note: "Botones: Posponer y Descartar. Confirmar se añade cuando se aplica una política de escalado o recordatorio.",
    sticky: "Mantener la notificación tras tocarla (Android)",
    channel_id: "Nombre del canal de Android",
    channel_id_note: "Android conserva la primera importancia de un canal, así que cada nivel tiene su propio canal llamado <nombre>_<nivel>.",
    language: "Idioma hablado (vacío: el idioma de Home Assistant)",
    speech_note: "La voz usa announce cuando el reproductor lo permite y nunca cambia ni restaura un volumen.",
    save: "Guardar",
    saved: "Guardado.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    valid: "Sin problemas.",
    hub_off: "El hub está desactivado. Actívalo en Ajustes para editar esto.",
    bad_channel_id: "El nombre del canal usa minúsculas, dígitos y guiones bajos, hasta 40 caracteres.",
  },
};

const SEVERITIES = ["success", "info", "warning", "critical"];
const LEVELS = ["passive", "normal", "time-sensitive", "critical"];
const STYLES = ["card", "modal", "off"];
const LOCKSCREENS = ["full", "title_only", "generic"];

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

export function problems(values) {
  return validChannelId(values.push_channel_id) ? [] : ["bad_channel_id"];
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let values = null;
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    if (!data.hub) {
      root.append(el("div", { className: "hint", textContent: t.hub_off }));
      return;
    }
    root.append(el("div", { className: "hint", textContent: t.intro }));
    const push = el("section", {}, [el("h2", { textContent: t.push })]);
    for (const severity of SEVERITIES) {
      push.append(
        ui.field(
          fill(t.push_level, { severity: t.severities[severity] }),
          ui.selectInput(LEVELS.map((l) => ({ value: l, label: t.levels[l] })), values.push_levels[severity], (v) => { values.push_levels[severity] = v; paint(); }),
        ),
      );
    }
    push.append(el("div", { className: "hint", textContent: t.ios_note }));
    push.append(ui.field(t.lockscreen, ui.selectInput(LOCKSCREENS.map((l) => ({ value: l, label: t.lockscreens[l] })), values.push_lockscreen, (v) => { values.push_lockscreen = v; paint(); })));
    push.append(el("div", { className: "hint", textContent: t.buttons_note }));
    push.append(ui.checkbox(t.sticky, values.push_sticky, (on) => { values.push_sticky = on; paint(); }));
    push.append(ui.field(t.channel_id, ui.textInput(values.push_channel_id, (v) => { values.push_channel_id = v; paint(); }), t.channel_id_note));
    const popup = el("section", {}, [el("h2", { textContent: t.popup })]);
    for (const severity of SEVERITIES) {
      popup.append(
        ui.field(
          fill(t.popup_style, { severity: t.severities[severity] }),
          ui.selectInput(STYLES.map((x) => ({ value: x, label: t.styles[x] })), values.popup_styles[severity], (v) => { values.popup_styles[severity] = v; paint(); }),
        ),
      );
    }
    const speech = el("section", {}, [el("h2", { textContent: t.speech })]);
    speech.append(ui.field(t.language, ui.textInput(values.speak_language, (v) => { values.speak_language = v; paint(); })));
    speech.append(el("div", { className: "hint", textContent: t.speech_note }));
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveIt);
    root.append(push, popup, speech, save, status);
    function paint() {
      const found = problems(values);
      const dirty = Object.keys(changes(values, data.channels)).length > 0;
      save.disabled = found.length > 0 || !dirty;
      status.className = found.length ? "hint problems" : "hint ok";
      status.textContent = found.length ? found.map((c) => t[c]).join(" ") : message || (dirty ? t.valid : "");
    }
    paint();
  }

  async function saveIt() {
    try {
      const result = await hass.callWS({ type: "heads_up/channels_set", ...changes(values, data.channels) });
      message = t.saved;
      data.channels = result;
      values = JSON.parse(JSON.stringify(result));
    } catch (err) {
      message = t.failed;
    }
    render();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
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
