// Heads Up panel: "How policies work together" (DESIGN §25, D-224, D-235). Pick a kind of policy
// and see what it does and how it meets each of the others. The data follows the interaction matrix
// (docs/dev/policy-redesign/04-interaction-matrix.md); the mockup is docs/dev/mockups/policy-help.html.
// Examples may contain <b> only; everything else is text.

export const KINDS = [{"key": "summarize", "lane": "calm", "icon": "Σ"}, {"key": "quiet", "lane": "calm", "icon": "☾"}, {"key": "presence", "lane": "calm", "icon": "⌂"}, {"key": "through", "lane": "band", "icon": "⇡"}, {"key": "deliver", "lane": "send", "icon": "➤"}, {"key": "escalation", "lane": "send", "icon": "⇧"}, {"key": "reminder", "lane": "send", "icon": "↻"}, {"key": "fallback", "lane": "send", "icon": "⤳"}];

// One entry per pair, written once. va: verdict for the first kind, vb: for the second.
export const PAIRS = {
 "summarize|summarize": {
  "va": "one",
  "vb": "one",
  "en": [
   "If two summaries fit, the message goes into the one that is due next. Never into both.",
   "<b>Digest at 20:00</b> and <b>All info at 18:00</b>: an info message tagged digest is in the 18:00 summary."
  ],
  "de": [
   "Passen zwei Zusammenfassungen, kommt die Meldung in die, die als nächste fällig ist. Nie in beide.",
   "<b>Digest um 20:00</b> und <b>Alle Infos um 18:00</b>: eine Info-Meldung mit Tag digest steht in der Zusammenfassung um 18:00."
  ],
  "fr": [
   "Si deux résumés correspondent, le message va dans celui qui est dû en premier. Jamais dans les deux.",
   "<b>Digest à 20:00</b> et <b>Toutes les infos à 18:00</b> : un message info étiqueté digest est dans le résumé de 18:00."
  ],
  "es": [
   "Si encajan dos resúmenes, el mensaje va al que toca antes. Nunca a los dos.",
   "<b>Digest a las 20:00</b> y <b>Todas las infos a las 18:00</b>: un mensaje info con la etiqueta digest está en el resumen de las 18:00."
  ]
 },
 "summarize|quiet": {
  "va": "first",
  "vb": "after",
  "en": [
   "The summary collects the message first. Quiet hours then decide how the summary itself arrives.",
   "The summary at 23:00 falls into <b>Night quiet</b> (quietly): it arrives without a sound."
  ],
  "de": [
   "Die Zusammenfassung sammelt die Meldung zuerst. Die Ruhezeit entscheidet dann, wie die Zusammenfassung selbst ankommt.",
   "Die Zusammenfassung um 23:00 fällt in die <b>Nachtruhe</b> (leise): sie kommt ohne Ton."
  ],
  "fr": [
   "Le résumé collecte le message d'abord. Les heures calmes décident ensuite comment arrive le résumé lui-même.",
   "Le résumé de 23:00 tombe dans la <b>Nuit calme</b> (discrètement) : il arrive sans son."
  ],
  "es": [
   "El resumen recoge primero el mensaje. Las horas de silencio deciden después cómo llega el propio resumen.",
   "El resumen de las 23:00 cae en la <b>Noche tranquila</b> (en silencio): llega sin sonido."
  ]
 },
 "summarize|presence": {
  "va": "first",
  "vb": "after",
  "en": [
   "The summary collects the message first. Presence then decides about the summary itself.",
   "Anna is out at 20:00. If a Presence policy holds messages while she is away, she gets the summary when she comes home."
  ],
  "de": [
   "Die Zusammenfassung sammelt die Meldung zuerst. Die Anwesenheit entscheidet dann über die Zusammenfassung selbst.",
   "Anna ist um 20:00 unterwegs. Hält eine Anwesenheits-Richtlinie Meldungen zurück, solange sie weg ist, bekommt sie die Zusammenfassung, wenn sie heimkommt."
  ],
  "fr": [
   "Le résumé collecte le message d'abord. La présence décide ensuite du résumé lui-même.",
   "Anna est dehors à 20:00. Si une règle de présence retient les messages pendant son absence, elle reçoit le résumé en rentrant."
  ],
  "es": [
   "El resumen recoge primero el mensaje. La presencia decide después sobre el propio resumen.",
   "Anna está fuera a las 20:00. Si una regla de presencia retiene los mensajes mientras no está, recibe el resumen al volver."
  ]
 },
 "summarize|through": {
  "va": "yields",
  "vb": "wins",
  "en": [
   "A message that an Always-gets-through entry fits is never collected: it goes out at once. If the entry switches on later, waiting messages are taken out and sent. Exception: a summary marked \"Holds these anyway\".",
   "A water leak during the holiday summary: <b>Leaks get through</b> sends it at once instead of at 20:00."
  ],
  "de": [
   "Eine Meldung, auf die ein Eintrag von „Kommt immer durch“ passt, wird nie gesammelt: sie geht sofort raus. Schaltet sich der Eintrag später ein, werden wartende Meldungen herausgeholt und gesendet. Ausnahme: eine Zusammenfassung mit „Hält sie trotzdem“.",
   "Ein Wasserschaden während der Urlaubs-Zusammenfassung: <b>Lecks kommen durch</b> sendet ihn sofort statt um 20:00."
  ],
  "fr": [
   "Un message concerné par une entrée Passe toujours n'est jamais collecté : il part tout de suite. Si l'entrée s'active plus tard, les messages en attente sont sortis et envoyés. Exception : un résumé marqué « Les retient quand même ».",
   "Une fuite d'eau pendant le résumé des vacances : <b>Les fuites passent</b> l'envoie tout de suite au lieu de 20:00."
  ],
  "es": [
   "Un mensaje que encaja con una entrada Siempre pasa nunca se recoge: sale enseguida. Si la entrada se activa más tarde, los mensajes en espera se sacan y se envían. Excepción: un resumen marcado «Los retiene igualmente».",
   "Una fuga de agua durante el resumen de vacaciones: <b>Las fugas pasan</b> la envía enseguida en lugar de a las 20:00."
  ]
 },
 "summarize|deliver": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "A collected message is not sent extra by Deliver. The people Deliver would add get the summary instead.",
   "<b>Push to Ben for digest</b>: Ben gets the 20:00 summary, not a push for each message."
  ],
  "de": [
   "Eine gesammelte Meldung wird nicht zusätzlich zugestellt. Die Leute, die Zustellen ergänzen würde, bekommen stattdessen die Zusammenfassung.",
   "<b>Push an Ben für Digest</b>: Ben bekommt die Zusammenfassung um 20:00, nicht für jede Meldung einen Push."
  ],
  "fr": [
   "Un message collecté n'est pas envoyé en plus par Livrer. Les personnes que Livrer ajouterait reçoivent le résumé à la place.",
   "<b>Push à Ben pour digest</b> : Ben reçoit le résumé de 20:00, pas un push par message."
  ],
  "es": [
   "Un mensaje recogido no se envía además con Entregar. Las personas que Entregar añadiría reciben el resumen en su lugar.",
   "<b>Push a Ben para digest</b>: Ben recibe el resumen de las 20:00, no un push por mensaje."
  ]
 },
 "summarize|escalation": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "A collected message does not escalate: nobody is expected to react before the summary. If it is taken out of the summary, its clock starts then.",
   "A digest message at 14:00 never escalates; it is read at 20:00."
  ],
  "de": [
   "Eine gesammelte Meldung eskaliert nicht: vor der Zusammenfassung muss niemand reagieren. Wird sie herausgeholt, startet ihre Uhr ab dann.",
   "Eine Digest-Meldung um 14:00 eskaliert nie; sie wird um 20:00 gelesen."
  ],
  "fr": [
   "Un message collecté ne s'escalade pas : personne ne doit réagir avant le résumé. S'il est sorti du résumé, son horloge démarre alors.",
   "Un message digest à 14:00 ne s'escalade jamais ; il est lu à 20:00."
  ],
  "es": [
   "Un mensaje recogido no escala: nadie tiene que reaccionar antes del resumen. Si se saca del resumen, su reloj empieza entonces.",
   "Un mensaje digest a las 14:00 nunca escala; se lee a las 20:00."
  ]
 },
 "summarize|reminder": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "A collected message is not reminded. If it is taken out of the summary, reminders start then.",
   "The washing machine message waits for 20:00 without reminders."
  ],
  "de": [
   "An eine gesammelte Meldung wird nicht erinnert. Wird sie herausgeholt, starten die Erinnerungen ab dann.",
   "Die Waschmaschinen-Meldung wartet ohne Erinnerungen auf 20:00."
  ],
  "fr": [
   "Un message collecté ne fait pas l'objet de rappels. S'il est sorti du résumé, les rappels commencent alors.",
   "Le message de la machine à laver attend 20:00 sans rappels."
  ],
  "es": [
   "Un mensaje recogido no tiene recordatorios. Si se saca del resumen, los recordatorios empiezan entonces.",
   "El mensaje de la lavadora espera a las 20:00 sin recordatorios."
  ]
 },
 "summarize|fallback": {
  "va": "first",
  "vb": "after",
  "en": [
   "If the summary itself reaches nobody, the fallback steps in, as for any message.",
   "No phone answers at 20:00: the <b>Kitchen speaker</b> reads out the summary."
  ],
  "de": [
   "Erreicht die Zusammenfassung selbst niemanden, springt der Ersatz ein, wie bei jeder Meldung.",
   "Um 20:00 ist kein Handy erreichbar: der <b>Küchenlautsprecher</b> liest die Zusammenfassung vor."
  ],
  "fr": [
   "Si le résumé lui-même ne joint personne, le repli intervient, comme pour tout message.",
   "Aucun téléphone ne répond à 20:00 : le <b>haut-parleur de la cuisine</b> lit le résumé."
  ],
  "es": [
   "Si el propio resumen no llega a nadie, interviene la alternativa, como con cualquier mensaje.",
   "Ningún teléfono responde a las 20:00: el <b>altavoz de la cocina</b> lee el resumen."
  ]
 },
 "quiet|quiet": {
  "va": "calmer",
  "vb": "calmer",
  "en": [
   "Both act. The stricter one counts: drop, then wait, then quietly. Waiting lasts until the later end.",
   "<b>Weeknights</b> (quietly) and <b>Weekend lie-in</b> (wait until 10:00) on a Saturday at 08:00: the message waits until 10:00."
  ],
  "de": [
   "Beide wirken. Die strengere zählt: verwerfen, dann warten, dann leise. Gewartet wird bis zum späteren Ende.",
   "<b>Werktags-Nachtruhe</b> (leise) und <b>Ausschlafen am Wochenende</b> (warten bis 10:00) am Samstag um 08:00: die Meldung wartet bis 10:00."
  ],
  "fr": [
   "Les deux agissent. La plus stricte compte : abandonner, puis attendre, puis discrètement. L'attente dure jusqu'à la fin la plus tardive.",
   "<b>Nuits de semaine</b> (discrètement) et <b>Grasse matinée du week-end</b> (attendre jusqu'à 10:00) un samedi à 08:00 : le message attend jusqu'à 10:00."
  ],
  "es": [
   "Actúan las dos. Cuenta la más estricta: descartar, luego esperar, luego en silencio. La espera dura hasta el final más tardío.",
   "<b>Noches entre semana</b> (en silencio) y <b>Dormir el fin de semana</b> (esperar hasta las 10:00) un sábado a las 08:00: el mensaje espera hasta las 10:00."
  ]
 },
 "quiet|presence": {
  "va": "calmer",
  "vb": "calmer",
  "en": [
   "Both act and the calmer result counts. A message that waits for the morning is checked by Presence when it is released.",
   "Held until 07:00, then Anna is not home: <b>Shopping list on leaving</b> holds it again until she leaves."
  ],
  "de": [
   "Beide wirken, das ruhigere Ergebnis zählt. Eine Meldung, die auf den Morgen wartet, wird bei der Freigabe von der Anwesenheit geprüft.",
   "Bis 07:00 zurückgehalten, dann ist Anna zu Hause: <b>Einkaufsliste beim Losgehen</b> hält sie weiter, bis sie losgeht."
  ],
  "fr": [
   "Les deux agissent et le résultat le plus calme compte. Un message qui attend le matin est vérifié par la présence quand il est libéré.",
   "Retenu jusqu'à 07:00, puis Anna est à la maison : <b>Liste de courses au départ</b> le retient encore jusqu'à ce qu'elle parte."
  ],
  "es": [
   "Actúan las dos y cuenta el resultado más tranquilo. Un mensaje que espera a la mañana lo comprueba la presencia cuando se libera.",
   "Retenido hasta las 07:00, luego Anna está en casa: <b>Lista de la compra al salir</b> lo retiene hasta que sale."
  ]
 },
 "quiet|through": {
  "va": "yields",
  "vb": "wins",
  "en": [
   "For the people the entry covers, quiet hours do not apply; everyone else stays quiet. Exception: quiet hours marked \"Holds these anyway\".",
   "A leak at 03:00: the Admins' phones ring, Anna's push stays silent."
  ],
  "de": [
   "Für die Leute, für die der Eintrag gilt, zählt die Ruhezeit nicht; alle anderen bleiben leise. Ausnahme: eine Ruhezeit mit „Hält sie trotzdem“.",
   "Ein Leck um 03:00: die Handys der Admins klingeln, Annas Push bleibt still."
  ],
  "fr": [
   "Pour les personnes concernées par l'entrée, les heures calmes ne s'appliquent pas ; tous les autres restent au calme. Exception : des heures calmes marquées « Les retient quand même ».",
   "Une fuite à 03:00 : les téléphones des admins sonnent, le push d'Anna reste silencieux."
  ],
  "es": [
   "Para las personas que afecta la entrada no cuentan las horas de silencio; todos los demás siguen en silencio. Excepción: unas horas de silencio marcadas «Los retiene igualmente».",
   "Una fuga a las 03:00: suenan los teléfonos de los admins, el push de Anna sigue en silencio."
  ]
 },
 "quiet|deliver": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "What Deliver adds goes through the quiet hours too.",
   "<b>Push to the Admins</b> for a warning at 23:00 arrives quietly during <b>Night quiet</b>, unless an Always-gets-through entry covers the Admins."
  ],
  "de": [
   "Was Zustellen ergänzt, geht auch durch die Ruhezeit.",
   "<b>Push an die Admins</b> für eine Warnung um 23:00 kommt während der <b>Nachtruhe</b> leise an, außer ein Eintrag von „Kommt immer durch“ gilt für die Admins."
  ],
  "fr": [
   "Ce que Livrer ajoute passe aussi par les heures calmes.",
   "<b>Push aux admins</b> pour un avertissement à 23:00 arrive discrètement pendant la <b>Nuit calme</b>, sauf si une entrée Passe toujours concerne les admins."
  ],
  "es": [
   "Lo que añade Entregar también pasa por las horas de silencio.",
   "<b>Push a los admins</b> por un aviso a las 23:00 llega en silencio durante la <b>Noche tranquila</b>, salvo que una entrada Siempre pasa afecte a los admins."
  ]
 },
 "quiet|escalation": {
  "va": "warn",
  "vb": "warn",
  "en": [
   "An escalation that quiet hours hold, drop or send quietly is a setup mistake. Heads Up warns on the Policies page as soon as your setup allows it, and again when it happens. Fix it with an Always-gets-through entry for those people.",
   "<b>Nobody looked</b> (30 min, Admins) and <b>Night quiet</b> (wait): the page shows a warning before any message runs into it."
  ],
  "de": [
   "Eine Eskalation, die die Ruhezeit zurückhält, verwirft oder leise sendet, ist ein Einrichtungsfehler. Heads Up warnt auf der Richtlinien-Seite, sobald deine Einrichtung das zulässt, und noch einmal, wenn es passiert. Lösung: ein Eintrag von „Kommt immer durch“ für diese Leute.",
   "<b>Niemand hat geschaut</b> (30 Min., Admins) und <b>Nachtruhe</b> (warten): die Seite warnt, bevor eine Meldung in diese Falle läuft."
  ],
  "fr": [
   "Une escalade que les heures calmes retiennent, abandonnent ou envoient discrètement est une erreur de configuration. Heads Up avertit sur la page des règles dès que votre configuration le permet, puis quand cela arrive. Corrigez avec une entrée Passe toujours pour ces personnes.",
   "<b>Personne n'a regardé</b> (30 min, admins) et <b>Nuit calme</b> (attendre) : la page avertit avant qu'un message tombe dans ce piège."
  ],
  "es": [
   "Un escalado que las horas de silencio retienen, descartan o envían en silencio es un error de configuración. Heads Up avisa en la página de reglas en cuanto tu configuración lo permite, y otra vez cuando ocurre. Corrígelo con una entrada Siempre pasa para esas personas.",
   "<b>Nadie miró</b> (30 min, admins) y <b>Noche tranquila</b> (esperar): la página avisa antes de que un mensaje caiga en esa trampa."
  ]
 },
 "quiet|reminder": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "In a wait or drop window, reminders are skipped, not saved for the morning. In a quiet window they come quietly. People covered by an Always-gets-through entry are still reminded.",
   "<b>Critical repeat</b> every 10 minutes keeps going at night for the Admins, because the entry <b>Critical</b> covers them."
  ],
  "de": [
   "In einem Warte- oder Verwerfen-Fenster fallen Erinnerungen aus, sie werden nicht für morgens aufgehoben. In einem Leise-Fenster kommen sie leise. Wer von „Kommt immer durch“ erfasst ist, wird weiter erinnert.",
   "<b>Kritisch wiederholen</b> alle 10 Minuten läuft nachts für die Admins weiter, weil der Eintrag <b>Kritisch</b> für sie gilt."
  ],
  "fr": [
   "Dans une plage attendre ou abandonner, les rappels sont ignorés, pas gardés pour le matin. Dans une plage discrète, ils arrivent discrètement. Les personnes concernées par une entrée Passe toujours sont toujours rappelées.",
   "<b>Répéter le critique</b> toutes les 10 minutes continue la nuit pour les admins, car l'entrée <b>Critique</b> les concerne."
  ],
  "es": [
   "En una franja de esperar o descartar, los recordatorios se omiten, no se guardan para la mañana. En una franja en silencio llegan en silencio. A las personas que afecta una entrada Siempre pasa se les sigue recordando.",
   "<b>Repetir crítico</b> cada 10 minutos sigue de noche para los admins, porque la entrada <b>Crítico</b> los afecta."
  ]
 },
 "quiet|fallback": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "A fallback is never louder than its message: quiet hours apply to it. An Always-gets-through entry that covers the speaker lets it speak at night.",
   "An info message nobody received at 03:00: the <b>Kitchen speaker</b> stays silent."
  ],
  "de": [
   "Ein Ersatz ist nie lauter als seine Meldung: die Ruhezeit gilt auch für ihn. Ein Eintrag von „Kommt immer durch“, der den Lautsprecher erfasst, lässt ihn nachts sprechen.",
   "Eine Info-Meldung, die um 03:00 niemand bekommen hat: der <b>Küchenlautsprecher</b> bleibt still."
  ],
  "fr": [
   "Un repli n'est jamais plus fort que son message : les heures calmes s'y appliquent. Une entrée Passe toujours qui concerne le haut-parleur le laisse parler la nuit.",
   "Un message info que personne n'a reçu à 03:00 : le <b>haut-parleur de la cuisine</b> reste silencieux."
  ],
  "es": [
   "Una alternativa nunca suena más que su mensaje: le aplican las horas de silencio. Una entrada Siempre pasa que afecta al altavoz le deja hablar de noche.",
   "Un mensaje info que nadie recibió a las 03:00: el <b>altavoz de la cocina</b> sigue en silencio."
  ]
 },
 "presence|presence": {
  "va": "both",
  "vb": "both",
  "en": [
   "Both act. If they contradict each other (one holds while home, one while away), the message never arrives. The Policies page and the form warn you.",
   "<b>Shopping list on leaving</b> and <b>Hold everything while away</b>: a warning appears when you save the second one."
  ],
  "de": [
   "Beide wirken. Widersprechen sie sich (eine hält zu Hause zurück, eine unterwegs), kommt die Meldung nie an. Die Richtlinien-Seite und das Formular warnen dich.",
   "<b>Einkaufsliste beim Losgehen</b> und <b>Unterwegs alles zurückhalten</b>: beim Speichern der zweiten erscheint eine Warnung."
  ],
  "fr": [
   "Les deux agissent. Si elles se contredisent (l'une retient à la maison, l'autre en absence), le message n'arrive jamais. La page des règles et le formulaire vous avertissent.",
   "<b>Liste de courses au départ</b> et <b>Tout retenir en absence</b> : un avertissement apparaît à l'enregistrement de la deuxième."
  ],
  "es": [
   "Actúan las dos. Si se contradicen (una retiene en casa, otra fuera), el mensaje nunca llega. La página de reglas y el formulario te avisan.",
   "<b>Lista de la compra al salir</b> y <b>Retener todo fuera</b>: aparece un aviso al guardar la segunda."
  ]
 },
 "presence|through": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "Always gets through never overrides Presence: nothing is spoken into an empty house.",
   "A critical message, nobody home, <b>Speak only when someone is home</b>: nothing is spoken; phones still get it."
  ],
  "de": [
   "„Kommt immer durch“ übergeht nie die Anwesenheit: in ein leeres Haus wird nichts gesprochen.",
   "Eine kritische Meldung, niemand zu Hause, <b>Nur sprechen, wenn jemand da ist</b>: es wird nichts gesagt; die Handys bekommen sie trotzdem."
  ],
  "fr": [
   "Passe toujours ne contourne jamais la présence : rien n'est dit dans une maison vide.",
   "Un message critique, personne à la maison, <b>Parler seulement si quelqu'un est là</b> : rien n'est dit ; les téléphones le reçoivent quand même."
  ],
  "es": [
   "Siempre pasa nunca se salta la presencia: no se dice nada en una casa vacía.",
   "Un mensaje crítico, nadie en casa, <b>Hablar solo si hay alguien</b>: no se dice nada; los teléfonos lo reciben igualmente."
  ]
 },
 "presence|deliver": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "What Deliver adds is checked by Presence too.",
   "<b>Speak on the Kitchen speaker</b> for the doorbell stays silent when nobody is home."
  ],
  "de": [
   "Was Zustellen ergänzt, prüft die Anwesenheit auch.",
   "<b>Auf dem Küchenlautsprecher sprechen</b> für die Türklingel bleibt still, wenn niemand zu Hause ist."
  ],
  "fr": [
   "Ce que Livrer ajoute est aussi vérifié par la présence.",
   "<b>Parler sur le haut-parleur de la cuisine</b> pour la sonnette reste silencieux quand personne n'est là."
  ],
  "es": [
   "Lo que añade Entregar también lo comprueba la presencia.",
   "<b>Hablar en el altavoz de la cocina</b> por el timbre sigue en silencio cuando no hay nadie."
  ]
 },
 "presence|escalation": {
  "va": "warn",
  "vb": "warn",
  "en": [
   "If Presence holds every person an escalation goes to, the escalation reaches nobody. Heads Up warns on the Policies page and shows a notice when it happens. No fallback steps in.",
   "All Admins are away and their pushes are held: the escalation waits, and Overview shows the notice."
  ],
  "de": [
   "Hält die Anwesenheit jede Person zurück, an die eine Eskalation geht, erreicht die Eskalation niemanden. Heads Up warnt auf der Richtlinien-Seite und zeigt einen Hinweis, wenn es passiert. Ein Ersatz springt nicht ein.",
   "Alle Admins sind weg und ihre Pushes werden zurückgehalten: die Eskalation wartet, und die Übersicht zeigt den Hinweis."
  ],
  "fr": [
   "Si la présence retient chaque personne visée par une escalade, l'escalade ne joint personne. Heads Up avertit sur la page des règles et affiche un avis quand cela arrive. Aucun repli n'intervient.",
   "Tous les admins sont absents et leurs push sont retenus : l'escalade attend, et la vue d'ensemble affiche l'avis."
  ],
  "es": [
   "Si la presencia retiene a cada persona a la que va un escalado, el escalado no llega a nadie. Heads Up avisa en la página de reglas y muestra un aviso cuando ocurre. No interviene ninguna alternativa.",
   "Todos los admins están fuera y sus push se retienen: el escalado espera y la vista general muestra el aviso."
  ]
 },
 "presence|reminder": {
  "va": "yields",
  "vb": "wins",
  "en": [
   "Reminders are not checked by Presence: someone who already got the message is reminded wherever they are.",
   "Ben got the warning at home and left: the reminder still reaches his phone."
  ],
  "de": [
   "Erinnerungen prüft die Anwesenheit nicht: wer die Meldung schon bekommen hat, wird erinnert, egal wo er ist.",
   "Ben hat die Warnung zu Hause bekommen und ist losgegangen: die Erinnerung erreicht sein Handy trotzdem."
  ],
  "fr": [
   "Les rappels ne sont pas vérifiés par la présence : qui a déjà reçu le message est rappelé où qu'il soit.",
   "Ben a reçu l'avertissement à la maison puis est parti : le rappel atteint quand même son téléphone."
  ],
  "es": [
   "La presencia no comprueba los recordatorios: a quien ya recibió el mensaje se le recuerda esté donde esté.",
   "Ben recibió el aviso en casa y se fue: el recordatorio llega igualmente a su teléfono."
  ]
 },
 "presence|fallback": {
  "va": "wins",
  "vb": "yields",
  "en": [
   "The fallback is checked by Presence too: in an empty house the speaker stays silent.",
   "Nobody reached, nobody home: the <b>Kitchen speaker</b> says nothing."
  ],
  "de": [
   "Auch der Ersatz wird von der Anwesenheit geprüft: in einem leeren Haus bleibt der Lautsprecher still.",
   "Niemand erreicht, niemand zu Hause: der <b>Küchenlautsprecher</b> sagt nichts."
  ],
  "fr": [
   "Le repli est aussi vérifié par la présence : dans une maison vide, le haut-parleur reste silencieux.",
   "Personne joint, personne à la maison : le <b>haut-parleur de la cuisine</b> ne dit rien."
  ],
  "es": [
   "La presencia también comprueba la alternativa: en una casa vacía, el altavoz sigue en silencio.",
   "Nadie localizado, nadie en casa: el <b>altavoz de la cocina</b> no dice nada."
  ]
 },
 "through|through": {
  "va": "add",
  "vb": "add",
  "en": [
   "Both act: each entry lets its own people through.",
   "<b>Alarms wake the Admins</b> and <b>Alarms wake Anna</b>: at night the Admins and Anna are woken, everyone else stays quiet."
  ],
  "de": [
   "Beide wirken: jeder Eintrag lässt seine eigenen Leute durch.",
   "<b>Alarme wecken die Admins</b> und <b>Alarme wecken Anna</b>: nachts werden die Admins und Anna geweckt, alle anderen bleiben leise."
  ],
  "fr": [
   "Les deux agissent : chaque entrée fait passer ses propres personnes.",
   "<b>Les alarmes réveillent les admins</b> et <b>Les alarmes réveillent Anna</b> : la nuit, les admins et Anna sont réveillés, les autres restent au calme."
  ],
  "es": [
   "Actúan las dos: cada entrada deja pasar a sus propias personas.",
   "<b>Las alarmas despiertan a los admins</b> y <b>Las alarmas despiertan a Anna</b>: de noche se despierta a los admins y a Anna, los demás siguen en silencio."
  ]
 },
 "through|deliver": {
  "va": "add",
  "vb": "add",
  "en": [
   "Different jobs: the entry only allows waking, Deliver does the sending. Together they wake the Admins for leaks.",
   "<b>Alarms wake the Admins</b> plus <b>Alarms to the Admins</b> (push): a leak at 03:00 rings on the Admins' phones."
  ],
  "de": [
   "Verschiedene Aufgaben: der Eintrag erlaubt nur das Wecken, Zustellen sendet. Zusammen wecken sie die Admins bei Lecks.",
   "<b>Alarme wecken die Admins</b> plus <b>Alarme an die Admins</b> (Push): ein Leck um 03:00 klingelt auf den Handys der Admins."
  ],
  "fr": [
   "Des rôles différents : l'entrée autorise seulement le réveil, Livrer fait l'envoi. Ensemble, elles réveillent les admins pour les fuites.",
   "<b>Les alarmes réveillent les admins</b> plus <b>Alarmes aux admins</b> (push) : une fuite à 03:00 sonne sur les téléphones des admins."
  ],
  "es": [
   "Tareas distintas: la entrada solo permite despertar, Entregar hace el envío. Juntas despiertan a los admins por las fugas.",
   "<b>Las alarmas despiertan a los admins</b> más <b>Alarmas a los admins</b> (push): una fuga a las 03:00 suena en los teléfonos de los admins."
  ]
 },
 "through|escalation": {
  "va": "both",
  "vb": "both",
  "en": [
   "An escalation for messages the entry fits comes through the quiet hours for the people the entry covers.",
   "<b>Nobody looked</b> for an alarm at 02:00 rings for the Admins."
  ],
  "de": [
   "Eine Eskalation für Meldungen, auf die der Eintrag passt, kommt für die erfassten Leute durch die Ruhezeit.",
   "<b>Niemand hat geschaut</b> für einen Alarm um 02:00 klingelt bei den Admins."
  ],
  "fr": [
   "Une escalade pour les messages concernés par l'entrée passe les heures calmes pour les personnes concernées.",
   "<b>Personne n'a regardé</b> pour une alarme à 02:00 sonne chez les admins."
  ],
  "es": [
   "Un escalado de los mensajes que encaja la entrada pasa las horas de silencio para las personas afectadas.",
   "<b>Nadie miró</b> por una alarma a las 02:00 suena a los admins."
  ]
 },
 "through|reminder": {
  "va": "both",
  "vb": "both",
  "en": [
   "Reminders come through the quiet hours for the people the entry covers.",
   "<b>Critical repeat</b> every 10 minutes keeps ringing at night until someone acknowledges."
  ],
  "de": [
   "Erinnerungen kommen für die erfassten Leute durch die Ruhezeit.",
   "<b>Kritisch wiederholen</b> klingelt nachts alle 10 Minuten, bis jemand bestätigt."
  ],
  "fr": [
   "Les rappels passent les heures calmes pour les personnes concernées par l'entrée.",
   "<b>Répéter le critique</b> sonne la nuit toutes les 10 minutes jusqu'à une confirmation."
  ],
  "es": [
   "Los recordatorios pasan las horas de silencio para las personas que afecta la entrada.",
   "<b>Repetir crítico</b> suena de noche cada 10 minutos hasta que alguien confirma."
  ]
 },
 "through|fallback": {
  "va": "both",
  "vb": "both",
  "en": [
   "If the entry covers the fallback speaker, or everyone the message reaches, the fallback speaks even at night.",
   "A critical message nobody received at 03:00: the entry <b>Critical</b> lets the <b>Kitchen speaker</b> say it."
  ],
  "de": [
   "Erfasst der Eintrag den Ersatz-Lautsprecher, oder alle, die die Meldung erreicht, spricht der Ersatz auch nachts.",
   "Eine kritische Meldung, die um 03:00 niemand bekommen hat: der Eintrag <b>Kritisch</b> lässt den <b>Küchenlautsprecher</b> sprechen."
  ],
  "fr": [
   "Si l'entrée concerne le haut-parleur du repli, ou tous ceux que le message atteint, le repli parle même la nuit.",
   "Un message critique que personne n'a reçu à 03:00 : l'entrée <b>Critique</b> laisse le <b>haut-parleur de la cuisine</b> l'annoncer."
  ],
  "es": [
   "Si la entrada afecta al altavoz de la alternativa, o a todos a quienes llega el mensaje, la alternativa habla incluso de noche.",
   "Un mensaje crítico que nadie recibió a las 03:00: la entrada <b>Crítico</b> deja que el <b>altavoz de la cocina</b> lo diga."
  ]
 },
 "deliver|deliver": {
  "va": "add",
  "vb": "add",
  "en": [
   "Both send. Each person gets the message once per channel.",
   "<b>Push to the Admins</b> and <b>Push to Chris</b>: Chris, who is an Admin, gets one push."
  ],
  "de": [
   "Beide senden. Jede Person bekommt die Meldung einmal pro Kanal.",
   "<b>Push an die Admins</b> und <b>Push an Chris</b>: Chris, selbst Admin, bekommt einen Push."
  ],
  "fr": [
   "Les deux envoient. Chaque personne reçoit le message une fois par canal.",
   "<b>Push aux admins</b> et <b>Push à Chris</b> : Chris, qui est admin, reçoit un push."
  ],
  "es": [
   "Las dos envían. Cada persona recibe el mensaje una vez por canal.",
   "<b>Push a los admins</b> y <b>Push a Chris</b>: Chris, que es admin, recibe un push."
  ]
 },
 "deliver|escalation": {
  "va": "both",
  "vb": "both",
  "en": [
   "Both act: Deliver sends at once, the escalation later if nobody reacted. It also sends again to people who already have the message.",
   "The Admins get a push at once and, 15 minutes later without an acknowledgement, a second one from the escalation."
  ],
  "de": [
   "Beide wirken: Zustellen sendet sofort, die Eskalation später, wenn niemand reagiert hat. Sie sendet auch erneut an Leute, die die Meldung schon haben.",
   "Die Admins bekommen sofort einen Push und, 15 Minuten später ohne Bestätigung, einen zweiten von der Eskalation."
  ],
  "fr": [
   "Les deux agissent : Livrer envoie tout de suite, l'escalade plus tard si personne n'a réagi. Elle envoie aussi à nouveau aux personnes qui ont déjà le message.",
   "Les admins reçoivent un push tout de suite et, 15 minutes plus tard sans confirmation, un deuxième de l'escalade."
  ],
  "es": [
   "Actúan las dos: Entregar envía enseguida, el escalado más tarde si nadie reaccionó. También vuelve a enviar a quien ya tiene el mensaje.",
   "Los admins reciben un push enseguida y, 15 minutos después sin confirmación, un segundo del escalado."
  ]
 },
 "deliver|reminder": {
  "va": "both",
  "vb": "both",
  "en": [
   "Reminders repeat what Deliver sent too.",
   "Ben got the message from <b>Push to Ben</b>: he is reminded every 30 minutes like everyone else."
  ],
  "de": [
   "Erinnerungen wiederholen auch, was Zustellen gesendet hat.",
   "Ben hat die Meldung über <b>Push an Ben</b> bekommen: er wird alle 30 Minuten erinnert wie alle anderen."
  ],
  "fr": [
   "Les rappels répètent aussi ce que Livrer a envoyé.",
   "Ben a reçu le message par <b>Push à Ben</b> : il est rappelé toutes les 30 minutes comme les autres."
  ],
  "es": [
   "Los recordatorios también repiten lo que envió Entregar.",
   "Ben recibió el mensaje por <b>Push a Ben</b>: se le recuerda cada 30 minutos como a los demás."
  ]
 },
 "deliver|fallback": {
  "va": "first",
  "vb": "after",
  "en": [
   "The fallback only steps in if neither the automation nor Deliver reached anyone.",
   "Anna's phone is off, but <b>Push to the Admins</b> reached the Admins: the Kitchen speaker stays silent."
  ],
  "de": [
   "Der Ersatz springt nur ein, wenn weder die Automation noch Zustellen jemanden erreicht hat.",
   "Annas Handy ist aus, aber <b>Push an die Admins</b> hat die Admins erreicht: der Küchenlautsprecher bleibt still."
  ],
  "fr": [
   "Le repli n'intervient que si ni l'automatisation ni Livrer n'a joint quelqu'un.",
   "Le téléphone d'Anna est éteint, mais <b>Push aux admins</b> a joint les admins : le haut-parleur de la cuisine reste silencieux."
  ],
  "es": [
   "La alternativa solo interviene si ni la automatización ni Entregar llegaron a nadie.",
   "El teléfono de Anna está apagado, pero <b>Push a los admins</b> llegó a los admins: el altavoz de la cocina sigue en silencio."
  ]
 },
 "escalation|escalation": {
  "va": "add",
  "vb": "add",
  "en": [
   "Each fires once, at its own time.",
   "Admins after 5 minutes, everyone after 15 minutes: both steps happen if nobody acknowledges."
  ],
  "de": [
   "Jede geht einmal los, zu ihrer eigenen Zeit.",
   "Admins nach 5 Minuten, alle nach 15 Minuten: beide Stufen passieren, wenn niemand bestätigt."
  ],
  "fr": [
   "Chacune part une fois, à son propre moment.",
   "Admins après 5 minutes, tout le monde après 15 minutes : les deux étapes ont lieu si personne ne confirme."
  ],
  "es": [
   "Cada una salta una vez, en su propio momento.",
   "Admins tras 5 minutos, todos tras 15 minutos: los dos pasos ocurren si nadie confirma."
  ]
 },
 "escalation|reminder": {
  "va": "both",
  "vb": "both",
  "en": [
   "Both act. After an escalation, reminders repeat its messages too. An acknowledgement on any device stops both.",
   "The escalation added Chris; from then on Chris is reminded as well."
  ],
  "de": [
   "Beide wirken. Nach einer Eskalation wiederholen Erinnerungen auch ihre Meldungen. Eine Bestätigung auf irgendeinem Gerät stoppt beide.",
   "Die Eskalation hat Chris dazugenommen; ab dann wird auch Chris erinnert."
  ],
  "fr": [
   "Les deux agissent. Après une escalade, les rappels répètent aussi ses messages. Une confirmation sur n'importe quel appareil arrête les deux.",
   "L'escalade a ajouté Chris ; dès lors Chris est aussi rappelé."
  ],
  "es": [
   "Actúan los dos. Tras un escalado, los recordatorios repiten también sus mensajes. Una confirmación en cualquier dispositivo detiene ambos.",
   "El escalado añadió a Chris; desde entonces también se le recuerda a Chris."
  ]
 },
 "escalation|fallback": {
  "va": "warn",
  "vb": "warn",
  "en": [
   "An escalation that reaches nobody does not trigger the fallback. Heads Up shows a notice instead, and the Policies page warns in advance.",
   "The escalation's push fails on every phone: Overview shows a notice; the speaker stays silent."
  ],
  "de": [
   "Eine Eskalation, die niemanden erreicht, löst keinen Ersatz aus. Heads Up zeigt stattdessen einen Hinweis, und die Richtlinien-Seite warnt vorher.",
   "Der Push der Eskalation schlägt auf allen Handys fehl: die Übersicht zeigt einen Hinweis; der Lautsprecher bleibt still."
  ],
  "fr": [
   "Une escalade qui ne joint personne ne déclenche pas le repli. Heads Up affiche un avis à la place, et la page des règles avertit à l'avance.",
   "Le push de l'escalade échoue sur tous les téléphones : la vue d'ensemble affiche un avis ; le haut-parleur reste silencieux."
  ],
  "es": [
   "Un escalado que no llega a nadie no activa la alternativa. Heads Up muestra un aviso en su lugar, y la página de reglas avisa antes.",
   "El push del escalado falla en todos los teléfonos: la vista general muestra un aviso; el altavoz sigue en silencio."
  ]
 },
 "reminder|reminder": {
  "va": "one",
  "vb": "one",
  "en": [
   "One rhythm per channel: the fastest one in force wins, and each reminder keeps its own count. \"Runs alongside\" keeps both rhythms.",
   "<b>Every 15 min while the window is open</b> and <b>Every hour</b>: while the window is open, every 15 minutes; afterwards hourly, with the hourly count untouched."
  ],
  "de": [
   "Ein Rhythmus pro Kanal: der schnellste, der gerade gilt, gewinnt, und jede Erinnerung zählt für sich. „Läuft neben anderen Erinnerungen“ behält beide Rhythmen.",
   "<b>Alle 15 Min., solange das Fenster offen ist</b> und <b>Jede Stunde</b>: solange das Fenster offen ist, alle 15 Minuten; danach stündlich, die stündliche Zählung bleibt unberührt."
  ],
  "fr": [
   "Un rythme par canal : le plus rapide en vigueur l'emporte, et chaque rappel garde son propre compte. « Fonctionne à côté des autres rappels » garde les deux rythmes.",
   "<b>Toutes les 15 min tant que la fenêtre est ouverte</b> et <b>Toutes les heures</b> : fenêtre ouverte, toutes les 15 minutes ; ensuite toutes les heures, le compte horaire intact."
  ],
  "es": [
   "Un ritmo por canal: se impone el más rápido vigente, y cada recordatorio lleva su propio recuento. «Funciona junto a otros recordatorios» mantiene los dos ritmos.",
   "<b>Cada 15 min mientras la ventana está abierta</b> y <b>Cada hora</b>: con la ventana abierta, cada 15 minutos; después cada hora, con el recuento horario intacto."
  ]
 },
 "reminder|fallback": {
  "va": "both",
  "vb": "both",
  "en": [
   "Reminders repeat the fallback's announcement too, until someone acknowledges.",
   "The Kitchen speaker said it as the fallback; every 30 minutes it says it again."
  ],
  "de": [
   "Erinnerungen wiederholen auch die Ansage des Ersatzes, bis jemand bestätigt.",
   "Der Küchenlautsprecher hat es als Ersatz gesagt; alle 30 Minuten sagt er es erneut."
  ],
  "fr": [
   "Les rappels répètent aussi l'annonce du repli, jusqu'à une confirmation.",
   "Le haut-parleur de la cuisine l'a annoncé comme repli ; toutes les 30 minutes il l'annonce à nouveau."
  ],
  "es": [
   "Los recordatorios repiten también el aviso de la alternativa, hasta que alguien confirma.",
   "El altavoz de la cocina lo dijo como alternativa; cada 30 minutos lo vuelve a decir."
  ]
 },
 "fallback|fallback": {
  "va": "add",
  "vb": "add",
  "en": [
   "Each fallback that fits steps in once.",
   "<b>Say it in the house</b> and <b>Mail to Chris</b>: both happen when nobody was reached."
  ],
  "de": [
   "Jeder passende Ersatz springt einmal ein.",
   "<b>Im Haus ansagen</b> und <b>Mail an Chris</b>: beides passiert, wenn niemand erreicht wurde."
  ],
  "fr": [
   "Chaque repli qui correspond intervient une fois.",
   "<b>L'annoncer dans la maison</b> et <b>Courriel à Chris</b> : les deux ont lieu quand personne n'a été joint."
  ],
  "es": [
   "Cada alternativa que encaja interviene una vez.",
   "<b>Decirlo en casa</b> y <b>Correo a Chris</b>: ocurren las dos cuando no se localizó a nadie."
  ]
 }
};

