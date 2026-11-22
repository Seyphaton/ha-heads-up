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
    col_audience: "Audience",
    col_now: "Right now",
    col_used: "Messages",
    nobody: "Nobody",
    people_n: "{n} people",
    people_1: "1 person",
    count_n: "{n} messages",
    count_1: "1 message",
    count_0: "None yet",
    last_used: "last {when}",
    members_label: "Members right now",
    policies_label: "Policies",
    no_policy: "No policy uses it",
    usage_label: "Messages sent to it",
    usage_hint: "Counted once per message, kept across restarts.",
    show_log: "Show in Message Log",
    sensor_label: "Sensor for calls",
    intro: "An audience is a named group of people that calls and policies can address. The members are worked out when a delivery is made.",
    builtin: "Built in",
    custom: "Your audiences",
    none_custom: "You have no audiences yet.",
    entity_id: "Entity ID of the sensor",
    entity_id_new: "Home Assistant gives the audience this sensor when you save. Name the audience in a call by this ID: it keeps working when you rename the audience.",
    entity_id_own: "A rename does not change this ID. A call that names the audience by its text name is refused; a call that uses this ID is not.",
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
    col_audience: "Zielgruppe",
    col_now: "Jetzt",
    col_used: "Meldungen",
    nobody: "Niemand",
    people_n: "{n} Personen",
    people_1: "1 Person",
    count_n: "{n} Meldungen",
    count_1: "1 Meldung",
    count_0: "Noch keine",
    last_used: "zuletzt {when}",
    members_label: "Mitglieder jetzt",
    policies_label: "Richtlinien",
    no_policy: "Keine Richtlinie nutzt sie",
    usage_label: "Meldungen an sie",
    usage_hint: "Einmal pro Meldung gezählt, bleibt über Neustarts erhalten.",
    show_log: "Im Meldungsprotokoll zeigen",
    sensor_label: "Sensor für Aufrufe",
    intro: "Eine Zielgruppe ist eine benannte Personengruppe, die Aufrufe und Richtlinien ansprechen können. Die Mitglieder werden bei der Zustellung bestimmt.",
    builtin: "Eingebaut",
    custom: "Deine Zielgruppen",
    none_custom: "Du hast noch keine Zielgruppen.",
    entity_id: "Entitäts-ID des Sensors",
    entity_id_new: "Home Assistant legt beim Speichern diesen Sensor für die Zielgruppe an. Nenne die Zielgruppe in einem Aufruf mit dieser ID: Sie gilt weiter, wenn du die Zielgruppe umbenennst.",
    entity_id_own: "Eine Umbenennung ändert diese ID nicht. Ein Aufruf, der die Zielgruppe mit ihrem Namen nennt, wird abgelehnt; ein Aufruf mit dieser ID nicht.",
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
    col_audience: "Audience",
    col_now: "En ce moment",
    col_used: "Messages",
    nobody: "Personne",
    people_n: "{n} personnes",
    people_1: "1 personne",
    count_n: "{n} messages",
    count_1: "1 message",
    count_0: "Aucun pour l'instant",
    last_used: "dernier {when}",
    members_label: "Membres en ce moment",
    policies_label: "Politiques",
    no_policy: "Aucune politique ne l'utilise",
    usage_label: "Messages envoyés",
    usage_hint: "Compté une fois par message, conservé après un redémarrage.",
    show_log: "Voir dans le journal des messages",
    sensor_label: "Capteur pour les appels",
    intro: "Une audience est un groupe nommé de personnes que les appels et les politiques peuvent viser. Les membres sont déterminés lors d'une livraison.",
    builtin: "Intégrées",
    custom: "Vos audiences",
    none_custom: "Vous n'avez pas encore d'audience.",
    entity_id: "ID d'entité du capteur",
    entity_id_new: "Home Assistant crée ce capteur pour l'audience à l'enregistrement. Nommez l'audience dans un appel par cet ID : il reste valable si vous renommez l'audience.",
    entity_id_own: "Renommer ne change pas cet ID. Un appel qui désigne l'audience par son nom est refusé ; un appel qui utilise cet ID ne l'est pas.",
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
    col_audience: "Audiencia",
    col_now: "Ahora",
    col_used: "Mensajes",
    nobody: "Nadie",
    people_n: "{n} personas",
    people_1: "1 persona",
    count_n: "{n} mensajes",
    count_1: "1 mensaje",
    count_0: "Ninguno aún",
    last_used: "último {when}",
    members_label: "Miembros ahora",
    policies_label: "Políticas",
    no_policy: "Ninguna política la usa",
    usage_label: "Mensajes enviados",
    usage_hint: "Se cuenta una vez por mensaje y se conserva tras reiniciar.",
    show_log: "Ver en el registro de mensajes",
    sensor_label: "Sensor para llamadas",
    intro: "Una audiencia es un grupo con nombre de personas al que pueden dirigirse las llamadas y las políticas. Los miembros se calculan al hacer una entrega.",
    builtin: "Integradas",
    custom: "Tus audiencias",
    none_custom: "Aún no tienes audiencias.",
    entity_id: "ID de entidad del sensor",
    entity_id_new: "Home Assistant crea este sensor para la audiencia al guardar. Nombra la audiencia en una llamada con este ID: sigue valiendo si renombras la audiencia.",
    entity_id_own: "Renombrar no cambia este ID. Una llamada que nombra la audiencia por su texto se rechaza; una que usa este ID no.",
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

