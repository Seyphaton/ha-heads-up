"""Fixtures for the hub tests; see helpers.py for what each fake stands for."""

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from pytest_homeassistant_custom_component.common import async_mock_service

from .helpers import (
    FakeDevice,
    FakeSpeakers,
    PersistentCapture,
    add_fake_speakers,
    add_mobile_app_device,
    capture_persistent,
)

type AddDevice = Callable[..., Awaitable[FakeDevice]]
type AddNotify = Callable[[str], list[ServiceCall]]


@pytest.fixture
def options() -> dict[str, Any]:  # type: ignore[override]
    """Most hub tests stack several policies on one message, which is the mode "all". The tests
    of the default mode set `policy_mode` themselves."""
    return {"policy_mode": "all"}


@pytest.fixture
def mobile_app_device(hass: HomeAssistant) -> AddDevice:
    """Factory: `await mobile_app_device("Anna's phone", user_id=..., person_entity_id=...)`."""

    async def _add(device_name: str, **kwargs: object) -> FakeDevice:
        return await add_mobile_app_device(hass, device_name, **kwargs)  # type: ignore[arg-type]

    return _add


@pytest.fixture
def fake_notify(hass: HomeAssistant) -> AddNotify:
    """Factory: `fake_notify("mobile_app_other")` registers a recording `notify` service."""

    def _add(service: str) -> list[ServiceCall]:
        return async_mock_service(hass, "notify", service)

    return _add


@pytest.fixture
def fake_speakers(hass: HomeAssistant) -> FakeSpeakers:
    """Fake players, satellite and tts with recorded calls."""
    return add_fake_speakers(hass)


@pytest.fixture
def persistent_capture(hass: HomeAssistant) -> PersistentCapture:
    """Recorded persistent notification calls."""
    return capture_persistent(hass)
