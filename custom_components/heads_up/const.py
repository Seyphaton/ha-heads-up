"""Constants for Heads Up."""

import re
from typing import Any, Final

DOMAIN: Final = "heads_up"

STORAGE_KEY: Final = "heads_up.banners"
STORAGE_VERSION: Final = 2  # 2: policy and target references are keys (D-200)
SAVE_DELAY: Final = 1  # seconds; batches parallel callers (D-023)

# Ordered lowest to highest: eviction picks from the front, the card sorts from the back.
SEVERITIES: Final = ("passive", "info", "warning", "critical")
# Earlier names still accepted in calls and card options (D-231): `success` is now `passive`.
SEVERITY_ALIASES: Final = {"success": "passive"}
DEFAULT_SEVERITY: Final = "warning"
DEFAULT_ICONS: Final = {
    "passive": "mdi:check-circle",
    "info": "mdi:information",
    "warning": "mdi:alert",
    "critical": "mdi:alert-octagon",
}
DISMISS_SCOPES: Final = ("user", "global")
MODES: Final = ("once", "recurring")
SNOOZE_SCOPES: Final = ("user", "global")
GLOBAL_SNOOZE_KEY: Final = "*"  # key in `snoozed_until` for a snooze that hides the banner for all
MAX_ACTIONS: Final = 3
MAX_ACTION_LABEL: Final = 40
MIN_SNOOZE_SECONDS: Final = 60
MAX_SNOOZE_SECONDS: Final = 7 * 86400
# A duration the viewer chooses (`snooze_custom`, D-219) is at most this long.
MAX_CUSTOM_SNOOZE_SECONDS: Final = 86400
MAX_SNOOZE_OPTIONS: Final = 6
# Choices of the options flow, in minutes (D-069).
DEFAULT_SNOOZE_SECONDS: Final = (900, 3600, 14400)  # 15 min, 1 h, 4 h
SNOOZE_PRESET_MINUTES: Final = (5, 15, 30, 60, 120, 240, 480, 1440)

RULE_SUBENTRY: Final = "rule"  # subentry type of a watch rule (DESIGN §17)
RULE_TAG: Final = "rule"
RULE_ID_PREFIX: Final = "rule_"

ID_PATTERN: Final = re.compile(r"^[a-z0-9_-]{1,64}$")
MAX_TITLE: Final = 100
MAX_MESSAGE: Final = 1000
MAX_IMAGE: Final = 2048  # characters of an image URL or path (D-127)
MAX_TIMEOUT_DAYS: Final = 365
MAX_FOR_SECONDS: Final = 24 * 3600  # longest `for` of a condition (D-066)

