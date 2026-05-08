# NemoClaw layer — production wiring

This directory holds **governance YAML** plus **HTTP MCP tool servers** that ShalyaMitra runs beside the FastAPI orchestrator.

## Why it looked “not integrated” before

- The upstream **`nemoclaw` CLI** referenced in older docs is a deployment abstraction — this repo ships **declarative policy + MCP HTTP**, which FastAPI consumes directly.
- MCP scripts imported `app.*` but **`PYTHONPATH` must include `backend/`** — fixed via `_ensure_backend_on_path()` in each server.
- Nothing started Marma/Drug/Safety on **ports 3001–3003** in compose — **`gpu-stack/docker-compose.gpu.yml` now includes `nemoclaw-marma`, `nemoclaw-drug`, `nemoclaw-safety`** built from `gpu-stack/services/nemoclaw-mcp/Dockerfile`.

## Runtime integration

| Piece | Purpose |
|--------|---------|
| `nemoclaw.yaml` | Sandbox/inference/MCP definitions — loaded at runtime (`backend/app/nemoclaw/config_bundle.py`) for `/api/ops/metrics/summary` |
| `openshell-policy.yaml` | Target posture for container/OpenShell enforcement — informational until ops binds policies into orchestrators |
| `backend/app/nemoclaw/audit.py` | Optional JSONL audit (`NEMOCLAW_AUDIT_LOG_PATH`) for **`privacy_route`** events |
| `MARMA_MCP_URL` / `DRUG_MCP_URL` / `SAFETY_MCP_URL` | Agent-friendly MCP endpoints (`backend/app/config.py`) |

Agents may continue calling `app.knowledge.*` directly; use **`app.nemoclaw.call_mcp_tool`** when you want strict tool-call auditing identical to external MCP consumers.

## Deploy

From `gpu-stack/`:

```bash
docker compose -f docker-compose.gpu.yml up -d --build nemoclaw-marma nemoclaw-drug nemoclaw-safety agent-orchestrator
```

Mount `./nemoclaw` read-only into the agent container via **`NEMOCLAW_CONFIG_DIR=/nemoclaw/config`** (already in compose).
