import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { CDS_DISCLAIMER_SHORT } from "@/lib/cds";
import { ShieldCheck, ShieldAlert } from "lucide-react";
import { redactPhi } from "@/lib/phi-redact";

export type TranscriptLine = {
  id: string;
  speaker: "surgeon" | "anaesthetist" | "nurse" | "nael" | "system";
  text: string;
  at: number; // seconds from session start
};

const SPEAKER_COLORS: Record<TranscriptLine["speaker"], string> = {
  surgeon: "text-foreground",
  anaesthetist: "text-info",
  nurse: "text-success",
  nael: "text-primary",
  system: "text-muted-foreground",
};

const SPEAKER_LABELS: Record<TranscriptLine["speaker"], string> = {
  surgeon: "SURGEON",
  anaesthetist: "ANAES",
  nurse: "NURSE",
  nael: "NAEL",
  system: "SYSTEM",
};

function fmt(t: number) {
  const m = Math.floor(t / 60).toString().padStart(2, "0");
  const s = Math.floor(t % 60).toString().padStart(2, "0");
  return `T+${m}:${s}`;
}

/** Renders text with `[REDACTED]` chips highlighted as Morpheus PHI masks. */
function RedactedText({ text }: { text: string }) {
  // Already-redacted strings (from server-side Morpheus or local redactor)
  // contain literal "[REDACTED]" tokens; render them as inline chips.
  const parts = text.split(/(\[REDACTED\])/g);
  return (
    <>
      {parts.map((p, i) =>
        p === "[REDACTED]" ? (
          <span
            key={i}
            className="inline-flex items-center gap-1 mx-0.5 align-baseline rounded border border-primary/40 bg-primary/10 px-1.5 py-0 text-mono text-[10px] uppercase tracking-wider text-primary/90"
            title="PHI redacted by Morpheus"
          >
            <ShieldAlert className="h-2.5 w-2.5" />
            REDACTED
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
}

export function TranscriptStream({ lines }: { lines: TranscriptLine[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [lines]);

  return (
    <div ref={ref} className="h-full overflow-y-auto p-5 space-y-4">
      {lines.length === 0 && (
        <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
          Waiting for the first utterance…
        </div>
      )}
      {lines.map((l) => {
        // Apply client-side Morpheus-shape PHI scan as a defence-in-depth layer.
        // If text already contains [REDACTED] tokens we keep them as-is.
        const redacted = l.text.includes("[REDACTED]") ? { text: l.text, redacted: true } : redactPhi(l.text);
        return (
          <div key={l.id} className="animate-fade-in">
            <div className="flex items-baseline gap-3">
              <span className={cn("text-mono text-[10px] font-semibold tracking-[0.2em]", SPEAKER_COLORS[l.speaker])}>
                {SPEAKER_LABELS[l.speaker]}
              </span>
              <span className="text-mono text-[10px] text-muted-foreground">{fmt(l.at)}</span>
              {redacted.redacted && (
                <span className="text-mono text-[9px] tracking-wider text-primary/70 uppercase flex items-center gap-1">
                  <ShieldAlert className="h-2.5 w-2.5" /> PHI Masked
                </span>
              )}
            </div>
            <p className={cn(
              "mt-1 text-[15px] leading-relaxed",
              l.speaker === "nael" ? "text-foreground" : "text-foreground/90",
            )}>
              <RedactedText text={redacted.text} />
            </p>
            {l.speaker === "nael" && (
              <div className="mt-1.5 flex items-center gap-1.5 text-[10px] text-muted-foreground">
                <ShieldCheck className="h-3 w-3 text-primary" />
                <span>{CDS_DISCLAIMER_SHORT}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
