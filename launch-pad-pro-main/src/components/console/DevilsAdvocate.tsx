/**
 * DevilsAdvocate — Crimson-orange conflict overlay.
 *
 * Slides down from top-centre. Transparent over camera.
 * Auto-dismisses after 15s or on verbal confirmation.
 */

import { useEffect, useState } from "react";
import { Scale } from "lucide-react";

export type AdvocateEvent = {
  question: string;
  evidence: string;
  pillarSource: string;
};

export function DevilsAdvocate({
  event,
  onDismiss,
}: {
  event: AdvocateEvent | null;
  onDismiss: () => void;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (event) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(onDismiss, 400);
      }, 15000);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [event, onDismiss]);

  if (!event) return null;

  return (
    <div
      className={`
        fixed top-20 left-1/2 -translate-x-1/2 z-40
        max-w-lg w-[90vw]
        transition-all duration-500
        ${visible ? "translate-y-0 opacity-100" : "-translate-y-8 opacity-0"}
      `}
    >
      <div
        className="glass-panel rounded-xl p-4"
        style={{
          borderColor: "hsl(var(--pillar-advocate) / 0.4)",
          boxShadow: "var(--shadow-advocate), 0 20px 40px rgba(0,0,0,0.4)",
          animation: "viewport-pulse-orange 2.5s ease-in-out infinite",
        }}
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <Scale className="h-4 w-4" style={{ color: "hsl(var(--pillar-advocate))" }} />
          <span
            className="text-[10px] font-mono uppercase tracking-[0.2em]"
            style={{ color: "hsl(var(--pillar-advocate))" }}
          >
            DEVIL'S ADVOCATE
          </span>
        </div>

        {/* Conflict question */}
        <p className="text-sm text-foreground/95 leading-relaxed mb-3">
          {event.question}
        </p>

        {/* Evidence card */}
        <div className="rounded-md border border-border bg-surface-2/40 px-3 py-2">
          <p className="text-[10px] text-muted-foreground mb-1">EVIDENCE — {event.pillarSource}</p>
          <p className="text-xs text-foreground/70">{event.evidence}</p>
        </div>

        {/* Dismiss hint */}
        <p className="text-[10px] text-muted-foreground mt-3 text-center">
          Say <span className="text-primary font-medium">"Nael, acknowledged"</span> or auto-dismiss in 15s
        </p>
      </div>
    </div>
  );
}

export default DevilsAdvocate;
