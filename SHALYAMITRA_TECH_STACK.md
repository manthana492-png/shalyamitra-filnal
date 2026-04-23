ShalyaMitra — Production Tech Stack & Infrastructure Blueprint
Every technology choice serves one truth: the surgeon must never break flow. Every cost decision serves one reality: this must work in a district hospital, not just a tertiary centre.

Table of Contents

Architecture Overview

Camera & Video Infrastructure

Audio & Voice Infrastructure

Real-Time Communication Layer

GPU Compute Infrastructure

AI Model Stack — Speech

AI Model Stack — Vision

AI Model Stack — Intelligence (LLMs)

AI Model Stack — Voice Synthesis (TTS)

Agentic Orchestration Layer

Knowledge & RAG Infrastructure

Pharmacokinetic Engine

Theatre Display & Frontend

Backend & API Layer

Data Storage & Session Management

Android Companion App

NVIDIA Programme Benefits Integration

Cost Analysis Per Surgery

Complete Stack Summary Table
1. Architecture Overview
┌──────────────────────────── OPERATING THEATRE ─────────────────────────────┐
│                                                                            │
│  📱 Android Phone 1 ───── Monitor Camera (WebRTC via LiveKit)              │
│  📱 Android Phone 2 ───── Overhead Camera (WebRTC via LiveKit)             │
│  📷 GoPro / Phone 3 ──── Surgeon Head Camera (WebRTC via LiveKit)          │
│                                                                            │
│  🎧 BT Neckband 1 ─────── Surgeon Voice (audio stream via LiveKit)         │
│  🎧 BT Neckband 2 ─────── Anaesthesiologist Voice (audio stream)           │
│                                                                            │
│  📺 Smart TV / Monitor ── Theatre Display (Web App via Chromium)           │
│  🔊 BT Speakers ────────── AI Voice Output (distinct voice profiles)       │
│                                                                            │
└───────────────────────────────── │ ────────────────────────────────────────┘
                                  │ WebRTC (LiveKit)
                                  │ via Local Wi-Fi / Hospital Network
                                  ▼
┌──────────────────── CLOUD GPU (Surgery Session) ──────────────────────────┐
│                                                                            │
│  Lightning AI / Nebius — H100 GPU (1–3 hours per surgery)                  │
│                                                                            │
│  ┌── LiveKit Server (self-hosted) ── receives all audio + video ────────┐  │
│  │                                                                      │  │
│  │  ┌── VISION PIPELINE ────────────────────────────────────────────┐   │  │
│  │  │  Camera 1 → YOLOv11 + PaddleOCR  (Monitor Vital Reading)    │   │  │
│  │  │  Camera 2 → YOLOv11 + SAM2       (Instrument/Swab Counting) │   │  │
│  │  │  Camera 3 → RASO + MONAI + SAM2  (Anatomy Recognition)      │   │  │
│  │  │           → Bleeding Classifier   (Haemorrhage Sentinel)     │   │  │
│  │  │           → Retractor Detector    (Tissue Stress Monitor)    │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌── AUDIO PIPELINE ────────────────────────────────────────────┐   │  │
│  │  │  Surgeon Mic → Parakeet TDT / Whisper (STT)                  │   │  │
│  │  │             → Intent Classifier (AI query vs team talk)      │   │  │
│  │  │  Anaesth Mic → Parakeet TDT / Whisper (STT)                  │   │  │
│  │  │             → Pharmacist Channel (separate voice)            │   │  │
│  │  │  AI Response → Fish Speech / Piper (TTS, 3+ voice profiles)  │   │  │
│  │  │             → LiveKit audio track → BT neckband / speaker    │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌── INTELLIGENCE LAYER (OpenClaw + NemoClaw Agents) ───────────────────┐  │
│  │                                                                      │  │
│  │  ┌─ The Voice Agent ──────── Nemotron 3 Super (via NIM) ──────────┐  │  │
│  │  │  Listens → Reasons → Speaks → Commands Display                 │  │  │
│  │  │  Queries: Scholar, Oracle, Consultant, Devil's Advocate         │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌─ The Pharmacist Agent ── Drug DB + PyTCI PK Engine ────────────┐  │  │
│  │  │  Listens (anaesth channel) → Logs drugs → Calculates doses     │  │  │
│  │  │  Runs: Marsh/Schnider/Minto PK models in real-time             │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌─ The Scholar Agent ───── Pre-op RAG + Risk Scoring ────────────┐  │  │
│  │  │  Pre-surgery: analyses all patient docs via OpenRouter LLM     │  │  │
│  │  │  During surgery: silent reference queried by other agents       │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌─ The Oracle Agent ────── Qdrant RAG over Shalyatantra Corpus ──┐  │  │
│  │  │  Sushruta Samhita + Marma DB + Classical Texts                  │  │  │
│  │  │  Bidirectional: Classical↔Modern knowledge mapping              │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌─ Devil's Advocate ────── Cross-Agent Conflict Detector ────────┐  │  │
│  │  │  Monitors: Scholar flags × Pharmacist state × Monitor trends   │  │  │
│  │  │  Speaks once if conflict detected at decision point             │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌─ The Chronicler Agent ── Session Logger + Report Generator ────┐  │  │
│  │  │  Logs all events, alerts, decisions → Generates handover brief │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌── DATA LAYER ────────────────────────────────────────────────────────┐  │
│  │  Redis (session state + contextual memory)                           │  │
│  │  Qdrant (vector DB — Shalyatantra + Medical Knowledge embeddings)    │  │
│  │  PostgreSQL (surgeon profiles, surgery history)                      │  │
│  │  MinIO (patient files, reports, recordings)                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS (post-surgery only)
                                  ▼
