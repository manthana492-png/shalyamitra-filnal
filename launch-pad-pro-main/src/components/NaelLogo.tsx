import { cn } from "@/lib/utils";

interface NaelLogoProps {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  className?: string;
}

/**
 * ShalyaMitra / Nael brand mark.
 * A geometric "N" inside a hexagonal frame with glow accent.
 */
export function NaelLogo({ size = "md", showWordmark = true, className }: NaelLogoProps) {
  const dims = { sm: 28, md: 36, lg: 48 }[size];

  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg
        width={dims}
        height={dims}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0"
      >
        {/* Hexagonal frame */}
        <path
          d="M24 2L44 14V34L24 46L4 34V14L24 2Z"
          stroke="hsl(217 100% 62%)"
          strokeWidth="1.5"
          fill="hsl(217 100% 62% / 0.06)"
          className="drop-shadow-[0_0_12px_hsl(217_100%_62%_/_0.4)]"
        />
        {/* Inner glow */}
        <path
          d="M24 8L40 17V31L24 40L8 31V17L24 8Z"
          fill="hsl(217 100% 62% / 0.08)"
          stroke="hsl(217 100% 62% / 0.2)"
          strokeWidth="0.5"
        />
        {/* Letter N */}
        <text
          x="24"
          y="30"
          textAnchor="middle"
          fill="hsl(217 100% 62%)"
          fontSize="22"
          fontWeight="700"
          fontFamily="var(--font-sans)"
          className="drop-shadow-[0_0_8px_hsl(217_100%_62%_/_0.6)]"
        >
          N
        </text>
      </svg>
      {showWordmark && (
        <div className="flex flex-col leading-none">
          <span className={cn(
            "font-semibold text-glow tracking-tight",
            size === "sm" ? "text-sm" : size === "md" ? "text-base" : "text-lg"
          )}>
            ShalyaMitra
          </span>
          <span className="text-hud-label mt-0.5" style={{ fontSize: "8px", letterSpacing: "0.25em" }}>
            SURGICAL INTELLIGENCE
          </span>
        </div>
      )}
    </div>
  );
}

export default NaelLogo;
