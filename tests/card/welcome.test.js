import { describe, expect, it } from "vitest";
import {
  fill,
  ITEMS,
  payloadFor,
  resultText,
  STRINGS,
} from "../../custom_components/heads_up/frontend/panel/welcome.js";

const state = (on = {}, extra = {}) => ({
  on: { quiet: true, digest: true, critical: true, warnings: true, ...on },
  audience: "Admins",
  speakers: [],
  ...extra,
});

describe("welcome", () => {
  it("has the four defaults of the decision", () => {
    expect(ITEMS).toEqual(["quiet", "digest", "critical", "warnings"]);
  });

  it("sends only the switched-on items", () => {
    expect(payloadFor(state({ digest: false, warnings: false })).items).toEqual(["quiet", "critical"]);
    expect(payloadFor(state({ quiet: false, digest: false, critical: false, warnings: false }))).toEqual({
      type: "heads_up/welcome_apply",
      items: [],
    });
  });

  it("sends the audience and the speakers only with the critical item", () => {
    const withCritical = payloadFor(state({}, { audience: "Everyone", speakers: ["media_player.k"] }));
    expect(withCritical).toMatchObject({ audience: "Everyone", speakers: ["media_player.k"] });
    const without = payloadFor(state({ critical: false }, { audience: "Everyone", speakers: ["media_player.k"] }));
    expect(without.audience).toBeUndefined();
    expect(without.speakers).toBeUndefined();
  });

  it("does not change the state it is given", () => {
    const s = state({}, { speakers: ["a"] });
    payloadFor(s).speakers.push("b");
    expect(s.speakers).toEqual(["a"]);
  });

  it("words the result", () => {
    const t = STRINGS.en;
    expect(resultText({ added: ["Night quiet", "Evening summary"], skipped: [] }, t)).toBe("Created: Night quiet, Evening summary.");
    expect(resultText({ added: [], skipped: [{ name: "Night quiet", reason: "exists" }] }, t)).toBe(
      "Created: nothing. Already there or the same as one you have: Night quiet.",
    );
  });

  it("has the same keys and placeholders in every language and an item text for every default", () => {
    const keys = Object.keys(STRINGS.en).sort();
    const holders = (text) => (String(text).match(/\{[a-z]+\}/g) || []).sort();
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(Object.keys(language).sort(), code).toEqual(keys);
      for (const key of keys) expect(holders(language[key]), `${code}.${key}`).toEqual(holders(STRINGS.en[key]));
      for (const id of ITEMS) {
        expect(language[`item_${id}`], `${code}.item_${id}`).toBeTruthy();
        expect(language[`desc_${id}`], `${code}.desc_${id}`).toBeTruthy();
      }
    }
  });

  it("fills placeholders", () => {
    expect(fill("{a} and {b}", { a: 1, b: "x" })).toBe("1 and x");
  });
});