export const STRINGS = {
 "en": {
  "title": "How policies work together",
  "lead": "Pick a policy to see what it does and what happens when it meets each of the others.",
  "lanes": {
   "calm": "Keep it calm",
   "band": "Always gets through",
   "send": "Make sure it arrives"
  },
  "names": {
   "summarize": "Summarize",
   "quiet": "Quiet hours",
   "presence": "Presence",
   "through": "Get through",
   "deliver": "Deliver",
   "escalation": "Escalation",
   "reminder": "Reminder",
   "fallback": "Fallback"
  },
  "about": {
   "summarize": [
    "Collects messages and sends one summary at a time of day or every few minutes.",
    "<b>Evening summary</b>: messages tagged digest arrive together at 20:00."
   ],
   "quiet": [
    "During set hours, messages wait, arrive quietly or are dropped.",
    "<b>Night quiet</b>: info messages between 22:00 and 07:00 arrive without a sound."
   ],
   "presence": [
    "Sends depending on where people are: held until someone arrives or leaves, or dropped.",
    "<b>Speak only when someone is home</b>: no doorbell announcement in an empty house."
   ],
   "through": [
    "Says which messages may wake whom, despite quiet hours and summaries. It sends nothing itself.",
    "<b>Alarms wake the Admins</b>: a leak at night rings for the Admins only."
   ],
   "deliver": [
    "Also sends the message to more people or on more channels, at once.",
    "<b>Alarms to the Admins</b>: every alarm also goes to the Admins' phones."
   ],
   "escalation": [
    "If nobody acknowledges in time, it notifies more people or on more channels, once.",
    "<b>Nobody looked</b>: after 15 minutes without an acknowledgement, everyone gets it."
   ],
   "reminder": [
    "Repeats the message until someone acknowledges, at most a set number of times.",
    "<b>Warning reminder</b>: every 30 minutes, at most 3 times."
   ],
   "fallback": [
    "Steps in when nobody could be reached, for example by a speaker.",
    "<b>Say it in the house</b>: no phone answered, so the Kitchen speaker says it."
   ]
  },
  "what": "What it does",
  "example": "Example",
  "together": "Together with …",
  "all": "All",
  "conflicts": "Only conflicts",
  "show": "Show example",
  "hide": "Hide example",
  "self": "another",
  "verdicts": {
   "wins": "Wins",
   "yields": "Gives way",
   "both": "Both act",
   "add": "Add up",
   "first": "Acts first",
   "after": "Acts after",
   "one": "Only one counts",
   "calmer": "The calmer counts",
   "warn": "Warning"
  },
  "rulesTitle": "Three rules behind everything",
  "rules": [
   "Every policy that fits a message acts. When calming policies disagree, the calmer result counts.",
   "Escalations and reminders count from when the message was created. Each reminder keeps its own count.",
   "Always gets through lets messages past quiet hours and summaries for the people it covers. Presence is never passed."
  ],
  "notes": [
   "Switching a policy on only affects messages that arrive afterwards. \"Only if\" is checked at every step.",
   "When an automation turns automatic policies off, none of these act for that message."
  ],
  "lang": "en"
 },
 "de": {
  "title": "Wie Richtlinien zusammenwirken",
  "lead": "Wähle eine Richtlinie: du siehst, was sie tut und was passiert, wenn sie auf jede andere trifft.",
  "lanes": {
   "calm": "Für Ruhe sorgen",
   "band": "Kommt immer durch",
   "send": "Damit es ankommt"
  },
  "names": {
   "summarize": "Zusammenfassen",
   "quiet": "Ruhezeit",
   "presence": "Anwesenheit",
   "through": "Kommt durch",
   "deliver": "Zustellen",
   "escalation": "Eskalation",
   "reminder": "Erinnerung",
   "fallback": "Ersatz"
  },
  "about": {
   "summarize": [
    "Sammelt Meldungen und schickt eine Zusammenfassung zu einer Uhrzeit oder alle paar Minuten.",
    "<b>Abendzusammenfassung</b>: Meldungen mit Tag digest kommen gesammelt um 20:00."
   ],
   "quiet": [
    "In festgelegten Zeiten warten Meldungen, kommen leise oder werden verworfen.",
    "<b>Nachtruhe</b>: Info-Meldungen zwischen 22:00 und 07:00 kommen ohne Ton."
   ],
   "presence": [
    "Sendet abhängig davon, wo Leute sind: zurückgehalten, bis jemand ankommt oder geht, oder verworfen.",
    "<b>Nur sprechen, wenn jemand da ist</b>: keine Türklingel-Ansage in einem leeren Haus."
   ],
   "through": [
    "Legt fest, welche Meldungen wen trotz Ruhezeit und Zusammenfassung wecken dürfen. Sendet selbst nichts.",
    "<b>Alarme wecken die Admins</b>: ein Leck nachts klingelt nur bei den Admins."
   ],
   "deliver": [
    "Schickt die Meldung zusätzlich an weitere Leute oder auf weiteren Kanälen, sofort.",
    "<b>Alarme an die Admins</b>: jeder Alarm geht auch auf die Handys der Admins."
   ],
   "escalation": [
    "Bestätigt niemand rechtzeitig, benachrichtigt sie einmal weitere Leute oder Kanäle.",
    "<b>Niemand hat geschaut</b>: nach 15 Minuten ohne Bestätigung bekommen es alle."
   ],
   "reminder": [
    "Wiederholt die Meldung, bis jemand bestätigt, höchstens so oft wie eingestellt.",
    "<b>Warnungs-Erinnerung</b>: alle 30 Minuten, höchstens 3-mal."
   ],
   "fallback": [
    "Springt ein, wenn niemand erreicht werden konnte, zum Beispiel über einen Lautsprecher.",
    "<b>Im Haus ansagen</b>: kein Handy hat reagiert, also sagt es der Küchenlautsprecher."
   ]
  },
  "what": "Was sie tut",
  "example": "Beispiel",
  "together": "Zusammen mit …",
  "all": "Alle",
  "conflicts": "Nur Konflikte",
  "show": "Beispiel zeigen",
  "hide": "Beispiel ausblenden",
  "self": "eine zweite",
  "verdicts": {
   "wins": "Setzt sich durch",
   "yields": "Gibt nach",
   "both": "Beide wirken",
   "add": "Ergänzen sich",
   "first": "Wirkt zuerst",
   "after": "Wirkt danach",
   "one": "Nur eine zählt",
   "calmer": "Die ruhigere zählt",
   "warn": "Warnung"
  },
  "rulesTitle": "Drei Regeln hinter allem",
  "rules": [
   "Jede Richtlinie, die auf eine Meldung passt, wirkt. Sind sich beruhigende Richtlinien uneinig, zählt das ruhigere Ergebnis.",
   "Eskalationen und Erinnerungen zählen ab dem Erstellen der Meldung. Jede Erinnerung zählt für sich.",
   "„Kommt immer durch“ lässt Meldungen für die erfassten Leute an Ruhezeit und Zusammenfassung vorbei. Die Anwesenheit wird nie übergangen."
  ],
  "notes": [
   "Eine eingeschaltete Richtlinie wirkt nur auf Meldungen, die danach kommen. „Nur wenn“ wird bei jedem Schritt geprüft.",
   "Schaltet eine Automation die automatischen Richtlinien ab, wirkt für diese Meldung keine davon."
  ],
  "lang": "de"
 },
 "fr": {
  "title": "Comment les règles agissent ensemble",
  "lead": "Choisissez une règle : vous voyez ce qu'elle fait et ce qui se passe quand elle rencontre chacune des autres.",
  "lanes": {
   "calm": "Garder le calme",
   "band": "Passe toujours",
   "send": "S'assurer qu'il arrive"
  },
  "names": {
   "summarize": "Résumer",
   "quiet": "Heures calmes",
   "presence": "Présence",
   "through": "Laisser passer",
   "deliver": "Livrer",
   "escalation": "Escalade",
   "reminder": "Rappel",
   "fallback": "Repli"
  },
  "about": {
   "summarize": [
    "Collecte les messages et envoie un résumé à une heure donnée ou toutes les quelques minutes.",
    "<b>Résumé du soir</b> : les messages étiquetés digest arrivent ensemble à 20:00."
   ],
   "quiet": [
    "Pendant des heures fixées, les messages attendent, arrivent discrètement ou sont abandonnés.",
    "<b>Nuit calme</b> : les messages info entre 22:00 et 07:00 arrivent sans son."
   ],
   "presence": [
    "Envoie selon l'endroit où sont les gens : retenu jusqu'à une arrivée ou un départ, ou abandonné.",
    "<b>Parler seulement si quelqu'un est là</b> : pas d'annonce de sonnette dans une maison vide."
   ],
   "through": [
    "Dit quels messages peuvent réveiller qui, malgré les heures calmes et les résumés. N'envoie rien lui-même.",
    "<b>Les alarmes réveillent les admins</b> : une fuite la nuit ne sonne que chez les admins."
   ],
   "deliver": [
    "Envoie aussi le message à d'autres personnes ou sur d'autres canaux, tout de suite.",
    "<b>Alarmes aux admins</b> : chaque alarme va aussi sur les téléphones des admins."
   ],
   "escalation": [
    "Si personne ne confirme à temps, prévient d'autres personnes ou d'autres canaux, une fois.",
    "<b>Personne n'a regardé</b> : après 15 minutes sans confirmation, tout le monde le reçoit."
   ],
   "reminder": [
    "Répète le message jusqu'à une confirmation, au plus un nombre de fois fixé.",
    "<b>Rappel d'avertissement</b> : toutes les 30 minutes, au plus 3 fois."
   ],
   "fallback": [
    "Intervient quand personne n'a pu être joint, par exemple par un haut-parleur.",
    "<b>L'annoncer dans la maison</b> : aucun téléphone n'a répondu, le haut-parleur de la cuisine l'annonce."
   ]
  },
  "what": "Ce qu'elle fait",
  "example": "Exemple",
  "together": "Avec …",
  "all": "Toutes",
  "conflicts": "Seulement les conflits",
  "show": "Voir l'exemple",
  "hide": "Masquer l'exemple",
  "self": "une deuxième",
  "verdicts": {
   "wins": "L'emporte",
   "yields": "Cède",
   "both": "Les deux agissent",
   "add": "S'additionnent",
   "first": "Agit d'abord",
   "after": "Agit ensuite",
   "one": "Une seule compte",
   "calmer": "La plus calme compte",
   "warn": "Avertissement"
  },
  "rulesTitle": "Trois règles derrière tout",
  "rules": [
   "Chaque règle qui correspond à un message agit. Quand des règles qui calment divergent, le résultat le plus calme compte.",
   "Les escalades et les rappels comptent depuis la création du message. Chaque rappel compte pour lui-même.",
   "Passe toujours fait passer les messages au-delà des heures calmes et des résumés pour les personnes concernées. La présence n'est jamais contournée."
  ],
  "notes": [
   "Une règle activée n'agit que sur les messages qui arrivent ensuite. « Seulement si » est vérifié à chaque étape.",
   "Quand une automatisation désactive les règles automatiques, aucune d'elles n'agit pour ce message."
  ],
  "lang": "fr"
 },
 "es": {
  "title": "Cómo actúan juntas las reglas",
  "lead": "Elige una regla: ves lo que hace y qué pasa cuando se encuentra con cada una de las demás.",
  "lanes": {
   "calm": "Mantener la calma",
   "band": "Siempre pasa",
   "send": "Asegurar que llegue"
  },
  "names": {
   "summarize": "Resumir",
   "quiet": "Horas de silencio",
   "presence": "Presencia",
   "through": "Dejar pasar",
   "deliver": "Entregar",
   "escalation": "Escalado",
   "reminder": "Recordatorio",
   "fallback": "Alternativa"
  },
  "about": {
   "summarize": [
    "Recoge mensajes y envía un resumen a una hora del día o cada pocos minutos.",
    "<b>Resumen de la tarde</b>: los mensajes con la etiqueta digest llegan juntos a las 20:00."
   ],
   "quiet": [
    "Durante unas horas fijas, los mensajes esperan, llegan en silencio o se descartan.",
    "<b>Noche tranquila</b>: los mensajes info entre las 22:00 y las 07:00 llegan sin sonido."
   ],
   "presence": [
    "Envía según dónde está la gente: retenido hasta que alguien llega o se va, o descartado.",
    "<b>Hablar solo si hay alguien</b>: ningún aviso del timbre en una casa vacía."
   ],
   "through": [
    "Indica qué mensajes pueden despertar a quién, pese a las horas de silencio y los resúmenes. No envía nada.",
    "<b>Las alarmas despiertan a los admins</b>: una fuga de noche solo suena a los admins."
   ],
   "deliver": [
    "Envía también el mensaje a más personas o por más canales, enseguida.",
    "<b>Alarmas a los admins</b>: cada alarma va también a los teléfonos de los admins."
   ],
   "escalation": [
    "Si nadie confirma a tiempo, avisa a más personas o por más canales, una vez.",
    "<b>Nadie miró</b>: tras 15 minutos sin confirmación, lo reciben todos."
   ],
   "reminder": [
    "Repite el mensaje hasta que alguien confirma, como mucho las veces fijadas.",
    "<b>Recordatorio de aviso</b>: cada 30 minutos, como mucho 3 veces."
   ],
   "fallback": [
    "Interviene cuando no se pudo localizar a nadie, por ejemplo con un altavoz.",
    "<b>Decirlo en casa</b>: ningún teléfono respondió, así que lo dice el altavoz de la cocina."
   ]
  },
  "what": "Qué hace",
  "example": "Ejemplo",
  "together": "Junto con …",
  "all": "Todas",
  "conflicts": "Solo conflictos",
  "show": "Ver ejemplo",
  "hide": "Ocultar ejemplo",
  "self": "una segunda",
  "verdicts": {
   "wins": "Se impone",
   "yields": "Cede",
   "both": "Actúan las dos",
   "add": "Se suman",
   "first": "Actúa primero",
   "after": "Actúa después",
   "one": "Solo cuenta una",
   "calmer": "Cuenta la más tranquila",
   "warn": "Aviso"
  },
  "rulesTitle": "Tres reglas detrás de todo",
  "rules": [
   "Cada regla que encaja con un mensaje actúa. Cuando las reglas que calman discrepan, cuenta el resultado más tranquilo.",
   "Los escalados y recordatorios cuentan desde la creación del mensaje. Cada recordatorio lleva su propio recuento.",
   "Siempre pasa deja pasar los mensajes más allá de las horas de silencio y los resúmenes para las personas afectadas. La presencia nunca se salta."
  ],
  "notes": [
   "Una regla activada solo actúa en los mensajes que llegan después. «Solo si» se comprueba en cada paso.",
   "Cuando una automatización desactiva las reglas automáticas, ninguna actúa para ese mensaje."
  ],
  "lang": "es"
 }
};

