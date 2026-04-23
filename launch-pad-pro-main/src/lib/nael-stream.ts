/**
 * Nael Stream Adapter
 *
 * This is the seam between the UI and the *source* of live Nael data.
 *
 * In v1 we play back a scripted demo session (DEMO_EVENTS) at real time.
 * In production this same hook would subscribe to a LiveKit data channel
 * coming from the GPU backend (Riva ASR + NeMo proactive engine +
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
  type DemoPhaseEvent,
  type DemoOverlayEvent,
  type DemoKnowledgeEvent,
  type DemoInstrumentEvent,
  type DemoRetractionEvent,
  type DemoAdvocateEvent,
  type DemoNaelStateEvent,
} from "./demo-session";

export type StreamMode = "silent" | "reactive" | "proactive";

export type StreamHandlers = {
  onTranscript?: (e: DemoTranscriptEvent) => void;
  onAlert?: (e: DemoAlertEvent) => void;
  onVitals?: (e: DemoVitalsEvent) => void;
  onPhase?: (e: DemoPhaseEvent) => void;
  onOverlays?: (e: DemoOverlayEvent) => void;
  onKnowledge?: (e: DemoKnowledgeEvent) => void;
  onInstrumentCount?: (e: DemoInstrumentEvent) => void;
  onRetraction?: (e: DemoRetractionEvent) => void;
  onAdvocate?: (e: DemoAdvocateEvent) => void;
  onNaelState?: (e: DemoNaelStateEvent) => void;
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
      handlersRef.current.onVitals?.({
        kind: "vitals",
        at: Math.floor(t),
        ...v,
      });

      // Fire any due scripted events
      while (cursor.current < DEMO_EVENTS.length && DEMO_EVENTS[cursor.current].at <= t) {
        const evt: DemoEvent = DEMO_EVENTS[cursor.current];
        cursor.current += 1;

        switch (evt.kind) {
          case "transcript":
            handlersRef.current.onTranscript?.(evt);
            break;

          case "alert": {
            const m = modeRef.current;
            const sev = evt.severity;
            // Silent mode: suppress non-critical alerts
            if (m === "silent" && sev !== "critical") continue;
            // Reactive mode: only critical/warning
            if (m === "reactive" && (sev === "info" || sev === "caution")) continue;
            handlersRef.current.onAlert?.(evt);
            break;
          }

          case "phase":
            handlersRef.current.onPhase?.(evt);
            break;

          case "overlays":
            handlersRef.current.onOverlays?.(evt);
            break;

          case "knowledge":
            handlersRef.current.onKnowledge?.(evt);
            break;

          case "instrument_count":
            handlersRef.current.onInstrumentCount?.(evt);
            break;

          case "retraction":
            handlersRef.current.onRetraction?.(evt);
            break;

          case "advocate":
            handlersRef.current.onAdvocate?.(evt);
            break;

          case "nael_state":
            handlersRef.current.onNaelState?.(evt);
            break;
        }
      }

      if (t >= DEMO_DURATION) {
        handlersRef.current.onComplete?.();
        return;
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
