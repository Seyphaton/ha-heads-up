// Heads Up panel: the introduction tour (D-121, D-131, D-244). Four steps inside the Overview page:
// what Heads Up does, channels, audiences and policies. Step 2 saves the channel settings it shows
// when it is left; only the last step creates policies (the defaults the admin switches on).
// The Overview mounts it; it is not a dialog.

export const STRINGS = {
  en: {
    title: "Welcome to Heads Up",
    step_of: "Step {n} of {total}",
    steps_label: "Progress of the tour",
    next: "Next",
    back: "Back",
    skip: "Skip the tour",
    step_intro: "Introduction",
    intro_title: "The right message, to the right people, at the right time",
    intro_lead: "Your automations make one call. Heads Up delivers the message the way you set it up here: where it shows up, who gets it, and when it is delivered or escalated.",
    intro_where: "Where",
    intro_who: "Who",
    intro_when: "When",
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
    found_none: "none yet",
    item_quiet: "Quiet hours",
    desc_quiet: "From 22:00 to 07:00 pushes go out without sound and speech is skipped. Messages tagged digest are left to the evening summary. Critical messages get through only when Critical messages is switched on.",
    item_digest: "Evening summary",
    desc_digest: "Messages that your automations tag digest are held and sent as one summary at 20:00. With Critical messages switched on, critical ones are never held. Messages without that tag are not affected.",
    item_critical: "Critical messages",
    item_warnings: "Warning reminders",
    desc_warnings: "A warning that nobody acknowledges is repeated every 30 minutes, at most 3 times.",
    audience: "Push critical messages to",
    speakers: "Speak after 10 minutes on (none: no speech)",
    tts_engine: "Text-to-speech engine for speakers",
    tts_choose: "Choose an engine",
    tts_none: "Home Assistant has no text-to-speech engine. Set one up under Settings > Devices & services, then choose it in Settings > Speech.",
    not_now: "Not now",
    close: "Close",
    created: "Created: {added}.",
    skipped: "Already there or the same as one you have: {skipped}.",
    nothing: "nothing",
    failed: "Could not create the policies. Try again.",
    policies_title: "Policies: when to be loud or quiet",
    recipients_title: "Audiences: who gets it",
    intro_where_text: "Channels decide where a message shows up: a banner, a push, a popup, speech, mail or the bell.",
    intro_who_text: "Audiences decide who gets it: everyone, the admins, whoever is home or the person who left last.",
    intro_when_text: "Policies decide when: stay quiet at night, repeat what nobody acknowledged, hold small things for one summary.",
    intro_foot: "Policies are created only in the last step. The channel settings of step 2 are saved when you leave it. You can come back from Settings.",
    channels_foot: "Banner, push, popup and the bell need nothing here. The Channels page changes how each one looks and sounds.",
    mail_service: "Mail notify service",
    mail_service_none: "Not set (mail stays off)",
    mail_address: "Global address (optional)",
    mail_hint: "Mail is only set up here. No default policy sends it.",
    engine_found: "Speech engine: {engine}",
    save_failed: "Could not save: {error}",
    recipients_lead: "Most calls name an audience, a group of people worked out when the message goes out.",
    aud_everyone: "Everyone",
    aud_admins: "Admins",
    aud_at_home: "At home",
    aud_not_home: "Not home",
    aud_last_to_leave: "Last to leave",
    aud_first_home: "First home",
    aud_what_everyone: "Every person in Home Assistant.",
    aud_what_admins: "People whose Home Assistant user is an administrator.",
    aud_what_at_home: "People who are home right now.",
    aud_what_not_home: "People who are away right now.",
    aud_what_last_to_leave: "The person whose leaving emptied the house. Empty while anyone is home.",
    aud_what_first_home: "The first person back after the house was empty. Empty while nobody is home.",
    aud_example_everyone: "Example: a water leak that concerns the household.",
    aud_example_admins: "Example: a failed backup.",
    aud_example_at_home: "Example: the doorbell. Nobody away needs it.",
    aud_example_not_home: "Example: a window left open while you are out.",
    aud_example_last_to_leave: "Example: the stove is still on after the house emptied.",
    aud_example_first_home: "Example: the alarm needs switching off on arrival.",
    aud_home: "home",
    aud_away: "away",
    aud_nobody: "nobody now",
    aud_left: "Left at {time}",
    aud_arrived: "Arrived at {time}",
    aud_off: "switched off",
    aud_flip: "What does it mean?",
    aud_flip_back: "Who is in it?",
    aud_profiles: "Each person has a profile with their phones and, for mail, an address. Change it under Recipients. Your own audiences are under Audiences.",
    policies_lead: "A policy changes how messages are delivered without touching your automations. Each one belongs to a group.",
    lane_calm: "Keep it calm",
    lane_calm_text: "Holds, quiets or summarizes small messages.",
    lane_through: "Always gets through",
    lane_through_text: "Lets important messages past the calm group.",
    lane_arrive: "Make sure it arrives",
    lane_arrive_text: "Repeats or escalates until someone reacts.",
    lane_rule: "Every fitting policy acts. Where a calm and a loud one fit, the calmer hold counts.",
    rec_title: "Recommended default policies for you:",
    desc_critical: "Critical messages pass quiet hours and summaries for everyone. Each gets an Acknowledge button and is pushed at once as an alarm to the audience below, then again every 10 minutes (3 times). Dismissing counts as acknowledging.",
    speak_after: "With speakers chosen, it is also spoken after 10 minutes.",
    create_one: "Create 1 policy",
    create_many: "Create {n} policies",
  },
  de: {
    title: "Willkommen bei Heads Up",
    step_of: "Schritt {n} von {total}",
    steps_label: "Fortschritt der Tour",
    next: "Weiter",
    back: "Zurück",
    skip: "Tour überspringen",
    step_intro: "Einführung",
    intro_title: "Die richtige Meldung, an die richtigen Leute, zur richtigen Zeit",
    intro_lead: "Deine Automationen machen einen Aufruf. Heads Up stellt die Meldung so zu, wie du es hier einrichtest: wo sie erscheint, wer sie bekommt und wann sie zugestellt oder eskaliert wird.",
    intro_where: "Wo",
    intro_who: "Wer",
    intro_when: "Wann",
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
    found_none: "noch keine",
    item_quiet: "Ruhezeit",
    desc_quiet: "Von 22:00 bis 07:00 gehen Pushes ohne Ton raus und Sprachausgabe entfällt. Meldungen mit dem Tag digest bleiben der Abendzusammenfassung überlassen. Kritische Meldungen kommen nur durch, wenn Kritische Meldungen eingeschaltet ist.",
    item_digest: "Abendzusammenfassung",
    desc_digest: "Meldungen, die deine Automationen mit digest markieren, werden gesammelt und um 20:00 als eine Zusammenfassung gesendet. Mit eingeschalteten Kritischen Meldungen werden kritische nie gesammelt. Meldungen ohne diesen Tag sind nicht betroffen.",
    item_critical: "Kritische Meldungen",
    item_warnings: "Warnungs-Erinnerungen",
    desc_warnings: "Eine Warnung, die niemand bestätigt, wird alle 30 Minuten wiederholt, höchstens 3 Mal.",
    audience: "Kritische Meldungen pushen an",
    speakers: "Nach 10 Minuten sprechen auf (keiner: keine Sprachausgabe)",
    tts_engine: "Text-zu-Sprache-Engine für Lautsprecher",
    tts_choose: "Engine wählen",
    tts_none: "Home Assistant hat keine Text-zu-Sprache-Engine. Richte unter Einstellungen > Geräte & Dienste eine ein und wähle sie dann unter Einstellungen > Sprache.",
    not_now: "Jetzt nicht",
    close: "Schließen",
    created: "Erstellt: {added}.",
    skipped: "Schon vorhanden oder wie eine, die du hast: {skipped}.",
    nothing: "nichts",
    failed: "Die Richtlinien konnten nicht erstellt werden. Versuche es erneut.",
    policies_title: "Richtlinien: wann laut, wann leise",
    recipients_title: "Zielgruppen: wer sie bekommt",
    intro_where_text: "Kanäle bestimmen, wo eine Meldung erscheint: Banner, Push, Popup, Sprache, E-Mail oder die Glocke.",
    intro_who_text: "Zielgruppen bestimmen, wer sie bekommt: alle, die Admins, wer zu Hause ist oder wer zuletzt gegangen ist.",
    intro_when_text: "Richtlinien bestimmen, wann: nachts leise bleiben, wiederholen, was niemand bestätigt hat, Kleinkram zu einer Zusammenfassung sammeln.",
    intro_foot: "Richtlinien werden erst im letzten Schritt angelegt. Die Kanaleinstellungen aus Schritt 2 werden beim Verlassen des Schritts gespeichert. Du kannst über die Einstellungen zurückkommen.",
    channels_foot: "Banner, Push, Popup und die Glocke brauchen hier nichts. Auf der Seite Kanäle änderst du, wie jeder aussieht und klingt.",
    mail_service: "Notify-Dienst für E-Mail",
    mail_service_none: "Nicht gesetzt (E-Mail bleibt aus)",
    mail_address: "Gemeinsame Adresse (optional)",
    mail_hint: "E-Mail wird hier nur eingerichtet. Keine Standardrichtlinie sendet sie.",
    engine_found: "Sprach-Engine: {engine}",
    save_failed: "Speichern ging nicht: {error}",
    recipients_lead: "Die meisten Aufrufe nennen eine Zielgruppe, eine Gruppe von Personen, die beim Versand bestimmt wird.",
    aud_everyone: "Alle",
    aud_admins: "Admins",
    aud_at_home: "Zu Hause",
    aud_not_home: "Unterwegs",
    aud_last_to_leave: "Zuletzt gegangen",
    aud_first_home: "Zuerst zurück",
    aud_what_everyone: "Jede Person in Home Assistant.",
    aud_what_admins: "Personen, deren Home-Assistant-Benutzer Administrator ist.",
    aud_what_at_home: "Personen, die gerade zu Hause sind.",
    aud_what_not_home: "Personen, die gerade unterwegs sind.",
    aud_what_last_to_leave: "Die Person, deren Gehen das Haus geleert hat. Leer, solange jemand zu Hause ist.",
    aud_what_first_home: "Die erste Person zurück, nachdem das Haus leer war. Leer, solange niemand zu Hause ist.",
    aud_example_everyone: "Beispiel: ein Wasserschaden, der den Haushalt betrifft.",
    aud_example_admins: "Beispiel: ein fehlgeschlagenes Backup.",
    aud_example_at_home: "Beispiel: die Türklingel. Wer weg ist, braucht sie nicht.",
    aud_example_not_home: "Beispiel: ein offenes Fenster, während ihr unterwegs seid.",
    aud_example_last_to_leave: "Beispiel: der Herd ist noch an, nachdem das Haus leer ist.",
    aud_example_first_home: "Beispiel: die Alarmanlage muss bei der Ankunft aus.",
    aud_home: "zu Hause",
    aud_away: "unterwegs",
    aud_nobody: "im Moment niemand",
    aud_left: "Gegangen um {time}",
    aud_arrived: "Angekommen um {time}",
    aud_off: "ausgeschaltet",
    aud_flip: "Was bedeutet das?",
    aud_flip_back: "Wer ist drin?",
    aud_profiles: "Jede Person hat ein Profil mit ihren Handys und, für E-Mail, einer Adresse. Ändere es unter Empfänger. Eigene Zielgruppen findest du unter Zielgruppen.",
    policies_lead: "Eine Richtlinie ändert, wie Meldungen zugestellt werden, ohne deine Automationen anzufassen. Jede gehört zu einer Gruppe.",
    lane_calm: "Ruhe halten",
    lane_calm_text: "Hält kleine Meldungen zurück, macht sie leise oder fasst sie zusammen.",
    lane_through: "Kommt immer durch",
    lane_through_text: "Lässt wichtige Meldungen an der Ruhe-Gruppe vorbei.",
    lane_arrive: "Ankunft sicherstellen",
    lane_arrive_text: "Wiederholt oder eskaliert, bis jemand reagiert.",
    lane_rule: "Jede passende Richtlinie wirkt. Passen eine ruhige und eine laute, zählt das ruhigere Zurückhalten.",
    rec_title: "Empfohlene Standardrichtlinien für dich:",
    desc_critical: "Kritische Meldungen kommen für alle an Ruhezeiten und Zusammenfassungen vorbei. Jede bekommt einen Bestätigen-Knopf und geht sofort als Alarm an die Zielgruppe unten, danach alle 10 Minuten erneut (3-mal). Ausblenden zählt als Bestätigen.",
    speak_after: "Mit gewählten Lautsprechern wird sie nach 10 Minuten auch gesprochen.",
    create_one: "1 Richtlinie anlegen",
    create_many: "{n} Richtlinien anlegen",
  },
  fr: {
    title: "Bienvenue dans Heads Up",
    step_of: "Étape {n} sur {total}",
    steps_label: "Progression de la visite",
    next: "Suivant",
    back: "Retour",
    skip: "Passer la visite",
    step_intro: "Introduction",
    intro_title: "Le bon message, aux bonnes personnes, au bon moment",
    intro_lead: "Vos automatisations font un seul appel. Heads Up remet le message selon ce que vous réglez ici : où il apparaît, qui le reçoit, et quand il est livré ou escaladé.",
    intro_where: "Où",
    intro_who: "Qui",
    intro_when: "Quand",
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
    found_none: "aucun pour l'instant",
    item_quiet: "Heures calmes",
    desc_quiet: "De 22:00 à 07:00, les push partent sans son et la voix est ignorée. Les messages étiquetés digest sont laissés au résumé du soir. Les messages critiques ne passent que si Messages critiques est activé.",
    item_digest: "Résumé du soir",
    desc_digest: "Les messages que vos automatisations étiquettent digest sont retenus et envoyés en un résumé à 20:00. Avec Messages critiques activé, les critiques ne sont jamais retenus. Les messages sans cette étiquette ne sont pas concernés.",
    item_critical: "Messages critiques",
    item_warnings: "Rappels d'avertissement",
    desc_warnings: "Un avertissement que personne ne confirme est répété toutes les 30 minutes, au plus 3 fois.",
    audience: "Envoyer les messages critiques à",
    speakers: "Dire après 10 minutes sur (aucun : pas de voix)",
    tts_engine: "Moteur de synthèse vocale pour les haut-parleurs",
    tts_choose: "Choisir un moteur",
    tts_none: "Home Assistant n'a aucun moteur de synthèse vocale. Configurez-en un sous Paramètres > Appareils et services, puis choisissez-le dans Paramètres > Voix.",
    not_now: "Pas maintenant",
    close: "Fermer",
    created: "Créé : {added}.",
    skipped: "Déjà là ou identique à l'une des vôtres : {skipped}.",
    nothing: "rien",
    failed: "Les politiques n'ont pas pu être créées. Réessayez.",
    policies_title: "Politiques : quand être fort ou discret",
    recipients_title: "Audiences : qui le reçoit",
    intro_where_text: "Les canaux décident où un message apparaît : bannière, push, fenêtre, voix, courriel ou la cloche.",
    intro_who_text: "Les audiences décident qui le reçoit : tout le monde, les admins, ceux qui sont là ou la dernière personne partie.",
    intro_when_text: "Les politiques décident quand : rester calme la nuit, répéter ce que personne n'a confirmé, regrouper les petites choses en un résumé.",
    intro_foot: "Les politiques ne sont créées qu'à la dernière étape. Les réglages de canaux de l'étape 2 sont enregistrés quand vous la quittez. Vous pouvez revenir depuis les Réglages.",
    channels_foot: "Bannière, push, fenêtre et la cloche n'ont besoin de rien ici. La page Canaux change leur apparence et leur son.",
    mail_service: "Service notify pour le courriel",
    mail_service_none: "Non défini (le courriel reste désactivé)",
    mail_address: "Adresse commune (facultative)",
    mail_hint: "Le courriel est seulement configuré ici. Aucune politique par défaut ne l'envoie.",
    engine_found: "Moteur vocal : {engine}",
    save_failed: "Enregistrement impossible : {error}",
    recipients_lead: "La plupart des appels nomment une audience, un groupe de personnes déterminé à l'envoi.",
    aud_everyone: "Tout le monde",
    aud_admins: "Admins",
    aud_at_home: "À la maison",
    aud_not_home: "Absents",
    aud_last_to_leave: "Dernier parti",
    aud_first_home: "Premier rentré",
    aud_what_everyone: "Chaque personne de Home Assistant.",
    aud_what_admins: "Les personnes dont l'utilisateur Home Assistant est administrateur.",
    aud_what_at_home: "Les personnes qui sont à la maison en ce moment.",
    aud_what_not_home: "Les personnes qui sont absentes en ce moment.",
    aud_what_last_to_leave: "La personne dont le départ a vidé la maison. Vide tant que quelqu'un est là.",
    aud_what_first_home: "La première personne rentrée après une maison vide. Vide tant que personne n'est là.",
    aud_example_everyone: "Exemple : une fuite d'eau qui concerne le foyer.",
    aud_example_admins: "Exemple : une sauvegarde échouée.",
    aud_example_at_home: "Exemple : la sonnette. Les absents n'en ont pas besoin.",
    aud_example_not_home: "Exemple : une fenêtre ouverte pendant que vous êtes sortis.",
    aud_example_last_to_leave: "Exemple : la cuisinière est encore allumée après le départ de tous.",
    aud_example_first_home: "Exemple : l'alarme est à couper à l'arrivée.",
    aud_home: "présent",
    aud_away: "absent",
    aud_nobody: "personne pour l'instant",
    aud_left: "Parti à {time}",
    aud_arrived: "Arrivé à {time}",
    aud_off: "désactivée",
    aud_flip: "Que signifie-t-elle ?",
    aud_flip_back: "Qui en fait partie ?",
    aud_profiles: "Chaque personne a un profil avec ses téléphones et, pour le courriel, une adresse. Modifiez-le sous Destinataires. Vos propres audiences sont sous Audiences.",
    policies_lead: "Une politique change la façon dont les messages sont remis sans toucher à vos automatisations. Chacune appartient à un groupe.",
    lane_calm: "Rester calme",
    lane_calm_text: "Retient, rend discrets ou résume les petits messages.",
    lane_through: "Passe toujours",
    lane_through_text: "Laisse passer les messages importants malgré le groupe calme.",
    lane_arrive: "S'assurer d'arriver",
    lane_arrive_text: "Répète ou escalade jusqu'à ce que quelqu'un réagisse.",
    lane_rule: "Toute politique qui convient agit. Si une calme et une forte conviennent, la retenue la plus calme compte.",
    rec_title: "Politiques par défaut recommandées pour vous :",
    desc_critical: "Les messages critiques passent les heures calmes et les résumés pour tout le monde. Chacun reçoit un bouton Acquitter et part aussitôt comme alarme vers l'audience ci-dessous, puis toutes les 10 minutes (3 fois). Masquer vaut acquitter.",
    speak_after: "Avec des haut-parleurs choisis, il est aussi dit après 10 minutes.",
    create_one: "Créer 1 politique",
    create_many: "Créer {n} politiques",
  },
  es: {
    title: "Te damos la bienvenida a Heads Up",
    step_of: "Paso {n} de {total}",
    steps_label: "Progreso del recorrido",
    next: "Siguiente",
    back: "Atrás",
    skip: "Omitir el recorrido",
    step_intro: "Introducción",
    intro_title: "El mensaje justo, a las personas justas, en el momento justo",
    intro_lead: "Tus automatizaciones hacen una sola llamada. Heads Up entrega el mensaje según lo que configuras aquí: dónde aparece, quién lo recibe y cuándo se entrega o se escala.",
    intro_where: "Dónde",
    intro_who: "Quién",
    intro_when: "Cuándo",
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
    found_none: "ninguno por ahora",
    item_quiet: "Horas de silencio",
    desc_quiet: "De 22:00 a 07:00 los push salen sin sonido y se omite la voz. Los mensajes con la etiqueta digest se dejan al resumen de la tarde. Los mensajes críticos solo pasan si Mensajes críticos está activado.",
    item_digest: "Resumen de la tarde",
    desc_digest: "Los mensajes que tus automatizaciones etiquetan digest se retienen y se envían como un resumen a las 20:00. Con Mensajes críticos activado, los críticos nunca se retienen. Los mensajes sin esa etiqueta no se ven afectados.",
    item_critical: "Mensajes críticos",
    item_warnings: "Recordatorios de avisos",
    desc_warnings: "Un aviso que nadie confirma se repite cada 30 minutos, como máximo 3 veces.",
    audience: "Enviar los mensajes críticos a",
    speakers: "Decir a los 10 minutos en (ninguno: sin voz)",
    tts_engine: "Motor de texto a voz para los altavoces",
    tts_choose: "Elegir un motor",
    tts_none: "Home Assistant no tiene ningún motor de texto a voz. Configura uno en Ajustes > Dispositivos y servicios y elígelo después en Ajustes > Voz.",
    not_now: "Ahora no",
    close: "Cerrar",
    created: "Creado: {added}.",
    skipped: "Ya existe o es igual a una tuya: {skipped}.",
    nothing: "nada",
    failed: "No se pudieron crear las políticas. Inténtalo de nuevo.",
    policies_title: "Políticas: cuándo ser fuerte o discreto",
    recipients_title: "Audiencias: quién lo recibe",
    intro_where_text: "Los canales deciden dónde aparece un mensaje: banner, push, ventana, voz, correo o la campana.",
    intro_who_text: "Las audiencias deciden quién lo recibe: todos, los admins, quien está en casa o quien salió el último.",
    intro_when_text: "Las políticas deciden cuándo: callar de noche, repetir lo que nadie confirmó, juntar lo pequeño en un resumen.",
    intro_foot: "Las políticas se crean solo en el último paso. Los ajustes de canales del paso 2 se guardan al salir de él. Puedes volver desde Ajustes.",
    channels_foot: "Banner, push, ventana y la campana no necesitan nada aquí. La página Canales cambia cómo se ve y suena cada uno.",
    mail_service: "Servicio notify para el correo",
    mail_service_none: "Sin definir (el correo sigue apagado)",
    mail_address: "Dirección común (opcional)",
    mail_hint: "El correo solo se configura aquí. Ninguna política por defecto lo envía.",
    engine_found: "Motor de voz: {engine}",
    save_failed: "No se pudo guardar: {error}",
    recipients_lead: "La mayoría de las llamadas nombran una audiencia, un grupo de personas que se calcula al enviar.",
    aud_everyone: "Todos",
    aud_admins: "Admins",
    aud_at_home: "En casa",
    aud_not_home: "Fuera",
    aud_last_to_leave: "Último en salir",
    aud_first_home: "Primero en llegar",
    aud_what_everyone: "Cada persona de Home Assistant.",
    aud_what_admins: "Personas cuyo usuario de Home Assistant es administrador.",
    aud_what_at_home: "Personas que están en casa ahora.",
    aud_what_not_home: "Personas que están fuera ahora.",
    aud_what_last_to_leave: "La persona cuya salida vació la casa. Vacía mientras alguien esté en casa.",
    aud_what_first_home: "La primera persona que vuelve con la casa vacía. Vacía mientras nadie esté en casa.",
    aud_example_everyone: "Ejemplo: una fuga de agua que afecta al hogar.",
    aud_example_admins: "Ejemplo: una copia de seguridad fallida.",
    aud_example_at_home: "Ejemplo: el timbre. Quien está fuera no lo necesita.",
    aud_example_not_home: "Ejemplo: una ventana abierta mientras estáis fuera.",
    aud_example_last_to_leave: "Ejemplo: la cocina sigue encendida tras salir todos.",
    aud_example_first_home: "Ejemplo: hay que apagar la alarma al llegar.",
    aud_home: "en casa",
    aud_away: "fuera",
    aud_nobody: "nadie ahora",
    aud_left: "Salió a las {time}",
    aud_arrived: "Llegó a las {time}",
    aud_off: "desactivada",
    aud_flip: "¿Qué significa?",
    aud_flip_back: "¿Quién está dentro?",
    aud_profiles: "Cada persona tiene un perfil con sus teléfonos y, para el correo, una dirección. Cámbialo en Destinatarios. Tus propias audiencias están en Audiencias.",
    policies_lead: "Una política cambia cómo se entregan los mensajes sin tocar tus automatizaciones. Cada una pertenece a un grupo.",
    lane_calm: "Mantener la calma",
    lane_calm_text: "Retiene, silencia o resume los mensajes pequeños.",
    lane_through: "Siempre pasa",
    lane_through_text: "Deja pasar los mensajes importantes por el grupo tranquilo.",
    lane_arrive: "Asegurar que llega",
    lane_arrive_text: "Repite o escala hasta que alguien reaccione.",
    lane_rule: "Toda política que encaja actúa. Si encajan una tranquila y una fuerte, cuenta la retención más tranquila.",
    rec_title: "Políticas por defecto recomendadas para ti:",
    desc_critical: "Los mensajes críticos pasan las horas de silencio y los resúmenes para todos. Cada uno recibe un botón Confirmar y se envía de inmediato como alarma a la audiencia de abajo, y de nuevo cada 10 minutos (3 veces). Descartar cuenta como confirmar.",
    speak_after: "Con altavoces elegidos, también se dice a los 10 minutos.",
    create_one: "Crear 1 política",
    create_many: "Crear {n} políticas",
  },
};

