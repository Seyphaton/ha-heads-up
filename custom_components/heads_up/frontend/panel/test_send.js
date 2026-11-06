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
    policy: "Manual policy",
    disable_automatic: "Disable automatic policies",
    disable_automatic_hint: "Disables all automatically assigned policies (for example by severity or tag). Manually assigned policies still apply.",
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
    what_happened: "What happened",
    outcome_waiting: "Waiting for the delivery…",
    outcome_none: "No delivery was recorded yet. Open Message Log for the trace.",
    log_hint: "A failed delivery is also written to the Home Assistant log (Settings > System > Logs, search for heads_up).",
    clear: "Clear the test message",
    cleared: "Cleared.",
    preview_failed: "The preview is not available: {text}",
    send_failed: "Sending failed: {text}",
    valid: "The call is valid.",
    problems: { message_required: "Enter a message.", channels_required: "Choose at least one channel.", target_required: "{channel} needs a target.", target_exclusive: "{channel}: give either an audience or recipients." },
    tag_hint: "A label for the message, for example water or laundry. Policies can apply to chosen tags, a card can show only banners with one tag, and clearing can remove every message with a tag. Leave it empty for none. This tag decides which policies the preview applies; the test message itself always gets the tag test.",
    behaviour_none: "Nothing here applies: mail and speech cannot be taken back, dismissed or snoozed.",
    behaviour_some: "Mail and speech ignore these choices; the other channels use them.",
    behaviour: "Behaviour",
    dismiss_label: "Who can dismiss it",
    snooze_label: "Who can snooze it",
    who_default: "Use the default from Settings",
    who_off: "Nobody",
    who_user: "Each person for themselves",
    who_everyone: "Anyone, for everyone",
    behaviour_hint: "These choices apply to the real send. The result table does not change with them.",
    pinned_hint: "Nobody can close it. It ends by its timeout, its condition or a clear action; the test message still ends after 10 minutes.",
    ack_title: "Acknowledgement",
    ack_yes: "Someone has to acknowledge it: {policies} escalate or repeat the message until then. Pushes get an Acknowledge button and the card shows one.",
    ack_no: "Nothing waits for an acknowledgement, because no escalation or reminder policy applies. Acknowledging is not a setting of the call: add an Escalation or Reminder policy for this severity and tag, or choose one under Policy.",
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
    policy: "Manuelle Richtlinie",
    disable_automatic: "Automatische Richtlinien deaktivieren",
    disable_automatic_hint: "Deaktiviert alle automatisch zugewiesenen Richtlinien (zum Beispiel nach Schweregrad oder Tag). Manuell zugewiesene Richtlinien gelten weiterhin.",
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
    what_happened: "Was passiert ist",
    outcome_waiting: "Warte auf die Zustellung…",
    outcome_none: "Noch keine Zustellung aufgezeichnet. Öffne das Meldungsprotokoll für den Ablauf.",
    log_hint: "Eine fehlgeschlagene Zustellung steht auch im Home-Assistant-Protokoll (Einstellungen > System > Protokolle, nach heads_up suchen).",
    clear: "Testmeldung entfernen",
    cleared: "Entfernt.",
    preview_failed: "Die Vorschau ist nicht verfügbar: {text}",
    send_failed: "Senden fehlgeschlagen: {text}",
    valid: "Der Aufruf ist gültig.",
    problems: { message_required: "Gib eine Meldung ein.", channels_required: "Wähle mindestens einen Kanal.", target_required: "{channel} braucht ein Ziel.", target_exclusive: "{channel}: gib entweder eine Zielgruppe oder Empfänger an." },
    tag_hint: "Ein Etikett für die Meldung, zum Beispiel water oder laundry. Richtlinien können für bestimmte Tags gelten, eine Karte kann nur Banner mit einem Tag zeigen, und beim Entfernen lassen sich alle Meldungen mit einem Tag entfernen. Leer lassen für keins. Dieser Tag bestimmt, welche Richtlinien die Vorschau anwendet; die Testmeldung selbst bekommt immer den Tag test.",
    behaviour_none: "Hier gilt nichts: E-Mail und Sprache lassen sich nicht zurücknehmen, ausblenden oder zurückstellen.",
    behaviour_some: "E-Mail und Sprache ignorieren diese Auswahl; die anderen Kanäle nutzen sie.",
    behaviour: "Verhalten",
    dismiss_label: "Wer es ausblenden darf",
    snooze_label: "Wer es zurückstellen darf",
    who_default: "Standard aus den Einstellungen",
    who_off: "Niemand",
    who_user: "Jeder für sich",
    who_everyone: "Jeder, für alle",
    behaviour_hint: "Diese Auswahl gilt für das echte Senden. Die Ergebnistabelle ändert sich dadurch nicht.",
    pinned_hint: "Niemand kann sie schließen. Sie endet durch ihr Zeitlimit, ihre Bedingung oder eine Löschaktion; die Testmeldung endet trotzdem nach 10 Minuten.",
    ack_title: "Bestätigung",
    ack_yes: "Jemand muss sie bestätigen: {policies} eskalieren oder wiederholen die Meldung bis dahin. Pushes bekommen die Schaltfläche Bestätigen, die Karte zeigt sie auch.",
    ack_no: "Nichts wartet auf eine Bestätigung, weil keine Eskalations- oder Erinnerungsrichtlinie gilt. Bestätigen ist keine Einstellung des Aufrufs: Lege eine Eskalations- oder Erinnerungsrichtlinie für diesen Schweregrad und Tag an oder wähle unter Richtlinie eine.",
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
    policy: "Politique manuelle",
    disable_automatic: "Désactiver les politiques automatiques",
    disable_automatic_hint: "Désactive toutes les politiques attribuées automatiquement (par exemple par gravité ou étiquette). Les politiques attribuées à la main s'appliquent toujours.",
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
    what_happened: "Ce qui s'est passé",
    outcome_waiting: "En attente de la livraison…",
    outcome_none: "Aucune livraison enregistrée pour l'instant. Ouvrez le journal des messages pour la trace.",
    log_hint: "Une livraison échouée est aussi écrite dans le journal de Home Assistant (Réglages > Système > Journaux, cherchez heads_up).",
    clear: "Supprimer le message de test",
    cleared: "Supprimé.",
    preview_failed: "L'aperçu n'est pas disponible : {text}",
    send_failed: "Échec de l'envoi : {text}",
    valid: "L'appel est valide.",
    problems: { message_required: "Saisissez un message.", channels_required: "Choisissez au moins un canal.", target_required: "{channel} a besoin d'une cible.", target_exclusive: "{channel} : indiquez soit une audience soit des destinataires." },
    tag_hint: "Un libellé pour le message, par exemple water ou laundry. Des politiques peuvent s'appliquer à certaines étiquettes, une carte peut n'afficher que les bannières d'une étiquette, et la suppression peut retirer tous les messages d'une étiquette. Laissez vide pour aucune. Cette étiquette décide des politiques que l'aperçu applique ; le message de test reçoit toujours l'étiquette test.",
    behaviour_none: "Rien ne s'applique ici : un courriel et la voix ne peuvent pas être repris, masqués ni reportés.",
    behaviour_some: "Le courriel et la voix ignorent ces choix ; les autres canaux les utilisent.",
    behaviour: "Comportement",
    dismiss_label: "Qui peut le masquer",
    snooze_label: "Qui peut le reporter",
    who_default: "Valeur par défaut des réglages",
    who_off: "Personne",
    who_user: "Chacun pour soi",
    who_everyone: "N'importe qui, pour tout le monde",
    behaviour_hint: "Ces choix valent pour l'envoi réel. Le tableau de résultat ne change pas avec eux.",
    pinned_hint: "Personne ne peut le fermer. Il se termine par son délai, sa condition ou une action d'effacement ; le message de test se termine quand même après 10 minutes.",
    ack_title: "Confirmation",
    ack_yes: "Quelqu'un doit le confirmer : {policies} escaladent ou répètent le message jusque-là. Les push reçoivent un bouton Confirmer et la carte en montre un.",
    ack_no: "Rien n'attend une confirmation, car aucune politique d'escalade ou de rappel ne s'applique. Confirmer n'est pas un réglage de l'appel : ajoutez une politique d'escalade ou de rappel pour cette gravité et cette étiquette, ou choisissez-en une sous Politique.",
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
    policy: "Política manual",
    disable_automatic: "Desactivar políticas automáticas",
    disable_automatic_hint: "Desactiva todas las políticas asignadas automáticamente (por ejemplo por gravedad o etiqueta). Las políticas asignadas a mano siguen aplicándose.",
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
    what_happened: "Qué pasó",
    outcome_waiting: "Esperando la entrega…",
    outcome_none: "Aún no se registró ninguna entrega. Abre el registro de mensajes para ver la traza.",
    log_hint: "Una entrega fallida también se escribe en el registro de Home Assistant (Ajustes > Sistema > Registros, busca heads_up).",
    clear: "Borrar el mensaje de prueba",
    cleared: "Borrado.",
    preview_failed: "La vista previa no está disponible: {text}",
    send_failed: "Falló el envío: {text}",
    valid: "La llamada es válida.",
    problems: { message_required: "Introduce un mensaje.", channels_required: "Elige al menos un canal.", target_required: "{channel} necesita un destino.", target_exclusive: "{channel}: indica una audiencia o destinatarios." },
    tag_hint: "Un rótulo para el mensaje, por ejemplo water o laundry. Las políticas pueden aplicarse a ciertas etiquetas, una tarjeta puede mostrar solo avisos con una etiqueta, y al borrar se pueden quitar todos los mensajes con una etiqueta. Déjalo vacío para ninguna. Esta etiqueta decide qué políticas aplica la vista previa; el mensaje de prueba siempre recibe la etiqueta test.",
    behaviour_none: "Aquí no se aplica nada: el correo y la voz no se pueden retirar, descartar ni posponer.",
    behaviour_some: "El correo y la voz ignoran estas opciones; los demás canales las usan.",
    behaviour: "Comportamiento",
    dismiss_label: "Quién puede descartarlo",
    snooze_label: "Quién puede posponerlo",
    who_default: "Valor por defecto de los ajustes",
    who_off: "Nadie",
    who_user: "Cada persona por sí misma",
    who_everyone: "Cualquiera, para todos",
    behaviour_hint: "Estas opciones valen para el envío real. La tabla de resultados no cambia con ellas.",
    pinned_hint: "Nadie puede cerrarlo. Termina por su tiempo límite, su condición o una acción de borrado; el mensaje de prueba termina igualmente a los 10 minutos.",
    ack_title: "Confirmación",
    ack_yes: "Alguien tiene que confirmarlo: {policies} escalan o repiten el mensaje hasta entonces. Los push reciben un botón Confirmar y la tarjeta muestra uno.",
    ack_no: "Nada espera una confirmación, porque no se aplica ninguna política de escalado ni de recordatorio. Confirmar no es un ajuste de la llamada: añade una política de escalado o de recordatorio para esta gravedad y etiqueta, o elige una en Política.",
  },
};

