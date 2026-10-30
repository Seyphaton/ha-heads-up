# Hub decision index

Which hub decisions are current. Read this before any hub work, because several early decisions were replaced later. The decision text is in `docs/DECISIONS.md`; the consolidated design is `docs/DESIGN.md` section 23.

Status values: current, partly superseded (the part that still holds is named), superseded.

## Index
- D-075 Hub direction. Superseded in status by D-107: the hub is built, on feature branches only, and the "no push delivery" non-goal is gone.
- D-107 The hub is built; on by default with an off switch; the sidebar entry is chosen during initial setup; nothing reaches `main` until the maintainer confirms. Current.
- D-109 H2 choices: presence delay 60 s configurable, stored Last to leave / First home, areas by Home Assistant area, automatic profiles. Current.
- D-108 Generic clear is the new action `clear`; `clear_banner` matches only messages with the banner channel. Current.
- D-076 Everything existing works without the hub. Current.
- D-077 Banner is one channel; the unit is a message. Current. `create_banner` takes no `channel` argument.
- D-078 Banner and its notifications are one linked message; snooze clears the user's push and reminds at its end. Current.
- D-079 Audiences and policies. Partly superseded by D-097. Still holds: audiences are flat; a policy applies by severities and tags; the most specific policy wins. Superseded: a policy as up to 4 timed steps; the caller replacing step 0.
- D-080 Audience semantics. Current. Presence kinds, snapshot, person devices found automatically with manual override, all devices notified, unknown presence. "A step may deliver on arrival" is now the Away policy (D-097).
- D-081 Acknowledgement, escalation, severity change. Current in substance. Any recipient stops escalation; dismissal counting is a policy setting; quiet hours downgrade with critical passing; severity change restarts; overdue escalation fires once after a restart; swiping a push away means nothing. Gate wording superseded by D-097.
- D-082 Channels and admin UX. Partly superseded. Holds: channel list, persistent notification targets everyone, lock-screen text setting, own admin panel, wizard. Superseded: navigation (D-103); popup areas (narrowed by D-091).
- D-083 One generic `notify` action plus shortcuts. Partly superseded. Holds: `heads_up.notify`, shortcuts `push`, `popup`, `speak`, `create_banner` unchanged, one id for all channels, one generic clear, automatic Dismiss and Snooze buttons on push, shared written text with optional `tts_message`. Superseded: "watch rules are stored notify calls" (D-100).
- D-084 Source of truth. Partly superseded. Holds: when and what live with the producer, who and how in hub subentries, live state in the hub store, the panel keeps no store. Superseded: the rules statement (D-100).
- D-085 Escalation adds channels and audiences. Current as Escalation and Fallback policies (D-097).
- D-086 Conditions in the hub. Superseded by D-099 except: the generic condition stays the message lifecycle condition; if it ends the message, every channel is cleared and all policies for it stop.
- D-087 `notify` field list. Partly superseded. Holds: content, lifecycle and `policy` fields, `create_banner` unchanged, shortcut behavior, response. Superseded: top-level `audience`/`recipients` and `channels` as a plain list with one who (D-098).
- D-088 Audience, recipient group, recipient profile. Current.
- D-089 Policy mechanics. Mostly superseded by D-097. Holds: matching (most specific wins), fallback triggers as the Fallback policy.
- D-090 Channels: recipient kinds, push levels, speech text, popup. Current (popup recipients narrowed by D-091; wording about steps replaced by policies).
- D-091 Volume, speech cleanup, popup areas, rate limits. Current.
- D-092 Acknowledgement and push buttons. Partly superseded. Holds: button ids `hu:<message>:<recipient>:<action>`, Snooze uses the first snooze option, banner line "Acknowledged by <first name>" with a card option to hide it. Superseded: Acknowledge button set per step (it is added when an escalation or reminder policy applies, D-097).
- D-093 Admin panel and wizard. Partly superseded. Holds: own forms saving through the subentry flow APIs, wizard as panel flow and config flow entry, admin only. Superseded: navigation (D-103) and the first panel scope (D-101, D-104).
- D-094 Naming, gate types, response values, policy layout. Mostly superseded by D-097. Holds: "recipient profile" name; response values (`created`, `updated`, `waiting`, `condition_false` plus per channel `sent`, `held`, `skipped`, `failed`).
- D-095 Gate and profile fields. Superseded by D-097. Holds in spirit: the downgrade meaning (Quiet hours "quiet").
- D-096 One who per step. Superseded by D-098.
- D-097 Typed policies. Current.
- D-098 Targets per channel (`to` mapping). Current.
- D-099 No "only if" and no named conditions. Current.
- D-100 Watch rules are frozen. Current.
- D-101 One tab for preview and test send; no compose form. Current.
- D-102 Navigation, first version. Superseded by D-103.
- D-103 Navigation, second version. Current.
- D-104 Overview content. Current.
- D-105 Summarized message held on every channel, banner too. Current.
- D-106 Summary details, no default delivery, precedence. Current.

## The current truth in one page
- Status: approved for build (D-107). On by default with an off switch; the panel sidebar entry is opt-in during initial setup.
- Unit: a message with one id; channels: banner, push, popup, speak, persistent.
- Call: `heads_up.notify` with content, lifecycle, `channels` (required list), `to` (a target per channel: `audience` or `recipients`, never both), `policy` (omitted: all that apply; `none`: no policy behavior). Shortcuts `push`, `popup`, `speak`. `create_banner` and watch rules unchanged (rules frozen).
- Targets: banner (audience or persons, empty means everyone), push (audience, or persons and phones), popup (audience or persons), speak (speakers, groups, satellites, areas; no audience), persistent (none).
- Objects: audience (flat; persons or presence), recipient group, recipient profile, policy (typed rules). No named conditions.
- Policy types: Escalation, Quiet hours, Fallback, Reminder, Away, Summarize. Common fields: name, type, applies to, enabled. Precedence Summarize, Quiet hours, Away, Fallback.
- Panel: five groups (Overview; Notifications and Rules; Configuration; Settings; FAQ and Examples).
