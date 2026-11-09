"""Mail channel: one call of a notify service per recipient (DESIGN §23.8, D-129).

The service is chosen on the Channels page (any notify service that takes `title`, `message` and
`target`, such as the SMTP one, N-94). A person's address is a field of their profile; a shared
"Global address" can be named as a recipient but is never a stand-in for a person without one.
Subject and body come from two templates with `{placeholders}`. A mail cannot be taken back, so
this channel has no clear, and an update does not send again.
"""

from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceNotFound

from ...const import (
    DEFAULT_OPTIONS,
    MAIL_GLOBAL_KEY,
    MAIL_PLACEHOLDERS,
    MAX_MAIL_BODY,
    MAX_MAIL_SUBJECT,
    OPT_MAIL_ADDRESS,
    OPT_MAIL_BODY,
    OPT_MAIL_SERVICE,
    OPT_MAIL_SUBJECT,
)
from ...models import Banner
from .base import Capabilities, Outcome, Result, Target

if TYPE_CHECKING:
    from ...manager import BannerManager
    from ..engine import HubEngine

_LOGGER = logging.getLogger(__name__)
WARN_EVERY = 3600  # seconds between log warnings per recipient
_PLACEHOLDER = re.compile(r"\{(\w*)\}")

# The severity as a word, in the languages of the integration.
SEVERITY_WORDS = {
    "en": {"success": "Success", "info": "Info", "warning": "Warning", "critical": "Critical"},
    "de": {"success": "Erfolg", "info": "Info", "warning": "Warnung", "critical": "Kritisch"},
    "fr": {"success": "Succès", "info": "Info", "warning": "Avertissement", "critical": "Critique"},
    "es": {"success": "Éxito", "info": "Info", "warning": "Aviso", "critical": "Crítico"},
}


def check_template(template: str, limit: int) -> str | None:
    """An error code for a template, or None. Only the known placeholders are allowed."""
    if not template.strip():
        return "mail_template_empty"
    if len(template) > limit:
        return "mail_template_too_long"
    if any(name not in MAIL_PLACEHOLDERS for name in _PLACEHOLDER.findall(template)):
        return "mail_template_placeholder"
    return None


def check_subject(template: str) -> str | None:
    return check_template(template, MAX_MAIL_SUBJECT)


def check_body(template: str) -> str | None:
    return check_template(template, MAX_MAIL_BODY)


def render(template: str, values: dict[str, str]) -> str:
    """Fill the placeholders; a name that is not known is left as written."""
    return _PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), template)


class MailChannel:
    name = "mail"
    available = True
    capabilities = Capabilities(
        title=True, buttons=False, clear=False, replace=False, per_user=True
    )

    def __init__(self, hass: HomeAssistant, hub: HubEngine, manager: BannerManager) -> None:
        self._hass = hass
        self._hub = hub
        self._manager = manager
        self._warned: dict[str, float] = {}

    def _opt(self, key: str) -> Any:
        return self._manager.options.get(key, DEFAULT_OPTIONS[key])

    def values(self, message: Banner, person: str | None) -> dict[str, str]:
        words = SEVERITY_WORDS.get(self._hass.config.language, SEVERITY_WORDS["en"])
        name = ""
        if person and (state := self._hass.states.get(person)):
            name = str(state.attributes.get("friendly_name") or person)
        return {
            "severity": words.get(message.severity, message.severity),
            "title": message.title or message.message,
            "message": message.message,
            "person": name,
            # The object id of the person entity (`philip` for `person.philip`): stable and
            # lower case, whatever the friendly name says.
            "person_id": person.split(".", 1)[1] if person and "." in person else "",
            "id": message.id,
            "tag": message.tag or "",
        }

    def address_of(self, target: Target) -> str:
        if target.key == MAIL_GLOBAL_KEY:
            return str(self._opt(OPT_MAIL_ADDRESS))
        return self._hub.resolver.profile(target.key).mail_address

    def check(self, target: Target) -> tuple[str, str | None]:
        """The address a mail to this target would go to and why it would fail, for the preview
        (D-178); `deliver` stops at the same two reasons."""
        address = self.address_of(target)
        if not str(self._opt(OPT_MAIL_SERVICE)):
            return address, "no_mail_service"
        return address, (None if address else "no_mail_address")

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        service = str(self._opt(OPT_MAIL_SERVICE))
        if not service:
            return Outcome(Result.FAILED, "no_mail_service")
        address = self.address_of(target)
        if not address:
            self.warn_missing(target.key)
            return Outcome(Result.FAILED, "no_mail_address")
        values = self.values(
            message, target.person or (None if target.key == MAIL_GLOBAL_KEY else target.key)
        )
        data = {
            "title": render(message.mail_subject or str(self._opt(OPT_MAIL_SUBJECT)), values),
            "message": render(message.mail_body or str(self._opt(OPT_MAIL_BODY)), values),
            "target": [address],
        }
        try:
            await self._hass.services.async_call("notify", service, data, blocking=True)
        except ServiceNotFound:
            self._warn(target.key, "notify.%s does not exist", service)
            return Outcome(Result.FAILED, "service_not_found")
        except HomeAssistantError as err:
            self._warn(target.key, "Mail through notify.%s failed: %s", service, err)
            return Outcome(Result.FAILED, "send_failed")
        return Outcome(Result.SENT)

    async def update(self, message: Banner, target: Target) -> Outcome:
        # A mail cannot be replaced; an update does not send it again.
        row = self._hub.ledger.rows.get((message.id, self.name, target.key))
        if row is not None and row.state.value == "sent":
            return Outcome(Result.SKIPPED, "already_sent")
        return await self.deliver(message, target)

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        return Outcome(Result.SKIPPED, "not_clearable")

    def warn_missing(self, recipient: str) -> None:
        self._warn(recipient, "No mail address for %s", recipient)

    def _warn(self, key: str, message: str, *args: object) -> None:
        now = time.monotonic()
        if now - self._warned.get(key, -WARN_EVERY) >= WARN_EVERY:
            self._warned[key] = now
            _LOGGER.warning(message, *args)
