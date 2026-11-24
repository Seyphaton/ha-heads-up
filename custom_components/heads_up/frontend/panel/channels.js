// Heads Up panel: Channels page (D-119): one row per channel with its settings.

export const STRINGS = {
  en: {
    title: "Channels",
    banner: "Banner",
    banner_snooze: "Snooze choices on the banner",
    banner_snooze_hint: "Used when a call or watch rule sets no snooze choices of its own. Whether a message can be snoozed, and the dismiss settings, are under Settings, Messages: they apply to banner, push and popup. The look of the card is set in the card's options.",
    snooze_time: "Snooze time on push and popup (minutes)",
    snooze_time_hint: "1–1440. The Snooze button of the push and of the popup snoozes for this time. It is the same setting on the Push and Popup rows.",
    bad_snooze_time: "The snooze time is a whole number of minutes from 1 to 1440.",
    snooze_summary: "Snooze {time}",
    styles_label: "Popup by severity",
    styles_hint: "Set on the Severities page.",
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 hour", "120": "2 hours", "240": "4 hours", "480": "8 hours", "1440": "24 hours"},
    minutes_n: "{n} minutes",
    no_choices: "no snooze choices",
    col_channel: "Channel",
    col_settings: "Settings",
    sticky_on: "kept after a tap",
    android: "Android channel {id}",
    ha_language: "Home Assistant language",
    mail_off: "Off",
    global_to: "global address {a}",
    edit: "Edit {name}",
    changed: "changed",
    severities_note: "The push level and the popup style of each severity are set on the Severities page.",
    severities_link: "Severities",
    intro: "How each channel works for every message. Select a channel to change it.",
    push: "Push",
    popup: "Popup",
    speech: "Speech",
    severities: { passive: "Passive", info: "Info", warning: "Warning", critical: "Critical" },
    levels: { passive: "Passive (no sound)", normal: "Normal", "time-sensitive": "Time sensitive", critical: "Critical (alarm)" },
    styles: { card: "Corner, bottom right", card_bottom_left: "Corner, bottom left", card_top_right: "Corner, top right", card_top_left: "Corner, top left", modal: "Centered window", off: "Off" },
    push_level: "Push level when the severity is {severity}",
    popup_style: "Popup when the severity is {severity}",
    critical_note: "The level critical is an alarm on both platforms. iOS: the critical alert; it needs the app's permission, plays a sound even in silent mode and cannot be replaced or grouped. Android: the alarm channel; it sounds even in vibrate and silent mode and is delivered at once. Do Not Disturb is only overridden if you allow it for that channel in the Android settings. Time sensitive is delivered at once on Android too.",
    ha_language_named: "Home Assistant language ({name})",
    no_engine_languages: "Choose a text-to-speech engine under Settings, Speech to pick from its languages. Until then, type a language code such as en-US, or leave it empty for the Home Assistant language.",
    lockscreen: "Lock-screen text",
    lockscreens: { full: "Title and text", title_only: "Title only", generic: "Generic text" },
    buttons_note: "Buttons: Snooze and Dismiss. Acknowledge is added when an escalation or reminder policy applies.",
    sticky: "Keep the notification after a tap (Android)",
    severity_look: "Use severity icon & color for push notifications",
    severity_look_note: "Uses the severity's icon and color for each push notification. A message can set its own color and icon. Turned off, a push uses the Home Assistant icon.",
    channel_id: "Android channel name",
    channel_id_note: "Android keeps the first importance of a channel, so each level has its own channel named <name>_<level>.",
    language: "Spoken language",
    speech_note: "Speech uses announce when the player supports it. The volume is set under Settings, Speech volume. Assist satellites speak in the language of their own voice assistant.",
    save: "Save",
    saved: "Saved.",
    failed: "Could not save. Try again.",
    valid: "No problems.",
    bad_channel_id: "The channel name uses lower-case letters, digits and underscores, up to 40 characters.",
    progress_interval: "Seconds between two progress updates (1 to 300)",
    progress_interval_note: "Least time between two pushes of one message with a progress bar. A message can set its own with progress.interval. The Companion app and iOS throttle frequent updates; 5 seconds is a safe start.",
    bad_progress_interval: "The progress interval is a whole number of seconds from 1 to 300.",
    mail: "Mail",
    persistent: "Persistent Notification",
    persistent_summary: "No settings",
    persistent_none: "No configuration is available for this channel. It adds the message to Home Assistant's notification list, the bell in the sidebar, and needs no target.",
    inbox: "Inbox",
    inbox_summary: "Kept for {months} months",
    inbox_summary_all: "Kept for {months} months · all notifications",
    inbox_intro: "Items of the inbox channel: one per message and person, kept across restarts. The inbox card and the sensor of each person show them.",
    inbox_retention: "Months to keep inbox items",
    inbox_retention_note: "1–36. Older items are removed, and each person keeps at most 2000 items. The text of an item is stored in plain text, in backups too.",
    inbox_reminder: "A reminder marks a read item unread again",
    inbox_reminder_note: "On: a reminder or an escalation that reaches a person who already has the item brings it back to the unread count. Off: it only adds a line to the timeline.",
    inbox_all: "Add an optional \"Show all notifications\" section to the inbox",
    inbox_all_note: "Saves a copy of every notification per person in the tab All notifications of the inbox, for example one received by mail or spoken on a speaker (listed for the people at home). A copy is history: it is read and not counted. The text of every notification is stored in plain text, in backups too. Off: only messages sent to the inbox are kept.",
    inbox_messages: "Let people send short messages to each other",
    inbox_messages_note: "Any person can write to other people from the inbox card. A message is plain text up to 1000 characters, always has the severity Info, and goes to the inbox and, if the sender picks them, to push and popup. Each person can send 10 messages per minute. What each recipient accepts and your policies still apply.",
    inbox_summary_messages: " · messages between people",
    inbox_info: "{items} items for {people} people, the oldest from {oldest}.",
    inbox_empty: "No inbox items are stored.",
    inbox_clear: "Clear inbox",
    inbox_confirm: "Delete every item of every person's inbox? This cannot be undone.",
    inbox_cleared: "The inbox was cleared.",
    inbox_failed: "Could not clear the inbox: {error}",
    bad_retention: "The retention is a whole number of months from 1 to 36.",
    lbl_speak_max_length: "Spoken text: longest (characters)",
    note_speak_max_length: "Longer texts are cut at a word and end with an ellipsis.",
    lbl_speak_cooldown_seconds: "Spoken text: repeat pause (seconds)",
    note_speak_cooldown_seconds: "The same text is not spoken again on the same speaker within this time. 0: always speak.",
    lbl_speak_tts_entity: "Text-to-speech engine",
    note_speak_tts_entity: "The engine that speaks on media players. Empty: the only text-to-speech entity, if there is exactly one.",
    lbl_speak_restore_volume: "Put the volume back after speaking",
    note_speak_restore_volume: "A speaker whose volume Heads Up changed gets its earlier volume back once the message was said, unless someone changed the volume meanwhile. Sonos speakers keep their volume and say the message at the chosen level. Off: the speaker stays at the speech volume.",
    lbl_speak_severity_volume: "Volume by severity (percent)",
    note_speak_severity_volume: "0–100 per severity. Empty: the time of day decides. A volume in the action call comes first.",
    lbl_speak_volume_bands: "Volume by time of day",
    note_speak_volume_bands: "Up to 4 bands, each with a start, an end and a volume in percent. A band from 22:00 to 07:00 runs over midnight. Bands must not overlap. Outside every band the volume is not changed.",
    lbl_rate_per_device_per_minute: "Pushes per device per minute",
    note_rate_per_device_per_minute: "1–600. A push over the cap is skipped; critical messages are never held back.",
    lbl_rate_total_per_minute: "Deliveries per minute, all devices",
    note_rate_total_per_minute: "1–6000. A push over the cap is skipped; critical messages are never held back.",
    tts_auto: "Automatic",
    range: "{field} must be between {min} and {max}.",
    band_from: "From",
    band_to: "To",
    band_volume: "Volume (%)",
    band_add: "Add band",
    band_remove: "Remove",
    bands_invalid: "Each band needs a start and an end (HH:MM) and a volume from 0 to 100.",
    bands_too_many: "At most 4 bands.",
    bands_empty: "A band needs a start different from its end.",
    bands_overlap: "Bands must not overlap.",
    severity_volume_invalid: "Give a volume from 0 to 100 for passive, info, warning or critical.",
    mail_intro: "Mail calls a notify service once per recipient with a subject and a body. A person's address is set under Recipients, where Mail must be switched on for them.",
    mail_service: "Notify service",
    mail_service_none: "None (mail is off)",
    mail_global_address: "Global address",
    mail_global_note: "Optional. Not tied to a person: name Global address as a recipient to send to it. It is never used for a person without an address.",
    mail_subject: "Subject",
    mail_body: "Body",
    mail_placeholders: "Placeholders: {severity} (for example Critical), {title} (the title, or the message when there is none), {message}, {person} (the person's name, empty for the Global address), {person_id} (the part of the person's entity ID after person., for example philip; lower case), {id}, {tag}.",
    bad_mail_subject: "The subject needs text, up to 200 characters, and may use only the placeholders listed.",
    bad_mail_body: "The body needs text, up to 2000 characters, and may use only the placeholders listed.",
    bad_mail_address: "The address can have at most 254 characters.",
  },
  de: {
    title: "Kanäle",
    banner: "Banner",
    banner_snooze: "Auswahl beim Zurückstellen im Banner",
    banner_snooze_hint: "Gilt, wenn ein Aufruf oder eine Überwachungsregel keine eigene Auswahl angibt. Ob eine Meldung zurückgestellt werden kann und die Einstellungen zum Schließen stehen unter Einstellungen, Meldungen: Sie gelten für Banner, Push und Popup. Das Aussehen der Karte legst du in den Optionen der Karte fest.",
    snooze_time: "Zurückstellzeit bei Push und Popup (Minuten)",
    snooze_time_hint: "1–1440. Die Schaltfläche Zurückstellen von Push und Popup stellt für diese Zeit zurück. Es ist dieselbe Einstellung in den Zeilen Push und Popup.",
    bad_snooze_time: "Die Zurückstellzeit ist eine ganze Zahl von 1 bis 1440 Minuten.",
    snooze_summary: "Zurückstellen {time}",
    styles_label: "Popup nach Schweregrad",
    styles_hint: "Wird auf der Seite Schweregrade festgelegt.",
    minutes: {"5": "5 Minuten", "15": "15 Minuten", "30": "30 Minuten", "60": "1 Stunde", "120": "2 Stunden", "240": "4 Stunden", "480": "8 Stunden", "1440": "24 Stunden"},
    minutes_n: "{n} Minuten",
    no_choices: "keine Auswahl beim Zurückstellen",
    col_channel: "Kanal",
    col_settings: "Einstellungen",
    sticky_on: "bleibt nach Tippen",
    android: "Android-Kanal {id}",
    ha_language: "Sprache von Home Assistant",
    mail_off: "Aus",
    global_to: "globale Adresse {a}",
    edit: "{name} bearbeiten",
    changed: "geändert",
    severities_note: "Push-Stufe und Popup-Stil jedes Schweregrads stehen auf der Seite Schweregrade.",
    severities_link: "Schweregrade",
    intro: "Wie jeder Kanal für alle Meldungen arbeitet. Wähle einen Kanal, um ihn zu ändern.",
    push: "Push",
    popup: "Popup",
    speech: "Sprache",
    severities: { passive: "Passiv", info: "Info", warning: "Warnung", critical: "Kritisch" },
    levels: { passive: "Passiv (kein Ton)", normal: "Normal", "time-sensitive": "Zeitkritisch", critical: "Kritisch (Alarm)" },
    styles: { card: "Ecke unten rechts", card_bottom_left: "Ecke unten links", card_top_right: "Ecke oben rechts", card_top_left: "Ecke oben links", modal: "Zentriertes Fenster", off: "Aus" },
    push_level: "Push-Stufe bei Schweregrad {severity}",
    popup_style: "Popup bei Schweregrad {severity}",
    critical_note: "Die Stufe kritisch ist auf beiden Plattformen ein Alarm. iOS: die kritische Mitteilung; sie braucht die Erlaubnis der App, spielt auch im Lautlosmodus einen Ton und kann nicht ersetzt oder gruppiert werden. Android: der Alarmkanal; er ertönt auch im Vibrations- und Lautlosmodus und wird sofort zugestellt. Nicht stören wird nur übergangen, wenn du es in den Android-Einstellungen für diesen Kanal erlaubst. Zeitkritisch wird auch auf Android sofort zugestellt.",
    ha_language_named: "Sprache von Home Assistant ({name})",
    no_engine_languages: "Wähle unter Einstellungen, Sprache eine Text-zu-Sprache-Engine, um aus ihren Sprachen zu wählen. Bis dahin gib einen Sprachcode wie de-DE ein oder lass das Feld leer für die Sprache von Home Assistant.",
    lockscreen: "Text auf dem Sperrbildschirm",
    lockscreens: { full: "Titel und Text", title_only: "Nur Titel", generic: "Allgemeiner Text" },
    buttons_note: "Schaltflächen: Später und Schließen. Bestätigen kommt hinzu, wenn eine Eskalations- oder Erinnerungsrichtlinie gilt.",
    sticky: "Benachrichtigung nach einem Tippen behalten (Android)",
    severity_look: "Symbol und Farbe der Dringlichkeit für Push verwenden",
    severity_look_note: "Verwendet für jede Push-Benachrichtigung Symbol und Farbe der Dringlichkeit. Eine Nachricht kann eine eigene Farbe und ein eigenes Symbol setzen. Ausgeschaltet nutzt ein Push das Home-Assistant-Symbol.",
    channel_id: "Android-Kanalname",
    channel_id_note: "Android behält die erste Wichtigkeit eines Kanals, darum hat jede Stufe einen eigenen Kanal namens <Name>_<Stufe>.",
    language: "Gesprochene Sprache",
    speech_note: "Sprache nutzt announce, wenn der Player es unterstützt. Die Lautstärke steht unter Einstellungen, Lautstärke der Sprache. Assist-Satelliten sprechen in der Sprache ihres eigenen Sprachassistenten.",
    save: "Speichern",
    saved: "Gespeichert.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    valid: "Keine Probleme.",
    bad_channel_id: "Der Kanalname besteht aus Kleinbuchstaben, Ziffern und Unterstrichen, höchstens 40 Zeichen.",
    progress_interval: "Sekunden zwischen zwei Fortschrittsmeldungen (1 bis 300)",
    progress_interval_note: "Kürzeste Zeit zwischen zwei Pushs einer Nachricht mit Fortschrittsbalken. Eine Nachricht kann mit progress.interval eine eigene festlegen. Die Companion-App und iOS drosseln häufige Updates; 5 Sekunden sind ein sicherer Anfang.",
    bad_progress_interval: "Das Fortschrittsintervall ist eine ganze Zahl von Sekunden von 1 bis 300.",
    mail: "E-Mail",
    persistent: "Persistente Benachrichtigung",
    persistent_summary: "Keine Einstellungen",
    persistent_none: "Für diesen Kanal gibt es keine Einstellungen. Er legt die Nachricht in die Benachrichtigungsliste von Home Assistant, die Glocke in der Seitenleiste, und braucht kein Ziel.",
    inbox: "Posteingang",
    inbox_summary: "{months} Monate aufbewahrt",
    inbox_summary_all: "{months} Monate aufbewahrt · alle Benachrichtigungen",
    inbox_intro: "Einträge des Kanals Posteingang: einer je Nachricht und Person, über Neustarts hinweg gespeichert. Die Posteingangs-Karte und der Sensor jeder Person zeigen sie.",
    inbox_retention: "Monate, die Einträge im Posteingang bleiben",
    inbox_retention_note: "1–36. Ältere Einträge werden entfernt, und jede Person behält höchstens 2000 Einträge. Der Text eines Eintrags wird im Klartext gespeichert, auch in Sicherungen.",
    inbox_reminder: "Eine Erinnerung markiert einen gelesenen Eintrag wieder als ungelesen",
    inbox_reminder_note: "An: Eine Erinnerung oder Eskalation, die eine Person erreicht, die den Eintrag schon hat, setzt ihn wieder auf ungelesen. Aus: Sie fügt nur eine Zeile zum Verlauf hinzu.",
    inbox_all: "Optionalen Bereich „Alle Benachrichtigungen anzeigen“ im Posteingang hinzufügen",
    inbox_all_note: "Speichert pro Person eine Kopie jeder Benachrichtigung im Reiter Alle Benachrichtigungen des Posteingangs, zum Beispiel eine per E-Mail empfangene oder über einen Lautsprecher gesprochene (aufgelistet für die Personen, die zu Hause sind). Eine Kopie ist Verlauf: Sie ist gelesen und wird nicht gezählt. Der Text jeder Benachrichtigung wird im Klartext gespeichert, auch in Sicherungen. Aus: Nur Nachrichten an den Posteingang werden gespeichert.",
    inbox_messages: "Personen dürfen sich gegenseitig kurze Nachrichten schicken",
    inbox_messages_note: "Jede Person kann über die Posteingangs-Karte anderen Personen schreiben. Eine Nachricht ist reiner Text mit bis zu 1000 Zeichen, hat immer die Wichtigkeit Info und geht in den Posteingang und, wenn der Absender sie wählt, an Push und Popup. Jede Person kann 10 Nachrichten pro Minute senden. Was jeder Empfänger annimmt und deine Richtlinien gelten weiterhin.",
    inbox_summary_messages: " · Nachrichten zwischen Personen",
    inbox_info: "{items} Einträge für {people} Personen, der älteste vom {oldest}.",
    inbox_empty: "Es sind keine Einträge gespeichert.",
    inbox_clear: "Posteingang leeren",
    inbox_confirm: "Alle Einträge im Posteingang aller Personen löschen? Das lässt sich nicht rückgängig machen.",
    inbox_cleared: "Der Posteingang wurde geleert.",
    inbox_failed: "Der Posteingang konnte nicht geleert werden: {error}",
    bad_retention: "Die Aufbewahrung ist eine ganze Zahl von Monaten von 1 bis 36.",
    lbl_speak_max_length: "Gesprochener Text: höchstens (Zeichen)",
    note_speak_max_length: "Längere Texte werden an einem Wortende gekürzt und enden mit Auslassungspunkten.",
    lbl_speak_cooldown_seconds: "Gesprochener Text: Wiederholungspause (Sekunden)",
    note_speak_cooldown_seconds: "Derselbe Text wird auf demselben Lautsprecher innerhalb dieser Zeit nicht noch einmal gesprochen. 0: immer sprechen.",
    lbl_speak_tts_entity: "Text-zu-Sprache-Engine",
    note_speak_tts_entity: "Die Engine, die auf Mediaplayern spricht. Leer: die einzige Text-zu-Sprache-Entität, wenn es genau eine gibt.",
    lbl_speak_restore_volume: "Lautstärke nach dem Sprechen zurücksetzen",
    note_speak_restore_volume: "Ein Lautsprecher, dessen Lautstärke Heads Up geändert hat, bekommt seine vorherige Lautstärke zurück, sobald die Meldung gesagt ist, außer jemand hat die Lautstärke inzwischen geändert. Sonos-Lautsprecher behalten ihre Lautstärke und sagen die Meldung in der gewählten Lautstärke. Aus: der Lautsprecher bleibt auf der Sprachlautstärke.",
    lbl_speak_severity_volume: "Lautstärke nach Schweregrad (Prozent)",
    note_speak_severity_volume: "0–100 pro Schweregrad. Leer: die Uhrzeit entscheidet. Eine Lautstärke im Aktionsaufruf hat Vorrang.",
    lbl_speak_volume_bands: "Lautstärke nach Uhrzeit",
    note_speak_volume_bands: "Bis zu 4 Zeiträume, jeder mit Beginn, Ende und Lautstärke in Prozent. Ein Zeitraum von 22:00 bis 07:00 geht über Mitternacht. Zeiträume dürfen sich nicht überschneiden. Außerhalb aller Zeiträume bleibt die Lautstärke unverändert.",
    lbl_rate_per_device_per_minute: "Pushes pro Gerät und Minute",
    note_rate_per_device_per_minute: "1–600. Ein Push über dem Limit wird übersprungen; kritische Meldungen werden nie zurückgehalten.",
    lbl_rate_total_per_minute: "Zustellungen pro Minute, alle Geräte",
    note_rate_total_per_minute: "1–6000. Ein Push über dem Limit wird übersprungen; kritische Meldungen werden nie zurückgehalten.",
    tts_auto: "Automatisch",
    range: "{field} muss zwischen {min} und {max} liegen.",
    band_from: "Von",
    band_to: "Bis",
    band_volume: "Lautstärke (%)",
    band_add: "Zeitraum hinzufügen",
    band_remove: "Entfernen",
    bands_invalid: "Jeder Zeitraum braucht Beginn und Ende (HH:MM) und eine Lautstärke von 0 bis 100.",
    bands_too_many: "Höchstens 4 Zeiträume.",
    bands_empty: "Beginn und Ende eines Zeitraums müssen verschieden sein.",
    bands_overlap: "Zeiträume dürfen sich nicht überschneiden.",
    severity_volume_invalid: "Gib eine Lautstärke von 0 bis 100 für passive, info, warning oder critical an.",
    mail_intro: "E-Mail ruft einen Benachrichtigungsdienst einmal pro Empfänger mit Betreff und Text auf. Die Adresse einer Person stellst du unter Empfänger ein; dort muss E-Mail für sie aktiviert sein.",
    mail_service: "Benachrichtigungsdienst",
    mail_service_none: "Keiner (E-Mail ist aus)",
    mail_global_address: "Globale Adresse",
    mail_global_note: "Optional. Nicht an eine Person gebunden: Nenne Global address als Empfänger, um dorthin zu senden. Sie ersetzt nie die Adresse einer Person.",
    mail_subject: "Betreff",
    mail_body: "Text",
    mail_placeholders: "Platzhalter: {severity} (zum Beispiel Kritisch), {title} (der Titel, sonst die Nachricht), {message}, {person} (der Name der Person, leer bei der globalen Adresse), {person_id} (der Teil der Entitäts-ID nach person., zum Beispiel philip; kleingeschrieben), {id}, {tag}.",
    bad_mail_subject: "Der Betreff braucht Text, höchstens 200 Zeichen, und darf nur die genannten Platzhalter nutzen.",
    bad_mail_body: "Der Text braucht Inhalt, höchstens 2000 Zeichen, und darf nur die genannten Platzhalter nutzen.",
    bad_mail_address: "Die Adresse darf höchstens 254 Zeichen lang sein.",
  },
  fr: {
    title: "Canaux",
    banner: "Bannière",
    banner_snooze: "Durées de report sur la bannière",
    banner_snooze_hint: "Utilisé quand un appel ou une règle de surveillance ne définit pas ses propres durées. La possibilité de reporter un message et les réglages de fermeture sont dans Réglages, Messages : ils valent pour la bannière, le push et le popup. L'apparence de la carte se règle dans les options de la carte.",
    snooze_time: "Durée de report sur le push et le popup (minutes)",
    snooze_time_hint: "1–1440. Le bouton Reporter du push et du popup reporte pour cette durée. C'est le même réglage sur les lignes Push et Popup.",
    bad_snooze_time: "La durée de report est un nombre entier de minutes de 1 à 1440.",
    snooze_summary: "Report {time}",
    styles_label: "Popup par gravité",
    styles_hint: "Réglé sur la page Gravités.",
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 heure", "120": "2 heures", "240": "4 heures", "480": "8 heures", "1440": "24 heures"},
    minutes_n: "{n} minutes",
    no_choices: "aucune durée de report",
    col_channel: "Canal",
    col_settings: "Réglages",
    sticky_on: "conservée après un appui",
    android: "Canal Android {id}",
    ha_language: "Langue de Home Assistant",
    mail_off: "Désactivé",
    global_to: "adresse globale {a}",
    edit: "Modifier {name}",
    changed: "modifié",
    severities_note: "Le niveau du push et le style du popup de chaque gravité se règlent sur la page Gravités.",
    severities_link: "Gravités",
    intro: "Le fonctionnement de chaque canal pour tous les messages. Choisissez un canal pour le modifier.",
    push: "Push",
    popup: "Fenêtre",
    speech: "Voix",
    severities: { passive: "Passif", info: "Info", warning: "Avertissement", critical: "Critique" },
    levels: { passive: "Passif (sans son)", normal: "Normal", "time-sensitive": "Urgent", critical: "Critique (alarme)" },
    styles: { card: "Coin en bas à droite", card_bottom_left: "Coin en bas à gauche", card_top_right: "Coin en haut à droite", card_top_left: "Coin en haut à gauche", modal: "Fenêtre centrée", off: "Désactivé" },
    push_level: "Niveau du push quand la gravité est {severity}",
    popup_style: "Fenêtre quand la gravité est {severity}",
    critical_note: "Le niveau critique est une alarme sur les deux plateformes. iOS : l'alerte critique ; elle demande l'autorisation de l'app, joue un son même en mode silencieux et ne peut être ni remplacée ni groupée. Android : le canal d'alarme ; il sonne même en mode vibreur et silencieux et est livré tout de suite. Ne pas déranger n'est contourné que si vous l'autorisez pour ce canal dans les réglages d'Android. Urgent est aussi livré tout de suite sur Android.",
    ha_language_named: "Langue de Home Assistant ({name})",
    no_engine_languages: "Choisissez un moteur de synthèse vocale dans Réglages, Voix pour choisir parmi ses langues. En attendant, saisissez un code de langue comme fr-FR, ou laissez vide pour la langue de Home Assistant.",
    lockscreen: "Texte sur l'écran verrouillé",
    lockscreens: { full: "Titre et texte", title_only: "Titre seulement", generic: "Texte générique" },
    buttons_note: "Boutons : Reporter et Fermer. Confirmer s'ajoute quand une politique d'escalade ou de rappel s'applique.",
    sticky: "Garder la notification après un appui (Android)",
    severity_look: "Utiliser l'icône et la couleur de la gravité pour les push",
    severity_look_note: "Utilise l'icône et la couleur de la gravité pour chaque notification push. Un message peut définir sa propre couleur et sa propre icône. Désactivé, un push utilise l'icône de Home Assistant.",
    channel_id: "Nom du canal Android",
    channel_id_note: "Android garde la première importance d'un canal, donc chaque niveau a son propre canal nommé <nom>_<niveau>.",
    language: "Langue parlée",
    speech_note: "La voix utilise announce quand le lecteur le permet. Le volume se règle dans Réglages, Volume de la voix. Les satellites Assist parlent dans la langue de leur propre assistant vocal.",
    save: "Enregistrer",
    saved: "Enregistré.",
    failed: "Enregistrement impossible. Réessayez.",
    valid: "Aucun problème.",
    bad_channel_id: "Le nom du canal utilise des minuscules, des chiffres et des tirets bas, 40 caractères au plus.",
    progress_interval: "Secondes entre deux mises à jour de progression (1 à 300)",
    progress_interval_note: "Délai minimal entre deux push d'un message avec barre de progression. Un message peut définir le sien avec progress.interval. L'app Companion et iOS limitent les mises à jour fréquentes ; 5 secondes est un bon départ.",
    bad_progress_interval: "L'intervalle de progression est un nombre entier de secondes de 1 à 300.",
    mail: "Courriel",
    persistent: "Notification persistante",
    persistent_summary: "Aucun réglage",
    persistent_none: "Ce canal n'a aucun réglage. Il ajoute le message à la liste des notifications de Home Assistant, la cloche dans la barre latérale, et n'a besoin d'aucun destinataire.",
    inbox: "Boîte de réception",
    inbox_summary: "Conservé {months} mois",
    inbox_summary_all: "Conservé {months} mois · toutes les notifications",
    inbox_intro: "Éléments du canal boîte de réception : un par message et par personne, conservés après un redémarrage. La carte de la boîte de réception et le capteur de chaque personne les affichent.",
    inbox_retention: "Mois de conservation des éléments de la boîte de réception",
    inbox_retention_note: "1–36. Les éléments plus anciens sont supprimés, et chaque personne garde au plus 2000 éléments. Le texte d'un élément est stocké en clair, aussi dans les sauvegardes.",
    inbox_reminder: "Un rappel remet un élément lu en non lu",
    inbox_reminder_note: "Activé : un rappel ou une escalade qui atteint une personne ayant déjà l'élément le remet dans les non lus. Désactivé : il ajoute seulement une ligne à la chronologie.",
    inbox_all: "Ajouter une section facultative « Afficher toutes les notifications » à la boîte de réception",
    inbox_all_note: "Enregistre pour chaque personne une copie de chaque notification dans l'onglet Toutes les notifications de la boîte de réception, par exemple une notification reçue par courriel ou dite sur un haut-parleur (listée pour les personnes à la maison). Une copie est un historique : elle est lue et non comptée. Le texte de chaque notification est stocké en clair, aussi dans les sauvegardes. Désactivé : seuls les messages envoyés à la boîte de réception sont conservés.",
    inbox_messages: "Permettre aux personnes de s'envoyer de courts messages",
    inbox_messages_note: "Chaque personne peut écrire aux autres depuis la carte de boîte de réception. Un message est du texte brut de 1000 caractères au plus, a toujours la gravité Info et va dans la boîte de réception et, si l'expéditeur les choisit, en push et en popup. Chaque personne peut envoyer 10 messages par minute. Ce que chaque destinataire accepte et vos politiques restent appliqués.",
    inbox_summary_messages: " · messages entre personnes",
    inbox_info: "{items} éléments pour {people} personnes, le plus ancien du {oldest}.",
    inbox_empty: "Aucun élément n'est stocké.",
    inbox_clear: "Vider la boîte de réception",
    inbox_confirm: "Supprimer tous les éléments de la boîte de réception de chaque personne ? Cette action est irréversible.",
    inbox_cleared: "La boîte de réception a été vidée.",
    inbox_failed: "Impossible de vider la boîte de réception : {error}",
    bad_retention: "La conservation est un nombre entier de mois de 1 à 36.",
    lbl_speak_max_length: "Texte parlé : longueur maximale (caractères)",
    note_speak_max_length: "Les textes plus longs sont coupés à la fin d'un mot et se terminent par des points de suspension.",
    lbl_speak_cooldown_seconds: "Texte parlé : pause avant répétition (secondes)",
    note_speak_cooldown_seconds: "Le même texte n'est pas redit sur le même haut-parleur pendant ce délai. 0 : toujours dire.",
    lbl_speak_tts_entity: "Moteur de synthèse vocale",
    note_speak_tts_entity: "Le moteur qui parle sur les lecteurs multimédia. Vide : la seule entité de synthèse vocale, s'il n'y en a qu'une.",
    lbl_speak_restore_volume: "Remettre le volume après avoir parlé",
    note_speak_restore_volume: "Un haut-parleur dont Heads Up a changé le volume retrouve son volume précédent une fois le message dit, sauf si quelqu'un a changé le volume entre-temps. Les haut-parleurs Sonos gardent leur volume et disent le message au niveau choisi. Désactivé : le haut-parleur reste au volume de la voix.",
    lbl_speak_severity_volume: "Volume par gravité (pour cent)",
    note_speak_severity_volume: "0–100 par gravité. Vide : l'heure décide. Un volume dans l'appel d'action passe en premier.",
    lbl_speak_volume_bands: "Volume selon l'heure",
    note_speak_volume_bands: "Jusqu'à 4 plages, chacune avec un début, une fin et un volume en pour cent. Une plage de 22:00 à 07:00 passe minuit. Les plages ne doivent pas se chevaucher. En dehors de toute plage, le volume ne change pas.",
    lbl_rate_per_device_per_minute: "Push par appareil et par minute",
    note_rate_per_device_per_minute: "1–600. Un push au-delà de la limite est ignoré ; les messages critiques ne sont jamais retenus.",
    lbl_rate_total_per_minute: "Livraisons par minute, tous appareils",
    note_rate_total_per_minute: "1–6000. Un push au-delà de la limite est ignoré ; les messages critiques ne sont jamais retenus.",
    tts_auto: "Automatique",
    range: "{field} doit être entre {min} et {max}.",
    band_from: "De",
    band_to: "À",
    band_volume: "Volume (%)",
    band_add: "Ajouter une plage",
    band_remove: "Retirer",
    bands_invalid: "Chaque plage a besoin d'un début et d'une fin (HH:MM) et d'un volume de 0 à 100.",
    bands_too_many: "4 plages au plus.",
    bands_empty: "Le début et la fin d'une plage doivent être différents.",
    bands_overlap: "Les plages ne doivent pas se chevaucher.",
    severity_volume_invalid: "Indiquez un volume de 0 à 100 pour passive, info, warning ou critical.",
    mail_intro: "Le courriel appelle un service de notification une fois par destinataire avec un objet et un corps. L'adresse d'une personne se règle sous Destinataires, où Courriel doit être activé pour elle.",
    mail_service: "Service de notification",
    mail_service_none: "Aucun (courriel désactivé)",
    mail_global_address: "Adresse globale",
    mail_global_note: "Facultatif. Non liée à une personne : nommez Global address comme destinataire pour y envoyer. Elle ne remplace jamais l'adresse d'une personne.",
    mail_subject: "Objet",
    mail_body: "Corps",
    mail_placeholders: "Variables : {severity} (par exemple Critique), {title} (le titre, sinon le message), {message}, {person} (le nom de la personne, vide pour l'adresse globale), {person_id} (la partie de l'ID d'entité après person., par exemple philip ; en minuscules), {id}, {tag}.",
    bad_mail_subject: "L'objet a besoin de texte, 200 caractères au plus, et n'utilise que les variables listées.",
    bad_mail_body: "Le corps a besoin de texte, 2000 caractères au plus, et n'utilise que les variables listées.",
    bad_mail_address: "L'adresse peut avoir 254 caractères au plus.",
  },
  es: {
    title: "Canales",
    banner: "Aviso",
    banner_snooze: "Opciones de posposición en el aviso",
    banner_snooze_hint: "Se usa cuando una llamada o una regla de vigilancia no define sus propias opciones. Si un mensaje se puede posponer y los ajustes de cierre están en Ajustes, Mensajes: valen para aviso, push y ventana emergente. El aspecto de la tarjeta se ajusta en las opciones de la tarjeta.",
    snooze_time: "Tiempo de posposición en push y ventana emergente (minutos)",
    snooze_time_hint: "1–1440. El botón Posponer del push y de la ventana emergente pospone durante este tiempo. Es el mismo ajuste en las filas Push y Ventana.",
    bad_snooze_time: "El tiempo de posposición es un número entero de minutos de 1 a 1440.",
    snooze_summary: "Posponer {time}",
    styles_label: "Ventana por gravedad",
    styles_hint: "Se ajusta en la página Gravedades.",
    minutes: {"5": "5 minutos", "15": "15 minutos", "30": "30 minutos", "60": "1 hora", "120": "2 horas", "240": "4 horas", "480": "8 horas", "1440": "24 horas"},
    minutes_n: "{n} minutos",
    no_choices: "sin opciones de posposición",
    col_channel: "Canal",
    col_settings: "Ajustes",
    sticky_on: "se mantiene tras tocar",
    android: "Canal Android {id}",
    ha_language: "Idioma de Home Assistant",
    mail_off: "Desactivado",
    global_to: "dirección global {a}",
    edit: "Editar {name}",
    changed: "cambiado",
    severities_note: "El nivel del push y el estilo de la ventana de cada gravedad se ajustan en la página Gravedades.",
    severities_link: "Gravedades",
    intro: "Cómo funciona cada canal para todos los mensajes. Elige un canal para cambiarlo.",
    push: "Push",
    popup: "Ventana",
    speech: "Voz",
    severities: { passive: "Pasivo", info: "Info", warning: "Aviso", critical: "Crítico" },
    levels: { passive: "Pasivo (sin sonido)", normal: "Normal", "time-sensitive": "Urgente", critical: "Crítico (alarma)" },
    styles: { card: "Esquina inferior derecha", card_bottom_left: "Esquina inferior izquierda", card_top_right: "Esquina superior derecha", card_top_left: "Esquina superior izquierda", modal: "Ventana centrada", off: "Desactivado" },
    push_level: "Nivel del push cuando la gravedad es {severity}",
    popup_style: "Ventana cuando la gravedad es {severity}",
    critical_note: "El nivel crítico es una alarma en ambas plataformas. iOS: la alerta crítica; necesita el permiso de la app, suena incluso en modo silencio y no se puede reemplazar ni agrupar. Android: el canal de alarma; suena incluso en modo vibración y silencio y se entrega de inmediato. No molestar solo se anula si lo permites para ese canal en los ajustes de Android. Urgente también se entrega de inmediato en Android.",
    ha_language_named: "Idioma de Home Assistant ({name})",
    no_engine_languages: "Elige un motor de texto a voz en Ajustes, Voz para elegir entre sus idiomas. Mientras tanto, escribe un código de idioma como es-ES, o déjalo vacío para el idioma de Home Assistant.",
    lockscreen: "Texto en la pantalla de bloqueo",
    lockscreens: { full: "Título y texto", title_only: "Solo el título", generic: "Texto genérico" },
    buttons_note: "Botones: Posponer y Descartar. Confirmar se añade cuando se aplica una política de escalado o recordatorio.",
    sticky: "Mantener la notificación tras tocarla (Android)",
    severity_look: "Usar el icono y el color de la gravedad en los push",
    severity_look_note: "Usa el icono y el color de la gravedad en cada notificación push. Un mensaje puede definir su propio color e icono. Desactivado, un push usa el icono de Home Assistant.",
    channel_id: "Nombre del canal de Android",
    channel_id_note: "Android conserva la primera importancia de un canal, así que cada nivel tiene su propio canal llamado <nombre>_<nivel>.",
    language: "Idioma hablado",
    speech_note: "La voz usa announce cuando el reproductor lo admite. El volumen se ajusta en Ajustes, Volumen de la voz. Los satélites Assist hablan en el idioma de su propio asistente de voz.",
    save: "Guardar",
    saved: "Guardado.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    valid: "Sin problemas.",
    bad_channel_id: "El nombre del canal usa minúsculas, dígitos y guiones bajos, hasta 40 caracteres.",
    progress_interval: "Segundos entre dos actualizaciones de progreso (1 a 300)",
    progress_interval_note: "Tiempo mínimo entre dos push de un mensaje con barra de progreso. Un mensaje puede fijar el suyo con progress.interval. La app Companion e iOS limitan las actualizaciones frecuentes; 5 segundos es un buen comienzo.",
    bad_progress_interval: "El intervalo de progreso es un número entero de segundos de 1 a 300.",
    mail: "Correo",
    persistent: "Notificación persistente",
    persistent_summary: "Sin ajustes",
    persistent_none: "Este canal no tiene ajustes. Añade el mensaje a la lista de notificaciones de Home Assistant, la campana de la barra lateral, y no necesita destino.",
    inbox: "Bandeja de entrada",
    inbox_summary: "Se conserva {months} meses",
    inbox_summary_all: "Se conserva {months} meses · todas las notificaciones",
    inbox_intro: "Elementos del canal bandeja de entrada: uno por mensaje y persona, conservados tras un reinicio. La tarjeta de la bandeja de entrada y el sensor de cada persona los muestran.",
    inbox_retention: "Meses que se conservan los elementos de la bandeja",
    inbox_retention_note: "1–36. Los elementos más antiguos se eliminan y cada persona conserva como máximo 2000. El texto de un elemento se guarda en texto plano, también en las copias de seguridad.",
    inbox_reminder: "Un recordatorio vuelve a marcar como sin leer un elemento leído",
    inbox_reminder_note: "Activado: un recordatorio o un escalado que llega a una persona que ya tiene el elemento lo devuelve a los no leídos. Desactivado: solo añade una línea a la cronología.",
    inbox_all: "Añadir una sección opcional «Mostrar todas las notificaciones» a la bandeja de entrada",
    inbox_all_note: "Guarda para cada persona una copia de cada notificación en la pestaña Todas las notificaciones de la bandeja de entrada, por ejemplo una recibida por correo o dicha en un altavoz (listada para las personas en casa). Una copia es historial: está leída y no se cuenta. El texto de cada notificación se guarda en texto plano, también en las copias de seguridad. Desactivado: solo se guardan los mensajes enviados a la bandeja de entrada.",
    inbox_messages: "Permitir que las personas se envíen mensajes cortos",
    inbox_messages_note: "Cualquier persona puede escribir a otras desde la tarjeta de la bandeja de entrada. Un mensaje es texto sin formato de hasta 1000 caracteres, siempre tiene la gravedad Info y va a la bandeja de entrada y, si el remitente los elige, a push y popup. Cada persona puede enviar 10 mensajes por minuto. Lo que acepta cada destinatario y tus políticas siguen aplicándose.",
    inbox_summary_messages: " · mensajes entre personas",
    inbox_info: "{items} elementos de {people} personas, el más antiguo del {oldest}.",
    inbox_empty: "No hay elementos guardados.",
    inbox_clear: "Vaciar la bandeja de entrada",
    inbox_confirm: "¿Eliminar todos los elementos de la bandeja de entrada de cada persona? No se puede deshacer.",
    inbox_cleared: "La bandeja de entrada se vació.",
    inbox_failed: "No se pudo vaciar la bandeja de entrada: {error}",
    bad_retention: "La conservación es un número entero de meses de 1 a 36.",
    lbl_speak_max_length: "Texto hablado: longitud máxima (caracteres)",
    note_speak_max_length: "Los textos más largos se cortan al final de una palabra y terminan con puntos suspensivos.",
    lbl_speak_cooldown_seconds: "Texto hablado: pausa de repetición (segundos)",
    note_speak_cooldown_seconds: "El mismo texto no se repite en el mismo altavoz dentro de este tiempo. 0: hablar siempre.",
    lbl_speak_tts_entity: "Motor de texto a voz",
    note_speak_tts_entity: "El motor que habla en los reproductores multimedia. Vacío: la única entidad de texto a voz, si solo hay una.",
    lbl_speak_restore_volume: "Devolver el volumen después de hablar",
    note_speak_restore_volume: "Un altavoz cuyo volumen cambió Heads Up recupera su volumen anterior en cuanto se dijo el mensaje, salvo que alguien haya cambiado el volumen mientras tanto. Los altavoces Sonos mantienen su volumen y dicen el mensaje al nivel elegido. Desactivado: el altavoz se queda al volumen de la voz.",
    lbl_speak_severity_volume: "Volumen por gravedad (por ciento)",
    note_speak_severity_volume: "0–100 por gravedad. Vacío: decide la hora. Un volumen en la llamada a la acción va primero.",
    lbl_speak_volume_bands: "Volumen según la hora",
    note_speak_volume_bands: "Hasta 4 franjas, cada una con inicio, fin y un volumen en por ciento. Una franja de 22:00 a 07:00 pasa la medianoche. Las franjas no deben solaparse. Fuera de toda franja el volumen no cambia.",
    lbl_rate_per_device_per_minute: "Pushes por dispositivo y minuto",
    note_rate_per_device_per_minute: "1–600. Un push por encima del límite se omite; los mensajes críticos nunca se retienen.",
    lbl_rate_total_per_minute: "Entregas por minuto, todos los dispositivos",
    note_rate_total_per_minute: "1–6000. Un push por encima del límite se omite; los mensajes críticos nunca se retienen.",
    tts_auto: "Automático",
    range: "{field} debe estar entre {min} y {max}.",
    band_from: "Desde",
    band_to: "Hasta",
    band_volume: "Volumen (%)",
    band_add: "Añadir franja",
    band_remove: "Quitar",
    bands_invalid: "Cada franja necesita un inicio y un fin (HH:MM) y un volumen de 0 a 100.",
    bands_too_many: "Como máximo 4 franjas.",
    bands_empty: "El inicio y el fin de una franja deben ser distintos.",
    bands_overlap: "Las franjas no deben solaparse.",
    severity_volume_invalid: "Indica un volumen de 0 a 100 para passive, info, warning o critical.",
    mail_intro: "El correo llama a un servicio de notificación una vez por destinatario con asunto y cuerpo. La dirección de una persona se define en Destinatarios, donde Correo debe estar activado para ella.",
    mail_service: "Servicio de notificación",
    mail_service_none: "Ninguno (correo desactivado)",
    mail_global_address: "Dirección global",
    mail_global_note: "Opcional. No ligada a una persona: nombra Global address como destinatario para enviar allí. Nunca sustituye la dirección de una persona.",
    mail_subject: "Asunto",
    mail_body: "Cuerpo",
    mail_placeholders: "Variables: {severity} (por ejemplo Crítico), {title} (el título, si no el mensaje), {message}, {person} (el nombre de la persona, vacío para la dirección global), {person_id} (la parte del ID de entidad después de person., por ejemplo philip; en minúsculas), {id}, {tag}.",
    bad_mail_subject: "El asunto necesita texto, hasta 200 caracteres, y solo puede usar las variables indicadas.",
    bad_mail_body: "El cuerpo necesita texto, hasta 2000 caracteres, y solo puede usar las variables indicadas.",
    bad_mail_address: "La dirección puede tener 254 caracteres como máximo.",
  },
};

