// Heads Up panel: Watch rules page (D-134, D-242). A table of the rules with their state, like the
// other configuration pages, and an editor in a dialog that saves through the integration's own
// rule flow (D-119).

export const STRINGS = {
  en: {
    title: "Watch rules",
    intro: "A watch rule shows a banner while an entity is in a state, or while a template is true. When that is no longer the case, the banner goes away by itself.",
    none: "You have no watch rules yet.",
    showing: "Showing now",
    not_showing: "Not showing",
    off: "Off",
    new: "New watch rule",
    editing: "Edit watch rule",
    col_rule: "Rule",
    col_watches: "Watches",
    col_shows: "Shows",
    f_who: "Show to",
    who_everyone: "Everyone",
    who_people: "Chosen people",
    who_hint: "An audience is worked out at the moment the banner appears, as for a message.",
    d_when: "When",
    d_who: "Who sees it",
    d_dismiss: "Dismiss",
    turn_off: "Switch off",
    turn_on: "Switch on",
    unsaved_confirm: "You have changes that are not saved. Close anyway?",
    sec_when: "When",
    mode_label: "Editor",
    mode_visual: "Visual editor",
    mode_yaml: "YAML editor",
    yaml_hint: "The rule as YAML, with the same keys as the form. Switching to the Visual editor reads it into the form; Save checks it like the form does. An unquoted on or off as a state is read as the word.",
    yaml_error: "The YAML could not be read: {text}",
    sec_what: "What to show",
    sec_who: "Who sees it",
    sec_how: "Behaviour",
    kind_entity: "An entity is in a state",
    kind_template: "A template is true",
    f_kind: "Type of condition",
    f_entity: "Entity",
    f_operator: "Condition",
    f_state: "Value (several: separate with commas)",
    f_attribute: "Attribute (optional, instead of the state)",
    f_for: "Must hold for, in minutes (optional)",
    f_template: "Template",
    f_message: "Message",
    f_title: "Title (optional)",
    f_severity: "Severity",
    f_icon: "Icon (optional, like mdi:door)",
    f_image: "Image (optional, a URL or a path)",
    f_subtitle: "Subtitle (optional)",
    f_color: "Color (optional, #rrggbb)",
    f_icon_url: "Sender icon (optional, a URL or a path)",
    f_progress: "Progress bar from an entity (optional)",
    f_progress_min: "Bar empty at this value (default 0)",
    f_progress_max: "Bar full at this value (default 100)",
    f_people: "People",
    f_dismissible: "Viewers can dismiss it",
    f_policy: "Policy",
    policy_all: "All that apply (automatic)",
    policy_none: "None",
    policy_missing: "missing",
    policy_hint: "A policy that is not automatic applies only when it is named here. A named policy is the only one used for this rule.",
    f_dismiss_scope: "Dismissing hides it for",
    scope_default: "Default (each user)",
    scope_user: "Each user",
    scope_global: "Everyone",
    f_snoozable: "Viewers can snooze it",
    snooze_default: "Use the integration setting",
    snooze_on: "Yes",
    snooze_off: "No",
    f_snooze_scope: "Snoozing hides it for",
    f_snooze_minutes: "Snooze choices, in minutes",
    f_snooze_custom: "Viewer may choose another duration (at most 24 hours)",
    f_enabled: "Enabled",
    sentence: "Sentence",
    sentence_entity: "Shows “{message}” ({severity}) while {entity} {operator} {value}.",
    sentence_template: "Shows “{message}” ({severity}) while the template is true.",
    sentence_for: " The condition must hold for {n} min first.",
    watches: "watches {entity} {operator} {value}",
    watches_template: "watches a template",
    template_cell: "A template",
    operators: {"equals": "equals", "not_equals": "does not equal", "above": "above", "below": "below", "between": "between", "contains": "contains", "not_contains": "does not contain", "empty": "is empty", "not_empty": "is not empty"},
    severities: {"passive": "Passive", "info": "Info", "warning": "Warning", "critical": "Critical"},
    saved: "Saved.",
    failed: "Could not save. Try again.",
    errors: {"entity_not_found": "This entity does not exist.", "message_required": "Enter a message.", "message_too_long": "The message can have up to 1000 characters.", "message_template_invalid": "The message contains an invalid template.", "title_too_long": "The title can have up to 100 characters.", "state_count": "Above and below need one number, between needs two.", "state_not_numeric": "Enter numbers only for this condition.", "state_required": "Enter at least one value.", "for_too_long": "Use 24 hours or less.", "snoozable_needs_dismissible": "Snoozable needs Dismissible to be on.", "entity_and_template": "Use an entity or a template, not both.", "entity_or_template_required": "Choose an entity or enter a template.", "template_invalid": "The template is not valid.", "actions_invalid": "The buttons are not valid. Each needs a key and a label, up to 3.", "tap_action_invalid": "The tap action needs an action key.", "image_invalid": "The image must be an http(s) URL or a path starting with /.", "color_invalid": "The color must look like #03a9f4.", "progress_invalid": "Progress needs an entity, and max must be greater than min.", "icon_url_invalid": "The sender icon must be an http(s) URL or a path starting with /.", "actions_dismiss_needs_dismissible": "A button with dismiss needs Dismissible to be on.", "policy_unknown": "This policy does not exist. Use the name of a policy, or none.", "name_required": "Enter a name.", "name_exists": "This name is already used."},
  },
  de: {
    title: "Überwachungsregeln",
    intro: "Eine Überwachungsregel zeigt ein Banner, solange eine Entität in einem Zustand ist oder eine Vorlage wahr ist. Trifft das nicht mehr zu, verschwindet das Banner von selbst.",
    none: "Du hast noch keine Überwachungsregeln.",
    showing: "Wird gezeigt",
    not_showing: "Wird nicht gezeigt",
    off: "Aus",
    new: "Neue Überwachungsregel",
    editing: "Überwachungsregel bearbeiten",
    col_rule: "Regel",
    col_watches: "Überwacht",
    col_shows: "Zeigt",
    f_who: "Anzeigen für",
    who_everyone: "Alle",
    who_people: "Ausgewählte Personen",
    who_hint: "Eine Zielgruppe wird in dem Moment bestimmt, in dem das Banner erscheint, wie bei einer Meldung.",
    d_when: "Wann",
    d_who: "Wer sieht es",
    d_dismiss: "Ausblenden",
    turn_off: "Ausschalten",
    turn_on: "Einschalten",
    unsaved_confirm: "Du hast Änderungen, die nicht gespeichert sind. Trotzdem schließen?",
    sec_when: "Wann",
    mode_label: "Editor",
    mode_visual: "Visueller Editor",
    mode_yaml: "YAML-Editor",
    yaml_hint: "Die Regel als YAML mit denselben Schlüsseln wie das Formular. Der Wechsel zum visuellen Editor liest sie ins Formular; Speichern prüft sie wie das Formular. Ein unquotiertes on oder off als Zustand wird als Wort gelesen.",
    yaml_error: "Das YAML konnte nicht gelesen werden: {text}",
    sec_what: "Was gezeigt wird",
    sec_who: "Wer es sieht",
    sec_how: "Verhalten",
    kind_entity: "Eine Entität hat einen Zustand",
    kind_template: "Eine Vorlage ist wahr",
    f_kind: "Art der Bedingung",
    f_entity: "Entität",
    f_operator: "Bedingung",
    f_state: "Wert (mehrere: mit Kommas trennen)",
    f_attribute: "Attribut (optional, statt des Zustands)",
    f_for: "Muss gelten für, in Minuten (optional)",
    f_template: "Vorlage",
    f_message: "Meldung",
    f_title: "Titel (optional)",
    f_severity: "Schweregrad",
    f_icon: "Symbol (optional, etwa mdi:door)",
    f_image: "Bild (optional, eine URL oder ein Pfad)",
    f_subtitle: "Untertitel (optional)",
    f_color: "Farbe (optional, #rrggbb)",
    f_icon_url: "Absender-Symbol (optional, eine URL oder ein Pfad)",
    f_progress: "Fortschrittsbalken aus einer Entität (optional)",
    f_progress_min: "Balken leer bei diesem Wert (Standard 0)",
    f_progress_max: "Balken voll bei diesem Wert (Standard 100)",
    f_people: "Personen",
    f_dismissible: "Betrachter können es ausblenden",
    f_policy: "Richtlinie",
    policy_all: "Alle, die gelten (automatisch)",
    policy_none: "Keine",
    policy_missing: "fehlt",
    policy_hint: "Eine Richtlinie, die nicht automatisch gilt, wirkt nur, wenn sie hier genannt ist. Eine genannte Richtlinie ist die einzige für diese Regel.",
    f_dismiss_scope: "Ausblenden gilt für",
    scope_default: "Standard (jeder Benutzer)",
    scope_user: "Jeder Benutzer",
    scope_global: "Alle",
    f_snoozable: "Betrachter können es zurückstellen",
    snooze_default: "Einstellung der Integration verwenden",
    snooze_on: "Ja",
    snooze_off: "Nein",
    f_snooze_scope: "Zurückstellen gilt für",
    f_snooze_minutes: "Auswahl zum Zurückstellen, in Minuten",
    f_snooze_custom: "Betrachter darf eine andere Dauer wählen (höchstens 24 Stunden)",
    f_enabled: "Aktiv",
    sentence: "Satz",
    sentence_entity: "Zeigt „{message}“ ({severity}), solange {entity} {operator} {value}.",
    sentence_template: "Zeigt „{message}“ ({severity}), solange die Vorlage wahr ist.",
    sentence_for: " Die Bedingung muss zuerst {n} Min. gelten.",
    watches: "überwacht {entity} {operator} {value}",
    watches_template: "überwacht eine Vorlage",
    template_cell: "Eine Vorlage",
    operators: {"equals": "ist gleich", "not_equals": "ist ungleich", "above": "über", "below": "unter", "between": "zwischen", "contains": "enthält", "not_contains": "enthält nicht", "empty": "ist leer", "not_empty": "ist nicht leer"},
    severities: {"passive": "Passiv", "info": "Info", "warning": "Warnung", "critical": "Kritisch"},
    saved: "Gespeichert.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    errors: {"entity_not_found": "Diese Entität existiert nicht.", "message_required": "Gib eine Nachricht ein.", "message_too_long": "Die Nachricht darf bis zu 1000 Zeichen haben.", "message_template_invalid": "Die Nachricht enthält eine ungültige Vorlage.", "title_too_long": "Der Titel darf bis zu 100 Zeichen haben.", "state_count": "„Über“ und „Unter“ brauchen eine Zahl, „Zwischen“ braucht zwei.", "state_not_numeric": "Gib für diese Bedingung nur Zahlen ein.", "state_required": "Gib mindestens einen Wert ein.", "for_too_long": "Verwende 24 Stunden oder weniger.", "snoozable_needs_dismissible": "„Zurückstellbar“ benötigt, dass „Schließbar“ an ist.", "entity_and_template": "Verwende eine Entität oder eine Vorlage, nicht beides.", "entity_or_template_required": "Wähle eine Entität oder gib eine Vorlage ein.", "template_invalid": "Die Vorlage ist ungültig.", "actions_invalid": "Die Schaltflächen sind ungültig. Jede braucht key und label, höchstens 3.", "tap_action_invalid": "Die Tipp-Aktion braucht einen action-Schlüssel.", "image_invalid": "Das Bild muss eine http(s)-URL oder ein Pfad sein, der mit / beginnt.", "color_invalid": "Die Farbe muss so aussehen: #03a9f4.", "progress_invalid": "Der Fortschritt braucht eine Entität, und max muss größer als min sein.", "icon_url_invalid": "Das Absender-Symbol muss eine http(s)-URL oder ein Pfad sein, der mit / beginnt.", "actions_dismiss_needs_dismissible": "Eine Schaltfläche mit dismiss braucht „Schließbar“ an.", "policy_unknown": "Diese Richtlinie gibt es nicht. Nimm den Namen einer Richtlinie oder none.", "name_required": "Gib einen Namen ein.", "name_exists": "Dieser Name wird schon verwendet."},
  },
  fr: {
    title: "Règles de surveillance",
    intro: "Une règle de surveillance affiche une bannière tant qu'une entité est dans un état, ou tant qu'un modèle est vrai. Quand ce n'est plus le cas, la bannière disparaît d'elle-même.",
    none: "Vous n'avez pas encore de règle de surveillance.",
    showing: "Affichée",
    not_showing: "Non affichée",
    off: "Désactivée",
    new: "Nouvelle règle de surveillance",
    editing: "Modifier la règle de surveillance",
    col_rule: "Règle",
    col_watches: "Surveille",
    col_shows: "Affiche",
    f_who: "Afficher pour",
    who_everyone: "Tout le monde",
    who_people: "Personnes choisies",
    who_hint: "Une audience est déterminée au moment où la bannière apparaît, comme pour un message.",
    d_when: "Quand",
    d_who: "Qui la voit",
    d_dismiss: "Masquer",
    turn_off: "Désactiver",
    turn_on: "Activer",
    unsaved_confirm: "Certaines modifications ne sont pas enregistrées. Fermer quand même ?",
    sec_when: "Quand",
    mode_label: "Éditeur",
    mode_visual: "Éditeur visuel",
    mode_yaml: "Éditeur YAML",
    yaml_hint: "La règle en YAML, avec les mêmes clés que le formulaire. Passer à l'éditeur visuel la lit dans le formulaire ; Enregistrer la vérifie comme le formulaire. Un on ou off sans guillemets comme état est lu comme le mot.",
    yaml_error: "Le YAML n'a pas pu être lu : {text}",
    sec_what: "Quoi afficher",
    sec_who: "Qui la voit",
    sec_how: "Comportement",
    kind_entity: "Une entité est dans un état",
    kind_template: "Un modèle est vrai",
    f_kind: "Type de condition",
    f_entity: "Entité",
    f_operator: "Condition",
    f_state: "Valeur (plusieurs : séparez par des virgules)",
    f_attribute: "Attribut (facultatif, à la place de l'état)",
    f_for: "Doit durer, en minutes (facultatif)",
    f_template: "Modèle",
    f_message: "Message",
    f_title: "Titre (facultatif)",
    f_severity: "Gravité",
    f_icon: "Icône (facultatif, comme mdi:door)",
    f_image: "Image (facultatif, une URL ou un chemin)",
    f_subtitle: "Sous-titre (facultatif)",
    f_color: "Couleur (facultatif, #rrggbb)",
    f_icon_url: "Icône de l'expéditeur (facultatif, une URL ou un chemin)",
    f_progress: "Barre de progression d'une entité (facultatif)",
    f_progress_min: "Barre vide à cette valeur (0 par défaut)",
    f_progress_max: "Barre pleine à cette valeur (100 par défaut)",
    f_people: "Personnes",
    f_dismissible: "Les spectateurs peuvent la masquer",
    f_policy: "Politique",
    policy_all: "Toutes celles qui s'appliquent (automatiques)",
    policy_none: "Aucune",
    policy_missing: "manquante",
    policy_hint: "Une politique non automatique ne s'applique que si elle est nommée ici. Une politique nommée est la seule utilisée pour cette règle.",
    f_dismiss_scope: "Masquer vaut pour",
    scope_default: "Par défaut (chaque utilisateur)",
    scope_user: "Chaque utilisateur",
    scope_global: "Tout le monde",
    f_snoozable: "Les spectateurs peuvent la reporter",
    snooze_default: "Utiliser le réglage de l'intégration",
    snooze_on: "Oui",
    snooze_off: "Non",
    f_snooze_scope: "Reporter vaut pour",
    f_snooze_minutes: "Durées de report, en minutes",
    f_snooze_custom: "Le spectateur peut choisir une autre durée (24 heures au plus)",
    f_enabled: "Activée",
    sentence: "Phrase",
    sentence_entity: "Affiche « {message} » ({severity}) tant que {entity} {operator} {value}.",
    sentence_template: "Affiche « {message} » ({severity}) tant que le modèle est vrai.",
    sentence_for: " La condition doit d'abord durer {n} min.",
    watches: "surveille {entity} {operator} {value}",
    watches_template: "surveille un modèle",
    template_cell: "Un modèle",
    operators: {"equals": "est égal à", "not_equals": "est différent de", "above": "au-dessus de", "below": "en dessous de", "between": "entre", "contains": "contient", "not_contains": "ne contient pas", "empty": "est vide", "not_empty": "n'est pas vide"},
    severities: {"passive": "Passif", "info": "Info", "warning": "Avertissement", "critical": "Critique"},
    saved: "Enregistré.",
    failed: "Échec de l'enregistrement. Réessayez.",
    errors: {"entity_not_found": "Cette entité n'existe pas.", "message_required": "Saisissez un message.", "message_too_long": "Le message peut contenir jusqu'à 1000 caractères.", "message_template_invalid": "Le message contient un modèle non valide.", "title_too_long": "Le titre peut contenir jusqu'à 100 caractères.", "state_count": "« Supérieur » et « Inférieur » demandent un nombre, « Entre » en demande deux.", "state_not_numeric": "Saisissez uniquement des nombres pour cette condition.", "state_required": "Saisissez au moins une valeur.", "for_too_long": "Utilisez 24 heures ou moins.", "snoozable_needs_dismissible": "« Reportable » nécessite que « Fermable » soit activé.", "entity_and_template": "Utilisez une entité ou un modèle, pas les deux.", "entity_or_template_required": "Choisissez une entité ou saisissez un modèle.", "template_invalid": "Le modèle n'est pas valide.", "actions_invalid": "Les boutons ne sont pas valides. Chacun a besoin d'une key et d'un label, 3 au maximum.", "tap_action_invalid": "L'action au toucher a besoin d'une clé action.", "image_invalid": "L'image doit être une URL http(s) ou un chemin commençant par /.", "color_invalid": "La couleur doit ressembler à #03a9f4.", "progress_invalid": "La progression demande une entité, et max doit être supérieur à min.", "icon_url_invalid": "L'icône de l'expéditeur doit être une URL http(s) ou un chemin commençant par /.", "actions_dismiss_needs_dismissible": "Un bouton avec dismiss nécessite que « Fermable » soit activé.", "policy_unknown": "Cette politique n'existe pas. Utilisez le nom d'une politique, ou none.", "name_required": "Saisissez un nom.", "name_exists": "Ce nom est déjà utilisé."},
  },
  es: {
    title: "Reglas de vigilancia",
    intro: "Una regla de vigilancia muestra un aviso mientras una entidad está en un estado, o mientras una plantilla es verdadera. Cuando deja de serlo, el aviso desaparece solo.",
    none: "Aún no tienes reglas de vigilancia.",
    showing: "Mostrándose",
    not_showing: "No se muestra",
    off: "Desactivada",
    new: "Nueva regla de vigilancia",
    editing: "Editar regla de vigilancia",
    col_rule: "Regla",
    col_watches: "Vigila",
    col_shows: "Muestra",
    f_who: "Mostrar a",
    who_everyone: "Todos",
    who_people: "Personas elegidas",
    who_hint: "Una audiencia se calcula en el momento en que aparece el aviso, como para un mensaje.",
    d_when: "Cuándo",
    d_who: "Quién lo ve",
    d_dismiss: "Descartar",
    turn_off: "Desactivar",
    turn_on: "Activar",
    unsaved_confirm: "Hay cambios sin guardar. ¿Cerrar de todos modos?",
    sec_when: "Cuándo",
    mode_label: "Editor",
    mode_visual: "Editor visual",
    mode_yaml: "Editor YAML",
    yaml_hint: "La regla en YAML, con las mismas claves que el formulario. Pasar al editor visual la lee en el formulario; Guardar la comprueba como el formulario. Un on u off sin comillas como estado se lee como la palabra.",
    yaml_error: "No se pudo leer el YAML: {text}",
    sec_what: "Qué mostrar",
    sec_who: "Quién lo ve",
    sec_how: "Comportamiento",
    kind_entity: "Una entidad está en un estado",
    kind_template: "Una plantilla es verdadera",
    f_kind: "Tipo de condición",
    f_entity: "Entidad",
    f_operator: "Condición",
    f_state: "Valor (varios: sepáralos con comas)",
    f_attribute: "Atributo (opcional, en lugar del estado)",
    f_for: "Debe cumplirse durante, en minutos (opcional)",
    f_template: "Plantilla",
    f_message: "Mensaje",
    f_title: "Título (opcional)",
    f_severity: "Gravedad",
    f_icon: "Icono (opcional, como mdi:door)",
    f_image: "Imagen (opcional, una URL o una ruta)",
    f_subtitle: "Subtítulo (opcional)",
    f_color: "Color (opcional, #rrggbb)",
    f_icon_url: "Icono del remitente (opcional, una URL o una ruta)",
    f_progress: "Barra de progreso de una entidad (opcional)",
    f_progress_min: "Barra vacía con este valor (0 por defecto)",
    f_progress_max: "Barra llena con este valor (100 por defecto)",
    f_people: "Personas",
    f_dismissible: "Quien lo ve puede descartarlo",
    f_policy: "Política",
    policy_all: "Todas las que se aplican (automáticas)",
    policy_none: "Ninguna",
    policy_missing: "falta",
    policy_hint: "Una política que no es automática solo se aplica si se nombra aquí. Una política nombrada es la única que se usa para esta regla.",
    f_dismiss_scope: "Descartar vale para",
    scope_default: "Por defecto (cada usuario)",
    scope_user: "Cada usuario",
    scope_global: "Todos",
    f_snoozable: "Quien lo ve puede posponerlo",
    snooze_default: "Usar el ajuste de la integración",
    snooze_on: "Sí",
    snooze_off: "No",
    f_snooze_scope: "Posponer vale para",
    f_snooze_minutes: "Opciones de pospuesta, en minutos",
    f_snooze_custom: "El espectador puede elegir otra duración (como máximo 24 horas)",
    f_enabled: "Activada",
    sentence: "Frase",
    sentence_entity: "Muestra «{message}» ({severity}) mientras {entity} {operator} {value}.",
    sentence_template: "Muestra «{message}» ({severity}) mientras la plantilla sea verdadera.",
    sentence_for: " La condición debe cumplirse antes durante {n} min.",
    watches: "vigila {entity} {operator} {value}",
    watches_template: "vigila una plantilla",
    template_cell: "Una plantilla",
    operators: {"equals": "es igual a", "not_equals": "es distinto de", "above": "por encima de", "below": "por debajo de", "between": "entre", "contains": "contiene", "not_contains": "no contiene", "empty": "está vacío", "not_empty": "no está vacío"},
    severities: {"passive": "Pasivo", "info": "Info", "warning": "Aviso", "critical": "Crítico"},
    saved: "Guardado.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    errors: {"entity_not_found": "Esta entidad no existe.", "message_required": "Introduce un mensaje.", "message_too_long": "El mensaje puede tener hasta 1000 caracteres.", "message_template_invalid": "El mensaje contiene una plantilla no válida.", "title_too_long": "El título puede tener hasta 100 caracteres.", "state_count": "«Por encima» y «Por debajo» necesitan un número, «Entre» necesita dos.", "state_not_numeric": "Introduce solo números para esta condición.", "state_required": "Introduce al menos un valor.", "for_too_long": "Usa 24 horas o menos.", "snoozable_needs_dismissible": "«Se puede posponer» requiere que «Se puede cerrar» esté activado.", "entity_and_template": "Usa una entidad o una plantilla, no ambas.", "entity_or_template_required": "Elige una entidad o introduce una plantilla.", "template_invalid": "La plantilla no es válida.", "actions_invalid": "Los botones no son válidos. Cada uno necesita key y label, como máximo 3.", "tap_action_invalid": "La acción al tocar necesita una clave action.", "image_invalid": "La imagen debe ser una URL http(s) o una ruta que empieza por /.", "color_invalid": "El color debe tener este aspecto: #03a9f4.", "progress_invalid": "El progreso necesita una entidad, y max debe ser mayor que min.", "icon_url_invalid": "El icono del remitente debe ser una URL http(s) o una ruta que empieza por /.", "actions_dismiss_needs_dismissible": "Un botón con dismiss requiere que «Se puede cerrar» esté activado.", "policy_unknown": "Esta política no existe. Usa el nombre de una política, o none.", "name_required": "Introduce un nombre.", "name_exists": "Este nombre ya se usa."},
  },
};

