// Heads Up panel: Audiences page (D-119). Built in audiences are listed; custom ones are edited.

const KINDS = {
  en: { everyone: "Everyone", admins: "Administrators", persons: "Persons", at_home: "At home", not_home: "Not home", last_to_leave: "Last to leave", first_home: "First home", in_zone: "In a zone", not_in_zone: "Not in a zone", invalid: "Invalid" },
  de: { everyone: "Alle", admins: "Administratoren", persons: "Personen", at_home: "Zu Hause", not_home: "Nicht zu Hause", last_to_leave: "Als Letzter gegangen", first_home: "Als Erster angekommen", in_zone: "In einer Zone", not_in_zone: "Nicht in einer Zone", invalid: "Ungültig" },
  fr: { everyone: "Tout le monde", admins: "Administrateurs", persons: "Personnes", at_home: "À la maison", not_home: "Pas à la maison", last_to_leave: "Dernier parti", first_home: "Premier arrivé", in_zone: "Dans une zone", not_in_zone: "Hors d'une zone", invalid: "Invalide" },
  es: { everyone: "Todos", admins: "Administradores", persons: "Personas", at_home: "En casa", not_home: "Fuera de casa", last_to_leave: "El último en salir", first_home: "El primero en llegar", in_zone: "En una zona", not_in_zone: "Fuera de una zona", invalid: "No válida" },
};

