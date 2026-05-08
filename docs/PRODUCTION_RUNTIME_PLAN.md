# ShalyaMitra Production Runtime Plan

This plan defines the canonical runtime and deployment gates for a production-safe release.

## Canonical Modes

- `production` (default)
  - Real runtime paths only.
  - Demo/mock/scripted workflows are disabled.
  - Backend rejects demo-only routes unless explicitly enabled.
- `demo` (explicit)
  - Demo workflows are allowed behind explicit gates.
  - Demo frontend surface is `launch-pad-pro-main` route `/demo`.
  - Backend demo routes (`/ws/mock-gpu`, scripted `/ws/realtime` with demo session) require demo mode.

## Canonical Contracts (Single Path)

- **Realtime stream**: frontend `useRealtimeStream` -> backend `/ws/realtime`
- **RTC signaling**: frontend `webrtc.ts` -> backend `/ws/rtc`
- **TTS**: frontend voice hooks -> backend `/api/voice/voices/test` -> backend TTS router
- **Camera ingest**: holoscan bridge `/v1/ingest_frame` -> backend `/api/internal/camera/frame`
- **Ops metrics**: frontend/admin checks -> backend `/healthz` and `/api/ops/metrics/summary`

Deprecated/non-canonical paths are no longer used by production UX:
- Supabase edge realtime/tts assumptions for primary runtime.
- Silent scripted fallback in production console.
- Backend in-memory session APIs in production runtime.

## Production Acceptance Criteria

- [ ] `RUNTIME_MODE=production`
- [ ] `ENABLE_DEMO_MODE=false`
- [ ] `GPU_PROVIDER` is not `demo`
- [ ] `/healthz` returns `runtime_mode=production` and `demo_mode=false`
- [ ] `/ws/realtime` rejects demo session requests with `demo_disabled`
- [ ] `/ws/mock-gpu` returns `demo_disabled`
- [ ] Session console operates with live backend stream only (no scripted fallback)
- [ ] WebRTC signaling uses backend `/ws/rtc` only
- [ ] TTS placeholder tones are disabled (`ALLOW_AUDIO_PLACEHOLDER=false`)
- [ ] Pre-op Scholar returns structured output or explicit `503` (no silent mock shape in production)
- [ ] Lint/build/test smoke checks pass (see validation commands)

## Deployment Gates

Release is blocked if any of the following is true:

- Demo mode is enabled in production environment.
- Placeholder audio is enabled in production environment.
- Realtime path silently falls back to local scripted path.
- Backend auth allows unauthenticated access outside demo mode.
- In-memory session APIs are used as production storage.

## Environment Baselines

Backend:

- `DEBUG=false`
- `RUNTIME_MODE=production`
- `ENABLE_DEMO_MODE=false`
- `GPU_PROVIDER=local|lightning|nebius` (not `demo`)

GPU stack:

- `RUNTIME_MODE=production`
- `ENABLE_DEMO_MODE=false`
- `ALLOW_AUDIO_PLACEHOLDER=false`

Frontend:

- `VITE_BACKEND_URL=<backend-base-url>`
- `VITE_DEMO_MODE=false` for production deployments

## Validation Commands

Run from repo root (adapt if your shell requires `python` vs `python3`):

```bash
# Backend lint/test smoke
python -m compileall backend/app

# Frontend build smoke
cd launch-pad-pro-main && npm run build

# Backend health and mode checks
curl -s http://localhost:8000/healthz
curl -s http://localhost:8000/api/ops/metrics/summary

# Demo routes must be blocked in production
# (expect an error payload with code=demo_disabled)
```

## Runtime Commands

Production mode:

```bash
# Backend
set RUNTIME_MODE=production
set ENABLE_DEMO_MODE=false
set GPU_PROVIDER=local

# GPU stack
set ALLOW_AUDIO_PLACEHOLDER=false
docker compose -f gpu-stack/docker-compose.gpu.yml up -d --build
```

Demo mode:

```bash
set RUNTIME_MODE=demo
set ENABLE_DEMO_MODE=true
set GPU_PROVIDER=demo
set ALLOW_AUDIO_PLACEHOLDER=true
set VITE_DEMO_MODE=true
```

In demo mode, use frontend route `/demo` for scripted experience.
