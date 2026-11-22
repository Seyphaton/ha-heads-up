import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

// Clock times in the tests are UTC, whatever the machine's zone is.
process.env.TZ = "UTC";
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
  entriesOf,
  headingOf,
  fill,
  historyLine,
  joinDuration,
  problems,
  rangesOf,
  sizeText,
  splitDuration,
  STRINGS as SETTINGS_STRINGS,
  ttsEntities,
  volumeProblems,
} from "../../custom_components/heads_up/frontend/panel/settings.js";

describe("panel navigation", () => {
  it("has the five groups of the specification in order", () => {
    expect(NAV.map((g) => g.id)).toEqual(["overview", "configuration", "watch", "settings", "tests", "faq"]);
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
    expect(pageFromPath("/settings")).toBe("general");
    expect(pageFromPath("/configuration")).toBe("channels");
    expect(pageFromPath("/faq")).toBe("faq");
    expect(pageFromPath("/watch")).toBe("rules");
    expect(pageFromPath("/tests")).toBe("test");
    expect(pageFromPath("/notifications")).toBe("test"); // a bookmark of an earlier version
  });

  it("shows a second row only for a group with more than one page", () => {
    expect(secondRow("audiences")).toEqual(["channels", "audiences", "recipients", "policies", "severities"]);
    expect(secondRow("test")).toEqual(["test", "messages"]);
    expect(secondRow("rules")).toEqual([]);
    expect(secondRow("general")).toEqual([]);
    expect(secondRow("status")).toEqual([]);
    expect(secondRow("faq")).toEqual(["faq", "examples", "card", "policy-help"]);
    expect(secondRow("card")).toEqual(["faq", "examples", "card", "policy-help"]);
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

  it("fills placeholders", () => {
    expect(fill("{n} of {total}", { n: 1, total: 2 })).toBe("1 of 2");
  });
});

import {
  attentionText,
  inTime,
  logText,
  reasonText,
  reasonHint,
  stateText,
  timeAgo,
} from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import {
  barTip,
  bucketLabel,
  cellDetail,
  cellLabel,
  CELL_STATES,
  chartModel,
  comingText,
  contextLines,
  countText,
  durationText,
  fixKey,
  kpiModel,
  matrixModel,
  PERIODS,
  actionRow,
  shortcutCards,
  sourceRows,
  clockText,
  entryWho,
  pathEvents,
  statusHeadline,
  statusPills,
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
    const ghost = { kind: "reference_missing", subject: "Test title", detail: "01M7FJ294WW05K4M9FKCH2WMYZ" };
    const forMessage = attentionText({ ...ghost, page: "messages" }, S);
    expect(forMessage).toContain("The message \"Test title\" names a policy that was deleted");
    expect(forMessage).not.toContain("01M7FJ");
    expect(attentionText({ ...ghost, subject: "Door", page: "rules" }, S)).toContain("Edit the rule and choose another policy");
    expect(reasonText("something_new", S)).toBe("something_new");
    expect(reasonText(null, S)).toBe("");
    expect(reasonHint("no_tts_engine", S)).toContain("Settings > Speech");
    expect(reasonHint("quiet_hours", S)).toBe("");
    expect(reasonHint(null, S)).toBe("");
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
  const afmt0 = { reasonText: (code) => `r:${code}`, channelName: (c) => `ch:${c}` };
  const fmt = { inTime: (iso) => `in(${iso})`, reasonText: (code) => `r:${code}`, channelName: (c) => `ch:${c}` };
  const sh = { channel: { push: "Push" }, severity: { critical: "Critical" }, result: { sent: "sent", skipped: "skipped", acknowledged: "acknowledged" } };
  const t = OVERVIEW_STRINGS.en;

  it("words the status headline for none, one and many", () => {
    expect(statusHeadline(0, t)).toBe(t.status_clear);
    expect(statusHeadline(1, t)).toBe(t.status_one);
    expect(statusHeadline(3, t)).toBe("3 notifications need you");
  });

  it("lists the severities of the status pills, critical first", () => {
    const sh2 = { severity: { critical: "Critical", warning: "Warning" } };
    expect(statusPills([{ severity: "warning" }, { severity: "critical" }, { severity: "warning" }], sh2)).toEqual([
      { severity: "critical", text: "1 Critical" },
      { severity: "warning", text: "2 Warning" },
    ]);
    expect(statusPills([], sh2)).toEqual([]);
  });

  it("words a duration in seconds, minutes, and hours with minutes", () => {
    expect(durationText(45, t)).toBe("45 s");
    expect(durationText(210, t)).toBe("4 min");
    expect(durationText(3900, t)).toBe("1 h 5 min");
    expect(durationText(null, t)).toBe(t.kpi_none);
  });

  it("builds the four numbers and a pill for the change", () => {
    const model = kpiModel({ notifications: 12, change: 20, delivered: 80, median_ack_seconds: 210, held_quiet: 3 }, t);
    expect(model).toMatchObject({ notifications: "12", delivered: "80 %", median: "4 min", held: "3" });
    expect(model.change).toEqual({ up: true, text: "+20% against the period before" });
    expect(kpiModel({ notifications: 1, change: -5, delivered: null, median_ack_seconds: null, held_quiet: 0 }, t).change.text).toBe("-5% against the period before");
    const none = kpiModel({ notifications: 0, change: null, delivered: null, median_ack_seconds: null, held_quiet: 0 }, t);
    expect(none.change).toBeNull();
    expect(none.delivered).toBe(t.kpi_none);
  });

  it("scales the weekday grid to its busiest cell and hides it without data", () => {
    expect(matrixModel(null)).toBeNull();
    const grid = matrixModel([[0, 4], [2, 0]]);
    expect(grid.peak).toBe(4);
    expect(grid.total).toBe(6);
    expect(grid.rows[0][1]).toEqual({ n: 4, share: 1 });
    expect(grid.rows[1][0].share).toBe(0.5);
  });

  it("names the top sources with their kind and scales their bars", () => {
    const rows = sourceRows(
      [
        { kind: "rule", name: "Garage door", count: 10 },
        { kind: "id", name: "water_leak", count: 5 },
        { kind: "tag", name: "door", count: 4 },
        { kind: "test", name: null, count: 3 },
        { kind: "rule", name: null, count: 2 },
        { kind: "action", name: null, count: 1 },
      ],
      t,
    );
    expect(rows.map((r) => [r.text, r.kind])).toEqual([
      ["Garage door", "Watch rule"],
      ["water_leak", "Call"],
      ["door", "Tag"],
      [t.source_test, ""],
      [t.source_gone, "Watch rule"],
      [t.source_other, ""],
    ]);
    expect(rows.map((r) => r.share)).toEqual([1, 0.5, 0.4, 0.3, 0.2, 0.1]);
    expect(sourceRows([], t)).toEqual([]);
  });

  const item = (extra = {}) => ({
    id: "water_leak",
    title: null,
    message: "Water in the cellar",
    severity: "critical",
    source: { kind: "action", name: null },
    time: "2026-11-21T18:00:00Z",
    state: "ended",
    end_reason: "expired",
    results: { sent: 3, skipped: 1 },
    problems: [{ reason: "no_usable_device", count: 1 }],
    failed_on: [],
    held_by: [],
    acknowledged: null,
    escalated: 0,
    reminded: 0,
    ...extra,
  });
  const afmt = { timeAgo: () => "2 min ago", reasonText: (c) => `r:${c}`, channelName: (c) => `ch:${c}` };

  it("builds a row from a message: headline, source, outcome and state", () => {
    const row = actionRow(item(), 0, t, sh, afmt);
    expect(row).toMatchObject({ text: "Water in the cellar", source: "water_leak", when: "2 min ago", state: "Ended: r:expired", stateKind: "ended" });
    expect(row.outcome).toBe("3 sent · 1 skipped (r:no_usable_device)");
    expect(row.chips).toEqual([]);
    expect(actionRow(item({ title: "Leak" }), 0, t, sh, afmt).text).toBe("Leak");
  });

  it("names where a message came from: a rule, a made-up ID, a test", () => {
    expect(actionRow(item({ source: { kind: "rule", name: "Garage" } }), 0, t, sh, afmt).source).toBe("Watch rule Garage");
    expect(actionRow(item({ source: { kind: "rule", name: null } }), 0, t, sh, afmt).source).toBe(`Watch rule ${t.source_gone}`);
    expect(actionRow(item({ id: "hu_0123456789" }), 0, t, sh, afmt).source).toBe(t.act_source_action);
    expect(actionRow(item({ id: "hu_test_ab12cd34" }), 0, t, sh, afmt).source).toBe(t.source_test);
  });

  it("adds who acknowledged and how long it took", () => {
    const base = { results: { sent: 2 }, problems: [], state: "acknowledged" };
    expect(actionRow(item({ ...base, acknowledged: { by: "Anna", seconds: 240 } }), 0, t, sh, afmt).outcome).toBe("2 sent · acknowledged by Anna after 4 min");
    expect(actionRow(item({ ...base, acknowledged: { by: null, seconds: 45 } }), 0, t, sh, afmt).outcome).toBe("2 sent · acknowledged after 45 s");
    expect(actionRow(item({ ...base, acknowledged: { by: "Ben", seconds: null } }), 0, t, sh, afmt).outcome).toBe("2 sent · acknowledged by Ben");
    expect(actionRow(item({ ...base, acknowledged: { by: null, seconds: null } }), 0, t, sh, afmt).outcome).toBe("2 sent · acknowledged");
  });

  it("says when nothing was delivered and lists the chips", () => {
    const row = actionRow(item({ results: {}, problems: [], escalated: 1, reminded: 3, held_by: ["Night"], failed_on: ["mail"], state: "active" }), 0, t, sh, afmt);
    expect(row.outcome).toBe(t.act_nothing);
    expect(row.chips).toEqual(["Escalated", "3 reminders", "Held by Night", "Failed on ch:mail"]);
    expect(row.state).toBe("Active");
    expect(actionRow(item({ reminded: 1 }), 0, t, sh, afmt).chips).toEqual(["1 reminder"]);
  });

  it("labels a bar of a longer period with a day or a month and keeps the hourly wording", () => {
    expect(barTip({ total: 2, start: "2026-11-21", hoursAgo: 0 }, t, "week", "en")).toMatch(/^Nov 21 · 2 messages$/);
    expect(barTip({ total: 1, start: "2026-10-01", hoursAgo: 3 }, t, "year", "en")).toMatch(/^Oct 2026 · 1 message$/);
    expect(bucketLabel("nonsense", "week", "en")).toBe("");
    expect(barTip({ total: 3, hoursAgo: 5 }, t, "24h", "en")).toBe("3 messages · 5 h ago");
  });

  it("has a name for every period in every language", () => {
    for (const [code, language] of Object.entries(OVERVIEW_STRINGS)) for (const period of PERIODS) expect(language[`period_${period}`], `${code}.${period}`).toBeTruthy();
    expect(OVERVIEW_STRINGS.en.period_2y).toBe("2 years");
  });

  it("builds the four shortcut links with their page and title", () => {
    expect(shortcutCards(t)).toEqual([
      { page: "channels", title: "Channels" },
      { page: "audiences", title: "Audiences" },
      { page: "policies", title: "Policies" },
      { page: "rules", title: "Watch rules" },
    ]);
  });

  it("counts messages with the right plural", () => {
    expect(countText(1, t)).toBe("1 message");
    expect(countText(2, t)).toBe("2 messages");
  });

  it("words a Coming up entry with its policy, time and count", () => {
    const text = comingText({ kind: "escalation", policy: "Water", time: "T", count: 2 }, 0, t, sh, fmt);
    expect(text).toBe("Escalation Water: in(T) · 2 messages");
    expect(comingText({ kind: "quiet_release", policy: "", time: "T", count: 1 }, 0, t, sh, fmt)).toBe("Held by quiet hours, sent in(T) · 1 message");
  });

  it("shows a count in a cell only when the people differ", () => {
    expect(cellLabel({ state: "sound", count: 3, total: 3 }, t)).toEqual({ word: "Sound", count: null });
    expect(cellLabel({ state: "shown", count: 2, total: 3 }, t)).toEqual({ word: "Shown", count: "2 of 3" });
    expect(cellLabel({ state: "not_set_up", count: 0, total: 0 }, t)).toEqual({ word: "Not set up", count: null });
  });

  it("has a word and a sentence for every cell state in every language", () => {
    for (const [code, language] of Object.entries(OVERVIEW_STRINGS)) {
      for (const state of CELL_STATES) {
        expect(language[`cell_${state}`], `${code} ${state}`).toBeTruthy();
        expect(language[`sentence_${state}`], `${code} ${state}`).toBeTruthy();
      }
    }
  });

  it("describes a cell with the people and their reasons", () => {
    const cell = { state: "shown", count: 1, total: 2, reason: null, who: [{ name: "Anna", state: "shown", reason: null }, { name: "Ben", state: "held", reason: "quiet_hours" }] };
    const detail = cellDetail(cell, "push", "critical", t, sh, fmt);
    expect(detail.title).toBe("Push, Critical: Shown, 1 of 2");
    expect(detail.sentence).toBe(t.sentence_shown);
    expect(detail.people).toEqual(["Anna: Shown", "Ben: Waits (r:quiet_hours)"]);
    const none = cellDetail({ state: "skipped", count: 0, total: 0, reason: "no_recipients", who: [] }, "push", "critical", t, sh, fmt);
    expect(none.reason).toBe("r:no_recipients");
    expect(none.empty).toBe(t.reach_nobody);
  });

  it("lists the context: time, quiet hours, who is away and each summary", () => {
    const context = {
      now: "2026-11-02T22:30:00Z",
      quiet: { policies: ["Night"], until: "2026-11-03T06:00:00Z" },
      away: ["Ben"],
      summaries: [{ policy: "Digest", tags: ["digest"], due: "D" }, { policy: "All", tags: [], due: "E" }],
    };
    const lines = contextLines(context, 0, t, sh, fmt, "en");
    expect(lines).toHaveLength(5);
    expect(lines[1]).toMatch(/^Quiet hours until /);
    expect(lines[2]).toBe("Away: Ben.");
    expect(lines[3]).toBe("Messages tagged digest wait for the summary Digest, in(D).");
    expect(lines[4]).toBe("Messages wait for the summary All, in(E).");
    expect(contextLines({ now: context.now, quiet: { policies: ["Night"], until: null }, away: [], summaries: [] }, 0, t, sh, fmt, "en")[1]).toBe(t.reach_quiet_open);
    expect(contextLines(null, 0, t, sh, fmt, "en")).toEqual([]);
  });

  const T = (hhmm) => `2026-11-21T${hhmm}:00Z`;
  const ev = (entries, extra = {}) =>
    pathEvents(entries, {
      t,
      s: { ...sh, result: { sent: "sent", skipped: "skipped", held: "held", failed: "failed", cleared: "cleared" } },
      fmt: { reasonText: (c) => `r:${c}`, channelName: (c) => `ch:${c}` },
      who: (e) => `who:${e.person || e.recipient}`,
      now: Date.parse(T("14:00")),
      locale: "en-GB",
      ...extra,
    });
  const times = (list) => list.map((e) => e.text.match(/\d\d:\d\d/)?.[0]);

  it("lists what happened newest first, one event per moment, with its channels", () => {
    const entries = [
      { channel: "", result: "acknowledged", who: "Ben", time: T("13:58") },
      { channel: "push", result: "sent", origin: "reminder", time: T("13:57") },
      { channel: "banner", result: "sent", origin: "reminder", time: T("13:57") },
      { channel: "speak", result: "sent", origin: "reminder", time: T("13:57") },
      { channel: "banner", result: "sent", origin: "message", time: T("13:47") },
      { channel: "push", result: "sent", origin: "message", time: T("13:47") },
    ].reverse();
    const events = ev(entries);
    expect(events.map((e) => e.text)).toEqual([
      "Acknowledged by Ben at 13:58",
      "Reminder sent at 13:57 (ch:banner, ch:push, ch:speak)",
      "Sent at 13:47 (ch:banner, ch:push)",
    ]);
    expect(events.map((e) => e.kind)).toEqual(["note", "ok", "ok"]);
  });

  it("says when a send went out silently and which policy made it quiet", () => {
    const [event] = ev([{ channel: "push", result: "sent", origin: "message", by: "Night quiet", time: T("13:47") }]);
    expect(event.text).toBe("Sent at 13:47 (ch:push) · silently due to Night quiet");
    const [mixed] = ev([
      { channel: "push", result: "sent", origin: "message", by: "Night quiet", time: T("13:47") },
      { channel: "banner", result: "sent", origin: "message", time: T("13:47") },
    ].reverse());
    expect(mixed.text).toBe("Sent at 13:47 (ch:banner, ch:push) · ch:push silently (Night quiet)");
  });

  it("shows a message held for a summary and the summary that sent it", () => {
    const events = ev([
      { channel: "push", result: "summarized", origin: "summary", by: "Evening summary", time: T("20:00") },
      { channel: "banner", result: "summarized", origin: "summary", by: "Evening summary", time: T("20:00") },
      { channel: "", result: "held", reason: "summarize", by: "Evening summary", time: T("13:47") },
    ].reverse(), { now: Date.parse(T("20:30")) });
    expect(events.map((e) => e.text)).toEqual(["Summary sent at 20:00 (ch:banner, ch:push) · Evening summary", "Held for summary (Evening summary) at 13:47"]);
    expect(events[1].kind).toBe("hold");
  });

  it("shows a failed delivery as an event of its own with the reason", () => {
    const events = ev([
      { channel: "push", result: "sent", origin: "message", time: T("13:47") },
      { channel: "mail", result: "failed", reason: "no_mail_service", origin: "message", time: T("13:47") },
      { channel: "speak", result: "failed", reason: "no_tts_engine", origin: "message", time: T("13:47") },
    ].reverse());
    const failed = events.filter((e) => e.kind === "fail");
    expect(failed.map((e) => e.text)).toEqual(["Failed at 13:47 (ch:mail): r:no_mail_service", "Failed at 13:47 (ch:speak): r:no_tts_engine"]);
    expect(events.find((e) => e.kind === "ok").text).toBe("Sent at 13:47 (ch:push)");
  });

  it("shows held and not sent deliveries with the reason and the policy", () => {
    const events = ev([
      { channel: "push", result: "held", reason: "quiet_hours", by: "Night", origin: "message", time: T("13:47") },
      { channel: "mail", result: "skipped", reason: "no_mail_address", origin: "message", time: T("13:47") },
      { channel: "popup", result: "skipped", reason: "quiet_hours", by: "Night", origin: "message", time: T("13:47") },
    ].reverse());
    expect(events.map((e) => e.text).sort()).toEqual([
      "Held at 13:47 (ch:push) · Night",
      "Not sent at 13:47 (ch:mail): r:no_mail_address",
      "Not sent at 13:47 (ch:popup): r:quiet_hours · Night",
    ]);
  });

  it("puts who each line was for into the hover text", () => {
    const [event] = ev([
      { channel: "push", result: "sent", person: "person.anna", recipient: "device:a1", time: T("13:47") },
      { channel: "push", result: "sent", person: "person.anna", recipient: "device:a2", time: T("13:47") },
    ].reverse());
    expect(event.title).toBe("who:person.anna: sent\nwho:person.anna: sent");
  });

  it("starts a new event after 90 seconds and for another origin, and ignores timer entries", () => {
    const events = ev([
      { channel: "push", result: "sent", origin: "reminder", time: "2026-11-21T13:58:30Z" },
      { channel: "timer", result: "sent", time: T("13:58") },
      { channel: "push", result: "sent", origin: "escalation", time: T("13:57") },
      { channel: "push", result: "sent", origin: "message", time: "2026-11-21T13:47:50Z" },
      { channel: "banner", result: "sent", origin: "message", time: T("13:47") },
    ].reverse());
    expect(events.map((e) => e.text.split(" at ")[0])).toEqual(["Reminder sent", "Escalation sent", "Sent"]);
  });

  it("shows only the steps since the message appeared", () => {
    const entries = [
      { channel: "push", result: "sent", time: T("13:50") },
      { channel: "push", result: "cleared", time: "2026-11-18T10:00:00Z" },
      { channel: "push", result: "sent", time: "2026-11-18T09:00:00Z" },
    ];
    expect(ev(entries, { since: T("13:00") })).toHaveLength(1);
    expect(ev(entries)).toHaveLength(3);
    expect(times(ev(entries, { since: T("13:00") }))).toEqual(["13:50"]);
  });

  it("adds the date to an event that is not from today", () => {
    expect(clockText("2026-11-18T10:00:00Z", Date.parse(T("14:00")), "en-GB")).toMatch(/^18 Nov \d\d:\d\d$/);
    expect(clockText(T("13:47"), Date.parse(T("14:00")), "en-GB")).toBe("13:47");
  });

  it("names who an entry was for: the person and the phone, the phone, the person, or a dash", () => {
    const label = (v) => ({ "person.anna": "Anna", a1: "iPhone" })[v] || v;
    expect(entryWho({ person: "person.anna", recipient: "device:a1" }, {}, label)).toBe("Anna (iPhone)");
    expect(entryWho({ person: null, recipient: "device:a1" }, {}, label)).toBe("iPhone");
    expect(entryWho({ person: "person.anna", recipient: "" }, {}, label)).toBe("Anna");
    expect(entryWho({ person: null, recipient: "" }, {}, label)).toBe("—");
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

  it("has no key twice in a language of the Overview strings (the later one would hide the first)", () => {
    const source = readFileSync("custom_components/heads_up/frontend/panel/overview.js", "utf8");
    for (const lang of ["en", "de", "fr", "es"]) {
      const block = source.match(new RegExp(`\\n  ${lang}: \\{\\n([\\s\\S]*?)\\n  \\},`))[1];
      const keys = [...block.matchAll(/^ {4}(\w+):/gm)].map((m) => m[1]);
      expect(keys.filter((k, i) => keys.indexOf(k) !== i), lang).toEqual([]);
    }
  });

  it("defines every function the page calls (a missing startTour made the first load fail)", () => {
    const source = readFileSync("custom_components/heads_up/frontend/panel/overview.js", "utf8");
    const defined = new Set([...source.matchAll(/(?:async\s+)?function\s+(\w+)\(/g)].map((m) => m[1]).concat([...source.matchAll(/\bconst\s+(\w+)\s*=/g)].map((m) => m[1])));
    for (const name of ["startTour", "load", "loadStats", "togglePath", "pathNode", "pathButton", "act", "statusCard", "attentionCard", "comingCard", "lastActionsCard", "reachCard", "activityCards", "shortcutRow", "chartNode", "headed", "render"]) {
      expect(defined.has(name), name).toBe(true);
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

  it("names a timer entry by its policy and a press by the person", () => {
    const label = (value) => value;
    const groups = groupEntries(
      [
        { time: "2026-11-01T12:00:10Z", channel: "timer", recipient: "k", result: "sent", reason: "escalated", timer: { type: "escalation", policy: "Water" } },
        { time: "2026-11-01T12:00:05Z", channel: "", recipient: "Philip", result: "dismissed", reason: "", who: "Philip" },
      ],
      label,
      t,
    );
    expect(groups.map((g) => [g.channel, g.timer?.policy ?? null, g.recipients])).toEqual([
      ["timer", "Water", []],
      ["", null, ["Philip"]],
    ]);
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
    expect(statusLabel({ active: false, reason: null }, t, S, reasonText)).toBe("inactive");
  });
});

describe("volumeProblems", () => {
  const night = { from: "22:00", to: "07:00", volume: 20 };

  it("accepts bands over midnight and severity volumes", () => {
    expect(volumeProblems({ speak_volume_bands: [night, { from: "07:00", to: "09:00", volume: 50 }], speak_severity_volume: { critical: 80 } })).toEqual([]);
  });

  it("names empty, overlapping, invalid and too many bands", () => {
    expect(volumeProblems({ speak_volume_bands: [{ from: "08:00", to: "08:00", volume: 5 }] })).toEqual(["bands_empty"]);
    expect(volumeProblems({ speak_volume_bands: [night, { from: "06:00", to: "08:00", volume: 5 }] })).toEqual(["bands_overlap"]);
    expect(volumeProblems({ speak_volume_bands: [{ from: "", to: "08:00", volume: 5 }] })).toEqual(["bands_invalid"]);
    expect(volumeProblems({ speak_volume_bands: [{ ...night, volume: NaN }] })).toEqual(["bands_invalid"]);
    const five = [0, 1, 2, 3, 4].map((h) => ({ from: `0${h}:00`, to: `0${h}:30`, volume: 5 }));
    expect(volumeProblems({ speak_volume_bands: five })).toContain("bands_too_many");
    expect(volumeProblems({ speak_severity_volume: { critical: 101 } })).toEqual(["severity_volume_invalid"]);
  });
});

describe("settings wording equals the integration's options screen (D-122)", () => {
  const dir = new URL("../../custom_components/heads_up/", import.meta.url);
  const files = { en: "strings.json", de: "translations/de.json", fr: "translations/fr.json", es: "translations/es.json" };
  const SECTIONS = ["sidebar", "dismiss", "snooze", "snooze_banner", "snooze_push", "presence", "speech", "speech_volume", "limits", "history"];

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

describe("history in Settings", () => {
  it("writes the size in a unit a person reads", () => {
    expect(sizeText(900)).toBe("900 B");
    expect(sizeText(430000)).toBe("420 KB");
    expect(sizeText(5.1 * 1024 * 1024)).toBe("5.1 MB");
  });

  it("words what is stored, or that nothing is", () => {
    const t = SETTINGS_STRINGS.en;
    expect(historyLine({ days: 12, first: "2026-11-01", last: "2026-11-12", bytes: 84000 }, t)).toBe("12 days, from 2026-11-01 to 2026-11-12, about 82 KB.");
    expect(historyLine({ days: 0 }, t)).toBe(t.history_empty);
    expect(historyLine(null, t)).toBe(t.history_empty);
  });

  it("has the history texts in every language", () => {
    for (const [code, language] of Object.entries(SETTINGS_STRINGS)) {
      for (const key of ["history", "history_hint", "history_info", "history_empty", "history_clear", "history_confirm", "history_cleared", "history_failed"]) expect(language[key], `${code}.${key}`).toBeTruthy();
    }
  });
});