// The items, in the order their policies are created; every policy that fits acts (DESIGN §25.9).
export const ITEMS = ["critical", "warnings", "digest", "quiet"];
export const STEPS = ["intro", "channels", "audiences", "policies"];
export const BUILTIN_AUDIENCES = ["everyone", "admins", "at_home", "not_home", "last_to_leave", "first_home"];
const CHANNEL_ORDER = ["banner", "push", "popup", "speak", "persistent", "mail"];
// The groups of DESIGN §25 each default belongs to.
export const ITEM_LANES = { critical: ["through", "arrive"], warnings: ["arrive"], digest: ["calm"], quiet: ["calm"] };

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

// The call to heads_up/welcome_apply for the state of the tour: only the switched-on items.
export function payloadFor(state) {
  const items = ITEMS.filter((id) => state.on[id]);
  const payload = { type: "heads_up/welcome_apply", items };
  if (items.includes("critical")) {
    payload.audience = state.audience;
    payload.speakers = [...state.speakers];
  }
  if (state.ttsEngine) payload.tts_engine = state.ttsEngine;
  return payload;
}

// How many policies Create makes: Critical makes three, four with speakers (the escalation to speech).
export function policyCount(state) {
  let n = 0;
  if (state.on.critical) n += state.speakers.length ? 4 : 3;
  for (const id of ["warnings", "digest", "quiet"]) if (state.on[id]) n += 1;
  return n;
}

