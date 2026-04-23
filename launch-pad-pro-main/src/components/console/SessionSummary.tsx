/**
 * SessionSummary — Post-closure session summary screen.
 *
 * Spec: "After closure confirmed:
 * - Duration, alert count, Oracle queries, GPU cost (₹740)
 * - Chronicler's Handover Brief
 * - Auto-shutdown timer (60s) or 'Nael, keep session open'"
 *
 * Shown between end-session and navigate-to-PostOp.
 */

import { useEffect, useState } from "react";
import { AnimatedNumber } from "./AnimatedNumber";
import { Clock, AlertTriangle, BookOpen, IndianRupee, Cpu, FileText } from "lucide-react";

type SessionSummaryProps = {
  duration: number; // seconds
  alertCount: number;
  oracleQueries: number;
  procedureName: string;
  surgeonName?: string;
  onNavigatePostOp: () => void;
  onKeepOpen?: () => void;
};

function fmt(t: number) {
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function SessionSummary({
  duration,
  alertCount,
  oracleQueries,
  procedureName,
  surgeonName,
  onNavigatePostOp,
  onKeepOpen,
}: SessionSummaryProps) {
  const [countdown, setCountdown] = useState(60);
  const [held, setHeld] = useState(false);

  // GPU cost estimate (~₹300/hr for H100)
  const gpuCost = Math.round((duration / 3600) * 300);

  // Auto-redirect countdown
  useEffect(() => {
    if (held) return;
    if (countdown <= 0) {
      onNavigatePostOp();
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, held, onNavigatePostOp]);

  const handleKeepOpen = () => {
    setHeld(true);
    onKeepOpen?.();
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-8">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-mono text-[10px] uppercase tracking-[0.3em] text-primary/70 mb-2">
            SHALYAMITRA SESSION COMPLETE
          </div>
          <h1 className="text-2xl font-semibold text-glow">{procedureName}</h1>
          {surgeonName && (
            <p className="text-sm text-muted-foreground mt-1">{surgeonName}</p>
          )}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { icon: Clock, label: "Duration", value: fmt(duration), color: "text-primary" },
            { icon: AlertTriangle, label: "AI Alerts", value: String(alertCount), color: "text-caution" },
            { icon: BookOpen, label: "Oracle Queries", value: String(oracleQueries), color: "text-pillar-oracle" },
            { icon: IndianRupee, label: "GPU Cost", value: `₹${gpuCost}`, color: "text-pillar-pharmacist" },
          ].map((stat) => (
            <div key={stat.label} className="hud-frame hud-corners relative p-4 text-center">
              <span className="corner-tr" />
              <span className="corner-bl" />
              <stat.icon className={`h-5 w-5 mx-auto mb-2 ${stat.color}`} />
              <div className={`text-mono text-xl font-bold ${stat.color}`}>{stat.value}</div>
              <div className="text-mono text-[9px] uppercase tracking-[0.2em] text-muted-foreground mt-1">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Chronicler Handover Brief */}
        <div className="hud-frame hud-corners relative p-6 mb-6">
          <span className="corner-tr" />
          <span className="corner-bl" />
          <div className="flex items-center gap-2 mb-4">
            <FileText className="h-4 w-4 text-pillar-chronicler" />
            <span className="text-mono text-[10px] uppercase tracking-[0.3em] text-pillar-chronicler">
              CHRONICLER — HANDOVER BRIEF
            </span>
          </div>

          <div className="space-y-3 text-sm text-foreground/90">
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Procedure:</span>
              <span className="font-medium">{procedureName}</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Duration:</span>
              <span className="font-mono">{fmt(duration)}</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Key Findings:</span>
              <span>Anatomical variations managed per protocol</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Anaesthetic:</span>
              <span>TIVA (Propofol/Remifentanil), uneventful</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Blood Loss:</span>
              <span className="font-mono">~150mL (estimated)</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Alerts Fired:</span>
              <span className="font-mono">{alertCount}</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Post-Op Watch:</span>
              <span>MAP &gt;65, monitor eGFR (pre-existing)</span>
            </div>
            <div className="flex gap-3">
              <span className="text-muted-foreground shrink-0 w-28">Classical:</span>
              <span className="text-pillar-oracle">Ropana protocol recommended per Oracle</span>
            </div>

            <div className="border-t border-border/40 pt-3 mt-3">
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                <Cpu className="h-3 w-3" />
                <span>Full report exported to Chronicler archive</span>
              </div>
            </div>
          </div>
        </div>

        {/* Auto-redirect countdown */}
        <div className="text-center">
          {!held ? (
            <div className="space-y-3">
              <div className="text-sm text-muted-foreground">
                Redirecting to post-op review in{" "}
                <span className="text-mono font-bold text-primary">
                  <AnimatedNumber value={countdown} />s
                </span>
              </div>
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={onNavigatePostOp}
                  className="px-4 py-2 rounded-lg bg-gradient-primary text-primary-foreground text-sm font-medium shadow-glow hover:opacity-90 transition-opacity"
                >
                  Go to Post-Op Review →
                </button>
                <button
                  onClick={handleKeepOpen}
                  className="px-4 py-2 rounded-lg border border-primary/30 text-sm text-primary hover:bg-primary/10 transition-colors"
                >
                  Keep Session Open
                </button>
              </div>
              <div className="text-mono text-[10px] text-muted-foreground/60 tracking-wider">
                or say "Nael, keep session open"
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-sm text-success">Session held open</div>
              <button
                onClick={onNavigatePostOp}
                className="px-6 py-2.5 rounded-lg bg-gradient-primary text-primary-foreground text-sm font-medium shadow-glow hover:opacity-90 transition-opacity"
              >
                Go to Post-Op Review →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SessionSummary;
