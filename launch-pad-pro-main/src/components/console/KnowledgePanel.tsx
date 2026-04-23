/**
 * KnowledgePanel — Slide-in panel for Scholar/Oracle/Consultant/Drug content.
 */

import { useDirector } from "@/lib/director";
import { X, BookOpen, ScrollText, Stethoscope, Pill } from "lucide-react";
import { OracleContent, type OracleData } from "./OracleContent";

const PILLAR_CONFIG: Record<string, { icon: typeof BookOpen; label: string; colorVar: string }> = {
  oracle:     { icon: ScrollText, label: "THE ORACLE",   colorVar: "--pillar-oracle" },
  scholar:    { icon: BookOpen,   label: "THE SCHOLAR",  colorVar: "--pillar-scholar" },
  consultant: { icon: Stethoscope, label: "CONSULTANT",  colorVar: "--pillar-nael" },
  imaging:    { icon: Stethoscope, label: "IMAGING",     colorVar: "--pillar-scholar" },
  drugref:    { icon: Pill,       label: "DRUG REFERENCE", colorVar: "--pillar-pharmacist" },
};

export function KnowledgePanel() {
  const { knowledgePanel, closeKnowledgePanel } = useDirector();

  if (!knowledgePanel.open || !knowledgePanel.pillar) return null;

  const config = PILLAR_CONFIG[knowledgePanel.pillar] || PILLAR_CONFIG.scholar;
  const Icon = config.icon;

  return (
    <div
      className="h-full glass-panel overflow-y-auto animate-fade-in"
      style={{
        borderLeftColor: `hsl(var(${config.colorVar}))`,
        borderLeftWidth: "2px",
      }}
    >
      {/* Header */}
      <div className="sticky top-0 z-10 flex items-center justify-between px-4 py-3 border-b border-border bg-surface-1/90 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4" style={{ color: `hsl(var(${config.colorVar}))` }} />
          <span
            className="text-[10px] font-mono uppercase tracking-[0.2em]"
            style={{ color: `hsl(var(${config.colorVar}))` }}
          >
            {config.label}
          </span>
        </div>
        <button
          onClick={closeKnowledgePanel}
          className="rounded-md p-1 hover:bg-surface-3 transition-colors"
        >
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>

      {/* Content based on pillar */}
      {knowledgePanel.pillar === "oracle" && knowledgePanel.content && (
        <OracleContent data={knowledgePanel.content as OracleData} />
      )}

      {knowledgePanel.pillar === "scholar" && (
        <div className="p-4 space-y-3">
          <p className="text-hud-label" style={{ color: `hsl(var(${config.colorVar}))` }}>PRE-OPERATIVE FLAGS</p>
          {(knowledgePanel.content as string[] || ["No risk flags available"]).map((flag: string, i: number) => (
            <div key={i} className="flex items-start gap-2 rounded-md border border-border bg-surface-2/50 px-3 py-2">
              <span className="text-warning mt-0.5">⚠</span>
              <span className="text-sm text-foreground/90">{flag}</span>
            </div>
          ))}
        </div>
      )}

      {knowledgePanel.pillar === "drugref" && (
        <div className="p-4 space-y-3">
          <p className="text-hud-label" style={{ color: `hsl(var(${config.colorVar}))` }}>DRUG REFERENCE</p>
          <p className="text-sm text-foreground/80">{String(knowledgePanel.content || "No drug data available")}</p>
        </div>
      )}

      {knowledgePanel.pillar === "consultant" && (
        <div className="p-4 space-y-3">
          <p className="text-hud-label" style={{ color: `hsl(var(${config.colorVar}))` }}>CONSULTANT RESPONSE</p>
          <p className="text-sm text-foreground/80">{String(knowledgePanel.content || "No response available")}</p>
        </div>
      )}

      {knowledgePanel.pillar === "imaging" && (
        <div className="p-4 space-y-3">
          <p className="text-hud-label" style={{ color: `hsl(var(${config.colorVar}))` }}>IMAGING</p>
          <div className="aspect-square rounded-lg border border-border bg-black flex items-center justify-center">
            <span className="text-xs text-muted-foreground">DICOM Viewer placeholder</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default KnowledgePanel;
