/**
 * NaelCore — Jarvis-style rotating, pulsating AI agent visualization.
 *
 * A full-width SVG-based holographic core that reacts to Nael's state:
 *  - idle     : slow rotation, dim glow, STANDBY label
 *  - listening: expanding pulse rings, bright glow, LISTENING label
 *  - thinking : fast rotation + orbiting particles, PROCESSING label
 *  - speaking : amplitude-modulated inner core, SPEAKING label
 *
 * Shows: active mode (PROACTIVE/REACTIVE/SILENT), surgery timer,
 * active pillar ring segments, and the 8-pillar activity halo.
 */

import { useEffect, useRef, useMemo } from "react";
import { useDirector, type NaelState } from "@/lib/director";
import { PILLARS, type PillarId } from "@/lib/pillars";
import { cn } from "@/lib/utils";

// ── Constants ──────────────────────────────────────────────────────────────

const STATE_LABEL: Record<NaelState, string> = {
  idle: "STANDBY",
  listening: "LISTENING",
  thinking: "PROCESSING",
  speaking: "SPEAKING",
};

const STATE_SUBLABEL: Record<NaelState, string> = {
  idle: "Nael is monitoring",
  listening: "Capturing voice input",
  thinking: "Reasoning across pillars",
  speaking: "Delivering advisory",
};

const PILLAR_ORDER: PillarId[] = [
  "nael", "haemorrhage", "monitor", "sentinel",
  "pharmacist", "scholar", "oracle", "advocate",
];

const PILLAR_CSS_VARS: Record<string, string> = {
  nael: "--pillar-nael",
  haemorrhage: "--pillar-haemorrhage",
  monitor: "--pillar-monitor",
  sentinel: "--pillar-sentinel",
  pharmacist: "--pillar-pharmacist",
  scholar: "--pillar-scholar",
  oracle: "--pillar-oracle",
  advocate: "--pillar-advocate",
  chronicler: "--pillar-chronicler",
};

