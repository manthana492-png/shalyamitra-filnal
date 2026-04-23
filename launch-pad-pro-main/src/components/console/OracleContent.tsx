/**
 * OracleContent — Saffron-accented Oracle/Marma knowledge panel.
 *
 * Displays Marma data with Devanagari text, classification badge,
 * modern anatomical mapping, and shloka with verse reference.
 */

import { ScrollText } from "lucide-react";

export type OracleData = {
  marmaName: string;
  devanagari: string;
  classification: string;
  classificationSeverity: "sadya_pranahara" | "kalantara" | "vaikalyakara" | "vishalyaghna" | "rujakara";
  modernMapping: string;
  consequences: string;
  protectiveDoctrine: string;
  shloka: string;
  shlokaReference: string;
};

const SEVERITY_COLOURS: Record<string, string> = {
  sadya_pranahara: "bg-red-500/20 text-red-400 border-red-500/40",
  kalantara: "bg-orange-500/20 text-orange-400 border-orange-500/40",
  vaikalyakara: "bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
  vishalyaghna: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40",
  rujakara: "bg-amber-500/20 text-amber-400 border-amber-500/40",
};

const SEVERITY_LABELS: Record<string, string> = {
  sadya_pranahara: "Sadya Praṇahara — Immediately fatal if injured",
  kalantara: "Kālāntara Praṇahara — Fatal over time",
  vaikalyakara: "Vaikalyakara — Causes deformity",
  vishalyaghna: "Vishalyaghna — Fatal on foreign body removal",
  rujakara: "Rujakara — Causes severe pain",
};

export function OracleContent({ data }: { data: OracleData }) {
  const severityClass = SEVERITY_COLOURS[data.classificationSeverity] || SEVERITY_COLOURS.rujakara;
  const severityLabel = SEVERITY_LABELS[data.classificationSeverity] || data.classification;

  return (
    <div className="space-y-4 p-4">
      {/* Header with Oracle icon */}
      <div className="flex items-center gap-2 text-pillar-oracle">
        <ScrollText className="h-5 w-5" />
        <span className="text-hud-label" style={{ color: "hsl(var(--pillar-oracle))" }}>
          THE ORACLE
        </span>
      </div>

      {/* Marma name */}
      <div>
        <h3 className="text-devanagari text-2xl font-medium" style={{ color: "hsl(var(--pillar-oracle))" }}>
          {data.devanagari}
        </h3>
        <p className="text-lg text-foreground/90 mt-1">{data.marmaName}</p>
      </div>

      {/* Classification badge */}
      <div className={`inline-block rounded-md border px-3 py-1.5 text-xs font-medium ${severityClass}`}>
        {severityLabel}
      </div>

      {/* Modern mapping */}
      <div>
        <p className="text-hud-label mb-1" style={{ color: "hsl(var(--pillar-oracle))" }}>MODERN MAPPING</p>
        <p className="text-sm text-foreground/80">{data.modernMapping}</p>
      </div>

      {/* Consequences */}
      <div>
        <p className="text-hud-label mb-1" style={{ color: "hsl(var(--pillar-oracle))" }}>CONSEQUENCES</p>
        <p className="text-sm text-foreground/80">{data.consequences}</p>
      </div>

      {/* Protective doctrine */}
      <div className="rounded-md border border-pillar-oracle bg-surface-2/50 p-3">
        <p className="text-hud-label mb-1" style={{ color: "hsl(var(--pillar-oracle))" }}>PROTECTIVE DOCTRINE</p>
        <p className="text-sm text-foreground/90 italic">{data.protectiveDoctrine}</p>
      </div>

      {/* Shloka */}
      <div className="border-t border-border pt-4">
        <p className="text-devanagari text-base leading-relaxed" style={{ color: "hsl(var(--pillar-oracle))" }}>
          {data.shloka}
        </p>
        <p className="text-xs text-muted-foreground mt-2 italic">— {data.shlokaReference}</p>
      </div>
    </div>
  );
}

export default OracleContent;
