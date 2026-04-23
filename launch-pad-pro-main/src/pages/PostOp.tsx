import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CDS_DISCLAIMER_FULL } from "@/lib/cds";
import { ShieldCheck, ArrowLeft, Loader2, Download } from "lucide-react";
import { generatePostOpPdf } from "@/lib/post-op-pdf";
import { logAudit } from "@/lib/audit";
import { toast } from "@/hooks/use-toast";

type Session = {
  id: string; procedure_name: string; patient_code: string; status: string;
  surgeon_name: string | null; anaesthetist_name: string | null; theatre: string | null;
  started_at: string | null; ended_at: string | null; notes: string | null;
};
type Transcript = { id: string; speaker: string; text: string; spoken_at: string };
type Alert = { id: string; severity: string; title: string; body: string; source: string | null; created_at: string; acknowledged: boolean };

const PostOp = () => {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<Session | null>(null);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!id) return;
    (async () => {
      const [{ data: s }, { data: t }, { data: a }] = await Promise.all([
        supabase.from("sessions").select("*").eq("id", id).maybeSingle(),
        supabase.from("transcripts").select("*").eq("session_id", id).order("spoken_at"),
        supabase.from("alerts").select("*").eq("session_id", id).order("created_at"),
      ]);
      setSession(s as Session);
      setTranscripts((t ?? []) as Transcript[]);
      setAlerts((a ?? []) as Alert[]);
      setLoading(false);
    })();
  }, [id]);

  const handleExport = async () => {
    if (!session) return;
    setExporting(true);
    try {
      const blob = generatePostOpPdf({
        procedure: session.procedure_name,
        patientCode: session.patient_code,
        theatre: session.theatre,
        surgeon: session.surgeon_name,
        anaesthetist: session.anaesthetist_name,
        startedAt: session.started_at,
        endedAt: session.ended_at,
        notes: session.notes,
        transcripts,
        alerts,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `shalyamitra-${session.patient_code}-${session.id.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      logAudit({ action: "session.export_pdf", sessionId: session.id });
      toast({ title: "Report downloaded", description: "Post-op PDF saved to your device." });
    } catch (e) {
      toast({ title: "Export failed", description: e instanceof Error ? e.message : String(e), variant: "destructive" });
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <AppShell><div className="flex h-96 items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div></AppShell>;
  }
  if (!session) return <AppShell><div className="container py-8">Session not found.</div></AppShell>;

  const dur = session.started_at && session.ended_at
    ? Math.round((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000)
    : null;

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-5xl">
        <Button asChild variant="ghost" size="sm" className="mb-4">
          <Link to="/sessions"><ArrowLeft className="mr-1.5 h-4 w-4" /> All sessions</Link>
        </Button>

        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <div className="text-hud-label">POST-OPERATIVE REVIEW</div>
            <h1 className="text-display text-3xl font-semibold tracking-tight mt-1">{session.procedure_name}</h1>
            <p className="text-sm text-muted-foreground mt-2 text-mono">
              {session.patient_code} · {session.theatre ?? "—"} ·{" "}
              {session.started_at ? new Date(session.started_at).toLocaleString() : "—"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-info/15 text-info border-info/30 border self-start">
              {session.status.replace("_", " ")}
            </Badge>
            <Button onClick={handleExport} disabled={exporting} className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
              {exporting ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Download className="mr-1.5 h-4 w-4" />}
              Export PDF
            </Button>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="hud-frame hud-corners relative p-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="text-hud-label">DURATION</div>
            <div className="text-mono text-2xl font-semibold mt-2 text-glow">
              {dur !== null ? `${Math.floor(dur / 60)}m ${dur % 60}s` : "—"}
            </div>
          </div>
          <div className="hud-frame hud-corners relative p-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="text-hud-label">TRANSCRIPT LINES</div>
            <div className="text-mono text-2xl font-semibold mt-2 text-glow">{transcripts.length}</div>
          </div>
          <div className="hud-frame hud-corners relative p-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="text-hud-label">ALERTS SURFACED</div>
            <div className="text-mono text-2xl font-semibold mt-2 text-glow">{alerts.length}</div>
          </div>
        </div>

        {alerts.length > 0 && (
          <section className="mt-10">
            <h2 className="text-display text-xl font-semibold">Alerts</h2>
            <div className="mt-4 panel divide-y divide-border">
              {alerts.map((a) => (
                <div key={a.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold">{a.title}</h3>
                    <Badge variant="outline" className="text-[10px] uppercase tracking-wider">
                      {a.severity} · {a.source}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{a.body}</p>
                  <p className="text-mono text-[10px] text-muted-foreground mt-2">
                    {new Date(a.created_at).toLocaleTimeString()} · {a.acknowledged ? "acknowledged" : "not acknowledged"}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="mt-10">
          <h2 className="text-display text-xl font-semibold">Transcript</h2>
          <div className="mt-4 panel max-h-[480px] overflow-y-auto divide-y divide-border">
            {transcripts.length === 0 ? (
              <div className="p-6 text-sm text-muted-foreground">No transcript captured.</div>
            ) : transcripts.map((t) => (
              <div key={t.id} className="p-3 flex gap-4">
                <span className="text-mono text-[10px] uppercase tracking-[0.2em] text-primary/70 w-20 shrink-0 mt-1">
                  {t.speaker}
                </span>
                <p className="text-sm">{t.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-10 panel-strong p-6">
          <div className="flex items-center gap-2 text-hud-label">
            <ShieldCheck className="h-4 w-4 text-primary" /> CDS DISCLAIMER
          </div>
          <p className="mt-3 text-sm text-muted-foreground">{CDS_DISCLAIMER_FULL}</p>
        </section>
      </div>
    </AppShell>
  );
};

export default PostOp;
