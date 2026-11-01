// Heads Up panel: FAQ and examples page (H9f). Loaded by the shell when the page is opened.
// The examples are plain calls: `make docs-check` validates every `yaml:` block below against the
// real action schemas, so an example cannot drift from the actions.

export const EXAMPLES = [
  {
    id: "e1",
    yaml: `action: heads_up.create_banner
data:
  message: Window open`,
  },
  {
    id: "e2",
    yaml: `action: heads_up.notify
data:
  message: Water leak
  severity: critical
  tag: water
  channels: [banner, push]
  to:
    push: {audience: Everyone}`,
  },
  {
    id: "e3",
    yaml: `action: heads_up.notify
data:
  message: Water leak
  tts_message: Water in the utility room
  severity: critical
  channels: [push, speak, persistent]
  to:
    push: {audience: Admins}
    speak: {recipients: [Ground floor speakers]}`,
  },
  {
    id: "e4",
    yaml: `action: heads_up.notify
data:
  message: Doorbell
  tts_message: Someone is at the door
  channels: [speak]
  to:
    speak: {recipients: [Kitchen speaker]}
  policy: none`,
  },
  {
    id: "e5",
    yaml: `action: heads_up.push
data:
  message: Window left open
  audience: Last to leave`,
  },
  {
    id: "e6",
    yaml: `action: heads_up.notify
data:
  message: Washer is done
  severity: info
  channels: [push]
  to:
    push: {recipients: [Anna]}`,
  },
];

export const QUESTION_IDS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11"];

