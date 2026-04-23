# ShalyaMitra — NVIDIA Setup Guide

> You are accepted into **NVIDIA Inception** + **NVIDIA Digital Health Program**.
> This guide has TWO paths. Do Path A today (30 min). Do Path B when ready for hospital deployment.

---

## 🟢 PATH A — Go Live TODAY (No GPU, No Server, Free)

**This is what you do RIGHT NOW.** One API key = all 11 agents go live through NVIDIA infrastructure.

### Step 1: Get Your NVIDIA NIM API Key (10 minutes)

```
DO THIS NOW:

1. Open browser → go to https://build.nvidia.com
2. Click "Sign In" (top right)
3. Use your NVIDIA developer account (same one you used for Inception)
   - If you don't have one: click "Create Account" → use your email
   - Verify email → verify phone number
4. Once logged in → click your profile icon (top right)
5. Click "API Keys" or "Generate API Key"
6. Click "Generate Key"
7. COPY the key that starts with "nvapi-..."
8. SAVE IT somewhere safe (you won't see it again)
```

### Step 2: Paste The Key Into Your Project (2 minutes)

```
1. Open file: backend/.env
2. Find this line:    NVIDIA_API_KEY=
3. Paste your key:    NVIDIA_API_KEY=nvapi-your-actual-key-here
4. Save the file
```

**That's it.** All 11 agents now route through NVIDIA NIM API automatically.

### Step 3: Test It Works (5 minutes)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see in the terminal:
```
NIM API      : NIM API configured           ← THIS means it's working
NIM Models   : nvidia/llama-3.3-nemotron-super-49b-v1 (primary)
NIM Vision   : nvidia/nemotron-nano-12b-v2-vl
```

### What You Get With Path A

| What | Model | Cost |
|------|-------|------|
| All agent reasoning | Nemotron Super 49B | Free (1,000 calls/month) |
| Scholar / Consultant deep thinking | Kimi k2.5 | Free |
| Monitor / Haemorrhage fast alerts | Nemotron Nano 30B | Free |
| Surgical field vision analysis | Nemotron Nano VL 12B | Free |
| Output safety guardrails | Nemotron Safety 4B | Free |

**Free tier limit:** 1,000 API calls/month. For development and demos, this is plenty.
**Paid tier:** When you need more, upgrade at build.nvidia.com — pricing is per-call, pay-as-you-go.

### Step 4: Get Your OpenRouter Key (Fallback — 5 minutes)

```
This is your BACKUP if NIM API is temporarily down.

1. Go to https://openrouter.ai
2. Create account → verify email
3. Go to Settings → API Keys → Create Key
4. Copy the key starting with "sk-or-..."
5. Paste in backend/.env:
   OPENROUTER_API_KEY=sk-or-your-key-here
```

### ✅ PATH A DONE — You Can Stop Here

Your product is now **fully functional** with NVIDIA NIM API. Everything works.
The rest of this guide is for when you're ready for hospital deployment.

---
---

## 🔵 PATH B — Hospital-Grade Deployment (GPU Server)

**Do this when:** You have a hospital trial date, need offline capability in OR, or want sub-100ms latency.

You have THREE options for getting a GPU server. Pick ONE.

---

### OPTION 1: NVIDIA DGX Cloud (RECOMMENDED — Use Your Inception Credits)

**Why this is best:** Your Inception acceptance gives you **free DGX Cloud credits** ($1,000-$5,000). Use them.

#### Step-by-Step: Claim DGX Cloud Credits

```
1. Go to https://www.nvidia.com/en-us/startups/
2. Click "Member Login" (you're already accepted to Inception)
3. Log in with your NVIDIA account
4. In the Inception Dashboard:
   - Look for "Benefits" or "Cloud Credits" section
   - Click "Claim DGX Cloud Credits"
   - Select "DGX Cloud" as your preferred platform
   - Fill in your startup details (ShalyaMitra, healthcare/surgical AI)
5. You'll receive an email within 1-3 business days with:
   - Your DGX Cloud organization name
   - Login link for DGX Cloud console
   - Credit amount applied
```