┌──────────────────── CLOUD SERVICES (Pre/Post Operative) ──────────────────┐
│                                                                            │
│  OpenRouter API ─── Scholar (Claude/GPT for pre-op deep analysis)         │
│                 ─── Consultant (on-demand complex medical queries)         │
│                 ─── Chronicler (post-op report generation)                 │
│                                                                            │
│  Persistent Storage ─── Encrypted surgery archives                        │
│                     ─── Surgeon Profile cloud backup                      │
│                     ─── Research Mode anonymised data (consent-governed)   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
Continue
[ignoring loop detection]

Here's the complete tech stack document. Copy-paste everything below:

ShalyaMitra — Production Tech Stack & Infrastructure Blueprint
Every technology choice serves one truth: the surgeon must never break flow. Every cost decision serves one reality: this must work in a district hospital, not just a tertiary centre.

Document Date: April 2026

1. Architecture Philosophy — Smart & Lean
ShalyaMitra uses a cloud-GPU-during-surgery model instead of expensive in-theatre edge hardware. The key insight:

Surgery lasts 1–3 hours (rarely up to 6–8)
We spin up a single H100 GPU instance on Lightning AI or Nebius for the duration of the surgery
All cameras (Android phones + surgeon head cam) stream via WebRTC through LiveKit to this GPU
All AI inference (vision, voice, LLM reasoning, TTS) runs on this one GPU session
When surgery ends, the GPU is released — you pay only for surgery hours
Pre/post-operative work (Scholar analysis, Chronicler reports) runs on cheaper CPU instances or OpenRouter
Cost per surgery: approximately $3–$9 (₹250–₹750) for GPU compute. This is radically cheaper than any ₹3L+ edge server setup.

2. Camera & Video Infrastructure
The Smart Approach: Android Phones as Cameras
Instead of dedicated surgical cameras costing ₹50K–₹2L each, we use Android phones for 2 of 3 cameras, and support both phone + dedicated camera for the surgeon's head.

Camera Role	Hardware	Mount	Estimated Cost
Monitor Camera (Eye Two)	Any Android phone (1080p+, 2020 or newer)	Tripod/clamp aimed at patient monitor	₹0 (existing phone) or ₹5K–₹10K
Overhead Camera (Eye Three / Sentinel)	Any Android phone (wide-angle preferred)	Ceiling/boom mount or IV pole clamp	₹0 (existing phone) or ₹5K–₹10K
Surgeon Head Camera (Eye One)	Option A: Android phone in head mount harness	Surgical headband phone holder	₹500–₹2K for mount
Option B: GoPro Hero 12/13 with head strap	GoPro head strap mount, Linear lens mode	₹25K–₹35K
Option C: Insta360 GO 3S (tiny, magnetic clip)	Clips to surgical loupes or headband	₹20K–₹30K
Option D: Dedicated surgical camera (Zowietek/Oppila)	Integrated headlamp-style mount	₹40K–₹80K
Surgeon Head Camera — Detailed Options
For MVP / Phase 1: Android Phone

Mount phone to surgical headband using a lightweight phone head mount (₹500 on Amazon)
Use rear camera for best quality
Stream via the same ShalyaMitra Android app
Drawback: heavier than dedicated cameras, may shift during surgery
For Phase 2+: GoPro Hero 13 Black

Best balance of quality, size, weight, and ecosystem
Use Linear lens mode (removes fisheye distortion)
Connect via HDMI out → USB capture card (Elgato Cam Link 4K, ₹8K) → laptop running streaming software
OR use GoPro Labs firmware for direct RTMP streaming to our server
Power via USB-C for unlimited duration
Head strap mount: ₹1.5K (official GoPro accessory)
For Phase 3+: Dedicated Surgical Camera

Zowietek or similar NDI-based surgical cameras
Sub-66ms latency, designed for OR environments
Integrates directly into LiveKit via NDI-to-WebRTC bridge
Android Phone Camera App — What We Build
A custom ShalyaMitra Companion App (Android) that:

Opens the rear camera in 1080p / 30fps mode
Streams video via WebRTC to our LiveKit server on the GPU instance
Also captures and streams microphone audio (for the neckband-connected phones)
Shows a simple status UI: "Connected to ShalyaMitra ✓", battery %, connection quality
Supports role selection: "Monitor Camera", "Overhead Camera", "Surgeon Camera"
Auto-reconnects on network interruption
Keeps screen on, prevents sleep, optimises for low battery consumption
Tech stack for the app:

Language: Kotlin
WebRTC SDK: LiveKit Android SDK (open source, Apache 2.0)
Camera API: CameraX (Android Jetpack)
Streaming: LiveKit Room API handles all WebRTC complexity
Build: Gradle, target Android 10+ (API 29+)
3. Audio & Voice Infrastructure
Bluetooth Neckband Setup
User	Hardware	Purpose	Estimated Cost
Surgeon	Jabra Evolve2 65 / Poly Voyager Free 60+ or any good BT neckband with ANC	Voice input to AI + AI voice output in ear	₹3K–₹15K
Anaesthesiologist	Same or similar	Separate voice channel to The Pharmacist	₹3K–₹15K
Key requirements for the neckband:

Bluetooth 5.0+ with low-latency codec (aptX Low Latency or LC3)
AI noise cancellation / ENC — OR environments have cautery hums, suction noise, monitor alarms
Multi-point connection — connects to the Android phone running ShalyaMitra app
Minimum 8-hour battery — must last through extended procedures
Comfortable for 4+ hours — lightweight, no ear fatigue
Audio flow:

