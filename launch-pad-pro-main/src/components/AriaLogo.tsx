import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export function AriaLogo({ className, withWordmark = true }: { className?: string; withWordmark?: boolean }) {
  return (
    <Link to="/" className={cn("inline-flex items-center gap-2.5 group", className)}>
      <span className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary shadow-glow">
        <span className="absolute inset-0 rounded-lg bg-gradient-primary opacity-60 blur-md group-hover:opacity-90 transition-opacity" />
        <svg viewBox="0 0 24 24" className="relative h-5 w-5 text-primary-foreground" fill="none">
          <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
          <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          <path d="M12 3v3M12 18v3M3 12h3M18 12h3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </span>
      {withWordmark && (
        <div className="flex flex-col leading-none">
          <span className="text-display text-base font-semibold tracking-tight">ARIA</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Surgical Copilot</span>
        </div>
      )}
    </Link>
  );
}