OPT_MAX_BANNERS: Final = "max_banners"
OPT_EVICT: Final = "evict"
OPT_DEFAULT_DISMISS_SCOPE: Final = "default_dismiss_scope"
OPT_DEFAULT_TIMEOUT: Final = "default_timeout"  # seconds; 0 = none
OPT_DEFAULT_SNOOZABLE: Final = "default_snoozable"
OPT_DEFAULT_SNOOZE_SCOPE: Final = "default_snooze_scope"
OPT_DEFAULT_SNOOZE_OPTIONS: Final = "default_snooze_options"  # seconds
# One snooze time for the buttons of the push and the popup; the banner offers the choices above.
OPT_QUICK_SNOOZE: Final = "quick_snooze_minutes"
OPT_DISABLE_ENDED_BUTTONS: Final = "disable_ended_buttons"  # D-125
# Hub (DESIGN §23). Channels of a message; only `banner` delivers in H1.
CHANNEL_BANNER: Final = "banner"
CHANNEL_PERSISTENT: Final = "persistent"
CHANNEL_MAIL: Final = "mail"
CHANNELS: Final = ("banner", "push", "popup", "speak", "persistent", "mail")
TARGET_CHANNELS: Final = (
    "banner",
    "push",
    "popup",
    "speak",
    "mail",
)  # channels that accept a target
SOURCE_ACTION: Final = "action"
SOURCE_RULE: Final = "rule"
SOURCE_SUMMARY: Final = "summary"  # a summary the hub made itself (H4c)
SUMMARY_PREFIX: Final = "summary:"  # ledger message id of a Summarize policy timer
SUMMARY_LIFETIME_HOURS: Final = 24
SUMMARY_MAX_LISTED: Final = 10
POLICY_NONE: Final = "none"
# In a call's `policy` list: the automatic policies that apply, plus any policy named next to it.
POLICY_AUTOMATIC: Final = "automatic"
# How a policy attaches to a message: by itself when severity and tag match, or only when a call
# names it (D-146).
POLICY_APPLY: Final = ("auto", "manual")
# How the automatic policies interact (D-148, D-149): only the first that applies runs, in the order
# of the policy list, or every policy that applies runs.
DELIVERIES_KEY: Final = "heads_up.deliveries"
DELIVERIES_VERSION: Final = 2  # 2: timer and held rows hold policy keys (D-200)
DELIVERIES_MINOR_VERSION: Final = 1
AUDIENCE_SUBENTRY: Final = "audience"
GROUP_SUBENTRY: Final = "recipient_group"
PROFILE_SUBENTRY: Final = "recipient_profile"
POLICY_SUBENTRY: Final = "policy"
POLICY_TYPES: Final = (
    "escalation",
    "reminder",
    "quiet_hours",
    "presence",
    "fallback",
    "summarize",
    "deliver",
    "get_through",  # the band "Always gets through" (D-224)
)
WEEKDAYS: Final = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
QUIET_ACTIONS: Final = ("quiet", "wait", "drop")
FALLBACK_WHEN: Final = ("no_audience", "failed", "both")
HOLD_QUIET: Final = "quiet_hours"
# Kept as "away" in stored deliveries, so 1.0 holds stay valid (D-214); Presence uses it too.
HOLD_AWAY: Final = "away"
TYPE_AWAY_OLD: Final = "away"  # the 1.0 type key, converted to "presence" (D-212, D-214)
PRESENCE_WHEN: Final = ("not_in", "in")
PRESENCE_WHO: Final = ("nobody", "somebody")
PRESENCE_THEN: Final = ("hold", "drop")
AFTER_WAIT: Final = ("send", "drop")
PRESENCE_PEOPLE_CHANNELS: Final = ("push", "popup", "mail")
PRESENCE_CHANNELS: Final = ("push", "popup", "mail", "speak")
POLICY_CHANNELS: Final = (
    "push",
    "popup",
    "speak",
    "persistent",
    "mail",
)  # an escalation can add these
TIMER_CHANNEL: Final = "timer"  # ledger rows of this channel hold escalation and reminder due times
GROUP_SUFFIX: Final = " (group)"  # how a recipient group is named in calls
PRESENCE_KEY: Final = "heads_up.presence"
TRACE_VERSION: Final = 2  # raised with the other stores so older code refuses it (D-200)
AUDIENCE_USAGE_KEY: Final = "heads_up.audience_usage"  # count and last use (D-227)
TRACE_KEY: Final = "heads_up.trace"  # the delivery trace survives a restart (D-194)
# Built in, not stored (D-080). Names are the ones calls use.
# A banner whose audience is empty when it is created is aimed at this person, who does not exist:
# an empty `people` list would show it to everyone (D-131).
BANNER_NOBODY: Final = "person.heads_up_nobody"
# Needs-attention warnings the admin chose to hide, as a list of keys in the entry options (D-135).
OPT_ATTENTION_DISMISSED: Final = "attention_dismissed"
# Built-in audiences the admin switched off, as a list of names in the entry options (D-136).
OPT_AUDIENCES_DISABLED: Final = "audiences_disabled"
MAX_ATTENTION_DISMISSED: Final = 200
BUILTIN_AUDIENCES: Final = {
    "Everyone": "everyone",
    "Admins": "admins",
    "At home": "at_home",
    "Not home": "not_home",
    "Last to leave": "last_to_leave",
    "First home": "first_home",
}
# Sent when audiences, options or the settled presence change; the audience sensors listen (D-186).
SIGNAL_AUDIENCES: Final = f"{DOMAIN}_audiences_changed"
SIGNAL_POLICIES: Final = f"{DOMAIN}_policies_changed"  # the policy switches listen (D-186)
AUDIENCE_KINDS: Final = ("persons", "presence")
PRESENCE_KINDS: Final = (
    "at_home",
    "not_home",
    "last_to_leave",
    "first_home",
    "in_zone",
    "not_in_zone",
)
ZONE_KINDS: Final = ("in_zone", "not_in_zone")
HOME_ZONE: Final = "zone.home"
PROFILE_CHANNELS: Final = (
    "banner",
    "push",
    "popup",
    "mail",
)  # channels a person's profile can accept
DEFAULT_PROFILE_CHANNELS: Final = ("banner", "push", "popup")  # mail is opt-in per person (D-129)
MAIL_GLOBAL: Final = "Global address"  # the recipient name of the shared mail address (D-129)
MAIL_GLOBAL_KEY: Final = "mail:global"  # its ledger key
MAIL_PLACEHOLDERS: Final = ("severity", "title", "message", "person", "person_id", "id", "tag")
MAX_MAIL_SUBJECT: Final = 200
MAX_MAIL_BODY: Final = 2000
MAX_MAIL_ADDRESS: Final = 254
OPT_PRESENCE_DEBOUNCE: Final = "presence_debounce_seconds"  # D-109
# Push settings (D-097, D-110). Edited in the panel (H9c); no form in the options flow.
OPT_PUSH_LEVELS: Final = "push_levels"  # severity to level
OPT_PUSH_LOCKSCREEN: Final = "push_lockscreen"  # full, title_only, generic
OPT_PUSH_CHANNEL_ID: Final = "push_channel_id"  # Android notification channel prefix
OPT_PUSH_STICKY: Final = "push_sticky"
PUSH_LEVELS: Final = ("passive", "normal", "time-sensitive", "critical")
PUSH_LOCKSCREEN: Final = ("full", "title_only", "generic")
DEFAULT_PUSH_LEVELS: Final = {
    "passive": "passive",
    "info": "normal",
    "warning": "time-sensitive",
    "critical": "critical",  # an alarm on iOS and Android (D-155); default for new setups (D-230)
}
# The defaults up to 1.1.0-beta.2: written into the options of an existing setup at the upgrade,
# so its phones behave as before (D-230, D-213).
PUSH_LEVELS_1_0: Final = {
    "passive": "passive",
    "info": "passive",
    "warning": "normal",
    "critical": "time-sensitive",
}
# The admin panel (D-107, D-117). Off until the user switches it on in the setup step or Settings.
OPT_SHOW_PANEL: Final = "show_panel"
PANEL_URL_PATH: Final = "heads-up"
PANEL_TITLE: Final = "Heads Up"
PANEL_ICON: Final = "mdi:bell-ring-outline"
# Popup settings (D-090, D-115): how a popup looks per severity. Edited in the panel (H9c).
OPT_POPUP_STYLES: Final = "popup_styles"
# `card` is the corner card at the bottom right; the other corners and the centred window are the
# alternatives (D-180). A stored `card` keeps its meaning.
POPUP_STYLES: Final = (
    "card",
    "card_bottom_left",
    "card_top_right",
    "card_top_left",
    "modal",
    "off",
)
DEFAULT_POPUP_STYLES: Final[dict[str, str]] = {
    "passive": "card",
    "info": "card",
    "warning": "card",
    "critical": "modal",
}
# Speech settings (D-114).
OPT_SPEAK_MAX_LENGTH: Final = "speak_max_length"  # characters
TEST_ID_PREFIX: Final = "hu_test_"  # ids of the messages sent from Test send
OPT_SPEAK_COOLDOWN: Final = "speak_cooldown_seconds"  # 0 for none
OPT_SPEAK_TTS_ENTITY: Final = "speak_tts_entity"  # empty: the only tts entity
OPT_SPEAK_LANGUAGE: Final = "speak_language"  # empty: the Home Assistant language
# Speech volume (D-208, D-215, D-217): put back after speaking, time bands, per severity.
OPT_SPEAK_RESTORE_VOLUME: Final = "speak_restore_volume"
OPT_SPEAK_VOLUME_BANDS: Final = "speak_volume_bands"  # [{from, to, volume (percent)}], at most 4
OPT_SPEAK_SEVERITY_VOLUME: Final = "speak_severity_volume"  # {severity: percent}
MAX_VOLUME_BANDS: Final = 4
# Per severity: {label, icon, color} set on the Severities page (D-222, D-223). Empty: defaults.
OPT_SEVERITY_DISPLAY: Final = "severity_display"
MAX_SEVERITY_LABEL: Final = 30
# Mail settings (D-129). Edited on the panel's Channels page.
OPT_MAIL_SERVICE: Final = "mail_service"  # name of a notify service, empty: mail is off
OPT_MAIL_ADDRESS: Final = "mail_global_address"  # the shared address, empty: none
OPT_MAIL_SUBJECT: Final = "mail_subject"
OPT_MAIL_BODY: Final = "mail_body"
OPT_INSTALL_TOKEN: Final = "install_token"  # 6 hex characters, used in push tags (D-080)
OPT_TRACE_ENTRIES: Final = "trace_entries"
OPT_RECENT_MESSAGES: Final = "recent_messages"
# Stored in H1, enforced in H10.
OPT_RATE_PER_DEVICE: Final = "rate_per_device_per_minute"
OPT_RATE_TOTAL: Final = "rate_total_per_minute"
OPT_DEDUPE_SECONDS: Final = "dedupe_seconds"

