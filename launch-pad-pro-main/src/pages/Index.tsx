import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { NaelLogo } from "@/components/NaelLogo";
import { CdsBanner } from "@/components/CdsBanner";
import {
  Brain, Eye, Mic, ShieldCheck, Zap, ArrowRight,
  Headphones, Stethoscope, Lock, Camera, Cpu, Radio, ScanLine,
} from "lucide-react";
import heroImage from "@/assets/hero-hud.jpg";

const Index = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-background hud-scanline">
      {/* Top nav */}
      <header className="sticky top-0 z-30 border-b border-primary/20 bg-background/80 backdrop-blur-md">
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
        <div className="container flex h-14 items-center justify-between">
          <NaelLogo />
          <nav className="hidden md:flex items-center gap-7 text-mono text-[11px] tracking-[0.2em] uppercase text-muted-foreground">
            <a href="#capabilities" className="hover:text-primary transition-colors">Capabilities</a>
            <a href="#cameras" className="hover:text-primary transition-colors">Vision</a>
            <a href="#modes" className="hover:text-primary transition-colors">Modes</a>
            <a href="#compliance" className="hover:text-primary transition-colors">Compliance</a>
            <a href="#architecture" className="hover:text-primary transition-colors">Stack</a>
          </nav>
          <div className="flex items-center gap-2">
            {user ? (
              <Button asChild size="sm" className="bg-gradient-primary text-primary-foreground shadow-glow"><Link to="/dashboard">Open console <ArrowRight className="ml-1.5 h-4 w-4" /></Link></Button>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm"><Link to="/auth">Sign in</Link></Button>
                <Button asChild size="sm" className="bg-gradient-primary text-primary-foreground shadow-glow"><Link to="/auth?mode=signup">Request access</Link></Button>
              </>
            )}
          </div>
        </div>
      </header>

      <CdsBanner />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-glow" aria-hidden />
        <div className="absolute inset-0 hud-grid opacity-30" aria-hidden />
        <div className="container relative py-16 md:py-24">
          <div className="grid lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-surface-2/60 backdrop-blur px-3 py-1 text-mono text-[10px] uppercase tracking-[0.2em] text-primary">
                <span className="pulse-dot live" />
                <span>v3.0 · Eight Intelligence Pillars · Production ready</span>
              </div>
              <h1 className="text-display mt-6 text-4xl md:text-6xl font-semibold tracking-tight">
                Eight intelligences.{" "}
                <span className="bg-gradient-primary bg-clip-text text-transparent text-glow-strong">One surgical companion.</span>
              </h1>
              <p className="mt-5 text-lg text-muted-foreground max-w-xl">
                ShalyaMitra is a surgical intelligence platform. Nael — its voice — sees, listens, and speaks
                alongside the surgeon. Eight AI pillars from haemorrhage detection to Suśruta's wisdom.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg" className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
                  <Link to={user ? "/sessions/new" : "/auth?mode=signup"}>
                    {user ? "Start a session" : "Request pilot access"} <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="border-primary/40">
                  <Link to={user ? "/dashboard" : "/auth"}>{user ? "Open dashboard" : "Sign in"}</Link>
                </Button>
              </div>

              <dl className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl">
                {[
                  { k: "8 pillars", v: "intelligence systems" },
                  { k: "3 cams",  v: "laparo · overhead · monitor" },
                  { k: "7 states", v: "AI-driven layout engine" },
                  { k: "<500ms",    v: "haemorrhage detection" },
                ].map((s) => (
                  <div key={s.k}>
                    <dt className="text-mono text-2xl font-semibold text-primary text-glow">{s.k}</dt>
                    <dd className="text-[11px] uppercase tracking-wider text-muted-foreground mt-1">{s.v}</dd>
                  </div>
                ))}
              </dl>
            </div>

            <div className="lg:col-span-6 relative">
              <div className="hud-frame hud-corners relative aspect-video overflow-hidden">
                <span className="corner-tr" /><span className="corner-bl" />
                <img
                  src={heroImage}
                  alt="ShalyaMitra theatre HUD with 3 camera feeds, overlays, and live vitals"
                  className="absolute inset-0 h-full w-full object-cover"
                  width={1536}
                  height={896}
                />
                <div className="hud-sweep" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute top-3 left-3 text-mono text-[10px] tracking-[0.25em] text-primary text-glow">
                  ◆ SHALYAMITRA · OR-3 · LIVE
                </div>
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-mono text-[10px] uppercase tracking-wider text-primary/80">
                  <span className="flex items-center gap-1.5"><span className="pulse-dot live" /> 3 STREAMS · NEMO PROACTIVE</span>
                  <span>HR 72 · SpO₂ 98 · MAP 82</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Camera vision array */}
      <section id="cameras" className="py-20 border-t border-primary/15">
        <div className="container">
          <div className="max-w-2xl">
            <div className="text-hud-label">VISION ARRAY</div>
            <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2">
              Three feeds. One situational picture.
            </h2>
            <p className="mt-4 text-muted-foreground">
              ShalyaMitra fuses laparoscope, overhead, and patient-monitor cameras through NVIDIA Triton —
              then Nael surfaces anatomy overlays, Marma proximity, and safety alerts in real time.
            </p>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {[
              { i: Camera,   t: "CAM 1 · LAPAROSCOPE", d: "Critical View of Safety detection, instrument tracking, bleeding heuristics." },
              { i: ScanLine, t: "CAM 2 · OVERHEAD",    d: "Theatre overview, count compliance, sharps tracking, staff positioning." },
              { i: Radio,    t: "CAM 3 · PATIENT",     d: "Anaesthesia monitor OCR. Vitals captured even when EHR is offline." },
            ].map((f) => (
              <div key={f.t} className="hud-frame hud-corners relative p-5 hover:shadow-glow transition-shadow">
                <span className="corner-tr" /><span className="corner-bl" />
                <f.i className="h-5 w-5 text-primary" />
                <h3 className="mt-3 text-sm font-semibold tracking-wide">{f.t}</h3>
                <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">{f.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section id="capabilities" className="py-20 border-t border-primary/15">
        <div className="container">
          <div className="max-w-2xl">
            <div className="text-hud-label">CAPABILITIES</div>
            <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2">
              Built for the cognitive load of an OR.
            </h2>
            <p className="mt-4 text-muted-foreground">
              Voice-first, glanceable, agent-controlled HUD — tuned for the dim, time-critical environment of surgery.
            </p>
          </div>
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { i: Eye,         t: "Tri-stream vision",   d: "3 cameras fused with NVIDIA Triton inference into one situational picture." },
              { i: Mic,         t: "Full-duplex voice",   d: "Listens while it speaks. Wake word + Web Speech control of the entire HUD." },
              { i: Brain,       t: "Agentic UI Director", d: "Nael rearranges the 7-state layout based on phase, alerts, and surgeon voice — with a lock override." },
              { i: Zap,         t: "Sub-250ms target",    d: "India-aware 3-tier latency router. Edge / regional GPU / fallback." },
              { i: ShieldCheck, t: "CDS-wrapped",         d: "Every output passes through the disclaimer wrapper. Decision support, not diagnosis." },
              { i: Lock,        t: "DPDP-aligned",        d: "Morpheus PHI redaction on-GPU, append-only audit log, role-based access." },
            ].map((f) => (
              <div key={f.t} className="panel p-5 hover:border-primary/40 transition-colors">
                <f.i className="h-5 w-5 text-primary" />
                <h3 className="mt-3 font-semibold">{f.t}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{f.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Modes */}
      <section id="modes" className="py-20 border-t border-primary/15 bg-surface-1/40">
        <div className="container">
          <div className="max-w-2xl">
            <div className="text-hud-label">INTERACTION MODES</div>
            <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2">
              Three modes. One voice command away.
            </h2>
            <p className="mt-4 text-muted-foreground">
              The surgeon decides how present Nael is — moment to moment, case to case. Plus three voice control
              modes (Conservative / Dynamic / Agentic) deciding how much Nael can rearrange the UI itself.
            </p>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {[
              { name: "SILENT",    d: "Listens and logs. Surfaces only critical alerts. Use for the most delicate phases." },
              { name: "REACTIVE",  d: "Answers when asked. Surfaces warnings and critical alerts. The default mode." },
              { name: "PROACTIVE", d: "Volunteers reminders and protocol cues. Best for teaching cases and complex procedures." },
            ].map((m) => (
              <div key={m.name} className="hud-frame hud-corners relative p-6">
                <span className="corner-tr" /><span className="corner-bl" />
                <div className="text-hud-label">MODE</div>
                <div className="mt-2 text-2xl font-semibold text-glow">{m.name}</div>
                <p className="mt-3 text-sm text-muted-foreground">{m.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Compliance */}
      <section id="compliance" className="py-20 border-t border-primary/15">
        <div className="container grid gap-10 lg:grid-cols-2">
          <div>
            <div className="text-hud-label">COMPLIANCE</div>
            <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2">
              Architected as a CDS tool from day one.
            </h2>
            <p className="mt-4 text-muted-foreground">
              ShalyaMitra is structurally a Clinical Decision Support tool — not a diagnostic device. Every surface
              and every Nael voice line is wrapped with the CDS disclaimer. Every action is written to an
              append-only audit log. PHI is redacted on the GPU before it ever leaves the OR.
            </p>
            <ul className="mt-6 space-y-3 text-sm">
              {[
                "Class A/B software classification path under India's Medical Devices Rules 2017",
                "DPDP Act 2023 alignment — pseudonymous patient codes, no real PHI in transcripts",
                "Append-only audit log for every clinical action",
                "Mandatory session disclaimer accepted by the operating team",
                "Role-based access — surgeon, anaesthetist, admin/compliance",
              ].map((p) => (
                <li key={p} className="flex items-start gap-2.5">
                  <ShieldCheck className="mt-0.5 h-4 w-4 text-primary shrink-0" />
                  <span className="text-muted-foreground">{p}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="hud-frame hud-corners relative p-6 self-start">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="flex items-center gap-2 text-hud-label">
              <ShieldCheck className="h-4 w-4 text-primary" /> CDS WRAPPER · SAMPLE
            </div>
            <div className="mt-4 rounded-md border border-primary/20 bg-background/60 p-4">
              <div className="text-sm">
                <span className="text-mono text-[10px] uppercase tracking-[0.25em] text-primary text-glow">NAEL</span>
                <p className="mt-2 text-foreground">
                  Mean arterial pressure has dropped 14 points over 90 seconds. Consider reviewing depth of
                  anaesthesia and fluid status.
                </p>
                <div className="mt-3 border-t border-primary/15 pt-3 text-xs text-muted-foreground">
                  Decision support — not a diagnosis. Final clinical judgement rests with the operating team.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="py-20 border-t border-primary/15 bg-surface-1/40">
        <div className="container">
          <div className="max-w-2xl">
            <div className="text-hud-label">STACK</div>
            <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2">
              The web layer of a much bigger system.
            </h2>
            <p className="mt-4 text-muted-foreground">
              This application is the surgeon-facing surface of ShalyaMitra. Behind it sits the GPU stack:
              NVIDIA Riva ASR, NeMo proactive engine, Morpheus PHI redaction, Triton inference, and Guardrails.
              Deployable on Lightning AI, RunPod, or self-hosted H100 racks.
            </p>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-3">
            {[
              { i: Headphones,  t: "Edge: voice + vision",     d: "OR-side capture — 3 cameras, surgical neckband, monitor OCR." },
              { i: Cpu,         t: "GPU: intelligence core",   d: "Riva ASR → NeMo reasoning → Morpheus PHI → Triton vision → Guardrails." },
              { i: Stethoscope, t: "Web: this app",            d: "Surgeon HUD console, pre/post-op flows, admin compliance dashboard." },
            ].map((c) => (
              <div key={c.t} className="hud-frame hud-corners relative p-5">
                <span className="corner-tr" /><span className="corner-bl" />
                <c.i className="h-5 w-5 text-primary" />
                <h3 className="mt-3 font-semibold">{c.t}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{c.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 border-t border-primary/15">
        <div className="container">
          <div className="hud-frame hud-corners relative overflow-hidden p-10 md:p-14">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="absolute inset-0 bg-gradient-glow opacity-60" aria-hidden />
            <div className="relative max-w-2xl">
              <h2 className="text-display text-3xl md:text-4xl font-semibold tracking-tight">
                Bring ShalyaMitra into your theatre.
              </h2>
              <p className="mt-4 text-muted-foreground">
                Pilot the ShalyaMitra theatre console with your team today. Connect your NVIDIA GPU backend —
                the eight-pillar intelligence is ready.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg" className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
                  <Link to={user ? "/sessions/new" : "/auth?mode=signup"}>
                    {user ? "Start a session" : "Request pilot access"} <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                {!user && (
                  <Button asChild variant="outline" size="lg" className="border-primary/40"><Link to="/auth">Sign in</Link></Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-primary/15 py-8">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <NaelLogo size="sm" showWordmark={false} />
            <span>ShalyaMitra · Surgical Intelligence · Nael Companion</span>
          </div>
          <div className="text-mono text-[10px] uppercase tracking-wider">Clinical Decision Support · Not a diagnostic device · v3.0</div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
