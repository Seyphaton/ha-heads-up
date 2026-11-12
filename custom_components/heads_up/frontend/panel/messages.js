// Heads Up panel: Message Log page (D-118): recent messages and the delivery trace of one.

export const STRINGS = {
  en: {
    tap_hint: "Select a message to see where it was delivered.",
    close: "Close",
    unknown_phone: "Unknown phone ({id})",
    deliveries_title: "Deliveries",
    title: "Message Log",
    recent: "Recent messages",
    recent_hint: "Kept in memory; the list starts empty after a restart.",
    none: "No message yet.",
    active: "active",
    ended: "ended ({reason})",
    from_rule: "watch rule",
    trace: "Delivery trace",
    pick: "Choose a message to see its delivery trace.",
    time: "Time",
    channel: "Channel",
    recipient: "Recipient",
    result: "Result",
    timers: "Escalations and reminders",
    timer_escalation: "Escalation {policy}",
    timer_reminder: "Reminder {policy}",
    timer_deliver: "Delivery {policy}",
    timer_state_planned: "waiting, {when}",
    timer_state_sent: "done",
    timer_state_cleared: "stopped",
    timer_state_skipped: "skipped",
    ack: "Acknowledged by {names}",
    ack_count: "Acknowledged ({n})",
    held: "Held for a summary.",
    deliveries: "Deliveries now",
    no_entries: "No delivery was recorded for this message.",
    refresh: "Refresh",
    loading: "Loading…",
    load_failed: "The messages could not be loaded.",
    trace_failed: "The trace could not be loaded.",
    results: { sent: "sent", held: "held", skipped: "skipped", failed: "failed" },
  },
  de: {
    tap_hint: "Wähle eine Meldung, um zu sehen, wohin sie zugestellt wurde.",
    close: "Schließen",
    unknown_phone: "Unbekanntes Telefon ({id})",
    deliveries_title: "Zustellungen",
    title: "Meldungsprotokoll",
    recent: "Letzte Meldungen",
    recent_hint: "Im Speicher gehalten; die Liste ist nach einem Neustart leer.",
    none: "Noch keine Meldung.",
    active: "aktiv",
    ended: "beendet ({reason})",
    from_rule: "Überwachungsregel",
    trace: "Zustellprotokoll",
    pick: "Wähle eine Meldung, um ihr Zustellprotokoll zu sehen.",
    time: "Zeit",
    channel: "Kanal",
    recipient: "Empfänger",
    result: "Ergebnis",
    timers: "Eskalationen und Erinnerungen",
    timer_escalation: "Eskalation {policy}",
    timer_reminder: "Erinnerung {policy}",
    timer_deliver: "Zustellung {policy}",
    timer_state_planned: "wartet, {when}",
    timer_state_sent: "erledigt",
    timer_state_cleared: "gestoppt",
    timer_state_skipped: "übersprungen",
    ack: "Bestätigt von {names}",
    ack_count: "Bestätigt ({n})",
    held: "Für eine Zusammenfassung zurückgehalten.",
    deliveries: "Zustellungen jetzt",
    no_entries: "Für diese Meldung wurde keine Zustellung aufgezeichnet.",
    refresh: "Aktualisieren",
    loading: "Lädt…",
    load_failed: "Die Meldungen konnten nicht geladen werden.",
    trace_failed: "Das Protokoll konnte nicht geladen werden.",
    results: { sent: "gesendet", held: "zurückgehalten", skipped: "übersprungen", failed: "fehlgeschlagen" },
  },
  fr: {
    tap_hint: "Choisissez un message pour voir où il a été livré.",
    close: "Fermer",
    unknown_phone: "Téléphone inconnu ({id})",
    deliveries_title: "Livraisons",
    title: "Journal des messages",
    recent: "Messages récents",
    recent_hint: "Gardés en mémoire ; la liste est vide après un redémarrage.",
    none: "Aucun message pour l'instant.",
    active: "actif",
    ended: "terminé ({reason})",
    from_rule: "règle de surveillance",
    trace: "Trace de livraison",
    pick: "Choisissez un message pour voir sa trace de livraison.",
    time: "Heure",
    channel: "Canal",
    recipient: "Destinataire",
    result: "Résultat",
    timers: "Escalades et rappels",
    timer_escalation: "Escalade {policy}",
    timer_reminder: "Rappel {policy}",
    timer_deliver: "Livraison {policy}",
    timer_state_planned: "en attente, {when}",
    timer_state_sent: "terminé",
    timer_state_cleared: "arrêté",
    timer_state_skipped: "ignoré",
    ack: "Confirmé par {names}",
    ack_count: "Confirmé ({n})",
    held: "Retenu pour un résumé.",
    deliveries: "Livraisons actuelles",
    no_entries: "Aucune livraison n'a été enregistrée pour ce message.",
    refresh: "Actualiser",
    loading: "Chargement…",
    load_failed: "Les messages n'ont pas pu être chargés.",
    trace_failed: "La trace n'a pas pu être chargée.",
    results: { sent: "envoyé", held: "retenu", skipped: "ignoré", failed: "échec" },
  },
  es: {
    tap_hint: "Elige un mensaje para ver dónde se entregó.",
    close: "Cerrar",
    unknown_phone: "Teléfono desconocido ({id})",
    deliveries_title: "Entregas",
    title: "Registro de mensajes",
    recent: "Mensajes recientes",
    recent_hint: "Se guardan en memoria; la lista está vacía tras un reinicio.",
    none: "Aún no hay mensajes.",
    active: "activo",
    ended: "terminado ({reason})",
    from_rule: "regla de vigilancia",
    trace: "Traza de entrega",
    pick: "Elige un mensaje para ver su traza de entrega.",
    time: "Hora",
    channel: "Canal",
    recipient: "Destinatario",
    result: "Resultado",
    timers: "Escalados y recordatorios",
    timer_escalation: "Escalado {policy}",
    timer_reminder: "Recordatorio {policy}",
    timer_deliver: "Entrega {policy}",
    timer_state_planned: "esperando, {when}",
    timer_state_sent: "hecho",
    timer_state_cleared: "detenido",
    timer_state_skipped: "omitido",
    ack: "Confirmado por {names}",
    ack_count: "Confirmado ({n})",
    held: "Retenido para un resumen.",
    deliveries: "Entregas ahora",
    no_entries: "No se registró ninguna entrega para este mensaje.",
    refresh: "Actualizar",
    loading: "Cargando…",
    load_failed: "No se pudieron cargar los mensajes.",
    trace_failed: "No se pudo cargar la traza.",
    results: { sent: "enviado", held: "retenido", skipped: "omitido", failed: "falló" },
  },
};

