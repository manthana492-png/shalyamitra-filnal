"""
ShalyaMitra — WebSocket Realtime Endpoint

This is the CRITICAL bridge between the frontend Theatre Display and the
GPU backend. It replaces the Supabase edge functions (nael-realtime, mock-gpu).

The frontend's `realtime-stream.ts` connects here and receives ServerEvents
exactly matching the wire protocol defined in gpu-adapter.ts.

Modes:
  1. "demo"  — plays back a scripted demo session (no GPU required)
  2. "mock"  — server-side scripted feed (proves WS pipeline end-to-end)
  3. "live"  — relays events from the real GPU stack via LiveKit / internal bus

The frontend auto-falls-back: live → mock → scripted (client-side).
"""

from __future__ import annotations

import asyncio
import json
import math
import time
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import orjson

from app.config import settings
from app.auth.jwt import decode_supabase_jwt, AuthUser
from app.models.schemas import (
    AriaMode, EvTranscript, EvAlert, EvVitals, EvPhase,
    EvPong, EvError,
)

router = APIRouter()


# ══════════════════════════════════════════════════════════
# Demo Session Data (mirrors frontend's demo-session.ts)
# ══════════════════════════════════════════════════════════

DEMO_DURATION = 360  # seconds

DEMO_EVENTS: list[dict] = [
    # Phase: preparation
    {"type": "phase", "phase": "preparation", "confidence": 1.0, "at": 0},
    {"type": "transcript", "speaker": "system", "text": "All systems connected. Nael is listening.", "at": 2, "pillar": "nael"},
    {"type": "transcript", "speaker": "nael", "text": "Good morning, Dr. Shivalumar. Pre-operative analysis loaded. Two risk flags identified.", "at": 6, "pillar": "nael"},
    {"type": "transcript", "speaker": "anaesthetist", "text": "Patient asleep, paralysed, ready for prep.", "at": 14},
    {"type": "transcript", "speaker": "surgeon", "text": "Confirming patient identity. Time-out please.", "at": 18},
    {"type": "transcript", "speaker": "nurse", "text": "Time-out complete. Antibiotic given at induction.", "at": 24},
    {"type": "transcript", "speaker": "nael", "text": "Time-out logged. Antibiotic prophylaxis recorded.", "at": 26, "pillar": "nael"},

    # Phase: access
    {"type": "phase", "phase": "access", "confidence": 1.0, "at": 30},
    {"type": "transcript", "speaker": "surgeon", "text": "Veress needle in. Starting insufflation to 12 mmHg.", "at": 32},
    {"type": "alert", "severity": "info", "title": "Instrument Count Started", "body": "14 instruments, 6 swabs deployed. Sentinel tracking active.", "source": "sentinel", "at": 45, "pillar": "sentinel", "priority": 8},
    {"type": "alert", "severity": "info", "title": "Insufflation phase", "body": "Pneumoperitoneum confirmed. Keep IAP ≤ 15 mmHg.", "source": "protocol", "at": 55, "pillar": "nael", "priority": 8},

    # Phase: dissection
    {"type": "phase", "phase": "dissection", "confidence": 1.0, "at": 60},
    {"type": "transcript", "speaker": "surgeon", "text": "Three working ports in. Camera in. Retracting fundus.", "at": 62},
    {"type": "transcript", "speaker": "nael", "text": "Dissection phase identified. Anatomy overlays available.", "at": 67, "pillar": "nael"},
    {"type": "alert", "severity": "caution", "title": "Critical View of Safety — not yet achieved", "body": "Continue dissection until both structures isolated before clipping.", "source": "vision", "at": 85, "pillar": "nael", "priority": 7},

    # Monitor Sentinel
    {"type": "alert", "severity": "info", "title": "Heart rate climbing", "body": "HR trending up: 78 → 96. Surgical stress response. No intervention required.", "source": "monitor-sentinel", "at": 92, "pillar": "monitor", "priority": 7},

    # Oracle — Marma
    {"type": "transcript", "speaker": "nael", "text": "Oracle advisory: Nābhi Marma proximity detected. Sadya Praṇahara classification.", "at": 122, "pillar": "oracle"},

    # Pharmacist
    {"type": "alert", "severity": "info", "title": "Fentanyl 100μg IV logged", "body": "Total opioid: 100μg fentanyl. No interaction flags.", "source": "pharmacist", "at": 150, "pillar": "pharmacist", "priority": 8},
    {"type": "transcript", "speaker": "nael", "text": "Pharmacist: Fentanyl 100 microgram IV logged.", "at": 152, "pillar": "pharmacist"},

    {"type": "transcript", "speaker": "surgeon", "text": "I have the cystic duct and artery clearly.", "at": 172},
    {"type": "transcript", "speaker": "nael", "text": "Two structures isolated. Critical View of Safety achieved.", "at": 175, "pillar": "nael"},

    # HAEMORRHAGE ALERT — Critical Alert Path
    {"type": "alert", "severity": "critical", "title": "⚠ POSSIBLE ARTERIAL BLEED", "body": "Pulsatile pattern detected lateral to dissection. Confidence: 94%.", "source": "haemorrhage-sentinel", "at": 210, "pillar": "haemorrhage", "priority": 1},
    {"type": "transcript", "speaker": "nael", "text": "ALERT — Possible arterial bleed. Pulsatile pattern lateral to dissection.", "at": 211, "pillar": "haemorrhage"},
    {"type": "transcript", "speaker": "surgeon", "text": "That's controlled. Small cystic artery branch — cauterised.", "at": 222},
    {"type": "transcript", "speaker": "nael", "text": "Haemorrhage resolved. Returning to overview.", "at": 226, "pillar": "haemorrhage"},

    {"type": "transcript", "speaker": "surgeon", "text": "Clipping the cystic artery. Three clips proximal.", "at": 232},
    {"type": "transcript", "speaker": "nael", "text": "Both structures clipped and divided. No bleeding.", "at": 245, "pillar": "nael"},

    # Closure
    {"type": "phase", "phase": "closure", "confidence": 1.0, "at": 300},
    {"type": "transcript", "speaker": "surgeon", "text": "Gallbladder fully detached. Specimen out.", "at": 302},
    {"type": "transcript", "speaker": "nael", "text": "Instrument count: 14/14 instruments, 6/6 swabs. Field clear.", "at": 317, "pillar": "sentinel"},
    {"type": "transcript", "speaker": "surgeon", "text": "Closing fascia. Skin closure with subcuticular.", "at": 325},

    # Chronicler
    {"type": "transcript", "speaker": "nael", "text": "Chronicler: Session summary generating. AI compute cost: ₹740.", "at": 342, "pillar": "chronicler"},
    {"type": "transcript", "speaker": "system", "text": "Session complete. Post-operative review available.", "at": 355},
]


