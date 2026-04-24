# Holoscan + HoloHub + HSB

This directory is **bind-mounted** to `/app/pipelines` in the `holoscan` (NVIDIA Clara Holoscan) service.

## What runs where

- **`holoscan-bridge` (port 9100)** — ShalyaMitra service with `/health` and forwarders to the agent. The backend probes `HOLOSCAN_BASE_URL` (e.g. `http://holoscan-bridge:9100/health`) so `vision_orchestrator` can enter `holoscan_live` mode.
- **NVIDIA `holoscan` container** — GPU runtime for Holoscan graphs. You add built artifacts here.
- **Video ingest mode** — `VIDEO_INGEST_MODE=webrtc` (default): phones + LiveKit. Set to `hsb` when you use **Holoscan Sensor Bridge** (SDI/HDMI) so ops/docs stay aligned (same agent + bridge; ingest path changes in Holoscan).

## HoloHub (surgical video workflow)

1. Clone: [github.com/nvidia-holoscan/holohub](https://github.com/nvidia-holoscan/holohub)
2. Build the **Real-Time AI End-to-End Surgical Video** workflow (Holoscan 3.0+). See:  
   [HoloHub — AI surgical video](https://nvidia-holoscan.github.io/holohub/workflows/ai_surgical_video/)
3. Mount or copy the resulting application/pipelines into this folder as required by the Holoscan image layout you use.
4. Emit events to the agent in two ways:
   - HTTP: `POST http://holoscan-bridge:9100/v1/surgical_event` with JSON matching `SurgicalEventIn` (see `services/holoscan-bridge/main.py`).
   - Or `POST` directly to the agent: `/api/internal/holoscan/vision` (with `X-Internal-Token` if `INTERNAL_BUS_TOKEN` is set).

## Holoscan Sensor Bridge (HSB)

When you attach **medical** SDI/HDMI/USB capture to the GPU host:

- Set `VIDEO_INGEST_MODE=hsb` in `gpu-stack/.env` (and redeploy `holoscan-bridge` + `agent-orchestrator`).
- Configure the Holoscan graph to ingest via HSB (see NVIDIA HoloHub workflow docs for latency/ops).
- **WebRTC / phones** can stay for comms; primary video for AI can move off phones without changing the agent API.

## Event types (examples)

- `instrument_detected`, `phase`, `ood` (out-of-drape / privacy), `haemorrhage`, `overlay`, `ping` — mapped in `app/api/internal_holoscan.py` to `EventType` on the ShalyaMitra bus.
