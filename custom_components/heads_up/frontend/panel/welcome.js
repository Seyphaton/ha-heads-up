// Heads Up panel: the welcome (D-121, D-131). A four-step tour on the first opening: what Heads Up
// does, then channels, recipients and policies. Only the last step creates anything (the default
// policies the admin switches on). Loaded by the shell.

export const STRINGS = {
  en: {
    title: "Welcome to Heads Up",
    step_of: "Step {n} of {total}",
    steps_label: "Progress of the tour",
    next: "Next",
    back: "Back",
    skip: "Skip the tour",
    open_page: "Open {page}",
    page_channels: "Channels",
    page_audiences: "Audiences",
    page_recipients: "Recipients",
    intro_title: "The right message, to the right people, at the right time",
    intro_lead: "Your automations make one call. Heads Up orchestrates where the message shows up, who gets it, and when it is delivered or escalated.",
    intro_where: "Where",
    intro_where_text: "A banner on your dashboards, a push on phones, a popup on any open dashboard, speech on speakers, mail, or the entry in Home Assistant's own notification list.",
    intro_who: "Who",
    intro_who_text: "Everyone, only the admins, whoever is home, or the person who left last. Heads Up finds each person's phones by itself.",
    intro_when: "When",
    intro_when_text: "Stay quiet at night, repeat a warning that nobody acknowledged, or hold small messages for one summary in the evening.",
    intro_foot: "The next three steps show what to check first. It takes about two minutes. Nothing is created until the last step, and you can come back from Settings.",
    channels_title: "Channels: where a message shows up",
    channels_lead: "A channel is a place a message can appear. A call names one channel or several.",
    ch_banner: "A card on your dashboards. It stays until the problem is gone, someone dismisses it or it times out.",
    ch_push: "A notification in the Home Assistant app on phones and tablets.",
    ch_popup: "A window over any open Home Assistant page, useful on a wall tablet.",
    ch_speak: "Spoken on speakers and Assist satellites.",
    ch_persistent: "The entry in Home Assistant's bell menu. One list shared by everyone.",
    ch_mail: "One mail per person through a notify service you choose.",
    found_push: "App devices found: {n}",
    found_speak: "Speakers and satellites found: {n}",
    found_mail_on: "Notify service: set",
    found_mail_off: "Notify service: not set. Choose one on the Channels page.",
    found_none: "none yet",
    channels_foot: "Push, popup and speech work with their defaults. The Channels page changes how each one looks and sounds, by severity.",
    recipients_title: "Recipients: who gets it",
    recipients_lead: "Most calls name an audience: a group of people that is worked out at the moment the message goes out.",
    aud_builtin: "Built in: Everyone, Admins, At home, Not home, Last to leave and First home. The Audiences page explains each one, and you can add your own.",
    rec_profiles: "Each person also has a profile: their phones and, for mail, an address. Heads Up finds the phones by itself. Open Recipients to change that or to build groups of speakers for speech.",
    rec_found: "In your Home Assistant: people {persons}, with an app device {devices}; audiences of your own {audiences}; speaker groups {groups}.",
    policies_title: "Policies: when to be loud or quiet",
    policies_lead: "A policy changes how messages are delivered without touching your automations. Here are four to start from. Each one can be edited or deleted on the Policies page. Switch off what you do not want; nothing is created until you press Create.",
    item_quiet: "Quiet hours",
    desc_quiet: "From 22:00 to 07:00 pushes of messages that are not critical go out without sound and speech is skipped. Critical messages are not affected.",
    item_digest: "Evening summary",
    desc_digest: "Messages that your automations tag digest are held and sent as one summary at 20:00. Critical messages are never held. Messages without that tag are not affected.",
    item_critical: "Critical messages",
    desc_critical: "Every critical message, also from your existing automations, gets an Acknowledge button and is pushed at once to the audience below at the iOS critical level (the Companion app must allow critical alerts; it plays a sound even in silent mode). Without an acknowledgement it is pushed again every 10 minutes, 3 times, and after 10 minutes it is said on the speakers below. Dismissing counts as acknowledging.",
    item_warnings: "Warning reminders",
    desc_warnings: "A warning that nobody acknowledges is repeated every 30 minutes, at most 3 times.",
    audience: "Push critical messages to",
    speakers: "Speak after 10 minutes on (none: no speech)",
    create: "Create the selected",
    not_now: "Not now",
    close: "Close",
    created: "Created: {added}.",
    skipped: "Already there or the same as one you have: {skipped}.",
    nothing: "nothing",
    failed: "Could not create the policies. Try again.",
  },
  de: {
    title: "Willkommen bei Heads Up",
    step_of: "Schritt {n} von {total}",
    steps_label: "Fortschritt der Tour",
    next: "Weiter",
    back: "Zurück",
    skip: "Tour überspringen",
    open_page: "{page} öffnen",
    page_channels: "Kanäle",
    page_audiences: "Zielgruppen",
    page_recipients: "Empfänger",
    intro_title: "Die richtige Meldung, an die richtigen Leute, zur richtigen Zeit",
    intro_lead: "Deine Automationen machen einen Aufruf. Heads Up orchestriert, wo die Meldung erscheint, wer sie bekommt und wann sie zugestellt oder eskaliert wird.",
    intro_where: "Wo",
    intro_where_text: "Ein Banner auf deinen Dashboards, ein Push aufs Handy, ein Popup auf jedem offenen Dashboard, Sprache auf Lautsprechern, E-Mail oder der Eintrag in der Benachrichtigungsliste von Home Assistant.",
    intro_who: "Wer",
    intro_who_text: "Alle, nur die Admins, wer zu Hause ist oder wer zuletzt gegangen ist. Heads Up findet die Handys jeder Person selbst.",
    intro_when: "Wann",
    intro_when_text: "Nachts leise bleiben, eine Warnung wiederholen, die niemand bestätigt hat, oder kleine Meldungen für eine Zusammenfassung am Abend sammeln.",
    intro_foot: "Die nächsten drei Schritte zeigen, was du zuerst prüfen solltest. Es dauert etwa zwei Minuten. Erst im letzten Schritt wird etwas erstellt, und du kannst über die Einstellungen zurückkommen.",
    channels_title: "Kanäle: wo eine Meldung erscheint",
    channels_lead: "Ein Kanal ist ein Ort, an dem eine Meldung erscheinen kann. Ein Aufruf nennt einen Kanal oder mehrere.",
    ch_banner: "Eine Karte auf deinen Dashboards. Sie bleibt, bis das Problem weg ist, jemand sie ausblendet oder sie abläuft.",
    ch_push: "Eine Benachrichtigung in der Home-Assistant-App auf Handys und Tablets.",
    ch_popup: "Ein Fenster über jeder offenen Home-Assistant-Seite, nützlich auf einem Wandtablet.",
    ch_speak: "Gesprochen auf Lautsprechern und Assist-Satelliten.",
    ch_persistent: "Der Eintrag im Glockenmenü von Home Assistant. Eine Liste für alle.",
    ch_mail: "Eine E-Mail pro Person über einen Benachrichtigungsdienst deiner Wahl.",
    found_push: "Gefundene App-Geräte: {n}",
    found_speak: "Gefundene Lautsprecher und Satelliten: {n}",
    found_mail_on: "Benachrichtigungsdienst: gesetzt",
    found_mail_off: "Benachrichtigungsdienst: nicht gesetzt. Wähle einen auf der Seite Kanäle.",
    found_none: "noch keine",
    channels_foot: "Push, Popup und Sprache funktionieren mit ihren Standards. Die Seite Kanäle ändert, wie jeder aussieht und klingt, nach Schweregrad.",
    recipients_title: "Empfänger: wer sie bekommt",
    recipients_lead: "Die meisten Aufrufe nennen eine Zielgruppe: eine Personengruppe, die in dem Moment bestimmt wird, in dem die Meldung hinausgeht.",
    aud_builtin: "Eingebaut: Everyone, Admins, At home, Not home, Last to leave und First home. Die Seite Zielgruppen erklärt jede, und du kannst eigene hinzufügen.",
    rec_profiles: "Jede Person hat außerdem ein Profil: ihre Handys und für E-Mail eine Adresse. Heads Up findet die Handys selbst. Öffne Empfänger, um das zu ändern oder Lautsprechergruppen für Sprache anzulegen.",
    rec_found: "In deinem Home Assistant: Personen {persons}, davon mit App-Gerät {devices}; eigene Zielgruppen {audiences}; Lautsprechergruppen {groups}.",
    policies_title: "Richtlinien: wann laut, wann leise",
    policies_lead: "Eine Richtlinie ändert, wie Meldungen zugestellt werden, ohne deine Automationen anzufassen. Hier sind vier zum Start. Jede kannst du auf der Seite Richtlinien ändern oder löschen. Schalte aus, was du nicht willst; nichts wird erstellt, bis du Erstellen drückst.",
    item_quiet: "Ruhezeit",
    desc_quiet: "Von 22:00 bis 07:00 werden Pushs nicht kritischer Meldungen ohne Ton gesendet und die Sprachausgabe entfällt. Kritische Meldungen sind nicht betroffen.",
    item_digest: "Abendzusammenfassung",
    desc_digest: "Meldungen, die deine Automationen mit digest markieren, werden zurückgehalten und um 20:00 als eine Zusammenfassung gesendet. Kritische Meldungen werden nie zurückgehalten. Meldungen ohne diesen Tag sind nicht betroffen.",
    item_critical: "Kritische Meldungen",
    desc_critical: "Jede kritische Meldung, auch aus deinen bestehenden Automationen, bekommt eine Schaltfläche Bestätigen und wird sofort an die Zielgruppe unten auf der kritischen Stufe von iOS gepusht (die Companion-App muss kritische Hinweise erlauben; sie spielt auch im Lautlosmodus einen Ton). Ohne Bestätigung wird sie alle 10 Minuten erneut gepusht, 3 Mal, und nach 10 Minuten auf den Lautsprechern unten gesprochen. Ausblenden zählt als Bestätigung.",
    item_warnings: "Warnungs-Erinnerungen",
    desc_warnings: "Eine Warnung, die niemand bestätigt, wird alle 30 Minuten wiederholt, höchstens 3 Mal.",
    audience: "Kritische Meldungen pushen an",
    speakers: "Nach 10 Minuten sprechen auf (keiner: keine Sprachausgabe)",
    create: "Auswahl erstellen",
    not_now: "Jetzt nicht",
    close: "Schließen",
    created: "Erstellt: {added}.",
    skipped: "Schon vorhanden oder wie eine, die du hast: {skipped}.",
    nothing: "nichts",
    failed: "Die Richtlinien konnten nicht erstellt werden. Versuche es erneut.",
  },
  fr: {
    title: "Bienvenue dans Heads Up",
    step_of: "Étape {n} sur {total}",
    steps_label: "Progression de la visite",
    next: "Suivant",
    back: "Retour",
    skip: "Passer la visite",
    open_page: "Ouvrir {page}",
    page_channels: "Canaux",
    page_audiences: "Audiences",
    page_recipients: "Destinataires",
    intro_title: "Le bon message, aux bonnes personnes, au bon moment",
    intro_lead: "Vos automatisations font un seul appel. Heads Up orchestre où le message apparaît, qui le reçoit, et quand il est livré ou escaladé.",
    intro_where: "Où",
    intro_where_text: "Une bannière sur vos tableaux de bord, un push sur les téléphones, une fenêtre sur tout tableau de bord ouvert, la voix sur des haut-parleurs, un mail, ou l'entrée dans la liste de notifications de Home Assistant.",
    intro_who: "Qui",
    intro_who_text: "Tout le monde, seulement les administrateurs, qui est à la maison, ou la personne partie en dernier. Heads Up trouve seul les téléphones de chaque personne.",
    intro_when: "Quand",
    intro_when_text: "Rester discret la nuit, répéter un avertissement que personne n'a confirmé, ou retenir les petits messages pour un seul résumé le soir.",
    intro_foot: "Les trois étapes suivantes montrent ce qu'il faut vérifier d'abord. Cela prend environ deux minutes. Rien n'est créé avant la dernière étape, et vous pouvez revenir depuis Réglages.",
    channels_title: "Canaux : où un message apparaît",
    channels_lead: "Un canal est un endroit où un message peut apparaître. Un appel nomme un canal ou plusieurs.",
    ch_banner: "Une carte sur vos tableaux de bord. Elle reste jusqu'à la fin du problème, jusqu'à ce que quelqu'un la masque ou qu'elle expire.",
    ch_push: "Une notification dans l'app Home Assistant sur téléphones et tablettes.",
    ch_popup: "Une fenêtre au-dessus de toute page Home Assistant ouverte, utile sur une tablette murale.",
    ch_speak: "Dit sur des haut-parleurs et des satellites Assist.",
    ch_persistent: "L'entrée du menu cloche de Home Assistant. Une liste partagée par tous.",
    ch_mail: "Un mail par personne via un service de notification de votre choix.",
    found_push: "Appareils d'app trouvés : {n}",
    found_speak: "Haut-parleurs et satellites trouvés : {n}",
    found_mail_on: "Service de notification : défini",
    found_mail_off: "Service de notification : non défini. Choisissez-en un sur la page Canaux.",
    found_none: "aucun pour l'instant",
    channels_foot: "Push, fenêtre et voix fonctionnent avec leurs réglages par défaut. La page Canaux change l'apparence et le son de chacun, par gravité.",
    recipients_title: "Destinataires : qui le reçoit",
    recipients_lead: "La plupart des appels nomment une audience : un groupe de personnes déterminé au moment où le message part.",
    aud_builtin: "Intégrées : Everyone, Admins, At home, Not home, Last to leave et First home. La page Audiences explique chacune, et vous pouvez ajouter les vôtres.",
    rec_profiles: "Chaque personne a aussi un profil : ses téléphones et, pour le mail, une adresse. Heads Up trouve seul les téléphones. Ouvrez Destinataires pour changer cela ou pour créer des groupes de haut-parleurs pour la voix.",
    rec_found: "Dans votre Home Assistant : personnes {persons}, avec appareil d'app {devices} ; audiences à vous {audiences} ; groupes de haut-parleurs {groups}.",
    policies_title: "Politiques : quand être fort ou discret",
    policies_lead: "Une politique change la façon dont les messages sont livrés sans toucher vos automatisations. Voici quatre points de départ. Chacune se modifie ou se supprime sur la page Politiques. Désactivez ce que vous ne voulez pas ; rien n'est créé avant d'appuyer sur Créer.",
    item_quiet: "Heures calmes",
    desc_quiet: "De 22:00 à 07:00, les push des messages non critiques partent sans son et la voix est ignorée. Les messages critiques ne sont pas concernés.",
    item_digest: "Résumé du soir",
    desc_digest: "Les messages que vos automatisations marquent digest sont retenus et envoyés en un résumé à 20:00. Les messages critiques ne sont jamais retenus. Les messages sans cette étiquette ne sont pas concernés.",
    item_critical: "Messages critiques",
    desc_critical: "Chaque message critique, aussi ceux de vos automatisations existantes, reçoit un bouton Confirmer et est envoyé tout de suite à l'audience ci-dessous au niveau critique d'iOS (l'app Companion doit autoriser les alertes critiques ; elle joue un son même en mode silencieux). Sans confirmation, il est renvoyé toutes les 10 minutes, 3 fois, et après 10 minutes il est dit sur les haut-parleurs ci-dessous. Masquer vaut confirmer.",
    item_warnings: "Rappels d'avertissement",
    desc_warnings: "Un avertissement que personne ne confirme est répété toutes les 30 minutes, au plus 3 fois.",
    audience: "Envoyer les messages critiques à",
    speakers: "Dire après 10 minutes sur (aucun : pas de voix)",
    create: "Créer la sélection",
    not_now: "Pas maintenant",
    close: "Fermer",
    created: "Créé : {added}.",
    skipped: "Déjà là ou identique à l'une des vôtres : {skipped}.",
    nothing: "rien",
    failed: "Les politiques n'ont pas pu être créées. Réessayez.",
  },
  es: {
    title: "Te damos la bienvenida a Heads Up",
    step_of: "Paso {n} de {total}",
    steps_label: "Progreso del recorrido",
    next: "Siguiente",
    back: "Atrás",
    skip: "Omitir el recorrido",
    open_page: "Abrir {page}",
    page_channels: "Canales",
    page_audiences: "Audiencias",
    page_recipients: "Destinatarios",
    intro_title: "El mensaje justo, a las personas justas, en el momento justo",
    intro_lead: "Tus automatizaciones hacen una sola llamada. Heads Up orquesta dónde aparece el mensaje, quién lo recibe y cuándo se entrega o se escala.",
    intro_where: "Dónde",
    intro_where_text: "Un aviso en tus paneles, un push en los móviles, una ventana sobre cualquier panel abierto, voz en altavoces, correo, o la entrada en la lista de notificaciones de Home Assistant.",
    intro_who: "Quién",
    intro_who_text: "Todos, solo los administradores, quien está en casa o la persona que salió la última. Heads Up encuentra solo los móviles de cada persona.",
    intro_when: "Cuándo",
    intro_when_text: "Callar por la noche, repetir un aviso que nadie confirmó, o retener los mensajes pequeños para un solo resumen por la tarde.",
    intro_foot: "Los tres pasos siguientes muestran qué revisar primero. Lleva unos dos minutos. No se crea nada hasta el último paso, y puedes volver desde Ajustes.",
    channels_title: "Canales: dónde aparece un mensaje",
    channels_lead: "Un canal es un lugar donde puede aparecer un mensaje. Una llamada nombra un canal o varios.",
    ch_banner: "Una tarjeta en tus paneles. Se queda hasta que el problema desaparece, alguien la descarta o caduca.",
    ch_push: "Una notificación en la app de Home Assistant en móviles y tabletas.",
    ch_popup: "Una ventana sobre cualquier página abierta de Home Assistant, útil en una tableta de pared.",
    ch_speak: "Dicho en altavoces y satélites de Assist.",
    ch_persistent: "La entrada del menú de la campana de Home Assistant. Una lista compartida por todos.",
    ch_mail: "Un correo por persona mediante un servicio de notificación que elijas.",
    found_push: "Dispositivos de la app encontrados: {n}",
    found_speak: "Altavoces y satélites encontrados: {n}",
    found_mail_on: "Servicio de notificación: definido",
    found_mail_off: "Servicio de notificación: sin definir. Elige uno en la página Canales.",
    found_none: "ninguno por ahora",
    channels_foot: "Push, ventana y voz funcionan con sus valores por defecto. La página Canales cambia cómo se ve y suena cada uno, por gravedad.",
    recipients_title: "Destinatarios: quién lo recibe",
    recipients_lead: "La mayoría de las llamadas nombran una audiencia: un grupo de personas que se calcula en el momento en que sale el mensaje.",
    aud_builtin: "Integradas: Everyone, Admins, At home, Not home, Last to leave y First home. La página Audiencias explica cada una, y puedes añadir las tuyas.",
    rec_profiles: "Cada persona tiene además un perfil: sus móviles y, para el correo, una dirección. Heads Up encuentra solo los móviles. Abre Destinatarios para cambiarlo o para crear grupos de altavoces para la voz.",
    rec_found: "En tu Home Assistant: personas {persons}, con dispositivo de la app {devices}; audiencias propias {audiences}; grupos de altavoces {groups}.",
    policies_title: "Políticas: cuándo ser fuerte o discreto",
    policies_lead: "Una política cambia cómo se entregan los mensajes sin tocar tus automatizaciones. Aquí hay cuatro para empezar. Cada una se edita o se borra en la página Políticas. Desactiva lo que no quieras; no se crea nada hasta que pulses Crear.",
    item_quiet: "Horas de silencio",
    desc_quiet: "De 22:00 a 07:00 los push de mensajes no críticos salen sin sonido y se omite la voz. Los mensajes críticos no se ven afectados.",
    item_digest: "Resumen de la tarde",
    desc_digest: "Los mensajes que tus automatizaciones marcan con digest se retienen y se envían como un resumen a las 20:00. Los mensajes críticos nunca se retienen. Los mensajes sin esa etiqueta no se ven afectados.",
    item_critical: "Mensajes críticos",
    desc_critical: "Cada mensaje crítico, también los de tus automatizaciones existentes, recibe un botón Confirmar y se envía de inmediato a la audiencia de abajo con el nivel crítico de iOS (la app Companion debe permitir alertas críticas; suena incluso en modo silencio). Sin confirmación se vuelve a enviar cada 10 minutos, 3 veces, y a los 10 minutos se dice en los altavoces de abajo. Descartar cuenta como confirmar.",
    item_warnings: "Recordatorios de avisos",
    desc_warnings: "Un aviso que nadie confirma se repite cada 30 minutos, como máximo 3 veces.",
    audience: "Enviar los mensajes críticos a",
    speakers: "Decir a los 10 minutos en (ninguno: sin voz)",
    create: "Crear la selección",
    not_now: "Ahora no",
    close: "Cerrar",
    created: "Creado: {added}.",
    skipped: "Ya existe o es igual a una tuya: {skipped}.",
    nothing: "nada",
    failed: "No se pudieron crear las políticas. Inténtalo de nuevo.",
  },
};

