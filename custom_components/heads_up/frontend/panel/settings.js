// Heads Up panel: Settings page (D-117). Loaded by the shell when the page is opened.

export const STRINGS = {
  en: {
    title: "Settings",
    welcome: "Welcome",
    welcome_button: "Show the welcome",
    welcome_hint: "The welcome explains the default policies and lets you switch each one on or off. Switching an item on adds only the policies that are missing; nothing you have is changed.",
    hub: "Hub",
    hub_enabled: "Hub enabled",
    hub_hint: "Off: messages reach only the dashboard banner, as before the hub existed.",
    show_panel: "Show Heads Up in the sidebar",
    show_panel_hint: "Only administrators see the entry. It appears and disappears at once when you save.",
    people: "People and devices",
    people_none: "No persons found, or the hub is off.",
    person: "Person",
    devices: "Devices",
    no_device: "none: only banner and popup work",
    devices_usable: "{n} of {total} usable",
    no_user: "no user: no popup",
    user_ok: "linked",
    user: "User",
    limits: "Limits",
    rate_per_device_per_minute: "Pushes per device per minute",
    rate_total_per_minute: "Deliveries per minute, all devices",
    dedupe_seconds: "Seconds in which identical updates are ignored",
    history: "History",
    trace_entries: "Trace entries kept",
    recent_messages: "Recent messages kept",
    limits_hint: "Stored now; the limits are enforced in a later version.",
    identity: "Identity",
    install_token: "Install token",
    install_token_hint: "Part of every push tag, so two Home Assistant servers never clear each other's pushes. Read only.",
    save: "Save",
    saved: "Saved.",
    valid: "No problems.",
    range: "{field} must be between {min} and {max}.",
    failed: "Could not save. Try again.",
    loading: "Loading…",
    load_failed: "The settings could not be loaded.",
    edit_recipients: "Recipients",
  },
  de: {
    title: "Einstellungen",
    welcome: "Willkommen",
    welcome_button: "Willkommen anzeigen",
    welcome_hint: "Das Willkommen erklärt die Standardrichtlinien und lässt dich jede ein- oder ausschalten. Eine eingeschaltete Auswahl fügt nur fehlende Richtlinien hinzu; nichts, was du hast, wird geändert.",
    hub: "Hub",
    hub_enabled: "Hub aktiv",
    hub_hint: "Aus: Meldungen erreichen nur das Banner im Dashboard, wie vor dem Hub.",
    show_panel: "Heads Up in der Seitenleiste anzeigen",
    show_panel_hint: "Nur Administratoren sehen den Eintrag. Er erscheint und verschwindet sofort beim Speichern.",
    people: "Personen und Geräte",
    people_none: "Keine Personen gefunden, oder der Hub ist aus.",
    person: "Person",
    devices: "Geräte",
    no_device: "keine: nur Banner und Popup funktionieren",
    devices_usable: "{n} von {total} nutzbar",
    no_user: "kein Benutzer: kein Popup",
    user_ok: "verknüpft",
    user: "Benutzer",
    limits: "Grenzen",
    rate_per_device_per_minute: "Pushes pro Gerät und Minute",
    rate_total_per_minute: "Zustellungen pro Minute, alle Geräte",
    dedupe_seconds: "Sekunden, in denen gleiche Aktualisierungen ignoriert werden",
    history: "Verlauf",
    trace_entries: "Gespeicherte Protokolleinträge",
    recent_messages: "Gespeicherte letzte Meldungen",
    limits_hint: "Wird jetzt gespeichert; die Grenzen werden in einer späteren Version durchgesetzt.",
    identity: "Kennung",
    install_token: "Installations-Token",
    install_token_hint: "Teil jedes Push-Tags, damit zwei Home-Assistant-Server die Pushes des anderen nie löschen. Nur lesbar.",
    save: "Speichern",
    saved: "Gespeichert.",
    valid: "Keine Probleme.",
    range: "{field} muss zwischen {min} und {max} liegen.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    loading: "Lädt…",
    load_failed: "Die Einstellungen konnten nicht geladen werden.",
    edit_recipients: "Empfänger",
  },
  fr: {
    title: "Réglages",
    welcome: "Bienvenue",
    welcome_button: "Afficher la bienvenue",
    welcome_hint: "La bienvenue explique les politiques par défaut et vous laisse activer ou désactiver chacune. Activer un élément n'ajoute que les politiques manquantes ; rien de ce que vous avez n'est modifié.",
    hub: "Hub",
    hub_enabled: "Hub activé",
    hub_hint: "Désactivé : les messages n'atteignent que la bannière du tableau de bord, comme avant le hub.",
    show_panel: "Afficher Heads Up dans la barre latérale",
    show_panel_hint: "Seuls les administrateurs voient l'entrée. Elle apparaît et disparaît aussitôt à l'enregistrement.",
    people: "Personnes et appareils",
    people_none: "Aucune personne trouvée, ou le hub est désactivé.",
    person: "Personne",
    devices: "Appareils",
    no_device: "aucun : seuls la bannière et la fenêtre contextuelle fonctionnent",
    devices_usable: "{n} sur {total} utilisables",
    no_user: "pas d'utilisateur : pas de fenêtre contextuelle",
    user_ok: "lié",
    user: "Utilisateur",
    limits: "Limites",
    rate_per_device_per_minute: "Push par appareil et par minute",
    rate_total_per_minute: "Livraisons par minute, tous appareils",
    dedupe_seconds: "Secondes pendant lesquelles les mises à jour identiques sont ignorées",
    history: "Historique",
    trace_entries: "Entrées de trace conservées",
    recent_messages: "Messages récents conservés",
    limits_hint: "Enregistrées maintenant ; les limites seront appliquées dans une version ultérieure.",
    identity: "Identité",
    install_token: "Jeton d'installation",
    install_token_hint: "Fait partie de chaque étiquette de push, pour que deux serveurs Home Assistant n'effacent jamais les push de l'autre. Lecture seule.",
    save: "Enregistrer",
    saved: "Enregistré.",
    valid: "Aucun problème.",
    range: "{field} doit être entre {min} et {max}.",
    failed: "Enregistrement impossible. Réessayez.",
    loading: "Chargement…",
    load_failed: "Les réglages n'ont pas pu être chargés.",
    edit_recipients: "Destinataires",
  },
  es: {
    title: "Ajustes",
    welcome: "Bienvenida",
    welcome_button: "Mostrar la bienvenida",
    welcome_hint: "La bienvenida explica las políticas por defecto y te deja activar o desactivar cada una. Activar un elemento solo añade las políticas que faltan; nada de lo que tienes se modifica.",
    hub: "Hub",
    hub_enabled: "Hub activado",
    hub_hint: "Desactivado: los mensajes solo llegan al aviso del panel, como antes del hub.",
    show_panel: "Mostrar Heads Up en la barra lateral",
    show_panel_hint: "Solo los administradores ven la entrada. Aparece y desaparece al guardar.",
    people: "Personas y dispositivos",
    people_none: "No se encontraron personas, o el hub está desactivado.",
    person: "Persona",
    devices: "Dispositivos",
    no_device: "ninguno: solo funcionan el aviso y la ventana emergente",
    devices_usable: "{n} de {total} utilizables",
    no_user: "sin usuario: sin ventana emergente",
    user_ok: "vinculado",
    user: "Usuario",
    limits: "Límites",
    rate_per_device_per_minute: "Pushes por dispositivo y minuto",
    rate_total_per_minute: "Entregas por minuto, todos los dispositivos",
    dedupe_seconds: "Segundos en que se ignoran las actualizaciones idénticas",
    history: "Historial",
    trace_entries: "Entradas de traza guardadas",
    recent_messages: "Mensajes recientes guardados",
    limits_hint: "Se guardan ahora; los límites se aplicarán en una versión posterior.",
    identity: "Identidad",
    install_token: "Token de instalación",
    install_token_hint: "Parte de cada etiqueta de push, para que dos servidores de Home Assistant nunca borren los push del otro. Solo lectura.",
    save: "Guardar",
    saved: "Guardado.",
    valid: "Sin problemas.",
    range: "{field} debe estar entre {min} y {max}.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    loading: "Cargando…",
    load_failed: "No se pudieron cargar los ajustes.",
    edit_recipients: "Destinatarios",
  },
};

