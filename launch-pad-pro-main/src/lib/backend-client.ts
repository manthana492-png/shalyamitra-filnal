/**
 * ShalyaMitra — Backend Connection Hook
 *
 * Connects the frontend to the FastAPI backend:
 *   - REST endpoints for pre-op, sessions, voice, camera
 *   - WebSocket for real-time events during surgery
 *   - Auto-reconnection with exponential backoff
 *
 * Replaces the Supabase edge function relay with a direct
 * WebSocket connection to the FastAPI backend.
 */

// Backend base URL — defaults to localhost in dev
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const WS_URL = BACKEND_URL.replace(/^http/, "ws");

// ─── REST API Helpers ────────────────────────────────────

async function api<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("sb-access-token") || "";
  const resp = await fetch(`${BACKEND_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!resp.ok) {
    const err = await resp.text().catch(() => resp.statusText);
    throw new Error(`API ${resp.status}: ${err}`);
  }
  return resp.json() as Promise<T>;
}

// ─── Typed API Functions ─────────────────────────────────

/** Health check */
export const checkHealth = () => api<{
  status: string; service: string; version: string; gpu_provider: string;
}>("/healthz");

/** Pre-op analysis */
export const getPreopAnalysis = (sessionId: string) =>
  api(`/api/preop/${sessionId}`);

/** Post-op report */
export const getPostopReport = (sessionId: string) =>
  api(`/api/postop/${sessionId}`);

/** Sessions CRUD */
export const listSessions = () => api("/api/sessions/");
export const getSession = (id: string) => api(`/api/sessions/${id}`);

/** Voice profiles */
export const getVoiceProfiles = () =>
  api<{ voices: VoiceProfile[]; current_preference: string }>("/api/voice/voices");

export const setVoicePreference = (voiceId: string) =>
  api("/api/voice/voices/preference", {
    method: "POST",
    body: JSON.stringify({ voice_id: voiceId }),
  });

export const testVoice = (voiceId: string, text?: string) =>
  api<{ audio_b64: string; mime_type: string; engine_used: string; latency_ms: number }>(
    "/api/voice/voices/test",
    { method: "POST", body: JSON.stringify({ voice_id: voiceId, text }) },
  );

export const getAudioHealth = () => api("/api/voice/health");

/** Camera management */
export const getCameraStatus = () =>
  api<{ cameras: CameraStatus[]; connection_methods: ConnectionMethodInfo[] }>("/api/camera/status");

export const connectCamera = (cameraId: string, method: string) =>
  api("/api/camera/connect", {
    method: "POST",
    body: JSON.stringify({ camera_id: cameraId, method }),
  });

export const disconnectCamera = (cameraId: string) =>
  api(`/api/camera/disconnect/${cameraId}`, { method: "POST" });

export const getVisionHealth = () => api("/api/camera/vision/health");

export const getCameraQR = (cameraId: string) =>
  api<{ join_url: string; join_code: string; instructions: string }>(`/api/camera/qr/${cameraId}`);

/** Admin */
export const getGpuStatus = () => api("/api/admin/gpu/status");

// ─── WebSocket Realtime Connection ───────────────────────

export type RealtimeCallback = (event: ServerEvent) => void;

export type ServerEvent =
  | { type: "transcript"; speaker: string; text: string; at: number; pillar?: string }
  | { type: "alert"; severity: string; title: string; body: string; source: string; at: number; pillar?: string }
  | { type: "vitals"; hr: number; spo2: number; map: number; etco2: number; temp?: number; rr?: number; at: number }
  | { type: "phase"; phase: string; confidence: number; at: number }
  | { type: "vision"; camera: string; detections: Array<{ label: string; score: number }>; at: number }
  | { type: "tts"; audioBase64: string; mimeType: string; at: number }
  | { type: "drug_log"; drug: string; dose_mg: number; route: string; at: number }
  | { type: "report"; narrative: string; at: number }
  | { type: "pong"; ts: number }
  | { type: "error"; code: string; message: string };

export type ConnectionState = "idle" | "connecting" | "connected" | "reconnecting" | "error";

export class RealtimeConnection {
  private ws: WebSocket | null = null;
  private callbacks: Set<RealtimeCallback> = new Set();
  private state: ConnectionState = "idle";
  private sessionId: string = "";
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  get connectionState() { return this.state; }

  subscribe(cb: RealtimeCallback): () => void {
    this.callbacks.add(cb);
    return () => this.callbacks.delete(cb);
  }

  connect(sessionId: string, token?: string): void {
    this.sessionId = sessionId;
    this.state = "connecting";
    this.reconnectAttempts = 0;

    // Backend expects auth as first WS message, not in URL params
    const url = `${WS_URL}/ws/realtime`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.state = "connected";
        this.reconnectAttempts = 0;
        // Send auth message (backend expects this within 5s of connection)
        this.ws?.send(JSON.stringify({
          type: "auth",
          token: token || localStorage.getItem("sb-access-token") || "",
          sessionId,
        }));
      };

      this.ws.onmessage = (msg) => {
        try {
          const event = JSON.parse(msg.data) as ServerEvent;
          this.callbacks.forEach((cb) => cb(event));
        } catch { /* ignore malformed */ }
      };

      this.ws.onclose = () => {
        if (this.state !== "idle") {
          this.state = "reconnecting";
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = () => {
        this.state = "error";
      };
    } catch {
      this.state = "error";
    }
  }

  disconnect(): void {
    this.state = "idle";
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
    this.ws = null;
  }

  /** Send audio chunk for ASR */
  sendAudio(data: string, codec: "opus" | "pcm16" = "opus"): void {
    this.ws?.send(JSON.stringify({ type: "audio", codec, data, ts: Date.now() }));
  }

  /** Send video frame from camera */
  sendVideoFrame(camera: "cam1" | "cam2" | "cam3", data: string): void {
    this.ws?.send(JSON.stringify({ type: "video_frame", camera, data, ts: Date.now() }));
  }

  /** Set Nael mode */
  setMode(mode: "silent" | "reactive" | "proactive"): void {
    this.ws?.send(JSON.stringify({ type: "control", mode }));
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.state = "error";
      return;
    }
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      this.connect(this.sessionId);
    }, delay);
  }
}

// ─── Types ───────────────────────────────────────────────

export interface VoiceProfile {
  id: string;
  name: string;
  description: string;
  gender: string;
  category: string;
  is_default: boolean;
}

export interface CameraStatus {
  camera_id: string;
  label: string;
  description: string;
  connection: string;
  status: string;
  resolution: string;
  fps: number;
  frames_received: number;
  last_frame_age_seconds: number | null;
  reconnect_attempts: number;
  error: string | null;
}

export interface ConnectionMethodInfo {
  id: string;
  name: string;
  description: string;
  requires_app: boolean;
}

// ─── Singleton ───────────────────────────────────────────

export const realtime = new RealtimeConnection();