// The icon of an audience by its kind: the built-in ones and the two kinds of your own.
export const AUDIENCE_ICONS = {
  everyone: "mdi:account-group",
  admins: "mdi:shield-account",
  at_home: "mdi:home-account",
  not_home: "mdi:home-export-outline",
  last_to_leave: "mdi:exit-run",
  first_home: "mdi:home-import-outline",
  persons: "mdi:account-multiple",
};

export function audienceIcon(kind) {
  return AUDIENCE_ICONS[kind] || "mdi:account-group-outline";
}

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// Up to two initials of a name, for the member chips.
export function initials(name) {
  return String(name).trim().split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("") || "?";
}

// How many people are in it now, for the overview row.
export function peopleText(n, t) {
  return n === 1 ? t.people_1 : fill(t.people_n, { n });
}

export function countText(n, t) {
  if (!n) return t.count_0;
  return n === 1 ? t.count_1 : fill(t.count_n, { n });
}

// "12 messages, last 2 h ago" from the stored usage; "None yet" when it was never used.
export function usageText(usage, t, ago) {
  const n = usage?.count || 0;
  if (!n) return t.count_0;
  const when = usage.last ? ago(usage.last) : "";
  return when ? `${countText(n, t)} · ${fill(t.last_used, { when })}` : countText(n, t);
}

