import { describe, expect, it } from "vitest";
import { MODULES } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import { EXAMPLES, QUESTION_IDS, STRINGS } from "../../custom_components/heads_up/frontend/panel/help.js";

describe("faq and examples page", () => {
  it("is the module of the faq page", () => {
    expect(MODULES.faq).toBe("help.js");
  });

  it("has six examples and eleven questions", () => {
    expect(EXAMPLES).toHaveLength(6);
    expect(QUESTION_IDS).toHaveLength(11);
  });

  it("starts every example with an action of this integration", () => {
    for (const example of EXAMPLES) expect(example.yaml).toMatch(/^action: heads_up\.[a-z_]+\n/);
  });

  it("has a title and a note for every example and a text for every question in every language", () => {
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(Object.keys(language).sort(), code).toEqual(Object.keys(STRINGS.en).sort());
      for (const example of EXAMPLES) {
        expect(language.ex[example.id]?.title, `${code} ${example.id}`).toBeTruthy();
        expect(language.ex[example.id]?.note, `${code} ${example.id}`).toBeTruthy();
      }
      for (const id of QUESTION_IDS) {
        expect(language.q[id]?.q, `${code} ${id}`).toBeTruthy();
        expect(language.q[id]?.a, `${code} ${id}`).toBeTruthy();
      }
    }
  });
});
