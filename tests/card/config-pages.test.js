import { describe, expect, it } from "vitest";
import { countText, initials, peopleText, STRINGS as AUD, usageText } from "../../custom_components/heads_up/frontend/panel/audiences.js";
import { languageName, languageOptions, STRINGS as CH, summaryText } from "../../custom_components/heads_up/frontend/panel/channels.js";
import { byAudience, STRINGS as MSG } from "../../custom_components/heads_up/frontend/panel/messages.js";

const sameKeys = (strings) => {
  const keys = Object.keys(strings.en).sort();
  for (const t of Object.values(strings)) expect(Object.keys(t).sort()).toEqual(keys);
};

describe("Audiences overview (D-227)", () => {
  const t = AUD.en;
  it("says how many people are in it and how often it was used", () => {
    expect(peopleText(1, t)).toBe("1 person");
    expect(peopleText(3, t)).toBe("3 people");
    expect(countText(0, t)).toBe("None yet");
    expect(countText(1, t)).toBe("1 message");
    expect(usageText({ count: 12, last: "x" }, t, () => "2 hours ago")).toBe("12 messages · last 2 hours ago");
    expect(usageText(undefined, t, () => "")).toBe("None yet");
  });

  it("shows up to two initials on a member chip", () => {
    expect(initials("Dev Admin")).toBe("DA");
    expect(initials("anna")).toBe("A");
    expect(initials(" ")).toBe("?");
  });

  it("has the same keys in every language", () => sameKeys(AUD));
});

describe("Channels overview", () => {
  const t = CH.en;
  it("sums up each channel in one line", () => {
    expect(summaryText("push", { push_lockscreen: "full", push_channel_id: "heads_up", push_sticky: true }, t)).toBe("Title and text · Android channel heads_up · kept after a tap");
    expect(summaryText("speech", { speak_language: "" }, t)).toBe("Home Assistant language");
    expect(summaryText("mail", { mail_service: "" }, t)).toBe("Off");
    expect(summaryText("mail", { mail_service: "smtp", mail_global_address: "a@example.org" }, t)).toBe("notify.smtp · global address a@example.org");
  });

  it("offers the Home Assistant language first, then the engine's languages by name", () => {
    const options = languageOptions(["fr", "de-DE"], "", "en", "en", t);
    expect(options[0]).toEqual({ value: "", label: "Home Assistant language (English · en)" });
    expect(options.slice(1).map((o) => o.value)).toEqual(["fr", "de-DE"]);
    expect(languageName("de-DE", "en")).toBe("German (Germany) · de-DE");
  });

  it("keeps a saved language that the engine does not list", () => {
    expect(languageOptions(["fr"], "xx-YY", "en", "en", t).map((o) => o.value)).toContain("xx-YY");
  });

  it("has the same keys in every language", () => sameKeys(CH));
});

describe("Message Log filter", () => {
  it("keeps the messages sent to an audience", () => {
    const list = [{ id: "a", audiences: ["everyone"] }, { id: "b" }, { id: "c", audiences: ["admins", "everyone"] }];
    expect(byAudience(list, "everyone").map((m) => m.id)).toEqual(["a", "c"]);
  });

  it("has the same keys in every language", () => sameKeys(MSG));
});