const SEVERITIES = ["passive", "info", "warning", "critical"];
const LEVELS = ["passive", "normal", "time-sensitive", "critical"];
const STYLES = ["card", "card_bottom_left", "card_top_right", "card_top_left", "modal", "off"];
const LOCKSCREENS = ["full", "title_only", "generic"];

// The channels the page lists, the settings each one owns and its icon.
const CHANNELS = [
  { key: "banner", icon: "mdi:card-text-outline", keys: [], settings: ["default_snooze_options"] },
  { key: "push", icon: "mdi:cellphone-message", keys: ["push_lockscreen", "push_channel_id", "push_sticky", "push_severity_look", "push_progress_interval", "rate_per_device_per_minute", "rate_total_per_minute"], settings: ["quick_snooze_minutes"] },
  { key: "popup", icon: "mdi:dock-window", keys: [], settings: ["quick_snooze_minutes"] },
  { key: "speech", icon: "mdi:account-voice", keys: ["speak_language", "speak_max_length", "speak_cooldown_seconds", "speak_tts_entity", "speak_restore_volume", "speak_severity_volume", "speak_volume_bands"], settings: [] },
  { key: "persistent", icon: "mdi:bell-outline", keys: [], settings: [] },
  { key: "mail", icon: "mdi:email-outline", keys: ["mail_service", "mail_global_address", "mail_subject", "mail_body"], settings: [] },
  { key: "inbox", icon: "mdi:inbox-outline", keys: ["inbox_retention_months", "inbox_reminder_unread", "inbox_all_notifications", "inbox_messages"], settings: [] },
];

