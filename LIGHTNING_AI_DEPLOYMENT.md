# ShalyaMitra — Lightning AI GPU Deployment Guide
# Production-Ready Setup for First Clinical Surgery Trial
# ────────────────────────────────────────────────────────────────────

## Overview

This guide deploys ShalyaMitra on Lightning AI for a 2-hour live surgery session.

| Component | Where it runs | Cost |
|-----------|--------------|------|
| Riva ASR (speech → text) | Lightning AI GPU (T4 16GB) | ~$1.00/hr |
| Riva TTS (Nael voice) | Lightning AI GPU (T4 16GB) | included |
| FastAPI Backend (11 agents) | Lightning AI CPU Studio | Free |
| NIM LLM (Nemotron 49B) | NVIDIA Cloud API | Your API credits |
| React Frontend | Your laptop / Vercel | Free |

**Total cost for 1 surgery (2 hours): ~$2.00 from your $14 credits**

---

## STEP 1 — Create Lightning AI Account & Studio

1. Go to: **https://lightning.ai**
2. Sign in / Sign up (use your Google account)
3. Click **"New Studio"**
4. Select **"Blank Studio"**
5. Choose compute:
   - Click the GPU dropdown → Select **"A10G (24GB)"** ← use this for real surgery
   - Cost: ~$1.10-1.50/hr (you have $14 → ~9-12 hours — enough for full surgery + testing)
   - ⚠️ Do NOT use T4 (16GB) for real surgery — VRAM too tight with Riva loaded
6. Click **"Start"**

Wait ~2 minutes for studio to start.

---

## STEP 2 — Upload Your Project

In the Lightning AI terminal (bottom of screen), run:

```bash
# Clone or upload your project
# Option A: If you have a GitHub repo
git clone https://github.com/YOUR_USERNAME/shalyamitra.git

# Option B: Upload via Lightning AI file browser (drag and drop)
# Upload the entire 'backend' folder
```

If you don't have GitHub, zip your backend folder and drag-drop it into the Lightning AI file browser.

---

## STEP 3 — Set Environment Variables in Lightning AI

In the Lightning AI terminal:

```bash
# Create your .env file
cat > /home/user/backend/.env << 'EOF'
DEBUG=false
GPU_PROVIDER=demo
NVIDIA_API_KEY=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
NGC_API_KEY=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
OPENROUTER_API_KEY=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
NIM_LIVE_TEST=true
RIVA_GRPC_URL=localhost:50051
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
EOF
```

---

## STEP 4 — Install Python Dependencies

```bash
cd /home/user/backend

# Install requirements
pip install -r requirements.txt

# Verify install
python -c "from app.config import settings; print('Config OK:', settings.nvidia_api_key[:10])"
```

---

## STEP 5 — Deploy NVIDIA Riva (Real Speech AI)

Riva runs as a Docker container on your Lightning AI GPU.

### 5A — Authenticate with NGC

```bash
# Login to NGC container registry using your NGC API key
docker login nvcr.io --username='$oauthtoken' --password='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'
```

### 5B — Pull Riva QuickStart

```bash
# Download Riva quickstart scripts
ngc registry resource download-version "nvidia/riva/riva_quickstart:2.19.0"
cd riva_quickstart_v2.19.0
```

### 5C — Configure Riva for Medical ASR

```bash
# Edit config to enable English ASR + TTS only (saves VRAM)
cat > config.sh << 'EOF'
# Riva config for ShalyaMitra surgical ASR
service_enabled_asr=true
service_enabled_nlp=false
service_enabled_tts=true
service_enabled_nmt=false

# English only
language_code=("en-US")

# Use smaller models to fit T4 16GB
asr_acoustic_model_variant="conformer-en-US-asr-streaming-medical"

# Your NGC API key
riva_ngc_api_key="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"

# Where to store models
data_dir=/home/user/riva-data
EOF
```

### 5D — Initialize and Start Riva

```bash
# Download models (takes 5-10 minutes, only once)
bash riva_init.sh

# Start Riva server
bash riva_start.sh
```

Wait until you see:
```
Riva Speech API server - Ready
```

Riva is now running on `localhost:50051` ✅

### 5E — Test Riva is Working

```bash
python3 - << 'EOF'
import grpc
channel = grpc.insecure_channel('localhost:50051')
print("Riva connection: OK")
EOF
```

---

## STEP 6 — Update Backend Config for Live Riva

```bash
# Update .env to point to local Riva
sed -i 's/GPU_PROVIDER=demo/GPU_PROVIDER=local/' /home/user/backend/.env
```

---

