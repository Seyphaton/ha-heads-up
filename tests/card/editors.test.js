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
} from "../../custom_components/heads_up/frontend/panel/channels.js";
import { errorText, ERRORS, joinTags, splitTags, toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

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
    expect(profileValues(profile)).toEqual({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup"] });
  });

  it("needs no stored profile when nothing differs from the detected devices", () => {
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup"] })).toBe(true);
    expect(isDefault({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "d1", channels: ["banner", "push", "popup"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push"] })).toBe(false);
  });

  it("builds the flow data, with the person only when creating", () => {
    const values = { manual: ["d2"], removed: ["d9"], primary: "d1", channels: ["popup", "banner"] };
    expect(toProfileData("person.anna", values, true)).toEqual({ person: "person.anna", channels: ["banner", "popup"], devices: ["d2"], removed_devices: ["d9"], primary: "d1" });
    expect(toProfileData("person.anna", { manual: [], removed: [], primary: "", channels: ["push"] }, false)).toEqual({ channels: ["push"] });
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
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).toMatchObject({ from_time: "22:00:00", to_time: "07:00:00", days: [], action: "quiet", critical_passes: true });
    expect(policyData({ ...blankPolicy("away"), name: "Back", max_wait: 0 })).toMatchObject({ max_wait: 0 });
    expect(policyData({ ...blankPolicy("fallback"), name: "Backup", channels: ["speak"], speak_recipients: ["media_player.k"] })).toMatchObject({ when: "no_audience", channels: ["speak"], speak_recipients: ["media_player.k"] });
    expect(policyData({ ...blankPolicy("deliver"), name: "Crit", severities: ["critical"], channels: ["push"], push_audience: "Admins" })).toEqual({
      name: "Crit", type: "deliver", severities: ["critical"], tags: [], enabled: true, channels: ["push"], push_audience: "Admins",
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
    expect(sentence(water, t)).toBe("Messages with severity Critical and tag water: if nobody acknowledges within 5 min, it is also sent on Push, Bell.");
    expect(sentence({ ...blankPolicy("quiet_hours"), days: ["sat", "sun"] }, t)).toBe("Every message: between 22:00 and 07:00 on Saturday, Sunday, deliveries outside the dashboard are sent quietly, critical messages pass.");
    expect(sentence({ ...blankPolicy("reminder"), channels: ["push"] }, t)).toBe("Every message: while nobody acknowledges, the notification is repeated every 30 min, at most 3 times, only on Push.");
    expect(sentence({ ...blankPolicy("away"), max_wait: 30 }, t)).toBe("Every message: a person who is not home gets it when they arrive, for at most 30 min.");
    expect(sentence({ ...blankPolicy("fallback"), when: "both", channels: ["persistent"] }, t)).toBe("Every message: if the audience is empty or delivery fails, it is sent on Bell instead.");
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
