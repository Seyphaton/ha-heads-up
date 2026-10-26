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
DEFAULT_OPTIONS: Final = {
    OPT_MAX_BANNERS: 50,
    OPT_EVICT: True,
    OPT_DEFAULT_DISMISS_SCOPE: "user",
    OPT_DEFAULT_TIMEOUT: 24 * 3600,  # D-031
}

EVENT_CREATED: Final = f"{DOMAIN}_banner_created"
EVENT_UPDATED: Final = f"{DOMAIN}_banner_updated"
EVENT_DISMISSED: Final = f"{DOMAIN}_banner_dismissed"
EVENT_EXPIRED: Final = f"{DOMAIN}_banner_expired"
EVENT_CLEARED: Final = f"{DOMAIN}_banner_cleared"
