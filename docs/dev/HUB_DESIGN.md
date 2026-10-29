# Notification hub: design record (Phase 15, design only, not approved for build)

Status: draft on branch `design/notification-hub`, 2026-10-28. Not merged. No code exists for anything in this file. It holds the full planning record: maintainer decisions, vision, concept model and open items. README material is marked "README material".

## TERMINOLOGY NOTE (read first)
Drafts of Parts A to P below were written before decision 29 (the banner is one channel). Where they say "the banner is the source of truth", "banner always on" or "banner owns the lifecycle", read: the *message* (what an automation creates) owns the lifecycle and the dashboard banner is one of its channels. Where they list fields on `create_banner`, read: candidates for the dedicated API design session, not decided. Decisions 1 to 30 win over any other text in this file.


## GIT AND PROCESS RULES FOR THIS PHASE (maintainer, latest feedback — highest priority)
1. **First action after plan approval: create a feature branch off `main`** (e.g. `design/notification-hub`). Nothing about the hub is committed or changed on `main`, ever, before an explicit go to merge. No push, no merge.
2. **Then document everything on that branch and commit it** (small logical commits). The entire plan must be preserved with ALL details: this plan file's content (vision, decisions table 1–30 and later, concept model, audiences, policies, channels, state/ledger, technical architecture, panel, UX journeys, risks, open items, maintainer feedback) goes into repo docs (see PART N), so nothing is lost if the session ends. Plan content that is not yet decided stays marked "open".
3. **Pause before implementing.** This phase has no implementation; after the documentation commits, stop and wait.
4. Docs that become public later (README pitch) are marked as such inside the design docs; nothing is added to README/CHANGELOG now (docs-style forbids documenting non-existent features).

## MAINTAINER FEEDBACK ROUND 3 (overrides conflicting text below)
- **Positioning:** the integration becomes the central notification hub; *the banner is one channel*. **Everything that exists today (create banner, clear banner, clear all, rules, card) must keep working without any use of the full hub.** The hub is purely additive; no policy needed for banners.
- **A1 rephrase (use this wording):** "Today's implementation sets the foundation for how notifications (right now: banners) are delivered; the hub expands this idea to more channels and additional features."
- **Problem statement (A2) is approved** ("replace a phone → edit 30 automations; leak alert at night; doorbell with nobody home; critical alert nobody read; dismissed on the phone, still shown on the wall tablet, still spoken again"): reuse it in the future README sales pitch. Mark it so in the design.
- **B1 Vocabulary is approved** and becomes part of the README in the future. **C6 end-to-end journeys are approved** and also feed the sales pitch. Mark both in the design as "README material".
- **B2 (shared vs channel-specific) = a dedicated design session BEFORE any implementation:** the maintainer will explicitly decide which functions (actions) and arguments exist. Includes the careful decision: **one generic `notify` action vs individual per-channel actions** like today's `create_banner`. Until then the plan does NOT define any new action names or arguments (no `policy`, `audience`, `channels`, `spoken`, `notify` fields on `create_banner`).
- **`create_banner` is one channel.** It cannot have a `channel` argument. Therefore decisions 26 and 29 below are *behavioral* (what overrides mean, banner is a normal channel) and NOT a field list; where the plan text above lists fields on `create_banner`/rules, treat them as *candidates for the dedicated API design session*, not as decided.
- Keep `docs/dev/` design docs product-neutral (confidentiality rules).

Deliverable of this phase: a complete, reviewable design (vision → UX → model → mechanics → details), decisions, open questions and verified API facts. No code, no strings, no manifest change. Everything below is the *proposed content* of the design plus the steps to produce it. Positions marked **(rec)** are my recommendation and are confirmed with the maintainer via AskUserQuestion before they are written as decisions.

Confidentiality: the tracked design states the differentiators as capabilities and requirements only. No product names, no comparisons, no copying from `.private/` (CLAUDE.md, D-036).

Maintainer answers so far (2026-10-27): hub may become core next to banners (not decided); channels in scope: Companion push, popup, TTS/speakers, persistent notification; mental model: **audiences + policies**, with flexible presence-based audiences ("last person left home", "all persons at home", "all not at home"); setup for **both** UI-first households and power users; **acknowledgement and escalation designed now**; groups/policies as config subentries if they separate cleanly from watch rules; popup via tiny global loader with lazy popup code.

---

## DECISIONS MADE WITH THE MAINTAINER (2026-10-27/28) — these override anything below that differs
| # | Topic | Decision |
|---|---|---|
| 1 | Channels | Companion push, popup, TTS/speakers, persistent notification, and the dashboard banner as one equal channel (see 29; "banner always on" is superseded) |
| 2 | Mental model | Audiences + policies |
| 3 | Setup users | UI-first and power users equally (same data model, plain actions/YAML too) |
| 4 | Ack/escalation | Designed now |
| 5 | Audience evaluation | Snapshot when a step fires; optional per-step "deliver on arrival" for people not home |
| 6 | Device discovery | Auto-resolve a person's Companion devices + manual override/add |
| 7 | Multi-device | All devices of a person (same tag so duplicates replace); per-person configurable |
| 8 | Unknown presence | Critical: notify anyway; lower severities: skipped with trace |
| 9 | Presence audiences | at home, not home, last to leave, first home, in/not in a zone |
| 10 | Audience combos | **No**: audiences are flat (one kind each); combine via several policy steps |
| 11 | Dismiss vs ack | Per policy (policy field decides whether dismiss counts as ack) |
| 12 | Snooze | Clear the user's push, pause their repeats, remind (re-notify) at snooze end. **Separate decision to record: banner and its notifications are always one linked message** (state changes on one surface apply to all) |
| 13 | Policy steps | Up to 4 timed steps |
| 14 | Policy matching | A policy lists severities and tags it applies to (tag list on the policy; banner keeps its single tag). `tag` today = card filter list (`docs/card.md:18`) AND `clear_banner` by id and/or tag (`docs/actions.md:243-248`); routing becomes a third use, accepted and documented |
| 15 | Quiet hours | Downgrade; critical bypasses unless the policy says otherwise |
| 16 | Severity change while active | Always restart the timeline with that severity's policy (pushes replaced) |
| 17 | Ack rule | Any recipient acknowledging stops escalation (policy may require all/named audience later) |
| 18 | Overdue steps after restart | Fire once on startup if still active and unacknowledged |
| 19 | Swipe-away of a push | Means nothing (never changes banner state) |
| 20 | Hub status | **Decide later** (design as a proposal; keep §1 non-goal until a build phase is approved) |
| 21 | Config UX | **Own admin panel from the start** (plus first-run wizard with presets) |
| 22 | Popup scope | Global, all dashboards (policy decides severities); no per-card or per-display restriction in the design |
| 23 | TTS | Media players, Assist satellites and targeted speakers; **rooms = HA areas + assigned speakers/displays**, no occupancy sensors |
| 24 | Lock-screen text | Per policy (full / title only / generic), default full |
| 25 | Persistent notification | Targets everyone; no special warning or validation |
| 26 | Automation deviation (behavior only) | When the hub is used, the caller may choose a policy and may replace the audience/channels of step 0 only; later steps, quiet hours and ack rule stay the policy's. **Which action(s) and arguments carry this is NOT decided** (dedicated API design session; one generic `notify` action vs per-channel actions; `create_banner` stays one channel with no `channel` argument) |
| 27 | Phasing of the later build | Delayed until the design is final |

