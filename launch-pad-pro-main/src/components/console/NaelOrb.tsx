/**
 * NaelOrb — Compact AI presence indicator.
 *
 * A 48px floating indicator in the bottom-right corner showing Nael's current
 * state: idle, listening, thinking, or speaking. Always visible, always
 * positioned above all content.
 */

import { useDirector } from "@/lib/director";
import { cn } from "@/lib/utils";

export function NaelOrb() {
  const naelState = useDirector((s) => s.naelState);

  return (
    <div
      className={cn(
        "fixed bottom-6 right-6 z-50 flex items-center gap-2",
        "transition-all duration-300"
      )}
    >
      {/* State label */}
      {(naelState === "listening" || naelState === "thinking") && (
        <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-primary/70 animate-fade-in">
          {naelState === "listening" ? "LISTENING..." : "THINKING..."}
        </span>
      )}

      {/* The orb */}
      <div className="relative flex items-center justify-center w-12 h-12">
        {/* Idle: dim blue dot with slow pulse */}
        {naelState === "idle" && (
          <div className="w-3 h-3 rounded-full bg-primary/40 animate-hud-pulse" />
        )}

        {/* Listening: concentric rings expanding outward */}
        {naelState === "listening" && (
          <>
            <div className="absolute inset-0 rounded-full border border-primary/30 animate-nael-rings" />
            <div
              className="absolute inset-1 rounded-full border border-primary/20 animate-nael-rings"
              style={{ animationDelay: "0.3s" }}
            />
            <div
              className="absolute inset-2 rounded-full border border-primary/15 animate-nael-rings"
              style={{ animationDelay: "0.6s" }}
            />
            <div className="w-3 h-3 rounded-full bg-primary shadow-glow" />
          </>
        )}

        {/* Thinking: orbiting dot */}
        {naelState === "thinking" && (
          <>
            <div className="absolute inset-0 animate-nael-thinking">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-primary/80" />
            </div>
            <div
              className="absolute inset-0 animate-nael-thinking"
              style={{ animationDelay: "0.4s" }}
            >
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-primary/50" />
            </div>
            <div
              className="absolute inset-0 animate-nael-thinking"
              style={{ animationDelay: "0.8s" }}
            >
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-primary/30" />
            </div>
            <div className="w-2 h-2 rounded-full bg-primary/60" />
          </>
        )}

        {/* Speaking: amplitude bars */}
        {naelState === "speaking" && (
          <div className="flex items-center gap-[3px] h-6">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="w-[3px] rounded-full bg-primary"
                style={{
                  animation: `listening 0.8s ease-in-out infinite`,
                  animationDelay: `${i * 0.12}s`,
                  height: "100%",
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default NaelOrb;