> **NOTE:** If you don't see a "Claim Credits" option, email your Inception contact
> or write to inception@nvidia.com saying:
> "I'm an Inception member (ShalyaMitra - surgical AI). I'd like to activate my
> DGX Cloud credits for healthcare AI development."

#### Step-by-Step: Launch Your First DGX Cloud Instance

```
Once you have DGX Cloud access:

1. Go to your DGX Cloud console (URL from the email)
2. Log in with your NVIDIA account
3. Click "Launch Workload" or "New Instance"
4. Select GPU type:
   - For DEVELOPMENT: 1x H100 80GB ($3.70/hr with credits = FREE)
   - For PRODUCTION:  8x H100 80GB (full DGX node)
5. Select container image:
   - Choose "PyTorch" or "NVIDIA AI Enterprise" as base
6. Set storage: 500 GB minimum (for model weights)
7. Click "Launch"
8. Wait 2-5 minutes for the instance to start
9. You'll get:
   - SSH access: ssh user@<your-instance-ip>
   - JupyterLab URL (optional)
   - GPU status dashboard
```

#### What Your DGX Cloud Credits Get You

| Credit Amount | What You Can Run | Duration |
|---------------|-----------------|----------|
| $1,000 | 1x H100 development | ~270 hours (~34 days at 8hr/day) |
| $3,000 | 1x H100 development | ~810 hours (~101 days at 8hr/day) |
| $5,000 | 1x H100 development | ~1,350 hours (~169 days at 8hr/day) |
| $5,000 | 8x H100 (full DGX) | ~50 hours of enterprise testing |

---

### OPTION 2: AWS GPU Server (Best for India — Mumbai Region)

#### Cheapest Dev Setup: AWS g5.2xlarge

```
Step-by-step:

1. Go to https://aws.amazon.com → Sign In (create account if needed)
2. Go to EC2 → "Launch Instance"
3. Settings:
   - Name: ShalyaMitra-GPU
   - AMI: Search "Deep Learning AMI (Ubuntu)" → select latest
   - Instance type: g5.2xlarge
   - Key pair: Create new → download .pem file → SAVE IT
   - Storage: 200 GB gp3
   - Region: ap-south-1 (Mumbai)
4. Security Group:
   - Allow SSH (port 22) from your IP
   - Allow port 8000 (ShalyaMitra backend)
   - Allow port 50051 (Riva gRPC)
5. Click "Launch Instance"
6. Wait 2-3 minutes
7. Copy the "Public IPv4 address"
8. SSH in:
   ssh -i your-key.pem ubuntu@<your-ip>
```

| Instance | GPU | VRAM | Cost/hr | Monthly (8hr/day) | Good For |
|----------|-----|------|---------|-------------------|----------|
| g5.2xlarge | 1x A10G | 24 GB | $1.21 | $290 | Dev + Riva + NIM containers |
| g5.12xlarge | 4x A10G | 96 GB | $5.67 | $1,360 | Full stack + Holoscan |
| p4d.24xlarge | 8x A100 | 640 GB | $32.77 | $7,865 | Enterprise production |

> **COST SAVING TIP:** Use "Spot Instances" for 60-70% discount.
> g5.2xlarge spot = ~$0.40/hr instead of $1.21/hr.

---

### OPTION 3: Nebius / Lambda (Cheapest H100)

#### Nebius

```
1. Go to https://nebius.ai
2. Create account (mention NVIDIA Inception for priority)
3. Dashboard → Compute → Create VM
4. Select: 1x H100 80GB, 16 vCPU, 128 GB RAM, 500 GB SSD
5. Add your SSH key
6. Launch → get IP address
7. SSH in: ssh root@<ip>
8. Cost: ~$2.50/hr (~$600/month at 8hr/day)
```

