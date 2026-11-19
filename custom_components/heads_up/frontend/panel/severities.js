// Heads Up panel: Severities page (D-222, D-223): label, icon and color of each severity, and its
// push level and popup style. Saved through the same command as the Channels page.

export const STRINGS = {
  "en": {
    "title": "Severities",
    "intro": "What each severity looks like everywhere (card, popup, panel, mail) and how it sounds on push and popup. YAML, events and automations keep the names success, info, warning and critical.",
    "label": "Label",
    "icon": "Icon",
    "color": "Color",
    "column_severity": "Severity",
    "theme": "Theme",
    "pick": "Pick a color",
    "edit": "Edit {name}",
    "changed": "changed",
    "critical_help": "About the level critical",
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
    "label": "Bezeichnung",
    "icon": "Symbol",
    "color": "Farbe",
    "column_severity": "Schweregrad",
    "theme": "Theme",
    "pick": "Farbe wählen",
    "edit": "{name} bearbeiten",
    "changed": "geändert",
    "critical_help": "Zur Stufe Kritisch",
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
    "label": "Libellé",
    "icon": "Icône",
    "color": "Couleur",
    "column_severity": "Gravité",
    "theme": "Thème",
    "pick": "Choisir une couleur",
    "edit": "Modifier {name}",
    "changed": "modifié",
    "critical_help": "À propos du niveau critique",
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
    "label": "Etiqueta",
    "icon": "Icono",
    "color": "Color",
    "column_severity": "Gravedad",
    "theme": "Tema",
    "pick": "Elegir un color",
    "edit": "Editar {name}",
    "changed": "cambiado",
    "critical_help": "Sobre el nivel crítico",
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

const DEFAULT_COLORS = { critical: "var(--error-color)", warning: "var(--warning-color)", info: "var(--info-color)", success: "var(--success-color)" };

// A push level without its explanation in brackets, for the overview row: "Passive (no sound)" is "Passive".
export function short(text) {
  return String(text).replace(/\s*\([^)]*\)\s*$/, "");
}

// Whether anything of one severity differs from what is saved (the dot in its overview row).
export function rowChanged(severity, values, saved) {
  const now = cleanDisplay(values.severity_display || {})[severity] || {};
  const before = cleanDisplay(saved.severity_display || {})[severity] || {};
  return JSON.stringify(now) !== JSON.stringify(before)
    || (values.push_levels || {})[severity] !== (saved.push_levels || {})[severity]
    || (values.popup_styles || {})[severity] !== (saved.popup_styles || {})[severity];
}

// "rgb(12, 34, 56)" as "#0c2238", for the color picker's start value.
export function toHex(rgb) {
  const parts = String(rgb).match(/\d+(\.\d+)?/g);
  if (!parts || parts.length < 3) return "#000000";
  return `#${parts.slice(0, 3).map((n) => Math.round(Number(n)).toString(16).padStart(2, "0")).join("")}`;
}

// One row per severity; on a wide page the push level and popup are columns under a header, on a
// phone they are a second line with their own small labels. Only one severity is open at a time.
const PAGE_CSS = `
.hu-page .sev-list { container-type: inline-size; padding: 4px 0; overflow: hidden; }
.hu-page .sev-head, .hu-page .sev-row { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr) minmax(0, 1fr) 44px; gap: 12px; align-items: center; padding: 0 16px; }
.hu-page .sev-head { min-height: 36px; color: var(--secondary-text-color); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
.hu-page .sev-item { border-top: 1px solid var(--divider-color); }
.hu-page .sev-row { width: 100%; min-height: 56px; border: 0; border-radius: 0; background: transparent; text-align: left; font: inherit; color: var(--primary-text-color); }
.hu-page .sev-row:hover { background: var(--hu-fill); }
.hu-page .sev-row:focus-visible { outline-offset: -3px; }
.hu-page .sev-item.open .sev-row { background: var(--hu-fill); }
.hu-page .sev-chip { display: flex; align-items: center; gap: 10px; min-width: 0; color: var(--sev); font-weight: 600; }
.hu-page .sev-chip ha-icon { --mdc-icon-size: 22px; flex: none; }
.hu-page .sev-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hu-page .sev-meta { display: contents; }
.hu-page .sev-cell { min-width: 0; font-size: 14px; overflow-wrap: anywhere; }
.hu-page .sev-k { display: none; }
.hu-page .sev-end { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.hu-page .sev-mark { color: var(--primary-color); font-size: 12px; }
.hu-page .sev-chev { width: 8px; height: 8px; border-right: 2px solid var(--secondary-text-color); border-bottom: 2px solid var(--secondary-text-color); transform: rotate(45deg); margin: 0 6px 4px 0; transition: transform .15s; }
.hu-page .sev-item.open .sev-chev { transform: rotate(-135deg); margin-bottom: -4px; }
.hu-page .sev-edit { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px 16px; padding: 12px 16px 16px; background: var(--hu-fill); }
.hu-page .sev-edit label.field { margin: 0; gap: 6px; font-size: 14px; }
.hu-page .sev-edit input[type=text], .hu-page .sev-edit select { width: 100%; max-width: none; }
.hu-page .sev-wide { grid-column: 1 / -1; }
.hu-page .sev-wide .tip { margin: 0; }
.hu-page .sev-wide:not(:has(.tip.open)) { display: none; }
.hu-page .sev-with { display: flex; align-items: center; gap: 8px; }
.hu-page .sev-with input[type=text] { flex: 1; min-width: 0; }
.hu-page .sev-preview { --mdc-icon-size: 24px; flex: none; width: 44px; display: flex; justify-content: center; color: var(--secondary-text-color); }
.hu-page .sev-pick { flex: none; width: 44px; height: 44px; padding: 2px; border: 1px solid var(--hu-line); border-radius: 8px; background: transparent; cursor: pointer; }
.hu-page .sev-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 12px 0; background: var(--primary-background-color); }
.hu-page .sev-bar.dirty { position: sticky; bottom: 0; }
.hu-page .sev-bar .hint { margin: 0; flex: 1; min-width: 160px; }
@container (max-width: 520px) {
  .hu-page .sev-head { display: none; }
  .hu-page .sev-head + .sev-item { border-top: 0; }
  .hu-page .sev-row { grid-template-columns: minmax(0, 1fr) 44px; row-gap: 2px; padding: 8px 16px; }
  .hu-page .sev-meta { display: flex; flex-wrap: wrap; gap: 2px 16px; grid-column: 1; grid-row: 2; color: var(--secondary-text-color); }
  .hu-page .sev-cell { font-size: 13px; }
  .hu-page .sev-k { display: inline; margin-right: 4px; }
  .hu-page .sev-k::after { content: ":"; }
  .hu-page .sev-end { grid-column: 2; grid-row: 1 / span 2; }
  .hu-page .sev-chip ha-icon { --mdc-icon-size: 20px; }
  .hu-page .sev-edit { grid-template-columns: 1fr; padding: 12px 16px 16px; }
}
`;

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
  let open = null;
  let paint = () => {};
  const root = el("div", { className: "hu-page" });
  container.append(root);

  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + PAGE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    values.severity_display ||= {};
    const list = el("section", { className: "sev-list" });
    list.append(el("div", { className: "sev-head", ariaHidden: "true" }, [
      el("span", { textContent: t.column_severity }),
      el("span", { textContent: t.push_level }),
      el("span", { textContent: t.popup_style }),
    ]));
    const rows = {};
    for (const severity of SEVERITIES) {
      const shown = (values.severity_display[severity] ||= {});
      const editId = `hu-sev-${severity}`;
      const chipIcon = el("ha-icon");
      const chipText = el("span", { className: "sev-name" });
      const chip = el("span", { className: "sev-chip" }, [chipIcon, chipText]);
      const push = el("span", { className: "sev-val" });
      const popup = el("span", { className: "sev-val" });
      const mark = el("span", { className: "sev-mark" });
      const row = el("button", { type: "button", className: "sev-row" }, [
        chip,
        el("span", { className: "sev-meta" }, [
          el("span", { className: "sev-cell" }, [el("span", { className: "sev-k", textContent: t.push_level }), push]),
          el("span", { className: "sev-cell" }, [el("span", { className: "sev-k", textContent: t.popup_style }), popup]),
        ]),
        el("span", { className: "sev-end" }, [mark, el("span", { className: "sev-chev", ariaHidden: "true" })]),
      ]);
      row.setAttribute("aria-controls", editId);
      row.setAttribute("aria-expanded", String(open === severity));
      row.addEventListener("click", () => {
        open = open === severity ? null : severity;
        render();
        root.querySelector(`[aria-controls="${editId}"]`)?.focus();
      });
      const item = el("div", { className: open === severity ? "sev-item open" : "sev-item" }, [row]);
      rows[severity] = () => {
        const name = shown.label?.trim() || t.severities[severity];
        chipText.textContent = name;
        chipIcon.setAttribute("icon", ICON.test(shown.icon || "") ? shown.icon : DEFAULT_ICONS[severity]);
        const color = String(shown.color || "").trim();
        chip.style.setProperty("--sev", color && COLOR.test(color) ? color : DEFAULT_COLORS[severity]);
        push.textContent = short(t.levels[values.push_levels[severity]] || values.push_levels[severity] || "");
        popup.textContent = t.styles[values.popup_styles[severity]] || values.popup_styles[severity] || "";
        const changed = rowChanged(severity, values, data.channels);
        mark.textContent = changed ? "●" : "";
        row.setAttribute("aria-label", `${fill(t.edit, { name })}: ${push.textContent}, ${popup.textContent}${changed ? `, ${t.changed}` : ""}`);
      };
      if (open === severity) item.append(editor(severity, shown, editId, chip));
      list.append(item);
    }
    root.append(list);
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveIt);
    const bar = el("div", { className: "sev-bar" }, [save, status]);
    root.append(bar);
    paint = () => {
      for (const update of Object.values(rows)) update();
      const { errors, warnings } = problems(values);
      const dirty = Object.keys(changes(values, data.channels)).length > 0;
      save.disabled = errors.length > 0 || !dirty;
      bar.classList.toggle("dirty", dirty);
      status.className = errors.length ? "hint problems" : "hint ok";
      const texts = [...errors, ...warnings].map((c) => t[c]);
      status.textContent = texts.length ? texts.join(" ") : message || (dirty ? t.valid : "");
    };
    paint();
  }

  // The fields of one severity, in a grid: two or three columns on a wide screen, one on a phone.
  function editor(severity, shown, id, chip) {
    const set = (key) => (v) => {
      shown[key] = v;
      paint();
    };
    const box = el("div", { className: "sev-edit", id });
    box.append(ui.field(t.label, ui.textInput(shown.label || "", set("label"), { placeholder: t.severities[severity], maxLength: 30 })));
    const iconPreview = el("ha-icon", { className: "sev-preview" });
    const showIcon = () => iconPreview.setAttribute("icon", ICON.test(shown.icon || "") ? shown.icon : DEFAULT_ICONS[severity]);
    const iconInput = ui.textInput(shown.icon || "", (v) => { set("icon")(v); showIcon(); }, { placeholder: DEFAULT_ICONS[severity], spellcheck: false, autocapitalize: "off" });
    showIcon();
    box.append(ui.field(t.icon, el("span", { className: "sev-with" }, [iconPreview, iconInput])));
    const colorText = ui.textInput(shown.color || "", (v) => { set("color")(v); syncPicker(); }, { placeholder: t.theme, spellcheck: false, autocapitalize: "off" });
    const picker = el("input", { type: "color", className: "sev-pick", title: t.pick });
    picker.setAttribute("aria-label", t.pick);
    const syncPicker = () => {
      const now = String(shown.color || "").trim();
      picker.value = /^#[0-9a-fA-F]{6}$/.test(now) ? now.toLowerCase() : toHex(getComputedStyle(chip).color);
    };
    picker.addEventListener("input", () => {
      shown.color = picker.value;
      colorText.value = picker.value;
      paint();
    });
    box.append(ui.field(t.color, el("span", { className: "sev-with" }, [picker, colorText])));
    requestAnimationFrame(syncPicker);
    let note = null;
    const levels = ui.selectInput(LEVELS.map((l) => ({ value: l, label: t.levels[l] })), values.push_levels[severity], (v) => { values.push_levels[severity] = v; paint(); });
    if (severity === "critical") {
      const tip = ui.helpTip(t.critical_help, t.critical_note);
      const label = el("label", { className: "field" }, [el("span", {}, [document.createTextNode(t.push_level), tip.button]), levels]);
      box.append(label);
      note = el("div", { className: "sev-wide" }, [tip.note]);
    } else {
      box.append(ui.field(t.push_level, levels));
    }
    box.append(ui.field(t.popup_style, ui.selectInput(STYLES.map((x) => ({ value: x, label: t.styles[x] })), values.popup_styles[severity], (v) => { values.popup_styles[severity] = v; paint(); })));
    if (note) box.append(note);
    return box;
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
