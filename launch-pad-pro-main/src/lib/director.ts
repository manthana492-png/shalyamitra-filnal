/**
 * UI Director — ShalyaMitra's agentic layout controller.
 *
 * Nael's "hands" on the UI. Components subscribe to this Zustand store; voice
 * commands, alerts, and the proactive engine push intents into it.
 *
 * Three control modes:
 *  - conservative : voice can only switch mode, mute/unmute, ack alerts, end
 *  - dynamic      : voice can also rearrange layout (focus camera, overlays, knowledge)
 *  - agentic      : Nael proactively re-lays-out based on procedure phase + alerts
 *
 * The surgeon can always toggle "Lock layout" to freeze Nael's hands, even in
 * agentic mode. Safety-first.
 *
 * 7 Layout States (replaces old grid/focus/cinema presets):
 *  - theatre_overview   : 3 cameras equal + compact vitals
 *  - surgeon_focus      : 1 camera expanded + 2 PiP
 *  - anatomy_overlay    : surgeon cam + AI overlays
 *  - vital_alert        : monitor sentinel warning state
 *  - haemorrhage_alert  : critical alert full takeover
 *  - knowledge_display  : split camera + knowledge panel
 *  - pharmacokinetics   : TIVA dashboard
 */

import { create } from "zustand";
import { type PillarId, type ShalyaAlert, ALERT_PRIORITY } from "./pillars";

// ── Types ────────────────────────────────────────────────────────────────

export type ControlMode = "conservative" | "dynamic" | "agentic";

export type LayoutState =
  | "theatre_overview"
  | "surgeon_focus"
  | "anatomy_overlay"
  | "vital_alert"
  | "haemorrhage_alert"
  | "knowledge_display"
  | "pharmacokinetics";

export type CameraId = "cam1" | "cam2" | "cam3";

export type NaelState = "idle" | "listening" | "thinking" | "speaking";

export type KnowledgePillar = "oracle" | "scholar" | "consultant" | "imaging" | "drugref" | null;

export type OverlayState = {
  arteries: boolean;
  veins: boolean;
  nerves: boolean;
  ducts: boolean;
  marma: boolean;
};

export type KnowledgePanelState = {
  open: boolean;
  pillar: KnowledgePillar;
  content: unknown;
};

export type InstrumentCountState = {
  deployed: number;
  accounted: number;
  matched: boolean;
};

export type RetractionTimerState = {
  id: string;
  structure: string;
  startedAt: number;       // elapsed seconds when started
  thresholdMinutes: number;
};

export type OverlayItem = {
  id: string;
  type: "artery" | "vein" | "nerve" | "duct" | "marma";
  bbox: [number, number, number, number]; // normalised 0-1 [x1,y1,x2,y2]
  label: string;
  confidence: number;
};

// ── Directive types ──────────────────────────────────────────────────────

export type Directive =
  | { kind: "layout"; layoutState: LayoutState }
  | { kind: "focus"; camera: CameraId }
  | { kind: "panel"; panel: "transcript" | "vitals" | "alerts" | "cameras" | "nael"; show: boolean }
  | { kind: "overlay"; type: keyof OverlayState; show: boolean }
  | { kind: "overlay_all"; show: boolean }
  | { kind: "knowledge"; pillar: KnowledgePillar; content: unknown }
  | { kind: "close_knowledge" }
  | { kind: "alert"; alert: ShalyaAlert }
  | { kind: "nael_state"; state: NaelState }
  | { kind: "pillar"; pillar: PillarId | null }
  | { kind: "phase"; phase: string }
  | { kind: "instrument_count"; data: InstrumentCountState }
  | { kind: "retraction_start"; timer: RetractionTimerState }
  | { kind: "retraction_stop"; id: string }
  | { kind: "overlay_items"; items: OverlayItem[] };

// ── Store ────────────────────────────────────────────────────────────────

