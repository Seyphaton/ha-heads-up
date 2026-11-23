import { describe, expect, it } from "vitest";
import {
  ackText,
  blankValues,
  audienceIds,
  buildCall,
  callYaml,
  fromCall,
  laterText,
  outcomeDone,
  behaviourUnused,
  outcomeRows,
  plannedLine,
  rowRecipient,
  STRINGS,
  summaryLine,
  validate,
} from "../../custom_components/heads_up/frontend/panel/test_send.js";
import { STRINGS as SHELL } from "../../custom_components/heads_up/frontend/heads-up-panel.js";
import { targetMode, toYaml } from "../../custom_components/heads_up/frontend/panel/ui.js";

const S = SHELL.en.shared;
const T = STRINGS.en;

const values = (extra = {}) => ({ ...blankValues(), message: "Door open", ...extra });

describe("test send call", () => {
  it("finds the entity ID of an audience by the key the form stores", () => {
    const data = {
      audiences: [
        { name: "Admins", entity_id: "binary_sensor.heads_up_audience_admins" },
        { name: "Kids", entity_id: "binary_sensor.heads_up_audience_kids" },
      ],
      choices: { audience_choices: [{ id: "admins", name: "Admins" }, { id: "01ABC", name: "Kids" }] },
    };
    const ids = audienceIds(data);
    expect(ids.admins).toBe("binary_sensor.heads_up_audience_admins");
    expect(ids["01ABC"]).toBe("binary_sensor.heads_up_audience_kids");
    expect(buildCall(values({ channels: ["popup"], popup_audience: "admins" }), { audiences: ids }).audience).toBe("binary_sensor.heads_up_audience_admins");
  });

  it("names an audience and a policy by the entity ID of its sensor or switch", () => {
    const ids = { audiences: { "At home": "binary_sensor.heads_up_audience_at_home" }, policies: { Night: "switch.heads_up_policy_night" } };
    const call = buildCall(values({ channels: ["push"], push_audience: "At home", policy: ["Night", "none"] }), ids);
    expect(call.audience).toBe("binary_sensor.heads_up_audience_at_home");
    expect(call.policy).toEqual(["switch.heads_up_policy_night", "none"]);
    expect(buildCall(values({ policy: ["Night"] }), ids).policy).toBe("switch.heads_up_policy_night");
  });

  it("builds only what is set", () => {
    expect(buildCall(values())).toEqual({ message: "Door open", severity: "info", channels: ["banner"] });
  });

  it("adds title, tag, policy and trims the text", () => {
    const call = buildCall(values({ message: "  Door open ", title: " Garage ", tag: "door", policy: ["Night"] }));
    expect(call).toEqual({ message: "Door open", title: "Garage", tag: "door", policy: "Night", severity: "info", channels: ["banner"] });
  });

  it("adds the dismiss and snooze choices only when they differ from the defaults", () => {
    expect(buildCall(values({ dismiss: "everyone", snooze: "user" }))).toMatchObject({ dismiss: "everyone", snooze: "user" });
    const pinned = buildCall(values({ dismiss: "off", snooze: "everyone" }));
    expect(pinned.dismiss).toBe("off");
    expect(pinned.snooze).toBeUndefined();
    expect(buildCall(values())).not.toHaveProperty("dismiss");
    expect(buildCall(values())).not.toHaveProperty("snooze");
  });

  it("leaves the policies out by default, names one manual policy as text and several as a list", () => {
    expect(buildCall(values())).not.toHaveProperty("policy");
    expect(buildCall(values())).not.toHaveProperty("match_policies_automatically");
    expect(buildCall(values({ policy: ["Night"] })).policy).toBe("Night");
    expect(buildCall(values({ policy: ["Night", "By hand"] })).policy).toEqual(["Night", "By hand"]);
  });

  it("writes match_policies_automatically only when it is switched off", () => {
    expect(buildCall(values({ match_automatic: false })).match_policies_automatically).toBe(false);
    expect(buildCall(values({ match_automatic: true }))).not.toHaveProperty("match_policies_automatically");
  });

  it("writes the same people on every channel once, and speakers apart", () => {
    const call = buildCall(
      values({ channels: ["push", "popup", "speak"], push_recipients: ["person.a"], popup_recipients: ["person.a"], speak_recipients: ["media_player.k"] }),
    );
    expect(call.recipients).toEqual(["person.a"]);
    expect(call.speakers).toEqual(["media_player.k"]);
    expect(call.to).toBeUndefined();
  });

  it("keeps the per channel form when a banner is open to everyone but the push is not", () => {
    const call = buildCall(values({ channels: ["banner", "push"], push_audience: "At home" }));
    expect(call.to).toEqual({ push: { audience: "At home" } });
    expect(call.audience).toBeUndefined();
  });

  it("says whether anything waits for an acknowledgement, and how to make it so", () => {
    expect(ackText(["Water escalation", "Critical reminder"], T)).toContain("Water escalation, Critical reminder");
    expect(ackText([], T)).toContain("add an Escalation or Reminder policy");
    expect(ackText(undefined, T)).toBe(ackText([], T));
  });

  it("sends the spoken text only when speech is a channel", () => {
    expect(buildCall(values({ tts_message: "Hello" })).tts_message).toBeUndefined();
    const call = buildCall(values({ channels: ["speak"], tts_message: "Hello", speak_recipients: ["media_player.k"] }));
    expect(call.tts_message).toBe("Hello");
    expect(call.to).toEqual({ speak: { recipients: ["media_player.k"] } });
  });

  it("sends the volume as 0 to 1 only for speech and clamps it", () => {
    const speak = { channels: ["speak"], speak_recipients: ["media_player.k"] };
    expect(buildCall(values({ ...speak, volume: "40" })).volume).toBe(0.4);
    expect(buildCall(values({ ...speak, volume: "250" })).volume).toBe(1);
    expect(buildCall(values({ ...speak, volume: "" })).volume).toBeUndefined();
    expect(buildCall(values({ channels: ["push"], volume: "40" })).volume).toBeUndefined();
  });

  it("sends the mail subject and text only when mail is a channel", () => {
    expect(buildCall(values({ mail_subject: "{person}" })).mail_subject).toBeUndefined();
    const call = buildCall(values({ channels: ["mail"], mail_subject: " {person} ", mail_body: "{title}: {message}" }));
    expect(call.mail_subject).toBe("{person}");
    expect(call.mail_body).toBe("{title}: {message}");
    expect(buildCall(values({ channels: ["mail"] })).mail_subject).toBeUndefined();
  });

  it("sends the target of each chosen channel and nothing for the others", () => {
    const call = buildCall(
      values({
        channels: ["push", "popup", "persistent"],
        push_audience: "At home",
        popup_recipients: ["person.anna"],
        speak_recipients: ["media_player.k"],
        persistent_audience: "Everyone",
      }),
    );
    expect(call.to).toEqual({ push: { audience: "At home" }, popup: { recipients: ["person.anna"] } });
  });

  it("never sends an audience for speech", () => {
    const call = buildCall(values({ channels: ["speak"], speak_audience: "Everyone" }));
    expect(call.to).toBeUndefined();
  });
});

