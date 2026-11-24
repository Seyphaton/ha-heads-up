import { describe, expect, it } from "vitest";
import { countText, initials, peopleText, STRINGS as AUD, usageText } from "../../custom_components/heads_up/frontend/panel/audiences.js";
import { inboxLine, languageName, languageOptions, problems, settingChanges, settingProblems, STRINGS as CH, stylesText, summaryText, validRetention } from "../../custom_components/heads_up/frontend/panel/channels.js";
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
    expect(summaryText("persistent", {}, t)).toBe("No settings");
    expect(summaryText("inbox", { inbox_retention_months: 12 }, t)).toBe("Kept for 12 months");
    expect(summaryText("inbox", { inbox_retention_months: 6, inbox_all_notifications: true }, t)).toBe("Kept for 6 months · all notifications");
    expect(summaryText("mail", { mail_service: "smtp", mail_global_address: "a@example.org" }, t)).toBe("notify.smtp · global address a@example.org");
  });

  it("offers the Home Assistant language first, then the engine's languages by name", () => {
    const options = languageOptions(["fr", "de-DE"], "", "en", "en", t);
    expect(options[0]).toEqual({ value: "", label: "Home Assistant language (English · en)" });
    expect(options.slice(1).map((o) => o.value)).toEqual(["fr", "de-DE"]);
    expect(languageName("de-DE", "en")).toBe("German (Germany) · de-DE");
  });

  it("sums up the banner snooze choices and the popup styles by severity", () => {
    expect(summaryText("banner", {}, t, "en", { default_snooze_options: [15, 60] })).toBe("Snooze 15 minutes, 1 hour");
    expect(summaryText("banner", {}, t, "en", { default_snooze_options: [] })).toBe("no snooze choices");
    expect(stylesText({ critical: "modal", warning: "card", info: "card" }, t)).toBe("Centered window (Critical) · Corner, bottom right (Warning, Info)");
  });

  it("sends only the snooze settings that changed and checks the snooze time", () => {
    const saved = { default_snooze_options: [15], quick_snooze_minutes: 15 };
    expect(settingChanges({ ...saved, quick_snooze_minutes: 30 }, saved)).toEqual({ quick_snooze_minutes: 30 });
    expect(settingProblems({ quick_snooze_minutes: 0 })).toEqual(["bad_snooze_time"]);
    expect(settingProblems({ quick_snooze_minutes: 1440 })).toEqual([]);
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

import { phonesLabel, STRINGS as REC } from "../../custom_components/heads_up/frontend/panel/recipients.js";

describe("Recipients phones", () => {
  it("counts the phones that can be reached", () => {
    const t = REC.en;
    expect(phonesLabel({ devices: [] }, t)).toBe("none");
    expect(phonesLabel({ devices: [{ service_found: true }, { service_found: false }] }, t)).toBe("1 of 2");
  });

  it("has the same keys in every language", () => sameKeys(REC));
});


describe("the Inbox row of the Channels page", () => {
  const t = CH.en;

  it("takes a retention of one to thirty-six whole months", () => {
    for (const ok of [1, 12, 36, "6"]) expect(validRetention(ok)).toBe(true);
    for (const bad of [0, 37, 1.5, "", null, NaN]) expect(validRetention(bad)).toBe(false);
    expect(problems({ push_channel_id: "heads_up", inbox_retention_months: 0 })).toContain("bad_retention");
    expect(problems({ push_channel_id: "heads_up", inbox_retention_months: 12 })).not.toContain("bad_retention");
  });

  it("words what is stored without any text", () => {
    expect(inboxLine({ items: 12, people: 2, oldest: "2026-10-01T08:00:00+00:00" }, t)).toBe("12 items for 2 people, the oldest from 2026-10-01.");
    expect(inboxLine({ items: 0, people: 0, oldest: null }, t)).toBe(t.inbox_empty);
    expect(inboxLine(null, t)).toBe(t.inbox_empty);
  });

  it("has the same texts in every language", () => {
    for (const code of ["de", "fr", "es"]) {
      for (const key of ["inbox_retention", "inbox_all", "inbox_all_note", "inbox_clear", "inbox_confirm", "bad_retention", "inbox_summary", "inbox_summary_all"]) {
        expect(CH[code][key], `${code} ${key}`).toBeTruthy();
      }
    }
  });
});