const NUMBERS = ["rate_per_device_per_minute", "rate_total_per_minute", "dedupe_seconds", "trace_entries", "recent_messages"];
const BOOLEANS = ["hub_enabled", "show_panel"];

// Problems of a set of values, as { key, min, max } for the page to word. Empty means valid.
export function problems(values, ranges) {
  const found = [];
  for (const key of NUMBERS) {
    const [min, max] = ranges[key];
    const value = values[key];
    if (!Number.isInteger(value) || value < min || value > max) found.push({ key, min, max });
  }
  return found;
}

// What differs from the saved values: only those keys are sent.
export function changes(values, saved) {
  const out = {};
  for (const key of [...BOOLEANS, ...NUMBERS]) if (values[key] !== saved[key]) out[key] = values[key];
  return out;
}

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value), template);
}

export function devicesLabel(person, t) {
  if (person.devices_total === 0) return t.no_device;
  return fill(t.devices_usable, { n: person.devices, total: person.devices_total });
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-settings section { background: var(--card-background-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: var(--ha-card-box-shadow, none); border: 1px solid var(--divider-color); }
.hu-settings h2 { font-size: 16px; margin: 0 0 8px; }
.hu-settings .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; }
.hu-settings label.field { display: flex; align-items: center; gap: 10px; min-height: 48px; }
.hu-settings label.num { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
.hu-settings input[type=number], .hu-settings input[type=text] { min-height: 40px; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color);
  background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; max-width: 200px; }
.hu-settings input[type=checkbox] { width: 24px; height: 24px; }
.hu-settings button { min-height: 48px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-settings button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-settings button:disabled { opacity: .5; cursor: default; }
.hu-settings button:focus-visible, .hu-settings input:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-settings table { width: 100%; border-collapse: collapse; }
.hu-settings th, .hu-settings td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--divider-color); }
.hu-settings .problems { color: var(--error-color); }
.hu-settings .ok { color: var(--success-color); }
`;

export function mount(container, ctx) {
  const t = ctx.t;
  let hass = ctx.hass;
  let data = null;
  let values = {};
  let message = "";
  const root = el("div", { className: "hu-settings" });
  root.append(el("style", { textContent: CSS }), el("div", { textContent: t.loading }));
  container.append(root);

  const call = (payload) => hass.callWS(payload);

  function render() {
    root.replaceChildren(el("style", { textContent: CSS }));
    root.append(el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }));
    const checkbox = (key, label, hint) => {
      const input = el("input", { type: "checkbox", checked: Boolean(values[key]) });
      input.addEventListener("change", () => {
        values[key] = input.checked;
        message = "";
        render();
      });
      const row = el("label", { className: "field" }, [input, el("span", { textContent: label })]);
      return [row, el("div", { className: "hint", textContent: hint })];
    };
    const number = (key) => {
      const [min, max] = data.ranges[key];
      const input = el("input", { type: "number", value: String(values[key] ?? ""), min, max, step: 1 });
      input.addEventListener("input", () => {
        values[key] = input.value === "" ? NaN : Number(input.value);
        message = "";
        paintStatus();
      });
      return el("label", { className: "num" }, [el("span", { textContent: t[key] }), input]);
    };
    const section = (title, children) => {
      const box = el("section", {}, [el("h2", { textContent: title }), ...children]);
      root.append(box);
      return box;
    };

    section(t.hub, [
      ...checkbox("hub_enabled", t.hub_enabled, t.hub_hint),
      ...checkbox("show_panel", t.show_panel, t.show_panel_hint),
    ]);

    const welcomeButton = el("button", { type: "button", textContent: t.welcome_button });
    welcomeButton.addEventListener("click", () => ctx.openWelcome());
    section(t.welcome, [welcomeButton, el("div", { className: "hint", textContent: t.welcome_hint })]);

    const people = data.people;
    if (people.length === 0) {
      section(t.people, [el("div", { className: "hint", textContent: t.people_none })]);
    } else {
      const head = el("tr", {}, [t.person, t.devices, t.user].map((text) => el("th", { textContent: text })));
      const rows = people.map((p) =>
        el("tr", {}, [
          el("td", { textContent: p.name }),
          el("td", { textContent: devicesLabel(p, t) }),
          el("td", { textContent: p.user ? t.user_ok : t.no_user }),
        ]),
      );
      const link = el("button", { type: "button", textContent: t.edit_recipients });
      link.addEventListener("click", () => ctx.navigate("recipients"));
      section(t.people, [el("table", {}, [el("thead", {}, [head]), el("tbody", {}, rows)]), link]);
    }

    section(t.limits, [el("div", { className: "hint", textContent: t.limits_hint }), ...["rate_per_device_per_minute", "rate_total_per_minute", "dedupe_seconds"].map(number)]);
    section(t.history, ["trace_entries", "recent_messages"].map(number));

    const token = el("input", { type: "text", value: data.install_token, readOnly: true });
    token.setAttribute("aria-label", t.install_token);
    section(t.identity, [el("label", { className: "num" }, [el("span", { textContent: t.install_token }), token]), el("div", { className: "hint", textContent: t.install_token_hint })]);

    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveSettings);
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    root.append(save, status);
    root._save = save;
    root._status = status;
    paintStatus();
  }

  function paintStatus() {
    const found = problems(values, data.ranges);
    const dirty = Object.keys(changes(values, data.options)).length > 0;
    root._save.disabled = found.length > 0 || !dirty;
    root._status.className = found.length ? "hint problems" : "hint ok";
    root._status.textContent = found.length
      ? found.map((p) => fill(t.range, { field: t[p.key], min: p.min, max: p.max })).join(" ")
      : message || (dirty ? t.valid : "");
  }

  async function saveSettings() {
    try {
      const result = await call({ type: "heads_up/settings_set", ...changes(values, data.options) });
      data.options = result.options;
      values = { ...result.options };
      message = t.saved;
      await load(false);
    } catch (err) {
      message = t.failed;
      paintStatus();
    }
  }

  async function load(initial) {
    try {
      const keep = initial ? null : values;
      data = await call({ type: "heads_up/settings_get" });
      values = keep ? { ...data.options, ...keep } : { ...data.options };
      render();
    } catch (err) {
      root.replaceChildren(el("div", { textContent: t.load_failed }));
    }
  }

  load(true);
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      root.remove();
    },
  };
}
