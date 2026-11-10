// Heads Up panel: Watch rules page (D-134). A list of the rules with their state and an editor that
// saves through the integration's own rule flow, like the other editors (D-119).

export const STRINGS = {
  en: {
    title: "Watch rules",
    intro: "A watch rule shows a banner while an entity is in a state, or while a template is true.\n\n- When the condition no longer holds, Heads Up removes the banner by itself.\n- Rules are stored in Heads Up, not in a dashboard. Several cards with different filters share the same rules and messages without copying them.\n\nAn automation can do the same: a trigger that calls heads_up.create_banner, or heads_up.notify with the banner channel, with the condition filled in.",
    none: "You have no watch rules yet.",
    showing: "Showing now",
    not_showing: "Not showing",
    off: "Off",
    new: "New watch rule",
    editing: "Edit watch rule",
    sec_when: "When",
    sec_what: "What to show",
    sec_who: "Who sees it",
    sec_how: "Behaviour",
    kind_entity: "An entity is in a state",
    kind_template: "A template is true",
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
    f_people: "People (none: everyone)",
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
    f_enabled: "Enabled",
    kept: "Buttons and the tap action stay as they are. Change them in the full form on the integration page.",
    sentence: "Sentence",
    sentence_entity: "Shows “{message}” ({severity}) while {entity} {operator} {value}.",
    sentence_template: "Shows “{message}” ({severity}) while the template is true.",
    sentence_for: " The condition must hold for {n} min first.",
    watches: "watches {entity} {operator} {value}",
    watches_template: "watches a template",
    operators: {"equals": "equals", "not_equals": "does not equal", "above": "above", "below": "below", "between": "between", "contains": "contains", "not_contains": "does not contain", "empty": "is empty", "not_empty": "is not empty"},
    severities: {"success": "Success", "info": "Info", "warning": "Warning", "critical": "Critical"},
    saved: "Saved.",
    failed: "Could not save. Try again.",
    errors: {"entity_not_found": "This entity does not exist.", "message_required": "Enter a message.", "message_too_long": "The message can have up to 1000 characters.", "message_template_invalid": "The message contains an invalid template.", "title_too_long": "The title can have up to 100 characters.", "state_count": "Above and below need one number, between needs two.", "state_not_numeric": "Enter numbers only for this condition.", "state_required": "Enter at least one value.", "for_too_long": "Use 24 hours or less.", "snoozable_needs_dismissible": "Snoozable needs Dismissible to be on.", "entity_and_template": "Use an entity or a template, not both.", "entity_or_template_required": "Choose an entity or enter a template.", "template_invalid": "The template is not valid.", "actions_invalid": "The buttons are not valid. Each needs a key and a label, up to 3.", "tap_action_invalid": "The tap action needs an action key.", "image_invalid": "The image must be an http(s) URL or a path starting with /.", "actions_dismiss_needs_dismissible": "A button with dismiss needs Dismissible to be on.", "policy_unknown": "This policy does not exist. Use the name of a policy, or none.", "name_required": "Enter a name.", "name_exists": "This name is already used."},
  },
  de: {
    title: "Überwachungsregeln",
    intro: "Eine Überwachungsregel zeigt ein Banner, solange eine Entität einen Zustand hat oder eine Vorlage wahr ist.\n\n- Gilt die Bedingung nicht mehr, entfernt Heads Up das Banner von selbst.\n- Regeln liegen in Heads Up, nicht in einem Dashboard. Mehrere Karten mit unterschiedlichen Filtern nutzen dieselben Regeln und Meldungen, ohne sie zu kopieren.\n\nEine Automation kann dasselbe: ein Auslöser, der heads_up.create_banner oder heads_up.notify mit dem Kanal Banner aufruft, mit ausgefüllter Bedingung.",
    none: "Du hast noch keine Überwachungsregeln.",
    showing: "Wird gezeigt",
    not_showing: "Wird nicht gezeigt",
    off: "Aus",
    new: "Neue Überwachungsregel",
    editing: "Überwachungsregel bearbeiten",
    sec_when: "Wann",
    sec_what: "Was gezeigt wird",
    sec_who: "Wer es sieht",
    sec_how: "Verhalten",
    kind_entity: "Eine Entität hat einen Zustand",
    kind_template: "Eine Vorlage ist wahr",
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
    f_people: "Personen (keine: alle)",
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
    f_enabled: "Aktiv",
    kept: "Schaltflächen und Tippaktion bleiben unverändert. Ändere sie im vollständigen Formular auf der Integrationsseite.",
    sentence: "Satz",
    sentence_entity: "Zeigt „{message}“ ({severity}), solange {entity} {operator} {value}.",
    sentence_template: "Zeigt „{message}“ ({severity}), solange die Vorlage wahr ist.",
    sentence_for: " Die Bedingung muss zuerst {n} Min. gelten.",
    watches: "überwacht {entity} {operator} {value}",
    watches_template: "überwacht eine Vorlage",
    operators: {"equals": "ist gleich", "not_equals": "ist ungleich", "above": "über", "below": "unter", "between": "zwischen", "contains": "enthält", "not_contains": "enthält nicht", "empty": "ist leer", "not_empty": "ist nicht leer"},
    severities: {"success": "Erfolg", "info": "Info", "warning": "Warnung", "critical": "Kritisch"},
    saved: "Gespeichert.",
    failed: "Speichern fehlgeschlagen. Versuche es erneut.",
    errors: {"entity_not_found": "Diese Entität existiert nicht.", "message_required": "Gib eine Nachricht ein.", "message_too_long": "Die Nachricht darf bis zu 1000 Zeichen haben.", "message_template_invalid": "Die Nachricht enthält eine ungültige Vorlage.", "title_too_long": "Der Titel darf bis zu 100 Zeichen haben.", "state_count": "„Über“ und „Unter“ brauchen eine Zahl, „Zwischen“ braucht zwei.", "state_not_numeric": "Gib für diese Bedingung nur Zahlen ein.", "state_required": "Gib mindestens einen Wert ein.", "for_too_long": "Verwende 24 Stunden oder weniger.", "snoozable_needs_dismissible": "„Zurückstellbar“ benötigt, dass „Schließbar“ an ist.", "entity_and_template": "Verwende eine Entität oder eine Vorlage, nicht beides.", "entity_or_template_required": "Wähle eine Entität oder gib eine Vorlage ein.", "template_invalid": "Die Vorlage ist ungültig.", "actions_invalid": "Die Schaltflächen sind ungültig. Jede braucht key und label, höchstens 3.", "tap_action_invalid": "Die Tipp-Aktion braucht einen action-Schlüssel.", "image_invalid": "Das Bild muss eine http(s)-URL oder ein Pfad sein, der mit / beginnt.", "actions_dismiss_needs_dismissible": "Eine Schaltfläche mit dismiss braucht „Schließbar“ an.", "policy_unknown": "Diese Richtlinie gibt es nicht. Nimm den Namen einer Richtlinie oder none.", "name_required": "Gib einen Namen ein.", "name_exists": "Dieser Name wird schon verwendet."},
  },
  fr: {
    title: "Règles de surveillance",
    intro: "Une règle de surveillance affiche une bannière tant qu'une entité est dans un état, ou tant qu'un modèle est vrai.\n\n- Quand la condition n'est plus vraie, Heads Up retire la bannière tout seul.\n- Les règles sont stockées dans Heads Up, pas dans un tableau de bord. Plusieurs cartes avec des filtres différents partagent les mêmes règles et messages sans les copier.\n\nUne automatisation peut faire la même chose : un déclencheur qui appelle heads_up.create_banner, ou heads_up.notify avec le canal bannière, avec la condition renseignée.",
    none: "Vous n'avez pas encore de règle de surveillance.",
    showing: "Affichée",
    not_showing: "Non affichée",
    off: "Désactivée",
    new: "Nouvelle règle de surveillance",
    editing: "Modifier la règle de surveillance",
    sec_when: "Quand",
    sec_what: "Quoi afficher",
    sec_who: "Qui la voit",
    sec_how: "Comportement",
    kind_entity: "Une entité est dans un état",
    kind_template: "Un modèle est vrai",
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
    f_people: "Personnes (aucune : tout le monde)",
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
    f_enabled: "Activée",
    kept: "Les boutons et l'action au toucher restent inchangés. Modifiez-les dans le formulaire complet de la page de l'intégration.",
    sentence: "Phrase",
    sentence_entity: "Affiche « {message} » ({severity}) tant que {entity} {operator} {value}.",
    sentence_template: "Affiche « {message} » ({severity}) tant que le modèle est vrai.",
    sentence_for: " La condition doit d'abord durer {n} min.",
    watches: "surveille {entity} {operator} {value}",
    watches_template: "surveille un modèle",
    operators: {"equals": "est égal à", "not_equals": "est différent de", "above": "au-dessus de", "below": "en dessous de", "between": "entre", "contains": "contient", "not_contains": "ne contient pas", "empty": "est vide", "not_empty": "n'est pas vide"},
    severities: {"success": "Succès", "info": "Info", "warning": "Avertissement", "critical": "Critique"},
    saved: "Enregistré.",
    failed: "Échec de l'enregistrement. Réessayez.",
    errors: {"entity_not_found": "Cette entité n'existe pas.", "message_required": "Saisissez un message.", "message_too_long": "Le message peut contenir jusqu'à 1000 caractères.", "message_template_invalid": "Le message contient un modèle non valide.", "title_too_long": "Le titre peut contenir jusqu'à 100 caractères.", "state_count": "« Supérieur » et « Inférieur » demandent un nombre, « Entre » en demande deux.", "state_not_numeric": "Saisissez uniquement des nombres pour cette condition.", "state_required": "Saisissez au moins une valeur.", "for_too_long": "Utilisez 24 heures ou moins.", "snoozable_needs_dismissible": "« Reportable » nécessite que « Fermable » soit activé.", "entity_and_template": "Utilisez une entité ou un modèle, pas les deux.", "entity_or_template_required": "Choisissez une entité ou saisissez un modèle.", "template_invalid": "Le modèle n'est pas valide.", "actions_invalid": "Les boutons ne sont pas valides. Chacun a besoin d'une key et d'un label, 3 au maximum.", "tap_action_invalid": "L'action au toucher a besoin d'une clé action.", "image_invalid": "L'image doit être une URL http(s) ou un chemin commençant par /.", "actions_dismiss_needs_dismissible": "Un bouton avec dismiss nécessite que « Fermable » soit activé.", "policy_unknown": "Cette politique n'existe pas. Utilisez le nom d'une politique, ou none.", "name_required": "Saisissez un nom.", "name_exists": "Ce nom est déjà utilisé."},
  },
  es: {
    title: "Reglas de vigilancia",
    intro: "Una regla de vigilancia muestra un aviso mientras una entidad está en un estado, o mientras una plantilla es verdadera.\n\n- Cuando la condición deja de cumplirse, Heads Up quita el aviso solo.\n- Las reglas se guardan en Heads Up, no en un panel. Varias tarjetas con filtros distintos comparten las mismas reglas y mensajes sin copiarlos.\n\nUna automatización puede hacer lo mismo: un disparador que llama a heads_up.create_banner, o a heads_up.notify con el canal aviso, con la condición rellenada.",
    none: "Aún no tienes reglas de vigilancia.",
    showing: "Mostrándose",
    not_showing: "No se muestra",
    off: "Desactivada",
    new: "Nueva regla de vigilancia",
    editing: "Editar regla de vigilancia",
    sec_when: "Cuándo",
    sec_what: "Qué mostrar",
    sec_who: "Quién lo ve",
    sec_how: "Comportamiento",
    kind_entity: "Una entidad está en un estado",
    kind_template: "Una plantilla es verdadera",
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
    f_people: "Personas (ninguna: todos)",
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
    f_enabled: "Activada",
    kept: "Los botones y la acción al tocar se quedan como están. Cámbialos en el formulario completo de la página de la integración.",
    sentence: "Frase",
    sentence_entity: "Muestra «{message}» ({severity}) mientras {entity} {operator} {value}.",
    sentence_template: "Muestra «{message}» ({severity}) mientras la plantilla sea verdadera.",
    sentence_for: " La condición debe cumplirse antes durante {n} min.",
    watches: "vigila {entity} {operator} {value}",
    watches_template: "vigila una plantilla",
    operators: {"equals": "es igual a", "not_equals": "es distinto de", "above": "por encima de", "below": "por debajo de", "between": "entre", "contains": "contiene", "not_contains": "no contiene", "empty": "está vacío", "not_empty": "no está vacío"},
    severities: {"success": "Éxito", "info": "Info", "warning": "Aviso", "critical": "Crítico"},
    saved: "Guardado.",
    failed: "No se pudo guardar. Inténtalo de nuevo.",
    errors: {"entity_not_found": "Esta entidad no existe.", "message_required": "Introduce un mensaje.", "message_too_long": "El mensaje puede tener hasta 1000 caracteres.", "message_template_invalid": "El mensaje contiene una plantilla no válida.", "title_too_long": "El título puede tener hasta 100 caracteres.", "state_count": "«Por encima» y «Por debajo» necesitan un número, «Entre» necesita dos.", "state_not_numeric": "Introduce solo números para esta condición.", "state_required": "Introduce al menos un valor.", "for_too_long": "Usa 24 horas o menos.", "snoozable_needs_dismissible": "«Se puede posponer» requiere que «Se puede cerrar» esté activado.", "entity_and_template": "Usa una entidad o una plantilla, no ambas.", "entity_or_template_required": "Elige una entidad o introduce una plantilla.", "template_invalid": "La plantilla no es válida.", "actions_invalid": "Los botones no son válidos. Cada uno necesita key y label, como máximo 3.", "tap_action_invalid": "La acción al tocar necesita una clave action.", "image_invalid": "La imagen debe ser una URL http(s) o una ruta que empieza por /.", "actions_dismiss_needs_dismissible": "Un botón con dismiss requiere que «Se puede cerrar» esté activado.", "policy_unknown": "Esta política no existe. Usa el nombre de una política, o none.", "name_required": "Introduce un nombre.", "name_exists": "Este nombre ya se usa."},
  },
};

