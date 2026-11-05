// Heads Up popup (docs/configuration.md#popup). Imported by the loader when the first popup is due.
// Plain ES module, no build step (D-021, D-115). Message text only via textContent.

const SEVERITY_RANK = { critical: 3, warning: 2, info: 1, success: 0 };
const COLOR = {
  critical: "var(--error-color, #db4437)",
  warning: "var(--warning-color, #ffa600)",
  info: "var(--info-color, #4285f4)",
  success: "var(--success-color, #43a047)",
};

export const STRINGS = {
  en: { dismiss: "Dismiss", snooze: "Snooze", ack: "Acknowledge", close: "Close", critical: "Critical", warning: "Warning", info: "Info", success: "Success" },
  de: { dismiss: "Schließen", snooze: "Später", ack: "Bestätigen", close: "Ausblenden", critical: "Kritisch", warning: "Warnung", info: "Info", success: "Erfolg" },
  fr: { dismiss: "Fermer", snooze: "Reporter", ack: "Confirmer", close: "Masquer", critical: "Critique", warning: "Avertissement", info: "Info", success: "Succès" },
  es: { dismiss: "Descartar", snooze: "Posponer", ack: "Confirmar", close: "Ocultar", critical: "Crítico", warning: "Aviso", info: "Info", success: "Éxito" },
};

export function text(language, key) {
  const table = STRINGS[String(language || "en").split("-")[0]] || STRINGS.en;
  return table[key] ?? STRINGS.en[key];
}

// Highest severity first, then the oldest first (the order they should be read in).
export function sortQueue(messages) {
  return [...messages].sort(
    (a, b) =>
      (SEVERITY_RANK[b.severity] ?? 0) - (SEVERITY_RANK[a.severity] ?? 0) ||
      String(a.created_at).localeCompare(String(b.created_at)) ||
      String(a.id).localeCompare(String(b.id)),
  );
}

// What is shown now: the first message of the queue that was not closed on this page.
export function current(messages, closed) {
  return sortQueue(messages).find((m) => !closed.has(m.id)) || null;
}

// "card" in a corner or "modal" in the middle; the server decides per severity (D-090, D-180).
export function styleOf(message) {
  return message.style === "modal" ? "modal" : "card";
}

// The corner of a card: br (the default), bl, tr or tl.
const CORNERS = { card: "br", card_bottom_left: "bl", card_top_right: "tr", card_top_left: "tl" };
export function cornerOf(message) {
  return CORNERS[message.style] || "br";
}

// A modal may take focus when it is critical or nothing is being typed; a card never does.
export function mayTakeFocus(message, activeTag) {
  if (styleOf(message) !== "modal") return false;
  if (message.severity === "critical") return true;
  return !["INPUT", "TEXTAREA", "SELECT"].includes(String(activeTag || "").toUpperCase());
}

// Paths on this Home Assistant behind a login need a signed URL before an <img> can load them;
// /local and external URLs do not (N-93). Same rule as the card.
export function needsSignature(path) {
  return typeof path === "string" && (path.startsWith("/api/") || path.startsWith("/media/"));
}

const signedImages = new Map(); // path -> { src, until }

export async function imageSource(hass, path, now = Date.now()) {
  if (!needsSignature(path)) return path;
  const known = signedImages.get(path);
  if (known && known.until > now) return known.src;
  const signed = await hass.callWS({ type: "auth/sign_path", path, expires: 3600 });
  signedImages.set(path, { src: signed.path, until: now + 50 * 60 * 1000 });
  return signed.path;
}

// Buttons in the order the card uses: the message's own, Acknowledge, Snooze, Dismiss.
export function buttonsFor(message) {
  const own = (message.actions || []).map((a) => ({ kind: "action", key: a.key, label: a.label }));
  const out = [...own];
  if (message.ack) out.push({ kind: "ack" });
  if (message.snoozable && message.snooze_seconds) {
    out.push({ kind: "snooze", seconds: message.snooze_seconds });
  }
  if (message.dismissible) out.push({ kind: "dismiss" });
  return out;
}

const CSS = `
:host { all: initial; }
.card, .modal { font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); color: var(--primary-text-color, #212121);
  background: var(--card-background-color, #fff); border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.3); }
.card { position: fixed; right: 16px; bottom: 16px; width: min(360px, calc(100vw - 32px)); z-index: 8; padding: 12px 16px; border-left: 6px solid var(--c); }
.card[data-pos="bl"] { left: 16px; right: auto; }
.card[data-pos="tr"] { top: 16px; bottom: auto; }
.card[data-pos="tl"] { left: 16px; right: auto; top: 16px; bottom: auto; }
.scrim { position: fixed; inset: 0; z-index: 9; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; }
.modal { width: min(480px, calc(100vw - 32px)); max-height: calc(100vh - 32px); overflow: auto; padding: 16px 20px; border-top: 8px solid var(--c); }
.sev { font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--c); display: flex; gap: 6px; align-items: center; }
.title { font-size: 18px; font-weight: 600; margin: 4px 0; overflow-wrap: anywhere; }
.image { display: block; width: 100%; max-height: 200px; margin: 0 0 12px; border-radius: 8px; object-fit: cover; }
.msg { margin: 4px 0 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
.row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
button { min-height: 48px; min-width: 48px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color, #ccc);
  background: transparent; color: var(--primary-text-color, #212121); font: inherit; cursor: pointer; }
button:focus-visible { outline: 3px solid var(--primary-color, #03a9f4); outline-offset: 2px; }
button.main { background: var(--primary-color, #03a9f4); color: var(--text-primary-color, #fff); border-color: transparent; }
.x { position: absolute; top: 4px; right: 4px; border: none; font-size: 20px; }
.modal { position: relative; }
@media (prefers-reduced-motion: no-preference) { .card, .modal { animation: in .2s ease-out; } @keyframes in { from { opacity: 0; transform: translateY(8px); } }
  .card[data-pos="tr"], .card[data-pos="tl"] { animation-name: in-top; } @keyframes in-top { from { opacity: 0; transform: translateY(-8px); } } }
`;

