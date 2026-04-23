/**
 * NVIDIA GPU Adapter Contract
 *
 * ARIA's web layer talks to a GPU backend that runs:
 *   - NVIDIA Riva     — streaming ASR  (audio in → transcript)
 *   - NeMo            — proactive reasoning + dialogue (LLM)
 *   - Morpheus        — PHI redaction & guardrails
 *   - Triton Inference Server — vision models for the 3 cameras (CV-of-S
 *                       detection, instrument tracking, monitor OCR)
 *
 * That backend will live on Lightning AI / RunPod (NVIDIA H100 / A100 boxes).
 *
 * Until those credentials are dropped in (`add_secret` on the workspace), this
 * module exposes a TypeScript contract every UI/edge function codes against.
 * The real implementation is a thin shim over WebSocket / fetch — wired up
 * inside `supabase/functions/aria-realtime/index.ts`.
 *
 * Drop-in: set the env vars listed in `GPU_BACKEND_ENV` on the Cloud project,
 * then the realtime relay function will start streaming live events instead
 * of demo events. Zero UI changes required.
 */

// -----------------------------------------------------------------------------
// Hosting presets
// -----------------------------------------------------------------------------

export type GpuHost = "lightning" | "runpod" | "self_hosted" | "demo";

export type GpuPreset = {
  id: GpuHost;
  name: string;
  /** Where the user provisions the box. */
  consoleUrl: string;
  /** Recommended GPU SKU. */
  recommendedGpu: string;
  /** Env vars expected on the Cloud project for this preset. */
  envVars: { name: string; example: string; description: string }[];
  /** How to expose the realtime endpoint. */
  endpointShape: string;
  /** A health-check URL pattern to verify the box is alive. */
  healthCheckPath: string;
};

export const GPU_PRESETS: GpuPreset[] = [
  {
    id: "lightning",
    name: "Lightning AI",
    consoleUrl: "https://lightning.ai",
    recommendedGpu: "NVIDIA H100 80GB · 1× for Riva+NeMo, 1× for Triton vision",
    envVars: [
      { name: "GPU_BACKEND_URL",   example: "wss://aria-prod.lightning.ai/v1/realtime", description: "WebSocket endpoint exposed by your Lightning Studio." },
      { name: "GPU_BACKEND_TOKEN", example: "ls_••••••••",                              description: "Bearer token issued by Lightning AI for this Studio." },
      { name: "GPU_BACKEND_HOST",  example: "lightning",                                description: "Set to 'lightning'." },
    ],
    endpointShape: "WebSocket — bi-directional. Client sends opus frames + control msgs; server emits transcript / alert / vitals events.",
    healthCheckPath: "/healthz",
  },
  {
    id: "runpod",
    name: "RunPod",
    consoleUrl: "https://runpod.io",
    recommendedGpu: "NVIDIA A100 80GB · serverless or pod with persistent endpoint",
    envVars: [
      { name: "GPU_BACKEND_URL",   example: "wss://api.runpod.ai/v2/<endpoint-id>/runsync", description: "RunPod serverless endpoint or pod ws URL." },
      { name: "GPU_BACKEND_TOKEN", example: "rpa_••••••••",                                  description: "RunPod API key." },
      { name: "GPU_BACKEND_HOST",  example: "runpod",                                        description: "Set to 'runpod'." },
    ],
    endpointShape: "WebSocket on persistent pods, or HTTP /runsync for serverless. Same event protocol either way.",
    healthCheckPath: "/health",
  },
  {
    id: "self_hosted",
    name: "Self-hosted (NVIDIA NIM / on-prem H100)",
    consoleUrl: "https://catalog.ngc.nvidia.com",
    recommendedGpu: "Hospital-side: 1–2× H100 / L40S in a hardened rack",
    envVars: [
      { name: "GPU_BACKEND_URL",   example: "wss://aria-or.hospital.local/v1/realtime", description: "Internal hospital-network WebSocket endpoint." },
      { name: "GPU_BACKEND_TOKEN", example: "•••• mTLS / shared secret",                description: "Auth secret. Prefer mTLS for production." },
      { name: "GPU_BACKEND_HOST",  example: "self_hosted",                              description: "Set to 'self_hosted'." },
    ],
    endpointShape: "WebSocket inside the hospital VLAN. PHI never leaves the OR.",
    healthCheckPath: "/healthz",
  },
  {
    id: "demo",
    name: "Demo (no GPU)",
    consoleUrl: "",
    recommendedGpu: "—",
    envVars: [
      { name: "GPU_BACKEND_HOST", example: "demo", description: "Default. Plays back the scripted demo session." },
    ],
    endpointShape: "Local scripted playback — no network call.",
    healthCheckPath: "",
  },
];

