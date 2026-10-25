import { describe, expect, it } from "vitest";
import {
  CONFIG_KEYS,
  controlsFor,
  normalizeConfig,
  retryDelay,
  sortBanners,
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

  it("marks banners with a tap action as tappable", () => {
    const b = banner({ tap_action: { action: "navigate", navigation_path: "/lovelace/0" } });
    expect(controlsFor(b, false).tap).toBe(true);
  });
});
