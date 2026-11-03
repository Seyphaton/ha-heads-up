// Heads Up panel: Test send page (D-101, D-120). A preview of a call and the one real send.

export const STRINGS = {
  en: {
    title: "Test send",
    intro: "Try a call before you put it in an automation. The preview shows what would happen now, with the real clock and the real presence. Nothing is sent until you press Send test.",
    content: "Content",
    f_title: "Title (optional)",
    f_message: "Message",
    f_tts: "Spoken text (optional, speech only)",
    call: "The call",
    severity: "Severity",
    tag: "Tag (optional)",
    channels: "Channels",
    policy: "Policy",
    policy_all: "All that apply",
    policy_none: "None",
    who: "Who, per channel",
    banner_hint: "Banner: no target shows it to everyone; choose an audience or persons to limit it. An audience counts the people it has when the message is created.",
    target_channel: "Channel {channel}",
    target_audience: "Audience",
    target_recipients: "Recipients",
    target_persistent: "No target: it goes to everyone.",
    audience_now: "Right now: {names}",
    audience_nobody: "Right now: nobody",
    recipients_count: "{n} chosen",
    result: "Result",
    recipient: "Recipient",
    channel: "Channel",
    all_recipients: "everyone",
    nobody: "nobody",
    held_summary: "Held on every channel for the summary of {policy}.",
    held_until: "held until {when}",
    note_quiet: "quietly",
    via: "Fallback {policy}",
    summary: "Summary",
    policies_applied: "Policies that apply",
    none_applied: "No policy applies.",
    later: "Later steps",
    none_later: "No later step.",
    later_escalation: "Escalation {policy}: after {n} min unless someone acknowledges, also on {channels}.",
    later_reminder: "Reminder {policy}: every {n} min, at most {m} times{channels}.",
    later_away: "Away {policy}: people who are not home get it when they arrive{wait}.",
    later_fallback: "Fallback {policy}: if {when}, it is sent on {channels} instead.",
    later_summarize_every: "Summary {policy}: one summary {n} min after the first held message.",
    later_summarize_at: "Summary {policy}: one summary every day at {time}.",
    later_only: ", only on {channels}",
    later_wait: ", for at most {n} min",
    when_no_audience: "the audience is empty",
    when_failed: "delivery fails",
    when_both: "the audience is empty or delivery fails",
    yaml: "The call as YAML",
    copy: "Copy call",
    copied: "Copied.",
    copy_failed: "Copying is not possible here. Select the text.",
    send: "Send test",
    send_hint: "Sends one real message with the marker: the title starts with Test, the tag is test, and it ends after 10 minutes. Policies apply.",
    sent: "Sent {id}: {summary}",
    clear: "Clear the test message",
    cleared: "Cleared.",
    preview_failed: "The preview is not available: {text}",
    send_failed: "Sending failed: {text}",
    hub_off: "The hub is switched off. Switch it on in Settings to use this page.",
    valid: "The call is valid.",
    problems: { message_required: "Enter a message.", channels_required: "Choose at least one channel.", target_required: "{channel} needs a target.", target_exclusive: "{channel}: give either an audience or recipients." },
    tag_none: "No tag",
  },
  de: {
    title: "Testsenden",
    intro: "Probiere einen Aufruf aus, bevor du ihn in eine Automation übernimmst. Die Vorschau zeigt, was jetzt passieren würde, mit der echten Uhrzeit und der echten Anwesenheit. Gesendet wird erst, wenn du Test senden drückst.",
    content: "Inhalt",
    f_title: "Titel (optional)",
    f_message: "Meldung",
    f_tts: "Gesprochener Text (optional, nur Sprache)",
    call: "Der Aufruf",
    severity: "Schweregrad",
    tag: "Tag (optional)",
    channels: "Kanäle",
    policy: "Richtlinie",
    policy_all: "Alle, die gelten",
    policy_none: "Keine",
    who: "Wer, je Kanal",
    banner_hint: "Banner: ohne Ziel sehen es alle; wähle eine Zielgruppe oder Personen, um es einzuschränken. Eine Zielgruppe zählt die Personen, die sie beim Erstellen der Meldung hat.",
    target_channel: "Kanal {channel}",
    target_audience: "Zielgruppe",
    target_recipients: "Empfänger",
    target_persistent: "Kein Ziel: geht an alle.",
    audience_now: "Jetzt: {names}",
    audience_nobody: "Jetzt: niemand",
    recipients_count: "{n} gewählt",
    result: "Ergebnis",
    recipient: "Empfänger",
    channel: "Kanal",
    all_recipients: "alle",
    nobody: "niemand",
    held_summary: "Auf jedem Kanal für die Zusammenfassung von {policy} zurückgehalten.",
    held_until: "zurückgehalten bis {when}",
    note_quiet: "leise",
    via: "Ersatz {policy}",
    summary: "Zusammenfassung",
    policies_applied: "Richtlinien, die gelten",
    none_applied: "Keine Richtlinie gilt.",
    later: "Spätere Schritte",
    none_later: "Kein späterer Schritt.",
    later_escalation: "Eskalation {policy}: nach {n} Min., wenn niemand bestätigt, auch auf {channels}.",
    later_reminder: "Erinnerung {policy}: alle {n} Min., höchstens {m} Mal{channels}.",
    later_away: "Abwesend {policy}: wer nicht zu Hause ist, bekommt sie bei der Ankunft{wait}.",
    later_fallback: "Ersatz {policy}: wenn {when}, wird stattdessen auf {channels} gesendet.",
    later_summarize_every: "Zusammenfassung {policy}: eine Zusammenfassung {n} Min. nach der ersten zurückgehaltenen Meldung.",
    later_summarize_at: "Zusammenfassung {policy}: eine Zusammenfassung jeden Tag um {time}.",
    later_only: ", nur auf {channels}",
    later_wait: ", höchstens {n} Min.",
    when_no_audience: "die Zielgruppe leer ist",
    when_failed: "die Zustellung fehlschlägt",
    when_both: "die Zielgruppe leer ist oder die Zustellung fehlschlägt",
    yaml: "Der Aufruf als YAML",
    copy: "Aufruf kopieren",
    copied: "Kopiert.",
    copy_failed: "Kopieren ist hier nicht möglich. Markiere den Text.",
    send: "Test senden",
    send_hint: "Sendet eine echte Meldung mit der Markierung: Der Titel beginnt mit Test, der Tag ist test, und sie endet nach 10 Minuten. Richtlinien gelten.",
    sent: "Gesendet {id}: {summary}",
    clear: "Testmeldung entfernen",
    cleared: "Entfernt.",
    preview_failed: "Die Vorschau ist nicht verfügbar: {text}",
    send_failed: "Senden fehlgeschlagen: {text}",
    hub_off: "Der Hub ist ausgeschaltet. Schalte ihn in den Einstellungen ein, um diese Seite zu nutzen.",
    valid: "Der Aufruf ist gültig.",
    problems: { message_required: "Gib eine Meldung ein.", channels_required: "Wähle mindestens einen Kanal.", target_required: "{channel} braucht ein Ziel.", target_exclusive: "{channel}: gib entweder eine Zielgruppe oder Empfänger an." },
    tag_none: "Kein Tag",
  },
  fr: {
    title: "Envoi de test",
    intro: "Essayez un appel avant de le mettre dans une automatisation. L'aperçu montre ce qui se passerait maintenant, avec l'heure réelle et la présence réelle. Rien n'est envoyé avant d'appuyer sur Envoyer le test.",
    content: "Contenu",
    f_title: "Titre (facultatif)",
    f_message: "Message",
    f_tts: "Texte parlé (facultatif, voix seulement)",
    call: "L'appel",
    severity: "Gravité",
    tag: "Étiquette (facultatif)",
    channels: "Canaux",
    policy: "Politique",
    policy_all: "Toutes celles qui s'appliquent",
    policy_none: "Aucune",
    who: "Qui, par canal",
    banner_hint: "Bannière : sans cible, tout le monde la voit ; choisissez une audience ou des personnes pour la limiter. Une audience compte les personnes qu'elle a à la création du message.",
    target_channel: "Canal {channel}",
    target_audience: "Audience",
    target_recipients: "Destinataires",
    target_persistent: "Pas de cible : va à tout le monde.",
    audience_now: "En ce moment : {names}",
    audience_nobody: "En ce moment : personne",
    recipients_count: "{n} choisis",
    result: "Résultat",
    recipient: "Destinataire",
    channel: "Canal",
    all_recipients: "tout le monde",
    nobody: "personne",
    held_summary: "Retenu sur chaque canal pour le résumé de {policy}.",
    held_until: "retenu jusqu'à {when}",
    note_quiet: "discrètement",
    via: "Repli {policy}",
    summary: "Résumé",
    policies_applied: "Politiques qui s'appliquent",
    none_applied: "Aucune politique ne s'applique.",
    later: "Étapes suivantes",
    none_later: "Aucune étape suivante.",
    later_escalation: "Escalade {policy} : après {n} min si personne ne confirme, aussi sur {channels}.",
    later_reminder: "Rappel {policy} : toutes les {n} min, au plus {m} fois{channels}.",
    later_away: "Absent {policy} : les personnes qui ne sont pas à la maison le reçoivent à leur arrivée{wait}.",
    later_fallback: "Repli {policy} : si {when}, il est envoyé sur {channels} à la place.",
    later_summarize_every: "Résumé {policy} : un résumé {n} min après le premier message retenu.",
    later_summarize_at: "Résumé {policy} : un résumé chaque jour à {time}.",
    later_only: ", seulement sur {channels}",
    later_wait: ", au plus {n} min",
    when_no_audience: "l'audience est vide",
    when_failed: "la livraison échoue",
    when_both: "l'audience est vide ou la livraison échoue",
    yaml: "L'appel en YAML",
    copy: "Copier l'appel",
    copied: "Copié.",
    copy_failed: "La copie n'est pas possible ici. Sélectionnez le texte.",
    send: "Envoyer le test",
    send_hint: "Envoie un vrai message avec le marqueur : le titre commence par Test, l'étiquette est test, et il se termine après 10 minutes. Les politiques s'appliquent.",
    sent: "Envoyé {id} : {summary}",
    clear: "Supprimer le message de test",
    cleared: "Supprimé.",
    preview_failed: "L'aperçu n'est pas disponible : {text}",
    send_failed: "Échec de l'envoi : {text}",
    hub_off: "Le hub est désactivé. Activez-le dans Réglages pour utiliser cette page.",
    valid: "L'appel est valide.",
    problems: { message_required: "Saisissez un message.", channels_required: "Choisissez au moins un canal.", target_required: "{channel} a besoin d'une cible.", target_exclusive: "{channel} : indiquez soit une audience soit des destinataires." },
    tag_none: "Aucune étiquette",
  },
  es: {
    title: "Envío de prueba",
    intro: "Prueba una llamada antes de ponerla en una automatización. La vista previa muestra lo que pasaría ahora, con la hora real y la presencia real. No se envía nada hasta que pulses Enviar prueba.",
    content: "Contenido",
    f_title: "Título (opcional)",
    f_message: "Mensaje",
    f_tts: "Texto hablado (opcional, solo voz)",
    call: "La llamada",
    severity: "Gravedad",
    tag: "Etiqueta (opcional)",
    channels: "Canales",
    policy: "Política",
    policy_all: "Todas las que se apliquen",
    policy_none: "Ninguna",
    who: "Quién, por canal",
    banner_hint: "Aviso: sin destino lo ve todo el mundo; elige una audiencia o personas para limitarlo. Una audiencia cuenta las personas que tiene al crear el mensaje.",
    target_channel: "Canal {channel}",
    target_audience: "Audiencia",
    target_recipients: "Destinatarios",
    target_persistent: "Sin destino: va a todos.",
    audience_now: "Ahora: {names}",
    audience_nobody: "Ahora: nadie",
    recipients_count: "{n} elegidos",
    result: "Resultado",
    recipient: "Destinatario",
    channel: "Canal",
    all_recipients: "todos",
    nobody: "nadie",
    held_summary: "Retenido en cada canal para el resumen de {policy}.",
    held_until: "retenido hasta {when}",
    note_quiet: "en silencio",
    via: "Alternativa {policy}",
    summary: "Resumen",
    policies_applied: "Políticas que se aplican",
    none_applied: "No se aplica ninguna política.",
    later: "Pasos posteriores",
    none_later: "Ningún paso posterior.",
    later_escalation: "Escalado {policy}: tras {n} min si nadie confirma, también por {channels}.",
    later_reminder: "Recordatorio {policy}: cada {n} min, como máximo {m} veces{channels}.",
    later_away: "Ausente {policy}: quien no está en casa lo recibe al llegar{wait}.",
    later_fallback: "Alternativa {policy}: si {when}, se envía por {channels} en su lugar.",
    later_summarize_every: "Resumen {policy}: un resumen {n} min después del primer mensaje retenido.",
    later_summarize_at: "Resumen {policy}: un resumen cada día a las {time}.",
    later_only: ", solo por {channels}",
    later_wait: ", como máximo {n} min",
    when_no_audience: "la audiencia está vacía",
    when_failed: "la entrega falla",
    when_both: "la audiencia está vacía o la entrega falla",
    yaml: "La llamada en YAML",
    copy: "Copiar llamada",
    copied: "Copiado.",
    copy_failed: "No se puede copiar aquí. Selecciona el texto.",
    send: "Enviar prueba",
    send_hint: "Envía un mensaje real con la marca: el título empieza por Test, la etiqueta es test y termina a los 10 minutos. Se aplican las políticas.",
    sent: "Enviado {id}: {summary}",
    clear: "Borrar el mensaje de prueba",
    cleared: "Borrado.",
    preview_failed: "La vista previa no está disponible: {text}",
    send_failed: "Falló el envío: {text}",
    hub_off: "El hub está desactivado. Actívalo en Ajustes para usar esta página.",
    valid: "La llamada es válida.",
    problems: { message_required: "Introduce un mensaje.", channels_required: "Elige al menos un canal.", target_required: "{channel} necesita un destino.", target_exclusive: "{channel}: indica una audiencia o destinatarios." },
    tag_none: "Sin etiqueta",
  },
};

