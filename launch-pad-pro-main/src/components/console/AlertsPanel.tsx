/**
 * AlertsPanel — Pillar-aware alert display.
 *
 * Each alert card has a coloured left border matching the intelligence pillar.
 * Critical alerts trigger viewport border pulse.
 */

import { useDirector, type LayoutState } from "@/lib/director";
import { PILLARS, type PillarId, type ShalyaAlert } from "@/lib/pillars";
import { cn } from "@/lib/utils";
import { Bell, CheckCircle } from "lucide-react";

function fmt(t: number) {
  const m = Math.floor(t / 60).toString().padStart(2, "0");
  const s = Math.floor(t % 60).toString().padStart(2, "0");
  return `T+${m}:${s}`;
}

const SEVERITY_STYLES: Record<string, string> = {
  info: "border-l-info bg-info/5",
  caution: "border-l-caution bg-caution/5",
  warning: "border-l-warning bg-warning/5",
  critical: "border-l-critical bg-critical/5",
};

export function AlertsPanel({ alerts }: { alerts: ShalyaAlert[] }) {
  const { ackAlert } = useDirector();
  const visibleAlerts = alerts.filter((a) => !a.acknowledged).slice(-8);

  if (visibleAlerts.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        <Bell className="mr-2 h-4 w-4" />
        No active alerts
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-3 space-y-2">
      {visibleAlerts.map((alert) => {
        const pillar = PILLARS[alert.pillar];
        const PillarIcon = pillar?.icon;

        return (
          <div
            key={alert.id}
            className={cn(
              "rounded-md border-l-[3px] border border-border p-3 animate-fade-in",
              SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.info,
            )}
            style={{
              borderLeftColor: `hsl(var(${pillar?.cssVar || "--pillar-nael"}))`,
            }}
          >
            {/* Pillar badge + time */}
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-1.5">
                {PillarIcon && (
                  <PillarIcon
                    className="h-3 w-3"
                    style={{ color: `hsl(var(${pillar?.cssVar || "--pillar-nael"}))` }}
                  />
                )}
                <span
                  className="text-[9px] font-mono uppercase tracking-wider"
                  style={{ color: `hsl(var(${pillar?.cssVar || "--pillar-nael"}))` }}
                >
                  {pillar?.shortName || "Nael"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-muted-foreground">{fmt(alert.at)}</span>
                <button
                  onClick={() => ackAlert(alert.id)}
                  className="rounded p-0.5 hover:bg-surface-3 transition-colors"
                  title="Acknowledge"
                >
                  <CheckCircle className="h-3 w-3 text-muted-foreground hover:text-success" />
                </button>
              </div>
            </div>

            {/* Title */}
            <p className="text-sm font-medium text-foreground">{alert.title}</p>

            {/* Body */}
            <p className="mt-1 text-xs text-foreground/70 leading-relaxed">{alert.body}</p>
          </div>
        );
      })}
    </div>
  );
}

export default AlertsPanel;
