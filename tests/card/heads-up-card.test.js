import { afterEach, describe, expect, it } from "vitest";
import {
  clearableIds,
  collapse,
  colorParts,
  CONFIG_KEYS,
  controlsFor,
  emptyView,
  normalizeConfig,
  reservesActionSpace,
  relativeTime,
  resolveColors,
  retryDelay,
  sortBanners,
  setLanguage,
  snoozeLabel,
  snoozedBanners,
  backInLabel,
  STRINGS,
  TRANSLATIONS,
  whenFrontendReady,
  swipeOutcome,
  visibleBanners,
} from "../../custom_components/heads_up/frontend/heads-up-card.js";

const banner = (over = {}) => ({
  id: "a",
  message: "m",
  severity: "info",
  active: true,
  dismissed: false,
  dismissible: true,
  tag: null,
  updated_at: "2026-10-25T10:00:00+00:00",
  ...over,
});

describe("normalizeConfig", () => {
  it("fills defaults", () => {
    expect(normalizeConfig({ type: "custom:heads-up-card" })).toMatchObject({
      severity: [],
      tag: [],
      max_items: null,
      sort: "severity",
      layout: "comfortable",
      show_all: false,
      show_empty: false,
    });
  });

  it("returns every key listed in CONFIG_KEYS", () => {
    const config = normalizeConfig({});
    for (const key of CONFIG_KEYS) expect(config).toHaveProperty(key);
  });

  it("accepts a single string for severity and tag", () => {
    const config = normalizeConfig({ severity: "critical", tag: "laundry" });
    expect(config.severity).toEqual(["critical"]);
    expect(config.tag).toEqual(["laundry"]);
  });

  it.each([
    [{ severity: ["urgent"] }],
    [{ sort: "name" }],
    [{ layout: "wide" }],
    [{ max_items: 0 }],
    [{ max_items: 1.5 }],
    [{ tag: [1] }],
    [null],
  ])("rejects %j", (config) => {
    expect(() => normalizeConfig(config)).toThrow(Error);
  });
});

describe("sortBanners", () => {
  const list = [
    banner({ id: "info-new", severity: "info", updated_at: "2026-10-25T12:00:00+00:00" }),
    banner({ id: "crit-old", severity: "critical", updated_at: "2026-10-25T08:00:00+00:00" }),
    banner({ id: "warn", severity: "warning", updated_at: "2026-10-25T09:00:00+00:00" }),
    banner({ id: "crit-new", severity: "critical", updated_at: "2026-10-25T11:00:00+00:00" }),
  ];

  it("orders by severity, then newest first", () => {
    expect(sortBanners(list, "severity").map((b) => b.id)).toEqual([
      "crit-new",
      "crit-old",
      "warn",
      "info-new",
    ]);
  });

  it("orders by time, newest first", () => {
    expect(sortBanners(list, "time").map((b) => b.id)).toEqual([
      "info-new",
      "crit-new",
      "warn",
      "crit-old",
    ]);
  });

  it("does not change the input", () => {
    const ids = list.map((b) => b.id);
    sortBanners(list, "severity");
    expect(list.map((b) => b.id)).toEqual(ids);
  });
});

describe("visibleBanners", () => {
  const config = (over = {}) => normalizeConfig(over);

  it("hides waiting and dismissed banners", () => {
    const list = [
      banner({ id: "ok" }),
      banner({ id: "waiting", active: false }),
      banner({ id: "dismissed", dismissed: true }),
    ];
    expect(visibleBanners(list, config()).map((b) => b.id)).toEqual(["ok"]);
  });

  it("filters by severity and tag", () => {
    const list = [
      banner({ id: "a", severity: "critical", tag: "water" }),
      banner({ id: "b", severity: "info", tag: "water" }),
      banner({ id: "c", severity: "critical", tag: "laundry" }),
    ];
    const result = visibleBanners(list, config({ severity: ["critical"], tag: ["water"] }));
    expect(result.map((b) => b.id)).toEqual(["a"]);
  });

  it("caps the list after sorting", () => {
    const list = [
      banner({ id: "info", severity: "info" }),
      banner({ id: "crit", severity: "critical" }),
    ];
    expect(visibleBanners(list, config({ max_items: 1 })).map((b) => b.id)).toEqual(["crit"]);
  });

  it("treats a missing list as empty", () => {
    expect(visibleBanners(undefined, config())).toEqual([]);
  });
});

