"""Serving the card module (N-8, N-9, D-021)."""

import hashlib
from pathlib import Path

import pytest
from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.heads_up import frontend
from custom_components.heads_up.const import DOMAIN
from custom_components.heads_up.frontend import CARD_FILE


async def _card_url(hass: HomeAssistant) -> str:
    # Version plus the first 8 hex characters of the file's SHA-256, so a changed file always
    # gets a new URL even when the version is not bumped (N-52).
    integration = await async_get_integration(hass, DOMAIN)
    digest = hashlib.sha256(CARD_FILE.read_bytes()).hexdigest()[:8]
    return f"/heads_up/heads-up-card.js?v={integration.version}-{digest}"


async def test_module_registered_with_version_query(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    assert await _card_url(hass) in hass.data[DATA_EXTRA_MODULE_URL].urls


async def test_module_removed_on_unload_and_readded_on_reload(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    url = await _card_url(hass)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert url not in hass.data[DATA_EXTRA_MODULE_URL].urls

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert url in hass.data[DATA_EXTRA_MODULE_URL].urls


async def test_module_is_served(
    hass: HomeAssistant, entry: MockConfigEntry, hass_client: ClientSessionGenerator
) -> None:
    client = await hass_client()
    response = await client.get("/heads_up/heads-up-card.js")
    assert response.status == 200
    body = await response.text()
    assert 'customElements.define("heads-up-card"' in body


async def test_unload_removes_the_url_that_was_added_even_if_the_file_changed(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert await _card_url(hass) in hass.data[DATA_EXTRA_MODULE_URL].urls

    changed = tmp_path / "heads-up-card.js"
    changed.write_bytes(CARD_FILE.read_bytes() + b"\n// changed while loaded\n")
    monkeypatch.setattr(frontend, "CARD_FILE", changed)
    assert await hass.config_entries.async_unload(entry.entry_id)

    assert not any(u.startswith("/heads_up/") for u in hass.data[DATA_EXTRA_MODULE_URL].urls)


async def test_url_changes_when_the_file_changes(
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    before = await frontend.async_card_url(hass)
    changed = tmp_path / "heads-up-card.js"
    changed.write_bytes(CARD_FILE.read_bytes() + b"\n// changed\n")
    monkeypatch.setattr(frontend, "CARD_FILE", changed)
    assert await frontend.async_card_url(hass) != before


def test_translations_have_no_unresolved_key_references() -> None:
    # `[%key:...%]` is resolved only for core integrations; a custom one shows it as text.
    path = Path(__file__).parents[1] / "custom_components" / "heads_up" / "translations" / "en.json"
    assert "[%key" not in path.read_text()
