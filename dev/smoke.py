"""Smoke test against the local dev HA (http://127.0.0.1:8124). Dev instance only (D-003).

Run after `make dev-up` + `make dev-onboard`:
  uv run python dev/smoke.py create   # creates banners, checks sensor, per-user dismiss
  (restart the container)
  uv run python dev/smoke.py verify   # checks the banners survived the restart, then clears
  uv run python dev/smoke.py rules    # watch rule added through the subentry flow
  (restart the container)
  uv run python dev/smoke.py rules_verify
  uv run python dev/smoke.py stub     # the dev-only stub services record calls (hub work, H0a)
  uv run python dev/smoke.py hub_core # notify, shortcuts, trace (hub work, H1)
  (restart the container)
  uv run python dev/smoke.py hub_core_verify
  uv run python dev/smoke.py policies # policy form, `policy` field, acknowledge (hub work, H4a)
  uv run python dev/smoke.py policies_verify
  uv run python dev/smoke.py editors  # the panel's way: flows over REST, reconfigure, delete (H9c)
  uv run python dev/smoke.py hub_e2e  # bell, duplicates, acknowledge, panel data (H10)
  (restart the container)
  uv run python dev/smoke.py hub_e2e_verify
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

import aiohttp

BASE = "http://127.0.0.1:8124"
CLIENT_ID = f"{BASE}/"
CREDS = dict(
    line.split("=", 1)
    for line in (Path(__file__).parent / "dev-credentials.env").read_text().split()
)


async def token(s: aiohttp.ClientSession, user: str) -> str:
    r = await s.post(
        f"{BASE}/auth/login_flow",
        json={
            "client_id": CLIENT_ID,
            "handler": ["homeassistant", None],
            "redirect_uri": CLIENT_ID,
        },
    )
    flow = await r.json()
    r = await s.post(
        f"{BASE}/auth/login_flow/{flow['flow_id']}",
        json={
            "client_id": CLIENT_ID,
            "username": CREDS[f"DEV_{user}_USER"],
            "password": CREDS[f"DEV_{user}_PASSWORD"],
        },
    )
    code = (await r.json())["result"]
    r = await s.post(
        f"{BASE}/auth/token",
        data={"grant_type": "authorization_code", "code": code, "client_id": CLIENT_ID},
    )
    return str((await r.json())["access_token"])


class WS:
    def __init__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self.ws, self.n = ws, 0

    async def send(self, payload: dict[str, Any]) -> int:
        self.n += 1
        await self.ws.send_json({"id": self.n, **payload})
        return self.n

    async def recv(self, msg_id: int) -> dict[str, Any]:
        while True:
            m: dict[str, Any] = await self.ws.receive_json(timeout=5)
            if m.get("id") == msg_id:
                return m


async def connect(s: aiohttp.ClientSession, access_token: str) -> WS:
    ws = await s.ws_connect(f"{BASE}/api/websocket")
    await ws.receive_json()
    await ws.send_json({"type": "auth", "access_token": access_token})
    assert (await ws.receive_json())["type"] == "auth_ok"
    return WS(ws)


async def call(s: aiohttp.ClientSession, tok: str, service: str, data: dict[str, Any]) -> Any:
    r = await s.post(
        f"{BASE}/api/services/heads_up/{service}?return_response",
        json=data,
        headers={"Authorization": f"Bearer {tok}"},
    )
    body = await r.json()
    assert r.status == 200, body
    return body["service_response"]


async def call_service(
    s: aiohttp.ClientSession, tok: str, domain: str, service: str, data: dict[str, Any]
) -> None:
    r = await s.post(
        f"{BASE}/api/services/{domain}/{service}",
        json=data,
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status == 200, await r.text()


async def stub_calls(s: aiohttp.ClientSession, tok: str) -> list[dict[str, Any]]:
    """Calls recorded by the dev-only stub component (dev/stub_components/hub_stub)."""
    r = await s.get(
        f"{BASE}/api/states/sensor.hub_stub_calls", headers={"Authorization": f"Bearer {tok}"}
    )
    assert r.status == 200, "the hub_stub component is not loaded (restart the dev container)"
    return list((await r.json())["attributes"]["calls"])


async def sensor(s: aiohttp.ClientSession, tok: str) -> str:
    r = await s.get(
        f"{BASE}/api/states/sensor.heads_up_active_banners",
        headers={"Authorization": f"Bearer {tok}"},
    )
    return str((await r.json())["state"])


async def subscribe(ws: WS) -> list[dict[str, Any]]:
    msg_id = await ws.send({"type": "heads_up/subscribe"})
    assert (await ws.recv(msg_id))["success"]
    return list((await ws.recv(msg_id))["event"]["banners"])


async def create() -> None:
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        print(
            "create:",
            await call(
                s,
                admin,
                "create_banner",
                {"id": "smoke_warn", "message": "Smoke warning", "timeout": 0},
            ),
        )
        print(
            "create:",
            await call(
                s,
                user,
                "create_banner",
                {
                    "id": "smoke_crit",
                    "message": "Smoke critical",
                    "severity": "critical",
                    "timeout": 3600,
                },
            ),
        )
        print("generated:", await call(s, admin, "create_banner", {"message": "No id"}))
        print("sensor:", await sensor(s, admin))

        ws_admin, ws_user = await connect(s, admin), await connect(s, user)
        msg_id = await ws_admin.send({"type": "heads_up/dismiss", "banner_id": "smoke_warn"})
        print("admin dismiss:", (await ws_admin.recv(msg_id))["success"])
        print("admin sees:", sorted(b["id"] for b in await subscribe(ws_admin)))
        print("user sees:", sorted(b["id"] for b in await subscribe(ws_user)))
        msg_id = await ws_user.send({"type": "heads_up/admin_clear", "banner_id": "smoke_crit"})
        print("user admin_clear:", (await ws_user.recv(msg_id))["error"]["code"])


async def verify() -> None:
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        print("sensor after restart:", await sensor(s, admin))
        print("admin sees:", sorted(b["id"] for b in await subscribe(await connect(s, admin))))
        print("user sees:", sorted(b["id"] for b in await subscribe(await connect(s, user))))
        print("clear_all:", await call(s, admin, "clear_all", {}))
        print("sensor:", await sensor(s, admin))


async def toggle(s: aiohttp.ClientSession, tok: str, on: bool) -> None:
    r = await s.post(
        f"{BASE}/api/services/input_boolean/{'turn_on' if on else 'turn_off'}",
        json={"entity_id": "input_boolean.test_window"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status == 200
    await asyncio.sleep(0.5)


async def conditions() -> None:
    """Condition + people targeting against real entities (person.dev_user from dev-onboard)."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        await toggle(s, admin, False)
        data = {
            "id": "smoke_cond",
            "message": "Window open",
            "condition": {"entity_id": "input_boolean.test_window"},
            "people": ["person.dev_user"],
        }
        print("create while off:", (await call(s, admin, "create_banner", data))["status"])
        print("sensor:", await sensor(s, admin))
        await toggle(s, admin, True)
        print("on -> sensor:", await sensor(s, admin))
        print("admin sees:", [b["id"] for b in await subscribe(await connect(s, admin))])
        print("user sees:", [b["id"] for b in await subscribe(await connect(s, user))])
        await toggle(s, admin, False)
        print("off -> sensor:", await sensor(s, admin))
        print("user sees:", [b["id"] for b in await subscribe(await connect(s, user))])


