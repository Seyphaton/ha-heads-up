import { describe, expect, it } from "vitest";
import {
  buttonsFor,
  current,
  mayTakeFocus,
  sortQueue,
  STRINGS,
  styleOf,
  text,
} from "../../custom_components/heads_up/frontend/heads-up-popup.js";

const msg = (id, severity, created_at, extra = {}) => ({ id, severity, created_at, message: id, ...extra });

describe("popup queue", () => {
  it("shows the highest severity first, then the oldest", () => {
    const queue = sortQueue([
      msg("w2", "warning", "2026-11-01T10:05:00Z"),
      msg("i", "info", "2026-11-01T09:00:00Z"),
      msg("c", "critical", "2026-11-01T11:00:00Z"),
      msg("w1", "warning", "2026-11-01T10:00:00Z"),
    ]);
    expect(queue.map((m) => m.id)).toEqual(["c", "w1", "w2", "i"]);
  });

  it("does not change the list it is given", () => {
    const input = [msg("a", "info", "1"), msg("b", "critical", "2")];
    sortQueue(input);
    expect(input.map((m) => m.id)).toEqual(["a", "b"]);
  });

  it("current skips what was closed on this page and is null when nothing is left", () => {
    const list = [msg("a", "critical", "1"), msg("b", "info", "2")];
    expect(current(list, new Set()).id).toBe("a");
    expect(current(list, new Set(["a"])).id).toBe("b");
    expect(current(list, new Set(["a", "b"]))).toBeNull();
    expect(current([], new Set())).toBeNull();
  });
});

describe("popup style and focus", () => {
  it("is a card unless the server says modal", () => {
    expect(styleOf(msg("a", "info", "1", { style: "card" }))).toBe("card");
    expect(styleOf(msg("a", "info", "1"))).toBe("card");
    expect(styleOf(msg("a", "critical", "1", { style: "modal" }))).toBe("modal");
  });

  it("a card never takes focus", () => {
    expect(mayTakeFocus(msg("a", "critical", "1", { style: "card" }), "BODY")).toBe(false);
  });

  it("a critical modal takes focus even while typing", () => {
    expect(mayTakeFocus(msg("a", "critical", "1", { style: "modal" }), "INPUT")).toBe(true);
  });

  it("a modal that is not critical leaves an input alone", () => {
    const m = msg("a", "warning", "1", { style: "modal" });
    expect(mayTakeFocus(m, "textarea")).toBe(false);
    expect(mayTakeFocus(m, "BODY")).toBe(true);
  });
});

describe("popup buttons", () => {
  it("lists the message's own buttons, then Acknowledge, Snooze and Dismiss", () => {
    const buttons = buttonsFor(
      msg("a", "info", "1", {
        actions: [{ key: "seen", label: "Seen" }],
        ack: true,
        snoozable: true,
        snooze_options: [600, 3600],
        dismissible: true,
      }),
    );
    expect(buttons.map((b) => b.kind)).toEqual(["action", "ack", "snooze", "dismiss"]);
    expect(buttons[2].seconds).toBe(600);
  });

  it("has no Snooze without options and no Dismiss when not dismissible", () => {
    const buttons = buttonsFor(msg("a", "info", "1", { snoozable: true, snooze_options: [], dismissible: false }));
    expect(buttons).toEqual([]);
  });
});

describe("popup text", () => {
  it("follows the language and falls back to English", () => {
    expect(text("de", "dismiss")).toBe("Schließen");
    expect(text("de-AT", "snooze")).toBe("Später");
    expect(text("xx", "dismiss")).toBe("Dismiss");
  });

  it("has the same keys in every language", () => {
    const keys = Object.keys(STRINGS.en).sort();
    for (const table of Object.values(STRINGS)) expect(Object.keys(table).sort()).toEqual(keys);
  });
});