export function createLabel(n, t) {
  return n === 1 ? t.create_one : fill(t.create_many, { n });
}

// What leaving step 2 saves, and only what changed: the mail service and global address through
// `heads_up/channels_set`, the speech engine through `heads_up/settings_set`.
export function channelChanges(state, saved) {
  const calls = [];
  const mail = {};
  if (state.mailService !== saved.mailService) mail.mail_service = state.mailService;
  if (state.mailAddress !== saved.mailAddress) mail.mail_global_address = state.mailAddress;
  if (Object.keys(mail).length) calls.push({ type: "heads_up/channels_set", ...mail });
  if (state.ttsEngine !== saved.ttsEngine) calls.push({ type: "heads_up/settings_set", speak_tts_entity: state.ttsEngine });
  return calls;
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
    speakers: (config.choices?.speakers || []).length,
  };
}

// The line under a channel on the channels step, or "" for a channel that needs nothing found.
export function channelStatus(channel, summary, t) {
  if (!summary) return "";
  if (channel === "push") return fill(t.found_push, { n: summary.devices || t.found_none });
  if (channel === "speak") return fill(t.found_speak, { n: summary.speakers || t.found_none });
  return "";
}

// The note on an audience card: when the house emptied or filled, from the stored time.
export function audienceNote(audience, t, locale) {
  if (!audience.at) return "";
  const time = new Date(audience.at).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
  return fill(audience.key === "last_to_leave" ? t.aud_left : t.aud_arrived, { time });
}