def vitals_at(t: float) -> dict:
    """Generate realistic vital signs with drift — mirrors demo-session.ts."""
    hr = round(72 + 6 * math.sin(t / 12) + (22 if 200 < t < 225 else 0))
    spo2 = max(88, round(98 - (6 if 205 < t < 220 else 0) + math.sin(t / 9)))
    map_val = round(82 + 4 * math.sin(t / 18) - (14 if 200 < t < 225 else 0))
    etco2 = round(35 + 2 * math.sin(t / 7) + (4 if 205 < t < 220 else 0))
    temp = round(36.4 + 0.1 * math.sin(t / 60), 1)
    rr = round(14 + 2 * math.sin(t / 15))
    return {"hr": hr, "spo2": spo2, "map": map_val, "etco2": etco2, "temp": temp, "rr": rr}


# ══════════════════════════════════════════════════════════
# WebSocket Endpoint
# ══════════════════════════════════════════════════════════

@router.websocket("/ws/realtime")
async def ws_realtime(
    ws: WebSocket,
    apikey: Optional[str] = Query(None),
):
    """
    Primary realtime endpoint. The frontend connects here.

    Query params:
      - apikey: Supabase anon key (for auth)

    After connection, client sends:
      { type: "auth", token, sessionId }
      { type: "control", mode }  (silent | reactive | proactive)
      { type: "ping", ts }

    Server streams back ServerEvents continuously.
    """
    await ws.accept()

    # ── Auth handshake ────────────────────────────────────
    session_id: Optional[str] = None
    user: Optional[AuthUser] = None
    mode: AriaMode = AriaMode.reactive

    try:
        # Wait for auth message (5s timeout)
        raw = await asyncio.wait_for(ws.receive_text(), timeout=5.0)
        msg = json.loads(raw)

        if msg.get("type") == "auth":
            session_id = msg.get("sessionId", "demo")
            token = msg.get("token", "")
            try:
                user = decode_supabase_jwt(token)
            except Exception:
                # Accept anyway in demo mode
                user = AuthUser(
                    sub="00000000-0000-0000-0000-000000000000",
                    email="demo@shalyamitra.dev",
                )
    except (asyncio.TimeoutError, Exception):
        await ws.send_text(orjson.dumps({"type": "error", "code": "auth_timeout", "message": "Auth timeout"}).decode())
        await ws.close()
        return

    # ── Route to appropriate handler ──────────────────────
    gpu_mode = settings.gpu_provider.value
    use_nim = settings.nim_live_test and bool(settings.nvidia_api_key)

    if (gpu_mode == "demo" or session_id == "demo") and use_nim:
        # LIVE NIM MODE — real Nemotron 49B AI, simulated vitals
        from app.ws.nim_session import handle_nim_session
        print(f"[WS] Starting LIVE NIM session (real Nemotron 49B inference)")
        await handle_nim_session(ws, mode)
    elif gpu_mode == "demo" or session_id == "demo":
        await _handle_demo_session(ws, mode)
    else:
        # Live GPU mode — relay to GPU stack
        await _handle_live_session(ws, session_id, mode)


