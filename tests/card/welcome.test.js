import { describe, expect, it } from "vitest";
import {
  audienceMembers,
  audienceNote,
  BUILTIN_AUDIENCES,
  channelChanges,
  channelStatus,
  createLabel,
  fill,
  ITEM_LANES,
  ITEMS,
  payloadFor,
  policyCount,
  resultText,
  setupSummary,
  STEPS,
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
    expect(ITEMS).toEqual(["critical", "warnings", "digest", "quiet"]);
  });

  it("sends only the switched-on items", () => {
    expect(payloadFor(state({ digest: false, warnings: false })).items).toEqual(["critical", "quiet"]);
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

  it("sends the chosen text-to-speech engine only when one is chosen", () => {
    expect(payloadFor(state({}, { ttsEngine: "tts.cloud" })).tts_engine).toBe("tts.cloud");
    expect(payloadFor(state({}, { ttsEngine: "" })).tts_engine).toBeUndefined();
  });

  it("has the engine texts in every language", () => {
    for (const [code, language] of Object.entries(STRINGS)) {
      for (const key of ["tts_engine", "tts_choose", "tts_none"]) expect(language[key], `${code} ${key}`).toBeTruthy();
    }
  });

  it("sends no mode: every policy that fits acts (DESIGN §25.9)", () => {
    const payload = payloadFor(state({}, { speakers: ["media_player.k"] }));
    expect(payload.mode).toBeUndefined();
    expect(payload.speakers).toEqual(["media_player.k"]);
  });

  it("has the item texts in every language and no mode texts", () => {
    for (const [code, language] of Object.entries(STRINGS)) {
      for (const id of ITEMS) expect(language[`desc_${id}`], `${code} ${id}`).toBeTruthy();
      expect(language.mode_title, code).toBeUndefined();
    }
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

  it("is a tour of four steps: introduction, channels, audiences, policies", () => {
    expect(STEPS).toEqual(["intro", "channels", "audiences", "policies"]);
    for (const [code, language] of Object.entries(STRINGS)) {
      for (const key of ["intro_title", "channels_title", "recipients_title", "policies_title", "intro_lead", "intro_foot"]) {
        expect(language[key], `${code}.${key}`).toBeTruthy();
      }
      // Each box of step 1 starts with the key word of its page.
      for (const key of ["where", "who", "when"]) expect(language[`intro_${key}_text`], `${code}.${key}`).toBeTruthy();
    }
    expect(STRINGS.en.intro_where_text.startsWith("Channels decide where")).toBe(true);
    expect(STRINGS.en.intro_who_text.startsWith("Audiences decide who")).toBe(true);
    expect(STRINGS.en.intro_when_text.startsWith("Policies decide when")).toBe(true);
  });

  it("has a name, a meaning and an example for each of the six audiences in every language", () => {
    expect(BUILTIN_AUDIENCES).toEqual(["everyone", "admins", "at_home", "not_home", "last_to_leave", "first_home"]);
    for (const [code, language] of Object.entries(STRINGS)) {
      for (const key of BUILTIN_AUDIENCES) for (const prefix of ["aud_", "aud_what_", "aud_example_"]) expect(language[prefix + key], `${code}.${prefix}${key}`).toBeTruthy();
    }
  });

  const config = {
    profiles: [{ devices: [{}, {}] }, { devices: [{}] }, { devices: [] }],
    choices: { persons: [{}, {}, {}], speakers: ["media_player.a"] },
  };

  it("counts what the tour shows from the panel config", () => {
    expect(setupSummary(config)).toEqual({ persons: 3, devices: 3, speakers: 1 });
    expect(setupSummary(null)).toBeNull();
  });

  it("words what was found per channel and shows nothing without numbers", () => {
    const t = STRINGS.en;
    const summary = setupSummary(config);
    expect(channelStatus("push", summary, t)).toBe("App devices found: 3");
    expect(channelStatus("speak", { ...summary, speakers: 0 }, t)).toBe("Speakers and satellites found: none yet");
    expect(channelStatus("mail", summary, t)).toBe("");
    expect(channelStatus("banner", summary, t)).toBe("");
    expect(channelStatus("push", null, t)).toBe("");
  });

  it("counts the policies Create makes: Critical three, four with speakers", () => {
    const on = (extra) => ({ on: { critical: true, warnings: true, digest: true, quiet: true, ...extra }, speakers: [] });
    expect(policyCount(on())).toBe(6);
    expect(policyCount({ ...on(), speakers: ["media_player.k"] })).toBe(7);
    expect(policyCount(on({ critical: false }))).toBe(3);
    expect(policyCount(on({ critical: false, warnings: false, digest: false, quiet: false }))).toBe(0);
    expect(createLabel(1, STRINGS.en)).toBe("Create 1 policy");
    expect(createLabel(6, STRINGS.en)).toBe("Create 6 policies");
  });

  it("puts each default in its group, Critical in two", () => {
    expect(ITEM_LANES).toEqual({ critical: ["through", "arrive"], warnings: ["arrive"], digest: ["calm"], quiet: ["calm"] });
  });

  const saved = { mailService: "", mailAddress: "", ttsEngine: "", inboxAll: false };

  it("saves nothing when step 2 was left untouched", () => {
    expect(channelChanges({ ...saved }, saved)).toEqual([]);
  });

  it("saves only the mail fields that changed, through channels_set", () => {
    expect(channelChanges({ ...saved, mailService: "smtp_house" }, saved)).toEqual([{ type: "heads_up/channels_set", mail_service: "smtp_house" }]);
    expect(channelChanges({ ...saved, mailService: "smtp_house", mailAddress: "a@example.com" }, saved)).toEqual([
      { type: "heads_up/channels_set", mail_service: "smtp_house", mail_global_address: "a@example.com" },
    ]);
  });

  it("saves the All notifications switch of the inbox through channels_set, on and off", () => {
    expect(channelChanges({ ...saved, inboxAll: true }, saved)).toEqual([{ type: "heads_up/channels_set", inbox_all_notifications: true }]);
    expect(channelChanges({ ...saved }, { ...saved, inboxAll: true })).toEqual([{ type: "heads_up/channels_set", inbox_all_notifications: false }]);
  });

  it("puts the inbox among the channels the tour shows, with words in every language", () => {
    for (const code of ["en", "de", "fr", "es"]) {
      expect(STRINGS[code].ch_inbox, code).toBeTruthy();
      expect(STRINGS[code].inbox_all, code).toBeTruthy();
      expect(STRINGS[code].inbox_hint, code).toBeTruthy();
    }
  });

  it("saves the speech engine through settings_set, and clears it with an empty value", () => {
    expect(channelChanges({ ...saved, ttsEngine: "tts.cloud" }, saved)).toEqual([{ type: "heads_up/settings_set", speak_tts_entity: "tts.cloud" }]);
    expect(channelChanges({ ...saved }, { ...saved, ttsEngine: "tts.cloud" })).toEqual([{ type: "heads_up/settings_set", speak_tts_entity: "" }]);
  });

  it("writes the note of Last to leave and First home from the stored time", () => {
    const t = STRINGS.en;
    expect(audienceNote({ key: "last_to_leave", at: null }, t, "en")).toBe("");
    expect(audienceNote({ key: "last_to_leave", at: "2026-11-02T17:40:00Z" }, t, "en")).toMatch(/^Left at /);
    expect(audienceNote({ key: "first_home", at: "2026-11-03T07:12:00Z" }, t, "en")).toMatch(/^Arrived at /);
  });

  it("names the people of an audience with their home mark", () => {
    const people = [{ person: "person.a", name: "Anna", home: true }, { person: "person.b", name: "Ben", home: false }];
    expect(audienceMembers({ members: [{ person: "person.a" }, { person: "person.b" }, { person: "person.c" }] }, people)).toEqual([
      { name: "Anna", home: true },
      { name: "Ben", home: false },
      { name: "person.c", home: false },
    ]);
  });
});