const SYMBOL = { wins: "▲", yields: "▼", both: "=", add: "+", first: "1", after: "2", one: "1×", calmer: "☾", warn: "!" };
const CONFLICT = new Set(["wins", "yields", "one", "calmer", "warn"]);

// The verdict and the text of a pair from the side of .
export function pairFor(a, b, lang) {
  const direct = PAIRS[`${a}|${b}`];
  const found = direct || PAIRS[`${b}|${a}`];
  const text = found[lang] || found.en;
  return { verdict: direct ? found.va : found.vb, text };
}

// Text with <b> only, as nodes: no other markup reaches the page.
function rich(el, html) {
  const out = [];
  html.split(/(<b>.*?<\/b>)/).forEach((part) => {
    if (!part) return;
    const bold = part.match(/^<b>(.*)<\/b>$/);
    out.push(bold ? el("strong", { textContent: bold[1] }) : document.createTextNode(part));
  });
  return out;
}

const CSS = `
.hu-page .tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
.hu-page .tile { display: flex; gap: 10px; align-items: center; text-align: left; width: 100%; padding: 10px 12px; border-radius: 12px; border: 2px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; cursor: pointer; min-height: 52px; }
.hu-page .tile[aria-pressed="true"] { border-color: var(--primary-color); }
.hu-page .tile .ic { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; flex: none; font-weight: 700; background: var(--secondary-background-color); }
.hu-page h3.lane { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; margin: 16px 0 8px; }
.hu-page .detail { margin-top: 16px; border: 1px solid var(--divider-color); border-radius: 12px; padding: 12px; }
.hu-page .example { background: var(--secondary-background-color); border-radius: 8px; padding: 8px 10px; margin: 6px 0; }
.hu-page ul.pairs { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.hu-page ul.pairs li { border: 1px solid var(--divider-color); border-radius: 10px; }
.hu-page ul.pairs summary { cursor: pointer; padding: 8px 10px; list-style: none; }
.hu-page ul.pairs summary::-webkit-details-marker { display: none; }
.hu-page .verdict { display: inline-block; font-size: 13px; font-weight: 600; padding: 1px 8px; border-radius: 999px; background: var(--secondary-background-color); margin: 4px 0; }
.hu-page .verdict.warn { color: var(--error-color); }
.hu-page .chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 4px 0 8px; }
.hu-page .chip { border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); border-radius: 999px; padding: 4px 10px; font: inherit; cursor: pointer; }
.hu-page .chip[aria-pressed="true"] { border-color: var(--primary-color); color: var(--primary-color); font-weight: 600; }
.hu-page .more { font-size: 13px; color: var(--primary-color); }
.hu-page .body { padding: 0 10px 10px; }
@media (max-width: 420px) { .hu-page .tiles { grid-template-columns: 1fr 1fr; } }
`;

