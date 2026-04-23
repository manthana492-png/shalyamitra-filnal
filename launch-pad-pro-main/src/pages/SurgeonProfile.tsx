/**
 * SurgeonProfile — Surgeon settings & preferences.
 * Route: /settings/profile
 */

import { useState, useRef } from "react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NaelLogo } from "@/components/NaelLogo";
import {
  User, Mic, Bell, Eye, Lock, CheckCircle, Volume2, Brain, Upload, Play,
} from "lucide-react";
import { cn } from "@/lib/utils";

const SPECIALTIES = [
  "General Surgery", "Cardiothoracic Surgery", "Orthopaedic Surgery",
  "Neurosurgery", "Urology", "Gynaecology", "Vascular Surgery",
  "Paediatric Surgery", "Plastic Surgery",
];

const LOCKED_ALERTS = ["haemorrhage", "instrument_discrepancy", "devils_advocate"];

type AlertPref = "all" | "critical" | "none";

const ALERT_PREF_LABELS: Record<AlertPref, string> = {
  all: "All",
  critical: "Critical only",
  none: "Silent",
};

/* ── Voice Profiles ───────────────────────────────────── */
const VOICE_PROFILES = [
  { id: "nael_calm",       name: "Nael — Calm",               desc: "Default. Calm, composed, warm professional voice.", gender: "neutral" },
  { id: "nael_female_pro", name: "Nael — Professional Female", desc: "Clear, confident female voice with clinical precision.", gender: "female" },
  { id: "nael_male_pro",   name: "Nael — Professional Male",   desc: "Steady, authoritative male voice.", gender: "male" },
  { id: "nael_warm",       name: "Nael — Warm Companion",      desc: "Softer, empathetic voice with a reassuring quality.", gender: "neutral" },
  { id: "nael_classical",  name: "Nael — Classical",            desc: "Deeper, measured, Oracle-inspired tone.", gender: "male" },
] as const;

const SAFETY_VOICES = [
  { id: "alert_urgent", name: "Critical Alert Voice",  desc: "Firm, urgent tone for haemorrhage and critical safety alerts." },
  { id: "alert_warning", name: "Warning Alert Voice",  desc: "Measured but firm tone for warning-level alerts." },
];

