"""Test send of the panel: the dry run and the one real send (D-101, D-120).

The input is the input of the `notify` action, checked by the same schema and the same name checks,
so a call that previews well is a call that works.
"""

from __future__ import annotations

import secrets
from typing import Any

import probatio as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from ..const import CHANNEL_BANNER, DEFAULT_SEVERITY, DOMAIN
from ..models import Banner
from ..services import NOTIFY_SCHEMA, _check_names, banner_people
from .engine import HubEngine

TEST_TAG = "test"
TEST_TITLE = "Test"
TEST_ID_PREFIX = "hu_test_"
TEST_TIMEOUT_MINUTES = 10


class TestSendError(Exception):
    """The call is not valid: a code and a text for the panel."""

    __test__ = False  # not a pytest class

    def __init__(self, code: str, text: str) -> None:
        super().__init__(text)
        self.code = code


def check(hub: HubEngine, payload: dict[str, Any]) -> dict[str, Any]:
    """The call as `notify` would validate it, with the names checked."""
    try:
        data = dict(NOTIFY_SCHEMA(payload))
    except vol.Invalid as err:
        raise TestSendError("invalid_format", str(err)) from err
    try:
        _check_names(hub, data.get("to", {}), data.get("policy"))
    except ServiceValidationError as err:
        raise TestSendError(str(err.translation_key), str(err)) from err
    return data


async def build(hub: HubEngine, payload: dict[str, Any]) -> Banner:
    """A message for the dry run: never stored, never delivered."""
    data = check(hub, payload)
    now = dt_util.utcnow()
    severity = data.get("severity", DEFAULT_SEVERITY)
    return Banner(
        id="preview",
        message=data["message"],
        severity=severity,
        people=await banner_people(hub, data.get("to", {}).get(CHANNEL_BANNER, {}), severity),
        dismissible=True,
        dismiss_scope="user",
        created_at=now,
        updated_at=now,
        title=data.get("title"),
        tag=data.get("tag"),
        channels=list(data["channels"]),
        targets={k: dict(v) for k, v in data.get("to", {}).items()},
        policy=data.get("policy"),
        tts_message=data.get("tts_message"),
    )


def marked(payload: dict[str, Any]) -> dict[str, Any]:
    """The same call with the test marker: title prefix, id, tag and a short life (D-120)."""
    title = payload.get("title")
    return {
        **payload,
        "id": f"{TEST_ID_PREFIX}{secrets.token_hex(4)}",
        "title": f"{TEST_TITLE}: {title}" if title else TEST_TITLE,
        "tag": TEST_TAG,
        "timeout": {"minutes": TEST_TIMEOUT_MINUTES},
    }


async def send(hass: HomeAssistant, hub: HubEngine, payload: dict[str, Any]) -> dict[str, Any]:
    """The one real send of the panel: the `notify` action itself."""
    check(hub, payload)
    response = await hass.services.async_call(
        DOMAIN, "notify", marked(payload), blocking=True, return_response=True
    )
    return dict(response or {})
