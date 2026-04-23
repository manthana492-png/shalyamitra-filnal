/**
 * PreOpView — Pre-operative intelligence briefing.
 * Route: /sessions/:id/preop
 *
 * Shows Scholar risk synthesis, drug interactions, and Ayurvedic assessment
 * before the surgeon enters the theatre console.
 */

import { useParams, useNavigate } from "react-router-dom";
import { NaelLogo } from "@/components/NaelLogo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen, ScrollText, Pill, AlertTriangle, CheckCircle, ChevronRight,
  Activity, User, Calendar, Stethoscope, ShieldCheck,
} from "lucide-react";
import { CDS_DISCLAIMER_SHORT } from "@/lib/cds";
import { cn } from "@/lib/utils";

// ── Mock patient data (replace with Supabase fetch in production) ─────
const MOCK_PATIENT = {
  code: "PT-DEMO-001",
  procedure: "Laparoscopic Cholecystectomy",
  age: 52,
  sex: "Female",
  weight: 68,
  asa: 2,
  rcri: 1,
  surgeon: "Dr. Shivalumar",
  theatre: "OR-3",
  scheduledAt: "08:00",
};

const RISK_FLAGS = [
  { severity: "warning", text: "Borderline platelet count 142,000/μL — recheck if significant bleeding occurs" },
  { severity: "caution", text: "BMI 28 — moderate technical difficulty expected with trocar placement" },
  { severity: "info", text: "Previous open appendectomy (2014) — possible periumbilical adhesions" },
  { severity: "info", text: "Mild hypertension on Amlodipine 5mg — continue perioperatively" },
];

const DRUG_INTERACTIONS = [
  { drugs: ["Amlodipine", "Fentanyl"], severity: "low", note: "Minor additive hypotension. Monitor MAP closely." },
  { drugs: ["Amlodipine", "Rocuronium"], severity: "minimal", note: "No significant interaction. Standard dosing." },
];

const MARMA_ASSESSMENT = [
  { name: "Nābhi Marma", devanagari: "नाभि मर्म", zone: "Periumbilical", risk: "High", note: "Primary port site proximity — Sadya Praṇahara class" },
  { name: "Yakṛt Marma", devanagari: "यकृत् मर्म", zone: "Hepatic region", risk: "Moderate", note: "Liver bed dissection zone — monitor retractor pressure" },
];

const ASA_COLOURS: Record<number, string> = {
  1: "bg-success/20 text-success border-success/30",
  2: "bg-caution/20 text-caution border-caution/30",
  3: "bg-warning/20 text-warning border-warning/30",
  4: "bg-critical/20 text-critical border-critical/30",
  5: "bg-critical/30 text-critical border-critical/50",
};

const SEV_COLOURS: Record<string, string> = {
  warning: "text-warning",
  caution: "text-caution",
  info: "text-primary/70",
};

type TabId = "scholar" | "drugs" | "oracle";

