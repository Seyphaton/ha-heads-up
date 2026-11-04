"""Push channel: Companion app notifications through the legacy notify services (DESIGN §23.8).

Only `notify.mobile_app_<device>` forwards `data` (tag, actions, clear_notification); the notify
entity does not (N-61). One tag per message, so a device replaces instead of stacking and a clear
reaches every device (N-62). The service is worked out from the registration's current
`device_name` each time (N-78). Presses come back as `mobile_app_notification_action` events whose
button id carries message, recipient and action; nothing else in the event is trusted (N-79).
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceNotFound

from ...const import (
    DEFAULT_OPTIONS,
    OPT_INSTALL_TOKEN,
    OPT_PUSH_CHANNEL_ID,
    OPT_PUSH_LEVELS,
    OPT_PUSH_LOCKSCREEN,
    OPT_PUSH_STICKY,
)
from ...models import Banner
from ..recipients import notify_service, registration_data
from .base import Capabilities, Outcome, Result, Target

if TYPE_CHECKING:
    from ...manager import BannerManager
    from ..engine import HubEngine

_LOGGER = logging.getLogger(__name__)
ACTION_EVENT = "mobile_app_notification_action"
ID_PREFIX = "hu"
OWN_PREFIX = "b-"  # keeps a message's own button keys apart from dismiss, snooze and ack
MAX_BUTTONS = {"android": 3, "ios": 10}  # N-62
WARN_EVERY = 3600  # seconds between log warnings per device
IMPORTANCE = {"passive": "low", "normal": "default", "time-sensitive": "high", "critical": "max"}

# Text the hub itself puts on a notification, in the languages of the integration.
TEXT = {
    "dismiss": {"en": "Dismiss", "de": "Schließen", "fr": "Fermer", "es": "Descartar"},
    "snooze": {"en": "Snooze", "de": "Später", "fr": "Reporter", "es": "Posponer"},
    "ack": {"en": "Acknowledge", "de": "Bestätigen", "fr": "Confirmer", "es": "Confirmar"},
    "tap_to_read": {
        "en": "Open Home Assistant to read this message.",
        "de": "Öffne Home Assistant, um die Nachricht zu lesen.",
        "fr": "Ouvrez Home Assistant pour lire ce message.",
        "es": "Abre Home Assistant para leer este mensaje.",
    },
    "new_message": {
        "en": "New message",
        "de": "Neue Nachricht",
        "fr": "Nouveau message",
        "es": "Nuevo mensaje",
    },
}


def button_id(message_id: str, recipient: str, action: str) -> str:
    return f"{ID_PREFIX}:{message_id}:{recipient}:{action}"


def parse_button_id(value: str) -> tuple[str, str, str] | None:
    """(message, recipient, action) of a hub button id, or None for any other action."""
    parts = value.split(":")
    if len(parts) < 4 or parts[0] != ID_PREFIX:
        return None
    return parts[1], ":".join(parts[2:-1]), parts[-1]


def tag_for(token: str, message_id: str) -> str:
    return f"hu-{token}-{message_id}"


class PushChannel:
    name = "push"
    available = True
    capabilities = Capabilities(title=True, buttons=True, clear=True, replace=True, per_user=True)

    def __init__(self, hass: HomeAssistant, hub: HubEngine, manager: BannerManager) -> None:
        self._hass = hass
        self._hub = hub
        self._manager = manager
        self._warned: dict[str, float] = {}
        self._unsub = hass.bus.async_listen(ACTION_EVENT, self._on_action)

    def stop(self) -> None:
        self._unsub()

    # Settings ---------------------------------------------------------------------------

    def _opt(self, key: str) -> Any:
        return self._manager.options.get(key, DEFAULT_OPTIONS[key])

    def _token(self) -> str:
        return str(self._manager.options.get(OPT_INSTALL_TOKEN) or "local")

    def _text(self, key: str) -> str:
        table = TEXT[key]
        return table.get(self._hass.config.language, table["en"])

    # Payload ----------------------------------------------------------------------------

    def level_for(self, message: Banner, target: Target, ios: bool) -> str:
        if target.quiet:
            return "passive"
        level = str(self._opt(OPT_PUSH_LEVELS).get(message.severity, "normal"))
        if level == "critical" and not ios:
            return "time-sensitive"  # critical is an iOS notion (N-62)
        return level

    def payload(self, message: Banner, target: Target, platform: str) -> tuple[dict[str, Any], str]:
        """The `notify` call data for one device, and a note when something was left out."""
        ios = platform == "ios"
        level = self.level_for(message, target, ios)
        token = self._token()
        data: dict[str, Any] = {
            "tag": tag_for(token, message.id),
            "group": f"hu-{token}",
            "channel": f"{self._opt(OPT_PUSH_CHANNEL_ID)}_{level.replace('-', '_')}",
            "importance": IMPORTANCE[level],
            "push": {"interruption-level": level},
        }
        if level == "critical":
            data["push"]["sound"] = {"name": "default", "critical": 1, "volume": 1.0}
        if self._opt(OPT_PUSH_STICKY):
            data["sticky"] = "true"
        if uri := _click_target(message.tap_action):
            data["clickAction"] = uri
            data["url"] = uri
        actions, note = self._buttons(message, target, platform)
        if actions:
            data["actions"] = actions
        if message.image:
            # Android and iOS both read `image` (Companion docs, N-93). A picture on the lock
            # screen would defeat the lock screen setting, so it is left out unless it is `full`.
            if self._opt(OPT_PUSH_LOCKSCREEN) == "full":
                data["image"] = message.image
            else:
                note = ";".join(n for n in (note, "image_hidden") if n)
        title, body = self._lockscreen(message)
        out: dict[str, Any] = {"message": body, "data": data}
        if title:
            out["title"] = title
        return out, note

    def _lockscreen(self, message: Banner) -> tuple[str | None, str]:
        mode = self._opt(OPT_PUSH_LOCKSCREEN)
        if mode == "generic":
            return "Heads Up", self._text("new_message")
        if mode == "title_only":
            return message.title or "Heads Up", self._text("tap_to_read")
        return message.title, message.message

    def _buttons(
        self, message: Banner, target: Target, platform: str
    ) -> tuple[list[dict[str, str]], str]:
        who = target.person or target.key
        own = [
            {"action": button_id(message.id, who, OWN_PREFIX + b["key"]), "title": b["label"]}
            for b in message.actions
        ]
        extra: list[dict[str, str]] = []
        if target.ack_button:
            extra.append({"action": button_id(message.id, who, "ack"), "title": self._text("ack")})
        if message.snoozable:
            extra.append(
                {"action": button_id(message.id, who, "snooze"), "title": self._text("snooze")}
            )
        if message.dismissible:
            extra.append(
                {"action": button_id(message.id, who, "dismiss"), "title": self._text("dismiss")}
            )
        buttons = own + extra
        limit = MAX_BUTTONS.get(platform, MAX_BUTTONS["android"])
        if len(buttons) > limit:
            return buttons[:limit], f"buttons_clipped:{len(buttons) - limit}"
        return buttons, ""

    # Delivery ---------------------------------------------------------------------------

    async def deliver(self, message: Banner, target: Target) -> Outcome:
        registration = self._registration(target)
        if registration is None:
            return Outcome(Result.FAILED, "device_missing")
        platform = str(registration.get("os_name", "")).lower()
        platform = "ios" if platform == "ios" else "android"
        service = notify_service(str(registration.get("device_name", "")))
        payload, note = self.payload(message, target, platform)
        outcome = await self._call(target, service, payload)
        if outcome.result is Result.SENT:
            return Outcome(Result.SENT, note or None, ref=payload["data"]["tag"])
        return outcome

    async def update(self, message: Banner, target: Target) -> Outcome:
        # iOS critical notifications cannot be replaced: clear first, then send (N-62).
        registration = self._registration(target)
        ios = registration is not None and str(registration.get("os_name", "")).lower() == "ios"
        if ios and self.level_for(message, target, True) == "critical":
            token = self._token()
            await self.clear(message.id, target, tag_for(token, message.id))
        return await self.deliver(message, target)

    async def clear(self, message_id: str, target: Target, ref: str | None) -> Outcome:
        registration = self._registration(target)
        if registration is None:
            return Outcome(Result.FAILED, "device_missing")
        token = self._token()
        service = notify_service(str(registration.get("device_name", "")))
        payload = {
            "message": "clear_notification",
            "data": {"tag": ref or tag_for(token, message_id)},
        }
        return await self._call(target, service, payload)

    def _registration(self, target: Target) -> dict[str, Any] | None:
        device_id = target.key.removeprefix("device:")
        data = registration_data(self._hass, device_id)
        return dict(data) if data is not None else None

    async def _call(self, target: Target, service: str, payload: dict[str, Any]) -> Outcome:
        try:
            await self._hass.services.async_call("notify", service, payload, blocking=True)
        except ServiceNotFound:
            self._warn(target.key, "notify.%s does not exist", service)
            return Outcome(Result.FAILED, "service_not_found")
        except HomeAssistantError as err:
            self._warn(target.key, "Push through notify.%s failed: %s", service, err)
            return Outcome(Result.FAILED, "send_failed")
        return Outcome(Result.SENT)

    def _warn(self, key: str, message: str, *args: object) -> None:
        # One warning per device per hour; the trace keeps every failure.
        now = time.monotonic()
        if now - self._warned.get(key, -WARN_EVERY) >= WARN_EVERY:
            self._warned[key] = now
            _LOGGER.warning(message, *args)

    # Presses ----------------------------------------------------------------------------

    @callback
    def _on_action(self, event: Event[Any]) -> None:
        parsed = parse_button_id(str(event.data.get("action", "")))
        if parsed is None:
            return  # an action of some other automation
        message_id, recipient, action = parsed
        outcome = self._press(message_id, recipient, action, event.context.user_id)
        self._hub.note(message_id, "push", recipient, "press", outcome)

    def _press(self, message_id: str, recipient: str, action: str, event_user: str | None) -> str:
        manager = self._manager
        banner = manager.banners.get(message_id)
        if banner is None:
            return "stale_message"
        if not any(
            r.state.value == "sent" and recipient in (r.person, r.recipient)
            for r in self._hub.ledger.for_message(message_id)
            if r.channel == "push"
        ):
            return "unknown_recipient"
        # The id names the recipient, so the press counts for their user. A user on the event is
        # a cross-check only (N-72, D-110).
        person_user = self._hub.resolver.user_of_person(recipient) if "." in recipient else None
        if person_user and event_user and person_user != event_user:
            return "user_mismatch"
        user_id = person_user or event_user
        if user_id is None:
            return "no_user"
        from ...manager import HeadsUpError

        try:
            if action == "dismiss":
                manager.dismiss(message_id, user_id)
            elif action == "snooze":
                manager.snooze(message_id, user_id, manager.quick_snooze_seconds)
            elif action == "ack":
                manager.acknowledge(message_id, user_id)
            elif action.startswith(OWN_PREFIX):
                manager.press(message_id, user_id, action.removeprefix(OWN_PREFIX))
            else:
                return "unknown_action"
        except HeadsUpError as err:
            return err.code
        return "ok"


def _click_target(tap_action: dict[str, Any] | None) -> str | None:
    """A path or URL the notification opens, from a navigate or url tap action."""
    if not tap_action:
        return None
    if tap_action.get("action") == "navigate":
        return tap_action.get("navigation_path")
    if tap_action.get("action") == "url":
        return tap_action.get("url_path")
    return None