// The two snooze settings these rows show are stored with the other settings (heads_up/settings_set).
export const SETTING_KEYS = ["default_snooze_options", "quick_snooze_minutes"];
const SNOOZE_MINUTES = [5, 15, 30, 60, 120, 240, 480, 1440];
const SEVERITY_ORDER = ["critical", "warning", "info", "passive"];

export function minutesText(n, t) {
  return t.minutes[String(n)] || fill(t.minutes_n, { n });
}

// Popup styles grouped: "Centered window (Critical) · Corner, bottom right (Warning, Info, Success)".
export function stylesText(styles, t) {
  const groups = new Map();
  for (const severity of SEVERITY_ORDER) {
    const style = (styles || {})[severity];
    if (!style) continue;
    groups.set(style, [...(groups.get(style) || []), t.severities[severity] || severity]);
  }
  return [...groups].map(([style, names]) => `${t.styles[style] || style} (${names.join(", ")})`).join(" · ");
}

export function settingProblems(settings) {
  const time = settings.quick_snooze_minutes;
  return Number.isInteger(time) && time >= 1 && time <= 1440 ? [] : ["bad_snooze_time"];
}

export function settingChanges(settings, saved) {
  const out = {};
  for (const key of SETTING_KEYS) if (JSON.stringify(settings[key]) !== JSON.stringify(saved[key])) out[key] = settings[key];
  return out;
}