#### Lambda Labs

```
1. Go to https://lambda.ai
2. Create account
3. Dashboard → Launch Instance → 1x H100
4. Add SSH key → Launch
5. SSH in: ssh ubuntu@<ip>
6. Cost: ~$2.00/hr (~$480/month at 8hr/day)
```

---

### After You Have A GPU Server — Deploy NVIDIA Services

Once you're SSH'd into any GPU server (DGX Cloud, AWS, Nebius, or Lambda), run these commands:

#### Install Prerequisites (5 minutes)

```bash
# Update system
sudo apt update && sudo apt install -y docker.io nvidia-docker2

# Login to NVIDIA container registry
# Use your NGC API key (get it at ngc.nvidia.com → Setup → API Key)
docker login nvcr.io -u '$oauthtoken' -p YOUR_NGC_API_KEY

# Verify GPU is detected
nvidia-smi
```

#### Deploy NVIDIA Riva — Speech (ASR + TTS)

```bash
# Pull Riva container
docker pull nvcr.io/nvidia/riva/riva-speech:2.17.0

# Download models (~8 GB)
docker run --rm --gpus all \
  -v /home/riva-models:/data \
  nvcr.io/nvidia/riva/riva-speech:2.17.0 \
  bash -c "riva_init.sh"

# Start Riva server
docker run -d --name riva \
  --gpus '"device=0"' \
  -p 50051:50051 \
  -v /home/riva-models:/data \
  nvcr.io/nvidia/riva/riva-speech:2.17.0

# Test it works
# You should see: "Riva server is ready"
docker logs riva --tail 5
```

**After Riva is running**, update your `.env`:
```
RIVA_GRPC_URL=<your-gpu-server-ip>:50051
```

#### Deploy NIM Container — Local LLM (Optional upgrade from NIM API)

```bash
# This runs Nemotron LOCALLY on your GPU — zero internet needed in OR
# Only do this if you need offline capability

docker pull nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:latest

docker run -d --name nim \
  --gpus all \
  -p 8000:8000 \
  -e NGC_API_KEY=YOUR_NGC_API_KEY \
  nvcr.io/nim/nvidia/llama-3.3-nemotron-super-49b-v1:latest

# Test it works
curl http://localhost:8000/v1/models
```

**After local NIM is running**, update your `.env`:
```
# Switch from cloud NIM API to local NIM
NVIDIA_NIM_BASE_URL=http://<your-gpu-server-ip>:8000/v1
```

> **IMPORTANT:** When using local NIM, your code stays EXACTLY the same.
> The only change is the base URL. The Privacy Router handles everything.

#### Deploy Holoscan — Real-Time Surgical Vision (30 FPS)

```bash
# This is the GAME CHANGER — real-time video AI at 30 FPS
# Needs at least 8 GB GPU RAM (separate from NIM)

docker pull nvcr.io/nvidia/clara-holoscan/holoscan:2.0.0

docker run -d --name holoscan \
  --gpus '"device=0"' \
  -p 8100:8100 \
  -v /home/holoscan-pipelines:/workspace \
  nvcr.io/nvidia/clara-holoscan/holoscan:2.0.0

# Verify
docker logs holoscan --tail 5
```

#### Deploy Supporting Services

```bash
# Redis (event bus for agents)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Qdrant (vector database for knowledge)
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# LiveKit (camera streaming)
docker run -d --name livekit \
  -p 7880:7880 -p 7881:7881 \
  livekit/livekit-server:latest \
  --dev --bind 0.0.0.0
```

#### Deploy NemoClaw (Agent Security Layer)

