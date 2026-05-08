"""HTTP MCP helpers — matches nemoclaw/mcp_servers POST /tools/call contract."""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx

from app.config import settings


async def call_mcp_tool(
    base_url: str,
    tool_name: str,
    arguments: dict[str, Any],
    timeout: float = 15.0,
) -> Optional[dict[str, Any]]:
    """Invoke MCP tool; returns parsed JSON object from first text content chunk."""
    if not settings.nemoclaw_enabled:
        return None
    url = base_url.rstrip("/") + "/tools/call"
    try:
        async with httpx.AsyncClient(timeout=timeout) as http:
            r = await http.post(url, json={"name": tool_name, "arguments": arguments})
            if r.status_code != 200:
                return None
            data = r.json()
            parts = data.get("content") or []
            for p in parts:
                if isinstance(p, dict) and p.get("type") == "text":
                    return json.loads(p["text"])
    except Exception:
        return None
    return None


async def probe_mcp_health(base_url: str, timeout: float = 2.0) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/health"
    try:
        async with httpx.AsyncClient(timeout=timeout) as http:
            r = await http.get(url)
            return {"url": base_url, "ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"url": base_url, "ok": False, "error": str(e)}
