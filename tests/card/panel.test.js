import { describe, expect, it } from "vitest";
import {
  BASE_PATH,
  DEFAULT_PAGE,
  groupOf,
  MODULES,
  moduleUrl,
  NAV,
  pageFromPath,
  pageUrl,
  secondRow,
  STRINGS,
  table,
} from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import {
  changes,
  devicesLabel,
  fill,
  problems,
  STRINGS as SETTINGS_STRINGS,
} from "../../custom_components/heads_up/frontend/panel/settings.js";

describe("panel navigation", () => {
  it("has the five groups of the specification in order", () => {
    expect(NAV.map((g) => g.id)).toEqual(["overview", "notifications", "configuration", "settings", "faq"]);
  });

  it("finds the group of a page", () => {
    expect(groupOf("audiences").id).toBe("configuration");
    expect(groupOf("general").id).toBe("settings");
    expect(groupOf("nope")).toBeNull();
  });

  it("opens the page named in the path and falls back to the first page", () => {
    expect(pageFromPath("/policies")).toBe("policies");
    expect(pageFromPath("/policies/extra")).toBe("policies");
    expect(pageFromPath("")).toBe(DEFAULT_PAGE);
    expect(pageFromPath("/unknown")).toBe(DEFAULT_PAGE);
    expect(pageFromPath(undefined)).toBe(DEFAULT_PAGE);
  });

  it("shows a second row only for a group with more than one page", () => {
    expect(secondRow("audiences")).toEqual(["audiences", "recipients", "policies", "channels"]);
    expect(secondRow("test")).toEqual(["test", "rules", "messages"]);
    expect(secondRow("general")).toEqual([]);
    expect(secondRow("status")).toEqual([]);
    expect(secondRow("faq")).toEqual([]);
  });

  it("builds page and module URLs", () => {
    expect(pageUrl("general")).toBe(`${BASE_PATH}/general`);
    expect(moduleUrl("/heads_up/panel", "0.4.0-abcd1234", "settings.js")).toBe(
      "/heads_up/panel/settings.js?v=0.4.0-abcd1234",
    );
  });

  it("every module belongs to a page that exists", () => {
    for (const page of Object.keys(MODULES)) expect(groupOf(page)).not.toBeNull();
  });
});

describe("panel texts", () => {
  it("has a label for every group and page in every language", () => {
    const groups = NAV.map((g) => g.id).sort();
    const pages = NAV.flatMap((g) => g.pages).sort();
    for (const language of Object.values(STRINGS)) {
      expect(Object.keys(language.groups).sort()).toEqual(groups);
      expect(Object.keys(language.pages).sort()).toEqual(pages);
    }
  });

  it("has the same keys in every language", () => {
    for (const strings of [STRINGS, SETTINGS_STRINGS]) {
      const keys = Object.keys(strings.en).sort();
      for (const language of Object.values(strings)) expect(Object.keys(language).sort()).toEqual(keys);
    }
  });

  it("keeps the placeholders of every translation", () => {
    const holders = (text) => (String(text).match(/\{[a-z]+\}/g) || []).sort();
    for (const [key, text] of Object.entries(SETTINGS_STRINGS.en)) {
      for (const language of Object.values(SETTINGS_STRINGS)) expect(holders(language[key])).toEqual(holders(text));
    }
  });

  it("falls back to English for a missing language or key", () => {
    expect(table(STRINGS, "de").title).toBe("Heads Up");
    expect(table(STRINGS, "de-AT").menu).toBe("Seitenleiste öffnen");
    expect(table(STRINGS, "xx").menu).toBe("Open the sidebar");
    expect(table({ en: { a: "A" }, de: {} }, "de").a).toBe("A");
  });
});

describe("settings page functions", () => {
  const ranges = {
    rate_per_device_per_minute: [1, 600],
    rate_total_per_minute: [1, 6000],
    dedupe_seconds: [0, 3600],
    trace_entries: [50, 5000],
    recent_messages: [10, 1000],
  };
  const saved = {
    hub_enabled: true,
    show_panel: false,
    rate_per_device_per_minute: 10,
    rate_total_per_minute: 60,
    dedupe_seconds: 30,
    trace_entries: 500,
    recent_messages: 100,
  };

  it("finds no problem in the saved values", () => {
    expect(problems(saved, ranges)).toEqual([]);
  });

  it("reports a value outside its range, a fraction or an empty field", () => {
    const bad = { ...saved, trace_entries: 10, dedupe_seconds: 1.5, recent_messages: NaN };
    expect(problems(bad, ranges).map((p) => p.key).sort()).toEqual(["dedupe_seconds", "recent_messages", "trace_entries"]);
    expect(problems({ ...saved, dedupe_seconds: 0 }, ranges)).toEqual([]);
  });

  it("sends only what changed", () => {
    expect(changes(saved, saved)).toEqual({});
    expect(changes({ ...saved, show_panel: true, trace_entries: 600 }, saved)).toEqual({
      show_panel: true,
      trace_entries: 600,
    });
  });

  it("words the devices of a person", () => {
    const t = SETTINGS_STRINGS.en;
    expect(devicesLabel({ devices: 0, devices_total: 0 }, t)).toBe("none: only banner and popup work");
    expect(devicesLabel({ devices: 1, devices_total: 2 }, t)).toBe("1 of 2 usable");
  });

  it("fills placeholders", () => {
    expect(fill("{n} of {total}", { n: 1, total: 2 })).toBe("1 of 2");
  });
});