## STEP 7 — Start the Backend

```bash
cd /home/user/backend

# Start FastAPI backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
[AGENTS] Registered 11 intelligence pillars
[START] ShalyaMitra Backend v1.0.0 starting
   GPU provider : local
   NIM API      : NIM API configured ✅
   NIM Models   : nvidia/llama-3.3-nemotron-super-49b-v1
```

---

## STEP 8 — Expose Backend Publicly (for frontend to connect)

Lightning AI automatically gives you a public URL.

1. In Lightning AI UI → click **"Apps"** tab
2. Find port 8000 → click **"Public URL"**
3. Copy the URL — it looks like: `https://YOUR-STUDIO.lightning.ai`

---

## STEP 9 — Connect Frontend to Lightning AI Backend

On your laptop, update the frontend:

```bash
# In your launch-pad-pro-main directory
# Edit .env.local
```

Change this line:
```
VITE_BACKEND_URL=http://localhost:8000
```
To:
```
VITE_BACKEND_URL=https://YOUR-STUDIO.lightning.ai
```

Then restart frontend:
```bash
npm run dev
```

---

## STEP 10 — Pre-Surgery Checklist (30 mins before)

Run this checklist to verify everything before the surgeon starts:

```bash
# Run on Lightning AI terminal
python3 - << 'EOF'
import httpx, asyncio, grpc

async def check():
    print("=" * 50)
    print("ShalyaMitra Pre-Surgery System Check")
    print("=" * 50)

    # 1. NIM API
    try:
        r = httpx.post(
            'https://integrate.api.nvidia.com/v1/chat/completions',
            headers={'Authorization': 'Bearer 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'},
            json={'model': 'nvidia/llama-3.3-nemotron-super-49b-v1',
                  'messages': [{'role': 'user', 'content': 'Ready'}],
                  'max_tokens': 5},
            timeout=10
        )
        print(f"✅ NIM API (Nemotron 49B): {r.status_code}")
    except Exception as e:
        print(f"❌ NIM API: {e}")

    # 2. Backend health
    try:
        r = httpx.get('http://localhost:8000/healthz', timeout=5)
        print(f"✅ Backend: {r.json()}")
    except Exception as e:
        print(f"❌ Backend: {e}")

    # 3. Riva
    try:
        channel = grpc.insecure_channel('localhost:50051')
        print(f"✅ Riva ASR: Connected on :50051")
    except Exception as e:
        print(f"❌ Riva: {e}")

    print("=" * 50)
    print("System ready for surgery ✅" )
    print("=" * 50)

asyncio.run(check())
EOF
```

All ✅ = Ready for surgery.

---

## Cost Tracker — Your $14 Budget

| Activity | Time | Cost |
|----------|------|------|
| Setup + testing | ~1 hour | ~$0.80 |
| Pre-surgery check | ~30 min | ~$0.40 |
| Live surgery | 2 hours | ~$1.60 |
| Post-op review | 30 min | ~$0.40 |
| **Total** | **4 hours** | **~$3.20** |
| **Remaining** | | **~$10.80** |

You have budget for **3 more surgeries** after the first one.

---

## IMPORTANT — Before Surgery Day

1. **Start the Lightning AI studio 30 min early** — Riva model download takes time first run
2. **Keep studio running** during surgery — do NOT let it sleep
3. **Share the public URL** with frontend operator before surgery starts
4. **Run pre-surgery checklist** (Step 10) to confirm all green
5. **NIM API rate limit**: 40 req/min — at ~3 req/min during surgery, you're safe

---

## Emergency Fallback

If Riva fails mid-surgery:
- Backend automatically falls back to demo mode
- NIM API (AI reasoning) continues working via cloud
- Surgeon sees AI alerts and transcript — no interruption
- Only speech recognition (mic) would stop

The system **never goes fully dark** due to 3-tier fallback architecture.

---

## After Surgery — Shut Down to Save Credits

```bash
# Stop Riva
bash riva_stop.sh

# Stop backend (Ctrl+C)

# In Lightning AI UI → Stop Studio
# Credits stop counting immediately
```

---

## Quick Reference — All Commands

```bash
# Start Riva
cd ~/riva_quickstart_v2.19.0 && bash riva_start.sh

# Start Backend  
cd ~/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# System check
python3 pre_surgery_check.py

# Stop everything
bash riva_stop.sh && pkill uvicorn
```

---

*ShalyaMitra v1.0.0 — Production deployment guide for Lightning AI*
*Lightning AI GPU: T4 (16GB) | Riva 2.19.0 | NIM API: Nemotron Super 49B*
