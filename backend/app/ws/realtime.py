"""
ShalyaMitra — WebSocket Realtime Endpoint

This is the CRITICAL bridge between the frontend Theatre Display and the
GPU backend.

The frontend's `realtime-stream.ts` connects here and receives ServerEvents
exactly matching the wire protocol defined in gpu-adapter.ts.

Modes:
  1. demo mode (explicitly enabled) — scripted feed for demo surface only
  2. production mode (default)      — relays real live pipeline only
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


def _aria_allows_alert(mode: AriaMode, severity: str) -> bool:
    if severity == "critical":
        return True
    if mode == AriaMode.silent:
        return False
    if mode == AriaMode.reactive and severity in ("info", "caution"):
        return False
    return True


def _dev_bypass_user() -> AuthUser:
    return AuthUser(
        sub=settings.dev_auth_bypass_sub,
        email=settings.dev_auth_bypass_email,
        role=settings.dev_auth_bypass_role or "admin",
    )


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
            session_id = msg.get("sessionId", "")
            token = msg.get("token", "")
            try:
                if token:
                    user = decode_supabase_jwt(token)
                elif settings.dev_auth_bypass:
                    user = _dev_bypass_user()
                else:
                    user = decode_supabase_jwt(token)
            except Exception as exc:
                if settings.dev_auth_bypass:
                    user = _dev_bypass_user()
                    token = ""
                    pass
                elif not settings.demo_mode:
                    await ws.send_text(
                        orjson.dumps(
                            {"type": "error", "code": "unauthorized", "message": str(exc)}
                        ).decode()
                    )
                    await ws.close()
                    return
                else:
                    user = AuthUser(
                        sub="00000000-0000-0000-0000-000000000000",
                        email="demo@shalyamitra.quaasx108.com",
                    )
    except (asyncio.TimeoutError, Exception):
        await ws.send_text(orjson.dumps({"type": "error", "code": "auth_timeout", "message": "Auth timeout"}).decode())
        await ws.close()
        return

    # ── Route to appropriate handler ──────────────────────
    gpu_mode = settings.gpu_provider.value
    use_nim = settings.nim_live_test and bool(settings.nvidia_api_key)
    demo_requested = gpu_mode == "demo" or session_id == "demo"
    if demo_requested and not settings.demo_mode:
        await ws.send_text(
            orjson.dumps(
                {
                    "type": "error",
                    "code": "demo_disabled",
                    "message": "Demo mode is disabled in production runtime",
                }
            ).decode()
        )
        await ws.close()
        return

    if demo_requested and use_nim:
        from app.ws.nim_session import handle_nim_session

        print("[WS] Starting LIVE NIM demo session")
        await handle_nim_session(ws, mode)
        return
    if demo_requested:
        await _handle_demo_session(ws, mode)
        return
    if not session_id:
        await ws.send_text(
            orjson.dumps(
                {
                    "type": "error",
                    "code": "invalid_session",
                    "message": "sessionId is required for live runtime",
                }
            ).decode()
        )
        await ws.close()
        return
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
    """Live session — ShalyaBus + vision/audio ingress surfaced over this WebSocket."""
    import json as _json

    from app.session.lifecycle import SessionPhase, get_session_manager
    from app.agents.orchestrator import get_orchestrator, AgentEvent, EventType
    from app.agents.surgical_memory import get_cortex
    from app.ws.display_wire import agent_display_to_wire_dict
    from app.agents.asr_pipeline import get_asr_pipeline
    from app.agents.wake_word import get_wake_word_detector
    from app.agents.tts_router import get_tts_router

    mgr = get_session_manager()
    orch = get_orchestrator()
    metrics = getattr(ws.app.state, "metrics", {}) or {}

    if not mgr.get_session(session_id):
        await mgr.create_session(session_id, "Live theatre", {}, "")

    cx = get_cortex()
    if cx.session_id != session_id:
        await orch.start_session(session_id, procedure="Live theatre", weight_kg=70.0, age=50)

    ss = mgr.get_session(session_id)
    if ss and ss.phase != SessionPhase.INTRA_OP:
        await mgr.start_intraop(session_id)

    try:
        metrics["ws_live_sessions"] = int(metrics.get("ws_live_sessions", 0)) + 1
    except Exception:
        pass

    await get_tts_router().pregenerate_alerts()

    start_mono = time.monotonic()

    async def push_agent_event(agent_ev: AgentEvent):
        elapsed = time.monotonic() - start_mono
        wire = agent_display_to_wire_dict(agent_ev, elapsed)
        if not wire:
            return
        if wire.get("type") == "alert":
            sev = wire.get("severity", "info")
            if not _aria_allows_alert(mode, sev):
                return
        try:
            await ws.send_text(orjson.dumps(wire).decode())
        except Exception:
            pass

    mgr.register_ws_callback(session_id, push_agent_event)

    try:
        while True:
            raw = await ws.receive_text()
            msg = _json.loads(raw)
            mtype = msg.get("type")
            if mtype == "ping":
                await ws.send_text(orjson.dumps({"type": "pong", "ts": msg.get("ts", 0)}).decode())
            elif mtype == "control":
                try:
                    mode = AriaMode(msg.get("mode", "reactive"))
                except Exception:
                    mode = AriaMode.reactive
            elif mtype == "client_audio":
                metrics["asr_chunks"] = int(metrics.get("asr_chunks", 0)) + 1
                audio_b64 = msg.get("audioBase64") or msg.get("audio_b64") or ""
                codec = msg.get("codec", "opus")
                detector = get_wake_word_detector()
                ww_audio = await detector.detect_in_audio(audio_b64, codec)
                asr = await get_asr_pipeline().transcribe(audio_b64, codec)
                metrics[f"asr_engine_{asr.engine_used.value}"] = int(
                    metrics.get(f"asr_engine_{asr.engine_used.value}", 0)
                ) + 1

                text = (asr.text or "").strip()
                ww_text = await detector.detect_in_text(text) if text else None

                if ww_audio and ww_audio.detected:
                    await orch.dispatch(
                        AgentEvent(
                            type=EventType.WAKE_WORD,
                            source="wake_word_audio",
                            session_id=session_id,
                            priority=4,
                            data={
                                "word_type": getattr(
                                    ww_audio.word_type, "value", str(ww_audio.word_type)
                                ),
                                "keyword": ww_audio.keyword,
                                "confidence": ww_audio.confidence,
                                "engine": getattr(
                                    ww_audio.engine_used, "value", str(ww_audio.engine_used)
                                ),
                            },
                        )
                    )
                elif ww_text and ww_text.detected:
                    await orch.dispatch(
                        AgentEvent(
                            type=EventType.WAKE_WORD,
                            source="wake_word_text",
                            session_id=session_id,
                            priority=4,
                            data={
                                "word_type": getattr(
                                    ww_text.word_type, "value", str(ww_text.word_type)
                                ),
                                "keyword": ww_text.keyword,
                                "confidence": ww_text.confidence,
                                "engine": getattr(
                                    ww_text.engine_used, "value", str(ww_text.engine_used)
                                ),
                            },
                        )
                    )

                if text:
                    await orch.dispatch(
                        AgentEvent(
                            type=EventType.TRANSCRIPT,
                            source="asr_pipeline",
                            session_id=session_id,
                            priority=6,
                            data={
                                "text": text,
                                "speaker": msg.get("speaker", "surgeon"),
                                "language": asr.language,
                                "engine": asr.engine_used.value,
                                "at": time.monotonic() - start_mono,
                            },
                        )
                    )
    except WebSocketDisconnect:
        pass
    finally:
        mgr.unregister_ws_callback(session_id, push_agent_event)
        try:
            metrics["ws_live_sessions"] = max(
                0, int(metrics.get("ws_live_sessions", 0)) - 1
            )
        except Exception:
            pass


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
    if not settings.demo_mode:
        await ws.accept()
        await ws.send_text(
            orjson.dumps(
                {
                    "type": "error",
                    "code": "demo_disabled",
                    "message": "Mock GPU websocket is disabled in production runtime",
                }
            ).decode()
        )
        await ws.close()
        return

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
