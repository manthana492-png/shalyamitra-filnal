"""Load nemoclaw.yaml / openshell-policy.yaml for runtime introspection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.config import settings


def _resolved_config_dir() -> Path:
    if settings.nemoclaw_config_dir.strip():
        return Path(settings.nemoclaw_config_dir).resolve()
    # backend/app/nemoclaw/config_bundle.py → repo root is parents[3]
    here = Path(__file__).resolve()
    repo = here.parents[3]
    return repo / "nemoclaw"


@lru_cache(maxsize=1)
def _raw_bundle() -> dict[str, Any]:
    root = _resolved_config_dir()
    out: dict[str, Any] = {"config_dir": str(root), "nemoclaw_yaml": None, "openshell_policy": None}
    ny = root / "nemoclaw.yaml"
    op = root / "openshell-policy.yaml"
    try:
        if ny.is_file():
            with ny.open("r", encoding="utf-8") as f:
                out["nemoclaw_yaml"] = yaml.safe_load(f) or {}
    except Exception:
        out["nemoclaw_yaml"] = {"error": "failed_to_load"}
    try:
        if op.is_file():
            with op.open("r", encoding="utf-8") as f:
                out["openshell_policy"] = yaml.safe_load(f) or {}
    except Exception:
        out["openshell_policy"] = {"error": "failed_to_load"}
    return out


def invalidate_nemoclaw_cache() -> None:
    _raw_bundle.cache_clear()


def get_nemoclaw_summary() -> dict[str, Any]:
    """Compact summary safe for /ops and startup logs."""
    b = _raw_bundle()
    nc = b.get("nemoclaw_yaml") or {}
    agent = (nc.get("agent") or {}) if isinstance(nc, dict) else {}
    sand = nc.get("sandboxes") if isinstance(nc, dict) else None
    mcp = nc.get("mcp_servers") if isinstance(nc, dict) else None
    return {
        "config_dir": b["config_dir"],
        "nemoclaw_enabled": settings.nemoclaw_enabled,
        "agent_name": agent.get("name"),
        "agent_version": agent.get("version"),
        "sandbox_count": len(sand) if isinstance(sand, dict) else 0,
        "mcp_server_defs": len(mcp) if isinstance(mcp, dict) else 0,
        "audit_yaml_enabled": bool(((nc.get("audit") or {}) if isinstance(nc, dict) else {}).get("enabled")),
        "openshell_policy_version": (b.get("openshell_policy") or {}).get("version"),
        "marma_mcp_url": settings.marma_mcp_url,
        "drug_mcp_url": settings.drug_mcp_url,
        "safety_mcp_url": settings.safety_mcp_url,
    }