export const OPERATORS = ["equals", "not_equals", "above", "below", "between", "contains", "not_contains", "empty", "not_empty"];
const SEVERITIES = ["success", "info", "warning", "critical"];
const SNOOZE_MINUTES = [5, 15, 30, 60, 120, 240, 480, 1440];
const NO_VALUE = ["empty", "not_empty"];

export function fill(template, params) {
  return Object.entries(params).reduce((text, [key, value]) => text.replace(`{${key}}`, value ?? ""), template);
}

export function blankValues() {
  return {
    name: "", kind: "entity", entity_id: "", operator: "equals", state: "", attribute: "", for_minutes: "", template: "",
    message: "", title: "", severity: "warning", icon: "", image: "", people: [],
    dismissible: false, dismiss_scope: "", snoozable: "", snooze_scope: "", snooze_minutes: [], policy: "", enabled: true,
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
    people: [...(d.people || [])],
    dismissible: Boolean(d.dismissible),
    dismiss_scope: text(d.dismiss_scope),
    snoozable: d.snoozable === undefined ? "" : d.snoozable ? "on" : "off",
    snooze_scope: text(d.snooze_scope),
    snooze_minutes: (d.snooze_options || []).map((s) => String(Math.round(s / 60))),
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
    people: [...values.people],
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
  for (const key of ["title", "icon", "image"]) if (values[key].trim()) data[key] = values[key].trim();
  if (values.dismiss_scope) data.dismiss_scope = values.dismiss_scope;
  if (values.snoozable) data.snoozable = values.snoozable === "on";
  if (values.snooze_scope) data.snooze_scope = values.snooze_scope;
  if (values.snooze_minutes.length) data.snooze_options = [...values.snooze_minutes];
  if (values.policy) data.policy = values.policy;
  const kept = own?.data || {};
  if (kept.actions) data.actions = kept.actions;
  if (kept.tap_action) data.tap_action = kept.tap_action;
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

export function sentence(values, t) {
  const severity = t.severities[values.severity] || values.severity;
  const forText = Number(values.for_minutes) > 0 ? fill(t.sentence_for, { n: values.for_minutes }) : "";
  if (values.kind === "template") return fill(t.sentence_template, { message: values.message, severity }) + forText;
  const value = NO_VALUE.includes(values.operator) ? "" : splitValues(values.state).join(", ") || "on";
  return fill(t.sentence_entity, { message: values.message, severity, entity: values.entity_id || "…", operator: t.operators[values.operator], value }).replace(" .", ".") + forText;
}

export function mount(container, ctx) {
  const { t, ui } = ctx;
  const s = ctx.s;
  const { el } = ui;
  let hass = ctx.hass;
  let data = null;
  let editing = null; // { own, values }
  let message = "";
  const root = el("div", { className: "hu-page" });
  container.append(root);

  const personName = (id) => data.choices.persons.find((p) => p.id === id)?.name ?? id;
  const errorTexts = (codes) => codes.map((c) => t.errors[c] || ui.errorText(c, ctx.language)).join(" ");

  function row(rule) {
    const d = rule.data;
    const enabled = d.enabled !== false;
    const state = !enabled ? t.off : rule.showing ? t.showing : t.not_showing;
    const edit = el("button", { type: "button", textContent: s.common.edit });
    edit.addEventListener("click", () => {
      message = "";
      editing = { own: rule, values: fromRule(rule) };
      render();
    });
    return el("li", { className: enabled ? "" : "dim" }, [
      el("div", {}, [
        el("strong", { textContent: rule.name }),
        el("div", { className: "badges" }, [
          el("span", { className: `badge${enabled && rule.showing ? " on" : ""}`, textContent: state }),
          el("span", { className: `badge sev sev-${d.severity || "warning"}`, textContent: t.severities[d.severity || "warning"] }),
        ]),
        el("div", { className: "sub", textContent: watchesText(d, t) }),
        el("div", { className: "sub" }, [/\{[{%]/.test(d.message || "") ? el("code", { className: "tpl", textContent: d.message }) : document.createTextNode(d.message || "")]),
      ]),
      edit,
    ]);
  }

  function editor() {
    const { own, values } = editing;
    const existing = data.rules.map((r) => r.name);
    const box = el("section", {}, [el("h2", { textContent: own ? t.editing : t.new })]);
    const again = () => render();
    const text = (key, label, extra = {}) => ui.field(label, ui.textInput(values[key], (v) => { values[key] = v; paint(); }, extra));
    box.append(ui.field(s.common.name, ui.textInput(values.name, (v) => { values.name = v; paint(); })));

    box.append(el("h2", { textContent: t.sec_when, style: "margin-top:12px" }));
    box.append(ui.selectInput([{ value: "entity", label: t.kind_entity }, { value: "template", label: t.kind_template }], values.kind, (v) => { values.kind = v; again(); }));
    if (values.kind === "template") {
      const area = el("textarea", { value: values.template, rows: 3, style: "width:100%;max-width:100%;box-sizing:border-box" });
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

    box.append(el("h2", { textContent: t.sec_what, style: "margin-top:12px" }));
    const msg = el("textarea", { value: values.message, rows: 3, style: "width:100%;max-width:100%;box-sizing:border-box" });
    msg.addEventListener("input", () => { values.message = msg.value; paint(); });
    box.append(ui.field(t.f_message, msg), text("title", t.f_title));
    box.append(ui.field(t.f_severity, ui.selectInput(SEVERITIES.map((k) => ({ value: k, label: t.severities[k] })), values.severity, (v) => { values.severity = v; paint(); })));
    box.append(text("icon", t.f_icon), text("image", t.f_image, { style: "max-width:100%" }));

    box.append(el("h2", { textContent: t.sec_who, style: "margin-top:12px" }));
    box.append(ui.chips(t.f_people, data.choices.persons.map((p) => ({ value: p.id, label: p.name })), values.people, (list) => { values.people = list; paint(); }));

    box.append(el("h2", { textContent: t.sec_how, style: "margin-top:12px" }));
    box.append(ui.checkbox(t.f_dismissible, values.dismissible, (on) => { values.dismissible = on; paint(); }));
    const scopes = [{ value: "", label: t.scope_default }, { value: "user", label: t.scope_user }, { value: "global", label: t.scope_global }];
    box.append(ui.field(t.f_dismiss_scope, ui.selectInput(scopes, values.dismiss_scope, (v) => { values.dismiss_scope = v; paint(); })));
    box.append(ui.field(t.f_snoozable, ui.selectInput([{ value: "", label: t.snooze_default }, { value: "on", label: t.snooze_on }, { value: "off", label: t.snooze_off }], values.snoozable, (v) => { values.snoozable = v; paint(); })));
    box.append(ui.field(t.f_snooze_scope, ui.selectInput(scopes.map((o) => (o.value === "" ? { ...o, label: t.snooze_default } : o)), values.snooze_scope, (v) => { values.snooze_scope = v; paint(); })));
    box.append(ui.chips(t.f_snooze_minutes, SNOOZE_MINUTES.map((m) => ({ value: String(m), label: String(m) })), values.snooze_minutes, (list) => { values.snooze_minutes = list; paint(); }));
    // The value is the policy's key and the label its name, so a rename does not unset the rule (D-202).
    const listed = (data.policies || []).map((p) => ({ value: p.subentry_id, label: p.name }));
    if (values.policy && values.policy !== "none" && !listed.some((o) => o.value === values.policy)) {
      listed.push({ value: values.policy, label: `${values.policy.replace(/^name:/, "")} (${t.policy_missing})` });
    }
    const policies = [{ value: "", label: t.policy_all }, { value: "none", label: t.policy_none }, ...listed];
    box.append(ui.field(t.f_policy, ui.selectInput(policies, values.policy, (v) => { values.policy = v; paint(); }), t.policy_hint));
    box.append(ui.checkbox(t.f_enabled, values.enabled, (on) => { values.enabled = on; paint(); }));
    if (own && (own.data.actions || own.data.tap_action)) box.append(el("div", { className: "hint", textContent: t.kept }));

    const words = el("div", { className: "hint" });
    const status = el("div", { className: "hint" });
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
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
    box.append(el("h2", { textContent: t.sentence, style: "margin-top:12px" }), words, status, buttons);
    if (own) box.append(el("div", { className: "hint", textContent: s.common.yaml }), el("pre", { textContent: ui.toYaml({ name: own.name, ...own.data }) }));
    function paint() {
      const codes = Object.values(validate(values, existing, own?.name));
      words.textContent = sentence(values, t);
      save.disabled = codes.length > 0;
      status.className = codes.length || message ? "hint problems" : "hint ok";
      status.textContent = codes.length ? errorTexts(codes) : message || s.common.valid;
    }
    paint();
    return box;
  }

  function render() {
    root.replaceChildren(el("style", { textContent: ui.BASE_CSS }), el("h1", { textContent: t.title }));
    root.append(ui.richNode(t.intro, { className: "hint" }));
    if (editing) return void root.append(editor());
    const list = el("ul", { className: "list" }, data.rules.length ? data.rules.map(row) : [el("li", { className: "sub", textContent: t.none })]);
    const add = el("button", { type: "button", className: "primary", textContent: s.common.add });
    add.addEventListener("click", () => { message = ""; editing = { own: null, values: blankValues() }; render(); });
    root.append(el("section", {}, [list, add]));
  }

  async function saveIt() {
    const { own, values } = editing;
    const result = await ui.runFlow(hass, data.entry_id, "rule", own?.subentry_id, toFlowData(values, own));
    if (!result.ok) {
      message = errorTexts(Object.values(result.errors).map((c) => c));
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
