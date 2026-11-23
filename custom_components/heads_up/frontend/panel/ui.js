// Heads Up panel: helpers the editor pages share (D-119). The shell loads this module once and
// passes it to every page as ctx.ui, so a page never imports another file by a bare URL.

export function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(typeof child === "string" ? document.createTextNode(child) : child);
  return created;
}

// Redrawing a page empties it first, so for a moment it is shorter than the screen and the browser
// resets the scroll position to the top (seen on an iPhone when a channel is ticked in Test send).
// Hold the old height until the redraw is on screen, and put every scroll position that was set
// back afterwards, wherever the page scrolls (the window or a container of Home Assistant).
export function lockHeight(root) {
  const saved = [];
  const scroller = document.scrollingElement;
  if (scroller?.scrollTop) saved.push([scroller, scroller.scrollTop]);
  for (let n = root; n; ) {
    if (n.scrollTop && n !== scroller) saved.push([n, n.scrollTop]);
    const top = n.getRootNode?.();
    n = n.parentElement || (top && top.host ? top.host : null);
  }
  root.style.minHeight = `${root.offsetHeight}px`;
  const restore = () => {
    for (const [node, top] of saved) if (node.scrollTop !== top) node.scrollTop = top;
  };
  // Timers, not frame callbacks: a page in a background tab gets no frames.
  setTimeout(restore, 0);
  setTimeout(() => {
    restore();
    root.style.minHeight = "";
  }, 100);
}

// A YAML text with a Copy button under it. The clipboard API needs a secure page; the fallback
// selects a hidden textarea, which also works on a plain http address.
export function yamlBlock(text, common) {
  const status = el("span", { className: "hint", style: "margin-left:8px" });
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const button = el("button", { type: "button", textContent: common.copy });
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      status.textContent = common.copied;
    } catch (err) {
      const area = el("textarea", { value: text, style: "position:fixed;opacity:0" });
      document.body.append(area);
      area.select();
      let done = false;
      try {
        done = document.execCommand("copy");
      } catch (e) {
        done = false;
      }
      area.remove();
      status.textContent = done ? common.copied : common.copy_failed;
    }
  });
  return el("div", {}, [el("pre", { textContent: text }), el("div", { className: "row" }, [button, status])]);
}

// A small "?" button with a short explanation. Hover shows the native tooltip; a click or Enter
// opens the same text under the button, so touch and keyboard users get it too. Place `button`
// next to the label and `note` where the text may appear.
export function helpTip(label, text) {
  const note = el("div", { className: "tip", role: "note", textContent: text });
  const button = el("button", { type: "button", className: "help", textContent: "?", title: text });
  button.setAttribute("aria-label", label);
  button.setAttribute("aria-expanded", "false");
  button.addEventListener("click", () => {
    const open = note.classList.toggle("open");
    button.setAttribute("aria-expanded", String(open));
  });
  return { button, note };
}

// Longer explanations are plain text with paragraphs (a blank line) and bullets ("- " at the start of
// a line). Home Assistant's own forms show the same strings as Markdown, so one text serves both. The
// text is never parsed as HTML.
export function parseRich(text) {
  const blocks = [];
  let paragraph = [];
  let list = null;
  const flush = () => {
    if (paragraph.length) blocks.push({ type: "p", text: paragraph.join(" ") });
    paragraph = [];
  };
  for (const raw of String(text ?? "").split("\n")) {
    const line = raw.trim();
    if (!line) {
      flush();
      list = null;
    } else if (line.startsWith("- ")) {
      flush();
      if (!list) {
        list = { type: "ul", items: [] };
        blocks.push(list);
      }
      list.items.push(line.slice(2));
    } else {
      list = null;
      paragraph.push(line);
    }
  }
  flush();
  return blocks;
}

export function richNode(text, props = {}) {
  const box = el("div", { ...props, className: `rich ${props.className || ""}`.trim() });
  for (const block of parseRich(text)) {
    if (block.type === "p") box.append(el("p", { textContent: block.text }));
    else box.append(el("ul", {}, block.items.map((item) => el("li", { textContent: item }))));
  }
  return box;
}

