import { describe, expect, it } from "vitest";
import {
  blankValues as blankAudience,
  describe as describeAudience,
  fromAudience,
  STRINGS as AUDIENCE_STRINGS,
  toFlowData as audienceData,
  validate as validateAudience,
} from "../../custom_components/heads_up/frontend/panel/audiences.js";
import {
  addDevice,
  channelState,
  PROFILE_CHANNELS,
  groupData,
  isDefault,
  profileValues,
  removeDevice,
  restoreDevice,
  STRINGS as RECIPIENT_STRINGS,
  toProfileData,
  validateGroup,
} from "../../custom_components/heads_up/frontend/panel/recipients.js";
import {
  appliesText,
  blankValues as blankPolicy,
  dropItem,
  moveItem,
  overlapNames,
  shadowedBy,
  overlaps,
  fromPolicy,
  sentence,
  splitTags as policyTags,
  STRINGS as POLICY_STRINGS,
  toFlowData as policyData,
  validate as validatePolicy,
} from "../../custom_components/heads_up/frontend/panel/policies.js";
import {
  changes as channelChanges,
  problems as channelProblems,
  STRINGS as CHANNEL_STRINGS,
  validChannelId,
  validMailTemplate,
} from "../../custom_components/heads_up/frontend/panel/channels.js";
import { errorText, ERRORS, joinTags, parseRich, splitTags, toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

describe("yaml of stored data", () => {
  it("writes nested maps, lists and scalars", () => {
    const yaml = toYaml({ name: "Water", type: "escalation", after_minutes: 5, enabled: true, channels: ["push"], targets: { push: { audience: "Admins" } }, severities: [], note: null });
    expect(yaml).toBe(
      ["name: Water", "type: escalation", "after_minutes: 5", "enabled: true", "channels:", "  - push", "targets:", "  push:", "    audience: Admins", "severities: []", "note: null"].join("\n"),
    );
  });

  it("quotes strings that would be read as something else", () => {
    expect(toYaml({ a: "22:00:00", b: "true", c: "123", d: "a: b", e: "", f: "Water leak" })).toBe(
      'a: "22:00:00"\nb: "true"\nc: "123"\nd: "a: b"\ne: ""\nf: Water leak',
    );
  });
});

describe("tags", () => {
  it("splits, trims and removes duplicates", () => {
    expect(splitTags(" water, door ,water,, ")).toEqual(["water", "door"]);
    expect(splitTags("")).toEqual([]);
    expect(policyTags("a,b")).toEqual(["a", "b"]);
    expect(joinTags(["a", "b"])).toBe("a, b");
  });
});

describe("flow errors", () => {
  it("are worded in the language and fall back to English and to the code", () => {
    expect(errorText("name_required", "de")).toBe("Gib einen Namen ein.");
    expect(errorText("name_required", "xx")).toBe("Enter a name.");
    expect(errorText("something_else", "en")).toBe("something_else");
  });

  it("have the same keys in every language", () => {
    const keys = Object.keys(ERRORS.en).sort();
    for (const table of Object.values(ERRORS)) expect(Object.keys(table).sort()).toEqual(keys);
  });

  it("cover every error key the integration's forms return", () => {
    const flowKeys = ["name_required", "name_exists", "persons_required", "presence_required", "zone_required", "name_has_suffix", "group_empty", "member_not_found", "area_not_found", "person_not_found", "profile_exists", "device_unknown", "device_added_and_removed", "channels_required", "after_required", "channel_unknown", "every_required", "max_required", "window_empty", "time_invalid", "wait_invalid", "when_required", "target_exclusive", "audience_unknown", "recipient_unknown", "policy_duplicate"];
    for (const key of flowKeys) expect(ERRORS.en[key], key).toBeTruthy();
  });
});

describe("audience editor", () => {
  const names = ["Parents", "Kids"];

  it("needs a unique name and at least one person", () => {
    expect(validateAudience(blankAudience(), names)).toEqual({ name: "name_required", persons: "persons_required" });
    expect(validateAudience({ ...blankAudience(), name: "parents", persons: ["person.a"] }, names)).toEqual({ name: "name_exists" });
    expect(validateAudience({ ...blankAudience(), name: "Parents", persons: ["person.a"] }, names, "Parents")).toEqual({});
  });

  it("needs a zone for the zone kinds", () => {
    const values = { ...blankAudience(), name: "Work", kind: "presence", presence: "in_zone", zone: "" };
    expect(validateAudience(values, names)).toEqual({ zone: "zone_required" });
    expect(validateAudience({ ...values, zone: "zone.work" }, names)).toEqual({});
  });

  it("sends only the fields of its kind", () => {
    expect(audienceData({ ...blankAudience(), name: " P ", persons: ["person.a"], presence: "in_zone", zone: "zone.x" })).toEqual({ name: "P", kind: "persons", persons: ["person.a"] });
    expect(audienceData({ ...blankAudience(), name: "Z", kind: "presence", presence: "at_home", zone: "zone.x" })).toEqual({ name: "Z", kind: "presence", presence: "at_home" });
    expect(audienceData({ ...blankAudience(), name: "Z", kind: "presence", presence: "not_in_zone", zone: "zone.x" })).toEqual({ name: "Z", kind: "presence", presence: "not_in_zone", zone: "zone.x" });
  });

  it("reads a stored audience back into the form and describes it", () => {
    const stored = { name: "Parents", data: { kind: "persons", persons: ["person.a"] } };
    expect(fromAudience(stored)).toMatchObject({ name: "Parents", kind: "persons", persons: ["person.a"] });
    const choices = { persons: [{ id: "person.a", name: "Anna" }], zones: [{ id: "zone.work", name: "Work" }] };
    expect(describeAudience(fromAudience(stored), choices, AUDIENCE_STRINGS.en)).toBe("Anna (a fixed list).");
    const zone = { name: "W", data: { kind: "presence", presence: "in_zone", zone: "zone.work" } };
    expect(describeAudience(fromAudience(zone), choices, AUDIENCE_STRINGS.en)).toBe("People who are: In a zone (Work).");
  });
});

describe("recipient editor", () => {
  const profile = {
    person: "person.anna",
    primary: "",
    channels: ["banner", "push", "popup"],
    removed: [],
    devices: [
      { device_id: "d1", name: "Phone", service_found: true, source: "detected" },
      { device_id: "d2", name: "Tablet", service_found: true, source: "manual" },
    ],
  };

  it("starts from what the profile changes", () => {
    expect(profileValues(profile)).toEqual({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup"], mail_address: "", enabled: true });
  });

  it("needs no stored profile when nothing differs from the detected devices", () => {
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup"] })).toBe(true);
    expect(isDefault({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "d1", channels: ["banner", "push", "popup"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "mail"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup"], mail_address: "a@b.c" })).toBe(false);
  });

  it("builds the flow data, with the person only when creating", () => {
    const values = { manual: ["d2"], removed: ["d9"], primary: "d1", channels: ["popup", "banner"] };
    expect(toProfileData("person.anna", values, true)).toEqual({ person: "person.anna", channels: ["banner", "popup"], devices: ["d2"], removed_devices: ["d9"], primary: "d1" });
    expect(toProfileData("person.anna", { manual: [], removed: [], primary: "", channels: ["push"] }, false)).toEqual({ channels: ["push"] });
    expect(toProfileData("person.anna", { manual: [], removed: [], primary: "", channels: ["mail", "push"], mail_address: " anna@example.com " }, false)).toEqual({ channels: ["push", "mail"], mail_address: "anna@example.com" });
  });

  it("removes a detected device (and drops it as primary), drops an added one, and restores", () => {
    const start = { manual: ["d2"], removed: [], primary: "d1", channels: ["push"] };
    const removed = removeDevice(start, "d1", "detected");
    expect(removed.removed).toEqual(["d1"]);
    expect(removed.primary).toBe("");
    expect(removeDevice(start, "d2", "manual").manual).toEqual([]);
    expect(restoreDevice(removed, "d1").removed).toEqual([]);
    expect(start.manual).toEqual(["d2"]);
  });

  it("adds a device once and un-removes it", () => {
    const values = { manual: [], removed: ["d1"], primary: "", channels: ["push"] };
    expect(addDevice(values, "d1")).toMatchObject({ manual: ["d1"], removed: [] });
    expect(addDevice({ ...values, manual: ["d1"] }, "d1").manual).toEqual(["d1"]);
    expect(addDevice(values, "")).toBe(values);
  });

  it("checks a group", () => {
    expect(validateGroup({ name: "", members: [], areas: [] }, [])).toEqual({ name: "name_required", members: "group_empty" });
    expect(validateGroup({ name: "Hall (group)", members: ["x"], areas: [] }, [])).toEqual({ name: "name_has_suffix" });
    expect(validateGroup({ name: "hall", members: ["x"], areas: [] }, ["Hall"])).toEqual({ name: "name_exists" });
    expect(validateGroup({ name: "Hall", members: [], areas: ["a"] }, ["Hall"], "Hall")).toEqual({});
    expect(groupData({ name: " Hall ", members: ["m"], areas: ["a"] })).toEqual({ name: "Hall", members: ["m"], areas: ["a"] });
  });
});

describe("policy editor", () => {
  const water = {
    ...blankPolicy("escalation"),
    name: "Water",
    severities: ["critical"],
    tags: "water",
    channels: ["push", "persistent"],
    push_audience: "Admins",
  };

  it("sends only the fields of the type and the targets of the chosen channels", () => {
    expect(policyData(water)).toEqual({
      name: "Water",
      type: "escalation",
      apply: "auto",
      severities: ["critical"],
      tags: ["water"],
      enabled: true,
      after_minutes: 5,
      channels: ["push", "persistent"],
      dismiss_acks: false,
      push_audience: "Admins",
    });
    const popupLeft = { ...water, channels: ["push"], popup_audience: "Everyone" };
    expect(policyData(popupLeft).popup_audience).toBeUndefined();
  });

  it("sends the fields of each other type", () => {
    expect(policyData({ ...blankPolicy("reminder"), name: "Nag", channels: [] })).toMatchObject({ every_minutes: 30, max_count: 3, channels: [] });
    expect(policyData({ ...blankPolicy("away"), name: "Back" })).toMatchObject({ max_wait: 0, critical_passes: true });
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).toMatchObject({ from_time: "22:00:00", to_time: "07:00:00", days: [], action: "quiet", critical_passes: true });
    expect(policyData({ ...blankPolicy("away"), name: "Back", max_wait: 0 })).toMatchObject({ max_wait: 0 });
    expect(policyData({ ...blankPolicy("fallback"), name: "Backup", channels: ["speak"], speak_recipients: ["media_player.k"] })).toMatchObject({ when: "no_audience", channels: ["speak"], speak_recipients: ["media_player.k"] });
    expect(policyData({ ...blankPolicy("deliver"), name: "Crit", severities: ["critical"], channels: ["push"], push_audience: "Admins" })).toEqual({
      name: "Crit", type: "deliver", apply: "auto", severities: ["critical"], tags: [], enabled: true, channels: ["push"], push_audience: "Admins",
    });
    const every = policyData({ ...blankPolicy("summarize"), name: "Digest" });
    expect(every).toMatchObject({ summary_every: 60, include_critical: false });
    expect(every.summary_at).toBeUndefined();
    const at = policyData({ ...blankPolicy("summarize"), name: "Evening", summary_mode: "at" });
    expect(at.summary_at).toBe("20:00:00");
    expect(at.summary_every).toBeUndefined();
  });

  it("validates like the form does", () => {
    const base = blankPolicy("escalation");
    expect(validatePolicy({ ...base, name: "", channels: [] }, [])).toEqual({ name: "name_required", channels: "channels_required" });
    expect(validatePolicy({ ...base, name: "None", channels: ["push"], push_audience: "A" }, [])).toEqual({ name: "name_exists" });
    expect(validatePolicy({ ...base, name: "X", after_minutes: 0, channels: ["push"], push_audience: "A" }, [])).toEqual({ after_minutes: "after_required" });
    expect(validatePolicy({ ...base, name: "X", channels: ["push"] }, [])).toEqual({ push_target: "target_exclusive" });
    expect(validatePolicy({ ...base, name: "X", channels: ["speak"], speak_recipients: [] }, [])).toEqual({ speak_target: "target_exclusive" });
    expect(validatePolicy({ ...base, name: "X", channels: ["push"], push_audience: "A", push_recipients: ["p"] }, [])).toEqual({ push_target: "target_exclusive" });
    expect(validatePolicy({ ...base, name: "X", channels: ["persistent"] }, [])).toEqual({});
    expect(validatePolicy({ ...blankPolicy("reminder"), name: "R", every_minutes: 0, max_count: 0 }, [])).toEqual({ every_minutes: "every_required", max_count: "max_required" });
    expect(validatePolicy({ ...blankPolicy("quiet_hours"), name: "Q", from_time: "08:00:00", to_time: "08:00:00" }, [])).toEqual({ to_time: "window_empty" });
    expect(validatePolicy({ ...blankPolicy("summarize"), name: "S", summary_every: 0 }, [])).toEqual({ summary_every: "every_required" });
    expect(validatePolicy({ ...blankPolicy("summarize"), name: "S", summary_mode: "at", summary_at: "" }, [])).toEqual({ summary_at: "time_invalid" });
    expect(validatePolicy({ ...blankPolicy("fallback"), name: "F", channels: [] }, [])).toEqual({ channels: "channels_required" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: [] }, [])).toEqual({ channels: "channels_required" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: ["push"] }, [])).toEqual({ push_target: "target_exclusive" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: ["push"], push_audience: "Admins" }, [])).toEqual({});
    expect(validatePolicy({ ...blankPolicy("away"), name: "A", max_wait: -1 }, [])).toEqual({ max_wait: "wait_invalid" });
    expect(validatePolicy({ ...blankPolicy("away"), name: "water" }, ["Water"], "Water")).toEqual({});
    expect(validatePolicy({ ...blankPolicy("away"), name: "water" }, ["Water"])).toEqual({ name: "name_exists" });
  });

  it("reads a stored policy back into the form", () => {
    const stored = { name: "Water", data: { type: "escalation", severities: ["critical"], tags: ["water", "leak"], enabled: false, after_minutes: 9, channels: ["push", "speak"], dismiss_acks: true, targets: { push: { audience: "Admins" }, speak: { recipients: ["media_player.k"] } } } };
    expect(fromPolicy(stored)).toMatchObject({
      name: "Water", type: "escalation", severities: ["critical"], tags: "water, leak", enabled: false, after_minutes: 9, dismiss_acks: true,
      push_audience: "Admins", speak_recipients: ["media_player.k"],
    });
    const digest = fromPolicy({ name: "D", data: { type: "summarize", summary_at: "19:30:00", include_critical: true } });
    expect(digest).toMatchObject({ summary_mode: "at", summary_at: "19:30:00", include_critical: true });
  });

  it("describes a policy in plain words", () => {
    const t = POLICY_STRINGS.en;
    expect(appliesText(blankPolicy("away"), t)).toBe("Every message");
    expect(appliesText({ ...blankPolicy("away"), severities: ["critical", "warning"], tags: "water" }, t)).toBe("Messages with severity Critical, Warning and tag water");
    expect(appliesText({ ...blankPolicy("away"), tags: "smoke_never" }, t)).toBe("Messages with tag smoke_never");
    expect(appliesText({ ...blankPolicy("away"), severities: ["info"] }, t)).toBe("Messages with severity Info");
    expect(sentence(water, t)).toBe("Messages with severity Critical and tag water: if nobody acknowledges within 5 min, it is also sent on Push, Persistent Notification.");
    expect(sentence({ ...blankPolicy("quiet_hours"), days: ["sat", "sun"] }, t)).toBe("Every message: between 22:00 and 07:00 on Saturday, Sunday, deliveries outside the dashboard are sent quietly, critical messages pass.");
    expect(sentence({ ...blankPolicy("reminder"), channels: ["push"] }, t)).toBe("Every message: while nobody acknowledges, the notification is repeated every 30 min, at most 3 times, only on Push.");
    expect(sentence({ ...blankPolicy("away"), max_wait: 30 }, t)).toBe("Every message: a person who is not home gets it when they arrive, for at most 30 min, critical messages pass.");
    expect(sentence({ ...blankPolicy("away"), critical_passes: false }, t)).toBe("Every message: a person who is not home gets it when they arrive.");
    expect(sentence({ ...blankPolicy("fallback"), when: "both", channels: ["persistent"] }, t)).toBe("Every message: if the audience is empty or delivery fails, it is sent on Persistent Notification instead.");
    expect(sentence({ ...blankPolicy("deliver"), severities: ["critical"], channels: ["push"] }, t)).toBe("Messages with severity Critical: it is also sent at once on Push.");
    expect(sentence({ ...blankPolicy("summarize"), include_critical: true }, t)).toBe("Every message: held, and one summary is sent 60 min after the first held message, critical messages included.");
    expect(sentence({ ...blankPolicy("summarize"), summary_mode: "at" }, t)).toBe("Every message: held, and one summary is sent every day at 20:00.");
  });
});

describe("channel settings", () => {
  const saved = { push_levels: { info: "passive" }, popup_styles: { critical: "modal" }, push_lockscreen: "full", push_sticky: false, push_channel_id: "heads_up", speak_language: "" };

  it("sends only what changed, comparing maps by value", () => {
    expect(channelChanges(JSON.parse(JSON.stringify(saved)), saved)).toEqual({});
    const edited = JSON.parse(JSON.stringify(saved));
    edited.push_levels.info = "normal";
    edited.push_sticky = true;
    expect(channelChanges(edited, saved)).toEqual({ push_levels: { info: "normal" }, push_sticky: true });
  });

  it("accepts a channel name of lower-case letters, digits and underscores", () => {
    expect(validChannelId("heads_up")).toBe(true);
    expect(validChannelId("Heads Up")).toBe(false);
    expect(validChannelId("")).toBe(false);
    expect(validChannelId("a".repeat(41))).toBe(false);
    expect(channelProblems({ push_channel_id: "bad name" })).toEqual(["bad_channel_id"]);
    expect(channelProblems({ push_channel_id: "ok" })).toEqual([]);
  });
});

describe("editor texts", () => {
  const leaves = (object, path = "") =>
    Object.entries(object).flatMap(([key, value]) =>
      typeof value === "object" && value !== null ? leaves(value, `${path}${key}.`) : [`${path}${key}`],
    );

  it("have the same keys in every language", () => {
    for (const strings of [AUDIENCE_STRINGS, RECIPIENT_STRINGS, POLICY_STRINGS, CHANNEL_STRINGS]) {
      const keys = leaves(strings.en).sort();
      for (const [code, language] of Object.entries(strings)) expect(leaves(language).sort(), code).toEqual(keys);
    }
  });

  it("keep the placeholders of every translation", () => {
    const holders = (text) => (String(text).match(/\{[a-z]+\}/g) || []).sort();
    for (const strings of [AUDIENCE_STRINGS, RECIPIENT_STRINGS, POLICY_STRINGS, CHANNEL_STRINGS]) {
      const flat = (object) => Object.fromEntries(leaves(object).map((path) => [path, path.split(".").reduce((o, k) => o[k], object)]));
      const english = flat(strings.en);
      for (const language of Object.values(strings)) {
        const own = flat(language);
        for (const key of Object.keys(english)) expect(holders(own[key]), key).toEqual(holders(english[key]));
      }
    }
  });
});

describe("mail settings", () => {
  it("accepts the known placeholders and refuses anything else", () => {
    expect(validMailTemplate("{severity}: {title}", 200)).toBe(true);
    expect(validMailTemplate("{message}", 2000)).toBe(true);
    expect(validMailTemplate("{who}", 200)).toBe(false);
    expect(validMailTemplate("{}", 200)).toBe(false);
    expect(validMailTemplate("   ", 200)).toBe(false);
    expect(validMailTemplate("x".repeat(201), 200)).toBe(false);
    expect(validMailTemplate("plain text", 200)).toBe(true);
  });

  it("reports a bad subject, body or address", () => {
    const ok = { push_channel_id: "heads_up", mail_subject: "{title}", mail_body: "{message}", mail_global_address: "" };
    expect(channelProblems(ok)).toEqual([]);
    expect(channelProblems({ ...ok, mail_subject: "{x}" })).toEqual(["bad_mail_subject"]);
    expect(channelProblems({ ...ok, mail_body: "" })).toEqual(["bad_mail_body"]);
    expect(channelProblems({ ...ok, mail_global_address: "a".repeat(255) })).toEqual(["bad_mail_address"]);
  });

  it("has the mail texts in every language", () => {
    for (const language of ["en", "de", "fr", "es"]) {
      for (const key of ["mail", "mail_service", "mail_global_address", "mail_subject", "mail_body", "mail_placeholders", "bad_mail_subject", "bad_mail_body", "bad_mail_address"]) {
        expect(CHANNEL_STRINGS[language][key], `${language}.${key}`).toBeTruthy();
      }
    }
  });
});

describe("audience limit", () => {
  it("sends and reads the limit of a presence audience", () => {
    const values = { ...blankAudience(), name: "Anna home", kind: "presence", presence: "at_home", limit: ["person.anna"] };
    expect(audienceData(values)).toEqual({ name: "Anna home", kind: "presence", presence: "at_home", limit: ["person.anna"] });
    expect(audienceData({ ...values, limit: [] }).limit).toBeUndefined();
    expect(audienceData({ ...values, kind: "persons", persons: ["person.a"] }).limit).toBeUndefined();
    expect(fromAudience({ name: "Anna home", data: { kind: "presence", presence: "at_home", limit: ["person.anna"] } }).limit).toEqual(["person.anna"]);
    expect(fromAudience({ name: "P", data: { kind: "persons", persons: ["person.a"] } }).limit).toEqual([]);
  });
});


describe("long texts with paragraphs and bullets", () => {
  it("splits paragraphs at a blank line and collects bullets into one list", () => {
    expect(parseRich("First line.\nSecond line.\n\nWithout the panel you cannot use:\n- Test send\n- the Message Log\n\nThe rest.")).toEqual([
      { type: "p", text: "First line. Second line." },
      { type: "p", text: "Without the panel you cannot use:" },
      { type: "ul", items: ["Test send", "the Message Log"] },
      { type: "p", text: "The rest." },
    ]);
  });

  it("starts a new list after a paragraph and treats a plain text as one paragraph", () => {
    expect(parseRich("- a\nText\n- b")).toEqual([
      { type: "ul", items: ["a"] },
      { type: "p", text: "Text" },
      { type: "ul", items: ["b"] },
    ]);
    expect(parseRich("Only one sentence.")).toEqual([{ type: "p", text: "Only one sentence." }]);
    expect(parseRich("")).toEqual([]);
    expect(parseRich(undefined)).toEqual([]);
  });

  it("keeps markup as text", () => {
    expect(parseRich("- <b>x</b>")).toEqual([{ type: "ul", items: ["<b>x</b>"] }]);
  });
});

describe("manual and automatic policies", () => {
  const manual = { ...blankPolicy("escalation"), name: "By hand", apply: "manual", severities: ["critical"], tags: "water", channels: ["push"], push_audience: "Admins" };

  it("keeps no conditions for a manual policy", () => {
    const data = policyData(manual);
    expect(data.apply).toBe("manual");
    expect(data.severities).toEqual([]);
    expect(data.tags).toEqual([]);
    expect(policyData({ ...manual, apply: "auto" }).severities).toEqual(["critical"]);
  });

  it("reads the choice back from a stored policy and defaults to automatic", () => {
    expect(fromPolicy({ name: "A", data: { type: "away", apply: "manual" } }).apply).toBe("manual");
    expect(fromPolicy({ name: "A", data: { type: "away" } }).apply).toBe("auto");
  });

  it("says in words that a manual policy applies to the calls that name it", () => {
    const t = POLICY_STRINGS.en;
    expect(appliesText(manual, t)).toBe("Calls that name this policy");
    expect(sentence(manual, t)).toContain("Calls that name this policy");
  });

  it("has the headings of the two blocks, the type texts and the choice texts in every language", () => {
    for (const [code, language] of Object.entries(POLICY_STRINGS)) {
      for (const key of ["enabled_hint", "sec_when", "sec_does", "apply_label", "apply_auto", "apply_auto_hint", "apply_manual", "apply_manual_hint", "manual_how", "manual_note", "badge_manual", "s_applies_manual"]) {
        expect(language[key], `${code} ${key}`).toBeTruthy();
      }
      for (const type of Object.keys(language.types)) expect(language.type_desc[type], `${code} ${type}`).toBeTruthy();
    }
  });
});

describe("the policy list order and the overlap note", () => {
  it("moves a policy up or down and leaves the ends alone", () => {
    expect(moveItem(["a", "b", "c"], "b", -1)).toEqual(["b", "a", "c"]);
    expect(moveItem(["a", "b", "c"], "b", 1)).toEqual(["a", "c", "b"]);
    expect(moveItem(["a", "b", "c"], "a", -1)).toEqual(["a", "b", "c"]);
    expect(moveItem(["a", "b", "c"], "c", 1)).toEqual(["a", "b", "c"]);
    expect(moveItem(["a", "b"], "x", 1)).toEqual(["a", "b"]);
  });

  it("drops a policy in front of another or at the end, and does not change the input", () => {
    const ids = ["a", "b", "c", "d"];
    expect(dropItem(ids, "d", "b")).toEqual(["a", "d", "b", "c"]);
    expect(dropItem(ids, "a", "d")).toEqual(["b", "c", "a", "d"]);
    expect(dropItem(ids, "a", null)).toEqual(["b", "c", "d", "a"]);
    expect(dropItem(ids, "b", "b")).toEqual(ids);
    expect(dropItem(ids, "x", "b")).toEqual(ids);
    expect(ids).toEqual(["a", "b", "c", "d"]);
  });

  it("says two policies overlap when some message can match both, an empty list matching any", () => {
    expect(overlaps({ severities: [], tags: [] }, { severities: ["critical"], tags: ["water"] })).toBe(true);
    expect(overlaps({ severities: ["info"], tags: [] }, { severities: ["critical"], tags: [] })).toBe(false);
    expect(overlaps({ severities: ["info"], tags: ["digest"] }, { severities: ["info", "success"], tags: [] })).toBe(true);
    expect(overlaps({ severities: ["info"], tags: ["digest"] }, { severities: ["info"], tags: ["door"] })).toBe(false);
  });

  const list = [
    { name: "Critical delivery", subentry_id: "1", data: { type: "deliver", severities: ["critical"], tags: [], enabled: true } },
    { name: "Everything", subentry_id: "2", data: { type: "quiet_hours", severities: [], tags: [], enabled: true } },
    { name: "By hand", subentry_id: "3", data: { type: "quiet_hours", severities: [], tags: [], apply: "manual", enabled: true } },
    { name: "Off", subentry_id: "4", data: { type: "quiet_hours", severities: [], tags: [], enabled: false } },
    { name: "Quiet", subentry_id: "5", data: { type: "quiet_hours", severities: ["info"], tags: [], enabled: true } },
  ];
  const mine = (extra) => ({ ...blankPolicy("quiet_hours"), severities: ["info"], tags: "", ...extra });

  it("lists in the mode first the policies above that match some of the same messages", () => {
    const names = overlapNames({ values: mine(), own: list[4], policies: list, mode: "first" });
    expect(names).toEqual(["Everything"]); // not the manual, the disabled or the critical-only one
    expect(overlapNames({ values: mine(), own: null, policies: list, mode: "first" })).toEqual(["Everything", "Quiet"]);
  });

  it("lists in the mode all the other policies of the same type that match", () => {
    const names = overlapNames({ values: mine(), own: list[4], policies: list, mode: "all" });
    expect(names).toEqual(["Everything"]);
    const escalation = { ...blankPolicy("escalation"), severities: ["critical"] };
    expect(overlapNames({ values: escalation, own: null, policies: list, mode: "all" })).toEqual([]);
  });

  it("names the policy above that matches every message of a policy, so it never runs by itself", () => {
    const row = (name, id, severities, tags, extra = {}) => ({ name, subentry_id: id, data: { type: "deliver", severities, tags, enabled: true, ...extra } });
    const policies = [
      row("Critical delivery", "1", ["critical"], []),
      row("Water escalation", "2", ["critical"], ["water"]),
      row("Water reminder", "3", ["critical"], ["water"]),
      row("Warnings", "4", ["warning"], []),
      row("Any", "5", [], []),
    ];
    expect(shadowedBy(policies[0], policies)).toBeNull();
    expect(shadowedBy(policies[1], policies)).toBe("Critical delivery"); // narrower than the one above
    expect(shadowedBy(policies[2], policies)).toBe("Critical delivery");
    expect(shadowedBy(policies[3], policies)).toBeNull(); // another severity
    expect(shadowedBy(policies[4], policies)).toBeNull(); // wider than the ones above: partial overlap only
    const reordered = [policies[1], policies[0]];
    expect(shadowedBy(reordered[0], reordered)).toBeNull();
    expect(shadowedBy(reordered[1], reordered)).toBeNull(); // critical, any tag is wider than critical + water
  });

  it("ignores manual and disabled policies on both sides", () => {
    const base = { type: "deliver", severities: ["critical"], tags: [], enabled: true };
    const above = (extra) => ({ name: "Above", subentry_id: "1", data: { ...base, ...extra } });
    const below = (extra) => ({ name: "Below", subentry_id: "2", data: { ...base, ...extra } });
    expect(shadowedBy(below(), [above(), below()])).toBe("Above");
    expect(shadowedBy(below(), [above({ enabled: false }), below()])).toBeNull();
    expect(shadowedBy(below(), [above({ apply: "manual" }), below()])).toBeNull();
    expect(shadowedBy(below({ apply: "manual" }), [above(), below({ apply: "manual" })])).toBeNull();
    expect(shadowedBy(below({ enabled: false }), [above(), below({ enabled: false })])).toBeNull();
  });

  it("lists nothing for a manual policy", () => {
    expect(overlapNames({ values: mine({ apply: "manual" }), own: null, policies: list, mode: "first" })).toEqual([]);
  });

  it("has the texts of the mode choice and the order in every language", () => {
    for (const [code, language] of Object.entries(POLICY_STRINGS)) {
      for (const key of ["mode_title", "mode_first", "mode_first_hint", "mode_all", "mode_all_hint", "order_first", "order_all", "move_up", "move_down", "handle", "position", "overlap_first", "overlap_all", "order_failed"]) {
        expect(language[key], `${code} ${key}`).toBeTruthy();
      }
    }
  });
});

describe("recipients list channel states", () => {
  const anna = { channels: ["banner", "push", "popup", "mail"], devices: [{ service_found: true }], user: true, mail_address: "a@example.com" };

  it("lists the channels in the order of the table", () => {
    expect(PROFILE_CHANNELS).toEqual(["banner", "push", "popup", "mail"]);
  });

  it("is on for an accepted channel that can work", () => {
    for (const channel of PROFILE_CHANNELS) expect(channelState(anna, channel)).toEqual({ channel, state: "on", warn: null });
  });

  it("is off for a channel the profile does not accept", () => {
    expect(channelState({ ...anna, channels: ["banner"] }, "push").state).toBe("off");
  });

  it("warns for an accepted channel that cannot work", () => {
    expect(channelState({ ...anna, devices: [] }, "push").warn).toBe("device");
    expect(channelState({ ...anna, devices: [{ service_found: false }] }, "push").warn).toBe("device");
    expect(channelState({ ...anna, user: false }, "popup").warn).toBe("user");
    expect(channelState({ ...anna, mail_address: "  " }, "mail").warn).toBe("address");
    expect(channelState({ ...anna, user: false }, "banner").warn).toBeNull();
  });

  it("has the words for every warning in all four languages", () => {
    for (const lang of ["en", "de", "fr", "es"]) {
      for (const key of ["ch_warn_device", "ch_warn_user", "ch_warn_address", "ch_none", "ch_on", "ch_off", "person"]) {
        expect(RECIPIENT_STRINGS[lang][key], `${lang}.${key}`).toBeTruthy();
      }
      expect(RECIPIENT_STRINGS[lang].customized).toBeUndefined();
    }
  });
});

describe("policy channels and recipients from the call", () => {
  const base = (extra) => ({ ...blankPolicy("fallback"), name: "Everyone instead", when: "no_audience", ...extra });

  it("sends the two settings only when they are not the default", () => {
    const data = policyData(base({ channels: ["push"], push_recipients: ["person.ben"] }));
    expect(data.channels_from).toBeUndefined();
    expect(data.targets_from).toBeUndefined();
  });

  it("same channels, new people: no channels, the people and speakers targets", () => {
    const data = policyData(base({ channels_from: "call", channels: ["push"], people_audience: "Everyone", speak_recipients: ["media_player.hall"] }));
    expect(data.channels_from).toBe("call");
    expect(data.channels).toEqual([]);
    expect(data.people_audience).toBe("Everyone");
    expect(data.speak_recipients).toEqual(["media_player.hall"]);
    expect(data.push_audience).toBeUndefined();
  });

  it("only the failed channels is a fallback setting", () => {
    expect(policyData(base({ channels_from: "failed", people_audience: "Everyone" })).channels_from).toBe("failed");
  });

  it("new channels, same recipients: the channels and no targets", () => {
    const data = policyData(base({ targets_from: "call", channels: ["popup"], popup_audience: "Admins" }));
    expect(data.targets_from).toBe("call");
    expect(data.channels).toEqual(["popup"]);
    expect(data.popup_audience).toBeUndefined();
  });

  it("is checked like the server checks it", () => {
    expect(validatePolicy(base({ channels_from: "call", people_audience: "Everyone" }), [], "")).toEqual({});
    expect(validatePolicy(base({ channels_from: "call" }), [], "").people_target).toBe("target_required");
    expect(validatePolicy(base({ channels_from: "call", targets_from: "call" }), [], "").targets_from).toBe("nothing_new");
    expect(validatePolicy(base({ targets_from: "call", channels: [] }), [], "").channels).toBe("channels_required");
    expect(validatePolicy(base({ targets_from: "call", channels: ["push"] }), [], "")).toEqual({});
    expect(validatePolicy(base({ channels_from: "call", people_audience: "Everyone", people_recipients: ["person.ben"] }), [], "").people_target).toBe("target_exclusive");
  });

  it("reads the settings and the targets of a stored policy back", () => {
    const values = fromPolicy({ name: "P", data: { type: "fallback", when: "failed", channels_from: "failed", targets: { people: { audience: "Everyone" }, speak: { recipients: ["media_player.hall"] } } } });
    expect(values.channels_from).toBe("failed");
    expect(values.targets_from).toBe("policy");
    expect(values.people_audience).toBe("Everyone");
    expect(values.speak_recipients).toEqual(["media_player.hall"]);
  });

  it("says where the channels and the recipients come from", () => {
    const t = POLICY_STRINGS.en;
    expect(sentence(base({ channels_from: "call", people_audience: "Everyone" }), t)).toContain("the channels of the call");
    expect(sentence(base({ channels_from: "failed", people_audience: "Everyone" }), t)).toContain("that reached nobody");
    const same = sentence(base({ targets_from: "call", channels: ["popup"] }), t);
    expect(same).toContain("Popup");
    expect(same.endsWith(t.s_recipients_call)).toBe(true);
    const named = sentence(base({ channels_from: "call", people_audience: "Everyone", speak_recipients: ["media_player.hall"] }), t);
    expect(named.endsWith("It goes to Everyone, media_player.hall.")).toBe(true);
  });

  it("has the new words in all four languages", () => {
    for (const lang of ["en", "de", "fr", "es"]) {
      const t = POLICY_STRINGS[lang];
      for (const key of ["channels_from", "targets_from", "people_target", "speakers_target", "tf_call_hint", "same_empty", "s_recipients_policy", "s_channels_call", "s_channels_failed", "s_recipients_call"]) {
        expect(t[key], `${lang}.${key}`).toBeTruthy();
      }
      for (const key of ["policy", "call", "failed"]) expect(t.cf[key], `${lang}.cf.${key}`).toBeTruthy();
      for (const key of ["policy", "call"]) expect(t.tf[key], `${lang}.tf.${key}`).toBeTruthy();
    }
  });
});