Surgeon speaks → neckband mic captures → Bluetooth to Android phone
Android phone streams audio via LiveKit WebRTC to GPU server
GPU server processes speech (Whisper/Parakeet STT) → LLM reasoning → TTS response
TTS audio streams back via LiveKit WebRTC to Android phone
Android phone plays audio via Bluetooth to neckband earpiece
Surgeon hears AI response in their ear
Latency target: Full loop (speech → AI response → audio in ear) under 2 seconds. Achievable with:

LiveKit WebRTC: ~100–200ms round trip
Whisper/Parakeet STT: ~200–400ms
LLM inference (fast model): ~300–500ms
TTS generation (streaming): ~200–300ms
Total: ~1–1.5 seconds end-to-end
4. Real-Time Communication Layer — LiveKit
LiveKit is the backbone of all real-time audio and video transport in ShalyaMitra.

Aspect	Detail
What it is	Open-source WebRTC infrastructure (SFU architecture)
License	Apache 2.0 — fully open, no vendor lock-in
Why LiveKit	Purpose-built for real-time AI applications; has native SDKs for Android, Web, Python; supports AI agent rooms
Self-hosted	We deploy LiveKit Server on the same GPU instance used for surgery
GitHub	github.com/livekit/livekit
Cost	$0 (self-hosted, open source)
How it works in ShalyaMitra:

When a surgery session starts, we spin up a GPU instance and deploy LiveKit Server on it
A LiveKit "Room" is created for this surgery session
All 3 Android phones (cameras) join the room as video+audio publishers
The surgeon's neckband audio streams through the phone into the room
AI processing agents (Python) join the room as server-side participants
These agents receive video frames and audio chunks in real-time
AI agents publish audio responses back into the room
The Theatre Display (web app) joins the room to receive display commands
Everything is encrypted (DTLS-SRTP, standard WebRTC security)
LiveKit Agents Framework — LiveKit has a Python framework specifically for building AI agents that join rooms:

livekit-agents Python SDK
Supports STT → LLM → TTS pipelines natively
Supports custom vision processing on video tracks
We build each ShalyaMitra pillar as a LiveKit agent
5. GPU Compute Infrastructure
Primary: Lightning AI or Nebius (H100 GPU, pay-per-hour)
Provider	GPU	Price/Hour	3-Hour Surgery Cost
Nebius AI	H100 80GB	$2.95/hr	$8.85 (~₹740)
Lightning AI	H100 80GB	~$3.00–$3.50/hr	$9–$10.50 (~₹750–₹875)
Lightning AI	A100 80GB	~$1.50–$2.00/hr	$4.50–$6 (~₹375–₹500)
Nebius AI	H200 80GB	$3.50/hr	$10.50 (~₹875)
Recommended setup: Nebius H100 at $2.95/hr — best price-performance ratio.

What runs on this single GPU during surgery:

Service	VRAM Estimate	Notes
LiveKit Server	~0.5 GB (CPU-bound)	WebRTC routing, minimal GPU use
Whisper Large V3 Turbo (STT)	~3 GB	Real-time streaming speech recognition
Fish Speech / XTTS-v2 (TTS)	~4 GB	Multiple distinct voice profiles
YOLO v11 (monitor OCR pipeline)	~1 GB	Continuous vital sign reading
YOLO + SAM2 (instrument counting)	~3 GB	Overhead camera processing
Surgical anatomy model (RASO/MONAI)	~4 GB	Head camera structure recognition
Small/Medium LLM (Nemotron/Qwen)	~20–30 GB	Core reasoning, multi-agent orchestration
Pharmacokinetic engine	~0.1 GB (CPU)	Mathematical models, no GPU needed
Total estimated	~35–45 GB	Fits in H100 80GB with room for batch processing
Session lifecycle:

Pre-surgery (T-30 min): Spin up GPU instance, deploy all services, run health checks
Surgery active (1–3 hrs): All AI services running continuously, full contextual memory
Post-surgery (T+15 min): Chronicler generates reports, then GPU instance is terminated
Cost: Only the active hours are billed
Alternative: NVIDIA DGX Cloud (via Inception Programme)
If NVIDIA Inception provides DGX Cloud credits, we can use those for surgery sessions at zero marginal cost during the credit period. This is the ideal scenario for the first 6–12 months of clinical validation.

6. AI Model Stack — Speech (STT)
Primary: NVIDIA Parakeet TDT 0.6B v2
Aspect	Detail
Model	nvidia/parakeet-tdt-0.6b-v2
Source	Hugging Face, NVIDIA NeMo
License	CC-BY-4.0 (commercial use allowed)
Why	Best open-source ASR for medical fine-tuning; low latency; proven in clinical deployments (Heidi Health case study)
Architecture	Token-and-Duration Transducer (TDT) — optimised for streaming
Languages	English primary; can be fine-tuned for Hindi, Sanskrit terms
VRAM	~2–3 GB
Latency	<200ms for streaming chunks
NVIDIA benefit	Part of NeMo framework — free DLI training courses via Inception
Fallback: OpenAI Whisper Large V3 Turbo
Aspect	Detail
Model	openai/whisper-large-v3-turbo
License	MIT (fully open)
Why	Excellent multilingual support out of the box; handles Hindi-English code-switching well
Streaming	Use WhisperLive wrapper for real-time WebSocket streaming
VRAM	~3 GB
Medical Fine-Tuning Plan
Collect surgical audio recordings (with consent) during Phase 1 clinical validation
Build a surgical vocabulary dataset: anatomical terms, drug names, Sanskrit medical terminology, clinical shorthand
Fine-tune Parakeet TDT on this dataset using NVIDIA NeMo framework
Target: <5% WER on surgical speech by Phase 2
7. AI Model Stack — Vision
Camera 1 — Monitor Vital Reading (The Monitor Sentinel)
Component	Tool	Purpose
Object Detection	YOLOv11 (Ultralytics)	Detect and localise monitor screen, identify ROIs for each vital parameter
Image Processing	OpenCV	Perspective correction, contrast enhancement, colour filtering
OCR	PaddleOCR	Extract numeric values from detected regions — HR, BP, SpO₂, EtCO₂, temp
Trend Engine	Custom Python (NumPy/SciPy)	Time-series modelling, rate-of-change calculation, predictive projection
Pipeline: Camera frame → YOLO (detect monitor regions) → OpenCV (rectify) → PaddleOCR (read numbers) → Trend Engine (predict trajectory) → Alert if adverse trend detected

