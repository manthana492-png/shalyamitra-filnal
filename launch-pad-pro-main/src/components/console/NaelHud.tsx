/**
 * NaelHud — Compact voice status strip.
 *
 * Shows mic status, last wake word, and optional transcript line.
 * Replaces old VoiceHud.
 */

import { useDirector } from "@/lib/director";
import { Mic, MicOff, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";

export function NaelHud({
  micActive,
  lastTranscript,
}: {
  micActive: boolean;
  lastTranscript: string;
}) {
  const { voiceListening, naelState, lastIntent } = useDirector();

  return (
    <div className="flex items-center gap-3 px-3 py-1.5 rounded-md bg-surface-1/60 backdrop-blur-sm border border-border/50 text-xs">
      {/* Mic indicator */}
      <div className={cn(
        "flex items-center gap-1.5",
        micActive ? "text-success" : "text-muted-foreground"
      )}>
        {micActive ? <Mic className="h-3 w-3" /> : <MicOff className="h-3 w-3" />}
        <span className="font-mono text-[10px]">
          {micActive ? "MIC ON" : "MIC OFF"}
        </span>
      </div>

      {/* Connection */}
      <div className={cn(
        "flex items-center gap-1",
        voiceListening ? "text-primary" : "text-muted-foreground"
      )}>
        {voiceListening ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
      </div>

      {/* Wake word hint */}
      <span className="text-muted-foreground text-[10px] hidden sm:inline">
        Say <span className="text-primary/70 font-medium">"Nael, ..."</span>
      </span>

      {/* Last intent */}
      {lastIntent && (
        <span className="text-[10px] font-mono text-primary/50 truncate max-w-24">
          → {lastIntent}
        </span>
      )}

      {/* Live transcript */}
      {lastTranscript && (
        <span className="text-[10px] text-foreground/60 truncate max-w-48 hidden md:inline">
          {lastTranscript}
        </span>
      )}
    </div>
  );
}

export default NaelHud;
