// Heads Up card: shows banners from the heads_up integration (DESIGN §8).
// Plain ES module, no build step (D-021). Banner text is caller-supplied and is only
// ever written with textContent.

export const SEVERITIES = ["critical", "warning", "info", "success"];
const SEVERITY_RANK = Object.fromEntries(SEVERITIES.map((s, i) => [s, i]));
const SEVERITY_COLOR = {
  critical: "--error-color",
  warning: "--warning-color",
  info: "--info-color",
  success: "--success-color",
};
// Read by scripts/docs_check.py to keep docs/card.md in step with the card.
export const CONFIG_KEYS = [
  "severity",
  "tag",
  "max_items",
  "sort",
  "layout",
  "show_all",
  "show_empty",
];
const SORTS = ["severity", "time"];
const LAYOUTS = ["comfortable", "compact"];

// One table so other languages can be added later (D-037). Banner text is never translated.
export const STRINGS = {
  severity: {
    critical: "Critical",
    warning: "Warning",
    info: "Info",
    success: "Success",
  },
  dismiss: "Dismiss",
  clear: "Clear for everyone",
  error: "Heads Up is not available. Check that the integration is loaded.",
  editor: {
    severity: "Severities (empty = all)",
    tag: "Tags (empty = all)",
    max_items: "Maximum number of banners",
    sort: "Sort",
    layout: "Layout",
    show_all: "Show banners for all users (admins only)",
    show_empty: "Show the card when there are no banners",
    sort_severity: "Severity, then newest",
    sort_time: "Newest first",
    layout_comfortable: "Comfortable",
    layout_compact: "Compact",
  },
};

function toList(value, key) {
  if (value === undefined || value === null) return [];
  const list = Array.isArray(value) ? value : [value];
  if (!list.every((item) => typeof item === "string")) {
    throw new Error(`${key} must be a string or a list of strings`);
  }
  return list;
}

// Validates a card config and fills defaults. Throws Error with a readable message.
export function normalizeConfig(config) {
  if (!config || typeof config !== "object") throw new Error("Invalid configuration");
  const severity = toList(config.severity, "severity");
  for (const s of severity) {
    if (!SEVERITIES.includes(s)) {
      throw new Error(`severity must be one of ${SEVERITIES.join(", ")}`);
    }
  }
  const sort = config.sort ?? "severity";
  if (!SORTS.includes(sort)) throw new Error(`sort must be one of ${SORTS.join(", ")}`);
  const layout = config.layout ?? "comfortable";
  if (!LAYOUTS.includes(layout)) throw new Error(`layout must be one of ${LAYOUTS.join(", ")}`);
  const maxItems = config.max_items ?? null;
  if (maxItems !== null && (!Number.isInteger(maxItems) || maxItems < 1)) {
    throw new Error("max_items must be an integer of 1 or more");
  }
  return {
    ...config,
    severity,
    tag: toList(config.tag, "tag"),
    max_items: maxItems,
    sort,
    layout,
    show_all: config.show_all === true,
    show_empty: config.show_empty === true,
  };
}

function byNewest(a, b) {
  return Date.parse(b.updated_at) - Date.parse(a.updated_at);
}

export function sortBanners(banners, sort) {
  const list = [...banners];
  if (sort === "time") return list.sort(byNewest);
  return list.sort(
    (a, b) => (SEVERITY_RANK[a.severity] ?? 99) - (SEVERITY_RANK[b.severity] ?? 99) || byNewest(a, b),
  );
}

// Banners the card shows: active, not dismissed by this viewer, matching the filters, sorted, capped.
export function visibleBanners(banners, config) {
  const shown = (banners ?? []).filter(
    (b) =>
      b.active &&
      !b.dismissed &&
      (config.severity.length === 0 || config.severity.includes(b.severity)) &&
      (config.tag.length === 0 || config.tag.includes(b.tag)),
  );
  const sorted = sortBanners(shown, config.sort);
  return config.max_items === null ? sorted : sorted.slice(0, config.max_items);
}

// Seconds to wait before subscribe attempt n (0-based). During an HA start the websocket API
// accepts clients before this integration has registered heads_up/subscribe (N-40).
export function retryDelay(attempt) {
  return [1000, 2000, 5000, 10000, 30000][Math.min(attempt, 4)];
}

// Which buttons a banner gets for a viewer. Admin clear exists for banners nobody can dismiss (D-011).
export function controlsFor(banner, isAdmin) {
  return {
    dismiss: banner.dismissible !== false,
    adminClear: isAdmin && banner.dismissible === false,
    tap: Boolean(banner.tap_action),
  };
}

