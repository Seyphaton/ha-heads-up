// Heads Up panel: Severities page (D-222, D-223): label, icon and color of each severity, and its
// push level and popup style. Saved through the same command as the Channels page.

export const STRINGS = {
  "en": {
    "title": "Severities",
    "intro": "What each severity looks like everywhere (card, popup, panel, mail) and how it sounds on push and popup. YAML, events and automations keep the names success, info, warning and critical.",
    "label": "Label (empty: {name})",
    "icon": "Icon (empty: the default)",
    "color": "Color (CSS color or theme variable, empty: the theme)",
    "push_level": "Push level",
    "popup_style": "Popup",
    "save": "Save",
    "saved": "Saved.",
    "failed": "Could not save. Try again.",
    "valid": "No problems.",
    "bad_display": "A label has at most 30 characters, an icon looks like mdi:alarm-light and a color like #d00000 or var(--error-color).",
    "same_icon": "Two severities have the same icon: they then differ only by color and label.",
    "levels": {
      "passive": "Passive (no sound)",
      "normal": "Normal",
      "time-sensitive": "Time sensitive",
      "critical": "Critical (alarm)"
    },
    "styles": {
      "card": "Corner, bottom right",
      "card_bottom_left": "Corner, bottom left",
      "card_top_right": "Corner, top right",
      "card_top_left": "Corner, top left",
      "modal": "Centered window",
      "off": "Off"
    },
    "critical_note": "The level critical is an alarm on both platforms. iOS: the critical alert; it needs the app's permission, plays a sound even in silent mode and cannot be replaced or grouped. Android: the alarm channel; it sounds even in vibrate and silent mode and is delivered at once. Do Not Disturb is only overridden if you allow it for that channel in the Android settings. Time sensitive is delivered at once on Android too.",
    "severities": {
      "success": "Success",
      "info": "Info",
      "warning": "Warning",
      "critical": "Critical"
    }
  },
  "de": {
    "title": "Schweregrade",
    "intro": "Wie jeder Schweregrad überall aussieht (Karte, Popup, Panel, Mail) und wie er bei Push und Popup klingt. YAML, Ereignisse und Automationen behalten die Namen success, info, warning und critical.",
    "label": "Bezeichnung (leer: {name})",
    "icon": "Symbol (leer: Standard)",
    "color": "Farbe (CSS-Farbe oder Theme-Variable, leer: das Theme)",
    "push_level": "Push-Stufe",
    "popup_style": "Popup",
    "save": "Speichern",
    "saved": "Gespeichert.",
    "failed": "Speichern fehlgeschlagen. Bitte erneut versuchen.",
    "valid": "Keine Probleme.",
    "bad_display": "Eine Bezeichnung hat höchstens 30 Zeichen, ein Symbol sieht aus wie mdi:alarm-light und eine Farbe wie #d00000 oder var(--error-color).",
    "same_icon": "Zwei Schweregrade haben dasselbe Symbol: Sie unterscheiden sich dann nur durch Farbe und Bezeichnung.",
    "levels": {
      "passive": "Passiv (kein Ton)",
      "normal": "Normal",
      "time-sensitive": "Zeitkritisch",
      "critical": "Kritisch (Alarm)"
    },
    "styles": {
      "card": "Ecke unten rechts",
      "card_bottom_left": "Ecke unten links",
      "card_top_right": "Ecke oben rechts",
      "card_top_left": "Ecke oben links",
      "modal": "Zentriertes Fenster",
      "off": "Aus"
    },
    "critical_note": "Die Stufe kritisch ist auf beiden Plattformen ein Alarm. iOS: die kritische Mitteilung; sie braucht die Erlaubnis der App, spielt auch im Lautlosmodus einen Ton und kann nicht ersetzt oder gruppiert werden. Android: der Alarmkanal; er ertönt auch im Vibrations- und Lautlosmodus und wird sofort zugestellt. Nicht stören wird nur übergangen, wenn du es in den Android-Einstellungen für diesen Kanal erlaubst. Zeitkritisch wird auch auf Android sofort zugestellt.",
    "severities": {
      "success": "Erfolg",
      "info": "Info",
      "warning": "Warnung",
      "critical": "Kritisch"
    }
  },
  "fr": {
    "title": "Gravités",
    "intro": "L'apparence de chaque gravité partout (carte, popup, panneau, courriel) et son son sur le push et le popup. Le YAML, les événements et les automatisations gardent les noms success, info, warning et critical.",
    "label": "Libellé (vide : {name})",
    "icon": "Icône (vide : par défaut)",
    "color": "Couleur (couleur CSS ou variable de thème, vide : le thème)",
    "push_level": "Niveau du push",
    "popup_style": "Popup",
    "save": "Enregistrer",
    "saved": "Enregistré.",
    "failed": "Échec de l'enregistrement. Réessayez.",
    "valid": "Aucun problème.",
    "bad_display": "Un libellé a 30 caractères au plus, une icône ressemble à mdi:alarm-light et une couleur à #d00000 ou var(--error-color).",
    "same_icon": "Deux gravités ont la même icône : elles ne diffèrent alors que par la couleur et le libellé.",
    "levels": {
      "passive": "Passif (sans son)",
      "normal": "Normal",
      "time-sensitive": "Urgent",
      "critical": "Critique (alarme)"
    },
    "styles": {
      "card": "Coin en bas à droite",
      "card_bottom_left": "Coin en bas à gauche",
      "card_top_right": "Coin en haut à droite",
      "card_top_left": "Coin en haut à gauche",
      "modal": "Fenêtre centrée",
      "off": "Désactivé"
    },
    "critical_note": "Le niveau critique est une alarme sur les deux plateformes. iOS : l'alerte critique ; elle demande l'autorisation de l'app, joue un son même en mode silencieux et ne peut être ni remplacée ni groupée. Android : le canal d'alarme ; il sonne même en mode vibreur et silencieux et est livré tout de suite. Ne pas déranger n'est contourné que si vous l'autorisez pour ce canal dans les réglages d'Android. Urgent est aussi livré tout de suite sur Android.",
    "severities": {
      "success": "Succès",
      "info": "Info",
      "warning": "Avertissement",
      "critical": "Critique"
    }
  },
  "es": {
    "title": "Gravedades",
    "intro": "Cómo se ve cada gravedad en todas partes (tarjeta, ventana, panel, correo) y cómo suena en push y ventana. El YAML, los eventos y las automatizaciones mantienen los nombres success, info, warning y critical.",
    "label": "Etiqueta (vacío: {name})",
    "icon": "Icono (vacío: el predeterminado)",
    "color": "Color (color CSS o variable del tema, vacío: el tema)",
    "push_level": "Nivel del push",
    "popup_style": "Ventana",
    "save": "Guardar",
    "saved": "Guardado.",
    "failed": "No se pudo guardar. Inténtalo de nuevo.",
    "valid": "Sin problemas.",
    "bad_display": "Una etiqueta tiene como máximo 30 caracteres, un icono se parece a mdi:alarm-light y un color a #d00000 o var(--error-color).",
    "same_icon": "Dos gravedades tienen el mismo icono: entonces solo se distinguen por el color y la etiqueta.",
    "levels": {
      "passive": "Pasivo (sin sonido)",
      "normal": "Normal",
      "time-sensitive": "Urgente",
      "critical": "Crítico (alarma)"
    },
    "styles": {
      "card": "Esquina inferior derecha",
      "card_bottom_left": "Esquina inferior izquierda",
      "card_top_right": "Esquina superior derecha",
      "card_top_left": "Esquina superior izquierda",
      "modal": "Ventana centrada",
      "off": "Desactivado"
    },
    "critical_note": "El nivel crítico es una alarma en ambas plataformas. iOS: la alerta crítica; necesita el permiso de la app, suena incluso en modo silencio y no se puede reemplazar ni agrupar. Android: el canal de alarma; suena incluso en modo vibración y silencio y se entrega de inmediato. No molestar solo se anula si lo permites para ese canal en los ajustes de Android. Urgente también se entrega de inmediato en Android.",
    "severities": {
      "success": "Éxito",
      "info": "Info",
      "warning": "Aviso",
      "critical": "Crítico"
    }
  }
};

