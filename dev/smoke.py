"""Smoke test against the local dev HA (http://127.0.0.1:8124). Dev instance only (D-003).

Run after `make dev-up` + `make dev-onboard`:
  uv run python dev/smoke.py create   # creates banners, checks sensor, per-user dismiss
  (restart the container)
  uv run python dev/smoke.py verify   # checks the banners survived the restart, then clears
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


asyncio.run({"create": create, "verify": verify}[sys.argv[1]]())