export const BASE_CSS = `
.hu-page .rich p { margin: 0 0 8px; }
.hu-page .rich ul { margin: 0 0 8px; padding-left: 20px; list-style: disc; }
.hu-page .rich li { margin: 3px 0; padding: 0; border: 0; }
.hu-page .rich > :last-child { margin-bottom: 0; }
.hu-page section, .hu-page .card { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.hu-page h1 { font-size: 22px; margin: 0 0 16px; }
.hu-page h2 { font-size: 16px; margin: 0 0 8px; }
.hu-page .sub { color: var(--secondary-text-color); font-size: 13px; }
.hu-page .sub.shadowed { color: var(--warning-color, #b26a00); }
.hu-page .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; }
.hu-page ul.list { list-style: none; margin: 0 0 16px; padding: 0; }
.hu-page ul.list li { display: flex; gap: 8px; align-items: center; justify-content: space-between; padding: 8px 0; border-top: 1px solid var(--divider-color); min-height: 48px; }
.hu-page ul.list li:first-child { border-top: 0; }
.hu-page ul.list li.dim { opacity: .55; }
.hu-page code.entity { display: block; margin-top: 2px; font-size: 11px; color: var(--secondary-text-color); overflow-wrap: anywhere; }
.hu-page ul.list li > div:first-child { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.hu-page ul.list li > button { flex: none; }
.hu-page button.help { min-width: 24px; min-height: 24px; width: 24px; height: 24px; padding: 0; margin-left: 6px; border-radius: 50%; border: 1px solid var(--divider-color); background: transparent; color: var(--secondary-text-color); font: inherit; font-size: 13px; line-height: 1; cursor: help; vertical-align: middle; }
.hu-page button.help[aria-expanded="true"], .hu-page button.help:hover { color: var(--primary-text-color); border-color: var(--primary-text-color); }
.hu-page button.help:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-page .tip { display: none; margin: 6px 0; padding: 8px 10px; border-radius: 8px; background: var(--secondary-background-color); color: var(--primary-text-color); font-size: 13px; font-weight: normal; max-width: 460px; }
.hu-page .tip.open { display: block; }
.hu-page { --hu-line: color-mix(in srgb, var(--primary-text-color) 40%, transparent); --hu-fill: color-mix(in srgb, var(--primary-text-color) 9%, var(--card-background-color)); }
.hu-page .badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 12px; padding: 2px 10px; font-size: 12px; background: var(--hu-fill); border: 1px solid var(--hu-line); }
.hu-page .badge.bad { color: var(--error-color); border-color: var(--error-color); }
.hu-page .badge.on { color: var(--success-color); border-color: var(--success-color); }
.hu-page .badge.on::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
.hu-page .badge.sev { border-radius: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: .03em; font-size: 11px; }
.hu-page .badge.sev-info { color: var(--info-color); border-color: var(--info-color); }
.hu-page .badge.sev-warning { color: var(--warning-color); border-color: var(--warning-color); }
.hu-page .badge.sev-critical { color: var(--error-color); border-color: var(--error-color); }
.hu-page .badges { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 4px 0 6px; }
.hu-page code.tpl { display: block; margin-top: 4px; padding: 4px 8px; border-radius: 6px; background: var(--hu-fill); color: var(--secondary-text-color); font-size: 12px; overflow-wrap: anywhere; }
.hu-page label.field { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
.hu-page label.inline { display: flex; align-items: center; gap: 10px; min-height: 48px; }
.hu-page input[type=text], .hu-page input[type=number], .hu-page input[type=time], .hu-page select, .hu-page textarea { box-sizing: border-box; height: 44px; padding: 0 12px; border-radius: 8px; border: 1px solid var(--hu-line); background: var(--hu-fill); color: var(--primary-text-color); font: inherit; width: 100%; max-width: 360px; }
.hu-page textarea { height: auto; min-height: 88px; padding: 10px 12px; max-width: none; resize: vertical; }
.hu-page input[type=text]:hover, .hu-page input[type=number]:hover, .hu-page input[type=time]:hover, .hu-page select:hover { border-color: var(--primary-text-color); }
.hu-page section > select, .hu-page fieldset > select { display: block; margin-bottom: 20px; }
.hu-page .hu-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.hu-page .seg { display: inline-flex; border: 1px solid var(--divider-color); border-radius: 8px; overflow: hidden; }
.hu-page .seg button { border: 0; border-radius: 0; padding: 8px 14px; background: transparent; color: var(--primary-text-color); cursor: pointer; font: inherit; }
.hu-page .seg button[aria-pressed=true] { background: var(--primary-color); color: var(--text-primary-color, #fff); }
.hu-page .stack { display: grid; gap: 6px; padding-bottom: 8px; }
.hu-page .stack > .field, .hu-page .stack > fieldset, .hu-page .stack > .btn-row, .hu-page .stack > .action-editor { margin: 0; }
.hu-page .btn-row .field, .hu-page .action-editor .field { margin: 0; }
.hu-page details.fold { margin: 12px 0; padding: 4px 12px; border: 1px solid var(--divider-color); border-radius: 8px; }
.hu-page details.fold > summary { padding: 8px 0; font-weight: 600; cursor: pointer; }
.hu-page .btn-row { display: grid; gap: 8px; padding: 12px; margin: 8px 0; border: 1px solid var(--divider-color); border-radius: 8px; }
.hu-page .action-editor { display: grid; gap: 8px; }
.hu-page .color-input { display: flex; gap: 8px; align-items: center; }
.hu-page .color-input input[type=text] { flex: 1; max-width: 12em; }
.hu-page .color-input input[type=color] { flex: none; width: 44px; height: 36px; padding: 0; border: 1px solid var(--divider-color); border-radius: 6px; background: none; cursor: pointer; }
.hu-page input[type=checkbox], .hu-page input[type=radio] { appearance: none; -webkit-appearance: none; flex: none; width: 22px; height: 22px; margin: 0; border: 2px solid var(--primary-text-color); background: transparent; cursor: pointer; }
.hu-page input[type=checkbox] { border-radius: 5px; }
.hu-page input[type=radio] { border-radius: 50%; }
.hu-page input[type=checkbox]:checked { background: var(--primary-color) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 100% no-repeat; border-color: var(--primary-color); }
.hu-page input[type=radio]:checked { border-color: var(--primary-color); background: radial-gradient(var(--primary-color) 0 45%, transparent 50%); }
.hu-page h2 { margin-bottom: 12px; }
.hu-page fieldset { border: 1px solid var(--hu-line); border-radius: 8px; margin: 0 0 20px; padding: 12px 16px; }
.hu-page details.multi { border: 1px solid var(--hu-line); border-radius: 4px; padding: 0 12px; }
.hu-page details.multi > summary { padding: 10px 0; cursor: pointer; }
.hu-page details.multi .multi-list { max-height: 200px; overflow: auto; padding-bottom: 8px; }
.hu-page fieldset.scroll { max-height: 200px; overflow: auto; }
.hu-page legend { padding: 0 6px; color: var(--secondary-text-color); font-size: 13px; }
.hu-page button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--hu-line); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-page button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-page button.danger { color: var(--error-color); border-color: var(--error-color); }
.hu-page button:disabled { opacity: .5; cursor: default; }
.hu-page button:focus-visible, .hu-page input:focus-visible, .hu-page select:focus-visible, .hu-page textarea:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-page .problems { color: var(--error-color); }
.hu-page .ok { color: var(--success-color); }
.hu-page pre { background: var(--secondary-background-color); border-radius: 8px; padding: 10px; overflow: auto; font-size: 12px; margin: 4px 0 12px; }
.hu-page .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
`;