export const SEVERITIES = ["critical", "warning", "info", "success"];
const LEVELS = ["passive", "normal", "time-sensitive", "critical"];
const STYLES = ["card", "card_bottom_left", "card_top_right", "card_top_left", "modal", "off"];
const DEFAULT_ICONS = { critical: "mdi:alert-octagon", warning: "mdi:alert", info: "mdi:information", success: "mdi:check-circle" };
const ICON = /^mdi:[a-z0-9-]+$/;
const COLOR = /^(#[0-9a-fA-F]{3,8}|var\(--[a-z0-9-]+\)|[a-z]+|rgba?\([0-9., %]+\))$/;

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value), template);
}

// The keys of the Channels settings this page edits.
export const KEYS = ["severity_display", "push_levels", "popup_styles"];

// What differs from the saved values; only those keys are sent.
export function changes(values, saved) {
  const out = {};
  for (const key of KEYS) {
    const now = key === "severity_display" ? cleanDisplay(values[key]) : values[key] ?? {};
    const before = key === "severity_display" ? cleanDisplay(saved[key]) : saved[key] ?? {};
    if (JSON.stringify(now) !== JSON.stringify(before)) out[key] = now;
  }
  return out;
}

// Only what is set: empty texts and severities without anything set are left out.
export function cleanDisplay(display) {
  const out = {};
  for (const severity of SEVERITIES) {
    const kept = Object.fromEntries(Object.entries((display || {})[severity] || {}).map(([k, v]) => [k, String(v ?? "").trim()]).filter(([, v]) => v));
    if (Object.keys(kept).length) out[severity] = kept;
  }
  return out;
}

