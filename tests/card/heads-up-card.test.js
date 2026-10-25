import { describe, expect, it } from "vitest";
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
    expect(controlsFor(banner(), true)).toEqual({ dismiss: true, adminClear: false, tap: false });
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
});

describe("clearableIds", () => {
  it("lists only dismissible banners", () => {
    const list = [banner({ id: "a" }), banner({ id: "b", dismissible: false }), banner({ id: "c" })];
    expect(clearableIds(list)).toEqual(["a", "c"]);
  });
});
