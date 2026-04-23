/**
 * SurgeryTimeline — Horizontal event timeline bar.
 * Pillar-coloured dots marking events. Current time indicator.
 */

import { useDirector } from "@/lib/director";
import { PILLARS, type PillarId } from "@/lib/pillars";
import { Clock } from "lucide-react";

export type TimelineEvent = {
  at: number;
  pillar: PillarId;
  label: string;
};

export function SurgeryTimeline({
  events,
  duration,
}: {
  events: TimelineEvent[];
  duration: number;
}) {
  const surgeryTimer = useDirector((s) => s.surgeryTimer);
  const progress = Math.min(surgeryTimer / Math.max(duration, 1), 1);

  return (
    <div className="w-full px-4 py-2">
      <div className="flex items-center gap-2 mb-1.5">
        <Clock className="h-3 w-3 text-muted-foreground" />
        <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
          Surgery Timeline
        </span>
      </div>
      <div className="relative h-3 bg-surface-3 rounded-full overflow-visible">
        {/* Progress fill */}
        <div
          className="absolute top-0 left-0 h-full rounded-full bg-primary/30 transition-all duration-1000"
          style={{ width: `${progress * 100}%` }}
        />
        {/* Current position indicator */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary shadow-glow transition-all duration-1000"
          style={{ left: `calc(${progress * 100}% - 6px)` }}
        />
        {/* Event dots */}
        {events.map((ev, i) => {
          const pos = ev.at / Math.max(duration, 1);
          return (
            <div
              key={i}
              className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full transition-opacity"
              style={{
                left: `calc(${pos * 100}% - 4px)`,
                backgroundColor: `hsl(var(${PILLARS[ev.pillar]?.cssVar || "--pillar-nael"}))`,
                opacity: pos <= progress ? 1 : 0.3,
              }}
              title={`${ev.label} (T+${Math.floor(ev.at / 60)}:${String(ev.at % 60).padStart(2, "0")})`}
            />
          );
        })}
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-[9px] font-mono text-muted-foreground">T+00:00</span>
        <span className="text-[9px] font-mono text-muted-foreground">
          T+{String(Math.floor(duration / 60)).padStart(2, "0")}:{String(duration % 60).padStart(2, "0")}
        </span>
      </div>
    </div>
  );
}

export default SurgeryTimeline;
