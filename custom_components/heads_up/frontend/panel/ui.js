// Heads Up panel: helpers the editor pages share (D-119). The shell loads this module once and
// passes it to every page as ctx.ui, so a page never imports another file by a bare URL.

export function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(typeof child === "string" ? document.createTextNode(child) : child);
  return created;
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
.hu-page .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; }
.hu-page ul.list { list-style: none; margin: 0; padding: 0; }
.hu-page ul.list li { display: flex; gap: 8px; align-items: center; justify-content: space-between; padding: 8px 0; border-top: 1px solid var(--divider-color); min-height: 48px; }
.hu-page ul.list li.dim { opacity: .55; }
.hu-page button.help { min-width: 24px; min-height: 24px; width: 24px; height: 24px; padding: 0; margin-left: 6px; border-radius: 50%; border: 1px solid var(--divider-color); background: transparent; color: var(--secondary-text-color); font: inherit; font-size: 13px; line-height: 1; cursor: help; vertical-align: middle; }
.hu-page button.help[aria-expanded="true"], .hu-page button.help:hover { color: var(--primary-text-color); border-color: var(--primary-text-color); }
.hu-page button.help:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-page .tip { display: none; margin: 6px 0; padding: 8px 10px; border-radius: 8px; background: var(--secondary-background-color); color: var(--primary-text-color); font-size: 13px; font-weight: normal; max-width: 460px; }
.hu-page .tip.open { display: block; }
.hu-page .badge { border-radius: 12px; padding: 2px 10px; font-size: 12px; background: var(--secondary-background-color); border: 1px solid var(--divider-color); margin-left: 6px; }
.hu-page .badge.bad { color: var(--error-color); border-color: var(--error-color); }
.hu-page label.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.hu-page label.inline { display: flex; align-items: center; gap: 10px; min-height: 48px; }
.hu-page input[type=text], .hu-page input[type=number], .hu-page input[type=time], .hu-page select { min-height: 40px; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; max-width: 360px; }
.hu-page input[type=checkbox], .hu-page input[type=radio] { width: 22px; height: 22px; }
.hu-page fieldset { border: 1px solid var(--divider-color); border-radius: 8px; margin: 0 0 12px; padding: 8px 12px; }
.hu-page fieldset.scroll { max-height: 200px; overflow: auto; }
.hu-page legend { padding: 0 6px; color: var(--secondary-text-color); font-size: 13px; }
.hu-page button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-page button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-page button.danger { color: var(--error-color); border-color: var(--error-color); }
.hu-page button:disabled { opacity: .5; cursor: default; }
.hu-page button:focus-visible, .hu-page input:focus-visible, .hu-page select:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-page .problems { color: var(--error-color); }
.hu-page .ok { color: var(--success-color); }
.hu-page pre { background: var(--secondary-background-color); border-radius: 8px; padding: 10px; overflow: auto; font-size: 12px; margin: 4px 0 12px; }
.hu-page .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
`;

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
    time_invalid: "Enter a valid time.",
    wait_invalid: "Enter 0 or more minutes.",
    when_required: "Choose when to use this fallback.",
    target_exclusive: "Give either an audience or recipients for this channel.",
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
    time_invalid: "Gib eine gültige Uhrzeit ein.",
    wait_invalid: "Gib 0 oder mehr Minuten ein.",
    when_required: "Wähle, wann dieser Ersatz verwendet wird.",
    target_exclusive: "Gib für diesen Kanal entweder eine Zielgruppe oder Empfänger an.",
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
    time_invalid: "Saisissez une heure valide.",
    wait_invalid: "Saisissez 0 minute ou plus.",
    when_required: "Choisissez quand utiliser ce repli.",
    target_exclusive: "Indiquez soit une audience soit des destinataires pour ce canal.",
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
    time_invalid: "Introduce una hora válida.",
    wait_invalid: "Introduce 0 o más minutos.",
    when_required: "Elige cuándo usar esta alternativa.",
    target_exclusive: "Indica una audiencia o destinatarios para este canal.",
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
  const area = (choices.areas || []).find((a) => a.id === value);
  if (area) return area.name;
  return value;
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
    const options = [{ value: "", label: "—" }, ...choices.audience_names.map((n) => ({ value: n, label: n }))];
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