describe("retryDelay", () => {
  it("backs off and stops growing at 30 seconds", () => {
    expect([0, 1, 2, 3, 4, 5, 50].map(retryDelay)).toEqual([1000, 2000, 5000, 10000, 30000, 30000, 30000]);
  });
});

describe("controlsFor", () => {
  it("gives dismissible banners a dismiss button and no admin clear", () => {
    expect(controlsFor(banner(), true)).toEqual({
      dismiss: true,
      adminClear: false,
      tap: false,
      snooze: false,
      actions: [],
    });
  });

  it("gives admins a clear button on banners nobody can dismiss", () => {
    const b = banner({ dismissible: false });
    expect(controlsFor(b, true)).toMatchObject({ dismiss: false, adminClear: true });
    expect(controlsFor(b, false)).toMatchObject({ dismiss: false, adminClear: false });
  });

  it("gives no admin clear button on rule banners", () => {
    const b = banner({ dismissible: false, rule: true });
    expect(controlsFor(b, true)).toMatchObject({ dismiss: false, adminClear: false });
  });

  it("marks banners with a tap action as tappable", () => {
    const b = banner({ tap_action: { action: "navigate", navigation_path: "/lovelace/0" } });
    expect(controlsFor(b, false).tap).toBe(true);
  });
});

describe("controlsFor snooze and buttons", () => {
  it("offers snooze on a snoozable, dismissible banner with choices", () => {
    expect(controlsFor(banner({ snoozable: true, snooze_options: [900] }), false).snooze).toBe(true);
  });

  it("offers no snooze without the flag, choices or dismissibility", () => {
    expect(controlsFor(banner({ snooze_options: [900] }), false).snooze).toBe(false);
    expect(controlsFor(banner({ snoozable: true, snooze_options: [] }), false).snooze).toBe(false);
    const b = banner({ snoozable: true, snooze_options: [900], dismissible: false });
    expect(controlsFor(b, false).snooze).toBe(false);
  });

  it("passes the banner's buttons through", () => {
    const actions = [{ key: "ack", label: "Got it", dismiss: true }];
    expect(controlsFor(banner({ actions }), false).actions).toEqual(actions);
  });
});

describe("snoozeLabel", () => {
  it("formats minutes, hours and days", () => {
    expect([300, 900, 3600, 14400, 5400, 86400, 172800].map(snoozeLabel)).toEqual([
      "5 min",
      "15 min",
      "1 h",
      "4 h",
      "90 min",
      "1 d",
      "2 d",
    ]);
  });
});

describe("reservesActionSpace", () => {
  it("is true when any banner has a button", () => {
    const list = [banner({ dismissible: false, rule: true }), banner()];
    expect(reservesActionSpace(list, false)).toBe(true);
  });

  it("is false when no banner has a button", () => {
    const list = [banner({ dismissible: false, rule: true }), banner({ dismissible: false })];
    expect(reservesActionSpace(list, false)).toBe(false);
    expect(reservesActionSpace([banner({ dismissible: false, rule: true })], true)).toBe(false);
  });
});