// A table-like list (Severities, Audiences, Channels): column headers and one grid row per item on a
// wide page; on a phone the header hides and each row shows its lead line with the cells below,
// each with its own small label. A row is a button that opens its details underneath. The page sets
// the columns with --tl-cols on the list.
export const TABLE_CSS = `
.hu-page .tl-list { container-type: inline-size; padding: 4px 0; overflow: hidden; --tl-cols: minmax(0, 1.3fr) minmax(0, 1fr) minmax(0, 1fr); }
.hu-page .tl-head, .hu-page .tl-row { display: grid; grid-template-columns: var(--tl-cols) 52px; gap: 12px; align-items: center; padding: 0 16px; }
.hu-page .tl-head { min-height: 36px; color: var(--secondary-text-color); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
.hu-page .tl-item { border-top: 1px solid var(--divider-color); }
.hu-page .tl-item.dim .tl-row > :not(.tl-end) { opacity: .55; }
.hu-page .tl-row { width: 100%; min-height: 56px; border: 0; border-radius: 0; background: transparent; text-align: left; font: inherit; color: var(--primary-text-color); }
.hu-page .tl-row:hover, .hu-page .tl-item.open .tl-row { background: var(--hu-fill); }
.hu-page .tl-row:focus-visible { outline-offset: -3px; }
.hu-page .tl-lead { display: flex; align-items: center; gap: 10px; min-width: 0; font-weight: 600; }
.hu-page .tl-lead ha-icon { --mdc-icon-size: 22px; flex: none; }
.hu-page .tl-lead .tl-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hu-page .tl-lead .badge { font-weight: 400; }
.hu-page .tl-meta { display: contents; }
.hu-page .tl-cell { min-width: 0; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hu-page .tl-cell.muted { color: var(--secondary-text-color); }
.hu-page .tl-k { display: none; }
.hu-page .tl-end { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.hu-page .tl-mark { color: var(--primary-color); font-size: 12px; }
.hu-page .tl-chev { width: 8px; height: 8px; border-right: 2px solid var(--secondary-text-color); border-bottom: 2px solid var(--secondary-text-color); transform: rotate(45deg); margin: 0 6px 4px 0; transition: transform .15s; }
.hu-page .tl-item.open .tl-chev { transform: rotate(-135deg); margin-bottom: -4px; }
.hu-page .tl-body { padding: 12px 16px 16px; background: var(--hu-fill); }
.hu-page .tl-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px 16px; }
.hu-page .tl-grid label.field, .hu-page .tl-body label.field { margin: 0; gap: 6px; font-size: 14px; }
.hu-page .tl-grid input[type=text], .hu-page .tl-grid input[type=number], .hu-page .tl-grid select, .hu-page .tl-grid textarea { width: 100%; max-width: none; }
.hu-page .tl-wide { grid-column: 1 / -1; }
.hu-page .tl-facts { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 8px 16px; margin: 0 0 12px; font-size: 14px; }
.hu-page .tl-facts dt { color: var(--secondary-text-color); }
.hu-page .tl-facts dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
.hu-page .tl-facts code { font-size: 12px; }
.hu-page .tl-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 12px; }
.hu-page .tl-empty { padding: 12px 16px; color: var(--secondary-text-color); font-size: 14px; }
.hu-page .tl-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 12px 0; background: var(--primary-background-color); }
.hu-page .tl-bar.dirty { position: sticky; bottom: 0; z-index: 1; }
.hu-page .tl-bar .hint { margin: 0; flex: 1; min-width: 160px; }
@container (max-width: 520px) {
  .hu-page .tl-head { display: none; }
  .hu-page .tl-head + .tl-item, .hu-page .tl-list > .tl-item:first-child { border-top: 0; }
  .hu-page .tl-row { grid-template-columns: minmax(0, 1fr) 52px; row-gap: 2px; padding: 8px 16px; }
  .hu-page .tl-meta { display: flex; flex-wrap: wrap; gap: 2px 16px; grid-column: 1; grid-row: 2; color: var(--secondary-text-color); }
  .hu-page .tl-cell { font-size: 13px; white-space: normal; overflow-wrap: anywhere; }
  .hu-page .tl-k { display: inline; margin-right: 4px; }
  .hu-page .tl-k::after { content: ":"; }
  .hu-page .tl-end { grid-column: 2; grid-row: 1 / span 2; }
  .hu-page .tl-grid { grid-template-columns: 1fr; }
  .hu-page .tl-facts { grid-template-columns: 1fr; gap: 2px; }
  .hu-page .tl-facts dd { margin-bottom: 8px; }
}
`;

// The header row of a table-like list; hidden from screen readers, which hear each row's label.
export function tableHead(labels) {
  const head = el("div", { className: "tl-head" }, labels.map((text) => el("span", { textContent: text })));
  head.setAttribute("aria-hidden", "true");
  return head;
}

// One row: `lead` is the first column, `cells` the others ({ label, node }), `end` sits before the
// chevron. The row toggles its details; `body` is shown under it while open.
export function tableRow({ id, lead, cells = [], end = [], open = false, dim = false, label, onToggle, body }) {
  const row = el("button", { type: "button", className: "tl-row" }, [
    el("span", { className: "tl-lead" }, lead),
    el("span", { className: "tl-meta" }, cells.map((c) => el("span", { className: `tl-cell ${c.muted ? "muted" : ""}` }, [...(c.label ? [el("span", { className: "tl-k", textContent: c.label })] : []), c.node]))),
    el("span", { className: "tl-end" }, [...end, el("span", { className: "tl-chev" })]),
  ]);
  row.setAttribute("aria-expanded", String(open));
  row.setAttribute("aria-controls", id);
  if (label) row.setAttribute("aria-label", label);
  row.addEventListener("click", onToggle);
  const item = el("div", { className: `tl-item${open ? " open" : ""}${dim ? " dim" : ""}` }, [row]);
  if (open && body) {
    body.id = id;
    body.classList.add("tl-body");
    item.append(body);
  }
  return { item, row };
}

