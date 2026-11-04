// Heads Up panel: Overview page (D-118). Loaded by the shell when the page is opened.

export const STRINGS = {
  en: {
    title: "Overview",
    active: "Active notifications",
    rules: "Watch rules",
    badge_escalating: "escalating",
    badge_reminding: "reminding",
    badge_snoozed: "snoozed",
    badge_held: "in a summary",
    badge_acknowledged: "acknowledged",
    show_list: "Show list",
    hide_list: "Hide list",
    none_active: "No message is active.",
    active_sub: "Messages that have not ended yet. Some wait for someone to acknowledge them; others will come back (reminders, snooze) or escalate.",
    chart_title: "Last 24 hours",
    chart_one: "message",
    chart_many: "messages",
    chart_empty: "Nothing was sent in the last 24 hours.",
    chart_start: "24 h ago",
    chart_now: "now",
    chart_tip_ago: "{n} {unit} · {h} h ago",
    chart_tip_now: "{n} {unit} · last hour",
    chart_label: "Messages per hour over the last 24 hours, {total} in all",
    shortcuts: "Set up",
    sc_rules: "Watch rules",
    sc_rules_sub: "{showing} showing now",
    sc_channels: "Channels",
    sc_channels_sub_on: "Mail is set up",
    sc_channels_sub_off: "Mail is not set up",
    sc_audiences: "Audiences",
    sc_audiences_sub: "{custom} of your own, {builtin} built in",
    sc_policies: "Policies",
    sc_policies_sub: "{enabled} of {total} enabled",
    sc_open: "Open {page}",
    hide: "Hide",
    hidden_line: "{n} hidden.",
    show_hidden: "Show again",
    hide_label: "Hide this warning",
    attention: "Needs attention",
    attention_none: "Nothing needs attention.",
    error: "Error",
    warning: "Warning",
    fix_recipients: "Open Recipients",
    fix_rules: "Open Watch rules",
    fix_messages: "Open Message Log",
    fix_policies: "Open Policies",
    fix_general: "Open Settings",
    last_actions: "Last actions",
    last_none: "Nothing has happened since Home Assistant started.",
    open_messages: "Open Message Log",
    first_run: "No policies yet. The introduction explains a few defaults you can switch on.",
    first_run_button: "Restart introduction",
    refresh: "Refresh",
    loading: "Loading…",
    load_failed: "The overview could not be loaded.",
    source_rule: "watch rule",
  },
  de: {
    title: "Übersicht",
    active: "Aktive Benachrichtigungen",
    rules: "Überwachungsregeln",
    badge_escalating: "eskaliert",
    badge_reminding: "erinnert",
    badge_snoozed: "zurückgestellt",
    badge_held: "in einer Zusammenfassung",
    badge_acknowledged: "bestätigt",
    show_list: "Liste zeigen",
    hide_list: "Liste verbergen",
    none_active: "Keine Meldung ist aktiv.",
    active_sub: "Meldungen, die noch nicht beendet sind. Manche warten darauf, dass jemand sie bestätigt; andere kommen wieder (Erinnerungen, Zurückstellen) oder eskalieren.",
    chart_title: "Letzte 24 Stunden",
    chart_one: "Meldung",
    chart_many: "Meldungen",
    chart_empty: "In den letzten 24 Stunden wurde nichts gesendet.",
    chart_start: "vor 24 Std.",
    chart_now: "jetzt",
    chart_tip_ago: "{n} {unit} · vor {h} Std.",
    chart_tip_now: "{n} {unit} · letzte Stunde",
    chart_label: "Meldungen pro Stunde in den letzten 24 Stunden, insgesamt {total}",
    shortcuts: "Einrichten",
    sc_rules: "Überwachungsregeln",
    sc_rules_sub: "{showing} werden gerade gezeigt",
    sc_channels: "Kanäle",
    sc_channels_sub_on: "E-Mail ist eingerichtet",
    sc_channels_sub_off: "E-Mail ist nicht eingerichtet",
    sc_audiences: "Zielgruppen",
    sc_audiences_sub: "{custom} eigene, {builtin} eingebaute",
    sc_policies: "Richtlinien",
    sc_policies_sub: "{enabled} von {total} aktiv",
    sc_open: "{page} öffnen",
    hide: "Ausblenden",
    hidden_line: "{n} ausgeblendet.",
    show_hidden: "Wieder anzeigen",
    hide_label: "Diese Warnung ausblenden",
    attention: "Braucht Aufmerksamkeit",
    attention_none: "Nichts braucht Aufmerksamkeit.",
    error: "Fehler",
    warning: "Warnung",
    fix_recipients: "Empfänger öffnen",
    fix_rules: "Überwachungsregeln öffnen",
    fix_messages: "Meldungsprotokoll öffnen",
    fix_policies: "Richtlinien öffnen",
    fix_general: "Einstellungen öffnen",
    last_actions: "Letzte Aktionen",
    last_none: "Seit dem Start von Home Assistant ist nichts passiert.",
    open_messages: "Meldungsprotokoll öffnen",
    first_run: "Noch keine Richtlinien. Die Einführung erklärt ein paar Standards, die du einschalten kannst.",
    first_run_button: "Einführung neu starten",
    refresh: "Aktualisieren",
    loading: "Lädt…",
    load_failed: "Die Übersicht konnte nicht geladen werden.",
    source_rule: "Überwachungsregel",
  },
  fr: {
    title: "Vue d'ensemble",
    active: "Notifications actives",
    rules: "Règles de surveillance",
    badge_escalating: "en escalade",
    badge_reminding: "en rappel",
    badge_snoozed: "reportées",
    badge_held: "dans un résumé",
    badge_acknowledged: "confirmées",
    show_list: "Afficher la liste",
    hide_list: "Masquer la liste",
    none_active: "Aucun message n'est actif.",
    active_sub: "Messages qui ne sont pas encore terminés. Certains attendent une confirmation ; d'autres reviendront (rappels, report) ou seront escaladés.",
    chart_title: "Dernières 24 heures",
    chart_one: "message",
    chart_many: "messages",
    chart_empty: "Rien n'a été envoyé ces dernières 24 heures.",
    chart_start: "il y a 24 h",
    chart_now: "maintenant",
    chart_tip_ago: "{n} {unit} · il y a {h} h",
    chart_tip_now: "{n} {unit} · dernière heure",
    chart_label: "Messages par heure sur les dernières 24 heures, {total} au total",
    shortcuts: "Configurer",
    sc_rules: "Règles de surveillance",
    sc_rules_sub: "{showing} affichées en ce moment",
    sc_channels: "Canaux",
    sc_channels_sub_on: "Le mail est configuré",
    sc_channels_sub_off: "Le mail n'est pas configuré",
    sc_audiences: "Audiences",
    sc_audiences_sub: "{custom} à vous, {builtin} intégrées",
    sc_policies: "Politiques",
    sc_policies_sub: "{enabled} sur {total} actives",
    sc_open: "Ouvrir {page}",
    hide: "Masquer",
    hidden_line: "{n} masqué(s).",
    show_hidden: "Afficher à nouveau",
    hide_label: "Masquer cet avertissement",
    attention: "À surveiller",
    attention_none: "Rien à surveiller.",
    error: "Erreur",
    warning: "Avertissement",
    fix_recipients: "Ouvrir Destinataires",
    fix_rules: "Ouvrir Règles de surveillance",
    fix_messages: "Ouvrir le journal des messages",
    fix_policies: "Ouvrir Politiques",
    fix_general: "Ouvrir Réglages",
    last_actions: "Dernières actions",
    last_none: "Rien ne s'est passé depuis le démarrage de Home Assistant.",
    open_messages: "Ouvrir le journal des messages",
    first_run: "Aucune politique pour l'instant. L'introduction explique quelques réglages par défaut que vous pouvez activer.",
    first_run_button: "Relancer l'introduction",
    refresh: "Actualiser",
    loading: "Chargement…",
    load_failed: "La vue d'ensemble n'a pas pu être chargée.",
    source_rule: "règle de surveillance",
  },
  es: {
    title: "Resumen",
    active: "Notificaciones activas",
    rules: "Reglas de vigilancia",
    badge_escalating: "escalando",
    badge_reminding: "recordando",
    badge_snoozed: "pospuestas",
    badge_held: "en un resumen",
    badge_acknowledged: "confirmadas",
    show_list: "Mostrar lista",
    hide_list: "Ocultar lista",
    none_active: "Ningún mensaje está activo.",
    active_sub: "Mensajes que aún no han terminado. Algunos esperan a que alguien los confirme; otros volverán (recordatorios, pospuestas) o escalarán.",
    chart_title: "Últimas 24 horas",
    chart_one: "mensaje",
    chart_many: "mensajes",
    chart_empty: "No se envió nada en las últimas 24 horas.",
    chart_start: "hace 24 h",
    chart_now: "ahora",
    chart_tip_ago: "{n} {unit} · hace {h} h",
    chart_tip_now: "{n} {unit} · última hora",
    chart_label: "Mensajes por hora en las últimas 24 horas, {total} en total",
    shortcuts: "Configurar",
    sc_rules: "Reglas de vigilancia",
    sc_rules_sub: "{showing} mostrándose ahora",
    sc_channels: "Canales",
    sc_channels_sub_on: "El correo está configurado",
    sc_channels_sub_off: "El correo no está configurado",
    sc_audiences: "Audiencias",
    sc_audiences_sub: "{custom} propias, {builtin} integradas",
    sc_policies: "Políticas",
    sc_policies_sub: "{enabled} de {total} activas",
    sc_open: "Abrir {page}",
    hide: "Ocultar",
    hidden_line: "{n} oculta(s).",
    show_hidden: "Mostrar de nuevo",
    hide_label: "Ocultar este aviso",
    attention: "Requiere atención",
    attention_none: "Nada requiere atención.",
    error: "Error",
    warning: "Aviso",
    fix_recipients: "Abrir Destinatarios",
    fix_rules: "Abrir Reglas de vigilancia",
    fix_messages: "Abrir el registro de mensajes",
    fix_policies: "Abrir Políticas",
    fix_general: "Abrir Ajustes",
    last_actions: "Últimas acciones",
    last_none: "No ha pasado nada desde que arrancó Home Assistant.",
    open_messages: "Abrir el registro de mensajes",
    first_run: "Aún no hay políticas. La introducción explica algunos valores por defecto que puedes activar.",
    first_run_button: "Reiniciar la introducción",
    refresh: "Actualizar",
    loading: "Cargando…",
    load_failed: "No se pudo cargar el resumen.",
    source_rule: "regla de vigilancia",
  },
};

