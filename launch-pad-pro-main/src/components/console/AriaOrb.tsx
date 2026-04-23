import { cn } from "@/lib/utils";

export type AriaState = "idle" | "listening" | "speaking" | "thinking";

/**
 * Holographic ARIA orb — concentric rings with rotating outer glyph,
 * inner pulse colored by state.
 */
export function AriaOrb({
  state,
  size = "md",
  onClick,
}: {
  state: AriaState;
  size?: "sm" | "md" | "lg";
  onClick?: () => void;
}) {
  const dim =
    size === "lg" ? "h-36 w-36"
    : size === "md" ? "h-24 w-24"
    : "h-14 w-14";

  const colorClass =
    state === "speaking" ? "text-primary"
    : state === "listening" ? "text-primary"
    : state === "thinking" ? "text-info"
    : "text-muted-foreground";

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn("relative flex items-center justify-center", dim)}
      aria-label="ARIA voice"
    >
      {/* Outer rotating ring with tick marks */}
      <svg
        viewBox="0 0 100 100"
        className={cn(
          "absolute inset-0 animate-hud-orbit",
          colorClass,
          state === "idle" ? "opacity-30" : "opacity-80",
        )}
      >
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="0.4" />
        {Array.from({ length: 36 }).map((_, i) => {
          const a = (i / 36) * Math.PI * 2;
          const x1 = 50 + Math.cos(a) * 44;
          const y1 = 50 + Math.sin(a) * 44;
          const x2 = 50 + Math.cos(a) * (i % 3 === 0 ? 40 : 42);
          const y2 = 50 + Math.sin(a) * (i % 3 === 0 ? 40 : 42);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="currentColor" strokeWidth={i % 9 === 0 ? "0.9" : "0.4"} />;
        })}
      </svg>

      {/* Counter-rotating inner ring */}
      <svg
        viewBox="0 0 100 100"
        className={cn(
          "absolute inset-3 animate-hud-orbit-rev",
          colorClass,
          state === "idle" ? "opacity-25" : "opacity-60",
        )}
      >
        <circle cx="50" cy="50" r="38" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 6" />
        <circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="1 3" />
      </svg>

      {/* Core */}
      <span
        className={cn(
          "relative z-10 rounded-full transition-all",
          size === "lg" ? "h-12 w-12" : size === "md" ? "h-9 w-9" : "h-5 w-5",
          state === "speaking"  && "bg-gradient-primary shadow-glow-strong animate-hud-pulse",
          state === "listening" && "bg-primary/80 shadow-glow animate-pulse",
          state === "thinking"  && "bg-info/70 shadow-glow animate-pulse",
          state === "idle"      && "bg-surface-3 border border-primary/20",
        )}
      />

      {/* Listening EQ bars */}
      {state === "listening" && (
        <span className="absolute -bottom-3 left-1/2 -translate-x-1/2 flex items-end gap-0.5 h-3">
          {[0, 1, 2, 3, 4].map((i) => (
            <span
              key={i}
              className="w-0.5 h-full bg-primary rounded-full origin-bottom animate-listening"
              style={{ animationDelay: `${i * 110}ms` }}
            />
          ))}
        </span>
      )}
    </button>
  );
}
