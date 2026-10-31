import { describe, expect, it } from "vitest";
import {
  blankValues,
  buildCall,
  callYaml,
  laterText,
  STRINGS,
  summaryLine,
  validate,
} from "../../custom_components/heads_up/frontend/panel/test_send.js";
import { STRINGS as SHELL } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import { toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

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
      "Fallback Backup: if delivery fails, it is sent on Bell instead.",
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
