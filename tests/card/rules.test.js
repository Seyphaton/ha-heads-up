import { describe, expect, it } from "vitest";
import {
  blankValues,
  fromRule,
  OPERATORS,
  sentence,
  STRINGS,
  toFlowData,
  validate,
  watchesText,
} from "../../custom_components/heads_up/frontend/panel/rules.js";

const T = STRINGS.en;
const rule = {
  name: "Door",
  data: {
    entity_id: "binary_sensor.door",
    operator: "equals",
    state: ["on"],
    message: "Door open",
    severity: "warning",
    people: ["person.anna"],
    dismissible: true,
    snoozable: true,
    snooze_options: [900, 3600],
    for: 120,
    actions: [{ key: "ack", label: "Got it", dismiss: true }],
    enabled: false,
  },
};

describe("watch rule form", () => {
  it("reads a stored rule into form values", () => {
    expect(fromRule(rule)).toMatchObject({
      name: "Door", kind: "entity", entity_id: "binary_sensor.door", state: "on", for_minutes: "2",
      snoozable: "on", snooze_minutes: ["15", "60"], enabled: false, dismissible: true, people: ["person.anna"],
    });
    expect(fromRule({ name: "T", data: { template: "{{ true }}", message: "x" } }).kind).toBe("template");
  });

  it("sends the flow input with the duration, minutes and the kept buttons", () => {
    const data = toFlowData(fromRule(rule), rule);
    expect(data).toMatchObject({
      name: "Door", entity_id: "binary_sensor.door", operator: "equals", state: ["on"], message: "Door open",
      for: { hours: 0, minutes: 2, seconds: 0 }, snoozable: true, snooze_options: ["15", "60"],
      actions: [{ key: "ack", label: "Got it", dismiss: true }], enabled: false,
    });
    expect(data.template).toBeUndefined();
  });

  it("sends only the template for a template rule and no value for empty operators", () => {
    const template = { ...blankValues(), name: "T", kind: "template", template: " {{ true }} ", message: "x", entity_id: "light.a" };
    expect(toFlowData(template)).toMatchObject({ template: "{{ true }}" });
    expect(toFlowData(template).entity_id).toBeUndefined();
    const empty = { ...blankValues(), name: "E", entity_id: "sensor.a", operator: "empty", state: "on", message: "x" };
    expect(toFlowData(empty).state).toBeUndefined();
  });

  it("leaves unset optional fields out", () => {
    const data = toFlowData({ ...blankValues(), name: "A", entity_id: "light.a", message: "x" });
    for (const key of ["title", "icon", "image", "attribute", "for", "dismiss_scope", "snoozable", "snooze_scope", "snooze_options", "actions"]) {
      expect(data[key], key).toBeUndefined();
    }
  });

  it("checks name, message and condition before saving", () => {
    expect(validate(blankValues(), [], null)).toEqual({ name: "name_required", message: "message_required", entity_id: "entity_or_template_required" });
    const ok = { ...blankValues(), name: "Door", entity_id: "light.a", message: "x" };
    expect(validate(ok, ["door"], null)).toEqual({ name: "name_exists" });
    expect(validate(ok, ["Door"], "Door")).toEqual({});
  });

  it("words the rule", () => {
    expect(watchesText(rule.data, T)).toBe("watches binary_sensor.door equals on");
    expect(watchesText({ template: "{{ x }}" }, T)).toBe("watches a template");
    expect(watchesText({ entity_id: "sensor.a", operator: "empty" }, T)).toBe("watches sensor.a is empty");
    expect(sentence(fromRule(rule), T)).toBe("Shows “Door open” (Warning) while binary_sensor.door equals on. The condition must hold for 2 min first.");
  });

  it("has the same keys and placeholders in every language", () => {
    const holders = (v) => (String(v).match(/\{[a-z]+\}/g) || []).sort();
    const keys = Object.keys(STRINGS.en).sort();
    for (const [code, language] of Object.entries(STRINGS)) {
      expect(Object.keys(language).sort(), code).toEqual(keys);
      for (const key of keys.filter((k) => typeof STRINGS.en[k] === "string")) expect(holders(language[key]), `${code}.${key}`).toEqual(holders(STRINGS.en[key]));
      expect(Object.keys(language.operators).sort(), code).toEqual([...OPERATORS].sort());
      expect(Object.keys(language.errors).sort(), code).toEqual(Object.keys(STRINGS.en.errors).sort());
    }
  });
});
