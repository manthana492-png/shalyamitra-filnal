# ShalyaMitra — Production Tech Stack & Infrastructure Blueprint

> *Every technology choice serves one truth: the surgeon must never break flow.*
> *Every cost decision serves one reality: this must work in a district hospital, not just a tertiary centre.*

**Document Date:** April 2026
**Version:** 2.0 — Production Release (NVIDIA Inception + Digital Health Programme)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Camera & Video Infrastructure](#2-camera--video-infrastructure)
3. [Audio & Voice Infrastructure](#3-audio--voice-infrastructure)
4. [Real-Time Communication Layer](#4-real-time-communication-layer--livekit)
5. [GPU Compute Infrastructure](#5-gpu-compute-infrastructure)
6. [AI Model Stack — Speech (STT)](#6-ai-model-stack--speech-stt)
7. [AI Model Stack — Vision (NVIDIA Holoscan)](#7-ai-model-stack--vision-nvidia-holoscan)
8. [AI Model Stack — Intelligence (LLMs)](#8-ai-model-stack--intelligence-llms)
9. [AI Model Stack — Voice Synthesis (TTS)](#9-ai-model-stack--voice-synthesis-tts)
10. [Wake Word System — "Nael"](#10-wake-word-system--nael)
11. [Dual-Path Audio Architecture](#11-dual-path-audio-architecture)
12. [Agentic Orchestration Layer](#12-agentic-orchestration-layer)
13. [Knowledge & RAG Infrastructure](#13-knowledge--rag-infrastructure)
14. [Pharmacokinetic Engine](#14-pharmacokinetic-engine)
15. [Theatre Display & Frontend](#15-theatre-display--frontend)
16. [Backend & API Layer](#16-backend--api-layer)
17. [Data Storage & Session Management](#17-data-storage--session-management)
18. [Android Companion App](#18-android-companion-app)
19. [NVIDIA Programme Benefits Integration](#19-nvidia-programme-benefits-integration)
20. [Cost Analysis Per Surgery](#20-cost-analysis-per-surgery)
21. [Complete Stack Summary Table](#21-complete-stack-summary-table)
22. [Key Open Source Repositories](#22-key-open-source-repositories--quick-reference)
23. [Deployment Sequence](#23-deployment-sequence--how-a-surgery-session-works)
24. [Future Roadmap — Audio-to-Audio Models](#24-future-roadmap--audio-to-audio-models)

---

## 1. Architecture Overview

### Architecture Philosophy — Smart & Lean

ShalyaMitra uses a **cloud-GPU-during-surgery model** instead of expensive in-theatre edge hardware. The key insight:

- Surgery lasts 1–3 hours (rarely up to 6–8)
- We spin up a single H100 GPU instance on Lightning AI or Nebius for the duration of the surgery
- All cameras (Android phones + surgeon head cam) stream via WebRTC through LiveKit to this GPU
- All AI inference (vision, voice, LLM reasoning, TTS) runs on this one GPU session
- When surgery ends, the GPU is released — you pay only for surgery hours
- Pre/post-operative work (Scholar analysis, Chronicler reports) runs on cheaper CPU instances or OpenRouter
- **Cost per surgery: approximately $8–$10 (₹650–₹830) for GPU compute.** This is radically cheaper than any ₹3L+ edge server setup.

### System Architecture Diagram

```
┌──────────────────────────── OPERATING THEATRE ─────────────────────────────┐
│                                                                             │
│  📱 Android Phone 1 ───── Monitor Camera (WebRTC via LiveKit)               │
│  📱 Android Phone 2 ───── Overhead Camera (WebRTC via LiveKit)              │
│  📷 GoPro / Phone 3 ──── Surgeon Head Camera (WebRTC via LiveKit)           │
│                                                                             │
│  🎧 BT Neckband 1 ─────── Surgeon Voice (audio stream via LiveKit)          │
│  🎧 BT Neckband 2 ─────── Anaesthesiologist Voice (audio stream)            │
│                                                                             │
│  📺 Smart TV / Monitor ── Theatre Display (Web App via Chromium)            │
│  🔊 BT Speakers ────────── AI Voice Output (distinct voice profiles)        │
│                                                                             │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ WebRTC (LiveKit)
                                    │ via Local Wi-Fi / Hospital Network
                                    ▼
┌──────────────────── CLOUD GPU INSTANCE (Surgery Session) ──────────────────┐
│  Lightning AI / Nebius — H100 80GB (1–3 hours per surgery)                 │
│                                                                             │
│  ┌── LiveKit Server (self-hosted) ── receives all audio + video ─────────┐  │
│  │                                                                       │  │
│  │  ┌── NVIDIA HOLOSCAN SDK 3.0 — VISION PIPELINE ─────────────────┐    │  │
│  │  │                                                               │    │  │
│  │  │  [Camera 1] ──► Holoscan Graph A ──► YOLOv11 Operator        │    │  │
│  │  │                                  ──► PaddleOCR Operator       │    │  │
│  │  │                                  ──► Monitor Sentinel Output  │    │  │
│  │  │                                                               │    │  │
│  │  │  [Camera 2] ──► Holoscan Graph B ──► YOLOv11 Operator        │    │  │
│  │  │                                  ──► SAM2 Operator            │    │  │
│  │  │                                  ──► ByteTrack Operator       │    │  │
│  │  │                                  ──► Sentinel Count Output    │    │  │
│  │  │                                                               │    │  │
│  │  │  [Camera 3] ──► Holoscan Graph C ──► RASO Operator           │    │  │
│  │  │                                  ──► MONAI Operator           │    │  │
│  │  │                                  ──► SAM2 Operator            │    │  │
│  │  │                                  ──► Bleed Classifier Op      │    │  │
│  │  │                                  ──► Retractor Timer Op       │    │  │
│  │  │                                  ──► Anatomy Output           │    │  │
│  │  │                                                               │    │  │
│  │  │  GPU Direct + Holoscan Sensor Bridge — shared GPU memory      │    │  │
│  │  │  Pipeline latency: ~37ms end-to-end                           │    │  │
│  │  │  Out-of-body detection + de-identification built-in           │    │  │
│  │  └───────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  │  ┌── NVIDIA RIVA — SPEECH PIPELINE ─────────────────────────────┐    │  │
│  │  │                                                               │    │  │
│  │  │  ┌─ WAKE WORD DETECTION ────────────────────────────────┐    │    │  │
│  │  │  │  Always-on "Nael" keyword spotting (CPU, <1% usage)  │    │    │  │
│  │  │  │  Primary: Riva KWS │ Fallback: OpenWakeWord          │    │    │  │
│  │  │  └──────────────────────────────────────────────────────┘    │    │  │
│  │  │                                                               │    │  │
│  │  │  ┌─ PATH 1 — CRITICAL ALERT PATH (<500ms) ─────────────┐    │    │  │
│  │  │  │  Vision Classifier ──► Pre-recorded Audio Alert      │    │    │  │
│  │  │  │                   ──► Piper TTS (dynamic values)     │    │    │  │
│  │  │  │                   ──► LiveKit ──► Neckband           │    │    │  │
│  │  │  │  ⚠  NO LLM INVOLVED — direct classifier→audio       │    │    │  │
│  │  │  └──────────────────────────────────────────────────────┘    │    │  │
│  │  │                                                               │    │  │
│  │  │  ┌─ PATH 2 — CONVERSATIONAL PATH (<2s) ────────────────┐    │    │  │
│  │  │  │  "Nael" wake word ──► Riva ASR (streaming gRPC)     │    │    │  │
│  │  │  │              ──► Nemotron LLM reasoning              │    │    │  │
│  │  │  │              ──► Fish Speech TTS (streaming)         │    │    │  │
│  │  │  │              ──► LiveKit ──► Neckband                │    │    │  │
│  │  │  └──────────────────────────────────────────────────────┘    │    │  │
│  │  │                                                               │    │  │
│  │  │  Riva: TensorRT inference + Triton model management           │    │  │
│  │  │  Fallback: Parakeet TDT + Whisper + Fish Speech + Piper      │    │  │
│  │  └───────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌── INTELLIGENCE LAYER (OpenClaw + NemoClaw Agents) ──────────────────┐   │
│  │                                                                      │   │
│  │  ┌─ The Voice Agent ───── Nemotron 3 Super (via NIM) ─────────────┐ │   │
│  │  │  Activated by "Nael" wake word → Reasons → Speaks → Displays   │ │   │
│  │  │  Queries: Scholar, Oracle, Consultant, Devil's Advocate         │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─ The Pharmacist Agent ── Drug DB + PyTCI PK Engine ────────────┐ │   │
│  │  │  Listens (anaesth channel) → Logs drugs → Calculates doses     │ │   │
│  │  │  Runs: Marsh / Schnider / Minto PK models in real-time         │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─ The Scholar Agent ───── Pre-op RAG + Risk Scoring ────────────┐ │   │
│  │  │  Pre-surgery: analyses all patient docs via OpenRouter LLM     │ │   │
│  │  │  During surgery: silent reference queried by other agents      │ │   │
│  │  │  Imaging: NVIDIA Clara-compatible pre-op CT/MRI analysis       │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─ The Oracle Agent ───── Qdrant RAG over Shalyatantra Corpus ───┐ │   │
│  │  │  Sushruta Samhita + Marma DB + Classical Texts                  │ │   │
│  │  │  Bidirectional: Classical ↔ Modern knowledge mapping            │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─ Devil's Advocate ────── Cross-Agent Conflict Detector ────────┐ │   │
│  │  │  Monitors: Scholar flags × Pharmacist state × Monitor trends   │ │   │
│  │  │  Speaks once if conflict detected at decision point            │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─ The Chronicler Agent ── Session Logger + Report Generator ────┐ │   │
│  │  │  Logs all events, alerts, decisions → Generates handover brief │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌── DATA LAYER ─────────────────────────────────────────────────────────┐  │
│  │  Redis       — session state + contextual memory                      │  │
│  │  Qdrant      — vector DB (Shalyatantra + Medical Knowledge)           │  │
│  │  PostgreSQL  — surgeon profiles, surgery history                      │  │
│  │  MinIO       — patient files, reports, recordings                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS (post-surgery only)
                                    ▼
┌──────────────────── CLOUD SERVICES (Pre/Post Operative) ───────────────────┐
│                                                                             │
│  OpenRouter API ─── Scholar (Claude/GPT for pre-op deep analysis)          │
│                 ─── Consultant (on-demand complex medical queries)          │
│                 ─── Chronicler (post-op report generation)                  │
│                                                                             │
│  Persistent Storage ─── Encrypted surgery archives                         │
│                     ─── Surgeon profile cloud backup                        │
│                     ─── Research Mode anonymised data (consent-governed)    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Camera & Video Infrastructure

### The Smart Approach: Android Phones as Cameras

Instead of dedicated surgical cameras costing ₹50K–₹2L each, we use Android phones for 2 of 3 cameras, and support both phone and dedicated camera for the surgeon's head.

| Camera Role | Hardware | Mount | Estimated Cost |
|---|---|---|---|
| Monitor Camera (Eye Two) | Any Android phone (1080p+, 2020 or newer) | Tripod/clamp aimed at patient monitor | ₹0 (existing) or ₹5K–₹10K |
| Overhead Camera (Eye Three / Sentinel) | Any Android phone (wide-angle preferred) | Ceiling/boom mount or IV pole clamp | ₹0 (existing) or ₹5K–₹10K |
| Surgeon Head Camera (Eye One) | Option A: Android phone in head mount harness | Surgical headband phone holder | ₹500–₹2K |
| | Option B: GoPro Hero 12/13 with head strap | GoPro head strap mount, Linear lens mode | ₹25K–₹35K |
| | Option C: Insta360 GO 3S (tiny, magnetic clip) | Clips to surgical loupes or headband | ₹20K–₹30K |
| | Option D: Dedicated surgical camera (Zowietek/Oppila) | Integrated headlamp-style mount | ₹40K–₹80K |

### Surgeon Head Camera — Detailed Options

**For MVP / Phase 1: Android Phone**
- Mount phone to surgical headband using a lightweight phone head mount (₹500 on Amazon)
- Use rear camera for best quality
- Stream via the same ShalyaMitra Android app
- Drawback: heavier than dedicated cameras, may shift during surgery

**For Phase 2+: GoPro Hero 13 Black**
- Best balance of quality, size, weight, and ecosystem
- Use Linear lens mode (removes fisheye distortion)
- Connect via HDMI out → USB capture card (Elgato Cam Link 4K, ₹8K) → laptop running streaming software
- OR use GoPro Labs firmware for direct RTMP streaming to our server
- Power via USB-C for unlimited duration
- Head strap mount: ₹1.5K (official GoPro accessory)

**For Phase 3+: Dedicated Surgical Camera**
- Zowietek or similar NDI-based surgical cameras
- Sub-66ms latency, designed for OR environments
- Integrates directly into LiveKit via NDI-to-WebRTC bridge

### Android Phone Camera App — What We Build

A custom ShalyaMitra Companion App (Android) that:
- Opens the rear camera in 1080p / 30fps mode
- Streams video via WebRTC to our LiveKit server on the GPU instance
- Also captures and streams microphone audio (for the neckband-connected phones)
- Shows a simple status UI: "Connected to ShalyaMitra ✓", battery %, connection quality
- Supports role selection: "Monitor Camera", "Overhead Camera", "Surgeon Camera"
- Auto-reconnects on network interruption
- Keeps screen on, prevents sleep, optimises for low battery consumption

**Tech stack for the app:**

| Layer | Technology |
|---|---|
| Language | Kotlin |
| WebRTC SDK | LiveKit Android SDK (open source, Apache 2.0) |
| Camera API | CameraX (Android Jetpack) |
| Streaming | LiveKit Room API handles all WebRTC complexity |
| Build | Gradle, target Android 10+ (API 29+) |

---

## 3. Audio & Voice Infrastructure

### Bluetooth Neckband Setup

| User | Hardware | Purpose | Estimated Cost |
|---|---|---|---|
| Surgeon | Jabra Evolve2 65 / Poly Voyager Free 60+ or any good BT neckband with ANC | Voice input to AI + AI voice output in ear | ₹3K–₹15K |
| Anaesthesiologist | Same or similar | Separate voice channel to The Pharmacist | ₹3K–₹15K |

**Key requirements for the neckband:**
- Bluetooth 5.0+ with low-latency codec (aptX Low Latency or LC3)
- AI noise cancellation / ENC — OR environments have cautery hums, suction noise, monitor alarms
- Multi-point connection — connects to the Android phone running ShalyaMitra app
- Minimum 8-hour battery — must last through extended procedures
- Comfortable for 4+ hours — lightweight, no ear fatigue

### Audio Flow (Conversational Path)

```
Surgeon speaks "Nael, [query]"
    → Neckband mic captures audio
    → Bluetooth to Android phone
    → Android phone streams audio via LiveKit WebRTC to GPU server
    → Riva KWS detects "Nael" wake word
    → Riva ASR transcribes the query (streaming gRPC)
    → Nemotron LLM generates response
    → Fish Speech TTS streams audio chunks
    → Audio streams back via LiveKit WebRTC to Android phone
    → Android phone plays audio via Bluetooth to neckband earpiece
    → Surgeon hears AI response in their ear
```

**Latency target:** Full conversational loop under 2 seconds. Achievable with:
- LiveKit WebRTC: ~100–200ms round trip
- Riva ASR (streaming): ~150–300ms
- LLM inference (Nemotron MoE): ~300–500ms
- Fish Speech TTS (streaming): ~200–300ms
- **Total: ~1–1.5 seconds end-to-end**

---

## 4. Real-Time Communication Layer — LiveKit

LiveKit is the backbone of all real-time audio and video transport in ShalyaMitra.

| Aspect | Detail |
|---|---|
| What it is | Open-source WebRTC infrastructure (SFU architecture) |
| License | Apache 2.0 — fully open, no vendor lock-in |
| Why LiveKit | Purpose-built for real-time AI applications; native SDKs for Android, Web, Python; supports AI agent rooms |
| Self-hosted | We deploy LiveKit Server on the same GPU instance used for surgery |
| GitHub | `github.com/livekit/livekit` |
| Cost | $0 (self-hosted, open source) |

**How it works in ShalyaMitra:**
- When a surgery session starts, we spin up a GPU instance and deploy LiveKit Server on it
- A LiveKit "Room" is created for this surgery session
- All 3 Android phones (cameras) join the room as video + audio publishers
- The surgeon's neckband audio streams through the phone into the room
- AI processing agents (Python) join the room as server-side participants
- These agents receive video frames and audio chunks in real-time
- AI agents publish audio responses back into the room
- The Theatre Display (web app) joins the room to receive display commands
- Everything is encrypted (DTLS-SRTP, standard WebRTC security)

**LiveKit Agents Framework:** LiveKit has a Python framework specifically for building AI agents that join rooms:
- `livekit-agents` Python SDK
- Supports STT → LLM → TTS pipelines natively
- Supports custom vision processing on video tracks
- We build each ShalyaMitra pillar as a LiveKit agent

---

## 5. GPU Compute Infrastructure

### Primary: Lightning AI or Nebius (H100 GPU, pay-per-hour)

| Provider | GPU | Price/Hour | 3-Hour Surgery Cost |
|---|---|---|---|
| Nebius AI | H100 80GB | $2.95/hr | $8.85 (~₹740) |
| Lightning AI | H100 80GB | ~$3.00–$3.50/hr | $9–$10.50 (~₹750–₹875) |
| Lightning AI | A100 80GB | ~$1.50–$2.00/hr | $4.50–$6 (~₹375–₹500) |
| Nebius AI | H200 80GB | $3.50/hr | $10.50 (~₹875) |

**Recommended setup:** Nebius H100 at $2.95/hr — best price-performance ratio.

### What Runs on This Single GPU During Surgery

| Service | VRAM Estimate | Notes |
|---|---|---|
| LiveKit Server | ~0.5 GB (CPU-bound) | WebRTC routing, minimal GPU use |
| NVIDIA Riva (ASR + TTS + KWS) | ~4–5 GB | Unified speech container with TensorRT |
| NVIDIA Holoscan (all 3 vision graphs) | ~12–15 GB | Shared GPU memory across parallel graphs |
| YOLOv11 models (all 3 cameras, as Holoscan operators) | Included in Holoscan | |
| SAM2 (instrument + anatomy, as Holoscan operators) | Included in Holoscan | |
| MONAI (anatomy segmentation, as Holoscan operator) | Included in Holoscan | |
| Fish Speech TTS (conversational voice profiles) | ~3–4 GB | Multiple distinct voice profiles |
| Small/Medium LLM (Nemotron 3 Super via NIM) | ~20–30 GB | Core reasoning, multi-agent orchestration |
| Pharmacokinetic engine | ~0.1 GB (CPU) | Mathematical models, no GPU needed |
| **Total estimated** | **~40–55 GB** | **Fits in H100 80GB with margin** |

### Session Lifecycle

- **Pre-surgery (T-30 min):** Spin up GPU instance, deploy all services via Docker Compose, run health checks
- **Surgery active (1–3 hrs):** All AI services running continuously, full contextual memory
- **Post-surgery (T+15 min):** Chronicler generates reports, then GPU instance is terminated
- **Cost:** Only active hours are billed

### Alternative: NVIDIA DGX Cloud (via Inception Programme)

If NVIDIA Inception provides DGX Cloud credits, we can use those for surgery sessions at zero marginal cost during the credit period. This is the ideal scenario for the first 6–12 months of clinical validation.

---

## 6. AI Model Stack — Speech (STT)

### Primary: NVIDIA Riva (Production Speech Pipeline)

NVIDIA Riva is a GPU-accelerated, unified speech AI SDK that provides streaming ASR, TTS, and keyword spotting (KWS) in a single optimised container — replacing what would otherwise require three separate systems to integrate.

| Aspect | Detail |
|---|---|
| What it is | Unified GPU-accelerated speech AI SDK |
| Components | Streaming ASR + TTS + Keyword Spotting in one container |
| Inference engine | TensorRT — optimised for NVIDIA GPUs |
| Model management | NVIDIA Triton Inference Server — production-grade model serving |
| Streaming protocol | gRPC streaming — low-latency, bidirectional audio |
| Medical fine-tuning | NeMo-compatible — fine-tune ASR models on surgical vocabulary |
| License | NVIDIA (free via Inception programme) |
| Cost | Free for NVIDIA Inception members |
| GitHub (client) | `github.com/nvidia-riva` |

**Why Riva over standalone Parakeet/Whisper:**
- Riva uses Parakeet/NeMo models under the hood but adds TensorRT quantisation for 2–3× faster inference on H100
- Triton Inference Server handles batching, multi-model serving, and health monitoring automatically
- Built-in keyword spotting eliminates the need for a separate intent classifier
- Single container to manage vs three separate services
- Production-grade gRPC streaming with automatic reconnection

### Riva ASR Configuration for ShalyaMitra

```yaml
# Riva ASR config (simplified)
riva_asr:
  model: parakeet-tdt-0.6b-v2  # Uses Parakeet under the hood
  streaming: true
  language: en-IN               # Indian English
  custom_vocabulary:            # Surgical + Ayurvedic terms
    - "Sushruta"
    - "Marma"
    - "haemostasis"
    - "fascia"
    - "propofol"
    - "remifentanil"
    # ... full surgical vocabulary appended
  vad_enabled: true             # Voice Activity Detection
  profanity_filter: false       # Surgical speech is direct — no filtering
```

### Fallback: Open-Source Speech Stack

If Riva is unavailable or being updated, we fall back to a proven open-source stack:

| Role | Model | License | Notes |
|---|---|---|---|
| Primary STT | NVIDIA Parakeet TDT 0.6B v2 | CC-BY-4.0 | Best open-source medical ASR |
| Secondary STT | OpenAI Whisper Large V3 Turbo | MIT | Multilingual, Hindi-English code-switching |
| Streaming wrapper | WhisperLive (Collabora) | MIT | WebSocket streaming for Whisper |

### Medical Fine-Tuning Plan

1. Collect surgical audio recordings (with consent) during Phase 1 clinical validation
2. Build a surgical vocabulary dataset: anatomical terms, drug names, Sanskrit medical terminology, clinical shorthand
3. Fine-tune using NVIDIA NeMo framework — works for both Riva (primary) and Parakeet standalone (fallback)
4. Target: **<5% WER on surgical speech by Phase 2**
5. NVIDIA Inception benefit: Free DLI courses on NeMo fine-tuning

---

## 7. AI Model Stack — Vision (NVIDIA Holoscan)

### NVIDIA Holoscan SDK 3.0 — The Vision Pipeline Container

All three camera vision pipelines now run inside **NVIDIA Holoscan SDK 3.0**, a real-time sensor and video processing framework specifically designed for surgical AI environments.

| Aspect | Detail |
|---|---|
| What it is | Graph-based real-time surgical video processing SDK |
| Languages | Python + C++ operator definition |
| Pipeline design | Graph of operators: camera → preprocessor → AI model → output |
| End-to-end latency | ~37ms (vs unoptimised custom Python pipelines) |
| GPU memory | All 3 camera graphs share GPU memory via GPU Direct |
| Video ingestion | Holoscan Sensor Bridge for ultra-low-latency frame ingestion |
| Privacy compliance | Built-in out-of-body detection + de-identification modules |
| Regulatory | Designed for SaMD (Software as Medical Device) certification — critical for CDSCO approval |
| MONAI integration | Built-in MONAI operator — directly compatible with our anatomy models |
| Reference apps | NVIDIA provides end-to-end surgical video processing reference apps |
| License | Apache 2.0 |
| GitHub | `github.com/nvidia-holoscan/holoscan-sdk` |
| Cost | Free (free via NVIDIA Inception) |

**Key principle:** YOLOv11, PaddleOCR, SAM2, MONAI, ByteTrack remain our AI models — they now run **as Holoscan operators inside Holoscan graphs**, not as standalone Python scripts. Holoscan handles pipeline orchestration, GPU memory management, and low-latency frame routing.

### Holoscan Graph Architecture

```python
# Simplified Holoscan application structure (Python)

class MonitorSentinelApp(holoscan.core.Application):
    """Camera 1 — Monitor Vital Reading pipeline"""
    def compose(self):
        video_in    = VideoStreamReplayerOp(self, name="video_in")
        preprocessor = ImagePreprocessorOp(self, name="preprocessor")
        yolo_detect  = YOLOv11Operator(self, name="yolo_detect", model="monitor_roi_detector")
        ocr_reader   = PaddleOCROperator(self, name="ocr", target="vitals")
        trend_engine = TrendEngineOp(self, name="trend")
        alert_out    = AlertDispatchOp(self, name="alert_out", path="critical")  # Critical Alert Path

        self.add_flow(video_in, preprocessor)
        self.add_flow(preprocessor, yolo_detect)
        self.add_flow(yolo_detect, ocr_reader)
        self.add_flow(ocr_reader, trend_engine)
        self.add_flow(trend_engine, alert_out)

class SentinelApp(holoscan.core.Application):
    """Camera 2 — Instrument & Swab Counting pipeline"""
    def compose(self):
        video_in     = VideoStreamReplayerOp(self, name="video_in")
        preprocessor = ImagePreprocessorOp(self, name="preprocessor")
        yolo_detect  = YOLOv11Operator(self, name="yolo_detect", model="instrument_detector")
        segmenter    = SAM2Operator(self, name="sam2")
        tracker      = ByteTrackOperator(self, name="tracker")
        count_logic  = InstrumentCountOp(self, name="count")
        alert_out    = AlertDispatchOp(self, name="alert_out", path="critical")

        self.add_flow(video_in, preprocessor)
        self.add_flow(preprocessor, yolo_detect)
        self.add_flow(yolo_detect, [segmenter, tracker])
        self.add_flow([segmenter, tracker], count_logic)
        self.add_flow(count_logic, alert_out)

class SurgeonsEyeApp(holoscan.core.Application):
    """Camera 3 — Anatomy Recognition + Haemorrhage + Retraction pipeline"""
    def compose(self):
        video_in        = VideoStreamReplayerOp(self, name="video_in")
        deidentify      = DeidentificationOp(self, name="deidentify")  # Built-in Holoscan module
        raso_op         = RASOOperator(self, name="raso")
        monai_op        = MONAIOperator(self, name="monai", bundle="surgical_anatomy")
        sam2_op         = SAM2Operator(self, name="sam2_interactive")
        bleed_op        = HaemorrhageClassifierOp(self, name="bleed")
        retract_op      = RetractorTimerOp(self, name="retract")
        anatomy_out     = AnatomyOutputOp(self, name="anatomy_out")
        alert_out       = AlertDispatchOp(self, name="alert_out", path="critical")

        self.add_flow(video_in, deidentify)
        self.add_flow(deidentify, [raso_op, monai_op, bleed_op, retract_op])
        self.add_flow([raso_op, monai_op], sam2_op)
        self.add_flow(sam2_op, anatomy_out)
        self.add_flow([bleed_op, retract_op], alert_out)
```

### Camera 1 — Monitor Vital Reading (The Monitor Sentinel)

| Component | Tool | Runs As | Purpose |
|---|---|---|---|
| Object Detection | YOLOv11 (Ultralytics) | Holoscan Operator | Detect monitor screen, localise ROIs for each vital |
| Image Processing | OpenCV (built into Holoscan) | Holoscan preprocessor | Perspective correction, contrast enhancement |
| OCR | PaddleOCR | Holoscan Operator | Extract HR, BP, SpO₂, EtCO₂, temp values |
| Trend Engine | Custom Python (NumPy/SciPy) | Holoscan Operator | Time-series modelling, predictive projection |
| Alert dispatch | Holoscan AlertDispatch | Native graph output | Routes to Critical Alert Path (<500ms) |

**Pipeline:** `Camera frame → Holoscan Graph A → YOLO operator → PaddleOCR operator → Trend engine → Critical Alert Path`

### Camera 2 — Instrument & Swab Counting (The Sentinel)

| Component | Tool | Runs As | Purpose |
|---|---|---|---|
| Object Detection | YOLOv11 (custom trained) | Holoscan Operator | Detect and classify instruments and swabs |
| Instance Tracking | ByteTrack / BoT-SORT | Holoscan Operator | Track individual instruments across frames |
| Segmentation | SAM 2 | Holoscan Operator | Precise object segmentation |
| Count Logic | Custom Python | Holoscan Operator | Running inventory, discrepancy detection |

**SAM 2:** `github.com/facebookresearch/sam2` (Apache 2.0) — zero-shot segmentation, handles any object type without specific training.

**Training datasets for YOLOv11:**
- Endoscapes dataset (laparoscopic instruments, open source)
- CholecT50 dataset (surgical tool recognition)
- Custom dataset collected during Phase 1 clinical validation

### Camera 3 — Surgical Anatomy Recognition (The Surgeon's Eye)

| Component | Tool | Runs As | Purpose |
|---|---|---|---|
| Anatomy Segmentation | RASO (Recognize Any Surgical Object) | Holoscan Operator | Open-set surgical object recognition |
| Medical Segmentation | NVIDIA MONAI + nnU-Net | Holoscan MONAI Operator (built-in) | Pre-trained surgical segmentation models |
| Foundation Model | SAM 2 (interactive) | Holoscan Operator | On-demand segmentation on surgeon query |
| Haemorrhage Detection | Custom CNN classifier | Holoscan Operator | Venous vs arterial vs capillary bleeding |
| Retraction Tracking | Object detection + timer | Holoscan Operator | Detect retractor, track duration, alert at threshold |

**NVIDIA MONAI:** `github.com/Project-MONAI/MONAI` (Apache 2.0)
- Free via NVIDIA Inception programme
- Pre-trained bundles on Hugging Face and NVIDIA NGC
- Built-in Holoscan MONAI operator — zero integration work
- Specifically designed for medical imaging AI

**Holoscan engineering advantage:** All 3 camera pipelines run as parallel Holoscan application graphs sharing GPU memory via GPU Direct — no redundant data copies between cameras. Estimated development time reduction: **~60%** versus custom Python pipeline (pre-built surgical reference apps, operator library, SaMD-ready pipeline structure).

**Surgical Datasets for Vision Training:**
- Dresden Surgical Anatomy Dataset (8 abdominal organs + vessels, pixel-level)
- Endoscapes 2025 (laparoscopic anatomy + instruments)
- CholecT50 / Cholec80 (surgical workflow + anatomy)
- AutoLaparo (hysterectomy anatomy)

---

## 8. AI Model Stack — Intelligence (LLMs)

### Multi-Model Strategy

We use different models for different pillars, optimised for their specific needs:

| Pillar | Model | Source | Why |
|---|---|---|---|
| The Voice (primary reasoning) | NVIDIA Nemotron 3 Super (120B, 12B active MoE) | Self-hosted via NIM | Extremely fast inference (MoE architecture), medical reasoning, NVIDIA ecosystem |
| The Voice (fast fallback) | Inception Mercury 2 | OpenRouter | Diffusion-based parallel token generation — fastest available for real-time loops |
| The Scholar (pre-op analysis) | Claude Opus / GPT-5.4 | OpenRouter | Deep reasoning for complex clinical synthesis — latency not critical (runs pre-surgery) |
| The Pharmacist (drug calculations) | Nemotron 3 Super + custom PK engine | Self-hosted | Drug safety requires deterministic calculations, not LLM guessing |
| The Consultant (medical knowledge) | GPT-5.4 / Claude Opus | OpenRouter | Deepest medical knowledge for complex clinical queries |
| The Oracle (Shalyatantra) | Fine-tuned Nemotron / Qwen 2.5 72B | Self-hosted with RAG | Must be self-hosted — classical corpus is our proprietary knowledge graph |
| The Devil's Advocate (safety) | Same as Voice model | Shared NIM instance | Lightweight cross-referencing logic |
| The Chronicler (documentation) | GPT-5.4 / Claude | OpenRouter | Post-surgery report generation — latency not critical |

### OpenRouter Integration

| Aspect | Detail |
|---|---|
| API | `openrouter.ai/api/v1/chat/completions` (OpenAI-compatible) |
| Key benefit | Single API key to access 300+ models — switch models without code changes |
| Usage | Scholar (pre-op), Consultant (on-demand queries), Chronicler (post-op) |
| Cost control | Set per-model spending limits; use cheaper models for routine queries |
| NOT used for | Real-time voice loop (latency via cloud relay) — use self-hosted for that |

### Self-Hosted LLM on GPU (During Surgery)

For the real-time voice loop (Conversational Path), we self-host the reasoning model on the same H100:

| Aspect | Detail |
|---|---|
| Model | NVIDIA Nemotron 3 Super 120B (12B active parameters via MoE) |
| Serving | NVIDIA NIM (NVIDIA Inference Microservices) |
| VRAM | ~20–30 GB (quantised to INT4/FP8) |
| Latency | ~200–400ms for short responses (MoE makes this very fast) |
| Why NIM | Free via NVIDIA Inception; optimised for H100; production-ready serving; handles batching and quantisation |
| Alternative | Qwen 2.5 72B (if Nemotron unavailable) — excellent medical reasoning, Apache 2.0 |

**NVIDIA NIM:** `build.nvidia.com` — containerised inference microservices, free for Inception members. Pre-optimised for H100/A100. Handles batching, quantisation, and serving automatically.

---

## 9. AI Model Stack — Voice Synthesis (TTS)

We need **distinct voice profiles** so the surgical team instantly knows which AI intelligence is speaking without looking at the display.

### Primary: Fish Speech 1.5 (Conversational Path)

| Aspect | Detail |
|---|---|
| Model | Fish Speech 1.5 |
| GitHub | `github.com/fishaudio/fish-speech` |
| License | Apache 2.0 (commercial use allowed) |
| Why | State-of-the-art open-source TTS; LLM-based Dual-AR architecture; zero-shot voice cloning; streaming output; multilingual (English + Hindi + more) |
| VRAM | ~3–4 GB |
| Latency | ~200–300ms to first audio chunk (streaming) |
| Voice profiles | Clone distinct voices from short audio samples (10–30 seconds each) |
| Usage | Conversational Path — The Voice, The Oracle, The Pharmacist |

### Ultra-Fast: Piper TTS (Critical Alert Path)

| Aspect | Detail |
|---|---|
| Model | Piper |
| GitHub | `github.com/rhasspy/piper` |
| License | MIT |
| Why | Runs on CPU, **<50ms latency** — critical for the Alert Path latency budget |
| VRAM | 0 (CPU only) |
| Usage | Critical Alert Path — all pre-generated and dynamic alert audio |

### Fallback: Coqui XTTS-v2

| Aspect | Detail |
|---|---|
| Model | XTTS-v2 (Idiap Research Institute community fork) |
| GitHub | `github.com/idiap/coqui-ai-TTS` |
| License | MPL-2.0 |
| Why | Proven, high-quality multilingual TTS; excellent voice cloning; widely deployed |
| VRAM | ~4–5 GB |

### Voice Profile Design

| Voice | Character | TTS Engine | Audio Path |
|---|---|---|---|
| The Voice (Pillar I) | Calm, warm, measured surgical companion | Fish Speech — cloned from professional voice actor | Conversational Path |
| Monitor Sentinel (Pillar II-B) | Clinical, distinct pitch — instantly recognisable | Piper (pre-alerts) + Fish Speech (explanations) | Critical Alert Path |
| The Sentinel (Pillar II-C) | Quiet, brief, authoritative | Piper — speed-optimised | Critical Alert Path |
| The Pharmacist (Pillar IV) | Precise, clinical, anaesthesia-specialist register | Fish Speech — routed to anaesthesiologist neckband only | Conversational Path |
| The Oracle (Pillar VI) | Reverent, measured, scholarly — for reading shlokas | Fish Speech — slower, deliberate pacing | Conversational Path |

---

## 10. Wake Word System — "Nael"

### Overview

The surgeon activates the ShalyaMitra conversational AI by speaking the name **"Nael"**. This single design decision eliminates the need for a complex intent classifier to distinguish surgeon-to-AI speech from surgeon-to-team speech. When the surgeon addresses the team, they use names ("Suresh, retract more"). When they address the AI, they say "Nael".

### Always-On Keyword Spotting

- Runs **continuously** on CPU throughout the surgery session
- CPU load: **<1%** — no impact on GPU inference workload
- Detects "Nael" with low false-negative rate (misses are worse than false positives in OR)
- On detection: captures the following phrase and routes it to the Conversational Path
- After the AI responds: system returns to keyword spotting mode

### Primary: NVIDIA Riva Keyword Spotting (KWS)

| Aspect | Detail |
|---|---|
| Module | Riva KWS — part of the unified Riva speech container |
| Target keyword | "Nael" (custom keyword model, trained via Riva) |
| Latency | <100ms detection latency |
| CPU usage | <1% when running on CPU |
| Integration | Native — already in the Riva container, zero additional integration |

### Fallback: OpenWakeWord

| Aspect | Detail |
|---|---|
| Tool | OpenWakeWord |
| GitHub | `github.com/dscripka/openWakeWord` |
| License | MIT |
| Why | Lightweight, runs on CPU, supports custom wake word training |
| Custom word | Train "Nael" model using OpenWakeWord's training pipeline |
| CPU usage | <1% |

### Wake Word Interaction Flow

```
[Continuous background listening]
    │
    ├── Surgeon says anything without "Nael"
    │       → Ignored (surgeon talking to team)
    │
    └── Surgeon says "Nael, [query]"
            ↓
        Wake word detected (<100ms)
            ↓
        Capture following audio phrase
            ↓
        Route to Riva ASR → Nemotron LLM → Fish Speech TTS
            ↓
        AI responds via neckband
            ↓
        Return to keyword spotting mode
```

### Independence of Safety Alerts from Wake Word

**Critical design rule:** Safety alerts do NOT require the wake word. The following agents speak **proactively without being addressed**:

- **Haemorrhage Sentinel** — speaks on haemorrhage detection
- **Monitor Sentinel** — speaks on adverse vital trend
- **Tissue Stress Monitor** — speaks on retraction duration threshold
- **Instrument Sentinel** — speaks on count discrepancy at closure

These alerts go through the **Critical Alert Path** (see Section 11) and bypass the wake word system entirely.

### Pharmacist Channel

The anaesthesiologist's channel to The Pharmacist uses a **separate wake word** (e.g., "Nael Pharma") or is configured as always-on for drug logging — since the Pharmacist primarily listens passively for drug administration events rather than responding to queries.

---

## 11. Dual-Path Audio Architecture

This is one of the most important design decisions in ShalyaMitra. A single audio pipeline cannot satisfy both the <500ms requirement for safety-critical alerts and the full reasoning cycle of conversational AI. We use **two entirely separate audio paths**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DUAL-PATH AUDIO ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PATH 1 — CRITICAL ALERT PATH                                       │   │
│  │  Latency target: <500ms end-to-end                                  │   │
│  │                                                                     │   │
│  │  Holoscan Vision Classifier                                         │   │
│  │      │                                                              │   │
│  │      ├── Haemorrhage detected → [Pre-recorded alert audio]          │   │
│  │      │       "Bleeding detected — arterial pattern, check the field"│   │
│  │      │                                                              │   │
│  │      ├── Adverse vital trend → [Piper TTS, template sentence]       │   │
│  │      │       "Blood pressure declining — projected 85 systolic"     │   │
│  │      │       "in 8 minutes"                                         │   │
│  │      │                                                              │   │
│  │      ├── Retraction duration → [Pre-recorded alert audio]           │   │
│  │      │       "Retractor at 20 minutes over the femoral cutaneous"   │   │
│  │      │       "nerve"                                                │   │
│  │      │                                                              │   │
│  │      └── Count discrepancy → [Pre-recorded alert audio]             │   │
│  │              "Swab count discrepancy — 13 of 14 confirmed"          │   │
│  │                                                                     │   │
│  │      → LiveKit → BT Neckband / Theatre Speaker                      │   │
│  │                                                                     │   │
│  │  ⚠  THIS PATH NEVER TOUCHES THE LLM                                 │   │
│  │  End-to-end: ~37ms (Holoscan) + ~50ms (Piper) + ~100ms (LiveKit)   │   │
│  │            = ~200–400ms total                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PATH 2 — CONVERSATIONAL PATH                                       │   │
│  │  Latency target: <2 seconds end-to-end                              │   │
│  │                                                                     │   │
│  │  "Nael" wake word detected                                          │   │
│  │      ↓                                                              │   │
│  │  Riva ASR (streaming gRPC) — transcribes surgeon's query            │   │
│  │      ~150–300ms                                                     │   │
│  │      ↓                                                              │   │
│  │  Nemotron LLM reasoning — queries agents as needed                  │   │
│  │  (Scholar, Oracle, Consultant, Devil's Advocate)                    │   │
│  │      ~300–500ms                                                     │   │
│  │      ↓                                                              │   │
│  │  Fish Speech TTS (streaming) — generates voice response             │   │
│  │      ~200–300ms to first audio chunk                                │   │
│  │      ↓                                                              │   │
│  │  LiveKit → BT Neckband (surgeon's ear)                              │   │
│  │      ~100–200ms                                                     │   │
│  │                                                                     │   │
│  │  Used by: The Voice, The Oracle, The Consultant, The Pharmacist     │   │
│  │  Total: ~1–1.5 seconds end-to-end                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Critical Alert Path — Pre-Generated Audio Library

For static alert messages, audio files are generated **once during system setup** using Fish Speech TTS with the appropriate voice profile, then stored as `.wav` files on the GPU instance. This eliminates TTS latency entirely for the most time-critical alerts.

| Alert Type | Audio Strategy | Latency Contribution |
|---|---|---|
| Haemorrhage detected | Pre-recorded `.wav` file | 0ms (already generated) |
| Count discrepancy | Pre-recorded `.wav` file | 0ms |
| Retraction threshold | Pre-recorded `.wav` file | 0ms |
| Dynamic vital alerts (BP, SpO₂) | Piper TTS template — fill in values at runtime | ~50ms |
| Trending alerts (predicted values) | Piper TTS template | ~50ms |

**Example Piper template for dynamic alerts:**
```python
alert_template = "Blood pressure declining — projected {systolic} systolic in {minutes} minutes"
piper_tts.synthesise(alert_template.format(systolic=87, minutes=6))
# Output audio: ~50ms
```

### Path Selection Logic

```python
def route_audio_event(event_type: str, event_data: dict):
    if event_type in CRITICAL_ALERT_TYPES:
        # Haemorrhage, monitor trend, count discrepancy, retraction
        critical_alert_path.dispatch(event_type, event_data)
    elif event_type == "wake_word_detected":
        # Surgeon said "Nael"
        conversational_path.handle(event_data["audio_chunk"])
    # Safety alerts are NEVER blocked by conversational path activity
```

---

## 12. Agentic Orchestration Layer

### Primary: OpenClaw + NemoClaw (NVIDIA)

| Aspect | Detail |
|---|---|
| Framework | OpenClaw (open-source autonomous agent runtime) + NemoClaw (NVIDIA enterprise governance wrapper) |
| License | MIT (OpenClaw) + NVIDIA open source |
| What it does | Agentic backbone — persistent memory, multi-step autonomous workflows, tool execution, inter-agent communication |
| Why NemoClaw | NVIDIA's enterprise-hardened version with security guardrails, audit logging, RBAC, sandboxed execution via OpenShell — critical for medical use |
| GPU requirement | Runs on same GPU instance; uses NIM as LLM backend |
| NVIDIA benefit | Free via NVIDIA Inception + Digital Health programme; NemoClaw announced at GTC March 2026 |

### How We Use It for ShalyaMitra

Each intelligence pillar is implemented as an OpenClaw agent ("claw") with:
- Its own persistent memory (context of this surgery)
- Its own tools (camera feed access, TTS output, display commands)
- Its own personality configuration (speech style, alert thresholds)
- Communication channels to other agents via the orchestrator

| Agent (Claw) | Tools | Memory | Trigger |
|---|---|---|---|
| Voice Agent | Riva ASR input, LLM reasoning, Fish Speech TTS, display commands | Full surgery conversation history | Continuous — activates on "Nael" wake word |
| Monitor Agent | Holoscan Camera 1 graph output, trend engine | Vital sign time-series for entire surgery | Continuous — triggers on adverse trend |
| Sentinel Agent | Holoscan Camera 2 graph output, count logic | Running instrument/swab inventory | Continuous — triggers at closure |
| Surgeon Eye Agent | Holoscan Camera 3 graph output, anatomy pipeline | Current surgical phase, identified structures | Continuous — responds to Voice queries |
| Haemorrhage Agent | Holoscan Camera 3 bleed classifier output | Field colour baseline for this surgery | Continuous — triggers on detection |
| Tissue Stress Agent | Holoscan Camera 3 retractor detector output | Retractor positions and durations | Continuous — triggers at time threshold |
| Scholar Agent | Document parsing, risk scoring, NVIDIA Clara (imaging) | Pre-op analysis document | Pre-surgery — queried by agents during surgery |
| Pharmacist Agent | Drug database, PK engine, dose calculator | Anaesthetic drug log for this surgery | Continuous — listens to anaesthesiologist channel |
| Consultant Agent | RAG over medical knowledge base, OpenRouter LLM | Query history | On-demand — queried by Voice or Pharmacist |
| Oracle Agent | RAG over Shalyatantra corpus | Consultation history | On-demand — queried by Voice or Surgeon Eye |
| Devil's Advocate | Cross-references all other agent states | All current agent states | Triggered at decision points detected by Voice |
| Chronicler Agent | All agent logs, event timeline | Complete surgery log | Continuous logging — generates reports at closure |

### Inter-Agent Communication Bus

OpenClaw's built-in messaging system handles inter-agent communication:
- Voice Agent detects surgeon asking about anatomy → queries Surgeon Eye Agent + Oracle Agent
- Surgeon Eye Agent detects Marma proximity → notifies Oracle Agent + Display
- Monitor Agent detects adverse trend → dispatches to Critical Alert Path (speaks proactively) + Display
- Devil's Advocate cross-references Scholar + Pharmacist + Monitor states at every decision point
- Chronicler subscribes to all agent event streams and logs everything

---

## 13. Knowledge & RAG Infrastructure

### Vector Database: Qdrant

| Aspect | Detail |
|---|---|
| Tool | Qdrant |
| GitHub | `github.com/qdrant/qdrant` |
| License | Apache 2.0 |
| Why | Fast, production-grade vector search; runs on CPU (no extra GPU needed); excellent filtering and payload queries |
| Use | Stores embeddings for all knowledge corpora |

### Embedding Model: NVIDIA NV-Embed-v2

| Aspect | Detail |
|---|---|
| Model | `nvidia/nv-embedqa-e5-v5` or NV-Embed-v2 |
| Why | Top-ranked embedding model; free via NVIDIA NIM; optimised for retrieval |
| NVIDIA benefit | Free inference via NIM endpoints for Inception members |

### Knowledge Corpora

| Corpus | Content | Size Estimate | Format |
|---|---|---|---|
| Shalyatantra Corpus | Sushruta Samhita (complete), Ashtanga Hridayam, Charaka Samhita (surgical), Sharangadhara Samhita, Vagbhata, Dhanvantari Nighantu | ~5,000–10,000 pages | Chunked markdown with shloka IDs, chapter/verse references |
| Marma Database | All 107 Marmas — location, classification, extent, consequences, protective doctrine, relevant shlokas | ~500 entries | Structured JSON with Sanskrit + transliteration + modern anatomy mapping |
| Medical Knowledge Base | Surgical anatomy, pharmacology, pathology, emergency protocols, complication management | ~50,000 chunks | Sourced from open medical textbooks + guidelines |
| Drug Database | Anaesthetic agents, analgesics, muscle relaxants, vasopressors, emergency drugs — doses, interactions, max doses, timing | ~2,000 drug entries | Structured JSON with calculable dose ranges |

### RAG Pipeline

```
User Query
    → Embedding (NVIDIA NV-Embed-v2 via NIM)
    → Qdrant Vector Search (top-K relevant chunks)
    → Reranker (NVIDIA NV-RerankQA via NIM, or Cohere Rerank)
    → Context Window assembly
    → LLM generates response with citations
```

**Reranker:** Use NVIDIA NV-RerankQA (free via NIM) or Cohere Rerank (via OpenRouter) to improve retrieval precision for clinical queries.

### NVIDIA Clara — Scholar's Pre-Operative Imaging

NVIDIA Clara is a healthcare AI platform for medical imaging and diagnostics. It provides an integration layer for the Scholar Agent's pre-operative imaging analysis.

| Aspect | Detail |
|---|---|
| What it is | Healthcare AI platform for medical imaging diagnostics |
| Relevance | Scholar Agent uses it to analyse pre-op CT/MRI/X-ray data |
| MONAI compatibility | Our MONAI models are Clara-compatible — hospitals running Clara infrastructure can integrate directly |
| Scope | Pre-operative imaging analysis only — NOT for live surgical video |
| Why the distinction matters | Clara = imaging diagnostics; Holoscan = real-time intraoperative video (separate domains, separate tools) |
| Hospital integration | If a hospital already runs Clara, the Scholar's imaging pipeline can hook directly into their Clara instance |
| License | NVIDIA (free via Inception) |

**Scholar + Clara workflow (pre-operative):**
1. Surgeon uploads pre-op CT/MRI via web portal (T-60 min)
2. Scholar Agent parses DICOM files via Cornerstone.js viewer
3. Clara-compatible MONAI models run anatomy segmentation on pre-op scans
4. Scholar synthesises imaging findings + patient history + risk scores
5. Master Pre-Operative Analysis delivered to theatre display before incision

---

## 14. Pharmacokinetic Engine

This is **pure mathematics, not AI** — deterministic pharmacokinetic models that run on CPU with no GPU requirement and no LLM involvement.

| Aspect | Detail |
|---|---|
| Language | Python (NumPy + SciPy) |
| Models implemented | Marsh (propofol), Schnider (propofol), Minto (remifentanil), Eleveld (propofol, general-purpose) |
| What it calculates | Plasma concentration, effect-site concentration, time to emergence, recommended infusion rates |
| Input | Patient weight, height, age, lean body mass (from Scholar), drug doses + times (from Pharmacist agent) |
| Output | Real-time concentration curves on Theatre Display; verbal alerts via Pharmacist agent's Conversational Path |
| Open source reference | PyTCI library: `github.com/opentiva/pytci` (Python TCI pharmacokinetic models) |
| License | MIT |

**Pharmacist agent integration:**
- Listens continuously on anaesthesiologist's audio channel (Conversational Path, always-on mode)
- Logs each drug administration event with timestamp and dose
- Runs PK model in real-time, updating plasma concentration curves every 30 seconds
- Speaks alerts via Fish Speech TTS on the anaesthesiologist's neckband channel when thresholds are approached

---

## 15. Theatre Display & Frontend

### Web Application on Smart TV

| Aspect | Detail |
|---|---|
| Technology | Next.js 14+ (React) |
| Rendering | Client-side rendering for real-time updates |
| Deployment | Runs in Chromium browser on Smart TV, laptop, or Android tablet |
| Connection | Joins the LiveKit room as a subscriber — receives display commands from AI agents |
| Design | Dark theme, high contrast, theatre-optimised, large text (readable from 3m+ distance) |

### Display Components

| Component | Technology |
|---|---|
| Vital signs dashboard | Real-time charts using Recharts / Chart.js, fed by Monitor Agent via Holoscan output |
| Anatomy overlays | Three.js for 3D anatomy rendering; SVG for 2D diagrams |
| Marma diagrams | Pre-rendered SVGs with Sanskrit labels, interactive highlights |
| Surgical timeline | Custom React timeline component |
| Drug record | Real-time table updated by Pharmacist Agent |
| PK curves | Recharts line charts showing plasma/effect-site concentration |
| Shloka display | Devanagari text rendering with transliteration |
| Instrument count | Count display with status indicators (green/amber/red) |
| Patient imaging | DICOM viewer using Cornerstone.js (open source, MIT) |
| Alert feed | Real-time feed of all Critical Path alerts with timestamps |

### DICOM Viewer: Cornerstone.js

| Aspect | Detail |
|---|---|
| Tool | Cornerstone.js + OHIF Viewer |
| GitHub | `github.com/cornerstonejs/cornerstone3D` |
| License | MIT |
| What | View patient MRI/CT/X-ray directly in the Theatre Display |
| Why | Open source, browser-based, supports DICOM standard |

---

## 16. Backend & API Layer

| Component | Technology | Purpose |
|---|---|---|
| API Server | FastAPI (Python) | REST + WebSocket APIs for all services |
| Task Queue | Celery + Redis | Async processing for Scholar analysis, Chronicler reports |
| Session State | Redis | In-memory state for active surgery session — full contextual memory |
| Database | PostgreSQL | Persistent storage for surgeon profiles, surgery history |
| File Storage | MinIO (self-hosted S3-compatible) | Patient files, reports, session recordings |
| Auth | JWT + API keys | Surgeon auth, session security |
| Containers | Docker + Docker Compose | All services containerised for reproducible deployment |
| Orchestration | Docker Compose (Phase 1–2), Kubernetes (Phase 3+) | Single-command deployment of entire stack on GPU instance |

All open source. All free.

---

## 17. Data Storage & Session Management

| Data Type | Storage | Encryption | Retention |
|---|---|---|---|
| Active surgery session state | Redis (in-memory on GPU instance) | In-transit (TLS) | Deleted when GPU instance terminates |
| Surgery session archive | PostgreSQL + MinIO (persistent cloud) | AES-256 at rest | Surgeon-controlled retention |
| Surgeon Profile | PostgreSQL (encrypted columns) | AES-256 | Permanent until surgeon deletes |
| Pre-op analysis documents | MinIO | AES-256 at rest | Linked to patient record |
| Video recordings (Teaching Mode) | MinIO / Object storage | AES-256 at rest | Consent-governed |
| Holoscan de-identified frames | Separate MinIO bucket | AES-256 at rest | Consent-governed research use |
| Shalyatantra corpus | Qdrant + PostgreSQL | Not patient data | Permanent |

---

## 18. Android Companion App

### Tech Stack

| Layer | Technology |
|---|---|
| Language | Kotlin |
| UI Framework | Jetpack Compose |
| Camera | CameraX (Android Jetpack) |
| WebRTC | LiveKit Android SDK (`io.livekit:livekit-android`) |
| Bluetooth Audio | Android AudioManager + Bluetooth A2DP/HFP APIs |
| Background Service | Foreground Service (keeps camera streaming during screen-off) |
| Networking | OkHttp + Retrofit for REST APIs |
| Local Storage | Room Database (session metadata cache) |
| Min Android Version | Android 10 (API 29) |
| Distribution | APK sideload (Phase 1), Google Play (Phase 3+) |

### App Modes

| Mode | Function |
|---|---|
| Monitor Camera | Streams rear camera to LiveKit room; auto-aims at patient monitor |
| Overhead Camera | Streams rear camera; wide-angle mode if available |
| Surgeon Camera | Streams rear camera + neckband mic audio; highest priority stream |
| Display Mode | Turns phone/tablet into a Theatre Display (receives display commands) |

---

## 19. NVIDIA Programme Benefits Integration

ShalyaMitra is accepted into both **NVIDIA Inception** and **NVIDIA Digital Health Programme**. Here is how every free benefit is maximised:

| Benefit | How We Use It | Value |
|---|---|---|
| Free DLI courses | Train team on NeMo (ASR fine-tuning), MONAI (medical vision), CUDA optimisation, Holoscan development | ~$5K–$10K saved in training |
| NVIDIA NIM | Self-host Nemotron 3 Super and NV-Embed with optimised inference containers | Eliminates need for vLLM setup; production-grade serving |
| NVIDIA NeMo | Fine-tune Parakeet TDT on surgical speech data; powers Riva ASR under the hood | Best medical ASR pipeline, free framework |
| NVIDIA MONAI | Pre-trained surgical segmentation models; runs as native Holoscan operator | Free medical vision framework, zero integration overhead |
| **NVIDIA Riva** | **Production speech pipeline — ASR + TTS + keyword spotting in one container** | **Eliminates months of custom speech integration; TensorRT-optimised** |
| **NVIDIA Holoscan SDK** | **Medical-grade surgical video processing — parallel camera graphs, GPU Direct, SaMD-ready** | **~60% reduction in vision pipeline dev time; pre-built surgical reference apps** |
| **NVIDIA Clara** | **Pre-op imaging analysis for Scholar Agent; hospital Clara infrastructure compatibility** | **DICOM AI integration without custom pipeline development** |
| NemoClaw | Enterprise-grade agentic orchestration with security guardrails, audit logging | Free agentic infrastructure with medical-grade governance |
| ai.nvidia.com credits | Use NIM API endpoints for development/testing before self-hosting | Free API calls during development |
| DGX Cloud credits | Run surgery sessions at zero marginal cost during validation period | Zero GPU cost for first 6–12 months of clinical validation |
| Preferred GPU pricing | Discounts on NVIDIA hardware if we build edge devices | Future hardware cost reduction |
| VC network (Inception Capital Connect) | Fundraising connections when ready for Series A | Investor pipeline |
| Co-marketing | NVIDIA case study / newsletter feature once product launches | Brand credibility |
| Healthcare Alliance | Connections to GE Healthcare, hospital networks | Go-to-market partnerships |

### NemoClaw Stack (What We Get Free from NVIDIA)

```
NemoClaw = OpenClaw        (agent runtime)
         + OpenShell        (sandboxed execution)
         + Nemotron         (local LLM — The Voice, The Oracle)
         + NIM              (inference serving)
         + NeMo             (model training)
         + MONAI            (medical vision — as Holoscan operators)
         + NV-Embed         (embeddings)
         + Riva             (speech — ASR + TTS + KWS)
         + Holoscan SDK     (surgical video pipeline)
         + Clara            (pre-op medical imaging)
         + Privacy Routing  (local vs cloud model selection)
```

This is essentially our **entire agentic + LLM + speech + medical vision + surgical video + pre-op imaging infrastructure — free via NVIDIA programmes.**

---

## 20. Cost Analysis Per Surgery

### Engineering Efficiency Gains (One-Time Benefits)

The adoption of Riva and Holoscan does not change per-surgery costs (they run on the same H100 instance), but delivers significant engineering time savings:

| Tool | Engineering Time Reduction | Basis |
|---|---|---|
| NVIDIA Holoscan | ~60% reduction in vision pipeline dev time | Pre-built surgical video reference apps; built-in MONAI operator; SaMD-ready pipeline structure |
| NVIDIA Riva | ~70% reduction in speech pipeline integration time | Unified ASR + TTS + KWS container; TensorRT already optimised; replaces 3 separate integration efforts |
| Combined | ~2–3 months engineering time saved | Engineering hours redirected to clinical intelligence and product differentiation |

Both tools are **free via NVIDIA programmes** — zero additional cost, significant time benefit.

### Scenario: Standard 2-Hour Surgery

| Cost Item | Provider | Cost |
|---|---|---|
| GPU compute (H100 × 2.5 hrs including setup/teardown) | Nebius | $7.38 (~₹615) |
| OpenRouter API calls (Scholar pre-op + Consultant + Chronicler) | OpenRouter | $0.50–$2.00 (₹40–₹165) |
| LiveKit server | Self-hosted on GPU | $0 (included in GPU cost) |
| All AI models (Riva, Holoscan, LLM, Fish Speech) | Self-hosted on GPU | $0 (included in GPU cost) |
| Android app | Self-built | $0 |
| Theatre Display web app | Self-built | $0 |
| **Total per surgery** | | **$8–$10 (₹650–₹830)** |

### Scenario: Extended 4-Hour Surgery

| Cost Item | Cost |
|---|---|
| GPU compute (H100 × 4.5 hrs) | $13.28 (~₹1,107) |
| OpenRouter API calls | $1–$3 (₹80–₹250) |
| **Total per surgery** | **$14–$16 (₹1,150–₹1,350)** |

### Monthly Cost Projections (Per Surgeon)

| Surgeries/Month | GPU Cost | API Cost | Total Monthly |
|---|---|---|---|
| 10 surgeries | ₹6,150 | ₹1,650 | ~₹7,800 |
| 20 surgeries | ₹12,300 | ₹3,300 | ~₹15,600 |
| 40 surgeries | ₹24,600 | ₹6,600 | ~₹31,200 |

### Hardware Costs (One-Time, Per Theatre)

| Item | Cost |
|---|---|
| 2× Android phones (if not using existing) | ₹10K–₹20K |
| 1× GoPro Hero 13 + head mount + capture card | ₹35K–₹45K |
| 2× Bluetooth neckbands | ₹6K–₹30K |
| 1× Smart TV / large monitor (if not existing) | ₹20K–₹40K |
| **Total one-time hardware** | **₹70K–₹1.35L** |

Compare to the original blueprint estimate of ₹2.35L–₹5.05L for edge compute setup. **Hardware costs reduced by 60–70%.**

---

## 21. Complete Stack Summary Table

| Layer | Component | Technology | License | Cost |
|---|---|---|---|---|
| Camera (Monitor) | Android Phone | CameraX + LiveKit SDK | — | ₹0–₹10K |
| Camera (Overhead) | Android Phone | CameraX + LiveKit SDK | — | ₹0–₹10K |
| Camera (Surgeon) | Android/GoPro/Dedicated | LiveKit SDK / HDMI capture | — | ₹0–₹80K |
| Audio Input | BT Neckband | Bluetooth HFP/A2DP | — | ₹3K–₹15K each |
| Display | Smart TV + Web App | Next.js + Chromium | MIT | ₹20K–₹40K |
| Real-Time Transport | WebRTC Server | LiveKit (self-hosted) | Apache 2.0 | Free |
| GPU Compute | Surgery session | Nebius / Lightning AI (H100) | Pay-per-hour | ~₹650/surgery |
| **Vision Pipeline Framework** | **Surgical video processing** | **NVIDIA Holoscan SDK 3.0** | **Apache 2.0** | **Free** |
| Vision (Monitor) | Vital sign reading | YOLOv11 + PaddleOCR (Holoscan operators) | Apache 2.0 | Free |
| Vision (Counting) | Instrument/swab tracking | YOLOv11 + SAM2 + ByteTrack (Holoscan operators) | Apache 2.0 | Free |
| Vision (Anatomy) | Surgical structure recognition | RASO + MONAI + SAM2 (Holoscan operators) | Apache 2.0 | Free |
| **Speech Pipeline** | **Unified ASR + TTS + KWS** | **NVIDIA Riva** | **NVIDIA (Inception)** | **Free** |
| **Wake Word Detection** | **"Nael" keyword spotting** | **Riva KWS (primary) + OpenWakeWord (fallback)** | **NVIDIA / MIT** | **Free** |
| STT (Fallback) | Open-source ASR | NVIDIA Parakeet TDT 0.6B v2 | CC-BY-4.0 | Free |
| STT (Fallback) | Multilingual | Whisper Large V3 Turbo | MIT | Free |
| TTS (Conversational) | Multiple voice profiles | Fish Speech 1.5 | Apache 2.0 | Free |
| TTS (Critical Alerts) | Fast one-line alerts | Piper TTS | MIT | Free |
| LLM (Real-time) | Voice reasoning loop | Nemotron 3 Super (via NIM) | NVIDIA Open | Free (NIM) |
| LLM (Deep reasoning) | Scholar, Consultant, Chronicler | GPT-5.4 / Claude via OpenRouter | Pay-per-token | ~₹165/surgery |
| LLM (Fast fallback) | Voice loop backup | Inception Mercury 2 via OpenRouter | Pay-per-token | Variable |
| Agentic Framework | Multi-agent orchestration | OpenClaw + NemoClaw | MIT / NVIDIA | Free |
| Vector Database | Knowledge retrieval | Qdrant | Apache 2.0 | Free |
| Embeddings | Text embeddings | NVIDIA NV-Embed-v2 (via NIM) | NVIDIA | Free |
| PK Engine | Pharmacokinetic modelling | PyTCI + custom Python | MIT | Free |
| **Pre-Op Imaging** | **Scholar imaging analysis** | **NVIDIA Clara (compatibility layer)** | **NVIDIA** | **Free** |
| **Future Audio-to-Audio** | **Next-gen speech engine** | **Moshi by Kyutai (roadmap)** | **Apache 2.0 / CC-BY-4.0** | **Free** |
| Backend | API server | FastAPI + Redis + PostgreSQL | MIT/BSD | Free |
| Storage | Files & recordings | MinIO (self-hosted S3) | AGPL-3.0 | Free |
| Mobile App | Camera + audio companion | Kotlin + Jetpack Compose + LiveKit | Apache 2.0 | Free |
| ASR Fine-tuning | Medical vocabulary training | NVIDIA NeMo Framework | Apache 2.0 | Free |
| DICOM Viewer | Patient imaging display | Cornerstone.js + OHIF | MIT | Free |

---

## 22. Key Open Source Repositories — Quick Reference

| Repo | URL | What We Use It For |
|---|---|---|
| LiveKit | `github.com/livekit/livekit` | All real-time audio/video transport |
| LiveKit Agents | `github.com/livekit/agents` | Python AI agent framework |
| **NVIDIA Holoscan SDK** | **`github.com/nvidia-holoscan/holoscan-sdk`** | **Surgical video processing framework — vision pipeline container** |
| **NVIDIA Riva (client)** | **`github.com/nvidia-riva`** | **Speech AI SDK — ASR + TTS + keyword spotting** |
| Ultralytics YOLO | `github.com/ultralytics/ultralytics` | Object detection (as Holoscan operators) |
| SAM 2 | `github.com/facebookresearch/sam2` | Segmentation for instruments + anatomy (as Holoscan operators) |
| PaddleOCR | `github.com/PaddlePaddle/PaddleOCR` | Reading monitor vital signs (as Holoscan operator) |
| OpenCV | `github.com/opencv/opencv` | Image preprocessing (built into Holoscan) |
| NVIDIA NeMo | `github.com/NVIDIA/NeMo` | ASR training (Parakeet + Riva fine-tuning) |
| NVIDIA MONAI | `github.com/Project-MONAI/MONAI` | Medical image segmentation (native Holoscan operator) |
| Fish Speech | `github.com/fishaudio/fish-speech` | Multi-voice TTS (Conversational Path) |
| Piper TTS | `github.com/rhasspy/piper` | Fast alert voice synthesis (Critical Alert Path) |
| Coqui TTS (Idiap fork) | `github.com/idiap/coqui-ai-TTS` | XTTS-v2 fallback TTS |
| **OpenWakeWord** | **`github.com/dscripka/openWakeWord`** | **Wake word detection fallback ("Nael")** |
| **Moshi** | **`github.com/kyutai-labs/moshi`** | **Future audio-to-audio model (roadmap)** |
| **Mini-Omni** | **`github.com/gpt-omni/mini-omni`** | **Alternative S2S model (evaluation)** |
| OpenClaw | `github.com/openclaw` | Agentic orchestration runtime |
| Qdrant | `github.com/qdrant/qdrant` | Vector database for RAG |
| PyTCI | `github.com/opentiva/pytci` | Pharmacokinetic modelling |
| Cornerstone.js | `github.com/cornerstonejs/cornerstone3D` | DICOM medical image viewer |
| WhisperLive | `github.com/collabora/WhisperLive` | Streaming Whisper wrapper (fallback STT) |
| Endoscapes Dataset | `github.com/CAMMA-public/Endoscapes` | Surgical instrument training data |
| RASO | Search arxiv for latest release | Surgical object recognition |

---

## 23. Deployment Sequence — How a Surgery Session Works

### Step 1 — Pre-Surgery (T-60 min to T-30 min)

- Surgeon uploads patient files via web portal
- Scholar Agent runs on OpenRouter (Claude/GPT) — generates Master Pre-Operative Analysis
- NVIDIA Clara-compatible MONAI models analyse pre-op CT/MRI/X-ray scans
- Risk scores calculated, drug interactions mapped, Ayurvedic assessment if applicable
- Pre-generated alert audio files loaded into Critical Alert Path cache

### Step 2 — Session Spin-Up (T-15 min)

- System provisions H100 GPU on Nebius/Lightning AI
- Docker Compose deploys: LiveKit Server, NVIDIA Riva container, NVIDIA Holoscan runtime, NIM (Nemotron), all agents, Redis, FastAPI
- Holoscan application graphs initialised for all 3 camera feeds
- Riva KWS begins listening for "Nael" wake word
- Health checks confirm all services running
- LiveKit Room created for this surgery session

### Step 3 — Device Connection (T-5 min)

- Surgeon opens ShalyaMitra app on 3 Android phones → each joins LiveKit room
- Surgeon pairs neckband → audio routed through app to LiveKit
- Theatre Display (Smart TV) loads web app → joins LiveKit room
- Holoscan graphs confirm video stream ingestion from all 3 cameras
- System announces: *"All systems connected. ShalyaMitra is live. Nael is listening."*

### Step 4 — Surgery Active (1–3+ hours)

- All 3 Holoscan camera graphs processing at ~37ms end-to-end latency
- Riva KWS listening continuously for "Nael" on surgeon's audio channel
- Critical Alert Path operational — direct classifier-to-audio, no LLM required
- Conversational Path available — surgeon says "Nael" to query intelligence layer
- Pharmacist Agent listening on anaesthesiologist's channel
- All agents maintaining persistent memory of entire session via Redis
- Oracle, Consultant, Devil's Advocate available on demand via Conversational Path

### Step 5 — Closure & Handover (T+0 to T+15 min)

- Sentinel confirms instrument/swab count (Critical Alert Path announces result)
- Chronicler generates Intraoperative Chronicle + Handover Brief via OpenRouter
- Reports saved to persistent MinIO storage
- Session archived, Riva container gracefully shut down

### Step 6 — Teardown (T+15 min)

- GPU instance terminated
- Billing stops
- All session data encrypted and archived to persistent cloud storage
- Holoscan graph metrics logged for pipeline performance analysis

---

## 24. Future Roadmap — Audio-to-Audio Models

### Moshi by Kyutai Labs

As the surgical AI field matures, the cascaded pipeline (ASR → LLM → TTS) will eventually give way to **end-to-end audio-to-audio models** that process voice input directly and generate voice output without a text intermediate. This is the direction ShalyaMitra will move as the technology matures.

| Aspect | Detail |
|---|---|
| Model | Moshi |
| Developer | Kyutai Labs |
| GitHub | `github.com/kyutai-labs/moshi` |
| License | Apache 2.0 (model weights: CC-BY-4.0) |
| Key capability | End-to-end speech-to-speech LLM — no text intermediate |
| Full-duplex | Can listen while speaking — handles interruptions naturally |
| Current limitation | Not trained on medical data — cannot be trusted for drug dosing, anatomy, or clinical reasoning today |

### Phased Adoption Plan

**Phase 1 — Current Production (Cascaded Pipeline):**
- Riva ASR → Nemotron LLM → Fish Speech TTS
- Auditable: every step is logged as text
- Medically reliable: LLM operates on verified medical knowledge
- Regulatory-friendly: outputs are text-validated before synthesis

**Phase 2 — Moshi for Non-Critical Interactions:**
- Deploy Moshi for low-stakes conversational interactions: timeline queries, general status, casual Oracle requests
- Keep cascaded pipeline for all clinical reasoning, drug-related, and alert-critical interactions
- Parallel deployment — surgeon can experience both paths

**Phase 3 — ShalyaMitra Voice Engine:**
- Fine-tune Moshi on a corpus of surgical conversations collected during Phase 1 and Phase 2 validation
- Create "ShalyaMitra Voice Engine" — a native audio-to-audio surgical companion with a consistent identity
- Voice Engine handles Conversational Path; cascaded pipeline remains as auditable fallback

### Alternative Speech-to-Speech Models for Evaluation

| Model | Developer | License | Notes |
|---|---|---|---|
| Moshi | Kyutai Labs | Apache 2.0 / CC-BY-4.0 | Primary evaluation candidate |
| Mini-Omni | gpt-omni | MIT | Lightweight S2S model — `github.com/gpt-omni/mini-omni` |
| GLM-4-Voice | Zhipu AI | Apache 2.0 | Strong multilingual S2S capability (English + Chinese; evaluate for Hindi) |

**Evaluation criteria for surgical use:**
1. Medical vocabulary accuracy — does it hallucinate drug names or dosages?
2. Interruption handling — can the surgeon cut off a response mid-sentence?
3. Latency — is it faster than the current cascaded pipeline?
4. Auditability — can we log and review what was said and why?
5. Regulatory compatibility — can we demonstrate a clear reasoning trail for CDSCO?

---

*ShalyaMitra Tech Stack Blueprint v2.0*
*Built for surgeons, not for servers. Every rupee spent serves the patient on the table.*
*NVIDIA Inception Programme Member | NVIDIA Digital Health Programme Member*