export const OPERATORS = ["equals", "not_equals", "above", "below", "between", "contains", "not_contains", "empty", "not_empty"];
const SEVERITIES = ["passive", "info", "warning", "critical"];
const SNOOZE_MINUTES = [5, 15, 30, 60, 120, 240, 480, 1440];
const NO_VALUE = ["empty", "not_empty"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues() {
  return {
    name: "", kind: "entity", entity_id: "", operator: "equals", state: "", attribute: "", for_minutes: "", template: "",
    message: "", title: "", severity: "warning", icon: "", image: "", color: "", icon_url: "", subtitle: "", progress_entity: "", progress_min: "", progress_max: "", actions: [], tap_action: null, tap_problem: "", who: "everyone", audience: "", people: [],
    dismissible: false, dismiss_scope: "", snoozable: "", snooze_scope: "", snooze_minutes: [], snooze_custom: false, policy: "", enabled: true,
  };
}

const text = (value) => (value === undefined || value === null ? "" : String(value));

// The form values of a stored rule { name, data }. Buttons and the tap action are not edited here.
export function fromRule(rule) {
  const d = rule.data || {};
  return {
    ...blankValues(),
    name: rule.name,
    kind: d.template ? "template" : "entity",
    entity_id: text(d.entity_id),
    operator: d.operator || "equals",
    state: (d.state || []).join(", "),
    attribute: text(d.attribute),
    for_minutes: d.for ? String(Math.round(d.for / 60)) : "",
    template: text(d.template),
    message: text(d.message),
    title: text(d.title),
    severity: d.severity || "warning",
    icon: text(d.icon),
    image: text(d.image),
    color: text(d.color),
    icon_url: text(d.icon_url),
    subtitle: text(d.subtitle),
    progress_entity: text(d.progress?.entity_id),
    progress_min: text(d.progress?.min),
    progress_max: text(d.progress?.max),
    actions: (d.actions || []).map((a) => ({ ...a })),
    tap_action: d.tap_action ? { ...d.tap_action } : null,
    who: d.audience ? "audience" : (d.people || []).length ? "people" : "everyone",
    audience: text(d.audience),
    people: [...(d.people || [])],
    dismissible: Boolean(d.dismissible),
    dismiss_scope: text(d.dismiss_scope),
    snoozable: d.snoozable === undefined ? "" : d.snoozable ? "on" : "off",
    snooze_scope: text(d.snooze_scope),
    snooze_minutes: (d.snooze_options || []).map((s) => String(Math.round(s / 60))),
    snooze_custom: Boolean(d.snooze_custom),
    policy: text(d.policy),
    enabled: d.enabled !== false,
  };
}

export function splitValues(value) {
  return String(value || "").split(",").map((v) => v.trim()).filter(Boolean);
}

// The input of the rule flow: only what is set. `own` is the stored rule being edited, whose
// buttons and tap action are passed through unchanged.
export function toFlowData(values, own) {
  const data = {
    name: values.name.trim(),
    message: values.message.trim(),
    severity: values.severity,
    people: values.who === "people" ? [...values.people] : [],
    dismissible: Boolean(values.dismissible),
    enabled: Boolean(values.enabled),
  };
  if (values.kind === "template") {
    data.template = values.template.trim();
  } else {
    data.entity_id = values.entity_id.trim();
    data.operator = values.operator;
    if (!NO_VALUE.includes(values.operator)) data.state = splitValues(values.state);
    if (values.attribute.trim()) data.attribute = values.attribute.trim();
  }
  const minutes = Number(values.for_minutes);
  if (values.for_minutes !== "" && minutes > 0) data.for = { hours: Math.floor(minutes / 60), minutes: Math.floor(minutes % 60), seconds: Math.round((minutes % 1) * 60) };
  for (const key of ["title", "icon", "image", "color", "icon_url", "subtitle"]) if (values[key].trim()) data[key] = values[key].trim();
  if (values.progress_entity.trim()) {
    data.progress = { entity_id: values.progress_entity.trim() };
    for (const key of ["min", "max"]) if (values[`progress_${key}`].trim() !== "" && !Number.isNaN(Number(values[`progress_${key}`]))) data.progress[key] = Number(values[`progress_${key}`]);
  }
  if (values.dismiss_scope) data.dismiss_scope = values.dismiss_scope;
  if (values.snoozable) data.snoozable = values.snoozable === "on";
  if (values.snooze_scope) data.snooze_scope = values.snooze_scope;
  if (values.snooze_minutes.length) data.snooze_options = [...values.snooze_minutes];
  if (values.snooze_custom) data.snooze_custom = true;
  if (values.policy) data.policy = values.policy;
  if (values.who === "audience" && values.audience) data.audience = values.audience;
  const buttons = values.actions.filter((b) => String(b.label || "").trim());
  if (buttons.length) {
    data.actions = buttons.map((b) => {
      const out = { key: b.key, label: String(b.label).trim() };
      for (const flag of ["dismiss", "destructive", "require_auth"]) if (b[flag]) out[flag] = true;
      if (b.action) out.action = b.action;
      return out;
    });
  }
  if (values.tap_action) data.tap_action = values.tap_action;
  return data;
}

// The rule as it is stored and as the YAML editor shows it: `for` in seconds and the snooze
// choices in seconds (the flow takes a duration and minutes). fromRule reads it back.
export function storedShape(values) {
  const data = toFlowData(values);
  if (data.for) data.for = data.for.hours * 3600 + data.for.minutes * 60 + data.for.seconds;
  if (data.snooze_options) data.snooze_options = data.snooze_options.map((m) => Math.round(Number(m) * 60));
  return data;
}

// What can be checked before saving, as { field: code }. The flow checks the rest.
export function validate(values, existingNames, ownName) {
  const problems = {};
  const name = values.name.trim();
  if (!name) problems.name = "name_required";
  else if (existingNames.some((n) => n.toLowerCase() === name.toLowerCase() && n !== ownName)) problems.name = "name_exists";
  if (!values.message.trim()) problems.message = "message_required";
  if (values.kind === "template") {
    if (!values.template.trim()) problems.template = "entity_or_template_required";
  } else if (!values.entity_id.trim()) {
    problems.entity_id = "entity_or_template_required";
  }
  return problems;
}

export function valueText(data, t) {
  const states = (data.state || []).join(", ");
  return NO_VALUE.includes(data.operator || "equals") ? "" : states || "on";
}

// "watches light.x equals on" for the list.
export function watchesText(data, t) {
  if (data.template) return t.watches_template;
  return fill(t.watches, { entity: data.entity_id || "", operator: t.operators[data.operator || "equals"], value: valueText(data, t) }).replace(/\s+$/, "");
}

// "light.x equals on" for the Watches column, whose title already says "watches".
export function conditionText(data, t) {
  if (data.template) return t.template_cell;
  return `${data.entity_id || ""} ${t.operators[data.operator || "equals"]} ${valueText(data, t)}`.trim();
}

export function sentence(values, t) {
  const severity = t.severities[values.severity] || values.severity;
  const forText = Number(values.for_minutes) > 0 ? fill(t.sentence_for, { n: values.for_minutes }) : "";
  if (values.kind === "template") return fill(t.sentence_template, { message: values.message, severity }) + forText;
  const value = NO_VALUE.includes(values.operator) ? "" : splitValues(values.state).join(", ") || "on";
  return fill(t.sentence_entity, { message: values.message, severity, entity: values.entity_id || "…", operator: t.operators[values.operator], value }).replace(" .", ".") + forText;
}

const CSS = `
.hu-page .pol-intro { max-width: 72ch; margin-bottom: 12px; }
.hu-page .pol-bar { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 16px; }
.hu-page .pol-bar button, .hu-page .tl-actions button { display: inline-flex; align-items: center; gap: 8px; }
.hu-page .pol-bar ha-icon { --mdc-icon-size: 20px; }
.hu-page section.tl-list { padding: 0; overflow: hidden; --tl-cols: minmax(0, 1.2fr) minmax(0, 1.2fr) minmax(0, 1.4fr); }
.hu-page .tl-list .tl-cell { white-space: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.35; }
.hu-page .tl-cell .badge { white-space: nowrap; margin-right: 4px; }
.hu-page .tl-lead ha-icon { color: var(--secondary-text-color); }
.hu-page .tl-item.showing .tl-lead ha-icon { color: var(--warning-color, #ffa600); }
.hu-page .badge.on { border-color: var(--warning-color, #ffa600); color: var(--warning-color, #ffa600); }
.hu-page dialog.hu-modal { width: min(920px, calc(100vw - 32px)); max-height: calc(100dvh - 48px); padding: 0; border: 1px solid var(--divider-color); border-radius: 16px; background: var(--card-background-color); color: var(--primary-text-color); box-shadow: 0 12px 40px rgba(0, 0, 0, .35); overflow: hidden; }
.hu-page dialog.hu-modal[open] { display: flex; flex-direction: column; }
.hu-page dialog.hu-modal::backdrop { background: rgba(0, 0, 0, .55); }
.hu-page .hu-modal-head { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-bottom: 1px solid var(--divider-color); }
.hu-page .hu-modal-head h2 { margin: 0; }
.hu-page .hu-modal-head .lane-icon { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 10px; background: var(--hu-fill); --mdc-icon-size: 20px; }
.hu-page .hu-close { margin-left: auto; flex: none; width: 44px; height: 44px; padding: 0; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; }
.hu-page .hu-modal-body { overflow: auto; padding: 8px 20px 4px; }
.hu-page .hu-modal-body h3.sec { font-size: 15px; margin: 20px 0 6px; padding-top: 12px; border-top: 1px solid var(--divider-color); }
.hu-page .hu-modal-body h3.sec:first-of-type { border-top: 0; padding-top: 0; margin-top: 8px; }
.hu-page .hu-modal-body .row { position: sticky; bottom: -4px; background: var(--card-background-color); padding: 10px 0; z-index: 1; }
.hu-page .hu-modal-body textarea { width: 100%; max-width: 100%; box-sizing: border-box; }
.hu-page .summary { background: var(--hu-fill); border-radius: 10px; padding: 10px 12px; margin: 16px 0 12px; }
@media (max-width: 600px) {
  .hu-page dialog.hu-modal { width: 100vw; max-width: 100vw; height: 100dvh; max-height: 100dvh; border-radius: 0; border: 0; }
}
`;

const RULE_ICON = "mdi:eye-check-outline";

export function mount(container, ctx) {
  const { t, ui } = ctx;
  const s = ctx.s;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own, values, start }
  let editorDialog = null;
  let openKey = null;
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const personName = (id) => data.choices.persons.find((p) => p.id === id)?.name ?? id;
  const audienceName = (id) => (data.choices.audience_choices || []).find((a) => a.id === id)?.name ?? id;
  const policyName = (id) => (data.policies || []).find((p) => p.subentry_id === id)?.name ?? id;
  const errorTexts = (codes) => codes.map((c) => s.buttons.problems[c] || t.errors[c] || ui.errorText(c, ctx.language)).join(" ");
  const whoText = (d) => (d.audience ? audienceName(d.audience) : (d.people || []).length ? d.people.map(personName).join(", ") : t.who_everyone);

  // The rules as a table like the other pages: name and state, what it watches, what it shows.
  function table() {
    const box = el("section", { className: "tl-list" });
    if (data.rules.length) box.append(ui.tableHead([t.col_rule, t.col_watches, t.col_shows]));
    for (const rule of data.rules) box.append(ruleRow(rule));
    if (!data.rules.length) box.append(el("div", { className: "tl-empty", textContent: t.none }));
    return box;
  }

  function ruleRow(rule) {
    const d = rule.data;
    const enabled = d.enabled !== false;
    const id = `hu-rule-${rule.subentry_id}`;
    const isOpen = openKey === rule.subentry_id;
    const state = !enabled ? t.off : rule.showing ? t.showing : t.not_showing;
    const lead = [
      el("ha-icon", { icon: RULE_ICON }),
      el("span", { className: "tl-name", textContent: rule.name }),
    ];
    const shows = `${t.severities[d.severity || "warning"]} · ${d.message || ""}`;
    const { item } = ui.tableRow({
      id,
      lead,
      cells: [
        { label: t.col_watches, node: el("span", { textContent: conditionText(d, t) }) },
        { label: t.col_shows, node: el("span", {}, [el("span", { className: `badge${enabled && rule.showing ? " on" : ""}`, textContent: state }), document.createTextNode(` ${shows}`)]) },
      ],
      open: isOpen,
      dim: !enabled,
      label: `${rule.name}, ${state}: ${watchesText(d, t)}. ${shows}`,
      onToggle: () => {
        openKey = isOpen ? null : rule.subentry_id;
        render();
        root.querySelector(`[aria-controls="${id}"]`)?.focus();
      },
      body: isOpen ? details(rule) : null,
    });
    if (enabled && rule.showing) item.classList.add("showing");
    return item;
  }

  function details(rule) {
    const d = rule.data;
    const body = el("div", {});
    const shown = /\{[{%]/.test(d.message || "") ? el("code", { className: "tpl", textContent: d.message }) : d.message || "";
    const policy = !d.policy ? t.policy_all : d.policy === "none" ? t.policy_none : policyName(d.policy);
    body.append(
      ui.facts([
        [t.d_when, (d.template ? d.template : conditionText(d, t)) + (d.for ? fill(t.sentence_for, { n: Math.round(d.for / 60) }) : "")],
        [t.f_message, shown],
        [t.d_who, whoText(d)],
        [t.f_policy, policy],
        [t.d_dismiss, d.dismissible ? (d.dismiss_scope === "global" ? t.scope_global : t.scope_user) : t.snooze_off],
      ]),
    );
    const edit = el("button", { type: "button", className: "primary", textContent: s.common.edit });
    edit.addEventListener("click", () => openEditor(rule, fromRule(rule)));
    const enabled = d.enabled !== false;
    const flip = el("button", { type: "button", textContent: enabled ? t.turn_off : t.turn_on });
    flip.addEventListener("click", async () => {
      const result = await ui.runFlow(hass, data.entry_id, "rule", rule.subentry_id, toFlowData({ ...fromRule(rule), enabled: !enabled }, rule));
      message = result.ok ? "" : errorTexts(Object.values(result.errors));
      await load();
    });
    body.append(el("div", { className: "tl-actions" }, [edit, flip]));
    return body;
  }

  // A dialog over the page; X, Cancel, Escape and a click beside it ask first when something changed.
  function openEditor(own, values) {
    message = "";
    editing = { own, values, start: JSON.stringify(toFlowData(values, own)), mode: "visual", yaml: "", yamlStart: "" };
    const dialog = el("dialog", { className: "hu-modal" });
    const close = el("button", { type: "button", className: "hu-close" }, [el("ha-icon", { icon: "mdi:close" })]);
    close.setAttribute("aria-label", s.common.cancel);
    close.addEventListener("click", requestClose);
    const head = el("div", { className: "hu-modal-head" }, [
      el("span", { className: "lane-icon" }, [el("ha-icon", { icon: own ? RULE_ICON : "mdi:plus" })]),
      el("h2", { textContent: own ? `${t.editing}: ${own.name}` : t.new }),
      close,
    ]);
    const body = el("div", { className: "hu-modal-body" });
    dialog.append(head, body);
    dialog.addEventListener("cancel", (event) => { event.preventDefault(); requestClose(); });
    dialog.addEventListener("click", (event) => { if (event.target === dialog) requestClose(); });
    dialog.addEventListener("close", () => { dialog.remove(); editing = null; editorDialog = null; });
    root.append(dialog);
    editorDialog = { dialog, body };
    body.append(editor());
    dialog.showModal();
  }

  function refreshEditor() {
    if (!editorDialog) return;
    const scroll = editorDialog.body.scrollTop;
    editorDialog.body.replaceChildren(editor());
    editorDialog.body.scrollTop = scroll;
  }

  function requestClose() {
    if (!editorDialog) return;
    const changed = editing && (JSON.stringify(toFlowData(editing.values, editing.own)) !== editing.start || (editing.mode === "yaml" && editing.yaml !== editing.yamlStart));
    if (changed && !window.confirm(t.unsaved_confirm)) return;
    editorDialog.dialog.close();
  }

  // Visual editor or YAML editor of the same rule, as on Test send (D-260).
  function modeSwitch() {
    const seg = el("div", { className: "seg", role: "group" });
    seg.setAttribute("aria-label", t.mode_label);
    for (const [key, label] of [["visual", t.mode_visual], ["yaml", t.mode_yaml]]) {
      const button = el("button", { type: "button", textContent: label });
      button.setAttribute("aria-pressed", String(editing.mode === key));
      button.addEventListener("click", () => switchMode(key));
      seg.append(button);
    }
    return el("div", { style: "display:flex;justify-content:flex-end;margin-bottom:12px" }, [seg]);
  }

  async function parseYaml(yamlText) {
    const reply = await hass.callWS({ type: "heads_up/rule_parse_yaml", yaml: yamlText });
    const { name, ...rest } = reply.rule;
    return fromRule({ name: String(name ?? ""), data: rest });
  }

  async function switchMode(next) {
    if (next === editing.mode) return;
    if (next === "yaml") {
      editing.yaml = ui.toYaml(storedShape(editing.values));
      editing.yamlStart = editing.yaml;
      editing.mode = "yaml";
      message = "";
      refreshEditor();
      return;
    }
    try {
      Object.assign(editing.values, await parseYaml(editing.yaml));
      editing.mode = "visual";
      message = "";
    } catch (err) {
      message = fill(t.yaml_error, { text: err?.message || String(err?.code || "error") });
    }
    refreshEditor();
  }

  function yamlEditor(box) {
    const { own } = editing;
    box.append(el("div", { className: "hint", textContent: t.yaml_hint }));
    const area = el("textarea", { rows: 22, value: editing.yaml, spellcheck: false, style: "width:100%;box-sizing:border-box;font-family:monospace" });
    area.addEventListener("input", () => { editing.yaml = area.value; });
    box.append(ui.field(s.common.yaml, area));
    const status = el("div", { className: message ? "hint problems" : "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.textContent = message;
    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", saveYaml);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", requestClose);
    const buttons = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete });
      del.addEventListener("click", remove);
      buttons.append(del);
    }
    box.append(status, buttons);
    return box;
  }

  async function saveYaml() {
    try {
      Object.assign(editing.values, await parseYaml(editing.yaml));
    } catch (err) {
      message = fill(t.yaml_error, { text: err?.message || String(err?.code || "error") });
      refreshEditor();
      return;
    }
    await saveIt();
  }

  function editor() {
    const { own, values } = editing;
    const existing = data.rules.map((r) => r.name);
    const box = el("div", {});
    const again = () => refreshEditor();
    const text = (key, label, extra = {}) => ui.field(label, ui.textInput(values[key], (v) => { values[key] = v; paint(); }, extra));
    box.append(modeSwitch());
    if (editing.mode === "yaml") return yamlEditor(box);
    box.append(ui.checkbox(t.f_enabled, values.enabled, (on) => { values.enabled = on; paint(); }));
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; paint(); })));

    box.append(el("h3", { className: "sec", textContent: t.sec_when }));
    box.append(ui.field(t.f_kind, ui.selectInput([{ value: "entity", label: t.kind_entity }, { value: "template", label: t.kind_template }], values.kind, (v) => { values.kind = v; again(); })));
    if (values.kind === "template") {
      const area = el("textarea", { value: values.template, rows: 3 });
      area.addEventListener("input", () => { values.template = area.value; paint(); });
      box.append(ui.field(t.f_template, area));
    } else {
      const input = ui.textInput(values.entity_id, (v) => { values.entity_id = v; paint(); }, { style: "max-width:100%" });
      input.setAttribute("list", "hu-entities");
      const list = el("datalist", { id: "hu-entities" }, Object.keys(hass.states || {}).sort().map((id) => el("option", { value: id })));
      box.append(ui.field(t.f_entity, input), list);
      box.append(ui.field(t.f_operator, ui.selectInput(OPERATORS.map((o) => ({ value: o, label: t.operators[o] })), values.operator, (v) => { values.operator = v; again(); })));
      if (!NO_VALUE.includes(values.operator)) box.append(text("state", t.f_state));
      box.append(text("attribute", t.f_attribute));
    }
    box.append(ui.field(t.f_for, ui.numberInput(values.for_minutes, (v) => { values.for_minutes = Number.isNaN(v) ? "" : String(v); paint(); }, { min: 0, max: 1440, step: "any" })));

    box.append(el("h3", { className: "sec", textContent: t.sec_what }));
    const msg = el("textarea", { value: values.message, rows: 3 });
    msg.addEventListener("input", () => { values.message = msg.value; paint(); });
    box.append(ui.field(t.f_message, msg), text("title", t.f_title));
    box.append(ui.field(t.f_severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: t.severities[k] })), values.severity, (v) => { values.severity = v; paint(); })));
    box.append(text("icon", t.f_icon), text("image", t.f_image, { style: "max-width:100%" }));
    box.append(text("subtitle", t.f_subtitle), ui.field(t.f_color, ui.colorInput(values.color, (v) => { values.color = v; paint(); }, { placeholder: "#03a9f4", "aria-label": t.f_color })), text("icon_url", t.f_icon_url, { style: "max-width:100%" }));
    const bar = text("progress_entity", t.f_progress, { style: "max-width:100%" });
    bar.querySelector("input")?.setAttribute("list", "hu-entities");
    box.append(bar);
    box.append(text("progress_min", t.f_progress_min, { placeholder: "0" }), text("progress_max", t.f_progress_max, { placeholder: "100" }));

    box.append(el("h3", { className: "sec", textContent: t.sec_who }));
    const audiences = (data.choices.audience_choices || []).filter((a) => a.id !== "everyone");
    const whoOptions = [{ value: "everyone", label: t.who_everyone }, ...audiences.map((a) => ({ value: `audience:${a.id}`, label: a.name })), { value: "people", label: t.who_people }];
    const whoValue = values.who === "audience" ? `audience:${values.audience}` : values.who;
    box.append(ui.field(t.f_who, ui.selectInput(whoOptions, whoValue, (v) => {
      if (v.startsWith("audience:")) Object.assign(values, { who: "audience", audience: v.slice(9) });
      else Object.assign(values, { who: v, audience: "" });
      again();
    }), t.who_hint));
    if (values.who === "people") {
      box.append(ui.chips(t.f_people, data.choices.persons.map((p) => ({ value: p.id, label: p.name })), values.people, (list) => { values.people = list; paint(); }));
    }

    box.append(el("h3", { className: "sec", textContent: t.sec_how }));
    box.append(ui.checkbox(t.f_dismissible, values.dismissible, (on) => { values.dismissible = on; paint(); }));
    const scopes = [{ value: "", label: t.scope_default }, { value: "user", label: t.scope_user }, { value: "global", label: t.scope_global }];
    box.append(ui.field(t.f_dismiss_scope, ui.selectInput(scopes, values.dismiss_scope, (v) => { values.dismiss_scope = v; paint(); })));
    box.append(ui.field(t.f_snoozable, ui.selectInput([{ value: "", label: t.snooze_default }, { value: "on", label: t.snooze_on }, { value: "off", label: t.snooze_off }], values.snoozable, (v) => { values.snoozable = v; paint(); })));
    box.append(ui.field(t.f_snooze_scope, ui.selectInput(scopes.map((o) => (o.value === "" ? { ...o, label: t.snooze_default } : o)), values.snooze_scope, (v) => { values.snooze_scope = v; paint(); })));
    box.append(ui.chips(t.f_snooze_minutes, SNOOZE_MINUTES.map((m) => ({ value: String(m), label: String(m) })), values.snooze_minutes, (list) => { values.snooze_minutes = list; paint(); }));
    box.append(ui.checkbox(t.f_snooze_custom, values.snooze_custom, (on) => { values.snooze_custom = on; paint(); }));
    // The value is the policy's key and the label its name, so a rename does not unset the rule (D-202).
    const listed = (data.policies || []).map((p) => ({ value: p.subentry_id, label: p.name }));
    if (values.policy && values.policy !== "none" && !listed.some((o) => o.value === values.policy)) {
      listed.push({ value: values.policy, label: `${values.policy.replace(/^name:/, "")} (${t.policy_missing})` });
    }
    const policies = [{ value: "", label: t.policy_all }, { value: "none", label: t.policy_none }, ...listed];
    box.append(ui.field(t.f_policy, ui.selectInput(policies, values.policy, (v) => { values.policy = v; paint(); }), t.policy_hint));
    const sb = s.buttons;
    const buttonsBox = el("div", {});
    buttonsBox.append(ui.buttonsEditor(s, values.actions, (list) => { values.actions = list; paint(); }, { listId: "hu-entities" }));
    box.append(ui.fold(`${sb.title}${values.actions.length ? ` (${values.actions.length})` : ""}`, buttonsBox, values.actions.length > 0));
    const tapBox = el("div", {}, [el("div", { className: "hint", textContent: sb.tap_hint })]);
    tapBox.append(ui.actionEditor(s, values.tap_action, (action, problem) => { values.tap_action = action; values.tap_problem = problem; paint(); }, { listId: "hu-entities" }));
    box.append(ui.fold(sb.tap, tapBox, Boolean(values.tap_action)));

    const words = el("div", {});
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    const save = el("button", { type: "button", className: "primary", textContent: s.common.save });
    save.addEventListener("click", saveIt);
    const cancel = el("button", { type: "button", textContent: s.common.cancel });
    cancel.addEventListener("click", requestClose);
    const buttons = el("div", { className: "row" }, [save, cancel]);
    if (own) {
      const del = el("button", { type: "button", className: "danger", textContent: s.common.delete });
      del.addEventListener("click", remove);
      buttons.append(del);
    }
    box.append(el("div", { className: "summary" }, [el("strong", { textContent: t.sentence }), words, status]), buttons);
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), ui.yamlBlock(ui.toYaml({ name: own.name, ...own.data }), s.common));
    function paint() {
      const buttonCodes = ui.buttonProblems(values.actions, values.dismissible).map((p) => p.code);
      const codes = [...new Set([...Object.values(validate(values, existing, own?.name)), ...buttonCodes, ...(values.tap_problem ? [values.tap_problem] : [])])];
      words.textContent = sentence(values, t);
      save.disabled = codes.length > 0;
      status.className = codes.length || message ? "hint problems" : "hint ok";
      status.textContent = codes.length ? errorTexts(codes) : message || s.common.valid;
    }
    paint();
    return box;
  }

  function render() {
    ui.lockHeight(root);
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS + ui.TABLE_CSS + CSS }), el("h1", { textContent: t.title }));
    root.append(ui.richNode(t.intro, { className: "hint pol-intro" }));
    const add = el("button", { type: "button", className: "primary" }, [el("ha-icon", { icon: "mdi:plus" }), el("span", { textContent: t.new })]);
    add.setAttribute("aria-haspopup", "dialog");
    add.addEventListener("click", () => openEditor(null, blankValues()));
    root.append(el("div", { className: "pol-bar" }, [add]));
    if (message) root.append(el("div", { className: "hint problems", textContent: message, role: "alert" }));
    root.append(table());
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "rule", own?.subentry_id, toFlowData(values, own));
    if (!result.ok) {
      message = errorTexts(Object.values(result.errors));
      refreshEditor();
      return;
    }
    message = "";
    editorDialog?.dialog.close();
    await load();
  }

  async function remove() {
    const { own } = editing;
    if (!window.confirm(fill(s.common.delete_confirm, { name: own.name }))) return;
    await ui.removeSubentry(hass, data.entry_id, own.subentry_id);
    editorDialog?.dialog.close();
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