const STYLE = `
  :host { display: block; }
  ha-card { overflow: hidden; }
  .list { display: flex; flex-direction: column; gap: 8px; padding: 8px; }
  .banner {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 8px 12px 12px; border-radius: 8px;
    border-inline-start: 4px solid var(--accent);
    background: color-mix(in srgb, var(--accent) 15%, var(--card-background-color));
    color: var(--primary-text-color);
  }
  .compact .banner { padding: 6px 4px 6px 10px; gap: 8px; }
  .banner.tap { cursor: pointer; }
  .banner.tap:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  ha-icon { color: var(--accent); flex: none; margin-top: 2px; }
  .text { flex: 1; min-width: 0; overflow-wrap: anywhere; }
  .label { font-size: 0.75em; font-weight: 500; text-transform: uppercase; color: var(--accent); }
  .title { font-weight: 500; }
  .message { white-space: pre-line; }
  button.action {
    flex: none; width: 48px; height: 48px; padding: 0; border: 0; border-radius: 50%;
    background: transparent; color: var(--primary-text-color); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
  }
  button.action:focus-visible { outline: 2px solid var(--accent); }
  .error { padding: 16px; color: var(--error-color); }
`;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

// Lets the module load in Node, where vitest imports the pure functions above.
const Base = typeof HTMLElement !== "undefined" ? HTMLElement : class {};

class HeadsUpCard extends Base {
  static getConfigElement() {
    return document.createElement("heads-up-card-editor");
  }

  static getStubConfig() {
    return {};
  }

  constructor() {
    super();
    this._config = null;
    this._banners = [];
    this._error = false;
    this._unsub = null;
    this._subscribeKey = null;
    this._generation = 0;
    this._retryTimer = null;
    this._attempt = 0;
    this._connection = null;
    this._connected = false;
    this._onReady = () => this._resubscribe();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    this._config = normalizeConfig(config);
    if (this._connected) this._subscribe();
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
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
  }

  getCardSize() {
    return Math.max(1, this._shown().length);
  }

  getGridOptions() {
    return { columns: 12, rows: "auto" };
  }

  _shown() {
    return this._config ? visibleBanners(this._banners, this._config) : [];
  }

  _unsubscribe() {
    const unsub = this._unsub;
    this._unsub = null;
    this._subscribeKey = null;
    this._generation += 1; // late results of an older attempt are ignored
    clearTimeout(this._retryTimer);
    this._retryTimer = null;
    if (unsub) unsub.then((fn) => fn()).catch(() => {});
  }

  // After a reconnect the old subscription is gone on the server. The library's own
  // re-subscribe is switched off (resubscribe: false) because it cannot retry when the command
  // is not registered yet (N-39, N-40); the backend sends the full list again on subscribe.
  _resubscribe() {
    this._unsub = null; // dead connection: nothing to unsubscribe
    this._subscribeKey = null;
    this._generation += 1;
    this._attempt = 0;
    clearTimeout(this._retryTimer);
    this._subscribe();
  }