// A list of facts as label and value pairs, two columns on a wide page.
export function facts(pairs) {
  return el("dl", { className: "tl-facts" }, pairs.flatMap(([label, value]) => [el("dt", { textContent: label }), el("dd", {}, [typeof value === "string" ? document.createTextNode(value) : value])]));
}

// YAML of stored data, shown under every editor so nothing is hidden (UX_SPEC).
export function toYaml(value, indent = 0) {
  const pad = " ".repeat(indent);
  if (Array.isArray(value)) {
    if (value.length === 0) return "[]";
    return value
      .map((item) =>
        item !== null && typeof item === "object"
          ? `${pad}- ${toYaml(item, indent + 2).trimStart()}`
          : `${pad}- ${scalar(item)}`,
      )
      .join("\n");
  }
  if (value !== null && typeof value === "object") {
    const keys = Object.keys(value);
    if (keys.length === 0) return "{}";
    return keys
      .map((key) => {
        const item = value[key];
        if (item !== null && typeof item === "object" && Object.keys(item).length > 0) {
          return `${pad}${key}:\n${toYaml(item, indent + 2)}`;
        }
        return `${pad}${key}: ${item !== null && typeof item === "object" ? toYaml(item) : scalar(item)}`;
      })
      .join("\n");
  }
  return scalar(value);
}

// A plain scalar only for words YAML reads as text; anything else is quoted. A time such as
// 22:00:00 is quoted too: YAML 1.1 reads it as a number of seconds.
function scalar(value) {
  if (value === null || value === undefined) return "null";
  if (typeof value !== "string") return String(value);
  const plain = /^[A-Za-z_][A-Za-z0-9_.()-]*( [A-Za-z0-9_.()-]+)*$/.test(value) && !/^(true|false|null|yes|no|on|off)$/i.test(value);
  return plain ? value : JSON.stringify(value);
}

export function splitTags(text) {
  return [...new Set(String(text || "").split(",").map((tag) => tag.trim()).filter(Boolean))];
}

export function joinTags(list) {
  return (list || []).join(", ");
}