// "German (Germany) · de-DE" in the panel's language; the code alone where the browser cannot name it.
export function languageName(code, language) {
  try {
    const name = new Intl.DisplayNames([language || "en"], { type: "language" }).of(code);
    return name && name !== code ? `${name} · ${code}` : code;
  } catch (err) {
    return code;
  }
}

// The choices of the spoken language: the Home Assistant language first, then the engine's
// languages by name. A saved value the engine does not list stays selectable.
export function languageOptions(supported, current, haLanguage, language, t) {
  const codes = [...new Set([...(supported || []), ...(current ? [current] : [])])];
  const named = codes.map((code) => ({ value: code, label: languageName(code, language) })).sort((a, b) => a.label.localeCompare(b.label, language));
  return [{ value: "", label: fill(t.ha_language_named, { name: languageName(haLanguage, language) }) }, ...named];
}

// The overview line of a channel: what a reader needs to know without opening it.
export function summaryText(key, values, t, language, settings = {}) {
  if (key === "banner") {
    const choices = settings.default_snooze_options || [];
    return choices.length ? fill(t.snooze_summary, { time: choices.map((m) => minutesText(m, t)).join(", ") }) : t.no_choices;
  }
  if (key === "popup") {
    return [settings.quick_snooze_minutes ? fill(t.snooze_summary, { time: minutesText(settings.quick_snooze_minutes, t) }) : "", stylesText(values.popup_styles, t)].filter(Boolean).join(" · ");
  }
  if (key === "push") {
    return [t.lockscreens[values.push_lockscreen] || values.push_lockscreen, fill(t.android, { id: values.push_channel_id || "" }), values.push_sticky ? t.sticky_on : ""].filter(Boolean).join(" · ");
  }
  if (key === "speech") {
    const code = String(values.speak_language || "").trim();
    return code ? languageName(code, language) : t.ha_language;
  }
  if (key === "persistent") return t.persistent_summary;
  if (key === "inbox") {
    const base = fill(values.inbox_all_notifications ? t.inbox_summary_all : t.inbox_summary, { months: values.inbox_retention_months });
    return values.inbox_messages ? base + t.inbox_summary_messages : base;
  }
  if (!values.mail_service) return t.mail_off;
  const address = String(values.mail_global_address || "").trim();
  return [`notify.${values.mail_service}`, address ? fill(t.global_to, { a: address }) : ""].filter(Boolean).join(" · ");
}

