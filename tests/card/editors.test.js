import { describe, expect, it } from "vitest";
import {
  blankValues as blankAudience,
  describe as describeAudience,
  fromAudience,
  STRINGS as AUDIENCE_STRINGS,
  toFlowData as audienceData,
  validate as validateAudience,
  audienceIcon,
} from "../../custom_components/heads_up/frontend/panel/audiences.js";
import {
  addDevice,
  channelState,
  PROFILE_CHANNELS,
  groupData,
  haInZone,
  homeEntities,
  initials as recipientInitials,
  isDefault,
  profileValues,
  removeDevice,
  restoreDevice,
  STRINGS as RECIPIENT_STRINGS,
  toProfileData,
  validateGroup,
  zoneOrder,
} from "../../custom_components/heads_up/frontend/panel/recipients.js";
import {
  appliesText,
  blankValues as blankPolicy,
  checkLine,
  laneOf,
  whichText,
  notOverlap,
  doesText,
  leftOut,
  takenBy,
  overlapNames,
  overlaps,
  fromPolicy,
  sentence,
  splitTags as policyTags,
  STRINGS as POLICY_STRINGS,
  toFlowData as policyData,
  validate as validatePolicy,
  checklistAnswered,
  rowWho,
} from "../../custom_components/heads_up/frontend/panel/policies.js";
import {
  changes as channelChanges,
  problems as channelProblems,
  STRINGS as CHANNEL_STRINGS,
  validChannelId,
  validMailTemplate,
} from "../../custom_components/heads_up/frontend/panel/channels.js";
import { errorText, ERRORS, joinTags, parseRich, recipientLabel, splitTags, toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

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
    channels: ["banner", "push", "popup", "inbox"],
    removed: [],
    devices: [
      { device_id: "d1", name: "Phone", service_found: true, source: "detected" },
      { device_id: "d2", name: "Tablet", service_found: true, source: "manual" },
    ],
  };

  it("starts from what the profile changes", () => {
    expect(profileValues(profile)).toEqual({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"], mail_address: "", home_entity: "", zone_entities: {}, enabled: true });
    expect(profileValues({ ...profile, home_entity: "binary_sensor.anna_home" }).home_entity).toBe("binary_sensor.anna_home");
  });

  it("needs no stored profile when nothing differs from the detected devices", () => {
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"] })).toBe(true);
    expect(isDefault({ manual: ["d2"], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "d1", channels: ["banner", "push", "popup", "inbox"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup"] })).toBe(false); // the inbox is off
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "mail", "inbox"] })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"], mail_address: "a@b.c" })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"], home_entity: "input_boolean.x" })).toBe(false);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"], zone_entities: { "zone.work": "" } })).toBe(true);
    expect(isDefault({ manual: [], removed: [], primary: "", channels: ["banner", "push", "popup", "inbox"], zone_entities: { "zone.work": "binary_sensor.w" } })).toBe(false);
  });

  it("stores only the zones that have an entity", () => {
    const values = { manual: [], removed: [], primary: "", channels: ["push"], home_entity: "input_boolean.h", zone_entities: { "zone.work": "binary_sensor.w", "zone.gym": "" } };
    expect(toProfileData("person.anna", values, false)).toEqual({ channels: ["push"], home_entity: "input_boolean.h", zone_entities: { "zone.work": "binary_sensor.w" } });
  });

  it("offers on/off entities for a zone, without Heads Up's own audience sensors", () => {
    const hass = {
      states: { "input_boolean.b": {}, "binary_sensor.a": {}, "binary_sensor.heads_up_audience_admins": {}, "sensor.t": {} },
      entities: { "binary_sensor.heads_up_audience_admins": { platform: "heads_up" } },
    };
    expect(homeEntities(hass, "")).toEqual(["binary_sensor.a", "input_boolean.b"]);
    expect(homeEntities(hass, "binary_sensor.gone")).toEqual(["binary_sensor.a", "input_boolean.b", "binary_sensor.gone"]);
  });

  it("reads Home Assistant's zone of a person as the integration does", () => {
    expect(haInZone({ state: "home", attributes: {} }, "zone.home")).toBe(true);
    expect(haInZone({ state: "not_home", attributes: {} }, "zone.home")).toBe(false);
    expect(haInZone({ state: "not_home", attributes: { in_zones: ["zone.work"] } }, "zone.work")).toBe(true);
    expect(haInZone({ state: "work", attributes: {} }, "zone.work")).toBe(true);
    expect(haInZone({ state: "unavailable", attributes: {} }, "zone.work")).toBe(null);
    expect(haInZone(undefined, "zone.home")).toBe(null);
    expect(zoneOrder([{ id: "zone.work", name: "Work" }, { id: "zone.home", name: "Home" }, { id: "zone.gym", name: "Gym" }]).map((z) => z.id)).toEqual(["zone.home", "zone.gym", "zone.work"]);
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
    expect(policyData({ ...blankPolicy("presence"), name: "Back" })).toMatchObject({ max_wait: 0 });
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).toMatchObject({ from_time: "22:00:00", to_time: "07:00:00", days: [], action: "quiet" });
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).not.toHaveProperty("holds_anyway");
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).not.toHaveProperty("quiet_entity");
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night" })).not.toHaveProperty("channels");
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Night", channels: ["push"] }).channels).toEqual(["push"]);
    expect(fromPolicy({ name: "Night", data: { type: "quiet_hours", channels: ["popup"] } }).channels).toEqual(["popup"]);
    expect(policyData({ ...blankPolicy("quiet_hours"), name: "Nap", quiet_entity: "input_boolean.nap" }).quiet_entity).toBe("input_boolean.nap");
    expect(fromPolicy({ name: "Nap", data: { type: "quiet_hours", quiet_entity: "input_boolean.nap" } }).quiet_entity).toBe("input_boolean.nap");
    expect(policyData({ ...blankPolicy("presence"), name: "Back", max_wait: 0 })).toMatchObject({ max_wait: 0, after_wait: "send" });
    expect(policyData({ ...blankPolicy("presence"), name: "Back" })).not.toHaveProperty("zone");
    expect(policyData({ ...blankPolicy("presence"), name: "Say", channels: ["speak"], household_who: "somebody" })).toMatchObject({ channels: ["speak"], household_who: "somebody" });
    expect(fromPolicy({ name: "Old", data: { type: "away", max_wait: 30 } })).toMatchObject({ type: "presence", after_wait: "drop", max_wait: 30 });
    expect(policyData({ ...blankPolicy("fallback"), name: "Backup", channels: ["speak"], speak_recipients: ["media_player.k"] })).toMatchObject({ when: "no_audience", channels: ["speak"], speak_recipients: ["media_player.k"] });
    expect(policyData({ ...blankPolicy("deliver"), name: "Crit", severities: ["critical"], channels: ["push"], push_audience: "Admins" })).toEqual({
      name: "Crit", type: "deliver", apply: "auto", severities: ["critical"], tags: [], enabled: true, channels: ["push"], push_audience: "Admins",
    });
    const every = policyData({ ...blankPolicy("summarize"), name: "Digest" });
    expect(every).toMatchObject({ summary_every: 60 });
    expect(every).not.toHaveProperty("holds_anyway");
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
    expect(validatePolicy({ ...blankPolicy("quiet_hours"), name: "Q", quiet_entity: "schedule.night", from_time: "08:00:00", to_time: "08:00:00" }, [])).toEqual({});
    expect(validatePolicy({ ...blankPolicy("quiet_hours"), name: "Q", quiet_entity: "sensor.t" }, [])).toEqual({ quiet_entity: "quiet_entity_invalid" });
    expect(validatePolicy({ ...blankPolicy("summarize"), name: "S", summary_every: 0 }, [])).toEqual({ summary_every: "every_required" });
    expect(validatePolicy({ ...blankPolicy("summarize"), name: "S", summary_mode: "at", summary_at: "" }, [])).toEqual({ summary_at: "time_invalid" });
    expect(validatePolicy({ ...blankPolicy("fallback"), name: "F", channels: [] }, [])).toEqual({ channels: "channels_required" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: [] }, [])).toEqual({ channels: "channels_required" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: ["push"] }, [])).toEqual({ push_target: "target_exclusive" });
    expect(validatePolicy({ ...blankPolicy("deliver"), name: "D", channels: ["push"], push_audience: "Admins" }, [])).toEqual({});
    expect(validatePolicy({ ...blankPolicy("presence"), name: "A", max_wait: -1 }, [])).toEqual({ max_wait: "wait_invalid" });
    expect(validatePolicy({ ...blankPolicy("presence"), name: "water" }, ["Water"], "Water")).toEqual({});
    expect(validatePolicy({ ...blankPolicy("presence"), name: "water" }, ["Water"])).toEqual({ name: "name_exists" });
  });

  it("reads a stored policy back into the form", () => {
    const stored = { name: "Water", data: { type: "escalation", severities: ["critical"], tags: ["water", "leak"], enabled: false, after_minutes: 9, channels: ["push", "speak"], dismiss_acks: true, targets: { push: { audience: "Admins" }, speak: { recipients: ["media_player.k"] } } } };
    expect(fromPolicy(stored)).toMatchObject({
      name: "Water", type: "escalation", severities: ["critical"], tags: "water, leak", enabled: false, after_minutes: 9, dismiss_acks: true,
      push_audience: "Admins", speak_recipients: ["media_player.k"],
    });
    const digest = fromPolicy({ name: "D", data: { type: "summarize", summary_at: "19:30:00", holds_anyway: true } });
    expect(digest).toMatchObject({ summary_mode: "at", summary_at: "19:30:00", holds_anyway: true });
  });

  it("describes a policy in plain words", () => {
    const t = POLICY_STRINGS.en;
    expect(appliesText(blankPolicy("presence"), t)).toBe("Every message");
    expect(appliesText({ ...blankPolicy("presence"), severities: ["critical", "warning"], tags: "water" }, t)).toBe("Messages with severity Critical, Warning and tag water");
    expect(appliesText({ ...blankPolicy("presence"), tags: "smoke_never" }, t)).toBe("Messages with tag smoke_never");
    expect(appliesText({ ...blankPolicy("presence"), severities: ["info"] }, t)).toBe("Messages with severity Info");
    expect(sentence(water, t)).toBe("Messages with severity Critical and tag water: if nobody acknowledges within 5 min, it is also sent on Push, Persistent Notification.");
    expect(sentence({ ...blankPolicy("quiet_hours"), days: ["sat", "sun"] }, t)).toBe("Every message: between 22:00 and 07:00 on Saturday, Sunday, deliveries outside the dashboard are sent quietly.");
    expect(sentence({ ...blankPolicy("quiet_hours"), channels: ["push", "popup"] }, t)).toContain("sent quietly, only on");
    expect(sentence({ ...blankPolicy("quiet_hours"), quiet_entity: "schedule.night", action: "wait" }, t)).toBe("Every message: while schedule.night is on, deliveries outside the dashboard are held until the end.");
    expect(sentence({ ...blankPolicy("reminder"), channels: ["push"] }, t)).toBe("Every message: while nobody acknowledges, the notification is repeated every 30 min, at most 3 times, only on Push.");
    expect(sentence({ ...blankPolicy("presence"), max_wait: 30 }, t)).toBe("Every message: a recipient who is not in Home: push, popup, mail and inbox are held until that changes, for at most 30 min, then sent anyway.");
    expect(sentence({ ...blankPolicy("presence"), channels: ["speak"], presence_then: "drop" }, t)).toBe("Every message: speech while nobody of everyone is in Home is dropped.");
    expect(sentence({ ...blankPolicy("fallback"), when: "both", channels: ["persistent"] }, t)).toBe("Every message: if the audience is empty or delivery fails, it is sent on Persistent Notification instead.");
    expect(sentence({ ...blankPolicy("deliver"), severities: ["critical"], channels: ["push"] }, t)).toBe("Messages with severity Critical: it is also sent at once on Push.");
    expect(sentence({ ...blankPolicy("summarize") }, t)).toBe("Every message: held, and one summary is sent 60 min after the first held message.");
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

describe("the lanes and the overlap note", () => {
  it("says two policies overlap when some message can match both, an empty list matching any", () => {
    expect(overlaps({ severities: [], tags: [] }, { severities: ["critical"], tags: ["water"] })).toBe(true);
    expect(overlaps({ severities: ["info"], tags: [] }, { severities: ["critical"], tags: [] })).toBe(false);
    expect(overlaps({ severities: ["info"], tags: ["digest"] }, { severities: ["info", "passive"], tags: [] })).toBe(true);
    expect(overlaps({ severities: ["info"], tags: ["digest"] }, { severities: ["info"], tags: ["door"] })).toBe(false);
  });

  it("puts each policy in its lane, manual ones apart", () => {
    expect(laneOf({ data: { type: "quiet_hours" } })).toBe("calm");
    expect(laneOf({ data: { type: "away" } })).toBe("calm");
    expect(laneOf({ data: { type: "get_through" } })).toBe("band");
    expect(laneOf({ data: { type: "fallback" } })).toBe("arrive");
    expect(laneOf({ data: { type: "deliver", apply: "manual" } })).toBe("named");
  });

  const list = [
    { name: "Critical delivery", subentry_id: "1", data: { type: "deliver", severities: ["critical"], tags: [], enabled: true } },
    { name: "Everything", subentry_id: "2", data: { type: "quiet_hours", severities: [], tags: [], enabled: true } },
    { name: "By hand", subentry_id: "3", data: { type: "quiet_hours", severities: [], tags: [], apply: "manual", enabled: true } },
    { name: "Off", subentry_id: "4", data: { type: "quiet_hours", severities: [], tags: [], enabled: false } },
    { name: "Quiet", subentry_id: "5", data: { type: "quiet_hours", severities: ["info"], tags: [], enabled: true } },
    { name: "Away", subentry_id: "6", data: { type: "presence", severities: [], tags: [], enabled: true } },
  ];
  const mine = (extra) => ({ ...blankPolicy("quiet_hours"), severities: ["info"], tags: "", ...extra });

  it("names the other calming policies that fit some of the same messages", () => {
    expect(overlapNames({ values: mine(), own: list[4], policies: list })).toEqual(["Everything", "Away"]);
    expect(overlapNames({ values: mine(), own: null, policies: list })).toEqual(["Everything", "Quiet", "Away"]);
  });

  it("names for a sending policy only others of its type", () => {
    const escalation = { ...blankPolicy("escalation"), severities: ["critical"] };
    expect(overlapNames({ values: escalation, own: null, policies: list })).toEqual([]);
    const deliver = { ...blankPolicy("deliver"), severities: [] };
    expect(overlapNames({ values: deliver, own: null, policies: list })).toEqual(["Critical delivery"]);
  });

  it("has the texts of the lanes, the check list and the checker in every language", () => {
    const keys = ["lane_calm", "lane_calm_hint", "band", "band_hint", "lane_arrive", "lane_arrive_hint", "lane_named", "cl_title", "cl_keep", "cl_act", "cl_through", "ck_title", "ck_run", "r_quiet", "r_by", "help_button", "s_through", "holds_anyway", "only_if", "faster", "alongside", "not_tags"];
    for (const [code, language] of Object.entries(POLICY_STRINGS)) {
      for (const key of keys) expect(language[key], `${code} ${key}`).toBeTruthy();
      expect(language.mode_title, code).toBeUndefined();
      expect(language.types.get_through, code).toBeTruthy();
    }
  });
});

describe("2.0 policy fields", () => {
  it("sends Not for, From watch rule and Only if, and reads them back", () => {
    const values = { ...blankPolicy("quiet_hours"), name: "Night", not_tags: "digest", oi_entity: "input_boolean.guests", oi_state: "off", holds_anyway: true };
    const data = policyData(values);
    expect(data).toMatchObject({ not_tags: ["digest"], only_if: { entity_id: "input_boolean.guests", state: "off" }, holds_anyway: true });
    expect(fromPolicy({ name: "Night", data })).toMatchObject({ not_tags: "digest", oi_entity: "input_boolean.guests", oi_state: "off", holds_anyway: true });
  });

  it("keeps an Only if it cannot edit as it is", () => {
    const template = { template: "{{ is_state('input_boolean.x', 'on') }}" };
    const values = fromPolicy({ name: "T", data: { type: "deliver", channels: ["push"], only_if: template } });
    expect(values.only_if_raw).toEqual(template);
    expect(policyData({ ...values, push_audience: "Admins" }).only_if).toEqual(template);
  });

  it("sends Faster while and Runs alongside for a reminder", () => {
    const data = policyData({ ...blankPolicy("reminder"), name: "Nag", fw_entity: "binary_sensor.window", fw_state: "on", fw_every: 15, alongside: true });
    expect(data).toMatchObject({ faster_while: { condition: { entity_id: "binary_sensor.window", state: "on" }, every_minutes: 15 }, alongside: true });
  });

  it("sends a band entry with whom it covers", () => {
    expect(policyData({ ...blankPolicy("get_through"), name: "Critical", severities: ["critical"] })).toMatchObject({ type: "get_through", covers: "everyone" });
    const only = policyData({ ...blankPolicy("get_through"), name: "Alarms", covers: "only", covers_recipients: ["person.ben"] });
    expect(only).toMatchObject({ covers: "only", covers_recipients: ["person.ben"] });
    expect(validatePolicy({ ...blankPolicy("get_through"), name: "A", covers: "only" }, [])).toEqual({ covers_recipients: "target_required" });
  });

  it("says a band entry and the 2.0 extras in words", () => {
    const t = POLICY_STRINGS.en;
    expect(sentence({ ...blankPolicy("get_through"), tags: "alarm", covers: "only", covers_recipients: ["person.ben"] }, t, { recipient: () => "Ben" })).toBe("Messages with tag alarm: ignores quiet hours and summaries for Ben.");
    expect(sentence({ ...blankPolicy("get_through"), severities: ["critical"] }, t)).toBe("Messages with severity Critical: ignores quiet hours and summaries.");
    expect(sentence({ ...blankPolicy("quiet_hours"), not_tags: "digest", holds_anyway: true }, t)).toBe("Every message: between 22:00 and 07:00, deliveries outside the dashboard are sent quietly. Not for #digest. Nothing gets past it, not even Always gets through.");
    expect(sentence({ ...blankPolicy("reminder"), fw_entity: "binary_sensor.window", fw_state: "on", fw_every: 15, alongside: true }, t)).toBe("Every message: while nobody acknowledges, the notification is repeated every 30 min, at most 3 times. While binary_sensor.window is on: every 15 min. Runs alongside other reminders.");
  });

  it("says What it does in a few words that fit one row", () => {
    const t = POLICY_STRINGS.en;
    expect(doesText({ ...blankPolicy("reminder") }, t)).toBe("Every 30 min, at most 3 times");
    expect(doesText({ ...blankPolicy("quiet_hours") }, t)).toBe("22:00–07:00: send quietly");
    expect(doesText({ ...blankPolicy("get_through") }, t)).toBe("Ignores quiet hours and summaries");
    expect(doesText({ ...blankPolicy("escalation"), channels: ["push"] }, t)).toBe("After 5 min: Push");
    expect(doesText({ ...blankPolicy("presence") }, t)).toBe("Hold until the person is at Home");
    for (const type of ["summarize", "quiet_hours", "presence", "get_through", "deliver", "escalation", "reminder", "fallback"]) {
      expect(doesText({ ...blankPolicy(type), channels: ["push"] }, t).length, type).toBeLessThan(60);
    }
  });

  it("says in words what a converted policy leaves out", () => {
    const t = POLICY_STRINGS.en;
    expect(leftOut(["warning", "critical"], ["digest"], t)).toBe("messages with severity Warning, Critical or messages with the tag digest");
    expect(takenBy({ data: { severities: ["critical"], tags: ["water"] } }, t)).toBe("messages with severity Critical and the tag water");
    for (const [code, language] of Object.entries(POLICY_STRINGS)) {
      for (const key of ["cl_not_for", "cl_never", "cl_links", "cl_holds", "cl_sev", "cl_tag", "cl_sev_tag", "links_note"]) expect(language[key], `${code} ${key}`).toBeTruthy();
    }
  });

  it("warns when Not for repeats something from For", () => {
    const t = POLICY_STRINGS.en;
    expect(notOverlap({ ...blankPolicy("quiet_hours"), tags: "a, b", not_tags: "b" }, t)).toEqual(["#b"]);
    expect(notOverlap({ ...blankPolicy("quiet_hours"), tags: "a", not_tags: "b" }, t)).toEqual([]);
  });

  it("says Which messages in a few words", () => {
    const t = POLICY_STRINGS.en;
    expect(whichText(blankPolicy("quiet_hours"), t)).toBe("All messages");
    expect(whichText({ ...blankPolicy("quiet_hours"), severities: ["critical"], tags: "alarm", not_tags: "digest" }, t)).toBe("Severity: Critical · Tag: alarm · not #digest");
    expect(whichText({ ...blankPolicy("deliver"), apply: "manual" }, t)).toBe("Only when named");
  });

  it("never mentions the earlier version in the page texts", () => {
    for (const [code, language] of Object.entries(POLICY_STRINGS)) {
      for (const [key, value] of Object.entries(language)) {
        if (typeof value === "string") expect(value, `${code} ${key}`).not.toMatch(/1\.x/);
      }
    }
  });

  it("words one line of the checker", () => {
    const t = POLICY_STRINGS.en;
    expect(checkLine({ channel: "push", result: "sent", note: "quiet", by: "Night quiet" }, t, "Anna")).toBe("Anna · Push: sent quietly (by Night quiet)");
    expect(checkLine({ channel: "push", result: "sent", through: ["Alarms wake Admins"], via: "Alarms to Admins" }, t, "Ben")).toBe("Ben · Push: sent (let through by Alarms wake Admins; added by Alarms to Admins)");
    expect(checkLine({ channel: "push", result: "held", until: "x", untilText: "07:00", by: "Away" }, t, "Chris")).toBe("Chris · Push: held until 07:00 (by Away)");
    expect(checkLine({ channel: "push", result: "skipped", reason: "no_usable_device" }, t, "Ben", () => "no usable device")).toBe("Ben · Push: skipped (no usable device)");
  });
});

describe("recipients list channel states", () => {
  const anna = { channels: ["banner", "push", "popup", "mail", "inbox"], devices: [{ service_found: true }], user: true, mail_address: "a@example.com" };

  it("lists the channels in the order of the table", () => {
    expect(PROFILE_CHANNELS).toEqual(["banner", "push", "popup", "mail", "inbox"]);
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
      for (const key of ["ch_warn_device", "ch_warn_user", "ch_warn_address", "ch_on", "ch_off", "person", "col_group", "col_call", "col_speakers"]) {
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

describe("check list after the update", () => {
  const policies = [{ subentry_id: "a" }, { subentry_id: "b" }];
  it("counts as answered only when every item of an existing policy is answered", () => {
    expect(checklistAnswered([{ policy: "a", state: "kept" }, { policy: "b", state: "changed" }], policies)).toBe(true);
    expect(checklistAnswered([{ policy: "a", state: "kept" }, { policy: "b", state: "open" }], policies)).toBe(false);
  });

  it("ignores items of deleted policies and is not answered when nothing is left", () => {
    expect(checklistAnswered([{ policy: "a", state: "kept" }, { policy: "gone", state: "open" }], policies)).toBe(true);
    expect(checklistAnswered([{ policy: "gone", state: "kept" }], policies)).toBe(false);
    expect(checklistAnswered(undefined, policies)).toBe(false);
  });
});

describe("checker rows name the phone", () => {
  const choices = {
    persons: [{ id: "person.anna", name: "Anna" }],
    registrations: [
      { id: "aaaa1111", name: "iPhone" },
      { id: "bbbb2222", name: "iPad" },
    ],
  };
  const label = recipientLabel;

  it("shows the person and the phone, so two phones are not two duplicates", () => {
    expect(rowWho({ person: "person.anna", recipient: "device:aaaa1111" }, choices, label)).toBe("Anna (iPhone)");
    expect(rowWho({ person: "person.anna", recipient: "device:bbbb2222" }, choices, label)).toBe("Anna (iPad)");
  });

  it("shows the person alone for a row without a phone, the phone alone without a person, and a dash for nothing", () => {
    expect(rowWho({ person: "person.anna", recipient: "person.anna" }, choices, label)).toBe("Anna");
    expect(rowWho({ person: null, recipient: "device:aaaa1111" }, choices, label)).toBe("iPhone");
    expect(rowWho({ person: null, recipient: "" }, choices, label)).toBe("—");
  });
});

describe("icons and marks on the Audiences and Recipients rows", () => {
  it("gives every built-in audience kind and the persons kind its own icon, and a fallback", () => {
    const kinds = ["everyone", "admins", "at_home", "not_home", "last_to_leave", "first_home", "persons"];
    const icons = kinds.map((k) => audienceIcon(k));
    expect(new Set(icons).size).toBe(kinds.length);
    expect(icons.every((i) => i.startsWith("mdi:"))).toBe(true);
    expect(audienceIcon("something_new")).toBe("mdi:account-group-outline");
  });

  it("writes up to two initials for a person's mark", () => {
    expect(recipientInitials("Anna Berg")).toBe("AB");
    expect(recipientInitials("sho")).toBe("S");
    expect(recipientInitials("  ")).toBe("?");
  });
});
