// Heads Up panel: Recipients page (D-119): profiles of persons and groups of speakers.

export const STRINGS = {
  en: {
    title: "Recipients",
    intro: "Who can receive what. A tick means the person accepts the channel and it can work. A mark means it is accepted but cannot work yet; point at it for the reason. Open a person to change devices, channels and the mail address.",
    profiles: "People",
    groups: "Speaker groups",
    group_intro: "A group stands for its speakers. In calls it is written as the group name followed by (group).",
    device_detected: "detected",
    device_manual: "added",
    device_missing_service: "service not found",
    device_removed: "removed",
    no_devices: "No device: push is skipped for this person.",
    no_user: "No Home Assistant user: no popup.",
    primary: "Primary device",
    remove: "Remove this device",
    add_device: "Add a device",
    add_device_none: "Choose a device…",
    channels: "Accepted channels",
    enabled: "Receives notifications",
    enabled_hint: "Off: this person gets nothing on any channel, also not critical messages or messages that name them directly. Banners without a target stay visible on their dashboard. Devices and channels below are kept for when you switch it on again.",
    disabled: "disabled",
    channel_banner: "Banner",
    channel_push: "Push",
    channel_popup: "Popup",
    channel_mail: "Mail",
    mail_address: "Mail address",
    mail_address_hint: "Where this person's mail goes. Mail also has to be switched on in the accepted channels. Without an address, mail to this person fails.",
    person: "Person",
    ch_none: "no channel",
    ch_on: "accepted",
    ch_off: "not accepted",
    ch_warn_device: "no device",
    ch_warn_user: "no Home Assistant user",
    ch_warn_address: "no address",
    members: "Speakers",
    areas: "Areas",
    new_group: "New group",
    edit_group: "Edit group",
    call_name: "In calls: {name}",
    speakers_now: "{n} speakers reach it now",
    none_groups: "You have no speaker groups yet.",
    reset: "Reset to the detected devices",
  },
  de: {
    title: "Empfänger",
    intro: "Wer was erhalten kann. Ein Haken heißt: Die Person nimmt den Kanal an und er kann funktionieren. Ein Zeichen heißt: angenommen, aber noch nicht nutzbar; zeige darauf für den Grund. Öffne eine Person, um Geräte, Kanäle und die E-Mail-Adresse zu ändern.",
    profiles: "Personen",
    groups: "Lautsprechergruppen",
    group_intro: "Eine Gruppe steht für ihre Lautsprecher. In Aufrufen wird sie als Gruppenname gefolgt von (group) geschrieben.",
    device_detected: "gefunden",
    device_manual: "hinzugefügt",
    device_missing_service: "Dienst nicht gefunden",
    device_removed: "entfernt",
    no_devices: "Kein Gerät: Push wird für diese Person übersprungen.",
    no_user: "Kein Home-Assistant-Benutzer: kein Popup.",
    primary: "Hauptgerät",
    remove: "Dieses Gerät entfernen",
    add_device: "Gerät hinzufügen",
    add_device_none: "Gerät wählen…",
    channels: "Angenommene Kanäle",
    enabled: "Erhält Benachrichtigungen",
    enabled_hint: "Aus: Diese Person erhält auf keinem Kanal etwas, auch keine kritischen Meldungen und auch nicht, wenn sie direkt genannt wird. Banner ohne Ziel bleiben auf ihrem Dashboard sichtbar. Geräte und Kanäle unten bleiben für das Wiedereinschalten erhalten.",
    disabled: "deaktiviert",
    channel_banner: "Banner",
    channel_push: "Push",
    channel_popup: "Popup",
    channel_mail: "E-Mail",
    mail_address: "E-Mail-Adresse",
    mail_address_hint: "Wohin die Mail dieser Person geht. E-Mail muss auch bei den angenommenen Kanälen aktiviert sein. Ohne Adresse scheitert Mail an diese Person.",
    person: "Person",
    ch_none: "kein Kanal",
    ch_on: "angenommen",
    ch_off: "nicht angenommen",
    ch_warn_device: "kein Gerät",
    ch_warn_user: "kein Home-Assistant-Benutzer",
    ch_warn_address: "keine Adresse",
    members: "Lautsprecher",
    areas: "Bereiche",
    new_group: "Neue Gruppe",
    edit_group: "Gruppe bearbeiten",
    call_name: "In Aufrufen: {name}",
    speakers_now: "{n} Lautsprecher erreichen sie jetzt",
    none_groups: "Du hast noch keine Lautsprechergruppen.",
    reset: "Auf die gefundenen Geräte zurücksetzen",
  },
  fr: {
    title: "Destinataires",
    intro: "Qui peut recevoir quoi. Une coche signifie que la personne accepte le canal et qu'il peut fonctionner. Un signe signifie accepté mais pas encore utilisable ; survolez-le pour la raison. Ouvrez une personne pour changer appareils, canaux et adresse e-mail.",
    profiles: "Personnes",
    groups: "Groupes de haut-parleurs",
    group_intro: "Un groupe représente ses haut-parleurs. Dans les appels, il s'écrit avec le nom du groupe suivi de (group).",
    device_detected: "détecté",
    device_manual: "ajouté",
    device_missing_service: "service introuvable",
    device_removed: "retiré",
    no_devices: "Aucun appareil : le push est ignoré pour cette personne.",
    no_user: "Pas d'utilisateur Home Assistant : pas de fenêtre contextuelle.",
    primary: "Appareil principal",
    remove: "Retirer cet appareil",
    add_device: "Ajouter un appareil",
    add_device_none: "Choisir un appareil…",
    channels: "Canaux acceptés",
    enabled: "Reçoit les notifications",
    enabled_hint: "Désactivé : cette personne ne reçoit rien sur aucun canal, pas même les messages critiques ni quand elle est nommée directement. Les bannières sans cible restent visibles sur son tableau de bord. Les appareils et canaux ci-dessous sont conservés pour la réactivation.",
    disabled: "désactivé",
    channel_banner: "Bannière",
    channel_push: "Push",
    channel_popup: "Fenêtre",
    channel_mail: "Courriel",
    mail_address: "Adresse de courriel",
    mail_address_hint: "Où va le courriel de cette personne. Courriel doit aussi être activé dans les canaux acceptés. Sans adresse, le courriel à cette personne échoue.",
    person: "Personne",
    ch_none: "aucun canal",
    ch_on: "accepté",
    ch_off: "non accepté",
    ch_warn_device: "aucun appareil",
    ch_warn_user: "aucun utilisateur Home Assistant",
    ch_warn_address: "aucune adresse",
    members: "Haut-parleurs",
    areas: "Zones",
    new_group: "Nouveau groupe",
    edit_group: "Modifier le groupe",
    call_name: "Dans les appels : {name}",
    speakers_now: "{n} haut-parleurs l'atteignent maintenant",
    none_groups: "Vous n'avez pas encore de groupe de haut-parleurs.",
    reset: "Revenir aux appareils détectés",
  },
  es: {
    title: "Destinatarios",
    intro: "Quién puede recibir qué. Una marca de verificación significa que la persona acepta el canal y puede funcionar. Un signo significa aceptado pero aún sin poder funcionar; apunta a él para ver el motivo. Abre una persona para cambiar dispositivos, canales y la dirección de correo.",
    profiles: "Personas",
    groups: "Grupos de altavoces",
    group_intro: "Un grupo representa a sus altavoces. En las llamadas se escribe con el nombre del grupo seguido de (group).",
    device_detected: "detectado",
    device_manual: "añadido",
    device_missing_service: "servicio no encontrado",
    device_removed: "quitado",
    no_devices: "Sin dispositivo: el push se omite para esta persona.",
    no_user: "Sin usuario de Home Assistant: sin ventana emergente.",
    primary: "Dispositivo principal",
    remove: "Quitar este dispositivo",
    add_device: "Añadir un dispositivo",
    add_device_none: "Elige un dispositivo…",
    channels: "Canales aceptados",
    enabled: "Recibe notificaciones",
    enabled_hint: "Desactivado: esta persona no recibe nada por ningún canal, ni mensajes críticos ni aunque se la nombre directamente. Los banners sin destino siguen visibles en su panel. Los dispositivos y canales de abajo se conservan para cuando la reactives.",
    disabled: "desactivado",
    channel_banner: "Aviso",
    channel_push: "Push",
    channel_popup: "Ventana",
    channel_mail: "Correo",
    mail_address: "Dirección de correo",
    mail_address_hint: "A dónde va el correo de esta persona. Correo también debe estar activado en los canales aceptados. Sin dirección, el correo a esta persona falla.",
    person: "Persona",
    ch_none: "ningún canal",
    ch_on: "aceptado",
    ch_off: "no aceptado",
    ch_warn_device: "sin dispositivo",
    ch_warn_user: "sin usuario de Home Assistant",
    ch_warn_address: "sin dirección",
    members: "Altavoces",
    areas: "Áreas",
    new_group: "Nuevo grupo",
    edit_group: "Editar grupo",
    call_name: "En las llamadas: {name}",
    speakers_now: "{n} altavoces lo alcanzan ahora",
    none_groups: "Aún no tienes grupos de altavoces.",
    reset: "Volver a los dispositivos detectados",
  },
};

