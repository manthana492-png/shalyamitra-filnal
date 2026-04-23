import { cn } from "@/lib/utils";
import type { StreamMode } from "@/lib/nael-stream";
import { Ear, MessageSquare, Sparkles } from "lucide-react";

const MODES: {
  id: StreamMode;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { id: "silent",    name: "SILENT",    icon: Ear           },
  { id: "reactive",  name: "REACTIVE",  icon: MessageSquare },
  { id: "proactive", name: "PROACTIVE", icon: Sparkles      },
];

export function ModeSwitcher({
  value,
  onChange,
}: {
  value: StreamMode;
  onChange: (m: StreamMode) => void;
}) {
  return (
    <div className="grid grid-cols-3 gap-1 rounded-lg border border-primary/30 bg-surface-1/60 backdrop-blur-sm p-1">
      {MODES.map((m) => {
        const active = m.id === value;
        return (
          <button
            key={m.id}
            type="button"
            onClick={() => onChange(m.id)}
            className={cn(
              "flex flex-col items-center justify-center gap-1 rounded-md px-2 py-2 transition-all",
              active
                ? "bg-primary/15 ring-1 ring-primary/60 shadow-glow"
                : "hover:bg-surface-2 text-muted-foreground hover:text-foreground",
            )}
          >
            <m.icon className={cn("h-4 w-4", active && "text-primary")} />
            <span className={cn("text-mono text-[10px] tracking-[0.18em]", active ? "text-primary" : "")}>{m.name}</span>
          </button>
        );
      })}
    </div>
  );
}