  _subscribe() {
    if (!this._hass || !this._config) return;
    const connection = this._hass.connection;
    if (this._connection !== connection) {
      this._connection?.removeEventListener("ready", this._onReady);
      connection.addEventListener("ready", this._onReady);
      this._connection = connection;
    }
    const showAll = this._config.show_all && this._hass.user?.is_admin === true;
    if (this._subscribeKey === showAll) return;
    this._unsubscribe();
    this._subscribeKey = showAll;
    const generation = this._generation;
    const promise = connection.subscribeMessage(
      (event) => {
        if (generation !== this._generation) return;
        this._error = false;
        this._banners = event.banners;
        this._render();
      },
      { type: "heads_up/subscribe", show_all: showAll },
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
        this._subscribeKey = null;
        this._error = true;
        this._render();
        this._retryTimer = setTimeout(() => this._subscribe(), retryDelay(this._attempt++));
      },
    );
  }

  _dismiss(banner) {
    this._hass.callWS({ type: "heads_up/dismiss", banner_id: banner.id }).catch(() => {});
  }

  _adminClear(banner) {
    this._hass.callWS({ type: "heads_up/admin_clear", banner_id: banner.id }).catch(() => {});
  }

  _tap(banner) {
    // handleAction reads config.tap_action and handles confirmation itself (N-38).
    this.dispatchEvent(
      new CustomEvent("hass-action", {
        bubbles: true,
        composed: true,
        detail: { config: { tap_action: banner.tap_action }, action: "tap" },
      }),
    );
  }

  _bannerNode(banner, isAdmin) {
    const controls = controlsFor(banner, isAdmin);
    const node = el("div", `banner${controls.tap ? " tap" : ""}`);
    node.style.setProperty("--accent", `var(${SEVERITY_COLOR[banner.severity] ?? "--info-color"})`);

    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", banner.icon);
    icon.setAttribute("aria-hidden", "true");
    node.append(icon);

    const text = el("div", "text");
    text.append(el("div", "label", STRINGS.severity[banner.severity] ?? banner.severity));
    if (banner.title) text.append(el("div", "title", banner.title));
    text.append(el("div", "message", banner.message));
    node.append(text);

    if (controls.tap) {
      node.setAttribute("role", "button");
      node.tabIndex = 0;
      node.addEventListener("click", () => this._tap(banner));
      node.addEventListener("keydown", (ev) => {
        if (ev.target === node && (ev.key === "Enter" || ev.key === " ")) {
          ev.preventDefault();
          this._tap(banner);
        }
      });
    }

    const button = (icon_name, label, handler) => {
      const b = el("button", "action");
      b.type = "button";
      b.setAttribute("aria-label", label);
      b.title = label;
      const i = document.createElement("ha-icon");
      i.setAttribute("icon", icon_name);
      b.append(i);
      b.addEventListener("click", (ev) => {
        ev.stopPropagation();
        handler();
      });
      return b;
    };
    if (controls.dismiss) node.append(button("mdi:close", STRINGS.dismiss, () => this._dismiss(banner)));
    if (controls.adminClear) {
      node.append(button("mdi:delete-outline", STRINGS.clear, () => this._adminClear(banner)));
    }
    return node;
  }

  _render() {
    const root = this.shadowRoot;
    root.replaceChildren();
    const style = document.createElement("style");
    style.textContent = STYLE;
    root.append(style);

    if (this._error) {
      this.style.display = "";
      const card = el("ha-card");
      card.append(el("div", "error", STRINGS.error));
      root.append(card);
      return;
    }

    const shown = this._shown();
    if (shown.length === 0 && !this._config?.show_empty) {
      this.style.display = "none";
      return;
    }
    this.style.display = "";

    const isAdmin = this._hass?.user?.is_admin === true;
    const card = el("ha-card");
    const list = el("div", `list ${this._config.layout}`);
    // Critical banners are announced at once, the rest politely.
    const assertive = el("div");
    assertive.setAttribute("aria-live", "assertive");
    const polite = el("div");
    polite.setAttribute("aria-live", "polite");
    for (const region of [assertive, polite]) {
      region.style.display = "flex";
      region.style.flexDirection = "column";
      region.style.gap = "8px";
    }
    for (const banner of shown) {
      (banner.severity === "critical" ? assertive : polite).append(this._bannerNode(banner, isAdmin));
    }
    list.append(assertive, polite);
    card.append(list);
    root.append(card);
  }
}

class HeadsUpCardEditor extends Base {
  setConfig(config) {
    this._config = config;
    this._update();
  }

  set hass(hass) {
    this._hass = hass;
    this._update();
  }

  _schema() {
    const t = STRINGS.editor;
    return [
      {
        name: "severity",
        selector: {
          select: {
            multiple: true,
            mode: "list",
            options: SEVERITIES.map((s) => ({ value: s, label: STRINGS.severity[s] })),
          },
        },
      },
      { name: "tag", selector: { text: { multiple: true } } },
      { name: "max_items", selector: { number: { min: 1, step: 1, mode: "box" } } },
      {
        name: "sort",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "severity", label: t.sort_severity },
              { value: "time", label: t.sort_time },
            ],
          },
        },
      },
      {
        name: "layout",
        selector: {
          select: {
            mode: "dropdown",
            options: [
              { value: "comfortable", label: t.layout_comfortable },
              { value: "compact", label: t.layout_compact },
            ],
          },
        },
      },
      { name: "show_all", selector: { boolean: {} } },
      { name: "show_empty", selector: { boolean: {} } },
    ];
  }

  _update() {
    if (!this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) => STRINGS.editor[schema.name] ?? schema.name;
      this._form.addEventListener("value-changed", (ev) => {
        ev.stopPropagation();
        const config = { ...ev.detail.value };
        // Drop cleared values so the saved YAML stays minimal.
        for (const key of Object.keys(config)) {
          const v = config[key];
          if (v === undefined || v === null || v === "" || (Array.isArray(v) && v.length === 0)) {
            delete config[key];
          }
        }
        this.dispatchEvent(
          new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } }),
        );
      });
      this.append(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = this._config;
  }
}

if (typeof customElements !== "undefined") {
  customElements.define("heads-up-card", HeadsUpCard);
  customElements.define("heads-up-card-editor", HeadsUpCardEditor);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "heads-up-card",
    name: "Heads Up",
    description: "Banners created by the Heads Up integration.",
    documentationURL: "https://github.com/Seyphaton/ha-heads-up",
  });
}