| 28 | Empty audience | Fallback is configurable per policy step as fallback audiences and/or fallback channels, or none; no fixed default |
| 29 | **Banner is just one channel** (no special cases) | The unit an automation creates is a *message* with a lifecycle (existing `create_banner` keeps its name/API); banner, push, popup, speech, persistent notification are equal channels, each selectable per policy step (a step may use push only). With no policy, behavior is today's (dashboard channel only). No banner-only fields in the hub: no `notify: false` (opt-out = `channels` override without the unwanted channels); channel-specific text (e.g. speech) is a generic per-channel content override, not a special `spoken` field (exact shape to design) |
| 30 | First panel scope | Overview + editors, live preview ("who would be notified now"), per-message delivery trace, test send + first-run wizard |

Still open: exact shape of per-channel content overrides; where a dashboard session learns its room (for room-targeted popups); push identity / ledger / transition seam (technical, shown as "proposed" in the design for review, no UX impact); renaming of "banner" in docs/API (the API keeps `create_banner`; conceptual rename of the unit to "message" only in the hub design, to decide).

---

## PART A. Vision, USP, principles

### A1. One-sentence idea
Today's implementation sets the foundation for how notifications (right now: banners) are delivered; the hub expands this idea to more channels and additional features: *who must know, where, how loudly, and until when*, so automations only say what happened and the household's preferences live in one place. Existing banner features keep working on their own.

### A2. The problem the hub solves (README material: sales pitch, approved by the maintainer)
Today every automation hard-codes `notify.mobile_app_x`, speaker entities, quiet-hour templates and cleanup logic. Replace a phone → edit 30 automations. A leak alert at night, a doorbell with nobody home, a critical alert nobody read: all handled ad hoc, no shared state (dismissed on the phone, still shown on the wall tablet, still spoken again).

### A3. USP (what no part of the stack gives together)
1. **One lifecycle, many channels.** The banner is the single source of truth. Clear/expire/condition-false/dismiss on any surface removes or updates the push, popup, persistent notification and stops escalation. No ghost notifications.
2. **Audiences that follow the household, not device names.** People, roles, presence-based audiences, devices change without touching a rule or automation.
3. **Policies, not automations.** Severity-default behavior ("critical = push to everyone, popup on tablets, speak in occupied rooms, escalate after 5 min") defined once, overridable per banner/rule.
4. **Acknowledgement + escalation as first-class state.** "Someone saw it" is distinct from "hidden" and "snoozed"; unacknowledged critical items escalate to other people/channels, restart-safe.
5. **Explainability.** "Why did / didn't I get this?" per banner: a delivery trace (audience resolved to, policy step, skipped because quiet hours / not home / snoozed). Plus a preview: "who would be notified for severity X right now?" and a test action.
6. **Zero-config start, no lock-in.** Presets on first run; the same data is plain actions/YAML for power users; nothing changes for anyone who never enables the hub.
7. **Tiny footprint.** Global frontend cost for popups < 1 KB loader; no polling; presence via state listeners on person entities only; restart-safe delivery ledger.

### A4. Design principles
- Banner stays the owner of content and lifecycle; the hub only *delivers and mirrors state*.
- Additive and opt-in: hub disabled = today's behavior byte for byte (CLAUDE.md rule 3, D-073 parity, defaults off).
- Same capability for action banners and rule banners (rule 9).
- Never block banner creation on delivery. Delivery failures are visible but non-fatal.
- Prefer reusing what a channel already does well (Companion tag replace/clear, action buttons) over reimplementing.
- Every behavior is explainable and testable without real devices (fake notify/TTS services).
- Fewer concepts: Audience, Policy, Channel profile, Acknowledgement. Nothing else user-facing.

### A5. Explicit non-goals (v1 of the hub)
Phone calls/SMS/e-mail, chat services, non-Companion push services (documented path: later via a generic "notify service" channel), voice assistants asking questions, per-device volume learning, location history, presence *prediction*, access control beyond admin-only configuration (D-008). Recorded as ideas in OPEN_QUESTIONS.

---

## PART B. Top-down concept model

```
 Producer (action create_banner | watch rule)
        │  says: message, severity, [policy], [audience], [channels], buttons...
        ▼
   BANNER  (lifecycle owner: upsert, timeout, condition, dismiss, snooze, ack state)
        │  transitions: appeared · updated · hidden(reason) · acked · snoozed · ...
        ▼
   POLICY  (chosen by banner override, rule form, or severity default)
        │  steps over time: [audience + channels + profile] → wait → escalate ...
        ▼
   AUDIENCE → resolved to RECIPIENTS (people, devices, rooms) at the moment of delivery
        ▼
   CHANNELS: banner (dashboard) · push (Companion) · popup · TTS/speaker · persistent notification
        ▼
   DELIVERY LEDGER (what was sent where, state, next step due) → clears/updates follow the banner
```

### B1. Vocabulary (README material, approved by the maintainer)
- **Audience**: a named, reusable definition of *who*. Resolves to recipients when needed.
- **Policy**: a named, reusable definition of *how*: ordered steps (audience + channels + channel profile + timing), quiet hours, presence gating, acknowledgement rule, repeat/escalation.
- **Channel**: an output surface (banner, push, popup, tts, persistent). Banner is always on; the others are opt-in per policy step.
- **Recipient**: a resolved target within an audience: a person (with user_id), a device (notify target), a speaker (media player/satellite), a dashboard session.
- **Acknowledgement (ack)**: "a responsible recipient has seen/handled this". Stops escalation, does not hide the banner for others.
- **Delivery**: one (banner, recipient, channel) record with a state.

### B2. What is shared, what is not — DRAFT; a dedicated design session (before any implementation) decides explicitly which functions and arguments exist, incl. one generic `notify` action vs per-channel actions