const PAGE_CSS = `
.hu-page .tl-list { --tl-cols: minmax(0, 1fr) minmax(0, 2.4fr); }
.hu-page .tl-lead ha-icon { color: var(--secondary-text-color); }
.hu-page .tl-body .tl-wide label.field { margin: 0; }
.hu-page .tl-body .tl-wide label.inline { min-height: 44px; }
.hu-page .ch-lang { max-width: 460px; }
.hu-page .ch-chips fieldset { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); column-gap: 12px; margin: 0; }
.hu-page .ch-chips label.inline { min-height: 40px; }
.hu-page .ch-sub { font-size: 14px; margin: 4px 0 8px; }
.hu-page .ch-volumes, .hu-page .ch-bands { display: grid; gap: 4px 12px; }
.hu-page .ch-volumes { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
.hu-page .ch-volumes .ch-sub, .hu-page .ch-bands .ch-sub { grid-column: 1 / -1; }
.hu-page .ch-band { display: flex; flex-wrap: wrap; align-items: end; gap: 8px 12px; }
.hu-page .ch-go { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; }
.hu-page .ch-go .hint { margin: 0; }
.hu-page .ch-note { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; margin: 0 0 8px; }
.hu-page .ch-note .hint { margin: 0; flex: 1; min-width: 200px; }
`;

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function validChannelId(value) {
  return /^[a-z0-9_]{1,40}$/.test(String(value || ""));
}