export const STRINGS = {
  en: {
    title: "FAQ and examples",
    intro: "Examples of calls, from the simplest to the most detailed, and answers to common questions. Names such as Anna, Admins and Kitchen speaker are samples: use the names of your own audiences, persons and speakers.",
    examples: "Examples",
    questions: "Questions",
    copy: "Copy",
    copied: "Copied.",
    copy_failed: "Copying is not possible here. Select the text.",
    ex: {
      e1: { title: "1. Banner only, as before the hub", note: "No hub object is needed. Nothing else is sent." },
      e2: { title: "2. Banner and push, policies add the rest", note: "Policies that match the severity and the tag apply as well, for example an escalation to Admins after 5 minutes." },
      e3: { title: "3. Push, speech and persistent notification together", note: "Each channel has its own target. The persistent notification needs none." },
      e4: { title: "4. One call, no policy", note: "Speech on one speaker, ignoring every policy." },
      e5: { title: "5. Shortcut for one channel", note: "The push shortcut with a presence audience: the person whose departure emptied the house." },
      e6: { title: "6. To one person", note: "A direct recipient instead of an audience." },
    },
    q: {
      q1: { q: "Do I need the hub for banners?", a: "No. create_banner, clear_banner, clear_all, watch rules and the card work without any hub object." },
      q2: { q: "What is the difference between an audience and direct recipients?", a: "An audience is a named group of people that can change over time (Everyone, At home, Last to leave). Direct recipients are fixed targets such as one person, one phone or one speaker. A channel takes one or the other, never both." },
      q3: { q: "Why does speech take no audience?", a: "An audience is a set of people, and speech goes to a speaker in a place. The hub does not know which speaker a person is near, so you name the speakers." },
      q4: { q: "Can one call send push, speech and a persistent notification?", a: "Yes. Name the channels and give each channel its own target in \"to\", as in example 3." },
      q5: { q: "What happens if nobody reacts?", a: "An escalation policy can notify more people or channels after a delay, and a reminder policy can repeat the message. Any acknowledgement stops both. Whether dismissing counts as acknowledging is a setting of the escalation policy." },
      q6: { q: "How do I keep messages quiet at night?", a: "Add a quiet hours policy: hold messages until the end, send them quietly or drop them. Critical messages can pass anyway." },
      q7: { q: "What if someone is not home?", a: "An away policy sends the message when they arrive, while the message is still active. A fallback policy can send to someone else instead." },
      q8: { q: "Can I get one summary instead of many messages?", a: "Yes. A summarize policy holds matching messages and sends one summary every N minutes or at a fixed time, with the count and the titles. While a message waits, nothing is sent for it on any channel, the dashboard banner included." },
      q9: { q: "What happens when I replace a phone?", a: "Edit the person's recipient profile once. Audiences and policies do not change, and no automation needs editing." },
      q10: { q: "Why did I not get a notification?", a: "The Test send page shows who would be notified for a given call and why anyone was skipped, held or dropped. The Messages page shows what happened to a real message." },
      q11: { q: "What happens after a restart?", a: "Pending escalations keep their due times. A step that was due during the restart runs once if the message is still active and unacknowledged. Pushes of messages that no longer exist are cleared." },
    },
  },
  de: {
    title: "FAQ und Beispiele",
    intro: "Beispiele für Aufrufe, vom einfachsten bis zum ausführlichsten, und Antworten auf häufige Fragen. Namen wie Anna, Admins und Kitchen speaker sind Muster: Verwende die Namen deiner eigenen Zielgruppen, Personen und Lautsprecher.",
    examples: "Beispiele",
    questions: "Fragen",
    copy: "Kopieren",
    copied: "Kopiert.",
    copy_failed: "Kopieren ist hier nicht möglich. Markiere den Text.",
    ex: {
      e1: { title: "1. Nur Banner, wie vor dem Hub", note: "Es braucht kein Hub-Objekt. Es wird nichts anderes gesendet." },
      e2: { title: "2. Banner und Push, Richtlinien ergänzen den Rest", note: "Richtlinien, die zu Schweregrad und Tag passen, gelten ebenfalls, zum Beispiel eine Eskalation an Admins nach 5 Minuten." },
      e3: { title: "3. Push, Sprache und dauerhafte Benachrichtigung zusammen", note: "Jeder Kanal hat sein eigenes Ziel. Die dauerhafte Benachrichtigung braucht keines." },
      e4: { title: "4. Ein Aufruf ohne Richtlinie", note: "Sprache auf einem Lautsprecher, alle Richtlinien werden ignoriert." },
      e5: { title: "5. Kurzform für einen Kanal", note: "Die Push-Kurzform mit einer Anwesenheits-Zielgruppe: die Person, deren Weggang das Haus geleert hat." },
      e6: { title: "6. An eine Person", note: "Ein direkter Empfänger statt einer Zielgruppe." },
    },
    q: {
      q1: { q: "Brauche ich den Hub für Banner?", a: "Nein. create_banner, clear_banner, clear_all, Überwachungsregeln und die Karte funktionieren ohne Hub-Objekt." },
      q2: { q: "Was ist der Unterschied zwischen Zielgruppe und direkten Empfängern?", a: "Eine Zielgruppe ist eine benannte Gruppe von Personen, die sich mit der Zeit ändern kann (Alle, Zu Hause, Zuletzt gegangen). Direkte Empfänger sind feste Ziele wie eine Person, ein Telefon oder ein Lautsprecher. Ein Kanal nimmt das eine oder das andere, nie beides." },
      q3: { q: "Warum nimmt Sprache keine Zielgruppe?", a: "Eine Zielgruppe ist eine Menge von Personen, Sprache geht aber an einen Lautsprecher an einem Ort. Der Hub weiß nicht, bei welchem Lautsprecher eine Person ist, also nennst du die Lautsprecher." },
      q4: { q: "Kann ein Aufruf Push, Sprache und eine dauerhafte Benachrichtigung senden?", a: "Ja. Nenne die Kanäle und gib jedem Kanal in \"to\" sein eigenes Ziel, wie in Beispiel 3." },
      q5: { q: "Was passiert, wenn niemand reagiert?", a: "Eine Eskalationsrichtlinie kann nach einer Verzögerung weitere Personen oder Kanäle benachrichtigen, eine Erinnerungsrichtlinie kann die Meldung wiederholen. Jede Bestätigung stoppt beides. Ob Ausblenden als Bestätigen zählt, stellt die Eskalationsrichtlinie ein." },
      q6: { q: "Wie halte ich Meldungen nachts leise?", a: "Füge eine Ruhezeit-Richtlinie hinzu: Meldungen bis zum Ende zurückhalten, leise senden oder verwerfen. Kritische Meldungen können trotzdem durchkommen." },
      q7: { q: "Was, wenn jemand nicht zu Hause ist?", a: "Eine Abwesenheitsrichtlinie sendet die Meldung bei der Ankunft, solange sie noch aktiv ist. Eine Ersatzrichtlinie kann stattdessen an jemand anderen senden." },
      q8: { q: "Kann ich eine Zusammenfassung statt vieler Meldungen bekommen?", a: "Ja. Eine Zusammenfassungsrichtlinie hält passende Meldungen zurück und sendet alle N Minuten oder zu einer festen Uhrzeit eine Zusammenfassung mit Anzahl und Titeln. Solange eine Meldung wartet, wird für sie auf keinem Kanal etwas gesendet, auch nicht als Banner im Dashboard." },
      q9: { q: "Was passiert, wenn ich ein Telefon ersetze?", a: "Bearbeite einmal das Empfängerprofil der Person. Zielgruppen und Richtlinien ändern sich nicht, und keine Automatisierung muss angepasst werden." },
      q10: { q: "Warum habe ich keine Benachrichtigung bekommen?", a: "Die Seite Testsenden zeigt, wer für einen Aufruf benachrichtigt würde und warum jemand übersprungen, zurückgehalten oder verworfen wurde. Die Seite Meldungen zeigt, was mit einer echten Meldung geschah." },
      q11: { q: "Was passiert nach einem Neustart?", a: "Ausstehende Eskalationen behalten ihre Fälligkeit. Ein Schritt, der während des Neustarts fällig war, läuft einmal, wenn die Meldung noch aktiv und unbestätigt ist. Pushes zu Meldungen, die es nicht mehr gibt, werden entfernt." },
    },
  },
  fr: {
    title: "FAQ et exemples",
    intro: "Exemples d'appels, du plus simple au plus détaillé, et réponses aux questions courantes. Les noms comme Anna, Admins et Kitchen speaker sont des exemples : utilisez les noms de vos propres audiences, personnes et haut-parleurs.",
    examples: "Exemples",
    questions: "Questions",
    copy: "Copier",
    copied: "Copié.",
    copy_failed: "La copie n'est pas possible ici. Sélectionnez le texte.",
    ex: {
      e1: { title: "1. Bannière seule, comme avant le hub", note: "Aucun objet du hub n'est nécessaire. Rien d'autre n'est envoyé." },
      e2: { title: "2. Bannière et push, les politiques ajoutent le reste", note: "Les politiques qui correspondent à la gravité et à l'étiquette s'appliquent aussi, par exemple une escalade vers Admins après 5 minutes." },
      e3: { title: "3. Push, voix et notification persistante ensemble", note: "Chaque canal a sa propre cible. La notification persistante n'en a pas besoin." },
      e4: { title: "4. Un appel, sans politique", note: "Voix sur un haut-parleur, en ignorant toutes les politiques." },
      e5: { title: "5. Raccourci pour un canal", note: "Le raccourci push avec une audience de présence : la personne dont le départ a vidé la maison." },
      e6: { title: "6. À une personne", note: "Un destinataire direct au lieu d'une audience." },
    },
    q: {
      q1: { q: "Ai-je besoin du hub pour les bannières ?", a: "Non. create_banner, clear_banner, clear_all, les règles de surveillance et la carte fonctionnent sans aucun objet du hub." },
      q2: { q: "Quelle différence entre une audience et des destinataires directs ?", a: "Une audience est un groupe nommé de personnes qui peut changer avec le temps (Tout le monde, À la maison, Dernier parti). Des destinataires directs sont des cibles fixes : une personne, un téléphone ou un haut-parleur. Un canal prend l'un ou l'autre, jamais les deux." },
      q3: { q: "Pourquoi la voix n'accepte-t-elle pas d'audience ?", a: "Une audience est un ensemble de personnes, alors que la voix va vers un haut-parleur dans un lieu. Le hub ne sait pas près de quel haut-parleur se trouve une personne : vous nommez donc les haut-parleurs." },
      q4: { q: "Un appel peut-il envoyer push, voix et notification persistante ?", a: "Oui. Nommez les canaux et donnez à chacun sa propre cible dans « to », comme dans l'exemple 3." },
      q5: { q: "Que se passe-t-il si personne ne réagit ?", a: "Une politique d'escalade peut prévenir d'autres personnes ou canaux après un délai, et une politique de rappel peut répéter le message. Toute confirmation arrête les deux. Que masquer vaille confirmer est un réglage de la politique d'escalade." },
      q6: { q: "Comment garder les messages silencieux la nuit ?", a: "Ajoutez une politique d'heures calmes : retenir les messages jusqu'à la fin, les envoyer discrètement ou les abandonner. Les messages critiques peuvent passer quand même." },
      q7: { q: "Et si quelqu'un n'est pas à la maison ?", a: "Une politique d'absence envoie le message à l'arrivée, tant qu'il est encore actif. Une politique de repli peut envoyer à quelqu'un d'autre à la place." },
      q8: { q: "Puis-je recevoir un résumé au lieu de nombreux messages ?", a: "Oui. Une politique de résumé retient les messages correspondants et envoie un résumé toutes les N minutes ou à une heure fixe, avec le nombre et les titres. Tant qu'un message attend, rien n'est envoyé pour lui sur aucun canal, la bannière du tableau de bord comprise." },
      q9: { q: "Que se passe-t-il quand je remplace un téléphone ?", a: "Modifiez une fois le profil de destinataire de la personne. Les audiences et les politiques ne changent pas, et aucune automatisation n'est à modifier." },
      q10: { q: "Pourquoi n'ai-je pas reçu de notification ?", a: "La page Envoi de test montre qui serait prévenu pour un appel donné et pourquoi quelqu'un a été ignoré, retenu ou abandonné. La page Messages montre ce qui s'est passé pour un vrai message." },
      q11: { q: "Que se passe-t-il après un redémarrage ?", a: "Les escalades en attente gardent leur échéance. Une étape échue pendant le redémarrage s'exécute une fois si le message est encore actif et non confirmé. Les push de messages qui n'existent plus sont supprimés." },
    },
  },
  es: {
    title: "Preguntas y ejemplos",
    intro: "Ejemplos de llamadas, de la más simple a la más detallada, y respuestas a preguntas frecuentes. Nombres como Anna, Admins y Kitchen speaker son ejemplos: usa los nombres de tus propias audiencias, personas y altavoces.",
    examples: "Ejemplos",
    questions: "Preguntas",
    copy: "Copiar",
    copied: "Copiado.",
    copy_failed: "No se puede copiar aquí. Selecciona el texto.",
    ex: {
      e1: { title: "1. Solo aviso, como antes del hub", note: "No hace falta ningún objeto del hub. No se envía nada más." },
      e2: { title: "2. Aviso y push, las políticas añaden el resto", note: "Las políticas que coinciden con la gravedad y la etiqueta también se aplican, por ejemplo un escalado a Admins tras 5 minutos." },
      e3: { title: "3. Push, voz y notificación persistente juntos", note: "Cada canal tiene su propio destino. La notificación persistente no necesita ninguno." },
      e4: { title: "4. Una llamada sin política", note: "Voz en un altavoz, ignorando todas las políticas." },
      e5: { title: "5. Atajo para un canal", note: "El atajo push con una audiencia de presencia: la persona cuya salida vació la casa." },
      e6: { title: "6. A una persona", note: "Un destinatario directo en lugar de una audiencia." },
    },
    q: {
      q1: { q: "¿Necesito el hub para los avisos?", a: "No. create_banner, clear_banner, clear_all, las reglas de vigilancia y la tarjeta funcionan sin ningún objeto del hub." },
      q2: { q: "¿Qué diferencia hay entre una audiencia y destinatarios directos?", a: "Una audiencia es un grupo con nombre de personas que puede cambiar con el tiempo (Todos, En casa, Último en salir). Los destinatarios directos son destinos fijos: una persona, un teléfono o un altavoz. Un canal admite uno u otro, nunca ambos." },
      q3: { q: "¿Por qué la voz no admite audiencia?", a: "Una audiencia es un conjunto de personas, y la voz va a un altavoz en un lugar. El hub no sabe junto a qué altavoz está una persona, así que nombras los altavoces." },
      q4: { q: "¿Una llamada puede enviar push, voz y notificación persistente?", a: "Sí. Nombra los canales y da a cada uno su propio destino en \"to\", como en el ejemplo 3." },
      q5: { q: "¿Qué pasa si nadie reacciona?", a: "Una política de escalado puede avisar a más personas o canales tras una espera, y una política de recordatorio puede repetir el mensaje. Cualquier confirmación detiene ambas. Que descartar cuente como confirmar es un ajuste de la política de escalado." },
      q6: { q: "¿Cómo mantengo los mensajes en silencio por la noche?", a: "Añade una política de horas de silencio: retener los mensajes hasta el final, enviarlos en silencio o descartarlos. Los mensajes críticos pueden pasar igualmente." },
      q7: { q: "¿Y si alguien no está en casa?", a: "Una política de ausencia envía el mensaje al llegar, mientras siga activo. Una política de alternativa puede enviarlo a otra persona." },
      q8: { q: "¿Puedo recibir un resumen en lugar de muchos mensajes?", a: "Sí. Una política de resumen retiene los mensajes que coinciden y envía un resumen cada N minutos o a una hora fija, con el número y los títulos. Mientras un mensaje espera, no se envía nada por ningún canal, tampoco el aviso del panel." },
      q9: { q: "¿Qué pasa cuando cambio un teléfono?", a: "Edita una vez el perfil de destinatario de la persona. Las audiencias y las políticas no cambian, y ninguna automatización necesita edición." },
      q10: { q: "¿Por qué no recibí una notificación?", a: "La página Envío de prueba muestra a quién se avisaría con una llamada y por qué alguien se omitió, retuvo o descartó. La página Mensajes muestra qué pasó con un mensaje real." },
      q11: { q: "¿Qué pasa tras un reinicio?", a: "Los escalados pendientes conservan su vencimiento. Un paso que venció durante el reinicio se ejecuta una vez si el mensaje sigue activo y sin confirmar. Se eliminan los push de mensajes que ya no existen." },
    },
  },
};