async def for_template() -> None:
    """Condition `for` and a template condition on the real test_window (D-066, D-067)."""
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        await toggle(s, admin, False)
        entity = "input_boolean.test_window"
        waits = {"id": "smoke_for", "message": "Open", "condition": {"entity_id": entity, "for": 4}}
        templ = {
            "id": "smoke_tpl",
            "message": "Template",
            "mode": "recurring",
            "condition": {"template": "{{ is_state('" + entity + "', 'on') }}"},
        }
        print("create for:", (await call(s, admin, "create_banner", waits))["status"])
        print("create template:", (await call(s, admin, "create_banner", templ))["status"])
        await toggle(s, admin, True)
        seen = [b["id"] for b in await subscribe(await connect(s, admin))]
        assert seen == ["smoke_tpl"], seen
        print("on, right away:", seen)
        await asyncio.sleep(5)
        seen = sorted(b["id"] for b in await subscribe(await connect(s, admin)))
        assert seen == ["smoke_for", "smoke_tpl"], seen
        print("after 5 s:", seen)
        await toggle(s, admin, False)
        seen = [b["id"] for b in await subscribe(await connect(s, admin))]
        assert seen == [], seen
        print("off:", seen)
        for banner_id in ("smoke_for", "smoke_tpl"):
            await call(s, admin, "clear_banner", {"id": banner_id})


