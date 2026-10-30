"""Interfaces H2 (audiences, recipients) and H4 (policies) implement, with null defaults.

H1 ships the defaults so the engine and `notify` validation work today: no audience or policy
exists yet, and recipients are the Home Assistant entities a channel can address.
"""

from __future__ import annotations

from typing import Protocol

from homeassistant.core import HomeAssistant

from ..const import CHANNEL_BANNER


class AudienceResolver(Protocol):
    def names(self) -> list[str]: ...


class RecipientResolver(Protocol):
    def known(self, channel: str) -> list[str]: ...


class PolicyCatalog(Protocol):
    def names(self) -> list[str]: ...


class NoAudiences:
    def names(self) -> list[str]:
        return []


class NoPolicies:
    def names(self) -> list[str]:
        return []


class EntityRecipients:
    """Persons for banner, push and popup; speakers and satellites for speak."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def known(self, channel: str) -> list[str]:
        domains = ("media_player", "assist_satellite") if channel == "speak" else ("person",)
        if channel == CHANNEL_BANNER:
            domains = ("person",)
        return sorted(s.entity_id for d in domains for s in self._hass.states.async_all(d))
