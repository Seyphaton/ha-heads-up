import { describe, expect, it } from "vitest";
import {
  ackText,
  blankValues,
  buildCall,
  callYaml,
  laterText,
  outcomeDone,
  outcomeRows,
  plannedLine,
  rowRecipient,
  STRINGS,
  summaryLine,
  validate,
} from "../../custom_components/heads_up/frontend/panel/test_send.js";
import { STRINGS as SHELL } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import { targetMode, toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

const S = SHELL.en.shared;
const T = STRINGS.en;

const values = (extra = {}) => ({ ...blankValues(), message: "Door open", ...extra });

describe("test send call", () => {
  it("builds only what is set", () => {
    expect(buildCall(values())).toEqual({ message: "Door open", severity: "warning", channels: ["banner"] });
  });

  it("adds title, tag, policy and trims the text", () => {
    const call = buildCall(values({ message: "  Door open ", title: " Garage ", tag: "door", policy: "none" }));
    expect(call).toEqual({ message: "Door open", title: "Garage", tag: "door", policy: "none", severity: "warning", channels: ["banner"] });
  });

  it("adds the dismiss and snooze choices only when they differ from the defaults", () => {
    expect(buildCall(values({ dismiss_scope: "global", snoozable: true }))).toMatchObject({ dismiss_scope: "global", snoozable: true });
    const pinned = buildCall(values({ dismissible: false, dismiss_scope: "global", snoozable: true }));
    expect(pinned.dismissible).toBe(false);
    expect(pinned.dismiss_scope).toBeUndefined();
    expect(pinned.snoozable).toBeUndefined();
    expect(buildCall(values({ dismissible: true }))).not.toHaveProperty("dismissible");
  });

  it("says whether anything waits for an acknowledgement, and how to make it so", () => {
    expect(ackText(["Water escalation", "Critical reminder"], T)).toContain("Water escalation, Critical reminder");
    expect(ackText([], T)).toContain("add an Escalation or Reminder policy");
    expect(ackText(undefined, T)).toBe(ackText([], T));
  });

  it("sends the spoken text only when speech is a channel", () => {
    expect(buildCall(values({ tts_message: "Hello" })).tts_message).toBeUndefined();
    const call = buildCall(values({ channels: ["speak"], tts_message: "Hello", speak_recipients: ["media_player.k"] }));
    expect(call.tts_message).toBe("Hello");
    expect(call.to).toEqual({ speak: { recipients: ["media_player.k"] } });
  });

  it("sends the target of each chosen channel and nothing for the others", () => {
    const call = buildCall(
      values({
        channels: ["push", "popup", "persistent"],
        push_audience: "At home",
        popup_recipients: ["person.anna"],
        speak_recipients: ["media_player.k"],
        persistent_audience: "Everyone",
      }),
    );
    expect(call.to).toEqual({ push: { audience: "At home" }, popup: { recipients: ["person.anna"] } });
  });

  it("never sends an audience for speech", () => {
    const call = buildCall(values({ channels: ["speak"], speak_audience: "Everyone" }));
    expect(call.to).toBeUndefined();
  });
});

describe("test send validation", () => {
  it("needs a message and a channel", () => {
    expect(validate({ ...blankValues(), channels: [] }).map((p) => p.code)).toEqual(["message_required", "channels_required"]);
    expect(validate(values())).toEqual([]);
  });

  it("needs a target for push, popup and speak but not for the banner or the bell", () => {
    expect(validate(values({ channels: ["push"] }))).toEqual([{ code: "target_required", channel: "push" }]);
    expect(validate(values({ channels: ["speak"] }))).toEqual([{ code: "target_required", channel: "speak" }]);
    expect(validate(values({ channels: ["banner", "persistent"] }))).toEqual([]);
    expect(validate(values({ channels: ["push"], push_audience: "Everyone" }))).toEqual([]);
  });

  it("refuses an audience and recipients together", () => {
    const both = values({ channels: ["popup"], popup_audience: "Everyone", popup_recipients: ["person.a"] });
    expect(validate(both)).toEqual([{ code: "target_exclusive", channel: "popup" }]);
    const banner = values({ banner_audience: "Everyone", banner_recipients: ["person.a"] });
    expect(validate(banner)).toEqual([{ code: "target_exclusive", channel: "banner" }]);
  });
});

describe("the call as YAML", () => {
  it("is a heads_up.notify action with the data", () => {
    const yaml = callYaml(values({ title: "Garage", channels: ["banner", "push"], push_audience: "At home", policy: "Water escalation" }), toYaml);
    expect(yaml).toBe(
      [
        "action: heads_up.notify",
        "data:",
        "  message: Door open",
        "  severity: warning",
        "  channels:",
        "    - banner",
        "    - push",
        "  title: Garage",
        "  policy: Water escalation",
        "  to:",
        "    push:",
        "      audience: At home",
      ].join("\n"),
    );
  });
});

describe("test send wording", () => {
  it("counts the results per channel and leaves out fallback rows", () => {
    const rows = [
      { channel: "banner", result: "sent" },
      { channel: "push", result: "sent" },
      { channel: "push", result: "sent" },
      { channel: "push", result: "skipped" },
      { channel: "push", result: "sent", via: "Backup" },
    ];
    expect(summaryLine(rows, S)).toBe("Banner: 1 sent; Push: 2 sent, 1 skipped");
    expect(summaryLine([], S)).toBe("");
  });

  it("words each later step", () => {
    expect(laterText({ type: "escalation", policy: "Water", after_minutes: 5, channels: ["push", "speak"] }, T, S)).toBe(
      "Escalation Water: after 5 min unless someone acknowledges, also on Push, Speak.",
    );
    expect(laterText({ type: "reminder", policy: "Nag", every_minutes: 30, max_count: 3, channels: [] }, T, S)).toBe(
      "Reminder Nag: every 30 min, at most 3 times.",
    );
    expect(laterText({ type: "reminder", policy: "Nag", every_minutes: 30, max_count: 3, channels: ["push"] }, T, S)).toBe(
      "Reminder Nag: every 30 min, at most 3 times, only on Push.",
    );
    expect(laterText({ type: "away", policy: "Back", max_wait: 0 }, T, S)).toBe("Away Back: people who are not home get it when they arrive.");
    expect(laterText({ type: "away", policy: "Back", max_wait: 20 }, T, S)).toBe("Away Back: people who are not home get it when they arrive, for at most 20 min.");
    expect(laterText({ type: "fallback", policy: "Backup", when: "failed", channels: ["persistent"] }, T, S)).toBe(
      "Fallback Backup: if delivery fails, it is sent on Persistent Notification instead.",
    );
    expect(laterText({ type: "summarize", policy: "Digest", summary_every: 60 }, T, S)).toBe("Summary Digest: one summary 60 min after the first held message.");
    expect(laterText({ type: "summarize", policy: "Evening", summary_at: "20:00:00" }, T, S)).toBe("Summary Evening: one summary every day at 20:00.");
  });

  it("has the same keys and placeholders in every language", () => {
    const leaves = (object, path = "") =>
      Object.entries(object).flatMap(([key, value]) => (typeof value === "object" ? leaves(value, `${path}${key}.`) : [[`${path}${key}`, value]]));
    const english = Object.fromEntries(leaves(STRINGS.en));
    const holders = (text) => (String(text).match(/\{[a-z]+\}/g) || []).sort();
    for (const [code, language] of Object.entries(STRINGS)) {
      const own = Object.fromEntries(leaves(language));
      expect(Object.keys(own).sort(), code).toEqual(Object.keys(english).sort());
      for (const key of Object.keys(english)) expect(holders(own[key]), `${code}.${key}`).toEqual(holders(english[key]));
    }
  });
});

describe("test send rows and target mode", () => {
  const choices = { persons: [{ id: "person.anna", name: "Anna" }, { id: "person.ben", name: "Ben" }], registrations: [{ id: "d1", name: "Pixel" }] };

  it("shows the person and the device on a push row", () => {
    expect(rowRecipient({ recipient: "device:d1", person: "person.anna", channel: "push" }, {}, choices, T)).toBe("Anna · Pixel");
    expect(rowRecipient({ recipient: "person.anna", person: "person.anna", channel: "popup" }, {}, choices, T)).toBe("Anna");
  });

  it("shows who a banner is limited to, everyone, or nobody", () => {
    const row = { recipient: "", channel: "banner", result: "sent" };
    expect(rowRecipient(row, { banner_people: ["person.anna", "person.ben"] }, choices, T)).toBe("Anna, Ben");
    expect(rowRecipient(row, { banner_people: [] }, choices, T)).toBe("everyone");
    expect(rowRecipient({ ...row, result: "skipped" }, { banner_people: [] }, choices, T)).toBe("nobody");
  });

  it("keeps a chosen mode while no recipient is ticked", () => {
    expect(targetMode({}, "push")).toBe("audience");
    expect(targetMode({ push_recipients: ["person.anna"] }, "push")).toBe("recipients");
    expect(targetMode({ _mode_push: "recipients", push_recipients: [] }, "push")).toBe("recipients");
    expect(targetMode({ _mode_push: "audience", push_recipients: ["person.anna"] }, "push")).toBe("audience");
    expect(targetMode({}, "speak")).toBe("recipients");
  });
});

describe("test send outcome", () => {
  const entries = [
    { channel: "banner", recipient: "", result: "sent" },
    { channel: "speak", recipient: "media_player.k", result: "failed", reason: "no_tts_engine" },
    { channel: "push", recipient: "device:d1", result: "cleared" },
  ];

  it("keeps the real delivery results of the named channels, the banner included", () => {
    expect(outcomeRows(entries, ["banner", "speak", "push"])).toEqual([entries[0], entries[1]]);
    expect(outcomeRows(entries, ["banner"])).toEqual([entries[0]]);
    expect(outcomeRows(entries, ["speak"])).toEqual([entries[1]]);
  });

  it("is done once every named channel has a result", () => {
    expect(outcomeDone(entries, ["banner", "speak"])).toBe(true);
    expect(outcomeDone(entries, ["banner", "speak", "push"])).toBe(false);
    expect(outcomeDone([], ["banner"])).toBe(false); // a banner-only send waits for its row
    expect(outcomeDone(entries, ["banner"])).toBe(true);
  });

  it("words the planned counts with every kind, not only sent", () => {
    expect(plannedLine({ speak: { sent: 0, held: 0, skipped: 1, failed: 0 }, banner: { sent: 1, held: 0, skipped: 0, failed: 0 } }, S)).toBe(
      "Speak: 1 skipped; Banner: 1 sent",
    );
  });
});