export const ITEMS = ["quiet", "digest", "critical", "warnings"];
export const STEPS = ["intro", "channels", "recipients", "policies"];
const CHANNEL_ORDER = ["banner", "push", "popup", "speak", "persistent", "mail"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// The call to heads_up/welcome_apply for the state of the dialog: only the switched-on items.
export function payloadFor(state) {
  const items = ITEMS.filter((id) => state.on[id]);
  const payload = { type: "heads_up/welcome_apply", items };
  if (items.includes("critical")) {
    payload.audience = state.audience;
    payload.speakers = [...state.speakers];
  }
  return payload;
}

export function resultText(result, t) {
  const names = (list) => list.map((x) => (typeof x === "string" ? x : x.name)).join(", ") || t.nothing;
  const lines = [fill(t.created, { added: names(result.added) })];
  if (result.skipped.length) lines.push(fill(t.skipped, { skipped: names(result.skipped) }));
  return lines.join(" ");
}

// What the tour shows about this Home Assistant, from `heads_up/panel_config`; null when that
// call failed, in which case the tour shows no numbers.
export function setupSummary(config) {
  if (!config) return null;
  const profiles = config.profiles || [];
  return {
    persons: (config.choices?.persons || profiles).length,
    devices: profiles.reduce((sum, p) => sum + (p.devices || []).length, 0),
    withDevice: profiles.filter((p) => (p.devices || []).length > 0).length,
    speakers: (config.choices?.speakers || []).length,
    mail: Boolean(config.channels?.mail_service),
    audiences: (config.audiences || []).filter((a) => !a.builtin).length,
    groups: (config.groups || []).length,
  };
}

// The line under a channel on the channels step, or "" for a channel that needs nothing found.
export function channelStatus(channel, summary, t) {
  if (!summary) return "";
  switch (channel) {
    case "push":
      return fill(t.found_push, { n: summary.devices || t.found_none });
    case "speak":
      return fill(t.found_speak, { n: summary.speakers || t.found_none });
    case "mail":
      return summary.mail ? t.found_mail_on : t.found_mail_off;
    default:
      return "";
  }
}

export function recipientsStatus(summary, t) {
  if (!summary) return "";
  return fill(t.rec_found, { persons: summary.persons, devices: summary.withDevice, audiences: summary.audiences, groups: summary.groups });
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-scrim { position: fixed; inset: 0; z-index: 20; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; padding: 16px; }
.hu-dialog { background: var(--card-background-color); color: var(--primary-text-color); border-radius: 12px; max-width: 720px; width: 100%; max-height: calc(100vh - 32px); overflow: auto; padding: 20px 24px; box-shadow: 0 4px 24px rgba(0,0,0,.4); }
.hu-dialog h2 { margin: 0 0 4px; font-size: 22px; }
.hu-dialog h3 { margin: 16px 0 4px; font-size: 16px; }
.hu-dialog p { margin: 4px 0 8px; line-height: 1.5; }
.hu-dialog .eyebrow { color: var(--secondary-text-color); font-size: 13px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.hu-dialog .dots { display: flex; gap: 6px; margin: 0; padding: 0; list-style: none; }
.hu-dialog .dots li { width: 28px; height: 6px; border-radius: 3px; background: var(--divider-color); }
.hu-dialog .dots li.done { background: var(--primary-color); opacity: .5; }
.hu-dialog .dots li.now { background: var(--primary-color); }
.hu-dialog .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; line-height: 1.45; }
.hu-dialog .lead { font-size: 16px; }
.hu-dialog .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin: 12px 0; }
.hu-dialog .mini { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; }
.hu-dialog .mini strong { display: block; margin-bottom: 2px; }
.hu-dialog .mini .found { margin-top: 6px; font-size: 13px; color: var(--primary-text-color); }
.hu-dialog .facts { border-left: 3px solid var(--primary-color); padding: 2px 0 2px 12px; margin: 12px 0; }
.hu-dialog .item { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; }
.hu-dialog label.inline { display: flex; align-items: center; gap: 10px; min-height: 48px; font-weight: 600; }
.hu-dialog input[type=checkbox] { width: 22px; height: 22px; }
.hu-dialog select { min-height: 40px; max-width: 100%; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; }
.hu-dialog fieldset { border: 1px solid var(--divider-color); border-radius: 8px; max-height: 160px; overflow: auto; margin: 8px 0; }
.hu-dialog legend { color: var(--secondary-text-color); font-size: 13px; }
.hu-dialog button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-dialog button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-dialog button.link { border: none; color: var(--secondary-text-color); text-decoration: underline; padding: 0 8px; }
.hu-dialog button:focus-visible, .hu-dialog select:focus-visible, .hu-dialog input:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-dialog .row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; align-items: center; }
.hu-dialog .row .grow { flex: 1; }
`;

// Opens the welcome in `host`. On the first opening only while it has not been seen; with `force`
// always. `ctx.step` (0 to 3) is the step to start at; `ctx.leave(page, nextStep)` closes the tour and
// opens a page, and the shell offers to continue. Resolves to { close } or null when nothing is shown.
export async function open(host, ctx) {
  const { t, hass, ui } = ctx;
  const data = await hass.callWS({ type: "heads_up/welcome_get" });
  if (!ctx.force && !data.show) return null;
  const summary = setupSummary(await hass.callWS({ type: "heads_up/panel_config" }).catch(() => null));
  const state = { on: Object.fromEntries(ITEMS.map((id) => [id, true])), audience: data.default_audience, speakers: [], step: Math.min(Math.max(ctx.step || 0, 0), STEPS.length - 1) };
  const scrim = el("div", { className: "hu-scrim" });
  const dialog = el("div", { className: "hu-dialog", role: "dialog" });
  dialog.setAttribute("aria-modal", "true");
  dialog.setAttribute("aria-label", t.title);
  scrim.append(el("style", { textContent: CSS }), dialog);
  host.append(scrim);
  let previous = host.activeElement;
  let seen = !data.show;

  const close = () => {
    scrim.remove();
    if (previous?.isConnected) previous.focus?.();
  };
  // The first opening counts as seen once the admin closes, skips or leaves it, so it does not
  // return every time. Creating policies marks it seen on the server.
  const markSeen = async () => {
    if (!seen) await hass.callWS({ type: "heads_up/welcome_apply", items: [] }).catch(() => {});
    seen = true;
  };
  const dismiss = async () => {
    await markSeen();
    close();
  };
  const leaveTo = async (page) => {
    await markSeen();
    ctx.leave?.(page, state.step + 1);
  };

  const button = (text, onClick, className = "") => {
    const node = el("button", { type: "button", textContent: text, className });
    node.addEventListener("click", onClick);
    return node;
  };
  const go = (step) => {
    state.step = step;
    render();
    dialog.querySelector("h2")?.focus();
  };

  function header() {
    const dots = el("ol", { className: "dots" });
    dots.setAttribute("aria-label", t.steps_label);
    STEPS.forEach((id, i) => dots.append(el("li", { className: i < state.step ? "done" : i === state.step ? "now" : "" })));
    const title = [t.intro_title, t.channels_title, t.recipients_title, t.policies_title][state.step];
    const top = el("div", { className: "eyebrow" }, [el("span", { textContent: fill(t.step_of, { n: state.step + 1, total: STEPS.length }) }), dots]);
    const h2 = el("h2", { textContent: state.step === 0 ? t.title : title, tabIndex: -1 });
    return state.step === 0 ? [top, h2, el("p", { className: "lead", textContent: t.intro_title })] : [top, h2];
  }

  function nav(...extra) {
    const row = el("div", { className: "row" });
    if (state.step > 0) row.append(button(t.back, () => go(state.step - 1)));
    row.append(el("span", { className: "grow" }));
    row.append(...extra);
    return row;
  }

  function stepIntro() {
    const out = [el("p", { textContent: t.intro_lead })];
    const grid = el("div", { className: "grid" });
    for (const key of ["where", "who", "when"]) {
      grid.append(el("div", { className: "mini" }, [el("strong", { textContent: t[`intro_${key}`] }), el("span", { textContent: t[`intro_${key}_text`] })]));
    }
    out.push(grid, el("div", { className: "hint", textContent: t.intro_foot }));
    out.push(nav(button(t.skip, dismiss, "link"), button(t.next, () => go(1), "primary")));
    return out;
  }

  function stepChannels() {
    const out = [el("p", { textContent: t.channels_lead })];
    const grid = el("div", { className: "grid" });
    for (const channel of CHANNEL_ORDER) {
      const found = channelStatus(channel, summary, t);
      const box = el("div", { className: "mini" }, [el("strong", { textContent: ctx.s.channel[channel] || channel }), el("span", { textContent: t[`ch_${channel}`] })]);
      if (found) box.append(el("div", { className: "found", textContent: found }));
      grid.append(box);
    }
    out.push(grid, el("div", { className: "hint", textContent: t.channels_foot }));
    out.push(nav(button(fill(t.open_page, { page: t.page_channels }), () => leaveTo("channels")), button(t.next, () => go(2), "primary")));
    return out;
  }

  function stepRecipients() {
    const out = [el("p", { textContent: t.recipients_lead }), el("p", { textContent: t.aud_builtin }), el("p", { textContent: t.rec_profiles })];
    const facts = recipientsStatus(summary, t);
    if (facts) out.push(el("div", { className: "facts", textContent: facts }));
    out.push(nav(button(fill(t.open_page, { page: t.page_audiences }), () => leaveTo("audiences")), button(fill(t.open_page, { page: t.page_recipients }), () => leaveTo("recipients")), button(t.next, () => go(3), "primary")));
    return out;
  }

  function stepPolicies(message) {
    const out = [el("p", { textContent: t.policies_lead })];
    for (const id of ITEMS) {
      const box = el("input", { type: "checkbox", checked: state.on[id] });
      box.addEventListener("change", () => {
        state.on[id] = box.checked;
        render();
      });
      const item = el("div", { className: "item" }, [
        el("label", { className: "inline" }, [box, el("span", { textContent: t[`item_${id}`] })]),
        el("div", { className: "hint", textContent: t[`desc_${id}`] }),
      ]);
      if (id === "critical" && state.on.critical) {
        item.append(ui.field(t.audience, ui.selectInput(data.audiences.map((n) => ({ value: n, label: n })), state.audience, (v) => { state.audience = v; })));
        if (data.speakers.length) {
          item.append(ui.chips(t.speakers, data.speakers.map((id2) => ({ value: id2, label: ui.recipientLabel(id2, data) })), state.speakers, (list) => { state.speakers = list; }, true));
        }
      }
      out.push(item);
    }
    const create = button(t.create, async () => {
      try {
        const result = await hass.callWS(payloadFor(state));
        seen = true;
        render(resultText(result, t), true);
      } catch (err) {
        render(t.failed);
      }
    }, "primary");
    out.push(nav(button(t.not_now, dismiss), create));
    if (message) out.push(el("div", { className: "hint", textContent: message }));
    return out;
  }

  function render(message = "", done = false) {
    if (done) {
      dialog.replaceChildren(el("h2", { textContent: t.title }), el("p", { textContent: message }));
      const closeButton = button(t.close, close, "primary");
      dialog.append(el("div", { className: "row" }, [closeButton]));
      closeButton.focus();
      return;
    }
    const body = [stepIntro, stepChannels, stepRecipients, stepPolicies][state.step](message);
    dialog.replaceChildren(...header(), ...body);
  }
  scrim.addEventListener("keydown", (event) => {
    if (event.key === "Escape") dismiss();
  });
  render();
  dialog.querySelector("button, input")?.focus();
  return { close };
}
