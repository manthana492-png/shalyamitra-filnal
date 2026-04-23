/**
 * CameraGrid — 7-state layout engine.
 *
 * Renders the camera array differently based on director.layoutState:
 *  - theatre_overview   : 3 equal cameras in a grid
 *  - surgeon_focus      : focused cam 2/3 width + 2 PiP on right
 *  - anatomy_overlay    : surgeon_focus with OverlayCanvas active
 *  - vital_alert        : focused cam + amber border flash
 *  - haemorrhage_alert  : focused cam full + red pulsing border
 *  - knowledge_display  : focused cam only (KnowledgePanel renders alongside)
 *  - pharmacokinetics   : PKDashboard (rendered by SessionConsole, grid hidden)
 */

import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useDirector, type CameraId, type LayoutState } from "@/lib/director";
import { Camera, Maximize2, Minimize2, Lock, ScanLine, Monitor, Radio } from "lucide-react";
import { connectCamera, type CameraStreamHandle, type CameraSource } from "@/lib/webrtc";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Webcam icon compatibility
const Webcam = Camera;

const SOURCE_ICON: Record<CameraSource, typeof Camera> = {
  placeholder: Monitor,
  webcam: Webcam,
  webrtc: Radio,
};

const SOURCE_LABEL: Record<CameraSource, string> = {
  placeholder: "Placeholder",
  webcam: "Device webcam",
  webrtc: "WebRTC (GPU relay)",
};

// Camera identity — label and accent colour
const CAMERA_META: Record<CameraId, { label: string; detail: string; accent: string }> = {
  cam1: { label: "LAPAROSCOPE", detail: "Surgical view · 1080p", accent: "hsl(var(--pillar-nael))" },
  cam2: { label: "OVERHEAD", detail: "Theatre overview · 4K", accent: "hsl(var(--pillar-monitor))" },
  cam3: { label: "PATIENT", detail: "Anaesthesia monitor · OCR", accent: "hsl(var(--pillar-sentinel))" },
};

type CameraTileProps = {
  id: CameraId;
  focused: boolean;
  onFocus: () => void;
  compact?: boolean;
  alertState?: "haemorrhage" | "vital" | null;
};