| Concern | Shared across channels (banner/hub core) | Channel-specific |
|---|---|---|
| Content | `message`, `title`, `severity`, `icon`, `tag`, buttons (`actions`), `tap_action` | Rendering (HTML text / push payload / spoken text / persistent text), clipping to platform limits, optional `spoken` text |
| Identity | banner `id` | Push tag `hu-<install>-<id>`, notification_id, popup instance, TTS utterance id |
| Lifecycle | create/update/clear/expire/condition/mode/timeout/eviction | How a channel *shows* "cleared": push clear, popup close, persistent dismiss, TTS cannot unsay (optional "all clear" line) |
| Per-user state | dismissed_by, snoozed_until, ack | Which user a device maps to |
| Targeting | `people` (today) + audience (new) | Device/speaker resolution |
| Timing | timeout, condition, snooze | quiet hours, repeat, escalation delay, TTS queue |
| Actions | button keys, `heads_up_banner_action`, dismiss/snooze/ack semantics | Mapping to platform action ids; platform limit (3 Android, ~10 iOS) |
| Config | audiences, policies, severity defaults | channel profiles inside a policy step |

### B3. Capability matrix per channel (design table)
Columns: shows title/text · buttons · dismiss · snooze · ack · replaced on update · cleared when resolved · works when nobody is looking at a dashboard · privacy exposure (lock screen / room-wide / all HA users) · latency · failure signal. Filled during writing; examples: popup = needs an open dashboard, full UI, strongest attention on wall displays; TTS = no buttons, can't be cleared, room-wide exposure; persistent notification = visible to every HA user, no per-user dismiss (so only for audience "everyone/admins", flagged in the UI).

---

## PART C. User experience

### C1. Personas
- **Household admin (UI-first):** wants "tell everyone at home when X; tell me on my phone if nobody is home" without YAML.
- **Power user:** blueprints/YAML, many automations, wants one routing layer and explicit overrides.
- **Household member (viewer):** sees banners/popups/pushes; wants to dismiss, snooze, acknowledge from wherever they are; never configures.
- **Wall-tablet display:** passive, always on; popups and TTS matter most.

### C2. First run (guided, optional)
Options → "Set up notifications" (a config-flow wizard, repeatable):
1. *Who lives here?* pick persons → creates audience **Everyone** and **Adults** (optional).
2. *Which devices?* auto-detected phones per person (mobile_app), editable; unresolved persons flagged with a one-line fix. Optional: speakers and wall dashboards.
3. *How loud?* preset per severity: **Quiet** (banner only), **Balanced** (default: warning→push to people at home; critical→push to everyone + popup), **Loud** (critical also speaks, escalates). Shows a plain-language summary table.
4. *Test:* "Send a test" button (`heads_up.test_policy`) with a result list per recipient (sent / skipped because… / failed).
Result: a handful of audiences + three to four policies, all editable later as subentries. Skipping the wizard = hub off.

### C3. Day-to-day configuration screens (HA subentries, v1)
- NOTE (decision 21): the primary admin surface is an **own admin panel from the start** (sidebar panel: overview of audiences/policies/rules, editor, live "who would be notified now" preview, per-banner delivery trace, test sends, wizard entry). Subentries remain the storage and a fallback editor. The design must specify the panel (screens, WebSocket API, admin-only, build/serve approach under the no-build-step rule D-021, i18n) — a big addition to ask about.
- **Audiences** (list + add): name · type (People, Presence-based, Devices/rooms) · live preview line "right now: Anna, Ben".
- **Policies** (list + add): name · steps editor (guided form, 1–3 steps) · quiet hours · "applies to severities" · live explanation sentence generated from the config ("When a critical banner appears: push to Everyone and show a popup on tablets. If nobody acknowledges within 5 min, speak in the kitchen and push Backup contacts.").
- **Watch rules** (existing): new optional "Policy" select (default: by severity).
- **Options:** hub on/off, default policy per severity, install token (auto), delivery log size.
- A later admin panel (overview, live preview, delivery trace) is a candidate for 15f; v1 uses subentries + the explain/preview WebSocket + a diagnostics section.

### C4. Automation author experience (power users) — CANDIDATES ONLY; the real action/argument set is decided in the dedicated API design session (see feedback round 3). Existing `create_banner` etc. stay untouched.
- `create_banner` unchanged. New optional fields (decision 26): `policy` (name), `audience` and `channels` (replace the selected policy's step 0 only; later steps, quiet hours and ack rule stay the policy's). Open: `spoken` text and `notify: false`. Defaults come from the policy matching severity/tag. Everything also available as YAML in rule subentries and as plain actions (`heads_up.test_policy`, later `acknowledge`).
- Blueprint-friendly: names are slugs; audiences/policies referenced by name; unknown name = validation error with the list of valid names.

### C5. Recipient experience
- Push: concise text, severity-mapped sound/interruption, buttons mapped from banner buttons plus **Acknowledge / Snooze / Dismiss** where the platform allows; tapping opens the dashboard view (tap action → uri). Updating a banner replaces the push; resolving it removes it.
- Popup: only for configured severities; calm queue, shows next after dismiss; same buttons as the card; keyboard/focus-trap/Escape; reduced motion; 48 px targets; never steals typing focus except critical.
- Banner: unchanged, plus an "Acknowledged by Anna" line when relevant and an ack button when the policy asks for one.
- TTS: short, one sentence, queued, never repeats within a cooldown, "all clear" optional.
- Persistent notification (decision 25): targets everyone, opt-in per policy step, no warning or validation.

### C6. End-to-end journeys (README material for the sales pitch; each also becomes a design walkthrough and a test scenario)
1. **Leak at 03:00, family asleep:** critical rule banner → push (critical level, bypass quiet hours) to everyone, popup on tablet, speak in hallway; Ben acknowledges on phone → escalation stops, banner stays until the leak sensor is dry.
2. **Window left open, house empty:** audience "last person left home" gets a time-sensitive push; nobody else is bothered; when they return home and open the dashboard the banner shows; push cleared when window closes.
3. **Doorbell:** informational; popup on wall tablet + speak only if someone is home; nothing if nobody home (banner only). Condition/timeout 60 s clears everything.
4. **Washing machine done:** push to "who started it" (explicit audience via `people`), quiet hours turn it into banner only; delivered "on arrival" if they are out.
5. **Nobody acknowledges critical:** after 5 min escalate to "Backup contacts" (push) and speaker in the house; after 15 min repeat once; stops on ack/dismiss/clear.
6. **Phone replaced:** edit the person's device in one place; zero automation edits.
7. **"Why didn't I get that?"** open banner trace: "Skipped push to Anna: quiet hours (22:00–07:00), severity warning below bypass".
8. **Hub disabled / device offline:** banners work as today; failures logged once per device, visible in the trace.

