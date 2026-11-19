import { describe, expect, it } from "vitest";
import { withLabels } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import { changes, cleanDisplay, problems, STRINGS } from "../../custom_components/heads_up/frontend/panel/severities.js";

const saved = { severity_display: {}, push_levels: { critical: "critical" }, popup_styles: { critical: "modal" } };

describe("Severities page (D-222, D-223)", () => {
  it("sends nothing while only empty fields were touched", () => {
    const values = { ...structuredClone(saved), severity_display: { critical: { label: "", icon: " " }, info: {} } };
    expect(changes(values, saved)).toEqual({});
  });

  it("sends only what is set", () => {
    const values = { ...structuredClone(saved), severity_display: { critical: { label: "Alarm", icon: "", color: "#d00000" } } };
    expect(changes(values, saved)).toEqual({ severity_display: { critical: { label: "Alarm", color: "#d00000" } } });
    expect(cleanDisplay({ warning: { label: " " } })).toEqual({});
  });

  it("refuses a bad label, icon or color and warns about a shared icon", () => {
    expect(problems({ severity_display: { critical: { label: "x".repeat(31) } } }).errors).toEqual(["bad_display"]);
    expect(problems({ severity_display: { critical: { icon: "alarm" } } }).errors).toEqual(["bad_display"]);
    expect(problems({ severity_display: { critical: { color: "red; x" } } }).errors).toEqual(["bad_display"]);
    expect(problems({ severity_display: { critical: { icon: "mdi:alert" } } })).toEqual({ errors: [], warnings: ["same_icon"] });
    expect(problems({ severity_display: {} })).toEqual({ errors: [], warnings: [] });
  });

  it("has the same keys in every language", () => {
    const keys = Object.keys(STRINGS.en).sort();
    for (const t of Object.values(STRINGS)) expect(Object.keys(t).sort()).toEqual(keys);
  });

  it("puts the labels into the severity words of a page", () => {
    const t = { severity: { critical: "Critical", info: "Info" }, severity_names: { critical: "Critical" }, other: 1 };
    const out = withLabels(t, { critical: "Alarm" });
    expect(out.severity).toEqual({ critical: "Alarm", info: "Info" });
    expect(out.severity_names.critical).toBe("Alarm");
    expect(t.severity.critical).toBe("Critical"); // the table itself is unchanged
    expect(withLabels(t, {})).toBe(t);
  });
});