// What changed against the saved settings: only those keys are sent.
export function changes(values, saved) {
  const out = {};
  for (const key of Object.keys(saved)) {
    if (JSON.stringify(values[key]) !== JSON.stringify(saved[key])) out[key] = values[key];
  }
  return out;
}

export const MAIL_PLACEHOLDERS = ["severity", "title", "message", "person", "id", "tag"];

// A mail template needs text within the limit and may use only the known placeholders.
export function validMailTemplate(text, limit) {
  const value = String(text ?? "");
  if (!value.trim() || value.length > limit) return false;
  return [...value.matchAll(/\{(\w*)\}/g)].every((m) => MAIL_PLACEHOLDERS.includes(m[1]));
}

// Seconds between two progress pushes: a whole number from 1 to 300 (D-263).
export function validProgressInterval(value) {
  const n = Number(value);
  return value !== "" && value !== null && Number.isInteger(n) && n >= 1 && n <= 300;
}

// Months to keep inbox items: a whole number from 1 to 36.
export function validRetention(value) {
  const n = Number(value);
  return value !== "" && value !== null && Number.isInteger(n) && n >= 1 && n <= 36;
}

// What the inbox store holds, in a sentence: counts and the oldest day, never a text.
export function inboxLine(info, t) {
  if (!info || !info.items) return t.inbox_empty;
  return fill(t.inbox_info, { items: info.items, people: info.people, oldest: String(info.oldest || "").slice(0, 10) });
}