// The people of an audience card with their home mark, by name.
export function audienceMembers(audience, people) {
  const byId = Object.fromEntries((people || []).map((p) => [p.person, p]));
  return audience.members.map((m) => ({ name: byId[m.person]?.name || m.person, home: Boolean(byId[m.person]?.home) }));
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-tour { background: var(--card-background-color); border: 1px solid var(--divider-color); border-left: 4px solid var(--primary-color); border-radius: 12px; padding: 20px 24px; margin-bottom: 16px; }
.hu-tour h2 { margin: 0 0 4px; font-size: 22px; }
.hu-tour h3 { margin: 16px 0 4px; font-size: 16px; }
.hu-tour p { margin: 4px 0 8px; line-height: 1.5; }
.hu-tour .eyebrow { color: var(--secondary-text-color); font-size: 13px; margin-bottom: 12px; }
.hu-tour ol.steps { display: flex; gap: 6px; margin: 6px 0 0; padding: 0; list-style: none; flex-wrap: wrap; }
.hu-tour ol.steps li { display: flex; align-items: center; gap: 6px; padding: 2px 10px; border-radius: 12px; border: 1px solid var(--divider-color); font-size: 13px; }
.hu-tour ol.steps li.now { border-color: var(--primary-color); font-weight: 600; }
.hu-tour ol.steps li.done::before { content: "✓"; color: var(--primary-color); }
.hu-tour .hint, .hu-overview .hu-tour .hint { display: block; background: none; padding: 0; border-radius: 0; color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; line-height: 1.45; }
.hu-tour .intro-foot, .hu-overview .hu-tour .intro-foot { display: block; background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; margin: 8px 0; color: var(--secondary-text-color); font-size: 13px; }
.hu-tour .lead { font-size: 16px; }
.hu-tour .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin: 12px 0; }
.hu-tour .mini { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; }
.hu-tour .mini strong { display: block; margin-bottom: 2px; }
.hu-tour .mini .found { margin-top: 6px; font-size: 13px; }
.hu-tour .mini .setting { margin-top: 8px; }
.hu-tour button.card { text-align: left; min-height: 96px; padding: 10px 12px; border: 1px solid var(--divider-color); border-radius: 8px; background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; display: flex; flex-direction: column; gap: 4px; }
.hu-tour button.card:hover { border-color: var(--primary-color); }
.hu-tour button.card .name { font-weight: 600; }
.hu-tour button.card .person { font-size: 14px; }
.hu-tour button.card .flip { margin-top: auto; font-size: 12px; color: var(--primary-color); }
.hu-tour .item { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; }
.hu-tour .badges { display: inline-flex; gap: 6px; flex-wrap: wrap; margin-left: 8px; }
.hu-tour .badge { font-size: 12px; font-weight: 400; padding: 1px 8px; border-radius: 10px; border: 1px solid var(--divider-color); color: var(--secondary-text-color); }
.hu-tour label.inline { display: flex; align-items: center; gap: 10px; min-height: 48px; font-weight: 600; flex-wrap: wrap; }
.hu-tour input[type=checkbox] { width: 22px; height: 22px; }
.hu-tour label.field { display: flex; flex-direction: column; gap: 4px; margin: 8px 0; }
.hu-tour input[type=text], .hu-tour select { min-height: 40px; max-width: 100%; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; box-sizing: border-box; }
.hu-tour fieldset { border: 1px solid var(--divider-color); border-radius: 8px; max-height: 160px; overflow: auto; margin: 8px 0; }
.hu-tour legend { color: var(--secondary-text-color); font-size: 13px; }
.hu-tour button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-tour button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-tour button.link { border: none; color: var(--secondary-text-color); text-decoration: underline; padding: 0 8px; }
.hu-tour button:focus-visible, .hu-tour select:focus-visible, .hu-tour input:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-tour .row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; align-items: center; }
.hu-tour .row .grow { flex: 1; }
.hu-tour .error { color: var(--error-color); margin-top: 8px; }
`;

// Mounts the tour in `container`. Resolves to { destroy } or null when the tour should not show
// (already seen and not asked for). `ctx.force` shows it anyway; `ctx.onClose()` runs when it ends.
export async function mount(container, ctx) {
  const { t, hass, ui } = ctx;
  const data = await hass.callWS({ type: "heads_up/welcome_get" });
  if (!ctx.force && !data.show) return null;
  const config = await hass.callWS({ type: "heads_up/panel_config" }).catch(() => null);
  const summary = setupSummary(config);
  const audiences = await hass.callWS({ type: "heads_up/panel_audiences" }).catch(() => null);
  const saved = { mailService: data.mail_service || "", mailAddress: data.mail_global_address || "", ttsEngine: data.tts_engine || "" };
  const state = {
    on: Object.fromEntries(ITEMS.map((id) => [id, true])),
    audience: data.default_audience,
    speakers: [],
    ...saved,
    step: 0,
    flipped: new Set(),
  };
  const root = el("section", { className: "hu-tour" });
  root.setAttribute("aria-label", t.title);
  container.append(el("style", { textContent: CSS }), root);
  let seen = !data.show;
  let message = "";
  let done = false;

  // The first opening counts as seen once the admin closes, skips or finishes it, so it does not
  // return every time. Creating policies marks it seen on the server.
  const markSeen = async () => {
    if (!seen) await hass.callWS({ type: "heads_up/welcome_apply", items: [] }).catch(() => {});
    seen = true;
  };
  const end = async () => {
    await markSeen();
    root.remove();
    ctx.onClose?.();
  };

  const button = (text, onClick, className = "") => {
    const node = el("button", { type: "button", textContent: text, className });
    node.addEventListener("click", onClick);
    return node;
  };
  // Leaving step 2 saves its settings, only those that changed; an error keeps the step open.
  async function saveChannels() {
    for (const call of channelChanges(state, saved)) {
      try {
        await hass.callWS(call);
      } catch (err) {
        message = fill(t.save_failed, { error: (err && err.message) || String(err) });
        return false;
      }
    }
    Object.assign(saved, { mailService: state.mailService, mailAddress: state.mailAddress, ttsEngine: state.ttsEngine });
    return true;
  }
  const go = async (step) => {
    message = "";
    if (state.step === 1 && !(await saveChannels())) return render();
    state.step = step;
    render();
    root.querySelector("h2")?.focus();
  };

  function header() {
    const list = el("ol", { className: "steps" });
    list.setAttribute("aria-label", t.steps_label);
    const names = [t.intro_title, t.channels_title, t.recipients_title, t.policies_title];
    STEPS.forEach((id, i) => {
      const item = el("li", { className: i < state.step ? "done" : i === state.step ? "now" : "", textContent: `${i + 1}. ${i === 0 ? t.step_intro : names[i].split(/[:：]/)[0].trim()}` });
      if (i === state.step) item.setAttribute("aria-current", "step");
      list.append(item);
    });
    const top = el("div", { className: "eyebrow" }, [el("span", { textContent: fill(t.step_of, { n: state.step + 1, total: STEPS.length }) }), list]);
    const title = state.step === 0 ? t.title : names[state.step];
    const h2 = el("h2", { textContent: title, tabIndex: -1 });
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
    out.push(grid, el("div", { className: "intro-foot", textContent: t.intro_foot }));
    out.push(nav(button(t.skip, end, "link"), button(t.next, () => go(1), "primary")));
    return out;
  }

  // Step 2: what a channel needs to work. Mail and speech have a setting; the rest show what was found.
  function stepChannels() {
    const out = [el("p", { textContent: t.channels_lead })];
    const grid = el("div", { className: "grid" });
    const engines = data.tts_engines || [];
    for (const channel of CHANNEL_ORDER) {
      const found = channelStatus(channel, summary, t);
      const box = el("div", { className: "mini" }, [el("strong", { textContent: ctx.s.channel[channel] || channel }), el("span", { textContent: t[`ch_${channel}`] })]);
      if (found) box.append(el("div", { className: "found", textContent: found }));
      if (channel === "mail") {
        const services = data.notify_services || [];
        const options = [{ value: "", label: t.mail_service_none }, ...services.map((n) => ({ value: n, label: n }))];
        if (state.mailService && !services.includes(state.mailService)) options.push({ value: state.mailService, label: state.mailService });
        box.append(
          el("div", { className: "setting" }, [
            ui.field(t.mail_service, ui.selectInput(options, state.mailService, (v) => { state.mailService = v; })),
            ui.field(t.mail_address, ui.textInput(state.mailAddress, (v) => { state.mailAddress = v.trim(); }, { maxLength: 254 })),
            el("div", { className: "hint", textContent: t.mail_hint }),
          ]),
        );
      }
      if (channel === "speak") {
        const setting = el("div", { className: "setting" });
        if (engines.length === 0) setting.append(el("div", { className: "hint", textContent: t.tts_none }));
        else if (engines.length === 1 || (state.ttsEngine && engines.includes(state.ttsEngine))) {
          setting.append(el("div", { className: "found", textContent: fill(t.engine_found, { engine: state.ttsEngine || engines[0] }) }));
        } else {
          setting.append(ui.field(t.tts_engine, ui.selectInput([{ value: "", label: t.tts_choose }, ...engines.map((e) => ({ value: e, label: e }))], state.ttsEngine, (v) => { state.ttsEngine = v; })));
        }
        box.append(setting);
      }
      grid.append(box);
    }
    out.push(grid, el("div", { className: "hint", textContent: t.channels_foot }));
    if (message) out.push(el("div", { className: "error", role: "alert", textContent: message }));
    out.push(nav(button(t.next, () => go(2), "primary")));
    return out;
  }

  // Step 3: the six built-in audiences with who is in them now; a click turns a card over.
  function stepAudiences() {
    const out = [el("p", { textContent: t.recipients_lead })];
    const grid = el("div", { className: "grid" });
    const list = audiences?.audiences?.length ? audiences.audiences : BUILTIN_AUDIENCES.map((key) => ({ key, enabled: true, members: [], at: null }));
    for (const audience of list) {
      const back = state.flipped.has(audience.key);
      const card = el("button", { type: "button", className: "card" });
      card.setAttribute("aria-pressed", String(back));
      card.append(el("span", { className: "name", textContent: t[`aud_${audience.key}`] || audience.key }));
      if (back) {
        card.append(el("span", { textContent: t[`aud_what_${audience.key}`] }), el("span", { className: "hint", textContent: t[`aud_example_${audience.key}`] }));
      } else {
        const members = audienceMembers(audience, audiences?.people);
        if (!members.length) card.append(el("span", { className: "person hint", textContent: t.aud_nobody }));
        for (const m of members) card.append(el("span", { className: "person", textContent: `${m.name} · ${m.home ? t.aud_home : t.aud_away}` }));
        const note = audienceNote(audience, t, ctx.language);
        if (note) card.append(el("span", { className: "hint", textContent: note }));
        if (!audience.enabled) card.append(el("span", { className: "hint", textContent: t.aud_off }));
      }
      card.append(el("span", { className: "flip", textContent: back ? t.aud_flip_back : t.aud_flip }));
      card.addEventListener("click", () => {
        if (state.flipped.has(audience.key)) state.flipped.delete(audience.key);
        else state.flipped.add(audience.key);
        render();
      });
      grid.append(card);
    }
    out.push(grid, el("p", { className: "hint", textContent: t.aud_profiles }), nav(button(t.next, () => go(3), "primary")));
    return out;
  }

  function stepPolicies() {
    const out = [el("p", { textContent: t.policies_lead })];
    const lanes = el("div", { className: "grid" });
    for (const lane of ["calm", "through", "arrive"]) lanes.append(el("div", { className: "mini" }, [el("strong", { textContent: t[`lane_${lane}`] }), el("span", { textContent: t[`lane_${lane}_text`] })]));
    out.push(lanes, el("div", { className: "hint", textContent: t.lane_rule }), el("h3", { textContent: t.rec_title }));
    ITEMS.forEach((id) => {
      const box = el("input", { type: "checkbox", checked: state.on[id] });
      box.addEventListener("change", () => {
        state.on[id] = box.checked;
        render();
      });
      const badges = el("span", { className: "badges" }, ITEM_LANES[id].map((lane) => el("span", { className: "badge", textContent: t[`lane_${lane}`] })));
      const item = el("div", { className: "item" }, [el("label", { className: "inline" }, [box, el("span", { textContent: t[`item_${id}`] }), badges]), el("div", { className: "hint", textContent: t[`desc_${id}`] })]);
      if (id === "critical" && state.on.critical) {
        item.append(ui.field(t.audience, ui.selectInput(data.audiences.map((n) => ({ value: n, label: n })), state.audience, (v) => { state.audience = v; })));
        if (data.speakers.length) {
          item.append(el("div", { className: "hint", textContent: t.speak_after }));
          item.append(ui.chips(t.speakers, data.speakers.map((id2) => ({ value: id2, label: ui.recipientLabel(id2, data) })), state.speakers, (list) => { state.speakers = list; render(); }, true));
        }
      }
      out.push(item);
    });
    const create = button(createLabel(policyCount(state), t), async () => {
      try {
        const result = await hass.callWS(payloadFor(state));
        seen = true;
        done = true;
        message = resultText(result, t);
      } catch (err) {
        message = t.failed;
      }
      render();
    }, "primary");
    create.disabled = policyCount(state) === 0;
    out.push(nav(button(t.not_now, end), create));
    if (message) out.push(el("div", { className: "hint", role: "status", textContent: message }));
    return out;
  }

  function render() {
    if (done) {
      const closeButton = button(t.close, end, "primary");
      root.replaceChildren(el("h2", { textContent: t.title }), el("p", { textContent: message }), el("div", { className: "row" }, [closeButton]));
      closeButton.focus();
      return;
    }
    ui?.lockHeight?.(root);
    root.replaceChildren(...header(), ...[stepIntro, stepChannels, stepAudiences, stepPolicies][state.step]());
  }
  render();
  return { destroy: () => root.remove() };
}