const CSS = `
.hu-help details { border-top: 1px solid var(--divider-color); padding: 4px 0; }
.hu-help summary { cursor: pointer; min-height: 44px; display: flex; align-items: center; font-weight: 500; }
.hu-help summary:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-help p { margin: 4px 0 12px; color: var(--secondary-text-color); }
.hu-help h3 { font-size: 15px; margin: 16px 0 2px; }
`;

export function mount(container, ctx) {
  const t = ctx.t;
  const { el, BASE_CSS } = ctx.ui;
  const root = el("div", { className: "hu-page hu-help" });
  root.append(el("style", { textContent: BASE_CSS + CSS }), el("h1", { textContent: t.title }));
  root.append(el("div", { className: "hint", textContent: t.intro }));

  const examples = el("section", {}, [el("h2", { textContent: t.examples })]);
  for (const example of EXAMPLES) {
    const text = t.ex[example.id];
    const status = el("span", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const copy = el("button", { type: "button", textContent: t.copy });
    copy.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(example.yaml);
        status.textContent = t.copied;
      } catch (err) {
        status.textContent = t.copy_failed;
      }
    });
    examples.append(
      el("h3", { textContent: text.title }),
      el("div", { className: "hint", textContent: text.note }),
      el("pre", { textContent: example.yaml }),
      el("div", { className: "row" }, [copy, status]),
    );
  }
  root.append(examples);

  const questions = el("section", {}, [el("h2", { textContent: t.questions })]);
  for (const id of QUESTION_IDS) {
    const item = t.q[id];
    questions.append(el("details", {}, [el("summary", { textContent: item.q }), el("p", { textContent: item.a })]));
  }
  root.append(questions);
  container.append(root);
  return { setHass() {} };
}
