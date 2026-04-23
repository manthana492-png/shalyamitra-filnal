/**
 * VitalsBar — Compact vitals display for ShalyaMitra Theatre Display.
 *
 * Spec requirements:
 * - Compact horizontal bar: "HR:76↔ BP:118/72↔ SpO₂:99%↔ EtCO₂:35 Temp:36.4°C RR:14"
 * - Trend arrows based on history direction (↑ ↗ → ↘ ↓)
 * - Values animate (never jump) via AnimatedNumber
 * - Colour-coded by severity range (green/amber/red)
 * - JetBrains Mono for all data values
 * - Sparkline SVG for each vital
 */

import { cn } from "@/lib/utils";
import { AnimatedNumber } from "./AnimatedNumber";

export type Vitals = {
  hr: number;
  spo2: number;
  map: number;
  etco2: number;
  temp: number;
  rr: number;
};

const RANGES = {
  hr:    { ok: [60, 100], warn: [50, 120] },
  spo2:  { ok: [95, 100], warn: [92, 100] },
  map:   { ok: [70, 100], warn: [60, 110] },
  etco2: { ok: [35, 45],  warn: [30, 50]  },
  temp:  { ok: [36.0, 37.5], warn: [35.5, 38.0] },
  rr:    { ok: [12, 20],  warn: [10, 24]  },
} as const;

type VitalKey = keyof typeof RANGES;

function tone(value: number, key: VitalKey) {
  const r = RANGES[key];
  if (value >= r.ok[0] && value <= r.ok[1]) return "ok";
  if (value >= r.warn[0] && value <= r.warn[1]) return "warn";
  return "bad";
}

const TONE_CLASS: Record<string, string> = {
  ok: "text-success",
  warn: "text-caution",
  bad: "text-critical",
};

// Compute trend arrow from recent history
function trendArrow(history: number[]): string {
  if (history.length < 3) return "→";
  const recent = history.slice(-5);
  const first = recent[0];
  const last = recent[recent.length - 1];
  const diff = last - first;
  const range = Math.abs(first) * 0.03 || 1; // 3% threshold

  if (diff > range * 2) return "↑";
  if (diff > range) return "↗";
  if (diff < -range * 2) return "↓";
  if (diff < -range) return "↘";
  return "→";
}

function trendClass(arrow: string): string {
  if (arrow === "↑" || arrow === "↓") return "text-caution";
  if (arrow === "↗" || arrow === "↘") return "text-muted-foreground";
  return "text-success/60";
}

// Sparkline SVG
function Sparkline({ data, className }: { data: number[]; className?: string }) {
  const w = 64, h = 20;
  const safeData = data.length > 0 ? data.slice(-30) : [0];
  const min = Math.min(...safeData);
  const max = Math.max(...safeData);
  const range = Math.max(1, max - min);
  const points = safeData.map((v, i, arr) => {
    const x = (i / Math.max(1, arr.length - 1)) * w;
    const y = h - ((v - min) / range) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  return (
    <svg width={w} height={h} className={cn("opacity-70 shrink-0", className)}>
      <polyline points={points} fill="none" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

// Individual vital cell
function VitalCell({
  label, value, unit, k, history, decimals = 0,
}: {
  label: string;
  value: number;
  unit: string;
  k: VitalKey;
  history: number[];
  decimals?: number;
}) {
  const t = tone(value, k);
  const arrow = trendArrow(history);

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 min-w-0">
      <span className="text-mono text-[10px] uppercase tracking-[0.2em] text-primary/60 shrink-0">
        {label}
      </span>
      <AnimatedNumber
        value={value}
        decimals={decimals}
        className={cn(
          "text-mono text-lg font-bold tabular-nums shrink-0",
          TONE_CLASS[t],
          t === "bad" && "animate-hud-flicker",
        )}
      />
      <span className="text-[10px] text-muted-foreground shrink-0">{unit}</span>
      <span className={cn("text-sm shrink-0", trendClass(arrow))}>{arrow}</span>
      <Sparkline data={history} className={TONE_CLASS[t]} />
    </div>
  );
}

export function VitalsBar({
  current,
  histories,
  compact = true,
}: {
  current: Vitals;
  histories: { hr: number[]; spo2: number[]; map: number[]; etco2: number[] };
  compact?: boolean;
}) {
  // Extend histories with temp/rr (we may not have full histories for these yet)
  const tempHist = (histories as any).temp || [current.temp];
  const rrHist = (histories as any).rr || [current.rr];

  if (compact) {
    // Compact horizontal bar (spec: Theatre Overview default)
    return (
      <div className="hud-frame hud-corners relative">
        <span className="corner-tr" />
        <span className="corner-bl" />
        <div className="flex flex-wrap items-center divide-x divide-border/40">
          <VitalCell label="HR" value={current.hr} unit="bpm" k="hr" history={histories.hr} />
          <VitalCell label="SpO₂" value={current.spo2} unit="%" k="spo2" history={histories.spo2} />
          <VitalCell label="MAP" value={current.map} unit="mmHg" k="map" history={histories.map} />
          <VitalCell label="EtCO₂" value={current.etco2} unit="mmHg" k="etco2" history={histories.etco2} />
          <VitalCell label="Temp" value={current.temp} unit="°C" k="temp" history={tempHist} decimals={1} />
          <VitalCell label="RR" value={current.rr} unit="/min" k="rr" history={rrHist} />
        </div>
      </div>
    );
  }

  // Expanded 2×3 grid (for vital_alert or expanded view)
  return (
    <div className="grid grid-cols-3 gap-2">
      {[
        { label: "HR", value: current.hr, unit: "bpm", k: "hr" as VitalKey, history: histories.hr },
        { label: "SpO₂", value: current.spo2, unit: "%", k: "spo2" as VitalKey, history: histories.spo2 },
        { label: "MAP", value: current.map, unit: "mmHg", k: "map" as VitalKey, history: histories.map },
        { label: "EtCO₂", value: current.etco2, unit: "mmHg", k: "etco2" as VitalKey, history: histories.etco2 },
        { label: "Temp", value: current.temp, unit: "°C", k: "temp" as VitalKey, history: tempHist, decimals: 1 },
        { label: "RR", value: current.rr, unit: "/min", k: "rr" as VitalKey, history: rrHist },
      ].map((v) => (
        <div key={v.label} className="hud-frame hud-corners relative p-3">
          <span className="corner-tr" />
          <span className="corner-bl" />
          <div className="flex items-center justify-between">
            <span className="text-mono text-[9px] uppercase tracking-[0.25em] text-primary/70">{v.label}</span>
            <span className="text-[9px] text-muted-foreground">{v.unit}</span>
          </div>
          <div className="mt-1 flex items-baseline justify-between gap-2">
            <AnimatedNumber
              value={v.value}
              decimals={v.decimals || 0}
              className={cn(
                "text-mono text-2xl font-semibold tabular-nums",
                TONE_CLASS[tone(v.value, v.k)],
                tone(v.value, v.k) === "bad" && "animate-hud-flicker",
              )}
            />
            <span className={cn("text-sm", trendClass(trendArrow(v.history)))}>
              {trendArrow(v.history)}
            </span>
            <Sparkline data={v.history} className={TONE_CLASS[tone(v.value, v.k)]} />
          </div>
        </div>
      ))}
    </div>
  );
}
