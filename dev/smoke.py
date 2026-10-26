"""Smoke test against the local dev HA (http://127.0.0.1:8124). Dev instance only (D-003).

Run after `make dev-up` + `make dev-onboard`:
  uv run python dev/smoke.py create   # creates banners, checks sensor, per-user dismiss
  (restart the container)
  uv run python dev/smoke.py verify   # checks the banners survived the restart, then clears
  uv run python dev/smoke.py rules    # watch rule added through the subentry flow
  (restart the container)
  uv run python dev/smoke.py rules_verify
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
        "rules": rules,
        "rules_verify": rules_verify,
    }[sys.argv[1]]()
)
