import { afterEach, describe, expect, it } from "vitest";
import {
  CONFIG_KEYS,
  DESIGNS,
  STRINGS,
  TRANSLATIONS,
  dayGroups,
  filterItems,
  formatClock,
  mergePages,
  mosaicTiles,
  needsSignature,
  normalizeConfig,
  retryDelay,
  scopeItems,
  ringSegments,
  setLanguage,
  severityColor,
  severityCounts,
  severityIcon,
  summaryKind,
  summaryText,
  timelineText,
  topItem,
  visibleText,
  whenFrontendReady,
} from "../../custom_components/heads_up/frontend/heads-up-inbox-card.js";

const item = (over = {}) => ({
  message_id: "m",
  title: "Title",
  text: "Text",
  severity: "info",
  icon: null,
  unread: true,
  needs_action: false,
  resolved: false,
  updated: "2026-11-24T08:00:00+00:00",
  ...over,
});

afterEach(() => setLanguage("en"));

describe("config", () => {
  it("has size, design and titles_only", () => {
    expect(CONFIG_KEYS).toEqual(["size", "design", "titles_only"]);
  });

  it("defaults to the large list", () => {
    expect(normalizeConfig({})).toEqual({ size: "large", design: "", titles_only: false });
  });

  it("takes the first design of a small or medium card as the default", () => {
    expect(normalizeConfig({ size: "small" })).toMatchObject({ size: "small", design: "number" });
    expect(normalizeConfig({ size: "medium" })).toMatchObject({ size: "medium", design: "tile" });
  });

  it("accepts every design of its size", () => {
    for (const design of DESIGNS.small) expect(normalizeConfig({ size: "small", design }).design).toBe(design);
    for (const design of DESIGNS.medium) expect(normalizeConfig({ size: "medium", design }).design).toBe(design);
  });

  it("refuses a design that belongs to the other size", () => {
    expect(() => normalizeConfig({ size: "small", design: "split" })).toThrow(/design/);
    expect(() => normalizeConfig({ size: "medium", design: "mosaic" })).toThrow(/design/);
  });

  it("refuses a design on the large list", () => {
    expect(() => normalizeConfig({ size: "large", design: "tile" })).toThrow(/design/);
  });

  it("refuses an unknown size and a config that is not an object", () => {
    expect(() => normalizeConfig({ size: "huge" })).toThrow(/size/);
    expect(() => normalizeConfig(null)).toThrow();
    expect(() => normalizeConfig("x")).toThrow();
  });

  it("keeps titles_only only when it is true", () => {
    expect(normalizeConfig({ titles_only: true }).titles_only).toBe(true);
    expect(normalizeConfig({ titles_only: "yes" }).titles_only).toBe(false);
  });
});

describe("state of the inbox", () => {
  it("says needs action before unread before clear", () => {
    expect(summaryKind({ unread: 3, needs_action: 1 })).toBe("needs");
    expect(summaryKind({ unread: 3, needs_action: 0 })).toBe("unread");
    expect(summaryKind({ unread: 0, needs_action: 0 })).toBe("clear");
  });

  it("words the state", () => {
    expect(summaryText({ unread: 3, needs_action: 1 }, STRINGS)).toBe("1 needs action");
    expect(summaryText({ unread: 3, needs_action: 0 }, STRINGS)).toBe("3 unread");
    expect(summaryText({ unread: 0, needs_action: 0 }, STRINGS)).toBe("All caught up");
  });

  it("counts the unread items by severity, most urgent first", () => {
    const items = [
      item({ message_id: "a", severity: "info" }),
      item({ message_id: "b", severity: "critical" }),
      item({ message_id: "c", severity: "info" }),
      item({ message_id: "d", severity: "warning", unread: false }),
    ];
    expect(severityCounts(items)).toEqual([
      ["critical", 1],
      ["info", 2],
    ]);
    expect(severityCounts([])).toEqual([]);
  });

  it("picks the item a tile shows: needs action first, then the latest unread", () => {
    const a = item({ message_id: "a" });
    const b = item({ message_id: "b", needs_action: true, severity: "critical" });
    expect(topItem([a, b]).message_id).toBe("b");
    expect(topItem([a]).message_id).toBe("a");
    expect(topItem([item({ unread: false })])).toBeNull();
    expect(topItem([])).toBeNull();
  });
});

