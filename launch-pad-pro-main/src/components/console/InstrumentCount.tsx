/**
 * InstrumentCount — Teal (Sentinel) instrument & swab tracking display.
 *
 * Spec: Full-width banner at closure:
 * "🔧 Instruments: 14/14 ✓ COMPLETE | 🧹 Swabs: 18/18 ✓ COMPLETE"
 * "✅ FIELD IS CLEAR — Safe to close"
 * RED variant if discrepancy — does NOT auto-dismiss.
 *
 * Mini badge in theatre_overview: "🔧 14/14 ✓"
 */

import { useDirector } from "@/lib/director";
import { AnimatedNumber } from "./AnimatedNumber";
import { Eye, ShieldAlert, CheckCircle2 } from "lucide-react";

export function InstrumentCount() {
  const { instrumentCount, phase } = useDirector();
  const { deployed, accounted, matched } = instrumentCount;
  const isClosure = phase === "closure" || phase === "closing";

  if (deployed === 0) return null;

  // Simulated swab count (in production, comes from Sentinel data channel)
  const swabDeployed = Math.max(0, Math.round(deployed * 1.3));
  const swabAccounted = matched ? swabDeployed : swabDeployed - 1;
  const swabMatched = swabAccounted === swabDeployed;
  const allClear = matched && swabMatched;

  // Full closure banner
  if (isClosure) {
    return (
      <div
        className={`
          w-full border-b-2 backdrop-blur-sm
          ${allClear
            ? "bg-success/8 border-success/40"
            : "bg-critical/10 border-critical/50"
          }
        `}
      >
        {/* Main count row */}
        <div className="flex items-center justify-center gap-6 py-3 px-6">
          <div className="text-mono text-[10px] uppercase tracking-[0.3em] text-pillar-sentinel">
            SENTINEL — INSTRUMENT & SWAB COUNT
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 px-6 pb-2">
          {/* Instruments */}
          <div className={`
            flex items-center gap-3 rounded-lg px-4 py-2 border
            ${matched
              ? "border-success/30 bg-success/5"
              : "border-critical/40 bg-critical/8 animate-hud-pulse"
            }
          `}>
            <span className="text-lg">🔧</span>
            <div>
              <div className="text-mono text-[9px] uppercase tracking-[0.2em] text-muted-foreground">Instruments</div>
              <div className="flex items-center gap-2">
                <span className={`text-mono text-xl font-bold tabular-nums ${matched ? "text-success" : "text-critical"}`}>
                  <AnimatedNumber value={accounted} /> / <AnimatedNumber value={deployed} />
                </span>
                <span className={`text-sm font-semibold ${matched ? "text-success" : "text-critical"}`}>
                  {matched ? "✓ COMPLETE" : "✗ MISMATCH"}
                </span>
              </div>
            </div>
          </div>

          {/* Swabs */}
          <div className={`
            flex items-center gap-3 rounded-lg px-4 py-2 border
            ${swabMatched
              ? "border-success/30 bg-success/5"
              : "border-critical/40 bg-critical/8 animate-hud-pulse"
            }
          `}>
            <span className="text-lg">🧹</span>
            <div>
              <div className="text-mono text-[9px] uppercase tracking-[0.2em] text-muted-foreground">Swabs</div>
              <div className="flex items-center gap-2">
                <span className={`text-mono text-xl font-bold tabular-nums ${swabMatched ? "text-success" : "text-critical"}`}>
                  <AnimatedNumber value={swabAccounted} /> / <AnimatedNumber value={swabDeployed} />
                </span>
                <span className={`text-sm font-semibold ${swabMatched ? "text-success" : "text-critical"}`}>
                  {swabMatched ? "✓ COMPLETE" : "✗ MISMATCH"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Status banner */}
        <div className={`
          flex items-center justify-center gap-2 py-2.5 px-6 text-sm font-semibold
          ${allClear
            ? "bg-success/10 text-success"
            : "bg-critical/15 text-critical animate-hud-flicker"
          }
        `}>
          {allClear ? (
            <>
              <CheckCircle2 className="h-5 w-5" />
              <span>✅ FIELD IS CLEAR — Safe to close</span>
            </>
          ) : (
            <>
              <ShieldAlert className="h-5 w-5" />
              <span>⚠ DISCREPANCY — VERIFY BEFORE CLOSURE. DO NOT CLOSE UNTIL RESOLVED.</span>
            </>
          )}
        </div>
      </div>
    );
  }

  // Mini badge (inline in top bar)
  return (
    <div
      className={`
        inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-mono
        border transition-all duration-300
        ${matched
          ? "border-pillar-sentinel bg-pillar-sentinel/10 text-pillar-sentinel"
          : "border-critical bg-critical/10 text-critical animate-hud-pulse"
        }
      `}
    >
      <Eye className="h-3 w-3" />
      <span>{accounted}/{deployed}</span>
      <span>{matched ? "✓" : "✗"}</span>
    </div>
  );
}

export default InstrumentCount;
