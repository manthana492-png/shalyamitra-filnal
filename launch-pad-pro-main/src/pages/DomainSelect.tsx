/**
 * DomainSelect — Pre-session domain chooser.
 *
 * The surgeon selects between Ayurveda Surgery (Shalya Tantra) and
 * Modern Surgery (Allopathy · Evidence-Based) before configuring a new
 * OR session. Both paths lead to the same NewSession form.
 *
 * Also exposes the Knowledge Vault (ज्ञान कोष) for past sessions,
 * Shlokas, and Marma Atlas.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { NaelLogo } from "@/components/NaelLogo";
import { KnowledgeVault } from "@/components/KnowledgeVault";
import { Button } from "@/components/ui/button";
import {
  Leaf, Dna, ArrowRight, BookOpen, Landmark,
} from "lucide-react";

// ── Domain Cards Data ────────────────────────────────────────────────────

const DOMAINS = [
  {
    id: "ayurveda",
    title: "AYURVEDA SURGERY",
    subtitle: "Shalya Tantra · MS Ayurved",
    icon: Leaf,
    iconColor: "text-green-400",
    glowColor: "hsl(120, 60%, 40%)",
    tags: ["Sushruta Samhita", "Ksharasutra", "Agnikarma", "Marma Points"],
    bottomTag: "CCIM / NMC",
    decorative: "yantra", // which decorative SVG to show
  },
  {
    id: "modern",
    title: "MODERN SURGERY",
    subtitle: "Allopathy · Evidence-Based",
    icon: Dna,
    iconColor: "text-sky-400",
    glowColor: "hsl(200, 80%, 55%)",
    tags: ["Bailey & Love", "Schwartz", "Gray's Anatomy", "NICE / ACS"],
    bottomTag: "ERAS",
    decorative: "helix", // which decorative SVG to show
  },
] as const;

// ── Yantra Decorative SVG (Ayurveda) ─────────────────────────────────────

function YantraDecor() {
  return (
    <svg viewBox="0 0 120 120" className="w-20 h-20 mx-auto opacity-30">
      {/* Outer octagon */}
      <polygon
        points="60,5 95,20 110,55 95,90 60,105 25,90 10,55 25,20"
        fill="none" stroke="hsl(var(--primary))" strokeWidth="0.8"
      />
      {/* Inner octagon */}
      <polygon
        points="60,25 80,35 90,55 80,75 60,85 40,75 30,55 40,35"
        fill="none" stroke="hsl(var(--primary))" strokeWidth="0.5"
        strokeDasharray="3 3"
      />
      {/* Center circle */}
      <circle cx="60" cy="55" r="12" fill="none"
        stroke="hsl(var(--primary))" strokeWidth="0.6" />
      <circle cx="60" cy="55" r="4" fill="hsl(var(--primary))" opacity="0.3" />
      {/* Crosshairs */}
      <line x1="60" y1="5" x2="60" y2="105" stroke="hsl(var(--primary))" strokeWidth="0.3" opacity="0.3" />
      <line x1="10" y1="55" x2="110" y2="55" stroke="hsl(var(--primary))" strokeWidth="0.3" opacity="0.3" />
    </svg>
  );
}

// ── Helix Decorative SVG (Modern) ────────────────────────────────────────

function HelixDecor() {
  return (
    <svg viewBox="0 0 160 80" className="w-32 h-16 mx-auto opacity-30">
      {/* DNA helix strands */}
      <path
        d="M10,40 Q30,10 50,40 Q70,70 90,40 Q110,10 130,40 Q150,70 160,40"
        fill="none" stroke="hsl(200, 80%, 55%)" strokeWidth="1.2"
      />
      <path
        d="M10,40 Q30,70 50,40 Q70,10 90,40 Q110,70 130,40 Q150,10 160,40"
        fill="none" stroke="hsl(217, 100%, 62%)" strokeWidth="1.2"
      />
      {/* Rungs */}
      {[30, 50, 70, 90, 110, 130].map((x, i) => (
        <line key={i} x1={x} y1={25 + (i % 2) * 10} x2={x} y2={45 - (i % 2) * 10}
          stroke="hsl(var(--primary))" strokeWidth="0.5" opacity="0.4" />
      ))}
    </svg>
  );
}

