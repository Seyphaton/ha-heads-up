"""Two fake media players for the hub end-to-end checks (dev only)."""

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN


class StubPlayer(MediaPlayerEntity):
    """A player that records what it is asked to play and never makes a sound."""

    _attr_should_poll = False
    _attr_state = MediaPlayerState.IDLE

    def __init__(self, hass: HomeAssistant, name: str, announce: bool) -> None:
        self._record = hass.data[DOMAIN]
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{name.lower().replace(' ', '_')}"
        features = MediaPlayerEntityFeature.PLAY_MEDIA | MediaPlayerEntityFeature.VOLUME_SET
        if announce:
            features |= MediaPlayerEntityFeature.MEDIA_ANNOUNCE
        self._attr_supported_features = features

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        self._record(
            "media_player",
            "play_media",
            {"entity_id": self.entity_id, "media_type": media_type, "media_id": media_id, **kwargs},
        )

    async def async_set_volume_level(self, volume: float) -> None:
        self._record(
            "media_player", "volume_set", {"entity_id": self.entity_id, "volume_level": volume}
        )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Add the fake players."""
    async_add_entities(
        [
            StubPlayer(hass, "Hub stub kitchen", announce=True),
            StubPlayer(hass, "Hub stub office", announce=False),
        ]
    )
