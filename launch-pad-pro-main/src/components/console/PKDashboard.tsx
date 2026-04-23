/**
 * PKDashboard — Pharmacokinetics TIVA Dashboard.
 *
 * Full-screen view showing propofol + remifentanil concentration curves,
 * drug log, and emergence prediction. Violet (Pharmacist) accent.
 */

import { Pill, TrendingDown } from "lucide-react";
import { useDirector } from "@/lib/director";

// Mock PK data generator using exponential decay
function generatePKCurve(points: number = 30): { plasma: number[]; effectSite: number[] } {
  const plasma: number[] = [];
  const effectSite: number[] = [];
  for (let i = 0; i < points; i++) {
    const t = i / points;
    // Bolus followed by infusion steady state
    const bolus = 4 * Math.exp(-t * 6);
    const infusion = 3 * (1 - Math.exp(-t * 3));
    const p = bolus + infusion + 0.2 * Math.sin(t * 12);
    plasma.push(Math.max(0, p));
    effectSite.push(Math.max(0, p * 0.8 - 0.3 * Math.exp(-t * 2)));
  }
  return { plasma, effectSite };
}

function SVGChart({
  plasma,
  effectSite,
  label,
  unit,
  model,
  color,
}: {
  plasma: number[];
  effectSite: number[];
  label: string;
  unit: string;
  model: string;
  color: string;
}) {
  const max = Math.max(...plasma, ...effectSite, 1);
  const w = 400;
  const h = 120;
  const toX = (i: number) => (i / (plasma.length - 1)) * w;
  const toY = (v: number) => h - (v / max) * (h - 10);

  const plasmaPath = plasma.map((v, i) => `${i === 0 ? "M" : "L"} ${toX(i)} ${toY(v)}`).join(" ");
  const esPath = effectSite.map((v, i) => `${i === 0 ? "M" : "L"} ${toX(i)} ${toY(v)}`).join(" ");

  return (
    <div className="glass-panel p-3 rounded-lg" style={{ borderColor: `${color}33` }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium" style={{ color }}>{label}</span>
        <span className="text-[10px] text-muted-foreground font-mono">{model}</span>
      </div>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-24" preserveAspectRatio="none">
        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map((r) => (
          <line
            key={r}
            x1={0} y1={h * r} x2={w} y2={h * r}
            stroke="hsl(var(--border))"
            strokeWidth="0.5"
            strokeDasharray="2 4"
          />
        ))}
        {/* Plasma line (solid) */}
        <path d={plasmaPath} fill="none" stroke={color} strokeWidth="2" opacity="0.9" />
        {/* Effect-site line (dashed) */}
        <path d={esPath} fill="none" stroke={color} strokeWidth="1.5" strokeDasharray="4 3" opacity="0.5" />
      </svg>
      <div className="flex items-center gap-4 mt-2 text-[10px] text-muted-foreground font-mono">
        <span>
          <span style={{ color }}>━━</span> Plasma: {plasma[plasma.length - 1]?.toFixed(1)} {unit}
        </span>
        <span>
          <span style={{ color, opacity: 0.5 }}>╍╍</span> Ce: {effectSite[effectSite.length - 1]?.toFixed(1)} {unit}
        </span>
      </div>
    </div>
  );
}

export function PKDashboard() {
  const propofol = generatePKCurve(30);
  const remi = generatePKCurve(30);

  const drugLog = [
    { time: "T+00:02", drug: "Propofol", dose: "200mg IV", note: "Induction" },
    { time: "T+00:03", drug: "Fentanyl", dose: "100μg IV", note: "Analgesia" },
    { time: "T+00:05", drug: "Rocuronium", dose: "50mg IV", note: "Paralysis" },
    { time: "T+00:10", drug: "Propofol infusion", dose: "150μg/kg/min", note: "Maintenance" },
    { time: "T+00:10", drug: "Remifentanil infusion", dose: "0.15μg/kg/min", note: "Maintenance" },
    { time: "T+02:30", drug: "Fentanyl", dose: "50μg IV", note: "Supplemental" },
  ];

  return (
    <div className="h-full flex flex-col gap-4 p-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Pill className="h-5 w-5 text-pillar-pharmacist" />
        <span className="text-hud-label" style={{ color: "hsl(var(--pillar-pharmacist))" }}>
          PHARMACOKINETICS
        </span>
      </div>

      {/* Charts */}
      <SVGChart
        plasma={propofol.plasma}
        effectSite={propofol.effectSite}
        label="Propofol"
        unit="μg/mL"
        model="Schnider Model"
        color="hsl(271, 91%, 65%)"
      />
      <SVGChart
        plasma={remi.plasma}
        effectSite={remi.effectSite}
        label="Remifentanil"
        unit="ng/mL"
        model="Minto Model"
        color="hsl(271, 71%, 55%)"
      />

      {/* Emergence prediction */}
      <div className="glass-panel p-3 rounded-lg border-pillar-pharmacist/30">
        <div className="flex items-center gap-2 mb-1">
          <TrendingDown className="h-4 w-4 text-pillar-pharmacist" />
          <span className="text-xs font-medium text-pillar-pharmacist">Emergence Prediction</span>
        </div>
        <p className="text-lg font-mono text-foreground">
          ~8 min after cessation
        </p>
        <p className="text-[10px] text-muted-foreground mt-1">
          Based on current infusion rates and patient pharmacokinetic parameters
        </p>
      </div>

      {/* Drug log */}
      <div>
        <p className="text-hud-label mb-2" style={{ color: "hsl(var(--pillar-pharmacist))" }}>DRUG LOG</p>
        <div className="space-y-1">
          {drugLog.map((entry, i) => (
            <div key={i} className="flex items-center gap-3 text-xs py-1 border-b border-border/30 last:border-0">
              <span className="font-mono text-muted-foreground w-16">{entry.time}</span>
              <span className="text-foreground/90 flex-1">{entry.drug} — {entry.dose}</span>
              <span className="text-muted-foreground">{entry.note}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default PKDashboard;
