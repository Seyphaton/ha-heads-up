import { describe, expect, it } from "vitest";
import {
  actionFields,
  actionFromFields,
  actionKind,
  actionProblem,
  buttonProblems,
  buttonsToData,
  numericEntityOptions,
  slugKey,
} from "../../custom_components/heads_up/frontend/panel/ui.js";

describe("button keys", () => {
  it("makes a key from the text and avoids the ones taken", () => {
    expect(slugKey("Got it!")).toBe("got_it");
    expect(slugKey("Öffnen")).toBe("offnen");
    expect(slugKey("", [])).toBe("button");
    expect(slugKey("Got it", ["got_it"])).toBe("got_it_2");
    expect(slugKey("Got it", ["got_it", "got_it_2"])).toBe("got_it_3");
    expect(slugKey("x".repeat(60)).length).toBe(30);
  });
});

describe("action editor", () => {
  it("tells which editor shape a stored action has", () => {
    expect(actionKind(null)).toBe("none");
    expect(actionKind({ action: "navigate", navigation_path: "/a" })).toBe("navigate");
    expect(actionKind({ action: "url", url_path: "https://a.b" })).toBe("url");
    expect(actionKind({ action: "more-info", entity: "light.a" })).toBe("more-info");
    expect(actionKind({ action: "perform-action", perform_action: "light.toggle" })).toBe("perform-action");
    expect(actionKind({ action: "toggle" })).toBe("custom");
  });

  it("builds the action of each kind from the fields", () => {
    const base = actionFields(null);
    expect(actionFromFields({ ...base, kind: "none" }, null)).toBeNull();
    expect(actionFromFields({ ...base, kind: "navigate", path: " /lovelace/cameras " }, null)).toEqual({ action: "navigate", navigation_path: "/lovelace/cameras" });
    expect(actionFromFields({ ...base, kind: "url", url: "https://example.org" }, null)).toEqual({ action: "url", url_path: "https://example.org" });
    expect(actionFromFields({ ...base, kind: "more-info", entity: "light.a" }, null)).toEqual({ action: "more-info", entity: "light.a" });
    expect(
      actionFromFields({ ...base, kind: "perform-action", perform: "light.turn_on", target: "light.a", data: '{"brightness": 100}' }, null),
    ).toEqual({ action: "perform-action", perform_action: "light.turn_on", target: { entity_id: "light.a" }, data: { brightness: 100 } });
  });

  it("keeps keys it does not know while the kind stays", () => {
    const old = { action: "navigate", navigation_path: "/a", confirmation: { text: "Sure?" } };
    const fields = { ...actionFields(old), path: "/b" };
    expect(actionFromFields(fields, old)).toEqual({ action: "navigate", navigation_path: "/b", confirmation: { text: "Sure?" } });
    expect(actionFromFields({ ...fields, kind: "url", url: "https://a.b" }, old)).toEqual({ action: "url", url_path: "https://a.b" });
  });

  it("keeps an action of another type as it is", () => {
    const old = { action: "toggle", entity: "light.a" };
    expect(actionFromFields(actionFields(old), old)).toBe(old);
  });

  it("reads the fields back", () => {
    const old = { action: "perform-action", perform_action: "light.turn_on", target: { entity_id: "light.a" }, data: { brightness: 5 } };
    expect(actionFields(old)).toEqual({ kind: "perform-action", path: "", url: "", entity: "", perform: "light.turn_on", target: "light.a", data: '{"brightness":5}' });
  });

  it("names what is missing", () => {
    const base = actionFields(null);
    expect(actionProblem({ ...base, kind: "none" })).toBe("");
    expect(actionProblem({ ...base, kind: "navigate" })).toBe("action_incomplete");
    expect(actionProblem({ ...base, kind: "url" })).toBe("action_incomplete");
    expect(actionProblem({ ...base, kind: "more-info" })).toBe("action_incomplete");
    expect(actionProblem({ ...base, kind: "perform-action" })).toBe("action_incomplete");
    expect(actionProblem({ ...base, kind: "perform-action", perform: "a.b", data: "{oops" })).toBe("data_invalid");
    expect(actionProblem({ ...base, kind: "perform-action", perform: "a.b", data: "[1]" })).toBe("data_invalid");
    expect(actionProblem({ ...base, kind: "perform-action", perform: "a.b", data: '{"x": 1}' })).toBe("");
  });
});

describe("button list", () => {
  const ok = { key: "ack", label: "Got it" };

  it("accepts a clean list", () => {
    expect(buttonProblems([ok], true)).toEqual([]);
  });

  it("finds an empty text, a bad or repeated key, and a dismiss without dismissible", () => {
    expect(buttonProblems([{ key: "a", label: " " }], true)).toEqual([{ index: 0, code: "label_required" }]);
    expect(buttonProblems([{ key: "A b", label: "x" }], true)).toEqual([{ index: 0, code: "key_invalid" }]);
    expect(buttonProblems([ok, { ...ok, label: "Again" }], true)).toEqual([{ index: 1, code: "key_duplicate" }]);
    expect(buttonProblems([{ ...ok, dismiss: true }], false)).toEqual([{ index: 0, code: "dismiss_needs_dismissible" }]);
    expect(buttonProblems([{ ...ok, dismiss: true }], true)).toEqual([]);
  });

  it("finds a half-filled action", () => {
    expect(buttonProblems([{ ...ok, action: { action: "navigate", navigation_path: "" } }], true)).toEqual([{ index: 0, code: "action_incomplete" }]);
  });

  it("sends only the keys that are set", () => {
    expect(buttonsToData([{ key: "a", label: " Open ", destructive: true, dismiss: false }])).toEqual([{ key: "a", label: "Open", destructive: true }]);
    expect(buttonsToData([{ ...ok, action: { action: "url", url_path: "https://a.b" } }])).toEqual([{ key: "ack", label: "Got it", action: { action: "url", url_path: "https://a.b" } }]);
  });
});

describe("progress entity choices (D-260)", () => {
  const states = {
    "sensor.b_temp": { state: "21.5", attributes: { friendly_name: "Bedroom temperature" } },
    "sensor.a_count": { state: "3", attributes: {} },
    "light.lamp": { state: "on", attributes: { friendly_name: "Lamp" } },
    "sensor.gone": { state: "unavailable", attributes: {} },
    "sensor.empty": { state: "", attributes: {} },
    "sensor.neg": { state: "-4", attributes: { friendly_name: "Cold" } },
  };

  it("lists only entities with a numeric state, sorted by name", () => {
    expect(numericEntityOptions(states).map((o) => o.value)).toEqual(["sensor.a_count", "sensor.b_temp", "sensor.neg"]);
    expect(numericEntityOptions(states)[1].label).toBe("Bedroom temperature (sensor.b_temp)");
  });

  it("keeps the chosen entity selectable when it is not numeric now", () => {
    expect(numericEntityOptions(states, "sensor.gone")[0]).toEqual({ value: "sensor.gone", label: "sensor.gone" });
    expect(numericEntityOptions(states, "sensor.a_count").length).toBe(3);
    expect(numericEntityOptions(undefined)).toEqual([]);
  });
});