const REFRESH_MS = 10000;

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// "2 sent, 1 skipped": the counts of the results of a message, in a fixed order.
export function resultsLine(results, t) {
  return ["sent", "held", "skipped", "failed"]
    .filter((key) => (results?.[key] ?? 0) > 0)
    .map((key) => `${results[key]} ${t.results[key]}`)
    .join(", ");
}

export function statusLabel(message, t, s, reasonText) {
  if (message.active) return t.active;
  return fill(t.ended, { reason: reasonText(message.reason, s) || "?" });
}


// "device:<id>" is a phone: show its name, or a short id when the device is gone. Anything else is
// labelled by the editors' shared label function (person, speaker, group).
export function recipientName(value, label, t) {
  if (!value) return "";
  if (!value.startsWith("device:")) return label(value);
  const id = value.slice(7);
  const name = label(id);
  return name === id ? fill(t.unknown_phone, { id: id.slice(0, 4) }) : name;
}

// The trace entries of one message (newest first) as groups: one per channel, result and reason
// within a minute, with the recipients listed once. Five skipped persons become one line.
export const DELIVERY_CHANNELS = ["banner", "push", "popup", "speak", "persistent", "mail"];
const deliveryChannel = (channel) => DELIVERY_CHANNELS.includes(channel);

export function groupEntries(entries, label, t, windowMs = 60000) {
  const groups = [];
  for (const entry of entries) {
    const reason = entry.reason || "";
    const group = groups.find(
      (g) => g.channel === entry.channel && g.result === entry.result && g.reason === reason && Math.abs(Date.parse(g.time) - Date.parse(entry.time)) <= windowMs,
    );
    // Only a delivery channel has recipients worth naming; the other rows (acknowledged, timer)
    // carry internal ids.
    const who = deliveryChannel(entry.channel) ? recipientName(entry.recipient, label, t) : "";
    if (group) {
      if (who && !group.recipients.includes(who)) group.recipients.push(who);
    } else {
      groups.push({ channel: entry.channel, result: entry.result, reason, time: entry.time, recipients: who ? [who] : [] });
    }
  }
  return groups;
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-messages section { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.hu-messages h2 { font-size: 16px; margin: 0 0 8px; }
.hu-messages ul { list-style: none; margin: 0; padding: 0; }
.hu-messages .msgs li { margin-top: 8px; }
.hu-messages button.row { display: flex; align-items: center; gap: 12px; width: 100%; text-align: left; min-height: 56px; padding: 10px 12px; border: 1px solid var(--divider-color); border-radius: 10px; background: var(--secondary-background-color, transparent); color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-messages button.row:hover { border-color: var(--primary-color); }
.hu-messages button.row:active { background: var(--divider-color); }
.hu-messages button.row .main { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.hu-messages button.row .chev { font-size: 24px; line-height: 1; color: var(--primary-color); }
.hu-messages button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-messages .sub { color: var(--secondary-text-color); font-size: 13px; }
.hu-messages .sev { font-weight: 600; margin-right: 6px; }
.hu-messages .refresh { min-height: 40px; margin-top: 12px; padding: 0 14px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-sheet { width: min(560px, calc(100% - 24px)); max-height: 85vh; padding: 0; border: 1px solid var(--divider-color); border-radius: 16px; background: var(--card-background-color); color: var(--primary-text-color); }
.hu-sheet::backdrop { background: rgba(0, 0, 0, 0.5); }
.hu-sheet .head { position: sticky; top: 0; display: flex; align-items: flex-start; gap: 8px; padding: 16px 8px 8px 16px; background: var(--card-background-color); border-bottom: 1px solid var(--divider-color); }
.hu-sheet .head h2 { flex: 1; margin: 0; font-size: 18px; overflow-wrap: anywhere; }
.hu-sheet .close { flex: none; width: 48px; height: 48px; border: none; border-radius: 24px; background: transparent; color: var(--primary-text-color); font-size: 24px; cursor: pointer; }
.hu-sheet .body { padding: 8px 16px 16px; }
.hu-sheet h3 { font-size: 14px; margin: 16px 0 4px; color: var(--secondary-text-color); }
.hu-sheet .group { padding: 10px 0; border-bottom: 1px solid var(--divider-color); overflow-wrap: anywhere; }
.hu-sheet .group .top { display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: baseline; }
.hu-sheet .group .ch { font-weight: 600; }
.hu-sheet .sub { color: var(--secondary-text-color); font-size: 13px; }
@media (max-width: 480px) {
  /* A phone gets a sheet that sits at the bottom edge and fills the width. */
  .hu-sheet { width: 100%; max-width: 100%; margin: auto 0 0; border-radius: 16px 16px 0 0; max-height: 90vh; }
}
`;

// "Escalation Water", "Reminder Water", "Delivery Critical delivery"; any other type shows only the
// policy name instead of a wrong word.
export function timerName(row, t) {
  const text = { escalation: t.timer_escalation, reminder: t.timer_reminder, deliver: t.timer_deliver }[row.type];
  return text ? fill(text, { policy: row.policy }) : row.policy;
}

export function mount(container, ctx) {
  const { t, s, fmt, ui } = ctx;
  let hass = ctx.hass;
  let list = null;
  let selected = null;
  let trace = null;
  let choices = null;
  let timer = null;
  const root = el("div", { className: "hu-messages" });
  const listHost = el("div");
  // The sheet lives outside the list, so the 10-second refresh never closes it.
  const sheet = el("dialog", { className: "hu-sheet" });
  sheet.setAttribute("aria-labelledby", "hu-sheet-title");
  root.append(el("style", { textContent: CSS }), el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }), listHost, sheet);
  container.append(root);
  const now = () => Date.now();
  const label = (value) => (choices && ui ? ui.recipientLabel(value, choices) : value);
  const when = (iso) => {
    const date = new Date(iso);
    const absolute = Number.isNaN(date.getTime()) ? "" : date.toLocaleString(ctx.language, { dateStyle: "short", timeStyle: "short" });
    return [fmt.timeAgo(iso, now(), s), absolute].filter(Boolean).join(" · ");
  };

  function closeSheet() {
    if (typeof sheet.close === "function") sheet.close();
    else sheet.removeAttribute("open");
    onClosed();
  }

  function onClosed() {
    selected = null;
    trace = null;
    renderList();
  }
  sheet.addEventListener("close", onClosed);
  sheet.addEventListener("click", (event) => {
    if (event.target === sheet) closeSheet();
  });

  function traceBody() {
    const body = el("div", { className: "body" });
    if (!trace) return body.append(el("div", { className: "sub", textContent: t.loading })), body;
    if (trace.error) return body.append(el("div", { textContent: t.trace_failed })), body;
    if (trace.held) body.append(el("div", { className: "sub", textContent: t.held }));
    if (trace.acknowledged_count > 0) {
      const names = trace.acknowledged_by.join(", ");
      body.append(el("div", { textContent: names ? fill(t.ack, { names }) : fill(t.ack_count, { n: trace.acknowledged_count }) }));
    }
    body.append(el("h3", { textContent: t.deliveries_title }));
    if (trace.entries.length === 0) body.append(el("div", { className: "sub", textContent: t.no_entries }));
    for (const group of groupEntries(trace.entries, label, t)) {
      const reason = group.reason === "ok" ? "" : fmt.reasonText(group.reason, s);
      const outcome = [s.result[group.result] || group.result, reason].filter(Boolean).join(": ");
      body.append(
        el("div", { className: "group" }, [
          el("div", { className: "top" }, [...(deliveryChannel(group.channel) ? [el("span", { className: "ch", textContent: fmt.channelName(group.channel, s) })] : []), el("span", { className: deliveryChannel(group.channel) ? "" : "ch", textContent: outcome })]),
          ...(group.recipients.length ? [el("div", { textContent: group.recipients.join(", ") })] : []),
          el("div", { className: "sub", textContent: when(group.time) }),
        ]),
      );
    }
    if (trace.timers.length > 0) {
      body.append(el("h3", { textContent: t.timers }));
      body.append(
        el(
          "ul",
          {},
          trace.timers.map((row) => {
            const state = fill(t[`timer_state_${row.state}`] || row.state, { when: row.due ? fmt.inTime(row.due, now(), s) : "" });
            return el("li", { textContent: `${timerName(row, t)}: ${state}`, style: "padding:4px 0" });
          }),
        ),
      );
    }
    return body;
  }

  function renderSheet() {
    const message = list?.find((m) => m.id === selected) || trace?.message || { id: selected, title: selected };
    const close = el("button", { type: "button", className: "close", textContent: "×" });
    close.setAttribute("aria-label", t.close);
    close.addEventListener("click", closeSheet);
    const head = el("div", { className: "head" }, [
      el("h2", { id: "hu-sheet-title" }, [el("span", { className: "sev", textContent: s.severity[message.severity] || "" }), document.createTextNode(fmt.messageTitle(message))]),
      close,
    ]);
    sheet.replaceChildren(head, traceBody());
  }

  function renderList() {
    const box = el("section", {}, [el("h2", { textContent: t.recent }), el("div", { className: "sub", textContent: t.tap_hint }), el("div", { className: "sub", textContent: t.recent_hint })]);
    const ul = el("ul", { className: "msgs" });
    if (list.length === 0) ul.append(el("li", { className: "sub", textContent: t.none }));
    for (const message of list) {
      const row = el("button", { type: "button", className: "row" });
      row.setAttribute("aria-haspopup", "dialog");
      row.append(
        el("span", { className: "main" }, [
          el("span", { className: "sev", textContent: s.severity[message.severity] || message.severity }),
          el("span", { textContent: fmt.messageTitle(message) }),
          el("div", { className: "sub", textContent: [fmt.timeAgo(message.created_at, now(), s), statusLabel(message, t, s, fmt.reasonText), resultsLine(message.results, t), message.source === "rule" ? t.from_rule : ""].filter(Boolean).join(" · ") }),
        ]),
        el("span", { className: "chev", textContent: "›" }),
      );
      row.querySelector(".chev").setAttribute("aria-hidden", "true");
      row.addEventListener("click", () => select(message.id));
      ul.append(el("li", {}, [row]));
    }
    box.append(ul);
    const refresh = el("button", { type: "button", className: "refresh", textContent: t.refresh });
    refresh.addEventListener("click", load);
    box.append(refresh);
    listHost.replaceChildren(box);
  }

  async function select(id) {
    selected = id;
    trace = null;
    renderSheet();
    if (!sheet.open) {
      if (typeof sheet.showModal === "function") sheet.showModal();
      else sheet.setAttribute("open", "");
    }
    await loadTrace();
  }

  async function loadTrace() {
    if (!selected) return;
    const id = selected;
    try {
      const result = await hass.callWS({ type: "heads_up/panel_trace", message_id: id });
      if (id === selected) trace = result;
    } catch (err) {
      if (id === selected) trace = { error: true };
    }
    if (id === selected) renderSheet();
  }

  async function load() {
    try {
      list = (await hass.callWS({ type: "heads_up/panel_messages" })).messages;
      renderList();
      if (selected) await loadTrace();
    } catch (err) {
      listHost.replaceChildren(el("div", { textContent: t.load_failed }));
    }
  }

  listHost.append(el("div", { textContent: t.loading }));
  // Names for the recipients; without them the log shows the ids.
  hass.callWS({ type: "heads_up/panel_config" }).then((data) => {
    choices = data.choices;
    if (selected) renderSheet();
  }, () => {});
  load();
  timer = setInterval(load, REFRESH_MS);
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      clearInterval(timer);
      if (sheet.open && typeof sheet.close === "function") sheet.close();
      root.remove();
    },
  };
}
