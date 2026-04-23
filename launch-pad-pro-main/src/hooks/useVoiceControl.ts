/**
 * useVoiceControl — Web Speech API recognition + intent parsing.
 *
 * Listens for the wake word "Nael" (or "hey nael"), parses the command, and
 * dispatches it to the UI Director. Designed to degrade gracefully on
 * browsers without webkitSpeechRecognition.
 *
 * In conservative mode only safety-critical commands work.
 * In dynamic mode all UI commands work.
 * In agentic mode, the AI also pushes layout decisions on its own.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useDirector, type CameraId, type LayoutState } from "@/lib/director";
import type { KnowledgePillar } from "@/lib/director";

type Intent =
  | { kind: "mode"; value: "silent" | "reactive" | "proactive" }
  | { kind: "focus"; camera: CameraId }
  | { kind: "layout"; layoutState: LayoutState }
  | { kind: "panel"; panel: "transcript" | "vitals" | "alerts" | "cameras"; show: boolean }
  | { kind: "overlay"; type: "arteries" | "veins" | "nerves" | "ducts" | "marma"; show: boolean }
  | { kind: "overlay_all"; show: boolean }
  | { kind: "knowledge"; pillar: KnowledgePillar }
  | { kind: "close_knowledge" }
  | { kind: "mute" }
  | { kind: "unmute" }
  | { kind: "ack" }
  | { kind: "end" }
  | { kind: "lock" }
  | { kind: "unlock" }
  | { kind: "help" }
  | { kind: "instrument_count" }
  | { kind: "unknown"; raw: string };

function parseIntent(raw: string): Intent {
  const t = raw.toLowerCase().trim();

  // Mode commands
  if (/\b(silent|silence|mute mode)\b/.test(t)) return { kind: "mode", value: "silent" };
  if (/\b(reactive|standby)\b/.test(t)) return { kind: "mode", value: "reactive" };
  if (/\b(proactive|alert mode|active)\b/.test(t)) return { kind: "mode", value: "proactive" };

  // Camera focus commands
  if (/\b(expand surgical|full screen surgeon|focus.*(cam(era)?\s*1|laparoscope|laparo|surgical))\b/.test(t))
    return { kind: "focus", camera: "cam1" };
  if (/\b(show monitor|focus.*(cam(era)?\s*2|monitor))\b/.test(t))
    return { kind: "focus", camera: "cam2" };
  if (/\b(show overhead|show sentinel|focus.*(cam(era)?\s*3|overhead|sentinel))\b/.test(t))
    return { kind: "focus", camera: "cam3" };

  // Layout commands
  if (/\b(show all cameras|all cameras|grid|tile)\b/.test(t))
    return { kind: "layout", layoutState: "theatre_overview" };
  if (/\b(expand|full\s*screen|cinema|zoom)\b/.test(t))
    return { kind: "layout", layoutState: "surgeon_focus" };
  if (/\b(show pharmacokinetics|show pk|pharmacokinetics)\b/.test(t))
    return { kind: "layout", layoutState: "pharmacokinetics" };

  // Overlay commands
  if (/\bmark everything\b/.test(t)) return { kind: "overlay_all", show: true };
  if (/\b(remove overlays|clear overlays|remove all)\b/.test(t)) return { kind: "overlay_all", show: false };
  if (/\bmark arter(y|ies)\b/.test(t)) return { kind: "overlay", type: "arteries", show: true };
  if (/\bmark veins?\b/.test(t)) return { kind: "overlay", type: "veins", show: true };
  if (/\bmark nerves?\b/.test(t)) return { kind: "overlay", type: "nerves", show: true };
  if (/\bmark (marma|marma points?)\b/.test(t)) return { kind: "overlay", type: "marma", show: true };
  if (/\bmark ducts?\b/.test(t)) return { kind: "overlay", type: "ducts", show: true };
  if (/\bremove nerve\b/.test(t)) return { kind: "overlay", type: "nerves", show: false };
  if (/\bremove arter\b/.test(t)) return { kind: "overlay", type: "arteries", show: false };
  if (/\bremove vein\b/.test(t)) return { kind: "overlay", type: "veins", show: false };
  if (/\bremove marma\b/.test(t)) return { kind: "overlay", type: "marma", show: false };

  // Knowledge commands
  if (/\b(show risk flags?|risk flags?|pre.?op)\b/.test(t)) return { kind: "knowledge", pillar: "scholar" };
  if (/\b(show shloka|read.*shloka|show oracle|oracle)\b/.test(t)) return { kind: "knowledge", pillar: "oracle" };
  if (/\b(show.*(mri|ct|imaging)|imaging)\b/.test(t)) return { kind: "knowledge", pillar: "imaging" };
  if (/\b(show drug|drug (dose|log|reference))\b/.test(t)) return { kind: "knowledge", pillar: "drugref" };
  if (/\b(clear|back|back to cameras|close)\b/.test(t)) return { kind: "close_knowledge" };

  // Status commands
  if (/\b(instrument count|count)\b/.test(t)) return { kind: "instrument_count" };
  if (/\b(help|what can i (ask|say))\b/.test(t)) return { kind: "help" };

  // Panel visibility
  if (/\bshow vitals\b/.test(t)) return { kind: "panel", panel: "vitals", show: true };
  if (/\bhide vitals\b/.test(t)) return { kind: "panel", panel: "vitals", show: false };
  if (/\bshow transcript\b/.test(t)) return { kind: "panel", panel: "transcript", show: true };
  if (/\bhide transcript\b/.test(t)) return { kind: "panel", panel: "transcript", show: false };
  if (/\bshow alerts?\b/.test(t)) return { kind: "panel", panel: "alerts", show: true };
  if (/\bhide alerts?\b/.test(t)) return { kind: "panel", panel: "alerts", show: false };

  // Control
  if (/\bmute\b/.test(t)) return { kind: "mute" };
  if (/\bunmute\b/.test(t)) return { kind: "unmute" };
  if (/\b(ack|acknowledge|acknowledged)\b/.test(t)) return { kind: "ack" };
  if (/\b(end session|stop session|end procedure)\b/.test(t)) return { kind: "end" };
  if (/\block layout\b/.test(t)) return { kind: "lock" };
  if (/\bunlock layout\b/.test(t)) return { kind: "unlock" };

  return { kind: "unknown", raw };
}

export type VoiceHandlers = {
  onMute?: () => void;
  onUnmute?: () => void;
  onAckLatest?: () => void;
  onEnd?: () => void;
  onModeChange?: (m: "silent" | "reactive" | "proactive") => void;
  onIntent?: (i: Intent) => void;
};

export function useVoiceControl(handlers: VoiceHandlers = {}) {
  const [supported, setSupported] = useState(false);
  const [active, setActive] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<unknown>(null);
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;
  const director = useDirector();

  useEffect(() => {
    if (typeof window === "undefined") return;
    const w = window as unknown as {
      SpeechRecognition?: new () => unknown;
      webkitSpeechRecognition?: new () => unknown;
    };
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    setSupported(!!SR);
  }, []);

  const dispatch = useCallback(
    (intent: Intent) => {
      handlersRef.current.onIntent?.(intent);
      switch (intent.kind) {
        case "mode":
          handlersRef.current.onModeChange?.(intent.value);
          break;
        case "focus":
          director.setLayoutState("surgeon_focus");
          director.applyDirective({ kind: "focus", camera: intent.camera });
          break;
        case "layout":
          director.applyDirective({ kind: "layout", layoutState: intent.layoutState });
          break;
        case "panel":
          director.applyDirective({ kind: "panel", panel: intent.panel, show: intent.show });
          break;
        case "overlay":
          director.applyDirective({ kind: "overlay", type: intent.type, show: intent.show });
          break;
        case "overlay_all":
          director.applyDirective({ kind: "overlay_all", show: intent.show });
          break;
        case "knowledge":
          director.applyDirective({ kind: "knowledge", pillar: intent.pillar, content: null });
          break;
        case "close_knowledge":
          director.applyDirective({ kind: "close_knowledge" });
          break;
        case "mute":
          handlersRef.current.onMute?.();
          break;
        case "unmute":
          handlersRef.current.onUnmute?.();
          break;
        case "ack":
          handlersRef.current.onAckLatest?.();
          director.ackLatestAlert();
          break;
        case "end":
          handlersRef.current.onEnd?.();
          break;
        case "lock":
          director.setLayoutLocked(true);
          break;
        case "unlock":
          director.setLayoutLocked(false);
          break;
        case "help":
          director.setShowVoiceHelp(true);
          setTimeout(() => director.setShowVoiceHelp(false), 10000);
          break;
        case "instrument_count":
          // Toggle instrument count visibility — handled by SessionConsole
          break;
      }
      director.setLastIntent(
        intent.kind === "unknown" ? `?: ${intent.raw}` : intent.kind,
      );
    },
    [director],
  );

  const start = useCallback(() => {
    if (!supported) return;
    const w = window as unknown as {
      SpeechRecognition?: new () => unknown;
      webkitSpeechRecognition?: new () => unknown;
    };
    const SR = (w.SpeechRecognition || w.webkitSpeechRecognition) as
      | (new () => unknown)
      | undefined;
    if (!SR) return;
    const rec = new SR() as {
      continuous: boolean;
      interimResults: boolean;
      lang: string;
      onresult: (e: unknown) => void;
      onend: () => void;
      onerror: (e: unknown) => void;
      start: () => void;
      stop: () => void;
    };
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    rec.onresult = (event: unknown) => {
      const e = event as {
        resultIndex: number;
        results: { length: number; [k: number]: { 0: { transcript: string }; isFinal: boolean } };
      };
      let finalText = "";
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interim += r[0].transcript;
      }
      setTranscript(interim || finalText);
      if (finalText) {
        // Wake word: must contain "nael" or "hey nael"
        if (/\b(hey )?nael\b/i.test(finalText)) {
          director.setNaelState("listening");
          const command = finalText.replace(/\b(hey )?nael\b/i, "").trim();
          if (command) {
            director.setNaelState("thinking");
            dispatch(parseIntent(command));
            setTimeout(() => director.setNaelState("idle"), 1500);
          } else {
            setTimeout(() => director.setNaelState("idle"), 3000);
          }
        }
      }
    };
    rec.onerror = () => {
      try { rec.stop(); } catch { /* noop */ }
    };
    rec.onend = () => {
      if (recognitionRef.current === rec) {
        try { rec.start(); } catch { /* noop */ }
      }
    };
    try {
      rec.start();
      recognitionRef.current = rec;
      setActive(true);
      director.setVoiceListening(true);
    } catch {
      setActive(false);
    }
  }, [supported, dispatch, director]);

  const stop = useCallback(() => {
    const rec = recognitionRef.current as { stop?: () => void } | null;
    recognitionRef.current = null;
    try { rec?.stop?.(); } catch { /* noop */ }
    setActive(false);
    director.setVoiceListening(false);
  }, [director]);

  // Use a ref so the cleanup effect doesn't re-run on every render
  const stopRef = useRef(stop);
  stopRef.current = stop;

  useEffect(() => () => { stopRef.current(); }, []);

  return { supported, active, transcript, start, stop };
}