async def empty_operators() -> None:
    """`not_empty` in an action and in a rule made through the real form without a State (D-068)."""
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        headers = {"Authorization": f"Bearer {admin}"}
        entity = "sensor.smoke_note"

        async def put(state: str) -> None:
            r = await s.post(f"{BASE}/api/states/{entity}", json={"state": state}, headers=headers)
            assert r.status in (200, 201)
            await asyncio.sleep(0.5)

        async def seen() -> list[str]:
            return sorted(b["id"] for b in await subscribe(await connect(s, admin)))

        await put("")
        data = {
            "id": "smoke_note",
            "message": "Note",
            "mode": "recurring",
            "condition": {"entity_id": entity, "operator": "not_empty"},
        }
        print("create:", (await call(s, admin, "create_banner", data))["status"])
        eid = await entry_id(s, admin)
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow",
            json={"handler": [eid, "rule"], "show_advanced_options": False},
            headers=headers,
        )
        flow = await r.json()
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow/{flow['flow_id']}",
            json={
                "name": "Smoke note rule",
                "entity_id": entity,
                "operator": "not_empty",
                "message": "{name} has text",
            },
            headers=headers,
        )
        print("rule flow:", (await r.json())["type"])
        assert await seen() == [], await seen()
        await put("hello")
        shown = await seen()
        assert "smoke_note" in shown and len(shown) == 2, shown
        print("with text:", shown)
        await put("")
        assert await seen() == [], await seen()
        print("empty again: []")
        await call(s, admin, "clear_banner", {"id": "smoke_note"})
        ws = await connect(s, admin)
        msg_id = await ws.send({"type": "config_entries/subentries/list", "entry_id": eid})
        for sub in (await ws.recv(msg_id))["result"]:
            if sub["title"] == "Smoke note rule":
                msg_id = await ws.send(
                    {
                        "type": "config_entries/subentries/delete",
                        "entry_id": eid,
                        "subentry_id": sub["subentry_id"],
                    }
                )
                await ws.recv(msg_id)
        await s.delete(f"{BASE}/api/states/{entity}", headers=headers)


async def ids(ws: WS) -> list[str]:
    return [b["id"] for b in await subscribe(ws) if b["id"] == "smoke_snooze"]