function fmt(t: number) {
  const m = Math.floor(t / 60).toString().padStart(2, "0");
  const s = Math.floor(t % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

// ── Tick Ring (SVG) ─────────────────────────────────────────────────────────

function TickRing({
  radius,
  ticks,
  tickLen,
  strokeWidth = 1,
  opacity = 0.3,
  className = "",
}: {
  radius: number;
  ticks: number;
  tickLen: number;
  strokeWidth?: number;
  opacity?: number;
  className?: string;
}) {
  const lines = useMemo(() => {
    const arr = [];
    for (let i = 0; i < ticks; i++) {
      const angle = (i / ticks) * Math.PI * 2 - Math.PI / 2;
      const x1 = Math.cos(angle) * radius;
      const y1 = Math.sin(angle) * radius;
      const x2 = Math.cos(angle) * (radius + tickLen);
      const y2 = Math.sin(angle) * (radius + tickLen);
      arr.push({ x1, y1, x2, y2, key: i });
    }
    return arr;
  }, [radius, ticks, tickLen]);

  return (
    <g className={className} opacity={opacity}>
      {lines.map((l) => (
        <line
          key={l.key}
          x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2}
          stroke="hsl(var(--primary))"
          strokeWidth={strokeWidth}
        />
      ))}
    </g>
  );
}

// ── Pillar Arc Segments ──────────────────────────────────────────────────

function PillarArcs({
  radius,
  activePillar,
}: {
  radius: number;
  activePillar: PillarId | null;
}) {
  const arcAngle = (2 * Math.PI) / PILLAR_ORDER.length;
  const gap = 0.04; // radians gap between arcs

  return (
    <g>
      {PILLAR_ORDER.map((p, i) => {
        const startAngle = i * arcAngle - Math.PI / 2 + gap / 2;
        const endAngle = (i + 1) * arcAngle - Math.PI / 2 - gap / 2;
        const x1 = Math.cos(startAngle) * radius;
        const y1 = Math.sin(startAngle) * radius;
        const x2 = Math.cos(endAngle) * radius;
        const y2 = Math.sin(endAngle) * radius;
        const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
        const isActive = activePillar === p;
        const cssVar = PILLAR_CSS_VARS[p] || "--pillar-nael";

        return (
          <path
            key={p}
            d={`M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none"
            stroke={`hsl(var(${cssVar}))`}
            strokeWidth={isActive ? 4 : 2}
            opacity={isActive ? 1 : 0.25}
            strokeLinecap="round"
            className={isActive ? "nael-core-arc-active" : ""}
          />
        );
      })}
    </g>
  );
}

// ── Orbiting Particles (thinking state) ──────────────────────────────────

function OrbitParticles({ radius }: { radius: number }) {
  return (
    <g>
      {[0, 1, 2, 3, 4].map((i) => (
        <circle
          key={i}
          r={2.5 - i * 0.3}
          fill="hsl(var(--primary))"
          opacity={1 - i * 0.15}
          className="nael-core-particle"
          style={{
            transformOrigin: "0 0",
            animation: `nael-core-orbit ${1.8 + i * 0.4}s linear infinite`,
            offsetPath: `path("M ${radius} 0 A ${radius} ${radius} 0 1 1 ${radius - 0.01} 0")`,
            offsetRotate: "0deg",
            animationDelay: `${i * -0.35}s`,
          }}
        />
      ))}
    </g>
  );
}

// ── Amplitude Bars (speaking state) ──────────────────────────────────────

function AmplitudeBars() {
  return (
    <g>
      {[-20, -10, 0, 10, 20].map((x, i) => (
        <rect
          key={i}
          x={x - 2}
          y={-12}
          width={4}
          height={24}
          rx={2}
          fill="hsl(var(--primary))"
          className="nael-core-bar"
          style={{
            transformOrigin: `${x}px 0px`,
            animation: `nael-core-amplitude 0.6s ease-in-out infinite alternate`,
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </g>
  );
}

// ── Main Component ──────────────────────────────────────────────────────

export function NaelCore({ className }: { className?: string }) {
  const naelState = useDirector((s) => s.naelState);
  const activePillar = useDirector((s) => s.activePillar);
  const phase = useDirector((s) => s.phase);
  const surgeryTimer = useDirector((s) => s.surgeryTimer);
  const mode = useDirector((s) => s.controlMode);
  const alertQueue = useDirector((s) => s.alertQueue);

  const unackedAlerts = alertQueue.filter((a) => !a.acknowledged).length;

  // Determine glow intensity based on state
  const glowClass = {
    idle: "nael-core-glow-idle",
    listening: "nael-core-glow-listening",
    thinking: "nael-core-glow-thinking",
    speaking: "nael-core-glow-speaking",
  }[naelState];

  const rotationClass = {
    idle: "nael-core-rotate-slow",
    listening: "nael-core-rotate-slow",
    thinking: "nael-core-rotate-fast",
    speaking: "nael-core-rotate-medium",
  }[naelState];

  const rotationClassRev = {
    idle: "nael-core-rotate-rev-slow",
    listening: "nael-core-rotate-rev-slow",
    thinking: "nael-core-rotate-rev-fast",
    speaking: "nael-core-rotate-rev-medium",
  }[naelState];

  const modeLabel = mode === "conservative" ? "SILENT" :
                    mode === "dynamic" ? "REACTIVE" : "PROACTIVE";

  return (
    <div className={cn("hud-frame hud-corners relative overflow-hidden", className)}>
      <span className="corner-tr" /><span className="corner-bl" />

      {/* Header */}
      <div className="flex items-center justify-center border-b border-primary/20 px-4 py-2">
        <span className="text-mono text-[10px] uppercase tracking-[0.3em] text-primary/70">
          NAEL · CORE
        </span>
      </div>

      {/* Core visualization */}
      <div className="flex flex-col items-center justify-center py-8 px-4">
        <div className="relative w-[280px] h-[280px] flex items-center justify-center">
          {/* SVG Rings */}
          <svg
            viewBox="-150 -150 300 300"
            className="absolute inset-0 w-full h-full"
            style={{ filter: "drop-shadow(0 0 12px hsl(var(--primary) / 0.3))" }}
          >
            {/* Outer ring — slow rotation */}
            <g className={rotationClass}>
              <circle
                r={130}
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth={0.5}
                opacity={0.2}
              />
              <TickRing radius={125} ticks={72} tickLen={8} strokeWidth={0.8} opacity={0.2} />
            </g>

            {/* Pillar arcs — mid ring */}
            <g className={rotationClassRev}>
              <PillarArcs radius={108} activePillar={activePillar} />
            </g>

            {/* Mid ring — counter-rotation */}
            <g className={rotationClassRev}>
              <circle
                r={100}
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth={0.5}
                opacity={0.15}
              />
              <TickRing radius={96} ticks={48} tickLen={5} strokeWidth={0.6} opacity={0.25} />
            </g>

            {/* Inner detail ring */}
            <g className={rotationClass}>
              <circle
                r={75}
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth={0.5}
                opacity={0.2}
                strokeDasharray="4 8"
              />
              <TickRing radius={70} ticks={36} tickLen={6} strokeWidth={0.5} opacity={0.15} />
            </g>

            {/* Innermost detail ring */}
            <g className={rotationClassRev}>
              <circle
                r={55}
                fill="none"
                stroke="hsl(var(--primary))"
                strokeWidth={0.3}
                opacity={0.15}
                strokeDasharray="2 6"
              />
            </g>

            {/* Core glow */}
            <defs>
              <radialGradient id="nael-core-gradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.6} />
                <stop offset="50%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </radialGradient>
              <radialGradient id="nael-core-inner" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="hsl(var(--primary-glow))" stopOpacity={0.9} />
                <stop offset="60%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </radialGradient>
              {/* Listening pulse gradient */}
              <radialGradient id="nael-pulse-gradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                <stop offset="70%" stopColor="hsl(var(--primary))" stopOpacity={0.15} />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </radialGradient>
            </defs>

            {/* Ambient glow circle */}
            <circle r={45} fill="url(#nael-core-gradient)" className={glowClass} />

            {/* Listening: expanding pulse rings */}
            {naelState === "listening" && (
              <>
                <circle r={40} fill="none" stroke="hsl(var(--primary))" strokeWidth={1.5}
                  opacity={0.4} className="nael-core-pulse-ring" />
                <circle r={40} fill="none" stroke="hsl(var(--primary))" strokeWidth={1}
                  opacity={0.25} className="nael-core-pulse-ring"
                  style={{ animationDelay: "0.5s" }} />
                <circle r={40} fill="none" stroke="hsl(var(--primary))" strokeWidth={0.5}
                  opacity={0.15} className="nael-core-pulse-ring"
                  style={{ animationDelay: "1s" }} />
              </>
            )}

            {/* Thinking: orbiting particles */}
            {naelState === "thinking" && <OrbitParticles radius={55} />}

            {/* Speaking: amplitude bars */}
            {naelState === "speaking" && <AmplitudeBars />}

            {/* Inner core circle */}
            <circle r={28} fill="url(#nael-core-inner)" className={glowClass} />
            <circle
              r={20}
              fill="hsl(var(--primary) / 0.15)"
              stroke="hsl(var(--primary))"
              strokeWidth={1}
              opacity={0.6}
              className={glowClass}
            />

            {/* Center dot */}
            <circle r={4} fill="hsl(var(--primary-glow))" opacity={0.9} className={glowClass} />

            {/* Cross-hair lines */}
            <line x1={-35} y1={0} x2={-22} y2={0}
              stroke="hsl(var(--primary))" strokeWidth={0.5} opacity={0.3} />
            <line x1={22} y1={0} x2={35} y2={0}
              stroke="hsl(var(--primary))" strokeWidth={0.5} opacity={0.3} />
            <line x1={0} y1={-35} x2={0} y2={-22}
              stroke="hsl(var(--primary))" strokeWidth={0.5} opacity={0.3} />
            <line x1={0} y1={22} x2={0} y2={35}
              stroke="hsl(var(--primary))" strokeWidth={0.5} opacity={0.3} />

            {/* Cardinal labels */}
            <text x={0} y={-138} textAnchor="middle" fill="hsl(var(--primary))"
              fontSize={7} fontFamily="var(--font-mono)" opacity={0.4}
              letterSpacing="0.2em">N</text>
            <text x={140} y={3} textAnchor="middle" fill="hsl(var(--primary))"
              fontSize={7} fontFamily="var(--font-mono)" opacity={0.4}
              letterSpacing="0.2em">E</text>
            <text x={0} y={145} textAnchor="middle" fill="hsl(var(--primary))"
              fontSize={7} fontFamily="var(--font-mono)" opacity={0.4}
              letterSpacing="0.2em">S</text>
            <text x={-140} y={3} textAnchor="middle" fill="hsl(var(--primary))"
              fontSize={7} fontFamily="var(--font-mono)" opacity={0.4}
              letterSpacing="0.2em">W</text>
          </svg>

          {/* Decorative outer halo */}
          <div className={cn(
            "absolute inset-0 rounded-full",
            naelState === "listening" && "nael-core-halo-pulse",
          )} style={{
            background: "radial-gradient(circle, transparent 55%, hsl(var(--primary) / 0.05) 70%, transparent 85%)",
          }} />
        </div>

        {/* Status Text */}
        <div className="flex flex-col items-center mt-4 gap-1.5">
          <div className="flex items-center gap-2">
            <span className={cn(
              "pulse-dot",
              naelState === "idle" ? "nael" : "live",
            )} />
            <span className={cn(
              "text-mono text-sm uppercase tracking-[0.3em] font-semibold",
              naelState === "idle" ? "text-primary/60" : "text-primary text-glow",
            )}>
              {STATE_LABEL[naelState]}
            </span>
          </div>

          <span className="text-[11px] text-muted-foreground">
            {STATE_SUBLABEL[naelState]}
          </span>

          {/* Mode + Phase + Timer row */}
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-primary/20 bg-surface-2/60">
              <span className="text-mono text-[9px] text-muted-foreground uppercase tracking-[0.15em]">
                Mode:
              </span>
              <span className="text-mono text-[10px] text-primary font-semibold uppercase tracking-[0.15em]">
                {modeLabel}
              </span>
            </div>

            <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-primary/20 bg-surface-2/60">
              <span className="text-mono text-[9px] text-muted-foreground uppercase tracking-[0.15em]">
                Phase:
              </span>
              <span className="text-mono text-[10px] text-primary font-semibold uppercase tracking-[0.15em]">
                {phase.toUpperCase()}
              </span>
            </div>

            <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-primary/20 bg-surface-2/60">
              <span className="text-mono text-[9px] text-muted-foreground uppercase tracking-[0.15em]">
                T+
              </span>
              <span className="text-mono text-[10px] text-primary font-semibold tracking-[0.1em]">
                {fmt(surgeryTimer)}
              </span>
            </div>

            {unackedAlerts > 0 && (
              <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-critical/30 bg-critical/10">
                <span className="pulse-dot" />
                <span className="text-mono text-[10px] text-critical font-semibold uppercase tracking-[0.15em]">
                  {unackedAlerts} ALERT{unackedAlerts > 1 ? "S" : ""}
                </span>
              </div>
            )}
          </div>

          {/* Pillar Legend */}
          <div className="flex items-center gap-3 mt-3 flex-wrap justify-center">
            {PILLAR_ORDER.map((p) => {
              const isActive = activePillar === p;
              const cssVar = PILLAR_CSS_VARS[p] || "--pillar-nael";
              const pillarData = PILLARS[p];
              return (
                <div
                  key={p}
                  className={cn(
                    "flex items-center gap-1 transition-opacity",
                    isActive ? "opacity-100" : "opacity-30",
                  )}
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: `hsl(var(${cssVar}))` }}
                  />
                  <span className="text-mono text-[8px] uppercase tracking-[0.15em] text-muted-foreground">
                    {pillarData?.shortName || p}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default NaelCore;
