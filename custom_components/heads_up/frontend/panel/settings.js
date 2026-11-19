// Heads Up panel: Settings page (D-117, D-122). Loaded by the shell when the page is opened.
// The entries come from the server in the order of the integration's options screen; the wording
// is the same as in strings.json and a test compares the two.

export const STRINGS = {
  en: {
    title: "Settings",
    welcome: "Introduction",
    welcome_button: "Restart introduction",
    welcome_hint: "The introduction is a short tour: what Heads Up does, then channels, recipients and policies. Its last step offers four default policies; switching one on adds only the policies that are missing and changes nothing you have.",
    save: "Save",
    saved: "Saved.",
    valid: "No problems.",
    range: "{field} must be between {min} and {max}.",
    failed: "Could not save. Try again.",
    loading: "Loading…",
    load_failed: "The settings could not be loaded.",
    names: {"sidebar": "Sidebar panel", "dismiss": "Messages › Dismiss settings", "snooze": "Messages › Snooze settings", "snooze_banner": "Messages › Snooze settings › Banners", "snooze_push": "Messages › Snooze settings › Push & Popup", "presence": "Presence", "speech": "Speech", "speech_volume": "Speech volume", "limits": "Limits", "history": "History", "identity": "Identity"},
    desc: {"dismiss": "These settings apply to the banner, the push and the popup of a message.", "snooze": "Whether a message can be snoozed and for whom. Applies to the banner, the push and the popup.", "snooze_banner": "The banner card offers a menu with these snooze times.", "snooze_push": "The push and the popup have one Snooze button with one snooze time."},
    label: {"max_banners": "Maximum number of stored messages", "evict": "Evict the oldest lowest-severity message when full", "default_dismiss_scope": "Default dismiss scope", "default_timeout": "Default timeout", "default_snoozable": "Messages can be snoozed by default", "default_snooze_scope": "Default snooze scope", "default_snooze_options": "Snooze choices on the banner", "quick_snooze_minutes": "Snooze time on push and popup (minutes)", "disable_ended_buttons": "Disable message buttons once the message has ended", "presence_debounce_seconds": "Presence delay (seconds)", "speak_max_length": "Spoken text: longest (characters)", "speak_cooldown_seconds": "Spoken text: repeat pause (seconds)", "speak_tts_entity": "Text-to-speech engine", "speak_restore_volume": "Put the volume back after speaking", "speak_severity_volume": "Volume by severity (percent)", "speak_volume_bands": "Volume by time of day", "show_panel": "Show Heads Up in the sidebar", "rate_per_device_per_minute": "Pushes per device per minute", "rate_total_per_minute": "Deliveries per minute, all devices", "dedupe_seconds": "Seconds in which identical updates are ignored", "trace_entries": "Trace entries kept", "recent_messages": "Recent messages kept", "install_token": "Install token"},
    hint: {"max_banners": "1–200. How many messages from action calls can exist at once, on any channel; watch rules do not count. It protects Home Assistant's storage and timers, not the phones or the card (the card has its own max_items). Critical messages are never evicted.", "evict": "When off, creating a message beyond the maximum fails with an error. An evicted message ends on every channel.", "default_dismiss_scope": "Used when an action call sets no dismiss_scope. user: closing hides the message only for that person, on the banner, the push and the popup. global: closing ends it for everyone.", "default_timeout": "Used when an action call sets no timeout. The message ends on every channel after this time. Warning: if you clear this field, messages without their own timeout stay until they are dismissed or cleared.", "default_snoozable": "Used when an action call sets no snoozable. Adds a Snooze button to the banner, the push and the popup. Messages that are not dismissible are never snoozable.", "default_snooze_scope": "Used when an action call sets no snooze_scope. user: a snooze hides the message only for that person. global: for everyone. Applies to the banner, the push and the popup.", "default_snooze_options": "Used when an action call sets no snooze_options. The banner offers all choices. The push and the popup use the snooze time below. Leave empty for 15 minutes, 1 hour and 4 hours.", "quick_snooze_minutes": "1–1440. The Snooze button of the push and of the popup snoozes for this time. The banner has its own choices above.", "disable_ended_buttons": "A press of the message's own buttons is ignored after the message was dismissed, acknowledged or its condition turned false, on the banner, the push and the popup. Dismiss, Snooze and Acknowledge are not affected. Off: presses are accepted until the message is removed.", "presence_debounce_seconds": "A person must stay in or out of a zone this long before \"Last to leave\" and \"First home\" change and a Presence policy releases what it holds. 0 reacts at once.", "speak_max_length": "Longer texts are cut at a word and end with an ellipsis.", "speak_cooldown_seconds": "The same text is not spoken again on the same speaker within this time. 0: always speak.", "speak_tts_entity": "The engine that speaks on media players. Empty: the only text-to-speech entity, if there is exactly one.", "speak_restore_volume": "A speaker whose volume Heads Up changed gets its earlier volume back once the message was said, unless someone changed the volume meanwhile. Sonos speakers keep their volume and say the message at the chosen level. Off: the speaker stays at the speech volume.", "speak_severity_volume": "0–100 per severity. Empty: the time of day decides. A volume in the action call comes first.", "speak_volume_bands": "Up to 4 bands, each with a start, an end and a volume in percent. A band from 22:00 to 07:00 runs over midnight. Bands must not overlap. Outside every band the volume is not changed.", "show_panel": "Only administrators see the entry. It appears and disappears at once when you save.\n\nWithout the panel you cannot use:\n- Test send\n- the Message Log with the delivery trace of each message\n- the Overview with Needs attention\n- the introduction that creates the default policies\n- the Channels settings (push levels, popup styles, mail)\n- the Help pages\n\nAudiences, recipients, policies, watch rules and the other settings stay available under Devices & services.", "rate_per_device_per_minute": "1–600. A push over the cap is skipped; critical messages are never held back.", "rate_total_per_minute": "1–6000. A push over the cap is skipped; critical messages are never held back.", "dedupe_seconds": "0–3600. An update with the same content is not sent again within this time. 0: off.", "trace_entries": "50–5000. The delivery trace: why each message did or did not arrive. Kept across restarts. Also the length of the last actions on the Overview, which start empty after a restart.", "recent_messages": "10–1000. The messages listed in the Message Log. After a restart the list holds only the messages that have not ended.", "install_token": "Part of every push tag, so two Home Assistant servers never clear each other's pushes. Read only."},
    scope: {"user": "Per user", "global": "Everyone"},
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 hour", "120": "2 hours", "240": "4 hours", "480": "8 hours", "1440": "24 hours"},
    units: {"days": "Days", "hours": "Hours", "minutes": "Minutes", "seconds": "Seconds"},
    tts_auto: "Automatic",
    severity: {"passive": "Passive", "info": "Info", "warning": "Warning", "critical": "Critical"},
    band: {"from": "From", "to": "To", "volume": "Volume (%)", "add": "Add band", "remove": "Remove"},
    volume_errors: {"bands_invalid": "Each band needs a start and an end (HH:MM) and a volume from 0 to 100.", "bands_too_many": "At most 4 bands.", "bands_empty": "A band needs a start different from its end.", "bands_overlap": "Bands must not overlap.", "severity_volume_invalid": "Give a volume from 0 to 100 for passive, info, warning or critical."},
  },
  de: {
    title: "Einstellungen",
    welcome: "Einführung",
    welcome_button: "Einführung neu starten",
    welcome_hint: "Die Einführung ist eine kurze Tour: was Heads Up kann, dann Kanäle, Empfänger und Richtlinien. Der letzte Schritt bietet vier Standardrichtlinien an; wer eine einschaltet, fügt nur fehlende Richtlinien hinzu und ändert nichts, was du hast.",
    save: "Speichern",
    saved: "Gespeichert.",
    valid: "Keine Probleme.",
    range: "{field} muss zwischen {min} und {max} liegen.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    loading: "Lädt…",
    load_failed: "Die Einstellungen konnten nicht geladen werden.",
    names: {"sidebar": "Seitenleisten-Panel", "dismiss": "Meldungen › Einstellungen zum Schließen", "snooze": "Meldungen › Einstellungen zum Zurückstellen", "snooze_banner": "Meldungen › Einstellungen zum Zurückstellen › Banner", "snooze_push": "Meldungen › Einstellungen zum Zurückstellen › Push & Popup", "presence": "Anwesenheit", "speech": "Sprache", "speech_volume": "Lautstärke der Sprache", "limits": "Grenzen", "history": "Verlauf", "identity": "Kennung"},
    desc: {"dismiss": "Diese Einstellungen gelten für Banner, Push und Popup einer Meldung.", "snooze": "Ob eine Meldung zurückgestellt werden kann und für wen. Gilt für Banner, Push und Popup.", "snooze_banner": "Die Banner-Karte bietet ein Menü mit diesen Zeiten an.", "snooze_push": "Push und Popup haben eine Schaltfläche Zurückstellen mit einer Zeit."},
    label: {"max_banners": "Maximale Anzahl gespeicherter Meldungen", "evict": "Älteste Meldung mit der niedrigsten Dringlichkeit entfernen, wenn voll", "default_dismiss_scope": "Standard-Bereich beim Schließen", "default_timeout": "Standard-Zeitlimit", "default_snoozable": "Meldungen sind standardmäßig zurückstellbar", "default_snooze_scope": "Standard-Bereich beim Zurückstellen", "default_snooze_options": "Auswahl beim Zurückstellen im Banner", "quick_snooze_minutes": "Zurückstellzeit bei Push und Popup (Minuten)", "disable_ended_buttons": "Meldungs-Schaltflächen sperren, sobald die Meldung beendet ist", "presence_debounce_seconds": "Anwesenheitsverzögerung (Sekunden)", "speak_max_length": "Gesprochener Text: höchstens (Zeichen)", "speak_cooldown_seconds": "Gesprochener Text: Wiederholungspause (Sekunden)", "speak_tts_entity": "Text-zu-Sprache-Engine", "speak_restore_volume": "Lautstärke nach dem Sprechen zurücksetzen", "speak_severity_volume": "Lautstärke nach Schweregrad (Prozent)", "speak_volume_bands": "Lautstärke nach Uhrzeit", "show_panel": "Heads Up in der Seitenleiste anzeigen", "rate_per_device_per_minute": "Pushes pro Gerät und Minute", "rate_total_per_minute": "Zustellungen pro Minute, alle Geräte", "dedupe_seconds": "Sekunden, in denen gleiche Aktualisierungen ignoriert werden", "trace_entries": "Gespeicherte Protokolleinträge", "recent_messages": "Gespeicherte letzte Meldungen", "install_token": "Installations-Token"},
    hint: {"max_banners": "1–200. Wie viele Meldungen aus Aktionsaufrufen gleichzeitig bestehen können, auf jedem Kanal; Überwachungsregeln zählen nicht. Es schützt Speicher und Timer von Home Assistant, nicht die Telefone oder die Karte (die Karte hat ihr eigenes max_items). Kritische Meldungen werden nie entfernt.", "evict": "Wenn aus, schlägt das Erstellen einer Meldung über dem Maximum mit einem Fehler fehl. Eine entfernte Meldung endet auf jedem Kanal.", "default_dismiss_scope": "Gilt, wenn ein Aktionsaufruf kein dismiss_scope angibt. user: Schließen verbirgt die Meldung nur für diese Person, im Banner, im Push und im Popup. global: Schließen beendet sie für alle.", "default_timeout": "Gilt, wenn ein Aktionsaufruf kein timeout angibt. Die Meldung endet nach dieser Zeit auf jedem Kanal. Achtung: Wenn du dieses Feld leerst, bleiben Meldungen ohne eigenes Zeitlimit, bis sie geschlossen oder entfernt werden.", "default_snoozable": "Gilt, wenn ein Aktionsaufruf kein snoozable angibt. Fügt dem Banner, dem Push und dem Popup eine Schaltfläche Zurückstellen hinzu. Meldungen, die nicht schließbar sind, sind nie zurückstellbar.", "default_snooze_scope": "Gilt, wenn ein Aktionsaufruf kein snooze_scope angibt. user: Zurückstellen verbirgt die Meldung nur für diese Person. global: für alle. Gilt für Banner, Push und Popup.", "default_snooze_options": "Gilt, wenn ein Aktionsaufruf kein snooze_options angibt. Der Banner bietet alle Möglichkeiten an. Push und Popup nutzen die Zeit darunter. Leer lassen für 15 Minuten, 1 Stunde und 4 Stunden.", "quick_snooze_minutes": "1–1440. Die Schaltfläche Zurückstellen von Push und Popup stellt für diese Zeit zurück. Der Banner hat oben seine eigene Auswahl.", "disable_ended_buttons": "Ein Tastendruck auf die eigenen Schaltflächen der Meldung wird ignoriert, wenn die Meldung geschlossen oder bestätigt wurde oder ihre Bedingung nicht mehr erfüllt ist, im Banner, im Push und im Popup. Schließen, Zurückstellen und Bestätigen sind nicht betroffen. Aus: Tastendrücke gelten, bis die Meldung entfernt wird.", "presence_debounce_seconds": "Eine Person muss so lange in oder außerhalb einer Zone bleiben, bevor sich \"Last to leave\" und \"First home\" ändern und eine Anwesenheitsrichtlinie freigibt, was sie zurückhält. 0 reagiert sofort.", "speak_max_length": "Längere Texte werden an einem Wortende gekürzt und enden mit Auslassungspunkten.", "speak_cooldown_seconds": "Derselbe Text wird auf demselben Lautsprecher innerhalb dieser Zeit nicht noch einmal gesprochen. 0: immer sprechen.", "speak_tts_entity": "Die Engine, die auf Mediaplayern spricht. Leer: die einzige Text-zu-Sprache-Entität, wenn es genau eine gibt.", "speak_restore_volume": "Ein Lautsprecher, dessen Lautstärke Heads Up geändert hat, bekommt seine vorherige Lautstärke zurück, sobald die Meldung gesagt ist, außer jemand hat die Lautstärke inzwischen geändert. Sonos-Lautsprecher behalten ihre Lautstärke und sagen die Meldung in der gewählten Lautstärke. Aus: der Lautsprecher bleibt auf der Sprachlautstärke.", "speak_severity_volume": "0–100 pro Schweregrad. Leer: die Uhrzeit entscheidet. Eine Lautstärke im Aktionsaufruf hat Vorrang.", "speak_volume_bands": "Bis zu 4 Zeiträume, jeder mit Beginn, Ende und Lautstärke in Prozent. Ein Zeitraum von 22:00 bis 07:00 geht über Mitternacht. Zeiträume dürfen sich nicht überschneiden. Außerhalb aller Zeiträume bleibt die Lautstärke unverändert.", "show_panel": "Nur Administratoren sehen den Eintrag. Er erscheint und verschwindet sofort beim Speichern.\n\nOhne das Panel kannst du nicht nutzen:\n- Testsenden\n- das Meldungsprotokoll mit dem Ablauf jeder Meldung\n- die Übersicht mit Braucht Aufmerksamkeit\n- die Einführung mit den Standardrichtlinien\n- die Kanal-Einstellungen (Push-Stufen, Popup-Stile, Mail)\n- die Hilfe-Seiten\n\nZielgruppen, Empfänger, Richtlinien, Überwachungsregeln und die übrigen Einstellungen bleiben unter Geräte & Dienste verfügbar.", "rate_per_device_per_minute": "1–600. Ein Push über dem Limit wird übersprungen; kritische Meldungen werden nie zurückgehalten.", "rate_total_per_minute": "1–6000. Ein Push über dem Limit wird übersprungen; kritische Meldungen werden nie zurückgehalten.", "dedupe_seconds": "0–3600. Eine Aktualisierung mit gleichem Inhalt wird in dieser Zeit nicht erneut gesendet. 0: aus.", "trace_entries": "50–5000. Die Zustellspur: warum jede Meldung ankam oder nicht. Bleibt über Neustarts erhalten. Auch die Länge der letzten Aktionen in der Übersicht, die nach einem Neustart leer beginnen.", "recent_messages": "10–1000. Die Meldungen im Meldungsprotokoll. Nach einem Neustart enthält die Liste nur Meldungen, die noch nicht beendet sind.", "install_token": "Teil jedes Push-Tags, damit zwei Home-Assistant-Server die Pushes des anderen nie löschen. Nur lesbar."},
    scope: {"user": "Pro Benutzer", "global": "Alle"},
    minutes: {"5": "5 Minuten", "15": "15 Minuten", "30": "30 Minuten", "60": "1 Stunde", "120": "2 Stunden", "240": "4 Stunden", "480": "8 Stunden", "1440": "24 Stunden"},
    units: {"days": "Tage", "hours": "Stunden", "minutes": "Minuten", "seconds": "Sekunden"},
    tts_auto: "Automatisch",
    severity: {"passive": "Passiv", "info": "Info", "warning": "Warnung", "critical": "Kritisch"},
    band: {"from": "Von", "to": "Bis", "volume": "Lautstärke (%)", "add": "Zeitraum hinzufügen", "remove": "Entfernen"},
    volume_errors: {"bands_invalid": "Jeder Zeitraum braucht Beginn und Ende (HH:MM) und eine Lautstärke von 0 bis 100.", "bands_too_many": "Höchstens 4 Zeiträume.", "bands_empty": "Beginn und Ende eines Zeitraums müssen verschieden sein.", "bands_overlap": "Zeiträume dürfen sich nicht überschneiden.", "severity_volume_invalid": "Gib eine Lautstärke von 0 bis 100 für passive, info, warning oder critical an."},
  },
  fr: {
    title: "Réglages",
    welcome: "Introduction",
    welcome_button: "Relancer l'introduction",
    welcome_hint: "L'introduction est une courte visite : ce que fait Heads Up, puis les canaux, les destinataires et les politiques. Sa dernière étape propose quatre politiques par défaut ; en activer une n'ajoute que les politiques manquantes et ne change rien de ce que vous avez.",
    save: "Enregistrer",
    saved: "Enregistré.",
    valid: "Aucun problème.",
    range: "{field} doit être entre {min} et {max}.",
    failed: "Enregistrement impossible. Réessayez.",
    loading: "Chargement…",
    load_failed: "Les réglages n'ont pas pu être chargés.",
    names: {"sidebar": "Panneau de la barre latérale", "dismiss": "Messages › Réglages de fermeture", "snooze": "Messages › Réglages du report", "snooze_banner": "Messages › Réglages du report › Bannières", "snooze_push": "Messages › Réglages du report › Push et popup", "presence": "Présence", "speech": "Voix", "speech_volume": "Volume de la voix", "limits": "Limites", "history": "Historique", "identity": "Identité"},
    desc: {"dismiss": "Ces réglages valent pour la bannière, le push et le popup d'un message.", "snooze": "Si un message peut être reporté, et pour qui. Valable pour la bannière, le push et le popup.", "snooze_banner": "La carte bannière propose un menu avec ces durées.", "snooze_push": "Le push et le popup ont un bouton Reporter avec une seule durée."},
    label: {"max_banners": "Nombre maximal de messages conservés", "evict": "Supprimer le plus ancien message de moindre gravité quand la limite est atteinte", "default_dismiss_scope": "Portée de fermeture par défaut", "default_timeout": "Délai d'expiration par défaut", "default_snoozable": "Les messages peuvent être reportés par défaut", "default_snooze_scope": "Portée du report par défaut", "default_snooze_options": "Durées de report sur la bannière", "quick_snooze_minutes": "Durée de report sur le push et le popup (minutes)", "disable_ended_buttons": "Désactiver les boutons du message une fois celui-ci terminé", "presence_debounce_seconds": "Délai de présence (secondes)", "speak_max_length": "Texte parlé : longueur maximale (caractères)", "speak_cooldown_seconds": "Texte parlé : pause avant répétition (secondes)", "speak_tts_entity": "Moteur de synthèse vocale", "speak_restore_volume": "Remettre le volume après avoir parlé", "speak_severity_volume": "Volume par gravité (pour cent)", "speak_volume_bands": "Volume selon l'heure", "show_panel": "Afficher Heads Up dans la barre latérale", "rate_per_device_per_minute": "Push par appareil et par minute", "rate_total_per_minute": "Livraisons par minute, tous appareils", "dedupe_seconds": "Secondes pendant lesquelles les mises à jour identiques sont ignorées", "trace_entries": "Entrées de trace conservées", "recent_messages": "Messages récents conservés", "install_token": "Jeton d'installation"},
    hint: {"max_banners": "1–200. Combien de messages d'appels d'action peuvent exister en même temps, sur tout canal ; les règles de surveillance ne comptent pas. Cela protège le stockage et les minuteries de Home Assistant, pas les téléphones ni la carte (la carte a son propre max_items). Les messages critiques ne sont jamais supprimés.", "evict": "Désactivé : créer un message au-delà du maximum échoue avec une erreur. Un message supprimé se termine sur tous les canaux.", "default_dismiss_scope": "Utilisé quand l'appel d'action ne définit pas dismiss_scope. user : fermer ne masque le message que pour cette personne, sur la bannière, le push et le popup. global : fermer le termine pour tout le monde.", "default_timeout": "Utilisé quand l'appel d'action ne définit pas timeout. Le message se termine sur tous les canaux après ce délai. Attention : si vous videz ce champ, les messages sans délai propre restent jusqu'à leur fermeture ou suppression.", "default_snoozable": "Utilisé quand l'appel d'action ne définit pas snoozable. Ajoute un bouton Reporter à la bannière, au push et au popup. Les messages non fermables ne sont jamais reportables.", "default_snooze_scope": "Utilisé quand l'appel d'action ne définit pas snooze_scope. user : un report ne masque le message que pour cette personne. global : pour tout le monde. Valable pour la bannière, le push et le popup.", "default_snooze_options": "Utilisé quand l'appel d'action ne définit pas snooze_options. La bannière propose toutes les durées. Le push et le popup utilisent la durée ci-dessous. Laisser vide pour 15 minutes, 1 heure et 4 heures.", "quick_snooze_minutes": "1–1440. Le bouton Reporter du push et du popup reporte pour cette durée. La bannière a ses propres durées ci-dessus.", "disable_ended_buttons": "Un appui sur les boutons propres du message est ignoré après que le message a été fermé, confirmé ou que sa condition n'est plus vraie, sur la bannière, le push et le popup. Fermer, Reporter et Confirmer ne sont pas concernés. Désactivé : les appuis sont acceptés jusqu'à la suppression du message.", "presence_debounce_seconds": "Une personne doit rester dans ou hors d'une zone ce temps avant que « Last to leave » et « First home » changent et qu'une politique de présence libère ce qu'elle retient. 0 réagit tout de suite.", "speak_max_length": "Les textes plus longs sont coupés à la fin d'un mot et se terminent par des points de suspension.", "speak_cooldown_seconds": "Le même texte n'est pas redit sur le même haut-parleur pendant ce délai. 0 : toujours dire.", "speak_tts_entity": "Le moteur qui parle sur les lecteurs multimédia. Vide : la seule entité de synthèse vocale, s'il n'y en a qu'une.", "speak_restore_volume": "Un haut-parleur dont Heads Up a changé le volume retrouve son volume précédent une fois le message dit, sauf si quelqu'un a changé le volume entre-temps. Les haut-parleurs Sonos gardent leur volume et disent le message au niveau choisi. Désactivé : le haut-parleur reste au volume de la voix.", "speak_severity_volume": "0–100 par gravité. Vide : l'heure décide. Un volume dans l'appel d'action passe en premier.", "speak_volume_bands": "Jusqu'à 4 plages, chacune avec un début, une fin et un volume en pour cent. Une plage de 22:00 à 07:00 passe minuit. Les plages ne doivent pas se chevaucher. En dehors de toute plage, le volume ne change pas.", "show_panel": "Seuls les administrateurs voient l'entrée. Elle apparaît et disparaît tout de suite à l'enregistrement.\n\nSans le panneau, vous ne pouvez pas utiliser :\n- Envoi de test\n- le journal des messages avec la trace de chaque message\n- la vue d'ensemble avec À surveiller\n- l'introduction qui crée les politiques par défaut\n- les réglages des canaux (niveaux de push, styles de popup, mail)\n- les pages d'aide\n\nLes audiences, destinataires, politiques, règles de surveillance et les autres réglages restent disponibles sous Appareils et services.", "rate_per_device_per_minute": "1–600. Un push au-delà de la limite est ignoré ; les messages critiques ne sont jamais retenus.", "rate_total_per_minute": "1–6000. Un push au-delà de la limite est ignoré ; les messages critiques ne sont jamais retenus.", "dedupe_seconds": "0–3600. Une mise à jour au contenu identique n'est pas renvoyée pendant ce délai. 0 : désactivé.", "trace_entries": "50–5000. La trace de distribution : pourquoi chaque message est arrivé ou non. Conservée après un redémarrage. Aussi la longueur des dernières actions de la vue d'ensemble, vides après un redémarrage.", "recent_messages": "10–1000. Les messages listés dans le journal des messages. Après un redémarrage, la liste ne contient que les messages qui ne sont pas terminés.", "install_token": "Fait partie de chaque étiquette de push, pour que deux serveurs Home Assistant n'effacent jamais les push de l'autre. Lecture seule."},
    scope: {"user": "Par utilisateur", "global": "Tout le monde"},
    minutes: {"5": "5 minutes", "15": "15 minutes", "30": "30 minutes", "60": "1 heure", "120": "2 heures", "240": "4 heures", "480": "8 heures", "1440": "24 heures"},
    units: {"days": "Jours", "hours": "Heures", "minutes": "Minutes", "seconds": "Secondes"},
    tts_auto: "Automatique",
    severity: {"passive": "Passif", "info": "Info", "warning": "Avertissement", "critical": "Critique"},
    band: {"from": "De", "to": "À", "volume": "Volume (%)", "add": "Ajouter une plage", "remove": "Retirer"},
    volume_errors: {"bands_invalid": "Chaque plage a besoin d'un début et d'une fin (HH:MM) et d'un volume de 0 à 100.", "bands_too_many": "4 plages au plus.", "bands_empty": "Le début et la fin d'une plage doivent être différents.", "bands_overlap": "Les plages ne doivent pas se chevaucher.", "severity_volume_invalid": "Indiquez un volume de 0 à 100 pour passive, info, warning ou critical."},
  },
  es: {
    title: "Ajustes",
    welcome: "Introducción",
    welcome_button: "Reiniciar la introducción",
    welcome_hint: "La introducción es un recorrido corto: qué hace Heads Up, luego canales, destinatarios y políticas. Su último paso ofrece cuatro políticas por defecto; activar una solo añade las políticas que faltan y no cambia nada de lo que tienes.",
    save: "Guardar",
    saved: "Guardado.",
    valid: "Sin problemas.",
    range: "{field} debe estar entre {min} y {max}.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    loading: "Cargando…",
    load_failed: "No se pudieron cargar los ajustes.",
    names: {"sidebar": "Panel de la barra lateral", "dismiss": "Mensajes › Ajustes de cierre", "snooze": "Mensajes › Ajustes de posposición", "snooze_banner": "Mensajes › Ajustes de posposición › Avisos", "snooze_push": "Mensajes › Ajustes de posposición › Push y ventana emergente", "presence": "Presencia", "speech": "Voz", "speech_volume": "Volumen de la voz", "limits": "Límites", "history": "Historial", "identity": "Identidad"},
    desc: {"dismiss": "Estos ajustes valen para el aviso, el push y la ventana emergente de un mensaje.", "snooze": "Si un mensaje se puede posponer y para quién. Vale para el aviso, el push y la ventana emergente.", "snooze_banner": "La tarjeta de avisos ofrece un menú con estos tiempos.", "snooze_push": "El push y la ventana emergente tienen un botón Posponer con un solo tiempo."},
    label: {"max_banners": "Número máximo de mensajes guardados", "evict": "Eliminar el mensaje más antiguo de menor gravedad cuando se llena", "default_dismiss_scope": "Ámbito de cierre predeterminado", "default_timeout": "Tiempo de caducidad predeterminado", "default_snoozable": "Los mensajes se pueden posponer de forma predeterminada", "default_snooze_scope": "Ámbito de posposición predeterminado", "default_snooze_options": "Opciones de posposición en el aviso", "quick_snooze_minutes": "Tiempo de posposición en push y ventana emergente (minutos)", "disable_ended_buttons": "Desactivar los botones del mensaje cuando haya terminado", "presence_debounce_seconds": "Retraso de presencia (segundos)", "speak_max_length": "Texto hablado: longitud máxima (caracteres)", "speak_cooldown_seconds": "Texto hablado: pausa de repetición (segundos)", "speak_tts_entity": "Motor de texto a voz", "speak_restore_volume": "Devolver el volumen después de hablar", "speak_severity_volume": "Volumen por gravedad (por ciento)", "speak_volume_bands": "Volumen según la hora", "show_panel": "Mostrar Heads Up en la barra lateral", "rate_per_device_per_minute": "Pushes por dispositivo y minuto", "rate_total_per_minute": "Entregas por minuto, todos los dispositivos", "dedupe_seconds": "Segundos en que se ignoran las actualizaciones idénticas", "trace_entries": "Entradas de traza guardadas", "recent_messages": "Mensajes recientes guardados", "install_token": "Token de instalación"},
    hint: {"max_banners": "1–200. Cuántos mensajes de llamadas a la acción pueden existir a la vez, en cualquier canal; las reglas de vigilancia no cuentan. Protege el almacenamiento y los temporizadores de Home Assistant, no los teléfonos ni la tarjeta (la tarjeta tiene su propio max_items). Los mensajes críticos nunca se eliminan.", "evict": "Si está desactivado, crear un mensaje por encima del máximo falla con un error. Un mensaje eliminado termina en todos los canales.", "default_dismiss_scope": "Se usa cuando la llamada a la acción no define dismiss_scope. user: cerrar oculta el mensaje solo a esa persona, en el aviso, el push y la ventana emergente. global: cerrar lo termina para todos.", "default_timeout": "Se usa cuando la llamada a la acción no define timeout. El mensaje termina en todos los canales tras este tiempo. Atención: si vacías este campo, los mensajes sin tiempo propio permanecen hasta que se cierran o se eliminan.", "default_snoozable": "Se usa cuando la llamada a la acción no define snoozable. Añade un botón Posponer al aviso, al push y a la ventana emergente. Los mensajes que no se pueden cerrar nunca se pueden posponer.", "default_snooze_scope": "Se usa cuando la llamada a la acción no define snooze_scope. user: posponer oculta el mensaje solo a esa persona. global: a todos. Vale para el aviso, el push y la ventana emergente.", "default_snooze_options": "Se usa cuando la llamada a la acción no define snooze_options. El aviso ofrece todas las opciones. El push y la ventana emergente usan el tiempo de abajo. Déjalo vacío para 15 minutos, 1 hora y 4 horas.", "quick_snooze_minutes": "1–1440. El botón Posponer del push y de la ventana emergente pospone durante este tiempo. El aviso tiene sus propias opciones arriba.", "disable_ended_buttons": "Se ignora una pulsación en los botones propios del mensaje después de que el mensaje se descarte, se confirme o su condición deje de cumplirse, en el aviso, el push y la ventana emergente. Descartar, Posponer y Confirmar no se ven afectados. Desactivado: se aceptan pulsaciones hasta que se elimine el mensaje.", "presence_debounce_seconds": "Una persona debe estar dentro o fuera de una zona este tiempo antes de que cambien \"Last to leave\" y \"First home\" y una política de presencia libere lo que retiene. 0 reacciona al instante.", "speak_max_length": "Los textos más largos se cortan al final de una palabra y terminan con puntos suspensivos.", "speak_cooldown_seconds": "El mismo texto no se repite en el mismo altavoz dentro de este tiempo. 0: hablar siempre.", "speak_tts_entity": "El motor que habla en los reproductores multimedia. Vacío: la única entidad de texto a voz, si solo hay una.", "speak_restore_volume": "Un altavoz cuyo volumen cambió Heads Up recupera su volumen anterior en cuanto se dijo el mensaje, salvo que alguien haya cambiado el volumen mientras tanto. Los altavoces Sonos mantienen su volumen y dicen el mensaje al nivel elegido. Desactivado: el altavoz se queda al volumen de la voz.", "speak_severity_volume": "0–100 por gravedad. Vacío: decide la hora. Un volumen en la llamada a la acción va primero.", "speak_volume_bands": "Hasta 4 franjas, cada una con inicio, fin y un volumen en por ciento. Una franja de 22:00 a 07:00 pasa la medianoche. Las franjas no deben solaparse. Fuera de toda franja el volumen no cambia.", "show_panel": "Solo los administradores ven la entrada. Aparece y desaparece al guardar.\n\nSin el panel no puedes usar:\n- Envío de prueba\n- el registro de mensajes con el rastro de cada mensaje\n- el resumen con Requiere atención\n- la introducción que crea las políticas por defecto\n- los ajustes de canales (niveles de push, estilos de ventana, correo)\n- las páginas de ayuda\n\nLas audiencias, destinatarios, políticas, reglas de vigilancia y los demás ajustes siguen disponibles en Dispositivos y servicios.", "rate_per_device_per_minute": "1–600. Un push por encima del límite se omite; los mensajes críticos nunca se retienen.", "rate_total_per_minute": "1–6000. Un push por encima del límite se omite; los mensajes críticos nunca se retienen.", "dedupe_seconds": "0–3600. Una actualización con el mismo contenido no se reenvía durante este tiempo. 0: desactivado.", "trace_entries": "50–5000. La traza de entrega: por qué cada mensaje llegó o no. Se conserva tras reiniciar. También la longitud de las últimas acciones del resumen, que empiezan vacías tras reiniciar.", "recent_messages": "10–1000. Los mensajes del registro de mensajes. Tras reiniciar, la lista solo contiene los mensajes que no han terminado.", "install_token": "Parte de cada etiqueta de push, para que dos servidores de Home Assistant nunca borren los push del otro. Solo lectura."},
    scope: {"user": "Por usuario", "global": "Todos"},
    minutes: {"5": "5 minutos", "15": "15 minutos", "30": "30 minutos", "60": "1 hora", "120": "2 horas", "240": "4 horas", "480": "8 horas", "1440": "24 horas"},
    units: {"days": "Días", "hours": "Horas", "minutes": "Minutos", "seconds": "Segundos"},
    tts_auto: "Automático",
    severity: {"passive": "Pasivo", "info": "Info", "warning": "Advertencia", "critical": "Crítico"},
    band: {"from": "Desde", "to": "Hasta", "volume": "Volumen (%)", "add": "Añadir franja", "remove": "Quitar"},
    volume_errors: {"bands_invalid": "Cada franja necesita un inicio y un fin (HH:MM) y un volumen de 0 a 100.", "bands_too_many": "Como máximo 4 franjas.", "bands_empty": "El inicio y el fin de una franja deben ser distintos.", "bands_overlap": "Las franjas no deben solaparse.", "severity_volume_invalid": "Indica un volumen de 0 a 100 para passive, info, warning o critical."},
  },
};