async def _handle_demo_session(ws: WebSocket, mode: AriaMode):
    """
    Play back the scripted demo session at real time.
    Emits vitals every second + scripted events at their timestamps.
    """
    start_time = time.monotonic()
    event_cursor = 0

    try:
        while True:
            elapsed = time.monotonic() - start_time

            if elapsed >= DEMO_DURATION:
                # Session complete
                await ws.send_text(orjson.dumps({
                    "type": "transcript", "speaker": "system",
                    "text": "Demo session complete.", "at": elapsed,
                }).decode())
                break

            # ── Emit vitals ───────────────────────────────
            v = vitals_at(elapsed)
            await ws.send_text(orjson.dumps({
                "type": "vitals", "at": elapsed, **v,
            }).decode())

            # ── Fire due scripted events ──────────────────
            while event_cursor < len(DEMO_EVENTS) and DEMO_EVENTS[event_cursor]["at"] <= elapsed:
                evt = DEMO_EVENTS[event_cursor].copy()
                event_cursor += 1

                # Apply mode filtering for alerts
                if evt.get("type") == "alert":
                    sev = evt.get("severity", "info")
                    if mode == AriaMode.silent and sev != "critical":
                        continue
                    if mode == AriaMode.reactive and sev in ("info", "caution"):
                        continue

                await ws.send_text(orjson.dumps(evt).decode())

            # ── Check for client messages (non-blocking) ──
            try:
                raw = await asyncio.wait_for(ws.receive_text(), timeout=0.05)
                msg = json.loads(raw)
                if msg.get("type") == "control":
                    mode = AriaMode(msg.get("mode", "reactive"))
                elif msg.get("type") == "ping":
                    await ws.send_text(orjson.dumps({
                        "type": "pong", "ts": msg.get("ts", 0),
                    }).decode())
            except asyncio.TimeoutError:
                pass  # No client message — continue

            # ── Tick interval ─────────────────────────────
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await ws.send_text(orjson.dumps({
                "type": "error", "code": "internal", "message": "Internal error",
            }).decode())
        except Exception:
            pass


async def _handle_live_session(ws: WebSocket, session_id: str, mode: AriaMode):
    """
    Live GPU session — relay events between frontend and GPU stack.

    In production, this:
      1. Verifies the GPU instance is running for this session
      2. Opens an internal connection to the agent orchestrator on the GPU
      3. Relays frontend audio/video → GPU, GPU events → frontend

    For now (pre-GPU), falls back to demo mode with a notice.
    """
    # TODO: Implement GPU relay when GPU orchestrator is ready
    # For now, notify frontend that live mode isn't available
    await ws.send_text(orjson.dumps({
        "type": "error", "code": "demo_mode",
        "message": "GPU backend not connected. Falling back to demo mode.",
    }).decode())
    # The frontend's realtime-stream.ts will auto-fallback to scripted mode
    await ws.close()


# ══════════════════════════════════════════════════════════
# Mock GPU Endpoint (replaces Supabase mock-gpu edge fn)
# ══════════════════════════════════════════════════════════

@router.websocket("/ws/mock-gpu")
async def ws_mock_gpu(
    ws: WebSocket,
    apikey: Optional[str] = Query(None),
):
    """
    Mock GPU endpoint — identical to demo but accessed via a separate URL.
    Proves the WebSocket pipeline end-to-end without a real GPU.
    """
    await ws.accept()

    # Simple auth handshake
    try:
        raw = await asyncio.wait_for(ws.receive_text(), timeout=5.0)
        msg = json.loads(raw)
    except Exception:
        await ws.close()
        return

    mode = AriaMode.reactive
    if msg.get("type") == "auth":
        # Accept and proceed
        pass

    # Check for control message
    try:
        raw = await asyncio.wait_for(ws.receive_text(), timeout=0.5)
        ctrl = json.loads(raw)
        if ctrl.get("type") == "control":
            mode = AriaMode(ctrl.get("mode", "reactive"))
    except (asyncio.TimeoutError, Exception):
        pass

    await _handle_demo_session(ws, mode)
