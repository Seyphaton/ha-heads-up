// Heads Up panel: Overview page (D-118). Loaded by the shell when the page is opened.

export const STRINGS = {
  en: {
    title: "Overview",
    active: "Active notifications",
    rules: "Watch rules",
    rules_active: "{enabled} of {total} active",
    badge_escalating: "escalating",
    badge_reminding: "reminding",
    badge_snoozed: "snoozed",
    badge_held: "in a summary",
    badge_acknowledged: "acknowledged",
    badge_disabled: "disabled",
    badge_showing: "showing now",
    show_list: "Show list",
    hide_list: "Hide list",
    none_active: "No message is active.",
    rule_disabled: "disabled",
    rule_showing: "showing",
    rule_waiting: "waiting",
    rule_watches: "watches {entity} {operator} {state}",
    rule_template: "watches a template",
    attention: "Needs attention",
    attention_none: "Nothing needs attention.",
    error: "Error",
    warning: "Warning",
    fix_recipients: "Open Recipients",
    fix_rules: "Open Watch rules",
    fix_policies: "Open Policies",
    fix_general: "Open Settings",
    last_actions: "Last actions",
    last_none: "Nothing has happened since Home Assistant started.",
    open_messages: "Open Messages",
    first_run: "No policies yet. The presets in Settings add a starting set.",
    first_run_button: "Open Settings",
    refresh: "Refresh",
    loading: "Loading…",
    load_failed: "The overview could not be loaded.",
    source_rule: "watch rule",
    operators: { equals: "equals", not_equals: "does not equal", above: "above", below: "below", between: "between", contains: "contains", not_contains: "does not contain", empty: "is empty", not_empty: "is not empty" },
  },
  de: {
    title: "Übersicht",
    active: "Aktive Benachrichtigungen",
    rules: "Überwachungsregeln",
    rules_active: "{enabled} von {total} aktiv",
    badge_escalating: "eskaliert",
    badge_reminding: "erinnert",
    badge_snoozed: "zurückgestellt",
    badge_held: "in einer Zusammenfassung",
    badge_acknowledged: "bestätigt",
    badge_disabled: "deaktiviert",
    badge_showing: "zeigt gerade",
    show_list: "Liste zeigen",
    hide_list: "Liste verbergen",
    none_active: "Keine Meldung ist aktiv.",
    rule_disabled: "deaktiviert",
    rule_showing: "zeigt",
    rule_waiting: "wartet",
    rule_watches: "überwacht {entity} {operator} {state}",
    rule_template: "überwacht eine Vorlage",
    attention: "Braucht Aufmerksamkeit",
    attention_none: "Nichts braucht Aufmerksamkeit.",
    error: "Fehler",
    warning: "Warnung",
    fix_recipients: "Empfänger öffnen",
    fix_rules: "Überwachungsregeln öffnen",
    fix_policies: "Richtlinien öffnen",
    fix_general: "Einstellungen öffnen",
    last_actions: "Letzte Aktionen",
    last_none: "Seit dem Start von Home Assistant ist nichts passiert.",
    open_messages: "Meldungen öffnen",
    first_run: "Noch keine Richtlinien. Die Voreinstellungen in den Einstellungen fügen einen Grundstock hinzu.",
    first_run_button: "Einstellungen öffnen",
    refresh: "Aktualisieren",
    loading: "Lädt…",
    load_failed: "Die Übersicht konnte nicht geladen werden.",
    source_rule: "Überwachungsregel",
    operators: { equals: "ist gleich", not_equals: "ist ungleich", above: "über", below: "unter", between: "zwischen", contains: "enthält", not_contains: "enthält nicht", empty: "ist leer", not_empty: "ist nicht leer" },
  },
  fr: {
    title: "Vue d'ensemble",
    active: "Notifications actives",
    rules: "Règles de surveillance",
    rules_active: "{enabled} sur {total} actives",
    badge_escalating: "en escalade",
    badge_reminding: "en rappel",
    badge_snoozed: "reportées",
    badge_held: "dans un résumé",
    badge_acknowledged: "confirmées",
    badge_disabled: "désactivées",
    badge_showing: "affichées",
    show_list: "Afficher la liste",
    hide_list: "Masquer la liste",
    none_active: "Aucun message n'est actif.",
    rule_disabled: "désactivée",
    rule_showing: "affiche",
    rule_waiting: "attend",
    rule_watches: "surveille {entity} {operator} {state}",
    rule_template: "surveille un modèle",
    attention: "À surveiller",
    attention_none: "Rien à surveiller.",
    error: "Erreur",
    warning: "Avertissement",
    fix_recipients: "Ouvrir Destinataires",
    fix_rules: "Ouvrir Règles de surveillance",
    fix_policies: "Ouvrir Politiques",
    fix_general: "Ouvrir Réglages",
    last_actions: "Dernières actions",
    last_none: "Rien ne s'est passé depuis le démarrage de Home Assistant.",
    open_messages: "Ouvrir Messages",
    first_run: "Aucune politique pour l'instant. Les préréglages dans Réglages ajoutent un jeu de départ.",
    first_run_button: "Ouvrir Réglages",
    refresh: "Actualiser",
    loading: "Chargement…",
    load_failed: "La vue d'ensemble n'a pas pu être chargée.",
    source_rule: "règle de surveillance",
    operators: { equals: "égale", not_equals: "diffère de", above: "au-dessus de", below: "au-dessous de", between: "entre", contains: "contient", not_contains: "ne contient pas", empty: "est vide", not_empty: "n'est pas vide" },
  },
  es: {
    title: "Resumen",
    active: "Notificaciones activas",
    rules: "Reglas de vigilancia",
    rules_active: "{enabled} de {total} activas",
    badge_escalating: "escalando",
    badge_reminding: "recordando",
    badge_snoozed: "pospuestas",
    badge_held: "en un resumen",
    badge_acknowledged: "confirmadas",
    badge_disabled: "desactivadas",
    badge_showing: "mostrándose",
    show_list: "Mostrar lista",
    hide_list: "Ocultar lista",
    none_active: "Ningún mensaje está activo.",
    rule_disabled: "desactivada",
    rule_showing: "muestra",
    rule_waiting: "espera",
    rule_watches: "vigila {entity} {operator} {state}",
    rule_template: "vigila una plantilla",
    attention: "Requiere atención",
    attention_none: "Nada requiere atención.",
    error: "Error",
    warning: "Aviso",
    fix_recipients: "Abrir Destinatarios",
    fix_rules: "Abrir Reglas de vigilancia",
    fix_policies: "Abrir Políticas",
    fix_general: "Abrir Ajustes",
    last_actions: "Últimas acciones",
    last_none: "No ha pasado nada desde que arrancó Home Assistant.",
    open_messages: "Abrir Mensajes",
    first_run: "Aún no hay políticas. Los ajustes preestablecidos en Ajustes añaden un conjunto inicial.",
    first_run_button: "Abrir Ajustes",
    refresh: "Actualizar",
    loading: "Cargando…",
    load_failed: "No se pudo cargar el resumen.",
    source_rule: "regla de vigilancia",
    operators: { equals: "es igual a", not_equals: "es distinto de", above: "por encima de", below: "por debajo de", between: "entre", contains: "contiene", not_contains: "no contiene", empty: "está vacío", not_empty: "no está vacío" },
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

// One line about what a rule watches, from its structured fields.
export function ruleCondition(rule, t) {
  if (rule.template) return t.rule_template;
  const state = Array.isArray(rule.state) ? rule.state.join(", ") : rule.state || "";
  const operator = t.operators[rule.operator] || rule.operator;
  return fill(t.rule_watches, { entity: rule.entity_id, operator, state }).trim();
}

export function ruleState(rule, t) {
  if (!rule.enabled) return t.rule_disabled;
  return rule.showing ? t.rule_showing : t.rule_waiting;
}

// The page that fixes an item of "Needs attention", as the key of the button text.
export function fixKey(page) {
  return `fix_${page}`;
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
.hu-overview .hint { background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
`;

export function mount(container, ctx) {
  const { t, s, fmt } = ctx;
  let hass = ctx.hass;
  let data = null;
  let open = { active: false, rules: false };
  let timer = null;
  const root = el("div", { className: "hu-overview" });
  container.append(root);

  const now = () => Date.now();
  const section = (title, children, label) => {
    const box = el("section", {}, [el("h2", { textContent: title }), ...children]);
    if (label) box.setAttribute("aria-label", label);
    root.append(box);
    return box;
  };

  function render() {
    root.replaceChildren(el("style", { textContent: CSS }), el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }));
    if (data.first_run) {
      const go = el("button", { type: "button", textContent: t.first_run_button });
      go.addEventListener("click", () => ctx.navigate("general"));
      root.append(el("div", { className: "hint" }, [el("span", { textContent: t.first_run }), go]));
    }

    const tiles = el("div", { className: "tiles" });
    root.append(tiles);
    const tile = (title, big, sub, badges, key, list) => {
      const toggle = el("button", { type: "button", textContent: open[key] ? t.hide_list : t.show_list });
      toggle.setAttribute("aria-expanded", String(open[key]));
      toggle.addEventListener("click", () => {
        open[key] = !open[key];
        render();
      });
      const box = el("section", {}, [
        el("h2", { textContent: title }),
        el("div", { className: "big", textContent: big }),
        el("div", { className: "sub", textContent: sub }),
        el("div", { className: "badges" }, badges.map((b) => el("span", { className: "badge", textContent: b }))),
        toggle,
      ]);
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
    tile(t.active, String(data.active.count), "", badges, "active", activeList);

    const rules = data.rules;
    const ruleBadges = [];
    if (rules.disabled) ruleBadges.push(`${rules.disabled} ${t.badge_disabled}`);
    if (rules.showing) ruleBadges.push(`${rules.showing} ${t.badge_showing}`);
    const ruleList = el("ul");
    for (const rule of rules.items) {
      ruleList.append(
        el("li", {}, [
          el("strong", { textContent: rule.name }),
          el("span", { className: "sub", textContent: ` · ${ruleState(rule, t)}` }),
          el("div", { className: "sub", textContent: ruleCondition(rule, t) }),
        ]),
      );
    }
    tile(t.rules, String(rules.total), fill(t.rules_active, { enabled: rules.enabled, total: rules.total }), ruleBadges, "rules", ruleList);

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
      attList.append(row);
    }
    section(t.attention, [attList]);

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