// Ranges of the numbers and the duration, from the layout the server sends: { key: [min, max] }.
// Sections the Channels page shows on its Banner, Push and Popup rows; Home Assistant's own
// options form still lists them.
export const ON_CHANNELS = ["snooze_banner", "snooze_push"];

export function rangesOf(layout) {
  const ranges = {};
  for (const section of layout) for (const entry of section.entries) if (entry.range) ranges[entry.key] = entry.range;
  return ranges;
}

// Problems of a set of values, as { key, min, max } for the page to word. Empty means valid.
export function problems(values, ranges) {
  const found = [];
  for (const [key, [min, max]] of Object.entries(ranges)) {
    const value = values[key];
    if (!Number.isInteger(value) || value < min || value > max) found.push({ key, min, max });
  }
  return found;
}

const SEVERITY_ORDER = ["critical", "warning", "info", "passive"];
const MAX_BANDS = 4;

function bandMinutes(band) {
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

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// What differs from the saved values: only those keys are sent.
export function changes(values, saved) {
  const out = {};
  for (const key of Object.keys(saved)) if (!same(values[key], saved[key])) out[key] = values[key];
  return out;
}

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value), template);
}

// A duration in seconds as days, hours, minutes and seconds, and back (the form of the options screen).
export function splitDuration(seconds) {
  const total = Number.isInteger(seconds) && seconds > 0 ? seconds : 0;
  return { days: Math.floor(total / 86400), hours: Math.floor((total % 86400) / 3600), minutes: Math.floor((total % 3600) / 60), seconds: total % 60 };
}

