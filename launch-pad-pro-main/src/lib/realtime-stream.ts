/**
 * useRealtimeStream — backend-agnostic Nael event stream.
 *
 * Canonical runtime contract:
 *   - Production path: "live" only, backed by `/ws/realtime`
 *   - Demo path: "scripted" only, and only when explicitly enabled by caller
 */

import { useEffect, useRef, useState } from "react";
import { useScriptedSession, type StreamMode, type StreamHandlers } from "./nael-stream";
import { DEMO_DURATION } from "./demo-session";
import type { ServerEvent } from "./gpu-adapter";

export type RealtimeSource = "scripted" | "live";
export type RealtimeStatus = "idle" | "connecting" | "connected" | "scripted-fallback" | "error";

export type UseRealtimeStreamOpts = {
  source: RealtimeSource;
  running: boolean;
  mode: StreamMode;
  sessionId?: string;
  handlers: StreamHandlers;
  allowDemoScripted?: boolean;
};

// Connect to the FastAPI backend (not Supabase edge functions)
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
const WS_BACKEND_URL = BACKEND_URL.replace(/^http/, "ws");

function wsUrl(endpoint: string): string {
  return `${WS_BACKEND_URL}${endpoint}`;
}

export function useRealtimeStream(opts: UseRealtimeStreamOpts) {
  const { source, running, mode, sessionId, handlers, allowDemoScripted = false } = opts;
  const [status, setStatus] = useState<RealtimeStatus>("idle");
  const [resolvedSource, setResolvedSource] = useState<RealtimeSource>("live");
  const [elapsed, setElapsed] = useState(0);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const wsRef = useRef<WebSocket | null>(null);

  // Local scripted fallback (only ticks when resolvedSource is "scripted")
  const scripted = useScriptedSession({
    running: running && source === "scripted" && allowDemoScripted,
    mode,
    handlers,
  });

  useEffect(() => {
    if (source === "scripted" && allowDemoScripted) {
      setResolvedSource("scripted");
      setStatus("connected");
      setElapsed(scripted.elapsed);
      return;
    }
    if (source === "scripted" && !allowDemoScripted) {
      setStatus("error");
      setResolvedSource("live");
    }
  }, [source, allowDemoScripted, scripted.elapsed]);

  // Connect / disconnect WS for live mode
  useEffect(() => {
    if (!running || source !== "live") {
      return;
    }

    let cancelled = false;
    setStatus("connecting");
    setResolvedSource("live");

    const url = wsUrl("/ws/realtime");

    let ws: WebSocket;
    try {
      ws = new WebSocket(url);
    } catch {
      if (!cancelled) {
        setStatus("error");
      }
      return;
    }
    wsRef.current = ws;
    let startedAt = Date.now();

    ws.onopen = () => {
      if (cancelled) return;
      setStatus("connected");
      startedAt = Date.now();
      try {
        // Send auth message (backend expects this as first message within 5s)
        const token = localStorage.getItem("sb-access-token") || "";
        ws.send(JSON.stringify({
          type: "auth",
          token: token,
          sessionId: sessionId ?? "",
        }));
        // Send initial mode control
        ws.send(JSON.stringify({ type: "control", mode }));
      } catch { /* noop */ }
    };

    ws.onmessage = (e) => {
      if (cancelled) return;
      try {
        const evt = JSON.parse(typeof e.data === "string" ? e.data : "") as ServerEvent;

        if (evt.type === "error") {
          setStatus("error");
          try { ws.close(); } catch { /* noop */ }
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

    ws.onerror = () => {
      if (!cancelled) setStatus("error");
    };
    ws.onclose = () => {
      if (cancelled) return;
      setStatus("error");
    };

    // Cleanup
    return () => {
      cancelled = true;
      try { ws.close(); } catch { /* noop */ }
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, source, sessionId, mode]);

  // Push mode changes to the live socket
  useEffect(() => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try { ws.send(JSON.stringify({ type: "control", mode })); } catch { /* noop */ }
    }
  }, [mode]);

  const reset = () => {
    if (source === "scripted" && allowDemoScripted) {
      scripted.reset();
    }
    setElapsed(0);
  };

  return {
    elapsed,
    total: source === "scripted" ? DEMO_DURATION : 0,
    status,
    resolvedSource,
    reset,
  };
}