export default function PreOpView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Simple tab state using URL hash
  const hash = (window.location.hash.replace("#", "") as TabId) || "scholar";
  const setTab = (t: TabId) => { window.location.hash = t; };
  const activeTab = ["scholar", "drugs", "oracle"].includes(hash) ? hash as TabId : "scholar";

  return (
    <div className="min-h-screen bg-background hud-scanline flex flex-col">
      {/* Header */}
      <header className="border-b border-primary/20 bg-surface-1/50 backdrop-blur-md">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-4">
            <NaelLogo size="sm" />
            <div>
              <h1 className="text-sm font-semibold text-glow">{MOCK_PATIENT.procedure}</h1>
              <p className="text-[10px] font-mono text-primary/60 uppercase tracking-wider mt-0.5">
                Pre-operative Intelligence Briefing
              </p>
            </div>
          </div>
          <Button
            onClick={() => navigate(`/sessions/${id ?? "demo"}`)}
            className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow"
          >
            Begin Surgery
            <ChevronRight className="ml-1.5 h-4 w-4" />
          </Button>
        </div>
      </header>

      <div className="flex-1 max-w-5xl mx-auto w-full px-6 py-6 space-y-6">
        {/* Patient summary card */}
        <div className="hud-frame hud-corners relative p-5">
          <span className="corner-tr" />
          <span className="corner-bl" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-hud-label mb-1">PATIENT</p>
              <p className="text-sm font-mono">{MOCK_PATIENT.code}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{MOCK_PATIENT.age}y {MOCK_PATIENT.sex} · {MOCK_PATIENT.weight}kg</p>
            </div>
            <div>
              <p className="text-hud-label mb-1">SURGEON</p>
              <p className="text-sm font-mono">{MOCK_PATIENT.surgeon}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{MOCK_PATIENT.theatre} · {MOCK_PATIENT.scheduledAt}</p>
            </div>
            <div>
              <p className="text-hud-label mb-1">ASA SCORE</p>
              <span className={cn("inline-flex items-center rounded border px-3 py-1 text-sm font-semibold", ASA_COLOURS[MOCK_PATIENT.asa])}>
                ASA {MOCK_PATIENT.asa}
              </span>
            </div>
            <div>
              <p className="text-hud-label mb-1">RCRI SCORE</p>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-mono font-bold text-primary">{MOCK_PATIENT.rcri}</span>
                <span className="text-xs text-success">Low cardiac risk</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-border">
          {[
            { id: "scholar" as TabId, label: "Clinical Synthesis", icon: BookOpen, color: "--pillar-scholar" },
            { id: "drugs" as TabId, label: "Drug Interactions", icon: Pill, color: "--pillar-pharmacist" },
            { id: "oracle" as TabId, label: "Ayurvedic Assessment", icon: ScrollText, color: "--pillar-oracle" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 text-sm border-b-2 transition-all",
                activeTab === tab.id
                  ? "border-current font-medium"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
              style={activeTab === tab.id ? { color: `hsl(var(${tab.color}))`, borderColor: `hsl(var(${tab.color}))` } : {}}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Scholar tab */}
        {activeTab === "scholar" && (
          <div className="space-y-4 animate-fade-in">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" style={{ color: "hsl(var(--pillar-scholar))" }} />
              <h2 className="text-sm font-semibold" style={{ color: "hsl(var(--pillar-scholar))" }}>
                Pre-Operative Risk Synthesis
              </h2>
            </div>
            <div className="space-y-2">
              {RISK_FLAGS.map((flag, i) => (
                <div key={i} className="flex items-start gap-3 rounded-lg border border-border bg-surface-2/50 px-4 py-3">
                  <AlertTriangle className={cn("h-4 w-4 mt-0.5 shrink-0", SEV_COLOURS[flag.severity])} />
                  <p className="text-sm text-foreground/90">{flag.text}</p>
                  <Badge variant="outline" className={cn("ml-auto shrink-0 text-[9px] uppercase", SEV_COLOURS[flag.severity])}>
                    {flag.severity}
                  </Badge>
                </div>
              ))}
            </div>
            <div className="rounded-lg border border-success/30 bg-success/5 px-4 py-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-success" />
              <p className="text-sm text-foreground/80">
                Antibiotic prophylaxis: <span className="font-medium text-foreground">Cefazolin 2g IV at induction</span>. DVT prophylaxis: <span className="font-medium text-foreground">TED stockings + LMWH post-op</span>.
              </p>
            </div>
          </div>
        )}

        {/* Drug interactions tab */}
        {activeTab === "drugs" && (
          <div className="space-y-4 animate-fade-in">
            <div className="flex items-center gap-2">
              <Pill className="h-4 w-4 text-pillar-pharmacist" />
              <h2 className="text-sm font-semibold text-pillar-pharmacist">Drug Interaction Analysis</h2>
            </div>
            {DRUG_INTERACTIONS.map((di, i) => (
              <div key={i} className="rounded-lg border border-border bg-surface-2/50 p-4">
                <div className="flex items-center gap-2 mb-2">
                  {di.drugs.map((d) => (
                    <Badge key={d} variant="outline" className="text-xs border-pillar-pharmacist/40 text-pillar-pharmacist">{d}</Badge>
                  ))}
                  <Badge className={cn("ml-auto text-[9px] uppercase",
                    di.severity === "low" ? "bg-caution/20 text-caution border-caution/30" :
                    "bg-success/20 text-success border-success/30"
                  )}>
                    {di.severity} risk
                  </Badge>
                </div>
                <p className="text-sm text-foreground/80">{di.note}</p>
              </div>
            ))}
            <div className="rounded-lg border border-success/30 bg-success/5 px-4 py-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-success shrink-0" />
              <p className="text-sm text-foreground/80">No absolute contraindications found. Proceed with standard TIVA protocol.</p>
            </div>
          </div>
        )}

        {/* Oracle tab */}
        {activeTab === "oracle" && (
          <div className="space-y-4 animate-fade-in">
            <div className="flex items-center gap-2">
              <ScrollText className="h-4 w-4 text-pillar-oracle" />
              <h2 className="text-sm font-semibold text-pillar-oracle">Ayurvedic Surgical Assessment</h2>
              <Badge variant="outline" className="ml-2 text-[9px] text-pillar-oracle border-pillar-oracle/40">
                Oracle Intelligence
              </Badge>
            </div>
            <div className="space-y-3">
              {MARMA_ASSESSMENT.map((m, i) => (
                <div key={i} className="rounded-lg border bg-surface-2/50 p-4" style={{ borderColor: "hsl(var(--pillar-oracle) / 0.3)" }}>
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="text-devanagari text-lg font-medium text-pillar-oracle">{m.devanagari}</p>
                      <p className="text-sm text-foreground/90 mt-0.5">{m.name}</p>
                    </div>
                    <Badge variant="outline" className={cn("text-[9px] uppercase",
                      m.risk === "High" ? "text-critical border-critical/40" :
                      m.risk === "Moderate" ? "text-warning border-warning/40" :
                      "text-success border-success/40"
                    )}>
                      {m.risk} risk zone
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{m.zone}</p>
                  <p className="text-sm text-foreground/80 mt-2">{m.note}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CDS footer */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground border-t border-border pt-4">
          <ShieldCheck className="h-3.5 w-3.5 text-primary/70" />
          <span>{CDS_DISCLAIMER_SHORT}</span>
        </div>
      </div>
    </div>
  );
}