async def snooze() -> None:
    """Dismiss button and a per-user snooze that survives the restart (D-069, D-070)."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        data = {
            "id": "smoke_snooze",
            "message": "Snooze me",
            "timeout": 0,
            "snoozable": True,
            "actions": [{"key": "ack", "label": "Got it", "dismiss": True}],
        }
        print("create:", (await call(s, admin, "create_banner", data))["status"])
        ws_user = await connect(s, user)
        first = [b for b in await subscribe(ws_user) if b["id"] == "smoke_snooze"]
        assert first[0]["snoozable"] is True and first[0]["actions"][0]["key"] == "ack", first
        msg_id = await ws_user.send(
            {"type": "heads_up/snooze", "banner_id": "smoke_snooze", "seconds": 3600}
        )
        assert (await ws_user.recv(msg_id))["success"]
        assert await ids(await connect(s, user)) == []
        assert await ids(await connect(s, admin)) == ["smoke_snooze"]
        print("snoozed for dev-user only")
        ws_admin = await connect(s, admin)
        msg_id = await ws_admin.send(
            {"type": "heads_up/action", "banner_id": "smoke_snooze", "key": "ack"}
        )
        assert (await ws_admin.recv(msg_id))["success"]
        assert await ids(await connect(s, admin)) == []
        print("dismiss button hid it for the admin")


async def snooze_verify() -> None:
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        assert await ids(await connect(s, user)) == []
        assert await ids(await connect(s, admin)) == []
        await call(s, admin, "clear_banner", {"id": "smoke_snooze"})
        print("snooze and dismissal survived the restart")


async def hub_core() -> None:
    """notify with the banner channel and a skipped push; the message survives a restart (H1)."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        data = {
            "id": "smoke_hub",
            "message": "Hub core",
            "timeout": 0,
            "channels": ["banner", "push"],
            "to": {"push": {"recipients": ["person.dev_admin"]}},
        }
        try:
            result = await call(s, admin, "notify", data)
        except AssertionError as err:  # the dev instance may have no person of that name
            print("notify refused:", err)
            data["channels"], data["to"] = ["banner"], {}
            result = await call(s, admin, "notify", data)
        print("notify:", result)
        assert result["channels"]["banner"]["sent"] == 1, result
        assert "smoke_hub" in [b["id"] for b in await subscribe(await connect(s, user))]
        ws_user = await connect(s, user)
        msg_id = await ws_user.send({"type": "heads_up/hub_trace"})
        assert (await ws_user.recv(msg_id))["error"]["code"] == "unauthorized"
        ws_admin = await connect(s, admin)
        msg_id = await ws_admin.send({"type": "heads_up/hub_trace", "message_id": "smoke_hub"})
        trace = (await ws_admin.recv(msg_id))["result"]["entries"]
        assert trace and trace[-1]["channel"] == "banner", trace
        print("trace:", trace)
        sent = await call(s, admin, "push", {"message": "once", "recipients": ["person.dev_admin"]})
        print("push shortcut:", sent)
        audience = await call(s, admin, "popup", {"message": "once", "audience": "Everyone"})
        print("popup to Everyone:", audience)
        msg_id = await ws_admin.send(
            {"type": "heads_up/hub_preview_audience", "audience": "Everyone"}
        )
        preview = (await ws_admin.recv(msg_id))["result"]
        print("Everyone now:", preview)
        assert "members" in preview and "skipped" in preview, preview
        msg_id = await ws_user.send(
            {"type": "heads_up/hub_preview_audience", "audience": "Everyone"}
        )
        assert (await ws_user.recv(msg_id))["error"]["code"] == "unauthorized"


async def hub_core_verify() -> None:
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        assert "smoke_hub" in [b["id"] for b in await subscribe(await connect(s, user))]
        ws_admin = await connect(s, admin)
        msg_id = await ws_admin.send({"type": "heads_up/hub_trace"})
        assert (await ws_admin.recv(msg_id))["success"]
        print("clear:", await call(s, admin, "clear", {"id": "smoke_hub"}))
        assert "smoke_hub" not in [b["id"] for b in await subscribe(await connect(s, user))]
        print("hub core survived the restart")


SMOKE_POLICY = "Smoke reminder"