// The numbers of the speech and push rows and their limits (D-276); the server checks the same.
export const CHANNEL_RANGES = {
  speak_max_length: [20, 1000],
  speak_cooldown_seconds: [0, 3600],
  rate_per_device_per_minute: [1, 600],
  rate_total_per_minute: [1, 6000],
};
const MAX_BANDS = 4;

export function bandMinutes(band) {
  const minute = (text) => {
    const match = /^(\d{1,2}):(\d{2})/.exec(String(text || ""));
    if (!match || Number(match[1]) > 23 || Number(match[2]) > 59) return null;
    return Number(match[1]) * 60 + Number(match[2]);
  };
  const start = minute(band.from);
  const end = minute(band.to);
  if (start === null || end === null) return null;
  const set = new Set();
  if (start < end) for (let m = start; m < end; m++) set.add(m);
  else if (start > end) {
    for (let m = start; m < 1440; m++) set.add(m);
    for (let m = 0; m < end; m++) set.add(m);
  }
  return set;
}

// Problems of the speech volume settings, as the error codes of the server (D-217).
export function volumeProblems(values) {
  const found = new Set();
  const bands = values.speak_volume_bands || [];
  if (bands.length > MAX_BANDS) found.add("bands_too_many");
  const taken = new Set();
  for (const band of bands) {
    const minutes = bandMinutes(band);
    if (minutes === null || !Number.isInteger(band.volume) || band.volume < 0 || band.volume > 100) {
      found.add("bands_invalid");
      continue;
    }
    if (minutes.size === 0) found.add("bands_empty");
    for (const m of minutes) {
      if (taken.has(m)) {
        found.add("bands_overlap");
        break;
      }
    }
    for (const m of minutes) taken.add(m);
  }
  for (const value of Object.values(values.speak_severity_volume || {})) {
    if (!Number.isInteger(value) || value < 0 || value > 100) found.add("severity_volume_invalid");
  }
  return [...found];
}

// The numbers outside their range, as "range:<key>" for the page to word.
export function rangeProblems(values) {
  const found = [];
  for (const [key, [min, max]] of Object.entries(CHANNEL_RANGES)) {
    if (values[key] === undefined) continue;
    const n = values[key];
    if (!Number.isInteger(n) || n < min || n > max) found.push(`range:${key}`);
  }
  return found;
}

// The text-to-speech entities of this Home Assistant, plus the saved one if it is gone.
export function ttsEntities(hass, current) {
  const ids = Object.keys(hass?.states || {}).filter((id) => id.startsWith("tts.")).sort();
  if (current && !ids.includes(current)) ids.push(current);
  return ids;
}

// A problem code in words: a number out of its range, or a code of the server.
export function problemText(code, t) {
  if (code.startsWith("range:")) {
    const key = code.slice(6);
    const [min, max] = CHANNEL_RANGES[key];
    return fill(t.range, { field: t[`lbl_${key}`], min, max });
  }
  return t[code] || code;
}

export function problems(values) {
  const found = [];
  if (values.inbox_retention_months !== undefined && !validRetention(values.inbox_retention_months)) found.push("bad_retention");
  if (!validChannelId(values.push_channel_id)) found.push("bad_channel_id");
  if (values.push_progress_interval !== undefined && !validProgressInterval(values.push_progress_interval)) found.push("bad_progress_interval");
  if (values.mail_subject !== undefined && !validMailTemplate(values.mail_subject, 200)) found.push("bad_mail_subject");
  if (values.mail_body !== undefined && !validMailTemplate(values.mail_body, 2000)) found.push("bad_mail_body");
  if (String(values.mail_global_address ?? "").trim().length > 254) found.push("bad_mail_address");
  found.push(...rangeProblems(values), ...volumeProblems(values));
  return found;
}