describe("ring and mosaic", () => {
  it("gives every severity a segment that adds up to the circle", () => {
    const C = 2 * Math.PI * 29;
    const segments = ringSegments([["critical", 1], ["info", 3]], 29, 5);
    expect(segments.map((s) => s.severity)).toEqual(["critical", "info"]);
    const used = segments.reduce((sum, s) => sum + s.length + 5, 0);
    expect(used).toBeCloseTo(C, 5);
    expect(segments[0].offset).toBe(0);
    expect(segments[1].offset).toBeCloseTo(segments[0].length + 5, 5);
  });

  it("has no gap for a single severity", () => {
    const [only] = ringSegments([["info", 4]], 29, 5);
    expect(only.length).toBeCloseTo(2 * Math.PI * 29, 5);
  });

  it("has no segments when nothing is unread", () => {
    expect(ringSegments([], 29, 5)).toEqual([]);
  });

  it("shows up to four unread icons, needing action first", () => {
    const items = [
      item({ message_id: "a" }),
      item({ message_id: "b", needs_action: true, severity: "critical" }),
      item({ message_id: "c" }),
    ];
    const tiles = mosaicTiles(items);
    expect(tiles.map((t) => t.item.message_id)).toEqual(["b", "a", "c"]);
    expect(tiles.some((t) => t.more)).toBe(false);
  });

  it("shows three icons and +N from five unread items on", () => {
    const items = Array.from({ length: 6 }, (_, n) => item({ message_id: `m${n}` }));
    const tiles = mosaicTiles(items);
    expect(tiles).toHaveLength(4);
    expect(tiles.slice(0, 3).every((t) => t.item)).toBe(true);
    expect(tiles[3]).toEqual({ more: 3 });
  });

  it("shows all four when there are exactly four", () => {
    const items = Array.from({ length: 4 }, (_, n) => item({ message_id: `m${n}` }));
    expect(mosaicTiles(items).every((t) => t.item)).toBe(true);
  });

  it("skips read items", () => {
    expect(mosaicTiles([item({ unread: false })])).toEqual([]);
  });
});

describe("the list", () => {
  it("filters unread items", () => {
    const items = [item({ message_id: "a" }), item({ message_id: "b", unread: false })];
    expect(filterItems(items, "all")).toHaveLength(2);
    expect(filterItems(items, "unread").map((i) => i.message_id)).toEqual(["a"]);
  });

  it("puts items that need action first and keeps the order otherwise", () => {
    const items = [
      item({ message_id: "a" }),
      item({ message_id: "b", needs_action: true }),
      item({ message_id: "c" }),
    ];
    expect(filterItems(items, "all").map((i) => i.message_id)).toEqual(["b", "a", "c"]);
  });

  it("groups by local day with today, yesterday, a weekday and a date", () => {
    const now = new Date(2026, 10, 24, 12, 0, 0); // Tuesday
    const at = (d, h) => new Date(2026, 10, d, h, 0, 0).toISOString();
    const items = [
      item({ message_id: "a", updated: at(24, 9) }),
      item({ message_id: "b", updated: at(23, 20) }),
      item({ message_id: "c", updated: at(21, 8) }),
      item({ message_id: "d", updated: new Date(2026, 9, 1, 8).toISOString() }),
    ];
    const groups = dayGroups(items, now);
    expect(groups.map((g) => g.kind)).toEqual(["today", "yesterday", "weekday", "date"]);
    expect(groups[2].date.getDay()).toBe(6); // Saturday, 21 November
    expect(groups.map((g) => g.items.length)).toEqual([1, 1, 1, 1]);
  });

  it("puts two items of one day into one group", () => {
    const now = new Date(2026, 10, 24, 12, 0, 0);
    const at = (h) => new Date(2026, 10, 24, h, 0, 0).toISOString();
    const groups = dayGroups([item({ message_id: "a", updated: at(9) }), item({ message_id: "b", updated: at(8) })], now);
    expect(groups).toHaveLength(1);
    expect(groups[0].items.map((i) => i.message_id)).toEqual(["a", "b"]);
  });

  it("merges a later page behind the first without duplicates", () => {
    const first = [item({ message_id: "a" }), item({ message_id: "b" })];
    const more = [item({ message_id: "b", title: "old" }), item({ message_id: "c" })];
    const merged = mergePages(first, more);
    expect(merged.map((i) => i.message_id)).toEqual(["a", "b", "c"]);
    expect(merged[1].title).toBe("Title");
  });

  it("hides the text only with titles_only", () => {
    expect(visibleText(item(), { titles_only: false })).toBe("Text");
    expect(visibleText(item(), { titles_only: true })).toBe("");
  });

  it("words the timeline", () => {
    const t = (kind, extra = {}) => timelineText({ kind, at: "2026-11-24T08:02:00+00:00", ...extra }, STRINGS);
    expect(t("sent", { channel: "push" })).toBe("Sent: Push");
    expect(t("sent")).toBe("Sent");
    expect(t("reminder", { channel: "popup" })).toBe("Reminder: Popup");
    expect(t("escalation")).toBe("Escalated");
    expect(t("acknowledged")).toBe("Acknowledged");
    expect(t("acknowledged_by_other")).toBe("Acknowledged by someone else");
    expect(t("updated")).toBe("Updated");
    expect(t("resolved")).toBe("Ended");
    expect(t("surprise")).toBe("surprise");
  });

  it("words why an item ended", () => {
    expect(STRINGS.reasons.cleared).toBeTruthy();
    for (const reason of ["cleared", "expired", "condition", "dismissed"]) {
      expect(STRINGS.reasons[reason]).toBeTruthy();
    }
  });
});

