"""Dev-only stub services for the hub end-to-end checks (work package H0a).

Never shipped with the integration and never loaded outside the dev container. It registers two
recording notify services (like `notify.mobile_app_<device>`), two fake media players (one with the
announce feature) and the service `hub_stub.reset`. Every call is recorded with its data in
`sensor.hub_stub_calls` (state: number of calls, attribute `calls`: the last 50) so `dev/smoke.py`
can check what the hub sent, including tags and buttons.
"""

from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType

DOMAIN = "hub_stub"
SENSOR = "sensor.hub_stub_calls"
NOTIFY_SERVICES = ("mobile_app_stub_phone", "mobile_app_stub_tablet")
MAX_CALLS = 50


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the stub services and platforms."""
    calls: list[dict[str, Any]] = []

    def publish() -> None:
        hass.states.async_set(SENSOR, len(calls), {"calls": calls[-MAX_CALLS:]})

    def record(domain: str, service: str, data: dict[str, Any]) -> None:
        calls.append(
            {
                "domain": domain,
                "service": service,
                "data": data,
                "time": datetime.now(UTC).isoformat(),
            }
        )
        publish()

    hass.data[DOMAIN] = record

    def make_handler(name: str):  # type: ignore[no-untyped-def]
        async def handler(call: ServiceCall) -> None:
            record("notify", name, dict(call.data))

        return handler

    for name in NOTIFY_SERVICES:
        hass.services.async_register("notify", name, make_handler(name))

    async def reset(call: ServiceCall) -> None:
        calls.clear()
        publish()

    hass.services.async_register(DOMAIN, "reset", reset)
    publish()
    hass.async_create_task(async_load_platform(hass, "media_player", DOMAIN, {}, config))
    return True