// ── Main Component ──────────────────────────────────────────────────────

const DomainSelect = () => {
  const navigate = useNavigate();
  const [vaultOpen, setVaultOpen] = useState(false);

  const handleDomainClick = (domainId: string) => {
    // Both domains go to same NewSession page — domain stored as query param
    navigate(`/sessions/new?domain=${domainId}`);
  };

  return (
    <AppShell>
      <CdsBanner />
      <div className="hud-scanline min-h-[calc(100vh-4rem)]">
        <div className="container py-10 md:py-16 max-w-5xl">

          {/* ── Header ── */}
          <div className="text-center">
            <NaelLogo size="md" />
            <h1 className="text-devanagari text-4xl md:text-5xl font-bold mt-6 bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 bg-clip-text text-transparent">
              शल्य मित्र
            </h1>
            <p className="text-mono text-[11px] uppercase tracking-[0.35em] text-primary/70 mt-3">
              AI Surgical Intelligence · v4.0
            </p>
          </div>

          {/* ── Domain Cards ── */}
          <div className="grid md:grid-cols-2 gap-5 mt-12 max-w-4xl mx-auto">
            {DOMAINS.map((d) => {
              const Icon = d.icon;
              return (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => handleDomainClick(d.id)}
                  className="group hud-frame hud-corners relative p-6 md:p-8 text-left transition-all duration-300 hover:shadow-glow-strong hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <span className="corner-tr" /><span className="corner-bl" />

                  {/* Decorative background */}
                  <div className="flex justify-center mb-5">
                    {d.decorative === "yantra" ? <YantraDecor /> : <HelixDecor />}
                  </div>

                  {/* Icon */}
                  <div className="flex justify-center mb-4">
                    <div className="w-14 h-14 rounded-full border border-primary/30 bg-surface-2/60 flex items-center justify-center group-hover:shadow-glow transition-shadow">
                      <Icon className={`h-7 w-7 ${d.iconColor}`} />
                    </div>
                  </div>

                  {/* Title */}
                  <h2 className="text-mono text-lg md:text-xl font-semibold tracking-[0.15em] text-center text-primary text-glow">
                    {d.title}
                  </h2>
                  <p className="text-center text-sm text-muted-foreground mt-1.5">
                    {d.subtitle}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap justify-center gap-2 mt-5">
                    {d.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-mono text-[10px] uppercase tracking-[0.1em] px-2.5 py-1 rounded-full border border-primary/25 bg-surface-2/40 text-primary/70"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex justify-center mt-3">
                    <span className="text-mono text-[10px] uppercase tracking-[0.15em] px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary/80">
                      {d.bottomTag}
                    </span>
                  </div>

                  {/* Hover arrow */}
                  <div className="flex justify-center mt-5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowRight className="h-5 w-5 text-primary" />
                  </div>
                </button>
              );
            })}
          </div>

          {/* ── Knowledge Vault Button ── */}
          <div className="flex justify-center mt-10">
            <Button
              variant="outline"
              className="border-amber-500/40 text-amber-400/80 hover:text-amber-300 hover:border-amber-500/60 gap-2"
              onClick={() => setVaultOpen(true)}
            >
              <Landmark className="h-4 w-4" />
              <span className="text-mono text-[11px] uppercase tracking-[0.2em]">
                Knowledge Vault
              </span>
            </Button>
          </div>

        </div>
      </div>

      {/* Knowledge Vault Overlay */}
      {vaultOpen && (
        <KnowledgeVault onClose={() => setVaultOpen(false)} />
      )}
    </AppShell>
  );
};

export default DomainSelect;
