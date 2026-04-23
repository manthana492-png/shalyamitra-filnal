/**
 * RetractionTimer — floating retractor nerve-compression tracker.
 *
 * Shows progress bar: green → yellow → amber → red as time approaches threshold.
 * Pulses and fires alert at threshold.
 */

import { useDirector } from "@/lib/director";
import { Timer } from "lucide-react";

function progressColor(ratio: number): string {
  if (ratio < 0.5) return "bg-success";
  if (ratio < 0.75) return "bg-caution";
  if (ratio < 0.9) return "bg-warning";
  return "bg-critical";
}

function progressBorder(ratio: number): string {
  if (ratio < 0.75) return "border-border";
  if (ratio < 0.9) return "border-warning/40";
  return "border-critical/40";
}

export function RetractionTimer() {
  const { retractionTimers, surgeryTimer } = useDirector();

  if (retractionTimers.length === 0) return null;

  return (
    <div className="fixed bottom-6 left-6 z-40 space-y-2 max-w-xs">
      {retractionTimers.map((timer) => {
        const elapsed = (surgeryTimer - timer.startedAt) / 60; // minutes
        const ratio = Math.min(elapsed / timer.thresholdMinutes, 1);
        const atThreshold = ratio >= 1;

        return (
          <div
            key={timer.id}
            className={`
              glass-panel px-3 py-2.5 rounded-lg border
              ${progressBorder(ratio)}
              ${atThreshold ? "animate-hud-pulse" : ""}
            `}
          >
            <div className="flex items-center gap-2 mb-1.5">
              <Timer className="h-3 w-3 text-muted-foreground" />
              <span className="text-xs text-foreground/80 truncate">{timer.structure}</span>
            </div>
            <div className="h-1.5 rounded-full bg-surface-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${progressColor(ratio)}`}
                style={{ width: `${ratio * 100}%` }}
              />
            </div>
            <div className="flex justify-between mt-1">
              <span className="text-[10px] font-mono text-muted-foreground">
                {elapsed.toFixed(1)}min
              </span>
              <span className="text-[10px] font-mono text-muted-foreground">
                {timer.thresholdMinutes}min
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default RetractionTimer;
