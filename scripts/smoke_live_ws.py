#!/usr/bin/env python3
"""
Smoke test: `/ws/realtime` live bootstrap emits at least one theatre event.

Usage:
  python scripts/smoke_live_ws.py --url ws://127.0.0.1:9000/ws/realtime
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys


async def main() -> int:
    p = argparse.ArgumentParser(description="ShalyaMitra live WS smoke probe")
    p.add_argument("--url", default="ws://127.0.0.1:9000/ws/realtime", help="realtime WebSocket URL")
    p.add_argument("--session", default="smoke-live-session", help="session id")
    args = p.parse_args()

    try:
        import websockets
    except ImportError:
        print("Requires `websockets` (included in backend/requirements.txt)", file=sys.stderr)
        return 2

    async with websockets.connect(args.url, max_size=None) as ws:
        await ws.send(json.dumps({"type": "auth", "token": "", "sessionId": args.session}))
        for _ in range(60):
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            except asyncio.TimeoutError:
                print("timeout waiting for WS frames", file=sys.stderr)
                return 1
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if msg.get("type") in {"vitals", "transcript", "alert", "tts", "phase", "vision"}:
                print(json.dumps({"ok": True, "saw": msg.get("type")}))
                return 0
        print("no theatre events observed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