const BADGES = ["escalating", "reminding", "snoozed", "held", "acknowledged"];
const REFRESH_MS = 10000;

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// The badges of the active tile: only the states that occur, in a fixed order.
export function badgeList(counts) {
  return BADGES.filter((key) => (counts?.[key] ?? 0) > 0).map((key) => ({ key, n: counts[key] }));
}

// The page that fixes an item of "Needs attention", as the key of the button text.
export function fixKey(page) {
  return `fix_${page}`;
}

// The bars of the activity chart: one per hour, oldest first, stacked by severity (the least
// severe at the bottom). An empty hour is a small capsule so the chart never looks broken.
export const CHART_SEVERITIES = ["critical", "warning", "info", "success"];

export function chartModel(activity, { width = 600, height = 150, gap = 6, minimum = 5 } = {}) {
  const buckets = activity?.buckets ?? [];
  const count = buckets.length;
  const barWidth = count ? (width - gap * (count - 1)) / count : 0;
  const peak = Math.max(1, ...buckets.map((b) => b.total));
  const bars = buckets.map((bucket, index) => {
    const full = bucket.total ? Math.max(minimum * 2, (bucket.total / peak) * height) : minimum;
    let y = height;
    const segments = [];
    for (const severity of [...CHART_SEVERITIES].reverse()) {
      const n = bucket.by?.[severity] ?? 0;
      if (!n) continue;
      const h = (full * n) / bucket.total;
      y -= h;
      segments.push({ severity, y, h });
    }
    return {
      index,
      x: index * (barWidth + gap),
      width: barWidth,
      top: height - full,
      height: full,
      empty: bucket.total === 0,
      total: bucket.total,
      hoursAgo: count - 1 - index,
      segments,
    };
  });
  return { width, height, barWidth, bars, peak, total: activity?.total ?? 0 };
}