```bash
# Initialize NemoClaw with our config
cd /path/to/surgical-intelligence-final
nemoclaw init --config ./nemoclaw/nemoclaw.yaml

# Apply security policy
nemoclaw policy apply ./nemoclaw/openshell-policy.yaml

# Start MCP tool servers
nemoclaw mcp start marma_server --port 3001
nemoclaw mcp start drug_server --port 3002
nemoclaw mcp start safety_server --port 3003

# Start ShalyaMitra inside NemoClaw sandbox
nemoclaw run -- python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## GPU Spec Reference — What Each Service Needs

| Service | GPU RAM Needed | Can Share GPU? | Required For |
|---------|---------------|----------------|-------------|
| **NIM API (cloud)** | 0 GB — runs on NVIDIA cloud | N/A | ✅ Already working (Path A) |
| **NIM Local (Nemotron 49B)** | ~40 GB | No — needs own GPU | Offline OR mode |
| **Riva ASR + TTS** | ~4 GB | Yes — shares with others | Low-latency speech in OR |
| **Holoscan** | ~8 GB per camera | Yes — shares with Riva | Real-time surgical vision |
| **Triton** | ~2 GB per model | Yes | Custom trained models only |
| **Redis** | 0 GB (CPU) | N/A | Agent event bus |
| **Qdrant** | 0 GB (CPU) | N/A | Knowledge base |
| **LiveKit** | 0 GB (CPU) | N/A | Camera streaming |

### Minimum GPU Specs By Deployment Level

| Level | GPU | VRAM | Cost | What Runs |
|-------|-----|------|------|-----------|
| **Demo / Dev** | No GPU needed | 0 | Free | NIM API (cloud) handles everything |
| **Clinical Trial** | 1x A10G (24 GB) | 24 GB | $1.2/hr | Riva speech + NIM API (cloud LLM) |
| **Hospital OR (online)** | 1x A100 (40 GB) | 40 GB | $3.5/hr | Riva + local NIM + Holoscan |
| **Hospital OR (offline)** | 1x H100 (80 GB) | 80 GB | $2-3/hr | Everything local, zero internet |
| **Enterprise (multi-OR)** | 8x H100 (DGX) | 640 GB | Credits | Multiple ORs simultaneously |

---

## Your Credentials Checklist

| # | What | Where To Get | Time | Status |
|---|------|-------------|------|--------|
| 1 | **NVIDIA NIM API Key** | build.nvidia.com → API Keys | 10 min | ☐ Do today |
| 2 | **OpenRouter API Key** | openrouter.ai/settings/keys | 5 min | ☐ Do today |
| 3 | **NGC API Key** | ngc.nvidia.com → Setup → API Key | 10 min | ☐ Need for GPU server |
| 4 | **DGX Cloud Credits** | Inception Dashboard → Claim Credits | 1-3 days | ☐ Email if not visible |
| 5 | **Supabase URL + Keys** | supabase.com/dashboard → Settings → API | 10 min | ☐ Already have? |
| 6 | **Grounding DINO Token** | deepdataspace.com (apply) | 1 day | ☐ Optional |

---

## Your .env File — Complete Template

```env
# ═══════════════════════════════════════════════════════
# REQUIRED TODAY (Path A — NIM API)
# ═══════════════════════════════════════════════════════
NVIDIA_API_KEY=nvapi-paste-your-key-here
OPENROUTER_API_KEY=sk-or-paste-your-key-here

# ═══════════════════════════════════════════════════════
# REQUIRED FOR AUTH (when you have these)
# ═══════════════════════════════════════════════════════
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ═══════════════════════════════════════════════════════
# REQUIRED ONLY FOR GPU SERVER (Path B — future)
# ═══════════════════════════════════════════════════════
# Uncomment these when you have a GPU server running:
# NVIDIA_NIM_BASE_URL=http://your-gpu-ip:8000/v1
# RIVA_GRPC_URL=your-gpu-ip:50051
# GPU_PROVIDER=local