describe("normalizeConfig: design options", () => {
  it("defaults the new options", () => {
    expect(normalizeConfig({})).toMatchObject({
      title: "",
      show_time: false,
      show_severity: false,
      colors: {},
      colorize: "all",
      clear_all: false,
      swipe_to_dismiss: false,
      collapsed_items: null,
      empty_message: "",
      empty_icon: "mdi:bell-check-outline",
    });
  });

  it("keeps valid values", () => {
    const config = normalizeConfig({
      title: "Notices",
      show_time: true,
      show_severity: true,
      colors: { critical: "#c62828", info: "var(--primary-color)" },
      colorize: "icon",
      clear_all: true,
      swipe_to_dismiss: true,
      collapsed_items: 2,
      empty_message: "All clear",
      empty_icon: "mdi:check",
    });
    expect(config).toMatchObject({
      title: "Notices",
      show_time: true,
      show_severity: true,
      colorize: "icon",
      collapsed_items: 2,
      empty_icon: "mdi:check",
    });
    expect(config.colors).toEqual({ critical: "#c62828", info: "var(--primary-color)" });
  });

  it.each([
    [{ title: 5 }],
    [{ colorize: "text" }],
    [{ colors: { urgent: "red" } }],
    [{ colors: { critical: "" } }],
    [{ colors: { critical: "red; background: url(x)" } }],
    [{ colors: { critical: 5 } }],
    [{ colors: ["red"] }],
    [{ collapsed_items: 0 }],
    [{ collapsed_items: 1.5 }],
    [{ empty_message: 5 }],
    [{ empty_icon: "bell" }],
  ])("rejects %j", (config) => {
    expect(() => normalizeConfig(config)).toThrow(Error);
  });
});

describe("relativeTime", () => {
  const now = Date.parse("2026-10-25T12:00:00+00:00");
  const ago = (ms) => new Date(now - ms).toISOString();
  it.each([
    [0, "just now"],
    [59 * 1000, "just now"],
    [60 * 1000, "1 min ago"],
    [50 * 60 * 1000, "50 min ago"],
    [59 * 60 * 1000 + 59000, "59 min ago"],
    [60 * 60 * 1000, "1 h ago"],
    [23 * 3600 * 1000, "23 h ago"],
    [24 * 3600 * 1000, "1 day ago"],
    [47 * 3600 * 1000, "1 day ago"],
    [48 * 3600 * 1000, "2 days ago"],
    [40 * 24 * 3600 * 1000, "40 days ago"],
  ])("%i ms ago reads %s", (ms, text) => {
    expect(relativeTime(ago(ms), now)).toBe(text);
  });

  it("treats a time in the future or an invalid time as just now", () => {
    expect(relativeTime(new Date(now + 5000).toISOString(), now)).toBe("just now");
    expect(relativeTime("not a date", now)).toBe("just now");
  });
});

describe("collapse", () => {
  const list = [1, 2, 3, 4, 5];
  it("shows everything without a limit", () => {
    expect(collapse(list, null, false)).toEqual({ shown: list, hidden: 0 });
  });
  it("shows the first N and counts the rest", () => {
    expect(collapse(list, 2, false)).toEqual({ shown: [1, 2], hidden: 3 });
  });
  it("shows everything once expanded, and still reports how many were hidden", () => {
    expect(collapse(list, 2, true)).toEqual({ shown: list, hidden: 3 });
  });
  it("needs no button when the list fits", () => {
    expect(collapse([1, 2], 2, false)).toEqual({ shown: [1, 2], hidden: 0 });
  });
});

describe("emptyView", () => {
  it("is hidden by default", () => {
    expect(emptyView(normalizeConfig({}))).toBe("hidden");
  });
  it("is blank with show_empty", () => {
    expect(emptyView(normalizeConfig({ show_empty: true }))).toBe("blank");
  });
  it("shows the message when one is set, even without show_empty", () => {
    expect(emptyView(normalizeConfig({ empty_message: "All clear" }))).toBe("message");
    expect(emptyView(normalizeConfig({ empty_message: "All clear", show_empty: true }))).toBe(
      "message",
    );
  });
});

