# ShalyaMitra deployment architecture

## Recommended production topology (hybrid edge-cloud)

- **Edge GPU node (OR / hospital LAN)**  
  LiveKit or WebRTC ingest, optional NVIDIA Holoscan/HoloHub path, Riva (optional), Piper/Fish TTS containers, Redis/Qdrant when co-located, FastAPI agent orchestrator (`backend`), holoscan-bridge.

- **Cloud control plane**  
  Session metadata, analytics, reporting, non-real-time workflows; optional Supabase for auth and persistence.

- **Cloud AI (primary reasoning)**  
  NVIDIA NIM API (`integrate.api.nvidia.com`) and/or OpenRouter remain the default for Nemotron, Scholar, Consultant, and vision fallbacks via VLMs when configured.

- **Optional small/medium local LLM on GPU**  
  Use only as an offline/degraded fallback for short assistant replies when WAN or cloud APIs fail—not as the primary reasoning tier.

## Realtime data plane

1. Theatre UI connects to **`/ws/realtime`** after optional **`POST /api/sessions/{id}/start`** (initializes lifecycle + vision).
2. Browser camera/WebRTC signaling uses **`/ws/rtc`** (viewer vs ingest roles in the same session room).
3. Display-bound agent events (`display_*`) route by `session_id` to all WebSockets registered for that session.
4. Vision frames can enter via **`POST /api/internal/camera/frame`** (from holoscan-bridge **`/v1/ingest_frame`**) or via existing camera manager callbacks.

## Service map (GPU stack)

| Service | Role |
|--------|------|
| `agent-orchestrator` | FastAPI + ShalyaBus |
| `livekit` | WebRTC SFU |
| `holoscan-bridge` | Health + HoloHub event proxy + frame ingest |
| `holoscan` (profile `nvidia`) | GPU vision runtime when deployed |
| `riva` (profile `nvidia`) | ASR/TTS/NMT when initialized |
| `piper` | Critical-path low-latency TTS |
| `fish-speech` | Conversational TTS (OpenRouter speech proxy when key present) |
| `redis`, `qdrant` | Session bus / RAG |

## Environment highlights

- `GPU_PROVIDER=local` — enable live WebSocket session path (not demo-only).
- `INTERNAL_BUS_TOKEN` — protect `/api/internal/*` and holoscan-bridge forwards.
- `OPENROUTER_API_KEY` — Scholar, vision fallback VLMs, Fish-speech proxy TTS.
- `NVIDIA_API_KEY` — cloud NIM reasoning.
