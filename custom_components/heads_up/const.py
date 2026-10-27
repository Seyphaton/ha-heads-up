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
DEFAULT_OPTIONS: Final = {
    OPT_MAX_BANNERS: 50,
    OPT_EVICT: True,
    OPT_DEFAULT_DISMISS_SCOPE: "user",
    OPT_DEFAULT_TIMEOUT: 24 * 3600,  # D-031
    OPT_DEFAULT_SNOOZABLE: False,  # existing dashboards look the same after an update (D-069)
    OPT_DEFAULT_SNOOZE_SCOPE: "user",
    OPT_DEFAULT_SNOOZE_OPTIONS: list(DEFAULT_SNOOZE_SECONDS),
}

EVENT_CREATED: Final = f"{DOMAIN}_banner_created"
EVENT_UPDATED: Final = f"{DOMAIN}_banner_updated"
EVENT_DISMISSED: Final = f"{DOMAIN}_banner_dismissed"
EVENT_EXPIRED: Final = f"{DOMAIN}_banner_expired"
EVENT_CLEARED: Final = f"{DOMAIN}_banner_cleared"
EVENT_ACTION: Final = f"{DOMAIN}_banner_action"
EVENT_SNOOZED: Final = f"{DOMAIN}_banner_snoozed"
