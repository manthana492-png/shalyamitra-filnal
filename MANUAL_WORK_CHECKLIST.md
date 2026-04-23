# ShalyaMitra — Manual Work Checklist

> Everything the code needs from YOU to go production-ready.
> Sorted by priority. Estimated time per task included.

---

## 🔴 CRITICAL — Must Do Before First Demo

### 1. Get API Keys (~10 min)

| Key | Where to Get | Cost | What It Unlocks |
|-----|-------------|------|-----------------|
| **OpenRouter API Key** | [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) | Free tier available | Scholar, Consultant, Chronicler, Vision Fallback (Gemini/Qwen/GPT), ASR fallback |
| **Supabase Credentials** | [supabase.com/dashboard](https://supabase.com/dashboard) → Settings → API | Free tier | Auth (JWT), Database, User profiles |

**Action:**
```bash
# Copy and fill in your .env file
cd backend
copy .env.example .env
# Then edit .env and paste your keys:
#   OPENROUTER_API_KEY=sk-or-v1-xxxxx
#   SUPABASE_URL=https://your-project.supabase.co
#   SUPABASE_ANON_KEY=eyJhbGci...
#   SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

### 2. Start the Backend (~2 min)

```bash
cd backend
pip install -r requirements.txt   # first time only
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
[AGENTS] Registered 11 intelligence pillars
[START] ShalyaMitra Backend v1.0.0 starting
   Agents       : 11 pillars
   Marma DB     : 107 points (52 entries)
```

### 3. Start the Frontend (~1 min)

```bash
cd launch-pad-pro-main
npm install          # first time only
npm run dev
```

Open `http://localhost:5173` — it connects to backend at `http://localhost:8000`.

---

## 🟡 IMPORTANT — Before Clinical Trial

### 4. Supabase Database Setup (~30 min)

Create these tables in your Supabase SQL editor:

```sql
-- Sessions table
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by UUID REFERENCES auth.users(id),
  procedure_name TEXT NOT NULL,
  patient_name TEXT,
  patient_age INT,
  patient_weight_kg NUMERIC,
  patient_bmi NUMERIC,
  asa_grade INT DEFAULT 2,
  comorbidities TEXT,
  domain TEXT DEFAULT 'general',
  status TEXT DEFAULT 'scheduled',
  current_mode TEXT DEFAULT 'reactive',
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own sessions" ON sessions
  FOR ALL USING (auth.uid() = created_by);

-- Surgeon profiles
CREATE TABLE surgeon_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  display_name TEXT,
  speciality TEXT,
  voice_preference TEXT DEFAULT 'nael_v1',
  custom_voice_url TEXT,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE surgeon_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own profile" ON surgeon_profiles
  FOR ALL USING (auth.uid() = id);
```

### 5. Connect OT Page to Real Backend (~20 min)

In `launch-pad-pro-main/src/pages/OT.tsx` (or wherever the theatre display lives):

```typescript
// Replace the demo event import with:
import { realtime, type ServerEvent } from '@/lib/backend-client';

// In the component:
useEffect(() => {
  const unsubscribe = realtime.subscribe((event: ServerEvent) => {
    switch (event.type) {
      case 'transcript':
        // Add to transcript list
        break;
      case 'alert':
        // Add to alert stream
        break;
      case 'vitals':
        // Update vitals display
        break;
      case 'phase':
        // Update phase indicator
        break;
    }
  });

  realtime.connect(sessionId);

  return () => {
    unsubscribe();
    realtime.disconnect();
  };
}, [sessionId]);
```

### 6. Test Voice Pipeline End-to-End (~15 min)

1. Open `http://localhost:8000/docs`
2. Try `POST /api/voice/voices/test` with:
   ```json
   { "voice_id": "nael_v1", "text": "Pre-operative brief ready" }
   ```
3. If OpenRouter key is set, you'll get audio back
4. Test ASR by sending audio via WebSocket

---

## 🟠 GPU STACK — Before H100 Deployment

### 7. Provision GPU Instance (~1 hour)

**Option A: Nebius AI Cloud (Recommended)**
1. Go to [nebius.ai](https://nebius.ai)
2. Create a GPU VM with H100 or A100
3. Install NVIDIA Container Toolkit
4. Set environment variables:
   ```bash
   GPU_PROVIDER=nebius
   GPU_BACKEND_URL=http://<your-gpu-ip>:8000
   GPU_BACKEND_TOKEN=<your-token>
   ```

**Option B: Lightning AI**
1. Go to [lightning.ai](https://lightning.ai)
2. Create a GPU Studio
3. Same env vars as above but `GPU_PROVIDER=lightning`

### 8. Deploy GPU Services (~30 min)

```bash
# On the GPU machine:
cd gpu-stack
docker compose -f docker-compose.gpu.yml up -d

# This starts:
#   1. NVIDIA Riva (ASR) — port 50051
#   2. NeMo (LLM) — port 8000
#   3. Triton (Vision) — port 8001
#   4. Holoscan (Surgical Vision) — port 8100
#   5. LiveKit (WebRTC) — port 7880
#   6. Piper TTS — port 8090
#   7. Fish Speech TTS — port 8080
#   8. Qdrant (Vector DB) — port 6333
#   9. Redis (Event Bus) — port 6379
```

### 9. Train YOLOv11 Instrument Detector (~2-4 hours)

**What you need:** 500+ labelled images of surgical instruments on tray

1. Collect images from surgeries (or use public datasets like Cholec80, m2cai16)
2. Label with [Roboflow](https://roboflow.com) or [CVAT](https://cvat.ai)
3. Classes to label: `scalpel`, `forceps`, `scissors`, `retractor`, `clamp`, `needle_holder`, `suction`, `cautery`, `swab`, `needle`
4. Train:
   ```bash
   pip install ultralytics
   yolo train model=yolo11n.pt data=instruments.yaml epochs=100 imgsz=640
   ```
5. Deploy to Triton Inference Server

### 10. Set Up LiveKit for Camera Streaming (~20 min)

```bash
# Install LiveKit server
docker run -d \
  -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  -e LIVEKIT_KEYS="your-api-key: your-api-secret" \
  livekit/livekit-server

# Update backend .env:
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

---

## 🔵 POLISH — Before Public Launch

### 11. Record Alert Audio Files (~1 hour)

Generate pre-recorded alert audio for the Critical Alert Path (< 50ms latency):

| File | Content | Priority |
|------|---------|----------|
| `alerts/haemorrhage_detected.wav` | "Active haemorrhage detected" | Critical |
| `alerts/vitals_critical.wav` | "Vitals critical — immediate attention required" | Critical |
| `alerts/instrument_missing.wav` | "Instrument count discrepancy" | Critical |
| `alerts/closure_count_failed.wav` | "Closure count FAILED — instruments unaccounted" | Critical |
| `alerts/retraction_limit.wav` | "Retraction time limit reached" | Warning |
| `alerts/phase_change.wav` | *Short chime* | Info |
| `alerts/cvs_achieved.wav` | "Critical view of safety achieved" | Info |

**How to generate:**
- Use [ElevenLabs](https://elevenlabs.io) or [Piper TTS](https://github.com/rhasspy/piper) locally
- Record at 16kHz mono WAV format
- Place in `backend/alerts/pregenerated/`

### 12. Populate Qdrant Vector Database (~2 hours)

For Scholar Agent RAG (literature search):

```python
# Install
pip install qdrant-client sentence-transformers

# Run the embedding pipeline
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient("localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create collections
client.create_collection("shalyatantra", vectors_config={"size": 384, "distance": "Cosine"})
client.create_collection("medical_kb", vectors_config={"size": 384, "distance": "Cosine"})

# Index your medical texts
# - Sushruta Samhita chapters
# - Surgical guidelines (NICE, ACS, SAGES)
# - Drug reference texts
# - Procedure-specific literature
```

### 13. SSL + Domain Setup (~30 min)

For production deployment:

```bash
# Option 1: Vercel (frontend)
cd launch-pad-pro-main
npx vercel --prod

# Option 2: Docker (full stack)
# Update CORS_ORIGINS in .env:
CORS_ORIGINS=["https://shalyamitra.dev","https://app.shalyamitra.dev"]
```

### 14. Camera Hardware Setup (~30 min per camera)

| Camera | Recommended Hardware | Connection |
|--------|---------------------|------------|
| **Cam1 (Monitor)** | Any smartphone | Scan QR code on theatre screen |
| **Cam2 (Instruments)** | Smartphone on boom/stand | Scan QR code — mount overhead |
| **Cam3 (Surgical Field)** | GoPro Hero 12 OR phone headmount | USB-C to capture card OR QR code |
| **Laparoscope** | Existing hospital laparoscope | HDMI capture card (Elgato/AVerMedia) → USB |

**Phone camera setup (easiest):**
1. Start backend + frontend
2. Go to `GET /api/camera/qr/cam1` — shows QR code
3. Nurse scans QR on any phone
4. Browser opens, camera shares automatically
5. No app install needed

---

## 📋 Quick Summary

| Category | Tasks | Est. Time |
|----------|-------|-----------|
| 🔴 Critical (first demo) | API keys + start servers | ~15 min |
| 🟡 Important (clinical trial) | DB setup + frontend wiring + voice test | ~1.5 hours |
| 🟠 GPU Stack (H100 deploy) | Provision + services + training | ~4-5 hours |
| 🔵 Polish (public launch) | Audio + vectors + SSL + cameras | ~4-5 hours |
| **Total** | | **~10-12 hours** |

---

## What's Already Done (No Action Needed)

- ✅ 36 API endpoints across 9 tag groups — all tested 200 OK
- ✅ 11 intelligence agents — auto-registered at startup
- ✅ 107 Marma points with Sushruta Samhita shlokas and modern anatomy
- ✅ 16 surgical drugs with 12 interaction pairs and dose validation
- ✅ 3-camera system with 4 connection methods each
- ✅ Vision fallback: Holoscan → Gemini Flash → Qwen2.5-VL → GPT-4.1 → OpenCV
- ✅ Audio fallback: Riva → Gemini → Whisper → Browser Web Speech
- ✅ Session lifecycle: create → pre-op → intra-op → post-op → close
- ✅ Frontend backend-client.ts with typed REST + WebSocket
- ✅ Voice profile selection (5 voices + custom upload)
- ✅ Devil's Advocate safety agent (cognitive bias prevention)
- ✅ Chronicler (auto-generated WHO-compliant operative notes)
- ✅ Docker configs for GPU stack (9 services)