# ═══════════════════════════════════════════════════════
# DEFAULTS (don't change unless needed)
# ═══════════════════════════════════════════════════════
GPU_PROVIDER=demo
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
LIVEKIT_URL=ws://localhost:7880
FLORENCE2_ENABLED=true
```

---

## What You Get From NVIDIA Programs

### NVIDIA Inception (you're accepted ✅)
- **$1,000 - $5,000 cloud credits** (DGX Cloud, AWS, Azure, or GCP)
- **Free NVIDIA AI Enterprise licence** (1 year) — unlocks Riva, NIM containers, Holoscan
- **Technical mentorship** from NVIDIA solutions architects
- **Access to NGC** private container registry
- **Co-marketing** — NVIDIA may feature ShalyaMitra as healthcare showcase

### NVIDIA Digital Health Program (you're accepted ✅)
- **Free Holoscan SDK** + Clara AGX developer kit (apply for hardware grant)
- **Holoscan medical device certification support** (FDA/CE pathway)
- **Access to Clara Train** for medical AI model training
- **Direct support from NVIDIA healthcare team**

---

## NemoClaw — Agent Security (Already Built ✅)

NemoClaw wraps all 11 agents in isolated sandboxes with privacy routing:

```
NemoClaw Container (on GPU server)
│
├── Sandbox 1:  Voice Agent (Nael)        [mic + speaker]
├── Sandbox 2:  Monitor Agent             [Cam1 + vitals]
├── Sandbox 3:  Haemorrhage Agent         [CRITICAL <50ms]
├── Sandbox 4:  Sentinel Agent            [Cam2 + GDINO]
├── Sandbox 5:  Eye Agent                 [Cam3 + NIM Vision]
├── Sandbox 6:  Scholar Agent             [Qdrant + cloud LLM]
├── Sandbox 7:  Pharmacist Agent          [Drug MCP + NIM]
├── Sandbox 8:  Oracle Agent              [Marma MCP]
├── Sandbox 9:  Consultant Agent          [cloud LLM only]
├── Sandbox 10: Devil's Advocate          [NO network — rules only]
├── Sandbox 11: Chronicler Agent          [filesystem + NIM]
│
├── ShalyaBus Event Router                [Redis pub/sub]
├── Privacy Router                        [PHI strip → NIM API]
└── 3 MCP Tool Servers                    [marma:3001, drug:3002, safety:3003]
```

---

## Complete NVIDIA Stack Summary

| NVIDIA Tech | What It Does | Status |
|------------|-------------|--------|
| **NIM API (Nemotron 49B)** | Primary LLM for all agents | ✅ Integrated — needs API key |
| **NIM API (Kimi k2.5)** | Deep thinking (Scholar/Consultant) | ✅ Integrated — needs API key |
| **NIM API (Nano 30B)** | Fast alerts (Monitor/Haemorrhage) | ✅ Integrated — needs API key |
| **NIM API (Nano VL 12B)** | Surgical vision analysis | ✅ Integrated — needs API key |
| **NIM API (Safety 4B)** | Output guardrails | ✅ Integrated — needs API key |
| **NemoClaw** | Agent sandboxing + lifecycle | ✅ Config built |
| **OpenShell** | Runtime isolation | ✅ Policy defined |
| **Privacy Router** | PHI redaction + routing | ✅ Fully implemented |
| **MCP Servers** | Marma/Drug/Safety tools | ✅ 3 servers, 12 tools |
| **Riva** | Low-latency ASR + TTS | ⏳ Path B (GPU server) |
| **Holoscan** | 30 FPS surgical vision | ⏳ Path B (GPU server) |
| **Triton** | Custom model serving | ⏳ Optional |

---

## Timeline

| When | What To Do |
|------|-----------|
| **Today** | Path A: Get NIM API key + OpenRouter key → paste in .env → test |
| **This week** | Claim Inception DGX Cloud credits (email if needed) |
| **Week 2** | Get NGC API key → test NIM API with all 11 agents |
| **Week 3** | Launch DGX Cloud instance → deploy Riva (speech) |
| **Week 4** | Deploy Holoscan (vision) → end-to-end dry run |
| **Week 5** | First clinical trial at target hospital |
