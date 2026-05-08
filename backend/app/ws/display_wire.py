"""Convert ShalyaBus display_* AgentEvents to Theatre WebSocket JSON wire format."""

from __future__ import annotations

import time
from typing import Any, Optional

from app.agents.orchestrator import AgentEvent, EventType
from app.agents.tts_router import get_tts_router


async def enrich_display_for_wire(event: AgentEvent) -> AgentEvent:
    """If DISPLAY_TTS lacks audio, synthesize via TTS router (critical vs normal)."""
    if event.type != EventType.DISPLAY_TTS:
        return event
    data = dict(event.data)
    if data.get("audioBase64"):
        return event
    text = data.get("text") or ""
    if not text.strip():
        return event
    severity = "critical" if data.get("voice") == "critical" else "warning"
    router = get_tts_router()
    tts = await router.synthesize(text, pillar="nael", severity=severity)
    if tts.audio_b64:
        data["audioBase64"] = tts.audio_b64
        data["mimeType"] = tts.mime_type
        data["engine"] = tts.engine_used.value
    return AgentEvent(
        id=event.id,
        type=event.type,
        source=event.source,
        priority=event.priority,
        timestamp=event.timestamp,
        session_id=event.session_id,
        data=data,
    )


def agent_display_to_wire_dict(event: AgentEvent, elapsed: float) -> Optional[dict[str, Any]]:
    """Map display_* event to frontend ServerEvent shape."""
    d = event.data
    et = event.type

    if et == EventType.DISPLAY_TRANSCRIPT:
        return {
            "type": "transcript",
            "speaker": d.get("speaker", "nael"),
            "text": d.get("text", ""),
            "at": d.get("at", elapsed),
            "pillar": d.get("pillar", "nael"),
        }

    if et == EventType.DISPLAY_ALERT:
        return {
            "type": "alert",
            "severity": d.get("severity", "info"),
            "title": d.get("title", "Alert"),
            "body": d.get("body", ""),
            "source": d.get("source", event.source),
            "at": d.get("at", elapsed),
            "pillar": d.get("pillar", "nael"),
            "priority": d.get("priority", 8),
        }

    if et == EventType.DISPLAY_VITALS:
        return {
            "type": "vitals",
            "at": d.get("at", elapsed),
            "hr": d.get("hr"),
            "spo2": d.get("spo2"),
            "map": d.get("map"),
            "etco2": d.get("etco2"),
            "temp": d.get("temp", 36.5),
            "rr": d.get("rr", 14),
        }

    if et == EventType.DISPLAY_PHASE:
        return {
            "type": "phase",
            "phase": d.get("phase", "preparation"),
            "confidence": d.get("confidence", 1.0),
            "at": d.get("at", elapsed),
        }

    if et == EventType.DISPLAY_TTS:
        payload: dict[str, Any] = {
            "type": "tts",
            "at": d.get("at", elapsed),
            "text": d.get("text", ""),
            "mimeType": d.get("mimeType", "audio/wav"),
        }
        if d.get("audioBase64"):
            payload["audioBase64"] = d["audioBase64"]
        return payload

    if et == EventType.DISPLAY_VISION:
        return {
            "type": "vision",
            "at": d.get("at", elapsed),
            "camera_id": d.get("camera_id"),
            "summary": d.get("summary", d.get("description", "")),
        }

    return None
