"""Constants for Heads Up."""

import re
from typing import Final

DOMAIN: Final = "heads_up"

STORAGE_KEY: Final = "heads_up.banners"
STORAGE_VERSION: Final = 1
SAVE_DELAY: Final = 1  # seconds; batches parallel callers (D-023)

# Ordered lowest to highest: eviction picks from the front, the card sorts from the back.
SEVERITIES: Final = ("success", "info", "warning", "critical")
DEFAULT_SEVERITY: Final = "warning"
DEFAULT_ICONS: Final = {
    "success": "mdi:check-circle",
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
MAX_TIMEOUT_DAYS: Final = 365
MAX_FOR_SECONDS: Final = 24 * 3600  # longest `for` of a condition (D-066)

OPT_MAX_BANNERS: Final = "max_banners"
OPT_EVICT: Final = "evict"
OPT_DEFAULT_DISMISS_SCOPE: Final = "default_dismiss_scope"
OPT_DEFAULT_TIMEOUT: Final = "default_timeout"  # seconds; 0 = none
OPT_DEFAULT_SNOOZABLE: Final = "default_snoozable"
OPT_DEFAULT_SNOOZE_SCOPE: Final = "default_snooze_scope"
OPT_DEFAULT_SNOOZE_OPTIONS: Final = "default_snooze_options"  # seconds
# Hub (DESIGN §23). Channels of a message; only `banner` delivers in H1.
CHANNEL_BANNER: Final = "banner"
CHANNEL_PERSISTENT: Final = "persistent"
CHANNELS: Final = ("banner", "push", "popup", "speak", "persistent")
TARGET_CHANNELS: Final = ("banner", "push", "popup", "speak")  # channels that accept a target
SOURCE_ACTION: Final = "action"
SOURCE_RULE: Final = "rule"
SOURCE_SUMMARY: Final = "summary"  # a summary the hub made itself (H4c)
SUMMARY_PREFIX: Final = "summary:"  # ledger message id of a Summarize policy timer
SUMMARY_LIFETIME_HOURS: Final = 24
SUMMARY_MAX_LISTED: Final = 10
POLICY_NONE: Final = "none"
DELIVERIES_KEY: Final = "heads_up.deliveries"
DELIVERIES_VERSION: Final = 1
DELIVERIES_MINOR_VERSION: Final = 1
AUDIENCE_SUBENTRY: Final = "audience"
GROUP_SUBENTRY: Final = "recipient_group"
PROFILE_SUBENTRY: Final = "recipient_profile"
POLICY_SUBENTRY: Final = "policy"
POLICY_TYPES: Final = (
    "escalation",
    "reminder",
    "quiet_hours",
    "away",
    "fallback",
    "summarize",
    "deliver",
)
WEEKDAYS: Final = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
QUIET_ACTIONS: Final = ("quiet", "wait", "drop")
FALLBACK_WHEN: Final = ("no_audience", "failed", "both")
HOLD_QUIET: Final = "quiet_hours"
HOLD_AWAY: Final = "away"
POLICY_CHANNELS: Final = ("push", "popup", "speak", "persistent")  # an escalation can add these
TIMER_CHANNEL: Final = "timer"  # ledger rows of this channel hold escalation and reminder due times
GROUP_SUFFIX: Final = " (group)"  # how a recipient group is named in calls
PRESENCE_KEY: Final = "heads_up.presence"
# Built in, not stored (D-080). Names are the ones calls use.
BUILTIN_AUDIENCES: Final = {
    "Everyone": "everyone",
    "Admins": "admins",
    "At home": "at_home",
    "Not home": "not_home",
    "Last to leave": "last_to_leave",
    "First home": "first_home",
}
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
PROFILE_CHANNELS: Final = ("banner", "push", "popup")  # channels a person's profile can accept
OPT_PRESENCE_DEBOUNCE: Final = "presence_debounce_seconds"  # D-109
# Push settings (D-097, D-110). Edited in the panel (H9c); no form in the options flow.
OPT_PUSH_LEVELS: Final = "push_levels"  # severity to level
OPT_PUSH_LOCKSCREEN: Final = "push_lockscreen"  # full, title_only, generic
OPT_PUSH_CHANNEL_ID: Final = "push_channel_id"  # Android notification channel prefix
OPT_PUSH_STICKY: Final = "push_sticky"
PUSH_LEVELS: Final = ("passive", "normal", "time-sensitive", "critical")
PUSH_LOCKSCREEN: Final = ("full", "title_only", "generic")
DEFAULT_PUSH_LEVELS: Final = {
    "success": "passive",
    "info": "passive",
    "warning": "normal",
    "critical": "time-sensitive",  # "critical" is the iOS opt-in
}
# The admin panel (D-107, D-117). Off until the user switches it on in the setup step or Settings.
OPT_SHOW_PANEL: Final = "show_panel"
PANEL_URL_PATH: Final = "heads-up"
PANEL_TITLE: Final = "Heads Up"
PANEL_ICON: Final = "mdi:bell-ring-outline"
# Popup settings (D-090, D-115): how a popup looks per severity. Edited in the panel (H9c).
OPT_POPUP_STYLES: Final = "popup_styles"
POPUP_STYLES: Final = ("card", "modal", "off")
DEFAULT_POPUP_STYLES: Final[dict[str, str]] = {
    "success": "card",
    "info": "card",
    "warning": "card",
    "critical": "modal",
}
# Speech settings (D-114).
OPT_SPEAK_MAX_LENGTH: Final = "speak_max_length"  # characters
OPT_SPEAK_COOLDOWN: Final = "speak_cooldown_seconds"  # 0 for none
OPT_SPEAK_TTS_ENTITY: Final = "speak_tts_entity"  # empty: the only tts entity
OPT_SPEAK_LANGUAGE: Final = "speak_language"  # empty: the Home Assistant language
OPT_HUB_ENABLED: Final = "hub_enabled"  # D-107: on by default, this is the off switch
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
    OPT_HUB_ENABLED: True,
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
