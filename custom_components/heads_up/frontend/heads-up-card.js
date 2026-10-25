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
  "title",
  "show_time",
  "show_severity",
  "colors",
  "colorize",
  "clear_all",
  "swipe_to_dismiss",
  "collapsed_items",
  "empty_message",
  "empty_icon",
];
// Shown in the editor for options that are not set; not written to the saved config.
const EDITOR_DEFAULTS = {
  sort: "severity",
  layout: "comfortable",
  colorize: "all",
  empty_icon: "mdi:bell-check-outline",
};
const SORTS = ["severity", "time"];
const LAYOUTS = ["comfortable", "compact"];
const COLORIZE = ["all", "background", "icon", "bar"];
const DEFAULT_EMPTY_ICON = "mdi:bell-check-outline";
const TIME_REFRESH_MS = 30000;
const SWIPE_START_PX = 10;

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
  clear_all: "Clear all",
  show_more: "Show {n} more",
  show_less: "Show less",
  time: {
    just_now: "just now",
    minute: "{n} min ago",
    hour: "{n} h ago",
    day: "1 day ago",
    days: "{n} days ago",
  },
  error: "Heads Up is not available. Check that the integration is loaded.",
  editor: {
    severity: "Severities (empty = all)",
    tag: "Tags (empty = all)",
    max_items: "Maximum number of banners",
    sort: "Sort",
    layout: "Layout",
    show_all: "Show banners for all users (admins only)",
    show_empty: "Show the card when there are no banners",
    title: "Card title",
    show_time: "Show how long ago a banner was created or replaced",
    show_severity: "Show the severity label",
    colors: "Severity colors (CSS color or theme variable)",
    colorize: "Colorize",
    clear_all: "Show a Clear all button",
    swipe_to_dismiss: "Swipe a banner to dismiss it",
    collapsed_items: "Show only this many banners, then a Show more button",
    empty_message: "Message when there are no banners (shows the card)",
    empty_icon: "Icon for that message",
    sort_severity: "Severity, then newest",
    sort_time: "Newest first",
    layout_comfortable: "Comfortable",
    layout_compact: "Compact (one line)",
    colorize_all: "Background, icon and left bar",
    colorize_background: "Background only",
    colorize_icon: "Icon and label only",
    colorize_bar: "Left bar only",
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

function toBool(value) {
  return value === true;
}

function toText(value, key) {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") throw new Error(`${key} must be text`);
  return value;
}

function toColors(value) {
  if (value === undefined || value === null) return {};
  if (typeof value !== "object" || Array.isArray(value)) {
    throw new Error("colors must map severities to colors");
  }
  const colors = {};
  for (const [severity, color] of Object.entries(value)) {
    if (!SEVERITIES.includes(severity)) {
      throw new Error(`colors: ${severity} is not one of ${SEVERITIES.join(", ")}`);
    }
    // The value goes into a CSS custom property; refuse anything that could end the declaration.
    if (typeof color !== "string" || color.trim() === "" || /[;{}]/.test(color)) {
      throw new Error(`colors.${severity} must be a CSS color or a var(--name)`);
    }
    colors[severity] = color.trim();
  }
  return colors;
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
  const colorize = config.colorize ?? "all";
  if (!COLORIZE.includes(colorize)) {
    throw new Error(`colorize must be one of ${COLORIZE.join(", ")}`);
  }
  const maxItems = config.max_items ?? null;
  if (maxItems !== null && (!Number.isInteger(maxItems) || maxItems < 1)) {
    throw new Error("max_items must be an integer of 1 or more");
  }
  const collapsed = config.collapsed_items ?? null;
  if (collapsed !== null && (!Number.isInteger(collapsed) || collapsed < 1)) {
    throw new Error("collapsed_items must be an integer of 1 or more");
  }
  const emptyIcon = config.empty_icon ?? DEFAULT_EMPTY_ICON;
  if (typeof emptyIcon !== "string" || !/^[a-z0-9_-]+:[a-z0-9_-]+$/i.test(emptyIcon)) {
    throw new Error("empty_icon must look like mdi:bell-check-outline");
  }
  return {
    ...config,
    severity,
    tag: toList(config.tag, "tag"),
    max_items: maxItems,
    sort,
    layout,
    show_all: toBool(config.show_all),
    show_empty: toBool(config.show_empty),
    title: toText(config.title, "title"),
    show_time: toBool(config.show_time),
    show_severity: toBool(config.show_severity),
    colors: toColors(config.colors),
    colorize,
    clear_all: toBool(config.clear_all),
    swipe_to_dismiss: toBool(config.swipe_to_dismiss),
    collapsed_items: collapsed,
    empty_message: toText(config.empty_message, "empty_message"),
    empty_icon: emptyIcon,
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

// "just now", "50 min ago", "3 h ago", "1 day ago", "2 days ago". Anything unreadable or in the
// future reads "just now".
export function relativeTime(iso, now = Date.now()) {
  const t = STRINGS.time;
  const diff = now - Date.parse(iso);
  if (!(diff >= 60 * 1000)) return t.just_now;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return t.minute.replace("{n}", minutes);
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return t.hour.replace("{n}", hours);
  const days = Math.floor(hours / 24);
  return days === 1 ? t.day : t.days.replace("{n}", days);
}

// Applies collapsed_items. `hidden` counts the banners behind the button, also when expanded
// (the button then reads "Show less").
export function collapse(list, collapsedItems, expanded) {
  if (collapsedItems === null) return { shown: list, hidden: 0 };
  const hidden = Math.max(0, list.length - collapsedItems);
  return { shown: expanded ? list : list.slice(0, collapsedItems), hidden };
}

// What an empty card shows: a message with an icon, a blank card, or nothing (D-040, D-048).
export function emptyView(config) {
  if (config.empty_message !== "") return "message";
  return config.show_empty ? "blank" : "hidden";
}

export function resolveColors(config) {
  return Object.fromEntries(
    SEVERITIES.map((s) => [s, config.colors[s] ?? `var(${SEVERITY_COLOR[s]})`]),
  );
}

// Which parts of a banner take the severity color. Uncolored parts use theme text colors.
export function colorParts(colorize) {
  return {
    background: colorize === "all" || colorize === "background",
    icon: colorize === "all" || colorize === "icon",
    bar: colorize === "all" || colorize === "bar",
  };
}

// Swipe to dismiss (D-048): mostly horizontal, and at least 80 px or 30% of the banner width.
export function swipeOutcome(dx, dy, width) {
  if (Math.abs(dx) <= Math.abs(dy)) return "cancel";
  return Math.abs(dx) >= Math.max(80, width * 0.3) ? "dismiss" : "cancel";
}

// IDs the "Clear all" button dismisses: every dismissible banner of the list.
export function clearableIds(banners) {
  return banners.filter((b) => b.dismissible !== false).map((b) => b.id);
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
  .header {
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
    padding: 8px 8px 0 16px; min-height: 40px;
  }
  .card-title { font-size: 1.1em; font-weight: 500; color: var(--primary-text-color); }
  .list { display: flex; flex-direction: column; gap: 8px; padding: 8px; }
  .region { display: flex; flex-direction: column; gap: 8px; }
  .banner {
    position: relative; display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 8px 12px 12px; border-radius: 8px;
    border-inline-start: 4px solid transparent;
    background: var(--secondary-background-color);
    color: var(--primary-text-color);
  }
  .banner.c-bg { background: color-mix(in srgb, var(--accent) 15%, var(--card-background-color)); }
  .banner.c-bar { border-inline-start-color: var(--accent); }
  .banner.swipe { touch-action: pan-y; user-select: none; }
  .banner.tap { cursor: pointer; }
  .banner.tap:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .banner ha-icon { flex: none; margin-top: 2px; color: var(--primary-text-color); }
  .banner.c-icon ha-icon { color: var(--accent); }
  .text { flex: 1; min-width: 0; overflow-wrap: anywhere; }
  .meta { display: flex; justify-content: space-between; gap: 8px; font-size: 0.75em; }
  .label { font-weight: 500; text-transform: uppercase; color: var(--secondary-text-color); }
  .c-icon .label { color: var(--accent); }
  .time { color: var(--secondary-text-color); white-space: nowrap; }
  .title { font-weight: 500; }
  .message { white-space: pre-line; }
  .sr-only {
    position: absolute; width: 1px; height: 1px; overflow: hidden;
    clip: rect(0 0 0 0); white-space: nowrap;
  }
  .compact .banner { align-items: center; gap: 8px; padding: 0 0 0 10px; min-height: 40px; }
  .compact .banner ha-icon { margin-top: 0; --mdc-icon-size: 20px; }
  .compact .text {
    display: flex; align-items: baseline; gap: 8px; white-space: nowrap; overflow: hidden;
  }
  .compact .meta { flex: none; gap: 6px; }
  .compact .title { flex: none; max-width: 40%; overflow: hidden; text-overflow: ellipsis; }
  .compact .message { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  button.action {
    flex: none; width: 48px; height: 48px; padding: 0; border: 0; border-radius: 50%;
    background: transparent; color: var(--primary-text-color); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
  }
  .compact button.action { margin: -4px 0; } /* keeps the 48 px target inside a 40 px row */
  button.action:focus-visible { outline: 2px solid var(--accent); }
  button.text-button {
    min-height: 40px; padding: 0 12px; border: 0; border-radius: 20px; background: transparent;
    color: var(--primary-color); font: inherit; font-weight: 500; cursor: pointer;
  }
  button.text-button:focus-visible { outline: 2px solid var(--primary-color); }
  .more { display: flex; justify-content: center; padding: 0 8px 8px; }
  .empty {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    padding: 24px 16px; color: var(--secondary-text-color);
  }
  .error { padding: 16px; color: var(--error-color); }
`;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function validColor(value) {
  return typeof CSS === "undefined" || typeof CSS.supports !== "function"
    ? true
    : CSS.supports("color", value);
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
    this._expanded = false;
    this._timeNodes = [];
    this._timeTimer = null;
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
    this._expanded = false;
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
    this._startTimeRefresh();
  }

  disconnectedCallback() {
    this._connected = false;
    this._connection?.removeEventListener("ready", this._onReady);
    this._connection = null;
    this._unsubscribe();
    clearInterval(this._timeTimer);
    this._timeTimer = null;
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

  // The "50 min ago" texts change without a new event, so they are rewritten on a timer.
  _startTimeRefresh() {
    if (this._timeTimer) return;
    this._timeTimer = setInterval(() => {
      const now = Date.now();
      for (const { node, iso } of this._timeNodes) node.textContent = relativeTime(iso, now);
    }, TIME_REFRESH_MS);
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

  _dismissAll(ids) {
    this._hass.callWS({ type: "heads_up/dismiss_many", banner_ids: ids }).catch(() => {});
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

  // Pointer events cover touch, pen and mouse. touch-action: pan-y keeps vertical scrolling with
  // the browser, so only horizontal movements reach this code (D-048, N-49).
  _attachSwipe(node, banner) {
    node.classList.add("swipe");
    let start = null;
    let swiping = false;
    let suppressClick = false;

    const reset = (animate) => {
      node.style.transition = animate ? "transform 0.15s, opacity 0.15s" : "";
      node.style.transform = "";
      node.style.opacity = "";
    };

    node.addEventListener("pointerdown", (ev) => {
      if ((ev.pointerType === "mouse" && ev.button !== 0) || ev.target.closest("button")) return;
      start = { x: ev.clientX, y: ev.clientY, id: ev.pointerId };
      swiping = false;
    });
    node.addEventListener("pointermove", (ev) => {
      if (!start || ev.pointerId !== start.id) return;
      const dx = ev.clientX - start.x;
      const dy = ev.clientY - start.y;
      if (!swiping) {
        if (Math.abs(dy) > SWIPE_START_PX && Math.abs(dy) > Math.abs(dx)) {
          start = null; // a vertical gesture: leave it to the browser
          return;
        }
        if (Math.abs(dx) <= SWIPE_START_PX) return;
        swiping = true;
        node.setPointerCapture(ev.pointerId);
        node.style.transition = "";
      }
      node.style.transform = `translateX(${dx}px)`;
      node.style.opacity = String(1 - Math.min(Math.abs(dx) / node.offsetWidth, 1) * 0.6);
    });
    const finish = (ev) => {
      if (!start || ev.pointerId !== start.id) return;
      const dx = ev.clientX - start.x;
      const dy = ev.clientY - start.y;
      const wasSwiping = swiping;
      start = null;
      swiping = false;
      if (!wasSwiping) return;
      suppressClick = true; // the click that follows a drag must not run the tap action
      setTimeout(() => (suppressClick = false), 0);
      if (ev.type === "pointerup" && swipeOutcome(dx, dy, node.offsetWidth) === "dismiss") {
        node.style.transition = "transform 0.15s, opacity 0.15s";
        node.style.transform = `translateX(${dx < 0 ? "-" : ""}${node.offsetWidth}px)`;
        node.style.opacity = "0";
        this._dismiss(banner);
      } else {
        reset(true);
      }
    };
    node.addEventListener("pointerup", finish);
    node.addEventListener("pointercancel", finish);
    node.addEventListener(
      "click",
      (ev) => {
        if (suppressClick) {
          ev.stopImmediatePropagation();
          ev.preventDefault();
        }
      },
      true,
    );
  }

  _bannerNode(banner, isAdmin, colors) {
    const cfg = this._config;
    const controls = controlsFor(banner, isAdmin);
    const parts = colorParts(cfg.colorize);
    const classes = ["banner"];
    if (parts.background) classes.push("c-bg");
    if (parts.icon) classes.push("c-icon");
    if (parts.bar) classes.push("c-bar");
    if (controls.tap) classes.push("tap");
    const node = el("div", classes.join(" "));
    const color = validColor(colors[banner.severity])
      ? colors[banner.severity]
      : `var(${SEVERITY_COLOR[banner.severity] ?? "--info-color"})`;
    node.style.setProperty("--accent", color);
    if (cfg.layout === "compact") {
      node.title = banner.title ? `${banner.title}: ${banner.message}` : banner.message;
    }

    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", banner.icon);
    icon.setAttribute("aria-hidden", "true");
    node.append(icon);

    const text = el("div", "text");
    const meta = el("div", "meta");
    const severity = STRINGS.severity[banner.severity] ?? banner.severity;
    // The label stays in the page for screen readers when it is not shown (D-048).
    meta.append(el("span", cfg.show_severity ? "label" : "sr-only", severity));
    if (cfg.show_time) {
      const time = el("span", "time", relativeTime(banner.updated_at));
      this._timeNodes.push({ node: time, iso: banner.updated_at });
      meta.append(time);
    }
    text.append(meta);
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
    if (cfg.swipe_to_dismiss && controls.dismiss) this._attachSwipe(node, banner);

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

  _header(clearable) {
    const cfg = this._config;
    const showClear = cfg.clear_all && clearable.length > 0;
    if (cfg.title === "" && !showClear) return null;
    const header = el("div", "header");
    header.append(el("div", "card-title", cfg.title));
    if (showClear) {
      const b = el("button", "text-button", STRINGS.clear_all);
      b.type = "button";
      b.addEventListener("click", () => this._dismissAll(clearable));
      header.append(b);
    }
    return header;
  }

  _render() {
    const root = this.shadowRoot;
    root.replaceChildren();
    this._timeNodes = [];
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

    const cfg = this._config;
    const all = this._shown();
    if (all.length === 0) {
      const view = emptyView(cfg);
      if (view === "hidden") {
        this.style.display = "none";
        return;
      }
      this.style.display = "";
      const card = el("ha-card");
      const header = this._header([]);
      if (header) card.append(header);
      if (view === "message") {
        const empty = el("div", "empty");
        const icon = document.createElement("ha-icon");
        icon.setAttribute("icon", cfg.empty_icon);
        icon.setAttribute("aria-hidden", "true");
        empty.append(icon, el("div", "empty-text", cfg.empty_message));
        card.append(empty);
      }
      root.append(card);
      return;
    }
    this.style.display = "";

    const { shown, hidden } = collapse(all, cfg.collapsed_items, this._expanded);
    const isAdmin = this._hass?.user?.is_admin === true;
    const colors = resolveColors(cfg);
    const card = el("ha-card");
    const header = this._header(clearableIds(all));
    if (header) card.append(header);
    const list = el("div", `list ${cfg.layout}`);
    // Critical banners are announced at once, the rest politely.
    const assertive = el("div", "region");
    assertive.setAttribute("aria-live", "assertive");
    const polite = el("div", "region");
    polite.setAttribute("aria-live", "polite");
    for (const banner of shown) {
      (banner.severity === "critical" ? assertive : polite).append(
        this._bannerNode(banner, isAdmin, colors),
      );
    }
    list.append(assertive, polite);
    card.append(list);
    if (hidden > 0) {
      const more = el("div", "more");
      const b = el(
        "button",
        "text-button",
        this._expanded ? STRINGS.show_less : STRINGS.show_more.replace("{n}", hidden),
      );
      b.type = "button";
      b.addEventListener("click", () => {
        this._expanded = !this._expanded;
        this._render();
      });
      more.append(b);
      card.append(more);
    }
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
    const select = (name, options) => ({
      name,
      selector: { select: { mode: "dropdown", options } },
    });
    return [
      { name: "title", selector: { text: {} } },
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
      { name: "collapsed_items", selector: { number: { min: 1, step: 1, mode: "box" } } },
      select("sort", [
        { value: "severity", label: t.sort_severity },
        { value: "time", label: t.sort_time },
      ]),
      select("layout", [
        { value: "comfortable", label: t.layout_comfortable },
        { value: "compact", label: t.layout_compact },
      ]),
      { name: "show_time", selector: { boolean: {} } },
      { name: "show_severity", selector: { boolean: {} } },
      select("colorize", COLORIZE.map((v) => ({ value: v, label: t[`colorize_${v}`] }))),
      {
        name: "colors",
        type: "expandable",
        schema: SEVERITIES.map((s) => ({ name: s, selector: { text: {} } })),
      },
      { name: "clear_all", selector: { boolean: {} } },
      { name: "swipe_to_dismiss", selector: { boolean: {} } },
      { name: "show_all", selector: { boolean: {} } },
      { name: "show_empty", selector: { boolean: {} } },
      { name: "empty_message", selector: { text: {} } },
      { name: "empty_icon", selector: { icon: {} } },
    ];
  }

  _update() {
    if (!this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.computeLabel = (schema) =>
        STRINGS.editor[schema.name] ?? STRINGS.severity[schema.name] ?? schema.name;
      this._form.addEventListener("value-changed", (ev) => {
        ev.stopPropagation();
        const config = { ...ev.detail.value };
        if (config.colors && typeof config.colors === "object") {
          config.colors = Object.fromEntries(
            Object.entries(config.colors).filter(([, v]) => typeof v === "string" && v.trim() !== ""),
          );
        }
        // Keep the saved YAML minimal: no cleared values, no values equal to the default,
        // no switches that are off.
        for (const key of Object.keys(config)) {
          const v = config[key];
          const empty =
            v === undefined ||
            v === null ||
            v === "" ||
            v === false ||
            (Array.isArray(v) && v.length === 0) ||
            (key === "colors" && Object.keys(v).length === 0) ||
            EDITOR_DEFAULTS[key] === v;
          if (empty) delete config[key];
        }
        this.dispatchEvent(
          new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config } }),
        );
      });
      this.append(this._form);
    }
    this._form.hass = this._hass;
    this._form.schema = this._schema();
    this._form.data = { ...EDITOR_DEFAULTS, ...this._config };
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