function CameraTile({ id, focused, onFocus, compact, alertState }: CameraTileProps) {
  const { id: sessionId } = useParams<{ id: string }>();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [source, setSource] = useState<CameraSource>("placeholder");
  const [handle, setHandle] = useState<CameraStreamHandle | null>(null);
  const meta = CAMERA_META[id];

  useEffect(() => {
    let cancelled = false;
    let h: CameraStreamHandle | null = null;
    setHandle(null);
    connectCamera(id, source, sessionId)
      .then((next) => {
        if (cancelled) { next.close(); return; }
        h = next;
        setHandle(next);
        if (videoRef.current && next.stream) videoRef.current.srcObject = next.stream;
      })
      .catch(() => {});
    return () => { cancelled = true; h?.close(); };
  }, [id, source, sessionId]);

  useEffect(() => {
    if (videoRef.current && handle?.stream && videoRef.current.srcObject !== handle.stream) {
      videoRef.current.srcObject = handle.stream;
    }
  }, [handle?.stream]);

  const status = handle?.status ?? "idle";
  const SourceIcon = SOURCE_ICON[source];

  // Alert border styles
  const alertBorder = alertState === "haemorrhage"
    ? "ring-2 ring-pillar-haemorrhage shadow-[0_0_0_2px_hsl(var(--pillar-haemorrhage))] animate-hud-pulse"
    : alertState === "vital"
    ? "ring-2 ring-pillar-monitor animate-hud-pulse"
    : "";

  return (
    <div
      className={cn(
        "hud-frame hud-corners group relative aspect-video w-full overflow-hidden cursor-pointer",
        "transition-all duration-500",
        focused ? "ring-1 shadow-glow-strong" : "hover:ring-1 hover:ring-primary/40",
        alertBorder,
      )}
      style={focused ? { borderColor: meta.accent, boxShadow: `0 0 24px -4px ${meta.accent}88` } : {}}
      onClick={onFocus}
    >
      <span className="corner-tr" style={{ borderColor: meta.accent }} />
      <span className="corner-bl" style={{ borderColor: meta.accent }} />

      {/* Camera feed / placeholder */}
      <div className="absolute inset-0 bg-black hud-grid">
        {handle?.stream && (
          <video ref={videoRef} autoPlay muted playsInline className="h-full w-full object-cover opacity-90" />
        )}
        {!handle?.stream && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative">
              <div className="h-16 w-16 rounded-full border animate-hud-orbit" style={{ borderColor: `${meta.accent}50` }} />
              <div className="absolute inset-2 rounded-full border animate-hud-orbit-rev" style={{ borderColor: `${meta.accent}30` }} />
              <div className="absolute inset-0 flex items-center justify-center">
                <Camera className={cn("text-primary/50", compact ? "h-4 w-4" : "h-6 w-6")} />
              </div>
            </div>
          </div>
        )}
        <div className="hud-sweep" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-black/30 pointer-events-none" />
      </div>

      {/* Top-left label */}
      <div className="absolute top-2 left-2 flex items-center gap-1.5 text-mono text-[10px] tracking-[0.2em] pointer-events-none" style={{ color: meta.accent }}>
        <span className={cn("pulse-dot", status === "live" ? "live" : "nael")} />
        <span className="uppercase text-glow">{id.toUpperCase()} · {meta.label}</span>
      </div>

      {/* Source dropdown */}
      {!compact && (
        <div className="absolute top-1.5 right-1.5 z-10">
          <DropdownMenu>
            <DropdownMenuTrigger
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 rounded border border-primary/30 bg-background/70 backdrop-blur-sm px-1.5 py-0.5 text-mono text-[9px] uppercase tracking-wider text-primary/80 hover:text-primary hover:border-primary/60 transition"
              aria-label={`Change source for ${meta.label}`}
            >
              <SourceIcon className="h-2.5 w-2.5" />
              <span className="hidden md:inline">{source}</span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="text-xs">
              {(Object.keys(SOURCE_LABEL) as CameraSource[]).map((s) => {
                const Icon = SOURCE_ICON[s];
                return (
                  <DropdownMenuItem
                    key={s}
                    onClick={(e) => { e.stopPropagation(); setSource(s); }}
                    className={cn(source === s && "text-primary")}
                  >
                    <Icon className="mr-2 h-3 w-3" />
                    {SOURCE_LABEL[s]}
                  </DropdownMenuItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}

      {/* Bottom bar */}
      <div className="absolute bottom-0 inset-x-0 px-2 py-1.5 flex items-center justify-between border-t border-primary/20 bg-background/60 backdrop-blur-sm pointer-events-none">
        <span className="text-mono text-[9px] tracking-wider text-foreground/70 uppercase">{meta.detail}</span>
        <span className="text-mono text-[9px] tracking-wider text-primary/60 flex items-center gap-1">
          {focused ? <Maximize2 className="h-2.5 w-2.5" /> : <Minimize2 className="h-2.5 w-2.5" />}
          {focused ? "FOCUSED" : "TAP"}
        </span>
      </div>
    </div>
  );
}

const ALL_CAMS: CameraId[] = ["cam1", "cam2", "cam3"];

export function CameraGrid() {
  const { layoutState, focusedCamera, setFocus, layoutLocked, setLayoutState } = useDirector();

  const handleTileFocus = (camId: CameraId) => {
    if (camId === focusedCamera && layoutState === "surgeon_focus") {
      setLayoutState("theatre_overview");
    } else {
      setFocus(camId);
      setLayoutState("surgeon_focus");
    }
  };

  // ── theatre_overview: 3 equal cameras ──────────────────────────────
  if (layoutState === "theatre_overview") {
    return (
      <div className="grid grid-cols-3 gap-2">
        {ALL_CAMS.map((c) => (
          <CameraTile key={c} id={c} focused={false} onFocus={() => handleTileFocus(c)} />
        ))}
      </div>
    );
  }

  // ── haemorrhage_alert: full-screen focused cam with red border ──────
  if (layoutState === "haemorrhage_alert") {
    const cam = focusedCamera || "cam1";
    return (
      <div className="relative">
        <CameraTile id={cam} focused onFocus={() => {}} alertState="haemorrhage" />
        {/* Mini PiP row */}
        <div className="grid grid-cols-2 gap-1.5 mt-1.5">
          {ALL_CAMS.filter((c) => c !== cam).map((c) => (
            <CameraTile key={c} id={c} focused={false} onFocus={() => handleTileFocus(c)} compact />
          ))}
        </div>
      </div>
    );
  }

  // ── vital_alert: focused cam + amber border ─────────────────────────
  if (layoutState === "vital_alert") {
    const cam = focusedCamera || "cam1";
    const others = ALL_CAMS.filter((c) => c !== cam);
    return (
      <div className="grid grid-cols-3 gap-2">
        <div className="col-span-2">
          <CameraTile id={cam} focused onFocus={() => {}} alertState="vital" />
        </div>
        <div className="flex flex-col gap-2">
          {others.map((c) => (
            <CameraTile key={c} id={c} focused={false} onFocus={() => handleTileFocus(c)} compact />
          ))}
        </div>
      </div>
    );
  }

  // ── surgeon_focus / anatomy_overlay / knowledge_display: 2/3 + PiP ──
  const cam = focusedCamera || "cam1";
  const others = ALL_CAMS.filter((c) => c !== cam);
  return (
    <div className="grid grid-cols-3 gap-2">
      <div className="col-span-2 relative">
        <CameraTile id={cam} focused onFocus={() => setLayoutState("theatre_overview")} />
      </div>
      <div className="flex flex-col gap-2">
        {others.map((c) => (
          <CameraTile key={c} id={c} focused={false} onFocus={() => handleTileFocus(c)} compact />
        ))}
        <div className="hud-frame aspect-video flex items-center justify-center text-[10px] text-mono text-primary/40 opacity-40">
          <Lock className="h-3 w-3 mr-1" /> {layoutLocked ? "LOCKED" : "AUX"}
        </div>
      </div>
    </div>
  );
}

export function CameraGridStatus() {
  const { layoutState, focusedCamera } = useDirector();
  return (
    <div className="flex items-center gap-3 text-mono text-[10px] uppercase tracking-[0.2em] text-primary/60">
      <ScanLine className="h-3 w-3" />
      <span>VISION · {layoutState.replace(/_/g, " ").toUpperCase()} · {focusedCamera.toUpperCase()}</span>
    </div>
  );
}
