/**
 * VitalAlertPanel — Expanded vital display for vital_alert layout state.
 *
 * Spec: "Vital panel expands to 40% screen — declining value at 96px
 * with animated arrow. Real-time trend graph (SVG) with projected
 * dashed line showing AI prediction. Plain language prediction text."
 */

import { useMemo } from "react";
import { AnimatedNumber } from "./AnimatedNumber";
import { cn } from "@/lib/utils";

type VitalAlertPanelProps = {
  label: string;
  value: number;
  unit: string;
  history: number[];
  className?: string;
};

// Simple linear regression for projection
function linearProject(data: number[], steps: number): number[] {
  const n = data.length;
  if (n < 3) return [];
  const recent = data.slice(-20);
  const rn = recent.length;
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
  for (let i = 0; i < rn; i++) {
    sumX += i;
    sumY += recent[i];
    sumXY += i * recent[i];
    sumX2 += i * i;
  }
  const slope = (rn * sumXY - sumX * sumY) / (rn * sumX2 - sumX * sumX);
  const intercept = (sumY - slope * sumX) / rn;
  const lastX = rn - 1;
  const projected: number[] = [];
  for (let i = 1; i <= steps; i++) {
    projected.push(slope * (lastX + i) + intercept);
  }
  return projected;
}

function predictionText(label: string, history: number[], projected: number[]): string {
  if (projected.length === 0 || history.length < 5) return "";
  const recent = history.slice(-10);
  const ratePerStep = (recent[recent.length - 1] - recent[0]) / recent.length;
  const direction = ratePerStep > 0 ? "rising" : "declining";
  const absRate = Math.abs(ratePerStep).toFixed(1);
  const projectedVal = Math.round(projected[projected.length - 1]);
  return `${label} ${direction} ~${absRate}/min over ${recent.length} readings. Projected: ${projectedVal} in ${projected.length} min.`;
}

export function VitalAlertPanel({ label, value, unit, history, className }: VitalAlertPanelProps) {
  const projected = useMemo(() => linearProject(history, 10), [history]);
  const prediction = useMemo(() => predictionText(label, history, projected), [label, history, projected]);

  // Determine if declining or rising
  const trend = history.length >= 3
    ? history[history.length - 1] - history[history.length - 3]
    : 0;
  const isDecline = trend < 0;
  const arrowRotation = isDecline ? "rotate-180" : trend > 0 ? "" : "rotate-90";

  // SVG trend graph
  const w = 320, h = 140;
  const allData = [...history.slice(-30), ...projected];
  const min = Math.min(...allData) - 2;
  const max = Math.max(...allData) + 2;
  const range = Math.max(1, max - min);

  const histPoints = history.slice(-30).map((v, i, arr) => {
    const x = (i / Math.max(1, arr.length + projected.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const projPoints = projected.map((v, i) => {
    const x = ((history.slice(-30).length + i) / Math.max(1, history.slice(-30).length + projected.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  // Combine last history point + projected for dashed line
  const projLine = histPoints.length > 0
    ? [histPoints[histPoints.length - 1], ...projPoints].join(" ")
    : projPoints.join(" ");

  return (
    <div className={cn(
      "hud-frame hud-corners relative p-6 border-pillar-monitor",
      className,
    )}>
      <span className="corner-tr" />
      <span className="corner-bl" />

      {/* Label */}
      <div className="text-mono text-[10px] uppercase tracking-[0.3em] text-pillar-monitor mb-2">
        MONITOR SENTINEL — {label} ALERT
      </div>

      {/* Large value + arrow */}
      <div className="flex items-center gap-4 mb-4">
        <AnimatedNumber
          value={value}
          className="text-mono text-[72px] md:text-[96px] font-bold tabular-nums text-caution leading-none"
        />
        <span className="text-2xl text-muted-foreground">{unit}</span>
        <svg
          viewBox="0 0 24 24"
          className={cn(
            "w-12 h-12 text-caution transition-transform duration-500",
            arrowRotation,
          )}
          fill="none"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path d="M12 5v14M5 12l7-7 7 7" />
        </svg>
      </div>

      {/* Trend graph */}
      <div className="glass-panel p-4 mb-4">
        <div className="text-mono text-[9px] uppercase tracking-[0.2em] text-muted-foreground mb-2">
          TREND — LAST 30 READINGS + 10 MIN PROJECTION
        </div>
        <svg width={w} height={h} className="w-full" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
          {/* Grid lines */}
          {[0.25, 0.5, 0.75].map((frac) => (
            <line
              key={frac}
              x1={0} y1={h * frac} x2={w} y2={h * frac}
              stroke="hsl(var(--border))" strokeWidth={0.5}
            />
          ))}
          {/* History line (solid) */}
          <polyline
            points={histPoints.join(" ")}
            fill="none"
            stroke="hsl(var(--pillar-monitor))"
            strokeWidth={2}
          />
          {/* Projected line (dashed) */}
          {projPoints.length > 0 && (
            <polyline
              points={projLine}
              fill="none"
              stroke="hsl(var(--pillar-monitor))"
              strokeWidth={1.5}
              strokeDasharray="6 4"
              opacity={0.6}
            />
          )}
          {/* Current value marker */}
          {histPoints.length > 0 && (
            <circle
              cx={histPoints[histPoints.length - 1].split(",")[0]}
              cy={histPoints[histPoints.length - 1].split(",")[1]}
              r={4}
              fill="hsl(var(--pillar-monitor))"
            />
          )}
          {/* Projected endpoint marker */}
          {projPoints.length > 0 && (
            <>
              <circle
                cx={projPoints[projPoints.length - 1].split(",")[0]}
                cy={projPoints[projPoints.length - 1].split(",")[1]}
                r={4}
                fill="hsl(var(--pillar-monitor))"
                opacity={0.5}
              />
              <text
                x={Number(projPoints[projPoints.length - 1].split(",")[0]) - 8}
                y={Number(projPoints[projPoints.length - 1].split(",")[1]) - 8}
                fill="hsl(var(--pillar-monitor))"
                fontSize={11}
                fontFamily="var(--font-mono)"
                opacity={0.7}
              >
                ← {Math.round(projected[projected.length - 1])}
              </text>
            </>
          )}
        </svg>
      </div>

      {/* Prediction text */}
      {prediction && (
        <div className="glass-panel p-3 text-sm text-foreground/90">
          <span className="text-pillar-monitor font-medium">Prediction: </span>
          {prediction}
        </div>
      )}
    </div>
  );
}

export default VitalAlertPanel;
