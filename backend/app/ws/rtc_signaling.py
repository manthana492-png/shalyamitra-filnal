"""
WebRTC signaling relay — pairs viewer ↔ ingest for the same session + camera.

Contract (matches launch-pad-pro-main/src/lib/webrtc.ts):
  - viewer sends { type: "rtc.offer", camera, sdp }
  - ingest responds with { type: "rtc.answer", camera, sdp }
  - either side sends { type: "rtc.ice", camera, candidate }

Connection URL:
  /ws/rtc?sessionId=<id>&role=viewer|ingest&camera=cam1
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

import orjson
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from app.config import settings

router = APIRouter()


def _key(session_id: str, camera: str) -> tuple[str, str]:
    return session_id, camera


class _RtcRoom:
    def __init__(self):
        self.viewers: list[WebSocket] = []
        self.ingests: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def add(self, role: str, ws: WebSocket) -> None:
        async with self._lock:
            if role == "ingest":
                self.ingests.append(ws)
            else:
                self.viewers.append(ws)

    async def remove(self, role: str, ws: WebSocket) -> None:
        async with self._lock:
            bucket = self.ingests if role == "ingest" else self.viewers
            if ws in bucket:
                bucket.remove(ws)

    async def targets_for(self, role: str) -> list[WebSocket]:
        async with self._lock:
            return list(self.ingests if role == "viewer" else self.viewers)


_rooms: dict[tuple[str, str], _RtcRoom] = {}
_rooms_guard = asyncio.Lock()


async def _get_room(session_id: str, camera: str) -> _RtcRoom:
    k = _key(session_id, camera)
    async with _rooms_guard:
        if k not in _rooms:
            _rooms[k] = _RtcRoom()
        return _rooms[k]


async def _broadcast(session_id: str, camera: str, sender_role: str, payload: dict[str, Any]) -> None:
    """Forward payload to the opposite role (viewer ↔ ingest)."""
    room = await _get_room(session_id, camera)
    targets = await room.targets_for(sender_role)
    dead: list[WebSocket] = []
    txt = orjson.dumps(payload).decode()
    for peer in targets:
        try:
            await peer.send_text(txt)
        except Exception:
            dead.append(peer)
    for peer in dead:
        opp = "ingest" if sender_role == "viewer" else "viewer"
        await room.remove(opp, peer)


@router.websocket("/ws/rtc")
async def rtc_signaling(
    ws: WebSocket,
    session_id: str = Query("", alias="sessionId"),
    role: str = Query("viewer"),
    camera: str = Query("cam1"),
):
    await ws.accept()
    if not session_id:
        if settings.demo_mode:
            session_id = "demo"
        else:
            await ws.send_text(
                orjson.dumps(
                    {
                        "type": "error",
                        "code": "invalid_session",
                        "message": "sessionId is required for rtc signaling in production",
                    }
                ).decode()
            )
            await ws.close()
            return
    room = await _get_room(session_id, camera)
    rnorm = "ingest" if role.lower() == "ingest" else "viewer"
    await room.add(rnorm, ws)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue

            mtype = msg.get("type")
            if mtype == "rtc.offer" and rnorm == "viewer":
                await _broadcast(session_id, camera, "viewer", msg)
            elif mtype == "rtc.answer" and rnorm == "ingest":
                await _broadcast(session_id, camera, "ingest", msg)
            elif mtype == "rtc.ice":
                # Forward ICE to opposite role
                await _broadcast(session_id, camera, rnorm, msg)
            elif mtype == "ping":
                await ws.send_text(orjson.dumps({"type": "pong", "ts": msg.get("ts")}).decode())

    except WebSocketDisconnect:
        pass
    finally:
        await room.remove(rnorm, ws)