const SEVERITIES = ["success", "info", "warning", "critical"];
const CHANNELS = ["banner", "push", "popup", "speak", "persistent", "mail"];
const NEEDS_TARGET = ["push", "popup", "speak", "mail"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues() {
  return { title: "", message: "", tts_message: "", severity: "warning", tag: "", channels: ["banner"], policy: [], disable_automatic: false, dismiss: "", snooze: "" };
}

// The `notify` call the values describe: only what is set, targets only for the chosen channels.
export function buildCall(values) {
  const data = { message: String(values.message).trim(), severity: values.severity, channels: [...values.channels] };
  if (String(values.title).trim()) data.title = String(values.title).trim();
  if (values.channels.includes("speak") && String(values.tts_message).trim()) data.tts_message = String(values.tts_message).trim();
  if (String(values.tag).trim()) data.tag = String(values.tag).trim();
  // The default (automatic policies apply) is left out of the YAML; one manual policy is a string.
  if (values.disable_automatic) data.disable_automatic_policies = true;
  const policy = values.policy || [];
  if (policy.length) data.policy = policy.length === 1 ? policy[0] : [...policy];
  // Only what differs from the defaults, so the YAML stays short; snoozing means nothing for a
  // message nobody can dismiss.
  if (values.dismiss) data.dismiss = values.dismiss;
  if (values.snooze && values.dismiss !== "off") data.snooze = values.snooze;
  const targets = {};
  for (const channel of values.channels) {
    if (channel === "persistent") continue;
    const audience = values[`${channel}_audience`];
    const recipients = values[`${channel}_recipients`] || [];
    if (audience && channel !== "speak") targets[channel] = { audience };
    else if (recipients.length) targets[channel] = { recipients: [...recipients] };
  }
  // The same people on every channel that takes people become one `audience` or `recipients`
  // field; speech has its own `speakers`. A banner without a target is open to everyone, so it
  // blocks the short form when the others have one.
  const people = values.channels.filter((c) => c !== "speak" && c !== "persistent");
  const first = targets[people[0]];
  const shared = first && people.every((c) => JSON.stringify(targets[c]) === JSON.stringify(first));
  if (shared) {
    Object.assign(data, first);
    if (targets.speak) data.speakers = targets.speak.recipients;
  } else {
    if (Object.keys(targets).length) data.to = targets;
  }
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

// Whether anything waits for an acknowledgement, in words. Acknowledging has no field of its own:
// it matters when an escalation or a reminder applies.
export function ackText(policies, t) {
  return policies?.length ? fill(t.ack_yes, { policies: policies.join(", ") }) : t.ack_no;
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

// The trace entries that are real delivery results of a message, banner included, without
// housekeeping such as a clear.
export function outcomeRows(entries, channels) {
  return (entries || []).filter((e) => channels.includes(e.channel) && ["sent", "failed", "skipped", "held"].includes(e.result));
}

// True once every channel the call named has a result.
export function outcomeDone(entries, channels) {
  const rows = outcomeRows(entries, channels);
  return channels.every((c) => rows.some((r) => r.channel === c));
}

// "Speak: 1 sent, 1 skipped" from the counts of the `notify` response, in the order the call named.
export function plannedLine(counts, s) {
  return Object.entries(counts || {})
    .map(([channel, c]) => {
      const parts = ["sent", "held", "skipped", "failed"].filter((k) => c[k]).map((k) => `${c[k]} ${s.result[k] || k}`);
      return `${s.channel[channel] || channel}: ${parts.join(", ") || "0"}`;
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

// Mail and speech cannot be taken back, dismissed or snoozed: "behaviour_none" when the call has
// nothing else, "behaviour_some" when other channels still use the choices, otherwise null.
export function behaviourUnused(channels) {
  const quiet = (channels || []).filter((c) => c === "mail" || c === "speak");
  if (quiet.length === 0) return null;
  return quiet.length === (channels || []).length ? "behaviour_none" : "behaviour_some";
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
  if (row.recipient === "mail:global") return "Global address"; // the name a call uses for it
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
  let outcome = null; // the trace rows of the real send, filled in when they arrive
  let waiting = false;
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const channelLabel = (c) => s.channel[c] || c;

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    const change = () => schedule();

    const content = el("section", {}, [el("h2", { textContent: t.content })]);
    content.append(ui.field(t.f_title, ui.textInput(values.title, (v) => { values.title = v; change(); })));
    content.append(ui.field(t.f_message, ui.textInput(values.message, (v) => { values.message = v; change(); }, { style: "max-width:100%" })));
    if (values.channels.includes("speak")) content.append(ui.field(t.f_tts, ui.textInput(values.tts_message, (v) => { values.tts_message = v; change(); }, { style: "max-width:100%" })));

    const callBox = el("section", {}, [el("h2", { textContent: t.call })]);
    callBox.append(ui.field(t.severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: s.severity[k] })), values.severity, (v) => { values.severity = v; change(); })));
    callBox.append(ui.field(t.tag, ui.textInput(values.tag, (v) => { values.tag = v; change(); }), t.tag_hint));
    callBox.append(ui.chips(t.channels, CHANNELS.map((c) => ({ value: c, label: channelLabel(c) })), values.channels, (list) => { values.channels = list; render(); schedule(); }));
    callBox.append(ui.checkbox(t.disable_automatic, values.disable_automatic, (on) => { values.disable_automatic = on; change(); }));
    callBox.append(el("div", { className: "hint", textContent: t.disable_automatic_hint }));
    callBox.append(ui.chips(t.policy, data.policies.map((p) => ({ value: p.name, label: p.name })), values.policy, (list) => { values.policy = list; change(); }));

    const behaviour = el("section", {}, [el("h2", { textContent: t.behaviour })]);
    const whoCan = [{ value: "", label: t.who_default }, { value: "off", label: t.who_off }, { value: "user", label: t.who_user }, { value: "everyone", label: t.who_everyone }];
    behaviour.append(ui.field(t.dismiss_label, ui.selectInput(whoCan, values.dismiss, (v) => { values.dismiss = v; render(); schedule(); })));
    if (values.dismiss !== "off") {
      behaviour.append(ui.field(t.snooze_label, ui.selectInput(whoCan, values.snooze, (v) => { values.snooze = v; change(); })));
    } else {
      behaviour.append(el("div", { className: "hint", textContent: t.pinned_hint }));
    }
    behaviour.append(el("div", { className: "hint", textContent: t.behaviour_hint }));
    const unused = behaviourUnused(values.channels);
    if (unused) behaviour.append(el("div", { className: "hint", textContent: t[unused] }));

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
    root.append(content, callBox, behaviour, who, resultNode(), yamlNode());
  }

  function resultNode() {
    const box = el("section", { className: "hu-result" }, [el("h2", { textContent: t.result })]);
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
      const to = row.address ? `${recipient} (${row.address})` : recipient;
      return el("tr", {}, [el("td", { textContent: via + to }), el("td", { textContent: row.channel ? channelLabel(row.channel) : "" }), el("td", { textContent: words.filter(Boolean).join(" · ") })]);
    });
    box.append(el("table", {}, [el("thead", {}, [head]), el("tbody", {}, rows)]));
    box.append(el("h2", { textContent: t.summary, style: "margin-top:12px" }), el("div", { textContent: summaryLine(result.rows, s) }));
    box.append(el("h2", { textContent: t.policies_applied, style: "margin-top:12px" }));
    box.append(el("div", { textContent: result.policies.length ? result.policies.map((p) => p.name).join(", ") : t.none_applied }));
    box.append(el("h2", { textContent: t.ack_title, style: "margin-top:12px" }));
    box.append(el("div", { textContent: ackText(result.acknowledge, t) }));
    box.append(el("h2", { textContent: t.later, style: "margin-top:12px" }));
    box.append(result.later.length ? el("ul", {}, result.later.map((step) => el("li", { textContent: laterText(step, t, s) }))) : el("div", { textContent: t.none_later }));
    return box;
  }

  function outcomeNode() {
    const box = el("div", {}, [el("h2", { textContent: t.what_happened, style: "margin-top:12px" })]);
    if (outcome.length === 0) {
      box.append(el("div", { className: "hint", textContent: waiting ? t.outcome_waiting : t.outcome_none }));
      return box;
    }
    const head = el("tr", {}, [t.recipient, t.channel, t.result].map((text) => el("th", { textContent: text })));
    const rows = outcome.map((entry) => {
      const words = [s.result[entry.result] || entry.result];
      if (entry.reason) words.push(fmt.reasonText(entry.reason, s));
      const who = rowRecipient({ recipient: entry.recipient || "", channel: entry.channel, result: entry.result }, result || {}, data.choices, t);
      return el("tr", {}, [el("td", { textContent: who }), el("td", { textContent: channelLabel(entry.channel) }), el("td", { textContent: words.filter(Boolean).join(" · ") })]);
    });
    box.append(el("table", {}, [el("thead", {}, [head]), el("tbody", {}, rows)]));
    if (outcome.some((entry) => entry.result === "failed")) box.append(el("div", { className: "hint problems", textContent: t.log_hint }));
    return box;
  }

  function yamlNode() {
    const box = el("section", { className: "hu-yaml" }, [el("h2", { textContent: t.yaml })]);
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
    if (outcome !== null) box.append(outcomeNode());
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
    // Found by class, not by position: a section added to the form must not shift what is replaced.
    const resultBox = root.querySelector("section.hu-result");
    const yamlBox = root.querySelector("section.hu-yaml");
    if (!resultBox || !yamlBox) return;
    resultBox.replaceWith(resultNode());
    yamlBox.replaceWith(yamlNode());
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
      notice = fill(t.sent, { id: response.id, summary: plannedLine(response.channels, s) });
      outcome = [];
      waiting = true;
      repaintResult();
      await collectOutcome(response.id, [...values.channels]);
    } catch (err) {
      notice = fill(t.send_failed, { text: err?.message || "" });
    }
    repaintResult();
  }

  // The delivery runs after the call returns, so the real results come from the trace a moment later.
  async function collectOutcome(id, channels) {
    for (let attempt = 0; attempt < 8; attempt += 1) {
      try {
        const trace = await hass.callWS({ type: "heads_up/panel_trace", message_id: id });
        outcome = outcomeRows(trace.entries, channels);
        if (outcomeDone(trace.entries, channels)) break;
      } catch (err) {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 600));
    }
    waiting = false;
    repaintResult();
  }

  async function clearTest() {
    try {
      await hass.callWS({ type: "heads_up/admin_clear", banner_id: testId });
      notice = t.cleared;
      testId = null;
      outcome = null;
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
