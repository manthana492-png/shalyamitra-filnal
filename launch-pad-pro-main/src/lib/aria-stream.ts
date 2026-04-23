/**
 * ARIA Stream Adapter
 *
 * This is the seam between the UI and the *source* of live ARIA data.
 *
 * In v1 we play back a scripted demo session (DEMO_EVENTS) at real time.
 * In production this same hook would subscribe to a WebSocket / WebRTC data
 * channel coming from the GPU backend (Riva ASR + NeMo proactive engine +
 * Morpheus PHI redaction) and emit the same shape of events.
 *
 * The component layer doesn't know or care which source it is.
 */

import { useEffect, useRef, useState } from "react";
import {
  DEMO_EVENTS,
  DEMO_DURATION,
  vitalsAt,
  type DemoEvent,
  type DemoTranscriptEvent,
  type DemoAlertEvent,
  type DemoVitalsEvent,
} from "./demo-session";

export type StreamMode = "silent" | "reactive" | "proactive";

export type StreamHandlers = {
  onTranscript?: (e: DemoTranscriptEvent) => void;
  onAlert?: (e: DemoAlertEvent) => void;
  onVitals?: (e: DemoVitalsEvent) => void;
  onTick?: (elapsed: number) => void;
  onComplete?: () => void;
};

export function useScriptedSession(opts: {
  running: boolean;
  mode: StreamMode;
  handlers: StreamHandlers;
}) {
  const { running, mode, handlers } = opts;
  const [elapsed, setElapsed] = useState(0);
  const startedAt = useRef<number | null>(null);
  const cursor = useRef(0);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const modeRef = useRef(mode);
  modeRef.current = mode;

  useEffect(() => {
    if (!running) {
      startedAt.current = null;
      return;
    }
    if (startedAt.current === null) {
      startedAt.current = Date.now() - elapsed * 1000;
    }

    const tick = () => {
      const t = (Date.now() - (startedAt.current ?? Date.now())) / 1000;
      setElapsed(t);
      handlersRef.current.onTick?.(t);

      // Fire vitals every second
      const v = vitalsAt(Math.floor(t));
      handlersRef.current.onVitals?.({ kind: "vitals", at: Math.floor(t), ...v });

      // Fire any due scripted events
      while (cursor.current < DEMO_EVENTS.length && DEMO_EVENTS[cursor.current].at <= t) {
        const evt: DemoEvent = DEMO_EVENTS[cursor.current];
        cursor.current += 1;

        if (evt.kind === "transcript") {
          // In silent mode, ARIA still listens & logs but does not speak.
          // In reactive mode, ARIA only speaks when its line is in the script
          // and was a *response*. In proactive mode, ARIA volunteers info.
          // For v1 demo simplicity we surface all transcript events; the UI
          // suppresses ARIA TTS playback in silent mode.
          handlersRef.current.onTranscript?.(evt);
        } else if (evt.kind === "alert") {
          // Silent mode: suppress non-critical alerts entirely.
          // Reactive mode: only critical/warning alerts.
          // Proactive mode: all alerts.
          const m = modeRef.current;
          const sev = evt.severity;
          if (m === "silent" && sev !== "critical") continue;
          if (m === "reactive" && (sev === "info" || sev === "caution")) continue;
          handlersRef.current.onAlert?.(evt);
        }
      }

      if (t >= DEMO_DURATION) {
        handlersRef.current.onComplete?.();
        return; // stop ticking
      }
    };

    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  const reset = () => {
    cursor.current = 0;
    startedAt.current = null;
    setElapsed(0);
  };

  return { elapsed, reset, total: DEMO_DURATION };
}