export function joinDuration(parts) {
  const n = (v) => (Number.isInteger(v) && v > 0 ? v : 0);
  return n(parts.days) * 86400 + n(parts.hours) * 3600 + n(parts.minutes) * 60 + n(parts.seconds);
}

// A section name can be a path ("Messages › Snooze settings › Banners"): the first part is a heading
// over the sections that share it, the rest is the title of the card. The options screen of Home
// Assistant has no nesting, so it shows the whole path as the name of its section.
export const PATH_SEPARATOR = " › ";

export function headingOf(name) {
  const parts = name.split(PATH_SEPARATOR);
  return parts.length > 1 ? { group: parts[0], title: parts.slice(1).join(PATH_SEPARATOR) } : { group: null, title: name };
}

// The entries of every section in the order the server sends, with their texts: the same list the
// integration's options screen shows (D-122).
export function entriesOf(layout, t) {
  return layout.map((section) => ({
    name: t.names[section.name],
    desc: t.desc?.[section.name] ?? "",
    entries: section.entries.map((entry) => ({ ...entry, label: t.label[entry.key], hint: t.hint[entry.key] })),
  }));
}

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-settings section { background: var(--card-background-color); border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: var(--ha-card-box-shadow, none); border: 1px solid var(--divider-color); }
.hu-settings h2 { font-size: 16px; margin: 0 0 8px; }
.hu-settings h2.group { font-size: 18px; margin: 24px 0 8px; }
.hu-settings h3 { font-size: 15px; margin: 0 0 8px; }
.hu-settings .rich p { margin: 0 0 6px; }
.hu-settings .rich ul { margin: 0 0 6px; padding-left: 20px; list-style: disc; }
.hu-settings .rich li { margin: 2px 0; padding: 0; }
.hu-settings .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; }
.hu-settings label.field { display: flex; align-items: center; gap: 10px; min-height: 48px; }
.hu-settings label.num { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
.hu-settings input[type=number], .hu-settings input[type=text] { min-height: 40px; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color);
  background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; max-width: 200px; }