export const STRINGS = {
  en: {
    title: "Audiences",
    intro: "An audience is a named group of people that calls and policies can address. The members are worked out when a delivery is made.",
    builtin: "Built in",
    custom: "Your audiences",
    none_custom: "You have no audiences yet.",
    members_now: "Right now: {names}",
    nobody_now: "Right now: nobody",
    used_by: "Used by {names}",
    unused: "Not used by any policy",
    new: "New audience",
    editing: "Edit audience",
    kind: "Kind",
    persons: "Persons",
    presence: "Presence",
    zone: "Zone",
    kind_persons: "Persons: a fixed list",
    kind_presence: "Presence: whoever matches when a delivery is made",
    unknown_presence: "Unknown presence counts for critical messages only; lower severities skip those people with a trace entry.",
    sentence_persons: "{names} (a fixed list).",
    sentence_presence: "People who are: {kind}{zone}.",
    limit_label: "Only these persons (none: everyone)",
    limit_hint: "Limits the audience, for example to one person for At home. For Last to leave and First home the person must also be the last to leave or the first home.",
    limited_to: " Limited to {names}.",
    off_failed: "Could not change this audience. Try again.",
    off: "Off",
    off_hint: "Switched off: calls and policies cannot use it.",
    kinds: KINDS.en,
    tip_label: "What is {name}?",
    tips: {
      everyone: "Every person in Home Assistant, wherever they are. Use it for messages the whole household should get.",
      admins: "People whose Home Assistant user is an administrator. Use it for technical messages, such as a failed backup.",
      at_home: "People who are home at the moment the message goes out. Use it to leave out people who are away.",
      not_home: "People whose state is anything but home, including a zone such as Work. Use it for news that matters to people who are away, such as a window left open.",
      last_to_leave: "The person whose departure left the house empty; nobody while anyone is home. Use it for messages like lights left on in an empty house.",
      first_home: "The first person to arrive after the house was empty; nobody while it is empty. Use it for something to know on arrival, such as an alarm still armed.",
    },
  },
  de: {
    title: "Zielgruppen",
    intro: "Eine Zielgruppe ist eine benannte Personengruppe, die Aufrufe und Richtlinien ansprechen können. Die Mitglieder werden bei der Zustellung bestimmt.",
    builtin: "Eingebaut",
    custom: "Deine Zielgruppen",
    none_custom: "Du hast noch keine Zielgruppen.",
    members_now: "Jetzt: {names}",
    nobody_now: "Jetzt: niemand",
    used_by: "Verwendet von {names}",
    unused: "Von keiner Richtlinie verwendet",
    new: "Neue Zielgruppe",
    editing: "Zielgruppe bearbeiten",
    kind: "Art",
    persons: "Personen",
    presence: "Anwesenheit",
    zone: "Zone",
    kind_persons: "Personen: eine feste Liste",
    kind_presence: "Anwesenheit: wer bei der Zustellung passt",
    unknown_presence: "Unbekannte Anwesenheit zählt nur für kritische Meldungen; niedrigere Schweregrade überspringen diese Personen mit einem Protokolleintrag.",
    sentence_persons: "{names} (eine feste Liste).",
    sentence_presence: "Personen, die: {kind}{zone}.",
    limit_label: "Nur diese Personen (keine: alle)",
    limit_hint: "Beschränkt die Zielgruppe, zum Beispiel auf eine Person für „Zu Hause“. Bei „Als Letzter gegangen“ und „Als Erster angekommen“ muss die Person auch die letzte beziehungsweise erste sein.",
    limited_to: " Beschränkt auf {names}.",
    off_failed: "Diese Zielgruppe konnte nicht geändert werden. Versuche es erneut.",
    off: "Aus",
    off_hint: "Ausgeschaltet: Aufrufe und Richtlinien können sie nicht nutzen.",
    kinds: KINDS.de,
    tip_label: "Was ist {name}?",
    tips: {
      everyone: "Alle Personen in Home Assistant, wo auch immer sie sind. Für Meldungen, die der ganze Haushalt bekommen soll.",
      admins: "Personen, deren Home-Assistant-Benutzer Administrator ist. Für technische Meldungen, etwa ein fehlgeschlagenes Backup.",
      at_home: "Personen, die zu Hause sind, wenn die Meldung versendet wird. Damit lässt du Personen aus, die unterwegs sind.",
      not_home: "Personen, deren Status nicht „home“ ist, auch in einer Zone wie Arbeit. Für Neuigkeiten, die Abwesende betreffen, etwa ein offenes Fenster.",
      last_to_leave: "Die Person, mit deren Weggang das Haus leer wurde; niemand, solange jemand zu Hause ist. Für Meldungen wie Licht an in einem leeren Haus.",
      first_home: "Die erste Person, die ankommt, nachdem das Haus leer war; niemand, solange es leer ist. Für etwas, das man bei der Ankunft wissen sollte, etwa eine noch scharfe Alarmanlage.",
    },
  },
  fr: {
    title: "Audiences",
    intro: "Une audience est un groupe nommé de personnes que les appels et les politiques peuvent viser. Les membres sont déterminés lors d'une livraison.",
    builtin: "Intégrées",
    custom: "Vos audiences",
    none_custom: "Vous n'avez pas encore d'audience.",
    members_now: "En ce moment : {names}",
    nobody_now: "En ce moment : personne",
    used_by: "Utilisée par {names}",
    unused: "Utilisée par aucune politique",
    new: "Nouvelle audience",
    editing: "Modifier l'audience",
    kind: "Type",
    persons: "Personnes",
    presence: "Présence",
    zone: "Zone",
    kind_persons: "Personnes : une liste fixe",
    kind_presence: "Présence : qui correspond lors d'une livraison",
    unknown_presence: "Une présence inconnue ne compte que pour les messages critiques ; les gravités plus basses ignorent ces personnes avec une entrée de trace.",
    sentence_persons: "{names} (une liste fixe).",
    sentence_presence: "Les personnes qui sont : {kind}{zone}.",
    limit_label: "Seulement ces personnes (aucune : toutes)",
    limit_hint: "Limite l'audience, par exemple à une personne pour À la maison. Pour Dernier parti et Premier arrivé, la personne doit aussi être la dernière partie ou la première arrivée.",
    limited_to: " Limitée à {names}.",
    off_failed: "Cette audience n'a pas pu être modifiée. Réessayez.",
    off: "Désactivée",
    off_hint: "Désactivée : les appels et les politiques ne peuvent pas l'utiliser.",
    kinds: KINDS.fr,
    tip_label: "Qu'est-ce que {name} ?",
    tips: {
      everyone: "Toutes les personnes de Home Assistant, où qu'elles soient. Pour les messages que tout le foyer doit recevoir.",
      admins: "Les personnes dont l'utilisateur Home Assistant est administrateur. Pour les messages techniques, comme une sauvegarde échouée.",
      at_home: "Les personnes à la maison au moment de l'envoi. Pour exclure celles qui sont absentes.",
      not_home: "Les personnes dont l'état n'est pas « home », y compris dans une zone comme Travail. Pour ce qui concerne les absents, comme une fenêtre restée ouverte.",
      last_to_leave: "La personne dont le départ a vidé la maison ; personne tant que quelqu'un est là. Pour des messages comme une lumière restée allumée dans une maison vide.",
      first_home: "La première personne à arriver après que la maison était vide ; personne tant qu'elle est vide. Pour ce qu'il faut savoir en arrivant, comme une alarme encore active.",
    },
  },
  es: {
    title: "Audiencias",
    intro: "Una audiencia es un grupo con nombre de personas al que pueden dirigirse las llamadas y las políticas. Los miembros se calculan al hacer una entrega.",
    builtin: "Integradas",
    custom: "Tus audiencias",
    none_custom: "Aún no tienes audiencias.",
    members_now: "Ahora: {names}",
    nobody_now: "Ahora: nadie",
    used_by: "Usada por {names}",
    unused: "No la usa ninguna política",
    new: "Nueva audiencia",
    editing: "Editar audiencia",
    kind: "Tipo",
    persons: "Personas",
    presence: "Presencia",
    zone: "Zona",
    kind_persons: "Personas: una lista fija",
    kind_presence: "Presencia: quien coincida al hacer una entrega",
    unknown_presence: "La presencia desconocida solo cuenta para mensajes críticos; las gravedades menores omiten a esas personas con una entrada de traza.",
    sentence_persons: "{names} (una lista fija).",
    sentence_presence: "Las personas que están: {kind}{zone}.",
    limit_label: "Solo estas personas (ninguna: todas)",
    limit_hint: "Limita la audiencia, por ejemplo a una persona para En casa. Para El último en salir y El primero en llegar, la persona debe ser también la última en salir o la primera en llegar.",
    limited_to: " Limitada a {names}.",
    off_failed: "No se pudo cambiar esta audiencia. Inténtalo de nuevo.",
    off: "Desactivada",
    off_hint: "Desactivada: las llamadas y las políticas no pueden usarla.",
    kinds: KINDS.es,
    tip_label: "¿Qué es {name}?",
    tips: {
      everyone: "Todas las personas de Home Assistant, estén donde estén. Para mensajes que debe recibir todo el hogar.",
      admins: "Personas cuyo usuario de Home Assistant es administrador. Para mensajes técnicos, como una copia de seguridad fallida.",
      at_home: "Personas que están en casa cuando sale el mensaje. Sirve para dejar fuera a quien está fuera.",
      not_home: "Personas cuyo estado no es «home», incluida una zona como Trabajo. Para lo que importa a quien está fuera, como una ventana abierta.",
      last_to_leave: "La persona cuya salida dejó la casa vacía; nadie mientras haya alguien en casa. Para mensajes como luces encendidas en una casa vacía.",
      first_home: "La primera persona en llegar tras estar la casa vacía; nadie mientras esté vacía. Para algo que conviene saber al llegar, como una alarma aún activada.",
    },
  },
};

