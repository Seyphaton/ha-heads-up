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
export const MODULES = { general: "settings.js" };
export const DEFAULT_PAGE = "status";
export const BASE_PATH = "/heads-up";

export const STRINGS = {
  en: {
    title: "Heads Up",
    menu: "Open the sidebar",
    groups: { overview: "Overview", notifications: "Notifications and rules", configuration: "Configuration", settings: "Settings", faq: "FAQ and examples" },
    pages: { status: "Status", test: "Test send", rules: "Watch rules", messages: "Messages", audiences: "Audiences", recipients: "Recipients", policies: "Policies", channels: "Channels", general: "General", faq: "FAQ and examples" },
    not_built: "This page is not available yet.",
    loading: "Loading…",
    load_failed: "The page could not be loaded. Reload the browser page.",
    nav_label: "Heads Up pages",
  },
  de: {
    title: "Heads Up",
    menu: "Seitenleiste öffnen",
    groups: { overview: "Übersicht", notifications: "Benachrichtigungen und Regeln", configuration: "Konfiguration", settings: "Einstellungen", faq: "FAQ und Beispiele" },
    pages: { status: "Status", test: "Testsenden", rules: "Überwachungsregeln", messages: "Meldungen", audiences: "Zielgruppen", recipients: "Empfänger", policies: "Richtlinien", channels: "Kanäle", general: "Allgemein", faq: "FAQ und Beispiele" },
    not_built: "Diese Seite ist noch nicht verfügbar.",
    loading: "Lädt…",
    load_failed: "Die Seite konnte nicht geladen werden. Lade die Browserseite neu.",
    nav_label: "Heads-Up-Seiten",
  },
  fr: {
    title: "Heads Up",
    menu: "Ouvrir la barre latérale",
    groups: { overview: "Vue d'ensemble", notifications: "Notifications et règles", configuration: "Configuration", settings: "Réglages", faq: "FAQ et exemples" },
    pages: { status: "État", test: "Envoi de test", rules: "Règles de surveillance", messages: "Messages", audiences: "Audiences", recipients: "Destinataires", policies: "Politiques", channels: "Canaux", general: "Général", faq: "FAQ et exemples" },
    not_built: "Cette page n'est pas encore disponible.",
    loading: "Chargement…",
    load_failed: "La page n'a pas pu être chargée. Rechargez la page du navigateur.",
    nav_label: "Pages Heads Up",
  },
  es: {
    title: "Heads Up",
    menu: "Abrir la barra lateral",
    groups: { overview: "Resumen", notifications: "Notificaciones y reglas", configuration: "Configuración", settings: "Ajustes", faq: "Preguntas y ejemplos" },
    pages: { status: "Estado", test: "Envío de prueba", rules: "Reglas de vigilancia", messages: "Mensajes", audiences: "Audiencias", recipients: "Destinatarios", policies: "Políticas", channels: "Canales", general: "General", faq: "Preguntas y ejemplos" },
    not_built: "Esta página aún no está disponible.",
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

const CSS = `
:host { display: block; min-height: 100vh; background: var(--primary-background-color); color: var(--primary-text-color);
  font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
header { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 12px; background: var(--app-header-background-color, var(--primary-color));
  color: var(--app-header-text-color, var(--text-primary-color, #fff)); }
header h1 { font-size: 20px; font-weight: 500; margin: 0; }
button { font: inherit; cursor: pointer; }
.menu { min-width: 48px; min-height: 48px; border: none; background: transparent; color: inherit; font-size: 22px; }
nav { background: var(--card-background-color); border-bottom: 1px solid var(--divider-color); }
nav .row { display: flex; gap: 4px; overflow-x: auto; padding: 0 8px; }
nav button { min-height: 48px; padding: 0 14px; border: none; border-bottom: 3px solid transparent; background: transparent; color: var(--secondary-text-color); white-space: nowrap; }
nav button[aria-current="page"] { color: var(--primary-color); border-bottom-color: var(--primary-color); font-weight: 600; }
nav .second { background: var(--secondary-background-color); }
nav button:focus-visible, .menu:focus-visible { outline: 3px solid var(--primary-color); outline-offset: -3px; }
main { max-width: 900px; margin: 0 auto; padding: 16px; }
.note { color: var(--secondary-text-color); padding: 24px 0; }
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
    root.append(this._header, this._nav, this._main);
    this._renderHeader();
    this._open(pageFromPath(this._route?.path));
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
      const mod = await import(moduleUrl(this._config?.base ?? "/heads_up/panel", this._config?.v ?? "", file));
      if (token !== this._token) return; // another page was opened meanwhile
      const container = node("div");
      this._main.replaceChildren(container);
      this._mounted = mod.mount(container, {
        hass: this._hass,
        t: table(mod.STRINGS, this._hass?.language),
        navigate: (target) => this.navigate(target),
      });
    } catch (err) {
      if (token === this._token) this._main.replaceChildren(node("div", { className: "note", textContent: t.load_failed }));
    }
  }
}

if (typeof customElements !== "undefined" && !customElements.get("heads-up-panel")) {
  customElements.define("heads-up-panel", HeadsUpPanel);
}
