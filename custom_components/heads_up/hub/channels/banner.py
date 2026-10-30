"""Banner channel: the dashboard card reads the manager itself, so delivery is bookkeeping."""

from __future__ import annotations

from ...models import Banner
from .base import Capabilities, Outcome, Result


class BannerChannel:
    name = "banner"
    available = True
    capabilities = Capabilities(title=True, buttons=True, clear=True, replace=True, per_user=True)

    async def deliver(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SENT)

    async def update(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SENT)

    async def clear(self, message: Banner, recipient: str) -> Outcome:
        return Outcome(Result.SENT)