// Flow errors are translation keys of the integration; the panel words them itself.
export const ERRORS = {
  en: {
    name_required: "Enter a name.",
    name_exists: "This name is already used.",
    name_has_suffix: "The name must not end with (group): calls add it themselves.",
    persons_required: "Choose at least one person.",
    presence_required: "Choose which presence this audience follows.",
    zone_required: "Choose a zone.",
    group_empty: "Choose at least one speaker or area.",
    member_not_found: "One of the speakers does not exist.",
    area_not_found: "One of the areas does not exist.",
    person_not_found: "This person does not exist.",
    profile_exists: "This person already has a profile.",
    device_unknown: "One of the devices is not a Companion registration.",
    device_added_and_removed: "A device cannot be both added and removed.",
    channels_required: "Choose at least one channel.",
    channel_unknown: "This channel cannot be used here.",
    after_required: "Enter a time of at least one minute.",
    every_required: "Enter a time of at least one minute.",
    max_required: "Enter at least one reminder.",
    window_empty: "The window must start and end at different times.",
    quiet_entity_invalid: "Choose a schedule, an input boolean or a binary sensor.",
    time_invalid: "Enter a valid time.",
    wait_invalid: "Enter 0 or more minutes.",
    when_required: "Choose when to use this fallback.",
    target_exclusive: "Give either an audience or recipients for this channel.",
    nothing_new: "Take either the channels or the recipients from the call, not both: the policy would add nothing.",
    target_required: "Give the people or the speakers who should receive it.",
    audience_unknown: "This audience does not exist.",
    recipient_unknown: "One of these recipients is not known for this channel.",
    policy_duplicate: "Another policy of this type already applies to the same messages with the same trigger.",
    flow_failed: "Home Assistant could not save this. Try again.",
  },
  de: {
    name_required: "Gib einen Namen ein.",
    name_exists: "Dieser Name wird schon verwendet.",
    name_has_suffix: "Der Name darf nicht auf (group) enden: Aufrufe ergänzen es selbst.",
    persons_required: "Wähle mindestens eine Person.",
    presence_required: "Wähle, welcher Anwesenheit diese Zielgruppe folgt.",
    zone_required: "Wähle eine Zone.",
    group_empty: "Wähle mindestens einen Lautsprecher oder Bereich.",
    member_not_found: "Einer der Lautsprecher existiert nicht.",
    area_not_found: "Einer der Bereiche existiert nicht.",
    person_not_found: "Diese Person existiert nicht.",
    profile_exists: "Diese Person hat schon ein Profil.",
    device_unknown: "Eines der Geräte ist keine Companion-Registrierung.",
    device_added_and_removed: "Ein Gerät kann nicht gleichzeitig hinzugefügt und entfernt werden.",
    channels_required: "Wähle mindestens einen Kanal.",
    channel_unknown: "Dieser Kanal kann hier nicht verwendet werden.",
    after_required: "Gib eine Zeit von mindestens einer Minute ein.",
    every_required: "Gib eine Zeit von mindestens einer Minute ein.",
    max_required: "Gib mindestens eine Erinnerung an.",
    window_empty: "Das Zeitfenster muss zu verschiedenen Zeiten beginnen und enden.",
    quiet_entity_invalid: "Wähle einen Zeitplan, einen Eingabe-Schalter oder einen binären Sensor.",
    time_invalid: "Gib eine gültige Uhrzeit ein.",
    wait_invalid: "Gib 0 oder mehr Minuten ein.",
    when_required: "Wähle, wann dieser Ersatz verwendet wird.",
    target_exclusive: "Gib für diesen Kanal entweder eine Zielgruppe oder Empfänger an.",
    nothing_new: "Nimm entweder die Kanäle oder die Empfänger aus dem Aufruf, nicht beides: Die Richtlinie würde nichts hinzufügen.",
    target_required: "Gib die Personen oder Lautsprecher an, die es erhalten sollen.",
    audience_unknown: "Diese Zielgruppe gibt es nicht.",
    recipient_unknown: "Einer dieser Empfänger ist für diesen Kanal nicht bekannt.",
    policy_duplicate: "Eine andere Richtlinie dieser Art gilt schon für dieselben Meldungen mit demselben Auslöser.",
    flow_failed: "Home Assistant konnte das nicht speichern. Versuche es erneut.",
  },
  fr: {
    name_required: "Saisissez un nom.",
    name_exists: "Ce nom est déjà utilisé.",
    name_has_suffix: "Le nom ne doit pas finir par (group) : les appels l'ajoutent eux-mêmes.",
    persons_required: "Choisissez au moins une personne.",
    presence_required: "Choisissez la présence que suit cette audience.",
    zone_required: "Choisissez une zone.",
    group_empty: "Choisissez au moins un haut-parleur ou une zone.",
    member_not_found: "L'un des haut-parleurs n'existe pas.",
    area_not_found: "L'une des zones n'existe pas.",
    person_not_found: "Cette personne n'existe pas.",
    profile_exists: "Cette personne a déjà un profil.",
    device_unknown: "L'un des appareils n'est pas un enregistrement Companion.",
    device_added_and_removed: "Un appareil ne peut pas être à la fois ajouté et retiré.",
    channels_required: "Choisissez au moins un canal.",
    channel_unknown: "Ce canal ne peut pas être utilisé ici.",
    after_required: "Saisissez une durée d'au moins une minute.",
    every_required: "Saisissez une durée d'au moins une minute.",
    max_required: "Saisissez au moins un rappel.",
    window_empty: "La plage doit commencer et finir à des heures différentes.",
    quiet_entity_invalid: "Choisissez un planning, un interrupteur d'entrée ou un capteur binaire.",
    time_invalid: "Saisissez une heure valide.",
    wait_invalid: "Saisissez 0 minute ou plus.",
    when_required: "Choisissez quand utiliser ce repli.",
    target_exclusive: "Indiquez soit une audience soit des destinataires pour ce canal.",
    nothing_new: "Prenez soit les canaux, soit les destinataires de l'appel, pas les deux : la politique n'ajouterait rien.",
    target_required: "Indiquez les personnes ou les haut-parleurs qui doivent le recevoir.",
    audience_unknown: "Cette audience n'existe pas.",
    recipient_unknown: "L'un de ces destinataires est inconnu pour ce canal.",
    policy_duplicate: "Une autre politique de ce type s'applique déjà aux mêmes messages avec le même déclencheur.",
    flow_failed: "Home Assistant n'a pas pu enregistrer. Réessayez.",
  },
  es: {
    name_required: "Introduce un nombre.",
    name_exists: "Este nombre ya se usa.",
    name_has_suffix: "El nombre no debe acabar en (group): las llamadas lo añaden solas.",
    persons_required: "Elige al menos una persona.",
    presence_required: "Elige qué presencia sigue esta audiencia.",
    zone_required: "Elige una zona.",
    group_empty: "Elige al menos un altavoz o área.",
    member_not_found: "Uno de los altavoces no existe.",
    area_not_found: "Una de las áreas no existe.",
    person_not_found: "Esta persona no existe.",
    profile_exists: "Esta persona ya tiene un perfil.",
    device_unknown: "Uno de los dispositivos no es un registro de Companion.",
    device_added_and_removed: "Un dispositivo no puede añadirse y quitarse a la vez.",
    channels_required: "Elige al menos un canal.",
    channel_unknown: "Este canal no se puede usar aquí.",
    after_required: "Introduce un tiempo de al menos un minuto.",
    every_required: "Introduce un tiempo de al menos un minuto.",
    max_required: "Introduce al menos un recordatorio.",
    window_empty: "La franja debe empezar y acabar a horas distintas.",
    quiet_entity_invalid: "Elige un horario, un interruptor de entrada o un sensor binario.",
    time_invalid: "Introduce una hora válida.",
    wait_invalid: "Introduce 0 o más minutos.",
    when_required: "Elige cuándo usar esta alternativa.",
    target_exclusive: "Indica una audiencia o destinatarios para este canal.",
    nothing_new: "Toma de la llamada o los canales o los destinatarios, no ambos: la política no añadiría nada.",
    target_required: "Indica las personas o los altavoces que deben recibirlo.",
    audience_unknown: "Esta audiencia no existe.",
    recipient_unknown: "Uno de estos destinatarios no se conoce para este canal.",
    policy_duplicate: "Otra política de este tipo ya se aplica a los mismos mensajes con el mismo disparador.",
    flow_failed: "Home Assistant no pudo guardarlo. Inténtalo de nuevo.",
  },
};

export function errorText(code, language) {
  const table = ERRORS[String(language || "en").split("-")[0]] || ERRORS.en;
  return table[code] ?? ERRORS.en[code] ?? code;
}

// Save through the integration's own flow (D-119): start a flow for the object, send the whole data,
// and cancel the flow when it returns errors. `errors` maps a field to a translation key.
export async function runFlow(hass, entryId, type, subentryId, data) {
  const start = { handler: [entryId, type], show_advanced_options: false };
  if (subentryId) start.subentry_id = subentryId;
  const base = "config/config_entries/subentries/flow";
  let flow;
  try {
    flow = await hass.callApi("POST", base, start);
    const result = await hass.callApi("POST", `${base}/${flow.flow_id}`, data);
    if (result.type === "form") {
      await hass.callApi("DELETE", `${base}/${flow.flow_id}`).catch(() => {});
      return { ok: false, errors: result.errors || { base: "flow_failed" } };
    }
    return { ok: true, errors: {} };
  } catch (err) {
    if (flow) await hass.callApi("DELETE", `${base}/${flow.flow_id}`).catch(() => {});
    return { ok: false, errors: { base: "flow_failed" } };
  }
}