describe("the views Inbox and Everything", () => {
  const items = [item({ message_id: "real" }), item({ message_id: "copy", copy: true, unread: false })];

  it("shows only real items in Inbox and everything in Everything", () => {
    expect(scopeItems(items, "inbox").map((i) => i.message_id)).toEqual(["real"]);
    expect(scopeItems(items, "all").map((i) => i.message_id)).toEqual(["real", "copy"]);
  });

  it("never counts a copy as unread or as needing action in the mosaic and the tile", () => {
    const copy = item({ message_id: "c", copy: true, unread: false, needs_action: false });
    expect(mosaicTiles([copy])).toEqual([]);
    expect(topItem([copy])).toBeNull();
    expect(severityCounts([copy])).toEqual([]);
  });

  it("has words for the view and the hint in every language", () => {
    for (const code of ["en", "de", "fr", "es"]) {
      setLanguage(code);
      expect(STRINGS.everything).toBeTruthy();
      expect(STRINGS.copy_hint).toBeTruthy();
    }
  });
});

describe("severity look", () => {
  it("uses theme colors and a distinct icon for each severity", () => {
    expect(severityColor("critical")).toBe("var(--error-color)");
    expect(severityColor("warning")).toBe("var(--warning-color)");
    expect(severityColor("info")).toBe("var(--info-color)");
    expect(severityColor("passive")).toBe("var(--success-color)");
    expect(severityColor("nonsense")).toBe("var(--info-color)");
    const icons = new Set(["critical", "warning", "info", "passive"].map(severityIcon));
    expect(icons.size).toBe(4);
  });

  it("shows the message's own icon first", () => {
    expect(severityIcon("info", "mdi:water")).toBe("mdi:water");
  });
});

describe("small helpers", () => {
  it("formats a clock time in the user's language", () => {
    expect(formatClock("2026-11-24T08:05:00", "en")).toMatch(/8:05|08:05/);
    expect(formatClock("not a date", "en")).toBe("");
  });

  it("backs off after a failed subscription, up to a limit", () => {
    expect(retryDelay(0)).toBeLessThan(retryDelay(3));
    expect(retryDelay(50)).toBe(retryDelay(20));
  });

  it("asks for a signed path only for protected addresses", () => {
    expect(needsSignature("/api/camera_proxy/camera.door")).toBe(true);
    expect(needsSignature("/media/local/x.png")).toBe(true);
    expect(needsSignature("/local/x.png")).toBe(false);
    expect(needsSignature("https://example.com/x.png")).toBe(false);
  });
});

describe("languages", () => {
  it("has German, French and Spanish with the same keys as English", () => {
    const keys = (o, prefix = "") =>
      Object.entries(o).flatMap(([k, v]) => (v && typeof v === "object" ? keys(v, `${prefix}${k}.`) : [`${prefix}${k}`]));
    setLanguage("en");
    const english = keys(STRINGS).sort();
    for (const code of ["de", "fr", "es"]) {
      expect(keys(TRANSLATIONS[code]).sort()).toEqual(english);
    }
  });

  it("switches and falls back to English", () => {
    expect(setLanguage("de-AT")).toBe("de");
    expect(STRINGS.inbox).toBe("Posteingang");
    expect(setLanguage("xx")).toBe("en");
    expect(STRINGS.inbox).toBe("Inbox");
  });

  it("words the state in German", () => {
    setLanguage("de");
    expect(summaryText({ unread: 0, needs_action: 0 }, STRINGS)).toBe(STRINGS.all_caught_up);
    expect(summaryText({ unread: 2, needs_action: 0 }, STRINGS)).toContain("2");
  });
});

describe("registration", () => {
  it("waits for the frontend before defining the element", async () => {
    const registry = new Map();
    let ticks = 0;
    const wait = (fn) => {
      ticks += 1;
      if (ticks === 3) registry.set("home-assistant", {});
      fn();
    };
    registry.get = Map.prototype.get.bind(registry);
    await whenFrontendReady(() => registry, wait, 10000, () => 0);
    expect(ticks).toBe(3);
  });

  it("gives up after the maximum wait", async () => {
    let now = 0;
    await whenFrontendReady(() => new Map(), (fn) => { now += 5000; fn(); }, 10000, () => now);
    expect(now).toBeGreaterThanOrEqual(10000);
  });
});
