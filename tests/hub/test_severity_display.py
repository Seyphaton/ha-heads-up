"""Severity label, icon and color (D-222, D-223): stored, checked, used by card, popup and mail."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.heads_up.hub.channels.mail import MailChannel

ALARM = {"critical": {"label": "Alarm", "icon": "mdi:alarm-light", "color": "#d00000"}}


async def ask(client: Any, command: str, **data: Any) -> dict[str, Any]:
    await client.send_json_auto_id({"type": f"heads_up/{command}", **data})
    return dict(await client.receive_json())


async def test_the_severities_are_stored_without_empty_values_and_checked(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client(hass)
    shown = {**ALARM, "info": {"label": "", "icon": "", "color": ""}}
    reply = await ask(client, "channels_set", severity_display=shown)
    assert reply["success"], reply
    assert entry.options["severity_display"] == ALARM
    assert (await ask(client, "severity_display"))["result"] == ALARM
    for bad in (
        {"urgent": {"label": "x"}},
        {"critical": {"label": "x" * 31}},
        {"critical": {"icon": "alarm"}},
        {"critical": {"color": "red; background: url(x)"}},
        {"critical": {"size": "big"}},
    ):
        assert not (await ask(client, "channels_set", severity_display=bad))["success"], bad


async def test_the_card_payload_carries_the_label_color_and_icon(
    hass: HomeAssistant, entry: MockConfigEntry, hass_admin_user: Any
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "severity_display": ALARM}
    )
    await hass.async_block_till_done()
    await hass.services.async_call(
        "heads_up",
        "create_banner",
        {"id": "a", "message": "x", "severity": "critical"},
        blocking=True,
    )
    await hass.services.async_call(
        "heads_up",
        "create_banner",
        {"id": "b", "message": "y", "severity": "critical", "icon": "mdi:water"},
        blocking=True,
    )
    await hass.services.async_call(
        "heads_up", "create_banner", {"id": "c", "message": "z", "severity": "info"}, blocking=True
    )
    shown = {b["id"]: b for b in entry.runtime_data.visible(hass_admin_user.id)}
    assert shown["a"]["severity_label"] == "Alarm" and shown["a"]["severity_color"] == "#d00000"
    assert shown["a"]["icon"] == "mdi:alarm-light"
    assert shown["b"]["icon"] == "mdi:water"  # the message's own icon wins
    assert "severity_label" not in shown["c"] and shown["c"]["icon"] == "mdi:information"


async def test_the_mail_placeholder_uses_the_label(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "severity_display": ALARM}
    )
    await hass.async_block_till_done()
    await hass.services.async_call(
        "heads_up",
        "create_banner",
        {"id": "a", "message": "x", "severity": "critical"},
        blocking=True,
    )
    mail = entry.runtime_data.hub.channels.get("mail")
    assert isinstance(mail, MailChannel)
    assert mail.values(entry.runtime_data.banners["a"], None)["severity"] == "Alarm"
