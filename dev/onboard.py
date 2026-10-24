"""Onboard the local dev HA (http://127.0.0.1:8124) with two test users and the Heads Up entry.

Dev instance only (D-003). Generated passwords are written to dev/dev-credentials.env (gitignored).
Run: uv run python dev/onboard.py
"""

import asyncio
import secrets
from pathlib import Path

import aiohttp

BASE = "http://127.0.0.1:8124"
CLIENT_ID = f"{BASE}/"
CREDS = Path(__file__).parent / "dev-credentials.env"


async def main() -> None:
    admin_pw, user_pw = secrets.token_urlsafe(12), secrets.token_urlsafe(12)
    async with aiohttp.ClientSession() as s:
        r = await s.post(
            f"{BASE}/api/onboarding/users",
            json={
                "client_id": CLIENT_ID,
                "name": "Dev Admin",
                "username": "dev-admin",
                "password": admin_pw,
                "language": "en",
            },
        )
        r.raise_for_status()
        code = (await r.json())["auth_code"]
        r = await s.post(
            f"{BASE}/auth/token",
            data={"grant_type": "authorization_code", "code": code, "client_id": CLIENT_ID},
        )
        r.raise_for_status()
        headers = {"Authorization": f"Bearer {(await r.json())['access_token']}"}

        for step, body in (
            ("core_config", {}),
            ("analytics", {}),
            ("integration", {"client_id": CLIENT_ID, "redirect_uri": f"{BASE}/?auth_callback=1"}),
        ):
            r = await s.post(f"{BASE}/api/onboarding/{step}", json=body, headers=headers)
            print("onboarding", step, r.status)

        async with s.ws_connect(f"{BASE}/api/websocket") as ws:
            await ws.receive_json()
            await ws.send_json({"type": "auth", "access_token": headers["Authorization"][7:]})
            assert (await ws.receive_json())["type"] == "auth_ok"
            msg_id = 0

            async def call(payload: dict) -> dict:
                nonlocal msg_id
                msg_id += 1
                await ws.send_json({"id": msg_id, **payload})
                while True:
                    m = await ws.receive_json()
                    if m.get("id") == msg_id:
                        if not m.get("success"):
                            raise RuntimeError(m)
                        return m.get("result") or {}

            users = await call({"type": "config/auth/list"})
            admin_id = next(u["id"] for u in users if u["name"] == "Dev Admin")
            user = await call(
                {"type": "config/auth/create", "name": "Dev User", "group_ids": ["system-users"]}
            )
            user_id = user["user"]["id"]
            await call(
                {
                    "type": "config/auth_provider/homeassistant/create",
                    "user_id": user_id,
                    "username": "dev-user",
                    "password": user_pw,
                }
            )
            persons = await call({"type": "person/list"})
            linked = {p.get("user_id") for p in persons.get("storage", [])}
            for name, uid in (("Dev Admin", admin_id), ("Dev User", user_id)):
                if uid not in linked:
                    await call({"type": "person/create", "name": name, "user_id": uid})
            print("users + persons created")

        r = await s.post(
            f"{BASE}/api/config/config_entries/flow", json={"handler": "heads_up"}, headers=headers
        )
        flow = await r.json()
        r = await s.post(
            f"{BASE}/api/config/config_entries/flow/{flow['flow_id']}", json={}, headers=headers
        )
        print("heads_up flow:", (await r.json()).get("type"))

    CREDS.write_text(
        f"DEV_ADMIN_USER=dev-admin\nDEV_ADMIN_PASSWORD={admin_pw}\n"
        f"DEV_USER_USER=dev-user\nDEV_USER_PASSWORD={user_pw}\n"
    )
    print(f"credentials written to {CREDS.name}")


asyncio.run(main())
