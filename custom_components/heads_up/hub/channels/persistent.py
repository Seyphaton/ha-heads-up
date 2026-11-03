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
from homeassistant.helpers import area_registry as ar
from homeassistant.util import slugify

from ...models import Banner
from ..recipients import find_area
from .base import Capabilities, Outcome, Result, Target

_LOGGER = logging.getLogger(__name__)
DOMAIN = "persistent_notification"
WARN_EVERY = 3600  # seconds between log warnings


def notification_id(message_id: str) -> str:
    return f"hu_{message_id}"


# Text of the bell entry that reports speech with nobody to say it (D-126). The entry carries
# the area, group or speaker, never the message, because every user sees the bell.
WARNING_TEXT = {
    "no_speaker": {
        "en": (
            "Heads Up: no speaker",
            "Speech was requested for {who}, but it has no speaker. Check which area your media "
            "players and Assist satellites are in.",
        ),
        "de": (
            "Heads Up: kein Lautsprecher",
            "Für {who} wurde eine Sprachausgabe angefordert, aber dort gibt es keinen "
            "Lautsprecher. Prüfe, in welchem Bereich deine Mediaplayer und Assist-Satelliten sind.",
        ),
        "fr": (
            "Heads Up : aucun haut-parleur",
            "Une annonce vocale a été demandée pour {who}, mais il n'y a aucun haut-parleur. "
            "Vérifiez la pièce de vos lecteurs multimédia et satellites Assist.",
        ),
        "es": (
            "Heads Up: sin altavoz",
            "Se pidió una locución para {who}, pero no tiene altavoz. Revisa en qué área están "
            "tus reproductores y satélites de Assist.",
        ),
    },
    "entity_missing": {
        "en": (
            "Heads Up: speaker not found",
            "Speech was requested on {who}, but that speaker does not exist.",
        ),
        "de": (
            "Heads Up: Lautsprecher nicht gefunden",
            "Auf {who} wurde eine Sprachausgabe angefordert, aber dieser Lautsprecher existiert "
            "nicht.",
        ),
        "fr": (
            "Heads Up : haut-parleur introuvable",
            "Une annonce vocale a été demandée sur {who}, mais ce haut-parleur n'existe pas.",
        ),
        "es": (
            "Heads Up: altavoz no encontrado",
            "Se pidió una locución en {who}, pero ese altavoz no existe.",
        ),
    },
}


async def warn_speech(hass: HomeAssistant, who: str, reason: str) -> None:
    """One bell entry per area, group or speaker; a repeat replaces it (same id)."""
    kind = "entity_missing" if reason == "entity_missing" else "no_speaker"
    table = WARNING_TEXT[kind]
    title, text = table.get(hass.config.language, table["en"])
    area = find_area(hass, who)
    name = ar.async_get(hass).async_get_area(area).name if area else who  # type: ignore[union-attr]
    data = {
        "notification_id": f"heads_up_warning_{slugify(who)}",
        "title": title,
        "message": text.format(who=name),
    }
    try:
        await hass.services.async_call(DOMAIN, "create", data, blocking=True)
    except HomeAssistantError as err:  # ServiceNotFound is one; a warning must never break delivery
        _LOGGER.debug("Could not report a missing speaker: %s", err)


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