// The channels a profile can accept, in the order of the list.
export const PROFILE_CHANNELS = ["banner", "push", "popup", "mail"];
const DEFAULT_CHANNELS = ["banner", "push", "popup"]; // mail is opt-in per person

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// The editable values of a profile: what is manual, what was removed, the primary and the channels.
export function profileValues(profile) {
  return {
    manual: profile.devices.filter((d) => d.source === "manual").map((d) => d.device_id),
    removed: [...(profile.removed || [])],
    primary: profile.primary || "",
    channels: [...profile.channels],
    mail_address: profile.mail_address || "",
    enabled: profile.enabled !== false,
  };
}

// A profile equal to the detected devices needs no subentry.
export function isDefault(values) {
  return (
    values.enabled !== false &&
    values.manual.length === 0 &&
    values.removed.length === 0 &&
    !values.primary &&
    !values.mail_address &&
    PROFILE_CHANNELS.every((c) => values.channels.includes(c) === DEFAULT_CHANNELS.includes(c))
  );
}

export function toProfileData(person, values, creating) {
  const data = { channels: PROFILE_CHANNELS.filter((c) => values.channels.includes(c)) };
  if (creating) data.person = person;
  if (values.enabled === false) data.enabled = false;
  if (values.manual.length) data.devices = [...values.manual];
  if (values.removed.length) data.removed_devices = [...values.removed];
  if (values.primary) data.primary = values.primary;
  if (String(values.mail_address || "").trim()) data.mail_address = String(values.mail_address).trim();
  return data;
}

