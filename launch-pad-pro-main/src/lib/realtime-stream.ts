/**
 * useRealtimeStream — backend-agnostic Nael event stream.
 *
 * Selects between three sources, automatically falling back:
 *
 *   1. "live"     — connect to FastAPI backend WebSocket (/ws/realtime)
 *                   Receives real NIM API responses + simulated vitals
 *   2. "mock"     — connect to FastAPI mock-gpu WebSocket (/ws/mock-gpu)
 *                   Server-side scripted feed, proves WS pipeline end-to-end
 *   3. "scripted" — local in-browser playback (DEMO_EVENTS), zero network
 *
 * Selection rule:
 *   - Caller passes a preferred `source`
 *   - If "live" / "mock" fails to connect or returns code "demo_mode", we
 *     transparently fall back to "scripted" so the demo never breaks
 *
 * The handler shape matches `nael-stream.ts` so SessionConsole consumes both
 * adapters interchangeably.
 */

import { useEffect, useRef, useState } from "react";
import { useScriptedSession, type StreamMode, type StreamHandlers } from "./nael-stream";
import { DEMO_DURATION } from "./demo-session";
import type { ServerEvent } from "./gpu-adapter";

export type RealtimeSource = "scripted" | "mock" | "live";
export type RealtimeStatus = "idle" | "connecting" | "connected" | "scripted-fallback" | "error";

export type UseRealtimeStreamOpts = {
  source: RealtimeSource;
  running: boolean;
  mode: StreamMode;
  sessionId?: string;
  handlers: StreamHandlers;
};

// Connect to the FastAPI backend (not Supabase edge functions)
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const WS_BACKEND_URL = BACKEND_URL.replace(/^http/, "ws");

function wsUrl(endpoint: string): string {
  return `${WS_BACKEND_URL}${endpoint}`;
}

export function useRealtimeStream(opts: UseRealtimeStreamOpts) {
  const { source, running, mode, sessionId, handlers } = opts;
  const [status, setStatus] = useState<RealtimeStatus>("idle");
  const [resolvedSource, setResolvedSource] = useState<RealtimeSource>(source);
  const [elapsed, setElapsed] = useState(0);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const wsRef = useRef<WebSocket | null>(null);

  // Local scripted fallback (only ticks when resolvedSource is "scripted")
  const scripted = useScriptedSession({
    running: running && resolvedSource === "scripted",
    mode,
    handlers,
  });

  // Mirror elapsed when running on scripted
  useEffect(() => {
    if (resolvedSource === "scripted") setElapsed(scripted.elapsed);
  }, [scripted.elapsed, resolvedSource]);

  // Connect / disconnect WS for live or mock
  useEffect(() => {
    if (!running || source === "scripted") {
      setResolvedSource("scripted");
      return;
    }

    let cancelled = false;
    setStatus("connecting");

    // Route to FastAPI backend endpoints
    const endpoint = source === "mock" ? "/ws/mock-gpu" : "/ws/realtime";
    const url = wsUrl(endpoint);

    let ws: WebSocket;
    try {
      ws = new WebSocket(url);
    } catch {
      if (!cancelled) {
        setStatus("scripted-fallback");
        setResolvedSource("scripted");
      }
      return;
    }
    wsRef.current = ws;
    let startedAt = Date.now();

    const fallback = () => {
      if (cancelled) return;
      setStatus("scripted-fallback");
      setResolvedSource("scripted");
    };

    ws.onopen = () => {
      if (cancelled) return;
      setStatus("connected");
      setResolvedSource(source);
      startedAt = Date.now();
      try {
        // Send auth message (backend expects this as first message within 5s)
        const token = localStorage.getItem("sb-access-token") || "";
        ws.send(JSON.stringify({
          type: "auth",
          token: token,
          sessionId: sessionId ?? "demo",
        }));
        // Send initial mode control
        ws.send(JSON.stringify({ type: "control", mode }));
      } catch { /* noop */ }
    };

    ws.onmessage = (e) => {
      if (cancelled) return;
      try {
        const evt = JSON.parse(typeof e.data === "string" ? e.data : "") as ServerEvent;

        // If backend says "demo_mode" (no GPU), fall back to scripted
        if (evt.type === "error" && evt.code === "demo_mode") {
          fallback();
          return;
        }

        const t = (Date.now() - startedAt) / 1000;
        setElapsed(t);
        handlersRef.current.onTick?.(t);

        if (evt.type === "transcript") {
          handlersRef.current.onTranscript?.({
            kind: "transcript",
            at: evt.at,
            text: evt.text,
            // Remap legacy "aria" speaker → "nael" at the WS boundary
            speaker: (evt.speaker === "aria" ? "nael" : evt.speaker) as import("./demo-session").DemoSpeaker,
          });
        } else if (evt.type === "alert") {
          handlersRef.current.onAlert?.({
            kind: "alert",
            at: evt.at,
            severity: evt.severity,
            pillar: (evt as any).pillar ?? "nael",
            priority: (evt as any).priority ?? 8,
            title: evt.title,
            body: evt.body,
            source: evt.source,
          });
        } else if (evt.type === "vitals") {
          handlersRef.current.onVitals?.({
            kind: "vitals",
            at: evt.at,
            hr: evt.hr,
            spo2: evt.spo2,
            map: evt.map,
            etco2: evt.etco2,
            temp: (evt as any).temp ?? 36.5,
            rr: (evt as any).rr ?? 14,
          });
        } else if (evt.type === "phase") {
          handlersRef.current.onPhase?.({
            kind: "phase",
            at: (evt as any).at ?? 0,
            phase: (evt as any).phase,
          });
        }
      } catch { /* ignore parse errors */ }
    };

    ws.onerror = () => fallback();
    ws.onclose = (e) => {
      if (cancelled) return;
      // Normal close after demo_mode handshake → fallback already triggered.
      if (status === "connecting") fallback();
    };

    // Cleanup
    return () => {
      cancelled = true;
      try { ws.close(); } catch { /* noop */ }
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, source, sessionId]);

  // Push mode changes to the live socket
  useEffect(() => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try { ws.send(JSON.stringify({ type: "control", mode })); } catch { /* noop */ }
    }
  }, [mode]);

  const reset = () => {
    scripted.reset();
    setElapsed(0);
  };

  return {
    elapsed,
    total: DEMO_DURATION,
    status,
    resolvedSource,
    reset,
  };
}
