// Heads Up panel: Policies page (D-119). One form for the six types, saved through the policy flow.

const TYPE_NAMES = {
  en: { escalation: "Escalation", reminder: "Reminder", quiet_hours: "Quiet hours", away: "Away", fallback: "Fallback", summarize: "Summarize", deliver: "Deliver" },
  de: { escalation: "Eskalation", reminder: "Erinnerung", quiet_hours: "Ruhezeit", away: "Abwesend", fallback: "Ersatz", summarize: "Zusammenfassen", deliver: "Zustellen" },
  fr: { escalation: "Escalade", reminder: "Rappel", quiet_hours: "Heures calmes", away: "Absent", fallback: "Repli", summarize: "Résumer", deliver: "Livrer" },
  es: { escalation: "Escalado", reminder: "Recordatorio", quiet_hours: "Horas de silencio", away: "Ausente", fallback: "Alternativa", summarize: "Resumir", deliver: "Entregar" },
};
const DAY_NAMES = {
  en: { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" },
  de: { mon: "Montag", tue: "Dienstag", wed: "Mittwoch", thu: "Donnerstag", fri: "Freitag", sat: "Samstag", sun: "Sonntag" },
  fr: { mon: "Lundi", tue: "Mardi", wed: "Mercredi", thu: "Jeudi", fri: "Vendredi", sat: "Samedi", sun: "Dimanche" },
  es: { mon: "Lunes", tue: "Martes", wed: "Miércoles", thu: "Jueves", fri: "Viernes", sat: "Sábado", sun: "Domingo" },
};
const ACTIONS = {
  en: { quiet: "Send quietly", wait: "Hold until the end", drop: "Drop" },
  de: { quiet: "Leise senden", wait: "Bis zum Ende zurückhalten", drop: "Verwerfen" },
  fr: { quiet: "Envoyer discrètement", wait: "Retenir jusqu'à la fin", drop: "Abandonner" },
  es: { quiet: "Enviar en silencio", wait: "Retener hasta el final", drop: "Descartar" },
};
const WHENS = {
  en: { no_audience: "Nobody to notify", failed: "Delivery failed", both: "Either" },
  de: { no_audience: "Niemand zu benachrichtigen", failed: "Zustellung fehlgeschlagen", both: "Eines von beiden" },
  fr: { no_audience: "Personne à notifier", failed: "Échec de l'envoi", both: "L'un ou l'autre" },
  es: { no_audience: "Nadie a quien avisar", failed: "Falló el envío", both: "Cualquiera de los dos" },
};

export const STRINGS = {
  en: {
    title: "Policies",
    intro: "A policy adds behavior to messages: escalate, remind, keep quiet at night, wait for people to come home, send somewhere else, or summarize.",
    none: "You have no policies yet. The introduction (Settings, Restart introduction) offers a starting set.",
    new: "New policy",
    editing: "Edit policy",
    type: "Type",
    types: TYPE_NAMES.en,
    disabled: "disabled",
    applies: "Applies to",
    severities: "Severities (none selected: any)",
    tags: "Tags, comma separated (empty: any)",
    severity_names: { success: "Success", info: "Info", warning: "Warning", critical: "Critical" },
    channel_names: { push: "Push", popup: "Popup", speak: "Speak", persistent: "Persistent Notification", mail: "Mail" },
    after: "Escalate after (minutes)",
    channels: "Channels",
    channels_reminder: "Limit to these channels (none selected: all)",
    dismiss_acks: "Dismissing counts as acknowledging",
    every: "Repeat every (minutes)",
    max_count: "At most this many reminders",
    from: "Quiet from",
    to: "Quiet until",
    days: "Days (none selected: every day)",
    days_names: DAY_NAMES.en,
    action: "During quiet hours",
    actions: ACTIONS.en,
    critical_passes: "Critical messages pass",
    max_wait: "Wait for arrival (minutes, 0: as long as the message lives)",
    when: "Use when",
    whens: WHENS.en,
    summary_mode: "Send the summary",
    summary_every_mode: "Every N minutes",
    summary_at_mode: "At a time of day",
    summary_every: "Minutes after the first held message",
    summary_at: "Time of day",
    include_critical: "Include critical messages",
    critical_warning: "Critical messages are then held too and arrive only in the summary.",
    summarize_note: "Nothing is sent individually while a message waits. The summary shows the count and the titles, marks resolved ones and cuts at 10 (“and N more”).",
    ack_note: "Pushes of messages this policy covers get an Acknowledge button.",
    target_channel: "Channel {channel}",
    target_audience: "Audience",
    target_recipients: "Recipients",
    target_persistent: "No target: it goes to everyone.",
    sentence: "In words",
    s_applies_any: "Every message",
    enabled_hint: "A disabled policy is never used, not even when a call names it.",
    sec_when: "Which messages",
    sec_does: "What it does",
    type_desc: {"escalation": "If nobody acknowledges within the time, the message is also delivered on the channels and to the targets you choose.", "reminder": "While nobody acknowledges, the message is repeated at an interval, up to a maximum.", "quiet_hours": "Between two times of day, deliveries outside the dashboard are sent quietly, held until the end or dropped.", "away": "A person who is not home gets the message when they arrive, if it is still there.", "fallback": "If the first delivery reached nobody, the message is delivered on other channels or to other targets.", "summarize": "Matching messages are held on every channel, the banner included, and one summary is sent instead.", "deliver": "Matching messages are also delivered at once to the audience and channels you choose."},
    apply_label: "Attaches to messages",
    apply_auto: "Automatically",
    apply_auto_hint: "Every message whose severity and tag match gets this policy. An empty list matches any.",
    apply_manual: "Manually",
    apply_manual_hint: "Only a call that names this policy gets it. The severity and the tag of the message do not matter.",
    manual_how: "Name it in a call:",
    manual_note: "A call that names a policy uses only that policy, not the automatic ones. policy: none switches every policy off for a call.",
    badge_manual: "manual",
    mode_title: "How policies interact",
    mode_first: "Only the first policy that applies runs",
    mode_first_hint: "Each message gets one policy: the first in the list below that fits. A call or a watch rule that names a policy uses only that one.",
    mode_all: "Every policy that applies runs",
    mode_all_hint: "A message can get several policies at once, for example quiet hours and a reminder. They can interfere, so check them with Test send.",
    order_first: "The list decides. Drag a policy, or use the arrows, to change the order.",
    order_all: "In this mode the order of the list does not matter.",
    move_up: "Move up",
    move_down: "Move down",
    handle: "Drag to change the order",
    position: "Position {n}",
    overlap_first: "These policies come first and also match some of the same messages, so they run instead: {names}",
    shadowed: "Never runs by itself: {name} is above it and matches all the same messages. Move this policy above it, or narrow that one.",
    overlap_all: "Other policies of this type that match some of the same messages: {names}",
    order_failed: "The order could not be saved. Try again.",
    s_applies_manual: "Calls that name this policy",
    s_applies: "Messages with {parts}",
    s_severity: "severity {severities}",
    s_tag: "tag {tags}",
    s_and: " and ",
    s_escalation: "{applies}: if nobody acknowledges within {n} min, it is also sent on {channels}.",
    s_reminder: "{applies}: while nobody acknowledges, the notification is repeated every {n} min, at most {m} times{channels}.",
    s_quiet_hours: "{applies}: between {from} and {to}{days}, deliveries outside the dashboard are {action}{critical}.",
    s_away: "{applies}: a person who is not home gets it when they arrive{wait}.",
    s_deliver: "{applies}: it is also sent at once on {channels}.",
    s_fallback: "{applies}: if {when}, it is sent on {channels} instead.",
    s_summarize_every: "{applies}: held, and one summary is sent {n} min after the first held message{critical}.",
    s_summarize_at: "{applies}: held, and one summary is sent every day at {time}{critical}.",
    s_in_channels: ", only on {channels}",
    s_days: " on {days}",
    s_critical_pass: ", critical messages pass",
    s_critical_held: ", critical messages included",
    s_wait: ", for at most {n} min",
    a_quiet: "sent quietly",
    a_wait: "held until the end",
    a_drop: "dropped",
    w_no_audience: "the audience is empty",
    w_failed: "delivery fails",
    w_both: "the audience is empty or delivery fails",
  },
  de: {
    title: "Richtlinien",
    intro: "Eine Richtlinie ergänzt Meldungen um Verhalten: eskalieren, erinnern, nachts ruhig sein, auf Heimkehrende warten, anderswohin senden oder zusammenfassen.",
    none: "Du hast noch keine Richtlinien. Die Einführung (Einstellungen, Einführung neu starten) bietet einen Grundstock an.",
    new: "Neue Richtlinie",
    editing: "Richtlinie bearbeiten",
    type: "Art",
    types: TYPE_NAMES.de,
    disabled: "deaktiviert",
    applies: "Gilt für",
    severities: "Schweregrade (keiner gewählt: alle)",
    tags: "Tags, durch Komma getrennt (leer: alle)",
    severity_names: { success: "Erfolg", info: "Info", warning: "Warnung", critical: "Kritisch" },
    channel_names: { push: "Push", popup: "Popup", speak: "Sprache", persistent: "Persistente Benachrichtigung", mail: "E-Mail" },
    after: "Eskalieren nach (Minuten)",
    channels: "Kanäle",
    channels_reminder: "Auf diese Kanäle beschränken (keiner gewählt: alle)",
    dismiss_acks: "Ausblenden zählt als Bestätigung",
    every: "Wiederholen alle (Minuten)",
    max_count: "Höchstens so viele Erinnerungen",
    from: "Ruhe ab",
    to: "Ruhe bis",
    days: "Tage (keiner gewählt: jeden Tag)",
    days_names: DAY_NAMES.de,
    action: "Während der Ruhezeit",
    actions: ACTIONS.de,
    critical_passes: "Kritische Meldungen kommen durch",
    max_wait: "Auf Ankunft warten (Minuten, 0: solange die Meldung besteht)",
    when: "Verwenden, wenn",
    whens: WHENS.de,
    summary_mode: "Zusammenfassung senden",
    summary_every_mode: "Alle N Minuten",
    summary_at_mode: "Zu einer Uhrzeit",
    summary_every: "Minuten nach der ersten zurückgehaltenen Meldung",
    summary_at: "Uhrzeit",
    include_critical: "Kritische Meldungen einschließen",
    critical_warning: "Kritische Meldungen werden dann auch zurückgehalten und kommen nur in der Zusammenfassung an.",
    summarize_note: "Solange eine Meldung wartet, wird nichts einzeln gesendet. Die Zusammenfassung zeigt die Anzahl und die Titel, markiert erledigte und kürzt bei 10 („und N weitere“).",
    ack_note: "Pushes von Meldungen, die diese Richtlinie abdeckt, bekommen eine Schaltfläche Bestätigen.",
    target_channel: "Kanal {channel}",
    target_audience: "Zielgruppe",
    target_recipients: "Empfänger",
    target_persistent: "Kein Ziel: geht an alle.",
    sentence: "In Worten",
    s_applies_any: "Jede Meldung",
    enabled_hint: "Eine deaktivierte Richtlinie wird nie genutzt, auch nicht, wenn ein Aufruf sie nennt.",
    sec_when: "Welche Meldungen",
    sec_does: "Was sie tut",
    type_desc: {"escalation": "Bestätigt niemand innerhalb der Zeit, wird die Meldung zusätzlich auf den gewählten Kanälen und an die gewählten Ziele zugestellt.", "reminder": "Solange niemand bestätigt, wird die Meldung in einem Abstand wiederholt, höchstens so oft wie eingestellt.", "quiet_hours": "Zwischen zwei Uhrzeiten werden Zustellungen außerhalb des Dashboards leise gesendet, bis zum Ende zurückgehalten oder verworfen.", "away": "Eine Person, die nicht zu Hause ist, bekommt die Meldung bei der Ankunft, wenn sie noch da ist.", "fallback": "Hat die erste Zustellung niemanden erreicht, wird die Meldung auf anderen Kanälen oder an andere Ziele zugestellt.", "summarize": "Passende Meldungen werden auf jedem Kanal zurückgehalten, auch im Banner, und stattdessen wird eine Zusammenfassung gesendet.", "deliver": "Passende Meldungen werden zusätzlich sofort an die gewählte Zielgruppe auf den gewählten Kanälen zugestellt."},
    apply_label: "Gilt für Meldungen",
    apply_auto: "Automatisch",
    apply_auto_hint: "Jede Meldung, deren Schweregrad und Tag passen, bekommt diese Richtlinie. Eine leere Liste passt auf alles.",
    apply_manual: "Manuell",
    apply_manual_hint: "Nur ein Aufruf, der diese Richtlinie nennt, bekommt sie. Schweregrad und Tag der Meldung spielen keine Rolle.",
    manual_how: "In einem Aufruf nennen:",
    manual_note: "Ein Aufruf, der eine Richtlinie nennt, nutzt nur diese, nicht die automatischen. policy: none schaltet alle Richtlinien für einen Aufruf ab.",
    badge_manual: "manuell",
    mode_title: "Wie Richtlinien zusammenwirken",
    mode_first: "Nur die erste passende Richtlinie läuft",
    mode_first_hint: "Jede Meldung bekommt eine Richtlinie: die erste in der Liste unten, die passt. Ein Aufruf oder eine Überwachungsregel, die eine Richtlinie nennt, nutzt nur diese.",
    mode_all: "Jede passende Richtlinie läuft",
    mode_all_hint: "Eine Meldung kann mehrere Richtlinien gleichzeitig bekommen, zum Beispiel Ruhezeit und eine Erinnerung. Sie können sich stören, prüfe sie daher mit Testsenden.",
    order_first: "Die Liste entscheidet. Ziehe eine Richtlinie oder nutze die Pfeile, um die Reihenfolge zu ändern.",
    order_all: "In diesem Modus spielt die Reihenfolge der Liste keine Rolle.",
    move_up: "Nach oben",
    move_down: "Nach unten",
    handle: "Ziehen, um die Reihenfolge zu ändern",
    position: "Position {n}",
    overlap_first: "Diese Richtlinien stehen weiter oben und passen auch auf einige derselben Meldungen, laufen also stattdessen: {names}",
    shadowed: "Läuft nie von selbst: {name} steht darüber und passt auf alle dieselben Meldungen. Verschiebe diese Richtlinie darüber oder schränke jene ein.",
    overlap_all: "Andere Richtlinien dieses Typs, die auf einige derselben Meldungen passen: {names}",
    order_failed: "Die Reihenfolge konnte nicht gespeichert werden. Versuche es erneut.",
    s_applies_manual: "Aufrufe, die diese Richtlinie nennen",
    s_applies: "Meldungen mit {parts}",
    s_severity: "Schweregrad {severities}",
    s_tag: "Tag {tags}",
    s_and: " und ",
    s_escalation: "{applies}: bestätigt niemand innerhalb von {n} Min., wird zusätzlich auf {channels} gesendet.",
    s_reminder: "{applies}: solange niemand bestätigt, wird die Benachrichtigung alle {n} Min. wiederholt, höchstens {m} Mal{channels}.",
    s_quiet_hours: "{applies}: zwischen {from} und {to}{days} werden Zustellungen außerhalb des Dashboards {action}{critical}.",
    s_away: "{applies}: wer nicht zu Hause ist, bekommt sie bei der Ankunft{wait}.",
    s_deliver: "{applies}: wird zusätzlich sofort auf {channels} gesendet.",
    s_fallback: "{applies}: wenn {when}, wird stattdessen auf {channels} gesendet.",
    s_summarize_every: "{applies}: zurückgehalten, und eine Zusammenfassung wird {n} Min. nach der ersten zurückgehaltenen Meldung gesendet{critical}.",
    s_summarize_at: "{applies}: zurückgehalten, und eine Zusammenfassung wird jeden Tag um {time} gesendet{critical}.",
    s_in_channels: ", nur auf {channels}",
    s_days: " an {days}",
    s_critical_pass: ", kritische Meldungen kommen durch",
    s_critical_held: ", kritische Meldungen eingeschlossen",
    s_wait: ", höchstens {n} Min.",
    a_quiet: "leise gesendet",
    a_wait: "bis zum Ende zurückgehalten",
    a_drop: "verworfen",
    w_no_audience: "die Zielgruppe leer ist",
    w_failed: "die Zustellung fehlschlägt",
    w_both: "die Zielgruppe leer ist oder die Zustellung fehlschlägt",
  },
  fr: {
    title: "Politiques",
    intro: "Une politique ajoute un comportement aux messages : escalader, rappeler, rester discret la nuit, attendre le retour des personnes, envoyer ailleurs ou résumer.",
    none: "Vous n'avez pas encore de politique. L'introduction (Réglages, Relancer l'introduction) propose un jeu de départ.",
    new: "Nouvelle politique",
    editing: "Modifier la politique",
    type: "Type",
    types: TYPE_NAMES.fr,
    disabled: "désactivée",
    applies: "S'applique à",
    severities: "Gravités (aucune choisie : toutes)",
    tags: "Étiquettes, séparées par des virgules (vide : toutes)",
    severity_names: { success: "Succès", info: "Info", warning: "Avertissement", critical: "Critique" },
    channel_names: { push: "Push", popup: "Fenêtre", speak: "Voix", persistent: "Notification persistante", mail: "Courriel" },
    after: "Escalader après (minutes)",
    channels: "Canaux",
    channels_reminder: "Limiter à ces canaux (aucun choisi : tous)",
    dismiss_acks: "Masquer vaut acquittement",
    every: "Répéter toutes les (minutes)",
    max_count: "Au plus ce nombre de rappels",
    from: "Calme de",
    to: "Calme jusqu'à",
    days: "Jours (aucun choisi : tous les jours)",
    days_names: DAY_NAMES.fr,
    action: "Pendant les heures calmes",
    actions: ACTIONS.fr,
    critical_passes: "Les messages critiques passent",
    max_wait: "Attendre l'arrivée (minutes, 0 : tant que le message existe)",
    when: "Utiliser quand",
    whens: WHENS.fr,
    summary_mode: "Envoyer le résumé",
    summary_every_mode: "Toutes les N minutes",
    summary_at_mode: "À une heure du jour",
    summary_every: "Minutes après le premier message retenu",
    summary_at: "Heure",
    include_critical: "Inclure les messages critiques",
    critical_warning: "Les messages critiques sont alors retenus aussi et n'arrivent que dans le résumé.",
    summarize_note: "Rien n'est envoyé individuellement tant qu'un message attend. Le résumé montre le nombre et les titres, marque les messages résolus et s'arrête à 10 (« et N autres »).",
    ack_note: "Les push des messages que cette politique couvre ont un bouton Confirmer.",
    target_channel: "Canal {channel}",
    target_audience: "Audience",
    target_recipients: "Destinataires",
    target_persistent: "Pas de cible : va à tout le monde.",
    sentence: "En clair",
    s_applies_any: "Tout message",
    enabled_hint: "Une politique désactivée n'est jamais utilisée, même si un appel la nomme.",
    sec_when: "Quels messages",
    sec_does: "Ce qu'elle fait",
    type_desc: {"escalation": "Si personne ne confirme dans le délai, le message est aussi remis sur les canaux et aux cibles que vous choisissez.", "reminder": "Tant que personne ne confirme, le message est répété à intervalle régulier, jusqu'à un maximum.", "quiet_hours": "Entre deux heures de la journée, les remises hors tableau de bord sont envoyées discrètement, retenues jusqu'à la fin ou abandonnées.", "away": "Une personne absente reçoit le message à son arrivée, s'il est encore là.", "fallback": "Si la première remise n'a joint personne, le message est remis sur d'autres canaux ou à d'autres cibles.", "summarize": "Les messages correspondants sont retenus sur chaque canal, bannière comprise, et un seul résumé est envoyé à la place.", "deliver": "Les messages correspondants sont aussi remis tout de suite à l'audience et sur les canaux que vous choisissez."},
    apply_label: "S'applique aux messages",
    apply_auto: "Automatiquement",
    apply_auto_hint: "Chaque message dont la gravité et l'étiquette correspondent reçoit cette politique. Une liste vide correspond à tout.",
    apply_manual: "Manuellement",
    apply_manual_hint: "Seul un appel qui nomme cette politique la reçoit. La gravité et l'étiquette du message n'ont pas d'importance.",
    manual_how: "La nommer dans un appel :",
    manual_note: "Un appel qui nomme une politique n'utilise que celle-là, pas les automatiques. policy: none désactive toutes les politiques pour un appel.",
    badge_manual: "manuelle",
    mode_title: "Comment les politiques interagissent",
    mode_first: "Seule la première politique qui s'applique agit",
    mode_first_hint: "Chaque message reçoit une politique : la première de la liste ci-dessous qui convient. Un appel ou une règle de surveillance qui nomme une politique n'utilise que celle-là.",
    mode_all: "Chaque politique qui s'applique agit",
    mode_all_hint: "Un message peut recevoir plusieurs politiques à la fois, par exemple des heures calmes et un rappel. Elles peuvent se gêner : vérifiez-les avec Envoi de test.",
    order_first: "La liste décide. Faites glisser une politique, ou utilisez les flèches, pour changer l'ordre.",
    order_all: "Dans ce mode, l'ordre de la liste n'a pas d'importance.",
    move_up: "Monter",
    move_down: "Descendre",
    handle: "Faire glisser pour changer l'ordre",
    position: "Position {n}",
    overlap_first: "Ces politiques sont plus haut et correspondent aussi à certains des mêmes messages, elles agissent donc à la place : {names}",
    shadowed: "Ne s'exécute jamais seule : {name} est au-dessus et correspond à tous les mêmes messages. Place cette politique au-dessus ou restreins l'autre.",
    overlap_all: "Autres politiques de ce type qui correspondent à certains des mêmes messages : {names}",
    order_failed: "L'ordre n'a pas pu être enregistré. Réessayez.",
    s_applies_manual: "Appels qui nomment cette politique",
    s_applies: "Messages avec {parts}",
    s_severity: "la gravité {severities}",
    s_tag: "l'étiquette {tags}",
    s_and: " et ",
    s_escalation: "{applies} : si personne ne confirme en {n} min, il est aussi envoyé sur {channels}.",
    s_reminder: "{applies} : tant que personne ne confirme, la notification est répétée toutes les {n} min, au plus {m} fois{channels}.",
    s_quiet_hours: "{applies} : entre {from} et {to}{days}, les livraisons hors tableau de bord sont {action}{critical}.",
    s_away: "{applies} : une personne qui n'est pas à la maison le reçoit à son arrivée{wait}.",
    s_deliver: "{applies} : il est aussi envoyé tout de suite sur {channels}.",
    s_fallback: "{applies} : si {when}, il est envoyé sur {channels} à la place.",
    s_summarize_every: "{applies} : retenu, et un résumé est envoyé {n} min après le premier message retenu{critical}.",
    s_summarize_at: "{applies} : retenu, et un résumé est envoyé chaque jour à {time}{critical}.",
    s_in_channels: ", seulement sur {channels}",
    s_days: " le {days}",
    s_critical_pass: ", les messages critiques passent",
    s_critical_held: ", messages critiques inclus",
    s_wait: ", au plus {n} min",
    a_quiet: "envoyées discrètement",
    a_wait: "retenues jusqu'à la fin",
    a_drop: "abandonnées",
    w_no_audience: "l'audience est vide",
    w_failed: "la livraison échoue",
    w_both: "l'audience est vide ou la livraison échoue",
  },
  es: {
    title: "Políticas",
    intro: "Una política añade comportamiento a los mensajes: escalar, recordar, callar de noche, esperar a que la gente vuelva a casa, enviar a otro sitio o resumir.",
    none: "Aún no tienes políticas. La introducción (Ajustes, Reiniciar la introducción) ofrece un conjunto inicial.",
    new: "Nueva política",
    editing: "Editar política",
    type: "Tipo",
    types: TYPE_NAMES.es,
    disabled: "desactivada",
    applies: "Se aplica a",
    severities: "Gravedades (ninguna elegida: todas)",
    tags: "Etiquetas, separadas por comas (vacío: todas)",
    severity_names: { success: "Éxito", info: "Info", warning: "Aviso", critical: "Crítico" },
    channel_names: { push: "Push", popup: "Ventana", speak: "Voz", persistent: "Notificación persistente", mail: "Correo" },
    after: "Escalar tras (minutos)",
    channels: "Canales",
    channels_reminder: "Limitar a estos canales (ninguno elegido: todos)",
    dismiss_acks: "Descartar cuenta como confirmar",
    every: "Repetir cada (minutos)",
    max_count: "Como máximo este número de recordatorios",
    from: "Silencio desde",
    to: "Silencio hasta",
    days: "Días (ninguno elegido: todos los días)",
    days_names: DAY_NAMES.es,
    action: "Durante las horas de silencio",
    actions: ACTIONS.es,
    critical_passes: "Los mensajes críticos pasan",
    max_wait: "Esperar la llegada (minutos, 0: mientras exista el mensaje)",
    when: "Usar cuando",
    whens: WHENS.es,
    summary_mode: "Enviar el resumen",
    summary_every_mode: "Cada N minutos",
    summary_at_mode: "A una hora del día",
    summary_every: "Minutos tras el primer mensaje retenido",
    summary_at: "Hora",
    include_critical: "Incluir mensajes críticos",
    critical_warning: "Los mensajes críticos también se retienen y solo llegan en el resumen.",
    summarize_note: "No se envía nada por separado mientras un mensaje espera. El resumen muestra el número y los títulos, marca los resueltos y corta en 10 («y N más»).",
    ack_note: "Los push de los mensajes que cubre esta política tienen un botón Confirmar.",
    target_channel: "Canal {channel}",
    target_audience: "Audiencia",
    target_recipients: "Destinatarios",
    target_persistent: "Sin destino: va a todos.",
    sentence: "En palabras",
    s_applies_any: "Todos los mensajes",
    enabled_hint: "Una política desactivada nunca se usa, ni siquiera si una llamada la nombra.",
    sec_when: "Qué mensajes",
    sec_does: "Qué hace",
    type_desc: {"escalation": "Si nadie confirma en el tiempo, el mensaje se entrega también por los canales y a los destinos que elijas.", "reminder": "Mientras nadie confirma, el mensaje se repite a intervalos, hasta un máximo.", "quiet_hours": "Entre dos horas del día, las entregas fuera del panel se envían en silencio, se retienen hasta el final o se descartan.", "away": "Una persona que no está en casa recibe el mensaje al llegar, si sigue ahí.", "fallback": "Si la primera entrega no llegó a nadie, el mensaje se entrega por otros canales o a otros destinos.", "summarize": "Los mensajes que coinciden se retienen en todos los canales, el aviso incluido, y se envía un solo resumen.", "deliver": "Los mensajes que coinciden también se entregan al instante a la audiencia y por los canales que elijas."},
    apply_label: "Se aplica a los mensajes",
    apply_auto: "Automáticamente",
    apply_auto_hint: "Cada mensaje cuya gravedad y etiqueta coinciden recibe esta política. Una lista vacía coincide con todo.",
    apply_manual: "Manualmente",
    apply_manual_hint: "Solo una llamada que nombra esta política la recibe. La gravedad y la etiqueta del mensaje no importan.",
    manual_how: "Nómbrala en una llamada:",
    manual_note: "Una llamada que nombra una política usa solo esa, no las automáticas. policy: none desactiva todas las políticas para una llamada.",
    badge_manual: "manual",
    mode_title: "Cómo interactúan las políticas",
    mode_first: "Solo actúa la primera política que se aplica",
    mode_first_hint: "Cada mensaje recibe una política: la primera de la lista de abajo que encaja. Una llamada o una regla de vigilancia que nombra una política usa solo esa.",
    mode_all: "Actúa cada política que se aplica",
    mode_all_hint: "Un mensaje puede recibir varias políticas a la vez, por ejemplo horas de silencio y un recordatorio. Pueden estorbarse: compruébalas con Envío de prueba.",
    order_first: "La lista decide. Arrastra una política, o usa las flechas, para cambiar el orden.",
    order_all: "En este modo el orden de la lista no importa.",
    move_up: "Subir",
    move_down: "Bajar",
    handle: "Arrastra para cambiar el orden",
    position: "Posición {n}",
    overlap_first: "Estas políticas van antes y también coinciden con algunos de los mismos mensajes, así que actúan en su lugar: {names}",
    shadowed: "No se ejecuta nunca por sí sola: {name} está encima y coincide con todos los mismos mensajes. Mueve esta política por encima o limita la otra.",
    overlap_all: "Otras políticas de este tipo que coinciden con algunos de los mismos mensajes: {names}",
    order_failed: "No se pudo guardar el orden. Inténtalo de nuevo.",
    s_applies_manual: "Llamadas que nombran esta política",
    s_applies: "Mensajes con {parts}",
    s_severity: "gravedad {severities}",
    s_tag: "etiqueta {tags}",
    s_and: " y ",
    s_escalation: "{applies}: si nadie confirma en {n} min, se envía también por {channels}.",
    s_reminder: "{applies}: mientras nadie confirme, la notificación se repite cada {n} min, como máximo {m} veces{channels}.",
    s_quiet_hours: "{applies}: entre {from} y {to}{days}, las entregas fuera del panel se {action}{critical}.",
    s_away: "{applies}: quien no está en casa lo recibe al llegar{wait}.",
    s_deliver: "{applies}: se envía además de inmediato por {channels}.",
    s_fallback: "{applies}: si {when}, se envía por {channels} en su lugar.",
    s_summarize_every: "{applies}: retenido, y se envía un resumen {n} min después del primer mensaje retenido{critical}.",
    s_summarize_at: "{applies}: retenido, y se envía un resumen cada día a las {time}{critical}.",
    s_in_channels: ", solo por {channels}",
    s_days: " en {days}",
    s_critical_pass: ", los mensajes críticos pasan",
    s_critical_held: ", mensajes críticos incluidos",
    s_wait: ", como máximo {n} min",
    a_quiet: "envían en silencio",
    a_wait: "retienen hasta el final",
    a_drop: "descartan",
    w_no_audience: "la audiencia está vacía",
    w_failed: "la entrega falla",
    w_both: "la audiencia está vacía o la entrega falla",
  },
};

const CSS = `
.hu-page h3.sec { font-size: 15px; margin: 20px 0 6px; padding-top: 12px; border-top: 1px solid var(--divider-color); }
.hu-page .summary { background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; margin: 16px 0 12px; }
.hu-page .summary .sentence { margin: 4px 0; }
.hu-page label.radio { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; cursor: pointer; }
.hu-page label.radio input { margin-top: 4px; width: 20px; height: 20px; }
.hu-page .type-desc { margin-top: 0; }
.hu-page li.dragging { opacity: .4; }
.hu-page li.over { outline: 2px dashed var(--primary-color); }
.hu-page li.drop-end { height: 12px; padding: 0; border: 0; }
.hu-page .handle { cursor: grab; user-select: none; padding: 0 8px; color: var(--secondary-text-color); }
.hu-page .position { min-width: 1.6em; text-align: right; font-weight: 600; color: var(--secondary-text-color); }
.hu-page button.move { min-width: 44px; padding: 0; }
.hu-page li.policy { display: flex; align-items: center; gap: 4px; }
.hu-page li.policy .grow { flex: 1; }
`;

const TYPES = ["escalation", "reminder", "quiet_hours", "away", "fallback", "deliver", "summarize"];
const SEVERITIES = ["success", "info", "warning", "critical"];
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const POLICY_CHANNELS = ["push", "popup", "speak", "persistent", "mail"];
const TARGET_CHANNELS = ["push", "popup", "speak", "mail"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues(type = "escalation") {
  return {
    name: "",
    type,
    severities: [],
    tags: "",
    enabled: true,
    apply: "auto",
    after_minutes: 5,
    channels: [],
    dismiss_acks: false,
    every_minutes: 30,
    max_count: 3,
    from_time: "22:00:00",
    to_time: "07:00:00",
    days: [],
    action: "quiet",
    critical_passes: true,
    max_wait: 0,
    when: "no_audience",
    summary_mode: "every",
    summary_every: 60,
    summary_at: "20:00:00",
    include_critical: false,
    push_audience: "",
    push_recipients: [],
    popup_audience: "",
    popup_recipients: [],
    speak_recipients: [],
  };
}

// The values of the form from a stored policy: the targets are flattened per channel.
export function fromPolicy(policy) {
  const data = policy.data || {};
  const values = { ...blankValues(data.type), name: policy.name };
  for (const key of ["severities", "channels", "days"]) values[key] = [...(data[key] || [])];
  values.tags = (data.tags || []).join(", ");
  values.apply = data.apply === "manual" ? "manual" : "auto";
  for (const key of ["enabled", "dismiss_acks", "critical_passes", "include_critical"]) {
    if (key in data) values[key] = Boolean(data[key]);
  }
  for (const key of ["after_minutes", "every_minutes", "max_count", "max_wait", "summary_every"]) {
    if (data[key] !== undefined) values[key] = data[key];
  }
  for (const key of ["from_time", "to_time", "action", "when", "summary_at"]) {
    if (data[key]) values[key] = data[key];
  }
  if (data.type === "summarize") values.summary_mode = data.summary_at ? "at" : "every";
  for (const [channel, target] of Object.entries(data.targets || {})) {
    if (target.audience) values[`${channel}_audience`] = target.audience;
    if (target.recipients) values[`${channel}_recipients`] = [...target.recipients];
  }
  return values;
}

export function splitTags(text) {
  return [...new Set(String(text || "").split(",").map((tag) => tag.trim()).filter(Boolean))];
}

// What goes to the policy flow: only the fields of the type, targets for the chosen channels only.
export function toFlowData(values) {
  const data = {
    name: String(values.name).trim(),
    type: values.type,
    apply: values.apply === "manual" ? "manual" : "auto",
    // A manual policy has no conditions.
    severities: values.apply === "manual" ? [] : [...values.severities],
    tags: values.apply === "manual" ? [] : splitTags(values.tags),
    enabled: Boolean(values.enabled),
  };
  const targets = () => {
    for (const channel of values.channels.filter((c) => TARGET_CHANNELS.includes(c))) {
      if (values[`${channel}_audience`]) data[`${channel}_audience`] = values[`${channel}_audience`];
      if ((values[`${channel}_recipients`] || []).length) data[`${channel}_recipients`] = [...values[`${channel}_recipients`]];
    }
  };
  switch (values.type) {
    case "escalation":
      Object.assign(data, { after_minutes: values.after_minutes, channels: [...values.channels], dismiss_acks: Boolean(values.dismiss_acks) });
      targets();
      break;
    case "reminder":
      Object.assign(data, { every_minutes: values.every_minutes, max_count: values.max_count, channels: [...values.channels] });
      break;
    case "quiet_hours":
      Object.assign(data, { from_time: values.from_time, to_time: values.to_time, days: [...values.days], action: values.action, critical_passes: Boolean(values.critical_passes) });
      break;
    case "away":
      data.max_wait = values.max_wait || 0;
      break;
    case "fallback":
      Object.assign(data, { when: values.when, channels: [...values.channels] });
      targets();
      break;
    case "deliver":
      data.channels = [...values.channels];
      targets();
      break;
    default:
      data.include_critical = Boolean(values.include_critical);
      if (values.summary_mode === "at") data.summary_at = values.summary_at;
      else data.summary_every = values.summary_every;
  }
  return data;
}

const positive = (n) => Number.isInteger(n) && n >= 1;

// Problems as { field: code }; the codes are the policy flow's own error keys.
export function validate(values, existingNames, ownName) {
  const problems = {};
  const name = String(values.name || "").trim();
  const taken = existingNames.filter((n) => n.toLowerCase() !== String(ownName || "").toLowerCase());
  if (!name) problems.name = "name_required";
  else if (name.toLowerCase() === "none" || taken.some((n) => n.toLowerCase() === name.toLowerCase())) problems.name = "name_exists";
  const needsTargets = ["escalation", "fallback", "deliver"].includes(values.type);
  if (values.type === "escalation" && !positive(values.after_minutes)) problems.after_minutes = "after_required";
  if (values.type === "reminder") {
    if (!positive(values.every_minutes)) problems.every_minutes = "every_required";
    if (!positive(values.max_count)) problems.max_count = "max_required";
  }
  if (values.type === "quiet_hours" && (!values.from_time || !values.to_time)) problems.from_time = "time_invalid";
  else if (values.type === "quiet_hours" && values.from_time === values.to_time) problems.to_time = "window_empty";
  if (values.type === "away" && !(values.max_wait >= 0)) problems.max_wait = "wait_invalid";
  if (values.type === "summarize") {
    if (values.summary_mode === "at" && !values.summary_at) problems.summary_at = "time_invalid";
    if (values.summary_mode !== "at" && !positive(values.summary_every)) problems.summary_every = "every_required";
  }
  if (needsTargets) {
    if (values.channels.length === 0) problems.channels = "channels_required";
    for (const channel of values.channels.filter((c) => TARGET_CHANNELS.includes(c))) {
      const audience = values[`${channel}_audience`];
      const recipients = values[`${channel}_recipients`] || [];
      if (Boolean(audience) === (recipients.length > 0)) problems[`${channel}_target`] = "target_exclusive";
    }
  }
  return problems;
}

// The ids of the list with one moved up or down; unchanged at the ends.
export function moveItem(ids, id, delta) {
  const from = ids.indexOf(id);
  const to = from + delta;
  const next = [...ids];
  if (from < 0 || to < 0 || to >= next.length) return next;
  [next[from], next[to]] = [next[to], next[from]];
  return next;
}

// The ids with `dragId` dropped in front of `targetId`; at the end when the target is null.
export function dropItem(ids, dragId, targetId) {
  if (!ids.includes(dragId) || dragId === targetId) return [...ids];
  const rest = ids.filter((id) => id !== dragId);
  const at = targetId === null ? rest.length : rest.indexOf(targetId);
  if (at < 0) return [...ids];
  rest.splice(at, 0, dragId);
  return rest;
}

// Two policies overlap when some message can match both: an empty list matches any.
export function overlaps(a, b) {
  const meet = (x, y) => x.length === 0 || y.length === 0 || x.some((item) => y.includes(item));
  return meet(a.severities, b.severities) && meet(a.tags, b.tags);
}

// The names the editor lists as a note: in the mode "first" the policies above this one that also
// match some of its messages (they run instead); in the mode "all" the other policies of the same
// type that do. `policies` is the list in order; a policy that is not saved yet goes to the bottom.
export function overlapNames({ values, own, policies, mode }) {
  if (values.apply === "manual") return [];
  const mine = { severities: values.severities, tags: splitTags(values.tags) };
  const at = own ? policies.findIndex((p) => p.subentry_id === own.subentry_id) : policies.length;
  const pool = mode === "first" ? policies.slice(0, at < 0 ? policies.length : at) : policies.filter((p) => p.subentry_id !== own?.subentry_id);
  return pool
    .filter((p) => p.data.apply !== "manual" && p.data.enabled !== false)
    .filter((p) => mode === "first" || p.data.type === values.type)
    .filter((p) => overlaps(mine, { severities: p.data.severities || [], tags: p.data.tags || [] }))
    .map((p) => p.name);
}

// Whether every message that matches `b` also matches `a`: an empty list matches any.
function covers(a, b) {
  const within = (x, y) => x.length === 0 || (y.length > 0 && y.every((item) => x.includes(item)));
  return within(a.severities, b.severities) && within(a.tags, b.tags);
}

// The name of the first policy above this one that matches every message this one matches. In the
// mode "first" such a policy never runs by itself (a call that names it still uses it). `policies`
// is the list in order; manual and disabled policies neither shadow nor are shadowed.
export function shadowedBy(policy, policies) {
  const runs = (p) => p.data.apply !== "manual" && p.data.enabled !== false;
  if (!runs(policy)) return null;
  const filters = (p) => ({ severities: p.data.severities || [], tags: p.data.tags || [] });
  for (const other of policies) {
    if (other.subentry_id === policy.subentry_id) return null;
    if (runs(other) && covers(filters(other), filters(policy))) return other.name;
  }
  return null;
}

export function appliesText(values, t) {
  if (values.apply === "manual") return t.s_applies_manual;
  const tags = splitTags(values.tags);
  if (values.severities.length === 0 && tags.length === 0) return t.s_applies_any;
  const parts = [];
  if (values.severities.length) {
    parts.push(fill(t.s_severity, { severities: values.severities.map((x) => t.severity_names[x]).join(", ") }));
  }
  if (tags.length) parts.push(fill(t.s_tag, { tags: tags.join(", ") }));
  return fill(t.s_applies, { parts: parts.join(t.s_and) });
}

export function sentence(values, t) {
  const applies = appliesText(values, t);
  const channels = values.channels.map((c) => t.channel_names[c]).join(", ") || "—";
  switch (values.type) {
    case "escalation":
      return fill(t.s_escalation, { applies, n: values.after_minutes, channels });
    case "reminder":
      return fill(t.s_reminder, { applies, n: values.every_minutes, m: values.max_count, channels: values.channels.length ? fill(t.s_in_channels, { channels }) : "" });
    case "quiet_hours": {
      const days = values.days.length ? fill(t.s_days, { days: values.days.map((d) => t.days_names[d]).join(", ") }) : "";
      return fill(t.s_quiet_hours, {
        applies,
        from: String(values.from_time).slice(0, 5),
        to: String(values.to_time).slice(0, 5),
        days,
        action: t[`a_${values.action}`],
        critical: values.critical_passes ? t.s_critical_pass : "",
      });
    }
    case "away":
      return fill(t.s_away, { applies, wait: values.max_wait > 0 ? fill(t.s_wait, { n: values.max_wait }) : "" });
    case "fallback":
      return fill(t.s_fallback, { applies, when: t[`w_${values.when}`], channels });
    case "deliver":
      return fill(t.s_deliver, { applies, channels });
    default: {
      const critical = values.include_critical ? t.s_critical_held : "";
      return values.summary_mode === "at"
        ? fill(t.s_summarize_at, { applies, time: String(values.summary_at).slice(0, 5), critical })
        : fill(t.s_summarize_every, { applies, n: values.summary_every, critical });
    }
  }
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own, values }
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  let dragging = null;
  const ordered = () => data.policies.map((p) => p.subentry_id);

  async function saveOrder(ids) {
    try {
      await hass.callWS({ type: "heads_up/policy_order_set", order: ids });
      message = "";
    } catch (err) {
      message = t.order_failed;
    }
    await load();
  }

  function row(policy, index) {
    const values = fromPolicy(policy);
    const first = data.policy_mode !== "all";
    const edit = el("button", { type: "button", textContent: s.common.edit });
    edit.addEventListener("click", () => { message = ""; editing = { own: policy, values }; render(); });
    const shadow = first ? shadowedBy(policy, data.policies) : null;
    const body = el("div", { className: "grow" }, [
      el("strong", { textContent: policy.name }),
      el("span", { className: "badge", textContent: t.types[values.type] || values.type }),
      ...(values.apply === "manual" ? [el("span", { className: "badge", textContent: t.badge_manual })] : []),
      ...(values.enabled ? [] : [el("span", { className: "badge", textContent: t.disabled })]),
      el("div", { className: "sub", textContent: appliesText(values, t) }),
      ...(shadow ? [el("div", { className: "sub shadowed", textContent: fill(t.shadowed, { name: `“${shadow}”` }) })] : []),
    ]);
    const parts = [];
    if (first) {
      const handle = el("span", { className: "handle", textContent: "⠿", title: t.handle });
      handle.setAttribute("aria-hidden", "true");
      const position = el("span", { className: "position", textContent: String(index + 1) });
      position.setAttribute("aria-label", fill(t.position, { n: index + 1 }));
      parts.push(handle, position);
    }
    parts.push(body);
    if (first) {
      const move = (label, glyph, delta, disabled) => {
        const button = el("button", { type: "button", className: "move", textContent: glyph, disabled });
        button.setAttribute("aria-label", `${label}: ${policy.name}`);
        button.addEventListener("click", () => saveOrder(moveItem(ordered(), policy.subentry_id, delta)));
        return button;
      };
      parts.push(move(t.move_up, "↑", -1, index === 0), move(t.move_down, "↓", 1, index === data.policies.length - 1));
    }
    parts.push(edit);
    const li = el("li", { className: `policy${values.enabled ? "" : " dim"}` }, parts);
    if (first) {
      li.draggable = true;
      li.addEventListener("dragstart", (event) => {
        dragging = policy.subentry_id;
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.setData("text/plain", dragging);
        li.classList.add("dragging");
      });
      li.addEventListener("dragend", () => {
        dragging = null;
        li.classList.remove("dragging");
      });
      li.addEventListener("dragover", (event) => {
        if (!dragging) return;
        event.preventDefault();
        li.classList.add("over");
      });
      li.addEventListener("dragleave", () => li.classList.remove("over"));
      li.addEventListener("drop", (event) => {
        event.preventDefault();
        li.classList.remove("over");
        if (dragging) saveOrder(dropItem(ordered(), dragging, policy.subentry_id));
      });
    }
    return li;
  }

  async function setMode(mode) {
    try {
      await hass.callWS({ type: "heads_up/policy_mode_set", mode });
      message = "";
    } catch (err) {
      message = t.order_failed;
    }
    await load();
  }

  function modeBox() {
    const box = el("section", {}, [el("h2", { textContent: t.mode_title })]);
    const choice = el("fieldset", {});
    for (const mode of ["first", "all"]) {
      const input = el("input", { type: "radio", name: "mode", checked: (data.policy_mode || "first") === mode });
      input.addEventListener("change", () => setMode(mode));
      choice.append(el("label", { className: "radio" }, [input, el("span", {}, [el("strong", { textContent: t[`mode_${mode}`] }), el("div", { className: "hint", textContent: t[`mode_${mode}_hint`] })])]));
    }
    box.append(choice, el("div", { className: "hint", textContent: data.policy_mode === "all" ? t.order_all : t.order_first }));
    return box;
  }

  function editor() {
    const { own, values } = editing;
    const existing = data.policies.map((p) => p.name);
    const box = el("section", {}, [el("h2", { textContent: own ? t.editing : t.new })]);
    const again = () => render();

    // Header: always visible. Enabled first, then what the policy is called and what type it is.
    box.append(ui.checkbox(s.common.enabled, values.enabled, (on) => { values.enabled = on; paint(); }));
    box.append(el("div", { className: "hint", textContent: t.enabled_hint }));
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; paint(); })));
    box.append(ui.field(t.type, ui.selectInput(TYPES.map((k) => ({ value: k, label: t.types[k] })), values.type, (v) => { values.type = v; again(); })));
    box.append(el("div", { className: "hint type-desc", textContent: t.type_desc[values.type] }));

    // The sentence and the status come under the buttons, above the stored YAML.
    const words = el("div", { className: "sentence" });
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    const noteUpdaters = [];
    const does = el("div");
    const when = el("div");
    const number = (key, label, min = 1) => does.append(ui.field(label, ui.numberInput(values[key], (v) => { values[key] = v; paint(); }, { min })));
    const channelChips = (label) =>
      does.append(ui.chips(label, POLICY_CHANNELS.map((c) => ({ value: c, label: t.channel_names[c] })), values.channels, (list) => { values.channels = list; again(); }));
    const targetBlocks = () => {
      const labels = { audience: t.target_audience, recipients: t.target_recipients, persistent: t.target_persistent };
      for (const channel of values.channels) {
        does.append(ui.targetBlock(channel, values, data.choices, { ...labels, channel: fill(t.target_channel, { channel: t.channel_names[channel] }) }, (mode) => (mode ? again() : paint())));
      }
    };
    switch (values.type) {
      case "escalation":
        number("after_minutes", t.after);
        channelChips(t.channels);
        targetBlocks();
        does.append(ui.checkbox(t.dismiss_acks, values.dismiss_acks, (on) => { values.dismiss_acks = on; paint(); }));
        does.append(el("div", { className: "hint", textContent: t.ack_note }));
        break;
      case "reminder":
        number("every_minutes", t.every);
        number("max_count", t.max_count);
        channelChips(t.channels_reminder);
        does.append(el("div", { className: "hint", textContent: t.ack_note }));
        break;
      case "quiet_hours":
        does.append(ui.field(t.from, ui.timeInput(values.from_time, (v) => { values.from_time = v; paint(); })));
        does.append(ui.field(t.to, ui.timeInput(values.to_time, (v) => { values.to_time = v; paint(); })));
        does.append(ui.chips(t.days, DAYS.map((d) => ({ value: d, label: t.days_names[d] })), values.days, (list) => { values.days = list; paint(); }));
        does.append(ui.field(t.action, ui.selectInput(["quiet", "wait", "drop"].map((k) => ({ value: k, label: t.actions[k] })), values.action, (v) => { values.action = v; paint(); })));
        does.append(ui.checkbox(t.critical_passes, values.critical_passes, (on) => { values.critical_passes = on; paint(); }));
        break;
      case "away":
        number("max_wait", t.max_wait, 0);
        break;
      case "deliver":
        channelChips(t.channels);
        targetBlocks();
        break;
      case "fallback":
        does.append(ui.field(t.when, ui.selectInput(["no_audience", "failed", "both"].map((k) => ({ value: k, label: t.whens[k] })), values.when, (v) => { values.when = v; paint(); })));
        channelChips(t.channels);
        targetBlocks();
        break;
      default:
        does.append(ui.field(t.summary_mode, ui.selectInput([{ value: "every", label: t.summary_every_mode }, { value: "at", label: t.summary_at_mode }], values.summary_mode, (v) => { values.summary_mode = v; again(); })));
        if (values.summary_mode === "at") does.append(ui.field(t.summary_at, ui.timeInput(values.summary_at, (v) => { values.summary_at = v; paint(); })));
        else number("summary_every", t.summary_every);
        does.append(ui.checkbox(t.include_critical, values.include_critical, (on) => { values.include_critical = on; again(); }));
        if (values.include_critical) does.append(el("div", { className: "hint problems", textContent: t.critical_warning }));
        does.append(el("div", { className: "hint", textContent: t.summarize_note }));
    }

    // When it applies: automatic (conditions) or manual (named in a call).
    const radio = (value, label, hint) => {
      const input = el("input", { type: "radio", name: "apply", checked: values.apply === value });
      input.addEventListener("change", () => { values.apply = value; again(); });
      return el("label", { className: "radio" }, [input, el("span", {}, [el("strong", { textContent: label }), el("div", { className: "hint", textContent: hint })])]);
    };
    const choice = el("fieldset", {}, [el("legend", { textContent: t.apply_label }), radio("auto", t.apply_auto, t.apply_auto_hint), radio("manual", t.apply_manual, t.apply_manual_hint)]);
    when.append(choice);
    if (values.apply === "manual") {
      when.append(el("div", { className: "hint", textContent: t.manual_how }), el("pre", { textContent: `policy: ${String(values.name).trim() || "…"}` }), el("div", { className: "hint", textContent: t.manual_note }));
    } else {
      when.append(ui.chips(t.severities, SEVERITIES.map((k) => ({ value: k, label: t.severity_names[k] })), values.severities, (list) => { values.severities = list; paint(); }));
      when.append(ui.field(t.tags, ui.textInput(values.tags, (v) => { values.tags = v; paint(); })));
      const note = el("div", { className: "hint" });
      const paintNote = () => {
        const names = overlapNames({ values, own, policies: data.policies, mode: data.policy_mode || "first" });
        note.textContent = names.length ? fill((data.policy_mode || "first") === "first" ? t.overlap_first : t.overlap_all, { names: names.join(", ") }) : "";
      };
      paintNote();
      noteUpdaters.push(paintNote);
      when.append(note);
    }

    // Two blocks under a heading each: which messages the policy applies to, then what it does.
    box.append(el("h3", { className: "sec", textContent: t.sec_when }), when, el("h3", { className: "sec", textContent: t.sec_does }), does);

    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", saveIt);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", () => { editing = null; render(); });
    const buttons = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete });
      del.addEventListener("click", remove);
      buttons.append(del);
    }
    box.append(buttons, el("div", { className: "summary" }, [el("strong", { textContent: t.sentence }), words, status]));
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), el("pre", { textContent: ui.toYaml({ name: own.name, ...own.data }) }));
    function paint() {
      const found = validate(values, existing, own?.name);
      const codes = Object.values(found);
      words.textContent = sentence(values, t);
      save.disabled = codes.length > 0;
      status.className = codes.length ? "hint problems" : "hint ok";
      status.textContent = codes.length ? codes.map((c) => ui.errorText(c, ctx.language)).join(" ") : message || s.common.valid;
      noteUpdaters.forEach((update) => update());
    }
    paint();
    return box;
  }

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    if (editing) return void root.append(editor());
    const items = data.policies.length ? data.policies.map(row) : [el("li", { className: "sub", textContent: t.none })];
    if (data.policies.length && data.policy_mode !== "all") {
      const end = el("li", { className: "drop-end" });
      end.addEventListener("dragover", (event) => {
        if (dragging) event.preventDefault();
      });
      end.addEventListener("drop", (event) => {
        event.preventDefault();
        if (dragging) saveOrder(dropItem(ordered(), dragging, null));
      });
      items.push(end);
    }
    const list = el("ul", { className: "list" }, items);
    const add = el("button", { type: "button", className: "primary", textContent: s.common.add });
    add.addEventListener("click", () => { message = ""; editing = { own: null, values: blankValues() }; render(); });
    root.append(modeBox());
    if (message) root.append(el("div", { className: "hint problems", textContent: message }));
    root.append(el("section", {}, [list, add]));
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "policy", own?.subentry_id, toFlowData(values));
    if (!result.ok) {
      message = Object.values(result.errors).map((c) => ui.errorText(c, ctx.language)).join(" ");
      render();
      return;
    }
    editing = null;
    message = "";
    await load();
  }

  async function remove() {
    const { own } = editing;
    if (!window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
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