async def policies() -> None:
    """A reminder policy added through the real subentry flow, used by a message, acknowledged."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        headers = {"Authorization": f"Bearer {admin}"}
        eid = await entry_id(s, admin)
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow",
            json={"handler": [eid, "policy"], "show_advanced_options": False},
            headers=headers,
        )
        flow = await r.json()
        assert flow["type"] == "form", flow
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow/{flow['flow_id']}",
            json={"name": SMOKE_POLICY, "type": "reminder", "every_minutes": 30, "max_count": 3},
            headers=headers,
        )
        result = await r.json()
        print("policy form:", result["type"], result.get("errors"))
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow",
            json={"handler": [eid, "policy"], "show_advanced_options": False},
            headers=headers,
        )
        flow = await r.json()
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow/{flow['flow_id']}",
            json={"name": "Smoke night", "type": "quiet_hours"},
            headers=headers,
        )
        print("quiet hours form:", (await r.json())["type"])
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow",
            json={"handler": [eid, "policy"], "show_advanced_options": False},
            headers=headers,
        )
        flow = await r.json()
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow/{flow['flow_id']}",
            # Disabled and limited to a tag nothing uses: it must not hide the other smoke banners.
            json={
                "name": "Smoke digest",
                "type": "summarize",
                "enabled": False,
                "tags": ["smoke_never"],
            },
            headers=headers,
        )
        print("summarize form:", (await r.json())["type"])
        await asyncio.sleep(1)
        data = {"id": "smoke_policy", "message": "Policy", "timeout": 0, "policy": SMOKE_POLICY}
        print(
            "notify with policy:", await call(s, admin, "notify", {**data, "channels": ["banner"]})
        )
        ws_user, ws_admin = await connect(s, user), await connect(s, admin)
        msg_id = await ws_user.send({"type": "heads_up/acknowledge", "banner_id": "smoke_policy"})
        print("acknowledge:", await ws_user.recv(msg_id))
        msg_id = await ws_user.send({"type": "heads_up/acknowledge", "banner_id": "missing"})
        assert (await ws_user.recv(msg_id))["error"]["code"] == "not_found"
        msg_id = await ws_user.send({"type": "heads_up/hub_usage", "name": "Everyone"})
        assert (await ws_user.recv(msg_id))["error"]["code"] == "unauthorized"
        msg_id = await ws_admin.send({"type": "heads_up/hub_usage", "name": "Everyone"})
        assert (await ws_admin.recv(msg_id))["result"] == {"policies": []}
        msg_id = await ws_admin.send({"type": "heads_up/hub_trace", "message_id": "smoke_policy"})
        trace = (await ws_admin.recv(msg_id))["result"]["entries"]
        assert any(e["result"] == "acknowledged" for e in trace), trace


async def editors() -> None:
    """What the panel's editors do: create, reconfigure and delete a subentry through the REST
    flow API and the delete command, and read the result through heads_up/panel_config."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        headers = {"Authorization": f"Bearer {admin}"}
        ws = await connect(s, admin)
        base = f"{BASE}/api/config/config_entries/subentries/flow"

        async def config() -> dict[str, Any]:
            msg_id = await ws.send({"type": "heads_up/panel_config"})
            return dict((await ws.recv(msg_id))["result"])

        async def flow(start: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
            r = await s.post(base, json={"show_advanced_options": False, **start}, headers=headers)
            opened = await r.json()
            r = await s.post(f"{base}/{opened['flow_id']}", json=data, headers=headers)
            return dict(await r.json())

        state = await config()
        eid = state["entry_id"]
        for old in [a for a in state["audiences"] if a["name"] == "Smoke family"]:
            msg_id = await ws.send(
                {
                    "type": "config_entries/subentries/delete",
                    "entry_id": eid,
                    "subentry_id": old["subentry_id"],
                }
            )
            await ws.recv(msg_id)
        made = await flow(
            {"handler": [eid, "audience"]},
            {"name": "Smoke family", "kind": "persons", "persons": ["person.dev_admin"]},
        )
        print("create:", made["type"])
        assert made["type"] == "create_entry", made
        await asyncio.sleep(1)
        mine = next(a for a in (await config())["audiences"] if a["name"] == "Smoke family")
        assert mine["data"]["persons"] == ["person.dev_admin"] and mine["members"] == [
            "person.dev_admin"
        ], mine
        bad = await flow(
            {"handler": [eid, "audience"]},
            {"name": "Smoke family", "kind": "persons", "persons": ["person.dev_admin"]},
        )
        assert bad["type"] == "form" and bad["errors"] == {"name": "name_exists"}, bad
        print("duplicate refused:", bad["errors"])
        both = ["person.dev_admin", "person.dev_user"]
        changed = await flow(
            {"handler": [eid, "audience"], "subentry_id": mine["subentry_id"]},
            {"name": "Smoke family", "kind": "persons", "persons": both},
        )
        print("reconfigure:", changed["type"])
        assert changed["type"] == "abort" and changed["reason"] == "reconfigure_successful", changed
        await asyncio.sleep(1)
        mine = next(a for a in (await config())["audiences"] if a["name"] == "Smoke family")
        assert mine["data"]["persons"] == both, mine
        ws_user = await connect(s, user)
        msg_id = await ws_user.send({"type": "heads_up/panel_config"})
        assert (await ws_user.recv(msg_id))["error"]["code"] == "unauthorized"
        msg_id = await ws.send(
            {
                "type": "config_entries/subentries/delete",
                "entry_id": eid,
                "subentry_id": mine["subentry_id"],
            }
        )
        assert (await ws.recv(msg_id))["success"]
        await asyncio.sleep(1)
        assert "Smoke family" not in [a["name"] for a in (await config())["audiences"]]
        print("delete: ok")


async def policies_verify() -> None:
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        # The policy survived the restart: a call naming it is still accepted.
        data = {"id": "smoke_policy", "message": "Policy", "timeout": 0, "policy": SMOKE_POLICY}
        await call(s, admin, "notify", {**data, "channels": ["banner"]})
        print("clear:", await call(s, admin, "clear", {"id": "smoke_policy"}))
        print("policies survived the restart")


async def persistent_ids(ws: WS) -> list[str]:
    msg_id = await ws.send({"type": "persistent_notification/get"})
    return sorted(n["notification_id"] for n in (await ws.recv(msg_id))["result"])


async def hub_e2e() -> None:
    """A message on the banner and the bell, an identical update ignored, acknowledged, the
    panel's data commands answering, the limits stored (H10). Pushes need a real device (rule 2)."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        ws = await connect(s, admin)
        data = {
            "id": "smoke_e2e",
            "message": "End to end",
            "severity": "warning",
            "timeout": 0,
            "channels": ["banner", "persistent"],
        }
        result = await call(s, admin, "notify", data)
        assert result["channels"]["persistent"]["sent"] == 1, result
        assert "hu_smoke_e2e" in await persistent_ids(ws)
        await call(s, admin, "notify", data)  # the same update again
        msg_id = await ws.send({"type": "heads_up/hub_trace", "message_id": "smoke_e2e"})
        trace = (await ws.recv(msg_id))["result"]["entries"]
        assert any(e["reason"] == "duplicate" for e in trace), trace
        ws_user = await connect(s, user)
        msg_id = await ws_user.send({"type": "heads_up/acknowledge", "banner_id": "smoke_e2e"})
        assert (await ws_user.recv(msg_id))["success"]
        for command, extra in (
            ("panel_overview", {}),
            ("panel_messages", {}),
            ("panel_trace", {"message_id": "smoke_e2e"}),
            ("settings_get", {}),
            ("welcome_get", {}),
        ):
            msg_id = await ws.send({"type": f"heads_up/{command}", **extra})
            reply = await ws.recv(msg_id)
            assert reply["success"], (command, reply)
        msg_id = await ws.send({"type": "heads_up/settings_get"})
        options = (await ws.recv(msg_id))["result"]["options"]
        assert options["rate_per_device_per_minute"] == 5, options
        msg_id = await ws.send({"type": "heads_up/settings_set", "rate_per_device_per_minute": 7})
        assert (await ws.recv(msg_id))["result"]["options"]["rate_per_device_per_minute"] == 7
        msg_id = await ws.send({"type": "heads_up/settings_set", "rate_per_device_per_minute": 5})
        assert (await ws.recv(msg_id))["success"]
        print("hub e2e ok:", len(trace), "trace entries")


async def hub_e2e_verify() -> None:
    """After the restart: the message and its bell notification are still there, then cleared."""
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        ws = await connect(s, admin)
        assert "smoke_e2e" in [b["id"] for b in await subscribe(await connect(s, admin))]
        assert "hu_smoke_e2e" in await persistent_ids(ws)
        await call(s, admin, "clear", {"id": "smoke_e2e"})
        await asyncio.sleep(0.5)
        assert "hu_smoke_e2e" not in await persistent_ids(ws)
        print("hub e2e survived the restart")


async def stub() -> None:
    """The stub notify services and fake players record their calls with data (H0a)."""
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        await call_service(s, admin, "hub_stub", "reset", {})
        assert await stub_calls(s, admin) == []
        await call_service(
            s,
            admin,
            "notify",
            "mobile_app_stub_phone",
            {
                "message": "hi",
                "data": {"tag": "hu-test-1", "actions": [{"action": "a", "title": "A"}]},
            },
        )
        await call_service(
            s,
            admin,
            "media_player",
            "play_media",
            {
                "entity_id": "media_player.hub_stub_kitchen",
                "media": {"media_content_id": "x", "media_content_type": "music"},
                "announce": True,
            },
        )
        calls = await stub_calls(s, admin)
        assert [(c["domain"], c["service"]) for c in calls] == [
            ("notify", "mobile_app_stub_phone"),
            ("media_player", "play_media"),
        ], calls
        assert calls[0]["data"]["data"]["tag"] == "hu-test-1", calls[0]
        assert calls[1]["data"]["announce"] is True, calls[1]
        print("stub recorded:", [(c["domain"], c["service"]) for c in calls])
        await call_service(s, admin, "hub_stub", "reset", {})
        assert await stub_calls(s, admin) == []


SMOKE_RULE = "Smoke window"


async def entry_id(s: aiohttp.ClientSession, tok: str) -> str:
    r = await s.get(
        f"{BASE}/api/config/config_entries/entry?domain=heads_up",
        headers={"Authorization": f"Bearer {tok}"},
    )
    return str((await r.json())[0]["entry_id"])


async def rules() -> None:
    """Watch rule added through the real subentry flow, then seen by admin and user."""
    async with aiohttp.ClientSession() as s:
        admin, user = await token(s, "ADMIN"), await token(s, "USER")
        headers = {"Authorization": f"Bearer {admin}"}
        await toggle(s, admin, False)
        eid = await entry_id(s, admin)
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow",
            json={"handler": [eid, "rule"], "show_advanced_options": False},
            headers=headers,
        )
        flow = await r.json()
        print("flow step:", flow["type"], flow["step_id"])
        r = await s.post(
            f"{BASE}/api/config/config_entries/subentries/flow/{flow['flow_id']}",
            json={
                "name": SMOKE_RULE,
                "entity_id": "input_boolean.test_window",
                "message": "{name} is open",
                "severity": "critical",
            },
            headers=headers,
        )
        print("flow result:", (await r.json())["type"])
        print("off -> admin sees:", [b["id"] for b in await subscribe(await connect(s, admin))])
        await toggle(s, admin, True)
        a_ws = await connect(s, admin)
        banners = await subscribe(a_ws)
        print("on -> admin sees:", [(b["id"], b["message"], b["dismissible"]) for b in banners])
        print("on -> user sees:", [b["id"] for b in await subscribe(await connect(s, user))])
        print("sensor:", await sensor(s, admin))
        bid = next(b["id"] for b in banners if b["id"].startswith("rule_"))
        for command in ("dismiss", "admin_clear"):
            msg_id = await a_ws.send({"type": f"heads_up/{command}", "banner_id": bid})
            print(command, "->", (await a_ws.recv(msg_id)).get("error", {}).get("code"))


async def rules_verify() -> None:
    """After a restart the banner is back; deleting the rule removes it."""
    async with aiohttp.ClientSession() as s:
        admin = await token(s, "ADMIN")
        ws = await connect(s, admin)
        print("after restart admin sees:", [b["id"] for b in await subscribe(ws)])
        eid = await entry_id(s, admin)
        msg_id = await ws.send({"type": "config_entries/subentries/list", "entry_id": eid})
        for sub in (await ws.recv(msg_id))["result"]:
            if sub["title"] != SMOKE_RULE:
                continue  # leave rules the maintainer made on the dev instance alone
            msg_id = await ws.send(
                {
                    "type": "config_entries/subentries/delete",
                    "entry_id": eid,
                    "subentry_id": sub["subentry_id"],
                }
            )
            print("delete rule:", (await ws.recv(msg_id))["success"])
        await asyncio.sleep(0.5)
        print(
            "after delete admin sees:", [b["id"] for b in await subscribe(await connect(s, admin))]
        )
        await toggle(s, admin, False)


asyncio.run(
    {
        "create": create,
        "verify": verify,
        "conditions": conditions,
        "for_template": for_template,
        "empty_operators": empty_operators,
        "rules": rules,
        "rules_verify": rules_verify,
        "snooze": snooze,
        "snooze_verify": snooze_verify,
        "stub": stub,
        "hub_core": hub_core,
        "hub_core_verify": hub_core_verify,
        "policies": policies,
        "policies_verify": policies_verify,
        "editors": editors,
        "hub_e2e": hub_e2e,
        "hub_e2e_verify": hub_e2e_verify,
    }[sys.argv[1]]()
)
