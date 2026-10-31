"""Persistent notification channel: the notification bell of Home Assistant (DESIGN §23.8).

One entry per message, with the id `hu_<message id>`. A notification of the bell is visible to
every user, so this channel has no recipients and takes no target (D-082, N-67). A dismissal in
the bell is not reported back to Heads Up; a later update creates the entry again.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceNotFound

from ...models import Banner
from .base import Capabilities, Outcome, Result, Target

_LOGGER = logging.getLogger(__name__)
DOMAIN = "persistent_notification"
WARN_EVERY = 3600  # seconds between log warnings


def notification_id(message_id: str) -> str:
    return f"hu_{message_id}"


class PersistentChannel:
    name = "persistent"
    available = True
    capabilities = Capabilities(title=True, buttons=False, clear=True, replace=True, per_user=False)

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._warned: float = -WARN_EVERY

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        data: dict[str, Any] = {
            "notification_id": notification_id(message.id),
            "message": message.message,
        }
        if message.title:
            data["title"] = message.title
        outcome = await self._call("create", data)
        if outcome.result is Result.SENT:
            return Outcome(Result.SENT, ref=data["notification_id"])
        return outcome

    async def update(self, message: Banner, target: Target) -> Outcome:
        return await self.deliver(message, target)  # the same id replaces the entry

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        return await self._call("dismiss", {"notification_id": ref or notification_id(message_id)})

    async def _call(self, service: str, data: dict[str, Any]) -> Outcome:
        try:
            await self._hass.services.async_call(DOMAIN, service, data, blocking=True)
        except ServiceNotFound:
            self._warn("%s.%s does not exist", DOMAIN, service)
            return Outcome(Result.FAILED, "service_not_found")
        except HomeAssistantError as err:
            self._warn("%s.%s failed: %s", DOMAIN, service, err)
            return Outcome(Result.FAILED, "send_failed")
        return Outcome(Result.SENT)

    def _warn(self, message: str, *args: object) -> None:
        now = time.monotonic()
        if now - self._warned >= WARN_EVERY:
            self._warned = now
            _LOGGER.warning(message, *args)