describe("test send validation", () => {
  it("needs a message and a channel", () => {
    expect(validate({ ...blankValues(), channels: [] }).map((p) => p.code)).toEqual(["message_required", "channels_required"]);
    expect(validate(values())).toEqual([]);
  });

  it("needs a target for push, popup and speak but not for the banner or the bell", () => {
    expect(validate(values({ channels: ["push"] }))).toEqual([{ code: "target_required", channel: "push" }]);
    expect(validate(values({ channels: ["speak"] }))).toEqual([{ code: "target_required", channel: "speak" }]);
    expect(validate(values({ channels: ["banner", "persistent"] }))).toEqual([]);
    expect(validate(values({ channels: ["push"], push_audience: "Everyone" }))).toEqual([]);
  });

  it("refuses an audience and recipients together", () => {
    const both = values({ channels: ["popup"], popup_audience: "Everyone", popup_recipients: ["person.a"] });
    expect(validate(both)).toEqual([{ code: "target_exclusive", channel: "popup" }]);
    const banner = values({ banner_audience: "Everyone", banner_recipients: ["person.a"] });
    expect(validate(banner)).toEqual([{ code: "target_exclusive", channel: "banner" }]);
  });
});

describe("the call as YAML", () => {
  it("is a heads_up.notify action with the data", () => {
    const yaml = callYaml(values({ title: "Garage", channels: ["banner", "push"], push_audience: "At home", policy: ["Water escalation"] }), toYaml);
    expect(yaml).toBe(
      [
        "action: heads_up.notify",
        "data:",
        "  message: Door open",
        "  severity: info",
        "  channels:",
        "    - banner",
        "    - push",
        "  title: Garage",
        "  policy: Water escalation",
        "  to:",
        "    push:",
        "      audience: At home",
      ].join("\n"),
    );
  });
});

