"""The severity `success` is called `passive` (D-231); `success` is still accepted."""

from typing import Any

from homeassistant.config_entries import ConfigSubentryData
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heads_up.const import DOMAIN, SEVERITIES
from custom_components.heads_up.models import Banner

from ..conftest import CreateBanner, banners


def test_the_four_severities() -> None:
    assert SEVERITIES == ("passive", "info", "warning", "critical")


async def test_a_call_with_success_makes_a_passive_message(
    hass: HomeAssistant, entry: MockConfigEntry, create: CreateBanner
) -> None:
    await create(id="old", message="x", severity="success")
    await create(id="new", message="x", severity="passive")
    assert banners(entry)["old"].severity == "passive"
    assert banners(entry)["new"].severity == "passive"


def test_a_stored_success_message_loads_as_passive() -> None:
    data = {
        "id": "a",
        "message": "x",
        "severity": "success",
        "dismissible": True,
        "dismiss_scope": "user",
        "created_at": "2026-11-19T10:00:00+00:00",
        "updated_at": "2026-11-19T10:00:00+00:00",
    }
    assert Banner.from_dict(data).severity == "passive"


def _sub(kind: str, title: str, data: dict[str, Any]) -> ConfigSubentryData:
    return ConfigSubentryData(data=data, subentry_type=kind, title=title, unique_id=None)


async def test_the_upgrade_renames_success_in_options_policies_and_rules(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        minor_version=3,
        options={
            "push_levels": {"success": "normal", "info": "passive"},
            "popup_styles": {"success": "off"},
            "severity_display": {"success": {"label": "Done"}},
            "speak_severity_volume": {"success": 20},
        },
        subentries_data=[
            _sub("policy", "Quiet", {"type": "quiet_hours", "severities": ["info", "success"]}),
            _sub(
                "rule",
                "Door",
                {"entity_id": "binary_sensor.door", "message": "Open", "severity": "success"},
            ),
        ],
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert (entry.version, entry.minor_version) == (3, 2)
    assert entry.options["push_levels"] == {"passive": "normal", "info": "passive"}
    assert entry.options["popup_styles"] == {"passive": "off"}
    assert entry.options["severity_display"] == {"passive": {"label": "Done"}}
    assert entry.options["speak_severity_volume"] == {"passive": 20}
    data = {s.title: dict(s.data) for s in entry.subentries.values()}
    assert data["Quiet"]["severities"] == ["info", "passive"]
    assert data["Door"]["severity"] == "passive"


async def test_an_upgrade_through_every_step_also_renames_success(hass: HomeAssistant) -> None:
    styles = {"critical": "modal", "info": "card", "success": "card", "warning": "card"}
    entry = MockConfigEntry(
        domain=DOMAIN, version=2, minor_version=2, options={"popup_styles": styles}
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert (entry.version, entry.minor_version) == (3, 2)
    assert entry.options["popup_styles"] == {
        "critical": "modal",
        "info": "card",
        "passive": "card",
        "warning": "card",
    }
    assert "success" not in entry.options["push_levels"]