export function removeSubentry(hass, entryId, subentryId) {
  return hass.callWS({ type: "config_entries/subentries/delete", entry_id: entryId, subentry_id: subentryId });
}

// ---- small form builders: each takes the current value and a change handler ----

export function textInput(value, onInput, props = {}) {
  const input = el("input", { type: "text", value: value ?? "", ...props });
  input.addEventListener("input", () => onInput(input.value));
  return input;
}

// A `#rrggbb` text field with a color picker beside it (D-260). Empty means no color. The text
// is the value: the picker writes into it, and typing a valid value moves the picker.
export function colorInput(value, onInput, props = {}) {
  const valid = (text) => /^#[0-9a-fA-F]{6}$/.test(text);
  const input = el("input", { type: "text", value: value ?? "", spellcheck: false, autocapitalize: "off", ...props });
  const picker = el("input", { type: "color", value: valid(value) ? value : "#03a9f4" });
  picker.setAttribute("aria-label", props["aria-label"] || "Color");
  picker.addEventListener("input", () => {
    input.value = picker.value;
    onInput(input.value);
  });
  input.addEventListener("input", () => {
    if (valid(input.value)) picker.value = input.value;
    onInput(input.value);
  });
  return el("div", { className: "color-input" }, [input, picker]);
}

export function numberInput(value, onInput, props = {}) {
  const input = el("input", { type: "number", value: value ?? "", step: 1, ...props });
  input.addEventListener("input", () => onInput(input.value === "" ? NaN : Number(input.value)));
  return input;
}

export function timeInput(value, onInput) {
  const input = el("input", { type: "time", step: 60, value: String(value || "").slice(0, 5) });
  input.addEventListener("input", () => onInput(input.value ? `${input.value}:00` : ""));
  return input;
}

export function selectInput(options, value, onChange, props = {}) {
  const select = el("select", props);
  for (const option of options) {
    const node = el("option", { value: option.value, textContent: option.label });
    if (option.value === value) node.selected = true;
    select.append(node);
  }
  select.addEventListener("change", () => onChange(select.value));
  return select;
}

export function checkbox(label, checked, onChange) {
  const input = el("input", { type: "checkbox", checked: Boolean(checked) });
  input.addEventListener("change", () => onChange(input.checked));
  return el("label", { className: "inline" }, [input, el("span", { textContent: label })]);
}

// A group of checkboxes for a multiple choice.
export function chips(legend, options, selected, onChange, scroll = false) {
  const box = el("fieldset", { className: scroll ? "scroll" : "" }, [el("legend", { textContent: legend })]);
  const chosen = new Set(selected || []);
  for (const option of options) {
    box.append(
      checkbox(option.label, chosen.has(option.value), (on) => {
        if (on) chosen.add(option.value);
        else chosen.delete(option.value);
        onChange(options.map((o) => o.value).filter((v) => chosen.has(v)).concat([...chosen].filter((v) => !options.some((o) => o.value === v))));
      }),
    );
  }
  return box;
}

// A multiple choice as a dropdown: the closed box lists the chosen labels (or `empty`), the open one
// holds the checkboxes. Takes one line instead of one per option.
export function multiSelect(legend, options, selected, onChange, empty = "") {
  const box = el("details", { className: "multi" });
  const summary = el("summary", {});
  const chosen = new Set(selected || []);
  const sync = () => {
    const names = options.filter((o) => chosen.has(o.value)).map((o) => o.label);
    summary.textContent = names.length ? names.join(", ") : empty;
  };
  sync();
  const list = el("div", { className: "multi-list" });
  for (const option of options) {
    list.append(
      checkbox(option.label, chosen.has(option.value), (on) => {
        if (on) chosen.add(option.value);
        else chosen.delete(option.value);
        sync();
        onChange(options.map((o) => o.value).filter((v) => chosen.has(v)).concat([...chosen].filter((v) => !options.some((o) => o.value === v))));
      }),
    );
  }
  box.append(summary, list);
  return field(legend, box);
}

// The entities whose state is a number now, for a progress bar: [{ value, label }] by name. A value
// that is not in the list (the entity is not numeric at the moment) stays selectable (D-260).
export function numericEntityOptions(states, current = "") {
  const options = Object.entries(states || {})
    .filter(([, state]) => {
      const raw = String(state?.state ?? "").trim();
      return raw !== "" && Number.isFinite(Number(raw));
    })
    .map(([id, state]) => ({ value: id, label: `${state.attributes?.friendly_name || id} (${id})` }))
    .sort((a, b) => a.label.localeCompare(b.label));
  if (current && !options.some((o) => o.value === current)) options.unshift({ value: current, label: current });
  return options;
}

// Buttons and tap action (D-260). The pure functions are tested without a DOM; the two editors
// build on them and are shared by the watch rule form and Test send. Wording comes from the
// page's `s.buttons`.
export const MAX_BUTTONS = 3;
export const ACTION_KINDS = ["none", "navigate", "url", "more-info", "perform-action", "custom"];

export function slugKey(label, taken = []) {
  const base =
    String(label || "")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9_-]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 30) || "button";
  let key = base;
  for (let n = 2; taken.includes(key); n += 1) key = `${base}_${n}`;
  return key;
}

// Which editor shape a stored Home Assistant action has. Other action types are kept as they are.
export function actionKind(action) {
  if (!action || !action.action) return "none";
  if (action.action === "navigate") return "navigate";
  if (action.action === "url") return "url";
  if (action.action === "more-info") return "more-info";
  if (action.action === "perform-action") return "perform-action";
  return "custom";
}

// The editor fields of a stored action.
export function actionFields(action) {
  const a = action || {};
  return {
    kind: actionKind(action),
    path: a.navigation_path ?? "",
    url: a.url_path ?? "",
    entity: a.entity ?? "",
    perform: a.perform_action ?? "",
    target: a.target?.entity_id ?? "",
    data: a.data && Object.keys(a.data).length ? JSON.stringify(a.data) : "",
  };
}