describe("test send wording", () => {
  it("counts the results per channel and leaves out fallback rows", () => {
    const rows = [
      { channel: "banner", result: "sent" },
      { channel: "push", result: "sent" },
      { channel: "push", result: "sent" },
      { channel: "push", result: "skipped" },
      { channel: "push", result: "sent", via: "Backup" },
    ];
    expect(summaryLine(rows, S)).toBe("Banner: 1 sent; Push: 2 sent, 1 skipped");
    expect(summaryLine([], S)).toBe("");
  });

  it("words each later step", () => {
    expect(laterText({ type: "escalation", policy: "Water", after_minutes: 5, channels: ["push", "speak"] }, T, S)).toBe(
      "Escalation Water: after 5 min unless someone acknowledges, also on Push, Speak.",
    );
    expect(laterText({ type: "reminder", policy: "Nag", every_minutes: 30, max_count: 3, channels: [] }, T, S)).toBe(
      "Reminder Nag: every 30 min, at most 3 times.",
    );
    expect(laterText({ type: "reminder", policy: "Nag", every_minutes: 30, max_count: 3, channels: ["push"] }, T, S)).toBe(
      "Reminder Nag: every 30 min, at most 3 times, only on Push.",
    );
    expect(laterText({ type: "presence", policy: "Back", max_wait: 0 }, T, S)).toBe("Presence Back: held until the people it waits for are where it expects them.");
    expect(laterText({ type: "presence", policy: "Back", max_wait: 20 }, T, S)).toBe("Presence Back: held until the people it waits for are where it expects them, for at most 20 min.");
    expect(laterText({ type: "fallback", policy: "Backup", when: "failed", channels: ["persistent"] }, T, S)).toBe(
      "Fallback Backup: if delivery fails, it is sent on Persistent Notification instead.",
    );
    expect(laterText({ type: "summarize", policy: "Digest", summary_every: 60 }, T, S)).toBe("Summary Digest: one summary 60 min after the first held message.");
    expect(laterText({ type: "summarize", policy: "Evening", summary_at: "20:00:00" }, T, S)).toBe("Summary Evening: one summary every day at 20:00.");
  });

  it("has the same keys and placeholders in every language", () => {
    const leaves = (object, path = "") =>
      Object.entries(object).flatMap(([key, value]) => (typeof value === "object" ? leaves(value, `${path}${key}.`) : [[`${path}${key}`, value]]));
    const english = Object.fromEntries(leaves(STRINGS.en));
    const holders = (text) => (String(text).match(/\{[a-z]+\}/g) || []).sort();
    for (const [code, language] of Object.entries(STRINGS)) {
      const own = Object.fromEntries(leaves(language));
      expect(Object.keys(own).sort(), code).toEqual(Object.keys(english).sort());
      for (const key of Object.keys(english)) expect(holders(own[key]), `${code}.${key}`).toEqual(holders(english[key]));
    }
  });
});

