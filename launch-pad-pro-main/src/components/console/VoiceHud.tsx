import { useDirector, type ControlMode } from "@/lib/director";
import { Mic, MicOff, Lock, Unlock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const MODES: { id: ControlMode; label: string; hint: string }[] = [
  { id: "conservative", label: "SAFE",      hint: "Voice: critical commands only" },
  { id: "dynamic",      label: "DYNAMIC",   hint: "Voice rearranges layout on command" },
  { id: "agentic",      label: "AGENTIC",   hint: "ARIA proactively re-lays-out" },
];

export function VoiceHud({
  active,
  supported,
  onToggle,
  transcript,
}: {
  active: boolean;
  supported: boolean;
  onToggle: () => void;
  transcript: string;
}) {
  const { controlMode, setControlMode, lastIntent, layoutLocked, setLayoutLocked } = useDirector();

  return (
    <div className="hud-frame hud-corners relative p-3 space-y-3">
      <span className="corner-tr" />
      <span className="corner-bl" />

      <div className="flex items-center justify-between">
        <div className="text-hud-label">VOICE CONTROL</div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setLayoutLocked(!layoutLocked)}
            title={layoutLocked ? "Unlock layout" : "Lock layout"}
            className="h-7 px-2 text-mono text-[10px] uppercase tracking-wider"
          >
            {layoutLocked ? <Lock className="h-3 w-3 mr-1 text-caution" /> : <Unlock className="h-3 w-3 mr-1 text-primary/70" />}
            {layoutLocked ? "LOCKED" : "OPEN"}
          </Button>
          <Button
            size="sm"
            variant={active ? "default" : "outline"}
            onClick={onToggle}
            disabled={!supported}
            className={cn(
              "h-7 px-2 text-mono text-[10px] uppercase tracking-wider",
              active && "bg-primary text-primary-foreground shadow-glow",
            )}
            title={supported ? (active ? "Stop listening" : "Start listening") : "Voice not supported in this browser"}
          >
            {active ? <Mic className="h-3 w-3 mr-1" /> : <MicOff className="h-3 w-3 mr-1" />}
            {active ? "LISTENING" : supported ? "STANDBY" : "N/A"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-1.5">
        {MODES.map((m) => {
          const isActive = controlMode === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setControlMode(m.id)}
              className={cn(
                "rounded-md border px-2 py-1.5 text-left transition-all",
                isActive
                  ? "border-primary/60 bg-primary/10 shadow-glow"
                  : "border-border/60 hover:border-primary/40 hover:bg-surface-2/50",
              )}
            >
              <div className={cn("text-mono text-[10px] tracking-[0.2em]", isActive ? "text-primary" : "text-muted-foreground")}>
                {m.label}
              </div>
              <div className="mt-0.5 text-[10px] text-foreground/60 leading-tight">{m.hint}</div>
            </button>
          );
        })}
      </div>

      <div className="rounded-md bg-background/60 border border-border/40 px-2.5 py-1.5 min-h-[34px]">
        <div className="text-[9px] uppercase tracking-[0.2em] text-muted-foreground mb-0.5">SAY · "ARIA …"</div>
        <div className="text-mono text-xs text-primary truncate">
          {active ? (transcript || "…") : "voice off"}
        </div>
      </div>

      {lastIntent && (
        <div className="text-mono text-[10px] uppercase tracking-wider text-success">
          ▸ {lastIntent}
        </div>
      )}
    </div>
  );
}
