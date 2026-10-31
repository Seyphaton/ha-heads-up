// Heads Up panel: the welcome (D-121). A dialog on the first opening that explains the default
// policies and lets the admin switch each on or off. Loaded by the shell.

export const STRINGS = {
  en: {
    title: "Welcome to Heads Up",
    intro: "Heads Up can start with a few sensible defaults. Each one is a policy you can change or delete later on the Policies page. Switch off what you do not want; nothing is created until you press Create.",
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
    hub_off: "The hub is switched off. Switch it on in Settings to use the defaults.",
    failed: "Could not create the policies. Try again.",
  },
  de: {
    title: "Willkommen bei Heads Up",
    intro: "Heads Up kann mit ein paar sinnvollen Standards starten. Jeder ist eine Richtlinie, die du später auf der Seite Richtlinien ändern oder löschen kannst. Schalte aus, was du nicht willst; nichts wird erstellt, bis du Erstellen drückst.",
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
    hub_off: "Der Hub ist ausgeschaltet. Schalte ihn in den Einstellungen ein, um die Standards zu nutzen.",
    failed: "Die Richtlinien konnten nicht erstellt werden. Versuche es erneut.",
  },
  fr: {
    title: "Bienvenue dans Heads Up",
    intro: "Heads Up peut démarrer avec quelques réglages par défaut raisonnables. Chacun est une politique que vous pouvez modifier ou supprimer plus tard sur la page Politiques. Désactivez ce que vous ne voulez pas ; rien n'est créé avant d'appuyer sur Créer.",
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
    hub_off: "Le hub est désactivé. Activez-le dans Réglages pour utiliser les réglages par défaut.",
    failed: "Les politiques n'ont pas pu être créées. Réessayez.",
  },
  es: {
    title: "Te damos la bienvenida a Heads Up",
    intro: "Heads Up puede empezar con unos valores por defecto razonables. Cada uno es una política que puedes cambiar o borrar luego en la página Políticas. Desactiva lo que no quieras; no se crea nada hasta que pulses Crear.",
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
    hub_off: "El hub está desactivado. Actívalo en Ajustes para usar los valores por defecto.",
    failed: "No se pudieron crear las políticas. Inténtalo de nuevo.",
  },
};

export const ITEMS = ["quiet", "digest", "critical", "warnings"];

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

function el(tag, props = {}, children = []) {
  const created = document.createElement(tag);
  Object.assign(created, props);
  for (const child of children) created.append(child);
  return created;
}

const CSS = `
.hu-scrim { position: fixed; inset: 0; z-index: 20; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; padding: 16px; }
.hu-dialog { background: var(--card-background-color); color: var(--primary-text-color); border-radius: 12px; max-width: 640px; width: 100%; max-height: calc(100vh - 32px); overflow: auto; padding: 20px; box-shadow: 0 4px 24px rgba(0,0,0,.4); }
.hu-dialog h2 { margin: 0 0 8px; font-size: 20px; }
.hu-dialog .hint { color: var(--secondary-text-color); font-size: 13px; margin: 2px 0 8px; }
.hu-dialog .item { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; }
.hu-dialog label.inline { display: flex; align-items: center; gap: 10px; min-height: 48px; font-weight: 600; }
.hu-dialog input[type=checkbox] { width: 22px; height: 22px; }
.hu-dialog select { min-height: 40px; max-width: 100%; padding: 0 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--secondary-background-color); color: var(--primary-text-color); font: inherit; }
.hu-dialog fieldset { border: 1px solid var(--divider-color); border-radius: 8px; max-height: 160px; overflow: auto; margin: 8px 0; }
.hu-dialog legend { color: var(--secondary-text-color); font-size: 13px; }
.hu-dialog button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid var(--divider-color); background: transparent; color: var(--primary-text-color); font: inherit; cursor: pointer; }
.hu-dialog button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
.hu-dialog button:focus-visible, .hu-dialog select:focus-visible, .hu-dialog input:focus-visible { outline: 3px solid var(--primary-color); outline-offset: 2px; }
.hu-dialog .row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
`;

// Opens the welcome in `host`. On the first opening only while it has not been seen; with `force`
// always. Resolves to { close } or null when nothing is shown.
export async function open(host, ctx) {
  const { t, hass, ui } = ctx;
  const data = await hass.callWS({ type: "heads_up/welcome_get" });
  if (!ctx.force && !data.show) return null;
  const state = { on: Object.fromEntries(ITEMS.map((id) => [id, true])), audience: data.default_audience, speakers: [] };
  const scrim = el("div", { className: "hu-scrim" });
  const dialog = el("div", { className: "hu-dialog", role: "dialog" });
  dialog.setAttribute("aria-modal", "true");
  dialog.setAttribute("aria-label", t.title);
  scrim.append(el("style", { textContent: CSS }), dialog);
  host.append(scrim);
  let previous = host.activeElement;

  const close = () => {
    scrim.remove();
    if (previous?.isConnected) previous.focus?.();
  };
  const dismiss = async () => {
    // On the first opening "Not now" also counts as seen, so the dialog does not return every time.
    if (data.show) await hass.callWS({ type: "heads_up/welcome_apply", items: [] }).catch(() => {});
    close();
  };

  function render(message = "", done = false) {
    dialog.replaceChildren(el("h2", { textContent: t.title }));
    if (!data.hub) {
      dialog.append(el("div", { className: "hint", textContent: t.hub_off }));
      const closeButton = el("button", { type: "button", className: "primary", textContent: t.close });
      closeButton.addEventListener("click", close);
      dialog.append(el("div", { className: "row" }, [closeButton]));
      return;
    }
    if (done) {
      dialog.append(el("div", { textContent: message }));
      const closeButton = el("button", { type: "button", className: "primary", textContent: t.close });
      closeButton.addEventListener("click", close);
      dialog.append(el("div", { className: "row" }, [closeButton]));
      closeButton.focus();
      return;
    }
    dialog.append(el("div", { className: "hint", textContent: t.intro }));
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
          item.append(ui.chips(t.speakers, data.speakers.map((id2) => ({ value: id2, label: id2 })), state.speakers, (list) => { state.speakers = list; }, true));
        }
      }
      dialog.append(item);
    }
    const create = el("button", { type: "button", className: "primary", textContent: t.create });
    create.addEventListener("click", async () => {
      try {
        const result = await hass.callWS(payloadFor(state));
        render(resultText(result, t), true);
      } catch (err) {
        render(t.failed);
      }
    });
    const later = el("button", { type: "button", textContent: t.not_now });
    later.addEventListener("click", dismiss);
    dialog.append(el("div", { className: "row" }, [create, later]));
    if (message) dialog.append(el("div", { className: "hint", textContent: message }));
  }
  scrim.addEventListener("keydown", (event) => {
    if (event.key === "Escape") dismiss();
  });
  render();
  dialog.querySelector("input,button")?.focus();
  return { close };
}
