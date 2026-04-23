import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Activity, Stethoscope, ShieldCheck, ArrowRight, Clock, Cpu, Radio, Eye,
} from "lucide-react";
import { NaelLogo } from "@/components/NaelLogo";

type SessionRow = {
  id: string;
  procedure_name: string;
  patient_code: string;
  status: string;
  current_mode: string;
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
};

const Dashboard = () => {
  const { profile, user, roles } = useAuth();
  const [sessions, setSessions] = useState<SessionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const isAdmin = roles.includes("admin");

  useEffect(() => {
    let alive = true;
    (async () => {
      const { data } = await supabase
        .from("sessions")
        .select("id, procedure_name, patient_code, status, current_mode, created_at, started_at, ended_at")
        .order("created_at", { ascending: false })
        .limit(8);
      if (alive) {
        setSessions((data ?? []) as SessionRow[]);
        setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 18) return "Good afternoon";
    return "Good evening";
  })();

  const completed = sessions.filter((s) => s.status === "completed").length;
  const inProgress = sessions.filter((s) => s.status === "in_progress").length;

  return (
    <AppShell>
      <div className="hud-scanline">
        <CdsBanner />
        <div className="container py-8 md:py-10 max-w-6xl">
          {/* Hero header */}
          <div className="hud-frame hud-corners relative p-6 md:p-8 overflow-hidden">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="absolute inset-0 hud-grid opacity-40 pointer-events-none" />
            <div className="absolute -right-20 -top-20 w-72 h-72 rounded-full bg-primary/5 blur-3xl pointer-events-none" />

            <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div className="flex items-start gap-5 min-w-0">
                <NaelLogo size="md" showWordmark={false} />
                <div className="min-w-0">
                  <div className="text-mono text-[10px] uppercase tracking-[0.3em] text-primary/70 flex items-center gap-2">
                    <span className="pulse-dot nael" />
                    {greeting} · NAEL STANDBY
                  </div>
                  <h1 className="text-display text-3xl md:text-4xl font-semibold tracking-tight mt-2 text-glow">
                    {profile?.title ? `${profile.title} ` : ""}{profile?.full_name || user?.email?.split("@")[0]}
                  </h1>
                  {profile?.hospital && (
                    <p className="mt-1 text-sm text-muted-foreground text-mono uppercase tracking-wider">
                      {profile.hospital}
                    </p>
                  )}
                </div>
              </div>
              <Button asChild size="lg" className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
                <Link to="/sessions/domain">
                  <Stethoscope className="mr-2 h-4 w-4" /> New OR Session
                </Link>
              </Button>
            </div>
          </div>

          {/* Stat strip */}
          <div className="mt-6 grid gap-3 md:grid-cols-4">
            <StatCard icon={Activity} label="Recent" value={sessions.length.toString()} sub="last 8 sessions" />
            <StatCard icon={Radio}    label="In progress" value={inProgress.toString()} sub="live now" highlight={inProgress > 0} />
            <StatCard icon={Eye}      label="Completed" value={completed.toString()} sub="this view" />
            <StatCard icon={ShieldCheck} label="Compliance" value="DPDP" sub="CDS · audit logged" />
          </div>

          {/* Recent sessions */}
          <div className="mt-8">
            <div className="flex items-center justify-between mb-3">
              <div className="text-hud-label">RECENT SESSIONS · ARCHIVE</div>
              <Button asChild variant="ghost" size="sm" className="text-mono text-[11px] uppercase tracking-wider text-primary/80 hover:text-primary">
                <Link to="/sessions">View all <ArrowRight className="ml-1.5 h-3 w-3" /></Link>
              </Button>
            </div>

            <div className="hud-frame hud-corners relative">
              <span className="corner-tr" /><span className="corner-bl" />
              {loading ? (
                <div className="p-8 text-mono text-[11px] uppercase tracking-wider text-muted-foreground text-center">
                  Querying archive…
                </div>
              ) : sessions.length === 0 ? (
                <div className="p-10 text-center">
                  <div className="text-mono text-[10px] uppercase tracking-[0.3em] text-primary/60">NO SESSIONS · STANDBY</div>
                  <p className="mt-3 text-sm text-muted-foreground">Initiate the first OR session to populate your archive.</p>
                  <Button asChild className="mt-5 bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
                    <Link to="/sessions/domain">Start your first session</Link>
                  </Button>
                </div>
              ) : (
                <ul className="divide-y divide-primary/15">
                  {sessions.map((s) => (
                    <li key={s.id}>
                      <Link
                        to={s.status === "completed" ? `/sessions/${s.id}/post-op` : `/sessions/${s.id}/console`}
                        className="group flex items-center justify-between gap-4 px-4 py-3.5 hover:bg-primary/5 transition-colors"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span className={`pulse-dot ${s.status === "in_progress" ? "live" : "nael"} shrink-0`} />
                          <div className="min-w-0">
                            <div className="font-medium truncate text-foreground/95 group-hover:text-glow">
                              {s.procedure_name}
                            </div>
                            <div className="text-mono text-[10px] uppercase tracking-wider text-muted-foreground mt-0.5 truncate">
                              {s.patient_code} · {new Date(s.created_at).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <Badge variant="outline" className="text-[9px] uppercase tracking-wider border-primary/30 text-primary/80">
                            {s.current_mode}
                          </Badge>
                          <StatusBadge status={s.status} />
                          <ArrowRight className="h-3.5 w-3.5 text-primary/40 group-hover:text-primary group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Admin panel */}
          {isAdmin && (
            <div className="mt-8 hud-frame hud-corners relative p-6">
              <span className="corner-tr" /><span className="corner-bl" />
              <div className="flex items-center gap-2 text-hud-label">
                <Cpu className="h-3 w-3" /> ADMIN · OPS CONSOLE
              </div>
              <h3 className="mt-2 text-lg font-semibold text-glow">Compliance & infrastructure</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Audit log, user management, and GPU backend health for the ShalyaMitra realtime relay.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button asChild variant="outline" className="border-primary/40 hover:border-primary"><Link to="/admin/audit">Audit log</Link></Button>
                <Button asChild variant="outline" className="border-primary/40 hover:border-primary"><Link to="/admin/users">User management</Link></Button>
                <Button asChild variant="outline" className="border-primary/40 hover:border-primary"><Link to="/admin/gpu">GPU backend</Link></Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
};

function StatCard({ icon: Icon, label, value, sub, highlight }: {
  icon: React.ComponentType<{ className?: string }>;
  label: string; value: string; sub?: string; highlight?: boolean;
}) {
  return (
    <div className={`hud-frame hud-corners relative p-4 ${highlight ? "ring-1 ring-primary/40 shadow-glow" : ""}`}>
      <span className="corner-tr" /><span className="corner-bl" />
      <div className="flex items-center justify-between">
        <span className="text-hud-label">{label}</span>
        <Icon className="h-3.5 w-3.5 text-primary/80" />
      </div>
      <div className="mt-3 text-mono text-2xl font-semibold text-glow">{value}</div>
      {sub && <div className="text-mono text-[10px] uppercase tracking-wider text-muted-foreground mt-1">{sub}</div>}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, string> = {
    in_progress: "bg-success/15 text-success border-success/30",
    completed: "bg-info/15 text-info border-info/30",
    scheduled: "bg-muted text-muted-foreground border-border",
    aborted: "bg-destructive/15 text-destructive border-destructive/30",
  };
  return (
    <Badge className={`text-[9px] uppercase tracking-wider border ${variants[status] ?? variants.scheduled}`}>
      {status.replace("_", " ")}
    </Badge>
  );
}

export default Dashboard;