let host = null;
let root = null;
let lastFocus = null;
const closed = new Set();
let state = { ha: null, messages: [] };

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  Object.assign(node, props);
  for (const child of children) node.append(child);
  return node;
}

function call(message, payload) {
  const connection = state.ha?.hass?.connection;
  return connection ? connection.sendMessagePromise({ ...payload, banner_id: message.id }) : Promise.resolve();
}

function pressed(message, button) {
  if (button.kind === "action") return call(message, { type: "heads_up/action", key: button.key });
  if (button.kind === "snooze") return call(message, { type: "heads_up/snooze", seconds: button.seconds });
  if (button.kind === "dismiss") return call(message, { type: "heads_up/dismiss" });
  return call(message, { type: "heads_up/acknowledge" });
}

function close(message) {
  closed.add(message.id);
  render();
}

function build(message, language) {
  const style = styleOf(message);
  const t = (key) => text(language, key);
  const box = el("div", {
    className: style,
    role: style === "modal" ? "alertdialog" : "status",
    tabIndex: -1,
  });
  box.style.setProperty("--c", COLOR[message.severity] || COLOR.info);
  if (style === "card") box.dataset.pos = cornerOf(message);
  if (style === "modal") box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", message.title || message.message);
  const label = el("div", { className: "sev" });
  if (message.icon) label.append(el("ha-icon", { icon: message.icon }));
  label.append(el("span", { textContent: t(message.severity) }));
  box.append(label);
  if (message.title) box.append(el("div", { className: "title", textContent: message.title }));
  box.append(el("div", { className: "msg", textContent: message.message }));
  if (message.image && state.ha?.hass) {
    const picture = el("img", { className: "image", alt: "", loading: "lazy" });
    imageSource(state.ha.hass, message.image)
      .then((src) => (picture.src = src))
      .catch(() => picture.remove());
    picture.addEventListener("error", () => picture.remove());
    box.append(picture);
  }
  const row = el("div", { className: "row" });
  for (const button of buttonsFor(message)) {
    const labelText = button.kind === "action" ? button.label : t(button.kind === "ack" ? "ack" : button.kind);
    const node = el("button", { type: "button", textContent: labelText });
    if (button.kind === "dismiss" || button.kind === "ack") node.className = "main";
    node.addEventListener("click", () => {
      pressed(message, button).catch(() => {});
      if (button.kind === "ack") close(message); // seen: hide here, the banner stays
    });
    row.append(node);
  }
  box.append(row);
  const x = el("button", { type: "button", className: "x", textContent: "×" });
  x.setAttribute("aria-label", t("close"));
  x.addEventListener("click", () => close(message));
  box.append(x);
  box.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.stopPropagation();
      close(message);
    } else if (event.key === "Tab" && style === "modal") {
      const items = [...box.querySelectorAll("button")];
      const first = items[0];
      const last = items[items.length - 1];
      const active = root.activeElement;
      if (event.shiftKey && (active === first || active === box)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
  return { box, style };
}

function render() {
  const message = current(state.messages, closed);
  if (!message) {
    host?.remove();
    host = root = null;
    if (lastFocus?.isConnected) lastFocus.focus();
    lastFocus = null;
    return;
  }
  if (!host) {
    host = document.createElement("div");
    host.id = "heads-up-popup";
    root = host.attachShadow({ mode: "open" });
    root.append(el("style", { textContent: CSS }));
    document.body.append(host);
  }
  for (const node of [...root.children]) if (node.tagName !== "STYLE") node.remove();
  const { box, style } = build(message, state.ha?.hass?.language);
  if (style === "modal") {
    const scrim = el("div", { className: "scrim" }, [box]);
    root.append(scrim);
  } else {
    root.append(box);
  }
  if (mayTakeFocus(message, document.activeElement?.tagName)) {
    lastFocus ||= document.activeElement;
    box.querySelector("button")?.focus();
  }
}

// Called by the loader with every change of this user's popups.
export function show(ha, messages) {
  state = { ha, messages };
  const ids = new Set(messages.map((m) => m.id));
  for (const id of closed) if (!ids.has(id)) closed.delete(id); // a resolved message may come back
  render();
}
