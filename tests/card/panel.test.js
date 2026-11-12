import { readFileSync } from "node:fs";
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
import { audienceLabel, recipientLabel } from "../../custom_components/heads_up/frontend/panel/ui.js";
import { isDefault, profileValues, toProfileData } from "../../custom_components/heads_up/frontend/panel/recipients.js";
import {
  changes,
  devicesLabel,
  entriesOf,
  headingOf,
  fill,
  joinDuration,
  problems,
  rangesOf,
  splitDuration,
  STRINGS as SETTINGS_STRINGS,
  ttsEntities,
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
    expect(secondRow("faq")).toEqual(["faq", "examples", "card"]);
    expect(secondRow("card")).toEqual(["faq", "examples", "card"]);
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
  const layout = [
    { name: "dismiss", entries: [{ key: "default_timeout", kind: "duration", range: [0, 31536000] }] },
    { name: "snooze_banner", entries: [{ key: "default_snooze_options", kind: "minutes", choices: [5, 15] }] },
    { name: "limits", entries: [{ key: "max_banners", kind: "int", range: [1, 200] }, { key: "rate_per_device_per_minute", kind: "int", range: [1, 600] }, { key: "rate_total_per_minute", kind: "int", range: [1, 6000] }, { key: "dedupe_seconds", kind: "int", range: [0, 3600] }] },
    { name: "history", entries: [{ key: "trace_entries", kind: "int", range: [50, 5000] }, { key: "recent_messages", kind: "int", range: [10, 1000] }] },
    { name: "sidebar", entries: [{ key: "show_panel", kind: "bool" }] },
  ];
  const ranges = rangesOf(layout);
  const saved = {
    show_panel: false,
    max_banners: 50,
    default_timeout: 86400,
    default_snooze_options: [15, 60, 240],
    rate_per_device_per_minute: 10,
    rate_total_per_minute: 60,
    dedupe_seconds: 30,
    trace_entries: 500,
    recent_messages: 100,
  };

  it("takes the ranges from the layout the server sends", () => {
    expect(ranges.trace_entries).toEqual([50, 5000]);
    expect(ranges.show_panel).toBeUndefined();
  });

  it("splits a duration into days, hours, minutes and seconds and joins it again", () => {
    expect(splitDuration(90061)).toEqual({ days: 1, hours: 1, minutes: 1, seconds: 1 });
    expect(joinDuration({ days: 1, hours: 1, minutes: 1, seconds: 1 })).toBe(90061);
    expect(splitDuration(0)).toEqual({ days: 0, hours: 0, minutes: 0, seconds: 0 });
    expect(joinDuration({ days: "", hours: -1, minutes: 2.5, seconds: 5 })).toBe(5);
  });

  it("detects a changed list and sends only that key", () => {
    expect(changes({ ...saved, default_snooze_options: [15, 60] }, saved)).toEqual({ default_snooze_options: [15, 60] });
    expect(changes({ ...saved, default_snooze_options: [15, 60, 240] }, saved)).toEqual({});
  });

  it("lists the tts entities and keeps a stored one that no longer exists", () => {
    const hass = { states: { "tts.b": {}, "light.x": {}, "tts.a": {} } };
    expect(ttsEntities(hass, "")).toEqual(["tts.a", "tts.b"]);
    expect(ttsEntities(hass, "tts.gone")).toEqual(["tts.a", "tts.b", "tts.gone"]);
    expect(ttsEntities(undefined, "")).toEqual([]);
  });

  it("finds no problem in the saved values", () => {
    expect(problems(saved, ranges)).toEqual([]);
  });

  it("reports a value outside its range, a fraction or an empty field", () => {
    const bad = { ...saved, trace_entries: 10, dedupe_seconds: 1.5, recent_messages: NaN };
    expect(problems(bad, ranges).map((p) => p.key).sort()).toEqual(["dedupe_seconds", "recent_messages", "trace_entries"]);
    expect(problems({ ...saved, dedupe_seconds: 0 }, ranges)).toEqual([]);
  });

  it("puts a label and a hint on every entry in the order of the layout", () => {
    const groups = entriesOf(layout, SETTINGS_STRINGS.en);
    expect(groups.map((g) => g.name)).toEqual(["Messages › Dismiss settings", "Messages › Snooze settings › Banners", "Limits", "History", "Sidebar panel"]);
    expect(groups[0].desc).toMatch(/banner, the push and the popup/);
    expect(groups[2].entries.map((e) => e.label)).toEqual([
      "Maximum number of stored messages",
      "Pushes per device per minute",
      "Deliveries per minute, all devices",
      "Seconds in which identical updates are ignored",
    ]);
    expect(groups[4].entries[0].hint).toMatch(/^Only administrators/);
  });

  it("shows a section path as a heading over the cards that share it", () => {
    expect(headingOf("Messages › Snooze settings › Banners")).toEqual({ group: "Messages", title: "Snooze settings › Banners" });
    expect(headingOf("Limits")).toEqual({ group: null, title: "Limits" });
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

import {
  attentionText,
  inTime,
  logText,
  reasonText,
  stateText,
  timeAgo,
} from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import {
  badgeList,
  barTip,
  chartModel,
  fixKey,
  STRINGS as OVERVIEW_STRINGS,
} from "../../custom_components/heads_up/frontend/panel/overview.js";
import {
  groupEntries,
  recipientName,
  resultsLine,
  statusLabel,
  timerName,
  STRINGS as MESSAGES_STRINGS,
} from "../../custom_components/heads_up/frontend/panel/messages.js";

const S = STRINGS.en.shared;
const NOW = Date.parse("2026-11-01T12:00:00Z");

describe("shared wording", () => {
  it("says how long ago, in the largest fitting unit", () => {
    expect(timeAgo("2026-11-01T11:59:40Z", NOW, S)).toBe("just now");
    expect(timeAgo("2026-11-01T11:50:00Z", NOW, S)).toBe("10 min ago");
    expect(timeAgo("2026-11-01T09:00:00Z", NOW, S)).toBe("3 h ago");
    expect(timeAgo("2026-10-30T12:00:00Z", NOW, S)).toBe("2 d ago");
  });

  it("says how long until, and any moment when it is due", () => {
    expect(inTime("2026-11-01T12:03:00Z", NOW, S)).toBe("in 3 min");
    expect(inTime("2026-11-01T14:00:00Z", NOW, S)).toBe("in 2 h");
    expect(inTime("2026-11-01T11:59:00Z", NOW, S)).toBe("any moment");
    expect(inTime(null, NOW, S)).toBe("any moment");
  });

  it("words each state of a message", () => {
    const due = "2026-11-01T12:03:00Z";
    expect(stateText({ state: "escalating", phase: "pending", policy: "Water", due }, NOW, S)).toBe(
      "Escalation Water sends in 3 min unless someone acknowledges",
    );
    expect(stateText({ state: "escalating", phase: "sent", policy: "Water" }, NOW, S)).toBe(
      "Escalation Water was sent, nobody acknowledged yet",
    );
    expect(stateText({ state: "reminding", policy: "Nag", due }, NOW, S)).toBe("Reminding (Nag), next in 3 min");
    expect(stateText({ state: "snoozed", until: due }, NOW, S)).toBe("Snoozed, back in 3 min");
    expect(stateText({ state: "held", policy: "Digest" }, NOW, S)).toBe("In the summary of Digest");
    expect(stateText({ state: "acknowledged" }, NOW, S)).toBe("Acknowledged");
  });

  it("words each kind of log entry", () => {
    const e = (kind, detail, severity) => ({ kind, detail, severity });
    expect(logText(e("created", "banner,push", "critical"), S)).toBe("Created (Critical, Banner, Push)");
    expect(logText(e("acknowledged", "Anna"), S)).toBe("Acknowledged by Anna");
    expect(logText(e("acknowledged", null), S)).toBe("Acknowledged");
    expect(logText(e("dismissed", "Ben"), S)).toBe("Dismissed by Ben");
    expect(logText(e("snoozed", null), S)).toBe("Snoozed");
    expect(logText(e("unsnoozed", "Ben"), S)).toBe("Snooze ended for Ben");
    expect(logText(e("escalation_sent", "Water"), S)).toBe("Escalation sent: Water");
    expect(logText(e("reminder_sent", "Nag"), S)).toBe("Reminder sent: Nag");
    expect(logText(e("summary_sent", "push|3"), S)).toBe("Summary sent on Push (3 messages)");
    expect(logText(e("skipped", "push|no_usable_device"), S)).toBe("Skipped on Push: no usable device");
    expect(logText(e("failed", "speak|send_failed"), S)).toBe("Failed on Speak: sending failed");
    expect(logText(e("cleared", "admin"), S)).toBe("Cleared (cleared by an admin)");
    expect(logText(e("cleared", "cleared"), S)).toBe("Cleared");
    expect(logText(e("cleared", null), S)).toBe("Cleared");
    expect(logText(e("expired", null), S)).toBe("Expired");
    expect(logText(e("fallback_sent", "Backup"), S)).toBe("Fallback sent: Backup");
  });

  it("words each needs-attention item and falls back to the code for an unknown reason", () => {
    expect(attentionText({ kind: "rule_entity", subject: "Window", detail: "binary_sensor.w" }, S)).toBe(
      "Rule Window watches binary_sensor.w, which is unavailable.",
    );
    expect(attentionText({ kind: "policy_invalid", subject: "Odd", detail: "unknown_type" }, S)).toBe(
      "Policy Odd is invalid: unknown policy type.",
    );
    expect(reasonText("something_new", S)).toBe("something_new");
    expect(reasonText(null, S)).toBe("");
  });

  it("has every log, attention, reason and result key in every language", () => {
    const keys = Object.keys(STRINGS.en.shared).sort();
    const reasons = Object.keys(STRINGS.en.shared.reason).sort();
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(Object.keys(language.shared).sort(), code).toEqual(keys);
      expect(Object.keys(language.shared.reason).sort(), code).toEqual(reasons);
      expect(Object.keys(language.shared.result).sort(), code).toEqual(Object.keys(STRINGS.en.shared.result).sort());
    }
  });
});

describe("overview functions", () => {
  it("lists only the badges that occur, in a fixed order", () => {
    expect(badgeList({ escalating: 0, reminding: 2, snoozed: 1, held: 0, acknowledged: 3 })).toEqual([
      { key: "reminding", n: 2 },
      { key: "snoozed", n: 1 },
      { key: "acknowledged", n: 3 },
    ]);
    expect(badgeList(undefined)).toEqual([]);
  });

  it("draws one bar per hour, stacked by severity with the least severe at the bottom", () => {
    const buckets = Array.from({ length: 24 }, () => ({ total: 0, by: {} }));
    buckets[23] = { total: 4, by: { critical: 1, info: 3 } };
    buckets[10] = { total: 2, by: { warning: 2 } };
    const model = chartModel({ buckets, total: 6, peak: 4 }, { width: 600, height: 120, gap: 6, minimum: 5 });
    expect(model.bars).toHaveLength(24);
    expect(model.barWidth).toBeCloseTo((600 - 6 * 23) / 24);
    const last = model.bars[23];
    expect(last.height).toBe(120);
    expect(last.segments.map((seg) => seg.severity)).toEqual(["info", "critical"]);
    expect(last.segments[0].h).toBeCloseTo(90);
    expect(last.segments[1].y).toBeCloseTo(0);
    expect(model.bars[10].height).toBe(60);
    expect(model.bars[0]).toMatchObject({ empty: true, height: 5, segments: [] });
    expect(model.bars[23].hoursAgo).toBe(0);
    expect(model.bars[0].hoursAgo).toBe(23);
  });

  it("draws a flat chart when there is no history", () => {
    expect(chartModel(undefined).bars).toEqual([]);
    const flat = chartModel({ buckets: Array.from({ length: 24 }, () => ({ total: 0, by: {} })), total: 0 });
    expect(flat.bars.every((bar) => bar.empty)).toBe(true);
  });

  it("words a bar for the tooltip, with the right plural, in every language", () => {
    for (const [code, language] of Object.entries(OVERVIEW_STRINGS)) {
      for (const key of ["chart_title", "chart_one", "chart_many", "chart_empty", "chart_start", "chart_now", "chart_tip_ago", "chart_tip_now", "chart_label"]) {
        expect(language[key], `${code} ${key}`).toBeTruthy();
      }
    }
    const t = OVERVIEW_STRINGS.en;
    expect(barTip({ total: 1, hoursAgo: 0 }, t)).toBe("1 message · last hour");
    expect(barTip({ total: 3, hoursAgo: 5 }, t)).toBe("3 messages · 5 h ago");
  });

  it("names the button text key of a fix page", () => {
    expect(fixKey("policies")).toBe("fix_policies");
  });

  it("has a text for every fix page of the attention items", () => {
    for (const language of Object.values(OVERVIEW_STRINGS)) {
      for (const page of ["recipients", "rules", "policies", "general", "messages"]) expect(language[fixKey(page)]).toBeTruthy();
    }
  });

  it("has the same keys in every language", () => {
    for (const strings of [OVERVIEW_STRINGS, MESSAGES_STRINGS]) {
      const keys = Object.keys(strings.en).sort();
      for (const language of Object.values(strings)) expect(Object.keys(language).sort()).toEqual(keys);
    }
  });
});

describe("messages functions", () => {
  const t = MESSAGES_STRINGS.en;

  it("counts delivery results in a fixed order", () => {
    const t = MESSAGES_STRINGS.en;
    expect(resultsLine({ skipped: 1, sent: 2 }, t)).toBe("2 sent, 1 skipped");
    expect(resultsLine({}, t)).toBe("");
    expect(resultsLine(undefined, t)).toBe("");
  });

  it("names a phone, and shows a short id for a phone that is gone", () => {
    const label = (value) => ({ "person.anna": "Anna", abc123: "Anna's phone" })[value] || value;
    expect(recipientName("device:abc123", label, t)).toBe("Anna's phone");
    expect(recipientName("device:4ED34B13-6E36", label, t)).toBe("Unknown phone (4ED3)");
    expect(recipientName("person.anna", label, t)).toBe("Anna");
    expect(recipientName(null, label, t)).toBe("");
  });

  it("groups the entries of one send by channel, result and reason", () => {
    const label = (value) => value;
    const at = (time, channel, recipient, result, reason) => ({ time, channel, recipient, result, reason });
    const groups = groupEntries(
      [
        at("2026-11-01T12:00:10Z", "push", "person.a", "skipped", "presence_unknown"),
        at("2026-11-01T12:00:09Z", "push", "person.b", "skipped", "presence_unknown"),
        at("2026-11-01T12:00:08Z", "push", "device:x1", "sent", null),
        at("2026-11-01T12:00:07Z", "push", "device:x2", "sent", null),
        at("2026-11-01T12:00:06Z", "banner", null, "sent", null),
        at("2026-10-31T12:00:00Z", "push", "device:x1", "sent", null),
      ],
      label,
      t,
    );
    expect(groups.map((g) => [g.channel, g.result, g.recipients])).toEqual([
      ["push", "skipped", ["person.a", "person.b"]],
      ["push", "sent", ["Unknown phone (x1)", "Unknown phone (x2)"]],
      ["banner", "sent", []],
      ["push", "sent", ["Unknown phone (x1)"]],
    ]);
  });

  it("labels an active or ended message", () => {
    const t = MESSAGES_STRINGS.en;
    expect(statusLabel({ active: true }, t, S, reasonText)).toBe("active");
    expect(statusLabel({ active: false, reason: "expired" }, t, S, reasonText)).toBe("ended (expired)");
    expect(statusLabel({ active: false, reason: null }, t, S, reasonText)).toBe("ended (?)");
  });
});

describe("settings wording equals the integration's options screen (D-122)", () => {
  const dir = new URL("../../custom_components/heads_up/", import.meta.url);
  const files = { en: "strings.json", de: "translations/de.json", fr: "translations/fr.json", es: "translations/es.json" };
  const SECTIONS = ["sidebar", "dismiss", "snooze", "snooze_banner", "snooze_push", "presence", "speech", "limits", "history"];

  for (const [code, file] of Object.entries(files)) {
    it(`uses the same section names, labels and hints in ${code}`, () => {
      const json = JSON.parse(readFileSync(new URL(file, dir), "utf8"));
      const init = json.options.step.init;
      const t = SETTINGS_STRINGS[code];
      expect(Object.keys(init.sections)).toEqual(SECTIONS);
      for (const name of SECTIONS) {
        const section = init.sections[name];
        expect(t.names[name], `${code} ${name}`).toBe(section.name);
        if (section.description) expect(t.desc[name], `${code} ${name} description`).toBe(section.description);
        for (const key of Object.keys(section.data)) {
          expect(t.label[key], `${code} ${key} label`).toBe(section.data[key]);
          expect(t.hint[key], `${code} ${key} hint`).toBe(section.data_description[key]);
        }
      }
      expect(init.description).toContain(t.label.install_token);
      expect(init.description).toContain(t.hint.install_token);
      expect(t.scope).toEqual(json.selector.dismiss_scope.options);
      expect(t.scope).toEqual(json.selector.snooze_scope.options);
      expect(t.minutes).toEqual(json.selector.snooze_minutes.options);
    });
  }

  it("has the same nested keys in every language", () => {
    for (const part of ["names", "label", "hint", "scope", "minutes", "units"]) {
      const keys = Object.keys(SETTINGS_STRINGS.en[part]).sort();
      for (const language of Object.values(SETTINGS_STRINGS)) expect(Object.keys(language[part]).sort()).toEqual(keys);
    }
  });

  it("words a timer row by its policy type", () => {
    const t = MESSAGES_STRINGS.en;
    expect(timerName({ type: "escalation", policy: "Water" }, t)).toBe("Escalation Water");
    expect(timerName({ type: "reminder", policy: "Water" }, t)).toBe("Reminder Water");
    expect(timerName({ type: "deliver", policy: "Critical delivery" }, t)).toBe("Delivery Critical delivery");
    expect(timerName({ type: "summarize", policy: "Evening" }, t)).toBe("Evening");
    expect(MESSAGES_STRINGS.de.timer_deliver && MESSAGES_STRINGS.fr.timer_deliver && MESSAGES_STRINGS.es.timer_deliver).toBeTruthy();
  });
});

describe("recipient labels", () => {
  const choices = {
    persons: [{ id: "person.anna", name: "Anna" }],
    registrations: [
      { id: "CF4A4B33-F09E-427E-BE65-3CFC768209E7", name: "Anna's phone" },
      { id: "C06734F2-5594-55A7-B578-237337248192", name: "Tablet" },
      { id: "DB21AB31-DA6A-4A56-9AD3-DDA5D1C62FE8", name: "Tablet" },
    ],
    speaker_names: { "media_player.kitchen": "Kitchen speaker", "media_player.hall": "media_player.hall" },
    areas: [{ id: "living_room", name: "Living Room" }],
  };

  it("names a person, a phone, a speaker and an area instead of showing an id", () => {
    expect(recipientLabel("person.anna", choices)).toBe("Anna");
    expect(recipientLabel("CF4A4B33-F09E-427E-BE65-3CFC768209E7", choices)).toBe("Anna's phone");
    expect(recipientLabel("media_player.kitchen", choices)).toBe("Kitchen speaker (media_player.kitchen)");
    expect(recipientLabel("living_room", choices)).toBe("Living Room");
  });

  it("tells phones with the same name apart and keeps unknown values as they are", () => {
    expect(recipientLabel("C06734F2-5594-55A7-B578-237337248192", choices)).toBe("Tablet (C067)");
    expect(recipientLabel("DB21AB31-DA6A-4A56-9AD3-DDA5D1C62FE8", choices)).toBe("Tablet (DB21)");
    expect(recipientLabel("media_player.hall", choices)).toBe("media_player.hall");
    expect(recipientLabel("Global address", choices)).toBe("Global address");
    expect(recipientLabel("Ground floor (group)", choices)).toBe("Ground floor (group)");
  });
});

describe("recipient profile enabled switch", () => {
  const base = { devices: [], removed: [], primary: "", channels: ["banner", "push", "popup"], mail_address: "" };

  it("reads enabled from the profile and treats a missing value as on", () => {
    expect(profileValues({ ...base, enabled: false }).enabled).toBe(false);
    expect(profileValues({ ...base, enabled: true }).enabled).toBe(true);
    expect(profileValues({ ...base }).enabled).toBe(true);
  });

  it("is not a default profile when it is off, so it is stored", () => {
    expect(isDefault({ manual: [], removed: [], primary: "", mail_address: "", channels: ["banner", "push", "popup"], enabled: true })).toBe(true);
    expect(isDefault({ manual: [], removed: [], primary: "", mail_address: "", channels: ["banner", "push", "popup"], enabled: false })).toBe(false);
  });

  it("sends enabled only when it is off", () => {
    const values = { manual: [], removed: [], primary: "", mail_address: "", channels: ["push"], enabled: false };
    expect(toProfileData("person.anna", values, true).enabled).toBe(false);
    expect("enabled" in toProfileData("person.anna", { ...values, enabled: true }, true)).toBe(false);
  });
});

describe("keys are shown by name (D-199)", () => {
  const choices = {
    areas: [{ id: "kitchen", name: "Kitchen" }],
    group_labels: { "group:G1": "Ground floor" },
    audience_choices: [{ id: "A1", name: "Parents" }, { id: "at_home", name: "At home" }],
  };
  it("names a stored group and area by their current name", () => {
    expect(recipientLabel("group:G1", choices)).toBe("Ground floor (group)");
    expect(recipientLabel("area:kitchen", choices)).toBe("Kitchen");
    expect(recipientLabel("kitchen", choices)).toBe("Kitchen");
  });
  it("names an audience key, and shows what a missing reference said", () => {
    expect(audienceLabel("A1", choices)).toBe("Parents");
    expect(audienceLabel("at_home", choices)).toBe("At home");
    expect(audienceLabel("name:Old", choices)).toBe("Old");
  });
});