// The action for the editor fields, or null for none. Keys the editor does not know (for example
// `confirmation`) stay when the kind did not change. `data` is the JSON text.
export function actionFromFields(fields, old) {
  const same = actionKind(old) === fields.kind ? old : {};
  const keep = (known) => Object.fromEntries(Object.entries(same || {}).filter(([k]) => !known.includes(k)));
  switch (fields.kind) {
    case "navigate":
      return { ...keep(["navigation_path"]), action: "navigate", navigation_path: fields.path.trim() };
    case "url":
      return { ...keep(["url_path"]), action: "url", url_path: fields.url.trim() };
    case "more-info":
      return { ...keep(["entity"]), action: "more-info", entity: fields.entity.trim() };
    case "perform-action": {
      const out = { ...keep(["perform_action", "target", "data"]), action: "perform-action", perform_action: fields.perform.trim() };
      if (fields.target.trim()) out.target = { entity_id: fields.target.trim() };
      if (fields.data.trim()) {
        try {
          const parsed = JSON.parse(fields.data);
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) out.data = parsed;
        } catch {
          // reported by actionProblem
        }
      }
      return out;
    }
    case "custom":
      return old ?? null;
    default:
      return null;
  }
}

// What is missing in an action, as a code, or "".
export function actionProblem(fields) {
  if (fields.kind === "navigate" && !fields.path.trim()) return "action_incomplete";
  if (fields.kind === "url" && !fields.url.trim()) return "action_incomplete";
  if (fields.kind === "more-info" && !fields.entity.trim()) return "action_incomplete";
  if (fields.kind === "perform-action") {
    if (!fields.perform.trim()) return "action_incomplete";
    if (fields.data.trim()) {
      try {
        const parsed = JSON.parse(fields.data);
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return "data_invalid";
      } catch {
        return "data_invalid";
      }
    }
  }
  return "";
}

// Problems of a button list as [{ index, code }]; the flow checks the rest.
export function buttonProblems(buttons, dismissible) {
  const found = [];
  const keys = new Set();
  buttons.forEach((b, index) => {
    if (!String(b.label || "").trim()) found.push({ index, code: "label_required" });
    if (!/^[a-z0-9_-]+$/.test(b.key || "")) found.push({ index, code: "key_invalid" });
    else if (keys.has(b.key)) found.push({ index, code: "key_duplicate" });
    keys.add(b.key);
    if (b.dismiss && !dismissible) found.push({ index, code: "dismiss_needs_dismissible" });
    const problem = actionProblem(actionFields(b.action));
    if (problem) found.push({ index, code: problem });
  });
  return found;
}

// Buttons as the flow wants them: only the keys that are set.
export function buttonsToData(buttons) {
  return buttons.map((b) => {
    const out = { key: b.key, label: String(b.label).trim() };
    for (const flag of ["dismiss", "destructive", "require_auth"]) if (b[flag]) out[flag] = true;
    if (b.action) out.action = b.action;
    return out;
  });
}

// One action: a kind and the fields of that kind. `onChange(action)` gets null for none.
export function actionEditor(s, value, onChange, { listId } = {}) {
  const t = s.buttons;
  const fields = actionFields(value);
  let current = value ?? null;
  const box = el("div", { className: "action-editor" });
  const note = el("div", { className: "hint" });
  const emit = () => {
    current = actionFromFields(fields, current);
    note.textContent = actionProblem(fields) ? t.problems[actionProblem(fields)] : "";
    onChange(current, actionProblem(fields));
  };
  const text = (key, label, extra = {}) => ui_field(label, textInput(fields[key], (v) => { fields[key] = v; emit(); }, extra));
  const draw = () => {
    box.replaceChildren();
    box.append(ui_field(t.action, selectInput(ACTION_KINDS.map((k) => ({ value: k, label: t.kinds[k] })), fields.kind, (v) => { fields.kind = v; emit(); draw(); })));
    if (fields.kind === "navigate") box.append(text("path", t.path, { placeholder: "/lovelace/cameras" }));
    if (fields.kind === "url") box.append(text("url", t.address, { placeholder: "https://example.org" }));
    if (fields.kind === "more-info" || fields.kind === "perform-action") {
      const entity = text(fields.kind === "more-info" ? "entity" : "target", t.entity);
      if (listId) entity.querySelector("input")?.setAttribute("list", listId);
      if (fields.kind === "perform-action") box.append(text("perform", t.perform, { placeholder: "light.turn_on" }));
      box.append(entity);
      if (fields.kind === "perform-action") box.append(text("data", t.data, { placeholder: '{"brightness": 100}', style: "max-width:100%" }));
    }
    if (fields.kind === "custom") box.append(el("div", { className: "hint", textContent: t.custom_note }));
    box.append(note);
    note.textContent = actionProblem(fields) ? t.problems[actionProblem(fields)] : "";
  };
  draw();
  return box;
}