describe("resolveColors and colorParts", () => {
  it("falls back to the theme variables", () => {
    expect(resolveColors(normalizeConfig({}))).toEqual({
      critical: "var(--error-color)",
      warning: "var(--warning-color)",
      info: "var(--info-color)",
      success: "var(--success-color)",
    });
  });
  it("overrides single severities", () => {
    const colors = resolveColors(normalizeConfig({ colors: { warning: "#ff8800" } }));
    expect(colors.warning).toBe("#ff8800");
    expect(colors.critical).toBe("var(--error-color)");
  });
  it.each([
    ["all", { background: true, icon: true, bar: true }],
    ["background", { background: true, icon: false, bar: false }],
    ["icon", { background: false, icon: true, bar: false }],
    ["bar", { background: false, icon: false, bar: true }],
  ])("colorize %s", (value, parts) => {
    expect(colorParts(value)).toEqual(parts);
  });
});

describe("swipeOutcome", () => {
  it("cancels short or mostly vertical movements", () => {
    expect(swipeOutcome(30, 5, 400)).toBe("cancel");
    expect(swipeOutcome(150, 160, 400)).toBe("cancel");
  });
  it("dismisses after 80 px or 30% of the width, either direction", () => {
    expect(swipeOutcome(90, 4, 200)).toBe("dismiss");
    expect(swipeOutcome(-90, 4, 200)).toBe("dismiss");
    expect(swipeOutcome(90, 4, 600)).toBe("cancel"); // 30% of 600 is 180
    expect(swipeOutcome(-200, 4, 600)).toBe("dismiss");
  });
  it("opens the snooze choices on a right swipe of a snoozable banner only", () => {
    expect(swipeOutcome(90, 4, 200, true)).toBe("snooze");
    expect(swipeOutcome(-90, 4, 200, true)).toBe("dismiss");
    expect(swipeOutcome(90, 4, 200, false)).toBe("dismiss");
    expect(swipeOutcome(30, 4, 200, true)).toBe("cancel");
  });
});

describe("clearableIds", () => {
  it("lists only dismissible banners", () => {
    const list = [banner({ id: "a" }), banner({ id: "b", dismissible: false }), banner({ id: "c" })];
    expect(clearableIds(list)).toEqual(["a", "c"]);
  });
});

describe("setLanguage", () => {
  afterEach(() => setLanguage("en"));

  it("switches the card strings to German and back", () => {
    expect(setLanguage("de")).toBe("de");
    expect(STRINGS.dismiss).toBe("Schließen");
    expect(STRINGS.severity.critical).toBe("Kritisch");
    expect(relativeTime(new Date(Date.now() - 5 * 60000).toISOString())).toBe("vor 5 Min.");
    expect(setLanguage("en")).toBe("en");
    expect(STRINGS.dismiss).toBe("Dismiss");
  });

  it("reads a regional code and falls back to English for unknown languages", () => {
    expect(setLanguage("fr-CA")).toBe("fr");
    expect(STRINGS.snooze).toBe("Reporter");
    expect(setLanguage("xx")).toBe("en");
    expect(STRINGS.snooze).toBe("Snooze");
    expect(setLanguage(undefined)).toBe("en");
  });

  it("translates every key of the English table, with the same placeholders", () => {
    const flat = (o, path = []) =>
      Object.entries(o).flatMap(([k, v]) =>
        v !== null && typeof v === "object" ? flat(v, [...path, k]) : [[[...path, k].join("."), v]],
      );
    setLanguage("en");
    const english = new Map(flat(STRINGS));
    const tokens = (text) => (text.match(/\{[a-z]+\}/g) ?? []).sort().join();
    for (const [code, table] of Object.entries(TRANSLATIONS)) {
      const translated = new Map(flat(table));
      expect([...translated.keys()].sort(), code).toEqual([...english.keys()].sort());
      for (const [key, text] of translated) expect(tokens(text), `${code} ${key}`).toBe(tokens(english.get(key)));
    }
  });

  it("keeps the placeholders of every translated string", () => {
    for (const code of ["de", "fr", "es"]) {
      setLanguage(code);
      expect(STRINGS.show_more).toContain("{n}");
      expect(STRINGS.time.minute).toContain("{n}");
      expect(STRINGS.duration.hour).toContain("{n}");
    }
  });
});

