"""Channel registry. H1 registers the banner channel; every other channel is a placeholder
until its package exists (H3 push, H5 speak, H6 popup, H7 persistent) and replaces it.
"""

from __future__ import annotations

from ...const import CHANNELS
from ...models import Banner
from .banner import BannerChannel
from .base import Capabilities, Channel, Outcome, Result

__all__ = ["Capabilities", "Channel", "ChannelRegistry", "Outcome", "Result"]


class UnavailableChannel:
    available = False
    capabilities = Capabilities(False, False, False, False, False)

    def __init__(self, name: str) -> None:
        self.name = name

    async def deliver(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SKIPPED, "channel_unavailable")

    async def update(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SKIPPED, "channel_unavailable")

    async def clear(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SKIPPED, "channel_unavailable")


class ChannelRegistry:
    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {n: UnavailableChannel(n) for n in CHANNELS}
        self._channels["banner"] = BannerChannel()

    def register(self, channel: Channel) -> None:
        self._channels[channel.name] = channel

    def get(self, name: str) -> Channel:
        return self._channels[name]