.hu-settings select { min-height: 40px; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; max-width: 320px; }
.hu-settings input[type=checkbox] { width: 24px; height: 24px; }
.hu-settings fieldset { border: 1px solid var(--divider-color); border-radius: 8px; margin: 0 0 4px; padding: 4px 12px 8px; }
.hu-settings legend { padding: 0 6px; color: var(--secondary-text-color); font-size: 13px; }
.hu-settings .row { display: flex; gap: 12px; flex-wrap: wrap; }
.hu-settings button { min-height: 48px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-settings button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-settings button:disabled { opacity: .5; cursor: default; }
.hu-settings button:focus-visible, .hu-settings input:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-settings table { width: 100%; border-collapse: collapse; }
.hu-settings th, .hu-settings td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--divider-color); }
.hu-settings .problems { color: var(--error-color); }
.hu-settings .ok { color: var(--success-color); }
`;

export function mount(container, ctx) {
  const t = ctx.t;
  let hass = ctx.hass;
  let data = null;
  let values = {};
  let message = "";
  const root = el("div", { className: "hu-settings" });
  root.append(el("style", { textContent: CSS }), el("div", { textContent: t.loading }));
  container.append(root);

  const call = (payload) => hass.callWS(payload);
  const touched = () => {
    message = "";
    paintStatus();
  };

  function control(entry) {
    const { key, kind } = entry;
    const hint = ctx.ui.richNode(entry.hint, { className: "hint" });
    if (kind === "bool") {
      const input = el("input", { type: "checkbox", checked: Boolean(values[key]) });
      input.addEventListener("change", () => {
        values[key] = input.checked;
        touched();
      });
      return [el("label", { className: "field" }, [input, el("span", { textContent: entry.label })]), hint];
    }
    if (kind === "int") {
      const [min, max] = entry.range;
      const input = el("input", { type: "number", value: String(values[key] ?? ""), min, max, step: 1 });
      input.addEventListener("input", () => {
        values[key] = input.value === "" ? NaN : Number(input.value);
        touched();
      });
      return [el("label", { className: "num" }, [el("span", { textContent: entry.label }), input]), hint];
    }
    if (kind === "choice" || kind === "tts") {
      const options =
        kind === "choice"
          ? entry.choices.map((c) => [c, t.scope[c]])
          : [["", t.tts_auto], ...ttsEntities(hass, values[key]).map((id) => [id, id])];
      const select = el("select", {});
      for (const [value, text] of options) select.append(el("option", { value, textContent: text, selected: values[key] === value }));
      select.addEventListener("change", () => {
        values[key] = select.value;
        touched();
      });
      return [el("label", { className: "num" }, [el("span", { textContent: entry.label }), select]), hint];
    }
    if (kind === "duration") {
      const parts = splitDuration(values[key]);
      const row = el("div", { className: "row" });
      for (const unit of ["days", "hours", "minutes", "seconds"]) {
        const input = el("input", { type: "number", value: String(parts[unit]), min: 0, step: 1 });
        input.setAttribute("aria-label", `${entry.label}: ${t.units[unit]}`);
        input.addEventListener("input", () => {
          parts[unit] = input.value === "" ? 0 : Number(input.value);
          values[key] = joinDuration(parts);
          touched();
        });
        row.append(el("label", { className: "num" }, [el("span", { textContent: t.units[unit] }), input]));
      }
      return [el("fieldset", {}, [el("legend", { textContent: entry.label }), row]), hint];
    }
    if (kind === "severity_percent") {
      // One number per severity; empty means no volume for it (D-217).
      const row = el("div", { className: "row" });
      for (const severity of SEVERITY_ORDER) {
        const current = (values[key] || {})[severity];
        const input = el("input", { type: "number", value: current ?? "", min: 0, max: 100, step: 1 });
        input.setAttribute("aria-label", `${entry.label}: ${t.severity[severity]}`);
        input.addEventListener("input", () => {
          const next = { ...(values[key] || {}) };
          if (input.value === "") delete next[severity];
          else next[severity] = Number(input.value);
          values[key] = next;
          touched();
        });
        row.append(el("label", { className: "num" }, [el("span", { textContent: t.severity[severity] }), input]));
      }
      return [el("fieldset", {}, [el("legend", { textContent: entry.label }), row]), hint];
    }
    if (kind === "bands") {
      // Up to four rows of from, to and volume, with Remove and Add band (D-217).
      const box = el("fieldset", {}, [el("legend", { textContent: entry.label })]);
      const bands = values[key] || [];
      bands.forEach((band, index) => {
        const row = el("div", { className: "row" });
        const field = (name, props) => {
          const input = el("input", { ...props, value: String(band[name] ?? "") });
          input.setAttribute("aria-label", `${entry.label} ${index + 1}: ${t.band[name]}`);
          input.addEventListener("input", () => {
            const next = bands.map((b) => ({ ...b }));
            next[index][name] = name === "volume" ? (input.value === "" ? NaN : Number(input.value)) : input.value;
            values[key] = next;
            touched();
          });
          row.append(el("label", { className: "num" }, [el("span", { textContent: t.band[name] }), input]));
        };
        field("from", { type: "time" });
        field("to", { type: "time" });
        field("volume", { type: "number", min: 0, max: 100, step: 1 });
        const remove = el("button", { type: "button", textContent: t.band.remove });
        remove.setAttribute("aria-label", `${t.band.remove} ${index + 1}`);
        remove.addEventListener("click", () => {
          values[key] = bands.filter((_, i) => i !== index);
          touched();
          render();
        });
        row.append(remove);
        box.append(row);
      });
      if (bands.length < MAX_BANDS) {
        const add = el("button", { type: "button", textContent: t.band.add });
        add.addEventListener("click", () => {
          values[key] = [...bands, { from: "22:00", to: "07:00", volume: 30 }];
          touched();
          render();
        });
        box.append(add);
      }
      return [box, hint];
    }
    // minutes: the snooze choices, one checkbox each
    const box = el("fieldset", {}, [el("legend", { textContent: entry.label })]);
    for (const minutes of entry.choices) {
      const input = el("input", { type: "checkbox", checked: values[key].includes(minutes) });
      input.addEventListener("change", () => {
        const set = new Set(values[key]);
        if (input.checked) set.add(minutes);
        else set.delete(minutes);
        values[key] = [...set].sort((a, b) => a - b);
        touched();
      });
      box.append(el("label", { className: "field" }, [input, el("span", { textContent: t.minutes[String(minutes)] })]));
    }
    return [box, hint];
  }

  function render() {
    ctx.ui?.lockHeight(root);
    root.replaceChildren(el("style", { textContent: CSS }));
    root.append(el("h1", { textContent: t.title, style: "font-size:22px;margin:0 0 16px" }));
    // Every block of settings sits under a heading of its own, so a card never looks like it belongs to
    // the heading above it. A card of a path ("Messages › Snooze settings") has a smaller title of its own.
    const group = (title) => root.append(el("h2", { className: "group", textContent: title }));
    const section = (title, children, level = "h2") => {
      const box = el("section", {}, [...(title ? [el(level, { textContent: title })] : []), ...children]);
      root.append(box);
      return box;
    };

    const welcomeButton = el("button", { type: "button", textContent: t.welcome_button });
    welcomeButton.addEventListener("click", () => ctx.openWelcome());
    group(t.welcome);
    section(null, [welcomeButton, el("div", { className: "hint", textContent: t.welcome_hint })]);

    let shown = null;
    for (const block of entriesOf(data.layout.filter((section) => !ON_CHANNELS.includes(section.name)), t)) {
      const { group: top, title } = headingOf(block.name);
      if (!top || top !== shown) group(top || title);
      shown = top;
      const intro = block.desc ? [el("div", { className: "hint", textContent: block.desc })] : [];
      section(top ? title : null, [...intro, ...block.entries.flatMap(control)], "h3");
    }

    const token = el("input", { type: "text", value: data.install_token, readOnly: true });
    token.setAttribute("aria-label", t.label.install_token);
    group(t.names.identity);
    section(null, [
      el("label", { className: "num" }, [el("span", { textContent: t.label.install_token }), token]),
      el("div", { className: "hint", textContent: t.hint.install_token }),
    ]);

    const save = el("button", { type: "button", className: "primary", textContent: t.save });
    save.addEventListener("click", saveSettings);
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    root.append(save, status);
    root._save = save;
    root._status = status;
    paintStatus();
  }

  function paintStatus() {
    const found = problems(values, rangesOf(data.layout));
    const volume = volumeProblems(values);
    const dirty = Object.keys(changes(values, data.options)).length > 0;
    root._save.disabled = found.length > 0 || volume.length > 0 || !dirty;
    root._status.className = found.length || volume.length ? "hint problems" : "hint ok";
    root._status.textContent =
      found.length || volume.length
        ? [
            ...found.map((p) => fill(t.range, { field: t.label[p.key], min: p.min, max: p.max })),
            ...volume.map((code) => t.volume_errors[code]),
          ].join(" ")
        : message || (dirty ? t.valid : "");
  }

  async function saveSettings() {
    try {
      const result = await call({ type: "heads_up/settings_set", ...changes(values, data.options) });
      data.options = result.options;
      values = structuredClone(result.options);
      message = t.saved;
      await load(false);
    } catch (err) {
      message = t.failed;
      paintStatus();
    }
  }

  async function load(initial) {
    try {
      const keep = initial ? null : values;
      data = await call({ type: "heads_up/settings_get" });
      values = keep ? { ...structuredClone(data.options), ...keep } : structuredClone(data.options);
      render();
    } catch (err) {
      root.replaceChildren(el("div", { textContent: t.load_failed }));
    }
  }

  load(true);
  return {
    setHass(value) {
      hass = value;
    },
    destroy() {
      root.remove();
    },
  };
}

// The text-to-speech entities of the instance, plus the stored one when it no longer exists.
export function ttsEntities(hass, current) {
  const ids = Object.keys(hass?.states || {}).filter((id) => id.startsWith("tts.")).sort();
  if (current && !ids.includes(current)) ids.push(current);
  return ids;
}
