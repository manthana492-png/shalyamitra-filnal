import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { GPU_PRESETS, MODULE_DESCRIPTIONS, type GpuHost } from "@/lib/gpu-adapter";
import { Loader2, RefreshCw, Cpu, Wifi, WifiOff, ShieldCheck, Server } from "lucide-react";
import { CdsBanner } from "@/components/CdsBanner";

type HealthRes = {
  ok: boolean;
  mode: "live" | "demo";
  host: GpuHost;
  hasUrl: boolean;
  hasToken: boolean;
  protocol: string;
  message: string;
};

const AdminGpu = () => {
  const [health, setHealth] = useState<HealthRes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const projectId = import.meta.env.VITE_SUPABASE_PROJECT_ID as string | undefined;

  const check = async () => {
    setLoading(true); setError(null);
    try {
      const url = `https://${projectId}.functions.supabase.co/aria-realtime/health`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as HealthRes;
      setHealth(json);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { check(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  const isLive = health?.mode === "live";

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-5xl">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-hud-label">INFRASTRUCTURE</div>
            <h1 className="text-display text-3xl font-semibold tracking-tight mt-1">GPU Backend</h1>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
              Wires the ARIA web layer to the NVIDIA GPU stack — Riva, NeMo, Morpheus, Triton, Guardrails.
              Drop in your <code className="text-mono text-primary">GPU_BACKEND_URL</code> + <code className="text-mono text-primary">GPU_BACKEND_TOKEN</code> via
              backend secrets and the realtime relay goes live. No UI changes needed.
            </p>
          </div>
          <Button onClick={check} variant="outline" size="sm" className="border-primary/40">
            {loading ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-1.5 h-4 w-4" />}
            Re-check
          </Button>
        </div>

        {/* Status card */}
        <div className="mt-8 hud-frame hud-corners relative p-6">
          <span className="corner-tr" /><span className="corner-bl" />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`h-10 w-10 rounded-full flex items-center justify-center ${isLive ? "bg-success/20" : "bg-muted/30"}`}>
                {isLive ? <Wifi className="h-5 w-5 text-success" /> : <WifiOff className="h-5 w-5 text-muted-foreground" />}
              </div>
              <div>
                <div className="text-mono text-[10px] uppercase tracking-[0.25em] text-primary/70">RELAY STATUS</div>
                <div className="text-lg font-semibold mt-0.5">
                  {error ? "Health check failed" : isLive ? `Live · ${health?.host}` : "Demo mode"}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {error ?? health?.message ?? "Checking…"}
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <Badge variant="outline" className={`text-[10px] uppercase ${isLive ? "border-success/40 text-success" : "border-border"}`}>
                {health?.mode ?? "—"}
              </Badge>
              <Badge variant="outline" className="text-[10px] text-mono">
                Protocol {health?.protocol ?? "—"}
              </Badge>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
            <div className="rounded-lg bg-surface-1/60 p-3 border border-border/50">
              <div className="text-hud-label mb-1">GPU_BACKEND_URL</div>
              <div className="text-mono text-xs">{health?.hasUrl ? "✓ configured" : "— not set"}</div>
            </div>
            <div className="rounded-lg bg-surface-1/60 p-3 border border-border/50">
              <div className="text-hud-label mb-1">GPU_BACKEND_TOKEN</div>
              <div className="text-mono text-xs">{health?.hasToken ? "✓ configured" : "— not set"}</div>
            </div>
          </div>
        </div>

        {/* Hosting presets */}
        <div className="mt-10">
          <h2 className="text-display text-xl font-semibold mb-4">Hosting Presets</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {GPU_PRESETS.map((p) => (
              <div key={p.id} className="hud-frame hud-corners relative p-5">
                <span className="corner-tr" /><span className="corner-bl" />
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Server className="h-4 w-4 text-primary" />
                    <h3 className="font-semibold">{p.name}</h3>
                  </div>
                  {health?.host === p.id && (
                    <Badge variant="outline" className="text-[10px] border-success/40 text-success">CURRENT</Badge>
                  )}
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{p.recommendedGpu}</p>
                <p className="mt-3 text-xs text-foreground/80 leading-relaxed">{p.endpointShape}</p>
                <div className="mt-3 space-y-1.5">
                  {p.envVars.map((v) => (
                    <div key={v.name} className="text-mono text-[10px] flex items-start gap-2">
                      <span className="text-primary/80 shrink-0">{v.name}</span>
                      <span className="text-muted-foreground truncate" title={v.example}>= {v.example}</span>
                    </div>
                  ))}
                </div>
                {p.consoleUrl && (
                  <a href={p.consoleUrl} target="_blank" rel="noreferrer"
                     className="mt-4 inline-block text-xs text-primary hover:underline">
                    Open {p.name} console →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Module map */}
        <div className="mt-10">
          <h2 className="text-display text-xl font-semibold mb-4">NVIDIA Module Map</h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(MODULE_DESCRIPTIONS).map(([k, v]) => (
              <div key={k} className="panel p-4">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-primary" />
                  <h3 className="text-sm font-semibold">{v.name}</h3>
                </div>
                <p className="mt-1.5 text-xs text-muted-foreground">{v.purpose}</p>
                <div className="mt-2 text-mono text-[10px] uppercase tracking-wider text-primary/60">{k}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-10 panel-strong p-6">
          <div className="flex items-center gap-2 text-hud-label">
            <ShieldCheck className="h-4 w-4 text-primary" /> SECURITY
          </div>
          <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
            Tokens are stored as backend secrets and never exposed to the browser. The relay runs as a Lovable Cloud function;
            audio & video frames go directly through it (or via WebRTC) to your GPU box. PHI redaction happens inside Morpheus
            on your GPU before any transcript is written to the database.
          </p>
        </div>
      </div>
    </AppShell>
  );
};

export default AdminGpu;