describe("test send rows and target mode", () => {
  const choices = { persons: [{ id: "person.anna", name: "Anna" }, { id: "person.ben", name: "Ben" }], registrations: [{ id: "d1", name: "Pixel" }] };

  it("shows the person and the device on a push row", () => {
    expect(rowRecipient({ recipient: "device:d1", person: "person.anna", channel: "push" }, {}, choices, T)).toBe("Anna · Pixel");
    expect(rowRecipient({ recipient: "person.anna", person: "person.anna", channel: "popup" }, {}, choices, T)).toBe("Anna");
    expect(rowRecipient({ recipient: "mail:global", channel: "mail" }, {}, choices, T)).toBe("Global address");
  });

  it("shows who a banner is limited to, everyone, or nobody", () => {
    const row = { recipient: "", channel: "banner", result: "sent" };
    expect(rowRecipient(row, { banner_people: ["person.anna", "person.ben"] }, choices, T)).toBe("Anna, Ben");
    expect(rowRecipient(row, { banner_people: [] }, choices, T)).toBe("everyone");
    expect(rowRecipient({ ...row, result: "skipped" }, { banner_people: [] }, choices, T)).toBe("nobody");
  });

  it("keeps a chosen mode while no recipient is ticked", () => {
    expect(targetMode({}, "push")).toBe("audience");
    expect(targetMode({ push_recipients: ["person.anna"] }, "push")).toBe("recipients");
    expect(targetMode({ _mode_push: "recipients", push_recipients: [] }, "push")).toBe("recipients");
    expect(targetMode({ _mode_push: "audience", push_recipients: ["person.anna"] }, "push")).toBe("audience");
    expect(targetMode({}, "speak")).toBe("recipients");
  });
});

describe("test send outcome", () => {
  const entries = [
    { channel: "banner", recipient: "", result: "sent" },
    { channel: "speak", recipient: "media_player.k", result: "failed", reason: "no_tts_engine" },
    { channel: "push", recipient: "device:d1", result: "cleared" },
  ];

  it("keeps the real delivery results of the named channels, the banner included", () => {
    expect(outcomeRows(entries, ["banner", "speak", "push"])).toEqual([entries[0], entries[1]]);
    expect(outcomeRows(entries, ["banner"])).toEqual([entries[0]]);
    expect(outcomeRows(entries, ["speak"])).toEqual([entries[1]]);
  });

  it("is done once every named channel has a result", () => {
    expect(outcomeDone(entries, ["banner", "speak"])).toBe(true);
    expect(outcomeDone(entries, ["banner", "speak", "push"])).toBe(false);
    expect(outcomeDone([], ["banner"])).toBe(false); // a banner-only send waits for its row
    expect(outcomeDone(entries, ["banner"])).toBe(true);
  });

  it("words the planned counts with every kind, not only sent", () => {
    expect(plannedLine({ speak: { sent: 0, held: 0, skipped: 1, failed: 0 }, banner: { sent: 1, held: 0, skipped: 0, failed: 0 } }, S)).toBe(
      "Speak: 1 skipped; Banner: 1 sent",
    );
  });
});

describe("test send behaviour hint", () => {
  it("says the choices do not apply to a call of mail and speech only", () => {
    expect(behaviourUnused(["mail"])).toBe("behaviour_none");
    expect(behaviourUnused(["mail", "speak"])).toBe("behaviour_none");
  });

  it("says mail and speech ignore them when other channels still use them", () => {
    expect(behaviourUnused(["banner", "mail"])).toBe("behaviour_some");
    expect(behaviourUnused(["push", "speak", "popup"])).toBe("behaviour_some");
  });

  it("says nothing when no channel ignores them", () => {
    expect(behaviourUnused(["banner", "push"])).toBeNull();
    expect(behaviourUnused(["persistent"])).toBeNull();
    expect(behaviourUnused([])).toBeNull();
  });
});