export const GPU_BACKEND_ENV = ["GPU_BACKEND_URL", "GPU_BACKEND_TOKEN", "GPU_BACKEND_HOST"] as const;

// -----------------------------------------------------------------------------
// Wire protocol — what flows over the WebSocket
// -----------------------------------------------------------------------------

/** Inbound from web → GPU backend. */
export type ClientMessage =
  | { type: "auth"; token: string; sessionId: string }
  | { type: "audio"; codec: "opus" | "pcm16"; data: string /* base64 */; ts: number }
  | { type: "video_frame"; camera: "cam1" | "cam2" | "cam3"; data: string; ts: number }
  | { type: "control"; mode: "silent" | "reactive" | "proactive" }
  | { type: "ping"; ts: number };

/** Outbound from GPU backend → web. Mirrors `DemoEvent` so UI is unchanged. */
export type ServerEvent =
  | { type: "transcript"; speaker: "surgeon" | "anaesthetist" | "nurse" | "aria" | "system"; text: string; at: number; redacted?: boolean; piiSpans?: number[][] }
  | { type: "alert"; severity: "info" | "caution" | "warning" | "critical"; title: string; body: string; source: "vitals" | "vision" | "protocol" | "audio" | string; at: number; cite?: string }
  | { type: "vitals"; hr: number; spo2: number; map: number; etco2: number; at: number }
  | { type: "phase"; phase: string; confidence: number; at: number }
  | { type: "vision"; camera: "cam1" | "cam2" | "cam3"; detections: Array<{ label: string; score: number; bbox?: [number, number, number, number] }>; at: number }
  | { type: "tts"; audioBase64: string; mimeType: "audio/mpeg" | "audio/wav"; at: number }
  | { type: "pong"; ts: number }
  | { type: "error"; code: string; message: string };

// -----------------------------------------------------------------------------
// Module routing — Riva / NeMo / Morpheus / Triton
// -----------------------------------------------------------------------------

export type GpuModule = "riva_asr" | "nemo_dialog" | "morpheus_phi" | "triton_vision" | "guardrails";

export const MODULE_DESCRIPTIONS: Record<GpuModule, { name: string; purpose: string }> = {
  riva_asr:      { name: "NVIDIA Riva",      purpose: "Streaming automatic speech recognition" },
  nemo_dialog:   { name: "NVIDIA NeMo",      purpose: "Dialogue + proactive protocol reasoning" },
  morpheus_phi:  { name: "NVIDIA Morpheus",  purpose: "PHI/PII detection & redaction in transcripts" },
  triton_vision: { name: "NVIDIA Triton",    purpose: "Inference server for surgical vision models" },
  guardrails:    { name: "NVIDIA Guardrails", purpose: "CDS-safe response policy enforcement" },
};

// -----------------------------------------------------------------------------
// Connection helper
// -----------------------------------------------------------------------------

export type ConnectionStatus = "idle" | "connecting" | "connected" | "reconnecting" | "error" | "demo";

export type RealtimeBackendInfo = {
  host: GpuHost;
  url: string | null;
  hasToken: boolean;
  /** True when the relay edge function reports a healthy upstream. */
  upstreamHealthy: boolean | null;
};