export type DirectorState = {
  // Layout
  layoutState: LayoutState;
  previousLayoutState: LayoutState;
  focusedCamera: CameraId;
  panels: {
    transcript: boolean;
    vitals: boolean;
    alerts: boolean;
    cameras: boolean;
    nael: boolean;
  };

  // Nael
  naelState: NaelState;
  activePillar: PillarId | null;

  // Overlays
  overlays: OverlayState;
  overlayItems: OverlayItem[];

  // Knowledge panel
  knowledgePanel: KnowledgePanelState;

  // Instruments & retraction
  instrumentCount: InstrumentCountState;
  retractionTimers: RetractionTimerState[];

  // Alerts
  alertQueue: ShalyaAlert[];

  // Voice
  controlMode: ControlMode;
  voiceListening: boolean;
  lastIntent: string | null;
  layoutLocked: boolean;

  // Surgery
  phase: string;
  surgeryTimer: number;
  showVoiceHelp: boolean;
  showRecIndicator: boolean;

  // ── Actions ──
  setLayoutState: (l: LayoutState) => void;
  setFocus: (c: CameraId) => void;
  togglePanel: (p: keyof DirectorState["panels"]) => void;
  setPanel: (p: keyof DirectorState["panels"], v: boolean) => void;
  setControlMode: (m: ControlMode) => void;
  setVoiceListening: (b: boolean) => void;
  setLastIntent: (s: string | null) => void;
  setLayoutLocked: (b: boolean) => void;
  setPhase: (p: string) => void;
  setNaelState: (s: NaelState) => void;
  setActivePillar: (p: PillarId | null) => void;
  setOverlay: (type: keyof OverlayState, show: boolean) => void;
  setAllOverlays: (show: boolean) => void;
  setOverlayItems: (items: OverlayItem[]) => void;
  setKnowledgePanel: (pillar: KnowledgePillar, content: unknown) => void;
  closeKnowledgePanel: () => void;
  setInstrumentCount: (data: InstrumentCountState) => void;
  addRetractionTimer: (timer: RetractionTimerState) => void;
  removeRetractionTimer: (id: string) => void;
  pushAlert: (alert: ShalyaAlert) => void;
  ackAlert: (id: string) => void;
  ackLatestAlert: () => void;
  setSurgeryTimer: (t: number) => void;
  setShowVoiceHelp: (b: boolean) => void;

  /** Apply a directive from Nael (filtered by control mode + lock). */
  applyDirective: (d: Directive) => boolean;
  reset: () => void;

  // Legacy compatibility: maps to layoutState
  layout: string;
  setLayout: (l: string) => void;
};

const DEFAULTS = {
  layoutState: "theatre_overview" as LayoutState,
  previousLayoutState: "theatre_overview" as LayoutState,
  focusedCamera: "cam1" as CameraId,
  panels: { transcript: true, vitals: true, alerts: true, cameras: true, nael: true },
  naelState: "idle" as NaelState,
  activePillar: null as PillarId | null,
  overlays: { arteries: false, veins: false, nerves: false, ducts: false, marma: false },
  overlayItems: [] as OverlayItem[],
  knowledgePanel: { open: false, pillar: null, content: null } as KnowledgePanelState,
  instrumentCount: { deployed: 0, accounted: 0, matched: true } as InstrumentCountState,
  retractionTimers: [] as RetractionTimerState[],
  alertQueue: [] as ShalyaAlert[],
  controlMode: "dynamic" as ControlMode,
  voiceListening: false,
  lastIntent: null as string | null,
  layoutLocked: false,
  phase: "preparation",
  surgeryTimer: 0,
  showVoiceHelp: false,
  showRecIndicator: true,
};

// Layout state → legacy layout name mapping for backward compat
function layoutStateToLegacy(ls: LayoutState): string {
  switch (ls) {
    case "theatre_overview": return "grid";
    case "surgeon_focus": return "focus";
    case "anatomy_overlay": return "focus";
    case "haemorrhage_alert": return "cinema";
    case "vital_alert": return "focus";
    case "knowledge_display": return "focus";
    case "pharmacokinetics": return "vitals";
    default: return "grid";
  }
}