describe("every field of notify (D-260)", () => {
  const base = { ...blankValues(), message: "Door open", severity: "warning", channels: ["banner"] };

  it("writes the new fields only when they are set", () => {
    expect(Object.keys(buildCall(base)).sort()).toEqual(["channels", "message", "severity"]);
    const call = buildCall({
      ...base, icon: "mdi:door", image: "/local/a.jpg", color: " #03a9f4 ", subtitle: "Front", icon_url: "/local/b.png",
      progress_entity: "sensor.p", progress_min: "10", progress_max: "", timeout: "5",
      snooze_minutes: ["15", "60"], snooze_custom: true,
      actions: [{ key: "ok", label: "Got it", dismiss: true }, { key: "x", label: " " }],
      tap_action: { action: "navigate", navigation_path: "/a" },
    });
    expect(call).toMatchObject({
      icon: "mdi:door", image: "/local/a.jpg", color: "#03a9f4", subtitle: "Front", icon_url: "/local/b.png",
      progress: { entity_id: "sensor.p", min: 10 }, timeout: { minutes: 5 },
      snooze_options: [{ minutes: 15 }, { minutes: 60 }], snooze_custom: true,
      actions: [{ key: "ok", label: "Got it", dismiss: true }], tap_action: { action: "navigate", navigation_path: "/a" },
    });
  });

  it("writes the progress bar with an interval, without automatic updates, or with a fixed value", () => {
    const bar = { ...base, progress_entity: "sensor.p", progress_interval: "10", progress_auto: false };
    expect(buildCall(bar).progress).toEqual({ entity_id: "sensor.p", interval: 10, auto_update: false });
    expect(buildCall({ ...base, progress_entity: "sensor.p" }).progress).toEqual({ entity_id: "sensor.p" });
    const fixed = { ...base, progress_value: "45", progress_max: "80", progress_interval: "10", progress_auto: false };
    expect(buildCall(fixed).progress).toEqual({ value: 45, max: 80 });
    const back = fromCall({ message: "x", progress: { entity_id: "sensor.p", interval: 10, auto_update: false } });
    expect([back.progress_entity, back.progress_interval, back.progress_auto]).toEqual(["sensor.p", "10", false]);
    expect(fromCall({ message: "x", progress: { value: 7 } }).progress_value).toBe("7");
    expect(validate({ ...base, progress_entity: "sensor.p", progress_value: "5" }).map((p) => p.code)).toContain("progress_both");
  });

  it("keeps the keys the form has no field for", () => {
    const call = buildCall({ ...base, extra: { condition: { entity_id: "a.b", state: "on" } } });
    expect(call.condition).toEqual({ entity_id: "a.b", state: "on" });
  });

  it("reads a call back into the form and writes the same call again", () => {
    const ids = { audiences: { admins: "binary_sensor.heads_up_audience_admins" }, policies: { Night: "switch.heads_up_policy_night" } };
    const original = {
      message: "Door open", title: "Door", severity: "warning", channels: ["banner", "push"], color: "#03a9f4", icon: "mdi:door",
      subtitle: "Front", icon_url: "/local/b.png", progress: { entity_id: "sensor.p", max: 80 }, timeout: { minutes: 5 },
      snooze_options: [{ minutes: 15 }], snooze_custom: true, dismiss: "everyone", tag: "door",
      actions: [{ key: "ok", label: "Got it", destructive: true }], tap_action: { action: "url", url_path: "https://a.b" },
      audience: "binary_sensor.heads_up_audience_admins", policy: "switch.heads_up_policy_night", match_policies_automatically: false,
      condition: { entity_id: "a.b", state: "on" },
    };
    const values = fromCall(original, ids);
    expect(values.audience).toBeUndefined();
    expect(values.push_audience).toBe("admins");
    expect(values.policy).toEqual(["Night"]);
    expect(values.extra).toEqual({ condition: { entity_id: "a.b", state: "on" } });
    expect(buildCall(values, ids)).toEqual(original);
  });

  it("takes the color list of the color picker, an unwritten severity and a timeout in seconds", () => {
    expect(fromCall({ message: "x", color: [3, 169, 244], severity: "success", timeout: 90 }).color).toBe("#03a9f4");
    expect(fromCall({ message: "x", severity: "success" }).severity).toBe("passive");
    expect(fromCall({ message: "x", timeout: 90 }).timeout).toBe("1.5");
    expect(fromCall({ message: "x", timeout: { hours: 1, minutes: 30 } }).timeout).toBe("90");
  });

  it("puts to, speakers and per-channel targets on their channels and drops the marker keys", () => {
    const values = fromCall({ message: "x", channels: ["push", "speak"], to: { push: { recipients: ["person.anna"] } }, speakers: ["media_player.k"], id: "abc", dry_run: true });
    expect(values.push_recipients).toEqual(["person.anna"]);
    expect(values.speak_recipients).toEqual(["media_player.k"]);
    expect(values.extra).toEqual({});
  });

  it("finds a button without text, a dismiss that cannot happen and a half-filled tap action", () => {
    expect(validate({ ...base, actions: [{ key: "a", label: "" }] }).map((p) => p.code)).toContain("label_required");
    expect(validate({ ...base, dismiss: "off", actions: [{ key: "a", label: "x", dismiss: true }] }).map((p) => p.code)).toContain("dismiss_needs_dismissible");
    expect(validate({ ...base, tap_problem: "action_incomplete" }).map((p) => p.code)).toContain("action_incomplete");
  });
});
