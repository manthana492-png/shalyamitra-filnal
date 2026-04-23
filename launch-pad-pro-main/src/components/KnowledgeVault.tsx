/**
 * KnowledgeVault — ज्ञान कोष
 *
 * Full-screen overlay with 3 tabs:
 *  - Sessions  : Past completed sessions archive
 *  - Shlokas   : Sushruta Samhita reference shlokas (placeholder)
 *  - Marma Atlas : Anatomical marma point reference (placeholder)
 *
 * Accessible from the DomainSelect page and Dashboard.
 */

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  X, Landmark, FileText, ScrollText, Heart,
} from "lucide-react";

type Tab = "sessions" | "shlokas" | "marma";

const TABS: { id: Tab; label: string; icon: typeof FileText }[] = [
  { id: "sessions", label: "SESSIONS",    icon: FileText  },
  { id: "shlokas",  label: "SHLOKAS",     icon: ScrollText },
  { id: "marma",    label: "MARMA ATLAS", icon: Heart     },
];

export function KnowledgeVault({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<Tab>("sessions");

  return (
    <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-md flex flex-col animate-fade-in">
      {/* ── Header ── */}
      <header className="border-b border-amber-500/20 px-6 py-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Landmark className="h-6 w-6 text-amber-400" />
          <h1 className="text-2xl md:text-3xl font-bold">
            <span className="text-devanagari text-amber-400">ज्ञान कोष</span>
            <span className="text-foreground/90 ml-3">— Knowledge Vault</span>
          </h1>
        </div>
        <Button
          variant="outline"
          onClick={onClose}
          className="border-primary/30 gap-2"
        >
          <X className="h-4 w-4" /> Close
        </Button>
      </header>

      {/* ── Tab Bar ── */}
      <div className="border-b border-primary/15 px-6">
        <nav className="flex gap-0 max-w-4xl">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-6 py-3 text-mono text-[11px] uppercase tracking-[0.2em] transition-colors relative",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
                {/* Active indicator */}
                {isActive && (
                  <span className="absolute bottom-0 inset-x-0 h-[2px] bg-primary rounded-full" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── Content ── */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          {activeTab === "sessions" && <SessionsTab />}
          {activeTab === "shlokas" && <ShlokasTab />}
          {activeTab === "marma" && <MarmaTab />}
        </div>
      </div>
    </div>
  );
}

// ── Sessions Tab ─────────────────────────────────────────────────────────

function SessionsTab() {
  return (
    <div className="text-center py-16">
      <FileText className="h-10 w-10 text-primary/30 mx-auto" />
      <p className="mt-4 text-mono text-sm text-muted-foreground italic">
        No sessions saved yet. Complete a session to see it here.
      </p>
      <p className="mt-2 text-[11px] text-muted-foreground/60 text-mono uppercase tracking-wider">
        Session recordings, transcripts, and AI alerts will be archived here
      </p>
    </div>
  );
}

// ── Shlokas Tab ──────────────────────────────────────────────────────────

function ShlokasTab() {
  const SAMPLE_SHLOKAS = [
    {
      id: 1,
      sanskrit: "शस्त्रं यन्त्रं क्षारं अग्निश्चतुर्विधं कर्मसाधनम्",
      translation: "The four instruments of surgery are: the sharp instrument, the blunt instrument, the alkali, and the fire.",
      source: "Sushruta Samhita, Sutra Sthana 8.3",
    },
    {
      id: 2,
      sanskrit: "अथातो व्रणप्रतिषेधमध्यायं व्याख्यास्यामः",
      translation: "Now we shall expound the chapter on the prevention and management of wounds.",
      source: "Sushruta Samhita, Chikitsa Sthana 1.1",
    },
    {
      id: 3,
      sanskrit: "मर्मस्थानानि सप्तोत्तरशतम्",
      translation: "The vital points (Marma) in the body are one hundred and seven in number.",
      source: "Sushruta Samhita, Sharira Sthana 6.3",
    },
  ];

  return (
    <div className="space-y-4">
      <p className="text-[11px] text-mono text-muted-foreground uppercase tracking-wider mb-6">
        Reference shlokas from Sushruta Samhita — curated for surgical guidance
      </p>
      {SAMPLE_SHLOKAS.map((s) => (
        <div key={s.id} className="hud-frame hud-corners relative p-5">
          <span className="corner-tr" /><span className="corner-bl" />
          <p className="text-devanagari text-lg text-amber-400/90 leading-relaxed">
            {s.sanskrit}
          </p>
          <p className="mt-3 text-sm text-foreground/80 italic">
            "{s.translation}"
          </p>
          <p className="mt-2 text-mono text-[10px] text-primary/50 uppercase tracking-wider">
            {s.source}
          </p>
        </div>
      ))}
      <div className="text-center py-6">
        <p className="text-mono text-[10px] text-muted-foreground/50 uppercase tracking-wider">
          More shlokas will be loaded from the Oracle intelligence pillar
        </p>
      </div>
    </div>
  );
}

// ── Marma Atlas Tab ──────────────────────────────────────────────────────

function MarmaTab() {
  const MARMA_REGIONS = [
    { name: "Shira (Head)", count: 37, description: "Cranial and facial vital points including Adhipati, Sthapani, and Shankha" },
    { name: "Greeva (Neck)", count: 8, description: "Cervical Marma points including Nila and Manya" },
    { name: "Uras (Thorax)", count: 12, description: "Thoracic vital points including Hridaya and Stanamula" },
    { name: "Udara (Abdomen)", count: 3, description: "Abdominal Marma including Nabhi and Basti" },
    { name: "Prushtha (Back)", count: 14, description: "Posterior Marma including Katika Tarun and Nitamba" },
    { name: "Shakha (Extremities)", count: 33, description: "Limb Marma points including Kshipra, Talahridaya, and Kurcha" },
  ];

  return (
    <div>
      <p className="text-[11px] text-mono text-muted-foreground uppercase tracking-wider mb-6">
        107 Marma Points — Sushruta's anatomical vital point classification
      </p>
      <div className="grid md:grid-cols-2 gap-3">
        {MARMA_REGIONS.map((r) => (
          <div key={r.name} className="hud-frame hud-corners relative p-4 hover:shadow-glow transition-shadow">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-foreground/90">{r.name}</h3>
              <span className="text-mono text-lg font-bold text-primary text-glow">{r.count}</span>
            </div>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              {r.description}
            </p>
          </div>
        ))}
      </div>
      <div className="text-center py-6 mt-4">
        <div className="hud-frame hud-corners relative inline-block px-6 py-3">
          <span className="corner-tr" /><span className="corner-bl" />
          <p className="text-mono text-xs text-primary/60 uppercase tracking-wider">
            Total: 107 Marma · 5 Categories · Sadhya Pranahara to Vaikalyakara
          </p>
        </div>
      </div>
    </div>
  );
}

export default KnowledgeVault;