export function mount(container, ctx) {
  const { t, ui } = ctx;
  const { el } = ui;
  const lang = t.lang || "en";
  const state = { kind: "quiet", filter: "all" };
  const root = el("div", { className: "hu-page" });
  container.append(root);

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + CSS }), el("h1", { textContent: t.title }), el("div", { className: "hint", textContent: t.lead }));
    for (const lane of ["calm", "band", "send"]) {
      root.append(el("h3", { className: "lane", textContent: t.lanes[lane] }));
      const grid = el("div", { className: "tiles" });
      for (const kind of KINDS.filter((k) => k.lane === lane)) {
        const button = el("button", { type: "button", className: "tile" }, [el("span", { className: "ic", textContent: kind.icon }), el("span", { textContent: t.names[kind.key] })]);
        button.setAttribute("aria-pressed", String(state.kind === kind.key));
        button.querySelector(".ic").setAttribute("aria-hidden", "true");
        button.addEventListener("click", () => { state.kind = kind.key; render(); });
        grid.append(button);
      }
      root.append(grid);
    }
    const me = KINDS.find((k) => k.key === state.kind);
    const detail = el("section", { className: "detail" });
    detail.setAttribute("aria-live", "polite");
    detail.append(el("div", { className: "hint", textContent: t.lanes[me.lane] }), el("h2", { textContent: t.names[me.key] }), el("p", { textContent: t.about[me.key][0] }));
    detail.append(el("div", { className: "example" }, [el("strong", { textContent: `${t.example}: ` }), ...rich(el, t.about[me.key][1])]));
    detail.append(el("h3", { textContent: t.together }));
    const chips = el("div", { className: "chips" });
    for (const filter of ["all", "conflicts"]) {
      const chip = el("button", { type: "button", className: "chip", textContent: filter === "all" ? t.all : t.conflicts });
      chip.setAttribute("aria-pressed", String(state.filter === filter));
      chip.addEventListener("click", () => { state.filter = filter; render(); });
      chips.append(chip);
    }
    detail.append(chips);
    const list = el("ul", { className: "pairs" });
    for (const other of KINDS) {
      const pair = pairFor(me.key, other.key, lang);
      if (state.filter === "conflicts" && !CONFLICT.has(pair.verdict)) continue;
      const name = other.key === me.key ? `${t.names[other.key]} (${t.self})` : t.names[other.key];
      const summary = el("summary", {}, [
        el("strong", { textContent: `${other.icon} ${name}` }),
        el("div", { className: `verdict ${pair.verdict}`, textContent: `${SYMBOL[pair.verdict]} ${t.verdicts[pair.verdict]}` }),
        el("div", { textContent: pair.text[0] }),
        el("div", { className: "more", textContent: t.show }),
      ]);
      const details = el("details", {}, [summary, el("div", { className: "body" }, [el("div", { className: "example" }, [el("strong", { textContent: `${t.example}: ` }), ...rich(el, pair.text[1])])])]);
      details.addEventListener("toggle", () => { summary.querySelector(".more").textContent = details.open ? t.hide : t.show; });
      list.append(el("li", {}, [details]));
    }
    detail.append(list);
    root.append(detail);
    const rules = el("section", {}, [el("h2", { textContent: t.rulesTitle }), el("ol", {}, t.rules.map((r) => el("li", { textContent: r })))]);
    t.notes.forEach((n) => rules.append(el("p", { className: "hint", textContent: n })));
    root.append(rules);
  }

  render();
  return { setHass() {}, destroy() { root.remove(); } };
}
