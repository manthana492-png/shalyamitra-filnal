"""Append-only JSONL audit aligned with nemoclaw.yaml `audit.log_events`."""

from __future__ import annotations

import json
import time
from typing import Any

from app.config import settings


def log_privacy_route(
    *,
    agent_type: str,
    tier: str,
    reason: str,
    model: str,
    endpoint: str,
    phi_detected: bool,
    latency_ms: float,
    extra: dict[str, Any] | None = None,
) -> None:
    """Record an LLM routing decision (privacy router → cloud/local path)."""
    if not settings.nemoclaw_enabled:
        return
    path = settings.nemoclaw_audit_log_path
    if not path:
        return
    row = {
        "event": "privacy_route",
        "agent_type": agent_type,
        "tier": tier,
        "reason": reason,
        "model": model,
        "endpoint": endpoint,
        "phi_detected": phi_detected,
        "latency_ms": round(latency_ms, 2),
        "ts": time.time(),
    }
    if extra:
        row["extra"] = extra
    _append_jsonl(path, row)


def log_tool_call(agent_type: str, tool: str, arguments: dict[str, Any], ok: bool) -> None:
    if not settings.nemoclaw_enabled:
        return
    path = settings.nemoclaw_audit_log_path
    if not path:
        return
    _append_jsonl(path, {
        "event": "tool_call",
        "agent_type": agent_type,
        "tool": tool,
        "arguments_keys": list(arguments.keys()),
        "ok": ok,
        "ts": time.time(),
    })


def _append_jsonl(path: str, row: dict[str, Any]) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
    except Exception:
        pass