DEFAULT_OPTIONS: Final = {
    OPT_MAX_BANNERS: 50,
    OPT_EVICT: True,
    OPT_DEFAULT_DISMISS_SCOPE: "user",
    OPT_DEFAULT_TIMEOUT: 24 * 3600,  # D-031
    OPT_DEFAULT_SNOOZABLE: False,  # existing dashboards look the same after an update (D-069)
    OPT_DEFAULT_SNOOZE_SCOPE: "user",
    OPT_DEFAULT_SNOOZE_OPTIONS: list(DEFAULT_SNOOZE_SECONDS),
    OPT_QUICK_SNOOZE: 15,
    OPT_DISABLE_ENDED_BUTTONS: True,
    OPT_PRESENCE_DEBOUNCE: 60,
    OPT_PUSH_LEVELS: DEFAULT_PUSH_LEVELS,
    OPT_PUSH_LOCKSCREEN: "full",
    OPT_PUSH_CHANNEL_ID: "heads_up",
    OPT_PUSH_STICKY: False,
    OPT_SHOW_PANEL: False,
    OPT_POPUP_STYLES: DEFAULT_POPUP_STYLES,
    OPT_SPEAK_MAX_LENGTH: 200,
    OPT_SPEAK_COOLDOWN: 60,
    OPT_SPEAK_TTS_ENTITY: "",
    OPT_SPEAK_LANGUAGE: "",
    OPT_SPEAK_RESTORE_VOLUME: True,  # D-215
    OPT_SPEAK_VOLUME_BANDS: [],  # none: the volume is not changed (1.0 behaviour, D-213)
    OPT_SPEAK_SEVERITY_VOLUME: {},
    OPT_SEVERITY_DISPLAY: {},  # nothing set: everything looks as in 1.0 (D-213)
    OPT_MAIL_SERVICE: "",
    OPT_MAIL_ADDRESS: "",
    OPT_MAIL_SUBJECT: "{severity}: {title}",
    OPT_MAIL_BODY: "{message}",
    OPT_TRACE_ENTRIES: 500,
    OPT_RECENT_MESSAGES: 100,
    OPT_RATE_PER_DEVICE: 5,
    OPT_RATE_TOTAL: 60,
    OPT_DEDUPE_SECONDS: 30,
}

EVENT_CREATED: Final = f"{DOMAIN}_banner_created"
EVENT_UPDATED: Final = f"{DOMAIN}_banner_updated"
EVENT_DISMISSED: Final = f"{DOMAIN}_banner_dismissed"
EVENT_EXPIRED: Final = f"{DOMAIN}_banner_expired"
EVENT_CLEARED: Final = f"{DOMAIN}_banner_cleared"
EVENT_ACTION: Final = f"{DOMAIN}_banner_action"
EVENT_SNOOZED: Final = f"{DOMAIN}_banner_snoozed"
EVENT_UNSNOOZED: Final = f"{DOMAIN}_banner_unsnoozed"
# `reason` of the unsnoozed event (D-221): ended by the viewer, or the time ran out.
UNSNOOZE_USER: Final = "user"
UNSNOOZE_ENDED: Final = "ended"
EVENT_DELIVERY_FAILED: Final = f"{DOMAIN}_delivery_failed"  # D-128


def canonical_severity(value: Any) -> Any:
    """A severity by its current name: `success` is read as `passive` (D-231)."""
    return SEVERITY_ALIASES.get(value, value) if isinstance(value, str) else value