const SEVERITIES = ["success", "info", "warning", "critical"];
const CHANNELS = ["banner", "push", "popup", "speak", "persistent", "mail"];
const NEEDS_TARGET = ["push", "popup", "speak", "mail"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues() {
  return { title: "", message: "", tts_message: "", severity: "warning", tag: "", channels: ["banner"], policy: "" };
}

// The `notify` call the values describe: only what is set, targets only for the chosen channels.
export function buildCall(values) {
  const data = { message: String(values.message).trim(), severity: values.severity, channels: [...values.channels] };
  if (String(values.title).trim()) data.title = String(values.title).trim();
  if (values.channels.includes("speak") && String(values.tts_message).trim()) data.tts_message = String(values.tts_message).trim();
  if (String(values.tag).trim()) data.tag = String(values.tag).trim();
  if (values.policy) data.policy = values.policy;
  const to = {};
  for (const channel of values.channels) {
    if (channel === "persistent") continue;
    const audience = values[`${channel}_audience`];
    const recipients = values[`${channel}_recipients`] || [];
    if (audience && channel !== "speak") to[channel] = { audience };
    else if (recipients.length) to[channel] = { recipients: [...recipients] };
  }
  if (Object.keys(to).length) data.to = to;
  return data;
}

// Problems as a list of { code, channel? }; empty means the call is valid.
export function validate(values) {
  const found = [];
  if (!String(values.message).trim()) found.push({ code: "message_required" });
  if (values.channels.length === 0) found.push({ code: "channels_required" });
  for (const channel of values.channels.filter((c) => NEEDS_TARGET.includes(c))) {
    const audience = values[`${channel}_audience`];
    const recipients = values[`${channel}_recipients`] || [];
    if (!audience && recipients.length === 0) found.push({ code: "target_required", channel });
    else if (audience && recipients.length > 0) found.push({ code: "target_exclusive", channel });
  }
  const banner = values.banner_audience && (values.banner_recipients || []).length > 0;
  if (values.channels.includes("banner") && banner) found.push({ code: "target_exclusive", channel: "banner" });
  return found;
}

export function callYaml(values, toYaml) {
  return toYaml({ action: "heads_up.notify", data: buildCall(values) });
}

// "push: 2 sent, 1 skipped" for each channel, in the order the channels appear.
export function summaryLine(rows, s) {
  const order = [];
  const counts = {};
  for (const row of rows) {
    if (row.via || !row.channel) continue;
    if (!counts[row.channel]) {
      counts[row.channel] = {};
      order.push(row.channel);
    }
    counts[row.channel][row.result] = (counts[row.channel][row.result] || 0) + 1;
  }
  return order
    .map((channel) => {
      const parts = ["sent", "held", "skipped", "failed"].filter((k) => counts[channel][k]).map((k) => `${counts[channel][k]} ${s.result[k] || k}`);
      return `${s.channel[channel] || channel}: ${parts.join(", ")}`;
    })
    .join("; ");
}

export function laterText(step, t, s) {
  const channels = (step.channels || []).map((c) => s.channel[c] || c).join(", ");
  const only = channels ? fill(t.later_only, { channels }) : "";
  switch (step.type) {
    case "escalation":
      return fill(t.later_escalation, { policy: step.policy, n: step.after_minutes, channels });
    case "reminder":
      return fill(t.later_reminder, { policy: step.policy, n: step.every_minutes, m: step.max_count, channels: only });
    case "away":
      return fill(t.later_away, { policy: step.policy, wait: step.max_wait > 0 ? fill(t.later_wait, { n: step.max_wait }) : "" });
    case "fallback":
      return fill(t.later_fallback, { policy: step.policy, when: t[`when_${step.when}`], channels });
    default:
      return step.summary_at
        ? fill(t.later_summarize_at, { policy: step.policy, time: String(step.summary_at).slice(0, 5) })
        : fill(t.later_summarize_every, { policy: step.policy, n: step.summary_every });
  }
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

// Who a result row is for: the person (with the device on push), the people a banner is limited to,
// or everyone.
export function rowRecipient(row, result, choices, t) {
  const personName = (id) => choices.persons.find((p) => p.id === id)?.name ?? id;
  if (row.recipient.startsWith("device:")) {
    const device = choices.registrations.find((r) => `device:${r.id}` === row.recipient)?.name;
    const who = row.person ? personName(row.person) : "";
    return [who, device].filter(Boolean).join(" · ") || row.recipient;
  }
  if (row.recipient) return row.person ? personName(row.person) : (choices.persons.find((p) => p.id === row.recipient)?.name ?? row.recipient);
  if (row.channel === "banner") {
    if (row.result === "skipped") return t.nobody;
    const people = result.banner_people || [];
    return people.length ? people.map(personName).join(", ") : t.all_recipients;
  }
  return t.all_recipients;
}

export function mount(container, ctx) {
  const { t, s, ui, fmt } = ctx;
  let hass = ctx.hass;
  let data = null; // panel_config
  const values = blankValues();
  let result = null; // the preview
  let notice = "";
  let timer = null;
  let testId = null;
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const channelLabel = (c) => s.channel[c] || c;

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    if (!data.hub) {
      root.append(el("div", { className: "hint", textContent: t.hub_off }));
      return;
    }
    root.append(el("div", { className: "hint", textContent: t.intro }));
    const change = () => schedule();

    const content = el("section", {}, [el("h2", { textContent: t.content })]);
    content.append(ui.field(t.f_title, ui.textInput(values.title, (v) => { values.title = v; change(); })));
    content.append(ui.field(t.f_message, ui.textInput(values.message, (v) => { values.message = v; change(); }, { style: "max-width:100%" })));
    if (values.channels.includes("speak")) content.append(ui.field(t.f_tts, ui.textInput(values.tts_message, (v) => { values.tts_message = v; change(); }, { style: "max-width:100%" })));

    const callBox = el("section", {}, [el("h2", { textContent: t.call })]);
    callBox.append(ui.field(t.severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: s.severity[k] })), values.severity, (v) => { values.severity = v; change(); })));
    callBox.append(ui.field(t.tag, ui.textInput(values.tag, (v) => { values.tag = v; change(); }), t.tag_none));
    callBox.append(ui.chips(t.channels, CHANNELS.map((c) => ({ value: c, label: channelLabel(c) })), values.channels, (list) => { values.channels = list; render(); schedule(); }));
    const policies = [{ value: "", label: t.policy_all }, { value: "none", label: t.policy_none }, ...data.policies.map((p) => ({ value: p.name, label: p.name }))];
    callBox.append(ui.field(t.policy, ui.selectInput(policies, values.policy, (v) => { values.policy = v; change(); })));

    const who = el("section", {}, [el("h2", { textContent: t.who })]);
    const labels = { audience: t.target_audience, recipients: t.target_recipients, persistent: t.target_persistent };
    for (const channel of values.channels) {
      who.append(ui.targetBlock(channel, values, data.choices, { ...labels, channel: fill(t.target_channel, { channel: channelLabel(channel) }) }, (mode) => { if (mode) render(); schedule(); }));
      const audience = data.audiences.find((a) => a.name === values[`${channel}_audience`]);
      if (audience) {
        const names = audience.members.map((m) => data.choices.persons.find((p) => p.id === m)?.name ?? m);
        who.append(el("div", { className: "hint", textContent: names.length ? fill(t.audience_now, { names: names.join(", ") }) : t.audience_nobody }));
      }
      if (channel === "banner") who.append(el("div", { className: "hint", textContent: t.banner_hint }));
    }
    root.append(content, callBox, who, resultNode(), yamlNode());
  }

  function resultNode() {
    const box = el("section", {}, [el("h2", { textContent: t.result })]);
    const problems = validate(values);
    if (problems.length) {
      box.append(el("div", { className: "hint problems", textContent: problems.map((p) => fill(t.problems[p.code], { channel: p.channel ? channelLabel(p.channel) : "" })).join(" ") }));
      return box;
    }
    if (!result) {
      box.append(el("div", { className: "hint", textContent: "…" }));
      return box;
    }
    if (result.error) {
      box.append(el("div", { className: "hint problems", textContent: fill(t.preview_failed, { text: result.error }) }));
      return box;
    }
    if (result.held_for_summary) box.append(el("div", { className: "hint", textContent: fill(t.held_summary, { policy: result.held_for_summary }) }));
    const head = el("tr", {}, [t.recipient, t.channel, t.result].map((text) => el("th", { textContent: text })));
    const now = Date.now();
    const rows = result.rows.map((row) => {
      const recipient = rowRecipient(row, result, data.choices, t);
      const via = row.via ? `${fill(t.via, { policy: row.via })} · ` : "";
      const words = [s.result[row.result] || row.result];
      if (row.result === "held" && row.until) words[0] = fill(t.held_until, { when: fmt.inTime(row.until, now, s) });
      if (row.reason && row.reason !== "summarize") words.push(fmt.reasonText(row.reason, s));
      if (row.note === "quiet") words.push(t.note_quiet);
      return el("tr", {}, [el("td", { textContent: via + recipient }), el("td", { textContent: row.channel ? channelLabel(row.channel) : "" }), el("td", { textContent: words.filter(Boolean).join(" · ") })]);
    });
    box.append(el("table", {}, [el("thead", {}, [head]), el("tbody", {}, rows)]));
    box.append(el("h2", { textContent: t.summary, style: "margin-top:12px" }), el("div", { textContent: summaryLine(result.rows, s) }));
    box.append(el("h2", { textContent: t.policies_applied, style: "margin-top:12px" }));
    box.append(el("div", { textContent: result.policies.length ? result.policies.map((p) => p.name).join(", ") : t.none_applied }));
    box.append(el("h2", { textContent: t.later, style: "margin-top:12px" }));
    box.append(result.later.length ? el("ul", {}, result.later.map((step) => el("li", { textContent: laterText(step, t, s) }))) : el("div", { textContent: t.none_later }));
    return box;
  }

  function yamlNode() {
    const box = el("section", {}, [el("h2", { textContent: t.yaml })]);
    const valid = validate(values).length === 0;
    box.append(el("pre", { textContent: callYaml(values, ui.toYaml) }));
    const copy = el("button", { type: "button", textContent: t.copy });
    const status = el("span", { className: "hint", style: "margin-left:8px" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    copy.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(callYaml(values, ui.toYaml));
        status.textContent = t.copied;
      } catch (err) {
        status.textContent = t.copy_failed;
      }
    });
    const send = el("button", { type: "button", className: "primary", textContent: t.send, disabled: !valid || !result || Boolean(result.error) });
    send.addEventListener("click", sendTest);
    const row = el("div", { className: "row" }, [copy, send, status]);
    box.append(row, el("div", { className: "hint", textContent: t.send_hint }));
    if (notice) box.append(el("div", { className: "hint", textContent: notice }));
    if (testId) {
      const clear = el("button", { type: "button", textContent: t.clear });
      clear.addEventListener("click", clearTest);
      box.append(clear);
    }
    return box;
  }

  function schedule() {
    clearTimeout(timer);
    result = null;
    notice = "";
    timer = setTimeout(runPreview, 400);
    // The call and the result are redrawn as the preview arrives; the form stays as it is.
    repaintResult();
  }

  function repaintResult() {
    const boxes = [...root.querySelectorAll("section")];
    if (boxes.length < 5) return;
    boxes[3].replaceWith(resultNode());
    boxes[4].replaceWith(yamlNode());
  }

  async function runPreview() {
    if (validate(values).length) {
      repaintResult();
      return;
    }
    try {
      result = await hass.callWS({ type: "heads_up/hub_plan", ...buildCall(values) });
    } catch (err) {
      result = { error: err?.message || String(err?.code || "error") };
    }
    repaintResult();
  }

  async function sendTest() {
    try {
      const response = await hass.callWS({ type: "heads_up/hub_test_send", ...buildCall(values) });
      testId = response.id;
      const counts = Object.entries(response.channels || {}).map(([c, v]) => `${channelLabel(c)}: ${v.sent} ${s.result.sent}`).join("; ");
      notice = fill(t.sent, { id: response.id, summary: counts });
    } catch (err) {
      notice = fill(t.send_failed, { text: err?.message || "" });
    }
    repaintResult();
  }

  async function clearTest() {
    try {
      await hass.callWS({ type: "heads_up/admin_clear", banner_id: testId });
      notice = t.cleared;
      testId = null;
    } catch (err) {
      notice = fill(t.send_failed, { text: err?.message || "" });
    }
    repaintResult();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    render();
    runPreview();
  }

  root.append(el("div", { textContent: "…" }));
  load().catch(() => root.replaceChildren(el("div", { textContent: "…" })));
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      clearTimeout(timer);
      root.remove();
    },
  };
}