export function barTip(bar, t) {
  const unit = bar.total === 1 ? t.chart_one : t.chart_many;
  return fill(bar.hoursAgo === 0 ? t.chart_tip_now : t.chart_tip_ago, { n: bar.total, unit, h: bar.hoursAgo });
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-overview .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 16px; }
.hu-overview section { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
.hu-overview .tiles section { margin-bottom: 0; }
.hu-overview h2 { font-size: 16px; margin: 0 0 8px; }
.hu-overview .shortcuts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
.hu-overview button.shortcut { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; text-align: left; padding: 10px 14px; min-height: 48px; background: var(--card-background-color); border-radius: 12px; }
.hu-overview button.shortcut:hover { border-color: var(--primary-color); }
.hu-overview button.shortcut .name { font-size: 14px; font-weight: 600; }
.hu-overview button.shortcut .big { font-size: 24px; }
.hu-overview .big { font-size: 32px; font-weight: 600; }
.hu-overview .badges { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.hu-overview .badge { border-radius: 12px; padding: 2px 10px; font-size: 13px; background: var(--secondary-background-color); border: 1px solid var(--divider-color); }
.hu-overview button { min-height: 40px; padding: 0 14px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-overview button:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-overview ul { list-style: none; margin: 8px 0 0; padding: 0; }
.hu-overview li { padding: 8px 0; border-top: 1px solid var(--divider-color); }
.hu-overview .sub { color: var(--secondary-text-color); font-size: 13px; }
.hu-overview .sev { font-weight: 600; margin-right: 6px; }
.hu-overview .error { color: var(--error-color); font-weight: 600; margin-right: 6px; }
.hu-overview .warning { color: var(--warning-color); font-weight: 600; margin-right: 6px; }
.hu-overview .split { display: flex; flex-wrap: wrap; gap: 28px; align-items: flex-end; }
.hu-overview .split .info { flex: 1 1 240px; }
.hu-overview .split .chartbox { flex: 1.8 1 320px; min-width: 0; }
.hu-overview .chartbox .head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
.hu-overview .chartbox .head .total { font-weight: 600; }
.hu-overview .chartbox .axis { display: flex; justify-content: space-between; margin-top: 6px; }
.hu-overview svg.chart { display: block; width: 100%; height: auto; overflow: visible; }
.hu-overview svg.chart .bar { transform-box: fill-box; transform-origin: 50% 100%; transition: filter .2s; }
.hu-overview svg.chart .bar:hover { filter: brightness(1.18); }
.hu-overview svg.chart .empty { fill: var(--divider-color); opacity: .7; }
.hu-overview svg.chart .sev-critical { fill: var(--error-color, #db4437); }
.hu-overview svg.chart .sev-warning { fill: var(--warning-color, #ffa600); }
.hu-overview svg.chart .sev-info { fill: var(--info-color, #039be5); }
.hu-overview svg.chart .sev-success { fill: var(--success-color, #43a047); }
.hu-overview svg.chart.intro .bar { animation: hu-grow .8s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(var(--i) * 30ms); }
.hu-overview svg.chart .bar.now .shine { animation: hu-glow 2.6s ease-in-out infinite; }
@keyframes hu-grow { from { transform: scaleY(0); opacity: 0; } to { transform: scaleY(1); opacity: 1; } }
@keyframes hu-glow { 0%, 100% { opacity: .35; } 50% { opacity: .75; } }
@media (prefers-reduced-motion: reduce) { .hu-overview svg.chart .bar, .hu-overview svg.chart .bar .shine { animation: none !important; } }
.hu-overview .hint { background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
`;

export function mount(container, ctx) {
  const { t, s, fmt } = ctx;
  let hass = ctx.hass;
  let data = null;
  let open = { active: false };
  let timer = null;
  let played = false;
  const root = el("div", { className: "hu-overview" });
  container.append(root);

  const now = () => Date.now();
  const section = (title, children, label) => {
    const box = el("section", {}, [el("h2", { textContent: title }), ...children]);
    if (label) box.setAttribute("aria-label", label);
    root.append(box);
    return box;
  };

  // Small cards that open the page where the thing is set up; they show a number and nothing else
  // the page already shows.
  function shortcutRow() {
    const sc = data.shortcuts;
    const rules = data.rules;
    const cards = [
      { page: "rules", title: t.sc_rules, big: rules.enabled, sub: fill(t.sc_rules_sub, { showing: rules.showing }) },
      { page: "channels", title: t.sc_channels, big: sc.channels.total, sub: sc.channels.mail ? t.sc_channels_sub_on : t.sc_channels_sub_off },
      { page: "audiences", title: t.sc_audiences, big: sc.audiences.builtin + sc.audiences.custom, sub: fill(t.sc_audiences_sub, sc.audiences) },
      { page: "policies", title: t.sc_policies, big: sc.policies.enabled, sub: fill(t.sc_policies_sub, sc.policies) },
    ];
    const row = el("div", { className: "shortcuts" });
    row.setAttribute("aria-label", t.shortcuts);
    for (const card of cards) {
      const button = el("button", { type: "button", className: "shortcut" }, [
        el("span", { className: "name", textContent: card.title }),
        el("span", { className: "big", textContent: String(card.big) }),
        el("span", { className: "sub", textContent: card.sub }),
      ]);
      button.setAttribute("aria-label", `${fill(t.sc_open, { page: card.title })}: ${card.big}, ${card.sub}`);
      button.addEventListener("click", () => ctx.navigate(card.page));
      row.append(button);
    }
    root.append(row);
  }

  // The bars of the last 24 hours, stacked by severity. The bars grow in once, when the page opens;
  // the page refreshes every 10 seconds and must not replay that.
  function chartNode(intro) {
    const model = chartModel(data.activity);
    const NS = "http://www.w3.org/2000/svg";
    const make = (name, attrs = {}, children = []) => {
      const node = document.createElementNS(NS, name);
      for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
      node.append(...children);
      return node;
    };
    const defs = make("defs", {}, [
      make("linearGradient", { id: "hu-shine", x1: 0, y1: 0, x2: 0, y2: 1 }, [
        make("stop", { offset: "0%", "stop-color": "#fff", "stop-opacity": 0.55 }),
        make("stop", { offset: "100%", "stop-color": "#fff", "stop-opacity": 0 }),
      ]),
      ...model.bars.map((bar) =>
        make("clipPath", { id: `hu-clip-${bar.index}` }, [
          make("rect", { x: bar.x, y: bar.top, width: bar.width, height: bar.height, rx: Math.min(6, bar.width / 2) }),
        ]),
      ),
    ]);
    const bars = model.bars.map((bar) => {
      const inner = bar.empty
        ? [make("rect", { class: "empty", x: bar.x, y: bar.top, width: bar.width, height: bar.height })]
        : [
            ...bar.segments.map((seg) =>
              make("rect", { class: `sev-${seg.severity}`, x: bar.x, y: seg.y, width: bar.width, height: seg.h }),
            ),
            make("rect", { class: "shine", x: bar.x, y: bar.top, width: bar.width, height: bar.height, fill: "url(#hu-shine)" }),
          ];
      const title = make("title");
      title.textContent = barTip(bar, t);
      const group = make("g", { class: `bar${bar.hoursAgo === 0 ? " now" : ""}`, style: `--i:${bar.index}` }, [
        title,
        make("g", { "clip-path": `url(#hu-clip-${bar.index})` }, inner),
      ]);
      return group;
    });
    const svg = make("svg", {
      class: `chart${intro ? " intro" : ""}`,
      viewBox: `0 0 ${model.width} ${model.height}`,
      role: "img",
      "aria-label": fill(t.chart_label, { total: model.total }),
    }, [defs, ...bars]);
    const unit = model.total === 1 ? t.chart_one : t.chart_many;
    return el("div", { className: "chartbox" }, [
      el("div", { className: "head" }, [
        el("span", { className: "sub", textContent: t.chart_title }),
        el("span", model.total ? { className: "total", textContent: `${model.total} ${unit}` } : { className: "sub", textContent: t.chart_empty }),
      ]),
      svg,
      el("div", { className: "axis sub" }, [el("span", { textContent: t.chart_start }), el("span", { textContent: t.chart_now })]),
    ]);
  }

  function render() {
    const intro = !played;
    played = true;
    root.replaceChildren(el("style", { textContent: CSS }), el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }));
    if (data.first_run) {
      const go = el("button", { type: "button", textContent: t.first_run_button });
      go.addEventListener("click", () => ctx.openWelcome());
      root.append(el("div", { className: "hint" }, [el("span", { textContent: t.first_run }), go]));
    }

    const tiles = el("div", { className: "tiles" });
    root.append(tiles);
    const tile = (title, big, sub, badges, key, list, extra) => {
      const toggle = el("button", { type: "button", textContent: open[key] ? t.hide_list : t.show_list });
      toggle.setAttribute("aria-expanded", String(open[key]));
      toggle.addEventListener("click", () => {
        open[key] = !open[key];
        render();
      });
      const info = el("div", { className: "info" }, [
        el("div", { className: "big", textContent: big }),
        el("div", { className: "sub", textContent: sub }),
        el("div", { className: "badges" }, badges.map((b) => el("span", { className: "badge", textContent: b }))),
        toggle,
      ]);
      const box = el("section", {}, [el("h2", { textContent: title }), extra ? el("div", { className: "split" }, [info, extra]) : info]);
      if (open[key]) box.append(list);
      tiles.append(box);
    };

    const activeItems = data.active.items;
    const activeList = el("ul");
    if (activeItems.length === 0) activeList.append(el("li", { textContent: t.none_active }));
    for (const item of activeItems) {
      const lines = item.states.map((state) => el("div", { className: "sub", textContent: fmt.stateText(state, now(), s) }));
      const origin = item.source === "rule" ? el("span", { className: "sub", textContent: ` · ${t.source_rule}` }) : "";
      activeList.append(
        el("li", {}, [
          el("span", { className: "sev", textContent: s.severity[item.severity] || item.severity }),
          el("span", { textContent: fmt.messageTitle(item) }),
          origin,
          ...lines,
        ]),
      );
    }
    const badges = badgeList(data.active.counts).map((b) => `${b.n} ${t[`badge_${b.key}`]}`);
    tile(t.active, String(data.active.count), t.active_sub, badges, "active", activeList, chartNode(intro));

    shortcutRow();

    const attention = data.attention;
    const attList = el("ul");
    if (attention.length === 0) attList.append(el("li", { textContent: t.attention_none }));
    for (const item of attention) {
      const row = el("li", {}, [
        el("span", { className: item.level, textContent: t[item.level] }),
        el("span", { textContent: fmt.attentionText(item, s) }),
      ]);
      const key = fixKey(item.page === "recipients" ? "recipients" : item.page);
      if (t[key]) {
        const fix = el("button", { type: "button", textContent: t[key], style: "margin-left:8px" });
        fix.addEventListener("click", () => ctx.navigate(item.page));
        row.append(fix);
      }
      if (item.dismissible) {
        const hide = el("button", { type: "button", textContent: t.hide, style: "margin-left:8px" });
        hide.setAttribute("aria-label", `${t.hide_label}: ${fmt.attentionText(item, s)}`);
        hide.addEventListener("click", async () => {
          await hass.callWS({ type: "heads_up/attention_dismiss", key: item.key });
          await load();
        });
        row.append(hide);
      }
      attList.append(row);
    }
    const parts = [attList];
    if (data.attention_hidden > 0) {
      const again = el("button", { type: "button", textContent: t.show_hidden });
      again.addEventListener("click", async () => {
        await hass.callWS({ type: "heads_up/attention_restore" });
        await load();
      });
      parts.push(el("div", { className: "sub", style: "margin-top:8px" }, [el("span", { textContent: `${fill(t.hidden_line, { n: data.attention_hidden })} ` }), again]));
    }
    section(t.attention, parts);

    const log = el("ul");
    if (data.log.length === 0) log.append(el("li", { textContent: t.last_none }));
    for (const entry of data.log) {
      log.append(
        el("li", {}, [
          el("span", { className: "sub", textContent: `${fmt.timeAgo(entry.time, now(), s)} · ` }),
          el("span", { textContent: fmt.logText(entry, s) }),
          el("span", { className: "sub", textContent: entry.title ? ` · ${entry.title}` : "" }),
        ]),
      );
    }
    const more = el("button", { type: "button", textContent: t.open_messages });
    more.addEventListener("click", () => ctx.navigate("messages"));
    const refresh = el("button", { type: "button", textContent: t.refresh, style: "margin-left:8px" });
    refresh.addEventListener("click", load);
    section(t.last_actions, [log, el("div", { style: "margin-top:8px" }, [more, refresh])]);
  }

  async function load() {
    try {
      data = await hass.callWS({ type: "heads_up/panel_overview" });
      render();
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