export const useDirector = create<DirectorState>((set, get) => ({
  ...DEFAULTS,

  // Legacy compat
  layout: "grid",
  setLayout: (l) => {
    const map: Record<string, LayoutState> = {
      grid: "theatre_overview",
      focus: "surgeon_focus",
      cinema: "surgeon_focus",
      vitals: "theatre_overview",
      transcript: "theatre_overview",
    };
    const ls = map[l] || "theatre_overview";
    set({ layoutState: ls, layout: l });
  },

  // ── Layout ──
  setLayoutState: (l) =>
    set((s) => ({
      previousLayoutState: s.layoutState,
      layoutState: l,
      layout: layoutStateToLegacy(l),
    })),
  setFocus: (c) => set({ focusedCamera: c }),
  togglePanel: (p) =>
    set((s) => ({ panels: { ...s.panels, [p]: !s.panels[p] } })),
  setPanel: (p, v) =>
    set((s) => ({ panels: { ...s.panels, [p]: v } })),

  // ── Voice ──
  setControlMode: (m) => set({ controlMode: m }),
  setVoiceListening: (b) => set({ voiceListening: b }),
  setLastIntent: (s) => set({ lastIntent: s }),
  setLayoutLocked: (b) => set({ layoutLocked: b }),

  // ── Phase ──
  setPhase: (p) => set({ phase: p }),
  setSurgeryTimer: (t) => set({ surgeryTimer: t }),

  // ── Nael state ──
  setNaelState: (s) => set({ naelState: s }),
  setActivePillar: (p) => set({ activePillar: p }),

  // ── Overlays ──
  setOverlay: (type, show) =>
    set((s) => ({
      overlays: { ...s.overlays, [type]: show },
      layoutState: show ? "anatomy_overlay" : s.layoutState,
    })),
  setAllOverlays: (show) =>
    set((s) => ({
      overlays: { arteries: show, veins: show, nerves: show, ducts: show, marma: show },
      layoutState: show ? "anatomy_overlay" : s.previousLayoutState,
    })),
  setOverlayItems: (items) => set({ overlayItems: items }),

  // ── Knowledge ──
  setKnowledgePanel: (pillar, content) =>
    set((s) => ({
      knowledgePanel: { open: true, pillar, content },
      previousLayoutState: s.layoutState === "knowledge_display" ? s.previousLayoutState : s.layoutState,
      layoutState: "knowledge_display",
    })),
  closeKnowledgePanel: () =>
    set((s) => ({
      knowledgePanel: { open: false, pillar: null, content: null },
      layoutState: s.previousLayoutState,
    })),

  // ── Instruments ──
  setInstrumentCount: (data) => set({ instrumentCount: data }),

  // ── Retraction timers ──
  addRetractionTimer: (timer) =>
    set((s) => ({ retractionTimers: [...s.retractionTimers, timer] })),
  removeRetractionTimer: (id) =>
    set((s) => ({ retractionTimers: s.retractionTimers.filter((t) => t.id !== id) })),

  // ── Alerts ──
  pushAlert: (alert) =>
    set((s) => {
      const queue = [...s.alertQueue, alert].sort((a, b) => a.priority - b.priority);
      // Auto-layout switch for high-priority alerts
      let newLayout = s.layoutState;
      let prevLayout = s.previousLayoutState;
      if (alert.priority <= 2) {
        // Haemorrhage or instrument discrepancy — full takeover
        prevLayout = s.layoutState !== "haemorrhage_alert" ? s.layoutState : s.previousLayoutState;
        newLayout = "haemorrhage_alert";
      } else if (alert.priority <= 4) {
        // Monitor critical/warning
        prevLayout = s.layoutState !== "vital_alert" ? s.layoutState : s.previousLayoutState;
        newLayout = "vital_alert";
      }
      return {
        alertQueue: queue,
        layoutState: newLayout,
        previousLayoutState: prevLayout,
        activePillar: alert.pillar,
      };
    }),
  ackAlert: (id) =>
    set((s) => {
      const queue = s.alertQueue.map((a) =>
        a.id === id ? { ...a, acknowledged: true } : a,
      );
      const unacked = queue.filter((a) => !a.acknowledged);
      // If no more unacked alerts, revert layout
      const shouldRevert = unacked.length === 0;
      return {
        alertQueue: queue,
        layoutState: shouldRevert ? s.previousLayoutState : s.layoutState,
        activePillar: shouldRevert ? null : s.activePillar,
      };
    }),
  ackLatestAlert: () => {
    const { alertQueue } = get();
    const latest = alertQueue.filter((a) => !a.acknowledged).at(-1);
    if (latest) get().ackAlert(latest.id);
  },

  // ── Voice help overlay ──
  setShowVoiceHelp: (b) => set({ showVoiceHelp: b }),

  // ── Directive engine ──
  applyDirective: (d) => {
    const { controlMode, layoutLocked } = get();

    // Conservative mode forbids layout/panel/focus/overlay changes
    if (
      controlMode === "conservative" &&
      ["layout", "focus", "panel", "overlay", "overlay_all", "knowledge", "close_knowledge"].includes(d.kind)
    ) {
      return false;
    }
    if (layoutLocked && !["phase", "nael_state", "pillar", "alert", "instrument_count"].includes(d.kind)) {
      return false;
    }

    switch (d.kind) {
      case "layout":
        get().setLayoutState(d.layoutState);
        return true;
      case "focus":
        set({ focusedCamera: d.camera });
        return true;
      case "panel":
        set((s) => ({ panels: { ...s.panels, [d.panel]: d.show } }));
        return true;
      case "overlay":
        get().setOverlay(d.type, d.show);
        return true;
      case "overlay_all":
        get().setAllOverlays(d.show);
        return true;
      case "knowledge":
        get().setKnowledgePanel(d.pillar, d.content);
        return true;
      case "close_knowledge":
        get().closeKnowledgePanel();
        return true;
      case "alert":
        get().pushAlert(d.alert);
        return true;
      case "nael_state":
        set({ naelState: d.state });
        return true;
      case "pillar":
        set({ activePillar: d.pillar });
        return true;
      case "phase":
        set({ phase: d.phase });
        return true;
      case "instrument_count":
        get().setInstrumentCount(d.data);
        return true;
      case "retraction_start":
        get().addRetractionTimer(d.timer);
        return true;
      case "retraction_stop":
        get().removeRetractionTimer(d.id);
        return true;
      case "overlay_items":
        set({ overlayItems: d.items });
        return true;
    }
  },

  reset: () => set({ ...DEFAULTS, layout: "grid" }),
}));