### C7. Defaults and safety nets
Hub off by default. After the wizard, nothing sends until a policy is attached (severity default policies are created but marked "active" by the wizard's final confirmation). Rate limits (per device and global) with visible "suppressed N duplicates" entries. Critical always bypasses quiet hours unless the policy explicitly says otherwise. Safe fallback when an audience resolves to nobody: fallback audience (default: admins) or banner only, user-selectable, never silently nothing for critical.

### C8. Accessibility and i18n
Accessible names/roles on popup, live-region announcement policy, contrast via theme variables only, 48 px targets; all new strings in en/de/fr/es with key parity (existing test), spoken text uses the HA language per speaker where supported.

---

## PART D. Audiences in depth (flexible, presence-aware)

### D1. Audience kinds
- **People:** explicit person entities.
- **Role:** all admins; all persons; persons with a flag/label (label support to be verified).
- **Devices/rooms:** explicit notify targets, speakers, dashboards; "speakers in area X" via area registry (verify).
- **Presence-based (dynamic):**
  - `at_home` (all persons currently home)
  - `not_home` (all persons currently away)
  - `anyone_home` / `nobody_home` (also usable as policy gates)
  - `last_to_leave`: the person whose departure made the house empty; stays set until someone is home again
  - `first_home`: the first person arriving after the house was empty
  - `in_zone: <zone>` / `not_in_zone: <zone>` (e.g. work, school) (verify zone/person semantics)
  - `nearest/closest` is out (needs proximity; idea only)
- **No combinations (decision 10):** audiences are flat. To express "everyone except…" use several policy steps or a presence kind.

### D2. Evaluation semantics (the hard design questions, to be decided and written down)
- **When is membership computed?** *Snapshot* at the moment a policy step fires (rec) vs *live*. For steps with "deliver on arrival" the audience is live until the banner ends.
- **Pending delivery ("tell them when they're back"):** per step optional `hold_until_present`; recipients not home get the delivery when their presence flips to home, if the banner is still active and not dismissed/acked. Bounded by banner lifetime. Max hold configurable.
- **Presence flapping:** debounce (default 60 s) for `last_to_leave`/`first_home`; home/not_home from `person` state, not raw device trackers; `unknown/unavailable` person = treated as "unknown", never counted as away for critical (fail-safe notify).
- **Guests/no person:** explicit device recipients; never need a person.
- **Empty audience:** fallback chain (fallback audience → admins → banner only) with a trace line; for critical a fallback is mandatory (validated).
- **Person ↔ user_id ↔ devices:** person.user_id (existing N-10) for viewer mapping; person → device_trackers → mobile_app device → notify target (verify; if not resolvable, the form asks for the target explicitly and the preview marks it unresolved).
- **Multiple devices per person:** all, "most recently active" (unverified source), or "primary only"; per-person setting (rec: all, with replace-by-tag so duplicates don't stack).
- **Ordering/priority between audiences in one policy step:** union, de-duplicated by device; strictest profile wins.

### D3. Live preview
WebSocket `heads_up/preview_audience` and `preview_policy` (admin): returns the resolved recipients "right now" with the reason for each, powering the UI summary line and the diagnostics.

---

## PART E. Policies in depth

### E1. Structure
```
policy:
  name, description?
  applies_to: severities (default mapping) | explicit banner/rule reference only
  gate:            # optional preconditions for the whole policy
    quiet_hours: {from, to, days, bypass_severity: critical}
    presence: any | nobody_home | someone_home
  steps: [          # ordered, 1..4
    { after: 0s,
      audience: <name>,
      channels: [push, popup, tts, persistent],
      profile: { push: {...}, popup: {...}, tts: {...} },   # see PART F
      hold_until_present: false,
      repeat: {every: 10m, max: 3}? }
    { after: 5m, only_if: not_acknowledged, audience: ..., channels: [...] }
  ]
  acknowledgement: {mode: none | any | all | named, who: audience?, scope: banner}
  on_resolved: {announce_all_clear: false}
```
### E2. Selection order (which policy applies)
1. banner/rule explicit `policy` → 2. rule/tag mapping (optional, v1.1) → 3. severity default policy → 4. none (banner only). A `channels`/`audience` override on the banner modifies step 0 of the selected policy (documented precisely). `notify: false` skips the hub.
### E3. Quiet hours and presence gates
Quiet hours downgrade by profile (push → passive / banner only, TTS → skipped, popup → deferred to end of quiet hours or skipped) rather than dropping silently; `bypass_severity` and per-policy override. Time zone from HA config. DST-safe handling tested.
### E4. Escalation timeline
Steps are scheduled relative to the banner's *appearance for the policy* (first delivery). Timers are persisted as due-times in the ledger (like snoozes today) so restarts neither lose nor duplicate steps; a step whose due-time passed during downtime fires once on startup unless the banner is gone or acked (documented). A banner update with unchanged severity does not restart the timeline; severity increase restarts at the matching policy; severity decrease keeps going (decide).
### E5. Repeat
Max count, minimum interval, stops on ack/dismiss/snooze/clear, never re-pushes while a push with the same tag is still believed present unless `renotify` is set (Android `alert_once` semantics: verify).

---

## PART F. Channels in depth

For each: trigger mapping, payload, identity, update/clear semantics, buttons, failure modes, privacy, tests.

### F1. Banner (dashboard)
Unchanged contract. Additions: ack state fields in the payload (`acknowledged`, `acknowledged_by` first name/person only) behind card options; optional Acknowledge button (policy-driven). Parity with rules via the same payload builder (`to_client`).

### F2. Companion push
- Resolution: recipients → `notify.mobile_app_<device>` targets (verify service model in 2026.9/2026.10).
- Payload from banner + profile: `title`, `message`, `tag = hu-<install>-<id>`, `group`, Android `channel`/`importance` per severity (documented caveat: importance only lowered after first use, so channel ids are per severity+profile and stable), iOS `push.interruption-level` (passive/active/time-sensitive/critical; critical needs entitlement/permission, can't be replaced/grouped: therefore for critical, update = clear + send, flagged), `sticky`, `actions` (≤3 Android / ≤10 iOS: banner buttons first, then Ack, Snooze, Dismiss; clipped with a trace note), `clickAction` (tap action → uri).
- Action round trip: ids `hu:<banner>:<key>`; listener on `mobile_app_notification_action` → `press`/`dismiss`/`snooze`/`acknowledge` for the owning user (user mapping from device/person; verify event context). Unknown/stale ids are ignored with a trace line.
- Clear: `message: clear_notification` with the same tag on hide (cleared, expired, condition, dismiss by that user, snooze by that user) or ack when policy says "clear on ack".
- Android `notification_cleared` event (swipe away) is a *hint* only (not reliable on app close; iOS has none): policy option `swipe_means: nothing | dismiss | ack` (rec: nothing).
- Failure: unavailable service → trace `failed(service_not_found)`, one log warning per device per hour, no retry in v1 (retry/backoff idea).
- Multi-server collision: install token in tag/group.
### F3. Popup
- Delivery: no server push beyond the existing subscription; the loader asks `heads_up/popup_config` (is popup enabled for this user/dashboard/severity?), subscribes lazily, imports the popup module on first match.
- Loader budget < 1 KB, static path hashed + cached (D-050/D-064), `whenFrontendReady` (D-072), separate `HassKey`, removed on unload; survives N-42 (missing extra JS for 0.6 s after start) by re-checking on `visibilitychange`/reconnect.
- Behavior: queue by severity then age; one at a time; buttons = banner buttons + Ack/Snooze/Dismiss; closes on resolve; shown to the policy's audience on every dashboard (decision 22); rooms (HA areas) decide which displays when a step targets a room (how a dashboard session knows its area: open, ask in design); never on the login/onboarding pages; suppressed while the user is typing in an input unless critical.
- Frontend rule change: `frontend-card.md` "one module" → loader + popup module + card; decision recorded.
### F4. TTS / speakers
- Targets: media players, assist satellites (`announce`), or `tts` entities (verify the 2026.9/2026.10 actions: `tts.speak`, `assist_satellite.announce`, `media_player.play_media` with `announce`).
- Text: `spoken` field, else a short form of title/message; length limit; language per speaker (HA language default).
- Behavior: per-speaker queue, cooldown, no repeat of identical utterance within X, max volume cap, quiet-hours skip. Targets (decision 23): media players, Assist satellites, targeted speakers, and rooms = HA areas with their assigned speakers; no occupancy sensors, the audience's presence kinds decide who is told, rooms decide where.
- Volume handling and playback restore: use platform `announce` where available; otherwise "best effort, documented"; listed as unverified until checked.
- Not clearable. Optional "all clear" announcement on resolve.
### F5. Persistent notification
- `persistent_notification.create/dismiss` with `notification_id = hu_<id>`; visible to every HA user, so only for audiences that equal everyone/admins (UI warning, validation for per-user audiences). Update replaces; resolve dismisses. Fallback channel when push fails (optional step).

---

## PART G. State, lifecycle, consistency

### G1. Delivery states
`planned → held (until present / quiet hours / gate) → sent → (acked | cleared | superseded) ` or `skipped(reason)` / `failed(reason)`. All with timestamps; reasons are enumerated and translated for the trace.
### G2. Event × channel behavior matrix (to be completed in the design)
Rows: created, updated, severity raised/lowered, condition false/true flip, expired, evicted, cleared (action/admin/clear_all/rule), dismissed (user/global), snoozed (user/global), snooze ended, unsnoozed, acknowledged, button pressed, banner waiting → visible, startup/reload, person arrives/leaves. Columns: banner, push, popup, tts, persistent, escalation timer. Key defaults:
- Dismiss (user) → clear that user's push/popup; escalation unaffected unless dismiss counts as ack (rec: yes for scope user, configurable).
- Snooze (user) → clear their push, pause their repeats, **re-notify when the snooze ends** (remind semantics), escalation paused for that recipient only.
- Update → replace in place (push/popup/persistent); TTS re-speaks only if severity increased or policy says so.
- Cleared/expired/condition false → clear everywhere; "all clear" speech optional.
- Global dismiss → clear everywhere for everyone; ack implied.
### G3. Ledger and restart safety
Second Store `heads_up.deliveries` (own key, version 1, `minor_version` migration plan since the banner store has none): per (banner id, recipient key, channel) state + next due times + last tag/notification ids. Startup reconciliation: (1) drop ledger rows for banners that no longer exist and **clear** their pushes/persistent items, (2) never re-send anything already `sent` for a still-active banner, (3) fire overdue escalation steps once, (4) rules rebuilt silently (D-058) still reconcile. Size bound + age bound. Writes debounced.
### G4. The engine seam in the manager (technical)
Today there is no "became visible" hook (silent transitions: stored-banner `_apply_condition` false→true, `_snooze_elapsed`, startup rules; `created` fires for `waiting` banners). Design: the manager emits typed `BannerTransition(kind, banner_snapshot, reason, user_id, silent)` from **every** mutation point (one internal listener list beside `_listeners`), computed from visible-set diffs where needed; existing bus events and their exact payloads stay unchanged (tests pin them). The engine subscribes once; it never reads private manager state.
### G5. Concurrency
Manager mutators stay synchronous callbacks; engine work is async tasks created via `entry.async_create_background_task`, with per-banner serialization (a banner's deliveries run in order), bounded concurrency, cancellation on unload.

---

## PART H. Technical architecture

### H1. Modules (new, all optional at runtime)
`hub/audiences.py` (definitions + resolver + presence tracker), `hub/policies.py` (schema, selection, step planner), `hub/engine.py` (transitions → deliveries, escalation timers, ack), `hub/ledger.py` (Store), `hub/channels/{push,popup,tts,persistent}.py` (common `Channel` protocol: `capabilities`, `deliver`, `update`, `clear`), `hub/trace.py` (explain records, ring buffer), `frontend/heads-up-loader.js` + `heads-up-popup.js`.
### H2. Config storage
Config subentry types `audience` and `policy` (one `ConfigSubentryFlow` class each; registration dict; a `sync_hub` beside `sync_rules` called from `_async_entry_updated`; strings in `strings.json` + en/de/fr/es). **Separation test (to be documented with evidence):** rules and hub objects share no fields; only references go rule → policy name; therefore separable. Option keys for hub defaults go into `DEFAULT_OPTIONS`/options flow. Unknown subentry types on downgrade: verify behavior of older versions (document).
### H3. Public API (contract §13) — CANDIDATES ONLY, not decided (see feedback round 3)
- Actions: `heads_up.test_policy`, `heads_up.acknowledge` (id/tag), later `heads_up.send_test`. New optional fields on `create_banner`: `policy`, `audience`, `channels`, `spoken`, `acknowledge`, `notify`.
- Events: `heads_up_banner_acknowledged`, `heads_up_delivery_sent|cleared|failed|skipped` (compact payloads), unchanged existing events.
- WebSocket: `heads_up/acknowledge`, `heads_up/popup_config`, admin: `heads_up/preview_audience`, `heads_up/preview_policy`, `heads_up/deliveries`, `heads_up/trace`.
- Sensor: optional diagnostic entities only if useful (D-013 stays: no per-banner entities).
### H4. Dependencies
`after_dependencies` on `mobile_app`, `notify`, `tts`, `persistent_notification`, `media_player` as soft (verify HA semantics); hub features degrade gracefully when absent. manifest/hassfest implications recorded.
### H5. Performance and footprint
Listeners only on referenced `person.*`/zone/speaker entities; debounced ledger writes; trace ring buffer bounded (default 500 entries); popup loader < 1 KB gzipped test; no work when the hub is disabled.
### H6. Security and privacy
Hub configuration and diagnostics admin-only; ack/dismiss/snooze keep the existing "any targeted user" model (D-029) with targeting re-checked; notification-action events are accepted only for known pending ids, device-to-user mapping verified; message text on lock screens is the user's choice per policy (`privacy: full | title_only | generic`); logs contain ids and reasons, never message text.

---

## PART I. Parity and interplay rules
- Hub features are banner features: action and rule banners behave identically; the rule form gains Policy, Audience, Channels, Spoken, Acknowledge fields; §22.2 table gets rows; documented exceptions only with decision numbers.
- Existing `people` remains the *visibility* target of the banner; audience is the *delivery* target. Default: audience = people (if set) else policy audience, so existing banners behave sensibly (decision D-0xx).
- Snooze/dismiss/ack semantics are channel-independent and defined once (G2).

---

## PART J. Phasing for the later build — DELAYED until the design is final (decision 27). The list below is only a draft to stress-test the design; each sub-phase would be separately approved.
- **15a** Core: manager transition seam, ledger, audience (people/devices) + policy (single step), push create/update/clear, severity defaults, trace, test action, options + wizard skeleton.
- **15b** Presence-based audiences, quiet hours, hold-until-present, snooze remind.
- **15c** Acknowledgement + escalation + push action buttons round trip.
- **15d** Popup loader + popup.
- **15e** TTS/speakers.
- **15f** Persistent notification channel, admin overview/panel, polish.
Each sub-phase ships for action and rule banners, with docs, translations, `make check`/`hassfest`/`dev-smoke` (stub notify/TTS services in the dev config).

## PART K. Test strategy (design, for later)
Fake services via `async_mock_service` (notify, tts, persistent_notification); lifecycle×channel×source matrix (create, update, waiting→visible, condition flip, expire, evict, dismiss, snooze+end, unsnooze, ack, startup, reload); ledger restart/reconcile tests; presence flapping/debounce with the time freezer; DST/quiet-hour boundaries; audience cycle/empty/fallback cases; action-button round trip including spoofed/stale ids; payload exactness per platform; loader byte budget and registration tests; translation parity; dev-smoke with stub services; real-device checks listed as unverified in OPEN_QUESTIONS.

## PART L. Risks (R-11…)
Ghost/duplicate pushes after restart · platform limits (channels, critical level, action counts) · presence errors (unknown/stale) causing missed critical alerts · escalation storms · battery/rate · lock-screen privacy · loader missing after start (N-42) · speaker behavior varies by vendor · scope creep into a general notification platform · complexity of the UI for casual users (mitigated by wizard/presets/explain sentence) · downgrade with unknown subentries.

## PART M. Decisions → `docs/DECISIONS.md`. Decisions 1–27 above are made and are recorded as given (D-075 onward, one entry each, incl. the separate entry for "banner and notifications are one linked message"). The list below is the original draft; items already answered are done, the rest are asked next.
D-075 hub status and §1 amendment (core, opt-in) · D-076 mental model audiences+policies (**given**) · D-077 channel scope (**given**: push, popup, TTS, persistent) · D-078 audience kinds and presence semantics (snapshot vs live, debounce, unknown handling) · D-079 person→device resolution (auto + explicit fallback) · D-080 policy step model and selection order · D-081 ack semantics (dismiss implies ack?) and escalation timing/restart · D-082 delivery trigger via transition seam; push identity/tag · D-083 ledger store and reconcile rules · D-084 action-button mapping and permissions · D-085 snooze = remind later · D-086 popup loader scope/size budget/frontend rule change · D-087 TTS targets and volume handling · D-088 persistent notification privacy rule · D-089 override fields and parity rows · D-090 UX: wizard + subentries now, panel later · D-091 phasing 15a–15f. Already-answered ones are recorded as given; "not decided" stays where the maintainer said so.

## PART N. Steps to produce this phase's deliverables
0. **Branch first:** `git switch -c design/notification-hub` from `main` (clean tree confirmed). All following work and commits happen only there. No push, no merge, no change on main.
0b. **Preserve the plan first (commit 1):** write this plan's full content, nothing lost, into `docs/dev/HUB_DESIGN.md` (Claude-facing design doc, product-neutral): maintainer decisions table (1–30+), feedback round 3, vision/USP, vocabulary (marked README material), problem statement and journeys (marked README/pitch material), concept model, audiences, policies, channels, state/ledger, technical architecture, panel scope, risks, open items, process rules. Add decisions to `docs/DECISIONS.md` (D-075 onward, one per decision, incl. the separate record "banner and notifications are one linked message" and "banner is one channel, existing features work without the hub"). Open items go to `docs/OPEN_QUESTIONS.md`, including the dedicated API design session (actions/arguments, `notify` vs per-channel actions, per-channel content overrides, room↔dashboard-session mapping). Commit.
0c. Then continue with the steps below on the same branch (each its own commit), and **stop for approval** after the documentation commits; do not implement.
1. Read-only verification (HA docs/source for 2026.9.4 and 2026.10): notify service/entity model; mobile_app device↔person mapping and action event context; `tts`/`assist_satellite`/`media_player` announce actions; persistent_notification actions; `after_dependencies` semantics; second extra-JS URL registration; person/zone presence attributes; unknown-subentry-type behavior on older versions. New rows N-61… in `docs/dev/HA_API_NOTES.md`, status verified/unverified.
2. Separation check of subentry types (document evidence in the design).
3. Decision rounds with AskUserQuestion (grouped by topic: audience semantics; policy/ack/escalation; channels; UX; phasing); record each answer immediately in `docs/DECISIONS.md`.
4. Write the design: new `docs/DESIGN.md` §23 (sub-sections 23.1–23.20 following Parts A–L, with ASCII wireframes of the wizard, audience/policy forms, popup and push examples, the event×channel matrix, capability matrix, state diagrams); if it grows too long, a linked `docs/dev/HUB_DESIGN.md` referenced from §23. Update §0 row (proposed), §1 non-goal note, §3/§13/§14 (risks R-11…), §22.2 parity rows (planned).
5. `docs/OPEN_QUESTIONS.md`: replace the Phase 15 candidate with open design questions; ideas moved out of scope (retry/backoff, other push services, panel, proximity).
6. Update `docs/dev/STATE.md` and CLAUDE.md phase line. No human-facing docs (nothing user-visible exists yet; docs-style forbids documenting non-existent things).
7. `make check`; grep staged diff for product/competitor names and installation specifics; docs-check banned words/placeholders.
8. Local commits (one logical change each: API notes, decisions, design, state), nothing pushed. End with summary (done/decided/open/next) and ask whether to approve 15a.

## Critical files
Read-only references: `custom_components/heads_up/manager.py` (`_fire` 798, `_notify` 811, `_targets` 539, `_apply_condition` 593, `sync_rules` 394, `_snooze_elapsed` 776), `config_flow.py` (subentry registry 82, `RuleSubentryFlow` 274), `__init__.py` (`_async_entry_updated` 41), `frontend.py`, `models.py`, `websocket.py`, `services.py`, `tests/conftest.py`, `dev/smoke.py`.
Edited in this phase (docs only): `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`, `docs/dev/HA_API_NOTES.md`, `docs/dev/STATE.md`, `CLAUDE.md` (+ optional `docs/dev/HUB_DESIGN.md`).

## Verification of this phase
`make check` green; every requirement H-n traces to a planned test; every HA fact has a verified/unverified row; no section claims implemented behavior; staged-diff grep finds no product names, hosts or personal data; the maintainer can walk journeys C6.1–C6.8 against the design and find each step specified.

---

## API DESIGN SESSION (2026-10-28), answers so far
| # | Topic | Answer |
|---|---|---|
| A1 | Action shape | One generic action plus per-channel shortcuts (like `create_banner`) |
| A2 | Generic action name | `heads_up.notify` |
| A3 | Shortcuts besides `create_banner` | `push`, `popup`, `speak` (no persistent shortcut) |
| A4 | Lifecycle across channels | One id per message for all channels; clearing and re-sending the same id applies to every channel |
| A5 | Generic clear | One generic clear is enough for now; no separate acknowledge, snooze or dismiss actions |
| A6 | Push buttons | Dismiss and Snooze buttons are added automatically when the message allows them, handled by the hub with no automation; the message's own buttons come first |
| A7 | Shortcut behavior | Fixed channel, optional audience, no escalation steps |
| A8 | Routing fields on `notify` | `policy` and `channels`; per-call `audience` is allowed, but a call defines either channels or audience, not both (exact meaning to be confirmed) |
| A9 | Text | One shared text (message, title) for all written channels (banner, push, persistent, popup); speech gets an optional separate spoken text; no generic per-channel content block |
| A10 | Watch rules | Same behavior as `notify`; where rules live (source of truth) is open, review below |

## SOURCE-OF-TRUTH REVIEW: automations, hub page, or watch rules
Question: where do "when", "what" and "who/how" live so each fact has exactly one home, follows Home Assistant conventions and stays easy for UI-first users?

Three concerns:
1. **When** (trigger and lifecycle): an automation, or a watch rule's condition.
2. **What** (message content): text, title, severity, buttons, tag.
3. **Who and how** (delivery): audiences and policies (hub objects, D-079).

### Option 1: separate automations only (rules removed or frozen)
- For: Home Assistant's own place for triggers; full trigger power (events, time, webhooks); traces; YAML, blueprints, version control; no duplicated trigger logic.
- Against: UI users must write an automation plus a clear path; "show while the condition holds" is already solved by `create_banner` with `condition`, but needs an automation to call it; rules shipped in 0.4.0 and are documented, so removal breaks users; no single screen listing all watched conditions.
- Verdict: right for complex triggers, wrong as the only path.

### Option 2: hub page (panel) as the home of rules
- For: one screen for audiences, policies and rules; best UX for live preview and trace.
- Against: a custom panel is a UI, not a data store. If it keeps its own storage it leaves Home Assistant's conventions (config entries, subentries, backups, diagnostics); if it edits subentries it is only a front end; a second editor for the same objects must stay in sync; heavier to maintain (no build step, i18n, accessibility).
- Verdict: good as the editor, not as a separate source of truth.

### Option 3: watch rules as config subentries (today)
- For: native (Devices & services, backups, forms with selectors, reload on change); exists, tested, documented; same pipeline as actions (D-073).
- Against: a rule couples trigger, content and delivery in one form; every new delivery feature grows the form; content fields duplicate `notify`.
- Verdict: keep as the UI path for simple conditions, but thin it.

### Recommendation (to confirm)
- **Policies and audiences:** hub-owned config subentries. Single home of "who and how".
- **Rules:** stay subentries as *message sources*: trigger (entity or template, operator, `for`) plus message fields, plus `policy` and `channels` like `notify`. They carry no delivery logic of their own; they call the same pipeline as `notify`.
- **Automations:** keep calling `notify`, the shortcuts and `create_banner` for anything a rule cannot express.
- **Panel:** an editor and viewer over the same subentries (rules, audiences, policies, trace, preview). No second store.
- **Rule of single source:** when = rule or automation; what = the source's message fields; who and how = policy and audience, referenced by name. A change of phone or household member touches only audiences.
- **Open check:** whether a rule's message fields should be shared with `notify` through one schema (as D-073 already does for buttons and tap action).

---

## NOTIFY SHAPE AND SOURCE OF TRUTH (maintainer, 2026-10-28)
`heads_up.notify` states, and nothing else:
1. **Content:** title, message, optional text for speech.
2. **Primary channel:** banner, push, and so on.
3. **Audience OR direct recipients, never both:** a predefined audience (possibly dynamic, such as last to leave for push) or a group of speakers for speech; what is allowed depends on the channel.
4. **Policy:** the rules around delivery (quiet hours, escalation, and so on).

Watch rules also call `notify`: a rule is a stored `notify` call plus a trigger.

### Single source of truth (proposed answer)
| Fact | Single home |
|---|---|
| When a message exists (trigger, lifecycle) | The producer: an automation, or a watch rule's trigger and `for` |
| What is said (content, severity, tag, buttons) | The producer's `notify` call; for a rule, its stored `notify` arguments |
| Who can be reached (audiences, recipient groups, device mapping) | Hub subentries `audience` |
| How and when, escalation, quiet hours | Hub subentries `policy` |
| The live state of a message (dismissed, snoozed, acknowledged, deliveries) | The hub's message store and delivery ledger, one record per id |

Consequences:
- A rule holds the same fields as `notify` (one shared schema, as D-073 does for buttons) plus its trigger; parity between rules and actions follows from the schema.
- Replacing a phone or a household member touches audiences only.
- The panel is an editor and viewer over the same subentries; it keeps no store of its own.

### Open
- Whether a policy step may add channels beyond the call's primary channel (escalation to another channel), and how that reads with "primary channel".
- How the existing `create_banner` and `condition` map onto the `notify` content and trigger split.

---

## ESCALATION CHANNELS AND CONDITIONS (maintainer, 2026-10-28)

### Policy steps may add channels and audiences
The call's primary channel and audience are step 0. Later steps or fallbacks may use other channels and other audiences. Examples from the maintainer:
- a) Primary channel banner. By policy: escalate to push, then push to admins, then speech.
- b) Primary channel push to the last leavers. By policy: fallback to all not at home.
This also fixes how decision 28 (fallback audiences and channels) reads: fallbacks and escalations are policy steps.

### Conditions: a design session is needed (new)
Not covered so far in the hub design. Today's conditions: a message-level condition (entity with operators or a template, optional `for`), modes once and recurring, `wait_for_condition`, and the rule trigger. The hub adds places where a condition could matter:
1. **Lifecycle:** the message exists while a condition holds (today's behavior, must keep working).
2. **Trigger:** when a message is created (rule or automation).
3. **Policy gate:** the whole policy applies only if (quiet hours, someone home, any entity).
4. **Step gate:** a step runs only if (not acknowledged, entity state, time of day).
5. **Channel or recipient gate:** speak only if, push only to recipients for whom.
6. **Mid-flight changes:** a condition flips while escalation runs (stop, pause, restart, continue).
7. **One condition model or several:** reuse operators, `for` and templates everywhere, and whether conditions can be named and reused like audiences.
Open until the session: which levels get conditions, the shared schema, named conditions, flip behavior.

### Conditions: decisions (2026-10-28), see D-086
Generic condition only for the message lifecycle. Gates (policy, step, channel, recipient) are predefined: time window or quiet hours, presence, acknowledgement state, severity or tag. Escape hatch: named conditions as hub subentries holding the generic schema, usable as a gate and as a lifecycle condition. Lifecycle false ends the message; gates are checked when a step is due and a closed gate skips the step with a trace entry. Examples used to decide: guest mode on, alarm disarmed, freezer temperature above a limit for 10 minutes.

### notify field list (decided 2026-10-29, D-087)
| Group | Fields |
|---|---|
| Content | `message` (required), `title`, `icon`, `severity`, `actions`, `tap_action`, `tts_message` |
| Lifecycle | `id`, `tag`, `timeout`, `condition`, `mode`, `wait_for_condition`, `dismissible`, `dismiss_scope`, `snoozable`, `snooze_scope`, `snooze_options` |
| Delivery | `channels` (required list), `audience` XOR `recipients`, `policy` (omitted: matched by severity and tag; `none`: no policy behavior) |

Shortcuts `push`, `popup`, `speak`: fire and forget, tracked only when an `id` is given. `create_banner` is unchanged and keeps `people`. Return value: `id`, `status`, per-channel summary.

### Audience and recipient model (decided 2026-10-29, D-088)
- Audience: people-based, channel-neutral (persons or a presence kind). Recipient group: named explicit targets (speakers, satellites, areas, notify targets), tied to channels.
- `audience` takes an audience name; `recipients` takes entities or a recipient group name.
- Person profile (hub subentry): detected devices, manual overrides, primary device, accepted channels.
- Built-ins: Everyone, Admins, At home, Not home, Last to leave, First home.
- No usable device: skipped on push with a trace entry, shown in the panel with a fix link.

### Policy mechanics (decided 2026-10-29, D-089)
- Step timing: offset from the message start; due times stored.
- Closed gate outcomes: skip, delay until open, downgrade profile, stop completely (setting of the gate).
- Matching: most specific wins; identical matches refused at creation of the second policy.
- Fallback applies on empty audience, all deliveries failed, no acknowledgement in time.
- Open: whether "stop completely" ends delivery only or the whole message.

### Channels (decided 2026-10-29, D-090)
| Channel | audience | recipients |
|---|---|---|
| banner | yes | persons (empty = everyone) |
| push | yes | persons, notify targets or devices |
| popup | yes | persons, areas (displays) |
| speak | no | recipient groups, media players, Assist satellites, areas |
| persistent | no | none (targets everyone) |

Push levels: success/info passive, warning normal, critical time-sensitive; iOS critical is a policy opt-in. Speech fallback text: title if set, else message, shortened. Popup: corner card up to warning, centered modal for critical.

### Remaining channel details (decided 2026-10-29, D-091)
Speech: announce when supported, else current volume; no volume changes, no all-clear. Popup: persons only in v1 (area recipients not built; the popup row of the matrix narrows to persons). Rate limits: simple defaults in options, duplicate suppression, suppressed counts in the trace.

### Acknowledgement and push buttons (decided 2026-10-29, D-092)
Acknowledge button on push only if the policy step sets it. Button id `hu:<message>:<recipient>:<action>` identifies who pressed. Push Snooze uses the first snooze option. Banner line "Acknowledged by <first name>" with a card option to hide it.

### Admin panel and wizard (decided 2026-10-29, D-093)
Own forms (ha-form) saving through the subentry flow APIs; storage stays in subentries. Wizard as a panel stepper and as a config flow entry. Admin only, sidebar item. First panel: live preview, per-message delivery trace, recent messages list, test send. Open: restart survival of the recent list, panel registration API (to verify).

### Naming and field layout (accepted 2026-10-29, D-094)
Decided: the person profile is called **recipient profile** (hub subentry, D-088 object). Gate types: `time_window`, `presence`, `acknowledgement`, `severity_tag`, `named_condition`; outcomes `skip`, `delay`, `downgrade`, `stop`. `notify` response: message status `created`, `updated`, `waiting`, `condition_false` (as today) and per channel counts of `sent`, `held`, `skipped`, `failed`.

Policy layout (accepted; this supersedes the older sketch in Part E1 of this file):
```yaml
policy:
  name: Critical water
  match: {severities: [critical], tags: [water]}
  acknowledge: {dismiss_counts: true}
  steps:
    - after: 0                  # seconds from message start
      audience: Everyone        # or: recipients: [...]
      channels: [banner, push, popup]
      profile: {push: {level: time-sensitive}}
      gates:
        - {type: time_window, from: "22:00", to: "07:00", outcome: downgrade}
    - after: 300
      audience: Admins
      channels: [push]
      gates:
        - {type: acknowledgement, state: not_acknowledged, outcome: skip}
      fallback: {audience: Everyone}
    - after: 600
      recipients: [Ground floor speakers]
      channels: [speak]
      gates:
        - {type: acknowledgement, state: not_acknowledged, outcome: skip}
```
Correction 2026-10-29 (D-096): the first accepted sketch had push and speak in one step with an audience. A step has one "who"; speech and people channels go in separate steps.
