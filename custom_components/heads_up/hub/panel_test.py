"""Test send of the panel: the dry run and the one real send (D-101, D-120).

The input is the input of the `notify` action, checked by the same schema and the same name checks,
so a call that previews well is a call that works.
"""

from __future__ import annotations

import secrets
from typing import Any

import probatio as vol
import yaml  # type: ignore[import-untyped]  # PyYAML ships with Home Assistant, no stubs here
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError, TemplateError
from homeassistant.helpers.template import Template
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
        to, policy = _check_names(hub, data.get("to", {}), data.get("policy"))
    except ServiceValidationError as err:
        raise TestSendError(str(err.translation_key), str(err)) from err
    # The stored spelling, as the action uses it: a pasted call may name an audience by its sensor.
    if to:
        data["to"] = to
    if policy is not None:
        data["policy"] = policy
    return data


async def build(hub: HubEngine, payload: dict[str, Any]) -> Banner:
    """A message for the dry run: never stored, never delivered."""
    return await banner_from(hub, check(hub, payload))


async def banner_from(hub: HubEngine, data: dict[str, Any]) -> Banner:
    """The dry-run message of a call that the schema and the name checks already accepted."""
    now = dt_util.utcnow()
    severity = data.get("severity", DEFAULT_SEVERITY)
    return Banner(
        id="preview",
        message=data["message"],
        severity=severity,
        people=await banner_people(hub, data.get("to", {}).get(CHANNEL_BANNER, {}), severity),
        dismissible=data.get("dismissible", True),
        dismiss_scope=data.get("dismiss_scope", "user"),
        snoozable=data.get("snoozable", False),
        snooze_scope=data.get("snooze_scope", "user"),
        created_at=now,
        updated_at=now,
        title=data.get("title"),
        tag=data.get("tag"),
        channels=list(data["channels"]),
        targets={k: dict(v) for k, v in data.get("to", {}).items()},
        policy=data.get("policy"),
        tts_message=data.get("tts_message"),
        mail_subject=data.get("mail_subject"),
        mail_body=data.get("mail_body"),
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


def _render(hass: HomeAssistant, value: Any, variables: dict[str, Any]) -> Any:
    """Render every string that holds a template, anywhere in the value."""
    if isinstance(value, str):
        if "{{" not in value and "{%" not in value:
            return value
        try:
            return Template(value, hass).async_render(variables)
        except TemplateError as err:
            raise TestSendError("template_error", str(err)) from err
    if isinstance(value, list):
        return [_render(hass, v, variables) for v in value]
    if isinstance(value, dict):
        return {k: _render(hass, v, variables) for k, v in value.items()}
    return value


def _load(text: str, code: str) -> Any:
    try:
        # safe_load: no tags, so a pasted call cannot include a file or run anything.
        return yaml.safe_load(text)
    except yaml.YAMLError as err:
        raise TestSendError(code, str(err)) from err


def render_call(hass: HomeAssistant, text: str, variables: str = "") -> dict[str, Any]:
    """The `notify` input of a pasted call. It may be the data alone or a whole action step
    (`action: heads_up.notify` with `data`). Templates are rendered with the given variables,
    for example a sample `trigger`, as Home Assistant would render them before the call."""
    call = _load(text, "yaml_invalid")
    if isinstance(call, list) and len(call) == 1:
        call = call[0]
    if not isinstance(call, dict):
        raise TestSendError("call_not_found", "The text is not a call")
    if "action" in call or "service" in call:
        if call.get("action", call.get("service")) != f"{DOMAIN}.notify":
            raise TestSendError("not_notify", "Only heads_up.notify can be tested")
        call = call.get("data") or {}
    scope = _load(variables, "variables_invalid") if variables.strip() else {}
    if not isinstance(scope, dict):
        raise TestSendError("variables_invalid", "The sample values are not a mapping")
    payload = _render(hass, call, scope)
    if not isinstance(payload, dict):
        raise TestSendError("call_not_found", "The text is not a call")
    payload.pop("dry_run", None)  # the test decides whether it sends
    return payload
