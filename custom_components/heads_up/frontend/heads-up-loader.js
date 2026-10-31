// Heads Up popup loader (docs/popup.md)
(async () => {
 const ha = () => document.querySelector("home-assistant");
 let un, mod, busy;
 for (let i = 0; i < 60 && !ha()?.hass?.connection; i++)
  await new Promise((r) => setTimeout(r, 500));
 const run = async () => {
  const c = ha()?.hass?.connection;
  if (!c || un || busy) return;
  busy = 1;
  try {
   const cfg = await c.sendMessagePromise({ type: "heads_up/popup_config" });
   if (cfg.enabled)
    un = await c.subscribeMessage(
     async (e) => {
      if (!e.messages.length && !mod) return;
      mod ||= await import(cfg.module);
      mod.show(ha(), e.messages, cfg);
     },
     { type: "heads_up/popup_subscribe" },
     { resubscribe: false },
    );
  } catch (_) {}
  busy = 0;
 };
 run();
 ha()?.hass?.connection?.addEventListener("ready", () => ((un = 0), run()));
 document.addEventListener("visibilitychange", () => document.visibilityState == "visible" && run());
})();