const PRESENCE = ["at_home", "not_home", "last_to_leave", "first_home", "in_zone", "not_in_zone"];
const ZONE_KINDS = ["in_zone", "not_in_zone"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues() {
  return { name: "", kind: "persons", persons: [], presence: "at_home", zone: "", limit: [] };
}

export function fromAudience(audience) {
  const data = audience.data || {};
  if (data.kind === "persons") return { name: audience.name, kind: "persons", persons: [...(data.persons || [])], presence: "at_home", zone: "", limit: [] };
  return { name: audience.name, kind: "presence", persons: [], presence: data.presence || "at_home", zone: data.zone || "", limit: [...(data.limit || [])] };
}

// Problems as { field: code }; the codes are the integration's own flow error keys.
export function validate(values, existingNames, ownName) {
  const problems = {};
  const name = String(values.name || "").trim();
  const taken = existingNames.filter((n) => n.toLowerCase() !== String(ownName || "").toLowerCase());
  if (!name) problems.name = "name_required";
  else if (taken.some((n) => n.toLowerCase() === name.toLowerCase())) problems.name = "name_exists";
  if (values.kind === "persons") {
    if ((values.persons || []).length === 0) problems.persons = "persons_required";
  } else if (!values.presence) problems.presence = "presence_required";
  else if (ZONE_KINDS.includes(values.presence) && !values.zone) problems.zone = "zone_required";
  return problems;
}

export function toFlowData(values) {
  const data = { name: String(values.name).trim(), kind: values.kind };
  if (values.kind === "persons") data.persons = [...values.persons];
  else {
    data.presence = values.presence;
    if (ZONE_KINDS.includes(values.presence)) data.zone = values.zone;
    if ((values.limit || []).length) data.limit = [...values.limit];
  }
  return data;
}

export function describe(values, choices, t) {
  if (values.kind === "persons") {
    const names = (values.persons || []).map((id) => choices.persons.find((p) => p.id === id)?.name ?? id);
    return fill(t.sentence_persons, { names: names.join(", ") || "—" });
  }
  const zoneName = choices.zones.find((z) => z.id === values.zone)?.name ?? values.zone;
  const zone = ZONE_KINDS.includes(values.presence) ? ` (${zoneName || "—"})` : "";
  const limited = (values.limit || []).map((id) => choices.persons.find((p) => p.id === id)?.name ?? id);
  const limit = limited.length ? fill(t.limited_to, { names: limited.join(", ") }) : "";
  return fill(t.sentence_presence, { kind: t.kinds[values.presence] || values.presence, zone }) + limit;
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own: audience | null, values }
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const names = (keys) => keys.map((k) => data.choices.persons.find((p) => p.id === k)?.name ?? k);
  const memberLine = (audience) =>
    audience.members.length ? fill(t.members_now, { names: names(audience.members).join(", ") }) : t.nobody_now;
  const usedLine = (audience) =>
    audience.used_by.length ? fill(t.used_by, { names: audience.used_by.join(", ") }) : t.unused;

  async function toggle(audience, enabled) {
    try {
      await hass.callWS({ type: "heads_up/audience_enable", name: audience.name, enabled });
      message = "";
    } catch (err) {
      message = err?.code === "in_use" ? fill(s.common.in_use, { names: String(err.message || "").replace(/^.* is used by /, "") }) : t.off_failed;
    }
    await load();
  }

  function listNode() {
    const box = el("section", {}, [el("h2", { textContent: t.builtin })]);
    if (message) box.append(el("div", { className: "hint problems", textContent: message, role: "alert" }));
    const builtin = el("ul", { className: "list" });
    for (const a of data.audiences.filter((x) => x.builtin)) {
      const tip = t.tips[a.kind] ? ui.helpTip(fill(t.tip_label, { name: a.name }), t.tips[a.kind]) : null;
      const box2 = el("input", { type: "checkbox", checked: a.enabled !== false });
      box2.setAttribute("aria-label", `${s.common.enabled}: ${a.name}`);
      box2.addEventListener("change", () => toggle(a, box2.checked));
      const lines = a.enabled === false ? t.off_hint : `${memberLine(a)} · ${usedLine(a)}`;
      builtin.append(
        el("li", { className: a.enabled === false ? "dim" : "" }, [
          el("div", {}, [el("strong", { textContent: a.name }), ...(tip ? [tip.button] : []), ...(a.enabled === false ? [el("span", { className: "badge", textContent: t.off })] : []), ...(tip ? [tip.note] : []), el("div", { className: "sub", textContent: lines })]),
          el("label", { className: "inline" }, [box2]),
        ]),
      );
    }
    box.append(builtin);
    const mine = el("section", {}, [el("h2", { textContent: t.custom })]);
    const custom = data.audiences.filter((x) => !x.builtin);
    const list = el("ul", { className: "list" });
    if (custom.length === 0) list.append(el("li", { className: "sub", textContent: t.none_custom }));
    for (const a of custom) {
      const edit = el("button", { type: "button", textContent: s.common.edit });
      edit.addEventListener("click", () => open(a));
      list.append(el("li", {}, [el("div", {}, [el("strong", { textContent: a.name }), el("span", { className: "badge", textContent: t.kinds[a.kind] || a.kind }), el("div", { className: "sub", textContent: `${memberLine(a)} · ${usedLine(a)}` })]), edit]));
    }
    const add = el("button", { type: "button", className: "primary", textContent: s.common.add });
    add.addEventListener("click", () => open(null));
    mine.append(list, add);
    return [box, mine];
  }

  function editorNode() {
    const { own, values } = editing;
    const rerender = () => render();
    const box = el("section", {}, [el("h2", { textContent: own ? t.editing : t.new })]);
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; paint(); })));
    box.append(
      ui.field(t.kind, ui.selectInput(
        [{ value: "persons", label: t.kind_persons }, { value: "presence", label: t.kind_presence }],
        values.kind,
        (v) => { values.kind = v; rerender(); },
      )),
    );
    if (values.kind === "persons") {
      box.append(ui.chips(t.persons, data.choices.persons.map((p) => ({ value: p.id, label: p.name })), values.persons, (list) => { values.persons = list; paint(); }));
    } else {
      box.append(ui.field(t.presence, ui.selectInput(PRESENCE.map((k) => ({ value: k, label: t.kinds[k] })), values.presence, (v) => { values.presence = v; rerender(); })));
      if (ZONE_KINDS.includes(values.presence)) {
        box.append(ui.field(t.zone, ui.selectInput([{ value: "", label: "—" }, ...data.choices.zones.map((z) => ({ value: z.id, label: z.name }))], values.zone, (v) => { values.zone = v; paint(); })));
      }
      box.append(ui.chips(t.limit_label, data.choices.persons.map((p) => ({ value: p.id, label: p.name })), values.limit, (list) => { values.limit = list; paint(); }));
      box.append(el("div", { className: "hint", textContent: t.limit_hint }));
      box.append(el("div", { className: "hint", textContent: t.unknown_presence }));
    }
    const sentence = el("div", { className: "hint", id: "sentence" });
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", () => saveIt());
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", () => { editing = null; render(); });
    const row = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const blocked = own.used_by.length > 0;
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete, disabled: blocked });
      del.addEventListener("click", () => remove());
      row.append(del);
      if (blocked) box.append(el("div", { className: "hint problems", textContent: fill(s.common.in_use, { names: own.used_by.join(", ") }) }));
    }
    box.append(sentence, status, row);
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), el("pre", { textContent: ui.toYaml({ name: own.name, ...own.data }) }));
    function paint() {
      const found = validate(values, data.audiences.map((a) => a.name), own?.name);
      sentence.textContent = describe(values, data.choices, t);
      const codes = Object.values(found);
      save.disabled = codes.length > 0;
      status.className = codes.length ? "hint problems" : "hint ok";
      status.textContent = codes.length ? codes.map((c) => ui.errorText(c, ctx.language)).join(" ") : message || s.common.valid;
    }
    paint();
    return box;
  }

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    if (editing) root.append(editorNode());
    else root.append(...listNode());
  }

  function open(audience) {
    message = "";
    editing = { own: audience, values: audience ? fromAudience(audience) : blankValues() };
    render();
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "audience", own?.subentry_id, toFlowData(values));
    if (!result.ok) {
      message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      render();
      return;
    }
    message = "";
    editing = null;
    await load();
  }

  async function remove() {
    const { own } = editing;
    if (own.used_by.length > 0 || !window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
    await ui.removeSubentry(hass, data.entry_id, own.subentry_id);
    editing = null;
    await load();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    render();
  }

  root.append(el("div", { textContent: "…" }));
  load().catch(() => root.replaceChildren(el("div", { textContent: "…" })));
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      root.remove();
    },
  };
}