// Problems as codes: an invalid label, icon or color; the same icon on two severities is a warning.
export function problems(values) {
  const errors = [];
  const warnings = [];
  const display = values.severity_display || {};
  for (const shown of Object.values(display)) {
    const label = String(shown.label || "");
    const icon = String(shown.icon || "");
    const color = String(shown.color || "");
    if (label.length > 30 || (icon && !ICON.test(icon)) || (color && !COLOR.test(color))) errors.push("bad_display");
  }
  const icons = SEVERITIES.map((s) => (display[s] || {}).icon || DEFAULT_ICONS[s]);
  if (new Set(icons).size < icons.length) warnings.push("same_icon");
  return { errors: [...new Set(errors)], warnings };
}

export function mount(container, ctx) {
  const t = ctx.t;
  const { ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let values = null;
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    values.severity_display ||= {};
    for (const severity of SEVERITIES) {
      const shown = (values.severity_display[severity] ||= {});
      const set = (key) => (v) => {
        shown[key] = v;
        paint();
      };
      const box = el("section", {}, [el("h2", { textContent: shown.label || t.severities[severity] })]);
      box.append(ui.field(fill(t.label, { name: t.severities[severity] }), ui.textInput(shown.label || "", set("label"))));
      box.append(ui.field(t.icon, ui.textInput(shown.icon || "", set("icon")), DEFAULT_ICONS[severity]));
      box.append(ui.field(t.color, ui.textInput(shown.color || "", set("color"))));
      box.append(ui.field(t.push_level, ui.selectInput(LEVELS.map((l) => ({ value: l, label: t.levels[l] })), values.push_levels[severity], (v) => { values.push_levels[severity] = v; paint(); })));
      box.append(ui.field(t.popup_style, ui.selectInput(STYLES.map((x) => ({ value: x, label: t.styles[x] })), values.popup_styles[severity], (v) => { values.popup_styles[severity] = v; paint(); })));
      if (severity === "critical") box.append(el("div", { className: "hint", textContent: t.critical_note }));
      root.append(box);
    }
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveIt);
    root.append(save, status);
    function paint() {
      const { errors, warnings } = problems(values);
      const dirty = Object.keys(changes(values, data.channels)).length > 0;
      save.disabled = errors.length > 0 || !dirty;
      status.className = errors.length ? "hint problems" : "hint ok";
      const texts = [...errors, ...warnings].map((c) => t[c]);
      status.textContent = texts.length ? texts.join(" ") : message || (dirty ? t.valid : "");
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