export default function SurgeonProfile() {
  const [name, setName] = useState("Dr. Shivalumar");
  const [specialty, setSpecialty] = useState("General Surgery");
  const [naelMode, setNaelMode] = useState<"conservative" | "dynamic" | "agentic">("dynamic");
  const [voiceProfile, setVoiceProfile] = useState("nael_calm");
  const [customVoiceName, setCustomVoiceName] = useState<string | null>(null);
  const [overlayOpacity, setOverlayOpacity] = useState(70);
  const [shlokaFormat, setShlokaFormat] = useState<"devanagari" | "transliteration" | "both">("both");
  const [alertPrefs, setAlertPrefs] = useState<Record<string, AlertPref>>({
    monitor: "all",
    pharmacist: "critical",
    scholar: "critical",
    chronicler: "all",
  });
  const [saved, setSaved] = useState(false);
  const [testingVoice, setTestingVoice] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleVoiceTest = async (voiceId: string) => {
    setTestingVoice(voiceId);
    // In production: POST /api/voice/voices/test { voice_id, text }
    // For now: use browser speechSynthesis as preview
    if ("speechSynthesis" in window) {
      const utter = new SpeechSynthesisUtterance(
        "Good morning, Doctor. Pre-operative analysis loaded. I'm here when you need me."
      );
      utter.rate = 0.95;
      utter.onend = () => setTestingVoice(null);
      window.speechSynthesis.speak(utter);
    } else {
      setTimeout(() => setTestingVoice(null), 2000);
    }
  };

  const handleCustomUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    // In production: POST /api/voice/voices/custom with the file
    setCustomVoiceName(file.name);
    setVoiceProfile("custom");
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-6 py-8 space-y-8">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <User className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-semibold">Surgeon Profile</h1>
          </div>
          <p className="text-sm text-muted-foreground">Your ShalyaMitra preferences and Nael configuration</p>
        </div>

        {/* Basic info */}
        <div className="panel p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
            <User className="h-4 w-4 text-primary" /> Identity
          </h2>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">Full name & title</label>
              <input
                className="w-full rounded-md border border-border bg-surface-2 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary/60"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">Specialty</label>
              <select
                className="w-full rounded-md border border-border bg-surface-2 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary/60"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
              >
                {SPECIALTIES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Nael mode */}
        <div className="panel p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
            <Brain className="h-4 w-4 text-primary" /> Nael Intelligence Mode
          </h2>
          <div className="grid grid-cols-3 gap-2">
            {(["conservative", "dynamic", "agentic"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setNaelMode(m)}
                className={cn(
                  "rounded-lg border px-3 py-3 text-left transition-all",
                  naelMode === m
                    ? "border-primary/60 bg-primary/10 ring-1 ring-primary/40"
                    : "border-border hover:border-border-strong hover:bg-surface-2"
                )}
              >
                <p className={cn("text-xs font-semibold uppercase tracking-wider", naelMode === m ? "text-primary" : "text-foreground/70")}>
                  {m}
                </p>
                <p className="text-[10px] text-muted-foreground mt-1">
                  {m === "conservative" && "Voice only changes mode/mute"}
                  {m === "dynamic" && "Voice controls layout & overlays"}
                  {m === "agentic" && "Nael proactively re-layouts"}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* ── Voice Profile Selection ────────────────────── */}
        <div className="panel p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
            <Volume2 className="h-4 w-4 text-primary" /> Nael Voice Profile
          </h2>
          <p className="text-xs text-muted-foreground">
            Choose Nael's conversational voice. Safety alert voices are locked and cannot be changed.
          </p>

          {/* Selectable voices */}
          <div className="space-y-2">
            {VOICE_PROFILES.map((v) => (
              <button
                key={v.id}
                onClick={() => setVoiceProfile(v.id)}
                className={cn(
                  "w-full flex items-center justify-between rounded-lg border px-4 py-3 text-left transition-all",
                  voiceProfile === v.id
                    ? "border-primary/60 bg-primary/10 ring-1 ring-primary/40"
                    : "border-border hover:border-border-strong hover:bg-surface-2"
                )}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Mic className={cn("h-3.5 w-3.5", voiceProfile === v.id ? "text-primary" : "text-muted-foreground")} />
                    <span className={cn("text-sm font-medium", voiceProfile === v.id ? "text-primary" : "text-foreground/80")}>{v.name}</span>
                    {v.id === "nael_calm" && <Badge variant="outline" className="text-[8px] px-1.5 py-0 border-primary/30 text-primary">Default</Badge>}
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-0.5 ml-5.5">{v.desc}</p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); handleVoiceTest(v.id); }}
                  disabled={testingVoice !== null}
                  className={cn(
                    "ml-3 rounded-full p-1.5 border transition-all",
                    testingVoice === v.id
                      ? "border-primary bg-primary/20 text-primary animate-pulse"
                      : "border-border text-muted-foreground hover:text-primary hover:border-primary/40"
                  )}
                  title="Preview voice"
                >
                  <Play className="h-3 w-3" />
                </button>
              </button>
            ))}

            {/* Custom voice upload */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "w-full flex items-center justify-between rounded-lg border border-dashed px-4 py-3 text-left transition-all",
                voiceProfile === "custom"
                  ? "border-primary/60 bg-primary/10"
                  : "border-border hover:border-primary/40 hover:bg-surface-2"
              )}
            >
              <div className="flex items-center gap-2">
                <Upload className="h-3.5 w-3.5 text-muted-foreground" />
                <span className="text-sm text-foreground/80">
                  {customVoiceName ? `Custom: ${customVoiceName}` : "Upload Custom Voice (10-30s WAV/MP3)"}
                </span>
              </div>
              <span className="text-[10px] text-muted-foreground">Fish Speech cloning</span>
            </button>
            <input ref={fileInputRef} type="file" accept="audio/wav,audio/mp3,audio/mpeg" className="hidden" onChange={handleCustomUpload} />
          </div>

          {/* Safety voices (locked) */}
          <div className="mt-3 pt-3 border-t border-border/50">
            <p className="text-[10px] text-muted-foreground mb-2 uppercase tracking-wider font-semibold">Safety Voices (Locked)</p>
            {SAFETY_VOICES.map((v) => (
              <div key={v.id} className="flex items-center gap-2 rounded-md px-3 py-2 opacity-60">
                <Lock className="h-3 w-3 text-critical" />
                <span className="text-xs text-foreground/70">{v.name}</span>
                <span className="text-[9px] text-muted-foreground ml-auto">{v.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Alert preferences */}
        <div className="panel p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
            <Bell className="h-4 w-4 text-primary" /> Alert Preferences
          </h2>
          <p className="text-xs text-muted-foreground">
            Locked alerts cannot be silenced — they are critical safety systems.
          </p>
          <div className="space-y-2">
            {/* Locked alerts */}
            {LOCKED_ALERTS.map((pillar) => (
              <div key={pillar} className="flex items-center justify-between rounded-md border border-border/50 px-3 py-2.5">
                <div className="flex items-center gap-2">
                  <Lock className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-sm capitalize">{pillar.replace("_", " ")}</span>
                </div>
                <Badge variant="outline" className="text-[9px] text-critical border-critical/30">
                  Always on
                </Badge>
              </div>
            ))}
            {/* Configurable */}
            {Object.entries(alertPrefs).map(([pillar, pref]) => (
              <div key={pillar} className="flex items-center justify-between rounded-md border border-border px-3 py-2.5">
                <span className="text-sm capitalize">{pillar}</span>
                <div className="flex gap-1">
                  {(["all", "critical", "none"] as AlertPref[]).map((p) => (
                    <button
                      key={p}
                      onClick={() => setAlertPrefs((prev) => ({ ...prev, [pillar]: p }))}
                      className={cn(
                        "rounded px-2 py-0.5 text-[10px] uppercase tracking-wider transition-all",
                        pref === p
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:text-foreground border border-border"
                      )}
                    >
                      {ALERT_PREF_LABELS[p]}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Display preferences */}
        <div className="panel p-5 space-y-4">
          <h2 className="text-sm font-semibold text-foreground/90 flex items-center gap-2">
            <Eye className="h-4 w-4 text-primary" /> Display Preferences
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-muted-foreground mb-2 block">
                Anatomy overlay opacity: <span className="text-foreground font-medium">{overlayOpacity}%</span>
              </label>
              <input
                type="range" min={20} max={100} step={5}
                value={overlayOpacity}
                onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-2 block">Shloka display format</label>
              <div className="flex gap-2">
                {(["devanagari", "transliteration", "both"] as const).map((f) => (
                  <button
                    key={f}
                    onClick={() => setShlokaFormat(f)}
                    className={cn(
                      "rounded-md px-3 py-1.5 text-xs border transition-all",
                      shlokaFormat === f
                        ? "border-pillar-oracle bg-pillar-oracle/10 text-pillar-oracle"
                        : "border-border text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {f === "devanagari" && "देवनागरी"}
                    {f === "transliteration" && "Transliteration"}
                    {f === "both" && "Both"}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Save */}
        <div className="flex justify-end">
          <Button
            onClick={handleSave}
            className={cn(
              "transition-all",
              saved ? "bg-success text-success-foreground" : "bg-gradient-primary text-primary-foreground shadow-glow"
            )}
          >
            {saved ? (
              <><CheckCircle className="mr-2 h-4 w-4" /> Saved</>
            ) : (
              "Save Preferences"
            )}
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
