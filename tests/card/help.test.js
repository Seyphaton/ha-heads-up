import { describe, expect, it } from "vitest";
import { MODULES, NAV } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import {
  CARD_EXAMPLES,
  EXAMPLES,
  ISSUES_URL,
  PAGES,
  QUESTION_IDS,
  STRINGS,
} from "../../custom_components/heads_up/frontend/panel/help.js";

describe("help pages", () => {
  it("are three pills of the help group, all rendered by the help module", () => {
    expect(NAV.find((g) => g.id === "faq").pages).toEqual(["faq", "examples", "card"]);
    expect(PAGES).toEqual(["faq", "examples", "card"]);
    for (const page of PAGES) expect(MODULES[page]).toBe("help.js");
  });

  it("have six notify examples, six card examples and 27 questions", () => {
    expect(EXAMPLES).toHaveLength(6);
    expect(CARD_EXAMPLES).toHaveLength(6);
    expect(QUESTION_IDS).toHaveLength(27);
  });

  it("link to the issues page of the repository, which the manifest names as issue tracker", () => {
    expect(ISSUES_URL).toMatch(/^https:\/\/github\.com\/[^/]+\/[^/]+\/issues$/);
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(language.issues_lead, code).toBeTruthy();
      expect(language.issues_link, code).toBeTruthy();
    }
  });

  it("start every notify example with an action of this integration", () => {
    for (const example of EXAMPLES) expect(example.yaml).toMatch(/^action: heads_up\.[a-z_]+\n/);
  });

  it("start every card example with the card type", () => {
    for (const example of CARD_EXAMPLES) expect(example.yaml).toMatch(/^type: custom:heads-up-card(\n|$)/);
  });

  it("have a title, an intro, every example text and every question in every language", () => {
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(Object.keys(language).sort(), code).toEqual(Object.keys(STRINGS.en).sort());
      for (const page of PAGES) {
        expect(language.titles[page], `${code} title ${page}`).toBeTruthy();
        expect(language.intros[page], `${code} intro ${page}`).toBeTruthy();
      }
      for (const example of EXAMPLES) {
        expect(language.ex[example.id]?.title, `${code} ${example.id}`).toBeTruthy();
        expect(language.ex[example.id]?.note, `${code} ${example.id}`).toBeTruthy();
      }
      for (const example of CARD_EXAMPLES) {
        expect(language.card_ex[example.id]?.title, `${code} ${example.id}`).toBeTruthy();
        expect(language.card_ex[example.id]?.note, `${code} ${example.id}`).toBeTruthy();
      }
      for (const id of QUESTION_IDS) {
        expect(language.q[id]?.q, `${code} ${id}`).toBeTruthy();
        expect(language.q[id]?.a, `${code} ${id}`).toBeTruthy();
      }
    }
  });
});