export function mount(container, ctx) {
  const { t, s, ui } = ctx;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let values = null;
  let message = "";
  let open = null;
  let languages = null;
  let settings = {};
  let savedSettings = {};
  let paint = () => {};
  const root = el("div", { className: "hu-page" });
  container.append(root);

  // One row per channel with a summary of its settings; a row opens its fields underneath.
  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + ui.TABLE_CSS + PAGE_CSS }), el("h1", { textContent: t.title }));
    root.append(el("div", { className: "hint", textContent: t.intro }));
    const list = el("section", { className: "tl-list" }, [ui.tableHead([t.col_channel, t.col_settings])]);
    const rows = [];
    for (const channel of CHANNELS) {
      const id = `hu-ch-${channel.key}`;
      const isOpen = open === channel.key;
      const summary = el("span");
      const mark = el("span", { className: "tl-mark" });
      const body = isOpen ? el("div") : null;
      const { item, row } = ui.tableRow({
        id,
        lead: [el("ha-icon", { icon: channel.icon }), el("span", { className: "tl-name", textContent: t[channel.key] })],
        cells: [{ label: "", node: summary }],
        end: [mark],
        open: isOpen,
        onToggle: () => {
          open = isOpen ? null : channel.key;
          render();
          root.querySelector(`[aria-controls="${id}"]`)?.focus();
        },
        body,
      });
      if (body) body.append(fields(channel.key));
      rows.push(() => {
        summary.textContent = summaryText(channel.key, values, t, ctx.language, settings);
        const changed = channel.keys.some((k) => JSON.stringify(values[k]) !== JSON.stringify(data.channels[k])) || channel.settings.some((k) => JSON.stringify(settings[k]) !== JSON.stringify(savedSettings[k]));
        mark.textContent = changed ? "●" : "";
        row.setAttribute("aria-label", `${fill(t.edit, { name: t[channel.key] })}: ${summary.textContent}${changed ? `, ${t.changed}` : ""}`);
      });
      list.append(item);
    }
    root.append(list);
    // The push level and the popup style of each severity are on the Severities page (D-222).
    const toSeverities = el("button", { type: "button", textContent: t.severities_link });
    toSeverities.addEventListener("click", () => ctx.navigate("severities"));
    root.append(el("div", { className: "ch-note" }, [el("span", { className: "hint", textContent: t.severities_note }), toSeverities]));
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveIt);
    const bar = el("div", { className: "tl-bar" }, [save, status]);
    root.append(bar);
    paint = () => {
      for (const update of rows) update();
      const found = [...problems(values), ...settingProblems(settings)];
      const dirty = Object.keys(changes(values, data.channels)).length > 0 || Object.keys(settingChanges(settings, savedSettings)).length > 0;
      save.disabled = found.length > 0 || !dirty;
      bar.classList.toggle("dirty", dirty);
      status.className = found.length ? "hint problems" : "hint ok";
      status.textContent = found.length ? found.map((c) => problemText(c, t)).join(" ") : message || (dirty ? t.valid : "");
    };
    paint();
  }

  function fields(key) {
    const box = el("div", { className: "tl-grid" });
    const hint = (text) => el("div", { className: "hint tl-wide", textContent: text });
    const snoozeTime = () => ui.field(t.snooze_time, ui.numberInput(settings.quick_snooze_minutes, (v) => { settings.quick_snooze_minutes = v; paint(); }, { min: 1, max: 1440 }), t.snooze_time_hint);
    if (key === "banner") {
      box.append(el("div", { className: "tl-wide ch-chips" }, [ui.chips(t.banner_snooze, SNOOZE_MINUTES.map((m) => ({ value: m, label: minutesText(m, t) })), settings.default_snooze_options || [], (list) => { settings.default_snooze_options = SNOOZE_MINUTES.filter((m) => list.includes(m)); paint(); })]));
      box.append(hint(t.banner_snooze_hint));
      return box;
    }
    if (key === "popup") {
      box.append(snoozeTime());
      const styles = ui.facts(SEVERITY_ORDER.map((sev) => [t.severities[sev], t.styles[values.popup_styles?.[sev]] || values.popup_styles?.[sev] || "–"]));
      const go = el("button", { type: "button", textContent: t.severities_link });
      go.addEventListener("click", () => ctx.navigate("severities"));
      box.append(el("div", { className: "tl-wide" }, [el("div", { className: "ch-sub", textContent: t.styles_label }), styles, el("div", { className: "ch-go" }, [el("span", { className: "hint", textContent: t.styles_hint }), go])]));
      return box;
    }
    if (key === "persistent") {
      box.append(hint(t.persistent_none));
      return box;
    }
    if (key === "inbox") {
      box.append(hint(t.inbox_intro));
      box.append(ui.field(t.inbox_retention, ui.numberInput(values.inbox_retention_months, (v) => { values.inbox_retention_months = Number.isNaN(v) ? "" : v; paint(); }, { min: 1, max: 36, step: 1 }), t.inbox_retention_note));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.inbox_all, values.inbox_all_notifications, (on) => { values.inbox_all_notifications = on; paint(); })]), hint(t.inbox_all_note));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.inbox_messages, values.inbox_messages, (on) => { values.inbox_messages = on; paint(); })]), hint(t.inbox_messages_note));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.inbox_reminder, values.inbox_reminder_unread, (on) => { values.inbox_reminder_unread = on; paint(); })]), hint(t.inbox_reminder_note));
      // What is stored, and a button that deletes every person's items after a confirmation.
      const info = el("div", { className: "hint", textContent: inboxLine(data.inbox, t) });
      const done = el("div", { className: "hint", role: "status" });
      const clear = el("button", { type: "button", textContent: t.inbox_clear });
      clear.addEventListener("click", async () => {
        if (!window.confirm(t.inbox_confirm)) return;
        try {
          const result = await hass.callWS({ type: "heads_up/inbox_clear_all" });
          data.inbox = result.info;
          info.textContent = inboxLine(data.inbox, t);
          done.textContent = t.inbox_cleared;
        } catch (err) {
          done.textContent = fill(t.inbox_failed, { error: (err && err.message) || String(err) });
        }
      });
      box.append(el("div", { className: "tl-wide" }, [info, clear, done]));
      return box;
    }
    if (key === "push") {
      box.append(snoozeTime());
      box.append(ui.field(t.lockscreen, ui.selectInput(LOCKSCREENS.map((l) => ({ value: l, label: t.lockscreens[l] })), values.push_lockscreen, (v) => { values.push_lockscreen = v; paint(); })));
      box.append(ui.field(t.channel_id, ui.textInput(values.push_channel_id, (v) => { values.push_channel_id = v; paint(); }, { spellcheck: false, autocapitalize: "off" })));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.sticky, values.push_sticky, (on) => { values.push_sticky = on; paint(); })]));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.severity_look, values.push_severity_look, (on) => { values.push_severity_look = on; paint(); })]), hint(t.severity_look_note));
      box.append(ui.field(t.progress_interval, ui.numberInput(values.push_progress_interval, (v) => { values.push_progress_interval = Number.isNaN(v) ? "" : v; paint(); }, { min: 1, max: 300, step: 1 })), hint(t.progress_interval_note));
      for (const key of ["rate_per_device_per_minute", "rate_total_per_minute"]) {
        const [min, max] = CHANNEL_RANGES[key];
        box.append(ui.field(t[`lbl_${key}`], ui.numberInput(values[key], (v) => { values[key] = Number.isNaN(v) ? "" : v; paint(); }, { min, max, step: 1 })), hint(t[`note_${key}`]));
      }
      box.append(hint(t.channel_id_note), hint(t.buttons_note));
    } else if (key === "speech") {
      if (languages?.length) {
        const options = languageOptions(languages, values.speak_language, hass?.config?.language || "en", ctx.language, t);
        box.append(el("div", { className: "tl-wide ch-lang" }, [ui.field(t.language, ui.selectInput(options, values.speak_language || "", (v) => { values.speak_language = v; paint(); }))]));
      } else {
        box.append(ui.field(t.language, ui.textInput(values.speak_language, (v) => { values.speak_language = v; paint(); }, { placeholder: hass?.config?.language || "", spellcheck: false, autocapitalize: "off" }), t.no_engine_languages));
      }
      box.append(hint(t.speech_note));
      for (const key of ["speak_max_length", "speak_cooldown_seconds"]) {
        const [min, max] = CHANNEL_RANGES[key];
        box.append(ui.field(t[`lbl_${key}`], ui.numberInput(values[key], (v) => { values[key] = Number.isNaN(v) ? "" : v; paint(); }, { min, max, step: 1 })), hint(t[`note_${key}`]));
      }
      const engines = [{ value: "", label: t.tts_auto }, ...ttsEntities(hass, values.speak_tts_entity).map((id) => ({ value: id, label: id }))];
      box.append(ui.field(t.lbl_speak_tts_entity, ui.selectInput(engines, values.speak_tts_entity || "", (v) => { values.speak_tts_entity = v; paint(); })), hint(t.note_speak_tts_entity));
      box.append(el("div", { className: "tl-wide" }, [ui.checkbox(t.lbl_speak_restore_volume, values.speak_restore_volume, (on) => { values.speak_restore_volume = on; paint(); })]), hint(t.note_speak_restore_volume));
      // One number per severity; empty means no volume for it (D-217).
      const perSeverity = el("div", { className: "tl-wide ch-volumes" }, [el("div", { className: "ch-sub", textContent: t.lbl_speak_severity_volume })]);
      for (const severity of SEVERITY_ORDER) {
        const current = (values.speak_severity_volume || {})[severity];
        perSeverity.append(ui.field(t.severities[severity], ui.numberInput(current ?? "", (v) => {
          const next = { ...(values.speak_severity_volume || {}) };
          if (Number.isNaN(v)) delete next[severity];
          else next[severity] = v;
          values.speak_severity_volume = next;
          paint();
        }, { min: 0, max: 100, step: 1 })));
      }
      box.append(perSeverity, hint(t.note_speak_severity_volume));
      // Up to four bands of the day, each with a start, an end and a volume (D-217).
      const bandsBox = el("div", { className: "tl-wide ch-bands" }, [el("div", { className: "ch-sub", textContent: t.lbl_speak_volume_bands })]);
      const bands = values.speak_volume_bands || [];
      bands.forEach((band, index) => {
        const row = el("div", { className: "ch-band" });
        const edit = (name, v) => {
          const next = bands.map((b) => ({ ...b }));
          next[index][name] = v;
          values.speak_volume_bands = next;
          paint();
        };
        row.append(ui.field(t.band_from, ui.timeInput(band.from, (v) => edit("from", v))), ui.field(t.band_to, ui.timeInput(band.to, (v) => edit("to", v))));
        row.append(ui.field(t.band_volume, ui.numberInput(band.volume ?? "", (v) => edit("volume", Number.isNaN(v) ? "" : v), { min: 0, max: 100, step: 1 })));
        const remove = el("button", { type: "button", textContent: t.band_remove });
        remove.setAttribute("aria-label", `${t.band_remove} ${index + 1}`);
        remove.addEventListener("click", () => {
          values.speak_volume_bands = bands.filter((_, i) => i !== index);
          render();
        });
        row.append(remove);
        bandsBox.append(row);
      });
      if (bands.length < MAX_BANDS) {
        const add = el("button", { type: "button", textContent: t.band_add });
        add.addEventListener("click", () => {
          values.speak_volume_bands = [...bands, { from: "22:00", to: "07:00", volume: 30 }];
          render();
        });
        bandsBox.append(add);
      }
      box.append(bandsBox, hint(t.note_speak_volume_bands));
    } else {
      const services = [...(data.choices?.notify_services || [])];
      if (values.mail_service && !services.includes(values.mail_service)) services.push(values.mail_service);
      box.append(hint(t.mail_intro));
      box.append(ui.field(t.mail_service, ui.selectInput([{ value: "", label: t.mail_service_none }, ...services.map((n) => ({ value: n, label: `notify.${n}` }))], values.mail_service, (v) => { values.mail_service = v; paint(); })));
      box.append(ui.field(t.mail_global_address, ui.textInput(values.mail_global_address, (v) => { values.mail_global_address = v; paint(); }, { inputMode: "email", autocapitalize: "off", spellcheck: false }), t.mail_global_note));
      box.append(el("div", { className: "tl-wide" }, [ui.field(t.mail_subject, ui.textInput(values.mail_subject, (v) => { values.mail_subject = v; paint(); }))]));
      box.append(el("div", { className: "tl-wide" }, [ui.field(t.mail_body, ui.textInput(values.mail_body, (v) => { values.mail_body = v; paint(); }))]));
      box.append(hint(t.mail_placeholders));
    }
    return box;
  }

  async function saveIt() {
    try {
      const own = changes(values, data.channels);
      if (Object.keys(own).length) {
        const result = await hass.callWS({ type: "heads_up/channels_set", ...own });
        data.channels = result;
        values = JSON.parse(JSON.stringify(result));
      }
      const shared = settingChanges(settings, savedSettings);
      if (Object.keys(shared).length) {
        const stored = (await hass.callWS({ type: "heads_up/settings_set", ...shared })).options || {};
        savedSettings = Object.fromEntries(SETTING_KEYS.map((k) => [k, stored[k]]));
        settings = JSON.parse(JSON.stringify(savedSettings));
      }
      message = t.saved;
    } catch (err) {
      message = t.failed;
    }
    render();
  }

  async function load() {
    data = await hass.callWS({ type: "heads_up/panel_config" });
    const stored = (await hass.callWS({ type: "heads_up/settings_get" })).options || {};
    savedSettings = Object.fromEntries(SETTING_KEYS.map((k) => [k, stored[k]]));
    settings = JSON.parse(JSON.stringify(savedSettings));
    // The languages of the engine speech uses (N-108); without one the field stays free text.
    const engine = data.choices?.tts_engine;
    if (engine) {
      try {
        languages = (await hass.callWS({ type: "tts/engine/get", engine_id: engine })).provider?.supported_languages || null;
      } catch (err) {
        languages = null;
      }
    }
    values = JSON.parse(JSON.stringify(data.channels));
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