// Up to MAX_BUTTONS rows: text, key, three switches and the action the button runs.
export function buttonsEditor(s, buttons, onChange, { listId } = {}) {
  const t = s.buttons;
  const list = buttons.map((b) => ({ ...b }));
  const box = el("div", { className: "buttons-editor" });
  const emit = () => onChange(list.map((b) => ({ ...b })));
  const draw = () => {
    box.replaceChildren();
    list.forEach((b, index) => {
      const row = el("div", { className: "btn-row" });
      const label = textInput(b.label, (v) => {
        const taken = list.filter((_, i) => i !== index).map((x) => x.key);
        // The key follows the text until it has been changed by hand.
        if (!b.key || b.key === slugKey(b.label, taken)) {
          b.key = slugKey(v, taken);
          key.value = b.key;
        }
        b.label = v;
        emit();
      }, { maxLength: 40 });
      const key = textInput(b.key, (v) => { b.key = v; emit(); }, { spellcheck: false, autocapitalize: "off" });
      row.append(ui_field(t.label, label), ui_field(t.key, key, t.key_hint));
      row.append(
        checkbox(t.dismiss, b.dismiss, (on) => { b.dismiss = on; emit(); }),
        checkbox(t.destructive, b.destructive, (on) => { b.destructive = on; emit(); }),
        checkbox(t.require_auth, b.require_auth, (on) => { b.require_auth = on; emit(); }),
        actionEditor(s, b.action, (action) => { b.action = action || undefined; emit(); }, { listId }),
      );
      const remove = el("button", { type: "button", className: "danger", textContent: t.remove });
      remove.addEventListener("click", () => { list.splice(index, 1); emit(); draw(); });
      row.append(el("div", { className: "row" }, [remove]));
      box.append(row);
    });
    if (list.length < MAX_BUTTONS) {
      const add = el("button", { type: "button", textContent: t.add });
      add.addEventListener("click", () => {
        list.push({ key: slugKey("", list.map((x) => x.key)), label: "" });
        emit();
        draw();
      });
      box.append(add);
    } else box.append(el("div", { className: "hint", textContent: t.max }));
  };
  draw();
  return box;
}

const ui_field = (label, control, hint) => field(label, control, hint);

// A collapsible group: a heading that opens and closes its content (D-260).
export function fold(title, content, open = false) {
  const box = el("details", { className: "fold", open });
  box.append(el("summary", { textContent: title }), content);
  return box;
}

export function field(label, control, hint) {
  const wrap = el("label", { className: "field" }, [el("span", { textContent: label }), control]);
  if (hint) wrap.append(hint.includes("\n") ? richNode(hint, { className: "hint" }) : el("span", { className: "hint", textContent: hint }));
  return wrap;
}

// What a recipient value is called in a list: a person by name, a phone by its device name (a
// registration id is a UUID nobody can read), a speaker by its name and entity, an area by its name.
// Names that two phones share get the first four characters of the id after them.
export function recipientLabel(value, choices) {
  const person = (choices.persons || []).find((p) => p.id === value);
  if (person) return person.name;
  const phones = choices.registrations || [];
  const phone = phones.find((r) => r.id === value);
  if (phone) {
    const twin = phones.some((r) => r.id !== value && r.name === phone.name);
    return twin ? `${phone.name} (${value.slice(0, 4)})` : phone.name;
  }
  const speaker = (choices.speaker_names || {})[value];
  if (speaker) return speaker === value ? value : `${speaker} (${value})`;
  const area = (choices.areas || []).find((a) => a.id === value.replace(/^area:/, ""));
  if (area) return area.name;
  // A stored group is its key; the name is for display (D-199).
  const group = (choices.group_labels || {})[value];
  if (group) return `${group} (group)`;
  if (value.startsWith("name:")) return value.slice(5);
  return value;
}

// What an audience key is called: its name, or the text of a reference that matched nothing.
export function audienceLabel(value, choices) {
  const found = (choices.audience_choices || []).find((a) => a.id === value);
  if (found) return found.name;
  return value.startsWith("name:") ? value.slice(5) : value;
}

export function nameOf(list, id) {
  return list.find((item) => item.id === id)?.name ?? id;
}

// The target of one channel: an audience or recipients, never both (DESIGN 23.5). Shared by the
// Escalation and Fallback policies and by Test send. `values` holds `<channel>_audience` and
// `<channel>_recipients`; `choices` is the `choices` of heads_up/panel_config.
// "audience" or "recipients" for a channel's target block: the explicit choice when there is one,
// else what the data says (speech always takes recipients).
export function targetMode(values, channel) {
  if (channel === "speak") return "recipients";
  return values[`_mode_${channel}`] || ((values[`${channel}_recipients`] || []).length > 0 ? "recipients" : "audience");
}

export function targetBlock(channel, values, choices, labels, onChange) {
  const box = el("fieldset", {}, [el("legend", { textContent: labels.channel })]);
  if (channel === "persistent") {
    box.append(el("div", { className: "hint", textContent: labels.persistent }));
    return box;
  }
  const audienceKey = `${channel}_audience`;
  const recipientsKey = `${channel}_recipients`;
  const speech = channel === "speak"; // speech takes recipients, not an audience (D-098)
  // The chosen mode is remembered: with no recipient ticked yet it cannot be derived from the data,
  // and deriving it alone made the Recipients option snap back to Audience.
  const modeKey = `_mode_${channel}`;
  const mode = targetMode(values, channel);
  if (!speech) {
    const pick = (value) => {
      values[modeKey] = value;
      if (value === "audience") values[recipientsKey] = [];
      else values[audienceKey] = "";
      onChange(value);
    };
    box.append(
      el("div", { className: "row" }, [
        ...["audience", "recipients"].map((kind) => {
          const input = el("input", { type: "radio", name: `mode-${channel}`, checked: mode === kind });
          input.addEventListener("change", () => pick(kind));
          return el("label", { className: "inline" }, [input, el("span", { textContent: labels[kind] })]);
        }),
      ]),
    );
  }
  if (mode === "audience") {
    const choose = (choices.audience_choices || []).map((a) => ({ value: a.id, label: a.name }));
    // A key that no audience has any more stays in the list, marked, so the policy still opens.
    const current = values[audienceKey];
    if (current && !choose.some((o) => o.value === current)) choose.push({ value: current, label: audienceLabel(current, choices) });
    const options = [{ value: "", label: "—" }, ...choose];
    box.append(selectInput(options, values[audienceKey] || "", (v) => {
      values[audienceKey] = v;
      onChange();
    }));
  } else {
    const options = (choices.recipients[channel] || []).map((r) => ({ value: r, label: recipientLabel(r, choices) }));
    box.append(chips(labels.recipients, options, values[recipientsKey], (list) => {
      values[recipientsKey] = list;
      onChange();
    }, true));
  }
  return box;
}