const PAGE_CSS = `
.hu-page .tl-list { margin-bottom: 16px; --tl-cols: minmax(0, 1fr) minmax(0, 1.2fr) minmax(0, 1fr); }
.hu-page .tl-title { margin: 8px 16px 4px; }
.hu-page .tl-list .tl-title + .tl-head + .tl-item { border-top: 1px solid var(--divider-color); }
.hu-page .aud-about { margin: 0 0 14px; font-size: 14px; line-height: 1.45; max-width: 70ch; }
.hu-page .aud-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
.hu-page .aud-tile { display: flex; flex-direction: column; gap: 8px; min-width: 0; padding: 12px 14px; border-radius: 10px; background: var(--card-background-color); border: 1px solid var(--divider-color); }
.hu-page .aud-label { color: var(--secondary-text-color); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
.hu-page .aud-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.hu-page .aud-chip { display: inline-flex; align-items: center; gap: 6px; max-width: 100%; padding: 3px 10px 3px 3px; border-radius: 16px; background: var(--hu-fill); border: 1px solid var(--divider-color); font-size: 13px; }
.hu-page .aud-chip.plain { padding: 4px 10px; }
.hu-page .aud-initial { display: inline-flex; align-items: center; justify-content: center; flex: none; width: 22px; height: 22px; border-radius: 50%; background: var(--primary-color); color: var(--text-primary-color, #fff); font-size: 11px; font-weight: 600; }
.hu-page .aud-empty { color: var(--secondary-text-color); font-size: 14px; }
.hu-page .aud-big { display: flex; align-items: baseline; gap: 6px; font-size: 14px; }
.hu-page .aud-number { font-size: 26px; font-weight: 600; line-height: 1; }
.hu-page .aud-sub { font-size: 13px; color: var(--secondary-text-color); }
.hu-page .aud-note { margin-top: auto; font-size: 12px; color: var(--secondary-text-color); }
.hu-page .aud-sensor { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; margin-top: 14px; }
.hu-page .aud-pill { display: inline-flex; align-items: center; gap: 8px; min-width: 0; max-width: 100%; padding: 2px 2px 2px 12px; border-radius: 8px; background: var(--card-background-color); border: 1px solid var(--divider-color); }
.hu-page .aud-pill code { font-size: 12px; overflow-wrap: anywhere; }
.hu-page .aud-pill .aud-copy { min-height: 32px; padding: 0 10px; font-size: 13px; }
.hu-page .aud-details .tl-actions { margin-top: 14px; }
.hu-page .aud-switch { min-height: 44px; }
`;

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

  let openKey = null; // the audience whose details are shown
  const names = (keys) => keys.map((k) => data.choices.persons.find((p) => p.id === k)?.name ?? k);
  const ago = (iso) => (iso ? ctx.fmt.timeAgo(iso, Date.now(), s) : "");

  async function toggle(audience, enabled) {
    try {
      await hass.callWS({ type: "heads_up/audience_enable", name: audience.name, enabled });
      message = "";
    } catch (err) {
      message = err?.code === "in_use" ? fill(s.common.in_use, { names: String(err.message || "").replace(/^.* is used by /, "") }) : t.off_failed;
    }
    await load();
  }

  // One table per section: name, who is in it now, how often it was used. A row opens the details:
  // members, policies, usage with a link to the Message Log, the sensor, and the switch or Edit.
  function tableNode(audiences, heading) {
    const box = el("section", { className: "tl-list" });
    box.append(el("h2", { className: "tl-title", textContent: heading }));
    box.append(ui.tableHead([t.col_audience, t.col_now, t.col_used]));
    for (const a of audiences) {
      const key = a.key || a.subentry_id || a.name;
      const id = `hu-aud-${String(key).replace(/[^a-zA-Z0-9_-]/g, "_")}`;
      const off = a.enabled === false;
      const isOpen = openKey === key;
      const now = off ? t.off : peopleText(a.members.length, t);
      const nowNames = a.members.length ? names(a.members).join(", ") : t.nobody;
      const used = usageText(a.usage, t, ago);
      const lead = [el("ha-icon", { icon: audienceIcon(a.kind) }), el("span", { className: "tl-name", textContent: a.name })];
      if (!a.builtin) lead.push(el("span", { className: "badge", textContent: t.kinds[a.kind] || a.kind }));
      if (off) lead.push(el("span", { className: "badge", textContent: t.off }));
      const { item } = ui.tableRow({
        id,
        lead,
        cells: [
          { label: t.col_now, node: el("span", { textContent: off ? t.off : a.members.length ? `${now}: ${nowNames}` : t.nobody, title: nowNames }), muted: off || !a.members.length },
          { label: t.col_used, node: el("span", { textContent: used }), muted: !a.usage?.count },
        ],
        open: isOpen,
        dim: off,
        label: `${a.name}: ${off ? t.off : nowNames}. ${used}`,
        onToggle: () => {
          openKey = isOpen ? null : key;
          render();
          root.querySelector(`[aria-controls="${id}"]`)?.focus();
        },
        body: isOpen ? detailsNode(a, key) : null,
      });
      box.append(item);
    }
    if (audiences.length === 0) box.append(el("div", { className: "tl-empty", textContent: t.none_custom }));
    return box;
  }

  // The details of one audience: what it is, three tiles (members, messages, policies), the sensor
  // with a copy button, then the actions.
  function detailsNode(a, key) {
    const body = el("div", { className: "aud-details" });
    const about = a.builtin ? t.tips[a.kind] : describe(fromAudience(a), data.choices, t);
    if (about) body.append(el("p", { className: "aud-about", textContent: about }));
    const count = a.usage?.count || 0;
    const tile = (label, content, extra) => el("div", { className: "aud-tile" }, [el("div", { className: "aud-label", textContent: label }), ...content, ...(extra ? [extra] : [])]);
    const members = a.members.length
      ? el("div", { className: "aud-chips" }, names(a.members).map((name) => el("span", { className: "aud-chip" }, [el("span", { className: "aud-initial", textContent: initials(name) }), el("span", { textContent: name })])))
      : el("div", { className: "aud-empty", textContent: t.nobody });
    const policies = a.used_by.length
      ? el("div", { className: "aud-chips" }, a.used_by.map((name) => el("span", { className: "aud-chip plain", textContent: name })))
      : el("div", { className: "aud-empty", textContent: t.no_policy });
    const usage = count
      ? [el("div", { className: "aud-big" }, [el("span", { className: "aud-number", textContent: String(count) }), el("span", { textContent: count === 1 ? t.count_1.replace(/^1\s*/, "") : t.count_n.replace("{n}", "").trim() })]), el("div", { className: "aud-sub", textContent: fill(t.last_used, { when: ago(a.usage.last) }) })]
      : [el("div", { className: "aud-empty", textContent: t.count_0 })];
    body.append(
      el("div", { className: "aud-tiles" }, [
        tile(t.members_label, [members]),
        tile(t.usage_label, usage, el("div", { className: "aud-note", textContent: t.usage_hint })),
        tile(t.policies_label, [policies]),
      ]),
    );
    if (a.entity_id) {
      const copy = el("button", { type: "button", className: "aud-copy", textContent: s.common.copy });
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(a.entity_id);
          copy.textContent = s.common.copied;
        } catch (err) {
          copy.textContent = s.common.copy_failed;
        }
      });
      body.append(el("div", { className: "aud-sensor" }, [el("span", { className: "aud-label", textContent: t.sensor_label }), el("span", { className: "aud-pill" }, [el("code", { textContent: a.entity_id }), copy])]));
    }
    const actions = el("div", { className: "tl-actions" });
    if (count) {
      const log = el("button", { type: "button", textContent: t.show_log });
      log.addEventListener("click", () => ctx.navigate("messages", { audience: key }));
      actions.append(log);
    }
    if (a.builtin) {
      const box2 = el("input", { type: "checkbox", checked: a.enabled !== false });
      box2.addEventListener("change", () => toggle(a, box2.checked));
      actions.append(el("label", { className: "inline aud-switch" }, [box2, el("span", { textContent: s.common.enabled })]));
    } else {
      const edit = el("button", { type: "button", className: "primary", textContent: s.common.edit });
      edit.addEventListener("click", () => open(a));
      actions.append(edit);
    }
    body.append(actions);
    if (a.enabled === false) body.append(el("div", { className: "hint", textContent: t.off_hint }));
    return body;
  }

  function listNode() {
    const out = [];
    if (message) out.push(el("div", { className: "hint problems", textContent: message, role: "alert" }));
    out.push(tableNode(data.audiences.filter((x) => x.builtin), t.builtin));
    out.push(tableNode(data.audiences.filter((x) => !x.builtin), t.custom));
    const add = el("button", { type: "button", className: "primary", textContent: t.new });
    add.addEventListener("click", () => open(null));
    out.push(el("div", { className: "tl-actions" }, [add]));
    return out;
  }

  function editorNode() {
    const { own, values } = editing;
    const rerender = () => render();
    const box = el("section", {}, [el("h2", { textContent: own ? t.editing : t.new })]);
    // The sensor of the audience: the registered ID, or the one a new audience will get (D-198).
    const entityLine = el("code", { className: "tpl", textContent: own?.entity_id || "…" });
    let entityTimer = null;
    const showEntity = (name) => {
      if (own) return; // a rename does not change the ID of an existing audience
      clearTimeout(entityTimer);
      if (!String(name).trim()) {
        entityLine.textContent = "…";
        return;
      }
      entityTimer = setTimeout(async () => {
        try {
          const reply = await hass.callWS({ type: "heads_up/audience_entity_id", name: String(name).trim() });
          entityLine.textContent = reply.entity_id;
        } catch (err) {
          entityLine.textContent = "…";
        }
      }, 250);
    };
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; showEntity(v); paint(); })));
    box.append(ui.field(t.entity_id, entityLine, own ? t.entity_id_own : t.entity_id_new));
    showEntity(values.name);
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
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), ui.yamlBlock(ui.toYaml({ name: own.name, ...own.data }), s.common));
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
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + ui.TABLE_CSS + PAGE_CSS }), el("h1", { textContent: t.title }));
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
