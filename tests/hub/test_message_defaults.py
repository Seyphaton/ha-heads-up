"""The banner settings are message settings: they apply to a message on any channel (D-141)."""

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN

from ..conftest import banners


async def notify(hass: HomeAssistant, **data: Any) -> dict[str, Any]:
    response = await hass.services.async_call(
        DOMAIN, "notify", data, blocking=True, return_response=True
    )
    assert response is not None
    return dict(response)


async def set_options(hass: HomeAssistant, entry: MockConfigEntry, **options: Any) -> None:
    hass.config_entries.async_update_entry(entry, options={**entry.options, **options})
    await hass.async_block_till_done()


async def test_the_defaults_apply_to_a_message_without_the_banner_channel(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_options(
        hass,
        entry,
        default_dismiss_scope="global",
        default_snoozable=True,
        default_snooze_scope="global",
        default_snooze_options=[300, 900],
        default_timeout=7200,
    )
    await notify(hass, id="a", message="Door", channels=["persistent"], severity="info")
    message = banners(entry)["a"]
    assert message.channels == ["persistent"]
    assert message.dismiss_scope == "global"
    assert message.snoozable is True and message.snooze_scope == "global"
    assert message.snooze_options == [300, 900]
    assert message.expires_at is not None
    assert (message.expires_at - message.created_at).total_seconds() == 7200


async def test_messages_without_the_banner_channel_count_toward_the_maximum(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    await set_options(hass, entry, max_banners=1)
    await notify(hass, id="a", message="First", channels=["persistent"], severity="info")
    await notify(hass, id="b", message="Second", channels=["persistent"], severity="info")
    assert set(banners(entry)) == {"b"}