// A device can be removed (detected ones) or dropped again (added ones); the primary must stay in use.
export function removeDevice(values, deviceId, source) {
  const next = { ...values, manual: [...values.manual], removed: [...values.removed] };
  if (source === "manual") next.manual = next.manual.filter((id) => id !== deviceId);
  else if (!next.removed.includes(deviceId)) next.removed.push(deviceId);
  if (next.primary === deviceId) next.primary = "";
  return next;
}

export function restoreDevice(values, deviceId) {
  return { ...values, removed: values.removed.filter((id) => id !== deviceId) };
}

export function addDevice(values, deviceId) {
  if (!deviceId || values.manual.includes(deviceId)) return values;
  return { ...values, manual: [...values.manual, deviceId], removed: values.removed.filter((id) => id !== deviceId) };
}

export function validateGroup(values, existing, ownName) {
  const problems = {};
  const name = String(values.name || "").trim();
  const taken = existing.filter((n) => n.toLowerCase() !== String(ownName || "").toLowerCase());
  if (!name) problems.name = "name_required";
  else if (name.toLowerCase().endsWith(" (group)")) problems.name = "name_has_suffix";
  else if (taken.some((n) => n.toLowerCase() === name.toLowerCase())) problems.name = "name_exists";
  if ((values.members || []).length === 0 && (values.areas || []).length === 0) problems.members = "group_empty";
  return problems;
}

