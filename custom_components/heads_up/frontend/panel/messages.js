// Heads Up panel: Message Log page (D-118): recent messages and the delivery trace of one.

export const STRINGS = {
  en: {
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
.hu-messages li button.row { width: 100%; text-align: left; min-height: 48px; padding: 8px 12px; border: none; border-top: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-messages li button.row[aria-pressed="true"] { background: var(--secondary-background-color); }
.hu-messages button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: -3px; }
.hu-messages .sub { color: var(--secondary-text-color); font-size: 13px; }
.hu-messages .sev { font-weight: 600; margin-right: 6px; }
.hu-messages table { width: 100%; border-collapse: collapse; }
.hu-messages th, .hu-messages td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--divider-color); font-size: 14px; vertical-align: top; }
.hu-messages .refresh { min-height: 40px; padding: 0 14px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
`;

// "Escalation Water", "Reminder Water", "Delivery Critical delivery"; any other type shows only the
// policy name instead of a wrong word.
export function timerName(row, t) {
  const text = { escalation: t.timer_escalation, reminder: t.timer_reminder, deliver: t.timer_deliver }[row.type];
  return text ? fill(text, { policy: row.policy }) : row.policy;
}

export function mount(container, ctx) {
  const { t, s, fmt } = ctx;
  let hass = ctx.hass;
  let list = null;
  let selected = null;
  let trace = null;
  let timer = null;
  const root = el("div", { className: "hu-messages" });
  container.append(root);
  const now = () => Date.now();

  function traceNode() {
    const box = el("section", {}, [el("h2", { textContent: t.trace })]);
    if (!selected) {
      box.append(el("div", { className: "sub", textContent: t.pick }));
      return box;
    }
    if (!trace) {
      box.append(el("div", { className: "sub", textContent: t.loading }));
      return box;
    }
    if (trace.error) {
      box.append(el("div", { textContent: t.trace_failed }));
      return box;
    }
    if (trace.held) box.append(el("div", { className: "sub", textContent: t.held }));
    if (trace.acknowledged_count > 0) {
      const names = trace.acknowledged_by.join(", ");
      box.append(el("div", { textContent: names ? fill(t.ack, { names }) : fill(t.ack_count, { n: trace.acknowledged_count }) }));
    }
    if (trace.entries.length === 0) box.append(el("div", { className: "sub", textContent: t.no_entries }));
    else {
      const head = el("tr", {}, [t.time, t.channel, t.recipient, t.result].map((text) => el("th", { textContent: text })));
      const rows = trace.entries.map((e) =>
        el("tr", {}, [
          el("td", { textContent: fmt.timeAgo(e.time, now(), s) }),
          el("td", { textContent: fmt.channelName(e.channel, s) }),
          el("td", { textContent: e.recipient || "" }),
          el("td", { textContent: [s.result[e.result] || e.result, fmt.reasonText(e.reason, s)].filter(Boolean).join(": ") }),
        ]),
      );
      box.append(el("table", {}, [el("thead", {}, [head]), el("tbody", {}, rows)]));
    }
    if (trace.timers.length > 0) {
      box.append(el("h2", { textContent: t.timers, style: "margin-top:16px" }));
      const items = trace.timers.map((row) => {
        const name = timerName(row, t);
        const state = fill(t[`timer_state_${row.state}`] || row.state, { when: row.due ? fmt.inTime(row.due, now(), s) : "" });
        return el("li", {}, [el("span", { textContent: `${name}: ${state}` })]);
      });
      box.append(el("ul", {}, items));
    }
    return box;
  }

  function render() {
    root.replaceChildren(el("style", { textContent: CSS }), el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }));
    const box = el("section", {}, [el("h2", { textContent: t.recent }), el("div", { className: "sub", textContent: t.recent_hint })]);
    const ul = el("ul");
    if (list.length === 0) ul.append(el("li", { className: "sub", textContent: t.none }));
    for (const message of list) {
      const row = el("button", { type: "button", className: "row" });
      row.setAttribute("aria-pressed", String(message.id === selected));
      row.append(
        el("span", { className: "sev", textContent: s.severity[message.severity] || message.severity }),
        el("span", { textContent: fmt.messageTitle(message) }),
        el("div", { className: "sub", textContent: [fmt.timeAgo(message.created_at, now(), s), statusLabel(message, t, s, fmt.reasonText), resultsLine(message.results, t), message.source === "rule" ? t.from_rule : ""].filter(Boolean).join(" · ") }),
      );
      row.addEventListener("click", () => select(message.id));
      ul.append(el("li", {}, [row]));
    }
    box.append(ul);
    const refresh = el("button", { type: "button", className: "refresh", textContent: t.refresh });
    refresh.addEventListener("click", load);
    box.append(refresh);
    root.append(box, traceNode());
  }

  async function select(id) {
    selected = id;
    trace = null;
    render();
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
    render();
  }

  async function load() {
    try {
      list = (await hass.callWS({ type: "heads_up/panel_messages" })).messages;
      render();
      if (selected) await loadTrace();
    } catch (err) {
      root.replaceChildren(el("div", { textContent: t.load_failed }));
    }
  }

  root.append(el("div", { textContent: t.loading }));
  load();
  timer = setInterval(load, REFRESH_MS);
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      clearInterval(timer);
      root.remove();
    },
  };
}