describe("whenFrontendReady", () => {
  const fakeClock = () => {
    let time = 0;
    const queue = [];
    return {
      now: () => time,
      wait: (fn, ms) => queue.push({ fn, at: time + ms }),
      advance(ms) {
        time += ms;
        for (const job of queue.splice(0).sort((a, b) => a.at - b.at)) {
          if (job.at <= time) job.fn();
          else queue.push(job);
        }
      },
    };
  };

  it("resolves only after the frontend element is defined", async () => {
    const defined = new Set();
    const clock = fakeClock();
    let done = false;
    whenFrontendReady(() => ({ get: (tag) => defined.has(tag) }), clock.wait, 10000, clock.now).then(() => (done = true));
    clock.advance(100);
    await Promise.resolve();
    expect(done).toBe(false);
    defined.add("home-assistant");
    clock.advance(25);
    await Promise.resolve();
    expect(done).toBe(true);
  });

  it("asks the registry that is current at each check, not the one from the first call", async () => {
    const clock = fakeClock();
    let registry = { get: () => undefined };
    let done = false;
    whenFrontendReady(() => registry, clock.wait, 10000, clock.now).then(() => (done = true));
    registry = { get: (tag) => tag === "home-assistant" }; // the polyfill replaced it
    clock.advance(25);
    await Promise.resolve();
    expect(done).toBe(true);
  });

  it("gives up after the limit so the card is still defined", async () => {
    const clock = fakeClock();
    let done = false;
    whenFrontendReady(() => ({ get: () => undefined }), clock.wait, 1000, clock.now).then(() => (done = true));
    for (let i = 0; i < 50; i++) clock.advance(25);
    await Promise.resolve();
    expect(done).toBe(true);
  });
});

describe("snoozed banners", () => {
  const config = normalizeConfig({});
  const mk = (id, until, extra = {}) => ({
    id,
    active: true,
    dismissed: false,
    snoozed: true,
    snoozed_until: until,
    severity: "info",
    updated_at: "2026-01-01T00:00:00Z",
    ...extra,
  });

  it("keeps snoozed banners out of the main list and lists them by return time", () => {
    const banners = [mk("late", "2026-01-01T02:00:00Z"), mk("soon", "2026-01-01T01:00:00Z")];
    expect(visibleBanners(banners, config)).toEqual([]);
    expect(snoozedBanners(banners, config).map((b) => b.id)).toEqual(["soon", "late"]);
  });

  it("applies the card filters and ignores banners that are not snoozed", () => {
    const filtered = normalizeConfig({ severity: ["critical"] });
    const banners = [mk("a", "2026-01-01T01:00:00Z"), mk("b", "x", { snoozed: false })];
    expect(snoozedBanners(banners, filtered)).toEqual([]);
    expect(snoozedBanners(banners, config).map((b) => b.id)).toEqual(["a"]);
  });

  it("reads the time left, rounded up", () => {
    const now = Date.parse("2026-01-01T00:00:00Z");
    expect(backInLabel("2026-01-01T00:00:10Z", now)).toBe("back in 1 min");
    expect(backInLabel("2026-01-01T00:12:00Z", now)).toBe("back in 12 min");
    expect(backInLabel("2026-01-01T01:30:00Z", now)).toBe("back in 2 h");
    expect(backInLabel("2026-01-02T12:00:00Z", now)).toBe("back in 2 d");
    expect(backInLabel("nonsense", now)).toBe("back in 1 min");
  });

  it("show_snoozed is off by default and must be a boolean", () => {
    expect(config.show_snoozed).toBe(false);
    expect(normalizeConfig({ show_snoozed: true }).show_snoozed).toBe(true);
  });
});