All tools are open source:

YOLOv11: github.com/ultralytics/ultralytics (AGPL-3.0, commercial license available)
PaddleOCR: github.com/PaddlePaddle/PaddleOCR (Apache 2.0)
OpenCV: github.com/opencv/opencv (Apache 2.0)
Camera 2 — Instrument & Swab Counting (The Sentinel)
Component	Tool	Purpose
Object Detection	YOLOv11 (custom trained)	Detect and classify surgical instruments, swabs entering/leaving field
Instance Tracking	ByteTrack / BoT-SORT	Track individual instruments across frames
Segmentation	SAM 2 (Segment Anything Model 2)	Precise object segmentation for instrument identification
Count Logic	Custom Python	Running inventory: instruments in, instruments out, discrepancy detection
SAM 2: github.com/facebookresearch/sam2 (Apache 2.0) — zero-shot segmentation, handles any object type without specific training.

Training plan: Fine-tune YOLOv11 on surgical instrument datasets:

Endoscapes dataset (laparoscopic instruments, open source)
CholecT50 dataset (surgical tool recognition)
Custom dataset collected during Phase 1 clinical validation
Camera 3 — Surgical Anatomy Recognition (The Surgeon's Eye)
Component	Tool	Purpose
Anatomy Segmentation	RASO (Recognize Any Surgical Object)	Open-set surgical object recognition — can identify structures it wasn't explicitly trained on
Medical Segmentation	NVIDIA MONAI + nnU-Net	Pre-trained surgical segmentation models from the MONAI model zoo
Foundation Model	SAM 2 (interactive)	On-demand segmentation when surgeon points and asks "what is that?"
Haemorrhage Detection	Custom CNN classifier	Trained on operative field colour analysis: venous vs arterial vs capillary bleeding patterns
Retraction Tracking	Object detection + timer logic	Detect retractor placement, track duration, alert at physiological thresholds
NVIDIA MONAI: github.com/Project-MONAI/MONAI (Apache 2.0)

Free via NVIDIA Inception programme
Pre-trained bundles available on Hugging Face and NVIDIA NGC
Specifically designed for medical imaging AI
Surgical Datasets for Training:

Dresden Surgical Anatomy Dataset (8 abdominal organs + vessels, pixel-level annotations)
Endoscapes 2025 (laparoscopic anatomy + instruments)
CholecT50 / Cholec80 (surgical workflow + anatomy)
AutoLaparo (hysterectomy anatomy)
8. AI Model Stack — Intelligence (LLMs)
Multi-Model Strategy
We use different models for different pillars, optimised for their specific needs:

Pillar	Model	Source	Why
The Voice (primary reasoning)	NVIDIA Nemotron 3 Super (120B, 12B active MoE)	OpenRouter / Self-hosted via NIM	Extremely fast inference (MoE architecture), medical reasoning capability, NVIDIA ecosystem synergy
The Voice (fast fallback)	Inception Mercury 2	OpenRouter	Diffusion-based parallel token generation — fastest available model for real-time voice loops
The Scholar (pre-op analysis)	Claude Opus / GPT-5.4	OpenRouter	Deep reasoning for complex clinical synthesis — latency not critical (runs pre-surgery)
The Pharmacist (drug calculations)	Nemotron 3 Super + custom PK engine	Self-hosted	Drug safety requires deterministic calculations, not just LLM guessing
The Consultant (medical knowledge)	GPT-5.4 / Claude Opus	OpenRouter	Deepest medical knowledge for complex clinical queries
The Oracle (Shalyatantra)	Fine-tuned Nemotron / Qwen 2.5 72B	Self-hosted with RAG	Must be self-hosted — classical corpus is our proprietary knowledge graph
The Devil's Advocate (safety)	Same as Voice model	Shared instance	Lightweight cross-referencing logic, not a separate model
The Chronicler (documentation)	GPT-5.4 / Claude	OpenRouter	Post-surgery report generation — latency not critical
OpenRouter Integration
Aspect	Detail
API	openrouter.ai/api/v1/chat/completions (OpenAI-compatible)
Key benefit	Single API key to access 300+ models — switch models without code changes
Usage	Scholar (pre-op), Consultant (on-demand queries), Chronicler (post-op)
Cost control	Set per-model spending limits; use cheaper models for routine queries
NOT used for	Real-time voice loop (too much latency via cloud relay) — use self-hosted for that
Self-Hosted LLM on GPU (during surgery)
For the real-time voice loop, we self-host the reasoning model on the same H100:

Aspect	Detail
Model	NVIDIA Nemotron 3 Super 120B (12B active parameters via MoE)
Serving	vLLM or NVIDIA NIM (NVIDIA Inference Microservices)
VRAM	~20–30 GB (quantised to INT4/FP8)
Latency	~200–400ms for short responses (MoE makes this very fast)
Why NIM	Free via NVIDIA Inception; optimised for NVIDIA GPUs; production-ready serving
Alternative	Qwen 2.5 72B (if Nemotron unavailable) — excellent medical reasoning, Apache 2.0 license
NVIDIA NIM: build.nvidia.com — containerised inference microservices, free for Inception members. Pre-optimised for H100/A100. Handles batching, quantisation, and serving automatically.

9. AI Model Stack — Voice Synthesis (TTS)
We need 3 distinct voice profiles (The Voice, Monitor Sentinel, The Sentinel) so the surgical team instantly knows which AI intelligence is speaking.

Primary: Fish Speech 1.5
Aspect	Detail
Model	Fish Speech 1.5
GitHub	github.com/fishaudio/fish-speech
License	Apache 2.0 (commercial use allowed)
Why	State-of-the-art open source TTS; LLM-based Dual-AR architecture; zero-shot voice cloning; streaming output; multilingual (English + Hindi + more)
VRAM	~3–4 GB
Latency	~200–300ms to first audio chunk (streaming)
Voice profiles	Clone 3 distinct voices from short audio samples (10–30 seconds each) — calm surgical assistant, alert/urgent monitor voice, quiet sentinel voice
Fallback: Coqui XTTS-v2
Aspect	Detail
Model	XTTS-v2 (community-maintained fork)
GitHub	github.com/idiap/coqui-ai-TTS (Idiap Research Institute fork)
License	MPL-2.0
Why	Proven, high-quality multilingual TTS; excellent voice cloning; widely deployed
VRAM	~4–5 GB
Ultra-Fast Alternative: Piper TTS
Aspect	Detail
Model	Piper
GitHub	github.com/rhasspy/piper
License	MIT
Why	Runs on CPU, <50ms latency, perfect for short urgent alerts (Haemorrhage Sentinel, Monitor alerts) where speed matters more than naturalness
Use case	Combine with Fish Speech: Piper for critical one-line alerts, Fish Speech for conversational responses
Voice Profile Design
Voice	Character	Technical Approach
The Voice (Pillar I)	Calm, warm, measured surgical companion	Fish Speech — cloned from a professional voice actor sample
Monitor Sentinel (Pillar II-B)	Distinct, clinical, slightly higher pitch — immediately recognisable	Fish Speech — different cloned voice
The Sentinel (Pillar II-C)	Quiet, brief, authoritative	Piper — pre-built voice, speed-optimised
The Pharmacist (Pillar IV)	Precise, clinical, anaesthesia-specialist register	Fish Speech — third distinct voice, routed to anaesthesiologist's neckband only
The Oracle (Pillar VI)	Reverent, measured, scholarly — for reading shlokas	Fish Speech — voice with slower, more deliberate pacing
10. Agentic Orchestration Layer
Primary: OpenClaw + NemoClaw (NVIDIA)
Aspect	Detail
Framework	OpenClaw (open source autonomous agent runtime) + NemoClaw (NVIDIA enterprise governance wrapper)
License	MIT (OpenClaw) + NVIDIA open source
What it does	Provides the agentic backbone — persistent memory, multi-step autonomous workflows, tool execution, inter-agent communication
Why NemoClaw	NVIDIA's enterprise-hardened version with security guardrails, audit logging, RBAC, sandboxed execution via OpenShell — critical for medical use
GPU requirement	Runs on the same GPU instance; uses Ollama or NIM as the LLM backend
NVIDIA benefit	Free via NVIDIA Inception + Digital Health programme; NemoClaw announced at GTC March 2026
How We Use It for ShalyaMitra
Each intelligence pillar is implemented as an OpenClaw agent (a "claw") with:

Its own persistent memory (context of this surgery)
Its own tools (camera feed access, TTS output, display commands)
Its own personality configuration (speech style, alert thresholds)
Communication channels to other agents via the orchestrator
Agent (Claw)	Tools	Memory	Trigger
Voice Agent	STT input, LLM reasoning, TTS output, display commands	Full surgery conversation history	Continuous — always listening
Monitor Agent	Camera 1 video feed, YOLO+OCR pipeline, trend engine	Vital sign time-series for entire surgery	Continuous — triggers on adverse trend
Sentinel Agent	Camera 2 video feed, YOLO+SAM2 counting pipeline	Running instrument/swab inventory	Continuous — triggers at closure
Surgeon Eye Agent	Camera 3 video feed, RASO/MONAI anatomy pipeline	Current surgical phase, identified structures	Continuous — responds to Voice queries
Haemorrhage Agent	Camera 3 video feed, bleeding classifier	Field colour baseline for this surgery	Continuous — triggers on detection
Tissue Stress Agent	Camera 3 video feed, retractor detector + timer	Retractor positions and durations	Continuous — triggers at time threshold
Scholar Agent	Document parsing, risk scoring logic	Pre-op analysis document	Pre-surgery — queried by other agents during surgery
Pharmacist Agent	Drug database, PK engine, dose calculator	Anaesthetic drug log for this surgery	Continuous — listens to anaesthesiologist channel
Consultant Agent	RAG over medical knowledge base, OpenRouter LLM	Query history	On-demand — queried by Voice or Pharmacist
Oracle Agent	RAG over Shalyatantra corpus	Consultation history	On-demand — queried by Voice or Surgeon Eye
Devil's Advocate Agent	Cross-references all other agent states	All current agent states	Triggered at decision points detected by Voice
Chronicler Agent	Reads all agent logs, event timeline	Complete surgery log	Continuous logging — generates reports at closure
Inter-Agent Communication Bus
OpenClaw's built-in messaging system handles inter-agent communication:

Voice Agent detects surgeon asking about anatomy → queries Surgeon Eye Agent + Oracle Agent
Surgeon Eye Agent detects Marma proximity → notifies Oracle Agent + Display
Monitor Agent detects adverse trend → notifies Voice Agent (speaks to surgeon) + Display
Devil's Advocate Agent cross-references Scholar + Pharmacist + Monitor states at every decision point
11. Knowledge & RAG Infrastructure
Vector Database: Qdrant
Aspect	Detail
Tool	Qdrant
GitHub	github.com/qdrant/qdrant
License	Apache 2.0
Why	Fast, production-grade vector search; runs on CPU (no extra GPU needed); excellent filtering
Use	Stores embeddings for all knowledge corpora
Embedding Model: NVIDIA NV-Embed-v2
Aspect	Detail
Model	nvidia/nv-embedqa-e5-v5 or NV-Embed-v2
Why	Top-ranked embedding model; free via NVIDIA NIM; optimised for retrieval
NVIDIA benefit	Free inference via NIM endpoints for Inception members
Knowledge Corpora
Corpus	Content	Size Estimate	Format
Shalyatantra Corpus	Sushruta Samhita (complete), Ashtanga Hridayam, Charaka Samhita (surgical), Sharangadhara Samhita, Vagbhata, Dhanvantari Nighantu	~5,000–10,000 pages	Chunked markdown with shloka IDs, chapter/verse references
Marma Database	All 107 Marmas — location, classification, extent, consequences, protective doctrine, relevant shlokas	~500 entries	Structured JSON with Sanskrit + transliteration + modern anatomy mapping
Medical Knowledge Base	Surgical anatomy, pharmacology, pathology, emergency protocols, complication management	~50,000 chunks	Sourced from open medical textbooks + guidelines
Drug Database	Anaesthetic agents, analgesics, muscle relaxants, vasopressors, emergency drugs — doses, interactions, max doses, timing	~2,000 drug entries	Structured JSON with calculable dose ranges
RAG Pipeline
User Query → Embedding → Qdrant Vector Search → Top-K Relevant Chunks
    → Reranker (Cohere/NV-Rerankqa) → Context Window
    → LLM Generates Response with Citations
Reranker: Use NVIDIA NV-RerankQA (free via NIM) or Cohere Rerank (via OpenRouter) to improve retrieval precision.

12. Pharmacokinetic Engine
This is pure mathematics, not AI — deterministic pharmacokinetic models that run on CPU.

Implementation
Aspect	Detail
Language	Python (NumPy + SciPy)
Models implemented	Marsh (propofol), Schnider (propofol), Minto (remifentanil), Eleveld (propofol, general-purpose)
What it calculates	Plasma concentration, effect-site concentration, time to emergence, recommended infusion rates
Input	Patient weight, height, age, lean body mass (from Scholar), drug doses + times (from Pharmacist agent)
Output	Real-time concentration curves displayed on Theatre Display; verbal alerts via Pharmacist agent
Open source reference	PyTCI library: github.com/opentiva/pytci (Python implementation of TCI pharmacokinetic models)
License	MIT
13. Theatre Display & Frontend
Web Application on Smart TV
Aspect	Detail
Technology	Next.js 14+ (React)
Rendering	Client-side rendering for real-time updates
Deployment	Runs in Chromium browser on a Smart TV, laptop, or Android tablet connected to display
Connection	Joins the LiveKit room as a subscriber — receives display commands from AI agents
Design	Dark theme, high contrast, theatre-optimised, large text (readable from 3m+ distance)
Display Components
Component	Technology
Vital signs dashboard	Real-time charts using Recharts / Chart.js, fed by Monitor Agent
Anatomy overlays	Three.js for 3D anatomy rendering; SVG for 2D diagrams
Marma diagrams	Pre-rendered SVGs with Sanskrit labels, interactive highlights
Surgical timeline	Custom React timeline component
Drug record	Real-time table updated by Pharmacist Agent
PK curves	Recharts line charts showing plasma/effect-site concentration
Shloka display	Devanagari text rendering with transliteration
Instrument count	Simple count display with status indicators
Patient imaging	DICOM viewer using Cornerstone.js (open source, MIT)
DICOM Viewer: Cornerstone.js
Aspect	Detail
Tool	Cornerstone.js + OHIF Viewer
GitHub	github.com/cornerstonejs/cornerstone3D
License	MIT
What	View patient MRI/CT/X-ray directly in the Theatre Display
Why	Open source, browser-based, supports DICOM standard
14. Backend & API Layer
Component	Technology	Purpose
API Server	FastAPI (Python)	REST + WebSocket APIs for all services
Task Queue	Celery + Redis	Async processing for Scholar analysis, Chronicler reports
Session State	Redis	In-memory state for active surgery session
Database	PostgreSQL	Persistent storage for surgeon profiles, surgery history, patient records
File Storage	MinIO (self-hosted S3)	Store uploaded patient files, generated reports, session recordings
Authentication	JWT + API keys	Surgeon authentication, session security
Containerisation	Docker	
Hit the token limit. I'll continue from where I left off — Section 14 (Backend) onwards. Copy-paste this block right after the previous one:

[ignoring loop detection]

14. Backend & API Layer (continued)
Component	Technology	Purpose
API Server	FastAPI (Python)	REST + WebSocket APIs for all services
Task Queue	Celery + Redis	Async processing for Scholar analysis, Chronicler reports
Session State	Redis	In-memory state for active surgery session — full contextual memory
Database	PostgreSQL	Persistent storage for surgeon profiles, surgery history
File Storage	MinIO (self-hosted S3-compatible)	Patient files, reports, session recordings
Auth	JWT + API keys	Surgeon auth, session security
Containers	Docker + Docker Compose	All services containerised for reproducible deployment
Orchestration	Docker Compose (Phase 1–2), Kubernetes (Phase 3+)	Single-command deployment of entire stack on GPU instance
All open source. All free.

15. Data Storage & Session Management
Data Type	Storage	Encryption	Retention
Active surgery session state	Redis (in-memory on GPU instance)	In-transit (TLS)	Deleted when GPU instance terminates
Surgery session archive	PostgreSQL + MinIO (persistent cloud)	AES-256 at rest	Surgeon-controlled retention
Surgeon Profile	PostgreSQL (encrypted columns)	AES-256	Permanent until surgeon deletes
Pre-op analysis documents	MinIO	AES-256 at rest	Linked to patient record
Video recordings (if Teaching Mode)	MinIO / Object storage	AES-256 at rest	Consent-governed
Shalyatantra corpus	Qdrant + PostgreSQL	Not patient data — no special encryption	Permanent
16. Android Companion App
Tech Stack
Layer	Technology
Language	Kotlin
UI Framework	Jetpack Compose
Camera	CameraX (Android Jetpack)
WebRTC	LiveKit Android SDK (io.livekit:livekit-android)
Bluetooth Audio	Android AudioManager + Bluetooth A2DP/HFP APIs
Background Service	Foreground Service (keeps camera streaming during screen-off)
Networking	OkHttp + Retrofit for REST APIs
Local Storage	Room Database (session metadata cache)
Min Android Version	Android 10 (API 29)
Distribution	APK sideload (Phase 1), Google Play (Phase 3+)
App Modes
Mode	Function
Monitor Camera	Streams rear camera to LiveKit room; auto-aims at patient monitor
Overhead Camera	Streams rear camera; wide-angle mode if available
Surgeon Camera	Streams rear camera + neckband mic audio; highest priority stream
Display Mode	Turns phone/tablet into a Theatre Display (receives display commands)
17. NVIDIA Programme Benefits Integration
You're selected for both NVIDIA Inception and NVIDIA Digital Health Programme. Here's how to maximise every free benefit:

Benefit	How We Use It	Value
Free DLI courses	Train team on NeMo (ASR fine-tuning), MONAI (medical vision), CUDA optimisation	~$5K–$10K saved in training
NVIDIA NIM	Self-host Nemotron 3 Super and NV-Embed with optimised inference containers — free	Eliminates need for vLLM setup; production-grade serving
ai.nvidia.com credits	Use NIM API endpoints for development/testing before self-hosting	Free API calls during development
NVIDIA NeMo	Fine-tune Parakeet TDT on surgical speech data	Best medical ASR pipeline, free framework
NVIDIA MONAI	Pre-trained surgical segmentation models; fine-tune on surgical anatomy	Free medical vision framework
NemoClaw	Enterprise-grade agentic orchestration with security guardrails	Free agentic infrastructure
Preferred GPU pricing	Discounts on NVIDIA hardware if we later build edge devices	Future hardware cost reduction
VC network (Inception Capital Connect)	Fundraising connections when ready for Series A	Investor pipeline
Co-marketing	NVIDIA case study / newsletter feature once product launches	Brand credibility
Healthcare Alliance	Connections to GE Healthcare, hospital networks	Go-to-market partnerships
NeMoClaw Stack (What We Get Free from NVIDIA)
NemoClaw = OpenClaw (agent runtime)
         + OpenShell (sandboxed execution)
         + Nemotron (local LLM)
         + NIM (inference serving)
         + NeMo (model training)
         + MONAI (medical vision)
         + NV-Embed (embeddings)
         + Privacy Routing (local vs cloud model selection)
This is essentially our entire agentic + LLM + medical vision infrastructure — free via NVIDIA programmes.

18. Cost Analysis Per Surgery
Scenario: Standard 2-Hour Surgery
Cost Item	Provider	Cost
GPU compute (H100 x 2.5 hrs including setup/teardown)	Nebius	$7.38 (~₹615)
OpenRouter API calls (Scholar pre-op + Consultant queries + Chronicler post-op)	OpenRouter	$0.50–$2.00 (₹40–₹165)
LiveKit server	Self-hosted on GPU	$0 (included in GPU cost)
All AI models (STT, TTS, Vision, LLM reasoning)	Self-hosted on GPU	$0 (included in GPU cost)
Android app	Self-built	$0
Theatre Display web app	Self-built	$0
Total per surgery		$8–$10 (₹650–₹830)
Scenario: Extended 4-Hour Surgery
Cost Item	Cost
GPU compute (H100 x 4.5 hrs)	$13.28 (~₹1,107)
OpenRouter API calls	$1–$3 (₹80–₹250)
Total per surgery	$14–$16 (₹1,150–₹1,350)
Monthly Cost Projections (Per Surgeon)
Surgeries/Month	GPU Cost	API Cost	Total Monthly
10 surgeries	₹6,150	₹1,650	~₹7,800
20 surgeries	₹12,300	₹3,300	~₹15,600
40 surgeries	₹24,600	₹6,600	~₹31,200
Hardware Costs (One-Time)
Item	Cost
2x Android phones (if not using existing)	₹10K–₹20K
1x GoPro Hero 13 + head mount + capture card	₹35K–₹45K
2x Bluetooth neckbands	₹6K–₹30K
1x Smart TV / large monitor (if not existing)	₹20K–₹40K
Total one-time hardware	₹70K–₹1.35L
Compare this to the blueprint's original estimate of ₹2.35L–₹5.05L for edge compute setup. We've reduced hardware costs by 60–70%.

19. Complete Stack Summary Table
Layer	Component	Technology	License	Cost
Camera (Monitor)	Android Phone	CameraX + LiveKit SDK	—	₹0–₹10K
Camera (Overhead)	Android Phone	CameraX + LiveKit SDK	—	₹0–₹10K
Camera (Surgeon)	Android/GoPro/Dedicated	LiveKit SDK / HDMI capture	—	₹0–₹80K
Audio Input	BT Neckband	Bluetooth HFP/A2DP	—	₹3K–₹15K each
Display	Smart TV + Web App	Next.js + Chromium	MIT	₹20K–₹40K
Real-Time Transport	WebRTC Server	LiveKit (self-hosted)	Apache 2.0	Free
GPU Compute	Surgery session	Nebius / Lightning AI (H100)	Pay-per-hour	~₹650/surgery
STT (Speech-to-Text)	Surgical speech recognition	NVIDIA Parakeet TDT 0.6B v2	CC-BY-4.0	Free
STT (Fallback)	Multilingual recognition	Whisper Large V3 Turbo	MIT	Free
TTS (Voice Synthesis)	Multiple voice profiles	Fish Speech 1.5	Apache 2.0	Free
TTS (Fast Alerts)	Critical one-line alerts	Piper TTS	MIT	Free
LLM (Real-time)	Voice reasoning loop	Nemotron 3 Super (via NIM)	NVIDIA Open	Free (NIM)
LLM (Deep reasoning)	Scholar, Consultant, Chronicler	GPT-5.4 / Claude via OpenRouter	Pay-per-token	~₹165/surgery
LLM (Fast fallback)	Voice loop backup	Inception Mercury 2 via OpenRouter	Pay-per-token	Variable
Vision (Monitor)	Vital sign reading	YOLOv11 + PaddleOCR + OpenCV	Apache 2.0	Free
Vision (Counting)	Instrument/swab tracking	YOLOv11 + SAM 2 + ByteTrack	Apache 2.0	Free
Vision (Anatomy)	Surgical structure recognition	RASO + MONAI + SAM 2	Apache 2.0	Free
Agentic Framework	Multi-agent orchestration	OpenClaw + NemoClaw	MIT / NVIDIA	Free
Vector Database	Knowledge retrieval	Qdrant	Apache 2.0	Free
Embeddings	Text embeddings	NVIDIA NV-Embed-v2 (via NIM)	NVIDIA	Free
PK Engine	Pharmacokinetic modelling	PyTCI + custom Python	MIT	Free
Backend	API server	FastAPI + Redis + PostgreSQL	MIT/BSD	Free
Storage	Files & recordings	MinIO (self-hosted S3)	AGPL-3.0	Free
Mobile App	Camera + audio companion	Kotlin + Jetpack Compose + LiveKit	Apache 2.0	Free
ASR Fine-tuning	Medical vocabulary training	NVIDIA NeMo Framework	Apache 2.0	Free
DICOM Viewer	Patient imaging display	Cornerstone.js + OHIF	MIT	Free
20. Key Open Source Repositories — Quick Reference
Repo	URL	What We Use It For
LiveKit	github.com/livekit/livekit	All real-time audio/video transport
LiveKit Agents	github.com/livekit/agents	Python AI agent framework
Ultralytics YOLO	github.com/ultralytics/ultralytics	Object detection across all 3 cameras
SAM 2	github.com/facebookresearch/sam2	Segmentation for instruments + anatomy
PaddleOCR	github.com/PaddlePaddle/PaddleOCR	Reading monitor vital signs
OpenCV	github.com/opencv/opencv	Image preprocessing
NVIDIA NeMo	github.com/NVIDIA/NeMo	ASR training (Parakeet fine-tuning)
NVIDIA MONAI	github.com/Project-MONAI/MONAI	Medical image segmentation
Fish Speech	github.com/fishaudio/fish-speech	Multi-voice TTS
Piper TTS	github.com/rhasspy/piper	Fast alert voice synthesis
Coqui TTS (Idiap fork)	github.com/idiap/coqui-ai-TTS	XTTS-v2 fallback TTS
OpenClaw	github.com/openclaw	Agentic orchestration runtime
Qdrant	github.com/qdrant/qdrant	Vector database for RAG
PyTCI	github.com/opentiva/pytci	Pharmacokinetic modelling
Cornerstone.js	github.com/cornerstonejs/cornerstone3D	DICOM medical image viewer
WhisperLive	github.com/collabora/WhisperLive	Streaming Whisper wrapper
Endoscapes Dataset	github.com/CAMMA-public/Endoscapes	Surgical instrument training data
RASO	Search arxiv for latest release	Surgical object recognition
21. Deployment Sequence — How a Surgery Session Works
Step 1 — Pre-Surgery (T-60 min to T-30 min)

Surgeon uploads patient files via web portal
Scholar Agent runs on OpenRouter (Claude/GPT) — generates Master Pre-Operative Analysis
Risk scores calculated, drug interactions mapped, Ayurvedic assessment if applicable
Step 2 — Session Spin-Up (T-15 min)

System provisions H100 GPU on Nebius/Lightning AI
Docker Compose deploys: LiveKit Server, all AI models, all agents, Redis, FastAPI
Health checks confirm all services running
LiveKit Room created for this surgery session
Step 3 — Device Connection (T-5 min)

Surgeon opens ShalyaMitra app on 3 Android phones → each joins LiveKit room
Surgeon pairs neckband → audio routed through app to LiveKit
Theatre Display (Smart TV) loads web app → joins LiveKit room
System confirms: "All systems connected. ShalyaMitra is live."
Step 4 — Surgery Active (1–3+ hours)

All 3 camera feeds processing continuously on GPU
Voice Agent listening continuously, responding to surgeon
Monitor Agent watching vitals, running predictive model
Sentinel Agent counting instruments/swabs
All agents maintaining persistent memory of entire session
Oracle, Consultant, Devil's Advocate available on demand
Step 5 — Closure & Handover (T+0 to T+15 min)

Sentinel confirms instrument/swab count
Chronicler generates Intraoperative Chronicle + Handover Brief
Reports saved to persistent storage
Session archived
Step 6 — Teardown (T+15 min)

GPU instance terminated
Billing stops
All session data encrypted and archived to persistent cloud storage
ShalyaMitra Tech Stack Blueprint v1.0 Built for surgeons, not for servers. Every rupee spent serves the patient on the table.