export function groupData(values) {
  return { name: String(values.name).trim(), members: [...values.members], areas: [...values.areas] };
}

// How one channel stands for one person: "off" (not accepted), "on", or "on" with a `warn` when it
// is accepted but cannot work: push without a usable device, popup without a Home Assistant user,
// mail without an address.
export function channelState(profile, channel) {
  if (!(profile.channels || []).includes(channel)) return { channel, state: "off", warn: null };
  let warn = null;
  if (channel === "push" && !(profile.devices || []).some((d) => d.service_found)) warn = "device";
  if (channel === "popup" && !profile.user) warn = "user";
  if (channel === "mail" && !String(profile.mail_address || "").trim()) warn = "address";
  return { channel, state: "on", warn };
}

const PEOPLE_CSS = `
table.people { width: 100%; border-collapse: collapse; }
table.people th, table.people td { text-align: left; padding: 8px; border-top: 1px solid var(--divider-color); vertical-align: middle; }
table.people thead th { border-top: 0; font-weight: 500; color: var(--secondary-text-color); }
table.people .ch { text-align: center; width: 72px; }
table.people td.ch.on { color: var(--success-color, #2e7d32); }
table.people td.ch.warn { color: var(--warning-color, #b26a00); font-weight: 700; }
table.people td.ch.off { color: var(--secondary-text-color); }
table.people .go { width: 1%; white-space: nowrap; text-align: right; }
table.people tr.dim .who, table.people tr.dim td.ch { opacity: .55; }
table.people .sub.narrow { display: none; }
@media (max-width: 560px) {
  table.people thead, table.people td.ch { display: none; }
  table.people .sub.narrow { display: block; }
}
`;

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let profile = null; // { person, values, view }
  let group = null; // { own, values }
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);
  const regName = (id) => data.choices.registrations.find((r) => r.id === id)?.name ?? id;

  function profileRow(p) {
    const edit = el("button", { type: "button", textContent: s.common.edit });
    edit.addEventListener("click", () => {
      message = "";
      profile = { person: p.person, view: p, values: profileValues(p) };
      render();
    });
    const off = p.enabled === false;
    const states = PROFILE_CHANNELS.map((channel) => channelState(p, channel));
    // Narrow screens: the accepted channels under the name, a problem written after its channel.
    const words = states
      .filter((c) => c.state !== "off")
      .map((c) => `${s.channel[c.channel]}${c.warn ? ` (${t[`ch_warn_${c.warn}`]})` : ""}`);
    const sub = words.join(", ") || t.ch_none;
    const name = [el("strong", { textContent: p.name })];
    if (off) name.push(el("span", { className: "badge", textContent: t.disabled }));
    const cells = states.map((c) => {
      const mark = c.state === "off" ? "–" : c.warn ? "!" : "✓";
      const cell = el("td", { className: `ch ${c.state === "off" ? "off" : c.warn ? "warn" : "on"}`, textContent: mark });
      cell.setAttribute("aria-label", `${s.channel[c.channel]}: ${c.state === "off" ? t.ch_off : c.warn ? t[`ch_warn_${c.warn}`] : t.ch_on}`);
      if (c.warn) cell.title = t[`ch_warn_${c.warn}`];
      return cell;
    });
    return el("tr", { className: off ? "dim" : "" }, [
      el("td", { className: "who" }, [el("div", {}, name), el("div", { className: "sub narrow", textContent: sub })]),
      ...cells,
      el("td", { className: "go" }, [edit]),
    ]);
  }

  function peopleTable() {
    const head = el("tr", {}, [
      el("th", { textContent: t.person }),
      ...PROFILE_CHANNELS.map((c) => el("th", { className: "ch", textContent: s.channel[c] })),
      el("th", { className: "go" }),
    ]);
    return el("table", { className: "people" }, [el("thead", {}, [head]), el("tbody", {}, data.profiles.map(profileRow))]);
  }

  function profileEditor() {
    const { view } = profile;
    const values = profile.values;
    const box = el("section", {}, [el("h2", { textContent: view.name })]);
    box.append(ui.checkbox(t.enabled, values.enabled !== false, (on) => { values.enabled = on; render(); }));
    box.append(el("div", { className: "hint", textContent: t.enabled_hint }));
    if (!view.user) box.append(el("div", { className: "hint problems", textContent: t.no_user }));
    const devices = [];
    for (const d of view.devices) {
      const kept = d.source === "manual" ? values.manual.includes(d.device_id) : !values.removed.includes(d.device_id);
      if (kept) devices.push(d);
    }
    for (const id of values.manual) {
      if (!view.devices.some((d) => d.device_id === id)) {
        devices.push({ device_id: id, name: regName(id), service_found: true, source: "manual" });
      }
    }
    const list = el("ul", { className: "list" });
    if (devices.length === 0) list.append(el("li", { className: "sub", textContent: t.no_devices }));
    for (const d of devices) {
      const radio = el("input", { type: "radio", name: "primary", checked: values.primary === d.device_id });
      radio.addEventListener("change", () => { values.primary = d.device_id; render(); });
      const drop = el("button", { type: "button", textContent: t.remove });
      drop.addEventListener("click", () => { profile.values = removeDevice(values, d.device_id, d.source); render(); });
      const bad = d.service_found ? [] : [el("span", { className: "badge bad", textContent: t.device_missing_service })];
      list.append(el("li", {}, [el("label", { className: "inline" }, [radio, el("span", { textContent: `${d.name || d.device_id} · ${d.source === "manual" ? t.device_manual : t.device_detected}` }), ...bad]), drop]));
    }
    box.append(el("div", { className: "hint", textContent: t.primary }), list);
    for (const id of values.removed) {
      const back = el("button", { type: "button", textContent: `${regName(id)} · ${t.device_removed} · ${s.common.add}` });
      back.addEventListener("click", () => { profile.values = restoreDevice(values, id); render(); });
      box.append(back);
    }
    const present = new Set([...view.devices.map((d) => d.device_id), ...values.manual]);
    const options = [{ value: "", label: t.add_device_none }, ...data.choices.registrations.filter((r) => !present.has(r.id) || values.removed.includes(r.id)).map((r) => ({ value: r.id, label: r.name }))];
    box.append(ui.field(t.add_device, ui.selectInput(options, "", (v) => { profile.values = addDevice(values, v); render(); })));
    box.append(ui.field(t.mail_address, ui.textInput(values.mail_address || "", (v) => { values.mail_address = v; }), t.mail_address_hint));
    box.append(ui.chips(t.channels, PROFILE_CHANNELS.map((c) => ({ value: c, label: t[`channel_${c}`] })), values.channels, (list) => { values.channels = list; }));
    const status = el("div", { className: "hint", textContent: message });
    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.disabled = values.channels.length === 0;
    save.addEventListener("click", saveProfile);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", () => { profile = null; render(); });
    const row = el("div", { className: "row" }, [save, cancel]);
    if (view.subentry_id) {
      const reset = el("button", { type: "button", className: "danger", textContent: t.reset });
      reset.addEventListener("click", resetProfile);
      row.append(reset);
    }
    box.append(status, row);
    if (view.subentry_id) box.append(el("div", { className: "hint", textContent: s.common.yaml }), el("pre", { textContent: ui.toYaml({ person: view.person, enabled: values.enabled !== false, channels: values.channels, devices: values.manual, removed_devices: values.removed, primary: values.primary || null, mail_address: values.mail_address || null }) }));
    return box;
  }

  function groupRow(g) {
    const edit = el("button", { type: "button", textContent: s.common.edit });
    edit.addEventListener("click", () => { message = ""; group = { own: g, values: { name: g.name, members: [...(g.data.members || [])], areas: [...(g.data.areas || [])] } }; render(); });
    const used = g.used_by.length ? ` · ${g.used_by.join(", ")}` : "";
    return el("li", {}, [el("div", {}, [el("strong", { textContent: g.name }), el("div", { className: "sub", textContent: `${fill(t.call_name, { name: g.call_name })} · ${fill(t.speakers_now, { n: g.speakers.length })}${used}` })]), edit]);
  }

  function groupEditor() {
    const { own, values } = group;
    const box = el("section", {}, [el("h2", { textContent: own ? t.edit_group : t.new_group })]);
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; paint(); })));
    box.append(ui.chips(t.members, data.choices.speakers.map((id) => ({ value: id, label: ui.recipientLabel(id, data.choices) })), values.members, (list) => { values.members = list; paint(); }, true));
    box.append(ui.chips(t.areas, data.choices.areas.map((a) => ({ value: a.id, label: a.name })), values.areas, (list) => { values.areas = list; paint(); }, true));
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", saveGroup);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", () => { group = null; render(); });
    const row = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const blocked = own.used_by.length > 0;
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete, disabled: blocked });
      del.addEventListener("click", removeGroup);
      row.append(del);
      if (blocked) box.append(el("div", { className: "hint problems", textContent: fill(s.common.in_use, { names: own.used_by.join(", ") }) }));
    }
    box.append(status, row);
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), el("pre", { textContent: ui.toYaml({ name: own.name, ...own.data }) }));
    function paint() {
      const found = validate();
      const codes = Object.values(found);
      save.disabled = codes.length > 0;
      status.className = codes.length ? "hint problems" : "hint ok";
      status.textContent = codes.length ? codes.map((c) => ui.errorText(c, ctx.language)).join(" ") : message || s.common.valid;
    }
    paint();
    return box;
  }

  const validate = () => validateGroup(group.values, data.groups.map((g) => g.name), group.own?.name);

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + PEOPLE_CSS }), el("h1", { textContent: t.title }));
    if (profile) return void root.append(profileEditor());
    if (group) return void root.append(groupEditor());
    root.append(el("div", { className: "hint", textContent: t.intro }));
    root.append(el("section", {}, [el("h2", { textContent: t.profiles }), peopleTable()]));
    const groups = el("ul", { className: "list" }, data.groups.length ? data.groups.map(groupRow) : [el("li", { className: "sub", textContent: t.none_groups })]);
    const add = el("button", { type: "button", className: "primary", textContent: s.common.add });
    add.addEventListener("click", () => { message = ""; group = { own: null, values: { name: "", members: [], areas: [] } }; render(); });
    root.append(el("section", {}, [el("h2", { textContent: t.groups }), el("div", { className: "hint", textContent: t.group_intro }), groups, add]));
  }

  async function saveProfile() {
    const { person, view, values } = profile;
    if (isDefault(values)) {
      if (view.subentry_id) await ui.removeSubentry(hass, data.entry_id, view.subentry_id);
    } else {
      const result = await ui.runFlow(hass, data.entry_id, "recipient_profile", view.subentry_id, toProfileData(person, values, !view.subentry_id));
      if (!result.ok) {
        message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
        render();
        return;
      }
    }
    profile = null;
    message = "";
    await load();
  }

  async function resetProfile() {
    await ui.removeSubentry(hass, data.entry_id, profile.view.subentry_id);
    profile = null;
    await load();
  }

  async function saveGroup() {
    const { own, values } = group;
    const result = await ui.runFlow(hass, data.entry_id, "recipient_group", own?.subentry_id, groupData(values));
    if (!result.ok) {
      message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      render();
      return;
    }
    group = null;
    message = "";
    await load();
  }

  async function removeGroup() {
    const { own } = group;
    if (own.used_by.length > 0 || !window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
    await ui.removeSubentry(hass, data.entry_id, own.subentry_id);
    group = null;
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
